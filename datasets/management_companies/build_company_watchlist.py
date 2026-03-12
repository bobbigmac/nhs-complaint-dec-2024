#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
DATASETS_DIR = BASE_DIR.parent
WATCHLIST_JSON = BASE_DIR / "watchlist.json"
DATASET_JSON = DATASETS_DIR / "output" / "gtd-greater-manchester-gp-practice-reviews-2026-03-09" / "gtd_greater_manchester_gp_practices.json"
REPORT_DIR = BASE_DIR / "output"
REPORT_JSON = REPORT_DIR / "company_watchlist_report.json"
REPORT_MD = REPORT_DIR / "company_watchlist_report.md"


def load_watchlist() -> dict[str, Any]:
    return json.loads(WATCHLIST_JSON.read_text(encoding="utf-8"))


def load_rows() -> list[dict[str, Any]]:
    return json.loads(DATASET_JSON.read_text(encoding="utf-8"))


def summarize_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "ods_code": str(row.get("canonical_code", "")),
        "practice_name": str(row.get("practice_name", "")),
        "postcode": str(row.get("postcode", "")),
        "management_company_name": str(row.get("management_company_name", "")),
        "management_company_source": str(row.get("management_company_source", "")),
        "affiliated_group_name": str(row.get("affiliated_group_name", "")),
        "affiliated_group_source": str(row.get("affiliated_group_source", "")),
        "website_url": str(row.get("website_url", "")),
    }


def find_row(rows: list[dict[str, Any]], tracked: dict[str, Any]) -> dict[str, Any] | None:
    ods_code = str(tracked.get("ods_code", "")).strip()
    if ods_code:
        return next((row for row in rows if str(row.get("canonical_code", "")).strip() == ods_code), None)
    practice_name = str(tracked.get("practice_name", "")).strip().lower()
    if practice_name:
        return next((row for row in rows if str(row.get("practice_name", "")).strip().lower() == practice_name), None)
    return None


def build_company_entry(company: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    company_name = str(company["company_name"])
    management_matches = [
        summarize_row(row)
        for row in rows
        if str(row.get("management_company_name", "")).strip() == company_name
    ]
    affiliated_matches = [
        summarize_row(row)
        for row in rows
        if str(row.get("affiliated_group_name", "")).strip() == company_name
    ]

    tracked_results: list[dict[str, Any]] = []
    for tracked in company.get("tracked_practices", []):
        row = find_row(rows, tracked)
        tracked_results.append(
            {
                "tracked": tracked,
                "found_in_dataset": row is not None,
                "dataset_row": summarize_row(row) if row else None,
            }
        )

    candidate_results: list[dict[str, Any]] = []
    for candidate in company.get("candidate_practices", []):
        row = find_row(rows, candidate)
        candidate_results.append(
            {
                "candidate": candidate,
                "found_in_dataset": row is not None,
                "dataset_row": summarize_row(row) if row else None,
            }
        )

    return {
        "company_name": company_name,
        "kind": str(company.get("kind", "")),
        "summary": str(company.get("summary", "")),
        "legal_shape": str(company.get("legal_shape", "")),
        "relationship_to_gtd": str(company.get("relationship_to_gtd", "")),
        "why_it_matters": str(company.get("why_it_matters", "")),
        "source_strength": str(company.get("source_strength", "")),
        "notes": [str(item) for item in company.get("notes", [])],
        "key_sources": [str(item) for item in company.get("key_sources", [])],
        "management_match_count": len(management_matches),
        "affiliated_match_count": len(affiliated_matches),
        "management_matches": management_matches,
        "affiliated_matches": affiliated_matches,
        "tracked_results": tracked_results,
        "candidate_results": candidate_results,
    }


def build_auto_groups(rows: list[dict[str, Any]], field: str, minimum_size: int = 3) -> list[dict[str, Any]]:
    counter = Counter(str(row.get(field, "")).strip() for row in rows if str(row.get(field, "")).strip())
    groups: list[dict[str, Any]] = []
    for name, count in counter.most_common():
        if name == "GTD Healthcare" or count < minimum_size:
            continue
        matches = [summarize_row(row) for row in rows if str(row.get(field, "")).strip() == name]
        groups.append(
            {
                "name": name,
                "field": field,
                "count": count,
                "matches": matches,
            }
        )
    return groups


def build_report() -> dict[str, Any]:
    watchlist = load_watchlist()
    rows = load_rows()
    profiles = [build_company_entry(company, rows) for company in watchlist.get("profiles", [])]
    companies = [build_company_entry(company, rows) for company in watchlist.get("companies", [])]
    return {
        "source_quote": str(watchlist.get("source_quote", "")),
        "dataset_path": str(DATASET_JSON.relative_to(BASE_DIR.parent.parent)),
        "dataset_row_count": len(rows),
        "profiles": profiles,
        "watch_companies": companies,
        "auto_management_groups": build_auto_groups(rows, "management_company_name"),
        "auto_affiliated_groups": build_auto_groups(rows, "affiliated_group_name"),
    }


def render_match_lines(matches: list[dict[str, Any]], company_field: str) -> list[str]:
    lines: list[str] = []
    for match in matches:
        label = str(match.get(company_field, "")).strip()
        extra = f" via {company_field}" if label else ""
        lines.append(
            f"- `{match['ods_code']}` - {match['practice_name']} ({match['postcode']}){extra}"
        )
    return lines


def role_summary(row: dict[str, Any]) -> str:
    management = str(row.get("management_company_name", "")).strip() or "-"
    affiliated = str(row.get("affiliated_group_name", "")).strip() or "-"
    return f"management=`{management}`; affiliated=`{affiliated}`"


def render_company_profile(lines: list[str], company: dict[str, Any]) -> None:
    lines.append(f"### {company['company_name']}")
    lines.append("")
    lines.append(f"- Kind: `{company['kind']}`")
    if company["source_strength"]:
        lines.append(f"- Source strength: `{company['source_strength']}`")
    lines.append(f"- Direct management matches in current dataset: **{company['management_match_count']}**")
    lines.append(f"- Affiliated-group matches in current dataset: **{company['affiliated_match_count']}**")
    if company["summary"]:
        lines.append(f"- Summary: {company['summary']}")
    if company["legal_shape"]:
        lines.append(f"- Legal / organisational shape: {company['legal_shape']}")
    if company["relationship_to_gtd"]:
        lines.append(f"- Relationship to GTD: {company['relationship_to_gtd']}")
    if company["why_it_matters"]:
        lines.append(f"- Why it matters: {company['why_it_matters']}")
    for note in company["notes"]:
        lines.append(f"- Note: {note}")
    lines.append("")

    if company["management_matches"]:
        lines.append("Direct management-company examples in current dataset:")
        lines.extend(render_match_lines(company["management_matches"][:8], "management_company_name"))
        if len(company["management_matches"]) > 8:
            lines.append(f"- ... plus **{len(company['management_matches']) - 8}** more direct matches")
        lines.append("")

    if company["affiliated_matches"]:
        lines.append("Affiliated-group examples in current dataset:")
        lines.extend(render_match_lines(company["affiliated_matches"][:8], "affiliated_group_name"))
        if len(company["affiliated_matches"]) > 8:
            lines.append(f"- ... plus **{len(company['affiliated_matches']) - 8}** more affiliated-group matches")
        lines.append("")

    if company["tracked_results"]:
        lines.append("Tracked practice checks:")
        for item in company["tracked_results"]:
            tracked = item["tracked"]
            label = tracked.get("ods_code") or tracked.get("practice_name")
            if item["found_in_dataset"]:
                row = item["dataset_row"]
                lines.append(
                    f"- `{label}` found as {row['practice_name']} ({row['postcode']}) - {role_summary(row)}"
                )
            else:
                lines.append(f"- `{label}` not found in the current catchment dataset.")
        lines.append("")

    if company["candidate_results"]:
        lines.append("Candidate investigation rows:")
        for item in company["candidate_results"]:
            candidate = item["candidate"]
            label = candidate.get("ods_code") or candidate.get("practice_name")
            reason = candidate.get("reason", "")
            if item["found_in_dataset"]:
                row = item["dataset_row"]
                lines.append(
                    f"- `{label}` found as {row['practice_name']} ({row['postcode']}); {role_summary(row)}; reason: {reason}"
                )
            else:
                lines.append(f"- `{label}` not found; reason: {reason}")
        lines.append("")

    if company["key_sources"]:
        lines.append("Key sources:")
        for source in company["key_sources"]:
            lines.append(f"- {source}")
        lines.append("")


def render_report(report: dict[str, Any]) -> str:
    lines = [
        "# Management company watchlist report",
        "",
        report["source_quote"],
        "",
        f"Dataset checked: `{report['dataset_path']}`",
        "",
        f"Rows in current dataset: **{report['dataset_row_count']}**",
        "",
        "## Known operator profiles",
        "",
    ]

    for company in report["profiles"]:
        render_company_profile(lines, company)

    lines.extend(
        [
            "## Tender watchlist",
            "",
        ]
    )

    for company in report["watch_companies"]:
        render_company_profile(lines, company)

    lines.extend(
        [
            "## Auto-detected multi-practice groups already in catchment",
            "",
            "These come from the enriched dataset itself rather than the tender quote. They are useful for competitor/context scanning.",
            "",
            "### Management-company groups",
            "",
        ]
    )

    for group in report["auto_management_groups"]:
        lines.append(f"- **{group['name']}**: {group['count']} rows")
    lines.append("")
    lines.append("### Affiliated groups")
    lines.append("")
    for group in report["auto_affiliated_groups"]:
        lines.append(f"- **{group['name']}**: {group['count']} rows")
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    report = build_report()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    REPORT_MD.write_text(render_report(report), encoding="utf-8")
    print(json.dumps({"report_json": str(REPORT_JSON), "report_md": str(REPORT_MD)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
