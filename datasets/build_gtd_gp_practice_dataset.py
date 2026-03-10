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
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlencode


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "gtd-greater-manchester-gp-practice-reviews-2026-03-09"
GP_PATIENT_SURVEY_RAW_DIR = BASE_DIR / "gp_patient_survey_raw"
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
    SupplementalSearchCenter("Prestwich supplemental search", "M25 1BT", "Pull in north-west Manchester / Prestwich-side practices inside and just beyond the M60"),
    SupplementalSearchCenter("Radcliffe supplemental search", "M26 1LS", "Pull in Radcliffe-side practices around the north-west arc beyond the M60"),
    SupplementalSearchCenter("Swinton supplemental search", "M27 4AA", "Pull in Swinton and Pendlebury-side practices on the north-west / west side of the M60"),
    SupplementalSearchCenter("Little Hulton supplemental search", "M28 0BQ", "Pull in Walkden, Little Hulton and nearby western-edge practices around the M60"),
    SupplementalSearchCenter("Whitefield supplemental search", "M45 8WF", "Pull in Whitefield and Bury-south practices around the north-west arc of the M60"),
    SupplementalSearchCenter("Salford Quays supplemental search", "M50 3UB", "Pull in Salford Quays / Ordsall-side practices inside the western side of the M60"),
    SupplementalSearchCenter("Partington supplemental search", "M31 4FL", "Pull in Partington, Carrington and nearby outer-west practices around the M60"),
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
        }
        record["management_company_name"] = "GTD Healthcare" if matched_anchor else ""
        record["management_company_source"] = "gtd_anchor_match" if matched_anchor else ""
        record["management_company_confidence"] = "high" if matched_anchor else ""
        record["management_company_domain"] = "gtdhealthcare.co.uk" if matched_anchor else ""
        record["management_company_group_size"] = ""
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
    path.write_text(json.dumps(rows, indent=2), encoding="utf-8")


def write_summary(path: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    postcodes = sorted({row["postcode"].split()[0] for row in rows if row["postcode"]})
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
        "management_company_identified_count": sum(1 for row in rows if row.get("management_company_name", "")),
        "management_company_distinct_count": len({row.get("management_company_name", "") for row in rows if row.get("management_company_name", "")}),
        "trustpilot_coverage_count": sum(1 for row in rows if row["trustpilot_score"] != ""),
        "postcode_area_count": len(postcodes),
        "postcode_areas": postcodes,
        "source_urls": {
            "gtd_gp_practices_page": "https://www.gtdhealthcare.co.uk/patient-services/gp-practices",
            "nhs_find_a_gp": "https://www.nhs.uk/service-search/find-a-gp",
            "postcode_geocoder": "https://api.postcodes.io/",
            "google_review_mirror": "https://justvisits.co.uk/",
        },
        "supplemental_search_centers": [
            {"name": center.name, "postcode": center.postcode, "scope_note": center.scope_note}
            for center in SUPPLEMENTAL_SEARCH_CENTERS
        ],
        "notes": [
            "Google review fields were only filled when an exact or high-confidence Just Visits match was available.",
            "Trustpilot fields were left blank because no reliable per-practice public source was found in this run.",
            "This run intentionally keeps the broader NHS result set around each GTD anchor instead of trimming aggressively to 1 mile.",
            "Additional south, west and north-west Greater Manchester coverage was added with explicit supplemental NHS search centres.",
            "When available, direct Google Maps captures can add a review text file path per practice without embedding the review text in the main CSV.",
            "Management company fields are conservative and should only be filled when the NHS-listed website or GTD anchor match makes the operator identifiable.",
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
- `management_company_*` fields in the CSV/JSON: conservative operator identification where supported by the NHS-listed website or GTD source data

Source basis:

- GTD Healthcare GP practices page: https://www.gtdhealthcare.co.uk/patient-services/gp-practices
- NHS Find a GP search results and profile pages: https://www.nhs.uk/service-search/find-a-gp
- Postcode geocoding: https://api.postcodes.io/
- Google review mirror used when exact matches were found: https://justvisits.co.uk/
- Supplemental broader Greater Manchester search centres: M21 8AU, M22 5RX, M23 9JH, M25 1BT, M26 1LS, M27 4AA, M28 0BQ, M31 4FL, M32 0JG, M33 7ZF, M45 8WF, M50 3UB

Coverage snapshot:

- total rows: {summary['row_count']}
- GTD-managed rows: {summary['gtd_managed_count']}
- non-GTD nearby rows: {summary['non_gtd_count']}
- Google review coverage rows: {summary['google_review_coverage_count']}
- Google Maps direct coverage rows: {summary['google_maps_direct_coverage_count']}
- Review text files written: {summary['google_review_text_file_count']}
- Practices with management company identified: {summary.get('management_company_identified_count', 0)}
- Distinct management companies identified: {summary.get('management_company_distinct_count', 0)}
- Google Maps scans completed: {summary.get('google_maps_total_scanned_count', 0)}
- Google Maps manual review queue: {summary.get('google_maps_manual_review_count', 0)}

Caveats:

- Google review fields are partial. They were only populated when a high-confidence public mirror match could be identified.
- `management_company_*` fields should remain blank unless the operator is identifiable from GTD source data or a clear NHS-listed website-domain grouping.
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


def survey_metric(payload: dict[str, Any], question_name: str, field: str = "practice_percent") -> Any:
    key_questions = payload.get("key_questions", {})
    if not isinstance(key_questions, dict):
        return ""
    question = key_questions.get(question_name, {})
    if not isinstance(question, dict):
        return ""
    return question.get(field, "")


def write_map(path: Path, rows: list[dict[str, Any]]) -> None:
    survey_by_code = load_gp_patient_survey_index()
    known_management_companies = sorted(
        {
            row.get("management_company_name", "") or ("GTD Healthcare" if row["gtd_managed"] else "")
            for row in rows
            if row.get("management_company_name", "") or row["gtd_managed"]
        }
    )
    markers = []
    for row in rows:
        survey_payload = survey_by_code.get(str(row["canonical_code"]), {})
        markers.append(
            {
                "code": row["canonical_code"],
                "name": row["practice_name"],
                "lat": row["latitude"],
                "lon": row["longitude"],
                "postcode": row["postcode"],
                "gtd": row["gtd_managed"],
                "management_company": row.get("management_company_name", "") or ("GTD Healthcare" if row["gtd_managed"] else ""),
                "google_score": row["google_review_score"],
                "google_count": row["google_review_count"],
                "google_source_note": row.get("google_review_source_note", ""),
                "google_text_file": row.get("google_review_text_file", ""),
                "nhs_url": row["nhs_profile_url"],
                "gtd_url": row["gtd_site_url"],
                "nearby": row["nearby_to_gtd_anchors"],
                "survey_overall_good_percent": survey_metric(survey_payload, "overallexp"),
                "survey_overall_good_ics_percent": survey_metric(survey_payload, "overallexp", "ics_percent"),
                "survey_overall_good_national_percent": survey_metric(survey_payload, "overallexp", "national_percent"),
                "survey_completion_rate_percent": survey_payload.get("completion_rate_percent", ""),
                "survey_sent_out": survey_payload.get("surveys_sent_out", ""),
                "survey_sent_back": survey_payload.get("surveys_sent_back", ""),
            }
        )

    center_lat = sum(row["latitude"] for row in rows) / len(rows)
    center_lon = sum(row["longitude"] for row in rows) / len(rows)
    map_html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>GTD Greater Manchester GP Practice Experience</title>
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
  font: 14px/1.4 Georgia, serif;
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
  min-height: 100vh;
  min-height: 100dvh;
}}
#map {{
  height: 100vh;
  height: 100dvh;
  min-height: 100vh;
  min-height: 100dvh;
}}
.legend {{
  position: absolute;
  top: 12px;
  left: 12px;
  z-index: 1000;
  background: var(--panel-strong);
  padding: 12px 14px;
  border-radius: 14px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.12);
  max-width: 360px;
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
.segmented {{
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  border: 1px solid var(--line);
  border-radius: 999px;
  overflow: hidden;
  background: rgba(15, 94, 156, 0.06);
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
.metric-legend {{
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}}
.metric-legend .row {{
  padding: 4px 8px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: rgba(255,255,255,0.82);
  font-size: 12px;
}}
.metric-legend .row.shape-row {{
  background: rgba(76, 154, 82, 0.1);
}}
.metric-note {{
  margin-top: 6px;
  font-size: 11px;
  line-height: 1.35;
}}
.manager-list {{
  display: grid;
  gap: 8px;
  max-height: 210px;
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
.leaflet-marker-icon.marker-icon {{
  background: transparent;
  border: 0;
}}
.leaflet-popup-content {{
  min-width: 220px;
}}
.marker-shape {{
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font: 700 12px/1 ui-sans-serif, system-ui, sans-serif;
  text-shadow: 0 1px 2px rgba(0,0,0,0.35);
  border: 1px solid rgba(0,0,0,0.28);
  box-shadow: 0 4px 12px rgba(0,0,0,0.22);
  transform-origin: center center;
}}
.marker-circle {{
  width: 34px;
  height: 34px;
  border-radius: 999px;
}}
.marker-square {{
  width: 34px;
  height: 34px;
}}
.marker-diamond {{
  width: 34px;
  height: 34px;
  transform: rotate(45deg);
}}
.marker-triangle {{
  width: 42px;
  height: 36px;
  clip-path: polygon(50% 0, 0 100%, 100% 100%);
}}
.marker-hexagon {{
  width: 38px;
  height: 34px;
  clip-path: polygon(25% 0, 75% 0, 100% 50%, 75% 100%, 25% 100%, 0 50%);
}}
.marker-pentagon {{
  width: 38px;
  height: 36px;
  clip-path: polygon(50% 0, 100% 38%, 81% 100%, 19% 100%, 0 38%);
}}
.marker-label {{
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  white-space: nowrap;
  pointer-events: none;
}}
.marker-circle .marker-label {{
  top: 10px;
}}
.marker-square .marker-label {{
  top: 10px;
}}
.marker-diamond .marker-label {{
  top: 10px;
  transform: translateX(-50%) rotate(-45deg);
}}
.marker-triangle .marker-label {{
  top: 14px;
  font-size: 11px;
}}
.marker-hexagon .marker-label {{
  top: 10px;
}}
.marker-pentagon .marker-label {{
  top: 11px;
}}
.marker-missing .marker-label {{
  color: #f4f4f4;
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
#scatterplot {{
  width: 100%;
  height: 320px;
  display: block;
}}
.chart-note {{
  font-size: 12px;
  color: rgba(26, 28, 26, 0.72);
}}
.outlier-list {{
  display: grid;
  gap: 8px;
}}
.outlier-item {{
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid var(--line);
  background: rgba(255,255,255,0.72);
}}
.outlier-item strong {{
  display: block;
}}
.outlier-meta {{
  font-size: 12px;
  color: rgba(26, 28, 26, 0.72);
}}
@media (max-width: 960px) {{
  .page {{
    grid-template-rows: minmax(100vh, 100dvh) auto;
  }}
  .insights {{
    grid-template-columns: 1fr;
  }}
  .legend {{
    right: 12px;
    max-width: none;
  }}
}}
</style>
</head>
<body>
<div class="page">
  <div class="map-stage">
    <div class="legend">
      <h1>GTD GP Practice Experience Map</h1>
      <p>{len(rows)} GP surgery profiles from a broad catchment around GTD anchors.</p>
      <div class="control-group">
        <h2>Score Source</h2>
        <div class="segmented">
          <label><input type="radio" name="score-source" value="google" checked><span>Google</span></label>
          <label><input type="radio" name="score-source" value="survey"><span>GP Survey</span></label>
          <label><input type="radio" name="score-source" value="gap"><span>Gap</span></label>
        </div>
        <p id="metric-description" class="hint"></p>
        <div id="metric-legend" class="metric-legend"></div>
      </div>
      <h2>Management</h2>
      <p id="manager-hint" class="hint"></p>
      <div id="manager-list" class="manager-list"></div>
    </div>
    <div id="map"></div>
  </div>
  <div class="insights">
    <section class="panel">
      <h2>Completion Rate vs Score</h2>
      <p id="scatter-summary" class="hint"></p>
      <div class="chart-frame">
        <svg id="scatterplot" viewBox="0 0 920 320" preserveAspectRatio="xMidYMid meet" aria-labelledby="scatter-title" role="img">
          <title id="scatter-title">Survey completion rate against selected score</title>
        </svg>
      </div>
      <p class="chart-note">Y-axis is GP Patient Survey completion rate. X-axis changes with the selected score source.</p>
    </section>
    <section class="panel">
      <h2>Lowest Completion Rates</h2>
      <p class="hint">Quick check for practices where survey turnout may be too thin to trust at face value.</p>
      <div id="outlier-list" class="outlier-list"></div>
    </section>
  </div>
</div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const rows = {json.dumps(markers)};
const knownManagementCompanies = {json.dumps(known_management_companies)};
const map = L.map('map').setView([{center_lat:.6f}, {center_lon:.6f}], 11);
const markerLayer = L.layerGroup().addTo(map);
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
  maxZoom: 18,
  attribution: '&copy; OpenStreetMap contributors'
}}).addTo(map);
const managementShapePool = ['triangle', 'square', 'diamond', 'hexagon', 'pentagon'];
const selectedManagementCompanies = new Set(['GTD Healthcare']);
let activeMetric = 'google';

const metricConfigs = {{
  google: {{
    title: 'Google rating',
    description: 'Google data here is from this repo\\'s merged review collection.',
    legendRows: [
      ['No rating', 'var(--missing)'],
      ['0.0-1.9', 'var(--low)'],
      ['2.0-2.9', 'var(--midlow)'],
      ['3.0-3.9', 'var(--midhigh)'],
      ['4.0-4.4', 'var(--high)'],
      ['4.5+', 'var(--veryhigh)']
    ],
    value(row) {{
      const numeric = Number(row.google_score);
      return Number.isFinite(numeric) ? numeric : null;
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
      const count = Number(row.google_count);
      return Number.isFinite(count) && count > 0 ? count : 0;
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
    legendRows: [
      ['No survey score', 'var(--missing)'],
      ['0-49%', 'var(--low)'],
      ['50-59%', 'var(--midlow)'],
      ['60-69%', 'var(--midhigh)'],
      ['70-79%', 'var(--high)'],
      ['80%+', 'var(--veryhigh)']
    ],
    value(row) {{
      const numeric = Number(row.survey_overall_good_percent);
      return Number.isFinite(numeric) ? numeric : null;
    }},
    compareValue(row) {{
      const numeric = Number(row.survey_overall_good_ics_percent);
      return Number.isFinite(numeric) ? numeric : null;
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
      const count = Number(row.survey_sent_back);
      return Number.isFinite(count) && count > 0 ? count : 0;
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
    description: 'Indicator only: survey overall-good % is scaled to 0-5 and compared with Google.',
    legendRows: [
      ['Hidden if missing or <1.0', 'var(--missing)'],
      ['1.0-1.49', 'var(--midhigh)'],
      ['1.5-1.99', 'var(--midlow)'],
      ['2.0+ apart', 'var(--low)']
    ],
    value(row) {{
      const google = Number(row.google_score);
      const survey = Number(row.survey_overall_good_percent);
      if (!Number.isFinite(google) || !Number.isFinite(survey)) return null;
      const gap = Math.abs(google - (survey / 20));
      return gap < 1 ? null : gap;
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
      if (value >= 2.0) return '#c3472f';
      if (value >= 1.5) return '#dc8c23';
      if (value >= 1.0) return '#d2b529';
      if (value >= 0.5) return '#4c9a52';
      return '#1c7c54';
    }},
    scaleCount(row) {{
      const google = Number(row.google_count);
      const survey = Number(row.survey_sent_back);
      const googleValid = Number.isFinite(google) && google > 0;
      const surveyValid = Number.isFinite(survey) && survey > 0;
      if (googleValid && surveyValid) return Math.min(google, survey);
      if (googleValid) return google;
      if (surveyValid) return survey;
      return 0;
    }},
    averageLabel(value) {{
      return value === null ? '?' : value.toFixed(2);
    }},
    axisLabel: 'Absolute gap between Google and survey-equivalent stars',
    axisMin: 0,
    axisMax: 2.5
  }}
}};

function numericOrNull(value) {{
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : null;
}}

function maxCountForMetric(metricName) {{
  const metric = metricConfigs[metricName];
  return Math.max(0, ...rows.map((row) => metric.scaleCount(row)));
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

function scaleForRow(row) {{
  const metric = metricConfigs[activeMetric];
  const maxCount = maxCountForMetric(activeMetric);
  const count = metric.scaleCount(row);
  if (!Number.isFinite(count) || count <= 0) return 0.7;
  if (maxCount <= 0) return 0.7;
  const normalized = Math.log1p(count) / Math.log1p(maxCount);
  return 0.5 + (normalized ** 0.7) * 0.7;
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

function renderMetricLegend() {{
  const metric = metricConfigs[activeMetric];
  document.getElementById('metric-description').textContent = metric.description;
  document.getElementById('metric-description').className = 'hint metric-note';
  const legend = document.getElementById('metric-legend');
  legend.innerHTML = '';
  const shapeRow = document.createElement('div');
  shapeRow.className = 'row shape-row';
  shapeRow.innerHTML = '<span class="swatch triangle" style="background: var(--midhigh)"></span><span>Selected group</span>';
  legend.appendChild(shapeRow);
  metric.legendRows.forEach(([label, color]) => {{
    const row = document.createElement('div');
    row.className = 'row';
    row.innerHTML = `<span class="swatch circle" style="background: ${{color}}"></span><span>${{label}}</span>`;
    legend.appendChild(row);
  }});
}}

function renderManagementList() {{
  const container = document.getElementById('manager-list');
  container.innerHTML = '';
  const assignments = shapeAssignment();
  const metric = metricConfigs[activeMetric];
  document.getElementById('manager-hint').textContent = `Select up to ${{managementShapePool.length}} management companies. Selected groups get distinct shapes and show their current ${{metric.title.toLowerCase()}} average.`;
  for (const company of managementCompanies) {{
    const checked = selectedManagementCompanies.has(company.name);
    const shape = assignments.get(company.name) || 'circle';
    const average = metric.averageLabel(averageMetric(company.rows, activeMetric));
    const row = document.createElement('label');
    row.className = 'manager-option';
    row.innerHTML = `
      <input type="checkbox" ${{checked ? 'checked' : ''}} data-company="${{company.name}}">
      <span class="manager-name"><span class="swatch ${{shape}}" style="background:${{checked ? 'var(--midhigh)' : 'var(--missing)'}}; display:inline-block; margin-right:8px;"></span>${{company.name}}</span>
      <span class="manager-meta">${{average}} avg · ${{company.count}}</span>
    `;
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
  const google = numericOrNull(row.google_score);
  const surveyPercent = numericOrNull(row.survey_overall_good_percent);
  if (google === null || surveyPercent === null) return 'Survey/Google gap: ?';
  const surveyStars = surveyPercent / 20;
  const gap = Math.abs(google - surveyStars);
  return `Survey/Google gap: ${{gap.toFixed(2)}} stars · Google ${{google.toFixed(1)}} vs survey-equivalent ${{surveyStars.toFixed(2)}}`;
}}

function renderMarkers() {{
  markerLayer.clearLayers();
  const assignments = shapeAssignment();
  const metric = metricConfigs[activeMetric];
  for (const row of rows) {{
    const metricValue = metric.value(row);
    if (metricValue === null && activeMetric === 'gap') {{
      continue;
    }}
    const color = metric.markerColor(row);
    const label = metric.markerLabel(row);
    const shapeName = assignments.get(row.management_company) || 'circle';
    const shapeClass = `marker-${{shapeName}}`;
    const missingClass = label === '?' ? ' marker-missing' : '';
    const scale = scaleForRow(row);
    const metrics = baseShapeMetrics(shapeName);
    const fontSize = Math.max(9, Math.min(13, Math.round(10 + scale * 2)));
    const baseZIndex = assignments.has(row.management_company) ? 1000 : 0;
    const icon = L.divIcon({{
      className: 'marker-icon',
      html: `<div class="marker-shape ${{shapeClass}}${{missingClass}}" style="background:${{color}}; transform: scale(${{scale.toFixed(3)}});"><span class="marker-label" style="font-size:${{fontSize}}px">${{label}}</span></div>`,
      iconSize: [Math.round(metrics.width * scale), Math.round(metrics.height * scale)],
      iconAnchor: [Math.round(metrics.anchorX * scale), Math.round(metrics.anchorY * scale)],
      popupAnchor: [0, metrics.popupY]
    }});
    const marker = L.marker([row.lat, row.lon], {{ icon, zIndexOffset: baseZIndex }});
    const google = `<div>${{formatGoogle(row)}}</div>`;
    const googleSource = row.google_source_note ? `<div>Google source: ${{row.google_source_note}}</div>` : '<div>Google source: repo review dataset</div>';
    const googleText = row.google_text_file ? `<div><a href="${{row.google_text_file}}" target="_blank" rel="noreferrer">Review text</a></div>` : '';
    const management = row.management_company ? `<div>Management: ${{row.management_company}}</div>` : '<div>Management: unknown</div>';
    const survey = `<div>${{formatSurvey(row)}}</div>`;
    const surveyCompare = numericOrNull(row.survey_overall_good_ics_percent) === null ? '' : `<div>GP survey ICS overall-good: ${{Math.round(Number(row.survey_overall_good_ics_percent))}}%</div>`;
    const gap = `<div>${{formatGap(row)}}</div>`;
    const gtd = row.gtd_url ? `<div><a href="${{row.gtd_url}}" target="_blank" rel="noreferrer">GTD page</a></div>` : '';
    marker.bindPopup(`
      <strong>${{row.name}}</strong><br>
      ${{row.postcode}}<br>
      <div>Code: ${{row.code}}</div>
      <div>Near: ${{row.nearby}}</div>
      ${{management}}
      ${{google}}
      ${{googleSource}}
      ${{survey}}
      ${{surveyCompare}}
      ${{gap}}
      ${{googleText}}
      <div><a href="${{row.nhs_url}}" target="_blank" rel="noreferrer">NHS page</a></div>
      ${{gtd}}
    `);
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

function percentile(sortedValues, value) {{
  if (!sortedValues.length) return null;
  let lessOrEqual = 0;
  sortedValues.forEach((candidate) => {{
    if (candidate <= value) lessOrEqual += 1;
  }});
  return (lessOrEqual / sortedValues.length) * 100;
}}

function renderScatterplot() {{
  const metric = metricConfigs[activeMetric];
  const points = rows
    .map((row) => {{
      const x = metric.value(row);
      const y = numericOrNull(row.survey_completion_rate_percent);
      if (x === null || y === null) return null;
      return {{ row, x, y }};
    }})
    .filter(Boolean);
  const svg = document.getElementById('scatterplot');
  const width = 920;
  const height = 320;
  const margin = {{ top: 18, right: 18, bottom: 42, left: 52 }};
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const completionMax = Math.max(10, ...points.map((point) => point.y), 50);
  const xScale = (value) => margin.left + ((value - metric.axisMin) / (metric.axisMax - metric.axisMin)) * plotWidth;
  const yScale = (value) => margin.top + plotHeight - (value / completionMax) * plotHeight;
  const gridY = [];
  for (let tick = 0; tick <= completionMax; tick += 10) {{
    gridY.push(tick);
  }}
  const gridX = activeMetric === 'google'
    ? [0, 1, 2, 3, 4, 5]
    : activeMetric === 'survey'
      ? [0, 20, 40, 60, 80, 100]
      : [0, 0.5, 1.0, 1.5, 2.0, 2.5];
  const assignments = shapeAssignment();
  const pointMarkup = points.map((point) => {{
    const companyShape = assignments.get(point.row.management_company);
    const radius = Math.max(4, Math.min(9, scaleForRow(point.row) * 6));
    const stroke = companyShape ? '#1a1c1a' : 'rgba(26,28,26,0.25)';
    const label = activeMetric === 'google'
      ? point.x.toFixed(1)
      : activeMetric === 'survey'
        ? `${{Math.round(point.x)}}%`
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
    <text x="${{width / 2}}" y="${{height - 8}}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)">${{metric.axisLabel}}</text>
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

function renderOutliers() {{
  const list = document.getElementById('outlier-list');
  const metric = metricConfigs[activeMetric];
  const ranked = rows
    .map((row) => {{
      const completion = numericOrNull(row.survey_completion_rate_percent);
      if (completion === null) return null;
      const score = metric.value(row);
      if (activeMetric === 'gap' && score === null) return null;
      return {{
        row,
        completion,
        score
      }};
    }})
    .filter(Boolean)
    .sort((left, right) => left.completion - right.completion)
    .slice(0, 8);
  list.innerHTML = ranked.map((entry) => {{
    const scoreLabel = entry.score === null ? '?' : activeMetric === 'google' ? entry.score.toFixed(1) : activeMetric === 'survey' ? `${{Math.round(entry.score)}}%` : entry.score.toFixed(2);
    const googleLabel = numericOrNull(entry.row.google_score) === null ? 'Google ?' : `Google ${{Number(entry.row.google_score).toFixed(1)}}`;
    return `
      <div class="outlier-item">
        <strong>${{entry.row.name}}</strong>
        <div class="outlier-meta">${{entry.row.management_company || 'Unknown management'}} · completion ${{Math.round(entry.completion)}}%</div>
        <div class="outlier-meta">${{metric.title}} ${{scoreLabel}} · ${{googleLabel}}</div>
      </div>
    `;
  }}).join('');
}}

function rerenderAll() {{
  renderMetricLegend();
  renderManagementList();
  renderMarkers();
  renderScatterplot();
  renderOutliers();
}}

document.querySelectorAll('input[name="score-source"]').forEach((input) => {{
  input.addEventListener('change', (event) => {{
    activeMetric = event.target.value;
    rerenderAll();
  }});
}});

rerenderAll();
</script>
</body>
</html>
"""
    path.write_text(map_html, encoding="utf-8")


def main() -> int:
    OUTPUT_DIR.mkdir(exist_ok=True)
    rows = build_dataset()
    write_csv(OUTPUT_DIR / "gtd_greater_manchester_gp_practices.csv", rows)
    write_json(OUTPUT_DIR / "gtd_greater_manchester_gp_practices.json", rows)
    summary = write_summary(OUTPUT_DIR / "summary.json", rows)
    write_readme(OUTPUT_DIR / "README.md", summary)
    write_map(OUTPUT_DIR / "map.html", rows)
    print(f"Wrote {len(rows)} rows to {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
