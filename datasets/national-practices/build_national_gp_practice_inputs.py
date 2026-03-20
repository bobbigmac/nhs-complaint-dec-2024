#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
DATASETS_DIR = BASE_DIR.parent
GM_DATASET_DIR = DATASETS_DIR / "output" / "gtd-greater-manchester-gp-practice-reviews-2026-03-09"
GM_DATASET_CSV = GM_DATASET_DIR / "gtd_greater_manchester_gp_practices.csv"
ENGLAND_PATIENT_COUNTS = DATASETS_DIR / "raw" / "registered_patients" / "gp-reg-pat-prac-all.csv"

OUTPUT_DIR = BASE_DIR / "output"
RAW_DIR = BASE_DIR / "raw"
SUMMARY_JSON = OUTPUT_DIR / "summary.json"

ODS_BASE = "https://directory.spineservices.nhs.uk/ORD/2-0-0"
ODS_ORGS_URL = ODS_BASE + "/organisations"
ODS_ROLE_ENGLAND_WALES = "RO177"
ODS_ROLE_GP = "RO76"
ODS_ROLE_SCOTLAND = "RO227"
ODS_ROLE_NI = "RO315"
ODS_LIMIT = 500
DETAIL_WORKERS = 16


def fetch_text(url: str, *, data: bytes | None = None, headers: dict[str, str] | None = None, timeout: int = 60) -> str:
    req = urllib.request.Request(
        url,
        data=data,
        headers=headers or {
            "User-Agent": "Mozilla/5.0 (Codex national-practices builder)",
            "Accept": "application/json, text/xml, */*",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8", "ignore")


def fetch_json(url: str, *, timeout: int = 60, retries: int = 3) -> Any:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            return json.loads(fetch_text(url, timeout=timeout))
        except Exception as exc:  # pragma: no cover - network variability
            last_error = exc
            if attempt == retries - 1:
                break
            time.sleep(0.5 * (attempt + 1))
    if last_error is not None:
        raise last_error
    raise RuntimeError(f"Failed to fetch JSON from {url}")


def load_existing_codes(path: Path) -> set[str]:
    with path.open() as handle:
        return {
            str(row.get("canonical_code", "")).strip()
            for row in csv.DictReader(handle)
            if str(row.get("canonical_code", "")).strip()
        }


def load_england_patient_counts(path: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    with path.open() as handle:
        for row in csv.DictReader(handle):
            if row.get("TYPE") != "GP" or row.get("SEX") != "ALL" or row.get("AGE") != "ALL":
                continue
            code = str(row.get("CODE", "")).strip()
            if not code:
                continue
            try:
                counts[code] = int(str(row.get("NUMBER_OF_PATIENTS", "")).replace(",", ""))
            except ValueError:
                continue
    return counts


def iter_ods_organisations(primary_role_id: str) -> list[dict[str, Any]]:
    organisations: list[dict[str, Any]] = []
    offset = 0
    while True:
        url = f"{ODS_ORGS_URL}?PrimaryRoleId={primary_role_id}&Status=Active&Limit={ODS_LIMIT}"
        if offset > 0:
            url += f"&Offset={offset}"
        payload = fetch_json(url)
        batch = payload.get("Organisations", [])
        if not batch:
            break
        organisations.extend(batch)
        offset += len(batch)
    return organisations


def role_is_active(role: dict[str, Any], role_id: str) -> bool:
    return str(role.get("id", "")).strip() == role_id and str(role.get("Status", "")).strip() == "Active"


def active_role_ids(detail: dict[str, Any]) -> set[str]:
    roles = detail.get("Roles", {}).get("Role", []) or []
    return {
        str(role.get("id", "")).strip()
        for role in roles
        if str(role.get("Status", "")).strip() == "Active"
    }


def join_address(location: dict[str, Any]) -> str:
    parts = [
        str(location.get("AddrLn1", "")).strip(),
        str(location.get("AddrLn2", "")).strip(),
        str(location.get("Town", "")).strip(),
    ]
    return ", ".join(part for part in parts if part)


def first_contact(detail: dict[str, Any], contact_type: str) -> str:
    contacts = detail.get("Contacts", {}).get("Contact", []) or []
    for contact in contacts:
        if str(contact.get("type", "")).strip().lower() == contact_type:
            return str(contact.get("value", "")).strip()
    return ""


def fetch_detail(org_link: str) -> dict[str, Any]:
    payload = fetch_json(org_link, retries=4)
    return payload.get("Organisation", {})


def normalize_record(
    org: dict[str, Any],
    detail: dict[str, Any],
    *,
    nation: str,
    source_type: str,
    patient_count: int | None = None,
) -> dict[str, Any]:
    location = detail.get("GeoLoc", {}).get("Location", {}) or {}
    code = str(org.get("OrgId", "")).strip()
    name = str(detail.get("Name", "") or org.get("Name", "")).strip()
    postcode = str(location.get("PostCode", "") or org.get("PostCode", "")).strip()
    phone = first_contact(detail, "tel")
    email = first_contact(detail, "email")
    website = first_contact(detail, "url")
    address = join_address(location)
    country = str(location.get("Country", "")).strip() or nation.upper()
    active_roles = sorted(active_role_ids(detail))
    query = f"{name} {postcode}".strip()

    return {
        "practice_name": name,
        "canonical_code": code,
        "postcode": postcode,
        "street_address": address,
        "telephone": phone,
        "email": email,
        "website_url": website,
        "nhs_profile_url": "",
        "latitude": "",
        "longitude": "",
        "accepting_new_patients": "",
        "country": country,
        "nation": nation,
        "source_type": source_type,
        "ods_primary_role_id": str(org.get("PrimaryRoleId", "")).strip(),
        "ods_primary_role_description": str(org.get("PrimaryRoleDescription", "")).strip(),
        "ods_active_roles": ",".join(active_roles),
        "ods_org_link": str(org.get("OrgLink", "")).strip(),
        "last_change_date": str(org.get("LastChangeDate", "")).strip(),
        "registered_patient_count": patient_count if patient_count is not None else "",
        "google_maps_query": query,
    }


def build_england_wales_records(patient_counts: dict[str, int]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    organisations = iter_ods_organisations(ODS_ROLE_ENGLAND_WALES)
    england: list[dict[str, Any]] = []
    wales: list[dict[str, Any]] = []

    def load_one(org: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        return org, fetch_detail(str(org.get("OrgLink", "")).strip())

    with ThreadPoolExecutor(max_workers=DETAIL_WORKERS) as executor:
        futures = [executor.submit(load_one, org) for org in organisations]
        for future in as_completed(futures):
            org, detail = future.result()
            roles = active_role_ids(detail)
            if ODS_ROLE_GP not in roles:
                continue
            location = detail.get("GeoLoc", {}).get("Location", {}) or {}
            country = str(location.get("Country", "")).strip().upper()
            code = str(org.get("OrgId", "")).strip()
            record = normalize_record(
                org,
                detail,
                nation="wales" if country == "WALES" or code.startswith("W") else "england",
                source_type="ods_gp_practice",
                patient_count=patient_counts.get(code),
            )
            if record["nation"] == "wales":
                wales.append(record)
            else:
                england.append(record)

    england.sort(key=lambda row: (row["postcode"], row["practice_name"], row["canonical_code"]))
    wales.sort(key=lambda row: (row["postcode"], row["practice_name"], row["canonical_code"]))
    return england, wales


def build_role_specific_records(role_id: str, nation: str, source_type: str) -> list[dict[str, Any]]:
    organisations = iter_ods_organisations(role_id)
    records: list[dict[str, Any]] = []

    def load_one(org: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        return org, fetch_detail(str(org.get("OrgLink", "")).strip())

    with ThreadPoolExecutor(max_workers=DETAIL_WORKERS) as executor:
        futures = [executor.submit(load_one, org) for org in organisations]
        for future in as_completed(futures):
            org, detail = future.result()
            records.append(
                normalize_record(
                    org,
                    detail,
                    nation=nation,
                    source_type=source_type,
                )
            )

    records.sort(key=lambda row: (row["postcode"], row["practice_name"], row["canonical_code"]))
    return records


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    existing_codes = load_existing_codes(GM_DATASET_CSV)
    england_patient_counts = load_england_patient_counts(ENGLAND_PATIENT_COUNTS)

    england_rows, wales_rows = build_england_wales_records(england_patient_counts)
    scotland_rows = build_role_specific_records(ODS_ROLE_SCOTLAND, "scotland", "ods_scottish_gp_practice")
    ni_rows = build_role_specific_records(ODS_ROLE_NI, "northern_ireland", "ods_ni_gp_practice")

    all_rows = england_rows + wales_rows + scotland_rows + ni_rows
    remaining_rows = [row for row in all_rows if row["canonical_code"] not in existing_codes]
    remaining_rows.sort(key=lambda row: (row["nation"], row["postcode"], row["practice_name"], row["canonical_code"]))

    write_csv(OUTPUT_DIR / "england_gp_practices.csv", england_rows)
    write_csv(OUTPUT_DIR / "wales_gp_practices.csv", wales_rows)
    write_csv(OUTPUT_DIR / "scotland_gp_practices.csv", scotland_rows)
    write_csv(OUTPUT_DIR / "northern_ireland_gp_practices.csv", ni_rows)
    write_csv(OUTPUT_DIR / "uk_gp_practices_not_in_current_dataset.csv", remaining_rows)

    write_json(OUTPUT_DIR / "england_gp_practices.json", england_rows)
    write_json(OUTPUT_DIR / "wales_gp_practices.json", wales_rows)
    write_json(OUTPUT_DIR / "scotland_gp_practices.json", scotland_rows)
    write_json(OUTPUT_DIR / "northern_ireland_gp_practices.json", ni_rows)
    write_json(OUTPUT_DIR / "uk_gp_practices_not_in_current_dataset.json", remaining_rows)

    summary = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sources": {
            "ods_active_prescribing_cost_centres": f"{ODS_ORGS_URL}?PrimaryRoleId={ODS_ROLE_ENGLAND_WALES}&Status=Active",
            "ods_scottish_gp_practices": f"{ODS_ORGS_URL}?PrimaryRoleId={ODS_ROLE_SCOTLAND}&Status=Active",
            "ods_northern_ireland_gp_practices": f"{ODS_ORGS_URL}?PrimaryRoleId={ODS_ROLE_NI}&Status=Active",
            "england_patient_counts": str(ENGLAND_PATIENT_COUNTS.relative_to(DATASETS_DIR)),
        },
        "notes": [
            "England and Wales are derived from active ODS RO177 organisations, filtered down to those with an active RO76 GP PRACTICE role in the detail record.",
            "Scotland and Northern Ireland are derived from active ODS role-specific GP practice lists (RO227 and RO315).",
            "These files are collector-friendly short-form inputs for future Google Maps review lookups, not full-review crawl outputs.",
            "The combined UK file excludes canonical codes already present in the Greater Manchester dataset.",
        ],
        "counts": {
            "england": len(england_rows),
            "wales": len(wales_rows),
            "scotland": len(scotland_rows),
            "northern_ireland": len(ni_rows),
            "uk_all": len(all_rows),
            "uk_not_in_current_dataset": len(remaining_rows),
            "excluded_existing_codes": len(existing_codes & {row["canonical_code"] for row in all_rows}),
        },
    }
    write_json(SUMMARY_JSON, summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
