#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import random
import re
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_URL = "https://www.gp-patient.co.uk"
RAW_OUTPUT_DIR = Path("gp_patient_survey_raw")
SUMMARY_MD = Path("gp_patient_survey_focus.md")
DATASET_JSON = Path("gtd-greater-manchester-gp-practice-reviews-2026-03-09/gtd_greater_manchester_gp_practices.json")
USER_AGENT = "Mozilla/5.0 (compatible; Codex GP Patient Survey collector/1.0)"
ACTIVE_PROJECT = 16
TOP_LEVEL_ENDPOINTS = {
    "practice": f"{BASE_URL}/api/Data/{ACTIVE_PROJECT}/1/2/1",
    "ics": f"{BASE_URL}/api/Data/{ACTIVE_PROJECT}/1/2/3",
    "national": f"{BASE_URL}/api/Data/{ACTIVE_PROJECT}/1/2/4",
}
FALLBACK_QUESTION_COLUMNS = [
    "LocalGpServicesPhone",
    "localgpserviceswebsite",
    "localgpservicesapp",
    "localgpservicesreception",
    "localgpservicesprefhpsee",
    "gpcontactnextstep",
    "gpcontactnextsteptiming",
    "gpcontactoverall",
    "lastgpapptchoice_1",
    "lastgpapptchoice_2",
    "lastgpapptwait",
    "lastgpapptlisten",
    "lastgpapptcare",
    "lastgpapptmental",
    "lastgpapptinfo",
    "lastgpapptconf",
    "lastgpapptdecision",
    "lastgpapptneeds",
    "healthsupport",
    "overallexp",
]
PRACTICE_NAME_RE = re.compile(r'class="text-black txt-fs-lg practice-info-name fw-bold">\s*(.*?)\s*</p>', re.S)
PRACTICE_ADDRESS_RE = re.compile(r'class="text-black txt-fs-med practice-info-address"><address>(.*?)</address>', re.S)
ICS_CODE_RE = re.compile(r'<input type="hidden" id="icsCode" value="([^"]*)"', re.S)
EMPTY_PRACTICE_RE = re.compile(r'<input id="hdnEmptyPractice" type="hidden" value="([^"]*)"', re.S)
QUESTION_BLOCK_RE = re.compile(
    r'<div class="pe-question-container[^>]*data-question-id="(?P<question_id>\d+)" data-column="(?P<column>[^"]+)"[\s\S]*?<p class="txt-fs-lg mb-1">\s*(?P<content>[\s\S]*?)</p>',
    re.S,
)
INTERESTING_QUESTION_COLUMNS = [
    "LocalGpServicesPhone",
    "localgpserviceswebsite",
    "localgpservicesapp",
    "gpcontactoverall",
    "overallexp",
    "lastgpapptneeds",
    "healthsupport",
]
QUESTION_LABELS = {
    "LocalGpServicesPhone": "phone_easy",
    "localgpserviceswebsite": "website_easy",
    "localgpservicesapp": "app_easy",
    "gpcontactoverall": "contact_good",
    "overallexp": "overall_good",
    "lastgpapptneeds": "needs_met",
    "healthsupport": "support_ltc",
}


def load_dataset_rows(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_whitespace(value: str) -> str:
    return " ".join(value.split())


def strip_tags(value: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", value)
    return normalize_whitespace(html.unescape(without_tags))


def extract_metric_value(page_html: str, label: str) -> int | None:
    pattern = re.compile(
        rf'<span class="txt-fs-lg fw-bold">\s*([^<]+?)\s*</span>\s*<span class="txt-fs-med">{re.escape(label)}</span>',
        re.S,
    )
    match = pattern.search(page_html)
    if not match:
        return None
    raw = normalize_whitespace(match.group(1)).replace("%", "").replace(",", "")
    try:
        return int(raw)
    except ValueError:
        return None


def parse_practice_page(page_html: str) -> dict[str, Any]:
    question_texts: dict[str, str] = {}
    for match in QUESTION_BLOCK_RE.finditer(page_html):
        column = match.group("column").strip()
        if column in question_texts:
            continue
        question_text = strip_tags(match.group("content")).removeprefix("Loading...")
        question_texts[column] = normalize_whitespace(question_text)

    name_match = PRACTICE_NAME_RE.search(page_html)
    address_match = PRACTICE_ADDRESS_RE.search(page_html)
    ics_match = ICS_CODE_RE.search(page_html)
    empty_match = EMPTY_PRACTICE_RE.search(page_html)
    return {
        "practice_name_gpps": strip_tags(name_match.group(1)) if name_match else "",
        "practice_address": strip_tags(address_match.group(1)) if address_match else "",
        "ics_code": normalize_whitespace(ics_match.group(1)) if ics_match else "",
        "empty_practice": (empty_match.group(1) == "1") if empty_match else False,
        "surveys_sent_out": extract_metric_value(page_html, "Surveys sent out"),
        "surveys_sent_back": extract_metric_value(page_html, "Surveys sent back"),
        "completion_rate_percent": extract_metric_value(page_html, "Completion rate"),
        "question_texts": question_texts,
    }


def http_request(url: str, body: dict[str, Any] | None = None, timeout: float = 30.0, attempts: int = 3) -> str:
    payload = None
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json, text/html;q=0.9, */*;q=0.8",
    }
    if body is not None:
        payload = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        request = Request(url, data=payload, headers=headers, method="POST" if payload is not None else "GET")
        try:
            with urlopen(request, timeout=timeout) as response:
                return response.read().decode("utf-8", errors="replace")
        except (HTTPError, URLError, TimeoutError) as exc:
            last_error = exc
            if attempt == attempts:
                break
            time.sleep(0.6 * attempt)
    raise RuntimeError(f"request failed for {url}: {last_error}")


def fetch_json(url: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    return json.loads(http_request(url, body=body))


def top_level_index(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for item in items:
        question_name = str(item.get("questionName", "")).strip()
        if question_name and question_name not in indexed:
            indexed[question_name] = item
    return indexed


def build_question_record(
    question_column: str,
    question_texts: dict[str, str],
    practice_results: dict[str, dict[str, Any]],
    ics_results: dict[str, dict[str, Any]],
    national_results: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    practice_item = practice_results.get(question_column, {})
    ics_item = ics_results.get(question_column, {})
    national_item = national_results.get(question_column, {})
    return {
        "question_text": question_texts.get(question_column, ""),
        "practice_percent": practice_item.get("valuePER"),
        "practice_count": practice_item.get("count"),
        "practice_base": practice_item.get("base"),
        "practice_unweighted_base": practice_item.get("unweightedBase"),
        "ics_percent": ics_item.get("valuePER"),
        "ics_count": ics_item.get("count"),
        "ics_base": ics_item.get("base"),
        "ics_unweighted_base": ics_item.get("unweightedBase"),
        "national_percent": national_item.get("valuePER"),
        "national_count": national_item.get("count"),
        "national_base": national_item.get("base"),
        "national_unweighted_base": national_item.get("unweightedBase"),
    }


def collect_record(row: dict[str, Any], pause_min: float, pause_max: float) -> dict[str, Any]:
    code = str(row.get("canonical_code", "")).strip()
    practice_name = str(row.get("practice_name", "")).strip()
    survey_url = f"{BASE_URL}/patientexperience/results?code={code}"

    record: dict[str, Any] = {
        "canonical_code": code,
        "practice_name_dataset": practice_name,
        "gpps_url": survey_url,
        "management_company_name": row.get("management_company_name", ""),
        "google_review_score": row.get("google_review_score", ""),
        "google_review_count": row.get("google_review_count", ""),
        "fetch_status": "error",
    }

    try:
        page_html = http_request(survey_url)
        page_meta = parse_practice_page(page_html)
        question_columns = list(page_meta["question_texts"].keys()) or FALLBACK_QUESTION_COLUMNS

        practice_payload = {"dataColumns": question_columns, "code": code}
        practice_data = fetch_json(TOP_LEVEL_ENDPOINTS["practice"], practice_payload)

        ics_results: dict[str, dict[str, Any]] = {}
        ics_code = str(page_meta.get("ics_code", "")).strip()
        if ics_code:
            ics_data = fetch_json(TOP_LEVEL_ENDPOINTS["ics"], {"dataColumns": question_columns, "code": ics_code})
            ics_results = top_level_index(ics_data.get("data", []))

        national_data = fetch_json(TOP_LEVEL_ENDPOINTS["national"], {"dataColumns": question_columns})
        practice_results = top_level_index(practice_data.get("data", []))
        national_results = top_level_index(national_data.get("data", []))

        key_questions = {
            question_column: build_question_record(
                question_column,
                page_meta["question_texts"],
                practice_results,
                ics_results,
                national_results,
            )
            for question_column in question_columns
        }

        record.update(
            {
                "practice_name_gpps": page_meta["practice_name_gpps"],
                "practice_address": page_meta["practice_address"],
                "ics_code": page_meta["ics_code"],
                "empty_practice": page_meta["empty_practice"],
                "surveys_sent_out": page_meta["surveys_sent_out"],
                "surveys_sent_back": page_meta["surveys_sent_back"],
                "completion_rate_percent": page_meta["completion_rate_percent"],
                "details_level": "key_questions_top_level",
                "active_project": ACTIVE_PROJECT,
                "key_questions": key_questions,
                "fetch_status": "ok",
            }
        )
    except Exception as exc:
        record["error"] = str(exc)

    if pause_max > 0:
        time.sleep(random.uniform(pause_min, pause_max))
    return record


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "practice"


def write_raw_record(output_dir: Path, record: dict[str, Any]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    code = str(record.get("canonical_code", "")).strip() or "unknown"
    name = str(record.get("practice_name_dataset") or record.get("practice_name_gpps") or "")
    path = output_dir / f"{code}-{slugify(name)}.json"
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def metric_value(record: dict[str, Any], question_column: str, field: str = "practice_percent") -> Any:
    key_questions = record.get("key_questions", {})
    if not isinstance(key_questions, dict):
        return None
    question_data = key_questions.get(question_column, {})
    if not isinstance(question_data, dict):
        return None
    return question_data.get(field)


def format_percent(value: Any) -> str:
    if value in ("", None):
        return ""
    return f"{value}%"


def format_google(value: Any, count: Any) -> str:
    if value in ("", None):
        return ""
    if count in ("", None):
        return str(value)
    return f"{value} ({count})"


def delta_text(left: Any, right: Any) -> str:
    if left in ("", None) or right in ("", None):
        return ""
    try:
        delta = float(left) - float(right)
    except (TypeError, ValueError):
        return ""
    return f"{delta:+.0f}"


def markdown_escape(value: Any) -> str:
    return normalize_whitespace(str(value or "")).replace("|", "\\|")


def summary_markdown(records: list[dict[str, Any]], source_dataset: Path, raw_output_dir: Path) -> str:
    ok_records = [record for record in records if record.get("fetch_status") == "ok"]
    error_records = [record for record in records if record.get("fetch_status") != "ok"]
    ranked_records = sorted(
        ok_records,
        key=lambda record: (
            metric_value(record, "overallexp") is None,
            metric_value(record, "overallexp") if metric_value(record, "overallexp") is not None else 999,
            str(record.get("practice_name_dataset", "")),
        ),
    )

    lines = [
        "# GP Patient Survey Focus Summary",
        "",
        "This file is compiled from raw per-practice GP Patient Survey JSON records.",
        "It keeps only the access and satisfaction signals that are most relevant to the current work.",
        "",
        "## Scope",
        "",
        "- `phone_easy`: patients who find it easy to get through by phone",
        "- `website_easy`: patients who find it easy to contact the practice via its website",
        "- `app_easy`: patients who find it easy to contact the practice via the NHS App",
        "- `contact_good`: patients who describe contacting the practice as a good experience",
        "- `overall_good`: patients who describe their overall practice experience as good",
        "- `needs_met`: patients who felt their needs were met at their last appointment",
        "- `support_ltc`: patients who say they had enough support from local services for long-term conditions",
        "",
        "## Run Metadata",
        "",
        f"- generated_date: `{time.strftime('%Y-%m-%d')}`",
        f"- source_dataset: `{source_dataset}`",
        f"- raw_output_dir: `{raw_output_dir}`",
        f"- total_records: `{len(records)}`",
        f"- successful_records: `{len(ok_records)}`",
        f"- failed_records: `{len(error_records)}`",
        f"- source_site: `{BASE_URL}`",
        "",
        "## Practice Snapshot",
        "",
        "| code | practice | manager | google | completion | phone_easy | website_easy | app_easy | contact_good | overall_good | needs_met | support_ltc | overall_vs_ics | phone_vs_ics |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    for record in ranked_records:
        overall = metric_value(record, "overallexp")
        phone = metric_value(record, "LocalGpServicesPhone")
        lines.append(
            "| "
            + " | ".join(
                [
                    markdown_escape(record.get("canonical_code")),
                    markdown_escape(record.get("practice_name_dataset") or record.get("practice_name_gpps")),
                    markdown_escape(record.get("management_company_name")),
                    markdown_escape(format_google(record.get("google_review_score"), record.get("google_review_count"))),
                    markdown_escape(format_percent(record.get("completion_rate_percent"))),
                    markdown_escape(format_percent(phone)),
                    markdown_escape(format_percent(metric_value(record, "localgpserviceswebsite"))),
                    markdown_escape(format_percent(metric_value(record, "localgpservicesapp"))),
                    markdown_escape(format_percent(metric_value(record, "gpcontactoverall"))),
                    markdown_escape(format_percent(overall)),
                    markdown_escape(format_percent(metric_value(record, "lastgpapptneeds"))),
                    markdown_escape(format_percent(metric_value(record, "healthsupport"))),
                    markdown_escape(delta_text(overall, metric_value(record, "overallexp", "ics_percent"))),
                    markdown_escape(delta_text(phone, metric_value(record, "LocalGpServicesPhone", "ics_percent"))),
                ]
            )
            + " |"
        )

    if error_records:
        lines.extend(
            [
                "",
                "## Fetch Failures",
                "",
                "| code | practice | error |",
                "| --- | --- | --- |",
            ]
        )
        for record in error_records:
            lines.append(
                "| "
                + " | ".join(
                    [
                        markdown_escape(record.get("canonical_code")),
                        markdown_escape(record.get("practice_name_dataset") or record.get("practice_name_gpps")),
                        markdown_escape(record.get("error")),
                    ]
                )
                + " |"
            )

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect GP Patient Survey practice data into raw JSON files plus a focused markdown summary.")
    parser.add_argument("--dataset-json", type=Path, default=DATASET_JSON)
    parser.add_argument("--raw-output-dir", type=Path, default=RAW_OUTPUT_DIR)
    parser.add_argument("--summary-md", type=Path, default=SUMMARY_MD)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--pause-min", type=float, default=0.15)
    parser.add_argument("--pause-max", type=float, default=0.35)
    args = parser.parse_args()

    rows = load_dataset_rows(args.dataset_json)
    if args.limit > 0:
        rows = rows[: args.limit]

    records: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        record = collect_record(row, args.pause_min, args.pause_max)
        records.append(record)
        write_raw_record(args.raw_output_dir, record)
        status = record.get("fetch_status", "error")
        code = record.get("canonical_code", "")
        name = record.get("practice_name_dataset", "")
        print(f"[{index}/{len(rows)}] {status} {code} {name}", file=sys.stderr)

    args.summary_md.write_text(summary_markdown(records, args.dataset_json, args.raw_output_dir), encoding="utf-8")
    summary = {
        "raw_output_dir": str(args.raw_output_dir),
        "summary_md": str(args.summary_md),
        "total_records": len(records),
        "successful_records": sum(1 for record in records if record.get("fetch_status") == "ok"),
        "failed_records": sum(1 for record in records if record.get("fetch_status") != "ok"),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
