#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from build_gtd_gp_practice_dataset import OUTPUT_DIR, write_csv, write_json, write_map, write_readme, write_summary


DEFAULT_DATASET_JSON = OUTPUT_DIR / "gtd_greater_manchester_gp_practices.json"
DEFAULT_GOOGLE_JSON = OUTPUT_DIR / "google_maps_recent_reviews.json"
DEFAULT_UNMATCHED_JSON = OUTPUT_DIR / "google_maps_low_confidence_records.json"
DEFAULT_REVIEW_MD = OUTPUT_DIR / "google_maps_manual_review.md"


def normalize_name(value: str) -> str:
    value = (value or "").lower().replace("&", " and ")
    value = re.sub(r"[’']", "", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def is_high_confidence(result: dict[str, Any], threshold: float) -> bool:
    score = result.get("title_match_score")
    try:
        numeric_score = float(score)
    except (TypeError, ValueError):
        numeric_score = 0.0
    if numeric_score >= threshold:
        return True
    practice_name = normalize_name(str(result.get("practice_name", "")))
    google_title = normalize_name(str(result.get("google_maps_title", "")))
    return practice_name == google_title or practice_name in google_title or google_title in practice_name


def is_weak_confidence(result: dict[str, Any], threshold: float) -> bool:
    if is_high_confidence(result, threshold):
        return False
    if needs_manual_review(result):
        return False
    score = result.get("title_match_score")
    try:
        numeric_score = float(score)
    except (TypeError, ValueError):
        numeric_score = 0.0
    if numeric_score >= max(0.15, threshold * 0.4):
        return True
    return page_kind(result) == "place" and result.get("google_rating") is not None


def page_kind(result: dict[str, Any]) -> str:
    explicit = str(result.get("page_kind", "")).strip()
    if explicit:
        return explicit
    url = str(result.get("google_maps_url", ""))
    if "/place/" in url:
        return "place"
    if "/search/" in url:
        return "search"
    return "other"


def needs_manual_review(result: dict[str, Any]) -> bool:
    if bool(result.get("manual_review_required")):
        return True
    status = str(result.get("scan_status", "")).strip()
    if status in {"manual_review_search_result_only", "error"}:
        return True
    return page_kind(result) != "place"


def reset_google_maps_fields(row: dict[str, Any]) -> None:
    row["google_maps_title"] = ""
    row["google_maps_match_score"] = ""
    row["google_recent_reviews_captured"] = ""
    row["google_review_text_file"] = ""
    if "Google Maps direct" in str(row.get("google_review_source_note", "")):
        row["google_review_score"] = ""
        row["google_review_count"] = ""
        row["google_review_source_note"] = ""
        row["google_review_source_url"] = ""


def render_manual_review_md(path: Path, manual_review: list[dict[str, Any]], low_confidence: list[dict[str, Any]]) -> None:
    lines = [
        "# Google Maps Manual Review Queue",
        "",
        f"Generated from {len(manual_review) + len(low_confidence)} flagged Google Maps capture records.",
        "",
    ]
    if manual_review:
        lines.extend(
            [
                "## Manual Review Required",
                "",
                "| Practice | Code | Reason | Google title | URL |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for item in manual_review:
            url = str(item.get("google_maps_url", "")).strip()
            url_md = f"[link]({url})" if url else ""
            lines.append(
                f"| {item.get('practice_name', '')} | {item.get('canonical_code', '')} | {item.get('scan_status', '') or page_kind(item)} | {item.get('google_maps_title', '')} | {url_md} |"
            )
        lines.append("")
    if low_confidence:
        lines.extend(
            [
                "## Weak Name Match",
                "",
                "These were merged into the dataset as weak Google matches because the place page looked usable, but the title match was not strong.",
                "",
                "| Practice | Code | Match score | Google title | Merged note | URL |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
        for item in low_confidence:
            url = str(item.get("google_maps_url", "")).strip()
            url_md = f"[link]({url})" if url else ""
            lines.append(
                f"| {item.get('practice_name', '')} | {item.get('canonical_code', '')} | {item.get('title_match_score', '')} | {item.get('google_maps_title', '')} | weak name match | {url_md} |"
            )
        lines.append("")
    if not manual_review and not low_confidence:
        lines.append("No manual review items at this point.")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def relative_to_output(path_str: str) -> str:
    if not path_str:
        return ""
    path = Path(path_str)
    try:
        return str(path.relative_to(OUTPUT_DIR))
    except ValueError:
        parts = path.parts
        if "google-review-texts" in parts:
            index = parts.index("google-review-texts")
            return str(Path(*parts[index:]))
        return str(path)


def merge_rows(
    rows: list[dict[str, Any]],
    results: list[dict[str, Any]],
    threshold: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, int]]:
    result_by_code: dict[str, dict[str, Any]] = {}
    for result in results:
        code = str(result.get("canonical_code", "")).strip()
        if code:
            result_by_code[code] = result

    merged_count = 0
    direct_rating_count = 0
    text_file_count = 0
    manual_review: list[dict[str, Any]] = []
    low_confidence: list[dict[str, Any]] = []

    for row in rows:
        reset_google_maps_fields(row)

    for row in rows:
        result = result_by_code.get(str(row.get("canonical_code", "")).strip())
        if not result:
            continue
        if needs_manual_review(result):
            manual_review.append(result)
            continue
        high_confidence = is_high_confidence(result, threshold)
        weak_confidence = is_weak_confidence(result, threshold)
        if not high_confidence and not weak_confidence:
            low_confidence.append(result)
            continue
        if weak_confidence:
            low_confidence.append(result)

        row["google_maps_title"] = result.get("google_maps_title", "") or ""
        row["google_maps_match_score"] = result.get("title_match_score", "") or ""
        row["google_recent_reviews_captured"] = result.get("visible_review_cards_collected", "") or ""
        row["google_review_text_file"] = relative_to_output(str(result.get("review_text_file", "")))
        if row["google_review_text_file"]:
            text_file_count += 1
        if result.get("google_rating") is not None:
            row["google_review_score"] = result.get("google_rating", "")
            row["google_review_count"] = result.get("google_review_count", "")
            row["google_review_source_note"] = "Google Maps direct search"
            if result.get("reviews_opened"):
                row["google_review_source_note"] = "Google Maps direct search with visible recent reviews"
            if weak_confidence:
                row["google_review_source_note"] += " (weak name match)"
            row["google_review_source_url"] = result.get("google_maps_url", "") or ""
            direct_rating_count += 1
        merged_count += 1

    stats = {
        "input_google_result_count": len(results),
        "rows_merged": merged_count,
        "rows_with_direct_google_rating": direct_rating_count,
        "rows_with_review_text_file": text_file_count,
        "manual_review_result_count": len(manual_review),
        "low_confidence_result_count": len(low_confidence),
    }
    return rows, manual_review + low_confidence, stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge direct Google Maps review captures back into the GTD GP dataset.")
    parser.add_argument("--dataset-json", type=Path, default=DEFAULT_DATASET_JSON)
    parser.add_argument("--google-json", type=Path, default=DEFAULT_GOOGLE_JSON)
    parser.add_argument("--confidence-threshold", type=float, default=0.5)
    parser.add_argument("--unmatched-json", type=Path, default=DEFAULT_UNMATCHED_JSON)
    parser.add_argument("--manual-review-md", type=Path, default=DEFAULT_REVIEW_MD)
    args = parser.parse_args()

    rows = load_json(args.dataset_json)
    results = load_json(args.google_json)
    rows, flagged_results, stats = merge_rows(rows, results, args.confidence_threshold)

    write_csv(OUTPUT_DIR / "gtd_greater_manchester_gp_practices.csv", rows)
    write_json(OUTPUT_DIR / "gtd_greater_manchester_gp_practices.json", rows)
    summary = write_summary(OUTPUT_DIR / "summary.json", rows)
    summary["google_maps_total_scanned_count"] = len(results)
    summary["google_maps_manual_review_count"] = stats["manual_review_result_count"]
    summary["google_maps_flagged_result_count"] = stats["manual_review_result_count"] + stats["low_confidence_result_count"]
    (OUTPUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_readme(OUTPUT_DIR / "README.md", summary)
    write_map(OUTPUT_DIR / "map.html", rows)
    args.unmatched_json.write_text(json.dumps(flagged_results, indent=2), encoding="utf-8")
    manual_review = [item for item in flagged_results if needs_manual_review(item)]
    low_confidence = [item for item in flagged_results if not needs_manual_review(item)]
    render_manual_review_md(args.manual_review_md, manual_review, low_confidence)

    print(json.dumps(stats, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
