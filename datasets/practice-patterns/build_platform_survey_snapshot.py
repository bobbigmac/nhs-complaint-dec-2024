#!/usr/bin/env python3
from __future__ import annotations

import json
import statistics
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

from practice_rankings import build_relative_rankings, render_relative_rankings_html


BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = BASE_DIR / "reports"
RAW_GPPS_DIR = BASE_DIR.parent / "raw" / "gp_patient_survey"
OUTPUT_DIR = BASE_DIR / "output"
MERGED_JSON = OUTPUT_DIR / "reviewed_practice_platform_survey_merge.json"
SUMMARY_MD = OUTPUT_DIR / "reviewed_practice_platform_survey_summary.md"
RANKINGS_HTML = OUTPUT_DIR / "reviewed_practice_relative_rankings.html"
GENERATED_AT = date.today().isoformat()

SURVEY_KEYS = {
    "phone_easy": "LocalGpServicesPhone",
    "website_easy": "localgpserviceswebsite",
    "app_easy": "localgpservicesapp",
    "contact_good": "gpcontactoverall",
    "overall_good": "overallexp",
    "needs_met": "lastgpapptneeds",
    "next_step_known": "gpcontactnextstep",
    "next_step_known_2d": "gpcontactnextsteptiming",
    "choice_time_day": "lastgpapptchoice_1",
    "wait_right": "lastgpapptwait",
}

METRICS_FOR_GROUPS = [
    "overall_good",
    "contact_good",
    "phone_easy",
    "website_easy",
    "app_easy",
    "needs_met",
]

FLAG_DEFINITIONS = {
    "website_platform:concrete_cms": "Concrete CMS / concrete5 public site",
    "website_platform:wordpress": "WordPress public site",
    "website_platform:my_surgery_website": "My Surgery Website public site",
    "request_platform:patchs": "PATCHS present",
    "request_platform:accurx": "Accurx present",
    "request_platform:patient_access": "Patient Access / EMIS Access present",
    "request_platform:silicon_forms": "Silicon Practice hosted forms present",
    "access:phone_first": "Phone-first appointments wording",
    "access:limited_scope_patchs": "PATCHS described as limited-scope, not full front door",
    "website_identity:standalone_domain": "Standalone practice domain",
    "website_identity:shared_host_microsite": "Shared-host patient microsite",
    "site_status:broken_or_placeholder": "Broken or placeholder public site",
}


def slugify(value: str) -> str:
    lowered = value.lower().replace("&", " and ")
    chars: list[str] = []
    last_dash = False
    for ch in lowered:
        if ch.isalnum():
            chars.append(ch)
            last_dash = False
        elif not last_dash:
            chars.append("-")
            last_dash = True
    return "".join(chars).strip("-")


def mean_or_none(values: list[float | int | None]) -> float | None:
    clean = [float(value) for value in values if value is not None]
    if not clean:
        return None
    return round(statistics.fmean(clean), 1)


def diff_or_none(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return round(left - right, 1)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def survey_path_for_code(ods_code: str) -> Path | None:
    matches = sorted(RAW_GPPS_DIR.glob(f"{ods_code}-*.json"))
    if matches:
        return matches[0]
    return None


def extract_metric(question_block: dict[str, Any] | None) -> dict[str, Any] | None:
    if not question_block:
        return None
    return {
        "practice_percent": question_block.get("practice_percent"),
        "ics_percent": question_block.get("ics_percent"),
        "national_percent": question_block.get("national_percent"),
        "practice_base": question_block.get("practice_base"),
        "question_text": question_block.get("question_text"),
        "practice_minus_ics": diff_or_none(question_block.get("practice_percent"), question_block.get("ics_percent")),
    }


def summarize_survey(raw_survey: dict[str, Any]) -> dict[str, Any]:
    key_questions = raw_survey.get("key_questions", {})
    summary: dict[str, Any] = {
        "completion_rate_percent": raw_survey.get("completion_rate_percent"),
        "surveys_sent_out": raw_survey.get("surveys_sent_out"),
        "surveys_sent_back": raw_survey.get("surveys_sent_back"),
        "metrics": {},
    }
    for metric_name, survey_key in SURVEY_KEYS.items():
        summary["metrics"][metric_name] = extract_metric(key_questions.get(survey_key))
    return summary


def collect_text_fragments(report: dict[str, Any]) -> list[str]:
    fragments: list[str] = []

    def visit(value: Any) -> None:
        if isinstance(value, str):
            fragments.append(value)
        elif isinstance(value, list):
            for item in value:
                visit(item)
        elif isinstance(value, dict):
            for item in value.values():
                visit(item)

    visit(report)
    return fragments


def derive_tags(report: dict[str, Any]) -> dict[str, Any]:
    text = "\n".join(collect_text_fragments(report)).lower()
    practice = report.get("practice", {})
    website_identity = str(practice.get("website_identity", "")).lower()
    website_stack_section = report.get("website_stack", {})
    live_stack = website_stack_section.get("items", [])

    website_stack = None
    for item in live_stack:
        label = str(item.get("label", "")).lower()
        if "website stack" in label:
            website_stack = item.get("platform")
            break
    if website_stack is None and live_stack:
        website_stack = live_stack[0].get("platform")

    website_stack_text = str(website_stack or "").lower()

    tags: set[str] = set()

    if "concrete cms" in website_stack_text or "concrete5" in website_stack_text:
        tags.add("website_platform:concrete_cms")
    if "wordpress" in website_stack_text:
        tags.add("website_platform:wordpress")
    if "my surgery website" in website_stack_text:
        tags.add("website_platform:my_surgery_website")
    if "patchs" in text:
        tags.add("request_platform:patchs")
    if "accurx" in text:
        tags.add("request_platform:accurx")
    if "patient access" in text or "emis access" in text:
        tags.add("request_platform:patient_access")
    if "silicon practice hosted forms" in text or "silicon practice" in text:
        tags.add("request_platform:silicon_forms")
    if "phone first" in text or "all appointments will be by phone first" in text or '"kind": "phone-first appointment handling"' in text:
        tags.add("access:phone_first")
    if "limited-scope" in text or "non-urgent and routine" in text:
        tags.add("access:limited_scope_patchs")
    if "standalone practice domain" in website_identity:
        tags.add("website_identity:standalone_domain")
    if "microsite" in website_identity:
        tags.add("website_identity:shared_host_microsite")
    if "apache placeholder page" in website_stack_text or "placeholder page" in website_stack_text:
        tags.add("site_status:broken_or_placeholder")

    request_platforms = sorted(
        {
            tag.split(":", 1)[1]
            for tag in tags
            if tag.startswith("request_platform:")
        }
    )

    return {
        "website_stack": website_stack,
        "website_identity": practice.get("website_identity"),
        "derived_tags": sorted(tags),
        "request_platforms": request_platforms,
    }


def build_row(report_path: Path, report: dict[str, Any] | None = None) -> dict[str, Any]:
    if report is None:
        report = load_json(report_path)
    practice = report.get("practice", {})
    ods_code = str(practice.get("ods_code", "")).strip()
    survey_path = survey_path_for_code(ods_code)
    survey_summary = None
    if survey_path:
        survey_summary = summarize_survey(load_json(survey_path))

    derived = derive_tags(report)
    return {
        "ods_code": ods_code,
        "practice_name": practice.get("practice_name"),
        "report_path": str(report_path.relative_to(BASE_DIR.parent.parent)),
        "website_url": practice.get("website_url"),
        "website_stack": derived["website_stack"],
        "website_identity": derived["website_identity"],
        "request_platforms": derived["request_platforms"],
        "derived_tags": derived["derived_tags"],
        "google_review_score": practice.get("google_review_score"),
        "google_review_count": practice.get("google_review_count"),
        "survey": survey_summary,
        "headline": report.get("headline"),
    }


def average_metric(rows: list[dict[str, Any]], metric_name: str) -> float | None:
    values: list[float | int | None] = []
    for row in rows:
        metric = (((row.get("survey") or {}).get("metrics") or {}).get(metric_name) or {})
        values.append(metric.get("practice_percent"))
    return mean_or_none(values)


def average_metric_diff(rows: list[dict[str, Any]], metric_name: str) -> float | None:
    values: list[float | int | None] = []
    for row in rows:
        metric = (((row.get("survey") or {}).get("metrics") or {}).get(metric_name) or {})
        values.append(metric.get("practice_minus_ics"))
    return mean_or_none(values)


def build_flag_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for flag, label in FLAG_DEFINITIONS.items():
        with_flag = [row for row in rows if flag in row.get("derived_tags", [])]
        without_flag = [row for row in rows if flag not in row.get("derived_tags", [])]
        if not with_flag:
            continue
        metric_diffs = {}
        for metric_name in METRICS_FOR_GROUPS:
            metric_diffs[metric_name] = {
                "with_flag_avg": average_metric(with_flag, metric_name),
                "without_flag_avg": average_metric(without_flag, metric_name),
                "difference": diff_or_none(
                    average_metric(with_flag, metric_name),
                    average_metric(without_flag, metric_name),
                ),
                "with_flag_vs_ics_avg": average_metric_diff(with_flag, metric_name),
            }
        summaries.append(
            {
                "flag": flag,
                "label": label,
                "count_with_flag": len(with_flag),
                "count_without_flag": len(without_flag),
                "metrics": metric_diffs,
                "members": [row["ods_code"] for row in with_flag],
            }
        )
    summaries.sort(
        key=lambda item: (
            item["count_with_flag"],
            item["metrics"]["overall_good"]["difference"] or -999,
        ),
        reverse=True,
    )
    return summaries


def build_group_summary(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    grouped: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        value = row.get(key)
        if value:
            grouped[str(value)].append(row)
    summary: list[dict[str, Any]] = []
    for value, members in grouped.items():
        summary.append(
            {
                key: value,
                "count": len(members),
                "members": [row["ods_code"] for row in members],
                "google_review_score_avg": mean_or_none([row.get("google_review_score") for row in members]),
                "metrics": {
                    metric_name: {
                        "avg": average_metric(members, metric_name),
                        "avg_vs_ics": average_metric_diff(members, metric_name),
                    }
                    for metric_name in METRICS_FOR_GROUPS
                },
            }
        )
    summary.sort(key=lambda item: (item["count"], item["metrics"]["overall_good"]["avg"] or -999), reverse=True)
    return summary


def rank_rows(rows: list[dict[str, Any]], metric_name: str, descending: bool = True) -> list[dict[str, Any]]:
    def metric_value(row: dict[str, Any]) -> float:
        metric = (((row.get("survey") or {}).get("metrics") or {}).get(metric_name) or {})
        value = metric.get("practice_percent")
        return float(value) if value is not None else float("-inf")

    ranked = sorted(rows, key=metric_value, reverse=descending)
    output: list[dict[str, Any]] = []
    for row in ranked:
        metric = (((row.get("survey") or {}).get("metrics") or {}).get(metric_name) or {})
        if metric.get("practice_percent") is None:
            continue
        output.append(
            {
                "ods_code": row["ods_code"],
                "practice_name": row["practice_name"],
                "website_stack": row.get("website_stack"),
                "request_platforms": row.get("request_platforms"),
                "metric_percent": metric.get("practice_percent"),
                "metric_vs_ics": metric.get("practice_minus_ics"),
                "google_review_score": row.get("google_review_score"),
            }
        )
    return output


def build_summary_payload(rows: list[dict[str, Any]]) -> dict[str, Any]:
    rows_with_survey = [row for row in rows if row.get("survey")]
    return {
        "generated_at": GENERATED_AT,
        "reviewed_report_count": len(rows),
        "reviewed_with_survey_count": len(rows_with_survey),
        "metrics_considered": METRICS_FOR_GROUPS,
        "rows": rows,
        "flag_summaries": build_flag_summary(rows_with_survey),
        "website_stack_groups": build_group_summary(rows_with_survey, "website_stack"),
        "top_by_overall_good": rank_rows(rows_with_survey, "overall_good", descending=True)[:10],
        "bottom_by_overall_good": rank_rows(rows_with_survey, "overall_good", descending=False)[:10],
        "top_by_website_easy": rank_rows(rows_with_survey, "website_easy", descending=True)[:10],
        "bottom_by_website_easy": rank_rows(rows_with_survey, "website_easy", descending=False)[:10],
    }


def format_metric_cell(value: float | None) -> str:
    if value is None:
        return "-"
    if value == int(value):
        return f"{int(value)}"
    return f"{value:.1f}"


def render_markdown(summary: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Reviewed Practice Platform vs Survey Snapshot")
    lines.append("")
    lines.append("This is an exploratory merge of manual practice-pattern reports with per-practice GP Patient Survey metrics.")
    lines.append("It is not causal analysis, and it only covers practices that have already been reviewed manually.")
    lines.append("")
    lines.append("## Coverage")
    lines.append("")
    lines.append(f"- reviewed reports: `{summary['reviewed_report_count']}`")
    lines.append(f"- reviewed reports with GPPS data: `{summary['reviewed_with_survey_count']}`")
    lines.append(f"- generated_at: `{summary['generated_at']}`")
    lines.append(f"- interactive relative rankings: `{RANKINGS_HTML.name}`")
    lines.append("")
    lines.append("## Website Stack Groups")
    lines.append("")
    lines.append("| website stack | n | overall_good | contact_good | website_easy | app_easy | phone_easy | google |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for group in summary["website_stack_groups"]:
        metrics = group["metrics"]
        lines.append(
            "| "
            + " | ".join(
                [
                    str(group["website_stack"]),
                    str(group["count"]),
                    format_metric_cell(metrics["overall_good"]["avg"]),
                    format_metric_cell(metrics["contact_good"]["avg"]),
                    format_metric_cell(metrics["website_easy"]["avg"]),
                    format_metric_cell(metrics["app_easy"]["avg"]),
                    format_metric_cell(metrics["phone_easy"]["avg"]),
                    format_metric_cell(group["google_review_score_avg"]),
                ]
            )
            + " |"
        )
    lines.append("")
    lines.append("## Flag Deltas")
    lines.append("")
    lines.append("Positive `delta` means practices with the flag are scoring higher than reviewed practices without it.")
    lines.append("")
    lines.append("| flag | n | overall delta | website delta | app delta | phone delta | notes |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for item in summary["flag_summaries"]:
        metrics = item["metrics"]
        lines.append(
            "| "
            + " | ".join(
                [
                    item["label"],
                    str(item["count_with_flag"]),
                    format_metric_cell(metrics["overall_good"]["difference"]),
                    format_metric_cell(metrics["website_easy"]["difference"]),
                    format_metric_cell(metrics["app_easy"]["difference"]),
                    format_metric_cell(metrics["phone_easy"]["difference"]),
                    ", ".join(item["members"]),
                ]
            )
            + " |"
        )
    lines.append("")
    lines.append("## Top Reviewed Practices By Website Ease")
    lines.append("")
    for row in summary["top_by_website_easy"]:
        lines.append(
            f"- `{row['ods_code']}` {row['practice_name']}: website `{row['metric_percent']}%`, vs ICS `{format_metric_cell(row['metric_vs_ics'])}`, stack `{row['website_stack']}`, requests `{', '.join(row['request_platforms']) or '-'}`"
        )
    lines.append("")
    lines.append("## Bottom Reviewed Practices By Website Ease")
    lines.append("")
    for row in summary["bottom_by_website_easy"]:
        lines.append(
            f"- `{row['ods_code']}` {row['practice_name']}: website `{row['metric_percent']}%`, vs ICS `{format_metric_cell(row['metric_vs_ics'])}`, stack `{row['website_stack']}`, requests `{', '.join(row['request_platforms']) or '-'}`"
        )
    lines.append("")
    lines.append("## Top Reviewed Practices By Overall Experience")
    lines.append("")
    for row in summary["top_by_overall_good"]:
        lines.append(
            f"- `{row['ods_code']}` {row['practice_name']}: overall `{row['metric_percent']}%`, vs ICS `{format_metric_cell(row['metric_vs_ics'])}`, google `{format_metric_cell(row['google_review_score'])}`, stack `{row['website_stack']}`"
        )
    lines.append("")
    lines.append("## Bottom Reviewed Practices By Overall Experience")
    lines.append("")
    for row in summary["bottom_by_overall_good"]:
        lines.append(
            f"- `{row['ods_code']}` {row['practice_name']}: overall `{row['metric_percent']}%`, vs ICS `{format_metric_cell(row['metric_vs_ics'])}`, google `{format_metric_cell(row['google_review_score'])}`, stack `{row['website_stack']}`"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    reports_by_ods: dict[str, dict[str, Any]] = {}
    rows: list[dict[str, Any]] = []
    for path in sorted(REPORTS_DIR.glob("*.json")):
        report = load_json(path)
        row = build_row(path, report)
        reports_by_ods[row["ods_code"]] = report
        rows.append(row)
    summary = build_summary_payload(rows)
    summary["relative_rankings"] = build_relative_rankings(rows, reports_by_ods, GENERATED_AT)
    MERGED_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    SUMMARY_MD.write_text(render_markdown(summary), encoding="utf-8")
    RANKINGS_HTML.write_text(render_relative_rankings_html(summary["relative_rankings"]), encoding="utf-8")
    print(f"Wrote {MERGED_JSON}")
    print(f"Wrote {SUMMARY_MD}")
    print(f"Wrote {RANKINGS_HTML}")


if __name__ == "__main__":
    main()
