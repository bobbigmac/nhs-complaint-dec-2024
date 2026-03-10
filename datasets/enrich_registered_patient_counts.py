#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse

from build_gtd_gp_practice_dataset import (
    OUTPUT_DIR,
    ensure_registered_patients_cache,
    fetch_text,
    write_csv,
    write_json,
    write_map,
    write_readme,
    write_summary,
)


DATASET_CSV = OUTPUT_DIR / "gtd_greater_manchester_gp_practices.csv"
DATASET_JSON = OUTPUT_DIR / "gtd_greater_manchester_gp_practices.json"
SUMMARY_JSON = OUTPUT_DIR / "summary.json"
README_MD = OUTPUT_DIR / "README.md"
MAP_HTML = OUTPUT_DIR / "map.html"
RECONCILIATION_JSON = OUTPUT_DIR / "registered_patient_count_reconciliation.json"
RECONCILIATION_MD = OUTPUT_DIR / "registered_patient_count_reconciliation.md"


def atomic_write(path: Path, write_fn) -> None:
    with NamedTemporaryFile("w", delete=False, dir=path.parent, encoding="utf-8") as handle:
        temp_path = Path(handle.name)
    try:
        write_fn(temp_path)
        temp_path.replace(path)
    finally:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)


def load_rows() -> list[dict[str, object]]:
    return json.loads(DATASET_JSON.read_text(encoding="utf-8"))


def website_host(url: str) -> str:
    if not url:
        return ""
    return urlparse(url).netloc.lower().removeprefix("www.")


def load_registered_patient_rows() -> tuple[dict[str, int], dict[str, list[dict[str, str]]]]:
    direct_by_code: dict[str, int] = {}
    by_postcode: dict[str, list[dict[str, str]]] = {}
    with ensure_registered_patients_cache().open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row.get("SEX") != "ALL" or row.get("AGE") != "ALL":
                continue
            code = str(row.get("CODE", "")).strip().upper()
            postcode = str(row.get("POSTCODE", "")).strip().upper()
            count = int(row.get("NUMBER_OF_PATIENTS", "0") or "0")
            if not code:
                continue
            direct_by_code[code] = count
            if postcode:
                by_postcode.setdefault(postcode, []).append(
                    {"code": code, "postcode": postcode, "count": str(count)}
                )
    return direct_by_code, by_postcode


def branch_parent_code(code: str) -> str:
    if len(code) > 3 and code[-3:].isdigit():
        return code[:-3]
    return ""


def branch_like_page(url: str, cache: dict[str, bool]) -> bool:
    if url in cache:
        return cache[url]
    try:
        html = fetch_text(url)
    except Exception:
        cache[url] = False
        return False
    branch_like = bool(re.search(r"\bbranch\b", html, flags=re.I))
    cache[url] = branch_like
    return branch_like


def candidate_from_shared_website(
    row: dict[str, object], rows: list[dict[str, object]]
) -> tuple[str, int, str, str] | None:
    host = website_host(str(row.get("website_url", "")))
    if not host:
        return None
    peers = [
        peer
        for peer in rows
        if str(peer.get("canonical_code", "")) != str(row.get("canonical_code", ""))
        and website_host(str(peer.get("website_url", ""))) == host
        and str(peer.get("registered_patient_count", "")).strip() != ""
    ]
    distinct = {(str(peer["canonical_code"]), int(peer["registered_patient_count"])) for peer in peers}
    if len(distinct) != 1:
        return None
    peer_code, peer_count = next(iter(distinct))
    return peer_code, peer_count, "shared_website_domain_peer", "low"


def candidate_from_unique_postcode(
    row: dict[str, object], by_postcode: dict[str, list[dict[str, str]]]
) -> tuple[str, int, str, str] | None:
    postcode = str(row.get("postcode", "")).strip().upper()
    candidates = by_postcode.get(postcode, [])
    if len(candidates) != 1:
        return None
    candidate = candidates[0]
    return candidate["code"], int(candidate["count"]), "unique_exact_postcode", "medium"


def apply_registered_patient_reconciliation(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    direct_by_code, by_postcode = load_registered_patient_rows()
    branch_cache: dict[str, bool] = {}

    for row in rows:
        row.setdefault("registered_patient_count_source", "")
        row.setdefault("registered_patient_count_candidate", "")
        row.setdefault("registered_patient_count_candidate_code", "")
        row.setdefault("registered_patient_count_candidate_source", "")
        row.setdefault("registered_patient_count_candidate_confidence", "")

        direct_value = str(row.get("registered_patient_count", "")).strip()
        if direct_value:
            row["registered_patient_count_source"] = "nhs_monthly_direct"
            row["registered_patient_count_candidate"] = ""
            row["registered_patient_count_candidate_code"] = ""
            row["registered_patient_count_candidate_source"] = ""
            row["registered_patient_count_candidate_confidence"] = ""
            continue

        code = str(row.get("canonical_code", "")).strip().upper()
        candidate: tuple[str, int, str, str] | None = None

        parent_code = branch_parent_code(code)
        if parent_code and parent_code in direct_by_code:
            candidate = (
                parent_code,
                direct_by_code[parent_code],
                "trimmed_parent_practice_code",
                "medium",
            )

        if candidate is None:
            candidate = candidate_from_unique_postcode(row, by_postcode)

        if candidate is None:
            candidate = candidate_from_shared_website(row, rows)

        if candidate is not None:
            candidate_code, candidate_count, candidate_source, candidate_confidence = candidate
            row["registered_patient_count_candidate"] = candidate_count
            row["registered_patient_count_candidate_code"] = candidate_code
            row["registered_patient_count_candidate_source"] = candidate_source
            row["registered_patient_count_candidate_confidence"] = candidate_confidence

        if not row.get("registered_patient_count_source", "") and branch_like_page(
            str(row.get("nhs_profile_url", "")), branch_cache
        ):
            row["registered_patient_count_source"] = "nhs_branch_or_site_page"

    return rows


def build_reconciliation_records(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    branch_cache: dict[str, bool] = {}
    for row in rows:
        if str(row.get("registered_patient_count", "")).strip():
            continue
        nhs_url = str(row.get("nhs_profile_url", ""))
        records.append(
            {
                "canonical_code": row.get("canonical_code", ""),
                "practice_name": row.get("practice_name", ""),
                "postcode": row.get("postcode", ""),
                "nhs_profile_url": nhs_url,
                "branch_like_code_pattern": bool(branch_parent_code(str(row.get("canonical_code", "")))),
                "branch_like_nhs_page": branch_like_page(nhs_url, branch_cache),
                "candidate_code": row.get("registered_patient_count_candidate_code", ""),
                "candidate_count": row.get("registered_patient_count_candidate", ""),
                "candidate_source": row.get("registered_patient_count_candidate_source", ""),
                "candidate_confidence": row.get("registered_patient_count_candidate_confidence", ""),
            }
        )
    return records


def write_reconciliation_report(path: Path, rows: list[dict[str, object]], records: list[dict[str, object]]) -> None:
    candidate_count = sum(1 for item in records if item["candidate_count"] != "")
    unresolved = [item for item in records if item["candidate_count"] == ""]
    source_counts = Counter(
        str(item["candidate_source"]) for item in records if str(item["candidate_source"]).strip()
    )
    branch_page_count = sum(1 for item in records if item["branch_like_nhs_page"])

    lines = [
        "# Registered Patient Count Reconciliation",
        "",
        f"- Direct NHS monthly patient count coverage: {sum(1 for row in rows if str(row.get('registered_patient_count', '')).strip())}",
        f"- Missing direct count rows: {len(records)}",
        f"- Missing rows with candidate match: {candidate_count}",
        f"- Missing rows still unresolved: {len(unresolved)}",
        f"- Missing rows whose NHS page looks branch/site-like: {branch_page_count}",
        "",
        "## Candidate Sources",
        "",
    ]
    for source, count in sorted(source_counts.items()):
        lines.append(f"- `{source}`: {count}")
    lines.extend(["", "## Still Unresolved", ""])
    if unresolved:
        lines.append("| Code | Practice | Postcode | Branch-like NHS page |")
        lines.append("|---|---|---:|---|")
        for item in unresolved:
            lines.append(
                f"| {item['canonical_code']} | {item['practice_name']} | {item['postcode']} | {item['branch_like_nhs_page']} |"
            )
    else:
        lines.append("None.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_all(rows: list[dict[str, object]], records: list[dict[str, object]]) -> None:
    summary_holder: dict[str, object] = {}

    def write_summary_temp(temp_path: Path) -> None:
        summary = write_summary(temp_path, rows)
        summary_holder.update(summary)

    atomic_write(DATASET_CSV, lambda temp_path: write_csv(temp_path, rows))
    atomic_write(DATASET_JSON, lambda temp_path: write_json(temp_path, rows))
    atomic_write(SUMMARY_JSON, write_summary_temp)
    atomic_write(README_MD, lambda temp_path: write_readme(temp_path, summary_holder))
    atomic_write(MAP_HTML, lambda temp_path: write_map(temp_path, rows))
    atomic_write(RECONCILIATION_JSON, lambda temp_path: temp_path.write_text(json.dumps(records, indent=2), encoding="utf-8"))
    atomic_write(RECONCILIATION_MD, lambda temp_path: write_reconciliation_report(temp_path, rows, records))


def main() -> int:
    rows = load_rows()
    rows = apply_registered_patient_reconciliation(rows)
    records = build_reconciliation_records(rows)
    write_all(rows, records)
    print(
        json.dumps(
            {
                "direct_coverage": sum(1 for row in rows if str(row.get("registered_patient_count", "")).strip()),
                "candidate_coverage": sum(
                    1 for row in rows if str(row.get("registered_patient_count_candidate", "")).strip()
                ),
                "still_missing_direct": len(records),
                "still_unresolved": sum(1 for item in records if item["candidate_count"] == ""),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
