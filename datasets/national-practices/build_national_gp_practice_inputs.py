#!/usr/bin/env python3
from __future__ import annotations

import csv
import io
import json
import re
import time
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
DATASETS_DIR = BASE_DIR.parent
GM_DATASET_DIR = DATASETS_DIR / "output" / "gtd-greater-manchester-gp-practice-reviews-2026-03-09"
GM_DATASET_CSV = GM_DATASET_DIR / "gtd_greater_manchester_gp_practices.csv"
ENGLAND_PATIENT_COUNTS = DATASETS_DIR / "raw" / "registered_patients" / "gp-reg-pat-prac-all.csv"
ENGLAND_PATIENT_COUNTS_URL = "https://digital.nhs.uk/data-and-information/publications/statistical/patients-registered-at-a-gp-practice"
WALES_PATIENT_COUNTS_URL = "https://statswales.gov.wales/Download/File?fileName=HLTH0426.zip"
SCOTLAND_PATIENT_COUNTS_PAGE_URL = "https://www.opendata.nhs.scot/dataset/gp-practice-contact-details-and-list-sizes"
SCOTLAND_PATIENT_COUNTS_FALLBACK_URLS = [
    "https://www.opendata.nhs.scot/dataset/f23655c3-6e23-4103-a511-a80d998adb90/resource/ceddbf27-0686-4f4b-b9a2-0090d28c3864/download/practice_contact_details_20260101_opendata.csv",
    "https://www.opendata.nhs.scot/dataset/f23655c3-6e23-4103-a511-a80d998adb90/resource/47557411-7eda-4278-9d6d-d26ed2ceab5a/download/practice_contact_details_20251001_opendata.csv",
]
NI_PATIENT_COUNTS_PAGE_URL = "https://www.data.gov.uk/dataset/3d1a6615-5fc9-4f0e-ab2a-d2b0d71fb9ed/gp-practice-list-sizes"
NI_PATIENT_COUNTS_FALLBACK_URLS = [
    "https://admin.opendatani.gov.uk/dataset/3d1a6615-5fc9-4f0e-ab2a-d2b0d71fb9ed/resource/8578e0d4-47f6-4909-9ac4-32643a701e13/download/gp-practice-reference-file-january-2026.csv",
]

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
        "patient_survey_note": "Primary-care patient-experience framework exists, but this builder does not yet pull a practice-level Wales survey feed.",
    },
    "scotland": {
        "patient_survey_name": "Health and Care Experience Survey",
        "patient_survey_status": "equivalent_identified_not_yet_wired",
        "patient_survey_level": "dashboard_or_aggregate",
        "patient_survey_url": "https://publichealthscotland.scot/publications/health-and-care-experience-survey/health-and-care-experience-survey-2024/detailed-experience-ratings-results/",
        "patient_survey_note": "Equivalent survey source exists, but this builder does not yet parse the current Public Health Scotland experience dashboard export.",
    },
    "northern_ireland": {
        "patient_survey_name": "GP patient surveys",
        "patient_survey_status": "discontinued",
        "patient_survey_level": "historic_only",
        "patient_survey_url": "https://www.health-ni.gov.uk/articles/gp-patient-surveys",
        "patient_survey_note": "Northern Ireland GP patient survey ran from 2008/09 to 2010/11 and was then discontinued; no current practice-level equivalent is wired here.",
    },
}

OUTPUT_FIELD_ORDER = [
    "practice_name",
    "canonical_code",
    "postcode",
    "street_address",
    "telephone",
    "email",
    "website_url",
    "nhs_profile_url",
    "latitude",
    "longitude",
    "accepting_new_patients",
    "country",
    "nation",
    "source_type",
    "ods_primary_role_id",
    "ods_primary_role_description",
    "ods_active_roles",
    "ods_org_link",
    "last_change_date",
    "registered_patient_count",
    "registered_patient_count_source",
    "registered_patient_count_source_url",
    "registered_patient_count_snapshot",
    "patient_survey_name",
    "patient_survey_status",
    "patient_survey_level",
    "patient_survey_url",
    "patient_survey_note",
    "google_maps_query",
]


def fetch_text(url: str, *, timeout: int = 60) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Codex national-practices builder)",
            "Accept": "application/json, text/xml, text/html, */*",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8", "ignore")


def fetch_bytes(url: str, *, timeout: int = 60) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Codex national-practices builder)",
            "Accept": "*/*",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


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


def load_england_patient_counts(path: Path) -> dict[str, Any]:
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
    return {
        "counts": counts,
        "source": "nhs_england_patients_registered_at_a_gp_practice",
        "source_url": ENGLAND_PATIENT_COUNTS_URL,
        "snapshot": "",
    }


def extract_urls(page_url: str, pattern: str, prefix: str = "") -> list[str]:
    html = fetch_text(page_url)
    urls: list[str] = []
    for match in re.finditer(pattern, html, flags=re.I):
        url = match.group(0)
        if prefix and url.startswith("/"):
            url = prefix.rstrip("/") + url
        urls.append(url)
    return sorted(set(urls))


def month_number(name: str) -> int:
    months = {
        "january": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
        "july": 7,
        "august": 8,
        "september": 9,
        "october": 10,
        "november": 11,
        "december": 12,
    }
    return months.get(name.lower(), 0)


def url_date_key(url: str) -> tuple[int, int, int, str]:
    exact = re.search(r"(20\d{2})(\d{2})(\d{2})", url)
    if exact:
        return (int(exact.group(1)), int(exact.group(2)), int(exact.group(3)), url)
    month_year = re.search(
        r"(january|february|march|april|may|june|july|august|september|october|november|december)[-_ ]+(20\d{2})",
        url,
        flags=re.I,
    )
    if month_year:
        return (int(month_year.group(2)), month_number(month_year.group(1)), 1, url)
    year_only = re.search(r"(20\d{2})", url)
    if year_only:
        return (int(year_only.group(1)), 0, 0, url)
    return (0, 0, 0, url)


def choose_latest_url(urls: list[str]) -> str:
    if not urls:
        return ""
    return max(urls, key=url_date_key)


def load_wales_patient_counts() -> dict[str, Any]:
    raw = fetch_bytes(WALES_PATIENT_COUNTS_URL, timeout=120)
    zf = zipfile.ZipFile(io.BytesIO(raw))
    csv_name = next((name for name in zf.namelist() if name.lower().endswith(".csv")), "")
    if not csv_name:
        raise RuntimeError("StatsWales patient count zip did not contain a CSV")

    latest_snapshot = 0
    counts: dict[str, int] = {}
    with io.TextIOWrapper(zf.open(csv_name), encoding="latin-1", newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("Gender_ItemName_ENG_STR") != "Total":
                continue
            if row.get("Age_ItemName_ENG_STR") != "All Ages":
                continue
            date_code = str(row.get("Date_Code_INT", "")).strip()
            if not date_code.isdigit():
                continue
            snapshot = int(date_code)
            if snapshot < latest_snapshot:
                continue
            code = str(row.get("Area_Code_STR", "")).strip().upper()
            value = str(row.get("Data_INT", "")).strip()
            if not code or not value:
                continue
            try:
                count = int(float(value))
            except ValueError:
                continue
            if snapshot > latest_snapshot:
                latest_snapshot = snapshot
                counts = {}
            counts[code] = count

    return {
        "counts": counts,
        "source": "statswales_hlth0426",
        "source_url": WALES_PATIENT_COUNTS_URL,
        "snapshot": str(latest_snapshot) if latest_snapshot else "",
    }


def load_scotland_patient_counts() -> dict[str, Any]:
    try:
        discovered = extract_urls(
            SCOTLAND_PATIENT_COUNTS_PAGE_URL,
            r"(https://www\.opendata\.nhs\.scot)?/dataset/[^\"'\s]+/download/[^\"'\s]+\.csv",
            prefix="https://www.opendata.nhs.scot",
        )
    except Exception:
        discovered = []
    source_url = choose_latest_url(discovered) or choose_latest_url(SCOTLAND_PATIENT_COUNTS_FALLBACK_URLS)
    if not source_url:
        raise RuntimeError("Could not determine Scotland patient count source URL")

    counts: dict[str, int] = {}
    text = fetch_bytes(source_url, timeout=120).decode("utf-8-sig", "replace")
    for row in csv.DictReader(io.StringIO(text)):
        practice_code = str(row.get("PracticeCode", "")).strip()
        count_raw = str(row.get("PracticeListSize", "")).strip()
        if not practice_code or not count_raw:
            continue
        try:
            counts[f"S{practice_code.zfill(5)}"] = int(count_raw)
        except ValueError:
            continue

    match = re.search(r"(20\d{2}\d{2}\d{2})", source_url)
    return {
        "counts": counts,
        "source": "nhs_scotland_gp_practice_contact_details_and_list_sizes",
        "source_url": source_url,
        "snapshot": match.group(1) if match else "",
    }


def load_ni_patient_counts() -> dict[str, Any]:
    try:
        discovered = extract_urls(
            NI_PATIENT_COUNTS_PAGE_URL,
            r"(https://admin\.opendatani\.gov\.uk)?/dataset/[^\"'\s]+/download/[^\"'\s]+\.csv",
            prefix="https://admin.opendatani.gov.uk",
        )
    except Exception:
        discovered = []
    source_url = choose_latest_url(discovered) or choose_latest_url(NI_PATIENT_COUNTS_FALLBACK_URLS)
    if not source_url:
        raise RuntimeError("Could not determine Northern Ireland patient count source URL")

    counts: dict[str, int] = {}
    text = fetch_bytes(source_url, timeout=120).decode("utf-8-sig", "replace")
    for row in csv.DictReader(io.StringIO(text)):
        practice_code = str(row.get("PracNo", "")).strip()
        count_raw = str(row.get("Registered_Patients", "")).strip()
        if not practice_code or not count_raw:
            continue
        try:
            counts[f"Z{practice_code.zfill(5)}"] = int(count_raw)
        except ValueError:
            continue

    month_year = re.search(
        r"(january|february|march|april|may|june|july|august|september|october|november|december)[-_ ]+(20\d{2})",
        source_url,
        flags=re.I,
    )
    snapshot = ""
    if month_year:
        snapshot = f"{month_year.group(2)}-{month_number(month_year.group(1)):02d}"

    return {
        "counts": counts,
        "source": "opendatani_gp_practice_reference_file",
        "source_url": source_url,
        "snapshot": snapshot,
    }


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
    patient_count_bundle: dict[str, Any] | None = None,
) -> dict[str, Any]:
    patient_count_bundle = patient_count_bundle or {}
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

    record = {
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
        "registered_patient_count": patient_count_bundle.get("counts", {}).get(code, ""),
        "registered_patient_count_source": str(patient_count_bundle.get("source", "")),
        "registered_patient_count_source_url": str(patient_count_bundle.get("source_url", "")),
        "registered_patient_count_snapshot": str(patient_count_bundle.get("snapshot", "")),
        "google_maps_query": query,
    }
    record.update(SURVEY_METADATA_BY_NATION.get(nation, {}))
    return record


def build_england_wales_records(
    england_count_bundle: dict[str, Any],
    wales_count_bundle: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
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
            nation = "wales" if country == "WALES" or code.startswith("W") else "england"
            count_bundle = wales_count_bundle if nation == "wales" else england_count_bundle
            record = normalize_record(
                org,
                detail,
                nation=nation,
                source_type="ods_gp_practice",
                patient_count_bundle=count_bundle,
            )
            if record["nation"] == "wales":
                wales.append(record)
            else:
                england.append(record)

    england.sort(key=lambda row: (row["postcode"], row["practice_name"], row["canonical_code"]))
    wales.sort(key=lambda row: (row["postcode"], row["practice_name"], row["canonical_code"]))
    return england, wales


def build_role_specific_records(
    role_id: str,
    nation: str,
    source_type: str,
    count_bundle: dict[str, Any],
) -> list[dict[str, Any]]:
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
                    patient_count_bundle=count_bundle,
                )
            )

    records.sort(key=lambda row: (row["postcode"], row["practice_name"], row["canonical_code"]))
    return records


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(OUTPUT_FIELD_ORDER)
    extra_fields = sorted({key for row in rows for key in row.keys() if key not in fieldnames})
    fieldnames.extend(extra_fields)
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
    england_count_bundle = load_england_patient_counts(ENGLAND_PATIENT_COUNTS)
    wales_count_bundle = load_wales_patient_counts()
    scotland_count_bundle = load_scotland_patient_counts()
    ni_count_bundle = load_ni_patient_counts()

    england_rows, wales_rows = build_england_wales_records(england_count_bundle, wales_count_bundle)
    scotland_rows = build_role_specific_records(
        ODS_ROLE_SCOTLAND,
        "scotland",
        "ods_scottish_gp_practice",
        scotland_count_bundle,
    )
    ni_rows = build_role_specific_records(
        ODS_ROLE_NI,
        "northern_ireland",
        "ods_ni_gp_practice",
        ni_count_bundle,
    )

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
            "england_patient_counts": england_count_bundle.get("source_url", ""),
            "wales_patient_counts": wales_count_bundle.get("source_url", ""),
            "scotland_patient_counts": scotland_count_bundle.get("source_url", ""),
            "northern_ireland_patient_counts": ni_count_bundle.get("source_url", ""),
        },
        "patient_survey_sources": {
            nation: {
                "name": meta["patient_survey_name"],
                "status": meta["patient_survey_status"],
                "level": meta["patient_survey_level"],
                "url": meta["patient_survey_url"],
            }
            for nation, meta in SURVEY_METADATA_BY_NATION.items()
        },
        "notes": [
            "England and Wales are derived from active ODS RO177 organisations, filtered down to those with an active RO76 GP PRACTICE role in the detail record.",
            "Scotland and Northern Ireland are derived from active ODS role-specific GP practice lists (RO227 and RO315).",
            "Registered patient counts are now sourced separately for all four nations: NHS England monthly registrations, StatsWales HLTH0426, NHS Scotland GP practice contact details/list sizes, and OpenDataNI GP practice reference files.",
            "Patient-survey coverage is still asymmetric across the UK. England practice-level GP Patient Survey is available; the other nations now carry explicit survey-source metadata rather than silently looking England-like.",
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
        "registered_patient_count_coverage": {
            "england": sum(1 for row in england_rows if row.get("registered_patient_count", "") != ""),
            "wales": sum(1 for row in wales_rows if row.get("registered_patient_count", "") != ""),
            "scotland": sum(1 for row in scotland_rows if row.get("registered_patient_count", "") != ""),
            "northern_ireland": sum(1 for row in ni_rows if row.get("registered_patient_count", "") != ""),
        },
    }
    write_json(SUMMARY_JSON, summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
