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


def write_map(path: Path, rows: list[dict[str, Any]]) -> None:
    known_management_companies = sorted(
        {
            row.get("management_company_name", "") or ("GTD Healthcare" if row["gtd_managed"] else "")
            for row in rows
            if row.get("management_company_name", "") or row["gtd_managed"]
        }
    )
    markers = [
        {
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
        }
        for row in rows
    ]
    center_lat = sum(row["latitude"] for row in rows) / len(rows)
    center_lon = sum(row["longitude"] for row in rows) / len(rows)
    map_html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>GTD Greater Manchester GP Practice Reviews</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
:root {{
  --bg: #f6f4ef;
  --ink: #1a1c1a;
  --panel: rgba(255,255,255,0.92);
  --missing: #9aa0a6;
  --low: #c3472f;
  --midlow: #dc8c23;
  --midhigh: #d2b529;
  --high: #4c9a52;
  --veryhigh: #1c7c54;
}}
html, body, #map {{ height: 100%; margin: 0; }}
body {{ font: 14px/1.4 Georgia, serif; color: var(--ink); background: radial-gradient(circle at top, #fff7e3, var(--bg)); }}
#map {{ height: 100vh; }}
.legend {{
  position: absolute;
  top: 12px;
  left: 12px;
  z-index: 1000;
  background: var(--panel);
  padding: 12px 14px;
  border-radius: 14px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.12);
  max-width: 340px;
}}
.legend h1 {{ margin: 0 0 8px; font-size: 18px; }}
.legend p {{ margin: 0 0 8px; }}
.legend h2 {{ margin: 12px 0 8px; font-size: 13px; text-transform: uppercase; letter-spacing: 0.04em; }}
.legend .row {{
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 7px;
}}
.legend .hint {{ color: rgba(26, 28, 26, 0.72); font-size: 12px; }}
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
.swatch.circle {{ border-radius: 999px; }}
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
.leaflet-popup-content a {{ word-break: break-word; }}
</style>
</head>
<body>
<div class="legend">
  <h1>GTD GP Practice Map</h1>
  <p>{len(rows)} GP surgery profiles from a broad catchment around GTD anchors.</p>
  <div class="row"><span class="swatch triangle" style="background: var(--midhigh)"></span><span>Selected management company shape</span></div>
  <div class="row"><span class="swatch circle" style="background: var(--midhigh)"></span><span>Non-GTD practice</span></div>
  <div class="row"><span class="swatch circle" style="background: var(--missing)"></span><span>Missing Google rating</span></div>
  <div class="row"><span class="swatch circle" style="background: var(--low)"></span><span>0.0 to 1.9</span></div>
  <div class="row"><span class="swatch circle" style="background: var(--midlow)"></span><span>2.0 to 2.9</span></div>
  <div class="row"><span class="swatch circle" style="background: var(--midhigh)"></span><span>3.0 to 3.9</span></div>
  <div class="row"><span class="swatch circle" style="background: var(--high)"></span><span>4.0 to 4.4</span></div>
  <div class="row"><span class="swatch circle" style="background: var(--veryhigh)"></span><span>4.5+</span></div>
  <h2>Management</h2>
  <p class="hint">Select up to 5 management companies. Selected groups get distinct shapes and show their current Google average.</p>
  <div id="manager-list" class="manager-list"></div>
</div>
<div id="map"></div>
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
const maxGoogleReviewCount = Math.max(
  0,
  ...rows.map((row) => {{
    const numeric = Number(row.google_count);
    return Number.isFinite(numeric) && numeric > 0 ? numeric : 0;
  }})
);

function averageGoogleScore(rowsForCompany) {{
  const scores = rowsForCompany
    .map((row) => Number(row.google_score))
    .filter((value) => Number.isFinite(value));
  if (!scores.length) return null;
  return scores.reduce((sum, value) => sum + value, 0) / scores.length;
}}

const managementCompanies = knownManagementCompanies.map((name) => {{
  const companyRows = rows.filter((row) => row.management_company === name);
  return {{
    name,
    count: companyRows.length,
    averageScore: averageGoogleScore(companyRows)
  }};
}});

function markerColor(score) {{
  if (score === '' || score === null || Number.isNaN(Number(score))) return '#9aa0a6';
  const value = Number(score);
  if (value < 2) return '#c3472f';
  if (value < 3) return '#dc8c23';
  if (value < 4) return '#d2b529';
  if (value < 4.5) return '#4c9a52';
  return '#1c7c54';
}}

function markerLabel(score) {{
  if (score === '' || score === null || Number.isNaN(Number(score))) return '?';
  return Number(score).toFixed(1);
}}

function reviewScale(reviewCount) {{
  const count = Number(reviewCount);
  if (!Number.isFinite(count) || count <= 0) return 0.7;
  if (maxGoogleReviewCount <= 0) return 0.7;
  const normalized = Math.log1p(count) / Math.log1p(maxGoogleReviewCount);
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

function renderManagementList() {{
  const container = document.getElementById('manager-list');
  container.innerHTML = '';
  const assignments = shapeAssignment();
  for (const company of managementCompanies) {{
    const checked = selectedManagementCompanies.has(company.name);
    const shape = assignments.get(company.name) || 'circle';
    const average = company.averageScore === null ? '?' : company.averageScore.toFixed(2);
    const row = document.createElement('label');
    row.className = 'manager-option';
    row.innerHTML = `
      <input type="checkbox" ${'{'}checked ? 'checked' : ''{'}'} data-company="${'{'}company.name{'}'}">
      <span class="manager-name"><span class="swatch ${'{'}shape{'}'}" style="background:${'{'}checked ? 'var(--midhigh)' : 'var(--missing)'{'}'}; display:inline-block; margin-right:8px;"></span>${'{'}company.name{'}'}</span>
      <span class="manager-meta">${'{'}average{'}'} avg · ${'{'}company.count{'}'}</span>
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
      renderManagementList();
      renderMarkers();
    }});
    container.appendChild(row);
  }}
}}

function renderMarkers() {{
  markerLayer.clearLayers();
  const assignments = shapeAssignment();
  for (const row of rows) {{
    const color = markerColor(row.google_score);
    const label = markerLabel(row.google_score);
    const shapeName = assignments.get(row.management_company) || 'circle';
    const shapeClass = `marker-${'{'}shapeName{'}'}`;
    const missingClass = label === '?' ? ' marker-missing' : '';
    const scale = reviewScale(row.google_count);
    const metrics = baseShapeMetrics(shapeName);
    const fontSize = Math.max(9, Math.min(13, Math.round(10 + scale * 2)));
    const icon = L.divIcon({{
      className: 'marker-icon',
      html: `<div class="marker-shape ${'{'}shapeClass{'}'}${'{'}missingClass{'}'}" style="background:${'{'}color{'}'}; transform: scale(${'{'}scale.toFixed(3){'}'});"><span class="marker-label" style="font-size:${'{'}fontSize{'}'}px">${'{'}label{'}'}</span></div>`,
      iconSize: [Math.round(metrics.width * scale), Math.round(metrics.height * scale)],
      iconAnchor: [Math.round(metrics.anchorX * scale), Math.round(metrics.anchorY * scale)],
      popupAnchor: [0, metrics.popupY]
    }});
    const marker = L.marker([row.lat, row.lon], {{ icon }});
    const google = row.google_score !== "" ? `<div>Google: ${'{'}Number(row.google_score).toFixed(1){'}'} (${ '{' }row.google_count{'}'} reviews)</div>` : '<div>Google: ?</div>';
    const googleSource = row.google_source_note ? `<div>Source: ${'{'}row.google_source_note{'}'}</div>` : '';
    const googleText = row.google_text_file ? `<div><a href="${'{'}row.google_text_file{'}'}" target="_blank" rel="noreferrer">Review text</a></div>` : '';
    const management = row.management_company ? `<div>Management: ${'{'}row.management_company{'}'}</div>` : '<div>Management: unknown</div>';
    const gtd = row.gtd_url ? `<div><a href="${'{'}row.gtd_url{'}'}" target="_blank" rel="noreferrer">GTD page</a></div>` : '';
    marker.bindPopup(`
      <strong>${'{'}row.name{'}'}</strong><br>
      ${'{'}row.postcode{'}'}<br>
      <div>Near: ${'{'}row.nearby{'}'}</div>
      ${'{'}management{'}'}
      ${'{'}google{'}'}
      ${'{'}googleSource{'}'}
      ${'{'}googleText{'}'}
      <div><a href="${'{'}row.nhs_url{'}'}" target="_blank" rel="noreferrer">NHS page</a></div>
      ${'{'}gtd{'}'}
    `);
    marker.addTo(markerLayer);
  }}
}}

renderManagementList();
renderMarkers();
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
