#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


CURRENT_DIR = Path(__file__).resolve().parent
DATASETS_DIR = CURRENT_DIR.parent
MANCHESTER_DIR = DATASETS_DIR / "output" / "gtd-greater-manchester-gp-practice-reviews-2026-03-09"
MANCHESTER_CSV = MANCHESTER_DIR / "gtd_greater_manchester_gp_practices.csv"
MANCHESTER_GOOGLE_JSON = MANCHESTER_DIR / "google_maps_recent_reviews.json"
NATIONAL_POOL_CSV = CURRENT_DIR / "output" / "uk_gp_practices_not_in_current_dataset.csv"
NATIONAL_GOOGLE_JSON = CURRENT_DIR / "output" / "google_maps_recent_reviews.json"
NATIONAL_SUPPLEMENTALS_JS = MANCHESTER_DIR / "national-practice-supplementals.js"
OUTPUT_DIR = DATASETS_DIR / ".tmp" / "national-practice-followup"


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_json_list(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, list) else []


def parse_supplementals(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    prefix = "window.NATIONAL_PRACTICE_SUPPLEMENTALS="
    start = text.index(prefix) + len(prefix)
    end = text.index(";\nwindow.NATIONAL_PRACTICE_SUPPLEMENTALS_COUNT=")
    payload = json.loads(text[start:end])
    return payload if isinstance(payload, list) else []


def truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value or "").strip().lower()
    return text in {"1", "true", "yes", "y"}


def has_value(value: Any) -> bool:
    return value not in ("", None)


def usable_google_result(result: dict[str, Any]) -> bool:
    if not isinstance(result, dict):
        return False
    if any(
        truthy(result.get(field))
        for field in (
            "manual_review_required",
            "wrong_place_match",
            "blocked_place_match",
            "sponsored_place_match",
            "sponsored_search_results_only",
        )
    ):
        return False
    return has_value(result.get("google_rating")) and has_value(result.get("google_review_count")) and (
        str(result.get("page_kind", "")).strip() == "place"
        or has_value(result.get("google_maps_url"))
        or has_value(result.get("google_maps_title"))
    )


def write_csv(path: Path, rows: list[dict[str, Any]], preferred_order: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        fieldnames = preferred_order or []
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
        return

    seen: set[str] = set()
    ordered: list[str] = []
    for field in preferred_order or []:
        if field not in seen:
            ordered.append(field)
            seen.add(field)
    for row in rows:
        for field in row.keys():
            if field not in seen:
                ordered.append(field)
                seen.add(field)

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ordered)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def manchester_worklists() -> dict[str, int]:
    practice_rows = load_csv_rows(MANCHESTER_CSV)
    practice_by_code = {row.get("canonical_code", "").strip(): row for row in practice_rows if row.get("canonical_code")}
    review_rows = load_json_list(MANCHESTER_GOOGLE_JSON)

    residual_tail: list[dict[str, Any]] = []
    manual_review: list[dict[str, Any]] = []
    threshold_skip: list[dict[str, Any]] = []
    no_review_panel: list[dict[str, Any]] = []
    visible_without_raw: list[dict[str, Any]] = []

    for result in review_rows:
        code = str(result.get("canonical_code", "")).strip()
        if not code:
            continue
        source_row = dict(practice_by_code.get(code, {}))
        merged = dict(source_row)
        merged.update(
            {
                "followup_scan_status": str(result.get("scan_status", "") or ""),
                "followup_page_kind": str(result.get("page_kind", "") or ""),
                "followup_manual_review_required": truthy(result.get("manual_review_required")),
                "followup_retry_recommended": truthy(result.get("retry_recommended")),
                "followup_google_maps_title": result.get("google_maps_title", ""),
                "followup_google_review_count_current": result.get("google_review_count", ""),
                "followup_reviews_opened": truthy(result.get("reviews_opened")),
                "followup_visible_review_cards_collected": result.get("visible_review_cards_collected", ""),
                "followup_raw_review_responses_captured": result.get("raw_review_responses_captured", ""),
                "followup_google_maps_url": result.get("google_maps_url", ""),
            }
        )

        scan_status = merged["followup_scan_status"]
        if truthy(result.get("manual_review_required")) or truthy(result.get("retry_recommended")) or scan_status != "ok_with_visible_reviews":
            residual_tail.append(merged)
        if truthy(result.get("manual_review_required")):
            merged["recommended_action"] = "Headful manual match confirmation before any further crawl"
            manual_review.append(merged)
        if scan_status == "skipped_review_count_threshold":
            merged["recommended_action"] = "Headful full-review Manchester extension pass"
            threshold_skip.append(merged)
        if scan_status == "ok_no_review_panel":
            merged["recommended_action"] = "Headful verification of no review panel or hidden reviews entrypoint"
            no_review_panel.append(merged)
        if int(result.get("visible_review_cards_collected") or 0) > 0 and int(result.get("raw_review_responses_captured") or 0) == 0:
            merged["recommended_action"] = "Re-run under watched session and recover raw review transport capture"
            visible_without_raw.append(merged)

    residual_tail.sort(key=lambda row: (str(row.get("followup_scan_status", "")), -int(row.get("followup_google_review_count_current") or 0)))
    threshold_skip.sort(key=lambda row: -int(row.get("followup_google_review_count_current") or 0))
    no_review_panel.sort(key=lambda row: -int(row.get("followup_google_review_count_current") or 0))
    manual_review.sort(key=lambda row: row.get("canonical_code", ""))
    visible_without_raw.sort(key=lambda row: -int(row.get("followup_google_review_count_current") or 0))

    preferred = list(practice_rows[0].keys()) if practice_rows else []
    write_csv(OUTPUT_DIR / "manchester_residual_tail.csv", residual_tail, preferred)
    write_csv(OUTPUT_DIR / "manchester_manual_review.csv", manual_review, preferred)
    write_csv(OUTPUT_DIR / "manchester_threshold_skip_full_review.csv", threshold_skip, preferred)
    write_csv(OUTPUT_DIR / "manchester_no_review_panel.csv", no_review_panel, preferred)
    write_csv(OUTPUT_DIR / "manchester_visible_without_raw.csv", visible_without_raw, preferred)

    return {
        "manchester_residual_tail": len(residual_tail),
        "manchester_manual_review": len(manual_review),
        "manchester_threshold_skip_full_review": len(threshold_skip),
        "manchester_no_review_panel": len(no_review_panel),
        "manchester_visible_without_raw": len(visible_without_raw),
    }


def infer_excluded_reason(pool_row: dict[str, str], result: dict[str, Any]) -> str:
    if not result:
        return "no_google_result"
    if truthy(result.get("manual_review_required")):
        return "manual_review_required_google_match"
    if truthy(result.get("wrong_place_match")):
        return "wrong_place_match"
    if truthy(result.get("blocked_place_match")):
        return "blocked_place_match"
    if truthy(result.get("sponsored_place_match")) or truthy(result.get("sponsored_search_results_only")):
        return "sponsored_or_unusable_google_surface"
    if has_value(result.get("google_maps_title")) or has_value(result.get("google_maps_url")):
        return "google_surface_found_but_not_usable_for_supplemental"
    nation = str(pool_row.get("nation", "")).strip().lower()
    if nation in {"wales", "northern_ireland", "northern ireland"}:
        return "no_google_and_no_practice_level_survey_fallback"
    return "no_google_and_no_current_survey_fallback"


def national_worklists() -> dict[str, int]:
    pool_rows = load_csv_rows(NATIONAL_POOL_CSV)
    pool_by_code = {row.get("canonical_code", "").strip(): row for row in pool_rows if row.get("canonical_code")}
    national_results = load_json_list(NATIONAL_GOOGLE_JSON)
    results_by_code = {str(row.get("canonical_code", "")).strip(): row for row in national_results if row.get("canonical_code")}
    supplemental_rows = parse_supplementals(NATIONAL_SUPPLEMENTALS_JS)
    built_codes = {str(row.get("code", "")).strip() for row in supplemental_rows if row.get("code")}

    built_missing_google: list[dict[str, Any]] = []
    built_missing_patient_counts: list[dict[str, Any]] = []
    built_missing_survey: list[dict[str, Any]] = []
    excluded_rows: list[dict[str, Any]] = []

    for supplemental in supplemental_rows:
        code = str(supplemental.get("code", "")).strip()
        pool_row = dict(pool_by_code.get(code, {}))
        merged = dict(pool_row)
        merged.update(
            {
                "supplemental_nation": supplemental.get("nation", ""),
                "supplemental_google_score": supplemental.get("google_score", ""),
                "supplemental_google_count": supplemental.get("google_count", ""),
                "supplemental_google_source_note": supplemental.get("google_source_note", ""),
                "supplemental_google_review_scan_status": supplemental.get("google_review_scan_status", ""),
                "supplemental_google_url": supplemental.get("google_url", ""),
                "supplemental_survey_overall_good_percent": supplemental.get("survey_overall_good_percent", ""),
                "supplemental_survey_completion_rate_percent": supplemental.get("survey_completion_rate_percent", ""),
                "supplemental_number_of_responses": supplemental.get("number_of_responses", ""),
                "supplemental_registered_patient_count": supplemental.get("registered_patient_count", ""),
                "supplemental_patient_survey_name": supplemental.get("patient_survey_name", ""),
                "supplemental_patient_survey_status": supplemental.get("patient_survey_status", ""),
                "supplemental_patient_survey_level": supplemental.get("patient_survey_level", ""),
                "supplemental_patient_survey_note": supplemental.get("patient_survey_note", ""),
            }
        )
        if not (has_value(supplemental.get("google_score")) and has_value(supplemental.get("google_count"))):
            merged["recommended_action"] = "Confirm listing state or recover usable Google rating/count without full-history crawl"
            built_missing_google.append(merged)
        if not has_value(supplemental.get("registered_patient_count")):
            merged["recommended_action"] = "Verify patient count source coverage or explicit missing-source state"
            built_missing_patient_counts.append(merged)
        if not has_value(supplemental.get("survey_overall_good_percent")):
            merged["recommended_action"] = "Confirm survey status as present, missing in source, or structurally not wired"
            built_missing_survey.append(merged)

    for code, pool_row in pool_by_code.items():
        if code in built_codes:
            continue
        result = dict(results_by_code.get(code, {}))
        merged = dict(pool_row)
        merged.update(
            {
                "followup_google_rating": result.get("google_rating", ""),
                "followup_google_review_count": result.get("google_review_count", ""),
                "followup_google_maps_title": result.get("google_maps_title", ""),
                "followup_google_maps_url": result.get("google_maps_url", ""),
                "followup_page_kind": result.get("page_kind", ""),
                "followup_scan_status": result.get("scan_status", ""),
                "followup_manual_review_required": truthy(result.get("manual_review_required")),
                "followup_wrong_place_match": truthy(result.get("wrong_place_match")),
                "followup_blocked_place_match": truthy(result.get("blocked_place_match")),
                "followup_sponsored_place_match": truthy(result.get("sponsored_place_match")),
                "followup_sponsored_search_results_only": truthy(result.get("sponsored_search_results_only")),
                "followup_inferred_reason": infer_excluded_reason(pool_row, result),
                "recommended_action": "Watched validation pass to confirm explicit excluded state or recover a clean supplemental match",
            }
        )
        excluded_rows.append(merged)

    built_missing_google.sort(key=lambda row: (str(row.get("nation", "")), str(row.get("canonical_code", ""))))
    built_missing_patient_counts.sort(key=lambda row: (str(row.get("nation", "")), str(row.get("canonical_code", ""))))
    built_missing_survey.sort(key=lambda row: (str(row.get("nation", "")), str(row.get("canonical_code", ""))))
    excluded_rows.sort(key=lambda row: (str(row.get("followup_inferred_reason", "")), str(row.get("nation", "")), str(row.get("canonical_code", ""))))

    preferred = list(pool_rows[0].keys()) if pool_rows else []
    write_csv(OUTPUT_DIR / "national_supplemental_built_missing_google.csv", built_missing_google, preferred)
    write_csv(OUTPUT_DIR / "national_supplemental_built_missing_patient_counts.csv", built_missing_patient_counts, preferred)
    write_csv(OUTPUT_DIR / "national_supplemental_built_missing_survey.csv", built_missing_survey, preferred)
    write_csv(OUTPUT_DIR / "national_supplemental_excluded_from_map.csv", excluded_rows, preferred)

    excluded_reasons = Counter(str(row.get("followup_inferred_reason", "")) for row in excluded_rows)
    return {
        "national_supplemental_built_missing_google": len(built_missing_google),
        "national_supplemental_built_missing_patient_counts": len(built_missing_patient_counts),
        "national_supplemental_built_missing_survey": len(built_missing_survey),
        "national_supplemental_excluded_from_map": len(excluded_rows),
        "national_supplemental_excluded_reason_counts": dict(sorted(excluded_reasons.items())),
    }


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    summary = {
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "manchester": manchester_worklists(),
        "national_supplementals": national_worklists(),
    }
    (OUTPUT_DIR / "worklists_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
