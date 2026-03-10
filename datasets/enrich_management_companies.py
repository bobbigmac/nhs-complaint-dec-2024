#!/usr/bin/env python3
from __future__ import annotations

import csv
import html
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse

from build_gtd_gp_practice_dataset import OUTPUT_DIR, write_csv, write_json, write_map, write_readme, write_summary


DATASET_CSV = OUTPUT_DIR / "gtd_greater_manchester_gp_practices.csv"
DATASET_JSON = OUTPUT_DIR / "gtd_greater_manchester_gp_practices.json"
SUMMARY_JSON = OUTPUT_DIR / "summary.json"
README_MD = OUTPUT_DIR / "README.md"
MAP_HTML = OUTPUT_DIR / "map.html"
GOOGLE_REVIEWS_JSON = OUTPUT_DIR / "google_maps_recent_reviews.json"
GOOGLE_FLAGGED_JSON = OUTPUT_DIR / "google_maps_low_confidence_records.json"

KNOWN_DOMAIN_MANAGER_NAMES = {
    "gtdhealthcare.co.uk": ("GTD Healthcare", "nhs_website_domain_known_group", "high"),
    "ssphealth.com": ("SSP Health", "nhs_website_domain_known_group", "high"),
    "spctpractices.co.uk": ("Salford Primary Care Together", "nhs_website_domain_known_group", "high"),
    "towerfamilyhealthcare.co.uk": ("Tower Family Healthcare", "nhs_website_domain_known_group", "high"),
    "mimp.org.uk": ("Manchester Integrative Medical Practice", "nhs_website_domain_known_group", "high"),
    "thestrandandfamilypractice.co.uk": ("The Strand Medical Centre/Family Practice", "nhs_website_domain_known_group", "high"),
    "hopecitadel.org.uk": ("Hope Citadel Healthcare", "nhs_website_domain_known_group", "high"),
}
GENERIC_HOST_SUFFIXES = {"nhs.uk", "nhs.net"}

# Manual overrides for practices with practice-specific domains (verified via practice website)
MANUAL_OVERRIDES: dict[str, tuple[str, str]] = {
    "Y02753": ("Hope Citadel Healthcare", "hopecitadel.org.uk"),  # Hill Top Surgery
    "Y02933": ("Hope Citadel Healthcare", "hopecitadel.org.uk"),  # Hollinwood Medical Practice
    "P85614": ("Hope Citadel Healthcare", "hopecitadel.org.uk"),  # Village Medical Practice
    "Y02827": ("Hope Citadel Healthcare", "hopecitadel.org.uk"),  # John Street Medical Practice
    "P85622": ("Hope Citadel Healthcare", "hopecitadel.org.uk"),  # Glodwick Medical Practice
    "Y02795": ("Hope Citadel Healthcare", "hopecitadel.org.uk"),  # Middleton Health Centre
    "Y02720": ("Hope Citadel Healthcare", "hopecitadel.org.uk"),  # The Kingsway Practice
    "Y02721": ("Hope Citadel Healthcare", "hopecitadel.org.uk"),  # Kirkholt Medical Practice
    "Y02718": ("Hope Citadel Healthcare", "hopecitadel.org.uk"),  # Birtle View Medical Practice
    "Y02890": ("Hope Citadel Healthcare", "hopecitadel.org.uk"),  # Hawthorn MC
}

# Separate from core management. This captures federation, extended-hours, or other
# network/operator links that may coexist with a different core practice operator.
MANUAL_AFFILIATED_GROUP_OVERRIDES: dict[str, tuple[str, str, str, str]] = {
    "P84034": ("South Manchester GP Federation Limited", "cqc_enhanced_access_manual_lookup", "medium", "smgpf.ltd"),
    "P84043": ("South Manchester GP Federation Limited", "cqc_enhanced_access_manual_lookup", "medium", "smgpf.ltd"),
    "P84021": ("South Manchester GP Federation Limited", "cqc_enhanced_access_manual_lookup", "medium", "smgpf.ltd"),
    "P84045": ("South Manchester GP Federation Limited", "cqc_enhanced_access_manual_lookup", "medium", "smgpf.ltd"),
    "P84004": ("Northern Health GPPO Limited", "cqc_location_manual_lookup", "medium", ""),
    "P84064": ("Northern Health GPPO Limited", "cqc_location_manual_lookup", "medium", ""),
    "Y01695": ("Northern Health GPPO Limited", "cqc_location_manual_lookup", "medium", ""),
    "P84673": ("Northern Health GPPO Limited", "cqc_location_manual_lookup", "medium", ""),
    "P84009": ("Primary Care Manchester Ltd", "practice_website_link_manual_lookup", "medium", "manchesterpcp.co.uk"),
    "P84068": ("Primary Care Manchester Ltd", "practice_website_link_manual_lookup", "medium", "manchesterpcp.co.uk"),
}


def load_rows() -> list[dict[str, object]]:
    return json.loads(DATASET_JSON.read_text(encoding="utf-8"))


def load_json_if_possible(path: Path) -> object:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def website_host(url: str) -> str:
    if not url:
        return ""
    host = urlparse(url).netloc.lower().removeprefix("www.")
    return host


def fetch_title(url: str) -> str:
    parsed = urlparse(url)
    candidates = []
    if parsed.scheme and parsed.netloc:
        candidates.append(url)
        candidates.append(f"{parsed.scheme}://{parsed.netloc}/")
    if parsed.netloc:
        candidates.append(f"https://{parsed.netloc}/")
        candidates.append(f"http://{parsed.netloc}/")
    seen: set[str] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        try:
            html_text = subprocess.check_output(
                ["curl", "-LfsS", "--max-time", "20", candidate],
                text=True,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            continue
        match = re.search(r"<title>(.*?)</title>", html_text, flags=re.I | re.S)
        if match:
            return " ".join(html.unescape(match.group(1)).split())
    return ""


def clean_manager_title(title: str) -> str:
    if not title:
        return ""
    title = html.unescape(title).strip()
    title = re.sub(r"^(homepage|home)\s*[-|:]\s*", "", title, flags=re.I)
    for separator in [" | ", " :: ", " – ", " — ", " - "]:
        if separator in title:
            parts = [part.strip() for part in title.split(separator) if part.strip()]
            if not parts:
                continue
            if parts[0].lower() in {"homepage", "home"} and len(parts) > 1:
                title = parts[1]
            else:
                title = parts[0]
            break
    title = re.sub(r"\s+nhs gp surger(?:y|ies).*$", "", title, flags=re.I)
    title = re.sub(r"\s+nhs surgery.*$", "", title, flags=re.I)
    title = re.sub(r"\s+::.*$", "", title)
    return title.strip(" -|:")


def page_kind(result: dict[str, object]) -> str:
    explicit = str(result.get("page_kind", "")).strip()
    if explicit:
        return explicit
    url = str(result.get("google_maps_url", ""))
    if "/place/" in url:
        return "place"
    if "/search/" in url:
        return "search"
    return "other"


def needs_manual_review(result: dict[str, object]) -> bool:
    if bool(result.get("manual_review_required")):
        return True
    status = str(result.get("scan_status", "")).strip()
    if status in {"manual_review_search_result_only", "error"}:
        return True
    return page_kind(result) != "place"


def load_google_maps_metadata() -> dict[str, int]:
    metadata: dict[str, int] = {}
    existing_summary = load_json_if_possible(SUMMARY_JSON)
    if isinstance(existing_summary, dict):
        for key in (
            "google_maps_total_scanned_count",
            "google_maps_manual_review_count",
            "google_maps_flagged_result_count",
        ):
            value = existing_summary.get(key)
            if isinstance(value, int):
                metadata[key] = value

    recent_reviews = load_json_if_possible(GOOGLE_REVIEWS_JSON)
    if isinstance(recent_reviews, list):
        metadata["google_maps_total_scanned_count"] = len(recent_reviews)

    flagged_results = load_json_if_possible(GOOGLE_FLAGGED_JSON)
    if isinstance(flagged_results, list):
        metadata["google_maps_flagged_result_count"] = len(flagged_results)
        metadata["google_maps_manual_review_count"] = sum(
            1 for item in flagged_results if isinstance(item, dict) and needs_manual_review(item)
        )

    return metadata


def host_manager_mapping(rows: list[dict[str, object]]) -> dict[str, tuple[str, str, str]]:
    host_counts = Counter()
    host_examples: dict[str, str] = {}
    for row in rows:
        host = website_host(str(row.get("website_url", "")))
        if not host:
            continue
        host_counts[host] += 1
        host_examples.setdefault(host, str(row.get("website_url", "")))

    title_cache: dict[str, str] = {}
    mapping: dict[str, tuple[str, str, str]] = {}
    for host, count in host_counts.items():
        if host in KNOWN_DOMAIN_MANAGER_NAMES:
            mapping[host] = KNOWN_DOMAIN_MANAGER_NAMES[host]
            continue
        if count < 2:
            continue
        if any(host == suffix or host.endswith(f".{suffix}") for suffix in GENERIC_HOST_SUFFIXES):
            continue
        title = title_cache.setdefault(host, fetch_title(host_examples[host]))
        manager_name = clean_manager_title(title)
        if not manager_name:
            continue
        mapping[host] = (manager_name, "nhs_website_domain_shared", "medium")
    return mapping


def apply_management_enrichment(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    mapping = host_manager_mapping(rows)
    provisional_names: list[str] = []
    for row in rows:
        row.setdefault("management_company_name", "")
        row.setdefault("management_company_source", "")
        row.setdefault("management_company_confidence", "")
        row.setdefault("management_company_domain", "")
        row.setdefault("management_company_group_size", "")
        row.setdefault("affiliated_group_name", "")
        row.setdefault("affiliated_group_source", "")
        row.setdefault("affiliated_group_confidence", "")
        row.setdefault("affiliated_group_domain", "")
        row.setdefault("affiliated_group_group_size", "")

        if bool(row.get("gtd_managed")):
            row["management_company_name"] = "GTD Healthcare"
            row["management_company_source"] = "gtd_anchor_match"
            row["management_company_confidence"] = "high"
            row["management_company_domain"] = "gtdhealthcare.co.uk"
            provisional_names.append("GTD Healthcare")
            continue

        host = website_host(str(row.get("website_url", "")))
        if host and host in mapping:
            manager_name, source, confidence = mapping[host]
            row["management_company_name"] = manager_name
            row["management_company_source"] = source
            row["management_company_confidence"] = confidence
            row["management_company_domain"] = host
            provisional_names.append(manager_name)
            continue

        code = str(row.get("canonical_code", ""))
        if code in MANUAL_OVERRIDES:
            manager_name, domain = MANUAL_OVERRIDES[code]
            row["management_company_name"] = manager_name
            row["management_company_source"] = "manual_lookup"
            row["management_company_confidence"] = "high"
            row["management_company_domain"] = domain
            provisional_names.append(manager_name)

        if code in MANUAL_AFFILIATED_GROUP_OVERRIDES:
            group_name, source, confidence, domain = MANUAL_AFFILIATED_GROUP_OVERRIDES[code]
            row["affiliated_group_name"] = group_name
            row["affiliated_group_source"] = source
            row["affiliated_group_confidence"] = confidence
            row["affiliated_group_domain"] = domain

    name_counts = Counter(provisional_names)
    affiliated_name_counts = Counter(
        str(row.get("affiliated_group_name", ""))
        for row in rows
        if str(row.get("affiliated_group_name", ""))
    )
    for row in rows:
        name = str(row.get("management_company_name", ""))
        row["management_company_group_size"] = name_counts.get(name, "") if name else ""
        affiliated_name = str(row.get("affiliated_group_name", ""))
        row["affiliated_group_group_size"] = affiliated_name_counts.get(affiliated_name, "") if affiliated_name else ""
    return rows


def atomic_write(path: Path, write_fn) -> None:
    with NamedTemporaryFile("w", delete=False, dir=path.parent, encoding="utf-8") as handle:
        temp_path = Path(handle.name)
    try:
        write_fn(temp_path)
        temp_path.replace(path)
    finally:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)


def write_all(rows: list[dict[str, object]]) -> None:
    summary_holder: dict[str, object] = {}
    google_maps_metadata = load_google_maps_metadata()

    def write_summary_temp(temp_path: Path) -> None:
        summary = write_summary(temp_path, rows)
        summary.update(google_maps_metadata)
        temp_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        summary_holder.update(summary)

    atomic_write(DATASET_CSV, lambda temp_path: write_csv(temp_path, rows))
    atomic_write(DATASET_JSON, lambda temp_path: write_json(temp_path, rows))
    atomic_write(SUMMARY_JSON, write_summary_temp)
    atomic_write(README_MD, lambda temp_path: write_readme(temp_path, summary_holder))
    atomic_write(MAP_HTML, lambda temp_path: write_map(temp_path, rows))


def main() -> int:
    rows = load_rows()
    rows = apply_management_enrichment(rows)
    write_all(rows)
    identified = sum(1 for row in rows if row.get("management_company_name"))
    distinct = len({row.get("management_company_name") for row in rows if row.get("management_company_name")})
    affiliated_identified = sum(1 for row in rows if row.get("affiliated_group_name"))
    affiliated_distinct = len({row.get("affiliated_group_name") for row in rows if row.get("affiliated_group_name")})
    print(
        json.dumps(
            {
                "identified_count": identified,
                "distinct_count": distinct,
                "affiliated_identified_count": affiliated_identified,
                "affiliated_distinct_count": affiliated_distinct,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
