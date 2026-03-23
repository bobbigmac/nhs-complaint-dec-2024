#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from selenium.webdriver.common.by import By

import fetch_scotland_hace_tableau as base


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = base.DEFAULT_INPUT
DEFAULT_DATASET_JSON = BASE_DIR / "scotland" / "hace_metrics.json"
LEGACY_OUTPUT_DIR = BASE_DIR / "output" / "scotland-hace-metrics"
PROFILE_COPY_DIR = BASE_DIR / ".tooling" / "firefox-profile-copy-scotland-hace-metrics"

OVERALL_QUESTION_TEXT = "Overall, how would you rate the care provided by your General Practice?"
TOOLTIP_SELECTORS = (
    ".tab-ubertip",
    ".tabTooltip",
    "[class*='tooltip']",
    "[class*='Tooltip']",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Dev-only Scotland HACE metrics collector. Uses one persistent Firefox session, "
            "reads only the live tooltip values needed for map-page survey fields, and updates "
            "the canonical Scotland metrics file in place."
        )
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--dataset-json", type=Path, default=DEFAULT_DATASET_JSON)
    parser.add_argument("--profile-copy", type=Path, default=PROFILE_COPY_DIR)
    parser.add_argument("--canonical-code", action="append", default=[])
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--max-age-days", type=int, default=31)
    parser.add_argument("--pause-seconds", type=float, default=0.4)
    return parser.parse_args()


def should_skip_recent(practice_entry: dict[str, Any] | None, max_age_days: int, force: bool) -> bool:
    if force or not practice_entry:
        return False
    fetched_at = practice_entry.get("fetched_at") or practice_entry.get("last_fetched_at")
    if not isinstance(fetched_at, str) or not fetched_at:
        return False
    try:
        fetched_at_dt = datetime.fromisoformat(fetched_at.replace("Z", "+00:00"))
    except ValueError:
        return False
    return datetime.now(UTC) - fetched_at_dt < timedelta(days=max_age_days)


def load_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def normalize_polished_entry(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": payload.get("status", ""),
        "fetched_at": payload.get("fetched_at", ""),
        "practice_name": payload.get("practice_name", ""),
        "tableau_report_area_label": payload.get("tableau_report_area_label", ""),
        "survey_overall_good_percent": payload.get("survey_overall_good_percent"),
        "response_rate_percent": payload.get("response_rate_percent"),
        "number_of_responses": payload.get("number_of_responses"),
        "responses_for_overall_question": payload.get("responses_for_overall_question"),
    }


def bootstrap_polished_dataset(dataset_path: Path, legacy_output_dir: Path) -> dict[str, Any]:
    dataset = load_json_object(dataset_path)
    practices = dataset.get("practices")
    if isinstance(practices, dict):
        return dataset

    dataset = {"practices": {}}
    legacy_manifest = load_json_object(legacy_output_dir / "manifest.json")
    legacy_practices = legacy_manifest.get("practices", {})
    if not isinstance(legacy_practices, dict):
        return dataset

    for code, entry in legacy_practices.items():
        if not isinstance(entry, dict):
            continue
        result_file = str(entry.get("result_file", "")).strip()
        if not result_file:
            continue
        result_path = legacy_output_dir / result_file
        result_payload = load_json_object(result_path)
        if not result_payload:
            continue
        normalized_code = str(code).strip().upper()
        if not normalized_code:
            continue
        dataset["practices"][normalized_code] = normalize_polished_entry(result_payload)
    return dataset


def tooltip_texts(driver) -> list[str]:
    texts: list[str] = []
    seen: set[str] = set()
    for css in TOOLTIP_SELECTORS:
        for element in driver.find_elements(By.CSS_SELECTOR, css):
            try:
                text = base.normalize_text(element.text)
            except Exception:
                continue
            if not text or text in seen:
                continue
            seen.add(text)
            texts.append(text)
    return texts


def set_report_combo_to_option(driver, wait, option_text: str, post_wait_seconds: float = 2.5) -> bool:
    combo = base.find_combo(driver, "Select specific report:")
    if base.normalize_choice_text(combo.text) == base.normalize_choice_text(option_text):
        return False
    base.click_element(driver, wait, combo)
    wait.until(lambda drv: len(base.option_texts_in_open_dropdown(drv)) > 100)
    wait.until(lambda drv: option_text in base.option_texts_in_open_dropdown(drv))
    if not base.click_open_option_by_text(driver, option_text):
        raise TimeoutError(f"Could not find report dropdown option {option_text!r}")
    wait.until(
        lambda drv: base.normalize_choice_text(base.find_combo(drv, "Select specific report:").text)
        == base.normalize_choice_text(option_text)
    )
    time.sleep(post_wait_seconds)
    return True


def hover_canvas_point(driver, canvas, client_x: float, client_y: float) -> None:
    driver.execute_script(
        """
        const el = arguments[0];
        const x = arguments[1];
        const y = arguments[2];
        const opts = { bubbles: true, clientX: x, clientY: y, view: window };
        el.dispatchEvent(new MouseEvent('mousemove', opts));
        el.dispatchEvent(new MouseEvent('mouseover', opts));
        el.dispatchEvent(new MouseEvent('mouseenter', opts));
        """,
        canvas,
        client_x,
        client_y,
    )


def canvas_rect(driver, canvas) -> dict[str, float]:
    payload = driver.execute_script(
        """
        const r = arguments[0].getBoundingClientRect();
        return { x: r.left, y: r.top, width: r.width, height: r.height };
        """,
        canvas,
    )
    return {
        "x": float(payload["x"]),
        "y": float(payload["y"]),
        "width": float(payload["width"]),
        "height": float(payload["height"]),
    }


def extract_overall_metric(driver, pause_seconds: float) -> dict[str, Any]:
    zone = driver.find_element(By.ID, "tabZoneId23")
    canvas = zone.find_elements(By.CSS_SELECTOR, "canvas")[-1]
    rect = canvas_rect(driver, canvas)
    row_center_offsets = [rect["height"] * 0.92, rect["height"] * 0.94, rect["height"] * 0.96]
    x_offsets = range(80, max(int(rect["width"]) - 40, 81), 20)

    for y_offset in row_center_offsets:
        client_y = rect["y"] + y_offset
        for x_offset in x_offsets:
            client_x = rect["x"] + x_offset
            hover_canvas_point(driver, canvas, client_x, client_y)
            time.sleep(pause_seconds)
            for text in tooltip_texts(driver):
                if OVERALL_QUESTION_TEXT not in text:
                    continue
                positive_match = re.search(r"Positive:\s*([0-9]+)%", text)
                responses_match = re.search(r"Responses:\s*([0-9][0-9,]*)", text)
                if not positive_match:
                    continue
                return {
                    "survey_overall_good_percent": int(positive_match.group(1)),
                    "responses_for_overall_question": (
                        int(responses_match.group(1).replace(",", "")) if responses_match else None
                    ),
                }
    return {}


def extract_response_panel_metrics(driver, pause_seconds: float) -> dict[str, Any]:
    zone = driver.find_element(By.ID, "tabZoneId257")
    canvas = zone.find_elements(By.CSS_SELECTOR, "canvas")[-1]
    rect = canvas_rect(driver, canvas)
    found: dict[str, Any] = {}

    probe_points = (
        (120, 20),
        (220, 20),
        (120, 50),
        (220, 50),
    )
    for x_offset, y_offset in probe_points:
        client_x = rect["x"] + x_offset
        client_y = rect["y"] + y_offset
        hover_canvas_point(driver, canvas, client_x, client_y)
        time.sleep(pause_seconds)
        for text in tooltip_texts(driver):
            if "Response rate:" in text and "response_rate_percent" not in found:
                match = re.search(r"Response rate:\s*([0-9]+)%", text)
                if match:
                    found["response_rate_percent"] = int(match.group(1))
            if "Number of responses:" in text and "number_of_responses" not in found:
                match = re.search(r"Number of responses:\s*([0-9][0-9,]*)", text)
                if match:
                    found["number_of_responses"] = int(match.group(1).replace(",", ""))
        if "response_rate_percent" in found and "number_of_responses" in found:
            break
    return found


def collect_one_practice(driver, wait, row: dict[str, str], report_label: str, pause_seconds: float) -> dict[str, Any]:
    set_report_combo_to_option(driver, wait, report_label, post_wait_seconds=2.5)
    time.sleep(0.8)
    fetched_at = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    overall_metric = extract_overall_metric(driver, pause_seconds)
    response_metric = extract_response_panel_metrics(driver, pause_seconds)

    status = "ok" if overall_metric.get("survey_overall_good_percent") is not None else "metric_not_found"
    return {
        "status": status,
        "fetched_at": fetched_at,
        "practice_name": row.get("practice_name", ""),
        "tableau_report_area_label": report_label,
        "survey_overall_good_percent": overall_metric.get("survey_overall_good_percent"),
        "response_rate_percent": response_metric.get("response_rate_percent"),
        "number_of_responses": response_metric.get("number_of_responses"),
        "responses_for_overall_question": overall_metric.get("responses_for_overall_question"),
    }


def main() -> int:
    args = parse_args()
    dataset = bootstrap_polished_dataset(args.dataset_json, LEGACY_OUTPUT_DIR)
    dataset_practices = dataset.setdefault("practices", {})
    if not isinstance(dataset_practices, dict):
        dataset_practices = {}
        dataset["practices"] = dataset_practices

    canonical_codes = {code.strip().upper() for code in args.canonical_code if code.strip()}
    rows = base.load_rows(args.input, canonical_codes, args.limit)
    if not rows:
        print("No Scotland practice rows matched the requested filters.")
        return 0

    started_at = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    dataset_meta = dataset.setdefault("_meta", {})
    if not isinstance(dataset_meta, dict):
        dataset_meta = {}
        dataset["_meta"] = dataset_meta
    dataset_meta["last_run_started_at"] = started_at
    dataset_meta["source_url"] = base.VIEW_URL
    base.write_json(args.dataset_json, dataset)

    source_profile = base.discover_default_firefox_profile()
    profile_copy = base.refresh_profile_copy(source_profile, args.profile_copy)
    print(f"Using Firefox profile copy: {profile_copy}", flush=True)
    driver = base.build_driver(profile_copy, headless=args.headless)
    print("Firefox driver started", flush=True)
    wait = base.build_wait(driver)
    processed = 0

    try:
        print("Loading Tableau dashboard", flush=True)
        base.wait_for_dashboard_ready(driver, wait)
        print("Dashboard ready", flush=True)
        base.install_capture(driver)
        print("Capture hooks installed", flush=True)
        base.ensure_general_practice_context(driver, wait)
        print("General Practice context selected", flush=True)
        practice_option_map = base.build_practice_option_map(driver, wait)
        print(f"Loaded {len(practice_option_map)} report options", flush=True)

        for row in rows:
            canonical_code = row.get("canonical_code", "").strip().upper()
            if not canonical_code:
                continue
            practice_entry = dataset_practices.get(canonical_code)
            if should_skip_recent(practice_entry if isinstance(practice_entry, dict) else None, args.max_age_days, args.force):
                continue

            suffix = base.canonical_suffix(canonical_code)
            report_label = practice_option_map.get(suffix, "")
            if not report_label:
                payload = {
                    "status": "missing_dropdown_option",
                    "fetched_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                    "practice_name": row.get("practice_name", ""),
                    "tableau_report_area_label": "",
                    "survey_overall_good_percent": None,
                    "response_rate_percent": None,
                    "number_of_responses": None,
                    "responses_for_overall_question": None,
                }
            else:
                payload = collect_one_practice(driver, wait, row, report_label, args.pause_seconds)

            polished_payload = normalize_polished_entry(payload)
            dataset_practices[canonical_code] = polished_payload
            processed += 1
            dataset_meta["processed_this_run"] = processed
            dataset_meta["practice_count"] = len(dataset_practices)
            base.write_json(args.dataset_json, dataset)
            print(
                f"[{processed}/{len(rows)}] {canonical_code} "
                f"status={payload.get('status')} "
                f"overall={payload.get('survey_overall_good_percent')} "
                f"response_rate={payload.get('response_rate_percent')} "
                f"responses={payload.get('number_of_responses')}"
            )
    finally:
        driver.quit()

    finished_at = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    dataset_meta["last_run_finished_at"] = finished_at
    dataset_meta["practice_count"] = len(dataset_practices)
    base.write_json(args.dataset_json, dataset)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
