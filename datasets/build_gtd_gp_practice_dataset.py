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
from calendar import monthrange
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any
from urllib.parse import quote, urlencode


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output" / "gtd-greater-manchester-gp-practice-reviews-2026-03-09"
GP_PATIENT_SURVEY_RAW_DIR = BASE_DIR / "raw" / "gp_patient_survey"
GOOGLE_REVIEW_RESULTS_JSON = OUTPUT_DIR / "google_maps_recent_reviews.json"
GTD_TAKEOVER_METADATA_JSON = BASE_DIR / "config" / "gtd_takeover_dates.json"
GP_PATIENT_SURVEY_BRANCH_PARENT_JSON = BASE_DIR / "config" / "gp_patient_survey_branch_parent_codes.json"
PATIENT_COUNTS_BY_YEAR_JSON = BASE_DIR / "raw" / "registered_patients" / "patient_counts_by_year.json"
DEPRIVATION_SUBSET_GEOJSON = BASE_DIR / "deprivation" / "output" / "catchment_lsoa_imd_2025.geojson"

from deprivation.practice_deprivation_lookup import write_practice_deprivation_lookup
RADIUS_MILES = 5.0
RADIUS_METERS = 8046.72
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


def load_gtd_gpps_timeseries() -> dict[str, Any]:
    """Load GPPS historical subset for GTD practices (from extract script output)."""
    p = OUTPUT_DIR / "gtd_gpps_timeseries.json"
    if not p.exists():
        return {"years": [], "practice_series": [], "average_series": [], "gtd_practice_count": 0, "practices_with_survey_history": 0}
    return json.loads(p.read_text(encoding="utf-8"))


def build_patient_change_analysis(
    markers: list[dict[str, Any]],
    patient_counts_by_year: dict[str, dict[str, int]],
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

    return {
        "years": years,
        "dataset_average_by_year": dataset_average_by_year,
        "practice_count": len(practice_series),
        "practice_series": practice_series,
        "average_series": average_series,
    }


def write_map(path: Path, rows: list[dict[str, Any]]) -> None:
    rows = apply_gtd_takeover_metadata(rows)
    survey_by_code = load_gp_patient_survey_index()
    survey_branch_parent_by_code = load_gp_patient_survey_branch_parent_index()
    gtd_google_timeseries = build_gtd_google_score_timeseries(rows)
    gtd_survey_timeseries = load_gtd_gpps_timeseries()
    patient_counts_by_year = load_registered_patient_timeseries() or {}
    deprivation_geojson = load_deprivation_subset_geojson()
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
    for row in rows:
        survey_payload, survey_code_used, survey_resolution_note = resolve_gp_patient_survey_payload(
            str(row["canonical_code"]),
            survey_by_code,
            survey_branch_parent_by_code,
        )
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
                "gtd": row["gtd_managed"],
                "management_company": row.get("management_company_name", "") or ("GTD Healthcare" if row["gtd_managed"] else ""),
                "affiliated_group": row.get("affiliated_group_name", ""),
                "google_score": row["google_review_score"],
                "google_count": row["google_review_count"],
                "google_source_note": row.get("google_review_source_note", ""),
                "google_text_file": row.get("google_review_text_file", ""),
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
                "gp_patient_survey_2025_url": survey_payload.get("gpps_url", ""),
                "gp_patient_survey_code_used": survey_code_used,
                "gp_patient_survey_resolution_note": survey_resolution_note,
                "registered_patient_count": row.get("registered_patient_count", ""),
            }
        )

    patient_change_analysis = build_patient_change_analysis(markers, patient_counts_by_year)

    center_lat = sum(row["latitude"] for row in rows) / len(rows)
    center_lon = sum(row["longitude"] for row in rows) / len(rows)
    map_html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Manchester GPs' Reviews</title>
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
.map-stage.is-collapsed .overlay-toggle-label {{
  justify-content: center;
  padding-inline: 0;
}}
.map-stage.is-collapsed .overlay-toggle-label > span {{
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
  height: 92px;
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
  .treemap-mode-control .check-toggle {{
    width: 100%;
    justify-content: space-between;
  }}
  .panel-heading-row {{
    flex-direction: column;
    align-items: stretch;
  }}
  .legend {{
    border-right: 0;
    border-top: 1px solid var(--line);
    box-shadow: none;
  }}
}}
@media print {{
  * {{
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}
  body {{
    background: #fff;
  }}
  .page {{
    display: block;
  }}
  .map-stage {{
    grid-template-areas: "legend map";
    grid-template-columns: 280px minmax(0, 1fr);
    min-height: auto;
    break-inside: avoid-page;
  }}
  #map {{
    height: 170mm;
    min-height: 170mm;
  }}
  .legend {{
    border: 1px solid var(--line);
    border-right: 0;
    box-shadow: none;
  }}
  #score-source-control.is-fixed {{ position: static; width: auto; box-shadow: none; }}
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
        <h1>Manchester GPs' Reviews</h1>
        <p>{len(rows)} GP surgeries profiled.</p>
        <p>{total_registered_patients:,} patients across {registered_patient_rows} practices.</p>
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
        <p id="area-overlay-tip" class="hint"></p>
      </div>
      <div class="management-group">
        <h2>Management</h2>
        <p id="manager-hint" class="hint"></p>
        <div id="manager-list" class="manager-list"></div>
      </div>
    </div>
    <div id="map"></div>
  </div>
  <div class="insights">
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
      <h2 id="scatter-heading">Completion Rate vs Score</h2>
      <p id="scatter-summary" class="hint"></p>
      <div class="chart-frame">
        <svg id="scatterplot" viewBox="0 0 920 320" preserveAspectRatio="xMidYMid meet" aria-labelledby="scatter-title" role="img">
          <title id="scatter-title">Survey completion rate against selected score</title>
        </svg>
      </div>
      <p class="chart-note">Y-axis is GP Patient Survey completion rate. X-axis changes with the selected score source.</p>
    </section>
    <section class="panel comparison-panel">
      <h2 id="deprivation-heading">Score vs Deprivation</h2>
      <p id="deprivation-summary" class="hint"></p>
      <div class="chart-frame">
        <svg id="deprivation-chart" viewBox="0 0 920 320" preserveAspectRatio="xMidYMid meet" aria-labelledby="deprivation-title" role="img">
          <title id="deprivation-title">Selected score against area deprivation decile</title>
        </svg>
      </div>
      <p class="chart-note">X-axis is IMD 2025 decile (1 = most deprived). Y-axis changes with the selected score source, including the signed survey/Google gap.</p>
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
    </section>
    <section class="panel comparison-panel">
      <div class="panel-heading-row">
        <h2 id="patient-treemap-heading">Patient Count Treemap</h2>
        <div class="treemap-mode-control">
          <label class="overlay-toggle-label check-toggle" title="Flatten whole-dataset growth so the treemap shows how each practice's share of the Manchester patient pool changes over time, rather than absolute patient-count growth.">
            <input type="checkbox" id="normalize-patient-change-toggle">
            <span>Flatten Global</span>
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
        <svg id="patient-total-chart" viewBox="0 0 920 92" preserveAspectRatio="xMidYMid meet" aria-labelledby="patient-total-title" role="img">
          <title id="patient-total-title">Total registered patients across the full dataset over time</title>
        </svg>
      </div>
      <p class="chart-note">This uses a fixed-scale grouped strip-treemap rather than re-squarifying each frame, so practice blocks mostly grow and shrink in place. Block area is registered patients in the chosen year, on the same patient-to-pixel scale for all years; colour and score label use the currently selected metric. Independent / other is split into Google review-score bands so better and worse destinations can be compared. The small strip-chart below shows the whole-dataset registered-patient total over the same years.</p>
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
  </div>
</div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@turf/turf@7.2.0/turf.min.js"></script>
<script>
const rows = {json.dumps(markers)};
const gtdGoogleTimeseries = {json.dumps(gtd_google_timeseries)};
const gtdSurveyTimeseries = {json.dumps(gtd_survey_timeseries)};
const patientCountsByYear = {json.dumps(patient_counts_by_year)};
const patientChangeAnalysis = {json.dumps(patient_change_analysis)};
const knownManagementCompanies = {json.dumps(known_management_companies)};
const deprivationGeojson = {json.dumps(deprivation_geojson, separators=(",", ":"))};
const practiceDeprivationLookup = {json.dumps(practice_deprivation, separators=(",", ":"))};
const rowsByCode = new Map(rows.map((row) => [row.code, row]));
const NEW_BANK_CODE = 'Y02960';
const BASELINE_MANAGEMENT_COMPANY = 'GTD Healthcare';
const TREND_DEFAULT_CONTEXT_CODE = '__gtd_mean_with_new_bank__';
const LOCAL_RADIUS_MILES = 2.5;
const SIDEBAR_COLLAPSE_KEY = 'mapSidebarCollapsed';
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
let voronoiLayer = null;
let deprivationLayer = null;
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
let sidebarCollapsed = false;
let patientTreemapYearIndex = null;
let patientTreemapPlaying = false;
let patientTreemapTimer = null;
let patientTreemapNormalizeForChange = true;

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
      const count = numericOrNull(row.survey_sent_back);
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
      const survey = numericOrNull(row.survey_sent_back);
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
  const surveySentBack = numericOrNull(row.survey_sent_back);
  if (google === null || surveyPercent === null) return null;
  if (googleCount === null || googleCount <= 0) return null;
  if (surveySentBack === null || surveySentBack <= 0) return null;
  return {{
    google,
    surveyPercent,
    surveyStars: surveyPercent / 20,
  }};
}}

const gapNormalisationStats = (() => {{
  const inputs = rows.map((row) => gapInputs(row)).filter(Boolean);
  const rawGapValues = inputs.map((entry) => entry.google - entry.surveyStars);
  return {{
    rawGapMean: mean(rawGapValues),
    rawGapStd: standardDeviation(rawGapValues),
  }};
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
  const rawGapStd = gapNormalisationStats.rawGapStd;
  if (!rawGapStd) return null;
  const rawGap = inputs.google - inputs.surveyStars;
  const gap = (rawGap - gapNormalisationStats.rawGapMean) / rawGapStd;
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
    label: 'Normalised Google-minus-survey gap (z-score, positive = Google higher)',
    min: -roundedMax,
    max: roundedMax,
    magnitudeLabel: 'Survey/Google gap magnitude (abs, normalised z-score)',
    magnitudeTicks: ticks,
  }};
}}

function gapDescription() {{
  if (activeGapMode === 'normalized') {{
    return 'Normalised mode: the raw Google-minus-survey gap is converted to a cohort z-score, so positive means Google is higher than survey by more than is typical on this map.';
  }}
  return 'Indicator only: survey overall-good % is scaled to 0-5 and compared with Google; positive means Google is higher than the survey-equivalent score, negative means lower.';
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

function markerSvg(shape, color, label, fontSize, missing) {{
  const stroke = 'rgba(0,0,0,0.28)';
  const textColor = missing ? '#f4f4f4' : '#ffffff';
  if (shape === 'triangle') {{
    return `
      <svg class="marker-svg" width="100%" height="100%" viewBox="0 0 42 36" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <polygon points="21,1 41,35 1,35" fill="${{color}}" stroke="${{stroke}}" stroke-width="1.2" />
        <text x="21" y="24" text-anchor="middle" dominant-baseline="middle" fill="${{textColor}}" font-size="${{fontSize}}" font-weight="700" font-family="ui-sans-serif, system-ui, sans-serif">${{label}}</text>
      </svg>
    `;
  }}
  if (shape === 'square') {{
    return `
      <svg class="marker-svg" width="100%" height="100%" viewBox="0 0 34 34" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <rect x="1" y="1" width="32" height="32" fill="${{color}}" stroke="${{stroke}}" stroke-width="1.2" />
        <text x="17" y="18" text-anchor="middle" dominant-baseline="middle" fill="${{textColor}}" font-size="${{fontSize}}" font-weight="700" font-family="ui-sans-serif, system-ui, sans-serif">${{label}}</text>
      </svg>
    `;
  }}
  if (shape === 'diamond') {{
    return `
      <svg class="marker-svg" width="100%" height="100%" viewBox="0 0 34 34" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <polygon points="17,1 33,17 17,33 1,17" fill="${{color}}" stroke="${{stroke}}" stroke-width="1.2" />
        <text x="17" y="18" text-anchor="middle" dominant-baseline="middle" fill="${{textColor}}" font-size="${{fontSize}}" font-weight="700" font-family="ui-sans-serif, system-ui, sans-serif">${{label}}</text>
      </svg>
    `;
  }}
  if (shape === 'hexagon') {{
    return `
      <svg class="marker-svg" width="100%" height="100%" viewBox="0 0 38 34" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <polygon points="10,1 28,1 37,17 28,33 10,33 1,17" fill="${{color}}" stroke="${{stroke}}" stroke-width="1.2" />
        <text x="19" y="18" text-anchor="middle" dominant-baseline="middle" fill="${{textColor}}" font-size="${{fontSize}}" font-weight="700" font-family="ui-sans-serif, system-ui, sans-serif">${{label}}</text>
      </svg>
    `;
  }}
  if (shape === 'pentagon') {{
    return `
      <svg class="marker-svg" width="100%" height="100%" viewBox="0 0 38 36" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <polygon points="19,1 37,14 31,35 7,35 1,14" fill="${{color}}" stroke="${{stroke}}" stroke-width="1.2" />
        <text x="19" y="20" text-anchor="middle" dominant-baseline="middle" fill="${{textColor}}" font-size="${{fontSize}}" font-weight="700" font-family="ui-sans-serif, system-ui, sans-serif">${{label}}</text>
      </svg>
    `;
  }}
  return `
    <svg class="marker-svg" width="100%" height="100%" viewBox="0 0 34 34" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <circle cx="17" cy="17" r="16" fill="${{color}}" stroke="${{stroke}}" stroke-width="1.2" />
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
  if (value === null) return 'Google: ?';
  const count = numericOrNull(row.google_count);
  return `Google: ${{value.toFixed(1)}}${{count === null ? '' : ` (${{Math.round(count)}} reviews)`}}`;
}}

function formatSurvey(row) {{
  const overall = numericOrNull(row.survey_overall_good_percent);
  const completion = numericOrNull(row.survey_completion_rate_percent);
  const sentBack = numericOrNull(row.survey_sent_back);
  const sentOut = numericOrNull(row.survey_sent_out);
  if (overall === null && completion === null) return 'GP survey: ?';
  const parts = [];
  if (overall !== null) parts.push(`Overall good: ${{Math.round(overall)}}%`);
  if (completion !== null) parts.push(`Completion: ${{Math.round(completion)}}%`);
  if (sentBack !== null && sentOut !== null) parts.push(`${{Math.round(sentBack)}}/${{Math.round(sentOut)}} returned`);
  return `GP survey: ${{parts.join(' · ')}}`;
}}

function formatGap(row) {{
  const inputs = gapInputs(row);
  const gap = gapValue(row, {{ suppressSmall: false }});
  if (!inputs || gap === null) return 'Survey/Google gap: ?';
  const magnitude = Math.abs(gap);
  if (magnitude < 0.01) {{
    return activeGapMode === 'normalized'
      ? `Survey/Google gap: typical for this cohort · Google ${{inputs.google.toFixed(1)}} vs survey-equivalent ${{inputs.surveyStars.toFixed(2)}}`
      : `Survey/Google gap: aligned · Google ${{inputs.google.toFixed(1)}} vs survey-equivalent ${{inputs.surveyStars.toFixed(2)}}`;
  }}
  const direction = gap > 0 ? 'higher' : 'lower';
  return activeGapMode === 'normalized'
    ? `Survey/Google gap: ${{magnitude.toFixed(2)}} normalised-gap z-score (${{direction}}) · Google ${{inputs.google.toFixed(1)}} vs survey-equivalent ${{inputs.surveyStars.toFixed(2)}}`
    : `Survey/Google gap: ${{magnitude.toFixed(2)}} stars (${{direction}}) · Google ${{inputs.google.toFixed(1)}} vs survey-equivalent ${{inputs.surveyStars.toFixed(2)}}`;
}}

function popupMarkup(row) {{
  const google = `<div>${{formatGoogle(row)}}</div>`;
  const googleSource = row.google_source_note ? `<div>Google source: ${{row.google_source_note}}</div>` : '<div>Google source: repo review dataset</div>';
  const googleText = row.google_text_file ? `<div><a href="${{row.google_text_file}}" target="_blank" rel="noreferrer">Review text</a></div>` : '';
  const management = row.management_company ? `<div>Management: ${{row.management_company}}</div>` : '<div>Management: unknown</div>';
  const affiliatedGroup = row.affiliated_group ? `<div>Affiliated group: ${{row.affiliated_group}}</div>` : '';
  const takeoverDate = formatTakeoverDate(row.gtd_takeover_date, row.gtd_takeover_precision);
  const takeoverLine = takeoverDate ? `<div>GTD takeover: ${{takeoverDate}}</div>` : '';
  const takeoverNote = row.gtd_takeover_note ? `<div>${{row.gtd_takeover_note}}</div>` : '';
  const takeoverSource = row.gtd_takeover_source_url
    ? `<div><a href="${{row.gtd_takeover_source_url}}" target="_blank" rel="noreferrer">${{row.gtd_takeover_source_label || 'Takeover source'}}</a></div>`
    : '';
  const registeredPatients = numericOrNull(row.registered_patient_count);
  const registeredPatientsLine = `<div>Registered patients: ${{registeredPatients === null ? '?' : registeredPatients.toLocaleString('en-GB')}}</div>`;
  const survey = `<div>${{formatSurvey(row)}}</div>`;
  const surveyCompareValue = numericOrNull(row.survey_overall_good_ics_percent);
  const surveyCompare = surveyCompareValue === null ? '' : `<div>GP survey ICS overall-good: ${{Math.round(surveyCompareValue)}}%</div>`;
  const surveyResolution = row.gp_patient_survey_resolution_note ? `<div>${{row.gp_patient_survey_resolution_note}}</div>` : '';
  const surveyLink = row.gp_patient_survey_2025_url ? `<div><a href="${{row.gp_patient_survey_2025_url}}" target="_blank" rel="noreferrer">GP Patient Survey page</a></div>` : '';
  const gap = `<div>${{formatGap(row)}}</div>`;
  const gtd = row.gtd_url ? `<div><a href="${{row.gtd_url}}" target="_blank" rel="noreferrer">GTD page</a></div>` : '';
  return `
    <strong>${{row.name}}</strong><br>
    ${{row.postcode}}<br>
    <div>Code: ${{row.code}}</div>
    <div>Near: ${{row.nearby}}</div>
    ${{management}}
    ${{affiliatedGroup}}
    ${{takeoverLine}}
    ${{takeoverNote}}
    ${{registeredPatientsLine}}
    ${{google}}
    ${{googleSource}}
    ${{survey}}
    ${{surveyCompare}}
    ${{surveyResolution}}
    ${{gap}}
    ${{googleText}}
    <div><a href="${{row.nhs_url}}" target="_blank" rel="noreferrer">NHS page</a></div>
    ${{surveyLink}}
    ${{gtd}}
    ${{takeoverSource}}
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
      if (hoveredTrendPracticeCode === code) return;
      hoveredTrendPracticeCode = code;
      renderGtdScoreTrendChart();
    }});
    button.addEventListener('mouseleave', () => {{
      if (hoveredTrendPracticeCode !== code) return;
      hoveredTrendPracticeCode = null;
      renderGtdScoreTrendChart();
    }});
    button.addEventListener('focus', () => {{
      hoveredTrendPracticeCode = code;
      renderGtdScoreTrendChart();
    }});
    button.addEventListener('blur', () => {{
      if (hoveredTrendPracticeCode !== code) return;
      hoveredTrendPracticeCode = null;
      renderGtdScoreTrendChart();
    }});
    button.addEventListener('click', () => {{
      const nextCode = code === TREND_DEFAULT_CONTEXT_CODE
        ? TREND_DEFAULT_CONTEXT_CODE
        : pinnedTrendPracticeCode === code
          ? TREND_DEFAULT_CONTEXT_CODE
          : code;
      hoveredTrendPracticeCode = null;
      pinnedTrendPracticeCode = nextCode;
      focusPracticeByCode(nextCode === TREND_DEFAULT_CONTEXT_CODE ? NEW_BANK_CODE : nextCode);
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

function renderMarkers() {{
  markerLayer.clearLayers();
  const assignments = shapeAssignment();
  const metric = metricConfigs[activeMetric];
  const centroidByCode = activeAreaOverlay === 'population' ? voronoiCentroidByCode() : null;
  for (const row of rows) {{
    const metricValue = metric.value(row);
    if (metricValue === null && activeMetric === 'gap') {{
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
      html: markerSvg(shapeName, color, label, fontSize, label === '?'),
      iconSize: [scaledWidth, scaledHeight],
      iconAnchor: [Math.round(metrics.anchorX * scale), Math.round(metrics.anchorY * scale)],
      popupAnchor: [0, metrics.popupY]
    }});
    const pos = centroidByCode && centroidByCode.has(row.code) ? centroidByCode.get(row.code) : [row.lat, row.lon];
    const marker = L.marker(pos, {{ icon, zIndexOffset: baseZIndex }});
    marker.bindPopup(popupMarkup(row));
    marker.on('click', () => {{
      focusRow(row);
    }});
    marker.on('mouseover', () => marker.setZIndexOffset(baseZIndex + 2000));
    marker.on('mouseout', () => marker.setZIndexOffset(baseZIndex));
    marker.addTo(markerLayer);
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
  const points = rows
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
  const width = 920;
  const height = 320;
  const margin = {{ top: 34, right: 18, bottom: 42, left: 52 }};
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const headerBandY = 4;
  const headerBandHeight = 17;
  const headerTextY = 16;
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
  const assignments = shapeAssignment();
  const pointMarkup = points.map((point) => {{
    const companyShape = assignments.get(point.row.management_company);
    const radius = Math.max(4, Math.min(9, patientScaleForRow(point.row) * 6));
    const stroke = companyShape ? '#1a1c1a' : 'rgba(26,28,26,0.25)';
    const label = activeMetric === 'google'
      ? point.x.toFixed(1)
      : activeMetric === 'survey'
        ? `${{Math.round(point.x)}}%`
        : activeMetric === 'gap'
          ? `${{point.signed >= 0 ? '+' : ''}}${{point.signed.toFixed(2)}} (|${{point.x.toFixed(2)}}|)`
          : point.x.toFixed(2);
    return `
      <circle cx="${{xScale(point.x).toFixed(2)}}" cy="${{yScale(point.y).toFixed(2)}}" r="${{radius.toFixed(2)}}" fill="${{metric.markerColor(point.row)}}" stroke="${{stroke}}" stroke-width="${{companyShape ? 1.8 : 1}}">
        <title>${{point.row.name}} · ${{metric.title}}: ${{label}} · Completion: ${{Math.round(point.y)}}%</title>
      </circle>
    `;
  }}).join('');
  svg.innerHTML = `
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
    ${{pointMarkup}}
    <text x="${{width / 2}}" y="${{height - 8}}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)">${{scatterAxis.label}}</text>
    <text x="14" y="${{height / 2}}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)" transform="rotate(-90 14 ${{height / 2}})">GP survey completion rate</text>
  `;
  const completionValues = points.map((point) => point.y).sort((left, right) => left - right);
  const completionMedian = completionValues.length ? completionValues[Math.floor(completionValues.length / 2)] : null;
  const rValue = correlation(points);
  const newBank = points.find((point) => point.row.code === 'Y02960');
  const newBankSummary = !newBank
    ? ''
    : ` New Bank Health is at ${{Math.round(newBank.y)}}% completion and sits around the ${{percentile(completionValues, newBank.y).toFixed(0)}}th percentile for completion in this set.`;
  document.getElementById('scatter-summary').textContent =
    `${{points.length}} practices have both GP survey completion data and a usable ${{metric.title.toLowerCase()}} value. Median completion is ${{completionMedian === null ? '?' : `${{Math.round(completionMedian)}}%`}}. Pearson r is ${{rValue === null ? '?' : rValue.toFixed(2)}}.${{newBankSummary}}`;
}}

function renderDeprivationChart() {{
  const metric = metricConfigs[activeMetric];
  document.getElementById('deprivation-heading').textContent = `Score vs Deprivation - Showing ${{metricDisplayLabel(activeMetric)}}`;
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

function renderPatientChangeChart() {{
  const svg = document.getElementById('patient-change-chart');
  const summary = document.getElementById('patient-change-summary');
  const heading = document.getElementById('patient-change-heading');
  if (!svg || !summary || !heading) return;
  heading.textContent = `Registered Patients Over Time - Coloured by ${{metricDisplayLabel(activeMetric)}}`;

  const years = patientChangeAnalysis?.years || [];
  const series = (patientChangeAnalysis?.practice_series || []).filter((entry) =>
    (entry.points || []).filter((value) => value !== null && Number.isFinite(Number(value))).length >= 2
  );
  if (!years.length || !series.length) {{
    svg.innerHTML = '';
    summary.textContent = 'No practices currently have enough multi-year registered patient counts to plot.';
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
    `${{series.length}} practices have multi-year patient-count histories in this chart. Coloured lines show the average trajectory for each current ${{metricDisplayLabel(activeMetric).toLowerCase()}} band, and the dashed grey line is the Manchester average practice count for each year.${{flattenGlobal ? ' With Flatten Global on, the y-axis shows deviation from that yearly Manchester mean, so the chart shows which score bands are gaining or losing relative share rather than absolute patient volume.' : ' The y-axis is scoped to those displayed averages rather than every individual practice line.'}}${{newBankSummary}}`;
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
  const height = 92;
  const margin = {{ top: 8, right: 12, bottom: 22, left: 12 }};
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const minTotal = Math.min(...usableTotals);
  const maxTotal = Math.max(...usableTotals);
  const paddedMin = minTotal * 0.99;
  const paddedMax = maxTotal * 1.01;
  const yRange = Math.max(1, paddedMax - paddedMin);
  const xScale = (index) => margin.left + (years.length <= 1 ? plotWidth / 2 : (index / Math.max(1, years.length - 1)) * plotWidth);
  const yScale = (value) => margin.top + plotHeight - ((value - paddedMin) / yRange) * plotHeight;
  const path = totals.map((value, index) => `${{index === 0 ? 'M' : 'L'}}${{xScale(index).toFixed(2)}} ${{yScale(value).toFixed(2)}}`).join(' ');
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
    ${{tickIndexes.map((index) => `
      <text x="${{xScale(index).toFixed(2)}}" y="${{height - 6}}" text-anchor="middle" font-size="10.5" fill="rgba(26,28,26,0.68)">${{years[index]}}</text>
    `).join('')}}
    <circle cx="${{xScale(activeYearIndex).toFixed(2)}}" cy="${{yScale(activeTotal).toFixed(2)}}" r="4.2" fill="var(--accent)" stroke="white" stroke-width="1.2"></circle>
    <text x="${{Math.min(width - margin.right, xScale(activeYearIndex) + 8).toFixed(2)}}" y="${{Math.max(18, yScale(activeTotal) - 8).toFixed(2)}}" font-size="11" font-weight="700" fill="var(--accent)">${{years[activeYearIndex]}} · ${{activeTotal.toLocaleString('en-GB')}}</text>
    <text x="${{margin.left + 6}}" y="${{margin.top + 14}}" font-size="10.5" fill="rgba(26,28,26,0.72)">Whole dataset total: ${{firstTotal.toLocaleString('en-GB')}} -> ${{lastTotal.toLocaleString('en-GB')}} (${{changePct === null ? '?' : `${{changePct >= 0 ? '+' : ''}}${{changePct.toFixed(1)}}%`}})</text>
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
    ? `<circle cx="${{xScale(averageFinalIndex).toFixed(2)}}" cy="${{yScale(averageFinal).toFixed(2)}}" r="4.5" fill="var(--accent)" opacity="${{dimInactive ? '0.74' : '1'}}"></circle><text x="${{Math.min(width - margin.right, xScale(averageFinalIndex) + 8).toFixed(2)}}" y="${{(yScale(averageFinal) - 8).toFixed(2)}}" font-size="11" fill="var(--accent)" fill-opacity="${{dimInactive ? '0.74' : '1'}}" font-weight="700">GTD mean ${{Math.round(averageFinal)}}%</text>`
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
    ${{showAverage ? `<path d="${{averagePath}}" fill="none" stroke="var(--accent)" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round" opacity="${{dimInactive ? '0.78' : '1'}}"></path>` : ''}}
    ${{averageMarker}}
    ${{endMarkers}}
    ${{surveyPatientOverlay}}
    <text x="${{width / 2}}" y="${{height - 10}}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)">Survey year</text>
    <text x="14" y="${{height / 2}}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)" transform="rotate(-90 14 ${{height / 2}})">Overall experience good %</text>
    ${{patientOverlay?.length ? `<text x="${{width - 14}}" y="${{height / 2}}" text-anchor="middle" font-size="11" fill="rgba(26,28,26,0.6)" transform="rotate(90 ${{width - 14}} ${{height / 2}})">Patients vs GTD avg (%)</text>` : ''}}
  `;
  const defaultLabel = defaultEntry ? `GTD mean + ${{defaultEntry.series.name}}` : 'GTD mean';
  legend.innerHTML = [
    `<button type="button" class="trend-legend-item${{isMeanContext ? ' is-active' : ''}}" data-practice-code="${{TREND_DEFAULT_CONTEXT_CODE}}" aria-pressed="${{isMeanContext ? 'true' : 'false'}}" title="${{defaultLabel}}. Default chart view."><span class="trend-legend-swatch" style="background:var(--accent)"></span><span class="trend-legend-body"><span class="trend-legend-name">${{defaultLabel}}</span><span class="trend-legend-meta">Default view · GTD mean stays visible</span></span></button>`,
    ...practiceEntries.map((entry) => {{
    const latestText = entry.lastValue === null ? 'No data' : `Latest ${{Math.round(entry.lastValue)}}%`;
    const takeoverText = entry.series.takeover_date ? `Takeover ${{formatTakeoverDate(entry.series.takeover_date, entry.series.takeover_precision)}}` : 'Takeover date pending';
    const isActive = !isMeanContext && entry.series.code === activeCode;
    return `<button type="button" class="trend-legend-item${{isActive ? ' is-active' : ''}}" data-practice-code="${{entry.series.code}}" aria-pressed="${{isActive}}" title="${{entry.series.name}}. ${{latestText}}. ${{takeoverText}}."><span class="trend-legend-swatch" style="background:${{entry.color}}"></span><span class="trend-legend-body"><span class="trend-legend-name">${{entry.series.name}}</span><span class="trend-legend-meta">${{latestText}} · ${{takeoverText}}</span></span></button>`;
  }})
  ].join('');
  bindTrendLegendInteractions(legend);
  renderTrendOverlayLegend(overlayLegend, patientPath ? [
    {{ color: '#4c9a52', label: 'Patients vs GTD avg (%)' }},
  ] : []);
  const overlaySummary = patientPath ? ' Green dashed: registered patients as a share of the GTD yearly average, with raw patient counts left in the point labels.' : '';
  const activeSummary = !displayEntry
    ? ' Hover a practice in the legend to isolate its track.'
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
      <circle cx="${{xScale(averageFinalIndex).toFixed(2)}}" cy="${{yScale(averageFinal).toFixed(2)}}" r="4.5" fill="var(--accent)" opacity="${{dimInactive ? '0.74' : '1'}}"></circle>
      <text x="${{Math.min(width - margin.right, xScale(averageFinalIndex) + 8).toFixed(2)}}" y="${{(yScale(averageFinal) - 8).toFixed(2)}}" font-size="11" fill="var(--accent)" fill-opacity="${{dimInactive ? '0.74' : '1'}}" font-weight="700">GTD mean ${{averageFinal.toFixed(2)}}</text>
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
    ${{showAverage ? `<path d="${{averagePath}}" fill="none" stroke="var(--accent)" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round" opacity="${{dimInactive ? '0.78' : '1'}}"></path>` : ''}}
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
        title="${{defaultLabel}}. Default chart view."
      >
        <span class="trend-legend-swatch" style="background:var(--accent)"></span>
        <span class="trend-legend-body">
          <span class="trend-legend-name">${{defaultLabel}}</span>
          <span class="trend-legend-meta">Default view · GTD mean stays visible</span>
        </span>
      </button>
    `,
    ...practiceEntries.map((entry) => {{
    const latestText = entry.lastValue === null ? 'No latest score' : `Latest ${{entry.lastValue.toFixed(2)}}`;
    const takeoverText = entry.series.takeover_date
      ? `Takeover ${{formatTakeoverDate(entry.series.takeover_date, entry.series.takeover_precision)}}`
      : 'Takeover date pending';
    const isActive = !isMeanContext && entry.series.code === activeCode;
    return `
      <button
        type="button"
        class="trend-legend-item${{isActive ? ' is-active' : ''}}"
        data-practice-code="${{entry.series.code}}"
        aria-pressed="${{isActive ? 'true' : 'false'}}"
        title="${{entry.series.name}}. ${{latestText}}. ${{takeoverText}}."
      >
        <span class="trend-legend-swatch" style="background:${{entry.color}}"></span>
        <span class="trend-legend-body">
          <span class="trend-legend-name">${{entry.series.name}}</span>
          <span class="trend-legend-meta">${{latestText}} · ${{takeoverText}}</span>
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
    ? ' Hover a practice in the side legend to isolate its track and takeover marker, or click to pin it.'
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
  if (activeAreaOverlay === 'population') {{
    renderVoronoi();
  }} else if (activeAreaOverlay === 'deprivation') {{
    renderDeprivation();
  }}
  renderGtdScoreTrendChart();
  renderScatterplot();
  renderDeprivationChart();
  renderPatientChangeChart();
  renderPatientTreemap();
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
    renderPatientChangeChart();
    renderPatientTreemap();
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
  if (activeAreaOverlay === 'population') {{
    if (voronoiLayer) {{
      map.removeLayer(voronoiLayer);
      voronoiLayer = null;
    }}
    renderVoronoi();
  }}
}});

try {{
  sidebarCollapsed = localStorage.getItem(SIDEBAR_COLLAPSE_KEY) === '1';
}} catch (_error) {{
  sidebarCollapsed = false;
}}
updateSidebarState();
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

    write_csv(OUTPUT_DIR / "gtd_greater_manchester_gp_practices.csv", rows)
    write_json(OUTPUT_DIR / "gtd_greater_manchester_gp_practices.json", rows)
    summary = write_summary(OUTPUT_DIR / "summary.json", rows)
    write_readme(OUTPUT_DIR / "README.md", summary)
    write_map(OUTPUT_DIR / "map.html", rows)
    print(f"Wrote {len(rows)} rows to {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
