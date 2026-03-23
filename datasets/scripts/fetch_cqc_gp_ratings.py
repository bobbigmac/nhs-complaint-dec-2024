#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any
from xml.etree.ElementTree import iterparse
from zipfile import ZipFile


BASE_DIR = Path(__file__).resolve().parents[1]
CQC_RAW_DIR = BASE_DIR / "raw" / "cqc"
ENGLAND_GP_PRACTICES_CSV = BASE_DIR / "national-practices" / "output" / "england_gp_practices.csv"
USING_CQC_DATA_URL = "https://www.cqc.org.uk/about-us/transparency/using-cqc-data"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0 Safari/537.36"
GP_RATINGS_JSON = CQC_RAW_DIR / "cqc_gp_location_ratings.json"
GP_RATINGS_INDEX_JSON = CQC_RAW_DIR / "cqc_gp_location_index.json"
GP_RATINGS_CSV = CQC_RAW_DIR / "cqc_gp_location_ratings.csv"
GP_RATINGS_MANIFEST = CQC_RAW_DIR / "cqc_gp_location_ratings_manifest.json"
MAX_LOCATION_COLUMNS = 40

TABLE = "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table"
ROW = "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-row"
CELL = "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-cell"
P = "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p"
REPEAT = "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}number-columns-repeated"
NAME = "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}name"


def fetch_text(url: str) -> str:
    completed = subprocess.run(
        [
            "curl",
            "-LfsS",
            "--retry",
            "2",
            "--connect-timeout",
            "20",
            "--max-time",
            "180",
            "-A",
            USER_AGENT,
            url,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def download(url: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0:
        return
    subprocess.run(
        [
            "curl",
            "-LfsS",
            "--retry",
            "2",
            "--connect-timeout",
            "20",
            "--max-time",
            "300",
            "-A",
            USER_AGENT,
            "-o",
            str(path),
            url,
        ],
        check=True,
    )


def discover_source_urls() -> dict[str, str]:
    html = fetch_text(USING_CQC_DATA_URL)
    candidates = re.findall(r"/sites/default/files/[^\"]+\.(?:csv|zip|ods)", html, flags=re.I)
    absolute = [f"https://www.cqc.org.uk{item}" for item in candidates]
    directory_csv = next((url for url in absolute if "CQC_directory.csv" in url), "")
    latest_ratings_ods = next((url for url in absolute if "Latest_ratings.ods" in url), "")
    if not directory_csv or not latest_ratings_ods:
        raise RuntimeError("Could not discover required CQC source URLs from official page")
    return {
        "directory_csv": directory_csv,
        "latest_ratings_ods": latest_ratings_ods,
    }


def cell_text(cell: Any) -> str:
    parts: list[str] = []
    for child in cell.iter(P):
        if child.text:
            parts.append(child.text)
    return "".join(parts).strip()


def parse_date(value: str) -> tuple[int, int, int]:
    normalized = str(value or "").strip()
    try:
        dt = datetime.strptime(normalized, "%d/%m/%Y")
        return (dt.year, dt.month, dt.day)
    except ValueError:
        return (0, 0, 0)


def normalize_cqc_url(value: str) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        return ""
    normalized = normalized.replace("http://", "https://").rstrip("/")
    return normalized


def load_directory_website_lookup(path: Path) -> dict[str, str]:
    lookup: dict[str, str] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.reader(fh)
        header: list[str] | None = None
        for row in reader:
            if row and row[:4] == ["Name", "Also known as", "Address", "Postcode"]:
                header = row
                break
        if header is None:
            return lookup
        for row in reader:
            if not row:
                continue
            if len(row) < len(header):
                row = row + [""] * (len(header) - len(row))
            record = dict(zip(header, row))
            location_url = normalize_cqc_url(record.get("Location URL", ""))
            service_website = str(record.get("Service's website (if available)", "")).strip()
            if location_url and service_website:
                lookup[location_url] = service_website
    return lookup


def load_known_england_gp_codes(path: Path = ENGLAND_GP_PRACTICES_CSV) -> set[str]:
    codes: set[str] = set()
    if not path.exists():
        return codes
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            code = str(row.get("canonical_code", "")).strip().upper()
            if code:
                codes.add(code)
    return codes


def row_values(row_elem: Any, *, max_columns: int) -> list[str]:
    values: list[str] = []
    for cell in row_elem.findall(CELL):
        remaining = max_columns - len(values)
        if remaining <= 0:
            break
        repeat = min(int(cell.attrib.get(REPEAT, "1")), remaining)
        values.extend([cell_text(cell)] * repeat)
    return values


def better_record(candidate: dict[str, Any], existing: dict[str, Any] | None) -> bool:
    if existing is None:
        return True
    candidate_key = (
        parse_date(str(candidate.get("publication_date", ""))),
        1 if str(candidate.get("inherited_rating", "")).strip().upper() != "Y" else 0,
    )
    existing_key = (
        parse_date(str(existing.get("publication_date", ""))),
        1 if str(existing.get("inherited_rating", "")).strip().upper() != "Y" else 0,
    )
    return candidate_key > existing_key


def stream_gp_ratings_from_ods(
    path: Path, website_by_url: dict[str, str], known_gp_codes: set[str]
) -> tuple[dict[str, dict[str, Any]], dict[str, int]]:
    by_code: dict[str, dict[str, Any]] = {}
    stats = {
        "rows_seen": 0,
        "rows_matching_known_gp_code": 0,
        "overall_rows_matching_known_gp_code": 0,
        "rows_with_known_gp_ods_code": 0,
        "distinct_ods_codes": 0,
        "known_gp_code_count": len(known_gp_codes),
    }
    header: list[str] | None = None
    current_table = None

    with ZipFile(path) as zf, zf.open("content.xml") as fh:
        for event, elem in iterparse(fh, events=("start", "end")):
            if event == "start" and elem.tag == TABLE:
                current_table = elem.attrib.get(NAME)
            elif event == "end" and elem.tag == ROW and current_table == "Locations":
                values = row_values(elem, max_columns=MAX_LOCATION_COLUMNS)
                if header is None:
                    header = list(values)
                    while header and not header[-1]:
                        header.pop()
                    elem.clear()
                    continue
                if not values:
                    elem.clear()
                    continue
                stats["rows_seen"] += 1
                if stats["rows_seen"] % 5000 == 0:
                    print(
                        f"streamed {stats['rows_seen']:,} location rows; "
                        f"{stats['rows_matching_known_gp_code']:,} GP-code rows; "
                        f"{stats['overall_rows_matching_known_gp_code']:,} GP overall rows",
                        flush=True,
                    )
                row = dict(zip(header, values))
                ods_code = str(row.get("Location ODS Code", "")).strip().upper()
                if not ods_code or ods_code not in known_gp_codes:
                    elem.clear()
                    continue
                stats["rows_matching_known_gp_code"] += 1
                if str(row.get("Domain", "")).strip() != "Overall":
                    elem.clear()
                    continue
                stats["overall_rows_matching_known_gp_code"] += 1
                stats["rows_with_known_gp_ods_code"] += 1
                location_url = normalize_cqc_url(row.get("URL", ""))
                candidate = {
                    "ods_code": ods_code,
                    "location_id": str(row.get("Location ID", "")).strip(),
                    "location_name": str(row.get("Location Name", "")).strip(),
                    "location_type": str(row.get("Location Type", "")).strip(),
                    "inspection_category": str(row.get("Location Primary Inspection Category", "")).strip(),
                    "street_address": str(row.get("Location Street Address", "")).strip(),
                    "address_line_2": str(row.get("Location Address Line 2", "")).strip(),
                    "city": str(row.get("Location City", "")).strip(),
                    "postcode": str(row.get("Location Post Code", "")).strip(),
                    "local_authority": str(row.get("Location Local Authority", "")).strip(),
                    "region": str(row.get("Location Region", "")).strip(),
                    "nhs_region": str(row.get("Location NHS Region", "")).strip(),
                    "service_population_group": str(row.get("Service / Population Group", "")).strip(),
                    "domain": str(row.get("Domain", "")).strip(),
                    "overall_rating": str(row.get("Latest Rating", "")).strip(),
                    "publication_date": str(row.get("Publication Date", "")).strip(),
                    "report_type": str(row.get("Report Type", "")).strip(),
                    "inherited_rating": str(row.get("Inherited Rating (Y/N)", "")).strip(),
                    "url": location_url,
                    "service_website": website_by_url.get(location_url, ""),
                    "provider_id": str(row.get("Provider ID", "")).strip(),
                    "provider_name": str(row.get("Provider Name", "")).strip(),
                    "brand_id": str(row.get("Brand ID", "")).strip(),
                    "brand_name": str(row.get("Brand Name", "")).strip(),
                }
                existing = by_code.get(ods_code)
                if better_record(candidate, existing):
                    by_code[ods_code] = candidate
                elem.clear()

    stats["distinct_ods_codes"] = len(by_code)
    return by_code, stats


def write_outputs(records_by_code: dict[str, dict[str, Any]], manifest: dict[str, Any]) -> None:
    ordered = [records_by_code[code] for code in sorted(records_by_code)]
    json_payload = json.dumps(ordered, ensure_ascii=False, indent=2)
    json_tmp = GP_RATINGS_JSON.with_suffix(GP_RATINGS_JSON.suffix + ".tmp")
    json_tmp.write_text(json_payload, encoding="utf-8")
    json_tmp.replace(GP_RATINGS_JSON)
    index_payload = json.dumps(records_by_code, ensure_ascii=False, indent=2, sort_keys=True)
    index_tmp = GP_RATINGS_INDEX_JSON.with_suffix(GP_RATINGS_INDEX_JSON.suffix + ".tmp")
    index_tmp.write_text(index_payload, encoding="utf-8")
    index_tmp.replace(GP_RATINGS_INDEX_JSON)
    csv_fieldnames = [
        "ods_code",
        "location_id",
        "location_name",
        "location_type",
        "domain",
        "overall_rating",
        "publication_date",
        "report_type",
        "inherited_rating",
        "url",
        "service_website",
        "provider_id",
        "provider_name",
        "inspection_category",
        "service_population_group",
        "street_address",
        "address_line_2",
        "city",
        "postcode",
        "local_authority",
        "region",
        "nhs_region",
        "brand_id",
        "brand_name",
    ]
    csv_tmp = GP_RATINGS_CSV.with_suffix(GP_RATINGS_CSV.suffix + ".tmp")
    with csv_tmp.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=csv_fieldnames,
        )
        writer.writeheader()
        writer.writerows({key: row.get(key, "") for key in csv_fieldnames} for row in ordered)
    csv_tmp.replace(GP_RATINGS_CSV)
    manifest_tmp = GP_RATINGS_MANIFEST.with_suffix(GP_RATINGS_MANIFEST.suffix + ".tmp")
    manifest_tmp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest_tmp.replace(GP_RATINGS_MANIFEST)


def main() -> int:
    CQC_RAW_DIR.mkdir(parents=True, exist_ok=True)
    urls = discover_source_urls()
    directory_csv_path = CQC_RAW_DIR / Path(urls["directory_csv"]).name
    latest_ratings_ods_path = CQC_RAW_DIR / Path(urls["latest_ratings_ods"]).name
    print(f"Using official CQC data page: {USING_CQC_DATA_URL}", flush=True)
    print(f"Directory CSV: {directory_csv_path.name}", flush=True)
    print(f"Latest ratings ODS: {latest_ratings_ods_path.name}", flush=True)
    download(urls["directory_csv"], directory_csv_path)
    download(urls["latest_ratings_ods"], latest_ratings_ods_path)
    website_by_url = load_directory_website_lookup(directory_csv_path)
    known_gp_codes = load_known_england_gp_codes()
    print(f"Loaded {len(website_by_url):,} CQC directory website mappings", flush=True)
    print(f"Loaded {len(known_gp_codes):,} known England GP ODS codes", flush=True)
    print("Streaming GP ratings from ODS...", flush=True)
    by_code, stats = stream_gp_ratings_from_ods(latest_ratings_ods_path, website_by_url, known_gp_codes)
    manifest = {
        "source_page": USING_CQC_DATA_URL,
        "directory_csv_url": urls["directory_csv"],
        "latest_ratings_ods_url": urls["latest_ratings_ods"],
        "directory_csv_path": str(directory_csv_path),
        "latest_ratings_ods_path": str(latest_ratings_ods_path),
        "generated_files": {
            "gp_ratings_json": str(GP_RATINGS_JSON),
            "gp_ratings_index_json": str(GP_RATINGS_INDEX_JSON),
            "gp_ratings_csv": str(GP_RATINGS_CSV),
            "manifest_json": str(GP_RATINGS_MANIFEST),
        },
        "stats": stats,
    }
    write_outputs(by_code, manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
