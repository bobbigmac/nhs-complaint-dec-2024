#!/usr/bin/env python3
from __future__ import annotations

import csv
import html
import json
import math
import re
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
MANCHESTER_CATCHMENT_BUNDLE_NAME = "manchester-practice-catchments.geojson"
ENGLAND_GP_CATCHMENT_BY_PRACTICE_DIR = BASE_DIR / "catchments" / ".cache" / "gp-catchments-england" / "by_practice"
CQC_GP_RATINGS_JSON = BASE_DIR / "raw" / "cqc" / "cqc_gp_location_index.json"
GPPS_DOWNLOADS_DIR = Path.home() / "Downloads" / "nhs-gpps-stats"

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
    if not match:
        raise ValueError(f"Could not parse distance from {raw!r}")
    return float(match.group(1))


def parse_nhs_search_results(page_html: str) -> list[dict[str, Any]]:
    blocks = re.findall(r'(<li class="results__item.*?</li>)', page_html, flags=re.S)
    results: list[dict[str, Any]] = []
    for block in blocks:
        profile = re.search(r'href="(https://www\.nhs\.uk/services/gp-surgery/[^"]+)"', block)
        name = re.search(r'<h2[^>]*>\s*<a[^>]*>(.*?)</a>', block, flags=re.S)
        ods = re.search(r'<p id="item_id_\d+"[^>]*>(.*?)</p>', block, flags=re.S)
        distance = re.search(r'<p id="distance_\d+"[^>]*>.*?([0-9]+(?:\.[0-9]+)?\s*miles?\s*away)</p>', block, flags=re.S)
        address = re.search(r'<p id="address_\d+"[^>]*>(.*?)</p>', block, flags=re.S)
        phone = re.search(r'<a id="phone_\d+_link" href="tel:[^"]+">(.*?)</a>', block, flags=re.S)
        org_type = re.search(r'<p id="item_org_type_id_\d+"[^>]*>(.*?)</p>', block, flags=re.S)
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
                    "nearby_to_gtd_anchors": [],
                    "nearby_anchor_search_distances_miles": {},
                },
            )
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
                    "nearby_to_gtd_anchors": [],
                    "nearby_anchor_search_distances_miles": {},
                    "source_search_centers": [],
                },
            )
            source_centers = entry.setdefault("source_search_centers", [])
            if center["name"] not in source_centers:
                source_centers.append(center["name"])

    records: list[dict[str, Any]] = []
    total = len(practice_index)
    for index, practice in enumerate(practice_index.values(), start=1):
        print(f"[{index}/{total}] Enriching {practice['search_result_name']}", file=sys.stderr)
        profile = parse_nhs_profile(practice["initial_profile_url"])
        canonical_code = profile["canonical_code"]
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
            "accepting_new_patients": profile["accepting_new_patients"],
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
    supplementals: list[dict[str, Any]] = []

    for code, source_row in input_by_code.items():
        result = results_by_code.get(code, {})
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

        if google_score in ("", None) and survey_score in ("", None):
            continue

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
        if coords is None:
            continue

        cqc = cqc_by_code.get(code, {}) if str(source_row.get("nation", "")).strip().lower() == "england" else {}

        supplementals.append(
            {
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
                "cqc_overall_rating": str(cqc.get("overall_rating", "")).strip(),
                "cqc_location_url": str(cqc.get("url", "")).strip(),
                "cqc_service_website": str(cqc.get("service_website", "")).strip(),
                "cqc_publication_date": str(cqc.get("publication_date", "")).strip(),
                "cqc_inherited_rating": str(cqc.get("inherited_rating", "")).strip(),
                "cqc_provider_name": str(cqc.get("provider_name", "")).strip(),
                "is_national_supplemental": True,
            }
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
    manchester_catchment_bundle = write_manchester_catchment_bundle(path.parent / MANCHESTER_CATCHMENT_BUNDLE_NAME, rows)
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
    map_html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Manchester GPs' Reviews Map</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
:root {{
  --bg: #f6f4ef;
  --ink: #1a1c1a;
  --panel: rgba(255,255,255,0.92);
  --panel-strong: rgba(255,255,255,0.98);
  --missing: #9aa0a6;
  --low: #c3472f;
  --midlow: #dc8c23;
  --midhigh: #d2b529;
  --high: #4c9a52;
  --veryhigh: #1c7c54;
  --line: rgba(26,28,26,0.12);
  --accent: #0f5e9c;
}}
html, body {{
  margin: 0;
}}
body {{
  font: 18px/1.4 Georgia, serif;
  color: var(--ink);
  background: radial-gradient(circle at top, #fff7e3, var(--bg));
}}
.page {{
  min-height: 100vh;
  min-height: 100dvh;
  display: grid;
  grid-template-rows: minmax(100vh, 100dvh) auto;
}}
.map-stage {{
  position: relative;
  display: grid;
  grid-template-areas: "legend map";
  grid-template-columns: var(--sidebar-width, 360px) minmax(0, 1fr);
  min-height: 100vh;
  min-height: 100dvh;
  transition: grid-template-columns 180ms ease;
}}
#map {{
  grid-area: map;
  height: 100vh;
  height: 100dvh;
  min-height: 100vh;
  min-height: 100dvh;
}}
.legend {{
  grid-area: legend;
  position: relative;
  z-index: 10;
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: var(--panel-strong);
  padding: 12px 14px;
  border-right: 1px solid var(--line);
  box-shadow: inset -1px 0 0 rgba(26, 28, 26, 0.04);
  max-width: none;
  overflow: auto;
}}
.map-stage.is-collapsed {{
  --sidebar-width: 82px;
}}
.legend-header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}}
.home-link,
.legend-collapse {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 34px;
  padding: 0 12px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: rgba(15, 94, 156, 0.06);
  color: var(--ink);
  font: 600 12px/1.2 "Avenir Next", "Trebuchet MS", sans-serif;
  text-decoration: none;
  cursor: pointer;
}}
.legend-collapse {{
  min-width: 34px;
}}
.legend-intro {{
  display: grid;
}}
.legend h1 {{
  margin: 0 0 8px;
  font-size: 18px;
}}
.legend p {{
  margin: 0 0 8px;
}}
.legend h2 {{
  margin: 12px 0 8px;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}}
.legend .row {{
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}}
.legend .hint {{
  color: rgba(26, 28, 26, 0.72);
  font-size: 12px;
}}
.control-group {{
  display: grid;
  gap: 8px;
}}
#score-source-control-spacer[hidden] {{
  display: none !important;
}}
#score-source-control.is-fixed {{
  position: fixed;
  top: 0;
  left: var(--sticky-left, 0);
  width: var(--sticky-width, auto);
  z-index: 40;
  background: var(--panel-strong);
  background: transparent;
  /*box-shadow: 0 10px 18px -14px rgba(26, 28, 26, 0.42);*/
}}
#score-source-control.is-fixed h2,
#score-source-control.is-fixed #metric-description,
#score-source-control.is-fixed #gap-mode-note {{
  display: none;
}}
#score-source-control.is-fixed {{
  gap: 6px;
  padding-top: 8px;
  padding-bottom: 8px;
}}
#score-source-control.is-fixed .segmented {{
  background: white;
}}
.management-group {{
  flex: 1 1 auto;
  min-height: 0;
  display: grid;
  grid-template-rows: auto auto minmax(0, 1fr);
  align-content: start;
  gap: 0;
}}
.segmented {{
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  border: 1px solid var(--line);
  border-radius: 999px;
  overflow: hidden;
  background: rgba(15, 94, 156, 0.06);
}}
#completion-scope-control {{
  grid-template-columns: 1fr 1fr;
}}
#rating-survey-mode-control {{
  grid-template-columns: 1fr 1fr;
}}
#size-mode-control {{
  grid-template-columns: 1fr 1fr;
}}
#area-overlay-control {{
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}}
.overlay-toggle-label {{
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  padding: 8px 10px;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: rgba(15, 94, 156, 0.04);
}}
.overlay-toggle-label.is-active {{
  border-color: rgba(15, 94, 156, 0.28);
  background: rgba(15, 94, 156, 0.09);
}}
.overlay-action-button {{
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  padding: 8px 10px;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: rgba(15, 94, 156, 0.04);
  color: var(--ink);
  min-height: 40px;
  width: 100%;
}}
.overlay-action-button.is-active {{
  border-color: rgba(15, 94, 156, 0.28);
  background: rgba(15, 94, 156, 0.09);
}}
.overlay-action-button:disabled {{
  opacity: 0.46;
  cursor: default;
}}
.map-floating-action-button {{
  position: absolute;
  right: 22px;
  bottom: calc(22px + env(safe-area-inset-bottom, 0px));
  z-index: 420;
  width: auto;
  min-width: 0;
  padding: 10px 14px;
  border-radius: 999px;
  box-shadow: 0 10px 24px rgba(0,0,0,0.16);
  background: rgba(255,255,255,0.94);
  backdrop-filter: blur(8px);
}}
.map-floating-action-button:hover {{
  background: rgba(255,255,255,0.98);
}}
.circle-sample-controls {{
  display: grid;
  gap: 8px;
}}
.circle-sample-actions {{
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}}
.circle-radius-control {{
  display: grid;
  gap: 6px;
}}
.circle-radius-control[hidden] {{
  display: none !important;
}}
.circle-radius-label {{
  display: flex;
  justify-content: space-between;
  gap: 10px;
  font-size: 13px;
  font-weight: 700;
}}
.circle-radius-label span:last-child {{
  color: rgba(26, 28, 26, 0.68);
}}
.circle-radius-control input[type="range"] {{
  width: 100%;
}}
.check-toggle {{
  justify-content: space-between;
}}
.check-toggle input {{
  display: none;
}}
.check-toggle-mark {{
  width: 18px;
  height: 18px;
  border-radius: 999px;
  border: 1px solid rgba(26,28,26,0.22);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  line-height: 1;
  color: transparent;
  background: rgba(255,255,255,0.75);
  flex: 0 0 auto;
}}
.check-toggle input:checked + span + .check-toggle-mark {{
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
}}
.gap-mode-control[hidden] {{
  display: none !important;
}}
.gap-mode-note {{
  margin-top: 6px;
  font-size: 11px;
  line-height: 1.35;
}}
.overlay-toggle-label input {{
  display: inline-block;
  margin: 0;
}}
.overlay-toggle-icon,
.segmented-short {{
  display: none;
}}
.segmented label {{
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 7px 10px;
  cursor: pointer;
  font-size: 13px;
}}
.segmented input {{
  display: none;
}}
.segmented span {{
  width: 100%;
  text-align: center;
  border-radius: 999px;
  padding: 5px 8px;
}}
.segmented input:checked + span {{
  background: var(--accent);
  color: #fff;
}}
.metric-note {{
  margin-top: 6px;
  font-size: 11px;
  line-height: 1.35;
}}
.manager-list {{
  display: grid;
  gap: 8px;
  min-height: 0;
  overflow: auto;
  padding-right: 4px;
}}
.manager-option {{
  display: grid;
  grid-template-columns: 18px 1fr auto;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}}
.manager-option input {{
  margin: 0;
}}
.manager-name {{
  display: flex;
  align-items: center;
  min-width: 0;
}}
.manager-name-text {{
  min-width: 0;
}}
.manager-meta {{
  color: rgba(26, 28, 26, 0.68);
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}}
.swatch {{
  width: 14px;
  height: 14px;
  border: 1px solid rgba(0,0,0,0.25);
  flex: 0 0 auto;
}}
.swatch.circle {{
  border-radius: 999px;
}}
.swatch.square {{}}
.swatch.diamond {{
  transform: rotate(45deg);
}}
.swatch.triangle {{
  clip-path: polygon(50% 0, 0 100%, 100% 100%);
}}
.swatch.hexagon {{
  clip-path: polygon(25% 0, 75% 0, 100% 50%, 75% 100%, 25% 100%, 0 50%);
}}
.swatch.pentagon {{
  clip-path: polygon(50% 0, 100% 38%, 81% 100%, 19% 100%, 0 38%);
}}
.map-stage.is-collapsed .legend {{
  padding-inline: 10px;
}}
.map-stage.is-collapsed .legend-header {{
  flex-direction: column;
  align-items: stretch;
}}
.map-stage.is-collapsed .home-link,
.map-stage.is-collapsed .legend-collapse {{
  width: 100%;
  min-width: 0;
  padding-inline: 0;
}}
.map-stage.is-collapsed .home-link-text,
.map-stage.is-collapsed .legend-intro,
.map-stage.is-collapsed .control-group h2,
.map-stage.is-collapsed #metric-description,
.map-stage.is-collapsed #area-overlay-tip,
.map-stage.is-collapsed #manager-hint,
.map-stage.is-collapsed .manager-name-text,
.map-stage.is-collapsed .manager-meta {{
  display: none;
}}
.map-stage.is-collapsed .home-link::before {{
  content: "H";
}}
.map-stage.is-collapsed .segmented {{
  grid-template-columns: 1fr;
  border-radius: 16px;
}}
.map-stage.is-collapsed .segmented label {{
  padding: 0;
}}
.map-stage.is-collapsed .segmented span {{
  display: none;
}}
.map-stage.is-collapsed .segmented-short {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 38px;
  border-radius: 12px;
  font: 700 12px/1 "Avenir Next", "Trebuchet MS", sans-serif;
}}
.map-stage.is-collapsed .segmented input:checked + span + .segmented-short {{
  background: var(--accent);
  color: #fff;
}}
.map-stage.is-collapsed #area-overlay-control {{
  grid-template-columns: 1fr;
}}
.map-stage.is-collapsed .overlay-toggle-label,
.map-stage.is-collapsed .overlay-action-button {{
  justify-content: center;
  padding-inline: 0;
}}
.map-stage.is-collapsed .overlay-toggle-label > span,
.map-stage.is-collapsed .overlay-action-button > span {{
  display: none;
}}
.map-stage.is-collapsed .overlay-toggle-icon {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 22px;
  font: 700 12px/1 "Avenir Next", "Trebuchet MS", sans-serif;
}}
.map-stage.is-collapsed .manager-option {{
  grid-template-columns: 18px 1fr;
}}
.map-stage.is-collapsed .manager-name {{
  justify-content: center;
}}
.map-stage.is-collapsed .swatch {{
  margin-right: 0 !important;
}}
.leaflet-marker-icon.marker-icon {{
  background: transparent;
  border: 0;
}}
.marker-svg {{
  display: block;
  width: 100%;
  height: 100%;
  overflow: visible;
  filter: drop-shadow(0 4px 12px rgba(0,0,0,0.22));
}}
.leaflet-popup-content {{
  min-width: 220px;
}}
.leaflet-popup-content a {{
  word-break: break-word;
}}
.insights {{
  padding: 18px 18px 26px;
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
}}
.panel {{
  background: var(--panel-strong);
  border-radius: 16px;
  padding: 14px 16px;
  box-shadow: 0 10px 28px rgba(0,0,0,0.08);
}}
.panel h2 {{
  margin: 0 0 8px;
  font-size: 18px;
}}
.panel p {{
  margin: 0 0 10px;
}}
.chart-frame {{
  width: 100%;
  overflow-x: auto;
}}
.trend-chart-layout {{
  display: grid;
  grid-template-columns: minmax(0, 1fr) 190px;
  gap: 14px;
  align-items: start;
}}
.trend-legend {{
  display: grid;
  gap: 6px;
  max-height: 360px;
  overflow: auto;
  padding-right: 4px;
}}
.trend-legend-item {{
  display: grid;
  grid-template-columns: 12px minmax(0, 1fr);
  gap: 8px;
  align-items: start;
  width: 100%;
  padding: 7px 8px;
  border: 1px solid rgba(26, 28, 26, 0.12);
  border-radius: 10px;
  background: rgba(255,255,255,0.72);
  color: inherit;
  text-align: left;
  cursor: pointer;
}}
.trend-legend-item.is-active {{
  border-color: rgba(15, 94, 156, 0.48);
  background: rgba(15, 94, 156, 0.09);
  box-shadow: inset 0 0 0 1px rgba(15, 94, 156, 0.08);
}}
.trend-legend-item:hover {{
  border-color: rgba(26, 28, 26, 0.24);
}}
.trend-legend-swatch {{
  width: 12px;
  height: 12px;
  border-radius: 999px;
  margin-top: 3px;
}}
.trend-legend-body {{
  min-width: 0;
}}
.trend-overlay-legend {{
  display: flex;
  flex-wrap: wrap;
  gap: 10px 14px;
  margin: 10px 0 0;
}}
.trend-overlay-key {{
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  color: rgba(26, 28, 26, 0.78);
}}
.trend-overlay-swatch {{
  width: 26px;
  border-top: 3px dashed var(--swatch-color, currentColor);
}}
.trend-legend-name {{
  display: block;
  font-size: 12px;
  font-weight: 700;
  line-height: 1.25;
}}
.trend-legend-meta {{
  display: block;
  margin-top: 2px;
  font-size: 11px;
  color: rgba(26, 28, 26, 0.72);
  line-height: 1.3;
}}
#scatterplot {{
  width: 100%;
  height: 320px;
  display: block;
}}
#rating-survey-chart {{
  width: 100%;
  height: 320px;
  display: block;
}}
#gtd-score-trend-chart {{
  width: 100%;
  height: 360px;
  display: block;
}}
.chart-note {{
  font-size: 12px;
  color: rgba(26, 28, 26, 0.72);
}}
.comparison-panel {{
  grid-column: 1 / -1;
}}
.player-controls {{
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: 10px;
  align-items: center;
  margin: 0 0 10px;
}}
.player-button {{
  min-width: 78px;
}}
.player-scrubber {{
  width: 100%;
  accent-color: var(--accent);
}}
.player-year-label {{
  min-width: 72px;
  text-align: right;
  font: 600 12px/1.2 "Avenir Next", "Trebuchet MS", sans-serif;
  color: rgba(26, 28, 26, 0.78);
}}
.treemap-mode-control {{
  display: flex;
  justify-content: flex-start;
  margin: 0;
}}
.treemap-mode-control .check-toggle {{
  display: inline-flex;
  width: auto;
  max-width: 100%;
  justify-content: flex-start;
  gap: 10px;
}}
.treemap-mode-control .check-toggle > span:first-of-type {{
  flex: 0 1 auto;
}}
.panel-heading-row {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin: 0 0 8px;
}}
.panel-heading-row h2 {{
  margin: 0;
}}
#patient-treemap-chart {{
  width: 100%;
  height: 420px;
  display: block;
}}
#patient-total-chart {{
  width: 100%;
  height: 118px;
  display: block;
  margin-top: 8px;
}}
.comparison-grid {{
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}}
.comparison-card {{
  border: 1px solid var(--line);
  border-radius: 14px;
  background: rgba(255,255,255,0.72);
  padding: 12px 14px;
}}
.comparison-card.is-baseline {{
  border-color: rgba(15, 94, 156, 0.28);
  background: rgba(240, 247, 255, 0.9);
}}
.comparison-card.is-selected {{
  border-color: rgba(178, 83, 34, 0.24);
  background: rgba(255, 249, 242, 0.92);
}}
.comparison-card h3 {{
  margin: 0 0 8px;
  font-size: 17px;
}}
.comparison-kicker {{
  margin: 0 0 10px;
  color: rgba(26, 28, 26, 0.72);
  font-size: 12px;
}}
.comparison-summary {{
  margin: 0 0 12px;
  font-size: 14px;
  line-height: 1.45;
}}
.comparison-summary p {{
  margin: 0 0 10px;
}}
.rank-bar {{
  display: grid;
  gap: 8px;
  margin-top: 10px;
}}
.rank-bar-track {{
  position: relative;
  height: 14px;
  border-radius: 999px;
  background: linear-gradient(90deg, #b23322 0%, #d7b74b 50%, #1f7a3f 100%);
  box-shadow: inset 0 0 0 1px rgba(26, 28, 26, 0.14);
  overflow: hidden;
}}
.rank-bar-marker {{
  position: absolute;
  top: 50%;
  width: 16px;
  height: 16px;
  border-radius: 999px;
  background: #fff;
  border: 2px solid rgba(26, 28, 26, 0.82);
  box-shadow: 0 2px 6px rgba(0,0,0,0.16);
  transform: translate(-50%, -50%);
}}
.rank-bar-labels {{
  display: flex;
  justify-content: space-between;
  gap: 10px;
  font-size: 12px;
  line-height: 1.35;
}}
.rank-bar-labels span {{
  color: rgba(26, 28, 26, 0.8);
}}
.rank-bar-labels strong {{
  color: #161816;
}}
.rank-bar-labels .rank-worse {{
  text-align: left;
}}
.rank-bar-labels .rank-better {{
  text-align: right;
}}
.comparison-metrics {{
  display: grid;
  gap: 8px;
}}
.comparison-row {{
  display: grid;
  grid-template-columns: 140px 1fr 1fr 1fr 1.1fr;
  gap: 10px;
  align-items: baseline;
  padding: 8px 0;
  border-top: 1px solid rgba(26, 28, 26, 0.08);
}}
.comparison-row:first-child {{
  border-top: 0;
  padding-top: 0;
}}
.comparison-label {{
  font-size: 12px;
  color: rgba(26, 28, 26, 0.68);
  font-weight: 700;
}}
.comparison-stat strong {{
  display: block;
  font-size: 18px;
}}
.comparison-stat strong.tone-good {{
  color: #1f7a3f;
}}
.comparison-stat strong.tone-mid {{
  color: #9d6a00;
}}
.comparison-stat strong.tone-bad {{
  color: #b23322;
}}
.comparison-stat strong.tone-missing {{
  color: #7d838a;
}}
.comparison-stat span {{
  display: block;
  font-size: 12px;
  color: rgba(26, 28, 26, 0.68);
}}
.comparison-delta {{
  font-size: 13px;
  line-height: 1.4;
}}
.comparison-delta.tone-good {{
  color: #1f7a3f;
}}
.comparison-delta.tone-mid {{
  color: #9d6a00;
}}
.comparison-delta.tone-bad {{
  color: #b23322;
}}
.comparison-delta.tone-missing {{
  color: #7d838a;
}}
.place-benchmark-section {{
  display: grid;
  gap: 12px;
}}
.place-benchmark-block {{
  display: grid;
  gap: 6px;
}}
.place-benchmark-subheading {{
  margin: 0;
  font-size: 15px;
  line-height: 1.1;
}}
.place-benchmark-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 10px;
}}
.place-benchmark-card {{
  border-top-width: 4px;
  display: grid;
  gap: 6px;
  padding: 9px 11px;
}}
.place-benchmark-header {{
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 8px 12px;
  flex-wrap: wrap;
}}
.place-benchmark-card h3 {{
  margin: 0;
  font-size: 15px;
  line-height: 1.12;
}}
.data-pool-panel {{
  display: grid;
  gap: 12px;
}}
.data-pool-panel summary {{
  list-style: none;
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  cursor: pointer;
  font-weight: 700;
}}
.data-pool-panel summary::-webkit-details-marker {{
  display: none;
}}
.data-pool-panel summary small {{
  font-size: 12px;
  font-weight: 600;
  color: rgba(26, 28, 26, 0.68);
}}
.data-pool-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(270px, 1fr));
  gap: 10px;
}}
.data-pool-card {{
  border: 1px solid rgba(26, 28, 26, 0.12);
  border-radius: 14px;
  background: rgba(255,255,255,0.72);
  padding: 12px 14px;
}}
.data-pool-card h3 {{
  margin: 0 0 6px;
  font-size: 16px;
}}
.data-pool-kicker {{
  margin: 0 0 10px;
  font-size: 12px;
  color: rgba(26, 28, 26, 0.68);
}}
.data-pool-list {{
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 8px;
}}
.data-pool-list li {{
  display: grid;
  gap: 2px;
  padding-top: 8px;
  border-top: 1px solid rgba(26, 28, 26, 0.08);
}}
.data-pool-list li:first-child {{
  padding-top: 0;
  border-top: 0;
}}
.data-pool-list strong {{
  font-size: 12px;
  color: rgba(26, 28, 26, 0.7);
}}
.data-pool-list span {{
  font-size: 13px;
  line-height: 1.45;
}}
.data-pool-footnote {{
  margin-bottom: 0;
}}
.place-benchmark-counts {{
  display: flex;
  flex-wrap: wrap;
  gap: 4px 10px;
  align-items: center;
  font-size: 22px;
  font-weight: 700;
  line-height: 1.05;
}}
.place-benchmark-counts span {{
  display: inline-flex;
  align-items: center;
  gap: 4px;
}}
.place-benchmark-counts small {{
  font-size: 14px;
  font-weight: 600;
  color: rgba(26, 28, 26, 0.78);
}}
.place-benchmark-count-divider {{
  color: rgba(26, 28, 26, 0.32);
  font-size: 18px;
  font-weight: 700;
}}
.place-benchmark-stats {{
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}}
.place-benchmark-stat {{
  border: 1px solid rgba(26, 28, 26, 0.10);
  border-radius: 10px;
  padding: 7px 9px 8px;
  background: rgba(255,255,255,0.74);
  min-width: 0;
}}
.place-benchmark-stat.is-active {{
  border-color: rgba(15, 94, 156, 0.30);
  box-shadow: inset 0 0 0 2px rgba(15, 94, 156, 0.10);
  background: rgba(240, 247, 255, 0.96);
}}
.place-benchmark-stat.is-wide {{
  grid-column: 1 / -1;
}}
.place-benchmark-stat.is-warning {{
  border-color: rgba(166, 50, 34, 0.22);
  background: rgba(255, 241, 239, 0.96);
}}
.place-benchmark-stat-label {{
  display: block;
  margin-bottom: 2px;
  font-size: 11px;
  font-weight: 700;
  color: rgba(26, 28, 26, 0.72);
  text-transform: uppercase;
  letter-spacing: 0.02em;
}}
.place-benchmark-stat-label-warning {{
  color: #b23322;
  font-weight: 800;
  margin-left: 4px;
}}
.place-benchmark-stat-value {{
  display: block;
  font-size: 28px;
  line-height: 0.98;
  font-weight: 800;
  letter-spacing: -0.03em;
}}
.place-benchmark-stat-value.tone-good {{
  color: #1f7a3f;
}}
.place-benchmark-stat-value.tone-mid {{
  color: #9d6a00;
}}
.place-benchmark-stat-value.tone-bad {{
  color: #b23322;
}}
.place-benchmark-stat-value.tone-missing {{
  color: #7d838a;
}}
.service-finder-panel {{
  display: grid;
  gap: 14px;
}}
.service-finder-header {{
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(290px, 0.95fr);
  gap: 14px 18px;
  align-items: start;
}}
.service-finder-title-wrap {{
  display: grid;
  gap: 6px;
}}
.service-finder-title-wrap h2 {{
  margin: 0;
}}
.service-finder-kicker {{
  margin: 0;
  max-width: 68ch;
  font-size: 15px;
  line-height: 1.5;
  color: rgba(26, 28, 26, 0.8);
}}
.service-finder-actions {{
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}}
.service-finder-actions .overlay-action-button {{
  min-height: 44px;
  justify-content: space-between;
  font-size: 14px;
  font-weight: 700;
}}
.service-finder-table-wrap {{
  overflow-x: auto;
  border: 1px solid rgba(26, 28, 26, 0.10);
  border-radius: 16px;
  background: rgba(255,255,255,0.82);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.65);
}}
.service-finder-table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}}
.service-finder-table th,
.service-finder-table td {{
  padding: 11px 12px;
  border-top: 1px solid rgba(26, 28, 26, 0.08);
  vertical-align: top;
  text-align: left;
}}
.service-finder-table thead th {{
  border-top: 0;
  padding-left: 12px;
  padding-right: 12px;
  text-align: left;
  background: rgba(245, 242, 233, 0.9);
  position: sticky;
  top: 0;
  z-index: 1;
}}
.service-finder-sort-button {{
  width: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  border: 0;
  padding: 12px 0;
  background: transparent;
  padding-top: 12px;
  padding-bottom: 12px;
  font-size: 12px;
  font-family: inherit;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: rgba(26, 28, 26, 0.66);
  cursor: pointer;
}}
.service-finder-sort-button:hover {{
  color: rgba(26, 28, 26, 0.86);
}}
.service-finder-sort-button.is-active {{
  color: rgba(26, 28, 26, 0.92);
}}
.service-finder-sort-indicator {{
  min-width: 10px;
  text-align: right;
  font-size: 11px;
  color: rgba(26, 28, 26, 0.42);
}}
.service-finder-sort-button.is-active .service-finder-sort-indicator {{
  color: rgba(26, 28, 26, 0.82);
}}
.service-finder-table tbody tr:hover {{
  background: rgba(245, 249, 255, 0.9);
}}
.service-finder-table tbody tr:nth-child(even) {{
  background: rgba(250, 249, 245, 0.58);
}}
.service-finder-table thead th:first-child {{
  padding-left: 24px;
}}
.service-finder-practice {{
  position: relative;
  padding-left: 24px !important;
  padding-right: 90px !important;
}}
.service-finder-practice::before {{
  content: '';
  position: absolute;
  left: 0;
  top: 8px;
  bottom: 8px;
  width: 5px;
  border-radius: 0 999px 999px 0;
  background: var(--service-finder-accent, #9aa0a6);
  opacity: 0.95;
}}
.service-finder-practice-name {{
  border: 0;
  padding: 0;
  background: transparent;
  color: var(--service-finder-accent, var(--midhigh));
  font: inherit;
  font-size: 16px;
  font-weight: 800;
  line-height: 1.3;
  text-align: left;
  text-decoration: none;
  cursor: pointer;
}}
.service-finder-practice-name:hover {{
  text-decoration: underline;
}}
.service-finder-practice-layout {{
  display: block;
}}
.service-finder-practice-main {{
  min-width: 0;
}}
.service-finder-title-line {{
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}}
.service-finder-cqc-badge {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  text-decoration: none;
  font-size: 15px;
  line-height: 1;
  border-radius: 999px;
  flex: 0 0 auto;
}}
.service-finder-cqc-badge:hover {{
  transform: translateY(-1px);
}}
.service-finder-cqc-badge.is-good {{
  color: #1f7a3d;
}}
.service-finder-cqc-badge.is-outstanding {{
  color: #b8860b;
}}
.service-finder-cqc-badge.is-requires-improvement {{
  color: #b26a00;
}}
.service-finder-cqc-badge.is-inadequate {{
  color: #b42318;
}}
.service-finder-cqc-badge.is-insufficient-evidence {{
  color: #667085;
}}
.service-finder-subtle {{
  display: inline;
  margin-top: 4px;
  font-size: 13px;
  color: rgba(26, 28, 26, 0.68);
}}
.service-finder-address-link {{
  display: inline-block;
  margin-top: 4px;
  text-decoration: none;
}}
.service-finder-address-link .service-finder-subtle {{
  margin-top: 0;
}}
.service-finder-address-line {{
  display: inline-flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0;
}}
.service-finder-address-separator {{
  display: inline;
  margin: 0 6px;
  color: rgba(26, 28, 26, 0.42);
}}
.service-finder-address-link:hover .service-finder-subtle {{
  color: var(--service-finder-accent, var(--midhigh));
}}
.service-finder-address-link .service-finder-subtle:last-child {{
  border-bottom: 1px solid rgba(26, 28, 26, 0.18);
}}
.service-finder-address-link:hover .service-finder-subtle:last-child {{
  border-bottom-color: currentColor;
}}
.service-finder-register-link {{
  position: absolute;
  top: 14px;
  right: 14px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: #0f5e9c;
  text-decoration: none;
  font-size: 14px;
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: 0.01em;
  white-space: nowrap;
  opacity: 0;
  transform: translateY(-2px);
  pointer-events: none;
  transition:
    opacity 140ms ease,
    transform 140ms ease,
    color 140ms ease;
}}
.service-finder-register-link::after {{
  content: '↗';
  font-size: 0.95em;
  line-height: 1;
}}
.service-finder-row:hover .service-finder-register-link,
.service-finder-row:focus-within .service-finder-register-link {{
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}}
.service-finder-register-link:hover {{
  color: #0b4978;
  text-decoration: underline;
  text-underline-offset: 0.14em;
  text-decoration-thickness: 1px;
}}
.service-finder-primary-metric {{
  min-width: 78px;
}}
.service-finder-secondary-metric {{
  min-width: 110px;
}}
.service-finder-primary-value {{
  display: block;
  font-size: 25px;
  line-height: 0.95;
  font-weight: 800;
  letter-spacing: -0.04em;
  color: #161816;
}}
.service-finder-primary-value.is-missing {{
  color: #8a9097;
}}
.service-finder-primary-value-link {{
  display: inline-block;
  color: inherit;
  text-decoration: none;
}}
.service-finder-primary-value-link:hover {{
  text-decoration: underline;
  text-decoration-thickness: 1px;
  text-underline-offset: 0.1em;
}}
.service-finder-primary-label {{
  display: none;
  margin-top: 4px;
  font-size: 11px;
  line-height: 1.2;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: rgba(26, 28, 26, 0.56);
}}
.service-finder-secondary-value {{
  display: block;
  font-size: 16px;
  line-height: 1.12;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: #161816;
  font-variant-numeric: tabular-nums;
}}
.service-finder-secondary-value.is-missing {{
  color: #8a9097;
}}
.service-finder-secondary-detail {{
  color: rgba(26, 28, 26, 0.46);
  font-weight: 700;
}}
.service-finder-secondary-label {{
  display: none;
  margin-top: 4px;
  font-size: 11px;
  line-height: 1.2;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: rgba(26, 28, 26, 0.56);
}}
.service-finder-secondary-trend {{
  display: block;
  margin-top: 4px;
  font-size: 12px;
  line-height: 1.15;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}}
.service-finder-secondary-trend.is-positive {{
  color: #1f7a45;
}}
.service-finder-secondary-trend.is-negative {{
  color: #b4472d;
}}
.service-finder-secondary-trend.is-flat {{
  color: rgba(26, 28, 26, 0.54);
}}
.service-finder-distance-cell {{
  white-space: nowrap;
}}
.service-finder-distance-value {{
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  color: rgba(26, 28, 26, 0.82);
}}
.service-finder-pin {{
  width: 38px;
  height: 38px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  background: #161816;
  color: #ffffff;
  box-shadow: 0 10px 24px rgba(0,0,0,0.18), inset 0 0 0 2px rgba(255,255,255,0.94);
  font: 800 13px/1 "Avenir Next", "Trebuchet MS", sans-serif;
  letter-spacing: -0.02em;
}}
.service-finder-pin.is-large {{
  width: 44px;
  height: 44px;
  font-size: 14px;
}}
.service-finder-drag-ghost {{
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1200;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 14px;
  border-radius: 999px;
  border: 1px solid rgba(15, 94, 156, 0.22);
  background: rgba(255,255,255,0.96);
  box-shadow: 0 10px 26px rgba(0,0,0,0.16);
  color: var(--ink);
  font: 700 14px/1.1 "Avenir Next", "Trebuchet MS", sans-serif;
  pointer-events: none;
  transform: translate(-50%, -50%);
  white-space: nowrap;
}}
.service-finder-score {{
  font-weight: 800;
  font-variant-numeric: tabular-nums;
}}
.service-finder-empty {{
  padding: 18px 14px 16px;
  font-size: 14px;
  line-height: 1.5;
  color: rgba(26, 28, 26, 0.72);
}}
.service-finder-tag {{
  display: inline-block;
  margin-left: 6px;
  padding: 2px 7px;
  border-radius: 999px;
  background: rgba(15, 94, 156, 0.10);
  color: rgba(15, 94, 156, 0.9);
  font-size: 11px;
  font-weight: 700;
  vertical-align: middle;
}}
@media (max-width: 960px) {{
  .page {{
    grid-template-rows: minmax(100vh, 100dvh) auto;
  }}
  .map-stage {{
    grid-template-areas:
      "map"
      "legend";
    grid-template-columns: 1fr;
    grid-template-rows: minmax(62vh, 70dvh) auto;
    min-height: auto;
  }}
  #map {{
    height: 62vh;
    height: 62dvh;
    min-height: 62vh;
    min-height: 62dvh;
  }}
  .insights {{
    grid-template-columns: 1fr;
  }}
  .comparison-grid {{
    grid-template-columns: 1fr;
  }}
  .trend-chart-layout {{
    grid-template-columns: 1fr;
  }}
  .trend-legend {{
    max-height: none;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  }}
  .comparison-row {{
    grid-template-columns: 1fr;
    gap: 6px;
  }}
  .place-benchmark-header {{
    display: grid;
    gap: 4px;
  }}
  .treemap-mode-control .check-toggle {{
    width: 100%;
    justify-content: space-between;
  }}
  .panel-heading-row {{
    flex-direction: column;
    align-items: stretch;
  }}
  .service-finder-header {{
    grid-template-columns: 1fr;
  }}
  .service-finder-actions {{
    grid-template-columns: 1fr;
  }}
  .service-finder-title-line {{
    align-items: flex-start;
  }}
  .service-finder-practice {{
    padding-right: 72px !important;
  }}
  .service-finder-register-link {{
    top: 12px;
    right: 12px;
  }}
  .service-finder-primary-value {{
    font-size: 22px;
  }}
  .map-floating-action-button {{
    right: 16px;
    bottom: calc(16px + env(safe-area-inset-bottom, 0px));
    padding: 9px 12px;
  }}
  .legend {{
    border-right: 0;
    border-top: 1px solid var(--line);
    box-shadow: none;
  }}
}}
@media (max-width: 720px) {{
  .service-finder-table thead {{
    display: none;
  }}
  .service-finder-primary-label,
  .service-finder-secondary-label {{
    display: block;
  }}
  .service-finder-table,
  .service-finder-table tbody,
  .service-finder-table tr {{
    display: block;
  }}
  .service-finder-table tbody tr {{
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  }}
  .service-finder-table tbody td {{
    display: block;
  }}
  .service-finder-practice,
  .service-finder-distance-cell {{
    grid-column: 1 / -1;
  }}
  .service-finder-distance-cell {{
    padding-top: 0;
    padding-bottom: 8px;
  }}
  .service-finder-primary-metric-google {{
    grid-column: 1;
  }}
  .service-finder-primary-metric-survey {{
    grid-column: 1;
  }}
  .service-finder-secondary-metric-reviews {{
    grid-column: 2;
    grid-row: 3;
  }}
  .service-finder-secondary-metric-patients {{
    grid-column: 2;
    grid-row: 4;
  }}
}}
@media print {{
  @page {{
    margin: 8mm;
  }}
  * {{
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}
  body {{
    background: #fff;
  }}
  .page {{
    display: block;
    min-height: 0;
  }}
  .map-stage {{
    grid-template-areas: "legend map";
    grid-template-columns: 280px minmax(0, 1fr);
    height: 194mm;
    min-height: 194mm;
    max-height: 194mm;
    break-inside: avoid-page;
    break-after: page;
    page-break-after: always;
    overflow: hidden;
    align-items: stretch;
  }}
  #map {{
    height: 194mm;
    min-height: 194mm;
    max-height: 194mm;
  }}
  .legend {{
    border: 1px solid var(--line);
    border-right: 0;
    box-shadow: none;
    height: 194mm;
    min-height: 194mm;
    max-height: 194mm;
    overflow: hidden;
  }}
  #score-source-control.is-fixed {{ position: static; width: auto; box-shadow: none; }}
  .insights {{
    margin-top: 0;
  }}
  .panel {{
    box-shadow: none;
    border: 1px solid var(--line);
    break-inside: avoid-page;
  }}
  .trend-chart-layout {{
    grid-template-columns: minmax(0, 1fr) 170px;
  }}
  .leaflet-control-container {{
    display: none;
  }}
  .marker-svg {{
    filter: none;
  }}
}}
</style>
</head>
<body>
  <div class="page">
  <div class="map-stage">
    <div class="legend">
      <div class="legend-header">
        <a class="home-link" href="../index.html" title="Back to homepage"><span class="home-link-text">Home</span></a>
        <button type="button" class="legend-collapse" id="legend-collapse" aria-pressed="false" title="Collapse sidebar"><span>&lsaquo;</span></button>
      </div>
      <div class="legend-intro">
        <h1>Manchester GPs' Reviews Map</h1>
        <p>Manchester: {total_registered_patients:,} &#128101; &middot; {registered_patient_rows} &#127973;</p>
        <p id="national-supplemental-note" class="hint" data-total-patients="{national_registered_patients}" data-total-practices="{len(national_supplementals)}">&#127988; National: {national_registered_patients:,} &#128101; &middot; {len(national_supplementals)} &#127973;</p>
      </div>
      <div class="control-group" id="score-source-control">
        <h2>Score Source</h2>
        <div class="segmented">
          <label title="Google"><input type="radio" name="score-source" value="google" checked><span>Google</span><span class="segmented-short">G</span></label>
          <label title="GP Survey"><input type="radio" name="score-source" value="survey"><span>GP Survey</span><span class="segmented-short">S</span></label>
          <label title="Gap"><input type="radio" name="score-source" value="gap"><span>Gap</span><span class="segmented-short">X</span></label>
        </div>
        <div id="gap-mode-control" class="gap-mode-control" hidden>
          <label class="overlay-toggle-label check-toggle" title="Normalise the raw Google-vs-survey gap by the cohort spread, so the page shows how unusual each practice's gap is relative to this map.">
            <input type="checkbox" id="normalize-gap-toggle" checked>
            <span>Normalise gap</span>
            <span class="check-toggle-mark">✓</span>
          </label>
          <p id="gap-mode-note" class="hint gap-mode-note">Converts the raw Google-vs-survey gap into a cohort z-score, showing how unusual each practice's gap is on this map.</p>
        </div>
        <p id="metric-description" class="hint"></p>
      </div>
      <div id="score-source-control-spacer" hidden aria-hidden="true"></div>
      <div class="control-group">
        <h2>Area overlays</h2>
        <div id="area-overlay-control">
          <label id="population-overlay-control" class="overlay-toggle-label" title="An estimated population / affected-people view. This is a rough catchment proxy, not a real practice boundary map."><input type="checkbox" id="voronoi-toggle"><span>Est. population</span><span class="overlay-toggle-icon">P</span></label>
          <label id="deprivation-overlay-control" class="overlay-toggle-label" title="Official 2025 deprivation deciles for the current catchment subset, shown by 2021 LSOA polygon."><input type="checkbox" id="deprivation-toggle"><span>Deprivation</span><span class="overlay-toggle-icon">D</span></label>
        </div>
        <div class="circle-sample-controls">
          <div class="circle-sample-actions">
            <label class="overlay-toggle-label is-active" id="city-circles-control" title="Show the predefined UK city sample circles used in the benchmark panel.">
              <input type="checkbox" id="city-circles-toggle" checked><span>City circles</span><span class="overlay-toggle-icon">C</span>
            </label>
            <button type="button" id="sample-circle-button" class="overlay-action-button" title="Click, then click the map to place a custom sample circle."><span>Place sample</span><span class="overlay-toggle-icon">S</span></button>
            <button type="button" id="clear-sample-circle-button" class="overlay-action-button" title="Remove the current custom sample circle."><span>Clear sample</span><span class="overlay-toggle-icon">X</span></button>
          </div>
          <label class="circle-radius-control" for="sample-circle-radius" hidden>
            <span class="circle-radius-label"><span>Sample radius</span><span id="sample-circle-radius-label">6 miles</span></span>
            <input type="range" id="sample-circle-radius" min="2" max="20" step="0.5" value="6">
          </label>
        </div>
        <p id="area-overlay-tip" class="hint"></p>
        <p id="sample-circle-note" class="hint"></p>
      </div>
      <div class="management-group">
        <h2>Management</h2>
        <p id="manager-hint" class="hint"></p>
        <div id="manager-list" class="manager-list"></div>
      </div>
    </div>
    <div id="map"></div>
    <button type="button" id="service-finder-map-button" class="overlay-action-button map-floating-action-button" title="Click, then click the map to place a practice lookup pin."><span>📍 Find Practices</span></button>
  </div>
  <div class="insights">
    <section class="panel comparison-panel service-finder-panel">
      <div class="service-finder-header">
        <div class="service-finder-title-wrap">
          <h2 id="service-finder-heading">Find My Best Practice</h2>
          <p class="service-finder-kicker">Pick a location to see available practices, best first.</p>
        </div>
        <div class="service-finder-actions">
          <button type="button" id="service-finder-place-button" class="overlay-action-button" title="Click, then click the map to place a practice lookup pin."><span>📍 Find Practices</span></button>
          <button type="button" id="service-finder-locate-button" class="overlay-action-button" title="Use browser geolocation for the lookup pin."><span>Use my location</span><span class="overlay-toggle-icon">L</span></button>
          <button type="button" id="service-finder-clear-button" class="overlay-action-button" title="Clear the current lookup pin."><span>Clear</span><span class="overlay-toggle-icon">X</span></button>
        </div>
      </div>
      <div class="service-finder-table-wrap" aria-live="polite">
        <table class="service-finder-table">
          <thead>
            <tr>
              <th><button type="button" class="service-finder-sort-button" data-service-finder-sort="practice"><span>Practice</span><span class="service-finder-sort-indicator"></span></button></th>
              <th><button type="button" class="service-finder-sort-button" data-service-finder-sort="distance"><span>Distance</span><span class="service-finder-sort-indicator"></span></button></th>
              <th><button type="button" class="service-finder-sort-button" data-service-finder-sort="google"><span>Google</span><span class="service-finder-sort-indicator"></span></button></th>
              <th><button type="button" class="service-finder-sort-button" data-service-finder-sort="survey"><span>Survey</span><span class="service-finder-sort-indicator"></span></button></th>
              <th><button type="button" class="service-finder-sort-button" data-service-finder-sort="reviews"><span>Review Count</span><span class="service-finder-sort-indicator"></span></button></th>
              <th><button type="button" class="service-finder-sort-button" data-service-finder-sort="patients"><span>Patients</span><span class="service-finder-sort-indicator"></span></button></th>
            </tr>
          </thead>
          <tbody id="service-finder-results"></tbody>
        </table>
      </div>
    </section>
    <section class="panel comparison-panel">
      <h2 id="comparison-heading">Interactive Benchmarks</h2>
      <p id="comparison-note" class="hint"></p>
      <div id="comparison-grid" class="comparison-grid"></div>
    </section>
    <section class="panel comparison-panel" id="gtd-trend-section">
      <h2 id="gtd-trend-heading">GTD Google Score Over Time</h2>
      <p id="gtd-score-trend-summary" class="hint"></p>
      <div class="trend-chart-layout">
        <div class="chart-frame">
          <svg id="gtd-score-trend-chart" viewBox="0 0 920 360" preserveAspectRatio="xMidYMid meet" aria-labelledby="gtd-score-trend-title" role="img">
            <title id="gtd-score-trend-title">Approximate cumulative Google rating over time for GTD practices</title>
          </svg>
          <div id="gtd-score-trend-overlay-legend" class="trend-overlay-legend" aria-label="Trend overlay legend"></div>
        </div>
        <div id="gtd-score-trend-legend" class="trend-legend" aria-label="GTD practice legend"></div>
      </div>
      <p class="chart-note" id="gtd-trend-note">Thin lines show each GTD practice's reconstructed cumulative Google rating by month. Faint dashed vertical lines mark the documented GTD takeover date for each practice. Only the first legend entry shows the GTD mean; selecting any named practice hides it. The green dashed line shows registered patients as a percentage of the GTD-wide average patient count for that year, with raw patient counts kept in the point labels, and the orange dashed line shows GP Survey overall-good %. Review dates are approximate month buckets inferred from Google relative-date labels at scrape time.</p>
    </section>
    <section class="panel comparison-panel">
      <div class="panel-heading-row">
        <h2 id="scatter-heading">Completion Rate vs Score</h2>
        <div class="treemap-mode-control">
          <div class="segmented" id="completion-scope-control">
            <label title="Manchester scope"><input type="radio" name="completion-scope" value="regional" checked><span>Manchester</span><span class="segmented-short">M</span></label>
            <label id="completion-scope-national-option" title="Nation scope"><input type="radio" name="completion-scope" value="national"><span id="completion-scope-national-label">Nations</span><span class="segmented-short" id="completion-scope-national-short">N</span></label>
          </div>
        </div>
      </div>
      <p id="scatter-summary" class="hint"></p>
      <div class="chart-frame">
        <svg id="scatterplot" viewBox="0 0 920 320" preserveAspectRatio="xMidYMid meet" aria-labelledby="scatter-title" role="img">
          <title id="scatter-title">Survey completion rate against selected score</title>
        </svg>
      </div>
      <p id="scatter-note" class="chart-note">Y-axis is GP Patient Survey completion rate. X-axis changes with the selected score source. The GP survey score itself is heavily bunched near the top end, mostly around or just below 80%, while Google reviews look much more organically spread. At these demarcations that suggests either practices dropping below roughly 70% overall-good are corrected fairly quickly before they persist in the survey, or the patient survey is not really capturing the lower half of possible experience that clearly exists in review text.</p>
    </section>
    <section class="panel comparison-panel">
      <h2 id="deprivation-heading">Manchester Score vs Deprivation</h2>
      <p id="deprivation-summary" class="hint"></p>
      <div class="chart-frame">
        <svg id="deprivation-chart" viewBox="0 0 920 320" preserveAspectRatio="xMidYMid meet" aria-labelledby="deprivation-title" role="img">
          <title id="deprivation-title">Selected score against area deprivation decile</title>
        </svg>
      </div>
      <p class="chart-note">X-axis is IMD 2025 decile (1 = most deprived). Y-axis changes with the selected score source, including the signed survey/Google gap.</p>
    </section>
    <section class="panel comparison-panel">
      <div class="panel-heading-row">
        <h2 id="national-deprivation-heading">National Score vs Deprivation</h2>
        <div class="treemap-mode-control">
          <label class="overlay-toggle-label check-toggle" title="Switch this national contrast panel from practice counts to summed registered-patient totals per deprivation/score cell.">
            <input type="checkbox" id="national-deprivation-population-toggle">
            <span>Sum Patients</span>
            <span class="check-toggle-mark">✓</span>
          </label>
        </div>
      </div>
      <p id="national-deprivation-summary" class="hint"></p>
      <div class="chart-frame">
        <svg id="national-deprivation-chart" viewBox="0 0 920 320" preserveAspectRatio="xMidYMid meet" aria-labelledby="national-deprivation-title" role="img">
          <title id="national-deprivation-title">National selected score against deprivation decile</title>
        </svg>
      </div>
      <p class="chart-note">This national contrast bins practices into deprivation-decile and score buckets. It can show either practice counts or summed registered-patient totals per cell, updates with the selected metric, and is only as complete as the persisted deprivation lookup.</p>
    </section>
    <section class="panel comparison-panel">
      <h2 id="patient-change-heading">Registered Patients Over Time</h2>
      <p id="patient-change-summary" class="hint"></p>
      <div class="chart-frame">
        <svg id="patient-change-chart" viewBox="0 0 920 320" preserveAspectRatio="xMidYMid meet" aria-labelledby="patient-change-title" role="img">
          <title id="patient-change-title">Registered patients over time, coloured by current selected score</title>
        </svg>
      </div>
      <p class="chart-note">X-axis is year. Y-axis is registered patients. Thin lines show practice list-size trajectories, coloured by the current selected score; the dashed grey line is the Manchester-wide average practice count for each year.</p>
      <p id="patient-change-footnote" class="chart-note" hidden></p>
    </section>
    <section class="panel comparison-panel">
      <div class="panel-heading-row">
        <h2 id="patient-treemap-heading">Patient Count Treemap</h2>
        <div class="treemap-mode-control">
          <label class="overlay-toggle-label check-toggle" title="Flatten whole-dataset growth so the treemap shows how each practice's share of the Manchester patient pool changes over time, rather than absolute patient-count growth.">
            <input type="checkbox" id="normalize-patient-change-toggle">
            <span>Flatten for Population</span>
            <span class="check-toggle-mark">✓</span>
          </label>
        </div>
      </div>
      <p id="patient-treemap-summary" class="hint"></p>
      <div class="player-controls">
        <button type="button" id="patient-treemap-play" class="legend-collapse player-button" aria-pressed="false">Play</button>
        <input type="range" id="patient-treemap-year" class="player-scrubber" min="0" max="0" step="1" value="0" aria-label="Treemap year">
        <div id="patient-treemap-year-label" class="player-year-label">Year</div>
      </div>
      <div class="chart-frame">
        <svg id="patient-treemap-chart" viewBox="0 0 920 420" preserveAspectRatio="xMidYMid meet" aria-labelledby="patient-treemap-title" role="img">
          <title id="patient-treemap-title">Patient count treemap by management group and current selected score</title>
        </svg>
        <svg id="patient-total-chart" viewBox="0 0 920 118" preserveAspectRatio="xMidYMid meet" aria-labelledby="patient-total-title" role="img">
          <title id="patient-total-title">Total registered patients across the full dataset over time</title>
        </svg>
      </div>
      <p class="chart-note">This uses a fixed-scale grouped strip-treemap rather than re-squarifying each frame, so practice blocks mostly grow and shrink in place. Block area is registered patients in the chosen year, on the same patient-to-pixel scale for all years; colour and score label use the currently selected metric. Independent / other is split into Google review-score bands so better and worse destinations can be compared. The small strip-chart below shows the whole-dataset registered-patient total over the same years, alongside the dataset-wide average Google review score by year. Reviews appear to improve slightly across the Manchester dataset since 2021/2022 despite the rapidly growing population.</p>
    </section>
    <section class="panel comparison-panel place-benchmark-section">
      <h2 id="place-benchmark-heading">Nation and City Benchmarks</h2>
      <p id="place-benchmark-note" class="hint"></p>
      <div class="place-benchmark-block">
        <div class="panel-heading-row">
          <h3 id="nation-benchmark-heading" class="place-benchmark-subheading">Nations</h3>
        </div>
        <div id="nation-benchmark-grid" class="place-benchmark-grid nation-grid"></div>
      </div>
      <div class="place-benchmark-block">
        <div class="panel-heading-row">
          <h3 id="city-benchmark-heading" class="place-benchmark-subheading">UK city circles</h3>
        </div>
        <div id="city-benchmark-grid" class="place-benchmark-grid"></div>
      </div>
    </section>
    <section class="panel comparison-panel">
      <div class="panel-heading-row">
        <h2 id="rating-survey-heading">Google Rating vs Patient Survey</h2>
        <div class="treemap-mode-control">
          <div class="segmented" id="rating-survey-mode-control">
            <label title="Benchmark regions"><input type="radio" name="rating-survey-mode" value="regions" checked><span>Regions</span><span class="segmented-short">R</span></label>
            <label title="Individual practices"><input type="radio" name="rating-survey-mode" value="practices"><span>Practices</span><span class="segmented-short">P</span></label>
          </div>
        </div>
      </div>
      <p id="rating-survey-summary" class="hint"></p>
      <div class="chart-wrap">
        <svg id="rating-survey-chart" viewBox="0 0 920 320" preserveAspectRatio="xMidYMid meet" aria-labelledby="rating-survey-title" role="img">
          <title id="rating-survey-title">Google rating against patient survey overall good score</title>
        </svg>
      </div>
      <p id="rating-survey-note" class="chart-note">This is just an eyeball correlation check across all loaded rows with both values. England and Scotland are mixed here on purpose, even though GPPS and HACE are not identical measures.</p>
    </section>
    <section class="panel comparison-panel">
      <h2>Conclusions</h2>
      <p>This page suggests GTD is the weakest-performing management group in this catchment, with New Bank sitting at or near the bottom even within the deprived groups it belongs to. On both public reviews and GP Patient Survey measures, GTD has too many poor-performing practices relative to the wider sample.</p>
      <p>The Google-versus-survey gap matters because GTD practices often show a larger mismatch than typical surgeries, while survey return rates are low enough to leave room for hidden dissatisfaction. New Bank looks off-curve rather than merely unlucky within the normal local range.</p>
      <p>The deprivation views also point to a real but limited dataset-wide lean: more deprived areas do tend to have somewhat worse review and survey distributions. That said, this page does not suggest that the whole NHS only fails poorer areas or that poor areas only contain poor-quality practices (it's surprisingly a little more evenly distributed than I expected). Wider regional or national sampling could test how much of that lean is structural versus local.</p>
      <p>The practices sampled here also saw total registered patients rise by about 514,762 between 2018 and 2026, roughly 20.5% growth across the period. That is a significant resource-pressure context in its own right, so this overall pattern suggests a region that in many places responded surprisingly well to new demand, especially through years of reduced funding: some practices did not just maintain patient-facing scores, but improved them.</p>
      <p>The practical conclusion is local rather than fatalistic. National context matters, but the strongest actionable result here is that GTD, and especially New Bank, are performing worse than most of the sample even after allowing for deprivation.</p>
      <p>Change across GTD is both plausible and necessary, and in more deprived areas the benefit of improvement is larger because easy access matters most where health need is greatest.</p>
    </section>
    {data_pool_report_html}
  </div>
</div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@turf/turf@7.2.0/turf.min.js"></script>
<script>window.NATIONAL_PRACTICE_SUPPLEMENTALS = window.NATIONAL_PRACTICE_SUPPLEMENTALS || [];</script>
<script src="{NATIONAL_SUPPLEMENTAL_SCRIPT_NAME}"></script>
<script>
const rows = {json.dumps(client_markers)};
const nationalSupplementals = Array.isArray(window.NATIONAL_PRACTICE_SUPPLEMENTALS) ? window.NATIONAL_PRACTICE_SUPPLEMENTALS : [];
const nationOrder = {json.dumps(NATION_ORDER)};
const cityCatchments = {json.dumps(CITY_CATCHMENTS)};
const compositeRegionDefinitions = {json.dumps(composite_region_definitions)};
const MANCHESTER_CATCHMENT_BUNDLE_NAME = {json.dumps(MANCHESTER_CATCHMENT_BUNDLE_NAME)};
const MANCHESTER_CATCHMENT_MIN_ZOOM = 12;
const manchesterCatchmentBundleMeta = {json.dumps(manchester_catchment_bundle)};
const northSouthDivide = {{
  west: {{ lat: 51.62, lon: -3.05 }},
  east: {{ lat: 52.98, lon: 0.52 }},
}};
const gtdGoogleTimeseries = {json.dumps(gtd_google_timeseries)};
const gtdSurveyTimeseries = {json.dumps(gtd_survey_timeseries)};
const patientCountsByYear = {json.dumps(patient_counts_by_year)};
const patientChangeAnalysis = {json.dumps(patient_change_analysis)};
const knownManagementCompanies = {json.dumps(known_management_companies)};
const deprivationGeojson = {json.dumps(deprivation_geojson, separators=(",", ":"))};
const practiceDeprivationLookup = {json.dumps(practice_deprivation, separators=(",", ":"))};
const allPracticeDeprivationLookup = {json.dumps(all_practice_deprivation, separators=(",", ":"))};
const rowsByCode = new Map(rows.map((row) => [row.code, row]));
const NEW_BANK_CODE = 'Y02960';
const BASELINE_MANAGEMENT_COMPANY = 'GTD Healthcare';
const TREND_DEFAULT_CONTEXT_CODE = '__gtd_mean_with_new_bank__';
const LOCAL_RADIUS_MILES = 2.5;
const SIDEBAR_COLLAPSE_KEY = 'mapSidebarCollapsed';
const NATIONAL_SUPPLEMENTAL_MIN_ZOOM = 8;
const dataBbox = (() => {{
  const lons = rows.map(r => Number(r.lon));
  const lats = rows.map(r => Number(r.lat));
  const pad = 0.12;
  return [
    Math.min(...lons) - pad,
    Math.min(...lats) - pad,
    Math.max(...lons) + pad,
    Math.max(...lats) + pad
  ];
}})();
const map = L.map('map').setView([{center_lat:.6f}, {center_lon:.6f}], 11);
const markerLayer = L.layerGroup().addTo(map);
const nationalMarkerLayer = L.layerGroup().addTo(map);
const cityCircleLayer = L.layerGroup().addTo(map);
const sampleCircleLayer = L.layerGroup().addTo(map);
const catchmentOutlineLayer = L.layerGroup().addTo(map);
const serviceFinderPointLayer = L.layerGroup().addTo(map);
let voronoiLayer = null;
let deprivationLayer = null;
const nationalPane = map.createPane('nationalSupplementals');
nationalPane.style.zIndex = '350';
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
  maxZoom: 18,
  attribution: '&copy; OpenStreetMap contributors'
}}).addTo(map);
const managementShapePool = ['triangle', 'square', 'diamond', 'hexagon', 'pentagon'];
const selectedManagementCompanies = new Set([BASELINE_MANAGEMENT_COMPANY]);
let activeMetric = 'google';
let activeGapMode = 'normalized';
let activeAreaOverlay = null;
let focusedPracticeCode = NEW_BANK_CODE;
let pinnedTrendPracticeCode = TREND_DEFAULT_CONTEXT_CODE;
let hoveredTrendPracticeCode = null;
let trendLegendHoverSuppressed = false;
let sidebarCollapsed = false;
let patientTreemapYearIndex = null;
let patientTreemapPlaying = false;
let hoveredCatchmentCode = null;
const persistentCatchmentCodes = new Set();
let manchesterCatchmentIndex = null;
let manchesterCatchmentLoadPromise = null;
let serviceFinderArmed = false;
let serviceFinderPoint = null;
let serviceFinderLocationLabel = '';
let serviceFinderEmptyMessage = '';
let serviceFinderButtonFlash = '';
let serviceFinderButtonFlashTimer = null;
let serviceFinderDragActive = false;
let serviceFinderDragGhost = null;
let serviceFinderSortKey = 'google';
let serviceFinderSortDirection = 'desc';
let patientTreemapTimer = null;
let patientTreemapNormalizeForChange = true;
let nationalDeprivationUsePopulation = false;
let completionScatterScope = 'regional';
const completionScatterNationOrder = (() => {{
  const preferredOrder = ['england', 'scotland', 'wales', 'northern_ireland'];
  const allRows = rows.concat(nationalSupplementals);
  return preferredOrder.filter((nation) => allRows.some((row) => {{
    if (String(row?.nation || '').trim().toLowerCase() !== nation) return false;
    return numericOrNull(row.survey_completion_rate_percent) !== null;
  }}));
}})();
let completionScatterNationIndex = 0;
let ratingSurveyMode = 'regions';
let showCityCircles = true;
let sampleCircleArmed = false;
let sampleCircleRadiusMiles = 6;
let sampleCircleCenter = null;
const GTD_MEAN_COLOR = '#b23322';

const metricConfigs = {{
  google: {{
    title: 'Google rating',
    description: 'Google data here is from this repo\\'s merged review collection.',
    value(row) {{
      return numericOrNull(row.google_score);
    }},
    compareValue(_row) {{
      return null;
    }},
    markerLabel(row) {{
      const value = this.value(row);
      return value === null ? '?' : value.toFixed(1);
    }},
    markerColor(row) {{
      const value = this.value(row);
      if (value === null) return '#9aa0a6';
      if (value < 2) return '#c3472f';
      if (value < 3) return '#dc8c23';
      if (value < 4) return '#d2b529';
      if (value < 4.5) return '#4c9a52';
      return '#1c7c54';
    }},
    scaleCount(row) {{
      const count = numericOrNull(row.google_count);
      return count !== null && count > 0 ? count : 0;
    }},
    averageLabel(value) {{
      return value === null ? '?' : value.toFixed(2);
    }},
    axisLabel: 'Google rating',
    axisMin: 0,
    axisMax: 5
  }},
  survey: {{
    title: 'GP survey overall good %',
    description: 'GP Survey uses the official overall-experience-as-good percentage.',
    value(row) {{
      return numericOrNull(row.survey_overall_good_percent);
    }},
    compareValue(row) {{
      return numericOrNull(row.survey_overall_good_ics_percent);
    }},
    markerLabel(row) {{
      const value = this.value(row);
      return value === null ? '?' : String(Math.round(value));
    }},
    markerColor(row) {{
      const value = this.value(row);
      if (value === null) return '#9aa0a6';
      if (value < 50) return '#c3472f';
      if (value < 60) return '#dc8c23';
      if (value < 70) return '#d2b529';
      if (value < 80) return '#4c9a52';
      return '#1c7c54';
    }},
    scaleCount(row) {{
      const count = surveyParticipationCount(row);
      return count !== null && count > 0 ? count : 0;
    }},
    averageLabel(value) {{
      return value === null ? '?' : `${{value.toFixed(0)}}%`;
    }},
    axisLabel: 'GP survey overall-good %',
    axisMin: 0,
    axisMax: 100
  }},
  gap: {{
    title: 'Survey/Google gap',
    value(row) {{
      return gapValue(row, {{ suppressSmall: true }});
    }},
    compareValue(_row) {{
      return null;
    }},
    markerLabel(row) {{
      const value = this.value(row);
      return value === null ? '?' : value.toFixed(1);
    }},
    markerColor(row) {{
      const value = this.value(row);
      if (value === null) return '#9aa0a6';
      if (activeGapMode === 'normalized') {{
        if (value >= 0.75) return '#1c7c54';
        if (value >= 0.25) return '#4c9a52';
        if (value > -0.25) return '#d2b529';
        if (value > -0.75) return '#dc8c23';
        return '#c3472f';
      }}
      if (value >= 1.0) return '#1c7c54';
      if (value >= 0.5) return '#4c9a52';
      if (value > -0.5) return '#d2b529';
      if (value > -1.0) return '#dc8c23';
      return '#c3472f';
    }},
    scaleCount(row) {{
      const google = numericOrNull(row.google_count);
      const survey = surveyParticipationCount(row);
      const googleValid = google !== null && google > 0;
      const surveyValid = survey !== null && survey > 0;
      if (googleValid && surveyValid) return Math.min(google, survey);
      if (googleValid) return google;
      if (surveyValid) return survey;
      return 0;
    }},
    averageLabel(value) {{
      return value === null ? '?' : value.toFixed(2);
    }},
    axisLabel: '',
    axisMin: -2.5,
    axisMax: 2.5
  }}
}};

function numericOrNull(value) {{
  if (value === null || value === undefined) return null;
  if (typeof value === 'string' && value.trim() === '') return null;
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : null;
}}

function roundApproxPatientsPerYear(value) {{
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return null;
  const magnitude = Math.abs(numeric);
  if (magnitude >= 2000) return Math.round(numeric / 100) * 100;
  if (magnitude >= 500) return Math.round(numeric / 50) * 50;
  if (magnitude >= 100) return Math.round(numeric / 25) * 25;
  return Math.round(numeric / 10) * 10;
}}

function surveyParticipationCount(row) {{
  const surveySentBack = numericOrNull(row.survey_sent_back);
  if (surveySentBack !== null && surveySentBack > 0) return surveySentBack;
  const overallResponses = numericOrNull(row.responses_for_overall_question);
  if (overallResponses !== null && overallResponses > 0) return overallResponses;
  const responseCount = numericOrNull(row.number_of_responses);
  if (responseCount !== null && responseCount > 0) return responseCount;
  return null;
}}

function metricColorForValue(metricName, value) {{
  if (value === null || value === undefined || !Number.isFinite(Number(value))) return '#9aa0a6';
  const numeric = Number(value);
  if (metricName === 'google') {{
    if (numeric < 2) return '#c3472f';
    if (numeric < 3) return '#dc8c23';
    if (numeric < 4) return '#d2b529';
    if (numeric < 4.5) return '#4c9a52';
    return '#1c7c54';
  }}
  if (metricName === 'survey') {{
    if (numeric < 50) return '#c3472f';
    if (numeric < 60) return '#dc8c23';
    if (numeric < 70) return '#d2b529';
    if (numeric < 80) return '#4c9a52';
    return '#1c7c54';
  }}
  if (activeGapMode === 'normalized') {{
    if (numeric >= 0.75) return '#1c7c54';
    if (numeric >= 0.25) return '#4c9a52';
    if (numeric > -0.25) return '#d2b529';
    if (numeric > -0.75) return '#dc8c23';
    return '#c3472f';
  }}
  if (numeric >= 1.0) return '#1c7c54';
  if (numeric >= 0.5) return '#4c9a52';
  if (numeric > -0.5) return '#d2b529';
  if (numeric > -1.0) return '#dc8c23';
  return '#c3472f';
}}

function standardDeviation(values) {{
  if (!values.length) return null;
  const average = mean(values);
  if (average === null) return null;
  const variance = values.reduce((sum, value) => sum + ((value - average) ** 2), 0) / values.length;
  return variance > 0 ? Math.sqrt(variance) : 0;
}}

function gapInputs(row) {{
  const google = numericOrNull(row.google_score);
  const googleCount = numericOrNull(row.google_count);
  const surveyPercent = numericOrNull(row.survey_overall_good_percent);
  const surveyResponses = surveyParticipationCount(row);
  if (google === null || surveyPercent === null) return null;
  if (googleCount === null || googleCount <= 0) return null;
  if (surveyResponses === null || surveyResponses <= 0) return null;
  return {{
    google,
    surveyPercent,
    surveyStars: surveyPercent / 20,
  }};
}}

function gapNormalisationCohortKey(row) {{
  const nation = String(row?.nation || '').trim().toLowerCase();
  return nation || 'all';
}}

const gapNormalisationStatsByCohort = (() => {{
  const buckets = new Map();
  for (const row of rows.concat(nationalSupplementals)) {{
    const inputs = gapInputs(row);
    if (!inputs) continue;
    const key = gapNormalisationCohortKey(row);
    if (!buckets.has(key)) buckets.set(key, []);
    buckets.get(key).push(inputs.google - inputs.surveyStars);
  }}
  const stats = new Map();
  for (const [key, values] of buckets.entries()) {{
    stats.set(key, {{
      rawGapMean: mean(values),
      rawGapStd: standardDeviation(values),
      sampleSize: values.length,
    }});
  }}
  const allValues = Array.from(buckets.values()).flat();
  stats.set('all', {{
    rawGapMean: mean(allValues),
    rawGapStd: standardDeviation(allValues),
    sampleSize: allValues.length,
  }});
  return stats;
}})();

function absoluteGapValue(row, suppressSmall = true) {{
  const inputs = gapInputs(row);
  if (!inputs) return null;
  const gap = inputs.google - inputs.surveyStars;
  return suppressSmall && Math.abs(gap) < 1 ? null : gap;
}}

function normalizedGapValue(row, suppressSmall = true) {{
  const inputs = gapInputs(row);
  if (!inputs) return null;
  const cohortKey = gapNormalisationCohortKey(row);
  const cohortStats = gapNormalisationStatsByCohort.get(cohortKey) || gapNormalisationStatsByCohort.get('all');
  if (!cohortStats) return null;
  const rawGapStd = cohortStats.rawGapStd;
  if (!rawGapStd) return null;
  const rawGap = inputs.google - inputs.surveyStars;
  const gap = (rawGap - cohortStats.rawGapMean) / rawGapStd;
  return suppressSmall && Math.abs(gap) < 1 ? null : gap;
}}

function gapValue(row, options = {{}}) {{
  const suppressSmall = options.suppressSmall !== false;
  return activeGapMode === 'normalized'
    ? normalizedGapValue(row, suppressSmall)
    : absoluteGapValue(row, suppressSmall);
}}

function gapAxisInfo() {{
  if (activeGapMode !== 'normalized') {{
    return {{
      label: 'Google minus survey-equivalent stars (positive = Google higher)',
      min: -2.5,
      max: 2.5,
      magnitudeLabel: 'Survey/Google gap magnitude (abs, stars)',
      magnitudeTicks: [0, 0.5, 1.0, 1.5, 2.0, 2.5],
    }};
  }}
  const values = rows
    .map((row) => gapValue(row, {{ suppressSmall: false }}))
    .filter((value) => value !== null && Number.isFinite(value));
  const maxAbs = values.length ? Math.max(...values.map((value) => Math.abs(value))) : 1;
  const roundedMax = Math.max(1, Math.ceil(maxAbs * 2) / 2);
  const ticks = [];
  const step = roundedMax <= 2 ? 0.5 : 1;
  for (let tick = 0; tick <= roundedMax + 0.001; tick += step) {{
    ticks.push(Number(tick.toFixed(2)));
  }}
  return {{
    label: 'Normalised Google-minus-survey gap (within-nation z-score, positive = Google higher)',
    min: -roundedMax,
    max: roundedMax,
    magnitudeLabel: 'Survey/Google gap magnitude (abs, normalised z-score)',
    magnitudeTicks: ticks,
  }};
}}

function gapDescription() {{
  if (activeGapMode === 'normalized') {{
    return 'Normalised mode: the raw Google-minus-survey gap is converted to a within-nation z-score. Positive means Google reviews sit above the survey-equivalent score for that nation-relative cohort; negative means the survey-equivalent score sits above Google, which this view treats as worse.';
  }}
  return 'Indicator only: survey overall-good % is scaled to 0-5 and compared with Google. Positive means Google reviews are higher than the survey-equivalent score; negative means the survey-equivalent score is higher than Google, which this view treats as worse.';
}}

const gtdAveragePatientCountByYear = Object.fromEntries(
  Object.entries(patientCountsByYear || {{}}).map(([year, counts]) => {{
    const values = Object.values(counts || {{}})
      .map((value) => numericOrNull(value))
      .filter((value) => value !== null && value > 0);
    return [year, values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : null];
  }})
);

function maxRegisteredPatientCount() {{
  return Math.max(0, ...rows.map((row) => numericOrNull(row.registered_patient_count) || 0));
}}

function sizeValueForRow(row) {{
  const count = numericOrNull(row.registered_patient_count);
  return count !== null && count > 0 ? count : 0;
}}

function averageMetric(rowsForCompany, metricName) {{
  const metric = metricConfigs[metricName];
  const values = rowsForCompany
    .map((row) => metric.value(row))
    .filter((value) => value !== null);
  if (!values.length) return null;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}}

const managementCompanies = knownManagementCompanies.map((name) => {{
  const companyRows = rows.filter((row) => row.management_company === name);
  return {{
    name,
    count: companyRows.length,
    rows: companyRows
  }};
}});

function patientScaleForRow(row) {{
  const count = numericOrNull(row.registered_patient_count);
  const maxCount = maxRegisteredPatientCount();
  if (!Number.isFinite(count) || count <= 0) return 0.7;
  if (maxCount <= 0) return 0.7;
  const normalized = Math.log1p(count) / Math.log1p(maxCount);
  return 0.5 + (normalized ** 0.7) * 0.7;
}}

function mapScaleForRow(row) {{
  return patientScaleForRow(row);
}}

function nationalMapScaleForRow(row) {{
  return Math.max(0.52, patientScaleForRow(row) * 0.82);
}}

function mapRowsForOverlays() {{
  return rows.filter((row) => Number.isFinite(Number(row.lat)) && Number.isFinite(Number(row.lon)));
}}

function shapeAssignment() {{
  const selected = managementCompanies
    .filter((company) => selectedManagementCompanies.has(company.name))
    .slice(0, managementShapePool.length);
  const assignments = new Map();
  selected.forEach((company, index) => assignments.set(company.name, managementShapePool[index]));
  return assignments;
}}

function baseShapeMetrics(shape) {{
  if (shape === 'triangle') return {{ width: 42, height: 36, anchorX: 21, anchorY: 30, popupY: -14 }};
  if (shape === 'square') return {{ width: 34, height: 34, anchorX: 17, anchorY: 17, popupY: -14 }};
  if (shape === 'diamond') return {{ width: 34, height: 34, anchorX: 17, anchorY: 17, popupY: -14 }};
  if (shape === 'hexagon') return {{ width: 38, height: 34, anchorX: 19, anchorY: 17, popupY: -14 }};
  if (shape === 'pentagon') return {{ width: 38, height: 36, anchorX: 19, anchorY: 18, popupY: -14 }};
  return {{ width: 34, height: 34, anchorX: 17, anchorY: 17, popupY: -14 }};
}}

function markerSvg(shape, color, label, fontSize, missing, highlighted = false) {{
  const stroke = highlighted ? '#111111' : 'rgba(0,0,0,0.28)';
  const strokeWidth = highlighted ? '2.8' : '1.2';
  const textColor = missing ? '#f4f4f4' : '#ffffff';
  if (shape === 'triangle') {{
    return `
      <svg class="marker-svg" width="100%" height="100%" viewBox="0 0 42 36" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <polygon points="21,1 41,35 1,35" fill="${{color}}" stroke="${{stroke}}" stroke-width="${{strokeWidth}}" />
        <text x="21" y="24" text-anchor="middle" dominant-baseline="middle" fill="${{textColor}}" font-size="${{fontSize}}" font-weight="700" font-family="ui-sans-serif, system-ui, sans-serif">${{label}}</text>
      </svg>
    `;
  }}
  if (shape === 'square') {{
    return `
      <svg class="marker-svg" width="100%" height="100%" viewBox="0 0 34 34" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <rect x="1" y="1" width="32" height="32" fill="${{color}}" stroke="${{stroke}}" stroke-width="${{strokeWidth}}" />
        <text x="17" y="18" text-anchor="middle" dominant-baseline="middle" fill="${{textColor}}" font-size="${{fontSize}}" font-weight="700" font-family="ui-sans-serif, system-ui, sans-serif">${{label}}</text>
      </svg>
    `;
  }}
  if (shape === 'diamond') {{
    return `
      <svg class="marker-svg" width="100%" height="100%" viewBox="0 0 34 34" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <polygon points="17,1 33,17 17,33 1,17" fill="${{color}}" stroke="${{stroke}}" stroke-width="${{strokeWidth}}" />
        <text x="17" y="18" text-anchor="middle" dominant-baseline="middle" fill="${{textColor}}" font-size="${{fontSize}}" font-weight="700" font-family="ui-sans-serif, system-ui, sans-serif">${{label}}</text>
      </svg>
    `;
  }}
  if (shape === 'hexagon') {{
    return `
      <svg class="marker-svg" width="100%" height="100%" viewBox="0 0 38 34" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <polygon points="10,1 28,1 37,17 28,33 10,33 1,17" fill="${{color}}" stroke="${{stroke}}" stroke-width="${{strokeWidth}}" />
        <text x="19" y="18" text-anchor="middle" dominant-baseline="middle" fill="${{textColor}}" font-size="${{fontSize}}" font-weight="700" font-family="ui-sans-serif, system-ui, sans-serif">${{label}}</text>
      </svg>
    `;
  }}
  if (shape === 'pentagon') {{
    return `
      <svg class="marker-svg" width="100%" height="100%" viewBox="0 0 38 36" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <polygon points="19,1 37,14 31,35 7,35 1,14" fill="${{color}}" stroke="${{stroke}}" stroke-width="${{strokeWidth}}" />
        <text x="19" y="20" text-anchor="middle" dominant-baseline="middle" fill="${{textColor}}" font-size="${{fontSize}}" font-weight="700" font-family="ui-sans-serif, system-ui, sans-serif">${{label}}</text>
      </svg>
    `;
  }}
  return `
    <svg class="marker-svg" width="100%" height="100%" viewBox="0 0 34 34" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <circle cx="17" cy="17" r="16" fill="${{color}}" stroke="${{stroke}}" stroke-width="${{strokeWidth}}" />
      <text x="17" y="18" text-anchor="middle" dominant-baseline="middle" fill="${{textColor}}" font-size="${{fontSize}}" font-weight="700" font-family="ui-sans-serif, system-ui, sans-serif">${{label}}</text>
    </svg>
  `;
}}

function renderMetricLegend() {{
  const metric = metricConfigs[activeMetric];
  document.getElementById('metric-description').textContent =
    activeMetric === 'gap' ? gapDescription() : metric.description;
  document.getElementById('metric-description').className = 'hint metric-note';
  const gapModeControl = document.getElementById('gap-mode-control');
  const normalizeToggle = document.getElementById('normalize-gap-toggle');
  const gapModeNote = document.getElementById('gap-mode-note');
  const gapModeActive = activeMetric === 'gap';
  gapModeControl.hidden = !gapModeActive;
  normalizeToggle.checked = activeGapMode === 'normalized';
  gapModeControl.querySelector('label').classList.toggle('is-active', gapModeActive && activeGapMode === 'normalized');
  gapModeNote.textContent = activeGapMode === 'normalized'
    ? 'Converts the raw Google-vs-survey gap into a cohort z-score, showing how unusual each practice\\'s gap is on this map.'
    : 'Compares Google stars directly with survey-equivalent stars (survey overall-good % mapped to 0-5).';
}}

function updateSidebarState() {{
  const stage = document.querySelector('.map-stage');
  const button = document.getElementById('legend-collapse');
  stage.classList.toggle('is-collapsed', sidebarCollapsed);
  button.setAttribute('aria-pressed', sidebarCollapsed ? 'true' : 'false');
  button.setAttribute('title', sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar');
  button.textContent = sidebarCollapsed ? '>' : '<';
}}

function clearOverlayLayers() {{
  markerLayer.clearLayers();
  if (voronoiLayer) {{
    map.removeLayer(voronoiLayer);
    voronoiLayer = null;
  }}
  if (deprivationLayer) {{
    map.removeLayer(deprivationLayer);
    deprivationLayer = null;
  }}
}}

function updateAreaOverlayControls() {{
  const populationChecked = activeAreaOverlay === 'population';
  const deprivationChecked = activeAreaOverlay === 'deprivation';
  const populationToggle = document.getElementById('voronoi-toggle');
  const deprivationToggle = document.getElementById('deprivation-toggle');
  const tip = document.getElementById('area-overlay-tip');
  populationToggle.checked = populationChecked;
  deprivationToggle.checked = deprivationChecked;
  document.getElementById('population-overlay-control').classList.toggle('is-active', populationChecked);
  document.getElementById('deprivation-overlay-control').classList.toggle('is-active', deprivationChecked);
  if (populationChecked) {{
    tip.textContent = 'Approximate catchment cells built from practice locations and coloured by the active score metric. This is a rough vibes layer, not a real practice-boundary map.';
  }} else if (deprivationChecked) {{
    tip.textContent = 'Official 2025 IMD deciles for the current map catchment, shown by small-area LSOA polygon. This is area deprivation, not a practice-performance score.';
  }} else {{
    tip.textContent = '';
  }}
}}

function voronoiGhostPoints() {{
  const [minLon, minLat, maxLon, maxLat] = dataBbox;
  const width = maxLon - minLon;
  const height = maxLat - minLat;
  const lonInset = width * 0.035;
  const latInset = height * 0.035;
  const sideSteps = 6;
  const points = [];
  let ghostIndex = 0;

  for (let step = 0; step <= sideSteps; step += 1) {{
    const t = step / sideSteps;
    const lon = minLon + width * t;
    const lat = minLat + height * t;
    points.push(turf.point([lon, minLat + latInset], {{ code: `__ghost_top_${{ghostIndex++}}` }}));
    points.push(turf.point([lon, maxLat - latInset], {{ code: `__ghost_bottom_${{ghostIndex++}}` }}));
    points.push(turf.point([minLon + lonInset, lat], {{ code: `__ghost_left_${{ghostIndex++}}` }}));
    points.push(turf.point([maxLon - lonInset, lat], {{ code: `__ghost_right_${{ghostIndex++}}` }}));
  }}

  return points;
}}

function voronoiPoints() {{
  const rowsForMap = mapRowsForOverlays();
  const duplicateCounts = new Map();
  const realPoints = rowsForMap.map((row) => {{
    const key = `${{Number(row.lat).toFixed(6)}},${{Number(row.lon).toFixed(6)}}`;
    const duplicateIndex = duplicateCounts.get(key) || 0;
    duplicateCounts.set(key, duplicateIndex + 1);
    const angle = duplicateIndex * 2.399963229728653;
    const offset = duplicateIndex === 0 ? 0 : 0.00018 * Math.ceil(duplicateIndex / 2);
    const lon = Number(row.lon) + Math.cos(angle) * offset;
    const lat = Number(row.lat) + Math.sin(angle) * offset;
    return turf.point([lon, lat], {{ code: row.code }});
  }});
  return realPoints.concat(voronoiGhostPoints());
}}

function voronoiCentroidByCode() {{
  const points = voronoiPoints();
  if (!points.length) return new Map();
  const fc = turf.featureCollection(points);
  const polygons = turf.voronoi(fc, {{ bbox: dataBbox }});
  const rowByCode = new Map(rows.map((row) => [row.code, row]));
  const centroidByCode = new Map();
  (polygons?.features || []).forEach((feature) => {{
    const code = feature?.properties?.code;
    if (code && rowByCode.has(code)) {{
      const centroid = turf.centroid(feature);
      const [lon, lat] = centroid.geometry.coordinates;
      centroidByCode.set(code, [lat, lon]);
    }}
  }});
  return centroidByCode;
}}

function renderVoronoi() {{
  const points = voronoiPoints();
  if (!points.length) return;
  const fc = turf.featureCollection(points);
  const polygons = turf.voronoi(fc, {{ bbox: dataBbox }});
  const rowByCode = new Map(rows.map((row) => [row.code, row]));
  const features = (polygons && polygons.features ? polygons.features : [])
    .filter((feature) => feature && feature.properties && feature.properties.code && rowByCode.has(feature.properties.code))
    .map((feature) => {{
      const row = rowByCode.get(feature.properties.code);
      feature.properties.popupMarkup = popupMarkup(row);
      feature.properties.code = row.code;
      feature.properties.color = metricConfigs[activeMetric].markerColor(row);
      return feature;
    }});
  if (!features.length) return;
  voronoiLayer = L.geoJSON({{ type: 'FeatureCollection', features }}, {{
    style: (feature) => {{
      return {{
        color: 'rgba(26,28,26,0.26)',
        weight: 1,
        fillColor: feature.properties.color || '#9aa0a6',
        fillOpacity: 0.42
      }};
    }},
    onEachFeature: (feature, layer) => {{
      const row = rowByCode.get(feature.properties.code);
      layer.bindPopup(feature.properties.popupMarkup || '');
      layer.on('click', () => {{
        if (row) focusRow(row);
      }});
    }}
  }});
  voronoiLayer.addTo(map);
  voronoiLayer.bringToBack();
}}

function deprivationFillColor(decile) {{
  if (decile === null) return '#9aa0a6';
  if (decile <= 1) return '#8e1f1b';
  if (decile <= 2) return '#b93522';
  if (decile <= 4) return '#d86a1b';
  if (decile <= 6) return '#d2b529';
  if (decile <= 8) return '#72a847';
  return '#1c7c54';
}}

function deprivationPopupMarkup(properties) {{
  const decile = numericOrNull(properties.imd_decile);
  const rank = numericOrNull(properties.imd_rank);
  const score = numericOrNull(properties.imd_score);
  const healthDecile = numericOrNull(properties.health_decile);
  const population = numericOrNull(properties.population_2022);
  return [
    `<strong>${{properties.lsoa21nm || properties.lsoa21cd || 'LSOA'}}</strong>`,
    `<div>IMD 2025 decile: ${{decile === null ? '?' : decile}} / 10 (1 = most deprived)</div>`,
    `<div>IMD rank: ${{rank === null ? '?' : rank.toLocaleString('en-GB')}}</div>`,
    `<div>IMD score: ${{score === null ? '?' : score.toFixed(3)}}</div>`,
    `<div>Health deprivation decile: ${{healthDecile === null ? '?' : healthDecile}} / 10</div>`,
    `<div>Population (mid-2022): ${{population === null ? '?' : population.toLocaleString('en-GB')}}</div>`,
  ].join('');
}}

function renderDeprivation() {{
  const features = (deprivationGeojson && deprivationGeojson.features ? deprivationGeojson.features : []).map((feature) => {{
    const nextFeature = {{
      ...feature,
      properties: {{
        ...(feature.properties || {{}}),
        popupMarkup: deprivationPopupMarkup(feature.properties || {{}})
      }}
    }};
    return nextFeature;
  }});
  if (!features.length) return;
  deprivationLayer = L.geoJSON({{ type: 'FeatureCollection', features }}, {{
    style: (feature) => {{
      const decile = numericOrNull(feature?.properties?.imd_decile);
      return {{
        color: 'rgba(26,28,26,0.18)',
        weight: 0.8,
        fillColor: deprivationFillColor(decile),
        fillOpacity: 0.5
      }};
    }},
    onEachFeature: (feature, layer) => {{
      layer.bindPopup(feature?.properties?.popupMarkup || '');
    }}
  }});
  deprivationLayer.addTo(map);
  deprivationLayer.bringToBack();
}}

function renderManagementList() {{
  const container = document.getElementById('manager-list');
  container.innerHTML = '';
  const assignments = shapeAssignment();
  const metric = metricConfigs[activeMetric];
  document.getElementById('manager-hint').textContent = `GTD stays on as the baseline. Add up to ${{managementShapePool.length - 1}} more management companies to compare their average ${{metric.title.toLowerCase()}} with GTD.`;
  for (const company of managementCompanies) {{
    const checked = selectedManagementCompanies.has(company.name);
    const isBaselineCompany = company.name === BASELINE_MANAGEMENT_COMPANY;
    const shape = assignments.get(company.name) || 'circle';
    const average = metric.averageLabel(averageMetric(company.rows, activeMetric));
    const row = document.createElement('label');
    row.className = 'manager-option';
    row.title = isBaselineCompany
      ? `${{company.name}} · baseline company · ${{average}} avg · ${{company.count}} practices`
      : `${{company.name}} · ${{average}} avg · ${{company.count}} practices`;
    row.innerHTML = `
      <input type="checkbox" ${{checked ? 'checked' : ''}} ${{isBaselineCompany ? 'disabled' : ''}} data-company="${{company.name}}">
      <span class="manager-name"><span class="swatch ${{shape}}" style="background:${{checked ? 'var(--midhigh)' : 'var(--missing)'}}; display:inline-block; margin-right:8px;"></span><span class="manager-name-text">${{company.name}}</span></span>
      <span class="manager-meta">${{average}} avg · ${{company.count}}</span>
    `;
    if (isBaselineCompany) {{
      container.appendChild(row);
      continue;
    }}
    row.querySelector('input').addEventListener('change', (event) => {{
      if (event.target.checked) {{
        if (selectedManagementCompanies.size >= managementShapePool.length) {{
          event.target.checked = false;
          return;
        }}
        selectedManagementCompanies.add(company.name);
      }} else {{
        selectedManagementCompanies.delete(company.name);
      }}
      rerenderAll();
    }});
    container.appendChild(row);
  }}
}}

function formatGoogle(row) {{
  const value = numericOrNull(row.google_score);
  if (value === null) return row.google_missing_text || 'Google: ?';
  const count = numericOrNull(row.google_count);
  return `Google: ${{value.toFixed(1)}}${{count === null ? '' : ` (${{Math.round(count)}} reviews)`}}`;
}}

function formatSurvey(row) {{
  const surveyLabel = row.survey_label || 'GPPS';
  const overall = numericOrNull(row.survey_overall_good_percent);
  const completion = numericOrNull(row.survey_completion_rate_percent);
  const sentBack = numericOrNull(row.survey_sent_back);
  const sentOut = numericOrNull(row.survey_sent_out);
  if (overall === null && completion === null) {{
    return row.survey_missing_text || `${{surveyLabel}}: ?`;
  }}
  const parts = [];
  if (overall !== null) parts.push(`${{Math.round(overall)}}%`);
  if (completion !== null) parts.push(`${{Math.round(completion)}}% completion`);
  if (sentBack !== null && sentOut !== null) parts.push(`${{Math.round(sentBack)}}/${{Math.round(sentOut)}} returned`);
  return `${{surveyLabel}} ${{parts.join(' / ')}}`;
}}

function formatGap(row) {{
  const inputs = gapInputs(row);
  const gap = gapValue(row, {{ suppressSmall: false }});
  if (!inputs || gap === null) return 'Survey/Google gap: ?';
  const magnitude = Math.abs(gap);
  if (magnitude < 0.01) {{
    return activeGapMode === 'normalized'
      ? `Survey/Google gap: typical for this nation-relative cohort · Google ${{inputs.google.toFixed(1)}} vs survey-equivalent ${{inputs.surveyStars.toFixed(2)}}`
      : `Survey/Google gap: aligned · Google ${{inputs.google.toFixed(1)}} vs survey-equivalent ${{inputs.surveyStars.toFixed(2)}}`;
  }}
  const direction = gap > 0 ? 'higher' : 'lower';
  return activeGapMode === 'normalized'
    ? `Survey/Google gap: ${{magnitude.toFixed(2)}} within-nation z-score (${{direction}}) · Google ${{inputs.google.toFixed(1)}} vs survey-equivalent ${{inputs.surveyStars.toFixed(2)}}`
    : `Survey/Google gap: ${{magnitude.toFixed(2)}} stars (${{direction}}) · Google ${{inputs.google.toFixed(1)}} vs survey-equivalent ${{inputs.surveyStars.toFixed(2)}}`;
}}

function popupMarkup(row) {{
  const google = `<div>${{formatGoogle(row)}}</div>`;
  const googleText = row.google_text_url ? `<div><a href="${{row.google_text_url}}" target="_blank" rel="noreferrer">Review text</a></div>` : '';
  const cqcRating = row.cqc_overall_rating
    ? `<div>CQC: ${{row.cqc_overall_rating}}${{row.cqc_inherited_rating === 'Y' ? ' (inherited)' : ''}}${{row.cqc_publication_date ? ` · ${{row.cqc_publication_date}}` : ''}}</div>`
    : '';
  const cqcLink = row.cqc_location_url ? `<div><a href="${{row.cqc_location_url}}" target="_blank" rel="noreferrer">CQC page</a></div>` : '';
  const practiceWebsite = row.cqc_service_website ? `<div><a href="${{row.cqc_service_website}}" target="_blank" rel="noreferrer">Practice website</a></div>` : '';
  const management = row.management_company ? `<div>Management: ${{row.management_company}}</div>` : '<div>Management: unknown</div>';
  const affiliatedGroup = row.affiliated_group ? `<div>Affiliated group: ${{row.affiliated_group}}</div>` : '';
  const takeoverDate = formatTakeoverDate(row.gtd_takeover_date, row.gtd_takeover_precision);
  const takeoverLine = takeoverDate ? `<div>GTD takeover: ${{takeoverDate}}</div>` : '';
  const takeoverNote = row.gtd_takeover_note ? `<div>${{row.gtd_takeover_note}}</div>` : '';
  const takeoverSource = row.gtd_takeover_source_url
    ? `<div><a href="${{row.gtd_takeover_source_url}}" target="_blank" rel="noreferrer">${{row.gtd_takeover_source_label || 'Takeover source'}}</a></div>`
    : '';
  const registeredPatients = numericOrNull(row.registered_patient_count_effective ?? row.registered_patient_count);
  const registeredPatientsSource = String(row.registered_patient_count_effective_source || row.registered_patient_count_source || '').trim();
  const registeredPatientsLine = `<div>Registered patients: ${{registeredPatients === null ? '?' : registeredPatients.toLocaleString('en-GB')}}</div>`;
  const registeredPatientsNote = registeredPatients !== null && registeredPatientsSource === 'nhs_monthly_parent_ods_fallback'
    ? '<div class="popup-note">Count shown via parent practice ODS code.</div>'
    : '';
  const survey = `<div>${{formatSurvey(row)}}</div>`;
  const surveyCompareValue = numericOrNull(row.survey_overall_good_ics_percent);
  const surveyCompare = surveyCompareValue === null ? '' : `<div>GP survey ICS overall-good: ${{Math.round(surveyCompareValue)}}%</div>`;
  const surveyResolution = row.survey_resolution_note ? `<div>${{row.survey_resolution_note}}</div>` : '';
  const surveySourceNote = row.survey_note ? `<div>${{row.survey_note}}</div>` : '';
  const surveyUrl = row.survey_link_url || '';
  const surveyLinkLabel = row.survey_link_label || 'Survey source';
  const surveyLink = surveyUrl ? `<div><a href="${{surveyUrl}}" target="_blank" rel="noreferrer">${{surveyLinkLabel}}</a></div>` : '';
  const gap = `<div>${{formatGap(row)}}</div>`;
  const gtd = row.gtd_url ? `<div><a href="${{row.gtd_url}}" target="_blank" rel="noreferrer">GTD page</a></div>` : '';
  return `
    <strong>${{row.name}}</strong><br>
    ${{row.postcode}}<br>
    <div>Code: ${{row.code}}</div>
    ${{management}}
    ${{affiliatedGroup}}
    ${{takeoverLine}}
    ${{takeoverNote}}
    ${{registeredPatientsLine}}
    ${{registeredPatientsNote}}
    ${{google}}
    ${{survey}}
    ${{cqcRating}}
    ${{surveyCompare}}
    ${{surveyResolution}}
    ${{surveySourceNote}}
    ${{gap}}
    ${{googleText}}
    <div><a href="${{row.nhs_url}}" target="_blank" rel="noreferrer">NHS page</a></div>
    ${{cqcLink}}
    ${{practiceWebsite}}
    ${{surveyLink}}
    ${{gtd}}
    ${{takeoverSource}}
  `;
}}

function nationalPopupMarkup(row) {{
  const google = `<div>${{formatGoogle(row)}}</div>`;
  const survey = `<div>${{formatSurvey(row)}}</div>`;
  const gap = `<div>${{formatGap(row)}}</div>`;
  const cqcRating = row.cqc_overall_rating
    ? `<div>CQC: ${{row.cqc_overall_rating}}${{row.cqc_inherited_rating === 'Y' ? ' (inherited)' : ''}}${{row.cqc_publication_date ? ` · ${{row.cqc_publication_date}}` : ''}}</div>`
    : '';
  const registeredPatients = numericOrNull(row.registered_patient_count_effective ?? row.registered_patient_count);
  const registeredPatientsSource = String(row.registered_patient_count_effective_source || row.registered_patient_count_source || '').trim();
  const patientsLine = registeredPatients === null ? '' : `<div>Registered patients: ${{registeredPatients.toLocaleString('en-GB')}}</div>`;
  const patientsNote = registeredPatients !== null && registeredPatientsSource === 'nhs_monthly_parent_ods_fallback'
    ? '<div class="popup-note">Count shown via parent practice ODS code.</div>'
    : '';
  const surveyResolution = row.survey_resolution_note ? `<div>${{row.survey_resolution_note}}</div>` : '';
  const surveySourceNote = row.survey_note ? `<div>${{row.survey_note}}</div>` : '';
  const surveyUrl = row.survey_link_url || '';
  const surveyLinkLabel = row.survey_link_label || 'Survey source';
  const surveyLink = surveyUrl ? `<div><a href="${{surveyUrl}}" target="_blank" rel="noreferrer">${{surveyLinkLabel}}</a></div>` : '';
  const googleLink = row.google_maps_url ? `<div><a href="${{row.google_maps_url}}" target="_blank" rel="noreferrer">Google Maps page</a></div>` : '';
  const cqcLink = row.cqc_location_url ? `<div><a href="${{row.cqc_location_url}}" target="_blank" rel="noreferrer">CQC page</a></div>` : '';
  const practiceWebsite = row.cqc_service_website ? `<div><a href="${{row.cqc_service_website}}" target="_blank" rel="noreferrer">Practice website</a></div>` : '';
  return `
    <strong>${{row.name}}</strong><br>
    ${{row.postcode || ''}}<br>
    <div>Code: ${{row.code}}</div>
    <div>Nation: ${{row.nation || '?'}}</div>
    ${{patientsLine}}
    ${{patientsNote}}
    ${{google}}
    ${{survey}}
    ${{cqcRating}}
    ${{surveyResolution}}
    ${{surveySourceNote}}
    ${{gap}}
    ${{surveyLink}}
    ${{googleLink}}
    ${{cqcLink}}
    ${{practiceWebsite}}
  `;
}}

function focusRow(row) {{
  focusedPracticeCode = row.code;
  renderComparisons();
}}

function focusPracticeByCode(code) {{
  const row = rowsByCode.get(code);
  if (row) {{
    focusRow(row);
  }}
}}

function isTrendSpecialCode(code) {{
  return code === TREND_DEFAULT_CONTEXT_CODE;
}}

function validTrendCode(code, availableCodes) {{
  return isTrendSpecialCode(code) || availableCodes.has(code);
}}

function defaultTrendReferenceEntry(practiceEntries) {{
  return practiceEntries.find((entry) => entry.series.code === NEW_BANK_CODE) || practiceEntries[0] || null;
}}

function patientVsAveragePoint(yearKey, code, index) {{
  const raw = numericOrNull(patientCountsByYear?.[yearKey]?.[code]);
  const average = numericOrNull(gtdAveragePatientCountByYear?.[yearKey]);
  if (raw === null || average === null || average <= 0) return null;
  return {{
    i: index,
    v: (raw / average) * 100,
    raw,
    average,
  }};
}}

function overlayAxisMax(values) {{
  const usable = (values || []).filter((value) => value !== null && Number.isFinite(value));
  const maxValue = usable.length ? Math.max(100, ...usable) : 100;
  return maxValue <= 100 ? 100 : Math.ceil(maxValue / 25) * 25;
}}

function overlayAxisTicks(maxValue) {{
  const step = maxValue <= 100 ? 25 : maxValue <= 200 ? 50 : 100;
  const ticks = [];
  for (let tick = 0; tick <= maxValue; tick += step) {{
    ticks.push(tick);
  }}
  if (ticks[ticks.length - 1] !== maxValue) {{
    ticks.push(maxValue);
  }}
  return ticks;
}}

function bindTrendLegendInteractions(legend) {{
  legend.querySelectorAll('[data-practice-code]').forEach((button) => {{
    const code = button.getAttribute('data-practice-code');
    button.addEventListener('mouseenter', () => {{
      if (trendLegendHoverSuppressed) return;
      if (hoveredTrendPracticeCode === code) return;
      hoveredTrendPracticeCode = code;
      renderGtdScoreTrendChart();
    }});
    button.addEventListener('mouseleave', () => {{
      if (trendLegendHoverSuppressed) return;
      if (hoveredTrendPracticeCode !== code) return;
      hoveredTrendPracticeCode = null;
      renderGtdScoreTrendChart();
    }});
    button.addEventListener('focus', () => {{
      if (trendLegendHoverSuppressed) return;
      hoveredTrendPracticeCode = code;
      renderGtdScoreTrendChart();
    }});
    button.addEventListener('blur', () => {{
      if (trendLegendHoverSuppressed) return;
      if (hoveredTrendPracticeCode !== code) return;
      hoveredTrendPracticeCode = null;
      renderGtdScoreTrendChart();
    }});
    button.addEventListener('mousedown', (event) => {{
      event.preventDefault();
      const nextCode = code || TREND_DEFAULT_CONTEXT_CODE;
      trendLegendHoverSuppressed = true;
      hoveredTrendPracticeCode = null;
      pinnedTrendPracticeCode = nextCode;
      renderGtdScoreTrendChart();
    }});
    button.addEventListener('click', (event) => {{
      event.preventDefault();
      const nextCode = code || TREND_DEFAULT_CONTEXT_CODE;
      trendLegendHoverSuppressed = true;
      hoveredTrendPracticeCode = null;
      pinnedTrendPracticeCode = nextCode;
      renderGtdScoreTrendChart();
    }});
  }});
}}

function renderTrendOverlayLegend(container, items) {{
  if (!container) return;
  const activeItems = (items || []).filter((item) => item && item.label);
  container.innerHTML = activeItems.length
    ? activeItems.map((item) => `
        <span class="trend-overlay-key">
          <span class="trend-overlay-swatch" style="--swatch-color:${{item.color}}"></span>
          <span>${{item.label}}</span>
        </span>
      `).join('')
    : '';
}}

function buildManchesterCatchmentIndex(featureCollection) {{
  const index = new Map();
  const features = Array.isArray(featureCollection?.features) ? featureCollection.features : [];
  features.forEach((feature) => {{
    const codes = Array.isArray(feature?.properties?.codes) ? feature.properties.codes : [];
    codes.forEach((code) => {{
      const normalized = String(code || '').trim();
      if (!normalized) return;
      if (!index.has(normalized)) index.set(normalized, []);
      index.get(normalized).push(feature);
    }});
  }});
  return index;
}}

function loadManchesterCatchmentIndex() {{
  if (manchesterCatchmentIndex) return Promise.resolve(manchesterCatchmentIndex);
  if (manchesterCatchmentLoadPromise) return manchesterCatchmentLoadPromise;
  if (!manchesterCatchmentBundleMeta || !manchesterCatchmentBundleMeta.feature_count) {{
    manchesterCatchmentIndex = new Map();
    return Promise.resolve(manchesterCatchmentIndex);
  }}
  const catchmentUrl = new URL(MANCHESTER_CATCHMENT_BUNDLE_NAME, window.location.href).toString();
  manchesterCatchmentLoadPromise = fetch(catchmentUrl)
    .then((response) => {{
      if (!response.ok) throw new Error(`catchment fetch failed: ${{response.status}}`);
      return response.json();
    }})
    .then((payload) => {{
      manchesterCatchmentIndex = buildManchesterCatchmentIndex(payload);
      return manchesterCatchmentIndex;
    }})
    .catch((_error) => {{
      manchesterCatchmentIndex = new Map();
      return manchesterCatchmentIndex;
    }});
  return manchesterCatchmentLoadPromise;
}}

function preloadManchesterCatchments() {{
  if (!manchesterCatchmentBundleMeta || !manchesterCatchmentBundleMeta.feature_count) return;
  if (manchesterCatchmentIndex || manchesterCatchmentLoadPromise) return;
  window.setTimeout(() => {{
    loadManchesterCatchmentIndex().then(() => {{
      renderMarkers();
      updateHoveredCatchmentOutline();
      renderServiceFinderMarker();
      renderServiceFinder();
    }});
  }}, 0);
}}

function clearHoveredCatchmentOutline() {{
  catchmentOutlineLayer.clearLayers();
}}

function updateHoveredCatchmentOutline() {{
  clearHoveredCatchmentOutline();
  if (map.getZoom() < MANCHESTER_CATCHMENT_MIN_ZOOM) return;
  if (!manchesterCatchmentIndex) return;
  const codes = Array.from(persistentCatchmentCodes);
  if (hoveredCatchmentCode && !persistentCatchmentCodes.has(hoveredCatchmentCode)) {{
    codes.push(hoveredCatchmentCode);
  }}
  if (!codes.length) return;
  codes.forEach((activeCode) => {{
    const features = manchesterCatchmentIndex.get(activeCode) || [];
    if (!features.length) return;
    const layer = L.geoJSON({{ type: 'FeatureCollection', features }}, {{
      style: () => ({{
        color: '#7a7a7a',
        weight: 2.4,
        opacity: 0.9,
        fillOpacity: 0,
        dashArray: '6 4',
        interactive: false,
      }}),
    }});
    layer.addTo(catchmentOutlineLayer);
  }});
}}

function setHoveredCatchmentOutline(code) {{
  hoveredCatchmentCode = String(code || '').trim() || null;
  updateHoveredCatchmentOutline();
}}

function clearHoveredCatchment(code = '') {{
  const normalized = String(code || '').trim();
  if (normalized && hoveredCatchmentCode && hoveredCatchmentCode !== normalized) return;
  hoveredCatchmentCode = null;
  updateHoveredCatchmentOutline();
}}

function togglePersistentCatchment(code) {{
  const normalized = String(code || '').trim();
  if (!normalized) return;
  if (persistentCatchmentCodes.has(normalized)) {{
    persistentCatchmentCodes.delete(normalized);
  }} else {{
    persistentCatchmentCodes.add(normalized);
  }}
  updateHoveredCatchmentOutline();
}}

function serviceFinderDefaultDirection(sortKey) {{
  return sortKey === 'practice' || sortKey === 'distance' ? 'asc' : 'desc';
}}

function serviceFinderAccentColor(row) {{
  const google = numericOrNull(row?.google_score);
  if (google !== null) return metricColorForValue('google', google);
  const survey = numericOrNull(row?.survey_overall_good_percent);
  if (survey !== null) return metricColorForValue('survey', survey);
  return '#9aa0a6';
}}

function serviceFinderColumnValue(entry, sortKey) {{
  const row = entry.row || entry;
  if (sortKey === 'practice') return String(row?.name || '').trim().toLowerCase();
  if (sortKey === 'distance') return Number.isFinite(entry.distance) ? entry.distance : null;
  if (sortKey === 'google') return numericOrNull(row?.google_score);
  if (sortKey === 'reviews') return numericOrNull(row?.google_count);
  if (sortKey === 'survey') return numericOrNull(row?.survey_overall_good_percent);
  if (sortKey === 'patients') return numericOrNull(row?.registered_patient_count_effective ?? row?.registered_patient_count);
  return null;
}}

function updateServiceFinderSortButtons() {{
  document.querySelectorAll('[data-service-finder-sort]').forEach((button) => {{
    const key = button.getAttribute('data-service-finder-sort');
    const indicator = button.querySelector('.service-finder-sort-indicator');
    const isActive = key === serviceFinderSortKey;
    button.classList.toggle('is-active', isActive);
    if (indicator) indicator.textContent = isActive ? (serviceFinderSortDirection === 'asc' ? '▲' : '▼') : '';
  }});
}}

function clearServiceFinderButtonFlash() {{
  if (serviceFinderButtonFlashTimer) {{
    window.clearTimeout(serviceFinderButtonFlashTimer);
    serviceFinderButtonFlashTimer = null;
  }}
  serviceFinderButtonFlash = '';
}}

function flashServiceFinderButton(label, duration = 2600) {{
  clearServiceFinderButtonFlash();
  serviceFinderButtonFlash = label;
  renderServiceFinder();
  serviceFinderButtonFlashTimer = window.setTimeout(() => {{
    serviceFinderButtonFlash = '';
    serviceFinderButtonFlashTimer = null;
    renderServiceFinder();
  }}, duration);
}}

function serviceFinderButtonText() {{
  if (serviceFinderButtonFlash) return serviceFinderButtonFlash;
  if (serviceFinderDragActive) return '📍 Pick a Location';
  if (serviceFinderArmed || serviceFinderPoint) return '📍 Pick a Location';
  return '📍 Find Practices';
}}

function removeServiceFinderDragGhost() {{
  if (serviceFinderDragGhost?.parentNode) {{
    serviceFinderDragGhost.parentNode.removeChild(serviceFinderDragGhost);
  }}
  serviceFinderDragGhost = null;
}}

function updateServiceFinderDragGhost(clientX, clientY) {{
  if (!serviceFinderDragGhost) {{
    serviceFinderDragGhost = document.createElement('div');
    serviceFinderDragGhost.className = 'service-finder-drag-ghost';
    serviceFinderDragGhost.textContent = '📍 Pick a Location';
    document.body.appendChild(serviceFinderDragGhost);
  }}
  serviceFinderDragGhost.style.left = `${{clientX}}px`;
  serviceFinderDragGhost.style.top = `${{clientY}}px`;
}}

function mapLatLngFromClientPoint(clientX, clientY) {{
  const container = map.getContainer();
  if (!container) return null;
  const rect = container.getBoundingClientRect();
  if (clientX < rect.left || clientX > rect.right || clientY < rect.top || clientY > rect.bottom) {{
    return null;
  }}
  const point = L.point(clientX - rect.left, clientY - rect.top);
  return map.containerPointToLatLng(point);
}}

function updateServiceFinderButtons() {{
  const text = serviceFinderButtonText();
  const title = serviceFinderArmed
    ? 'Click the map to place a practice lookup pin.'
    : 'Click, then click the map to place a practice lookup pin.';
  ['service-finder-place-button', 'service-finder-map-button'].forEach((id) => {{
    const button = document.getElementById(id);
    if (!button) return;
    button.classList.toggle('is-active', serviceFinderArmed);
    button.title = title;
    const label = button.querySelector('span');
    if (label) label.textContent = text;
  }});
}}

function scrollToServiceFinder() {{
  const heading = document.getElementById('service-finder-heading');
  if (!heading) return;
  heading.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
}}

function renderServiceFinderMarker() {{
  serviceFinderPointLayer.clearLayers();
  if (!serviceFinderPoint) return;
  const matches = manchesterCatchmentIndex
    ? (serviceFinderRowsForPoint(serviceFinderPoint.lat, serviceFinderPoint.lon) || [])
    : null;
  const count = matches ? matches.length : null;
  const countText = count === null ? '…' : String(count);
  const icon = L.divIcon({{
    className: 'service-finder-pin-icon',
    html: `<div class="service-finder-pin${{count !== null && count >= 100 ? ' is-large' : ''}}">${{escapeHtml(countText)}}</div>`,
    iconSize: count !== null && count >= 100 ? [44, 44] : [38, 38],
    iconAnchor: count !== null && count >= 100 ? [22, 22] : [19, 19],
  }});
  const tooltip = count === null
    ? `${{serviceFinderLocationLabel || 'Selected location'}} · waiting for catchments`
    : `${{serviceFinderLocationLabel || 'Selected location'}} · ${{count.toLocaleString('en-GB')}} practice${{count === 1 ? '' : 's'}}`;
  const marker = L.marker([serviceFinderPoint.lat, serviceFinderPoint.lon], {{ icon, draggable: true }});
  marker.on('click', () => {{
    scrollToServiceFinder();
  }});
  marker.on('dragend', () => {{
    const latlng = marker.getLatLng();
    setServiceFinderPoint(latlng.lat, latlng.lng, 'Selected location');
  }});
  marker
    .bindTooltip(tooltip, {{ sticky: false, opacity: 0.94 }})
    .addTo(serviceFinderPointLayer);
}}

function clearServiceFinderPoint() {{
  serviceFinderArmed = false;
  serviceFinderPoint = null;
  serviceFinderLocationLabel = '';
  serviceFinderEmptyMessage = '';
  clearServiceFinderButtonFlash();
  renderMarkers();
  renderServiceFinderMarker();
  renderServiceFinder();
}}

function setServiceFinderPoint(lat, lon, label = 'Selected location') {{
  serviceFinderArmed = false;
  serviceFinderPoint = {{
    lat: Number(lat),
    lon: Number(lon),
  }};
  serviceFinderLocationLabel = label;
  serviceFinderEmptyMessage = '';
  renderMarkers();
  renderServiceFinderMarker();
  renderServiceFinder();
  flashServiceFinderButton('✅ List Updated');
}}

function serviceFinderRowsForPoint(lat, lon) {{
  if (!manchesterCatchmentIndex) return null;
  const point = turf.point([Number(lon), Number(lat)]);
  const matches = [];
  rows.forEach((row) => {{
    const features = manchesterCatchmentIndex.get(row.code) || [];
    if (!features.length) return;
    const isMatch = features.some((feature) => {{
      try {{
        return turf.booleanPointInPolygon(point, feature);
      }} catch (_error) {{
        return false;
      }}
    }});
    if (isMatch) matches.push(row);
  }});
  return matches;
}}

function serviceFinderResultRows(matches) {{
  const entries = matches.map((row) => ({{
    row,
    distance: distanceMiles(serviceFinderPoint.lat, serviceFinderPoint.lon, Number(row.lat), Number(row.lon)),
  }}));
  return entries.sort((left, right) => {{
    const leftValue = serviceFinderColumnValue(left, serviceFinderSortKey);
    const rightValue = serviceFinderColumnValue(right, serviceFinderSortKey);
    if (leftValue === null && rightValue !== null) return 1;
    if (leftValue !== null && rightValue === null) return -1;
    if (leftValue !== null && rightValue !== null && leftValue !== rightValue) {{
      if (typeof leftValue === 'string' || typeof rightValue === 'string') {{
        return serviceFinderSortDirection === 'asc'
          ? String(leftValue).localeCompare(String(rightValue), 'en')
          : String(rightValue).localeCompare(String(leftValue), 'en');
      }}
      return serviceFinderSortDirection === 'asc' ? leftValue - rightValue : rightValue - leftValue;
    }}
    const leftGoogle = numericOrNull(left.row.google_score);
    const rightGoogle = numericOrNull(right.row.google_score);
    if (leftGoogle === null && rightGoogle !== null) return 1;
    if (leftGoogle !== null && rightGoogle === null) return -1;
    if (leftGoogle !== null && rightGoogle !== null && leftGoogle !== rightGoogle) return rightGoogle - leftGoogle;
    return String(left.row.name || '').localeCompare(String(right.row.name || ''), 'en');
  }});
}}

function renderServiceFinder() {{
  const tbody = document.getElementById('service-finder-results');
  const clearButton = document.getElementById('service-finder-clear-button');
  if (!tbody) return;
  updateServiceFinderSortButtons();
  updateServiceFinderButtons();
  if (clearButton) clearButton.disabled = !serviceFinderPoint;

  if (!serviceFinderPoint) {{
    tbody.innerHTML = `<tr><td colspan="6" class="service-finder-empty">${{escapeHtml(serviceFinderEmptyMessage || 'Drop a pin or use your location.')}}</td></tr>`;
    return;
  }}

  if (!manchesterCatchmentIndex) {{
    tbody.innerHTML = `<tr><td colspan="6" class="service-finder-empty">Waiting for catchment polygons...</td></tr>`;
    return;
  }}

  const matches = serviceFinderRowsForPoint(serviceFinderPoint.lat, serviceFinderPoint.lon) || [];
  const ranked = serviceFinderResultRows(matches);

  if (!ranked.length) {{
    tbody.innerHTML = `<tr><td colspan="6" class="service-finder-empty">No practice catchment in the current bundle covers this point.</td></tr>`;
    return;
  }}

  tbody.innerHTML = ranked.map((entry, index) => {{
    const row = entry.row;
    const google = numericOrNull(row.google_score);
    const survey = numericOrNull(row.survey_overall_good_percent);
    const reviews = numericOrNull(row.google_count);
    const reviewsPerYear = numericOrNull(row.google_reviews_per_year);
    const patients = numericOrNull(row.registered_patient_count_effective ?? row.registered_patient_count);
    const patientChangePerYear = numericOrNull(row.patient_change_per_year);
    const distance = entry.distance;
    const accentColor = serviceFinderAccentColor(row);
    const nhsUrl = String(row.nhs_url || '').trim();
    const registerUrl = String(row.nhs_register_url || '').trim();
    const googleMapsUrl = String(row.google_maps_url || '').trim();
    const surveyUrl = String(row.survey_link_url || '').trim();
    const shortAddress = String(row.short_address || '').trim();
    const patientLabel = patients === null ? '?' : patients.toLocaleString('en-GB');
    const googleLabel = google === null ? '?' : google.toFixed(1);
    const reviewRateLabel = reviewsPerYear === null ? '' : `${{reviewsPerYear < 10 ? reviewsPerYear.toFixed(1) : Math.round(reviewsPerYear)}}/yr`;
    const reviewMainLabel = reviews === null ? '?' : Math.round(reviews).toLocaleString('en-GB');
    const reviewDetailMarkup = reviewRateLabel ? `<span class="service-finder-secondary-detail"> (${{reviewRateLabel}})</span>` : '';
    const reviewClass = reviews === null ? 'service-finder-secondary-value is-missing' : 'service-finder-secondary-value';
    const patientClass = patients === null ? 'service-finder-secondary-value is-missing' : 'service-finder-secondary-value';
    const roundedPatientChange = patientChangePerYear === null ? null : roundApproxPatientsPerYear(patientChangePerYear);
    const patientTrendClass = roundedPatientChange === null
      ? ''
      : roundedPatientChange > 0
        ? 'service-finder-secondary-trend is-positive'
        : roundedPatientChange < 0
          ? 'service-finder-secondary-trend is-negative'
          : 'service-finder-secondary-trend is-flat';
    const patientTrendLabel = roundedPatientChange === null
      ? ''
      : `(${{roundedPatientChange > 0 ? '+' : roundedPatientChange < 0 ? '-' : ''}}~${{Math.abs(roundedPatientChange).toLocaleString('en-GB')}}/yr)`;
    const surveyLabel = survey === null ? '?' : `${{Math.round(survey)}}%`;
    const googleClass = google === null ? 'service-finder-primary-value is-missing' : 'service-finder-primary-value';
    const surveyClass = survey === null ? 'service-finder-primary-value is-missing' : 'service-finder-primary-value';
    const googleStyle = google === null ? '' : ` style="color:${{metricColorForValue('google', google)}}"`;
    const surveyStyle = survey === null ? '' : ` style="color:${{metricColorForValue('survey', survey)}}"`;
    const distanceLabel = Number.isFinite(distance) ? `${{distance.toFixed(distance < 10 ? 1 : 0)}} mi` : '?';
    const scopeTag = row.gtd ? '<span class="service-finder-tag">GTD</span>' : '';
    const cqcRating = String(row.cqc_overall_rating || '').trim();
    const cqcUrl = String(row.cqc_location_url || '').trim();
    const cqcBadgeConfig = (() => {{
      if (!cqcRating || !cqcUrl) return null;
      if (cqcRating === 'Outstanding') return {{ icon: '⭐', className: 'is-outstanding', title: 'CQC: Outstanding' }};
      if (cqcRating === 'Good') return {{ icon: '✓', className: 'is-good', title: 'CQC: Good' }};
      if (cqcRating === 'Requires improvement') return {{ icon: '⚠', className: 'is-requires-improvement', title: 'CQC: Requires improvement' }};
      if (cqcRating === 'Inadequate') return {{ icon: '⛔', className: 'is-inadequate', title: 'CQC: Inadequate' }};
      if (cqcRating === 'Insufficient evidence to rate') return {{ icon: '❔', className: 'is-insufficient-evidence', title: 'CQC: Insufficient evidence to rate' }};
      return {{ icon: '❔', className: 'is-insufficient-evidence', title: `CQC: ${{cqcRating}}` }};
    }})();
    const cqcBadgeMarkup = cqcBadgeConfig
      ? `<a class="service-finder-cqc-badge ${{cqcBadgeConfig.className}}" href="${{escapeHtml(cqcUrl)}}" target="_blank" rel="noreferrer" title="${{escapeHtml(cqcBadgeConfig.title)}}">${{cqcBadgeConfig.icon}}</a>`
      : '';
    const titleMarkup = nhsUrl
      ? `<a class="service-finder-practice-name" href="${{escapeHtml(nhsUrl)}}" target="_blank" rel="noreferrer">${{escapeHtml(row.name || row.code)}}</a>`
      : `<button type="button" class="service-finder-practice-name" data-service-finder-code="${{escapeHtml(row.code)}}">${{escapeHtml(row.name || row.code)}}</button>`;
    const addressBits = [
      shortAddress ? `<span class="service-finder-subtle">${{escapeHtml(shortAddress)}}</span>` : '',
      row.postcode ? `<span class="service-finder-subtle">${{escapeHtml(row.postcode)}}</span>` : '',
    ].filter(Boolean);
    const addressLineMarkup = addressBits.length
      ? `<span class="service-finder-address-line">${{addressBits.join('<span class="service-finder-address-separator">·</span>')}}</span>`
      : '';
    const addressLinkUrl = googleMapsUrl || nhsUrl;
    const addressMarkup = addressLinkUrl
      ? (addressLineMarkup ? `<a class="service-finder-address-link" href="${{escapeHtml(addressLinkUrl)}}" target="_blank" rel="noreferrer">${{addressLineMarkup}}</a>` : '')
      : addressLineMarkup;
    const googleValueMarkup = googleMapsUrl && google !== null
      ? `<a class="service-finder-primary-value-link" href="${{escapeHtml(googleMapsUrl)}}" target="_blank" rel="noreferrer"><span class="${{googleClass}}"${{googleStyle}}>${{googleLabel}}</span></a>`
      : `<span class="${{googleClass}}"${{googleStyle}}>${{googleLabel}}</span>`;
    const surveyValueMarkup = surveyUrl && survey !== null
      ? `<a class="service-finder-primary-value-link" href="${{escapeHtml(surveyUrl)}}" target="_blank" rel="noreferrer"><span class="${{surveyClass}}"${{surveyStyle}}>${{surveyLabel}}</span></a>`
      : `<span class="${{surveyClass}}"${{surveyStyle}}>${{surveyLabel}}</span>`;
    return `
      <tr class="service-finder-row" style="--service-finder-accent:${{accentColor}}">
        <td class="service-finder-practice">
          <div class="service-finder-practice-layout">
            <div class="service-finder-practice-main">
              <div class="service-finder-title-line">
                ${{cqcBadgeMarkup}}${{titleMarkup}}${{scopeTag}}
              </div>
              ${{addressMarkup}}
            </div>
            ${{registerUrl ? `<a class="service-finder-register-link" href="${{escapeHtml(registerUrl)}}" target="_blank" rel="noreferrer">Register</a>` : ''}}
          </div>
        </td>
        <td class="service-finder-distance-cell"><span class="service-finder-distance-value">${{distanceLabel}}</span></td>
        <td class="service-finder-primary-metric service-finder-primary-metric-google">
          ${{googleValueMarkup}}
          <span class="service-finder-primary-label">Google</span>
        </td>
        <td class="service-finder-primary-metric service-finder-primary-metric-survey">
          ${{surveyValueMarkup}}
          <span class="service-finder-primary-label">Survey</span>
        </td>
        <td class="service-finder-secondary-metric service-finder-secondary-metric-reviews">
          <span class="${{reviewClass}}">${{reviewMainLabel}}${{reviewDetailMarkup}}</span>
          <span class="service-finder-secondary-label">Review Count</span>
        </td>
        <td class="service-finder-secondary-metric service-finder-secondary-metric-patients">
          <span class="${{patientClass}}">${{patientLabel}}</span>
          ${{patientTrendLabel ? `<span class="${{patientTrendClass}}">${{patientTrendLabel}}</span>` : ''}}
          <span class="service-finder-secondary-label">Patients</span>
        </td>
      </tr>
    `;
  }}).join('');

  tbody.querySelectorAll('[data-service-finder-code]').forEach((button) => {{
    button.addEventListener('click', () => {{
      const code = button.getAttribute('data-service-finder-code');
      const row = rowsByCode.get(code);
      if (!row) return;
      focusRow(row);
      map.flyTo([Number(row.lat), Number(row.lon)], Math.max(map.getZoom(), 12), {{ duration: 0.65 }});
      persistentCatchmentCodes.add(row.code);
      updateHoveredCatchmentOutline();
    }});
  }});
}}

function renderMarkers() {{
  markerLayer.clearLayers();
  clearHoveredCatchment();
  const assignments = shapeAssignment();
  const metric = metricConfigs[activeMetric];
  const centroidByCode = activeAreaOverlay === 'population' ? voronoiCentroidByCode() : null;
  const serviceFinderMatchedCodes = new Set(
    serviceFinderPoint && manchesterCatchmentIndex
      ? (serviceFinderRowsForPoint(serviceFinderPoint.lat, serviceFinderPoint.lon) || []).map((row) => row.code)
      : []
  );
  for (const row of rows) {{
    const metricValue = metric.value(row);
    if (metricValue === null && activeMetric === 'google') {{
      continue;
    }}
    if (metricValue === null && activeMetric === 'gap') {{
      continue;
    }}
    if (activeMetric === 'gap' && activeGapMode === 'normalized' && metricValue > 0) {{
      continue;
    }}
    const color = metric.markerColor(row);
    const label = metric.markerLabel(row);
    const shapeName = assignments.get(row.management_company) || 'circle';
    const scale = mapScaleForRow(row);
    const metrics = baseShapeMetrics(shapeName);
    const fontSize = Math.max(9, Math.min(13, Math.round(10 + scale * 2)));
    const baseZIndex = assignments.has(row.management_company) ? 1000 : 0;
    const scaledWidth = Math.round(metrics.width * scale);
    const scaledHeight = Math.round(metrics.height * scale);
    const icon = L.divIcon({{
      className: 'marker-icon',
      html: markerSvg(shapeName, color, label, fontSize, label === '?', serviceFinderMatchedCodes.has(row.code)),
      iconSize: [scaledWidth, scaledHeight],
      iconAnchor: [Math.round(metrics.anchorX * scale), Math.round(metrics.anchorY * scale)],
      popupAnchor: [0, metrics.popupY]
    }});
    const pos = centroidByCode && centroidByCode.has(row.code) ? centroidByCode.get(row.code) : [row.lat, row.lon];
    const marker = L.marker(pos, {{ icon, zIndexOffset: baseZIndex }});
    marker.bindPopup(popupMarkup(row));
    marker.on('click', () => {{
      togglePersistentCatchment(row.code);
      focusRow(row);
    }});
    marker.on('mouseover', () => {{
      marker.setZIndexOffset(baseZIndex + 2000);
      setHoveredCatchmentOutline(row.code);
    }});
    marker.on('mouseout', () => {{
      marker.setZIndexOffset(baseZIndex);
      clearHoveredCatchment(row.code);
    }});
    marker.addTo(markerLayer);
  }}
}}

function renderNationalSupplementals() {{
  nationalMarkerLayer.clearLayers();
  const note = document.getElementById('national-supplemental-note');
  const notePrefix = (() => {{
    if (!note) return '';
    const totalPatients = Number(note.dataset.totalPatients || 0).toLocaleString('en-GB');
    const totalPractices = Number(note.dataset.totalPractices || 0).toLocaleString('en-GB');
    return `🏴 National: ${{totalPatients}} 👥 · ${{totalPractices}} 🏥`;
  }})();
  if (!nationalSupplementals.length) {{
    if (note) note.textContent = '🏴 National: no supplementals built yet';
    return;
  }}
  if (map.getZoom() < NATIONAL_SUPPLEMENTAL_MIN_ZOOM) {{
    if (note) {{
      note.textContent = `${{notePrefix}} · zoom to ${{NATIONAL_SUPPLEMENTAL_MIN_ZOOM}}+ to show markers`;
    }}
    return;
  }}

  const bounds = map.getBounds().pad(0.04);
  const metric = metricConfigs[activeMetric];
  const visibleRows = nationalSupplementals.filter((row) => bounds.contains([Number(row.lat), Number(row.lon)]));
  for (const row of visibleRows) {{
    const metricValue = metric.value(row);
    if (metricValue === null && activeMetric === 'google') {{
      continue;
    }}
    if (metricValue === null && activeMetric === 'gap') {{
      continue;
    }}
    if (activeMetric === 'gap' && activeGapMode === 'normalized' && metricValue > 0) {{
      continue;
    }}
    const color = metric.markerColor(row);
    const label = metric.markerLabel(row);
    const scale = nationalMapScaleForRow(row);
    const metrics = baseShapeMetrics('circle');
    const fontSize = Math.max(8, Math.min(11, Math.round(9 + scale * 2)));
    const scaledWidth = Math.round(metrics.width * scale);
    const scaledHeight = Math.round(metrics.height * scale);
    const icon = L.divIcon({{
      className: 'marker-icon marker-icon-national',
      html: markerSvg('circle', color, label, fontSize, label === '?'),
      iconSize: [scaledWidth, scaledHeight],
      iconAnchor: [Math.round(metrics.anchorX * scale), Math.round(metrics.anchorY * scale)],
      popupAnchor: [0, metrics.popupY]
    }});
    const marker = L.marker([row.lat, row.lon], {{
      pane: 'nationalSupplementals',
      icon,
      zIndexOffset: -300,
    }});
    marker.bindPopup(nationalPopupMarkup(row));
    marker.addTo(nationalMarkerLayer);
  }}

  if (note) {{
    const visibleText = `${{visibleRows.length.toLocaleString('en-GB')}} visible`;
    note.textContent = `${{notePrefix}} · ${{visibleText}}`;
  }}
}}

function correlation(points) {{
  if (points.length < 2) return null;
  const xs = points.map((point) => point.x);
  const ys = points.map((point) => point.y);
  const meanX = xs.reduce((sum, value) => sum + value, 0) / xs.length;
  const meanY = ys.reduce((sum, value) => sum + value, 0) / ys.length;
  let numerator = 0;
  let sumSqX = 0;
  let sumSqY = 0;
  for (let index = 0; index < points.length; index += 1) {{
    const dx = xs[index] - meanX;
    const dy = ys[index] - meanY;
    numerator += dx * dy;
    sumSqX += dx * dx;
    sumSqY += dy * dy;
  }}
  if (sumSqX === 0 || sumSqY === 0) return null;
  return numerator / Math.sqrt(sumSqX * sumSqY);
}}

function linearRegression(points) {{
  if (points.length < 2) return null;
  const xs = points.map((point) => point.x);
  const ys = points.map((point) => point.y);
  const meanX = xs.reduce((sum, value) => sum + value, 0) / xs.length;
  const meanY = ys.reduce((sum, value) => sum + value, 0) / ys.length;
  let numerator = 0;
  let denominator = 0;
  for (let index = 0; index < points.length; index += 1) {{
    const dx = xs[index] - meanX;
    numerator += dx * (ys[index] - meanY);
    denominator += dx * dx;
  }}
  if (denominator === 0) return null;
  const slope = numerator / denominator;
  const intercept = meanY - (slope * meanX);
  return {{ slope, intercept }};
}}

function quadraticRegression(points) {{
  if (points.length < 3) return null;
  let n = 0;
  let sx = 0;
  let sx2 = 0;
  let sx3 = 0;
  let sx4 = 0;
  let sy = 0;
  let sxy = 0;
  let sx2y = 0;
  points.forEach((point) => {{
    const x = Number(point.x);
    const y = Number(point.y);
    if (!Number.isFinite(x) || !Number.isFinite(y)) return;
    const x2 = x * x;
    n += 1;
    sx += x;
    sx2 += x2;
    sx3 += x2 * x;
    sx4 += x2 * x2;
    sy += y;
    sxy += x * y;
    sx2y += x2 * y;
  }});
  if (n < 3) return null;
  const matrix = [
    [sx4, sx3, sx2, sx2y],
    [sx3, sx2, sx, sxy],
    [sx2, sx, n, sy],
  ];
  for (let pivot = 0; pivot < 3; pivot += 1) {{
    let bestRow = pivot;
    for (let row = pivot + 1; row < 3; row += 1) {{
      if (Math.abs(matrix[row][pivot]) > Math.abs(matrix[bestRow][pivot])) bestRow = row;
    }}
    if (Math.abs(matrix[bestRow][pivot]) < 1e-9) return null;
    if (bestRow !== pivot) [matrix[pivot], matrix[bestRow]] = [matrix[bestRow], matrix[pivot]];
    const pivotValue = matrix[pivot][pivot];
    for (let col = pivot; col < 4; col += 1) matrix[pivot][col] /= pivotValue;
    for (let row = 0; row < 3; row += 1) {{
      if (row === pivot) continue;
      const factor = matrix[row][pivot];
      for (let col = pivot; col < 4; col += 1) matrix[row][col] -= factor * matrix[pivot][col];
    }}
  }}
  const [a, b, c] = matrix.map((row) => row[3]);
  if (![a, b, c].every((value) => Number.isFinite(value))) return null;
  return {{ a, b, c }};
}}

function clamp01(value) {{
  return Math.max(0, Math.min(1, value));
}}

function normalizedCounts(counts) {{
  const safe = (counts || []).map((value) => Number(value) || 0);
  const total = safe.reduce((sum, value) => sum + value, 0);
  if (total <= 0) return safe.map(() => 0);
  return safe.map((value) => value / total);
}}

function jensenShannonDivergence(leftCounts, rightCounts) {{
  const left = normalizedCounts(leftCounts);
  const right = normalizedCounts(rightCounts);
  if (!left.length || left.length !== right.length) return 0;
  const midpoint = left.map((value, index) => (value + right[index]) / 2);
  const kl = (source, target) => source.reduce((sum, value, index) => {{
    if (value <= 0 || target[index] <= 0) return sum;
    return sum + (value * Math.log2(value / target[index]));
  }}, 0);
  return (kl(left, midpoint) + kl(right, midpoint)) / 2;
}}

function percentile(sortedValues, value) {{
  if (!sortedValues.length) return null;
  let lessOrEqual = 0;
  sortedValues.forEach((candidate) => {{
    if (candidate <= value) lessOrEqual += 1;
  }});
  return (lessOrEqual / sortedValues.length) * 100;
}}

function mean(values) {{
  if (!values.length) return null;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}}

function median(values) {{
  if (!values.length) return null;
  const sorted = [...values].sort((left, right) => left - right);
  const middle = Math.floor(sorted.length / 2);
  if (sorted.length % 2 === 1) return sorted[middle];
  return (sorted[middle - 1] + sorted[middle]) / 2;
}}

function escapeHtml(value) {{
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}}

function distanceMiles(lat1, lon1, lat2, lon2) {{
  const toRadians = (degrees) => (degrees * Math.PI) / 180;
  const earthRadiusMiles = 3958.8;
  const dLat = toRadians(lat2 - lat1);
  const dLon = toRadians(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRadians(lat1)) * Math.cos(toRadians(lat2)) * Math.sin(dLon / 2) ** 2;
  return 2 * earthRadiusMiles * Math.asin(Math.sqrt(a));
}}

function displayNationName(nation) {{
  const normalized = String(nation || '').trim().toLowerCase();
  if (normalized === 'england') return 'England';
  if (normalized === 'scotland') return 'Scotland';
  if (normalized === 'wales') return 'Wales';
  if (normalized === 'northern_ireland') return 'Northern Ireland';
  return normalized ? normalized.replace(/_/g, ' ').replace(/\\b\\w/g, (match) => match.toUpperCase()) : 'Unknown';
}}

function activeCompletionNation() {{
  return completionScatterNationOrder[completionScatterNationIndex] || 'england';
}}

function completionNationShortLabel(nation) {{
  const normalized = String(nation || '').trim().toLowerCase();
  if (normalized === 'england') return 'E';
  if (normalized === 'scotland') return 'S';
  if (normalized === 'wales') return 'W';
  if (normalized === 'northern_ireland') return 'NI';
  return 'N';
}}

function updateCompletionScopeControl() {{
  const option = document.getElementById('completion-scope-national-option');
  const text = document.getElementById('completion-scope-national-label');
  const short = document.getElementById('completion-scope-national-short');
  if (completionScatterScope !== 'national') {{
    if (option) option.title = 'Nation scope';
    if (text) text.textContent = 'Nations';
    if (short) short.textContent = 'N';
    return;
  }}
  const nation = activeCompletionNation();
  const label = displayNationName(nation);
  if (option) option.title = `${{label}} scope`;
  if (text) text.textContent = label;
  if (short) short.textContent = completionNationShortLabel(nation);
}}

function cityCatchmentForRow(row) {{
  const lat = Number(row?.lat);
  const lon = Number(row?.lon);
  if (!Number.isFinite(lat) || !Number.isFinite(lon)) return null;
  let best = null;
  cityCatchments.forEach((city) => {{
    const distance = distanceMiles(lat, lon, Number(city.lat), Number(city.lon));
    if (distance > Number(city.radius_miles)) return;
    if (!best || distance < best.distance) {{
      best = {{ city, distance }};
    }}
  }});
  return best ? best.city : null;
}}

function rowsWithinCircle(rowsSubset, lat, lon, radiusMiles) {{
  return rowsSubset.filter((row) => {{
    const rowLat = Number(row?.lat);
    const rowLon = Number(row?.lon);
    if (!Number.isFinite(rowLat) || !Number.isFinite(rowLon)) return false;
    return distanceMiles(lat, lon, rowLat, rowLon) <= radiusMiles;
  }});
}}

function northSouthBucketForRow(row) {{
  const lat = Number(row?.lat);
  const lon = Number(row?.lon);
  if (!Number.isFinite(lat) || !Number.isFinite(lon)) return null;
  const lonSpan = northSouthDivide.east.lon - northSouthDivide.west.lon;
  if (!Number.isFinite(lonSpan) || lonSpan === 0) return null;
  const t = (lon - northSouthDivide.west.lon) / lonSpan;
  const boundaryLat = northSouthDivide.west.lat + (t * (northSouthDivide.east.lat - northSouthDivide.west.lat));
  return lat >= boundaryLat ? 'North' : 'South';
}}

const allKnownRows = rows.concat(nationalSupplementals);
const allKnownRowsByCode = (() => {{
  const grouped = new Map();
  allKnownRows.forEach((row) => {{
    const code = String(row?.code || '').trim();
    if (code && !grouped.has(code)) grouped.set(code, row);
  }});
  return grouped;
}})();
const totalKnownGoogleReviews = allKnownRows.reduce((sum, row) => {{
  const count = numericOrNull(row?.google_count);
  return sum + (count !== null && count > 0 ? count : 0);
}}, 0);
const cityRowsByCatchment = (() => {{
  const grouped = new Map(cityCatchments.map((city) => [city.name, []]));
  allKnownRows.forEach((row) => {{
    const city = cityCatchmentForRow(row);
    if (city && grouped.has(city.name)) {{
      grouped.get(city.name).push(row);
    }}
  }});
  return grouped;
}})();
const northSouthRows = (() => {{
  const grouped = new Map([['North', []], ['South', []]]);
  allKnownRows.forEach((row) => {{
    const bucket = northSouthBucketForRow(row);
    if (bucket && grouped.has(bucket)) {{
      grouped.get(bucket).push(row);
    }}
  }});
  return grouped;
}})();
const compositeRegionRowsByLabel = (() => {{
  const grouped = new Map();
  compositeRegionDefinitions.forEach((definition) => {{
    const subset = (definition?.codes || [])
      .map((code) => allKnownRowsByCode.get(String(code || '').trim()))
      .filter(Boolean);
    grouped.set(definition.label, subset);
  }});
  return grouped;
}})();
const regionGoogleSortedValues = allKnownRows
  .map((row) => numericOrNull(row.google_score))
  .filter((value) => value !== null && Number.isFinite(value))
  .sort((left, right) => left - right);
const regionSurveySortedValues = allKnownRows
  .map((row) => numericOrNull(row.survey_overall_good_percent))
  .filter((value) => value !== null && Number.isFinite(value))
  .sort((left, right) => left - right);
const globalGoogleAverage = mean(regionGoogleSortedValues);
const globalSurveyAverage = mean(regionSurveySortedValues);

function positivePatientCount(row) {{
  const patients = numericOrNull(row?.registered_patient_count);
  return patients !== null && patients > 0 ? patients : null;
}}

function regionAverage(rowsSubset, extractor) {{
  const values = rowsSubset
    .map((row) => extractor(row))
    .filter((value) => value !== null && Number.isFinite(value));
  return {{
    value: values.length ? mean(values) : null,
    count: values.length,
  }};
}}

function formatPatientTotal(value) {{
  if (value === null || !Number.isFinite(value) || value <= 0) return '?';
  if (value >= 1000000) {{
    const millions = value / 1000000;
    return `${{millions >= 10 ? millions.toFixed(0) : millions.toFixed(1)}}m`;
  }}
  if (value >= 1000) {{
    const thousands = value / 1000;
    return `${{thousands >= 100 ? thousands.toFixed(0) : thousands.toFixed(1)}}k`;
  }}
  return Math.round(value).toLocaleString('en-GB');
}}

function formatAverageDelta(metricName, value) {{
  if (value === null || !Number.isFinite(value)) return null;
  const globalAverage = metricName === 'google' ? globalGoogleAverage : globalSurveyAverage;
  if (globalAverage === null || !Number.isFinite(globalAverage)) return null;
  const delta = value - globalAverage;
  const tolerance = metricName === 'google' ? 0.04 : 1.5;
  if (Math.abs(delta) <= tolerance) return 'around dataset avg';
  if (metricName === 'google') {{
    return `${{Math.abs(delta).toFixed(2)}} ${{delta > 0 ? 'above' : 'below'}} dataset avg`;
  }}
  return `${{Math.abs(delta).toFixed(1)}}pp ${{delta > 0 ? 'above' : 'below'}} dataset avg`;
}}

function datasetToneForAverage(metricName, value) {{
  if (value === null || !Number.isFinite(value)) return 'tone-missing';
  const globalAverage = metricName === 'google' ? globalGoogleAverage : globalSurveyAverage;
  if (globalAverage === null || !Number.isFinite(globalAverage)) return 'tone-missing';
  const delta = value - globalAverage;
  const tolerance = metricName === 'google' ? 0.04 : 1.5;
  if (Math.abs(delta) <= tolerance) return 'tone-mid';
  return delta > 0 ? 'tone-good' : 'tone-bad';
}}

function globalGapAverage() {{
  const values = allKnownRows
    .map((row) => gapValue(row, {{ suppressSmall: false }}))
    .filter((value) => value !== null && Number.isFinite(value));
  return values.length ? mean(values) : null;
}}

function formatGapDeltaFromAverage(value) {{
  if (value === null || !Number.isFinite(value)) return '?';
  return activeGapMode === 'normalized'
    ? `${{value >= 0 ? '+' : ''}}${{value.toFixed(2)}}z`
    : `${{value >= 0 ? '+' : ''}}${{value.toFixed(2)}}`;
}}

function gapDeltaTone(delta) {{
  if (delta === null || !Number.isFinite(delta)) return 'tone-missing';
  const tolerance = activeGapMode === 'normalized' ? 0.08 : 0.05;
  if (Math.abs(delta) <= tolerance) return 'tone-mid';
  return delta > 0 ? 'tone-good' : 'tone-bad';
}}

function regionCardStats(rowsSubset) {{
  const google = regionAverage(rowsSubset, (row) => numericOrNull(row.google_score));
  const survey = regionAverage(rowsSubset, (row) => numericOrNull(row.survey_overall_good_percent));
  const gap = regionAverage(rowsSubset, (row) => gapValue(row, {{ suppressSmall: false }}));
  const patientTotal = rowsSubset.reduce((sum, row) => sum + (positivePatientCount(row) || 0), 0);
  return {{
    practiceCount: rowsSubset.length,
    patientTotal: patientTotal > 0 ? patientTotal : null,
    google,
    survey,
    gap,
  }};
}}

function regionCountsMarkup(stats) {{
  return `
    <div class="place-benchmark-counts">
      <span>${{formatPatientTotal(stats.patientTotal)}} <small>&#128101;</small></span>
      <span class="place-benchmark-count-divider">/</span>
      <span>${{stats.practiceCount.toLocaleString('en-GB')}} <small>&#127973;</small></span>
    </div>
  `;
}}

function regionStatBoxMarkup(label, value, subtle, isActive, toneClass, extraClass = '') {{
  const title = subtle ? ` title="${{escapeHtml(String(subtle))}}"` : '';
  return `
    <div class="place-benchmark-stat${{isActive ? ' is-active' : ''}}${{extraClass ? ` ${{extraClass}}` : ''}}"${{title}}>
      <span class="place-benchmark-stat-label">${{label}}</span>
      <span class="place-benchmark-stat-value ${{toneClass || 'tone-missing'}}">${{value}}</span>
    </div>
  `;
}}

function surveyWarningForSubset(title, rowsSubset) {{
  const nations = Array.from(
    new Set(
      rowsSubset
        .map((row) => String(row?.nation || '').trim().toLowerCase())
        .filter(Boolean)
    )
  );
  if (!nations.length) return null;
  const onlyNation = nations.length === 1 ? nations[0] : null;
  if (onlyNation === 'wales' || title === 'Cardiff') {{
    return 'Wales does not currently have a standardized national practice-level survey feed here. Some Welsh practices appear to publish local survey results, but there is no comparable national dashboard, and mixing those local returns into this view would add noise.';
  }}
  if (onlyNation === 'northern_ireland' || title === 'Belfast') {{
    return 'Northern Ireland does not currently have a live standardized national practice-level survey feed here, so survey comparisons for this panel are incomplete.';
  }}
  return null;
}}

function regionCardMarkup(title, rowsSubset, accent) {{
  const stats = regionCardStats(rowsSubset);
  const googleValue = stats.google.value === null ? '?' : stats.google.value.toFixed(2);
  const surveyValue = stats.survey.value === null ? '?' : `${{stats.survey.value.toFixed(0)}}%`;
  const googleTone = datasetToneForAverage('google', stats.google.value);
  const surveyTone = datasetToneForAverage('survey', stats.survey.value);
  const googleDelta = formatAverageDelta('google', stats.google.value);
  const surveyDelta = formatAverageDelta('survey', stats.survey.value);
  const googleSubtle = stats.google.count
    ? `${{googleDelta || 'dataset avg unavailable'}} · ${{stats.google.count.toLocaleString('en-GB')}} scored`
    : 'Google score not yet present';
  const surveySubtle = stats.survey.count
    ? `${{surveyDelta || 'dataset avg unavailable'}} · ${{stats.survey.count.toLocaleString('en-GB')}} scored`
    : 'Survey score not yet present';
  const isGoogleActive = activeMetric === 'google';
  const isSurveyActive = activeMetric === 'survey';
  const surveyWarning = surveyWarningForSubset(title, rowsSubset);
  const surveyLabel = surveyWarning ? 'Survey <span class="place-benchmark-stat-label-warning" aria-hidden="true">!</span>' : 'Survey';
  const surveyTitle = surveyWarning
    ? `${{surveySubtle}} · ${{surveyWarning}}`
    : surveySubtle;
  const surveyExtraClass = surveyWarning ? 'is-warning' : '';
  if (activeMetric === 'gap') {{
    const overallGapAverage = globalGapAverage();
    const gapDelta = stats.gap.value === null || overallGapAverage === null ? null : stats.gap.value - overallGapAverage;
    const gapSubtle = stats.gap.count
      ? `Region avg: ${{metricConfigs.gap.averageLabel(stats.gap.value)}} · overall avg: ${{metricConfigs.gap.averageLabel(overallGapAverage)}} · ${{stats.gap.count.toLocaleString('en-GB')}} scored`
      : 'Gap score not yet present';
    return `
      <article class="comparison-card place-benchmark-card" style="border-top-color:${{accent}};">
        <div class="place-benchmark-header">
          <h3>${{title}}</h3>
          ${{regionCountsMarkup(stats)}}
        </div>
        <div class="place-benchmark-stats">
          ${{regionStatBoxMarkup('Gap vs avg', formatGapDeltaFromAverage(gapDelta), gapSubtle, true, gapDeltaTone(gapDelta), 'is-wide')}}
        </div>
      </article>
    `;
  }}
  return `
    <article class="comparison-card place-benchmark-card" style="border-top-color:${{accent}};">
      <div class="place-benchmark-header">
        <h3>${{title}}</h3>
        ${{regionCountsMarkup(stats)}}
      </div>
      <div class="place-benchmark-stats">
        ${{regionStatBoxMarkup('Google', googleValue, googleSubtle, isGoogleActive, googleTone)}}
        ${{regionStatBoxMarkup(surveyLabel, surveyValue, surveyTitle, isSurveyActive, surveyTone, surveyExtraClass)}}
      </div>
    </article>
  `;
}}

function renderCityCircles() {{
  cityCircleLayer.clearLayers();
  if (!showCityCircles) return;
  cityCatchments.forEach((city) => {{
    const subset = cityRowsByCatchment.get(city.name) || [];
    if (!subset.length) return;
    const circle = L.circle([city.lat, city.lon], {{
      radius: Number(city.radius_miles) * 1609.344,
      color: city.accent,
      weight: 2,
      opacity: 0.65,
      fillColor: city.accent,
      fillOpacity: 0.04,
      dashArray: '6 6',
      interactive: false,
    }});
    circle.bindTooltip(`${{city.name}} · ${{subset.length}} practices`, {{ sticky: false, opacity: 0.92 }});
    circle.addTo(cityCircleLayer);
  }});
}}

function renderSampleCircle() {{
  sampleCircleLayer.clearLayers();
  if (!sampleCircleCenter) return;
  const circle = L.circle([sampleCircleCenter.lat, sampleCircleCenter.lon], {{
    radius: Number(sampleCircleRadiusMiles) * 1609.344,
    color: '#161816',
    weight: 2.2,
    opacity: 0.9,
    fillColor: '#161816',
    fillOpacity: 0.05,
    dashArray: '10 6',
  }});
  circle.bindTooltip(`Custom sample · ${{sampleCircleRadiusMiles.toFixed(1)}} miles`, {{ sticky: false, opacity: 0.95 }});
  circle.addTo(sampleCircleLayer);
}}

function updateSampleCircleControls() {{
  const sampleButton = document.getElementById('sample-circle-button');
  const clearButton = document.getElementById('clear-sample-circle-button');
  const note = document.getElementById('sample-circle-note');
  const radiusLabel = document.getElementById('sample-circle-radius-label');
  const radiusControl = document.querySelector('.circle-radius-control');
  const cityToggleLabel = document.getElementById('city-circles-control');
  if (sampleButton) sampleButton.classList.toggle('is-active', sampleCircleArmed);
  if (clearButton) clearButton.disabled = !sampleCircleCenter;
  if (radiusControl) radiusControl.hidden = !sampleCircleCenter;
  if (radiusLabel) radiusLabel.textContent = `${{sampleCircleRadiusMiles.toFixed(sampleCircleRadiusMiles % 1 === 0 ? 0 : 1)}} miles`;
  if (cityToggleLabel) cityToggleLabel.classList.toggle('is-active', showCityCircles);
  if (note) {{
    note.textContent = sampleCircleArmed
      ? 'Click on the map to place the sample.'
      : sampleCircleCenter
        ? 'Drag the radius slider to resize the current sample.'
        : '';
  }}
}}

function googleCoverageRatio(rowsSubset) {{
  if (!rowsSubset.length) return 0;
  const covered = rowsSubset.filter((row) => numericOrNull(row.google_score) !== null).length;
  return covered / rowsSubset.length;
}}

function renderPlaceBenchmarks() {{
  const heading = document.getElementById('place-benchmark-heading');
  const note = document.getElementById('place-benchmark-note');
  const nationHeading = document.getElementById('nation-benchmark-heading');
  const cityHeading = document.getElementById('city-benchmark-heading');
  const nationGrid = document.getElementById('nation-benchmark-grid');
  const cityGrid = document.getElementById('city-benchmark-grid');
  if (!heading || !note || !nationGrid || !cityGrid) return;

  heading.textContent = 'Nation and City Benchmarks';
  if (nationHeading) nationHeading.textContent = 'Nations';
  if (cityHeading) cityHeading.textContent = 'Cities and composites';
  const sampleRows = sampleCircleCenter
    ? rowsWithinCircle(allKnownRows, sampleCircleCenter.lat, sampleCircleCenter.lon, sampleCircleRadiusMiles)
    : [];

  const nationCards = nationOrder
    .map((nation) => {{
      const subset = allKnownRows.filter((row) => String(row?.nation || '').trim().toLowerCase() === nation);
      if (!subset.length) return '';
      return regionCardMarkup(
        displayNationName(nation),
        subset,
        nation === 'england' ? '#8d3c17' : nation === 'scotland' ? '#2f6fa5' : nation === 'wales' ? '#3f7d4c' : '#6b4f9d'
      );
    }})
    .filter(Boolean)
    .join('');

  const cityCards = cityCatchments
    .map((city) => {{
      const subset = cityRowsByCatchment.get(city.name) || [];
      if (!subset.length) return '';
      return regionCardMarkup(city.name, subset, city.accent);
    }})
    .concat(
      [
        ['North', '#315f8f'],
        ['South', '#8c5a2a'],
      ].map(([label, accent]) => {{
        const subset = northSouthRows.get(label) || [];
        if (!subset.length) return '';
        return regionCardMarkup(label, subset, accent);
      }})
    )
    .concat(
      compositeRegionDefinitions.map((definition) => {{
        const subset = compositeRegionRowsByLabel.get(definition.label) || [];
        if (!subset.length) return '';
        return regionCardMarkup(definition.label, subset, definition.accent);
      }})
    )
    .filter(Boolean)
    .join('');

  const sampleCard = sampleRows.length
    ? regionCardMarkup(
        `Custom sample · ${{sampleCircleRadiusMiles.toFixed(sampleCircleRadiusMiles % 1 === 0 ? 0 : 1)}} mile radius`,
        sampleRows,
        '#161816'
      )
    : '';

  nationGrid.innerHTML = nationCards || '<p class="hint">No nation summaries are available yet.</p>';
  cityGrid.innerHTML = (sampleCard + cityCards) || '<p class="hint">No city-circle summaries are available yet.</p>';
  note.innerHTML = `${{allKnownRows.length.toLocaleString('en-GB')}} practices · ${{totalKnownGoogleReviews.toLocaleString('en-GB')}} Google reviews loaded overall.${{sampleRows.length ? ` Custom sample: ${{sampleRows.length.toLocaleString('en-GB')}} practices.` : ''}} Sparse/dense composites use bottom/top fifths by nearby-practice count within ${{Number({COMPOSITE_REGION_RADIUS_MILES}).toFixed(Number({COMPOSITE_REGION_RADIUS_MILES}) % 1 === 0 ? 0 : 1)}} miles, leaving the middle three-fifths neutral. List-size composites are separate: they use bottom/top fifths by registered patient count per practice, not local area population density, and rows without a patient count are excluded. <span class="hint">Footnote: Wales and Northern Ireland do not currently have comparable national practice-level survey feeds here. Some Welsh practices appear to publish local survey results, but there is no standardized national dashboard, and forcing those into the same pool would be easy to misread, especially given the limits of England's own standard survey.</span>`;
}}

function metricValues(rowsSubset, metricName, extractor = null) {{
  const metric = metricConfigs[metricName];
  return rowsSubset
    .map((row) => extractor ? extractor(row) : metric.value(row))
    .filter((value) => value !== null && Number.isFinite(value));
}}

function formatMetricValue(value, metricName) {{
  if (value === null) return '?';
  if (metricName === 'survey') return `${{Math.round(value)}}%`;
  return value.toFixed(metricName === 'gap' ? 2 : 1);
}}

function currentMetricValueForRow(row, options = {{}}) {{
  if (!row) return null;
  if (activeMetric === 'gap') {{
    return gapValue(row, {{ suppressSmall: options.suppressSmall === true }});
  }}
  return metricConfigs[activeMetric].value(row);
}}

function colorForCurrentMetric(row, options = {{}}) {{
  if (!row) return '#9aa0a6';
  if (activeMetric !== 'gap') return metricConfigs[activeMetric].markerColor(row);
  const value = gapValue(row, {{ suppressSmall: options.suppressSmall === true }});
  if (value === null) return '#9aa0a6';
  if (activeGapMode === 'normalized') {{
    if (value >= 0.75) return '#1c7c54';
    if (value >= 0.25) return '#4c9a52';
    if (value > -0.25) return '#d2b529';
    if (value > -0.75) return '#dc8c23';
    return '#c3472f';
  }}
  if (value >= 1.0) return '#1c7c54';
  if (value >= 0.5) return '#4c9a52';
  if (value > -0.5) return '#d2b529';
  if (value > -1.0) return '#dc8c23';
  return '#c3472f';
}}

function compactMetricValue(value, metricName) {{
  if (value === null) return '?';
  if (metricName === 'survey') return `${{Math.round(value)}}%`;
  if (metricName === 'google') return value.toFixed(1);
  return activeGapMode === 'normalized'
    ? `${{value >= 0 ? '+' : ''}}${{value.toFixed(1)}}z`
    : `${{value >= 0 ? '+' : ''}}${{value.toFixed(1)}}`;
}}

function compactPatientCount(value) {{
  if (!Number.isFinite(value)) return '?';
  if (value >= 100000) return `${{Math.round(value / 1000)}}k`;
  if (value >= 10000) return `${{(value / 1000).toFixed(1)}}k`;
  return Math.round(value).toLocaleString('en-GB');
}}

function ellipsize(text, maxChars) {{
  if (!text) return '';
  if (text.length <= maxChars) return text;
  return maxChars <= 3 ? text.slice(0, maxChars) : `${{text.slice(0, Math.max(0, maxChars - 3))}}...`;
}}

function metricToneClass(metricName, value) {{
  if (value === null) return 'tone-missing';
  if (metricName === 'google') {{
    if (value < 3) return 'tone-bad';
    if (value < 4) return 'tone-mid';
    return 'tone-good';
  }}
  if (metricName === 'survey') {{
    if (value < 60) return 'tone-bad';
    if (value < 75) return 'tone-mid';
    return 'tone-good';
  }}
  if (metricName === 'gap') {{
    if (activeGapMode === 'normalized') {{
      if (value <= -0.75) return 'tone-bad';
      if (value <= -0.25) return 'tone-mid';
      return 'tone-good';
    }}
    if (value <= -1) return 'tone-bad';
    if (value <= -0.5) return 'tone-mid';
    return 'tone-good';
  }}
  return 'tone-missing';
}}

function comparisonSense(metricName) {{
  return metricName === 'gap' ? 'higher' : 'higher';
}}

function deltaSentence(subjectValue, benchmarkValue, metricName) {{
  if (subjectValue === null || benchmarkValue === null) return 'insufficient data';
  const delta = subjectValue - benchmarkValue;
  if (Math.abs(delta) < (metricName === 'survey' ? 1 : 0.1)) return 'roughly in line';
  if (comparisonSense(metricName) === 'higher') {{
    return delta > 0
      ? `${{formatMetricValue(Math.abs(delta), metricName)}} above`
      : `${{formatMetricValue(Math.abs(delta), metricName)}} below`;
  }}
  return delta < 0
    ? `${{formatMetricValue(Math.abs(delta), metricName)}} lower gap`
    : `${{formatMetricValue(Math.abs(delta), metricName)}} higher gap`;
}}

function benchmarkPhrase(subjectValue, benchmarkValue, metricName, label) {{
  if (benchmarkValue === null) return `no ${{label}} comparison yet`;
  const delta = deltaSentence(subjectValue, benchmarkValue, metricName);
  if (delta === 'roughly in line') return `about the same as the ${{label}} typical score`;
  if (delta === 'insufficient data') return `not enough data for the ${{label}} comparison`;
  return `${{delta}} than the ${{label}} typical score`;
}}

function performancePercentile(values, subjectValue, metricName) {{
  if (!values.length || subjectValue === null) return null;
  if (comparisonSense(metricName) === 'higher') {{
    return percentile(values.slice().sort((left, right) => left - right), subjectValue);
  }}
  const reversed = values.map((value) => -value).sort((left, right) => left - right);
  return percentile(reversed, -subjectValue);
}}

function performanceCounts(values, subjectValue, metricName) {{
  if (!values.length || subjectValue === null) return {{ better: 0, worse: 0 }};
  if (comparisonSense(metricName) === 'higher') {{
    return {{
      better: values.filter((value) => subjectValue > value).length,
      worse: values.filter((value) => subjectValue < value).length
    }};
  }}
  return {{
    better: values.filter((value) => subjectValue < value).length,
    worse: values.filter((value) => subjectValue > value).length
  }};
}}

function benchmarkStats(subjectRows, localRows, regionalRows, metricName, subjectMode) {{
  const subjectValues = metricValues(
    subjectRows,
    metricName,
    metricName === 'gap' && subjectMode === 'single'
      ? (row) => gapValue(row, {{ suppressSmall: false }})
      : null
  );
  const localValues = metricValues(localRows, metricName);
  const regionalValues = metricValues(regionalRows, metricName);
  const completionSubjectValues = metricValues(subjectRows, metricName, (row) => numericOrNull(row.survey_completion_rate_percent));
  const completionLocalValues = metricValues(localRows, metricName, (row) => numericOrNull(row.survey_completion_rate_percent));
  const completionRegionalValues = metricValues(regionalRows, metricName, (row) => numericOrNull(row.survey_completion_rate_percent));
  const subjectValue = subjectMode === 'single'
    ? (subjectValues.length ? subjectValues[0] : null)
    : mean(subjectValues);
  const completionValue = subjectMode === 'single'
    ? (completionSubjectValues.length ? completionSubjectValues[0] : null)
    : mean(completionSubjectValues);
  return {{
    subjectValue,
    subjectCount: subjectValues.length,
    localMedian: median(localValues),
    localCount: localValues.length,
    regionalMedian: median(regionalValues),
    regionalCount: regionalValues.length,
    regionalPercentile: performancePercentile(regionalValues, subjectValue, metricName),
    regionalPerformanceCounts: performanceCounts(regionalValues, subjectValue, metricName),
    completionValue,
    completionLocalMedian: median(completionLocalValues),
    completionLocalCount: completionLocalValues.length,
    completionRegionalMedian: median(completionRegionalValues),
    completionRegionalCount: completionRegionalValues.length,
    completionRegionalPercentile: performancePercentile(completionRegionalValues, completionValue, 'survey')
  }};
}}

function comparisonCardMarkup(title, kicker, summary, rowsMarkup, variant = '') {{
  const cardClass = ['comparison-card', variant].filter(Boolean).join(' ');
  return `
    <article class="${{cardClass}}">
      <h3>${{title}}</h3>
      <p class="comparison-kicker">${{kicker}}</p>
      <div class="comparison-summary">${{summary}}</div>
      <div class="comparison-metrics">${{rowsMarkup}}</div>
    </article>
  `;
}}

function comparisonRowMarkup(label, subjectLabel, subjectValue, subjectMeta, subjectTone, localLabel, localValue, localMeta, localTone, regionalLabel, regionalValue, regionalMeta, regionalTone, deltaText, deltaTone) {{
  return `
    <div class="comparison-row">
      <div class="comparison-label">${{label}}</div>
      <div class="comparison-stat">
        <strong class="${{subjectTone}}">${{subjectValue}}</strong>
        <span>${{subjectLabel}}${{subjectMeta ? ` · ${{subjectMeta}}` : ''}}</span>
      </div>
      <div class="comparison-stat">
        <strong class="${{localTone}}">${{localValue}}</strong>
        <span>${{localLabel}}${{localMeta ? ` · ${{localMeta}}` : ''}}</span>
      </div>
      <div class="comparison-stat">
        <strong class="${{regionalTone}}">${{regionalValue}}</strong>
        <span>${{regionalLabel}}${{regionalMeta ? ` · ${{regionalMeta}}` : ''}}</span>
      </div>
      <div class="comparison-delta ${{deltaTone}}">${{deltaText}}</div>
    </div>
  `;
}}

function deltaToneClass(subjectValue, benchmarkValue, metricName) {{
  if (subjectValue === null || benchmarkValue === null) return 'tone-missing';
  const delta = subjectValue - benchmarkValue;
  if (Math.abs(delta) < (metricName === 'survey' ? 1 : 0.1)) return 'tone-mid';
  if (comparisonSense(metricName) === 'higher') return delta > 0 ? 'tone-good' : 'tone-bad';
  return delta < 0 ? 'tone-good' : 'tone-bad';
}}

function countUnitLabel(count, pluralUnit) {{
  if (pluralUnit === 'practices') return count === 1 ? 'practice' : 'practices';
  if (pluralUnit === 'management companies') return count === 1 ? 'management company' : 'management companies';
  return pluralUnit;
}}

function metricScopeLabel(metricName) {{
  if (metricName === 'google') return 'Google rating';
  if (metricName === 'survey') return 'patient survey overall good %';
  return activeGapMode === 'normalized' ? 'normalised survey/Google gap' : 'survey/Google gap';
}}

function metricDisplayLabel(metricName) {{
  if (metricName === 'google') return 'Reviews';
  if (metricName === 'survey') return 'Patient Survey';
  return activeGapMode === 'normalized' ? 'Normalised Gap' : 'Gap';
}}

function nearbyLabelForMode(subjectMode) {{
  return subjectMode === 'group' ? 'nearby non-company average' : 'nearby average';
}}

function widerLabel() {{
  return 'the wider map average';
}}

function rankBarMarkup(countStats, pluralUnit) {{
  if (!countStats) return '';
  const better = Number(countStats.better || 0);
  const worse = Number(countStats.worse || 0);
  const total = better + worse;
  if (total <= 0) return '';
  const position = (better / total) * 100;
  return `
    <div class="rank-bar" aria-label="Relative performance bar">
      <div class="rank-bar-track">
        <span class="rank-bar-marker" style="left:${{position.toFixed(1)}}%"></span>
      </div>
      <div class="rank-bar-labels">
        <span class="rank-worse">Worse than <strong>${{worse}}</strong> ${{countUnitLabel(worse, pluralUnit)}}</span>
        <span class="rank-better">Better than <strong>${{better}}</strong> ${{countUnitLabel(better, pluralUnit)}}</span>
      </div>
    </div>
  `;
}}

function practiceComparisonCard(row, title, kicker, variant = '') {{
  const metric = metricConfigs[activeMetric];
  const localRows = rows.filter((candidate) =>
    candidate.code !== row.code &&
    distanceMiles(row.lat, row.lon, candidate.lat, candidate.lon) <= LOCAL_RADIUS_MILES
  );
  const regionalRows = rows.filter((candidate) => candidate.code !== row.code);
  const stats = benchmarkStats([row], localRows, regionalRows, activeMetric, 'single');
  const summary = stats.subjectValue === null
    ? `<p>${{title}} does not have enough ${{metric.title.toLowerCase()}} data yet.</p>`
    : (() => {{
        const localPhrase = benchmarkPhrase(stats.subjectValue, stats.localMedian, activeMetric, nearbyLabelForMode('single'));
        const regionalPhrase = benchmarkPhrase(stats.subjectValue, stats.regionalMedian, activeMetric, widerLabel());
        const percentilePhrase = stats.regionalPercentile === null
          ? ''
          : ` It sits around the ${{Math.round(stats.regionalPercentile)}}th percentile on this map.`;
        return `<p>On ${{metricScopeLabel(activeMetric)}}, ${{title}} is ${{localPhrase}} and ${{regionalPhrase}}.${{percentilePhrase}}</p>${{rankBarMarkup(stats.regionalPerformanceCounts, 'practices')}}`;
      }})();
  return comparisonCardMarkup(
    title,
    kicker,
    summary,
    [
      comparisonRowMarkup(
        'Current score',
        'This practice',
        formatMetricValue(stats.subjectValue, activeMetric),
        stats.subjectCount ? `${{stats.subjectCount}} usable value` : '',
        metricToneClass(activeMetric, stats.subjectValue),
        'Nearby average',
        formatMetricValue(stats.localMedian, activeMetric),
        `${{stats.localCount}} peers`,
        metricToneClass(activeMetric, stats.localMedian),
        'Wider map average',
        formatMetricValue(stats.regionalMedian, activeMetric),
        `${{stats.regionalCount}} peers`,
        metricToneClass(activeMetric, stats.regionalMedian),
        stats.localMedian === null && stats.regionalMedian === null
          ? 'No comparison available yet'
          : `Nearby: ${{deltaSentence(stats.subjectValue, stats.localMedian, activeMetric)}}. Wider map: ${{deltaSentence(stats.subjectValue, stats.regionalMedian, activeMetric)}}.`,
        deltaToneClass(stats.subjectValue, stats.regionalMedian ?? stats.localMedian, activeMetric)
      ),
      comparisonRowMarkup(
        'Survey reply rate',
        'This practice',
        formatMetricValue(stats.completionValue, 'survey'),
        '',
        metricToneClass('survey', stats.completionValue),
        'Nearby average',
        formatMetricValue(stats.completionLocalMedian, 'survey'),
        `${{stats.completionLocalCount}} peers`,
        metricToneClass('survey', stats.completionLocalMedian),
        'Wider map average',
        formatMetricValue(stats.completionRegionalMedian, 'survey'),
        `${{stats.completionRegionalCount}} peers`,
        metricToneClass('survey', stats.completionRegionalMedian),
        stats.completionRegionalPercentile === null
          ? 'Reply-rate comparison unavailable'
          : `Reply rate sits around the ${{Math.round(stats.completionRegionalPercentile)}}th percentile on this map.`,
        deltaToneClass(stats.completionValue, stats.completionRegionalMedian ?? stats.completionLocalMedian, 'survey')
      )
    ].join(''),
    variant
  );
}}

function managementCompanyComparisonCard(company, title, kicker, variant = '') {{
  const metric = metricConfigs[activeMetric];
  const companyRows = company.rows;
  const companyOtherRows = rows.filter((row) => row.management_company !== company.name);
  const companyLocalRows = companyOtherRows.filter((row) =>
    companyRows.some((companyRow) => distanceMiles(companyRow.lat, companyRow.lon, row.lat, row.lon) <= LOCAL_RADIUS_MILES)
  );
  const stats = benchmarkStats(companyRows, companyLocalRows, companyOtherRows, activeMetric, 'group');
  const otherManagementCompanyValues = managementCompanies
    .filter((candidate) => candidate.name !== company.name)
    .map((candidate) => averageMetric(candidate.rows, activeMetric))
    .filter((value) => value !== null);
  const companyManagementPercentile = performancePercentile(otherManagementCompanyValues, stats.subjectValue, activeMetric);
  const companyManagementCounts = performanceCounts(otherManagementCompanyValues, stats.subjectValue, activeMetric);
  const summary = stats.subjectValue === null
    ? `<p>${{title}} does not have enough ${{metric.title.toLowerCase()}} data yet.</p>`
    : (() => {{
        const localPhrase = benchmarkPhrase(stats.subjectValue, stats.localMedian, activeMetric, nearbyLabelForMode('group'));
        const regionalPhrase = benchmarkPhrase(stats.subjectValue, stats.regionalMedian, activeMetric, widerLabel());
        const percentilePhrase = companyManagementPercentile === null
          ? ''
          : ` It sits around the ${{Math.round(companyManagementPercentile)}}th percentile against the other management companies on this map.`;
        return `<p>On ${{metricScopeLabel(activeMetric)}}, ${{title}} is ${{localPhrase}} and ${{regionalPhrase}}.${{percentilePhrase}}</p>${{rankBarMarkup(companyManagementCounts, 'management companies')}}`;
      }})();
  return comparisonCardMarkup(
    title,
    kicker,
    summary,
    [
      comparisonRowMarkup(
        'Current average',
        'Company average',
        formatMetricValue(stats.subjectValue, activeMetric),
        `${{stats.subjectCount}} practices with data`,
        metricToneClass(activeMetric, stats.subjectValue),
        'Nearby others',
        formatMetricValue(stats.localMedian, activeMetric),
        `${{stats.localCount}} peers`,
        metricToneClass(activeMetric, stats.localMedian),
        'Wider map average',
        formatMetricValue(stats.regionalMedian, activeMetric),
        `${{stats.regionalCount}} peers`,
        metricToneClass(activeMetric, stats.regionalMedian),
        stats.localMedian === null && stats.regionalMedian === null
          ? 'No comparison available yet'
          : `Nearby others: ${{deltaSentence(stats.subjectValue, stats.localMedian, activeMetric)}}. Wider map: ${{deltaSentence(stats.subjectValue, stats.regionalMedian, activeMetric)}}.`,
        deltaToneClass(stats.subjectValue, stats.regionalMedian ?? stats.localMedian, activeMetric)
      ),
      comparisonRowMarkup(
        'Survey reply rate',
        'Company average',
        formatMetricValue(stats.completionValue, 'survey'),
        `${{metricValues(companyRows, 'survey', (row) => numericOrNull(row.survey_completion_rate_percent)).length}} practices with data`,
        metricToneClass('survey', stats.completionValue),
        'Nearby others',
        formatMetricValue(stats.completionLocalMedian, 'survey'),
        `${{stats.completionLocalCount}} peers`,
        metricToneClass('survey', stats.completionLocalMedian),
        'Wider map average',
        formatMetricValue(stats.completionRegionalMedian, 'survey'),
        `${{stats.completionRegionalCount}} peers`,
        metricToneClass('survey', stats.completionRegionalMedian),
        stats.completionRegionalPercentile === null
          ? 'Reply-rate comparison unavailable'
          : `Reply rate sits around the ${{Math.round(stats.completionRegionalPercentile)}}th percentile on this map.`,
        deltaToneClass(stats.completionValue, stats.completionRegionalMedian ?? stats.completionLocalMedian, 'survey')
      )
    ].join(''),
    variant
  );
}}

function renderComparisons() {{
  const grid = document.getElementById('comparison-grid');
  const note = document.getElementById('comparison-note');
  const heading = document.getElementById('comparison-heading');
  const baselinePractice = rows.find((row) => row.code === NEW_BANK_CODE) || rows[0];
  const focusedPractice = rows.find((row) => row.code === focusedPracticeCode) || baselinePractice;
  const baselineCompany = managementCompanies.find((company) => company.name === BASELINE_MANAGEMENT_COMPANY) || null;
  const selectedCompanies = managementCompanies.filter((company) =>
    selectedManagementCompanies.has(company.name) && company.name !== BASELINE_MANAGEMENT_COMPANY
  );
  heading.textContent = `Quick comparisons - Showing ${{metricDisplayLabel(activeMetric)}}`;
  note.textContent = `New Bank and GTD always stay visible here. Click a practice on the map to compare it with New Bank. Use the management tickboxes to compare other companies with GTD. “Nearby” means within ${{LOCAL_RADIUS_MILES.toFixed(1)}} miles.`;

  const cards = [
    practiceComparisonCard(
      baselinePractice,
      baselinePractice.name,
      `Baseline practice${{baselinePractice.postcode ? ` · ${{baselinePractice.postcode}}` : ''}}`,
      'is-baseline'
    )
  ];

  if (focusedPractice && focusedPractice.code !== baselinePractice.code) {{
    cards.push(
      practiceComparisonCard(
        focusedPractice,
        focusedPractice.name,
        `Selected practice${{focusedPractice.postcode ? ` · ${{focusedPractice.postcode}}` : ''}}`,
        'is-selected'
      )
    );
  }}

  if (baselineCompany) {{
    cards.push(
      managementCompanyComparisonCard(
        baselineCompany,
        baselineCompany.name,
        `Baseline management company · ${{baselineCompany.count}} practices`,
        'is-baseline'
      )
    );
  }}

  selectedCompanies.forEach((company) => {{
    cards.push(
      managementCompanyComparisonCard(
        company,
        company.name,
        `Selected management company · ${{company.count}} practices`,
        'is-selected'
      )
    );
  }});

  grid.innerHTML = cards.join('');
}}

function renderScatterplot() {{
  const metric = metricConfigs[activeMetric];
  updateCompletionScopeControl();
  document.getElementById('scatter-heading').textContent = `Completion Rate vs Score - Showing ${{metricDisplayLabel(activeMetric)}}`;
  const scatterAxis = (() => {{
    if (activeMetric !== 'gap') {{
      return {{ min: metric.axisMin, max: metric.axisMax, label: metric.axisLabel, ticks: null }};
    }}
    const gapAxis = gapAxisInfo();
    return {{
      min: 0,
      max: Math.max(0.5, gapAxis.max),
      label: gapAxis.magnitudeLabel,
      ticks: gapAxis.magnitudeTicks,
    }};
  }})();
  const completionNation = activeCompletionNation();
  const completionNationLabel = displayNationName(completionNation);
  const sourceRows = completionScatterScope === 'national'
    ? rows.concat(nationalSupplementals).filter((row) => String(row?.nation || '').trim().toLowerCase() === completionNation)
    : rows;
  const points = sourceRows
    .map((row) => {{
      const signed = activeMetric === 'gap'
        ? gapValue(row, {{ suppressSmall: false }})
        : metric.value(row);
      const x = signed === null ? null : (activeMetric === 'gap' ? Math.abs(signed) : signed);
      const y = numericOrNull(row.survey_completion_rate_percent);
      if (x === null || y === null) return null;
      return {{ row, x, y, signed }};
    }})
    .filter(Boolean);
  const svg = document.getElementById('scatterplot');
  const summary = document.getElementById('scatter-summary');
  const note = document.getElementById('scatter-note');
  const width = 920;
  const height = 320;
  const margin = {{ top: 34, right: 18, bottom: 42, left: 52 }};
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const completionMax = Math.max(10, ...points.map((point) => point.y), 50);
  const xScale = (value) => margin.left + ((value - scatterAxis.min) / (scatterAxis.max - scatterAxis.min)) * plotWidth;
  const yScale = (value) => margin.top + plotHeight - (value / completionMax) * plotHeight;
  const gridY = [];
  for (let tick = 0; tick <= completionMax; tick += 10) {{
    gridY.push(tick);
  }}
  const gridX = scatterAxis.ticks || (
    activeMetric === 'google'
      ? [0, 1, 2, 3, 4, 5]
      : activeMetric === 'survey'
      ? [0, 20, 40, 60, 80, 100]
      : [0, 0.5, 1.0, 1.5, 2.0, 2.5]
  );
  const renderTrendLine = (linePoints, color, titleLabel, dash = '8 6') => {{
    const trend = linearRegression(linePoints);
    if (!trend) return '';
    const candidates = [];
    const yAtMinX = (trend.slope * scatterAxis.min) + trend.intercept;
    const yAtMaxX = (trend.slope * scatterAxis.max) + trend.intercept;
    if (yAtMinX >= 0 && yAtMinX <= completionMax) candidates.push({{ x: scatterAxis.min, y: yAtMinX }});
    if (yAtMaxX >= 0 && yAtMaxX <= completionMax) candidates.push({{ x: scatterAxis.max, y: yAtMaxX }});
    if (Math.abs(trend.slope) > 1e-9) {{
      const xAtZero = (0 - trend.intercept) / trend.slope;
      const xAtMaxY = (completionMax - trend.intercept) / trend.slope;
      if (xAtZero >= scatterAxis.min && xAtZero <= scatterAxis.max) candidates.push({{ x: xAtZero, y: 0 }});
      if (xAtMaxY >= scatterAxis.min && xAtMaxY <= scatterAxis.max) candidates.push({{ x: xAtMaxY, y: completionMax }});
    }}
    const unique = [];
    candidates.forEach((candidate) => {{
      const alreadyPresent = unique.some((entry) => Math.abs(entry.x - candidate.x) < 0.0001 && Math.abs(entry.y - candidate.y) < 0.0001);
      if (!alreadyPresent) unique.push(candidate);
    }});
    if (unique.length < 2) return '';
    unique.sort((left, right) => (left.x === right.x ? left.y - right.y : left.x - right.x));
    const segment = [unique[0], unique[unique.length - 1]];
    return `
      <line x1="${{xScale(segment[0].x).toFixed(2)}}" y1="${{yScale(segment[0].y).toFixed(2)}}" x2="${{xScale(segment[1].x).toFixed(2)}}" y2="${{yScale(segment[1].y).toFixed(2)}}" stroke="${{color}}" stroke-width="2.4" stroke-linecap="round" stroke-dasharray="${{dash}}">
        <title>${{titleLabel}} fitted trend line. Slope ${{trend.slope.toFixed(2)}} completion points per ${{metric.title.toLowerCase()}} unit.</title>
      </line>
    `;
  }};
  const axisMarkup = `
    <rect x="0" y="0" width="${{width}}" height="${{height}}" fill="transparent"></rect>
    ${{gridY.map((tick) => `
      <line x1="${{margin.left}}" y1="${{yScale(tick)}}" x2="${{width - margin.right}}" y2="${{yScale(tick)}}" stroke="rgba(26,28,26,0.10)" />
      <text x="${{margin.left - 8}}" y="${{yScale(tick) + 4}}" text-anchor="end" font-size="11" fill="rgba(26,28,26,0.72)">${{tick}}%</text>
    `).join('')}}
    ${{gridX.map((tick) => `
      <line x1="${{xScale(tick)}}" y1="${{margin.top}}" x2="${{xScale(tick)}}" y2="${{height - margin.bottom}}" stroke="rgba(26,28,26,0.08)" />
      <text x="${{xScale(tick)}}" y="${{height - margin.bottom + 18}}" text-anchor="middle" font-size="11" fill="rgba(26,28,26,0.72)">${{activeMetric === 'google' ? tick.toFixed(1) : activeMetric === 'survey' ? `${{tick}}%` : tick.toFixed(1)}}</text>
    `).join('')}}
    <line x1="${{margin.left}}" y1="${{height - margin.bottom}}" x2="${{width - margin.right}}" y2="${{height - margin.bottom}}" stroke="rgba(26,28,26,0.35)" />
    <line x1="${{margin.left}}" y1="${{margin.top}}" x2="${{margin.left}}" y2="${{height - margin.bottom}}" stroke="rgba(26,28,26,0.35)" />
    <text x="${{width / 2}}" y="${{height - 8}}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)">${{scatterAxis.label}}</text>
    <text x="14" y="${{height / 2}}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)" transform="rotate(-90 14 ${{height / 2}})">${{completionScatterScope === 'regional' ? 'GP survey completion rate' : 'Survey participation rate'}}</text>
  `;
  if (completionScatterScope === 'regional') {{
    const assignments = shapeAssignment();
    const pointMarkup = points.map((point) => {{
      const companyShape = assignments.get(point.row.management_company);
      const radius = Math.max(4, Math.min(9, patientScaleForRow(point.row) * 6));
      const stroke = companyShape ? '#1a1c1a' : 'rgba(26,28,26,0.25)';
      const label = activeMetric === 'google'
        ? point.x.toFixed(1)
        : activeMetric === 'survey'
          ? `${{Math.round(point.x)}}%`
          : `${{point.signed >= 0 ? '+' : ''}}${{point.signed.toFixed(2)}} (|${{point.x.toFixed(2)}}|)`;
      return `
        <circle cx="${{xScale(point.x).toFixed(2)}}" cy="${{yScale(point.y).toFixed(2)}}" r="${{radius.toFixed(2)}}" fill="${{metric.markerColor(point.row)}}" stroke="${{stroke}}" stroke-width="${{companyShape ? 1.8 : 1}}">
          <title>${{point.row.name}} · ${{metric.title}}: ${{label}} · Completion: ${{Math.round(point.y)}}%</title>
        </circle>
      `;
    }}).join('');
    const gtdPoints = points.filter((point) => point.row.gtd || point.row.management_company === BASELINE_MANAGEMENT_COMPANY);
    const gtdMeanPoint = gtdPoints.length
      ? {{
          x: mean(gtdPoints.map((point) => point.x)),
          y: mean(gtdPoints.map((point) => point.y)),
        }}
      : null;
    const newBankPoint = points.find((point) => point.row.code === NEW_BANK_CODE) || null;
    const regionalTrendMarkup = renderTrendLine(points, 'rgba(26,28,26,0.88)', 'Manchester');
    const focusMarkup = [
      gtdMeanPoint
        ? `
          <g>
            <circle cx="${{xScale(gtdMeanPoint.x).toFixed(2)}}" cy="${{yScale(gtdMeanPoint.y).toFixed(2)}}" r="6.5" fill="${{GTD_MEAN_COLOR}}" stroke="#ffffff" stroke-width="2">
              <title>GTD · ${{metric.title}} mean: ${{activeMetric === 'google' ? gtdMeanPoint.x.toFixed(2) : activeMetric === 'survey' ? `${{Math.round(gtdMeanPoint.x)}}%` : gtdMeanPoint.x.toFixed(2)}} · Completion mean: ${{gtdMeanPoint.y.toFixed(1)}}%</title>
            </circle>
            <text x="${{(xScale(gtdMeanPoint.x) + 10).toFixed(2)}}" y="${{(yScale(gtdMeanPoint.y) - 2).toFixed(2)}}" font-size="11" font-weight="700" fill="${{GTD_MEAN_COLOR}}">GTD</text>
          </g>
        `
        : '',
      newBankPoint
        ? `
          <g>
            <circle cx="${{xScale(newBankPoint.x).toFixed(2)}}" cy="${{yScale(newBankPoint.y).toFixed(2)}}" r="6.5" fill="#7b3fb2" stroke="#ffffff" stroke-width="2">
              <title>New Bank · ${{metric.title}}: ${{activeMetric === 'google' ? newBankPoint.x.toFixed(2) : activeMetric === 'survey' ? `${{Math.round(newBankPoint.x)}}%` : newBankPoint.x.toFixed(2)}} · Completion: ${{newBankPoint.y.toFixed(1)}}%</title>
            </circle>
            <text x="${{(xScale(newBankPoint.x) + 10).toFixed(2)}}" y="${{(yScale(newBankPoint.y) - 18).toFixed(2)}}" font-size="11" font-weight="700" fill="#7b3fb2">New Bank</text>
          </g>
        `
        : '',
    ].join('');
    svg.innerHTML = `${{axisMarkup}}${{regionalTrendMarkup}}${{pointMarkup}}${{focusMarkup}}`;
  }} else {{
    const showNationalOverlaySeries = completionNation === 'england';
    const xBinCount = activeMetric === 'google' ? 20 : 20;
    const yBinSize = 5;
    const yBinCount = Math.max(1, Math.ceil(completionMax / yBinSize));
    const cells = new Map();
    points.forEach((point) => {{
      const xRatio = (point.x - scatterAxis.min) / (scatterAxis.max - scatterAxis.min || 1);
      const yRatio = point.y / completionMax;
      const xBin = Math.max(0, Math.min(xBinCount - 1, Math.floor(xRatio * xBinCount)));
      const yBin = Math.max(0, Math.min(yBinCount - 1, Math.floor(yRatio * yBinCount)));
      const key = `${{xBin}}-${{yBin}}`;
      cells.set(key, (cells.get(key) || 0) + 1);
    }});
    const maxCellCount = Math.max(0, ...Array.from(cells.values()));
    const cellMarkup = [];
    for (let xBin = 0; xBin < xBinCount; xBin += 1) {{
      const x0Value = scatterAxis.min + ((xBin / xBinCount) * (scatterAxis.max - scatterAxis.min));
      const x1Value = scatterAxis.min + (((xBin + 1) / xBinCount) * (scatterAxis.max - scatterAxis.min));
      const xMidValue = (x0Value + x1Value) / 2;
      for (let yBin = 0; yBin < yBinCount; yBin += 1) {{
        const count = cells.get(`${{xBin}}-${{yBin}}`) || 0;
        const y0Value = (yBin / yBinCount) * completionMax;
        const y1Value = ((yBin + 1) / yBinCount) * completionMax;
        const x = xScale(x0Value);
        const y = yScale(y1Value);
        const widthPx = Math.max(0, xScale(x1Value) - xScale(x0Value));
        const heightPx = Math.max(0, yScale(y0Value) - yScale(y1Value));
        const fill = metricColorForValue(activeMetric, xMidValue);
        const opacity = count <= 0 || maxCellCount <= 0 ? 0.04 : 0.12 + (count / maxCellCount) * 0.74;
        cellMarkup.push(`
          <rect x="${{x.toFixed(2)}}" y="${{y.toFixed(2)}}" width="${{widthPx.toFixed(2)}}" height="${{heightPx.toFixed(2)}}" fill="${{fill}}" opacity="${{opacity.toFixed(2)}}" stroke="rgba(255,255,255,0.38)" stroke-width="0.5">
            <title>${{count > 0 ? `${{count.toLocaleString('en-GB')}} practices` : 'No practices'}} · ${{metric.title}} ${{activeMetric === 'google' ? `${{x0Value.toFixed(1)}} to ${{x1Value.toFixed(1)}}` : activeMetric === 'survey' ? `${{Math.round(x0Value)}}% to ${{Math.round(x1Value)}}%` : `${{x0Value.toFixed(2)}} to ${{x1Value.toFixed(2)}}`}} · Completion ${{Math.round(y0Value)}}% to ${{Math.round(y1Value)}}%</title>
          </rect>
        `);
      }}
    }}
    const overlaySeries = showNationalOverlaySeries ? [
      {{
        label: 'Manchester',
        color: '#1f5f8b',
        rows: rows,
      }},
      {{
        label: 'GTD',
        color: GTD_MEAN_COLOR,
        rows: rows.filter((row) => row.gtd || row.management_company === BASELINE_MANAGEMENT_COMPANY),
      }},
      {{
        label: 'New Bank',
        color: '#7b3fb2',
        rows: rows.filter((row) => row.code === NEW_BANK_CODE),
      }},
    ].map((series) => {{
      const seriesPoints = series.rows
        .map((row) => {{
          const signed = activeMetric === 'gap'
            ? gapValue(row, {{ suppressSmall: false }})
            : metric.value(row);
          const x = signed === null ? null : (activeMetric === 'gap' ? Math.abs(signed) : signed);
          const y = numericOrNull(row.survey_completion_rate_percent);
          if (x === null || y === null) return null;
          return {{ x, y, signed }};
        }})
        .filter(Boolean);
      return {{
        ...series,
        x: seriesPoints.length ? mean(seriesPoints.map((point) => point.x)) : null,
        y: seriesPoints.length ? mean(seriesPoints.map((point) => point.y)) : null,
        count: seriesPoints.length,
      }};
    }}).filter((series) => series.x !== null && series.y !== null) : [];
    const overlayMarkup = overlaySeries.map((series, index) => `
      <g>
        <circle cx="${{xScale(series.x).toFixed(2)}}" cy="${{yScale(series.y).toFixed(2)}}" r="6.5" fill="${{series.color}}" stroke="#ffffff" stroke-width="2">
          <title>${{series.label}} · ${{series.count}} practices · ${{metric.title}} mean: ${{activeMetric === 'google' ? series.x.toFixed(2) : activeMetric === 'survey' ? `${{Math.round(series.x)}}%` : series.x.toFixed(2)}} · Completion mean: ${{series.y.toFixed(1)}}%</title>
        </circle>
        <text x="${{(xScale(series.x) + 10).toFixed(2)}}" y="${{(yScale(series.y) - (index * 16)).toFixed(2)}}" font-size="11" font-weight="700" fill="${{series.color}}">${{series.label}}</text>
      </g>
    `).join('');
    const nationalTrendMarkup = renderTrendLine(points, 'rgba(26,28,26,0.88)', completionNationLabel);
    svg.innerHTML = `${{axisMarkup}}${{cellMarkup.join('')}}${{nationalTrendMarkup}}${{overlayMarkup}}`;
  }}
  const completionValues = points.map((point) => point.y).sort((left, right) => left - right);
  const completionMedian = completionValues.length ? completionValues[Math.floor(completionValues.length / 2)] : null;
  const rValue = correlation(points);
  const newBank = points.find((point) => point.row.code === 'Y02960');
  const newBankSummary = completionScatterScope !== 'regional' || !newBank
    ? ''
    : ` New Bank Health is at ${{Math.round(newBank.y)}}% completion and sits around the ${{percentile(completionValues, newBank.y).toFixed(0)}}th percentile for completion in this set.`;
  if (completionScatterScope === 'regional') {{
    summary.textContent =
      `${{points.length}} practices have both GP survey completion data and a usable ${{metric.title.toLowerCase()}} value. Median completion is ${{completionMedian === null ? '?' : `${{Math.round(completionMedian)}}%`}}. Pearson r is ${{rValue === null ? '?' : rValue.toFixed(2)}}.${{newBankSummary}}`;
    if (note) note.textContent = 'Y-axis is GP Patient Survey completion rate. X-axis changes with the selected score source. The GP survey score itself is heavily bunched near the top end, mostly around or just below 80%, while Google reviews look much more organically spread. At these demarcations that suggests either practices dropping below roughly 70% overall-good are corrected fairly quickly before they persist in the survey, or the patient survey is not really capturing the lower half of possible experience that clearly exists in review text.';
  }} else {{
    const regionalPoints = rows
      .map((row) => {{
        const signed = activeMetric === 'gap'
          ? gapValue(row, {{ suppressSmall: false }})
          : metric.value(row);
        const x = signed === null ? null : (activeMetric === 'gap' ? Math.abs(signed) : signed);
        const y = numericOrNull(row.survey_completion_rate_percent);
        if (x === null || y === null) return null;
        return {{ x, y, row }};
      }})
      .filter(Boolean);
    const gtdRegionalPoints = regionalPoints.filter((point) => point.row.gtd || point.row.management_company === BASELINE_MANAGEMENT_COMPANY);
    const newBankRegionalPoint = regionalPoints.find((point) => point.row.code === NEW_BANK_CODE) || null;
    const gmMeanX = regionalPoints.length ? mean(regionalPoints.map((point) => point.x)) : null;
    const gmMeanY = regionalPoints.length ? mean(regionalPoints.map((point) => point.y)) : null;
    const gtdMeanX = gtdRegionalPoints.length ? mean(gtdRegionalPoints.map((point) => point.x)) : null;
    const gtdMeanY = gtdRegionalPoints.length ? mean(gtdRegionalPoints.map((point) => point.y)) : null;
    summary.textContent = showNationalOverlaySeries
      ? `${{points.length.toLocaleString('en-GB')}} practices currently have both survey participation data and a usable ${{metric.title.toLowerCase()}} value in ${{completionNationLabel}}. Median participation is ${{completionMedian === null ? '?' : `${{Math.round(completionMedian)}}%`}}. Pearson r is ${{rValue === null ? '?' : rValue.toFixed(2)}}. Manchester is ${{gmMeanY === null ? '?' : `${{gmMeanY.toFixed(1)}}% participation`}} at ${{gmMeanX === null ? '?' : activeMetric === 'google' ? gmMeanX.toFixed(2) : activeMetric === 'survey' ? `${{Math.round(gmMeanX)}}%` : gmMeanX.toFixed(2)}}; GTD is ${{gtdMeanY === null ? '?' : `${{gtdMeanY.toFixed(1)}}% participation`}} at ${{gtdMeanX === null ? '?' : activeMetric === 'google' ? gtdMeanX.toFixed(2) : activeMetric === 'survey' ? `${{Math.round(gtdMeanX)}}%` : gtdMeanX.toFixed(2)}}; New Bank is ${{newBankRegionalPoint === null ? '?' : `${{newBankRegionalPoint.y.toFixed(1)}}% participation`}} at ${{newBankRegionalPoint === null ? '?' : activeMetric === 'google' ? newBankRegionalPoint.x.toFixed(2) : activeMetric === 'survey' ? `${{Math.round(newBankRegionalPoint.x)}}%` : newBankRegionalPoint.x.toFixed(2)}}.`
      : `${{points.length.toLocaleString('en-GB')}} practices currently have both survey participation data and a usable ${{metric.title.toLowerCase()}} value in ${{completionNationLabel}}. Median participation is ${{completionMedian === null ? '?' : `${{Math.round(completionMedian)}}%`}}. Pearson r is ${{rValue === null ? '?' : rValue.toFixed(2)}}.`;
    if (note) note.textContent = showNationalOverlaySeries
      ? 'Nation mode bins practices into density cells for speed and cycles England, Scotland, Wales, then Northern Ireland. Overlay dots keep Manchester, GTD, and New Bank visible as the local reference set. England currently uses GP Patient Survey completion rate; Scotland uses HACE response rate; Wales and Northern Ireland will show once equivalent practice-level rates are wired.'
      : 'Nation mode bins practices into density cells for speed and cycles England, Scotland, Wales, then Northern Ireland. For Scotland and other non-England nations, the local Manchester/GTD/New Bank overlays are hidden because the participation metric is not directly comparable enough. England currently uses GP Patient Survey completion rate; Scotland uses HACE response rate; Wales and Northern Ireland will show once equivalent practice-level rates are wired.';
  }}
}}

function renderDeprivationChart() {{
  const metric = metricConfigs[activeMetric];
  document.getElementById('deprivation-heading').textContent = `Manchester Score vs Deprivation - Showing ${{metricDisplayLabel(activeMetric)}}`;
  const svg = document.getElementById('deprivation-chart');
  if (!svg) return;
  const gapAxis = gapAxisInfo();

  const points = rows
    .map((row) => {{
      const dep = practiceDeprivationLookup[row.code];
      if (!dep) return null;
      const x = dep.imd_decile;
      const y = activeMetric === 'gap'
        ? gapValue(row, {{ suppressSmall: false }})
        : metric.value(row);
      if (x === null || x === undefined || y === null) return null;
      return {{ row, x, y }};
    }})
    .filter(Boolean);

  const width = 920;
  const height = 320;
  const margin = {{ top: 34, right: 18, bottom: 42, left: 52 }};
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const headerBandY = 4;
  const headerBandHeight = 17;
  const headerTextY = 16;

  const xMin = 1;
  const xMax = 10;
  const yMin = activeMetric === 'gap' ? gapAxis.min : metric.axisMin;
  const yMax = activeMetric === 'gap' ? gapAxis.max : metric.axisMax;

  const xBins = xMax - xMin + 1;
  const xCenter = (decile) => margin.left + ((decile - xMin + 0.5) / xBins) * plotWidth;
  const xBoundary = (boundaryIndex) => margin.left + (boundaryIndex / xBins) * plotWidth;
  const yScale = (value) => margin.top + plotHeight - ((value - yMin) / (yMax - yMin)) * plotHeight;

  const gridX = [];
  for (let tick = xMin; tick <= xMax; tick += 1) {{
    gridX.push(tick);
  }}

  const bucketCount = activeMetric === 'survey' ? 10 : 8;
  const gridY = [];
  const bucketHeight = (yMax - yMin) / bucketCount;
  for (let index = 0; index <= bucketCount; index += 1) {{
    gridY.push(yMin + bucketHeight * index);
  }}

  // Group points into (decile, value bucket) cells
  const cells = new Map();
  const overallBucketCounts = Array.from({{ length: bucketCount }}, () => 0);
  const columnBucketCounts = new Map(gridX.map((decile) => [decile, Array.from({{ length: bucketCount }}, () => 0)]));
  const columnPointMap = new Map(gridX.map((decile) => [decile, []]));
  points.forEach((point) => {{
    const decile = Math.max(xMin, Math.min(xMax, Math.round(point.x)));
    const clampedY = Math.max(yMin, Math.min(yMax, point.y));
    const bucketIndex = Math.min(
      bucketCount - 1,
      Math.max(0, Math.floor(((clampedY - yMin) / (yMax - yMin)) * bucketCount))
    );
    const key = `${{decile}}-${{bucketIndex}}`;
    if (!cells.has(key)) cells.set(key, []);
    cells.get(key).push(point);
    overallBucketCounts[bucketIndex] += 1;
    columnBucketCounts.get(decile)[bucketIndex] += 1;
    columnPointMap.get(decile).push(point);
  }});

  const assignments = shapeAssignment();
  const cellMarkup = [];
  const cellWidth = plotWidth / (xMax - xMin + 1);
  const cellInnerWidth = cellWidth * 0.92;
  const yPixelBucketHeight = plotHeight / bucketCount;
  const cellInnerHeight = yPixelBucketHeight * 0.92;

  // Fixed square size across the chart: pick the largest size that still fits the densest cell.
  const maxCellCount = Math.max(0, ...Array.from(cells.values(), (cellPoints) => cellPoints.length));
  function bestSquareSizeForCount(count) {{
    if (!count) return 0;
    let best = 0;
    for (let cols = 1; cols <= count; cols += 1) {{
      const rows = Math.ceil(count / cols);
      const size = Math.min(cellInnerWidth / cols, cellInnerHeight / rows);
      if (size > best) best = size;
    }}
    return best;
  }}
  const minSquareSize = 2.8;
  const maxSquareSize = 14;
  const fixedSquareSize = Math.max(minSquareSize, Math.min(maxSquareSize, bestSquareSizeForCount(maxCellCount)));
  const overallMeanValue = mean(points.map((point) => point.y));

  function bestCellLayout(count) {{
    if (!count) return {{ cols: 1, rows: 1 }};
    const targetAspect = cellInnerWidth / cellInnerHeight;
    let bestLayout = null;
    let bestScore = Infinity;
    for (let cols = 1; cols <= count; cols += 1) {{
      const rows = Math.ceil(count / cols);
      const totalWidth = cols * fixedSquareSize;
      const totalHeight = rows * fixedSquareSize;
      if (totalWidth > cellInnerWidth + 0.001 || totalHeight > cellInnerHeight + 0.001) continue;
      const aspect = cols / rows;
      const aspectPenalty = Math.abs(aspect - targetAspect);
      const widthSlack = (cellInnerWidth - totalWidth) / cellInnerWidth;
      const heightSlack = (cellInnerHeight - totalHeight) / cellInnerHeight;
      const score = aspectPenalty + (widthSlack * 0.08) + (heightSlack * 0.03);
      if (score < bestScore || (Math.abs(score - bestScore) < 0.0001 && bestLayout && cols > bestLayout.cols)) {{
        bestScore = score;
        bestLayout = {{ cols, rows }};
      }}
    }}
    if (bestLayout) return bestLayout;
    const cols = Math.ceil(Math.sqrt(count));
    return {{ cols, rows: Math.ceil(count / cols) }};
  }}

  const distributionMarkup = gridX.map((decile) => {{
    const columnPoints = columnPointMap.get(decile) || [];
    const counts = columnBucketCounts.get(decile) || Array.from({{ length: bucketCount }}, () => 0);
    const columnMean = columnPoints.length ? mean(columnPoints.map((point) => point.y)) : null;
    const shift = columnMean === null || overallMeanValue === null ? 0 : columnMean - overallMeanValue;
    const jsd = columnPoints.length ? jensenShannonDivergence(counts, overallBucketCounts) : 0;
    const shiftScale = Math.max(0.0001, (yMax - yMin) / 4);
    const shiftStrength = clamp01(Math.abs(shift) / shiftScale);
    const diffStrength = clamp01(jsd / 0.35);
    const isNeutral = shiftStrength < 0.12;
    const fill = isNeutral
      ? `hsl(215 12% ${{(95 - diffStrength * 10).toFixed(1)}}%)`
      : shift >= 0
        ? `hsl(151 40% ${{(92 - ((diffStrength * 14) + (shiftStrength * 8))).toFixed(1)}}%)`
        : `hsl(12 62% ${{(92 - ((diffStrength * 14) + (shiftStrength * 8))).toFixed(1)}}%)`;
    const bandFill = isNeutral
      ? `hsl(215 12% ${{(82 - diffStrength * 14).toFixed(1)}}%)`
      : shift >= 0
        ? `hsl(151 58% ${{(58 - ((diffStrength * 10) + (shiftStrength * 6))).toFixed(1)}}%)`
        : `hsl(12 64% ${{(58 - ((diffStrength * 10) + (shiftStrength * 6))).toFixed(1)}}%)`;
    const bandText = isNeutral ? 'rgba(26,28,26,0.82)' : '#ffffff';
    const x0 = xBoundary(decile - xMin);
    const x1 = xBoundary(decile - xMin + 1);
    const meanLabel = columnMean === null
      ? 'n/a'
      : activeMetric === 'survey'
        ? `${{Math.round(columnMean)}}%`
        : columnMean.toFixed(activeMetric === 'gap' ? 2 : 1);
    const title = !columnPoints.length
      ? `IMD decile ${{decile}}: no practices with usable data`
      : `IMD decile ${{decile}}: mean ${{meanLabel}}. Distribution is ${{isNeutral ? 'similar to' : shift >= 0 ? 'better than' : 'worse than'}} the overall pattern. Jensen-Shannon divergence ${{jsd.toFixed(2)}}.`;
    return `
      <g>
        <rect x="${{x0.toFixed(2)}}" y="${{margin.top.toFixed(2)}}" width="${{(x1 - x0).toFixed(2)}}" height="${{plotHeight.toFixed(2)}}" fill="${{fill}}">
          <title>${{title}}</title>
        </rect>
        <rect x="${{(x0 + 2).toFixed(2)}}" y="${{headerBandY.toFixed(2)}}" width="${{Math.max(0, x1 - x0 - 4).toFixed(2)}}" height="${{headerBandHeight}}" rx="6" fill="${{bandFill}}">
          <title>${{title}}</title>
        </rect>
        <text x="${{((x0 + x1) / 2).toFixed(2)}}" y="${{headerTextY.toFixed(2)}}" text-anchor="middle" font-size="10.5" font-weight="700" fill="${{bandText}}">${{meanLabel}}</text>
      </g>
    `;
  }}).join('');

  cells.forEach((cellPoints, key) => {{
    const [decileStr, bucketStr] = key.split('-');
    const decile = Number(decileStr);
    const bucketIndex = Number(bucketStr);
    const centerX = xCenter(decile);
    const bucketYMin = yMin + bucketHeight * bucketIndex;
    const bucketYMax = bucketYMin + bucketHeight;
    const centerYValue = (bucketYMin + bucketYMax) / 2;
    const centerY = yScale(centerYValue);

    const count = cellPoints.length;
    const {{ cols, rows }} = bestCellLayout(count);
    const totalWidth = cols * fixedSquareSize;
    const totalHeight = rows * fixedSquareSize;
    const startX = centerX - totalWidth / 2 + fixedSquareSize / 2;
    const startY = centerY - totalHeight / 2 + fixedSquareSize / 2;

    cellPoints.forEach((point, index) => {{
      const col = index % cols;
      const row = Math.floor(index / cols);
      const cx = startX + col * fixedSquareSize;
      const cy = startY + row * fixedSquareSize;
      const companyShape = assignments.get(point.row.management_company);
      const stroke = companyShape ? '#1a1c1a' : 'rgba(26,28,26,0.25)';
      const label = activeMetric === 'google'
        ? point.y.toFixed(1)
        : activeMetric === 'survey'
          ? `${{Math.round(point.y)}}%`
          : point.y.toFixed(2);
      cellMarkup.push(`
        <rect x="${{(cx - fixedSquareSize / 2).toFixed(2)}}" y="${{(cy - fixedSquareSize / 2).toFixed(2)}}" width="${{fixedSquareSize.toFixed(2)}}" height="${{fixedSquareSize.toFixed(2)}}" rx="1.2" fill="${{metric.markerColor(point.row)}}" stroke="${{stroke}}" stroke-width="${{companyShape ? 1 : 0.5}}">
          <title>${{point.row.name}} · ${{metric.title}}: ${{label}} · IMD decile: ${{decile}}</title>
        </rect>
      `);
    }});
  }});

  svg.innerHTML = `
    <rect x="0" y="0" width="${{width}}" height="${{height}}" fill="transparent"></rect>
    ${{distributionMarkup}}
    ${{gridY.map((tick) => `
      <line x1="${{margin.left}}" y1="${{yScale(tick)}}" x2="${{width - margin.right}}" y2="${{yScale(tick)}}" stroke="rgba(26,28,26,0.10)" />
    `).join('')}}
    ${{Array.from({{ length: xBins + 1 }}, (_, idx) => idx).map((boundaryIndex) => `
      <line x1="${{xBoundary(boundaryIndex)}}" y1="${{margin.top}}" x2="${{xBoundary(boundaryIndex)}}" y2="${{height - margin.bottom}}" stroke="rgba(26,28,26,0.08)" />
    `).join('')}}
    ${{Array.from({{ length: bucketCount }}, (_, idx) => idx).map((bucketIndex) => {{
      const bucketMid = yMin + bucketHeight * (bucketIndex + 0.5);
      const label = activeMetric === 'survey'
        ? `${{Math.round(bucketMid)}}%`
        : bucketMid.toFixed(activeMetric === 'gap' ? 2 : 1);
      return `
        <text x="${{margin.left - 8}}" y="${{(yScale(bucketMid) + 4).toFixed(2)}}" text-anchor="end" font-size="11" fill="rgba(26,28,26,0.72)">${{label}}</text>
      `;
    }}).join('')}}
    ${{gridX.map((tick) => `
      <text x="${{xCenter(tick)}}" y="${{height - margin.bottom + 18}}" text-anchor="middle" font-size="11" fill="rgba(26,28,26,0.72)">${{tick}}</text>
    `).join('')}}
    <line x1="${{margin.left}}" y1="${{height - margin.bottom}}" x2="${{width - margin.right}}" y2="${{height - margin.bottom}}" stroke="rgba(26,28,26,0.35)" />
    <line x1="${{margin.left}}" y1="${{margin.top}}" x2="${{margin.left}}" y2="${{height - margin.bottom}}" stroke="rgba(26,28,26,0.35)" />
    ${{cellMarkup.join('')}}
    <text x="${{width / 2}}" y="${{height - 8}}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)">IMD 2025 decile (1 = most deprived)</text>
    <text x="14" y="${{height / 2}}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)" transform="rotate(-90 14 ${{height / 2}})">${{activeMetric === 'gap' ? gapAxis.label : metric.axisLabel}}</text>
  `;

  const depValues = points.map((point) => point.x).sort((l, r) => l - r);
  const yValues = points.map((point) => point.y).sort((l, r) => l - r);
  const depMedian = depValues.length ? depValues[Math.floor(depValues.length / 2)] : null;
  const yMedian = yValues.length ? yValues[Math.floor(yValues.length / 2)] : null;
  const rValue = correlation(points.map((p) => ({{ x: p.x, y: p.y }})));
  const strongestDecile = gridX
    .map((decile) => {{
      const counts = columnBucketCounts.get(decile) || [];
      const pointCount = (columnPointMap.get(decile) || []).length;
      return {{
        decile,
        pointCount,
        jsd: pointCount ? jensenShannonDivergence(counts, overallBucketCounts) : 0,
      }};
    }})
    .sort((left, right) => right.jsd - left.jsd)[0];

  document.getElementById('deprivation-summary').textContent =
    `${{points.length}} practices have both a usable ${{metric.title.toLowerCase()}} value and mapped IMD 2025 decile. Median decile is ${{depMedian === null ? '?' : depMedian}} and median ${{metric.title.toLowerCase()}} is ${{yMedian === null ? '?' : (activeMetric === 'survey' ? `${{Math.round(yMedian)}}%` : yMedian.toFixed(activeMetric === 'gap' ? 2 : 1))}}. Pearson r for score vs decile is ${{rValue === null ? '?' : rValue.toFixed(2)}}. Column tint shows whether each decile skews better (green), worse (red), or similar (grey) versus the overall distribution, with stronger colour meaning a more different distribution. Strongest departure is decile ${{strongestDecile && strongestDecile.pointCount ? strongestDecile.decile : '?'}}.`;
}}

function renderNationalDeprivationChart() {{
  const metric = metricConfigs[activeMetric];
  const heading = document.getElementById('national-deprivation-heading');
  const summary = document.getElementById('national-deprivation-summary');
  const svg = document.getElementById('national-deprivation-chart');
  const populationToggle = document.getElementById('national-deprivation-population-toggle');
  if (!heading || !summary || !svg) return;
  if (populationToggle) {{
    populationToggle.checked = nationalDeprivationUsePopulation;
  }}
  heading.textContent = `National Score vs Deprivation - Showing ${{metricDisplayLabel(activeMetric)}}`;

  const combinedRows = rows.concat(nationalSupplementals);
  const gapAxis = gapAxisInfo();
  const points = combinedRows
    .map((row) => {{
      const dep = allPracticeDeprivationLookup[row.code];
      if (!dep) return null;
      const decile = numericOrNull(dep.imd_decile);
      if (decile === null) return null;
      const y = activeMetric === 'gap'
        ? gapValue(row, {{ suppressSmall: false }})
        : metric.value(row);
      if (y === null) return null;
      return {{ row, decile, y }};
    }})
    .filter(Boolean);

  const width = 920;
  const height = 320;
  const margin = {{ top: 28, right: 18, bottom: 42, left: 52 }};
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const headerBandY = 4;
  const headerBandHeight = 17;
  const headerTextY = 16;
  const xMin = 1;
  const xMax = 10;
  const yMin = activeMetric === 'gap' ? gapAxis.min : metric.axisMin;
  const yMax = activeMetric === 'gap' ? gapAxis.max : metric.axisMax;
  const bucketCount = activeMetric === 'survey' ? 10 : activeMetric === 'gap' ? 10 : 10;
  const bucketHeight = (yMax - yMin) / bucketCount;
  const xBins = xMax - xMin + 1;
  const cellWidth = plotWidth / xBins;
  const cellHeight = plotHeight / bucketCount;

  const xCenter = (decile) => margin.left + ((decile - xMin + 0.5) / xBins) * plotWidth;
  const xBoundary = (boundaryIndex) => margin.left + (boundaryIndex / xBins) * plotWidth;
  const yBoundary = (boundaryIndex) => margin.top + plotHeight - (boundaryIndex / bucketCount) * plotHeight;
  const bucketMidValue = (bucketIndex) => yMin + bucketHeight * (bucketIndex + 0.5);
  const aggregateValueForRow = (row) => {{
    if (!nationalDeprivationUsePopulation) return 1;
    const patients = numericOrNull(row.registered_patient_count);
    return patients !== null && patients > 0 ? patients : 0;
  }};
  const formatCellValue = (value) => {{
    if (value <= 0) return '';
    if (!nationalDeprivationUsePopulation) return String(Math.round(value));
    if (value >= 1000000) return `${{(value / 1000000).toFixed(value >= 10000000 ? 0 : 1)}}m`;
    if (value >= 1000) return `${{(value / 1000).toFixed(value >= 100000 ? 0 : 1)}}k`;
    return String(Math.round(value));
  }};
  const formatAggregateLong = (value) => {{
    if (!nationalDeprivationUsePopulation) {{
      const rounded = Math.round(value);
      return `${{rounded.toLocaleString('en-GB')}} practice${{rounded === 1 ? '' : 's'}}`;
    }}
    return `${{Math.round(value).toLocaleString('en-GB')}} registered patients`;
  }};

  const cells = new Map();
  const columnCounts = new Map(Array.from({{ length: xBins }}, (_, index) => [index + 1, 0]));
  const columnPoints = new Map(Array.from({{ length: xBins }}, (_, index) => [index + 1, []]));
  const columnBucketCounts = new Map(Array.from({{ length: xBins }}, (_, index) => [index + 1, Array.from({{ length: bucketCount }}, () => 0)]));
  const overallBucketCounts = Array.from({{ length: bucketCount }}, () => 0);
  points.forEach((point) => {{
    const decile = Math.max(xMin, Math.min(xMax, Math.round(point.decile)));
    const bucketIndex = Math.min(
      bucketCount - 1,
      Math.max(0, Math.floor(((Math.max(yMin, Math.min(yMax, point.y)) - yMin) / (yMax - yMin)) * bucketCount))
    );
    const key = `${{decile}}-${{bucketIndex}}`;
    const aggregate = aggregateValueForRow(point.row);
    cells.set(key, (cells.get(key) || 0) + aggregate);
    columnCounts.set(decile, (columnCounts.get(decile) || 0) + aggregate);
    columnPoints.get(decile).push(point);
    columnBucketCounts.get(decile)[bucketIndex] += 1;
    overallBucketCounts[bucketIndex] += 1;
  }});

  const maxCellCount = Math.max(0, ...Array.from(cells.values()));
  const allLookupRows = combinedRows.filter((row) => allPracticeDeprivationLookup[row.code]);
  const matchedRows = combinedRows.filter((row) => numericOrNull(allPracticeDeprivationLookup[row.code]?.imd_decile) !== null);
  const overallMeanValue = mean(points.map((point) => point.y));
  const cellMarkup = [];
  const headerMarkup = [];
  for (let decile = xMin; decile <= xMax; decile += 1) {{
    const columnTotal = columnCounts.get(decile) || 0;
    const decilePoints = columnPoints.get(decile) || [];
    const columnMean = decilePoints.length ? mean(decilePoints.map((point) => point.y)) : null;
    const counts = columnBucketCounts.get(decile) || Array.from({{ length: bucketCount }}, () => 0);
    const shift = columnMean === null || overallMeanValue === null ? 0 : columnMean - overallMeanValue;
    const jsd = decilePoints.length ? jensenShannonDivergence(counts, overallBucketCounts) : 0;
    const shiftScale = Math.max(0.0001, (yMax - yMin) / 4);
    const shiftStrength = clamp01(Math.abs(shift) / shiftScale);
    const diffStrength = clamp01(jsd / 0.35);
    const isNeutral = shiftStrength < 0.12;
    const x0 = xBoundary(decile - xMin);
    const x1 = xBoundary(decile - xMin + 1);
    const headerLabel = columnMean === null
      ? ''
      : activeMetric === 'survey'
        ? `${{Math.round(columnMean)}}%`
        : columnMean.toFixed(activeMetric === 'gap' ? 2 : 1);
    const headerFill = columnMean === null
      ? 'rgba(26,28,26,0.14)'
      : isNeutral
        ? `hsl(215 12% ${{(82 - diffStrength * 14).toFixed(1)}}%)`
        : shift >= 0
          ? `hsl(151 58% ${{(58 - ((diffStrength * 10) + (shiftStrength * 6))).toFixed(1)}}%)`
          : `hsl(12 64% ${{(58 - ((diffStrength * 10) + (shiftStrength * 6))).toFixed(1)}}%)`;
    headerMarkup.push(`
      <g>
        <rect x="${{(x0 + 2).toFixed(2)}}" y="${{headerBandY.toFixed(2)}}" width="${{Math.max(0, x1 - x0 - 4).toFixed(2)}}" height="${{headerBandHeight}}" rx="6" fill="${{headerFill}}">
          <title>IMD decile ${{decile}} average ${{metric.title.toLowerCase()}}: ${{headerLabel || 'n/a'}}. Column body is showing ${{formatAggregateLong(columnTotal)}}.</title>
        </rect>
        ${{headerLabel ? `<text x="${{((x0 + x1) / 2).toFixed(2)}}" y="${{headerTextY.toFixed(2)}}" text-anchor="middle" font-size="10.5" font-weight="700" fill="rgba(26,28,26,0.88)">${{headerLabel}}</text>` : ''}}
      </g>
    `);
    for (let bucketIndex = 0; bucketIndex < bucketCount; bucketIndex += 1) {{
      const key = `${{decile}}-${{bucketIndex}}`;
      const count = cells.get(key) || 0;
      const x = xBoundary(decile - xMin);
      const y = yBoundary(bucketIndex + 1);
      const bucketMid = bucketMidValue(bucketIndex);
      const fill = metricColorForValue(activeMetric, bucketMid);
      const opacity = count <= 0 || maxCellCount <= 0 ? 0.08 : 0.16 + (count / maxCellCount) * 0.72;
      const label = formatCellValue(count);
      const tooltipValue = activeMetric === 'survey'
        ? `${{Math.round(bucketMid)}}%`
        : bucketMid.toFixed(activeMetric === 'gap' ? 2 : 1);
      cellMarkup.push(`
        <g>
          <rect x="${{x.toFixed(2)}}" y="${{y.toFixed(2)}}" width="${{cellWidth.toFixed(2)}}" height="${{cellHeight.toFixed(2)}}" fill="${{fill}}" fill-opacity="${{opacity.toFixed(3)}}" stroke="rgba(26,28,26,0.14)" stroke-width="1">
            <title>IMD decile ${{decile}}, score bucket around ${{tooltipValue}}: ${{formatAggregateLong(count)}}</title>
          </rect>
          ${{label ? `<text x="${{(x + cellWidth / 2).toFixed(2)}}" y="${{(y + cellHeight / 2 + 4).toFixed(2)}}" text-anchor="middle" font-size="11" font-weight="700" fill="rgba(26,28,26,0.84)">${{label}}</text>` : ''}}
        </g>
      `);
    }}
  }}

  const yTicks = Array.from({{ length: bucketCount + 1 }}, (_, index) => yMin + bucketHeight * index);
  svg.innerHTML = `
    <rect x="0" y="0" width="${{width}}" height="${{height}}" fill="transparent"></rect>
    ${{headerMarkup.join('')}}
    ${{Array.from({{ length: xBins + 1 }}, (_, idx) => idx).map((boundaryIndex) => `
      <line x1="${{xBoundary(boundaryIndex)}}" y1="${{margin.top}}" x2="${{xBoundary(boundaryIndex)}}" y2="${{height - margin.bottom}}" stroke="rgba(26,28,26,0.10)" />
    `).join('')}}
    ${{Array.from({{ length: bucketCount + 1 }}, (_, idx) => idx).map((boundaryIndex) => `
      <line x1="${{margin.left}}" y1="${{yBoundary(boundaryIndex)}}" x2="${{width - margin.right}}" y2="${{yBoundary(boundaryIndex)}}" stroke="rgba(26,28,26,0.10)" />
    `).join('')}}
    ${{cellMarkup.join('')}}
    ${{yTicks.slice(0, -1).map((tick, index) => {{
      const bucketMid = tick + bucketHeight / 2;
      const label = activeMetric === 'survey'
        ? `${{Math.round(bucketMid)}}%`
        : bucketMid.toFixed(activeMetric === 'gap' ? 2 : 1);
      return `<text x="${{margin.left - 8}}" y="${{(yBoundary(index + 1) + cellHeight / 2 + 4).toFixed(2)}}" text-anchor="end" font-size="11" fill="rgba(26,28,26,0.72)">${{label}}</text>`;
    }}).join('')}}
    ${{Array.from({{ length: xBins }}, (_, idx) => idx + 1).map((tick) => `
      <text x="${{xCenter(tick)}}" y="${{height - margin.bottom + 18}}" text-anchor="middle" font-size="11" fill="rgba(26,28,26,0.72)">${{tick}}</text>
    `).join('')}}
    <line x1="${{margin.left}}" y1="${{height - margin.bottom}}" x2="${{width - margin.right}}" y2="${{height - margin.bottom}}" stroke="rgba(26,28,26,0.35)" />
    <line x1="${{margin.left}}" y1="${{margin.top}}" x2="${{margin.left}}" y2="${{height - margin.bottom}}" stroke="rgba(26,28,26,0.35)" />
    <text x="${{width / 2}}" y="${{height - 8}}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)">IMD 2025 decile (1 = most deprived)</text>
    <text x="14" y="${{height / 2}}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)" transform="rotate(-90 14 ${{height / 2}})">${{activeMetric === 'gap' ? gapAxis.label : metric.axisLabel}}</text>
  `;

  const unsupportedCount = combinedRows.filter((row) => {{
    const dep = allPracticeDeprivationLookup[row.code];
    return dep && dep.lookup_status === 'unsupported_nation';
  }}).length;
  const polygonOnlyCount = combinedRows.filter((row) => {{
    const dep = allPracticeDeprivationLookup[row.code];
    return dep && dep.lookup_status === 'matched_polygon_no_deprivation_index';
  }}).length;
  const topColumn = Array.from(columnCounts.entries()).sort((left, right) => right[1] - left[1])[0];
  const totalAggregate = Array.from(cells.values()).reduce((sum, value) => sum + value, 0);
  summary.textContent =
    `${{points.length}} practices currently contribute to this national contrast panel. Cells are showing ${{nationalDeprivationUsePopulation ? 'summed registered patients' : 'practice counts'}} across a total of ${{formatAggregateLong(totalAggregate)}}. ${{allLookupRows.length}} loaded rows have some cached deprivation lookup state, and ${{matchedRows.length}} have numeric IMD deciles. The densest deprivation column is decile ${{topColumn ? topColumn[0] : '?'}} with ${{topColumn ? formatAggregateLong(topColumn[1]) : '0 practices'}}. ${{polygonOnlyCount}} rows currently only have polygon identity without a joined deprivation index, and ${{unsupportedCount}} are in nations not yet wired into this lookup.`;
}}

function nationScatterColor(nation) {{
  const normalized = String(nation || '').trim().toLowerCase();
  if (normalized === 'england') return '#1f5f8b';
  if (normalized === 'scotland') return '#0c8b68';
  if (normalized === 'wales') return '#b14d5c';
  if (normalized === 'northern_ireland') return '#7b5ea7';
  return '#6b7280';
}}

function nationBenchmarkAccent(nation) {{
  const normalized = String(nation || '').trim().toLowerCase();
  if (normalized === 'england') return '#8d3c17';
  if (normalized === 'scotland') return '#2f6fa5';
  if (normalized === 'wales') return '#3f7d4c';
  if (normalized === 'northern_ireland') return '#6b4f9d';
  return '#4b5563';
}}

function renderRatingVsSurveyChart() {{
  const heading = document.getElementById('rating-survey-heading');
  const summary = document.getElementById('rating-survey-summary');
  const note = document.getElementById('rating-survey-note');
  const svg = document.getElementById('rating-survey-chart');
  if (!heading || !summary || !note || !svg) return;

  heading.textContent = 'Google Rating vs Patient Survey';
  const combinedRows = rows.concat(nationalSupplementals);
  const practicePoints = combinedRows
    .map((row) => {{
      const google = numericOrNull(row.google_score);
      const survey = numericOrNull(row.survey_overall_good_percent);
      if (google === null || survey === null) return null;
      return {{ row, x: google, y: survey }};
    }})
    .filter(Boolean);

  const allBenchmarkEntries = [
    ...nationOrder
      .map((nation) => {{
        const subset = allKnownRows.filter((row) => String(row?.nation || '').trim().toLowerCase() === nation);
        if (!subset.length) return null;
        const stats = regionCardStats(subset);
        return {{
          label: displayNationName(nation),
          kind: 'nation',
          x: stats.google.value,
          y: stats.survey.value,
          color: nationBenchmarkAccent(nation),
          practiceCount: stats.practiceCount,
        }};
      }})
      .filter(Boolean),
    ...cityCatchments
      .map((city) => {{
        const subset = cityRowsByCatchment.get(city.name) || [];
        if (!subset.length) return null;
        const stats = regionCardStats(subset);
        return {{
          label: city.name,
          kind: 'city',
          x: stats.google.value,
          y: stats.survey.value,
          color: city.accent,
          practiceCount: stats.practiceCount,
        }};
      }})
      .filter(Boolean),
    ...['North', 'South']
      .map((label) => {{
        const subset = northSouthRows.get(label) || [];
        if (!subset.length) return null;
        const stats = regionCardStats(subset);
        return {{
          label,
          kind: 'region',
          x: stats.google.value,
          y: stats.survey.value,
          color: label === 'North' ? '#315f8f' : '#8c5a2a',
          practiceCount: stats.practiceCount,
        }};
      }})
      .filter(Boolean),
    ...compositeRegionDefinitions
      .map((definition) => {{
        const subset = compositeRegionRowsByLabel.get(definition.label) || [];
        if (!subset.length) return null;
        const stats = regionCardStats(subset);
        return {{
          label: definition.label,
          kind: definition.kind || 'region',
          x: stats.google.value,
          y: stats.survey.value,
          color: definition.accent || '#4b5563',
          practiceCount: stats.practiceCount,
        }};
      }})
      .filter(Boolean),
    ...(sampleCircleCenter
      ? (() => {{
          const subset = rowsWithinCircle(allKnownRows, sampleCircleCenter.lat, sampleCircleCenter.lon, sampleCircleRadiusMiles);
          if (!subset.length) return [];
          const stats = regionCardStats(subset);
          return [{{
            label: `Custom sample (${{sampleCircleRadiusMiles.toFixed(sampleCircleRadiusMiles % 1 === 0 ? 0 : 1)}}mi)`,
            kind: 'sample',
            x: stats.google.value,
            y: stats.survey.value,
            color: '#161816',
            practiceCount: stats.practiceCount,
          }}];
        }})()
      : []),
  ].filter(Boolean);
  const benchmarkPoints = allBenchmarkEntries.filter((point) => point.x !== null && point.y !== null);
  const omittedBenchmarkEntries = allBenchmarkEntries.filter((point) => point.x === null || point.y === null);

  const showPractices = ratingSurveyMode === 'practices';
  const displayPoints = showPractices ? practicePoints : benchmarkPoints;

  if (!practicePoints.length && !benchmarkPoints.length) {{
    svg.innerHTML = '';
    summary.textContent = 'No loaded rows currently have both a usable Google rating and a survey/equivalent overall-good score.';
    return;
  }}
  if (!displayPoints.length) {{
    svg.innerHTML = '';
    summary.textContent = showPractices
      ? 'No loaded practice rows currently have both a usable Google rating and a survey/equivalent overall-good score.'
      : 'No benchmark regions currently have both a usable Google rating and a survey/equivalent overall-good score.';
    return;
  }}

  const width = 920;
  const height = 320;
  const margin = {{ top: 28, right: 18, bottom: 42, left: 52 }};
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const googleValues = displayPoints.map((point) => point.x);
  const surveyValues = displayPoints.map((point) => point.y);
  const rawXMin = Math.min(...googleValues);
  const rawXMax = Math.max(...googleValues);
  const rawYMin = Math.min(...surveyValues);
  const rawYMax = Math.max(...surveyValues);
  const xPad = Math.max(0.1, (rawXMax - rawXMin) * 0.08);
  const yPad = Math.max(2, (rawYMax - rawYMin) * 0.08);
  const xMin = showPractices ? 0 : Math.max(0, rawXMin - xPad);
  const xMax = showPractices ? 5 : Math.min(5, rawXMax + xPad);
  const yMin = showPractices ? 0 : Math.max(0, rawYMin - yPad);
  const yMax = showPractices ? 100 : Math.min(100, rawYMax + yPad);
  const xScale = (value) => margin.left + ((value - xMin) / (xMax - xMin)) * plotWidth;
  const yScale = (value) => margin.top + plotHeight - ((value - yMin) / (yMax - yMin)) * plotHeight;
  const xTicks = showPractices ? [0, 1, 2, 3, 4, 5] : (() => {{
    const step = (xMax - xMin) <= 1.5 ? 0.25 : (xMax - xMin) <= 3 ? 0.5 : 1;
    const ticks = [];
    for (let tick = Math.ceil(xMin / step) * step; tick <= xMax + 0.0001; tick += step) {{
      ticks.push(Number(tick.toFixed(2)));
    }}
    return ticks;
  }})();
  const yTicks = showPractices ? [0, 20, 40, 60, 80, 100] : (() => {{
    const step = (yMax - yMin) <= 20 ? 5 : (yMax - yMin) <= 50 ? 10 : 20;
    const ticks = [];
    for (let tick = Math.ceil(yMin / step) * step; tick <= yMax + 0.0001; tick += step) {{
      ticks.push(Number(tick.toFixed(2)));
    }}
    return ticks;
  }})();
  const trend = showPractices ? quadraticRegression(displayPoints) : null;
  const trendMarkup = trend
    ? (() => {{
        const steps = 48;
        const pathParts = [];
        for (let index = 0; index <= steps; index += 1) {{
          const xValue = xMin + ((index / steps) * (xMax - xMin));
          const yValue = (trend.a * xValue * xValue) + (trend.b * xValue) + trend.c;
          const clampedY = Math.max(yMin, Math.min(yMax, yValue));
          const command = index === 0 ? 'M' : 'L';
          pathParts.push(`${{command}}${{xScale(xValue).toFixed(2)}} ${{yScale(clampedY).toFixed(2)}}`);
        }}
        return `
          <path d="${{pathParts.join(' ')}}" fill="none" stroke="rgba(26,28,26,0.78)" stroke-width="2.6" stroke-dasharray="8 6" stroke-linecap="round" stroke-linejoin="round">
            <title>Overall fitted quadratic trend curve</title>
          </path>
        `;
      }})()
    : '';
  const benchmarkLayoutPoints = benchmarkPoints
    .map((point) => ({{
      ...point,
      plotX: xScale(point.x),
      plotY: yScale(point.y),
    }}))
    .sort((left, right) => (left.plotX - right.plotX) || (left.plotY - right.plotY))
    .map((point, index, plotted) => {{
      const stackIndex = plotted
        .slice(0, index)
        .filter((other) => Math.abs(other.plotX - point.plotX) < 44 && Math.abs(other.plotY - point.plotY) < 24)
        .length % 5;
      return {{
        ...point,
        stackIndex,
      }};
    }});
  const pointMarkup = showPractices ? practicePoints.map((point) => {{
    const nation = String(point.row.nation || '').trim().toLowerCase();
    const isHighlighted = point.row.code === NEW_BANK_CODE || point.row.gtd || point.row.management_company === BASELINE_MANAGEMENT_COMPANY;
    const radius = point.row.code === NEW_BANK_CODE ? 5.8 : isHighlighted ? 4.1 : 2.8;
    const fill = nationScatterColor(nation);
    const stroke = point.row.code === NEW_BANK_CODE ? '#7b3fb2' : isHighlighted ? '#1a1c1a' : 'rgba(26,28,26,0.14)';
    const strokeWidth = point.row.code === NEW_BANK_CODE ? 2.1 : isHighlighted ? 1.2 : 0.6;
    const opacity = isHighlighted ? 0.9 : 0.28;
    return `
      <circle cx="${{xScale(point.x).toFixed(2)}}" cy="${{yScale(point.y).toFixed(2)}}" r="${{radius.toFixed(2)}}" fill="${{fill}}" fill-opacity="${{opacity.toFixed(2)}}" stroke="${{stroke}}" stroke-width="${{strokeWidth}}">
        <title>${{point.row.name}} · ${{displayNationName(point.row.nation)}} · Google ${{point.x.toFixed(1)}} · Survey ${{Math.round(point.y)}}%</title>
      </circle>
    `;
  }}).join('') : '';
  const benchmarkMarkup = benchmarkLayoutPoints.map((point) => {{
    const size = point.kind === 'nation' ? 14 : point.kind === 'city' ? 12 : 12.5;
    const labelY = point.plotY - (size / 2) - 8 - (point.stackIndex * 12);
    return `
      <rect x="${{(point.plotX - size / 2).toFixed(2)}}" y="${{(point.plotY - size / 2).toFixed(2)}}" width="${{size.toFixed(2)}}" height="${{size.toFixed(2)}}" rx="1.4" fill="${{point.color}}" fill-opacity="0.96" stroke="#ffffff" stroke-width="1.6">
        <title>${{escapeHtml(point.label)}} benchmark · Google ${{point.x.toFixed(2)}} · Survey ${{Math.round(point.y)}}% · ${{point.practiceCount.toLocaleString('en-GB')}} practices</title>
      </rect>
      ${{
        showPractices
          ? ''
          : `
            <line x1="${{point.plotX.toFixed(2)}}" y1="${{(point.plotY - size / 2).toFixed(2)}}" x2="${{point.plotX.toFixed(2)}}" y2="${{(labelY + 3).toFixed(2)}}" stroke="${{point.color}}" stroke-opacity="0.42" stroke-width="1.1"></line>
            <text x="${{point.plotX.toFixed(2)}}" y="${{labelY.toFixed(2)}}" text-anchor="middle" font-size="${{point.kind === 'nation' ? '11.5' : '10.5'}}" font-weight="700" fill="${{point.color}}" stroke="rgba(255,255,255,0.92)" stroke-width="3" paint-order="stroke fill">${{escapeHtml(point.label)}}</text>
          `
      }}
    `;
  }}).join('');

  const nationCounts = ['england', 'scotland', 'wales', 'northern_ireland']
    .map((nation) => {{
      const count = practicePoints.filter((point) => String(point.row.nation || '').trim().toLowerCase() === nation).length;
      return count > 0 ? `${{displayNationName(nation)}} ${{count.toLocaleString('en-GB')}}` : '';
    }})
    .filter(Boolean)
    .join(' · ');
  const rValue = correlation(displayPoints.map((point) => ({{ x: point.x, y: point.y }})));
  const formula = trend
    ? `survey ≈ ${{trend.a >= 0 ? '' : '-'}}${{Math.abs(trend.a).toFixed(2)}}·rating² ${{trend.b >= 0 ? '+ ' : '- '}}${{Math.abs(trend.b).toFixed(2)}}·rating ${{trend.c >= 0 ? '+ ' : '- '}}${{Math.abs(trend.c).toFixed(2)}}`
    : 'no curve fit in region mode';
  summary.textContent =
    showPractices
      ? `${{practicePoints.length.toLocaleString('en-GB')}} practice entries currently have both a usable Google rating and a survey/equivalent overall-good score. Pearson r is ${{rValue === null ? '?' : rValue.toFixed(2)}}. ${{nationCounts}}. ${{benchmarkPoints.length}} region overlays are drawn as larger squares.`
      : `${{benchmarkPoints.length}} benchmark regions are currently shown from ${{allBenchmarkEntries.length}} listed entries. Pearson r between those aggregate points is ${{rValue === null ? '?' : rValue.toFixed(2)}}.`;
  note.textContent = showPractices
    ? `Practice mode shows all loaded rows on the full Google 0-5 and survey 0-100 scales, with larger squares for nation, city, North/South, and custom-sample aggregates. Quadratic fit: ${{formula}}.`
    : `Region mode shows only the benchmark aggregates from the Nation and City panel plus North/South and any custom sample, with axes fitted around their local spread. No curve fit is drawn in this mode.${{omittedBenchmarkEntries.length ? ` ${{omittedBenchmarkEntries.length}} listed entries are currently unplottable because one of the two scores is missing: ${{omittedBenchmarkEntries.map((entry) => entry.label).join(', ')}}.` : ''}}`;

  svg.innerHTML = `
    <rect x="0" y="0" width="${{width}}" height="${{height}}" fill="transparent"></rect>
    ${{yTicks.map((tick) => `
      <line x1="${{margin.left}}" y1="${{yScale(tick)}}" x2="${{width - margin.right}}" y2="${{yScale(tick)}}" stroke="rgba(26,28,26,0.10)" />
      <text x="${{margin.left - 8}}" y="${{yScale(tick) + 4}}" text-anchor="end" font-size="11" fill="rgba(26,28,26,0.72)">${{tick}}%</text>
    `).join('')}}
    ${{xTicks.map((tick) => `
      <line x1="${{xScale(tick)}}" y1="${{margin.top}}" x2="${{xScale(tick)}}" y2="${{height - margin.bottom}}" stroke="rgba(26,28,26,0.08)" />
      <text x="${{xScale(tick)}}" y="${{height - margin.bottom + 18}}" text-anchor="middle" font-size="11" fill="rgba(26,28,26,0.72)">${{tick.toFixed(1)}}</text>
    `).join('')}}
    <line x1="${{margin.left}}" y1="${{height - margin.bottom}}" x2="${{width - margin.right}}" y2="${{height - margin.bottom}}" stroke="rgba(26,28,26,0.35)" />
    <line x1="${{margin.left}}" y1="${{margin.top}}" x2="${{margin.left}}" y2="${{height - margin.bottom}}" stroke="rgba(26,28,26,0.35)" />
    ${{trendMarkup}}
    ${{pointMarkup}}
    ${{benchmarkMarkup}}
    <text x="${{width / 2}}" y="${{height - 8}}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)">Google rating</text>
    <text x="14" y="${{height / 2}}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)" transform="rotate(-90 14 ${{height / 2}})">Patient survey overall good</text>
  `;
}}

function renderPatientChangeChart() {{
  const svg = document.getElementById('patient-change-chart');
  const summary = document.getElementById('patient-change-summary');
  const heading = document.getElementById('patient-change-heading');
  const footnote = document.getElementById('patient-change-footnote');
  if (!svg || !summary || !heading || !footnote) return;
  heading.textContent = `Registered Patients Over Time - Coloured by ${{metricDisplayLabel(activeMetric)}}`;

  const years = patientChangeAnalysis?.years || [];
  const series = (patientChangeAnalysis?.practice_series || []).filter((entry) =>
    (entry.points || []).filter((value) => value !== null && Number.isFinite(Number(value))).length >= 2
  );
  if (!years.length || !series.length) {{
    svg.innerHTML = '';
    summary.textContent = 'No practices currently have enough multi-year registered patient counts to plot.';
    footnote.hidden = true;
    footnote.textContent = '';
    return;
  }}

  const width = 920;
  const height = 320;
  const margin = {{ top: 18, right: 18, bottom: 42, left: 56 }};
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const xScale = (index) => margin.left + (years.length <= 1 ? plotWidth / 2 : (index / Math.max(1, years.length - 1)) * plotWidth);
  const xTickIndexes = years.map((_, index) => index);

  function bucketInfo(value) {{
    if (value === null || !Number.isFinite(value)) return null;
    if (activeMetric === 'google') {{
      const bucketValue = Math.round(value * 2) / 2;
      return {{ key: bucketValue.toFixed(1), label: bucketValue.toFixed(1), value: bucketValue }};
    }}
    if (activeMetric === 'survey') {{
      const bucketValue = Math.round(value / 10) * 10;
      return {{ key: String(bucketValue), label: `${{bucketValue}}%`, value: bucketValue }};
    }}
    if (activeGapMode === 'normalized') {{
      const bucketValue = Math.round(value);
      return {{ key: `${{bucketValue}}z`, label: `${{bucketValue > 0 ? '+' : ''}}${{bucketValue}}z`, value: bucketValue }};
    }}
    const bucketValue = Math.round(value * 2) / 2;
    return {{ key: bucketValue.toFixed(1), label: `${{bucketValue > 0 ? '+' : ''}}${{bucketValue.toFixed(1)}}`, value: bucketValue }};
  }}

  const bucketMap = new Map();
  series.forEach((entry) => {{
    const row = rowsByCode.get(entry.code) || null;
    const currentValue = currentMetricValueForRow(row, {{ suppressSmall: false }});
    const bucket = bucketInfo(currentValue);
    if (!bucket) return;
    if (!bucketMap.has(bucket.key)) {{
      bucketMap.set(bucket.key, {{ ...bucket, series: [] }});
    }}
    bucketMap.get(bucket.key).series.push(entry);
  }});

  const sortedBuckets = Array.from(bucketMap.values()).sort((left, right) => left.value - right.value);
  const overallSeriesRaw = patientChangeAnalysis?.average_series || [];
  const flattenGlobal = patientTreemapNormalizeForChange;
  const bucketLineEntries = sortedBuckets.map((bucket) => {{
    const averagePointsRaw = years.map((_, index) => {{
      const values = bucket.series
        .map((entry) => entry.points?.[index])
        .filter((value) => value !== null && Number.isFinite(Number(value)))
        .map(Number);
      return values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : null;
    }});
    const averagePoints = averagePointsRaw.map((value, index) => {{
      if (value === null || !Number.isFinite(Number(value))) return null;
      if (!flattenGlobal) return value;
      const meanValue = Number(overallSeriesRaw[index]);
      if (!Number.isFinite(meanValue) || meanValue <= 0) return null;
      return ((value / meanValue) - 1) * 100;
    }});
    const representative = bucket.series
      .map((entry) => rowsByCode.get(entry.code))
      .find(Boolean);
    const color = representative ? colorForCurrentMetric(representative, {{ suppressSmall: false }}) : '#9aa0a6';
    const lastIndex = averagePoints.reduce((acc, value, index) => (value !== null && Number.isFinite(value) ? index : acc), -1);
    const lastValue = lastIndex >= 0 ? averagePoints[lastIndex] : null;
    return {{
      averagePoints,
      color,
      label: `${{bucket.label}} · n=${{bucket.series.length}}`,
      lastIndex,
      lastValue,
    }};
  }}).filter((entry) => entry.averagePoints.some((value) => value !== null && Number.isFinite(value)));

  const overallSeries = flattenGlobal
    ? overallSeriesRaw.map((value) => (value !== null && Number.isFinite(Number(value)) ? 0 : null))
    : overallSeriesRaw;
  const displayedValues = [
    ...overallSeries.filter((value) => value !== null && Number.isFinite(Number(value))).map(Number),
    ...bucketLineEntries.flatMap((entry) => entry.averagePoints.filter((value) => value !== null && Number.isFinite(Number(value))).map(Number)),
  ].sort((a, b) => a - b);
  let yMin = 0;
  let yMax = 1000;
  const yTicks = [];
  if (flattenGlobal) {{
    const maxAbs = displayedValues.length ? Math.max(...displayedValues.map((value) => Math.abs(value))) : 10;
    const roundedAbs = Math.max(10, Math.ceil(maxAbs / 5) * 5);
    yMin = -roundedAbs;
    yMax = roundedAbs;
    const yStep = roundedAbs <= 20 ? 5 : roundedAbs <= 50 ? 10 : 20;
    for (let tick = yMin; tick <= yMax + 0.001; tick += yStep) {{
      yTicks.push(Number(tick.toFixed(2)));
    }}
  }} else {{
    const scopedMax = displayedValues.length ? displayedValues[displayedValues.length - 1] : 0;
    yMax = Math.max(1000, Math.ceil((scopedMax || 1000) / 1000) * 1000);
    const yStep = yMax <= 5000 ? 1000 : yMax <= 15000 ? 2500 : 5000;
    for (let tick = 0; tick <= yMax; tick += yStep) {{
      yTicks.push(tick);
    }}
  }}
  const yScale = (value) => {{
    const clamped = Math.min(yMax, Math.max(yMin, value));
    return margin.top + plotHeight - ((clamped - yMin) / Math.max(1, (yMax - yMin))) * plotHeight;
  }};
  const bucketLines = bucketLineEntries.map((entry) => {{
    const path = linePath(entry.averagePoints, xScale, yScale);
    if (!path) return '';
    return `
      <path d="${{path}}" fill="none" stroke="${{entry.color}}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"></path>
      ${{entry.lastValue === null ? '' : `<circle cx="${{xScale(entry.lastIndex).toFixed(2)}}" cy="${{yScale(entry.lastValue).toFixed(2)}}" r="4.2" fill="${{entry.color}}"></circle>
      <text x="${{Math.min(width - margin.right, xScale(entry.lastIndex) + 8).toFixed(2)}}" y="${{(yScale(entry.lastValue) - 7).toFixed(2)}}" font-size="10.5" font-weight="700" fill="${{entry.color}}">${{entry.label}}</text>`}}
    `;
  }}).join('');

  const overallPath = linePath(overallSeries, xScale, yScale);

  svg.innerHTML = `
    <rect x="0" y="0" width="${{width}}" height="${{height}}" fill="transparent"></rect>
    ${{yTicks.map((tick) => `
      <line x1="${{margin.left}}" y1="${{yScale(tick)}}" x2="${{width - margin.right}}" y2="${{yScale(tick)}}" stroke="${{flattenGlobal && tick === 0 ? 'rgba(26,28,26,0.28)' : 'rgba(26,28,26,0.10)'}}" />
      <text x="${{margin.left - 8}}" y="${{yScale(tick) + 4}}" text-anchor="end" font-size="11" fill="rgba(26,28,26,0.72)">${{flattenGlobal ? `${{tick > 0 ? '+' : ''}}${{tick.toFixed(0)}}%` : tick.toLocaleString('en-GB')}}</text>
    `).join('')}}
    ${{xTickIndexes.map((index) => `
      <line x1="${{xScale(index)}}" y1="${{margin.top}}" x2="${{xScale(index)}}" y2="${{height - margin.bottom}}" stroke="rgba(26,28,26,0.08)" />
      <text x="${{xScale(index)}}" y="${{height - margin.bottom + 18}}" text-anchor="middle" font-size="11" fill="rgba(26,28,26,0.72)">${{years[index]}}</text>
    `).join('')}}
    <line x1="${{margin.left}}" y1="${{height - margin.bottom}}" x2="${{width - margin.right}}" y2="${{height - margin.bottom}}" stroke="rgba(26,28,26,0.35)" />
    <line x1="${{margin.left}}" y1="${{margin.top}}" x2="${{margin.left}}" y2="${{height - margin.bottom}}" stroke="rgba(26,28,26,0.35)" />
    ${{overallPath ? `<path d="${{overallPath}}" fill="none" stroke="rgba(26,28,26,0.55)" stroke-width="2.2" stroke-dasharray="6 4" stroke-linecap="round" stroke-linejoin="round"></path>` : ''}}
    ${{bucketLines}}
    <text x="${{width / 2}}" y="${{height - 8}}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)">Year</text>
    <text x="14" y="${{height / 2}}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)" transform="rotate(-90 14 ${{height / 2}})">${{flattenGlobal ? 'Variance from Manchester mean practice count (%)' : 'Registered patients'}}</text>
  `;

  const newBank = series.find((entry) => entry.code === NEW_BANK_CODE);
  const newBankStart = newBank ? newBank.points.find((value) => value !== null) : null;
  const newBankEnd = newBank ? [...newBank.points].reverse().find((value) => value !== null) : null;
  const newBankSummary = !newBank || newBankStart === null || newBankEnd === null
    ? ''
    : flattenGlobal
      ? (() => {{
          const startMean = Number(overallSeriesRaw[newBank.points.findIndex((value) => value !== null)]);
          const endMean = Number(overallSeriesRaw[newBank.points.length - 1 - [...newBank.points].reverse().findIndex((value) => value !== null)]);
          const startDelta = Number.isFinite(startMean) && startMean > 0 ? ((Number(newBankStart) / startMean) - 1) * 100 : null;
          const endDelta = Number.isFinite(endMean) && endMean > 0 ? ((Number(newBankEnd) / endMean) - 1) * 100 : null;
          return ` New Bank shifts from ${{startDelta === null ? '?' : `${{startDelta > 0 ? '+' : ''}}${{startDelta.toFixed(1)}}%`}} to ${{endDelta === null ? '?' : `${{endDelta > 0 ? '+' : ''}}${{endDelta.toFixed(1)}}%`}} versus the Manchester mean practice count.`;
        }})()
      : ` New Bank runs from ${{Number(newBankStart).toLocaleString('en-GB')}} to ${{Number(newBankEnd).toLocaleString('en-GB')}} patients across the available series.`;
  summary.textContent =
    `${{series.length}} practices have multi-year patient-count histories in this chart. Coloured lines show the average trajectory for each current ${{metricDisplayLabel(activeMetric).toLowerCase()}} band, and the dashed grey line is the Manchester average practice count for each year.${{flattenGlobal ? ' With Flatten Global on, the left y-axis shows deviation from that yearly Manchester mean, so the chart shows which score bands are gaining or losing relative share rather than absolute patient volume.' : ' The left y-axis is scoped to those displayed patient averages rather than every individual practice line.'}}${{newBankSummary}}`;
  
    footnote.hidden = false;
    footnote.textContent = 'Patient growth footnote: both stronger and weaker score bands show only VERY slight divergence from the mean, with better-rated / better-surveyed practices gaining patients a little faster and worse-performing GPs gaining a little more slowly. That suggests patients ARE moving toward better doctors, but INCREDIBLY slowly. One possible reading is that poor access can still trap patients who need more access, convenience, or support most, while others who have a choice (and know it) are more able to switch. This is however in a context of relative to growth, where population pressure is present, but seemingly not a large driver of experience. This suggests policy drives experience more than population pressure, though further investigation might help here.';
}}

function stopPatientTreemapPlayback() {{
  if (patientTreemapTimer) {{
    clearInterval(patientTreemapTimer);
    patientTreemapTimer = null;
  }}
  patientTreemapPlaying = false;
}}

function startPatientTreemapPlayback() {{
  const years = patientChangeAnalysis?.years || [];
  if (years.length < 2) return;
  if (patientTreemapYearIndex === null || patientTreemapYearIndex >= years.length - 1) {{
    patientTreemapYearIndex = 0;
  }}
  stopPatientTreemapPlayback();
  patientTreemapPlaying = true;
  patientTreemapTimer = setInterval(() => {{
    patientTreemapYearIndex = ((patientTreemapYearIndex ?? 0) + 1) % years.length;
    renderPatientTreemap();
  }}, 1100);
}}

function renderPatientTotalChart(years, activeYearIndex) {{
  const svg = document.getElementById('patient-total-chart');
  if (!svg) return;
  if (!years.length) {{
    svg.innerHTML = '';
    return;
  }}
  const totals = years.map((year) => {{
    const counts = patientCountsByYear?.[year] || {{}};
    return Object.values(counts).reduce((sum, value) => {{
      const numeric = numericOrNull(value);
      return numeric !== null && numeric > 0 ? sum + numeric : sum;
    }}, 0);
  }});
  const usableTotals = totals.filter((value) => Number.isFinite(value) && value > 0);
  if (!usableTotals.length) {{
    svg.innerHTML = '';
    return;
  }}

  const width = 920;
  const height = 118;
  const margin = {{ top: 8, right: 12, bottom: 22, left: 54 }};
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const reviewLineColor = '#d26a1b';
  const minTotal = Math.min(...usableTotals);
  const maxTotal = Math.max(...usableTotals);
  const paddedMin = minTotal * 0.99;
  const paddedMax = maxTotal * 1.01;
  const yRange = Math.max(1, paddedMax - paddedMin);
  const xScale = (index) => margin.left + (years.length <= 1 ? plotWidth / 2 : (index / Math.max(1, years.length - 1)) * plotWidth);
  const yScale = (value) => margin.top + plotHeight - ((value - paddedMin) / yRange) * plotHeight;
  const path = totals.map((value, index) => `${{index === 0 ? 'M' : 'L'}}${{xScale(index).toFixed(2)}} ${{yScale(value).toFixed(2)}}`).join(' ');
  const reviewSeriesRaw = patientChangeAnalysis?.dataset_review_average_series || [];
  const reviewCounts = patientChangeAnalysis?.dataset_review_average_practice_counts || [];
  const reviewSeries = years.map((_year, index) => {{
    const value = reviewSeriesRaw[index];
    return value !== null && Number.isFinite(Number(value)) ? Number(value) : null;
  }});
  const reviewYMin = 1;
  const reviewYMax = 5;
  const reviewYScale = (value) => margin.top + plotHeight - ((Math.min(reviewYMax, Math.max(reviewYMin, value)) - reviewYMin) / Math.max(1, (reviewYMax - reviewYMin))) * plotHeight;
  const reviewPath = linePath(reviewSeries, xScale, reviewYScale);
  const reviewActiveValue = reviewSeries[activeYearIndex] ?? null;
  const activeTotal = totals[activeYearIndex];
  const firstTotal = totals[0];
  const lastTotal = totals[totals.length - 1];
  const changePct = firstTotal > 0 ? ((lastTotal / firstTotal) - 1) * 100 : null;
  const labelStep = Math.max(1, Math.ceil(years.length / 6));
  const tickIndexes = years
    .map((_year, index) => index)
    .filter((index) => index % labelStep === 0 || index === years.length - 1);

  svg.innerHTML = `
    <rect x="0" y="0" width="${{width}}" height="${{height}}" fill="transparent"></rect>
    <rect x="${{margin.left}}" y="${{margin.top}}" width="${{plotWidth}}" height="${{plotHeight}}" fill="rgba(26,28,26,0.03)" rx="6"></rect>
    <path d="${{path}} L${{xScale(years.length - 1).toFixed(2)}} ${{(margin.top + plotHeight).toFixed(2)}} L${{xScale(0).toFixed(2)}} ${{(margin.top + plotHeight).toFixed(2)}} Z" fill="rgba(15,94,156,0.10)"></path>
    <path d="${{path}}" fill="none" stroke="var(--accent)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"></path>
    ${{reviewPath ? `<path d="${{reviewPath}}" fill="none" stroke="${{reviewLineColor}}" stroke-width="2.8" stroke-dasharray="5 4" stroke-linecap="round" stroke-linejoin="round"></path>` : ''}}
    ${{reviewSeries.map((value, index) => value === null ? '' : `<circle cx="${{xScale(index).toFixed(2)}}" cy="${{reviewYScale(value).toFixed(2)}}" r="2.9" fill="${{reviewLineColor}}" stroke="white" stroke-width="0.9"></circle>`).join('')}}
    ${{tickIndexes.map((index) => `
      <text x="${{xScale(index).toFixed(2)}}" y="${{height - 6}}" text-anchor="middle" font-size="10.5" fill="rgba(26,28,26,0.68)">${{years[index]}}</text>
    `).join('')}}
    ${{[1, 2, 3, 4, 5].map((tick) => `
      <text x="${{margin.left - 8}}" y="${{reviewYScale(tick) + 4}}" text-anchor="end" font-size="10" font-weight="700" fill="${{reviewLineColor}}">${{tick.toFixed(1)}}</text>
    `).join('')}}
    <circle cx="${{xScale(activeYearIndex).toFixed(2)}}" cy="${{yScale(activeTotal).toFixed(2)}}" r="4.2" fill="var(--accent)" stroke="white" stroke-width="1.2"></circle>
    ${{reviewActiveValue === null ? '' : `<circle cx="${{xScale(activeYearIndex).toFixed(2)}}" cy="${{reviewYScale(reviewActiveValue).toFixed(2)}}" r="3.4" fill="${{reviewLineColor}}" stroke="white" stroke-width="1.1"></circle>`}}
    <text x="${{Math.min(width - margin.right, xScale(activeYearIndex) + 8).toFixed(2)}}" y="${{Math.max(18, yScale(activeTotal) - 8).toFixed(2)}}" font-size="11" font-weight="700" fill="var(--accent)">${{years[activeYearIndex]}} · ${{activeTotal.toLocaleString('en-GB')}}</text>
    ${{reviewActiveValue === null ? '' : `<text x="${{Math.min(width - margin.right - 6, xScale(activeYearIndex) + 8).toFixed(2)}}" y="${{Math.min(height - margin.bottom - 6, reviewYScale(reviewActiveValue) + 14).toFixed(2)}}" font-size="10.5" font-weight="700" fill="${{reviewLineColor}}">${{reviewActiveValue.toFixed(2)}} ★ · n=${{Number(reviewCounts[activeYearIndex] || 0)}}</text>`}}
    <text x="${{margin.left + 6}}" y="${{margin.top + 14}}" font-size="10.5" fill="rgba(26,28,26,0.72)">Whole dataset total: ${{firstTotal.toLocaleString('en-GB')}} -> ${{lastTotal.toLocaleString('en-GB')}} (${{changePct === null ? '?' : `${{changePct >= 0 ? '+' : ''}}${{changePct.toFixed(1)}}%`}})</text>
    <text x="14" y="${{height / 2}}" text-anchor="middle" font-size="10.5" font-weight="700" fill="${{reviewLineColor}}" transform="rotate(-90 14 ${{height / 2}})">Average Google review score</text>
  `;
}}

function renderPatientTreemap() {{
  const svg = document.getElementById('patient-treemap-chart');
  const summary = document.getElementById('patient-treemap-summary');
  const heading = document.getElementById('patient-treemap-heading');
  const playButton = document.getElementById('patient-treemap-play');
  const slider = document.getElementById('patient-treemap-year');
  const yearLabel = document.getElementById('patient-treemap-year-label');
  const normalizeToggle = document.getElementById('normalize-patient-change-toggle');
  if (!svg || !summary || !heading || !playButton || !slider || !yearLabel || !normalizeToggle) return;

  const years = patientChangeAnalysis?.years || [];
  const sourceSeries = (patientChangeAnalysis?.practice_series || []).filter((entry) =>
    (entry.points || []).some((value) => value !== null && Number.isFinite(Number(value)) && Number(value) > 0)
  );
  if (!years.length || !sourceSeries.length) {{
    svg.innerHTML = '';
    renderPatientTotalChart([], 0);
    summary.textContent = 'No patient-count treemap data is available.';
    playButton.textContent = 'Play';
    yearLabel.textContent = 'Year';
    return;
  }}

  if (patientTreemapYearIndex === null || patientTreemapYearIndex >= years.length) {{
    patientTreemapYearIndex = years.length - 1;
  }}
  const latestIndex = years.length - 1;
  const yearIndex = Math.max(0, Math.min(years.length - 1, patientTreemapYearIndex));
  const year = years[yearIndex];
  slider.max = String(Math.max(0, years.length - 1));
  slider.value = String(yearIndex);
  playButton.textContent = patientTreemapPlaying ? 'Pause' : 'Play';
  playButton.setAttribute('aria-pressed', patientTreemapPlaying ? 'true' : 'false');
  yearLabel.textContent = year;
  normalizeToggle.checked = patientTreemapNormalizeForChange;
  heading.textContent = `Patient Count Treemap - Coloured by ${{metricDisplayLabel(activeMetric)}}`;

  const yearTotals = years.map((yearKey) => {{
    const counts = patientCountsByYear?.[yearKey] || {{}};
    return Object.values(counts).reduce((sum, value) => {{
      const numeric = numericOrNull(value);
      return numeric !== null && numeric > 0 ? sum + numeric : sum;
    }}, 0);
  }});
  const referenceTotal = yearTotals[latestIndex] || yearTotals[yearIndex] || 0;
  const scaledValueForYear = (rawValue, index) => {{
    const absolute = Math.max(0, Number(rawValue || 0));
    if (!patientTreemapNormalizeForChange) return absolute;
    const total = yearTotals[index] || 0;
    if (!(absolute > 0) || !(total > 0) || !(referenceTotal > 0)) return 0;
    return (absolute / total) * referenceTotal;
  }};

  function googleReviewBandInfo(row) {{
    const google = numericOrNull(row?.google_score);
    if (google === null) return {{ key: 'unknown', label: 'review unknown', shortLabel: 'Ind ?' , order: 4 }};
    if (google < 3) return {{ key: 'lt3', label: 'review <3.0', shortLabel: 'Ind <3.0', order: 0 }};
    if (google < 4) return {{ key: '3to4', label: 'review 3.0-3.9', shortLabel: 'Ind 3-3.9', order: 1 }};
    if (google < 4.5) return {{ key: '4to45', label: 'review 4.0-4.4', shortLabel: 'Ind 4-4.4', order: 2 }};
    return {{ key: 'gte45', label: 'review 4.5+', shortLabel: 'Ind 4.5+', order: 3 }};
  }}

  const latestTotalsByNamedGroup = new Map();
  sourceSeries.forEach((entry) => {{
    const row = rowsByCode.get(entry.code) || null;
    const rawGroup = entry.management_company || row?.management_company || '';
    if (!rawGroup) return;
    const latestValue = scaledValueForYear(entry.points?.[latestIndex], latestIndex);
    latestTotalsByNamedGroup.set(rawGroup, (latestTotalsByNamedGroup.get(rawGroup) || 0) + latestValue);
  }});

  const sortedNamedGroups = Array.from(latestTotalsByNamedGroup.entries())
    .sort((left, right) => {{
      if (left[0] === BASELINE_MANAGEMENT_COMPANY) return -1;
      if (right[0] === BASELINE_MANAGEMENT_COMPANY) return 1;
      return right[1] - left[1];
    }})
    .map(([name]) => name);
  const retainedNamedGroups = new Set([
    ...sortedNamedGroups.filter((name) => name === BASELINE_MANAGEMENT_COMPANY),
    ...sortedNamedGroups.filter((name) => name !== BASELINE_MANAGEMENT_COMPANY).slice(0, 4),
  ]);

  const grouped = new Map();
  sourceSeries.forEach((entry) => {{
    const row = rowsByCode.get(entry.code) || null;
    const rawGroup = entry.management_company || row?.management_company || '';
    const band = googleReviewBandInfo(row);
    const display = rawGroup && retainedNamedGroups.has(rawGroup)
      ? {{
          key: `named:${{rawGroup}}`,
          name: rawGroup,
          shortLabel: rawGroup,
          sortBucket: rawGroup === BASELINE_MANAGEMENT_COMPANY ? 0 : 1,
          sortValue: -(latestTotalsByNamedGroup.get(rawGroup) || 0),
        }}
      : {{
          key: `independent:${{band.key}}`,
          name: `Independent / other · ${{band.label}}`,
          shortLabel: band.shortLabel,
          sortBucket: 2,
          sortValue: band.order,
        }};
    if (!grouped.has(display.key)) {{
      grouped.set(display.key, {{ ...display, series: [] }});
    }}
    grouped.get(display.key).series.push(entry);
  }});

  const groups = Array.from(grouped.values())
    .map((group) => {{
      const orderedSeries = [...group.series].sort((left, right) => {{
        const leftLatest = scaledValueForYear(left.points?.[latestIndex], latestIndex);
        const rightLatest = scaledValueForYear(right.points?.[latestIndex], latestIndex);
        if (rightLatest !== leftLatest) return rightLatest - leftLatest;
        return String(left.name || '').localeCompare(String(right.name || ''));
      }});
      const totalsByYear = years.map((_year, index) =>
        orderedSeries.reduce((sum, entry) => sum + scaledValueForYear(entry.points?.[index], index), 0)
      );
      const peakTotal = Math.max(0, ...totalsByYear);
      const currentTotal = totalsByYear[yearIndex] || 0;
      return {{
        ...group,
        series: orderedSeries,
        totalsByYear,
        peakTotal,
        currentTotal,
      }};
    }})
    .filter((group) => group.peakTotal > 0)
    .sort((left, right) => (
      left.sortBucket - right.sortBucket ||
      left.sortValue - right.sortValue ||
      right.peakTotal - left.peakTotal ||
      left.name.localeCompare(right.name)
    ));

  if (!groups.length) {{
    svg.innerHTML = '';
    renderPatientTotalChart(years, yearIndex);
    summary.textContent = `No practices have a registered-patient value for ${{year}}.`;
    return;
  }}

  const width = 920;
  const height = 420;
  const margin = {{ top: 6, right: 6, bottom: 6, left: 6 }};
  const groupGap = 6;
  const headerHeight = 22;
  const innerPad = 2;
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const stackHeight = plotHeight - headerHeight - innerPad;
  const totalPeakPatients = groups.reduce((sum, group) => sum + group.peakTotal, 0);
  const pixelsPerPatient = totalPeakPatients > 0
    ? ((plotWidth - (groupGap * Math.max(0, groups.length - 1))) * stackHeight) / totalPeakPatients
    : 0;
  const patientsPerPixel = pixelsPerPatient > 0 ? 1 / pixelsPerPatient : null;

  function layoutAreaRects(entries, x, y, width, height, total) {{
    if (!entries.length || total <= 0 || width <= 0 || height <= 0) return [];
    if (entries.length === 1) {{
      return [{{ entry: entries[0], x, y, width, height }}];
    }}
    const horizontalSplit = width >= height;
    let splitIndex = 1;
    let firstTotal = scaledValueForYear(entries[0].points?.[yearIndex], yearIndex);
    while (splitIndex < entries.length - 1 && firstTotal < total / 2) {{
      splitIndex += 1;
      firstTotal += scaledValueForYear(entries[splitIndex - 1].points?.[yearIndex], yearIndex);
    }}
    const secondTotal = Math.max(0, total - firstTotal);
    const firstEntries = entries.slice(0, splitIndex);
    const secondEntries = entries.slice(splitIndex);
    if (!secondEntries.length || secondTotal <= 0) {{
      return [{{ entry: entries[0], x, y, width, height }}];
    }}
    if (horizontalSplit) {{
      const firstWidth = width * (firstTotal / total);
      return [
        ...layoutAreaRects(firstEntries, x, y, firstWidth, height, firstTotal),
        ...layoutAreaRects(secondEntries, x + firstWidth, y, width - firstWidth, height, secondTotal),
      ];
    }}
    const firstHeight = height * (firstTotal / total);
    return [
      ...layoutAreaRects(firstEntries, x, y, width, firstHeight, firstTotal),
      ...layoutAreaRects(secondEntries, x, y + firstHeight, width, height - firstHeight, secondTotal),
    ];
  }}

  let cursorX = margin.left;
  const groupMarkup = groups.map((group) => {{
    const groupWidth = group.peakTotal > 0 && pixelsPerPatient > 0
      ? (group.peakTotal * pixelsPerPatient) / stackHeight
      : 0;
    const x = cursorX;
    cursorX += groupWidth + groupGap;
    const usedHeight = group.peakTotal > 0 ? stackHeight * (group.currentTotal / group.peakTotal) : 0;
    const headerTitle = `${{group.name}} · ${{group.currentTotal.toLocaleString('en-GB')}} patients in ${{year}} · peak ${{group.peakTotal.toLocaleString('en-GB')}} across ${{group.series.length}} practices`;
    const headerText = groupWidth > 96
      ? `${{ellipsize(group.shortLabel, Math.max(8, Math.floor((groupWidth - 18) / 7)))}} · ${{compactPatientCount(group.currentTotal)}}`
      : '';
    let cursorY = margin.top + headerHeight + innerPad;
    const visibleSeries = group.series.filter((entry) => Number(entry.points?.[yearIndex] || 0) > 0);
    const rectFrames = group.sortBucket === 2
      ? layoutAreaRects(
          visibleSeries,
          x + innerPad,
          margin.top + headerHeight + innerPad,
          Math.max(0, groupWidth - innerPad * 2),
          Math.max(0, usedHeight),
          group.currentTotal
        )
      : visibleSeries.map((entry, index) => {{
          const patientCount = scaledValueForYear(entry.points?.[yearIndex], yearIndex);
          const remainingHeight = (margin.top + headerHeight + innerPad + usedHeight) - cursorY;
          const rectHeight = index === visibleSeries.length - 1
            ? remainingHeight
            : Math.max(1.5, usedHeight * (patientCount / group.currentTotal));
          const y = cursorY;
          cursorY += rectHeight;
          return {{
            entry,
            x: x + innerPad,
            y,
            width: Math.max(0, groupWidth - innerPad * 2),
            height: Math.max(0, rectHeight),
          }};
        }});
    const rectMarkup = rectFrames.map((frame) => {{
      const entry = frame.entry;
      const row = rowsByCode.get(entry.code) || null;
      const rawPatientCount = Math.max(0, Number(entry.points?.[yearIndex] || 0));
      const patientCount = scaledValueForYear(rawPatientCount, yearIndex);
      const fill = colorForCurrentMetric(row, {{ suppressSmall: false }});
      const metricValue = currentMetricValueForRow(row, {{ suppressSmall: false }});
      const badge = patientTreemapNormalizeForChange
        ? `${{compactMetricValue(metricValue, activeMetric)}} / ${{(yearTotals[yearIndex] > 0 ? ((rawPatientCount / yearTotals[yearIndex]) * 100) : 0).toFixed(1)}}%`
        : `${{compactMetricValue(metricValue, activeMetric)}} / ${{compactPatientCount(patientCount)}}`;
      const rectWidth = Math.max(0, frame.width);
      const rectHeight = Math.max(0, frame.height);
      const textPad = Math.max(3, Math.min(7, Math.floor(Math.min(rectWidth, rectHeight) * 0.08)));
      const nameFontSize = Math.max(7.5, Math.min(11, Math.min(rectWidth / 10.5, rectHeight / 3.1)));
      const badgeFontSize = Math.max(6.8, Math.min(10.5, Math.min(rectWidth / 9.5, rectHeight / 3.4)));
      const textWidthChars = Math.max(5, Math.floor((rectWidth - (textPad * 2)) / Math.max(5.6, badgeFontSize * 0.58)));
      const showName = rectWidth >= 70 && rectHeight >= 24;
      const showBadge = rectWidth >= 38 && rectHeight >= 12;
      const nameText = ellipsize(entry.name || entry.code, textWidthChars);
      const strokeWidth = row?.gtd ? 1.2 : 0.8;
      const title = patientTreemapNormalizeForChange
        ? `${{entry.name}} · ${{group.name}} · ${{year}} patients: ${{rawPatientCount.toLocaleString('en-GB')}} (${{yearTotals[yearIndex] > 0 ? ((rawPatientCount / yearTotals[yearIndex]) * 100).toFixed(2) : '0.00'}}% of dataset, scaled to constant pool) · Current ${{metricScopeLabel(activeMetric)}}: ${{compactMetricValue(metricValue, activeMetric)}}`
        : `${{entry.name}} · ${{group.name}} · ${{year}} patients: ${{patientCount.toLocaleString('en-GB')}} · Current ${{metricScopeLabel(activeMetric)}}: ${{compactMetricValue(metricValue, activeMetric)}}`;
      const nameY = frame.y + textPad + nameFontSize;
      const badgeY = frame.y + textPad + (showName ? nameFontSize + Math.max(2, badgeFontSize * 1.15) : badgeFontSize);
      return `
        <g>
          <rect x="${{frame.x.toFixed(2)}}" y="${{frame.y.toFixed(2)}}" width="${{rectWidth.toFixed(2)}}" height="${{Math.max(0, rectHeight - 1).toFixed(2)}}" rx="2.5" fill="${{fill}}" stroke="rgba(26,28,26,0.28)" stroke-width="${{strokeWidth}}">
            <title>${{title}}</title>
          </rect>
          ${{showName ? `<text x="${{(frame.x + textPad).toFixed(2)}}" y="${{nameY.toFixed(2)}}" font-size="${{nameFontSize.toFixed(1)}}" font-weight="700" fill="rgba(255,255,255,0.94)">${{nameText}}</text>` : ''}}
          ${{showBadge ? `<text x="${{(frame.x + textPad).toFixed(2)}}" y="${{badgeY.toFixed(2)}}" font-size="${{badgeFontSize.toFixed(1)}}" fill="rgba(255,255,255,0.94)">${{ellipsize(badge, Math.max(5, textWidthChars + (showName ? 0 : 2)))}}</text>` : ''}}
        </g>
      `;
    }}).join('');
    return `
      <g>
        <rect x="${{x.toFixed(2)}}" y="${{margin.top.toFixed(2)}}" width="${{groupWidth.toFixed(2)}}" height="${{plotHeight.toFixed(2)}}" fill="rgba(26,28,26,0.03)" rx="5"></rect>
        <rect x="${{x.toFixed(2)}}" y="${{margin.top.toFixed(2)}}" width="${{groupWidth.toFixed(2)}}" height="${{headerHeight.toFixed(2)}}" fill="rgba(26,28,26,0.08)" rx="5"></rect>
        <rect x="${{(x + innerPad).toFixed(2)}}" y="${{(margin.top + headerHeight + innerPad).toFixed(2)}}" width="${{Math.max(0, groupWidth - innerPad * 2).toFixed(2)}}" height="${{Math.max(0, stackHeight).toFixed(2)}}" fill="rgba(26,28,26,0.025)" rx="3"></rect>
        ${{headerText ? `<text x="${{(x + 7).toFixed(2)}}" y="${{(margin.top + 14).toFixed(2)}}" font-size="11" font-weight="700" fill="rgba(26,28,26,0.82)">${{headerText}}</text>` : ''}}
        <title>${{headerTitle}}</title>
        ${{rectMarkup}}
      </g>
    `;
  }}).join('');

  svg.innerHTML = `
    <rect x="0" y="0" width="${{width}}" height="${{height}}" fill="transparent"></rect>
    ${{groupMarkup}}
  `;
  renderPatientTotalChart(years, yearIndex);

  const largestGroup = groups[0] || null;
  const visiblePracticeCount = groups.reduce((sum, group) => sum + group.series.filter((entry) => Number(entry.points?.[yearIndex] || 0) > 0).length, 0);
  const largestCurrentGroup = [...groups].sort((left, right) => right.currentTotal - left.currentTotal)[0] || null;
  const totalFirst = yearTotals[0] || 0;
  const totalLast = yearTotals[yearTotals.length - 1] || 0;
  const totalChangePct = totalFirst > 0 ? ((totalLast / totalFirst) - 1) * 100 : null;
  const referenceYear = years[latestIndex] || year;
  summary.textContent =
    `${{visiblePracticeCount}} practices are shown for ${{year}} across ${{groups.length}} treemap columns. Rectangle area uses a fixed scale of ${{patientsPerPixel === null ? '?' : patientsPerPixel.toFixed(2)}} ${{patientTreemapNormalizeForChange ? 'normalised patients' : 'patients'}} per pixel, so the same area basis is used across all years and groups. Named operator columns stay separate, while independent/other practices are split by Google review band. Colour shows current ${{metricDisplayLabel(activeMetric).toLowerCase()}}, and labels use ${{patientTreemapNormalizeForChange ? 'score / dataset share' : 'score / patients'}}. Largest live block this year is ${{largestCurrentGroup ? `${{largestCurrentGroup.name}} with ${{patientTreemapNormalizeForChange ? `${{largestCurrentGroup.currentTotal.toFixed(0)}} normalised patients` : `${{largestCurrentGroup.currentTotal.toLocaleString('en-GB')}} patients`}}` : '?'}}, while the widest reserved column is ${{largestGroup ? `${{largestGroup.name}} at peak ${{patientTreemapNormalizeForChange ? `${{largestGroup.peakTotal.toFixed(0)}} normalised patients` : `${{largestGroup.peakTotal.toLocaleString('en-GB')}}`}}` : '?'}}. Whole-dataset registered patients move from ${{totalFirst.toLocaleString('en-GB')}} to ${{totalLast.toLocaleString('en-GB')}} across this series (${{totalChangePct === null ? '?' : `${{totalChangePct >= 0 ? '+' : ''}}${{totalChangePct.toFixed(1)}}%`}}).${{patientTreemapNormalizeForChange ? ` In this mode each year is rescaled to the ${{referenceYear}} total, so box changes reflect redistribution within the pool rather than overall pool growth.` : ''}}`;
}}

function formatMonthLabel(monthIso) {{
  const value = new Date(`${{monthIso}}T00:00:00`);
  return value.toLocaleDateString('en-GB', {{ month: 'short', year: 'numeric' }});
}}

function formatTakeoverDate(dateIso, precision = '') {{
  if (!dateIso) return '';
  const value = new Date(`${{dateIso}}T00:00:00`);
  if (Number.isNaN(value.getTime())) return dateIso;
  const options = precision === 'month'
    ? {{ month: 'long', year: 'numeric' }}
    : {{ day: 'numeric', month: 'long', year: 'numeric' }};
  return value.toLocaleDateString('en-GB', options);
}}

function linePath(points, xScale, yScale) {{
  let path = '';
  points.forEach((value, index) => {{
    if (value === null || !Number.isFinite(value)) return;
    const command = path ? 'L' : 'M';
    path += `${{command}}${{xScale(index).toFixed(2)}} ${{yScale(value).toFixed(2)}} `;
  }});
  return path.trim();
}}

function fractionalYearIndex(dateIso, years) {{
  if (!dateIso || !years.length) return null;
  const target = new Date(`${{dateIso}}T00:00:00`);
  if (Number.isNaN(target.getTime())) return null;
  const targetYear = target.getUTCFullYear();
  const firstYear = parseInt(years[0], 10);
  const lastYear = parseInt(years[years.length - 1], 10);
  if (targetYear < firstYear) return -1;
  if (targetYear > lastYear) return years.length;
  const idx = years.indexOf(String(targetYear));
  return idx >= 0 ? idx : null;
}}

function renderGtdSurveyTrendChart(svg, summary, legend, overlayLegend, heading, note) {{
  const years = gtdSurveyTimeseries.years || [];
  const practiceSeries = gtdSurveyTimeseries.practice_series || [];
  const averageSeries = gtdSurveyTimeseries.average_series || [];
  if (heading) heading.textContent = `GTD Score Over Time - Showing ${{metricDisplayLabel(activeMetric)}}`;
  if (note) note.textContent = 'Thin lines show each GTD practice\\'s GP Patient Survey overall-experience-as-good percentage by year. Faint dashed vertical lines mark the documented GTD takeover date. Only the first legend entry shows the GTD mean; selecting any named practice hides it. The green dashed line shows registered patients as a percentage of the GTD-wide average patient count for that year, with raw patient counts kept in the point labels. Data from gp-patient.co.uk practice-level CSV.';
  const width = 920;
  const height = 360;
  const margin = {{ top: 18, right: 22, bottom: 56, left: 46 }};
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const xScale = (index) => margin.left + (years.length <= 1 ? plotWidth / 2 : (index / Math.max(1, years.length - 1)) * plotWidth);
  const yMin = 0;
  const yMax = 100;
  const yScale = (value) => margin.top + plotHeight - ((value - yMin) / (yMax - yMin)) * plotHeight;
  const yTicks = [0, 25, 50, 75, 100];
  const palette = [
    '#6c8ebf', '#b67b4d', '#5f9b6b', '#9d6aa8', '#b35656', '#4f8f95', '#8c7a52',
    '#9070b2', '#4f7f5b', '#bf6f91', '#7d8ab5', '#6d8f43', '#af7b52'
  ];
  const practiceEntries = practiceSeries.map((series, index) => {{
    const points = series.points || [];
    const path = linePath(points, xScale, yScale);
    const lastIndex = points.reduce((memo, value, pointIndex) => (value !== null && Number.isFinite(value) ? pointIndex : memo), -1);
    const lastValue = lastIndex >= 0 ? points[lastIndex] : null;
    const rawTakeoverIndex = fractionalYearIndex(series.takeover_date, years);
    const takeoverIndex = rawTakeoverIndex === null ? null : Math.max(0, Math.min(years.length - 1, rawTakeoverIndex));
    return {{ series, color: palette[index % palette.length], path, lastIndex, lastValue, rawTakeoverIndex, takeoverIndex }};
  }}).filter((entry) => entry.path);
  const availableCodes = new Set(practiceEntries.map((e) => e.series.code));
  if (hoveredTrendPracticeCode && !validTrendCode(hoveredTrendPracticeCode, availableCodes)) hoveredTrendPracticeCode = null;
  if (pinnedTrendPracticeCode && !validTrendCode(pinnedTrendPracticeCode, availableCodes)) pinnedTrendPracticeCode = TREND_DEFAULT_CONTEXT_CODE;
  const activeCode = hoveredTrendPracticeCode || pinnedTrendPracticeCode || TREND_DEFAULT_CONTEXT_CODE;
  const isMeanContext = activeCode === TREND_DEFAULT_CONTEXT_CODE;
  const defaultEntry = defaultTrendReferenceEntry(practiceEntries);
  const displayEntry = isMeanContext
    ? defaultEntry
    : practiceEntries.find((e) => e.series.code === activeCode) || null;
  const emphasisCode = displayEntry?.series.code || null;
  const showAverage = isMeanContext;
  const dimInactive = Boolean(displayEntry);
  const patientOverlay = displayEntry
    ? years
        .map((year, index) => patientVsAveragePoint(year, displayEntry.series.code, index))
        .filter(Boolean)
    : null;
  const overlayValues = patientOverlay ? patientOverlay.map((point) => point.v) : [];
  const overlayMax = overlayAxisMax(overlayValues);
  const overlayTicks = overlayAxisTicks(overlayMax);
  const yScaleRight = patientOverlay?.length
    ? (value) => margin.top + plotHeight - (value / overlayMax) * plotHeight
    : null;
  const patientPoints = patientOverlay ? years.map((_, i) => {{ const p = patientOverlay.find((o) => o.i === i); return p ? p.v : null; }}) : [];
  const patientPath = patientPoints.length && yScaleRight ? linePath(patientPoints, xScale, yScaleRight) : '';
  const pathOpacity = (e) => !dimInactive ? 0.46 : e.series.code === emphasisCode ? 0.96 : 0.12;
  const markerOpacity = (e) => !dimInactive ? 0.26 : e.series.code === emphasisCode ? 0.9 : 0.12;
  const strokeWidth = (e) => e.series.code === emphasisCode ? 2.8 : 1.35;
  const pointRadius = (e) => e.series.code === emphasisCode ? 4.8 : 3.1;
  const practicePaths = practiceEntries.map((entry) => {{
    const finalText = entry.lastValue === null ? '?' : Math.round(entry.lastValue) + '%';
    const titleSuffix = entry.series.takeover_date ? ` Takeover: ${{formatTakeoverDate(entry.series.takeover_date, entry.series.takeover_precision)}}.` : '';
    return `<path d="${{entry.path}}" fill="none" stroke="${{entry.color}}" stroke-width="${{strokeWidth(entry)}}" stroke-linecap="round" stroke-linejoin="round" opacity="${{pathOpacity(entry).toFixed(2)}}"><title>${{entry.series.name}} · latest ${{finalText}}${{titleSuffix}}</title></path>`;
  }}).join('');
  const endMarkers = practiceEntries.filter((e) => e.lastIndex >= 0 && e.lastValue !== null).map((entry) =>
    `<circle cx="${{xScale(entry.lastIndex).toFixed(2)}}" cy="${{yScale(entry.lastValue).toFixed(2)}}" r="${{pointRadius(entry).toFixed(2)}}" fill="${{entry.color}}" opacity="${{Math.max(pathOpacity(entry), 0.24).toFixed(2)}}" stroke="rgba(255,255,255,0.92)" stroke-width="${{entry.series.code === emphasisCode ? '1.8' : '1.1'}}"><title>${{entry.series.name}} latest ${{Math.round(entry.lastValue)}}%</title></circle>`
  ).join('');
  const takeoverMarkers = practiceEntries.map((entry) => {{
    if (entry.takeoverIndex === null) return '';
    const markerX = xScale(entry.takeoverIndex);
    return `<line x1="${{markerX.toFixed(2)}}" y1="${{margin.top}}" x2="${{markerX.toFixed(2)}}" y2="${{height - margin.bottom}}" stroke="${{entry.color}}" stroke-width="${{entry.series.code === emphasisCode ? '2.2' : '1.2'}}" stroke-dasharray="4 4" opacity="${{markerOpacity(entry).toFixed(2)}}"><title>${{entry.series.name}} takeover: ${{formatTakeoverDate(entry.series.takeover_date, entry.series.takeover_precision)}}</title></line>`;
  }}).join('');
  const averagePath = linePath(averageSeries, xScale, yScale);
  const averageFinal = [...averageSeries].reverse().find((v) => v !== null && Number.isFinite(v));
  const averageFinalIndex = averageSeries.reduce((memo, v, i) => (v !== null && Number.isFinite(v) ? i : memo), -1);
  const averageMarker = showAverage && averageFinalIndex >= 0 && averageFinal !== undefined
    ? `<circle cx="${{xScale(averageFinalIndex).toFixed(2)}}" cy="${{yScale(averageFinal).toFixed(2)}}" r="4.5" fill="${{GTD_MEAN_COLOR}}" opacity="${{dimInactive ? '0.74' : '1'}}"></circle><text x="${{Math.min(width - margin.right, xScale(averageFinalIndex) + 8).toFixed(2)}}" y="${{(yScale(averageFinal) - 8).toFixed(2)}}" font-size="11" fill="${{GTD_MEAN_COLOR}}" fill-opacity="${{dimInactive ? '0.74' : '1'}}" font-weight="700">GTD mean ${{Math.round(averageFinal)}}%</text>`
    : '';
  const surveyPatientOverlay = patientPath ? `
    <path d="${{patientPath}}" fill="none" stroke="#4c9a52" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="6 4" opacity="0.88"></path>
    ${{patientOverlay.map((p) => `<circle cx="${{xScale(p.i).toFixed(2)}}" cy="${{yScaleRight(p.v).toFixed(2)}}" r="3.5" fill="#4c9a52" opacity="0.9"><title>Patients: ${{p.raw.toLocaleString()}} (${{p.v.toFixed(0)}}% of GTD yearly average ${{Math.round(p.average).toLocaleString()}})</title></circle>`).join('')}}
    <line x1="${{width - margin.right}}" y1="${{margin.top}}" x2="${{width - margin.right}}" y2="${{height - margin.bottom}}" stroke="rgba(26,28,26,0.25)" />
    ${{overlayTicks.map((tick) => `<text x="${{width - margin.right + 6}}" y="${{yScaleRight(tick) + 4}}" text-anchor="start" font-size="10" fill="rgba(26,28,26,0.6)">${{tick}}%</text>`).join('')}}
  ` : '';
  svg.innerHTML = `
    <rect x="0" y="0" width="${{width}}" height="${{height}}" fill="transparent"></rect>
    ${{yTicks.map((tick) => `<line x1="${{margin.left}}" y1="${{yScale(tick)}}" x2="${{width - margin.right}}" y2="${{yScale(tick)}}" stroke="rgba(26,28,26,0.10)" /><text x="${{margin.left - 8}}" y="${{yScale(tick) + 4}}" text-anchor="end" font-size="11" fill="rgba(26,28,26,0.72)">${{tick}}%</text>`).join('')}}
    ${{years.map((y, i) => `<line x1="${{xScale(i)}}" y1="${{margin.top}}" x2="${{xScale(i)}}" y2="${{height - margin.bottom}}" stroke="rgba(26,28,26,0.08)" /><text x="${{xScale(i)}}" y="${{height - margin.bottom + 18}}" text-anchor="middle" font-size="11" fill="rgba(26,28,26,0.72)">${{y}}</text>`).join('')}}
    <line x1="${{margin.left}}" y1="${{height - margin.bottom}}" x2="${{width - margin.right}}" y2="${{height - margin.bottom}}" stroke="rgba(26,28,26,0.35)" />
    <line x1="${{margin.left}}" y1="${{margin.top}}" x2="${{margin.left}}" y2="${{height - margin.bottom}}" stroke="rgba(26,28,26,0.35)" />
    ${{takeoverMarkers}}
    ${{practicePaths}}
    ${{showAverage ? `<path d="${{averagePath}}" fill="none" stroke="${{GTD_MEAN_COLOR}}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round" opacity="${{dimInactive ? '0.78' : '1'}}"></path>` : ''}}
    ${{averageMarker}}
    ${{endMarkers}}
    ${{surveyPatientOverlay}}
    <text x="${{width / 2}}" y="${{height - 10}}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)">Survey year</text>
    <text x="14" y="${{height / 2}}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)" transform="rotate(-90 14 ${{height / 2}})">Overall experience good %</text>
    ${{patientOverlay?.length ? `<text x="${{width - 14}}" y="${{height / 2}}" text-anchor="middle" font-size="11" fill="rgba(26,28,26,0.6)" transform="rotate(90 ${{width - 14}} ${{height / 2}})">Patients vs GTD avg (%)</text>` : ''}}
  `;
  const defaultLabel = defaultEntry ? `GTD mean + ${{defaultEntry.series.name}}` : 'GTD mean';
  legend.innerHTML = [
    `<button type="button" class="trend-legend-item${{isMeanContext ? ' is-active' : ''}}" data-practice-code="${{TREND_DEFAULT_CONTEXT_CODE}}" aria-pressed="${{isMeanContext ? 'true' : 'false'}}" title="${{defaultLabel}}"><span class="trend-legend-swatch" style="background:${{GTD_MEAN_COLOR}}"></span><span class="trend-legend-body"><span class="trend-legend-name">${{defaultLabel}}</span></span></button>`,
    ...practiceEntries.map((entry) => {{
    const isActive = !isMeanContext && entry.series.code === activeCode;
    return `<button type="button" class="trend-legend-item${{isActive ? ' is-active' : ''}}" data-practice-code="${{entry.series.code}}" aria-pressed="${{isActive}}" title="${{entry.series.name}}"><span class="trend-legend-swatch" style="background:${{entry.color}}"></span><span class="trend-legend-body"><span class="trend-legend-name">${{entry.series.name}}</span></span></button>`;
  }})
  ].join('');
  bindTrendLegendInteractions(legend);
  renderTrendOverlayLegend(overlayLegend, patientPath ? [
    {{ color: '#4c9a52', label: 'Patients vs GTD avg (%)' }},
  ] : []);
  const overlaySummary = patientPath ? ' Green dashed: registered patients as a share of the GTD yearly average, with raw patient counts left in the point labels.' : '';
  const activeSummary = !displayEntry
    ? ' Hover or click a practice in the legend to isolate its track.'
    : isMeanContext
      ? ` Default view shows the GTD mean with ${{displayEntry.series.name}} as the reference track.${{overlaySummary}}`
      : ` Highlighted: ${{displayEntry.series.name}}. Latest ${{displayEntry.lastValue === null ? '?' : Math.round(displayEntry.lastValue) + '%'}}.${{overlaySummary}}`;
  summary.textContent = `${{gtdSurveyTimeseries.practices_with_survey_history}} of ${{gtdSurveyTimeseries.gtd_practice_count}} GTD practices, ${{years.length}} survey years. Thin lines are practice-level overall-good %, dashed lines mark GTD takeover.${{activeSummary}}`;
}}

function renderGtdScoreTrendChart() {{
  const svg = document.getElementById('gtd-score-trend-chart');
  const summary = document.getElementById('gtd-score-trend-summary');
  const legend = document.getElementById('gtd-score-trend-legend');
  const overlayLegend = document.getElementById('gtd-score-trend-overlay-legend');
  const heading = document.getElementById('gtd-trend-heading');
  const note = document.getElementById('gtd-trend-note');
  const useSurvey = activeMetric === 'survey' && gtdSurveyTimeseries.years?.length && gtdSurveyTimeseries.practice_series?.length;
  if (useSurvey) {{
    renderGtdSurveyTrendChart(svg, summary, legend, overlayLegend, heading, note);
    return;
  }}
  if (heading) heading.textContent = `GTD Score Over Time - Showing ${{metricDisplayLabel(activeMetric)}}`;
  if (note) note.textContent = 'Thin lines show each GTD practice\\'s reconstructed cumulative Google rating by month. Faint dashed vertical lines mark the documented GTD takeover date for each practice. Only the first legend entry shows the GTD mean; selecting any named practice hides it. The green dashed line shows registered patients as a percentage of the GTD-wide average patient count for that year, with raw patient counts kept in the point labels, and the orange dashed line shows GP Survey overall-good %. Review dates are approximate month buckets inferred from Google relative-date labels at scrape time.';
  const months = gtdGoogleTimeseries.months || [];
  const practiceSeries = gtdGoogleTimeseries.practice_series || [];
  const averageSeries = gtdGoogleTimeseries.average_series || [];
  if (!months.length || !practiceSeries.length) {{
    svg.innerHTML = '';
    legend.innerHTML = '';
    renderTrendOverlayLegend(overlayLegend, []);
    summary.textContent = `No GTD Google review history is available yet in the current scrape output.`;
    return;
  }}

  const width = 920;
  const height = 360;
  const margin = {{ top: 18, right: 22, bottom: 56, left: 46 }};
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const xScale = (index) => margin.left + (months.length <= 1 ? plotWidth / 2 : (index / (months.length - 1)) * plotWidth);
  const yMin = 1;
  const yMax = 5;
  const yScale = (value) => margin.top + plotHeight - ((value - yMin) / (yMax - yMin)) * plotHeight;
  const yTicks = [1, 2, 3, 4, 5];
  const labelStep = Math.max(1, Math.ceil(months.length / 8));
  const xTickIndexes = months
    .map((_month, index) => index)
    .filter((index) => index % labelStep === 0 || index === months.length - 1);
  const palette = [
    '#6c8ebf', '#b67b4d', '#5f9b6b', '#9d6aa8', '#b35656', '#4f8f95', '#8c7a52',
    '#9070b2', '#4f7f5b', '#bf6f91', '#7d8ab5', '#6d8f43', '#af7b52'
  ];
  const fractionalMonthIndex = (dateIso) => {{
    if (!dateIso) return null;
    const target = new Date(`${{dateIso}}T00:00:00`);
    const first = new Date(`${{months[0]}}T00:00:00`);
    if (Number.isNaN(target.getTime()) || Number.isNaN(first.getTime())) return null;
    const monthDelta = (target.getUTCFullYear() - first.getUTCFullYear()) * 12 + (target.getUTCMonth() - first.getUTCMonth());
    const daysInMonth = new Date(Date.UTC(target.getUTCFullYear(), target.getUTCMonth() + 1, 0)).getUTCDate() || 31;
    const dayFraction = Math.max(0, Math.min(0.999, ((target.getUTCDate() || 1) - 1) / daysInMonth));
    return monthDelta + dayFraction;
  }};
  const practiceEntries = practiceSeries.map((series, index) => {{
    const points = series.points || [];
    const lastIndex = points.reduce((memo, value, pointIndex) => (
      value !== null && Number.isFinite(value) ? pointIndex : memo
    ), -1);
    const lastValue = lastIndex >= 0 ? points[lastIndex] : null;
    const rawTakeoverIndex = fractionalMonthIndex(series.takeover_date);
    const takeoverIndex = rawTakeoverIndex === null
      ? null
      : Math.max(0, Math.min(months.length - 1, rawTakeoverIndex));
    return {{
      series,
      color: palette[index % palette.length],
      path: linePath(points, xScale, yScale),
      lastIndex,
      lastValue,
      rawTakeoverIndex,
      takeoverIndex,
    }};
  }}).filter((entry) => entry.path);
  const availableCodes = new Set(practiceEntries.map((entry) => entry.series.code));
  if (hoveredTrendPracticeCode && !validTrendCode(hoveredTrendPracticeCode, availableCodes)) {{
    hoveredTrendPracticeCode = null;
  }}
  if (pinnedTrendPracticeCode && !validTrendCode(pinnedTrendPracticeCode, availableCodes)) {{
    pinnedTrendPracticeCode = TREND_DEFAULT_CONTEXT_CODE;
  }}
  const activeCode = hoveredTrendPracticeCode || pinnedTrendPracticeCode || TREND_DEFAULT_CONTEXT_CODE;
  const isMeanContext = activeCode === TREND_DEFAULT_CONTEXT_CODE;
  const defaultEntry = defaultTrendReferenceEntry(practiceEntries);
  const activeEntry = isMeanContext
    ? defaultEntry
    : practiceEntries.find((entry) => entry.series.code === activeCode) || null;
  const emphasisCode = activeEntry?.series.code || null;
  const showAverage = isMeanContext;
  const dimInactive = Boolean(activeEntry);

  const monthIndexForYear = (year) => {{
    const prefix = `${{year}}-01`;
    const idx = months.findIndex((m) => String(m).startsWith(prefix));
    return idx >= 0 ? idx : null;
  }};
  const buildOverlaySeries = (code) => {{
    const overlay = {{ google: null, patient: null, survey: null }};
    const surveySeries = (gtdSurveyTimeseries.practice_series || []).find((s) => s.code === code);
    const surveyYears = gtdSurveyTimeseries.years || [];
    const patientByYear = patientCountsByYear || {{}};
    const patientYears = Object.keys(patientByYear).filter((y) => patientByYear[y] && typeof patientByYear[y][code] === 'number').sort((a, b) => a - b);
    overlay.google = practiceSeries.find((s) => s.code === code)?.points || null;
    overlay.patient = patientYears.length
      ? patientYears
          .map((y) => {{
            const i = monthIndexForYear(parseInt(y, 10));
            return i !== null ? patientVsAveragePoint(y, code, i) : null;
          }})
          .filter(Boolean)
      : null;
    overlay.survey = surveySeries && surveyYears.length ? surveyYears.map((y, idx) => {{ const i = monthIndexForYear(parseInt(y, 10)); const v = surveySeries.points?.[idx]; return i !== null && v !== null && Number.isFinite(v) ? {{ i, v, raw: v }} : null; }}).filter(Boolean) : null;
    return overlay;
  }};
  const overlay = activeEntry ? buildOverlaySeries(activeEntry.series.code) : null;
  const hasOverlay = overlay && (overlay.patient?.length || overlay.survey?.length);
  const overlayValues = hasOverlay
    ? [
        ...(overlay.patient || []).map((point) => point.v),
        ...(overlay.survey || []).map((point) => point.v),
      ]
    : [];
  const overlayMax = overlayAxisMax(overlayValues);
  const overlayTicks = overlayAxisTicks(overlayMax);
  const yScaleRight = hasOverlay ? (v) => margin.top + plotHeight - (v / overlayMax) * plotHeight : null;
  const pathOpacity = (entry) => !dimInactive ? 0.46 : entry.series.code === activeEntry?.series.code ? 0.96 : 0.12;
  const markerOpacity = (entry) => !dimInactive ? 0.26 : entry.series.code === activeEntry?.series.code ? 0.9 : 0.12;
  const strokeWidth = (entry) => entry.series.code === emphasisCode ? 2.8 : 1.35;
  const pointRadius = (entry) => entry.series.code === emphasisCode ? 4.8 : 3.1;
  const overlayPath = (points, yS) => {{
    if (!points?.length || !yS) return '';
    let path = '';
    points.forEach(({{ i, v }}) => {{
      const cmd = path ? 'L' : 'M';
      path += `${{cmd}}${{xScale(i).toFixed(2)}} ${{yS(v).toFixed(2)}} `;
    }});
    return path.trim();
  }};
  const practicePaths = practiceEntries.map((entry) => {{
    const finalText = entry.lastValue === null ? '?' : entry.lastValue.toFixed(2);
    const titleSuffix = entry.series.takeover_date
      ? ` Takeover: ${{formatTakeoverDate(entry.series.takeover_date, entry.series.takeover_precision)}}.`
      : '';
    return `
      <path d="${{entry.path}}" fill="none" stroke="${{entry.color}}" stroke-width="${{strokeWidth(entry)}}" stroke-linecap="round" stroke-linejoin="round" opacity="${{pathOpacity(entry).toFixed(2)}}">
        <title>${{entry.series.name}} · latest reconstructed average ${{finalText}} from ${{entry.series.parsed_review_count || 0}} parsed reviews.${{titleSuffix}}</title>
      </path>
    `;
  }}).join('');
  const endMarkers = practiceEntries
    .filter((entry) => entry.lastIndex >= 0 && entry.lastValue !== null)
    .map((entry) => `
      <circle cx="${{xScale(entry.lastIndex).toFixed(2)}}" cy="${{yScale(entry.lastValue).toFixed(2)}}" r="${{pointRadius(entry).toFixed(2)}}" fill="${{entry.color}}" opacity="${{Math.max(pathOpacity(entry), 0.24).toFixed(2)}}" stroke="rgba(255,255,255,0.92)" stroke-width="${{entry.series.code === emphasisCode ? '1.8' : '1.1'}}">
        <title>${{entry.series.name}} latest reconstructed rating: ${{entry.lastValue.toFixed(2)}}</title>
      </circle>
    `).join('');
  const takeoverMarkers = practiceEntries.map((entry) => {{
    if (entry.takeoverIndex === null) return '';
    const markerX = xScale(entry.takeoverIndex);
    const timingNote = entry.rawTakeoverIndex < 0
      ? 'Takeover predates the visible review timeline'
      : entry.rawTakeoverIndex > months.length - 1
        ? 'Takeover is after the visible review timeline'
        : 'Takeover within the visible review timeline';
    return `
      <line x1="${{markerX.toFixed(2)}}" y1="${{margin.top}}" x2="${{markerX.toFixed(2)}}" y2="${{height - margin.bottom}}" stroke="${{entry.color}}" stroke-width="${{entry.series.code === emphasisCode ? '2.2' : '1.2'}}" stroke-dasharray="4 4" opacity="${{markerOpacity(entry).toFixed(2)}}">
        <title>${{entry.series.name}} takeover: ${{formatTakeoverDate(entry.series.takeover_date, entry.series.takeover_precision)}}. ${{timingNote}}. ${{entry.series.takeover_note || entry.series.takeover_source_label || 'Official GTD takeover source'}}</title>
      </line>
    `;
  }}).join('');
  const activeTakeoverMarkup = activeEntry && activeEntry.takeoverIndex !== null
    ? (() => {{
        const label = `Takeover ${{formatTakeoverDate(activeEntry.series.takeover_date, activeEntry.series.takeover_precision)}}`;
        const markerX = xScale(activeEntry.takeoverIndex);
        const labelX = Math.max(margin.left + 78, Math.min(width - margin.right - 78, markerX));
        return `
          <rect x="${{(labelX - 78).toFixed(2)}}" y="${{(margin.top + 6).toFixed(2)}}" width="156" height="22" rx="11" fill="rgba(255,255,255,0.90)" stroke="${{activeEntry.color}}" stroke-opacity="0.45"></rect>
          <text x="${{labelX.toFixed(2)}}" y="${{(margin.top + 21).toFixed(2)}}" text-anchor="middle" font-size="11" font-weight="700" fill="${{activeEntry.color}}">${{label}}</text>
        `;
      }})()
    : '';

  const averagePath = linePath(averageSeries, xScale, yScale);
  const averageFinal = [...averageSeries].reverse().find((value) => value !== null && Number.isFinite(value));
  const averageFinalIndex = averageSeries.reduce((lastIndex, value, index) => (value !== null && Number.isFinite(value) ? index : lastIndex), -1);
  const averageMarker = showAverage && averageFinalIndex >= 0 && averageFinal !== undefined
    ? `
      <circle cx="${{xScale(averageFinalIndex).toFixed(2)}}" cy="${{yScale(averageFinal).toFixed(2)}}" r="4.5" fill="${{GTD_MEAN_COLOR}}" opacity="${{dimInactive ? '0.74' : '1'}}"></circle>
      <text x="${{Math.min(width - margin.right, xScale(averageFinalIndex) + 8).toFixed(2)}}" y="${{(yScale(averageFinal) - 8).toFixed(2)}}" font-size="11" fill="${{GTD_MEAN_COLOR}}" fill-opacity="${{dimInactive ? '0.74' : '1'}}" font-weight="700">GTD mean ${{averageFinal.toFixed(2)}}</text>
    `
    : '';

  const overlayMarkup = hasOverlay && yScaleRight ? `
    ${{overlay.patient?.length ? `<path d="${{overlayPath(overlay.patient, yScaleRight)}}" fill="none" stroke="#4c9a52" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="6 4" opacity="0.88"></path>${{overlay.patient.map((p) => `<circle cx="${{xScale(p.i).toFixed(2)}}" cy="${{yScaleRight(p.v).toFixed(2)}}" r="3.5" fill="#4c9a52" opacity="0.9"><title>Patients: ${{p.raw.toLocaleString()}} (${{p.v.toFixed(0)}}% of GTD yearly average ${{Math.round(p.average).toLocaleString()}})</title></circle>`).join('')}}` : ''}}
    ${{overlay.survey?.length ? `<path d="${{overlayPath(overlay.survey, yScaleRight)}}" fill="none" stroke="#b67b4d" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="2 4" opacity="0.88"></path>${{overlay.survey.map((p) => `<circle cx="${{xScale(p.i).toFixed(2)}}" cy="${{yScaleRight(p.v).toFixed(2)}}" r="3.5" fill="#b67b4d" opacity="0.9"><title>Survey good: ${{Math.round(p.raw)}}%</title></circle>`).join('')}}` : ''}}
    <line x1="${{width - margin.right}}" y1="${{margin.top}}" x2="${{width - margin.right}}" y2="${{height - margin.bottom}}" stroke="rgba(26,28,26,0.25)" />
    ${{overlayTicks.map((t) => `<text x="${{width - margin.right + 6}}" y="${{yScaleRight(t) + 4}}" text-anchor="start" font-size="10" fill="rgba(26,28,26,0.6)">${{t}}%</text>`).join('')}}
  ` : '';
  svg.innerHTML = `
    <rect x="0" y="0" width="${{width}}" height="${{height}}" fill="transparent"></rect>
    ${{yTicks.map((tick) => `
      <line x1="${{margin.left}}" y1="${{yScale(tick)}}" x2="${{width - margin.right}}" y2="${{yScale(tick)}}" stroke="rgba(26,28,26,0.10)" />
      <text x="${{margin.left - 8}}" y="${{yScale(tick) + 4}}" text-anchor="end" font-size="11" fill="rgba(26,28,26,0.72)">${{tick.toFixed(1)}}</text>
    `).join('')}}
    ${{xTickIndexes.map((index) => `
      <line x1="${{xScale(index)}}" y1="${{margin.top}}" x2="${{xScale(index)}}" y2="${{height - margin.bottom}}" stroke="rgba(26,28,26,0.08)" />
      <text x="${{xScale(index)}}" y="${{height - margin.bottom + 18}}" text-anchor="middle" font-size="11" fill="rgba(26,28,26,0.72)">${{formatMonthLabel(months[index])}}</text>
    `).join('')}}
    <line x1="${{margin.left}}" y1="${{height - margin.bottom}}" x2="${{width - margin.right}}" y2="${{height - margin.bottom}}" stroke="rgba(26,28,26,0.35)" />
    <line x1="${{margin.left}}" y1="${{margin.top}}" x2="${{margin.left}}" y2="${{height - margin.bottom}}" stroke="rgba(26,28,26,0.35)" />
    ${{takeoverMarkers}}
    ${{practicePaths}}
    ${{showAverage ? `<path d="${{averagePath}}" fill="none" stroke="${{GTD_MEAN_COLOR}}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round" opacity="${{dimInactive ? '0.78' : '1'}}"></path>` : ''}}
    ${{averageMarker}}
    ${{endMarkers}}
    ${{activeTakeoverMarkup}}
    ${{overlayMarkup}}
    <text x="${{width / 2}}" y="${{height - 10}}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)">Approximate review month</text>
    <text x="14" y="${{height / 2}}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)" transform="rotate(-90 14 ${{height / 2}})">Reconstructed cumulative Google rating</text>
    ${{hasOverlay ? `<text x="${{width - 14}}" y="${{height / 2}}" text-anchor="middle" font-size="11" fill="rgba(26,28,26,0.6)" transform="rotate(90 ${{width - 14}} ${{height / 2}})">Patients vs GTD avg (%) · Survey %</text>` : ''}}
  `;
  const defaultLabel = defaultEntry ? `GTD mean + ${{defaultEntry.series.name}}` : 'GTD mean';
  legend.innerHTML = [
    `
      <button
        type="button"
        class="trend-legend-item${{isMeanContext ? ' is-active' : ''}}"
        data-practice-code="${{TREND_DEFAULT_CONTEXT_CODE}}"
        aria-pressed="${{isMeanContext ? 'true' : 'false'}}"
        title="${{defaultLabel}}"
      >
        <span class="trend-legend-swatch" style="background:${{GTD_MEAN_COLOR}}"></span>
        <span class="trend-legend-body">
          <span class="trend-legend-name">${{defaultLabel}}</span>
        </span>
      </button>
    `,
    ...practiceEntries.map((entry) => {{
    const isActive = !isMeanContext && entry.series.code === activeCode;
    return `
      <button
        type="button"
        class="trend-legend-item${{isActive ? ' is-active' : ''}}"
        data-practice-code="${{entry.series.code}}"
        aria-pressed="${{isActive ? 'true' : 'false'}}"
        title="${{entry.series.name}}"
      >
        <span class="trend-legend-swatch" style="background:${{entry.color}}"></span>
        <span class="trend-legend-body">
          <span class="trend-legend-name">${{entry.series.name}}</span>
        </span>
      </button>
    `;
  }})
  ].join('');
  bindTrendLegendInteractions(legend);
  renderTrendOverlayLegend(overlayLegend, hasOverlay ? [
    ...(overlay.patient?.length ? [{{ color: '#4c9a52', label: 'Patients vs GTD avg (%)' }}] : []),
    ...(overlay.survey?.length ? [{{ color: '#b67b4d', label: 'GP Survey good %' }}] : []),
  ] : []);

  const missingPractices = (gtdGoogleTimeseries.missing_practices || []).map((item) => item.name).filter(Boolean);
  const missingSuffix = missingPractices.length
    ? ` ${{missingPractices.length}} GTD practice${{missingPractices.length === 1 ? '' : 's'}} still have no usable dated review history in the scrape: ${{missingPractices.join(', ')}}.`
    : '';
  const overlaySummary = hasOverlay
    ? ' Green dashed: registered patients as a share of the GTD yearly average, with raw patient counts left in the point labels. Orange dashed: GP Survey good %.'
    : '';
  const activeSummary = !activeEntry
    ? ' Hover or click a practice in the side legend to isolate its track and takeover marker.'
    : isMeanContext
      ? ` Default view shows the GTD mean with ${{activeEntry.series.name}} as the reference track.${{overlaySummary}}`
      : ` Highlighted: ${{activeEntry.series.name}}. Latest reconstructed score is ${{activeEntry.lastValue === null ? '?' : activeEntry.lastValue.toFixed(2)}}${{activeEntry.series.takeover_date ? `, with GTD takeover on ${{formatTakeoverDate(activeEntry.series.takeover_date, activeEntry.series.takeover_precision)}}.` : '.'}}${{overlaySummary}}`;
  summary.textContent =
    `${{gtdGoogleTimeseries.practices_with_review_history}} of ${{gtdGoogleTimeseries.gtd_practice_count}} GTD practices contribute to this chart, based on ${{gtdGoogleTimeseries.parsed_review_count}} parsed Google review dates and ratings. Thin lines are practice-level reconstructed cumulative averages, dashed vertical lines mark documented GTD takeover dates, and the bold line is the mean of available practice trajectories. Relative dates are anchored to the scrape file timestamp ${{gtdGoogleTimeseries.anchor_date}}.${{activeSummary}}${{missingSuffix}}`;
}}

function rerenderAll() {{
  renderMetricLegend();
  updateAreaOverlayControls();
  renderManagementList();
  clearOverlayLayers();
  renderMarkers();
  renderNationalSupplementals();
  renderCityCircles();
  renderSampleCircle();
  updateSampleCircleControls();
  if (activeAreaOverlay === 'population') {{
    renderVoronoi();
  }} else if (activeAreaOverlay === 'deprivation') {{
    renderDeprivation();
  }}
  renderGtdScoreTrendChart();
  renderScatterplot();
  renderDeprivationChart();
  renderNationalDeprivationChart();
  renderPatientChangeChart();
  renderPatientTreemap();
  renderPlaceBenchmarks();
  renderServiceFinder();
  renderRatingVsSurveyChart();
  renderComparisons();
}}

document.querySelectorAll('input[name="score-source"]').forEach((input) => {{
  input.addEventListener('change', (event) => {{
    activeMetric = event.target.value;
    rerenderAll();
  }});
}});

document.getElementById('normalize-gap-toggle').addEventListener('change', (event) => {{
  activeGapMode = event.target.checked ? 'normalized' : 'absolute';
  rerenderAll();
}});

document.querySelectorAll('input[name="completion-scope"]').forEach((input) => {{
  input.addEventListener('click', (event) => {{
    if (event.target.value !== 'national') return;
    if (completionScatterScope !== 'national') return;
    completionScatterNationIndex = (completionScatterNationIndex + 1) % completionScatterNationOrder.length;
    updateCompletionScopeControl();
    renderScatterplot();
  }});
  input.addEventListener('change', (event) => {{
    const previousScope = completionScatterScope;
    completionScatterScope = event.target.value;
    if (completionScatterScope === 'national') {{
      if (previousScope !== 'national') completionScatterNationIndex = 0;
      updateCompletionScopeControl();
    }}
    renderScatterplot();
  }});
}});

document.querySelectorAll('input[name="rating-survey-mode"]').forEach((input) => {{
  input.addEventListener('change', (event) => {{
    ratingSurveyMode = event.target.value;
    renderRatingVsSurveyChart();
  }});
}});

document.getElementById('voronoi-toggle').addEventListener('change', (event) => {{
  activeAreaOverlay = event.target.checked ? 'population' : null;
  rerenderAll();
}});

document.getElementById('deprivation-toggle').addEventListener('change', (event) => {{
  activeAreaOverlay = event.target.checked ? 'deprivation' : null;
  rerenderAll();
}});

let resizeTimer = null;
window.addEventListener('resize', () => {{
  if (resizeTimer) clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {{
    updateStickyScoreControl();
    renderScatterplot();
    renderDeprivationChart();
    renderNationalDeprivationChart();
    renderPatientChangeChart();
    renderPatientTreemap();
    renderRatingVsSurveyChart();
  }}, 120);
}});

document.getElementById('patient-treemap-play').addEventListener('click', () => {{
  if (patientTreemapPlaying) {{
    stopPatientTreemapPlayback();
  }} else {{
    startPatientTreemapPlayback();
  }}
  renderPatientTreemap();
}});

document.getElementById('patient-treemap-year').addEventListener('input', (event) => {{
  stopPatientTreemapPlayback();
  patientTreemapYearIndex = Number(event.target.value);
  renderPatientTreemap();
}});

document.getElementById('normalize-patient-change-toggle').addEventListener('change', (event) => {{
  patientTreemapNormalizeForChange = event.target.checked;
  renderPatientChangeChart();
  renderPatientTreemap();
}});

document.getElementById('national-deprivation-population-toggle').addEventListener('change', (event) => {{
  nationalDeprivationUsePopulation = event.target.checked;
  renderNationalDeprivationChart();
}});

document.getElementById('city-circles-toggle').addEventListener('change', (event) => {{
  showCityCircles = event.target.checked;
  renderCityCircles();
  updateSampleCircleControls();
}});

document.getElementById('sample-circle-button').addEventListener('click', () => {{
  serviceFinderArmed = false;
  sampleCircleArmed = !sampleCircleArmed;
  renderServiceFinder();
  updateSampleCircleControls();
}});

document.getElementById('clear-sample-circle-button').addEventListener('click', () => {{
  sampleCircleCenter = null;
  sampleCircleArmed = false;
  renderSampleCircle();
  renderPlaceBenchmarks();
  updateSampleCircleControls();
}});

document.getElementById('sample-circle-radius').addEventListener('input', (event) => {{
  sampleCircleRadiusMiles = Number(event.target.value);
  renderSampleCircle();
  renderPlaceBenchmarks();
  updateSampleCircleControls();
}});

function toggleServiceFinderArmed() {{
  sampleCircleArmed = false;
  serviceFinderArmed = !serviceFinderArmed;
  clearServiceFinderButtonFlash();
  updateSampleCircleControls();
  renderServiceFinder();
}}

function bindServiceFinderDrag(buttonId) {{
  const button = document.getElementById(buttonId);
  if (!button) return;
  button.addEventListener('dragstart', (event) => {{
    event.preventDefault();
  }});
  button.addEventListener('pointerdown', (event) => {{
    if (event.button !== undefined && event.button !== 0) return;
    const startX = Number(event.clientX);
    const startY = Number(event.clientY);
    let dragging = false;
    const pointerId = event.pointerId;

    const cleanup = () => {{
      window.removeEventListener('pointermove', handleMove, true);
      window.removeEventListener('pointerup', handleUp, true);
      window.removeEventListener('pointercancel', handleCancel, true);
      serviceFinderDragActive = false;
      removeServiceFinderDragGhost();
      renderServiceFinder();
    }};

    const handleMove = (moveEvent) => {{
      if (moveEvent.pointerId !== pointerId) return;
      const distance = Math.hypot(Number(moveEvent.clientX) - startX, Number(moveEvent.clientY) - startY);
      if (!dragging && distance < 8) return;
      if (!dragging) {{
        dragging = true;
        sampleCircleArmed = false;
        serviceFinderArmed = false;
        clearServiceFinderButtonFlash();
        serviceFinderDragActive = true;
      }}
      updateServiceFinderDragGhost(Number(moveEvent.clientX), Number(moveEvent.clientY));
      renderServiceFinder();
      moveEvent.preventDefault();
    }};

    const handleUp = (upEvent) => {{
      if (upEvent.pointerId !== pointerId) return;
      if (!dragging) {{
        cleanup();
        toggleServiceFinderArmed();
        return;
      }}
      const latlng = mapLatLngFromClientPoint(Number(upEvent.clientX), Number(upEvent.clientY));
      cleanup();
      if (latlng) {{
        setServiceFinderPoint(latlng.lat, latlng.lng, 'Dropped pin');
      }}
    }};

    const handleCancel = (cancelEvent) => {{
      if (cancelEvent.pointerId !== pointerId) return;
      cleanup();
    }};

    window.addEventListener('pointermove', handleMove, true);
    window.addEventListener('pointerup', handleUp, true);
    window.addEventListener('pointercancel', handleCancel, true);
  }});
}}

bindServiceFinderDrag('service-finder-place-button');
bindServiceFinderDrag('service-finder-map-button');

document.querySelectorAll('[data-service-finder-sort]').forEach((button) => {{
  button.addEventListener('click', () => {{
    const sortKey = String(button.getAttribute('data-service-finder-sort') || '').trim();
    if (!sortKey) return;
    if (serviceFinderSortKey === sortKey) {{
      serviceFinderSortDirection = serviceFinderSortDirection === 'asc' ? 'desc' : 'asc';
    }} else {{
      serviceFinderSortKey = sortKey;
      serviceFinderSortDirection = serviceFinderDefaultDirection(sortKey);
    }}
    renderServiceFinder();
  }});
}});

document.getElementById('service-finder-clear-button').addEventListener('click', () => {{
  clearServiceFinderPoint();
}});

document.getElementById('service-finder-locate-button').addEventListener('click', () => {{
  if (!navigator.geolocation) {{
    serviceFinderArmed = false;
    serviceFinderEmptyMessage = 'Browser geolocation is not available here.';
    renderServiceFinder();
    return;
  }}
  navigator.geolocation.getCurrentPosition(
    (position) => {{
      const lat = Number(position.coords.latitude);
      const lon = Number(position.coords.longitude);
      setServiceFinderPoint(lat, lon, 'Browser location');
      map.flyTo([lat, lon], Math.max(map.getZoom(), 12), {{ duration: 0.65 }});
    }},
    () => {{
      serviceFinderArmed = false;
      serviceFinderEmptyMessage = 'Browser geolocation was unavailable or permission was denied.';
      renderServiceFinder();
    }},
    {{
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 300000,
    }}
  );
}});

const scoreSourceControl = document.getElementById('score-source-control');
const scoreSourceSpacer = document.getElementById('score-source-control-spacer');
const legendContainer = document.querySelector('.legend');

function updateStickyScoreControl() {{
  if (!scoreSourceControl || !scoreSourceSpacer) return;
  const isPrint = window.matchMedia && window.matchMedia('print').matches;
  if (isPrint) {{
    scoreSourceControl.classList.remove('is-fixed');
    scoreSourceSpacer.hidden = true;
    scoreSourceSpacer.style.height = '';
    scoreSourceControl.style.removeProperty('--sticky-left');
    scoreSourceControl.style.removeProperty('--sticky-width');
    return;
  }}

  const anchorRect = (scoreSourceControl.classList.contains('is-fixed') ? scoreSourceSpacer : scoreSourceControl).getBoundingClientRect();
  const rect = scoreSourceControl.getBoundingClientRect();
  const shouldFix = anchorRect.top < 0;

  if (!shouldFix) {{
    scoreSourceControl.classList.remove('is-fixed');
    scoreSourceSpacer.hidden = true;
    scoreSourceSpacer.style.height = '';
    scoreSourceControl.style.removeProperty('--sticky-left');
    scoreSourceControl.style.removeProperty('--sticky-width');
    return;
  }}

  const spacerHeight = scoreSourceControl.offsetHeight;
  scoreSourceSpacer.hidden = false;
  scoreSourceSpacer.style.height = `${{spacerHeight}}px`;
  scoreSourceControl.style.setProperty('--sticky-left', `${{rect.left}}px`);
  scoreSourceControl.style.setProperty('--sticky-width', `${{rect.width}}px`);
  scoreSourceControl.classList.add('is-fixed');
}}

window.addEventListener('scroll', updateStickyScoreControl, {{ passive: true }});
legendContainer?.addEventListener('scroll', updateStickyScoreControl, {{ passive: true }});

document.getElementById('legend-collapse').addEventListener('click', () => {{
  sidebarCollapsed = !sidebarCollapsed;
  updateSidebarState();
  updateStickyScoreControl();
  try {{
    localStorage.setItem(SIDEBAR_COLLAPSE_KEY, sidebarCollapsed ? '1' : '0');
  }} catch (_error) {{
  }}
}});

map.on('moveend', () => {{
  renderNationalSupplementals();
  updateHoveredCatchmentOutline();
  if (activeAreaOverlay === 'population') {{
    if (voronoiLayer) {{
      map.removeLayer(voronoiLayer);
      voronoiLayer = null;
    }}
    renderVoronoi();
  }}
}});

map.on('zoomend', () => {{
  updateHoveredCatchmentOutline();
}});

map.on('click', (event) => {{
  if (serviceFinderArmed) {{
    setServiceFinderPoint(event.latlng.lat, event.latlng.lng, 'Dropped pin');
    return;
  }}
  if (!sampleCircleArmed) return;
  sampleCircleCenter = {{
    lat: Number(event.latlng.lat),
    lon: Number(event.latlng.lng),
  }};
  sampleCircleArmed = false;
  renderSampleCircle();
  renderPlaceBenchmarks();
  updateSampleCircleControls();
}});

try {{
  sidebarCollapsed = localStorage.getItem(SIDEBAR_COLLAPSE_KEY) === '1';
}} catch (_error) {{
  sidebarCollapsed = false;
}}
updateSidebarState();
if (document.readyState === 'complete') {{
  preloadManchesterCatchments();
}} else {{
  window.addEventListener('load', preloadManchesterCatchments, {{ once: true }});
}}
rerenderAll();
updateStickyScoreControl();
</script>
</body>
</html>
"""
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
