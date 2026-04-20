#!/usr/bin/env python3
from __future__ import annotations

import csv
import html
import json
import math
import re
import shutil
import subprocess
import sys
import time
import zipfile
from collections import Counter
from calendar import monthrange
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any
from urllib.parse import quote, urlencode


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output" / "gtd-greater-manchester-gp-practice-reviews-2026-03-09"
COMPOSITE_REGION_DEFINITIONS_JSON = BASE_DIR / "config" / "composite_region_definitions.json"
GP_PATIENT_SURVEY_RAW_DIR = BASE_DIR / "raw" / "gp_patient_survey"
GOOGLE_REVIEW_RESULTS_JSON = OUTPUT_DIR / "google_maps_recent_reviews.json"
GTD_TAKEOVER_METADATA_JSON = BASE_DIR / "config" / "gtd_takeover_dates.json"
GP_PATIENT_SURVEY_BRANCH_PARENT_JSON = BASE_DIR / "config" / "gp_patient_survey_branch_parent_codes.json"
PATIENT_COUNTS_BY_YEAR_JSON = BASE_DIR / "raw" / "registered_patients" / "patient_counts_by_year.json"
DEPRIVATION_SUBSET_GEOJSON = BASE_DIR / "deprivation" / "output" / "catchment_lsoa_imd_2025.geojson"
NATIONAL_PRACTICES_OUTPUT_DIR = BASE_DIR / "national-practices" / "output"
NATIONAL_PRACTICES_SCOTLAND_DIR = BASE_DIR / "national-practices" / "scotland"
NATIONAL_GOOGLE_REVIEW_RESULTS_JSON = NATIONAL_PRACTICES_OUTPUT_DIR / "google_maps_recent_reviews.json"
NATIONAL_PRACTICES_INPUT_CSV = NATIONAL_PRACTICES_OUTPUT_DIR / "uk_gp_practices_not_in_current_dataset.csv"
SCOTLAND_HACE_DATA_JSON = NATIONAL_PRACTICES_SCOTLAND_DIR / "hace_metrics.json"
NATIONAL_SUPPLEMENTAL_SCRIPT_NAME = "national-practice-supplementals.js"
MAP_EMBED_SCRIPT_NAME = "map-embed-data.js"
RATING_CHANGE_EMBED_SCRIPT_NAME = "rating-change-over-time-embed.js"
MAP_ASSETS_DIR = BASE_DIR / "gtd_gp_map"
PUBLISHED_CATCHMENT_INDEX_REL_PATH = "catchments/index.json"
PUBLISHED_HEALTHCARE_TERRAIN_ROOT_REL_PATH = "healthcare-terrain"
PUBLISHED_HEALTHCARE_TERRAIN_CATCHMENT_REL_PATH = f"{PUBLISHED_HEALTHCARE_TERRAIN_ROOT_REL_PATH}/catchment-availability"
ENGLAND_GP_CATCHMENT_BY_PRACTICE_DIR = BASE_DIR / "catchments" / ".cache" / "gp-catchments-england" / "by_practice"
ENGLAND_GP_REGISTRATION_FLAGS_BY_PRACTICE_JSON = BASE_DIR / "catchments" / ".cache" / "gp-registration-flags-england" / "flags_by_practice.json"
CQC_GP_RATINGS_JSON = BASE_DIR / "raw" / "cqc" / "cqc_gp_location_index.json"
GPPS_DOWNLOADS_DIR = Path.home() / "Downloads" / "nhs-gpps-stats"
HEALTHCARE_TERRAIN_OUTPUT_DIR = BASE_DIR / "healthcare-terrain" / "output" / "england-catchment-availability"
HEALTHCARE_TERRAIN_DISTANCE_OUTPUT_DIR = BASE_DIR / "healthcare-terrain" / "output" / "distance-strength"

from deprivation.practice_deprivation_lookup import load_cached_practice_deprivation_lookup, write_practice_deprivation_lookup
RADIUS_MILES = 5.0
RADIUS_METERS = 8046.72
COMPOSITE_REGION_RADIUS_MILES = 5.0
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0 Safari/537.36"


@dataclass(frozen=True)
class GTDAnchor:
    gtd_site_name: str
    gtd_url: str
    postcode: str
    ods_code: str
    nhs_name_hint: str | None = None


@dataclass(frozen=True)
class SupplementalSearchCenter:
    name: str
    postcode: str
    scope_note: str


GTD_ANCHORS = [
    GTDAnchor("Ashton GP Service", "https://www.gtdhealthcare.co.uk/ashtongpservice", "OL6 7SR", "Y02586"),
    GTDAnchor("Charlestown Medical Practice", "https://www.gtdhealthcare.co.uk/charlestownmedicalpractice", "M9 7ED", "Y02325", "Charlestown MD"),
    GTDAnchor("City Health Centre", "https://www.gtdhealthcare.co.uk/cityhealthcentre", "M1 1PL", "Y02849"),
    GTDAnchor("Droylsden Medical Practice", "https://www.gtdhealthcare.co.uk/droylsdenmedicalpractice", "M43 7NP", "Y02663"),
    GTDAnchor("Gordon Street Medical Centre", "https://www.gtdhealthcare.co.uk/gordonstreetmedicalcentre", "OL6 6NE", "P89011"),
    GTDAnchor("Guide Bridge Medical Practice", "https://www.gtdhealthcare.co.uk/guidebridgemedicalpractice", "M34 5HY", "Y02713"),
    GTDAnchor("Hattersley Group Practice", "https://www.gtdhealthcare.co.uk/hattersleygrouppractice", "SK14 3NL", "P89013"),
    GTDAnchor("Lindley Medical Practice", "https://www.gtdhealthcare.co.uk/lindleymedicalpractice", "OL1 1NL", "Y02875", "Lindley House Health Centre"),
    GTDAnchor("Millbrook Medical Practice", "https://www.gtdhealthcare.co.uk/millbrookmedicalpractice", "SK15 3BJ", "Y02936"),
    GTDAnchor("Mossley Medical Practice", "https://www.gtdhealthcare.co.uk/mossleymedicalpractice", "OL5 9AB", "P89612"),
    GTDAnchor("New Bank Health Centre", "https://www.gtdhealthcare.co.uk/newbankhealthcentre", "M12 4JE", "Y02960", "New Bank Health"),
    GTDAnchor("Simpson Medical Practice", "https://www.gtdhealthcare.co.uk/simpsonmedicalpractice", "M40 9NB", "Y02520"),
    GTDAnchor("The Smithy Surgery", "https://www.gtdhealthcare.co.uk/thesmithysurgery", "SK14 8LJ", "P89602"),
]


SUPPLEMENTAL_SEARCH_CENTERS = [
    SupplementalSearchCenter("Chorlton supplemental search", "M21 8AU", "Pull in south-west Manchester and Chorlton-side practices"),
    SupplementalSearchCenter("Wythenshawe supplemental search", "M22 5RX", "Pull in Wythenshawe and airport-side practices"),
    SupplementalSearchCenter("Baguley supplemental search", "M23 9JH", "Pull in Baguley, Brooklands, Northern Moor and nearby south Manchester practices"),
    SupplementalSearchCenter("Stretford supplemental search", "M32 0JG", "Pull in Trafford / Stretford / west Manchester practices"),
    SupplementalSearchCenter("Sale supplemental search", "M33 7ZF", "Pull in Sale-side practices that the GTD anchors miss"),
    SupplementalSearchCenter("Bolton central supplemental search", "BL1 1RU", "Pull in clearly in-scope Bolton practices missed by the existing M60-side search centres"),
    SupplementalSearchCenter("Prestwich supplemental search", "M25 1BT", "Pull in north-west Manchester / Prestwich-side practices inside and just beyond the M60"),
    SupplementalSearchCenter("Radcliffe supplemental search", "M26 1LS", "Pull in Radcliffe-side practices around the north-west arc beyond the M60"),
    SupplementalSearchCenter("Swinton supplemental search", "M27 4AA", "Pull in Swinton and Pendlebury-side practices on the north-west / west side of the M60"),
    SupplementalSearchCenter("Little Hulton supplemental search", "M28 0BQ", "Pull in Walkden, Little Hulton and nearby western-edge practices around the M60"),
    SupplementalSearchCenter("Whitefield supplemental search", "M45 8WF", "Pull in Whitefield and Bury-south practices around the north-west arc of the M60"),
    SupplementalSearchCenter("Salford Quays supplemental search", "M50 3UB", "Pull in Salford Quays / Ordsall-side practices inside the western side of the M60"),
    SupplementalSearchCenter("Partington supplemental search", "M31 4FL", "Pull in Partington, Carrington and nearby outer-west practices around the M60"),
    SupplementalSearchCenter("Rochdale central supplemental search", "OL16 1AE", "Pull in clearly in-scope Rochdale-side practices that sit outside the current west and north-west searches"),
    SupplementalSearchCenter("Stockport central supplemental search", "SK1 1HE", "Pull in clearly in-scope Stockport and Reddish-side practices missed by the current Greater Manchester anchors"),
]


CITY_CATCHMENTS = [
    {"name": "Manchester", "lat": 53.4808, "lon": -2.2426, "radius_miles": 5.8, "accent": "#8d3c17"},
    {"name": "London", "lat": 51.5072, "lon": -0.1276, "radius_miles": 8.5, "accent": "#6f4aa8"},
    {"name": "Liverpool", "lat": 53.4084, "lon": -2.9916, "radius_miles": 5.3, "accent": "#2f6fa5"},
    {"name": "Leeds", "lat": 53.8008, "lon": -1.5491, "radius_miles": 5.8, "accent": "#3f7d4c"},
    {"name": "Sheffield", "lat": 53.3811, "lon": -1.4701, "radius_miles": 5.4, "accent": "#995b2e"},
    {"name": "Birmingham", "lat": 52.4862, "lon": -1.8904, "radius_miles": 6.6, "accent": "#5d6bb3"},
    {"name": "Bristol", "lat": 51.4545, "lon": -2.5879, "radius_miles": 5.1, "accent": "#8a4c7f"},
    {"name": "Newcastle", "lat": 54.9783, "lon": -1.6178, "radius_miles": 4.9, "accent": "#8d6f1f"},
    {"name": "Glasgow", "lat": 55.8642, "lon": -4.2518, "radius_miles": 6.2, "accent": "#2f7c7f"},
    {"name": "Edinburgh", "lat": 55.9533, "lon": -3.1883, "radius_miles": 5.0, "accent": "#7b3f69"},
    {"name": "Cardiff", "lat": 51.4816, "lon": -3.1791, "radius_miles": 4.8, "accent": "#5f5a9b"},
    {"name": "Belfast", "lat": 54.5973, "lon": -5.9301, "radius_miles": 5.2, "accent": "#3f6b6f"},
    {"name": "Oxford", "lat": 51.7520, "lon": -1.2577, "radius_miles": 3.7, "accent": "#7a5a2a"},
    {"name": "Harrogate", "lat": 53.9921, "lon": -1.5418, "radius_miles": 3.3, "accent": "#4c6b9a"},
]

NATION_ORDER = ["england", "scotland", "wales", "northern_ireland"]

SURVEY_METADATA_BY_NATION: dict[str, dict[str, str]] = {
    "england": {
        "patient_survey_name": "GP Patient Survey",
        "patient_survey_status": "practice_level_available",
        "patient_survey_level": "practice",
        "patient_survey_url": "https://www.gp-patient.co.uk",
        "patient_survey_note": "England practice-level patient survey source is available separately via GP Patient Survey page and CSV workflows.",
    },
    "wales": {
        "patient_survey_name": "People's Experience Survey",
        "patient_survey_status": "equivalent_identified_not_yet_wired",
        "patient_survey_level": "national_framework",
        "patient_survey_url": "https://www.gov.wales/peoples-experience-framework",
        "patient_survey_note": "Primary-care patient-experience framework exists, but this build does not yet pull a practice-level Wales survey feed.",
    },
    "scotland": {
        "patient_survey_name": "Health and Care Experience Survey",
        "patient_survey_status": "equivalent_identified_not_yet_wired",
        "patient_survey_level": "dashboard_or_aggregate",
        "patient_survey_url": "https://publichealthscotland.scot/publications/health-and-care-experience-survey/health-and-care-experience-survey-2024/detailed-experience-ratings-results/",
        "patient_survey_note": "Equivalent survey source exists, but this build does not yet parse the current Public Health Scotland experience dashboard export.",
    },
    "northern_ireland": {
        "patient_survey_name": "GP patient surveys",
        "patient_survey_status": "discontinued",
        "patient_survey_level": "historic_only",
        "patient_survey_url": "https://www.health-ni.gov.uk/articles/gp-patient-surveys",
        "patient_survey_note": "Northern Ireland GP patient survey ran from 2008/09 to 2010/11 and was then discontinued; no current practice-level equivalent is wired here.",
    },
}


COUNTY_WORDS = {
    "greater manchester",
    "cheshire",
    "derbyshire",
    "lancashire",
    "england",
    "uk",
}


def fetch_text(url: str) -> str:
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            completed = subprocess.run(
                [
                    "curl",
                    "-LfsS",
                    "--connect-timeout",
                    "15",
                    "--max-time",
                    "60",
                    "--retry",
                    "2",
                    "--retry-delay",
                    "1",
                    "-A",
                    USER_AGENT,
                    url,
                ],
                check=True,
                capture_output=True,
                text=True,
                timeout=70,
            )
            return completed.stdout
        except Exception as exc:
            last_error = exc
            time.sleep(1 + attempt)
    raise RuntimeError(f"Failed to fetch {url}") from last_error


def fetch_json(url: str) -> Any:
    return json.loads(fetch_text(url))


def is_truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def load_gtd_takeover_index(path: Path = GTD_TAKEOVER_METADATA_JSON) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(payload, dict):
        return {}
    normalized: dict[str, dict[str, Any]] = {}
    for code, item in payload.items():
        if isinstance(item, dict):
            normalized[str(code).strip()] = item
    return normalized


def apply_gtd_takeover_metadata(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    takeover_index = load_gtd_takeover_index()
    enriched_rows: list[dict[str, Any]] = []
    for row in rows:
        enriched = dict(row)
        meta = takeover_index.get(str(enriched.get("canonical_code", "")).strip(), {}) if is_truthy(enriched.get("gtd_managed")) else {}
        enriched["gtd_takeover_date"] = str(meta.get("takeover_date", "")).strip()
        enriched["gtd_takeover_date_precision"] = str(meta.get("date_precision", "")).strip()
        enriched["gtd_takeover_note"] = str(meta.get("note", "")).strip()
        enriched["gtd_takeover_source_label"] = str(meta.get("source_label", "")).strip()
        enriched["gtd_takeover_source_url"] = str(meta.get("source_url", "")).strip()
        enriched_rows.append(enriched)
    return enriched_rows


def load_registered_patient_timeseries(
    path: Path = PATIENT_COUNTS_BY_YEAR_JSON,
) -> dict[str, dict[str, int]] | None:
    """Load per-year patient counts for dataset practices. Run datasets/scripts/download_patient_counts_by_year.py to generate."""
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("by_year")


def load_registered_patient_index(path: Path = PATIENT_COUNTS_BY_YEAR_JSON) -> dict[str, int]:
    """Load current patient counts from pre-parsed patient_counts_by_year.json (latest year)."""
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    by_year = data.get("by_year")
    if not by_year:
        return {}
    latest = max(by_year.keys(), key=int)
    return dict(by_year[latest])


def parent_patient_ods_code(code: Any) -> str:
    normalized = str(code or "").strip().upper()
    match = re.fullmatch(r"([A-Z0-9]{6})\d{3}", normalized)
    return match.group(1) if match else ""


def registered_patient_count_candidate(
    code: Any,
    registered_patient_counts: dict[str, int],
) -> dict[str, Any] | None:
    parent_code = parent_patient_ods_code(code)
    if not parent_code:
        return None
    value = registered_patient_counts.get(parent_code)
    if value in ("", None):
        return None
    return {
        "count": value,
        "code": parent_code,
        "source": "nhs_monthly_parent_ods_fallback",
        "confidence": "medium",
    }


def slugify(value: str) -> str:
    value = value.lower()
    value = value.replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value


def normalize_name(value: str) -> str:
    value = html.unescape(value).lower()
    value = value.replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def token_set(value: str) -> set[str]:
    return {token for token in normalize_name(value).split() if token not in {"the", "and", "of", "medical", "practice", "centre", "surgery", "group"}}


def similarity_score(left: str, right: str) -> float:
    left_tokens = token_set(left)
    right_tokens = token_set(right)
    if not left_tokens or not right_tokens:
        return 0.0
    overlap = len(left_tokens & right_tokens)
    return overlap / max(len(left_tokens), len(right_tokens))


def miles_between(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 3958.7613
    lat1r = math.radians(lat1)
    lon1r = math.radians(lon1)
    lat2r = math.radians(lat2)
    lon2r = math.radians(lon2)
    dlat = lat2r - lat1r
    dlon = lon2r - lon1r
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1r) * math.cos(lat2r) * math.sin(dlon / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(a))


def postcode_lookup(postcode: str) -> dict[str, Any]:
    safe = quote(postcode)
    data = fetch_json(f"https://api.postcodes.io/postcodes/{safe}")
    if data.get("status") != 200 or not data.get("result"):
        raise RuntimeError(f"Could not geocode postcode {postcode}")
    return data["result"]


def parse_distance_miles(raw: str) -> float:
    raw = html.unescape(raw).strip().lower()
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*mile", raw)
    if match:
        return float(match.group(1))
    bare_number = re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", raw)
    if bare_number:
        return float(bare_number.group(0))
    raise ValueError(f"Could not parse distance from {raw!r}")


def parse_nhs_search_results(page_html: str) -> list[dict[str, Any]]:
    blocks = re.findall(r'(<li\b[^>]*class="[^"]*\bresults__item\b[^"]*"[^>]*>.*?</li>)', page_html, flags=re.S)
    results: list[dict[str, Any]] = []
    for block in blocks:
        profile = re.search(r'href="(https://www\.nhs\.uk/services/gp-surgery/[^"]+)"', block)
        name = re.search(r'<h2[^>]*>\s*<a[^>]*>(.*?)</a>', block, flags=re.S) or re.search(
            r'<h4[^>]*id="orgname_\d+"[^>]*>(.*?)</h4>',
            block,
            flags=re.S,
        )
        ods = re.search(r'<p id="item_id_\d+"[^>]*>(.*?)</p>', block, flags=re.S)
        distance = re.search(r'<p id="distance_\d+"[^>]*>.*?([0-9]+(?:\.[0-9]+)?\s*miles?\s*away)</p>', block, flags=re.S) or re.search(
            r'<span id="distance_\d+"[^>]*>([0-9]+(?:\.[0-9]+)?)</span>',
            block,
            flags=re.S,
        )
        address = re.search(r'<p id="address_\d+"[^>]*>(.*?)</p>', block, flags=re.S)
        phone = re.search(r'<a id="phone_\d+_link" href="tel:[^"]+">(.*?)</a>', block, flags=re.S)
        org_type = re.search(r'<p id="item_org_type_id_\d+"[^>]*>(.*?)</p>', block, flags=re.S)
        accepting_new_patients = bool(re.search(r'>\s*Accepting new patients\s*<', block, flags=re.I))
        accepts_out_of_area = bool(re.search(r'>\s*Accepts out of area registrations\s*<', block, flags=re.I))
        if not (profile and name and ods and distance and address):
            continue
        clean_name = re.sub(r"<span[^>]*>.*?</span>", "", name.group(1), flags=re.S)
        clean_name = re.sub(r"<.*?>", "", clean_name, flags=re.S)
        clean_address = re.sub(r"<.*?>", "", address.group(1), flags=re.S)
        results.append(
            {
                "profile_url": html.unescape(profile.group(1).strip()),
                "name": html.unescape(" ".join(clean_name.split())),
                "ods_code": html.unescape(ods.group(1).strip()),
                "distance_miles": parse_distance_miles(distance.group(1)),
                "address": html.unescape(" ".join(clean_address.split())),
                "phone": html.unescape(" ".join(phone.group(1).split())) if phone else "",
                "org_type_id": html.unescape(org_type.group(1).strip()) if org_type else "",
                "accepting_new_patients": accepting_new_patients,
                "accepts_out_of_area_registrations": accepts_out_of_area,
            }
        )
    return results


def find_script_jsonld(page_html: str) -> dict[str, Any]:
    match = re.search(r'<script id="json-ld-script"[^>]*>(.*?)</script>', page_html, flags=re.S)
    if not match:
        raise RuntimeError("Could not find NHS JSON-LD")
    payload = html.unescape(match.group(1)).strip()
    return json.loads(payload)


def parse_nhs_profile(url: str) -> dict[str, Any]:
    page_html = fetch_text(url)
    jsonld = find_script_jsonld(page_html)
    title_match = re.search(r'<h1 id="page-heading"[^>]*>(.*?)</h1>', page_html, flags=re.S)
    canonical_match = re.search(r'<link id="canonical-url-metadata" rel="canonical" href="([^"]+)"', page_html)
    accepting = False
    banner_match = re.search(r'<p id="gp_accepting_patients_banner_text">(.*?)</p>', page_html, flags=re.S)
    if banner_match:
        banner_text = " ".join(re.sub(r"<.*?>", "", banner_match.group(1)).split()).lower()
        accepting = "accepting new patients" in banner_text and "not" not in banner_text
    website_match = re.search(r'"url":"([^"]*)"', page_html)
    postcode = jsonld.get("address", {}).get("postalCode", "")
    address_line = jsonld.get("address", {}).get("streetAddress", "")
    phone = jsonld.get("telephone", "")
    latitude = float(jsonld.get("geo", {}).get("latitude"))
    longitude = float(jsonld.get("geo", {}).get("longitude"))
    canonical_url = canonical_match.group(1) if canonical_match else url
    code_match = re.search(r"/([A-Z0-9]+)$", canonical_url)
    return {
        "canonical_url": canonical_url,
        "canonical_code": code_match.group(1) if code_match else "",
        "nhs_page_title": html.unescape(" ".join(re.sub(r"<.*?>", "", title_match.group(1)).split())) if title_match else jsonld.get("name", ""),
        "website_url": html.unescape(website_match.group(1)) if website_match else jsonld.get("url", ""),
        "telephone": phone,
        "street_address": address_line,
        "postcode": postcode,
        "latitude": latitude,
        "longitude": longitude,
        "accepting_new_patients": accepting,
    }


def derive_locality(address_text: str) -> str:
    parts = [part.strip() for part in address_text.split(",") if part.strip()]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    if parts[-1].lower() in COUNTY_WORDS and len(parts) >= 2:
        return parts[-2]
    return parts[-1]


def extract_justvisits_listing_urls(search_html: str) -> list[str]:
    seen: list[str] = []
    for match in re.finditer(r'/listing/([a-z0-9-]+)', search_html):
        url = f"https://justvisits.co.uk/listing/{match.group(1)}"
        if url not in seen:
            seen.append(url)
    return seen


def parse_justvisits_rating(page_html: str) -> tuple[float, int] | None:
    title_match = re.search(r"<title>(.*?)</title>", page_html, flags=re.S)
    title = html.unescape(title_match.group(1).strip()) if title_match else ""
    if title == "Just Visits - Discover Amazing Places":
        return None
    decoded = page_html.encode("utf-8").decode("unicode_escape")
    rating_match = re.search(r'aggregateRating\\":\{.*?ratingValue\\":\\"([0-9.]+)\\",\\"reviewCount\\":([0-9]+)', decoded, flags=re.S)
    if not rating_match:
        return None
    return (float(rating_match.group(1)), int(rating_match.group(2)))


def lookup_google_reviews(name: str, address_text: str) -> dict[str, Any]:
    locality = derive_locality(address_text)
    if not locality:
        return {"google_review_score": "", "google_review_count": "", "google_review_source_url": "", "google_review_source_note": ""}

    expected_slug = slugify(f"{name} {locality}")
    direct_url = f"https://justvisits.co.uk/listing/{expected_slug}"
    try:
        direct_html = fetch_text(direct_url)
        direct_rating = parse_justvisits_rating(direct_html)
        if direct_rating:
            return {
                "google_review_score": direct_rating[0],
                "google_review_count": direct_rating[1],
                "google_review_source_url": direct_url,
                "google_review_source_note": "Just Visits exact listing match",
            }
    except Exception:
        pass

    search_query = f"{name} {locality}"
    search_url = f"https://justvisits.co.uk/properties/search-results?{urlencode({'location': search_query})}"
    try:
        search_html = fetch_text(search_url)
        candidate_urls = extract_justvisits_listing_urls(search_html)
        if direct_url in candidate_urls:
            candidate_urls = [direct_url] + [url for url in candidate_urls if url != direct_url]
        else:
            exact_prefix = slugify(name)
            preferred = [url for url in candidate_urls if exact_prefix in url]
            candidate_urls = preferred + [url for url in candidate_urls if url not in preferred]
        for candidate_url in candidate_urls[:8]:
            try:
                candidate_html = fetch_text(candidate_url)
                rating = parse_justvisits_rating(candidate_html)
                if not rating:
                    continue
                title_match = re.search(r"<title>(.*?)</title>", candidate_html, flags=re.S)
                title = html.unescape(title_match.group(1).strip()) if title_match else ""
                if similarity_score(title, name) < 0.6:
                    continue
                note = "Just Visits search match"
                if candidate_url.endswith(expected_slug):
                    note = "Just Visits exact search match"
                return {
                    "google_review_score": rating[0],
                    "google_review_count": rating[1],
                    "google_review_source_url": candidate_url,
                    "google_review_source_note": note,
                }
            except Exception:
                continue
    except Exception:
        pass

    return {"google_review_score": "", "google_review_count": "", "google_review_source_url": "", "google_review_source_note": ""}


def anchor_search_url(lat: float, lon: float, label: str) -> str:
    safe_label = quote(label)
    return (
        "https://www.nhs.uk/service-search/find-a-gp/results/"
        f"{safe_label}?latitude={lat}&longitude={lon}&distance={RADIUS_METERS}&resultsOnPageValue=50&isNational=0"
    )


def resolve_anchor(anchor: GTDAnchor) -> dict[str, Any]:
    geo = postcode_lookup(anchor.postcode)
    lat = float(geo["latitude"])
    lon = float(geo["longitude"])
    results = parse_nhs_search_results(fetch_text(anchor_search_url(lat, lon, anchor.postcode)))
    choices = results

    def score(row: dict[str, Any]) -> tuple[int, float]:
        code_bonus = 1 if row["ods_code"] == anchor.ods_code else 0
        target_name = anchor.nhs_name_hint or anchor.gtd_site_name
        return (code_bonus, similarity_score(row["name"], target_name))

    if not choices:
        raise RuntimeError(f"Could not resolve GTD anchor {anchor.gtd_site_name}")
    best = max(choices, key=score)
    profile = parse_nhs_profile(best["profile_url"])
    return {
        "gtd_site_name": anchor.gtd_site_name,
        "gtd_url": anchor.gtd_url,
        "postcode": anchor.postcode,
        "ods_code": anchor.ods_code,
        "nhs_match_name": best["name"],
        "nhs_profile_url": profile["canonical_url"],
        "latitude": profile["latitude"],
        "longitude": profile["longitude"],
        "address": profile["street_address"],
    }


def resolve_supplemental_center(center: SupplementalSearchCenter) -> dict[str, Any]:
    geo = postcode_lookup(center.postcode)
    return {
        "name": center.name,
        "postcode": center.postcode,
        "scope_note": center.scope_note,
        "latitude": float(geo["latitude"]),
        "longitude": float(geo["longitude"]),
    }


def build_dataset() -> list[dict[str, Any]]:
    resolved_anchors = [resolve_anchor(anchor) for anchor in GTD_ANCHORS]
    resolved_supplementals = [resolve_supplemental_center(center) for center in SUPPLEMENTAL_SEARCH_CENTERS]
    registered_patient_counts = load_registered_patient_index()
    registration_flags_by_code = load_registration_flags_by_code()
    anchor_codes = {anchor["ods_code"]: anchor for anchor in resolved_anchors}
    practice_index: dict[str, dict[str, Any]] = {}

    for anchor in resolved_anchors:
        search_html = fetch_text(anchor_search_url(anchor["latitude"], anchor["longitude"], anchor["gtd_site_name"]))
        nearby = parse_nhs_search_results(search_html)
        for row in nearby:
            entry = practice_index.setdefault(
                row["profile_url"],
                {
                    "initial_profile_url": row["profile_url"],
                    "search_result_name": row["name"],
                    "search_result_address": row["address"],
                    "search_result_phone": row["phone"],
                    "search_result_ods_code": row["ods_code"],
                    "search_result_accepting_new_patients": row["accepting_new_patients"],
                    "search_result_accepts_out_of_area_registrations": row["accepts_out_of_area_registrations"],
                    "nearby_to_gtd_anchors": [],
                    "nearby_anchor_search_distances_miles": {},
                },
            )
            entry["search_result_accepting_new_patients"] = bool(entry.get("search_result_accepting_new_patients")) or bool(
                row["accepting_new_patients"]
            )
            entry["search_result_accepts_out_of_area_registrations"] = bool(
                entry.get("search_result_accepts_out_of_area_registrations")
            ) or bool(row["accepts_out_of_area_registrations"])
            if anchor["gtd_site_name"] not in entry["nearby_to_gtd_anchors"]:
                entry["nearby_to_gtd_anchors"].append(anchor["gtd_site_name"])
            entry["nearby_anchor_search_distances_miles"][anchor["gtd_site_name"]] = row["distance_miles"]
            source_centers = entry.setdefault("source_search_centers", [])
            if anchor["gtd_site_name"] not in source_centers:
                source_centers.append(anchor["gtd_site_name"])

    for center in resolved_supplementals:
        search_html = fetch_text(anchor_search_url(center["latitude"], center["longitude"], center["postcode"]))
        nearby = parse_nhs_search_results(search_html)
        for row in nearby:
            entry = practice_index.setdefault(
                row["profile_url"],
                {
                    "initial_profile_url": row["profile_url"],
                    "search_result_name": row["name"],
                    "search_result_address": row["address"],
                    "search_result_phone": row["phone"],
                    "search_result_ods_code": row["ods_code"],
                    "search_result_accepting_new_patients": row["accepting_new_patients"],
                    "search_result_accepts_out_of_area_registrations": row["accepts_out_of_area_registrations"],
                    "nearby_to_gtd_anchors": [],
                    "nearby_anchor_search_distances_miles": {},
                    "source_search_centers": [],
                },
            )
            entry["search_result_accepting_new_patients"] = bool(entry.get("search_result_accepting_new_patients")) or bool(
                row["accepting_new_patients"]
            )
            entry["search_result_accepts_out_of_area_registrations"] = bool(
                entry.get("search_result_accepts_out_of_area_registrations")
            ) or bool(row["accepts_out_of_area_registrations"])
            source_centers = entry.setdefault("source_search_centers", [])
            if center["name"] not in source_centers:
                source_centers.append(center["name"])

    records: list[dict[str, Any]] = []
    total = len(practice_index)
    for index, practice in enumerate(practice_index.values(), start=1):
        print(f"[{index}/{total}] Enriching {practice['search_result_name']}", file=sys.stderr)
        profile = parse_nhs_profile(practice["initial_profile_url"])
        canonical_code = profile["canonical_code"]
        registration_flags = registration_flags_by_code.get(canonical_code) or registration_flags_by_code.get(
            str(practice.get("search_result_ods_code") or "").strip().upper()
        ) or {}
        matched_anchor = anchor_codes.get(canonical_code)
        record = {
            "practice_name": profile["nhs_page_title"],
            "canonical_code": canonical_code,
            "nhs_profile_url": profile["canonical_url"],
            "website_url": profile["website_url"],
            "telephone": profile["telephone"] or practice["search_result_phone"],
            "street_address": profile["street_address"] or practice["search_result_address"],
            "postcode": profile["postcode"],
            "latitude": profile["latitude"],
            "longitude": profile["longitude"],
            "accepting_new_patients": bool(
                registration_flags.get("accepting_new_patients")
                if registration_flags.get("accepting_new_patients") is not None
                else profile["accepting_new_patients"]
            ),
            "accepts_out_of_area_registrations": bool(
                registration_flags.get("accepts_out_of_area_registrations")
                if registration_flags.get("accepts_out_of_area_registrations") is not None
                else practice.get("search_result_accepts_out_of_area_registrations")
            ),
            "gtd_managed": bool(matched_anchor),
            "gtd_site_name": matched_anchor["gtd_site_name"] if matched_anchor else "",
            "gtd_site_url": matched_anchor["gtd_url"] if matched_anchor else "",
            "nearby_to_gtd_anchors": ", ".join(sorted(practice["nearby_to_gtd_anchors"])),
            "nearby_anchor_count": len(practice["nearby_to_gtd_anchors"]),
            "source_search_centers": ", ".join(sorted(practice.get("source_search_centers", []))),
            "source_search_center_count": len(practice.get("source_search_centers", [])),
            "registered_patient_count": registered_patient_counts.get(canonical_code, ""),
        }
        record["registered_patient_count_source"] = "nhs_monthly_direct" if record["registered_patient_count"] != "" else ""
        record["registered_patient_count_candidate"] = ""
        record["registered_patient_count_candidate_code"] = ""
        record["registered_patient_count_candidate_source"] = ""
        record["registered_patient_count_candidate_confidence"] = ""
        if record["registered_patient_count"] == "":
            patient_count_candidate = registered_patient_count_candidate(canonical_code, registered_patient_counts)
            if patient_count_candidate:
                record["registered_patient_count_candidate"] = patient_count_candidate["count"]
                record["registered_patient_count_candidate_code"] = patient_count_candidate["code"]
                record["registered_patient_count_candidate_source"] = patient_count_candidate["source"]
                record["registered_patient_count_candidate_confidence"] = patient_count_candidate["confidence"]
        record["management_company_name"] = "GTD Healthcare" if matched_anchor else ""
        record["management_company_source"] = "gtd_anchor_match" if matched_anchor else ""
        record["management_company_confidence"] = "high" if matched_anchor else ""
        record["management_company_domain"] = "gtdhealthcare.co.uk" if matched_anchor else ""
        record["management_company_group_size"] = ""
        record["affiliated_group_name"] = ""
        record["affiliated_group_source"] = ""
        record["affiliated_group_confidence"] = ""
        record["affiliated_group_domain"] = ""
        record["affiliated_group_group_size"] = ""
        min_distance = None
        if practice["nearby_to_gtd_anchors"]:
            distances = []
            for anchor_name in practice["nearby_to_gtd_anchors"]:
                anchor = next(item for item in resolved_anchors if item["gtd_site_name"] == anchor_name)
                distance = miles_between(anchor["latitude"], anchor["longitude"], record["latitude"], record["longitude"])
                distances.append(distance)
            if distances:
                min_distance = min(distances)
        record["min_distance_to_gtd_anchor_miles"] = round(min_distance, 3) if min_distance is not None else ""
        google = lookup_google_reviews(record["practice_name"], record["street_address"])
        record.update(google)
        record["google_maps_title"] = ""
        record["google_maps_match_score"] = ""
        record["google_recent_reviews_captured"] = ""
        record["google_review_text_file"] = ""
        record["trustpilot_score"] = ""
        record["trustpilot_review_count"] = ""
        record["trustpilot_source_url"] = ""
        records.append(record)
        time.sleep(0.05)

    return sorted(records, key=lambda row: (not row["gtd_managed"], row["postcode"], row["practice_name"]))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    rows = apply_gtd_takeover_metadata(rows)
    fields = [
        "practice_name",
        "canonical_code",
        "postcode",
        "street_address",
        "latitude",
        "longitude",
        "telephone",
        "website_url",
        "accepting_new_patients",
        "accepts_out_of_area_registrations",
        "gtd_managed",
        "gtd_site_name",
        "gtd_site_url",
        "gtd_takeover_date",
        "gtd_takeover_date_precision",
        "gtd_takeover_note",
        "gtd_takeover_source_label",
        "gtd_takeover_source_url",
        "nearby_to_gtd_anchors",
        "nearby_anchor_count",
        "source_search_centers",
        "source_search_center_count",
        "min_distance_to_gtd_anchor_miles",
        "management_company_name",
        "management_company_source",
        "management_company_confidence",
        "management_company_domain",
        "management_company_group_size",
        "affiliated_group_name",
        "affiliated_group_source",
        "affiliated_group_confidence",
        "affiliated_group_domain",
        "affiliated_group_group_size",
        "registered_patient_count",
        "registered_patient_count_source",
        "registered_patient_count_candidate",
        "registered_patient_count_candidate_code",
        "registered_patient_count_candidate_source",
        "registered_patient_count_candidate_confidence",
        "google_review_score",
        "google_review_count",
        "google_review_source_note",
        "google_review_source_url",
        "google_maps_title",
        "google_maps_match_score",
        "google_recent_reviews_captured",
        "google_review_text_file",
        "google_review_scan_status",
        "google_review_has_listing",
        "cqc_overall_rating",
        "cqc_location_url",
        "cqc_service_website",
        "cqc_publication_date",
        "cqc_inherited_rating",
        "cqc_provider_name",
        "trustpilot_score",
        "trustpilot_review_count",
        "trustpilot_source_url",
        "nhs_profile_url",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(json.dumps(apply_gtd_takeover_metadata(rows), indent=2), encoding="utf-8")


def load_google_review_results(path: Path = GOOGLE_REVIEW_RESULTS_JSON) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return payload if isinstance(payload, list) else []


def catchment_base_code(code: str) -> str:
    normalized = str(code or "").strip().upper()
    match = re.match(r"^([A-Z]\d{5})(\d{3})$", normalized)
    return match.group(1) if match else normalized


def compact_geojson_geometry(value: Any, digits: int = 5) -> Any:
    if isinstance(value, float):
        return round(value, digits)
    if isinstance(value, list):
        return [compact_geojson_geometry(item, digits) for item in value]
    if isinstance(value, dict):
        return {key: compact_geojson_geometry(item, digits) for key, item in value.items()}
    return value


def geojson_features_from_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    kind = payload.get("type")
    if kind == "FeatureCollection":
        features = payload.get("features", [])
        return features if isinstance(features, list) else []
    if kind == "Feature":
        return [payload]
    return []


def write_manchester_catchment_bundle(path: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    review_results = load_google_review_results()
    full_feed_results = [row for row in review_results if str(row.get("review_collection_mode", "")).strip() == "full_feed"]
    row_name_by_code = {
        str(row.get("canonical_code", "")).strip(): str(row.get("practice_name", "")).strip()
        for row in rows
        if str(row.get("canonical_code", "")).strip()
    }
    bundle_groups: dict[str, dict[str, Any]] = {}
    covered_full_feed_codes: set[str] = set()
    missing_codes: list[str] = []

    for result in full_feed_results:
        code = str(result.get("canonical_code", "")).strip()
        if not code:
            continue
        direct_path = ENGLAND_GP_CATCHMENT_BY_PRACTICE_DIR / f"{code}.geojson"
        base_code = catchment_base_code(code)
        base_path = ENGLAND_GP_CATCHMENT_BY_PRACTICE_DIR / f"{base_code}.geojson"
        if direct_path.exists():
            resolved_code = code
            source_path = direct_path
        elif base_path.exists():
            resolved_code = base_code
            source_path = base_path
        else:
            missing_codes.append(code)
            continue
        covered_full_feed_codes.add(code)
        group = bundle_groups.setdefault(
            resolved_code,
            {
                "source_path": source_path,
                "codes": set(),
                "names": set(),
            },
        )
        group["codes"].add(code)
        group["codes"].add(resolved_code)
        preferred_name = row_name_by_code.get(code) or row_name_by_code.get(resolved_code) or str(result.get("practice_name", "")).strip()
        if preferred_name:
            group["names"].add(preferred_name)

    features: list[dict[str, Any]] = []
    for resolved_code, group in sorted(bundle_groups.items()):
        payload = json.loads(Path(group["source_path"]).read_text(encoding="utf-8"))
        source_features = geojson_features_from_payload(payload)
        feature_names = sorted(name for name in group["names"] if name)
        label = feature_names[0] if feature_names else resolved_code
        codes = sorted(code for code in group["codes"] if code)
        for feature in source_features:
            source_props = feature.get("properties", {}) if isinstance(feature, dict) else {}
            out_props = {
                "source_code": resolved_code,
                "codes": codes,
                "label": label,
            }
            area_km2 = source_props.get("Area_Km2")
            if area_km2 not in ("", None):
                out_props["area_km2"] = area_km2
            features.append(
                {
                    "type": "Feature",
                    "properties": out_props,
                    "geometry": compact_geojson_geometry(feature.get("geometry", {}), digits=5),
                }
            )

    feature_collection = {
        "type": "FeatureCollection",
        "metadata": {
            "practice_count": len(bundle_groups),
            "feature_count": len(features),
            "full_feed_review_practice_count": len({str(row.get("canonical_code", "")).strip() for row in full_feed_results if str(row.get("canonical_code", "")).strip()}),
            "covered_full_feed_practice_codes": len(covered_full_feed_codes),
            "missing_practice_codes": sorted(set(missing_codes)),
        },
        "features": features,
    }
    path.write_text(json.dumps(feature_collection, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {
        "practice_count": len(bundle_groups),
        "feature_count": len(features),
        "missing_practice_codes": sorted(set(missing_codes)),
        "full_feed_review_practice_count": len({str(row.get("canonical_code", "")).strip() for row in full_feed_results if str(row.get("canonical_code", "")).strip()}),
        "covered_full_feed_practice_codes": len(covered_full_feed_codes),
        "file_size_bytes": path.stat().st_size if path.exists() else 0,
    }


def write_summary(path: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    rows = apply_gtd_takeover_metadata(rows)
    postcodes = sorted({row["postcode"].split()[0] for row in rows if row["postcode"]})
    ts = load_registered_patient_timeseries()
    total_registered_patients_in_scope = sum(
        int(row["registered_patient_count"])
        for row in rows
        if row.get("registered_patient_count", "") not in ("", None)
    )
    total_registered_patients_gtd = sum(
        int(row["registered_patient_count"])
        for row in rows
        if row.get("gtd_managed") and row.get("registered_patient_count", "") not in ("", None)
    )
    summary = {
        "generated_date": "2026-03-09",
        "scope": "All GTD Healthcare GP practice anchors from the GTD Healthcare GP practices page, plus the full NHS Find a GP result set returned for a broad Greater Manchester catchment around each GTD anchor.",
        "radius_miles": RADIUS_MILES,
        "row_count": len(rows),
        "gtd_managed_count": sum(1 for row in rows if row["gtd_managed"]),
        "non_gtd_count": sum(1 for row in rows if not row["gtd_managed"]),
        "google_review_coverage_count": sum(1 for row in rows if row["google_review_score"] != ""),
        "google_maps_direct_coverage_count": sum(1 for row in rows if "Google Maps direct" in str(row.get("google_review_source_note", ""))),
        "google_review_text_file_count": sum(1 for row in rows if row.get("google_review_text_file", "")),
        "gtd_takeover_date_count": sum(1 for row in rows if row.get("gtd_takeover_date", "")),
        "management_company_identified_count": sum(1 for row in rows if row.get("management_company_name", "")),
        "management_company_distinct_count": len({row.get("management_company_name", "") for row in rows if row.get("management_company_name", "")}),
        "affiliated_group_identified_count": sum(1 for row in rows if row.get("affiliated_group_name", "")),
        "affiliated_group_distinct_count": len({row.get("affiliated_group_name", "") for row in rows if row.get("affiliated_group_name", "")}),
        "registered_patient_count_coverage": sum(1 for row in rows if row.get("registered_patient_count", "") != ""),
        "registered_patient_count_total_in_scope": total_registered_patients_in_scope,
        "registered_patient_count_total_gtd": total_registered_patients_gtd,
        "registered_patient_count_candidate_coverage": sum(1 for row in rows if row.get("registered_patient_count_candidate", "") != ""),
        "trustpilot_coverage_count": sum(1 for row in rows if row["trustpilot_score"] != ""),
        "postcode_area_count": len(postcodes),
        "postcode_areas": postcodes,
        "source_urls": {
            "gtd_gp_practices_page": "https://www.gtdhealthcare.co.uk/patient-services/gp-practices",
            "nhs_find_a_gp": "https://www.nhs.uk/service-search/find-a-gp",
            "postcode_geocoder": "https://api.postcodes.io/",
            "google_review_mirror": "https://justvisits.co.uk/",
            "patient_counts_json": str(PATIENT_COUNTS_BY_YEAR_JSON.relative_to(BASE_DIR)) if PATIENT_COUNTS_BY_YEAR_JSON.exists() else "",
            "gtd_takeover_dates": str(GTD_TAKEOVER_METADATA_JSON.relative_to(BASE_DIR)),
        },
        "patient_counts_by_year_years": sorted(ts.keys(), key=int) if ts else [],
        "supplemental_search_centers": [
            {"name": center.name, "postcode": center.postcode, "scope_note": center.scope_note}
            for center in SUPPLEMENTAL_SEARCH_CENTERS
        ],
        "notes": [
            "Google review fields were only filled when an exact or high-confidence Just Visits match was available.",
            "Trustpilot fields were left blank because no reliable per-practice public source was found in this run.",
            "This run intentionally keeps the broader NHS result set around each GTD anchor instead of trimming aggressively to 1 mile.",
            "Additional south, west, north-west, Bolton, Rochdale and Stockport coverage was added with explicit supplemental NHS search centres.",
            "When available, direct Google Maps captures can add a review text file path per practice without embedding the review text in the main CSV.",
            "GTD takeover dates are manually curated from official NHS / commissioner / practice sources and are intended to mark GTD's current-tenure start date for each GTD-managed practice.",
            "Management company fields are conservative and should only be filled when the NHS-listed website or GTD anchor match makes the operator identifiable.",
            "Affiliated group fields are separate from management company fields and are intended for federations, extended-hours operators, or similar network relationships that may coexist with core management.",
            "Registered patient counts come from the NHS monthly GP registered patients totals file, matched by ODS code.",
            "Registered patient count candidate fields are advisory only and are used for branch/site reconciliation without replacing the direct NHS monthly match.",
        ],
    }
    path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def write_readme(path: Path, summary: dict[str, Any]) -> None:
    readme = f"""# GTD Greater Manchester GP Practice Reviews Dataset

Generated on 2026-03-09.

This folder contains a postcode-and-coordinates dataset for:

- all GTD Healthcare GP practice anchors listed on the GTD Healthcare GP practices page
- the broader NHS Find a GP result set returned around each GTD anchor

Files:

- `gtd_greater_manchester_gp_practices.csv`: tabular export
- `gtd_greater_manchester_gp_practices.json`: JSON export
- `summary.json`: dataset counts and source notes
- `map.html`: Leaflet map for local viewing
- `google_maps_recent_reviews.json`: raw structured Google Maps capture output
- `google_maps_manual_review.md`: ambiguous or failed captures queued for manual review
- `google-review-texts/`: per-practice text files for any captured visible Google review text
- `gtd_takeover_*` fields in the CSV/JSON: documented current-tenure GTD takeover dates plus source notes for GTD-managed practices
- `management_company_*` fields in the CSV/JSON: conservative operator identification where supported by the NHS-listed website or GTD source data
- `affiliated_group_*` fields in the CSV/JSON: separate network/federation/operator links that should not be treated as the core management company
- `registered_patient_count` in the CSV/JSON: NHS monthly registered patient total matched by ODS code
- `registered_patient_count_candidate_*` fields: advisory branch/site reconciliation matches where the direct ODS code is absent from the NHS monthly list-size file

Source basis:

- GTD Healthcare GP practices page: https://www.gtdhealthcare.co.uk/patient-services/gp-practices
- NHS Find a GP search results and profile pages: https://www.nhs.uk/service-search/find-a-gp
- Postcode geocoding: https://api.postcodes.io/
- Google review mirror used when exact matches were found: https://justvisits.co.uk/
- Registered patient counts: pre-parsed patient_counts_by_year.json (run datasets/scripts/download_patient_counts_by_year.py manually)
- Supplemental broader Greater Manchester search centres: M21 8AU, M22 5RX, M23 9JH, M25 1BT, M26 1LS, M27 4AA, M28 0BQ, M31 4FL, M32 0JG, M33 7ZF, M45 8WF, M50 3UB

Coverage snapshot:

- total rows: {summary['row_count']}
- GTD-managed rows: {summary['gtd_managed_count']}
- non-GTD nearby rows: {summary['non_gtd_count']}
- Google review coverage rows: {summary['google_review_coverage_count']}
- Google Maps direct coverage rows: {summary['google_maps_direct_coverage_count']}
- Review text files written: {summary['google_review_text_file_count']}
- GTD takeover dates documented: {summary.get('gtd_takeover_date_count', 0)}
- Practices with management company identified: {summary.get('management_company_identified_count', 0)}
- Distinct management companies identified: {summary.get('management_company_distinct_count', 0)}
- Practices with affiliated group identified: {summary.get('affiliated_group_identified_count', 0)}
- Distinct affiliated groups identified: {summary.get('affiliated_group_distinct_count', 0)}
- Practices with registered patient count: {summary.get('registered_patient_count_coverage', 0)}
- Practices with registered patient count candidate: {summary.get('registered_patient_count_candidate_coverage', 0)}
- Google Maps scans completed: {summary.get('google_maps_total_scanned_count', 0)}
- Google Maps manual review queue: {summary.get('google_maps_manual_review_count', 0)}

Caveats:

- Google review fields are partial. They were only populated when a high-confidence public mirror match could be identified.
- `gtd_takeover_*` fields reflect GTD's current-tenure start date for the GTD practices in this bundle and may use month-level precision where only month/year was published.
- `management_company_*` fields should remain blank unless the operator is identifiable from GTD source data or a clear NHS-listed website-domain grouping.
- `affiliated_group_*` fields may capture a federation, enhanced-hours operator, or similar network relationship even where the core management company is still blank.
- `registered_patient_count_candidate_*` fields should be treated as branch/site hints and should not be summed as if they were additional registered patients.
- Trustpilot fields are blank in this run because a reliable per-practice public source was not found.
- GTD's Lindley Medical Practice was matched to the NHS profile currently published as `Lindley House Health Centre` at the same Oldham site.
"""
    path.write_text(readme, encoding="utf-8")


def load_gp_patient_survey_index(raw_dir: Path = GP_PATIENT_SURVEY_RAW_DIR) -> dict[str, dict[str, Any]]:
    if not raw_dir.exists():
        return {}
    survey_by_code: dict[str, dict[str, Any]] = {}
    for survey_file in sorted(raw_dir.glob("*.json")):
        try:
            payload = json.loads(survey_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        code = str(payload.get("canonical_code", "")).strip()
        if code:
            survey_by_code[code] = payload
    return survey_by_code


def load_scotland_hace_index(
    data_path: Path = SCOTLAND_HACE_DATA_JSON,
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    if not data_path.exists():
        return {}, {}
    try:
        dataset = json.loads(data_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}, {}
    if not isinstance(dataset, dict):
        return {}, {}
    dataset_meta = dataset.get("_meta", {})
    if not isinstance(dataset_meta, dict):
        dataset_meta = {}
    practices = dataset.get("practices", {})
    if not isinstance(practices, dict):
        return {}, {}

    manifest_by_code: dict[str, dict[str, Any]] = {}
    payload_by_code: dict[str, dict[str, Any]] = {}
    for code, entry in practices.items():
        if not isinstance(entry, dict):
            continue
        normalized_code = str(code).strip().upper()
        if not normalized_code:
            continue
        manifest_by_code[normalized_code] = entry
        if entry.get("status") != "ok":
            continue
        overall_percent = percent_or_blank(entry.get("survey_overall_good_percent"))
        response_rate_percent = percent_or_blank(entry.get("response_rate_percent"))
        payload_by_code[normalized_code] = {
            "canonical_code": normalized_code,
            "source_url": str(entry.get("source_url") or dataset_meta.get("source_url") or "").strip(),
            "fetched_at": str(entry.get("fetched_at", "")).strip(),
            "tableau_report_area_label": str(entry.get("tableau_report_area_label", "")).strip(),
            "response_rate_percent": response_rate_percent,
            "completion_rate_percent": response_rate_percent,
            "number_of_responses": entry.get("number_of_responses", ""),
            "responses_for_overall_question": entry.get("responses_for_overall_question", ""),
            "key_questions": {
                "overallexp": {
                    "practice_percent": overall_percent,
                }
            },
        }
    return payload_by_code, manifest_by_code


def load_gp_patient_survey_branch_parent_index(
    path: Path = GP_PATIENT_SURVEY_BRANCH_PARENT_JSON,
) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(payload, dict):
        return {}
    index: dict[str, dict[str, Any]] = {}
    for code, item in payload.items():
        if str(code).startswith("_"):
            continue
        if isinstance(item, str):
            index[str(code).strip()] = {"parent_code": item.strip()}
        elif isinstance(item, dict):
            index[str(code).strip()] = item
    return index


def load_deprivation_subset_geojson(path: Path = DEPRIVATION_SUBSET_GEOJSON) -> dict[str, Any]:
    if not path.exists():
        return {"type": "FeatureCollection", "features": []}
    return json.loads(path.read_text(encoding="utf-8"))


def survey_metric(payload: dict[str, Any], question_name: str, field: str = "practice_percent") -> Any:
    key_questions = payload.get("key_questions", {})
    if not isinstance(key_questions, dict):
        return ""
    question = key_questions.get(question_name, {})
    if not isinstance(question, dict):
        return ""
    return question.get(field, "")


def has_usable_gp_patient_survey_data(payload: dict[str, Any]) -> bool:
    return (
        survey_metric(payload, "overallexp") not in ("", None)
        or payload.get("completion_rate_percent", "") not in ("", None)
    )


def resolve_gp_patient_survey_payload(
    code: str,
    survey_by_code: dict[str, dict[str, Any]],
    branch_parent_by_code: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], str, str]:
    direct_payload = survey_by_code.get(code, {})
    if has_usable_gp_patient_survey_data(direct_payload):
        return direct_payload, code, ""
    branch_meta = branch_parent_by_code.get(code, {})
    parent_code = str(branch_meta.get("parent_code", "")).strip()
    if not parent_code:
        return direct_payload, code, ""
    parent_payload = survey_by_code.get(parent_code, {})
    if not has_usable_gp_patient_survey_data(parent_payload):
        return direct_payload, code, ""
    branch_name = str(branch_meta.get("branch_name_ods", "")).strip()
    note = f"GP Patient Survey uses parent practice code {parent_code} for this NHS branch surgery"
    if branch_name:
        note += f" ({branch_name.title()})"
    note += "."
    return parent_payload, parent_code, note


def resolve_national_practice_survey_payload(
    code: str,
    nation: str,
    survey_by_code: dict[str, dict[str, Any]],
    branch_parent_by_code: dict[str, dict[str, Any]],
    scotland_hace_by_code: dict[str, dict[str, Any]],
    scotland_hace_manifest_by_code: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], str, str, dict[str, str]]:
    normalized_nation = str(nation or "").strip().lower()
    if normalized_nation == "scotland":
        direct_payload = scotland_hace_by_code.get(code, {})
        if survey_metric(direct_payload, "overallexp") not in ("", None):
            return (
                direct_payload,
                code,
                "",
                {
                    "patient_survey_status": "practice_level_available",
                    "patient_survey_level": "practice",
                    "patient_survey_url": str(direct_payload.get("source_url", "")).strip(),
                    "patient_survey_note": "",
                },
            )
        manifest_entry = scotland_hace_manifest_by_code.get(code, {})
        if manifest_entry.get("status") == "missing_dropdown_option":
            return (
                {},
                code,
                "",
                {
                    "patient_survey_status": "practice_level_missing_in_source",
                    "patient_survey_level": "practice_dashboard",
                    "patient_survey_note": (
                        "Current Health and Care Experience Survey practice dashboard "
                        "did not list this code in its General Practice dropdown."
                    ),
                },
            )
        if manifest_entry.get("status") == "metric_not_found":
            return (
                {},
                code,
                "",
                {
                    "patient_survey_status": "practice_metric_missing_in_source",
                    "patient_survey_level": "practice_dashboard",
                    "patient_survey_note": (
                        "Current Health and Care Experience Survey practice dashboard "
                        "listed this practice, but the overall-care metric could not be read."
                    ),
                },
            )
        return {}, code, "", {}
    payload, code_used, note = resolve_gp_patient_survey_payload(code, survey_by_code, branch_parent_by_code)
    return payload, code_used, note, {}


def parse_google_maps_coordinates(url: str) -> tuple[float, float] | None:
    if not url:
        return None
    for pattern in (
        r"!3d(-?\d+(?:\.\d+)?)!4d(-?\d+(?:\.\d+)?)",
        r"@(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)",
    ):
        match = re.search(pattern, url)
        if not match:
            continue
        try:
            return float(match.group(1)), float(match.group(2))
        except ValueError:
            continue
    return None


def coordinates_plausible_for_nation(coords: tuple[float, float] | None, nation: str) -> bool:
    if coords is None:
        return False
    lat, lon = coords
    nation_key = str(nation or "").strip().lower()
    if nation_key == "england":
        return 49.8 <= lat <= 55.9 and -6.6 <= lon <= 2.2
    if nation_key == "scotland":
        return 54.5 <= lat <= 61.5 and -8.0 <= lon <= -0.3
    if nation_key == "wales":
        return 51.2 <= lat <= 53.7 and -5.8 <= lon <= -2.3
    if nation_key == "northern_ireland":
        return 54.0 <= lat <= 55.4 and -8.4 <= lon <= -5.2
    return True


def percent_or_blank(value: Any) -> float | str:
    if value in ("", None):
        return ""
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return ""
    if numeric <= 0:
        return ""
    if numeric <= 1:
        numeric *= 100
    return round(numeric, 2)


def int_or_blank(value: Any) -> int | str:
    if value in ("", None):
        return ""
    try:
        return int(round(float(str(value).replace(",", ""))))
    except (TypeError, ValueError):
        return ""


def national_survey_metadata(nation: Any) -> dict[str, str]:
    normalized = str(nation or "").strip().lower()
    return dict(SURVEY_METADATA_BY_NATION.get(normalized, {}))


def load_national_input_index(path: Path = NATIONAL_PRACTICES_INPUT_CSV) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        code = str(row.get("canonical_code", "")).strip()
        if not code:
            continue
        enriched = dict(row)
        for key, value in national_survey_metadata(row.get("nation")).items():
            if str(enriched.get(key, "")).strip():
                continue
            enriched[key] = value
        indexed[code] = enriched
    return indexed


def detect_gpps_csv_schema(fieldnames: list[str]) -> tuple[str, str, str] | None:
    code_col = ""
    for candidate in ("ad_practicecode", "Practice_Code", "Practice_code"):
        if candidate in fieldnames:
            code_col = candidate
            break
    if not code_col:
        return None
    name_col = "ad_practicename" if "ad_practicename" in fieldnames else "Practice_Name"
    if "overallexp.pcteval" in fieldnames:
        return code_col, name_col, "overallexp.pcteval"
    if "Q28_12pct" in fieldnames:
        return code_col, name_col, "Q28_12pct"
    return None


def gpps_year_from_filename(path: Path) -> int:
    match = re.search(r"(20\d{2})", path.name)
    return int(match.group(1)) if match else 0


def latest_gpps_csv_candidates() -> list[Path]:
    candidates = [
        GPPS_DOWNLOADS_DIR / "archive-from-repo" / "GPPS_2025_Practice_data.csv",
        GPPS_DOWNLOADS_DIR / "archive-from-repo" / "GPPS_2024_Practice_data.csv",
    ]
    for pattern in ("*.csv", "archive-from-repo/*.csv"):
        candidates.extend(sorted(GPPS_DOWNLOADS_DIR.glob(pattern)))
    unique_existing: dict[str, Path] = {}
    for path in candidates:
        if path.exists():
            unique_existing[str(path)] = path
    return sorted(unique_existing.values(), key=lambda path: (gpps_year_from_filename(path), path.name), reverse=True)


def load_latest_gpps_csv_index() -> dict[str, dict[str, Any]]:
    for path in latest_gpps_csv_candidates():
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            schema = detect_gpps_csv_schema(reader.fieldnames or [])
            if not schema:
                continue
            code_col, name_col, overall_col = schema
            survey_by_code: dict[str, dict[str, Any]] = {}
            for row in reader:
                code = str(row.get(code_col, "")).strip().upper()
                if not code:
                    continue
                overall = percent_or_blank(row.get(overall_col))
                completion_rate = percent_or_blank(row.get("resprate"))
                survey_by_code[code] = {
                    "canonical_code": code,
                    "practice_name_gpps": str(row.get(name_col, "")).strip(),
                    "gpps_url": f"https://www.gp-patient.co.uk/patientexperience/results?code={code}",
                    "surveys_sent_out": int_or_blank(row.get("distributed")),
                    "surveys_sent_back": int_or_blank(row.get("received")),
                    "completion_rate_percent": completion_rate,
                    "key_questions": {
                        "overallexp": {
                            "practice_percent": overall,
                        }
                    },
                }
            if survey_by_code:
                return survey_by_code
    return {}


def load_existing_national_supplemental_script_index(
    path: Path = OUTPUT_DIR / NATIONAL_SUPPLEMENTAL_SCRIPT_NAME,
) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    prefix = "window.NATIONAL_PRACTICE_SUPPLEMENTALS="
    if not text.startswith(prefix):
        return {}
    payload = text[len(prefix):]
    split_marker = ";\nwindow.NATIONAL_PRACTICE_SUPPLEMENTALS_COUNT="
    if split_marker not in payload:
        split_marker = ";window.NATIONAL_PRACTICE_SUPPLEMENTALS_COUNT="
    payload = payload.split(split_marker, 1)[0].strip()
    try:
        rows = json.loads(payload)
    except json.JSONDecodeError:
        return {}
    if not isinstance(rows, list):
        return {}
    index: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        code = str(row.get("code") or "").strip().upper()
        if code:
            index[code] = row
    return index


def merge_existing_supplemental_survey_fields(
    row: dict[str, Any],
    existing_row: dict[str, Any] | None,
) -> dict[str, Any]:
    if not existing_row:
        return row
    merged = dict(row)
    fallback_fields = (
        "survey_overall_good_percent",
        "survey_overall_good_ics_percent",
        "survey_overall_good_national_percent",
        "survey_completion_rate_percent",
        "survey_sent_out",
        "survey_sent_back",
        "number_of_responses",
        "responses_for_overall_question",
        "gp_patient_survey_2025_url",
        "gp_patient_survey_code_used",
        "gp_patient_survey_resolution_note",
        "patient_survey_name",
        "patient_survey_status",
        "patient_survey_level",
        "patient_survey_url",
        "patient_survey_note",
    )
    for field in fallback_fields:
        if str(merged.get(field, "")).strip():
            continue
        fallback_value = existing_row.get(field, "")
        if str(fallback_value).strip():
            merged[field] = fallback_value
    return merged


def build_national_map_supplementals(
    national_results_path: Path = NATIONAL_GOOGLE_REVIEW_RESULTS_JSON,
    national_input_csv: Path = NATIONAL_PRACTICES_INPUT_CSV,
) -> list[dict[str, Any]]:
    if not national_results_path.exists():
        return []
    try:
        results = json.loads(national_results_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if not isinstance(results, list):
        return []

    input_by_code = load_national_input_index(national_input_csv)
    results_by_code: dict[str, dict[str, Any]] = {}
    for result in results:
        if not isinstance(result, dict):
            continue
        code = str(result.get("canonical_code", "")).strip()
        if not code:
            continue
        results_by_code[code] = result

    survey_by_code = load_latest_gpps_csv_index()
    if not survey_by_code:
        survey_by_code = load_gp_patient_survey_index()
    cqc_by_code = load_cqc_gp_location_index()
    branch_parent_by_code = load_gp_patient_survey_branch_parent_index()
    scotland_hace_by_code, scotland_hace_manifest_by_code = load_scotland_hace_index()
    existing_supplementals_by_code = load_existing_national_supplemental_script_index()
    supplementals: list[dict[str, Any]] = []

    for code, source_row in input_by_code.items():
        result = results_by_code.get(code, {})
        existing_row = existing_supplementals_by_code.get(code)
        survey_metadata = national_survey_metadata(source_row.get("nation"))
        for key in ("patient_survey_name", "patient_survey_status", "patient_survey_level", "patient_survey_url", "patient_survey_note"):
            value = str(source_row.get(key, "")).strip()
            if value:
                survey_metadata[key] = value
        survey_payload, survey_code_used, survey_resolution_note, survey_overrides = resolve_national_practice_survey_payload(
            code,
            str(source_row.get("nation", "")).strip(),
            survey_by_code,
            branch_parent_by_code,
            scotland_hace_by_code,
            scotland_hace_manifest_by_code,
        )
        for key, value in survey_overrides.items():
            if str(value).strip():
                survey_metadata[key] = str(value).strip()

        survey_score = survey_metric(survey_payload, "overallexp")
        if survey_score in ("", None) and existing_row:
            fallback_survey_score = existing_row.get("survey_overall_good_percent", "")
            if str(fallback_survey_score).strip():
                survey_score = fallback_survey_score
        google_score = ""
        google_count = ""
        google_maps_url = ""
        google_source_note = ""

        google_result_usable = isinstance(result, dict) and not any(
            bool(result.get(field))
            for field in (
                "manual_review_required",
                "wrong_place_match",
                "blocked_place_match",
                "sponsored_place_match",
                "sponsored_search_results_only",
            )
        )

        if google_result_usable:
            google_maps_url = str(result.get("google_maps_url", "")).strip()
            page_kind = str(result.get("page_kind", "")).strip()
            if not page_kind:
                if "/place/" in google_maps_url:
                    page_kind = "place"
                elif "/search/" in google_maps_url:
                    page_kind = "search"
                else:
                    page_kind = "other"
            if page_kind == "place":
                google_score = result.get("google_rating", "")
                google_count = result.get("google_review_count", "")
                google_source_note = "National Google Maps quick scan"

        coords = None
        if google_result_usable:
            raw_lat = result.get("latitude")
            raw_lon = result.get("longitude")
            try:
                if raw_lat not in ("", None) and raw_lon not in ("", None):
                    coords = (float(raw_lat), float(raw_lon))
            except (TypeError, ValueError):
                coords = None
            if coords is None:
                coords = parse_google_maps_coordinates(google_maps_url)
        if coords is None:
            raw_lat = source_row.get("latitude")
            raw_lon = source_row.get("longitude")
            try:
                if raw_lat not in ("", None) and raw_lon not in ("", None):
                    coords = (float(raw_lat), float(raw_lon))
            except (TypeError, ValueError):
                coords = None
        nation_key = str(source_row.get("nation") or "").strip()
        if coords is not None and not coordinates_plausible_for_nation(coords, nation_key):
            coords = None
        if coords is None and existing_row:
            try:
                fallback_lat = float(existing_row.get("lat"))
                fallback_lon = float(existing_row.get("lon"))
                coords = (fallback_lat, fallback_lon)
            except (TypeError, ValueError):
                coords = None
        if coords is not None and not coordinates_plausible_for_nation(coords, nation_key):
            coords = None
        if coords is None:
            continue
        if google_score in ("", None) and survey_score in ("", None):
            continue

        cqc = cqc_by_code.get(code, {}) if str(source_row.get("nation", "")).strip().lower() == "england" else {}

        supplemental_row = {
            "code": code,
            "name": str(source_row.get("practice_name") or result.get("practice_name") or result.get("google_maps_title") or code).strip(),
            "lat": round(coords[0], 6),
            "lon": round(coords[1], 6),
            "postcode": str(source_row.get("postcode") or result.get("postcode") or "").strip(),
            "nation": str(source_row.get("nation") or "").strip(),
            "record_scope": "National supplemental",
            "registered_patient_count": source_row.get("registered_patient_count", ""),
            "registered_patient_count_source": source_row.get("registered_patient_count_source", ""),
            "registered_patient_count_source_url": source_row.get("registered_patient_count_source_url", ""),
            "registered_patient_count_snapshot": source_row.get("registered_patient_count_snapshot", ""),
            "google_score": google_score,
            "google_count": google_count,
            "google_source_note": google_source_note,
            "google_url": google_maps_url,
            "google_review_scan_status": str(result.get("scan_status", "") or ""),
            "google_review_has_listing": "true" if (str(result.get("page_kind", "")).strip() == "place" or google_maps_url or result.get("google_maps_title")) else "false",
            "nhs_url": str(source_row.get("nhs_profile_url") or "").strip(),
            "website_url": str(source_row.get("website_url") or "").strip(),
            "ods_org_link": str(source_row.get("ods_org_link") or "").strip(),
            "survey_overall_good_percent": survey_score,
            "survey_overall_good_ics_percent": "",
            "survey_overall_good_national_percent": "",
            "survey_completion_rate_percent": survey_payload.get("completion_rate_percent", ""),
            "survey_sent_out": survey_payload.get("surveys_sent_out", ""),
            "survey_sent_back": survey_payload.get("surveys_sent_back", ""),
            "number_of_responses": survey_payload.get("number_of_responses", ""),
            "responses_for_overall_question": survey_payload.get("responses_for_overall_question", ""),
            "gp_patient_survey_2025_url": survey_payload.get("gpps_url", ""),
            "gp_patient_survey_code_used": survey_code_used,
            "gp_patient_survey_resolution_note": survey_resolution_note,
            "patient_survey_name": str(survey_metadata.get("patient_survey_name") or "").strip(),
            "patient_survey_status": str(survey_metadata.get("patient_survey_status") or "").strip(),
            "patient_survey_level": str(survey_metadata.get("patient_survey_level") or "").strip(),
            "patient_survey_url": str(survey_metadata.get("patient_survey_url") or "").strip(),
            "patient_survey_note": str(survey_metadata.get("patient_survey_note") or "").strip(),
            "accepting_new_patients": source_row.get("accepting_new_patients", False),
            "accepts_out_of_area_registrations": source_row.get("accepts_out_of_area_registrations", False),
            "cqc_overall_rating": str(cqc.get("overall_rating", "")).strip(),
            "cqc_location_url": str(cqc.get("url", "")).strip(),
            "cqc_service_website": str(cqc.get("service_website", "")).strip(),
            "cqc_publication_date": str(cqc.get("publication_date", "")).strip(),
            "cqc_inherited_rating": str(cqc.get("inherited_rating", "")).strip(),
            "cqc_provider_name": str(cqc.get("provider_name", "")).strip(),
            "is_national_supplemental": True,
        }
        supplementals.append(
            merge_existing_supplemental_survey_fields(
                supplemental_row,
                existing_row,
            )
        )

    return sorted(supplementals, key=lambda row: (str(row.get("nation", "")), str(row.get("postcode", "")), str(row.get("name", ""))))


def write_national_supplemental_script(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    path.write_text(
        "\n".join(
            [
                f"window.NATIONAL_PRACTICE_SUPPLEMENTALS={payload};",
                f"window.NATIONAL_PRACTICE_SUPPLEMENTALS_COUNT={len(rows)};",
                "",
            ]
        ),
        encoding="utf-8",
    )


def display_nation_name(nation: str) -> str:
    normalized = str(nation or "").strip().lower()
    if normalized == "england":
        return "England"
    if normalized == "scotland":
        return "Scotland"
    if normalized == "wales":
        return "Wales"
    if normalized == "northern_ireland":
        return "Northern Ireland"
    return normalized.replace("_", " ").title() if normalized else "Unknown"


def source_label_for_patient_count(value: str) -> str:
    mapping = {
        "nhs_monthly_direct": "NHS England monthly direct",
        "nhs_england_patients_registered_at_a_gp_practice": "NHS England practice counts",
        "nhs_scotland_gp_practice_contact_details_and_list_sizes": "NHS Scotland list sizes",
        "statswales_hlth0426": "StatsWales HLTH0426",
        "opendatani_gp_practice_reference_file": "OpenDataNI GP reference",
    }
    normalized = str(value or "").strip()
    return mapping.get(normalized, normalized.replace("_", " ").title() if normalized else "Unknown")


def survey_status_label(value: str) -> str:
    mapping = {
        "practice_level_missing_in_source": "missing in current source",
        "practice_metric_missing_in_source": "metric missing in source",
        "equivalent_identified_not_yet_wired": "equivalent identified, not wired",
        "discontinued": "discontinued",
    }
    normalized = str(value or "").strip()
    return mapping.get(normalized, normalized.replace("_", " ") if normalized else "Unknown")


def survey_short_label(value: str) -> str:
    normalized = str(value or "").strip()
    mapping = {
        "Health and Care Experience Survey": "HACE",
        "GP Patient Survey": "GPPS",
    }
    return mapping.get(normalized, normalized or "GPPS")


def survey_missing_display(label: str, status: str) -> str:
    normalized_status = str(status or "").strip()
    if normalized_status == "equivalent_identified_not_yet_wired":
        return f"{label}: source identified, practice-level feed not yet wired"
    if normalized_status == "practice_level_missing_in_source":
        return f"{label}: not listed in current practice dashboard"
    if normalized_status == "practice_metric_missing_in_source":
        return f"{label}: listed, but metric missing"
    if normalized_status == "discontinued":
        return f"{label}: historic/discontinued"
    return f"{label}: ?"


def google_missing_display(has_listing: Any, scan_status: Any) -> str:
    status = str(scan_status or "").strip()
    listing = str(has_listing or "").strip().lower() == "true"
    if status == "ok_no_review_panel":
        return "Google: listing found, no review panel"
    if status == "no_rating_found":
        return "Google: listing found, no rating shown"
    if status in {"sponsored_place_match", "sponsored_search_results_only", "wrong_place_match", "manual_review_search_result_only"}:
        return "Google: listing/search result needs manual review"
    if status == "skipped_review_count_threshold":
        return "Google: listing found, review scan skipped"
    if listing:
        return "Google: listing found, no usable score"
    return "Google: no usable listing found"


def deprivation_status_label(value: str) -> str:
    mapping = {
        "unsupported_nation": "unsupported nation",
        "matched_polygon_no_deprivation_index": "polygon matched, no deprivation index",
        "no_polygon_match": "no polygon match",
    }
    normalized = str(value or "").strip()
    return mapping.get(normalized, normalized.replace("_", " ") if normalized else "Unknown")


def html_counter_summary(counter: Counter[str]) -> str:
    if not counter:
        return "none"
    parts = []
    for label, count in sorted(counter.items(), key=lambda item: (-item[1], item[0])):
        parts.append(f"{html.escape(label)} {count:,}")
    return " · ".join(parts)


def nhs_registration_url(nhs_profile_url: str) -> str:
    normalized = str(nhs_profile_url or "").strip().rstrip("/")
    if not normalized:
        return ""
    return f"{normalized}/how-to-register"


def short_street_address(value: str) -> str:
    parts = [part.strip() for part in str(value or "").split(",") if part.strip()]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    first, second = parts[0], parts[1]
    street_pattern = re.compile(r"\b(road|rd|street|st|avenue|ave|lane|ln|close|drive|dr|way|court|crescent|place|walk|grove|park|gardens|square|terrace|boulevard|hill|rise|view)\b", re.I)
    if street_pattern.search(first):
        return first
    if street_pattern.search(second):
        return f"{first}, {second}"
    return first


def load_cqc_gp_location_index(path: Path = CQC_GP_RATINGS_JSON) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    by_code: dict[str, dict[str, Any]] = {}
    if isinstance(payload, dict):
        for code, item in payload.items():
            normalized_code = str(code or "").strip()
            if not normalized_code or not isinstance(item, dict):
                continue
            by_code[normalized_code] = item
        return by_code
    if not isinstance(payload, list):
        return {}
    for item in payload:
        if not isinstance(item, dict):
            continue
        code = str(item.get("ods_code", "")).strip()
        if not code:
            continue
        by_code[code] = item
    return by_code


def load_registration_flags_by_code(path: Path = ENGLAND_GP_REGISTRATION_FLAGS_BY_PRACTICE_JSON) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(payload, dict):
        return {}
    by_code: dict[str, dict[str, Any]] = {}
    for code, item in payload.items():
        normalized_code = str(code or "").strip().upper()
        if not normalized_code or not isinstance(item, dict):
            continue
        by_code[normalized_code] = item
    return by_code


def enrich_rows_with_cqc(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cqc_by_code = load_cqc_gp_location_index()
    if not cqc_by_code:
        return rows
    enriched_rows: list[dict[str, Any]] = []
    for row in rows:
        nation = str(row.get("nation") or "england").strip().lower()
        if nation != "england":
            enriched_rows.append(row)
            continue
        code = str(row.get("canonical_code") or row.get("code") or "").strip()
        cqc = cqc_by_code.get(code, {})
        if not cqc:
            enriched_rows.append(row)
            continue
        enriched = dict(row)
        enriched["cqc_overall_rating"] = str(cqc.get("overall_rating", "")).strip()
        enriched["cqc_location_url"] = str(cqc.get("url", "")).strip()
        enriched["cqc_service_website"] = str(cqc.get("service_website", "")).strip()
        enriched["cqc_publication_date"] = str(cqc.get("publication_date", "")).strip()
        enriched["cqc_inherited_rating"] = str(cqc.get("inherited_rating", "")).strip()
        enriched["cqc_provider_name"] = str(cqc.get("provider_name", "")).strip()
        enriched_rows.append(enriched)
    return enriched_rows


def enrich_rows_with_patient_count_candidates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    registered_patient_counts = load_registered_patient_index()
    if not registered_patient_counts:
        return rows
    enriched_rows: list[dict[str, Any]] = []
    for row in rows:
        enriched = dict(row)
        direct_count = enriched.get("registered_patient_count", "")
        if direct_count not in ("", None):
            enriched_rows.append(enriched)
            continue
        code = str(enriched.get("canonical_code") or enriched.get("code") or "").strip()
        candidate = registered_patient_count_candidate(code, registered_patient_counts)
        if candidate:
            enriched["registered_patient_count_candidate"] = candidate["count"]
            enriched["registered_patient_count_candidate_code"] = candidate["code"]
            enriched["registered_patient_count_candidate_source"] = candidate["source"]
            enriched["registered_patient_count_candidate_confidence"] = candidate["confidence"]
        enriched_rows.append(enriched)
    return enriched_rows


def build_client_map_row(row: dict[str, Any]) -> dict[str, Any]:
    survey_label = survey_short_label(str(row.get("patient_survey_name") or "").strip())
    survey_status = str(row.get("patient_survey_status") or "").strip()
    survey_note = str(row.get("patient_survey_note") or "").strip()
    if str(row.get("nation") or "").strip().lower() == "england" and survey_status == "practice_level_available":
        survey_note = ""
    direct_survey_url = str(row.get("gp_patient_survey_2025_url") or "").strip()
    fallback_survey_url = str(row.get("patient_survey_url") or "").strip()
    survey_link_url = direct_survey_url or fallback_survey_url
    survey_link_label = ""
    if survey_link_url:
        survey_link_label = f"{survey_label} page" if direct_survey_url else f"{survey_label} source"

    return {
        "code": row.get("code", ""),
        "name": row.get("name", ""),
        "lat": row.get("lat", ""),
        "lon": row.get("lon", ""),
        "postcode": row.get("postcode", ""),
        "short_address": short_street_address(str(row.get("street_address", ""))),
        "nation": row.get("nation", ""),
        "gtd": row.get("gtd", False),
        "management_company": row.get("management_company", ""),
        "affiliated_group": row.get("affiliated_group", ""),
        "google_score": row.get("google_score", ""),
        "google_count": row.get("google_count", ""),
        "google_review_span_years": row.get("google_review_span_years", ""),
        "google_reviews_per_year": row.get("google_reviews_per_year", ""),
        "google_text_url": row.get("google_text_file", ""),
        "google_maps_url": row.get("google_url", "") or row.get("google_maps_url", "") or row.get("google_review_source_url", ""),
        "google_missing_text": google_missing_display(row.get("google_review_has_listing", ""), row.get("google_review_scan_status", "")),
        "nhs_url": row.get("nhs_url", ""),
        "nhs_register_url": nhs_registration_url(str(row.get("nhs_url", ""))),
        "website_url": row.get("website_url", ""),
        "ods_org_link": row.get("ods_org_link", ""),
        "accepting_new_patients": row.get("accepting_new_patients", False),
        "accepts_out_of_area_registrations": row.get("accepts_out_of_area_registrations", False),
        "gtd_url": row.get("gtd_url", ""),
        "gtd_takeover_date": row.get("gtd_takeover_date", ""),
        "gtd_takeover_precision": row.get("gtd_takeover_precision", ""),
        "gtd_takeover_note": row.get("gtd_takeover_note", ""),
        "gtd_takeover_source_label": row.get("gtd_takeover_source_label", ""),
        "gtd_takeover_source_url": row.get("gtd_takeover_source_url", ""),
        "survey_overall_good_percent": row.get("survey_overall_good_percent", ""),
        "survey_overall_good_ics_percent": row.get("survey_overall_good_ics_percent", ""),
        "survey_completion_rate_percent": row.get("survey_completion_rate_percent", ""),
        "survey_sent_out": row.get("survey_sent_out", ""),
        "survey_sent_back": row.get("survey_sent_back", ""),
        "number_of_responses": row.get("number_of_responses", ""),
        "responses_for_overall_question": row.get("responses_for_overall_question", ""),
        "survey_label": survey_label,
        "survey_missing_text": survey_missing_display(survey_label, survey_status),
        "survey_note": survey_note,
        "survey_link_url": survey_link_url,
        "survey_link_label": survey_link_label,
        "survey_resolution_note": str(row.get("gp_patient_survey_resolution_note") or "").strip(),
        "cqc_overall_rating": row.get("cqc_overall_rating", ""),
        "cqc_location_url": row.get("cqc_location_url", ""),
        "cqc_service_website": row.get("cqc_service_website", ""),
        "cqc_publication_date": row.get("cqc_publication_date", ""),
        "cqc_inherited_rating": row.get("cqc_inherited_rating", ""),
        "cqc_provider_name": row.get("cqc_provider_name", ""),
        "registered_patient_count": row.get("registered_patient_count", ""),
        "registered_patient_count_candidate": row.get("registered_patient_count_candidate", ""),
        "registered_patient_count_candidate_code": row.get("registered_patient_count_candidate_code", ""),
        "registered_patient_count_candidate_source": row.get("registered_patient_count_candidate_source", ""),
        "registered_patient_count_effective": row.get("registered_patient_count", "") or row.get("registered_patient_count_candidate", ""),
        "registered_patient_count_effective_source": row.get("registered_patient_count_source", "") or row.get("registered_patient_count_candidate_source", ""),
        "patient_change_per_year": row.get("patient_change_per_year", ""),
        "patient_change_start_year": row.get("patient_change_start_year", ""),
        "patient_change_end_year": row.get("patient_change_end_year", ""),
    }


def has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    return True


def positive_number(value: Any) -> bool:
    try:
        if value in ("", None):
            return False
        return float(value) > 0
    except (TypeError, ValueError):
        return False


def numeric_value(value: Any) -> float | None:
    try:
        if value in ("", None):
            return None
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    return numeric if math.isfinite(numeric) else None


def top_bottom_fifth_codes(
    scored_rows: list[tuple[str, float]],
) -> tuple[list[str], list[str]]:
    if not scored_rows:
        return [], []
    ordered = sorted(scored_rows, key=lambda item: (item[1], item[0]))
    band_size = max(1, len(ordered) // 5)
    bottom = [code for code, _score in ordered[:band_size]]
    top = [code for code, _score in ordered[-band_size:]]
    return bottom, top


def build_composite_region_definitions(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped_rows: list[dict[str, Any]] = []
    seen_codes: set[str] = set()
    for row in rows:
        code = str(row.get("code", "")).strip()
        lat = numeric_value(row.get("lat"))
        lon = numeric_value(row.get("lon"))
        if not code or code in seen_codes or lat is None or lon is None:
            continue
        deduped_rows.append(
            {
                "code": code,
                "lat": lat,
                "lon": lon,
                "registered_patient_count": numeric_value(row.get("registered_patient_count")) or 0.0,
            }
        )
        seen_codes.add(code)

    practice_density_scores: list[tuple[str, float]] = []
    patient_density_scores: list[tuple[str, float]] = []
    for row in deduped_rows:
        nearby_practices = 0
        for other in deduped_rows:
            if other["code"] == row["code"]:
                continue
            if miles_between(row["lat"], row["lon"], other["lat"], other["lon"]) > COMPOSITE_REGION_RADIUS_MILES:
                continue
            nearby_practices += 1
        practice_density_scores.append((row["code"], float(nearby_practices)))
        if row["registered_patient_count"] > 0:
            patient_density_scores.append((row["code"], float(row["registered_patient_count"])))

    sparse_codes, dense_codes = top_bottom_fifth_codes(practice_density_scores)
    low_patient_density_codes, high_patient_density_codes = top_bottom_fifth_codes(patient_density_scores)

    return [
        {
            "label": "Rural / Sparse",
            "kind": "practice_density",
            "accent": "#466c5c",
            "codes": sparse_codes,
            "note": f"Bottom fifth by nearby-practice count within {COMPOSITE_REGION_RADIUS_MILES:g} miles.",
        },
        {
            "label": "Urban / Dense",
            "kind": "practice_density",
            "accent": "#a25b2a",
            "codes": dense_codes,
            "note": f"Top fifth by nearby-practice count within {COMPOSITE_REGION_RADIUS_MILES:g} miles.",
        },
        {
            "label": "Low list size",
            "kind": "patient_density",
            "accent": "#4b6cb7",
            "codes": low_patient_density_codes,
            "note": "Bottom fifth by registered patient count per practice.",
        },
        {
            "label": "High list size",
            "kind": "patient_density",
            "accent": "#9b3d5d",
            "codes": high_patient_density_codes,
            "note": "Top fifth by registered patient count per practice.",
        },
    ]


def load_composite_region_definitions(
    path: Path = COMPOSITE_REGION_DEFINITIONS_JSON,
) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return payload if isinstance(payload, list) else []


def write_composite_region_definitions(
    rows: list[dict[str, Any]],
    path: Path = COMPOSITE_REGION_DEFINITIONS_JSON,
) -> list[dict[str, Any]]:
    definitions = build_composite_region_definitions(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(definitions, indent=2), encoding="utf-8")
    return definitions


def build_data_pool_report_html(
    core_rows: list[dict[str, Any]],
    national_rows: list[dict[str, Any]],
    deprivation_lookup: dict[str, dict[str, Any]],
) -> str:
    combined_by_code: dict[str, dict[str, Any]] = {}
    for row in national_rows:
        code = str(row.get("code", "")).strip()
        if code:
            combined_by_code[code] = row
    for row in core_rows:
        code = str(row.get("code", "")).strip()
        if code:
            combined_by_code[code] = row
    combined_rows = list(combined_by_code.values())
    total_practices = len(combined_rows)
    total_nations = len({str(row.get("nation", "")).strip().lower() for row in combined_rows if str(row.get("nation", "")).strip()})
    cards: list[str] = []
    for nation in NATION_ORDER:
        nation_rows = [row for row in combined_rows if str(row.get("nation", "")).strip().lower() == nation]
        if not nation_rows:
            continue
        practice_total = len(nation_rows)
        with_coords = sum(1 for row in nation_rows if numeric_value(row.get("lat")) is not None and numeric_value(row.get("lon")) is not None)
        with_postcode = sum(1 for row in nation_rows if has_value(row.get("postcode")))
        scope_counts = Counter(str(row.get("record_scope") or "Unknown") for row in nation_rows)

        google_rows = [row for row in nation_rows if positive_number(row.get("google_count")) and has_value(row.get("google_score"))]
        google_source_counts = Counter(
            str(row.get("google_source_note") or "Repo review dataset").strip()
            for row in google_rows
        )

        survey_overall_rows = [row for row in nation_rows if has_value(row.get("survey_overall_good_percent"))]
        survey_participation_rows = [row for row in nation_rows if has_value(row.get("survey_completion_rate_percent"))]
        survey_source_counts = Counter(
            str(row.get("patient_survey_name") or "Unknown survey").strip()
            for row in nation_rows
            if has_value(row.get("survey_overall_good_percent")) or has_value(row.get("survey_completion_rate_percent"))
        )
        survey_issue_counts = Counter(
            survey_status_label(str(row.get("patient_survey_status") or "").strip())
            for row in nation_rows
            if str(row.get("patient_survey_status") or "").strip() not in ("", "practice_level_available")
        )

        patient_rows = [row for row in nation_rows if positive_number(row.get("registered_patient_count"))]
        patient_total = 0
        for row in patient_rows:
            try:
                patient_total += int(float(row.get("registered_patient_count")))
            except (TypeError, ValueError):
                continue
        patient_source_counts = Counter(
            source_label_for_patient_count(str(row.get("registered_patient_count_source") or ""))
            for row in patient_rows
        )

        cqc_rows = [row for row in nation_rows if has_value(row.get("cqc_overall_rating"))]
        cqc_rating_counts = Counter(
            str(row.get("cqc_overall_rating") or "").strip()
            for row in cqc_rows
            if str(row.get("cqc_overall_rating") or "").strip()
        )
        lookup_rows = [deprivation_lookup.get(str(row.get("code", "")).strip()) for row in nation_rows]
        lookup_rows = [row for row in lookup_rows if isinstance(row, dict)]
        deprivation_rows = [row for row in lookup_rows if has_value(row.get("imd_decile"))]
        deprivation_issue_counts = Counter(
            deprivation_status_label(str(row.get("lookup_status") or "").strip())
            for row in lookup_rows
            if str(row.get("lookup_status") or "").strip() not in ("", "matched_imd_2025_england")
        )
        missing_lookup_count = practice_total - len(lookup_rows)
        if missing_lookup_count > 0:
            deprivation_issue_counts["no cached lookup"] += missing_lookup_count

        items = [
            (
                "Practice info",
                f"{practice_total:,} records · {with_coords:,} with coordinates · {with_postcode:,} with postcode · {html_counter_summary(scope_counts)}",
            ),
            (
                "Google",
                f"{len(google_rows):,} with usable rating/count · {practice_total - len(google_rows):,} missing or unusable · {html_counter_summary(google_source_counts)}",
            ),
            (
                "Surveys",
                f"{len(survey_overall_rows):,} with overall score · {len(survey_participation_rows):,} with participation/completion · {html_counter_summary(survey_source_counts)}",
            ),
            (
                "Survey issues",
                html_counter_summary(survey_issue_counts),
            ),
            (
                "Patient counts",
                f"{len(patient_rows):,} with counts covering {patient_total:,} patients · {html_counter_summary(patient_source_counts)}",
            ),
            (
                "Deprivation",
                f"{len(deprivation_rows):,} with usable decile · {html_counter_summary(deprivation_issue_counts)}",
            ),
        ]
        if nation == "england":
            items.insert(
                5,
                (
                    "CQC",
                    f"{len(cqc_rows):,} with rating · {practice_total - len(cqc_rows):,} without match · {html_counter_summary(cqc_rating_counts)}",
                ),
            )
        item_markup = "".join(
            f"<li><strong>{html.escape(label)}</strong><span>{value}</span></li>"
            for label, value in items
        )
        cards.append(
            "\n".join(
                [
                    '<article class="data-pool-card">',
                    f"  <h3>{html.escape(display_nation_name(nation))}</h3>",
                    f'  <p class="data-pool-kicker">{practice_total:,} practices currently loaded into this page</p>',
                    f'  <ul class="data-pool-list">{item_markup}</ul>',
                    "</article>",
                ]
            )
        )

    summary_text = (
        f"{total_practices:,} unique practices across {total_nations} nations are currently loaded into this page. "
        "Counts below reflect what this build can actually use right now, including missing data and lookup failure states."
    )
    footnote = (
        "Survey participation means GP Patient Survey completion in England and HACE response rate in Scotland. "
        "National deprivation is currently English IMD only: Wales can retain polygon matches without a comparable index, "
        "while Scotland and Northern Ireland remain unsupported until equivalent sources are wired."
    )
    return "\n".join(
        [
            '<details class="panel comparison-panel data-pool-panel">',
            '  <summary>',
            '    <span>Data Coverage by Nation</span>',
            '    <small>Expand for source coverage, gaps, and lookup states</small>',
            '  </summary>',
            f'  <p class="chart-note">{html.escape(summary_text)}</p>',
            '  <div class="data-pool-grid">',
            *cards,
            '  </div>',
            f'  <p class="chart-note data-pool-footnote">{html.escape(footnote)}</p>',
            '</details>',
        ]
    )


# TODO: Detect and explicitly store/report practice replies (staff responses misparsed as patient reviews)
# as not really reviews. Use a reference file (e.g. datasets/reviews-analysis/practice_replies.json)
# to flag known cases; exclude from scores and counts; surface in reports.
def load_google_review_results(path: Path = GOOGLE_REVIEW_RESULTS_JSON) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return payload if isinstance(payload, list) else []


def shift_months(source: date, delta_months: int) -> date:
    month_index = (source.month - 1) + delta_months
    year = source.year + (month_index // 12)
    month = (month_index % 12) + 1
    day = min(source.day, monthrange(year, month)[1])
    return date(year, month, day)


def month_start(value: date) -> date:
    return value.replace(day=1)


def iter_month_starts(start: date, end: date) -> list[date]:
    months: list[date] = []
    current = month_start(start)
    finish = month_start(end)
    while current <= finish:
        months.append(current)
        current = shift_months(current, 1)
    return months


def parse_google_star_label(label: str) -> float | None:
    match = re.search(r"([0-5])\s+stars?", str(label).strip().lower())
    if not match:
        return None
    return float(match.group(1))


def parse_google_relative_review_date(label: str, anchor_date: date) -> date | None:
    cleaned = str(label or "").strip().lower()
    cleaned = re.sub(r"^edited\s+", "", cleaned)
    cleaned = " ".join(cleaned.split())
    if not cleaned:
        return None
    if cleaned == "today":
        return anchor_date
    if cleaned == "yesterday":
        return anchor_date - timedelta(days=1)

    match = re.fullmatch(r"(a|an|\d+)\s+(minute|hour|day|week|month|year)s?\s+ago", cleaned)
    if not match:
        return None

    quantity_label, unit = match.groups()
    quantity = 1 if quantity_label in {"a", "an"} else int(quantity_label)
    if unit in {"minute", "hour"}:
        return anchor_date
    if unit == "day":
        return anchor_date - timedelta(days=quantity)
    if unit == "week":
        return anchor_date - timedelta(weeks=quantity)
    if unit == "month":
        return shift_months(anchor_date, -quantity)
    if unit == "year":
        return shift_months(anchor_date, -(quantity * 12))
    return None


def parse_google_relative_review_precision(label: str) -> str | None:
    """How granular the relative-date phrase is. Used to widen chart bands for year-only labels."""
    cleaned = str(label or "").strip().lower()
    cleaned = re.sub(r"^edited\s+", "", cleaned)
    cleaned = " ".join(cleaned.split())
    if not cleaned:
        return None
    if cleaned in {"today", "yesterday"}:
        return "fine"
    match = re.fullmatch(r"(a|an|\d+)\s+(minute|hour|day|week|month|year)s?\s+ago", cleaned)
    if not match:
        return None
    _quantity_label, unit = match.groups()
    if unit in {"minute", "hour", "day", "week"}:
        return "fine"
    if unit == "month":
        return "month"
    if unit == "year":
        return "year"
    return "fine"


def merge_relative_date_precision(left: str, right: str) -> str:
    order = {"fine": 0, "month": 1, "year": 2}
    return left if order[left] >= order[right] else right


def build_gtd_google_score_timeseries(
    rows: list[dict[str, Any]],
    google_results_path: Path = GOOGLE_REVIEW_RESULTS_JSON,
) -> dict[str, Any]:
    rows = apply_gtd_takeover_metadata(rows)
    anchor_date = date.today()
    if google_results_path.exists():
        anchor_date = date.fromtimestamp(google_results_path.stat().st_mtime)

    gtd_rows = [row for row in rows if str(row.get("gtd_managed", "")).strip().lower() == "true"]
    result_by_code = {
        str(item.get("canonical_code", "")).strip(): item
        for item in load_google_review_results(google_results_path)
        if item.get("canonical_code")
    }

    month_values_by_practice: dict[str, dict[date, float]] = {}
    practice_review_counts: dict[str, int] = {}
    practice_google_counts: dict[str, int | None] = {}
    parsed_review_total = 0
    skipped_review_total = 0
    earliest_month: date | None = None

    for row in gtd_rows:
        code = str(row.get("canonical_code", "")).strip()
        result = result_by_code.get(code, {})
        reviews_payload = result.get("recent_reviews") or []
        reviews_by_month: dict[date, list[float]] = {}

        for review in reviews_payload:
            if not isinstance(review, dict):
                skipped_review_total += 1
                continue
            rating = parse_google_star_label(str(review.get("star_label", "")))
            review_date = parse_google_relative_review_date(str(review.get("relative_date", "")), anchor_date)
            if rating is None or review_date is None:
                skipped_review_total += 1
                continue
            bucket = month_start(review_date)
            reviews_by_month.setdefault(bucket, []).append(rating)
            parsed_review_total += 1
            if earliest_month is None or bucket < earliest_month:
                earliest_month = bucket

        practice_review_counts[code] = sum(len(values) for values in reviews_by_month.values())
        google_review_count = result.get("google_review_count")
        try:
            practice_google_counts[code] = int(google_review_count)
        except (TypeError, ValueError):
            practice_google_counts[code] = None
        if not reviews_by_month:
            continue

        cumulative_total = 0.0
        cumulative_count = 0
        cumulative_by_month: dict[date, float] = {}
        for bucket in sorted(reviews_by_month):
            values = reviews_by_month[bucket]
            cumulative_total += sum(values)
            cumulative_count += len(values)
            cumulative_by_month[bucket] = round(cumulative_total / cumulative_count, 4)
        month_values_by_practice[code] = cumulative_by_month

    if earliest_month is None:
        return {
            "anchor_date": anchor_date.isoformat(),
            "months": [],
            "practice_series": [],
            "average_series": [],
            "gtd_practice_count": len(gtd_rows),
            "practices_with_review_history": 0,
            "parsed_review_count": 0,
            "skipped_review_count": skipped_review_total,
        }

    timeline = iter_month_starts(earliest_month, month_start(anchor_date))
    practice_series = []
    for row in gtd_rows:
        code = str(row.get("canonical_code", "")).strip()
        cumulative_by_month = month_values_by_practice.get(code)
        if not cumulative_by_month:
            continue
        last_value: float | None = None
        points: list[float | None] = []
        for bucket in timeline:
            if bucket in cumulative_by_month:
                last_value = cumulative_by_month[bucket]
            points.append(last_value)
        practice_series.append(
            {
                "code": code,
                "name": row.get("practice_name", code),
                "points": points,
                "parsed_review_count": practice_review_counts.get(code, 0),
                "google_review_count": practice_google_counts.get(code),
                "takeover_date": row.get("gtd_takeover_date", ""),
                "takeover_precision": row.get("gtd_takeover_date_precision", ""),
                "takeover_note": row.get("gtd_takeover_note", ""),
                "takeover_source_label": row.get("gtd_takeover_source_label", ""),
                "takeover_source_url": row.get("gtd_takeover_source_url", ""),
            }
        )

    average_series: list[float | None] = []
    for index in range(len(timeline)):
        values = [series["points"][index] for series in practice_series if series["points"][index] is not None]
        average_series.append(round(sum(values) / len(values), 4) if values else None)

    missing_practices = [
        {
            "code": str(row.get("canonical_code", "")).strip(),
            "name": row.get("practice_name", ""),
            "google_review_count": practice_google_counts.get(str(row.get("canonical_code", "")).strip()),
        }
        for row in gtd_rows
        if str(row.get("canonical_code", "")).strip() not in month_values_by_practice
    ]

    return {
        "anchor_date": anchor_date.isoformat(),
        "months": [bucket.isoformat() for bucket in timeline],
        "practice_series": practice_series,
        "average_series": average_series,
        "gtd_practice_count": len(gtd_rows),
        "practices_with_review_history": len(practice_series),
        "parsed_review_count": parsed_review_total,
        "skipped_review_count": skipped_review_total,
        "missing_practices": missing_practices,
    }


def build_manchester_google_rating_timeseries_all_practices(
    rows: list[dict[str, Any]],
    google_results_path: Path = GOOGLE_REVIEW_RESULTS_JSON,
) -> dict[str, Any]:
    """Reconstructed cumulative Google rating by month for every Manchester-dataset practice with review history."""
    rows = apply_gtd_takeover_metadata(rows)
    anchor_date = date.today()
    if google_results_path.exists():
        anchor_date = date.fromtimestamp(google_results_path.stat().st_mtime)

    dataset_rows = [row for row in rows if str(row.get("canonical_code", "")).strip()]
    result_by_code = {
        str(item.get("canonical_code", "")).strip(): item
        for item in load_google_review_results(google_results_path)
        if item.get("canonical_code")
    }

    month_values_by_practice: dict[str, dict[date, float]] = {}
    month_precision_by_practice: dict[str, dict[date, str]] = {}
    practice_review_counts: dict[str, int] = {}
    practice_google_counts: dict[str, int | None] = {}
    parsed_review_total = 0
    skipped_review_total = 0
    earliest_month: date | None = None

    for row in dataset_rows:
        code = str(row.get("canonical_code", "")).strip()
        result = result_by_code.get(code, {})
        reviews_payload = result.get("recent_reviews") or []
        reviews_by_month: dict[date, list[float]] = {}
        precision_by_bucket: dict[date, str] = {}

        for review in reviews_payload:
            if not isinstance(review, dict):
                skipped_review_total += 1
                continue
            rating = parse_google_star_label(str(review.get("star_label", "")))
            rel = str(review.get("relative_date", ""))
            review_date = parse_google_relative_review_date(rel, anchor_date)
            if rating is None or review_date is None:
                skipped_review_total += 1
                continue
            bucket = month_start(review_date)
            reviews_by_month.setdefault(bucket, []).append(rating)
            prec = parse_google_relative_review_precision(rel)
            if prec:
                if bucket not in precision_by_bucket:
                    precision_by_bucket[bucket] = prec
                else:
                    precision_by_bucket[bucket] = merge_relative_date_precision(precision_by_bucket[bucket], prec)
            parsed_review_total += 1
            if earliest_month is None or bucket < earliest_month:
                earliest_month = bucket

        practice_review_counts[code] = sum(len(values) for values in reviews_by_month.values())
        google_review_count = result.get("google_review_count")
        try:
            practice_google_counts[code] = int(google_review_count)
        except (TypeError, ValueError):
            practice_google_counts[code] = None
        if not reviews_by_month:
            continue

        cumulative_total = 0.0
        cumulative_count = 0
        cumulative_by_month: dict[date, float] = {}
        for bucket in sorted(reviews_by_month):
            values = reviews_by_month[bucket]
            cumulative_total += sum(values)
            cumulative_count += len(values)
            cumulative_by_month[bucket] = round(cumulative_total / cumulative_count, 4)
        month_values_by_practice[code] = cumulative_by_month
        month_precision_by_practice[code] = precision_by_bucket

    if earliest_month is None:
        return {
            "anchor_date": anchor_date.isoformat(),
            "months": [],
            "practice_series": [],
            "dataset_practice_count": len(dataset_rows),
            "practices_with_review_history": 0,
            "parsed_review_count": 0,
            "skipped_review_count": skipped_review_total,
        }

    timeline = iter_month_starts(earliest_month, month_start(anchor_date))
    practice_series: list[dict[str, Any]] = []
    for row in dataset_rows:
        code = str(row.get("canonical_code", "")).strip()
        cumulative_by_month = month_values_by_practice.get(code)
        if not cumulative_by_month:
            continue
        last_value: float | None = None
        points: list[float | None] = []
        precision_for_timeline: list[str | None] = []
        pmap = month_precision_by_practice.get(code, {})
        for bucket in timeline:
            if bucket in cumulative_by_month:
                last_value = cumulative_by_month[bucket]
            points.append(last_value)
            precision_for_timeline.append(pmap.get(bucket))
        first_finite: float | None = None
        last_finite: float | None = None
        for value in points:
            if value is not None and isinstance(value, (int, float)) and math.isfinite(float(value)):
                if first_finite is None:
                    first_finite = float(value)
                last_finite = float(value)
        delta = round(last_finite - first_finite, 4) if first_finite is not None and last_finite is not None else None
        result_row = result_by_code.get(code, {})
        google_maps_url = (
            str(row.get("google_url", "") or "").strip()
            or str(row.get("google_review_source_url", "") or "").strip()
            or str(result_row.get("google_maps_url", "") or "").strip()
        )
        practice_series.append(
            {
                "code": code,
                "name": row.get("practice_name", code),
                "gtd_managed": bool(str(row.get("gtd_managed", "")).strip().lower() == "true"),
                "google_maps_url": google_maps_url,
                "points": points,
                "bucket_precision": precision_for_timeline,
                "delta": delta,
                "first_value": first_finite,
                "last_value": last_finite,
                "parsed_review_count": practice_review_counts.get(code, 0),
                "google_review_count": practice_google_counts.get(code),
            }
        )

    def _series_sort_key(item: dict[str, Any]) -> tuple:
        d = item.get("delta")
        name = str(item.get("name", "")).lower()
        if d is None:
            return (1, name)
        return (0, -float(d), name)

    practice_series.sort(key=_series_sort_key)

    missing_practices = [
        {
            "code": str(row.get("canonical_code", "")).strip(),
            "name": row.get("practice_name", ""),
            "google_review_count": practice_google_counts.get(str(row.get("canonical_code", "")).strip()),
        }
        for row in dataset_rows
        if str(row.get("canonical_code", "")).strip() not in month_values_by_practice
    ]

    return {
        "anchor_date": anchor_date.isoformat(),
        "months": [bucket.isoformat() for bucket in timeline],
        "practice_series": practice_series,
        "dataset_practice_count": len(dataset_rows),
        "practices_with_review_history": len(practice_series),
        "parsed_review_count": parsed_review_total,
        "skipped_review_count": skipped_review_total,
        "missing_practices": missing_practices,
    }


def build_dataset_google_review_yearly_average(
    rows: list[dict[str, Any]],
    google_results_path: Path = GOOGLE_REVIEW_RESULTS_JSON,
) -> dict[str, Any]:
    anchor_date = date.today()
    if google_results_path.exists():
        anchor_date = date.fromtimestamp(google_results_path.stat().st_mtime)

    result_by_code = {
        str(item.get("canonical_code", "")).strip(): item
        for item in load_google_review_results(google_results_path)
        if item.get("canonical_code")
    }

    year_values_by_practice: dict[str, dict[int, float]] = {}
    parsed_review_total = 0
    skipped_review_total = 0
    earliest_year: int | None = None

    for row in rows:
        code = str(row.get("canonical_code", "")).strip()
        if not code:
            continue
        result = result_by_code.get(code, {})
        reviews_payload = result.get("recent_reviews") or []
        reviews_by_year: dict[int, list[float]] = {}

        for review in reviews_payload:
            if not isinstance(review, dict):
                skipped_review_total += 1
                continue
            rating = parse_google_star_label(str(review.get("star_label", "")))
            review_date = parse_google_relative_review_date(str(review.get("relative_date", "")), anchor_date)
            if rating is None or review_date is None:
                skipped_review_total += 1
                continue
            review_year = review_date.year
            reviews_by_year.setdefault(review_year, []).append(rating)
            parsed_review_total += 1
            if earliest_year is None or review_year < earliest_year:
                earliest_year = review_year

        if not reviews_by_year:
            continue

        cumulative_total = 0.0
        cumulative_count = 0
        cumulative_by_year: dict[int, float] = {}
        for review_year in sorted(reviews_by_year):
            values = reviews_by_year[review_year]
            cumulative_total += sum(values)
            cumulative_count += len(values)
            cumulative_by_year[review_year] = round(cumulative_total / cumulative_count, 4)
        year_values_by_practice[code] = cumulative_by_year

    if earliest_year is None:
        return {
            "anchor_date": anchor_date.isoformat(),
            "years": [],
            "average_series": [],
            "practice_count_series": [],
            "practices_with_review_history": 0,
            "parsed_review_count": 0,
            "skipped_review_count": skipped_review_total,
        }

    years = list(range(earliest_year, anchor_date.year + 1))
    practice_points: dict[str, list[float | None]] = {}
    for code, cumulative_by_year in year_values_by_practice.items():
        last_value: float | None = None
        points: list[float | None] = []
        for year in years:
            if year in cumulative_by_year:
                last_value = cumulative_by_year[year]
            points.append(last_value)
        practice_points[code] = points

    average_series: list[float | None] = []
    practice_count_series: list[int] = []
    for index in range(len(years)):
        values = [
            points[index]
            for points in practice_points.values()
            if points[index] is not None
        ]
        practice_count_series.append(len(values))
        average_series.append(round(sum(values) / len(values), 4) if values else None)

    return {
        "anchor_date": anchor_date.isoformat(),
        "years": [str(year) for year in years],
        "average_series": average_series,
        "practice_count_series": practice_count_series,
        "practices_with_review_history": len(practice_points),
        "parsed_review_count": parsed_review_total,
        "skipped_review_count": skipped_review_total,
    }


def build_google_review_activity_lookup(
    google_results_path: Path = GOOGLE_REVIEW_RESULTS_JSON,
) -> dict[str, dict[str, Any]]:
    anchor_date = date.today()
    if google_results_path.exists():
        anchor_date = date.fromtimestamp(google_results_path.stat().st_mtime)

    review_activity_by_code: dict[str, dict[str, Any]] = {}
    for item in load_google_review_results(google_results_path):
        code = str(item.get("canonical_code", "")).strip()
        if not code:
            continue
        reviews_payload = item.get("recent_reviews") or []
        earliest_review_date: date | None = None
        latest_review_date: date | None = None
        parsed_review_count = 0
        for review in reviews_payload:
            if not isinstance(review, dict):
                continue
            review_date = parse_google_relative_review_date(str(review.get("relative_date", "")), anchor_date)
            if review_date is None:
                continue
            parsed_review_count += 1
            if earliest_review_date is None or review_date < earliest_review_date:
                earliest_review_date = review_date
            if latest_review_date is None or review_date > latest_review_date:
                latest_review_date = review_date
        if earliest_review_date is None:
            continue
        google_review_count = item.get("google_review_count")
        try:
            total_review_count = int(google_review_count)
        except (TypeError, ValueError):
            total_review_count = None
        span_days = max(1, (anchor_date - earliest_review_date).days)
        span_years = round(span_days / 365.25, 2)
        reviews_per_year = None
        if total_review_count is not None:
            reviews_per_year = round(total_review_count / max(span_days / 365.25, 1.0), 1)
        review_activity_by_code[code] = {
            "review_span_years": span_years,
            "reviews_per_year": reviews_per_year,
            "parsed_review_count": parsed_review_count,
            "earliest_review_date": earliest_review_date.isoformat(),
            "latest_review_date": latest_review_date.isoformat() if latest_review_date else "",
        }
    return review_activity_by_code


def build_patient_change_lookup(
    patient_counts_by_year: dict[str, dict[str, int]] | None,
) -> dict[str, dict[str, Any]]:
    if not patient_counts_by_year:
        return {}
    values_by_code: dict[str, list[tuple[int, int]]] = {}
    for year in sorted(patient_counts_by_year.keys(), key=int):
        counts = patient_counts_by_year.get(year) or {}
        year_number = int(year)
        for code, value in counts.items():
            try:
                count = int(value)
            except (TypeError, ValueError):
                continue
            values_by_code.setdefault(str(code).strip(), []).append((year_number, count))
    trend_by_code: dict[str, dict[str, Any]] = {}
    for code, points in values_by_code.items():
        if len(points) < 2:
            continue
        start_year, start_count = points[0]
        end_year, end_count = points[-1]
        year_span = end_year - start_year
        if year_span <= 0:
            continue
        annual_change = (end_count - start_count) / year_span
        trend_by_code[code] = {
            "patient_change_per_year": round(annual_change, 1),
            "patient_change_start_year": start_year,
            "patient_change_end_year": end_year,
            "patient_change_start_count": start_count,
            "patient_change_end_count": end_count,
        }
    return trend_by_code


def load_gtd_gpps_timeseries() -> dict[str, Any]:
    """Load GPPS historical subset for GTD practices (from extract script output)."""
    p = OUTPUT_DIR / "gtd_gpps_timeseries.json"
    if not p.exists():
        return {"years": [], "practice_series": [], "average_series": [], "gtd_practice_count": 0, "practices_with_survey_history": 0}
    return json.loads(p.read_text(encoding="utf-8"))


def build_patient_change_analysis(
    markers: list[dict[str, Any]],
    patient_counts_by_year: dict[str, dict[str, int]],
    dataset_google_review_average: dict[str, Any] | None = None,
) -> dict[str, Any]:
    dataset_average_by_year: dict[str, float | None] = {}
    for year, counts in (patient_counts_by_year or {}).items():
        values = []
        for value in (counts or {}).values():
            try:
                numeric = int(value)
            except (TypeError, ValueError):
                continue
            if numeric > 0:
                values.append(numeric)
        dataset_average_by_year[year] = (sum(values) / len(values)) if values else None

    years = sorted((patient_counts_by_year or {}).keys(), key=int)
    practice_series: list[dict[str, Any]] = []
    for marker in markers:
        code = str(marker.get("code", "")).strip()
        if not code:
            continue
        points: list[int | None] = []
        for year in years:
            try:
                value = int((patient_counts_by_year.get(year) or {}).get(code))
            except (TypeError, ValueError, AttributeError):
                value = None
            points.append(value if value and value > 0 else None)
        if sum(1 for value in points if value is not None) < 2:
            continue
        practice_series.append(
            {
                "code": code,
                "name": marker.get("name", code),
                "management_company": marker.get("management_company", ""),
                "gtd": bool(marker.get("gtd")),
                "registered_patient_count": marker.get("registered_patient_count"),
                "points": points,
            }
        )

    average_series: list[float | None] = []
    for year in years:
        value = dataset_average_by_year.get(year)
        average_series.append(round(value, 3) if value is not None else None)

    review_average_lookup = {
        str(year): value
        for year, value in zip(
            dataset_google_review_average.get("years", []) if dataset_google_review_average else [],
            dataset_google_review_average.get("average_series", []) if dataset_google_review_average else [],
            strict=False,
        )
    }
    review_average_practice_count_lookup = {
        str(year): value
        for year, value in zip(
            dataset_google_review_average.get("years", []) if dataset_google_review_average else [],
            dataset_google_review_average.get("practice_count_series", []) if dataset_google_review_average else [],
            strict=False,
        )
    }
    dataset_review_average_series = [review_average_lookup.get(str(year)) for year in years]
    dataset_review_average_practice_counts = [
        int(review_average_practice_count_lookup.get(str(year)) or 0) for year in years
    ]

    return {
        "years": years,
        "dataset_average_by_year": dataset_average_by_year,
        "practice_count": len(practice_series),
        "practice_series": practice_series,
        "average_series": average_series,
        "dataset_review_average_series": dataset_review_average_series,
        "dataset_review_average_practice_counts": dataset_review_average_practice_counts,
        "dataset_review_practice_history_count": int(
            (dataset_google_review_average or {}).get("practices_with_review_history", 0)
        ),
    }


def write_map_embed_data(path: Path, embed: dict[str, Any]) -> None:
    path.write_text(
        "window.__MAP_EMBED__ = " + json.dumps(embed, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


def write_rating_change_embed_data(path: Path, embed: dict[str, Any]) -> None:
    path.write_text(
        "window.__RATING_CHANGE_EMBED__ = " + json.dumps(embed, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


def render_map_html(
    *,
    total_registered_patients: int,
    registered_patient_rows: int,
    national_registered_patients: int,
    national_supplemental_count: int,
    data_pool_report_html: str,
) -> str:
    template = (MAP_ASSETS_DIR / "map.html").read_text(encoding="utf-8")
    html = template.replace("__MANCHESTER_TOTAL_PATIENTS__", f"{total_registered_patients:,}")
    html = html.replace("__MANCHESTER_REGISTERED_PRACTICE_ROWS__", str(registered_patient_rows))
    html = html.replace("__NATIONAL_TOTAL_PATIENTS_RAW__", str(national_registered_patients))
    html = html.replace("__NATIONAL_TOTAL_PATIENTS__", f"{national_registered_patients:,}")
    html = html.replace("__NATIONAL_SUPPLEMENTAL_COUNT__", str(national_supplemental_count))
    html = html.replace("__DATA_POOL_REPORT_HTML__", data_pool_report_html)
    html = html.replace("__NATIONAL_SUPPLEMENTAL_SCRIPT__", NATIONAL_SUPPLEMENTAL_SCRIPT_NAME)
    return html


def healthcare_terrain_overlay_from_metadata(
    metadata: dict[str, Any],
    *,
    rel_base_path: str,
    label: str,
    mode: str,
) -> dict[str, Any] | None:
    bbox = ((metadata.get("raster") or {}).get("lonlat_bbox") or metadata.get("bbox") or (metadata.get("source") or {}).get("bbox") or {})
    min_lon = bbox.get("min_lon")
    min_lat = bbox.get("min_lat")
    max_lon = bbox.get("max_lon")
    max_lat = bbox.get("max_lat")
    if not all(isinstance(value, (int, float)) for value in (min_lon, min_lat, max_lon, max_lat)):
        return None
    tile_manifest = metadata.get("tile_manifest") or {}
    overlay_id = str(metadata.get("overlay_id") or "").strip().lower() or (
        "england_catchment" if mode == "catchment_overlap" else str(metadata.get("nation") or "").strip().lower()
    )
    overlay_nation = str(metadata.get("overlay_nation") or metadata.get("nation") or "").strip().lower() or (
        "england" if mode == "catchment_overlap" else ""
    )
    return {
        "overlayId": overlay_id,
        "label": label,
        "mode": mode,
        "nation": overlay_nation,
        "tileUrl": f"./{rel_base_path}/tiles/{{z}}/{{x}}/{{y}}.png",
        "summaryUrl": f"./{rel_base_path}/summary.json",
        "previewUrl": f"./{rel_base_path}/availability-bands.png" if mode == "catchment_overlap" else f"./{rel_base_path}/distance-strength-bands.png",
        "bounds": [[float(min_lat), float(min_lon)], [float(max_lat), float(max_lon)]],
        "minZoom": int(tile_manifest.get("min_zoom", 4) or 4),
        "maxNativeZoom": int(tile_manifest.get("max_zoom", 9) or 9),
        "tileSize": int(tile_manifest.get("tile_size", 256) or 256),
        "opacity": 0.58 if mode == "catchment_overlap" else 0.5,
        "bands": metadata.get("bands") or [],
        "notes": metadata.get("notes") or [],
    }


def prepare_healthcare_terrain_overlays(out_dir: Path) -> list[dict[str, Any]]:
    overlays: list[dict[str, Any]] = []
    metadata_path = HEALTHCARE_TERRAIN_OUTPUT_DIR / "metadata.json"
    if metadata_path.exists():
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            metadata = None
        if isinstance(metadata, dict):
            published_dir = out_dir / PUBLISHED_HEALTHCARE_TERRAIN_CATCHMENT_REL_PATH
            shutil.copytree(HEALTHCARE_TERRAIN_OUTPUT_DIR, published_dir, dirs_exist_ok=True)
            overlay = healthcare_terrain_overlay_from_metadata(
                metadata,
                rel_base_path=PUBLISHED_HEALTHCARE_TERRAIN_CATCHMENT_REL_PATH,
                label="Catchment terrain",
                mode="catchment_overlap",
            )
            if overlay:
                overlays.append(overlay)

    distance_manifest_path = HEALTHCARE_TERRAIN_DISTANCE_OUTPUT_DIR / "manifest.json"
    if not distance_manifest_path.exists():
        return overlays
    try:
        distance_manifest = json.loads(distance_manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return overlays
    nations = distance_manifest.get("nations") if isinstance(distance_manifest, dict) else []
    if not isinstance(nations, list):
        return overlays
    for item in nations:
        if not isinstance(item, dict):
            continue
        slug = str(item.get("slug") or item.get("nation") or "").strip().lower()
        if not slug:
            continue
        nation_dir = HEALTHCARE_TERRAIN_DISTANCE_OUTPUT_DIR / slug
        nation_metadata_path = nation_dir / "metadata.json"
        if not nation_metadata_path.exists():
            continue
        try:
            nation_metadata = json.loads(nation_metadata_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        rel_base_path = f"{PUBLISHED_HEALTHCARE_TERRAIN_ROOT_REL_PATH}/distance-strength/{slug}"
        shutil.copytree(nation_dir, out_dir / rel_base_path, dirs_exist_ok=True)
        overlay = healthcare_terrain_overlay_from_metadata(
            nation_metadata,
            rel_base_path=rel_base_path,
            label=f"{str(item.get('label') or slug.title())} distance terrain",
            mode="distance_strength",
        )
        if overlay:
            overlays.append(overlay)
    return overlays


def write_map(
    path: Path,
    rows: list[dict[str, Any]],
    *,
    refresh_composite_region_cache: bool = False,
) -> None:
    rows = apply_gtd_takeover_metadata(rows)
    survey_by_code = load_gp_patient_survey_index()
    survey_branch_parent_by_code = load_gp_patient_survey_branch_parent_index()
    scotland_hace_by_code, scotland_hace_manifest_by_code = load_scotland_hace_index()
    gtd_google_timeseries = build_gtd_google_score_timeseries(rows)
    dataset_google_review_average = build_dataset_google_review_yearly_average(rows)
    google_review_activity_by_code = build_google_review_activity_lookup()
    gtd_survey_timeseries = load_gtd_gpps_timeseries()
    patient_counts_by_year = load_registered_patient_timeseries() or {}
    patient_change_by_code = build_patient_change_lookup(patient_counts_by_year)
    cqc_by_code = load_cqc_gp_location_index()
    deprivation_geojson = load_deprivation_subset_geojson()
    national_supplementals = build_national_map_supplementals()
    client_national_supplementals = [build_client_map_row(row) for row in national_supplementals]
    write_national_supplemental_script(path.parent / NATIONAL_SUPPLEMENTAL_SCRIPT_NAME, client_national_supplementals)
    all_practice_deprivation = load_cached_practice_deprivation_lookup()
    # Build a simple per-practice deprivation lookup JSON alongside the map
    practice_deprivation_lookup_path = path.parent / "practice_deprivation_lookup.json"
    practice_deprivation = write_practice_deprivation_lookup(practice_deprivation_lookup_path, rows)
    # TODO: Patient flow visualisation – use patient_counts_by_year to show where patients moved between practices over time
    known_management_companies = sorted(
        {
            row.get("management_company_name", "") or ("GTD Healthcare" if row["gtd_managed"] else "")
            for row in rows
            if row.get("management_company_name", "") or row["gtd_managed"]
        }
    )
    markers = []
    total_registered_patients = 0
    registered_patient_rows = 0
    national_registered_patients = 0
    for row in national_supplementals:
        registered_patient_count = row.get("registered_patient_count", "")
        if registered_patient_count in ("", None):
            continue
        try:
            national_registered_patients += int(registered_patient_count)
        except (TypeError, ValueError):
            continue
    for row in rows:
        review_activity = google_review_activity_by_code.get(str(row["canonical_code"]), {})
        nation = str(row.get("nation") or "england").strip().lower()
        survey_metadata = national_survey_metadata(nation)
        survey_payload, survey_code_used, survey_resolution_note, survey_overrides = resolve_national_practice_survey_payload(
            str(row["canonical_code"]),
            nation,
            survey_by_code,
            survey_branch_parent_by_code,
            scotland_hace_by_code,
            scotland_hace_manifest_by_code,
        )
        for key, value in survey_overrides.items():
            if str(value).strip():
                survey_metadata[key] = str(value).strip()
        cqc = cqc_by_code.get(str(row["canonical_code"]), {}) if nation == "england" else {}
        effective_registered_patient_count = row.get("registered_patient_count", "")
        effective_registered_patient_count_source = row.get("registered_patient_count_source", "")
        if effective_registered_patient_count in ("", None):
            effective_registered_patient_count = row.get("registered_patient_count_candidate", "")
            effective_registered_patient_count_source = row.get("registered_patient_count_candidate_source", "")
        patient_change = patient_change_by_code.get(str(row["canonical_code"]), {})
        if not patient_change:
            parent_code = parent_patient_ods_code(row["canonical_code"])
            if parent_code:
                patient_change = patient_change_by_code.get(parent_code, {})
        registered_patient_count = row.get("registered_patient_count", "")
        if registered_patient_count not in ("", None):
            try:
                total_registered_patients += int(registered_patient_count)
                registered_patient_rows += 1
            except (TypeError, ValueError):
                pass
        markers.append(
            {
                "code": row["canonical_code"],
                "name": row["practice_name"],
                "lat": row["latitude"],
                "lon": row["longitude"],
                "postcode": row["postcode"],
                "street_address": row.get("street_address", ""),
                "nation": nation,
                "record_scope": "Manchester core dataset",
                "gtd": row["gtd_managed"],
                "management_company": row.get("management_company_name", "") or ("GTD Healthcare" if row["gtd_managed"] else ""),
                "affiliated_group": row.get("affiliated_group_name", ""),
                "google_score": row["google_review_score"],
                "google_count": row["google_review_count"],
                "google_maps_url": row.get("google_url", "") or row.get("google_review_source_url", ""),
                "google_review_span_years": review_activity.get("review_span_years", ""),
                "google_reviews_per_year": review_activity.get("reviews_per_year", ""),
                "google_source_note": row.get("google_review_source_note", ""),
                "google_text_file": row.get("google_review_text_file", ""),
                "google_review_scan_status": row.get("google_review_scan_status", ""),
                "google_review_has_listing": row.get("google_review_has_listing", ""),
                "nhs_url": row["nhs_profile_url"],
                "website_url": row.get("website_url", ""),
                "ods_org_link": row.get("ods_org_link", ""),
                "gtd_url": row["gtd_site_url"],
                "gtd_takeover_date": row.get("gtd_takeover_date", ""),
                "gtd_takeover_precision": row.get("gtd_takeover_date_precision", ""),
                "gtd_takeover_note": row.get("gtd_takeover_note", ""),
                "gtd_takeover_source_label": row.get("gtd_takeover_source_label", ""),
                "gtd_takeover_source_url": row.get("gtd_takeover_source_url", ""),
                "nearby": row["nearby_to_gtd_anchors"],
                "survey_overall_good_percent": survey_metric(survey_payload, "overallexp"),
                "survey_overall_good_ics_percent": survey_metric(survey_payload, "overallexp", "ics_percent"),
                "survey_overall_good_national_percent": survey_metric(survey_payload, "overallexp", "national_percent"),
                "survey_completion_rate_percent": survey_payload.get("completion_rate_percent", ""),
                "survey_sent_out": survey_payload.get("surveys_sent_out", ""),
                "survey_sent_back": survey_payload.get("surveys_sent_back", ""),
                "number_of_responses": survey_payload.get("number_of_responses", ""),
                "responses_for_overall_question": survey_payload.get("responses_for_overall_question", ""),
                "gp_patient_survey_2025_url": survey_payload.get("gpps_url", ""),
                "gp_patient_survey_code_used": survey_code_used,
                "gp_patient_survey_resolution_note": survey_resolution_note,
                "patient_survey_name": survey_metadata.get("patient_survey_name", "GP Patient Survey"),
                "patient_survey_status": survey_metadata.get("patient_survey_status", "practice_level_available"),
                "patient_survey_level": survey_metadata.get("patient_survey_level", "practice"),
                "patient_survey_url": survey_metadata.get("patient_survey_url", "https://www.gp-patient.co.uk"),
                "patient_survey_note": survey_metadata.get("patient_survey_note", ""),
                "cqc_overall_rating": str(cqc.get("overall_rating", "")).strip(),
                "cqc_location_url": str(cqc.get("url", "")).strip(),
                "cqc_service_website": str(cqc.get("service_website", "")).strip(),
                "cqc_publication_date": str(cqc.get("publication_date", "")).strip(),
                "cqc_inherited_rating": str(cqc.get("inherited_rating", "")).strip(),
                "cqc_provider_name": str(cqc.get("provider_name", "")).strip(),
                "registered_patient_count": row.get("registered_patient_count", ""),
                "registered_patient_count_candidate": row.get("registered_patient_count_candidate", ""),
                "registered_patient_count_candidate_code": row.get("registered_patient_count_candidate_code", ""),
                "registered_patient_count_candidate_source": row.get("registered_patient_count_candidate_source", ""),
                "registered_patient_count_effective": effective_registered_patient_count,
                "patient_change_per_year": patient_change.get("patient_change_per_year", ""),
                "patient_change_start_year": patient_change.get("patient_change_start_year", ""),
                "patient_change_end_year": patient_change.get("patient_change_end_year", ""),
                "registered_patient_count_source": row.get("registered_patient_count_source", ""),
                "registered_patient_count_effective_source": effective_registered_patient_count_source,
            }
        )

    data_pool_report_html = build_data_pool_report_html(markers, national_supplementals, all_practice_deprivation)
    client_markers = [build_client_map_row(row) for row in markers]
    combined_client_rows_by_code: dict[str, dict[str, Any]] = {}
    for row in client_national_supplementals:
        code = str(row.get("code", "")).strip()
        if code:
            combined_client_rows_by_code[code] = row
    for row in client_markers:
        code = str(row.get("code", "")).strip()
        if code:
            combined_client_rows_by_code[code] = row
    combined_client_rows = list(combined_client_rows_by_code.values())
    composite_region_definitions = load_composite_region_definitions()
    if refresh_composite_region_cache or not composite_region_definitions:
        composite_region_definitions = write_composite_region_definitions(combined_client_rows)

    patient_change_analysis = build_patient_change_analysis(
        markers,
        patient_counts_by_year,
        dataset_google_review_average,
    )

    center_lat = sum(row["latitude"] for row in rows) / len(rows)
    center_lon = sum(row["longitude"] for row in rows) / len(rows)
    out_dir = path.parent
    healthcare_terrain_overlays = prepare_healthcare_terrain_overlays(out_dir)
    map_embed: dict[str, Any] = {
        "rows": client_markers,
        "nationOrder": NATION_ORDER,
        "cityCatchments": CITY_CATCHMENTS,
        "compositeRegionDefinitions": composite_region_definitions,
        "compositeRegionRadiusMiles": COMPOSITE_REGION_RADIUS_MILES,
        "publishedCatchmentIndexRelPath": PUBLISHED_CATCHMENT_INDEX_REL_PATH,
        "northSouthDivide": {
            "west": {"lat": 51.62, "lon": -3.05},
            "east": {"lat": 52.98, "lon": 0.52},
        },
        "gtdGoogleTimeseries": gtd_google_timeseries,
        "gtdSurveyTimeseries": gtd_survey_timeseries,
        "patientCountsByYear": patient_counts_by_year,
        "patientChangeAnalysis": patient_change_analysis,
        "knownManagementCompanies": known_management_companies,
        "deprivationGeojson": deprivation_geojson,
        "healthcareTerrainOverlays": healthcare_terrain_overlays,
        "practiceDeprivationLookup": practice_deprivation,
        "allPracticeDeprivationLookup": all_practice_deprivation,
        "centerLat": center_lat,
        "centerLon": center_lon,
        "mapZoom": 11,
    }
    shutil.copy2(MAP_ASSETS_DIR / "map.css", out_dir / "map.css")
    shutil.copy2(MAP_ASSETS_DIR / "map-app.js", out_dir / "map-app.js")
    if (MAP_ASSETS_DIR / "flags").exists():
        shutil.copytree(MAP_ASSETS_DIR / "flags", out_dir / "flags", dirs_exist_ok=True)
    write_map_embed_data(out_dir / MAP_EMBED_SCRIPT_NAME, map_embed)
    manchester_rating_timeseries = build_manchester_google_rating_timeseries_all_practices(rows)
    write_rating_change_embed_data(out_dir / RATING_CHANGE_EMBED_SCRIPT_NAME, manchester_rating_timeseries)
    for rating_page_asset in (
        "rating-change-over-time.html",
        "rating-change-over-time.js",
        "rating-change-over-time.css",
    ):
        src = MAP_ASSETS_DIR / rating_page_asset
        if src.exists():
            shutil.copy2(src, out_dir / rating_page_asset)
    map_html = render_map_html(
        total_registered_patients=total_registered_patients,
        registered_patient_rows=registered_patient_rows,
        national_registered_patients=national_registered_patients,
        national_supplemental_count=len(national_supplementals),
        data_pool_report_html=data_pool_report_html,
    )
    path.write_text(map_html, encoding="utf-8")


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Build GTD GP practice dataset")
    parser.add_argument("--fetch", action="store_true", help="Fetch from NHS (manual only); default loads from existing JSON")
    parser.add_argument(
        "--refresh-composite-region-cache",
        action="store_true",
        help="Recompute and rewrite the checked-in composite region cache.",
    )
    args = parser.parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if args.fetch:
        rows = build_dataset()
    else:
        existing = OUTPUT_DIR / "gtd_greater_manchester_gp_practices.json"
        if not existing.exists():
            print(f"Dataset JSON not found: {existing}. Run with --fetch to build from NHS (manual).", file=sys.stderr)
            return 1
        rows = json.loads(existing.read_text(encoding="utf-8"))

    if GOOGLE_REVIEW_RESULTS_JSON.exists():
        from merge_google_maps_reviews import merge_rows
        rows, _, _ = merge_rows(rows, json.loads(GOOGLE_REVIEW_RESULTS_JSON.read_text(encoding="utf-8")), 0.5)

    rows = enrich_rows_with_patient_count_candidates(rows)
    rows = enrich_rows_with_cqc(rows)

    write_csv(OUTPUT_DIR / "gtd_greater_manchester_gp_practices.csv", rows)
    write_json(OUTPUT_DIR / "gtd_greater_manchester_gp_practices.json", rows)
    summary = write_summary(OUTPUT_DIR / "summary.json", rows)
    write_readme(OUTPUT_DIR / "README.md", summary)
    write_map(
        OUTPUT_DIR / "map.html",
        rows,
        refresh_composite_region_cache=args.refresh_composite_region_cache,
    )
    print(f"Wrote {len(rows)} rows to {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
