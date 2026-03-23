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
DEFAULT_OUTPUT_DIR = BASE_DIR / "output" / "scotland-hace-metrics"
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
            "Dev-only Scotland HACE metrics collector. Uses one persistent Firefox session and "
            "reads only the live tooltip values needed for map-page survey fields."
        )
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--profile-copy", type=Path, default=PROFILE_COPY_DIR)
    parser.add_argument("--canonical-code", action="append", default=[])
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--max-age-days", type=int, default=31)
    parser.add_argument("--pause-seconds", type=float, default=0.4)
    return parser.parse_args()


def result_filename(row: dict[str, str]) -> str:
    return f"{row.get('canonical_code', '').lower()}-{base.slugify(row.get('practice_name', ''))}.json"


def should_skip_recent(manifest_entry: dict[str, Any] | None, result_path: Path, max_age_days: int, force: bool) -> bool:
    if force or not manifest_entry or not result_path.exists():
        return False
    fetched_at = manifest_entry.get("last_fetched_at")
    if not isinstance(fetched_at, str) or not fetched_at:
        return False
    try:
        fetched_at_dt = datetime.fromisoformat(fetched_at.replace("Z", "+00:00"))
    except ValueError:
        return False
    return datetime.now(UTC) - fetched_at_dt < timedelta(days=max_age_days)


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
                    "tooltip_text": text,
                    "survey_overall_good_percent": int(positive_match.group(1)),
                    "responses_for_overall_question": (
                        int(responses_match.group(1).replace(",", "")) if responses_match else None
                    ),
                    "hover_point": {
                        "x_offset": x_offset,
                        "y_offset": round(y_offset, 1),
                    },
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
                    found["response_rate_tooltip_text"] = text
            if "Number of responses:" in text and "number_of_responses" not in found:
                match = re.search(r"Number of responses:\s*([0-9][0-9,]*)", text)
                if match:
                    found["number_of_responses"] = int(match.group(1).replace(",", ""))
                    found["number_of_responses_tooltip_text"] = text
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
        "source_url": base.VIEW_URL,
        "canonical_code": row.get("canonical_code", ""),
        "practice_name": row.get("practice_name", ""),
        "tableau_report_area_label": report_label,
        "survey_overall_good_percent": overall_metric.get("survey_overall_good_percent"),
        "response_rate_percent": response_metric.get("response_rate_percent"),
        "number_of_responses": response_metric.get("number_of_responses"),
        "responses_for_overall_question": overall_metric.get("responses_for_overall_question"),
        "overall_tooltip_text": overall_metric.get("tooltip_text", ""),
        "response_rate_tooltip_text": response_metric.get("response_rate_tooltip_text", ""),
        "number_of_responses_tooltip_text": response_metric.get("number_of_responses_tooltip_text", ""),
        "hover_point": overall_metric.get("hover_point", {}),
    }


def save_result(output_dir: Path, payload: dict[str, Any]) -> Path:
    row = {
        "canonical_code": str(payload.get("canonical_code", "")).strip(),
        "practice_name": str(payload.get("practice_name", "")).strip(),
    }
    result_path = output_dir / "results" / result_filename(row)
    base.write_json(result_path, payload)
    return result_path


def main() -> int:
    args = parse_args()
    manifest_path = args.output_dir / "manifest.json"
    manifest = base.load_manifest(manifest_path)
    practices_manifest = manifest.setdefault("practices", {})
    if not isinstance(practices_manifest, dict):
        practices_manifest = {}
        manifest["practices"] = practices_manifest

    canonical_codes = {code.strip().upper() for code in args.canonical_code if code.strip()}
    rows = base.load_rows(args.input, canonical_codes, args.limit)
    if not rows:
        print("No Scotland practice rows matched the requested filters.")
        return 0

    started_at = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    manifest["last_run_started_at"] = started_at
    base.write_json(manifest_path, manifest)

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
            manifest_entry = practices_manifest.get(canonical_code)
            result_path = args.output_dir / "results" / result_filename(row)
            if should_skip_recent(manifest_entry if isinstance(manifest_entry, dict) else None, result_path, args.max_age_days, args.force):
                continue

            suffix = base.canonical_suffix(canonical_code)
            report_label = practice_option_map.get(suffix, "")
            if not report_label:
                payload = {
                    "status": "missing_dropdown_option",
                    "fetched_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                    "source_url": base.VIEW_URL,
                    "canonical_code": canonical_code,
                    "practice_name": row.get("practice_name", ""),
                    "tableau_report_area_label": "",
                    "survey_overall_good_percent": None,
                    "response_rate_percent": None,
                    "number_of_responses": None,
                    "responses_for_overall_question": None,
                    "overall_tooltip_text": "",
                    "response_rate_tooltip_text": "",
                    "number_of_responses_tooltip_text": "",
                    "hover_point": {},
                }
            else:
                payload = collect_one_practice(driver, wait, row, report_label, args.pause_seconds)

            written_path = save_result(args.output_dir, payload)
            practices_manifest[canonical_code] = {
                "status": payload.get("status", ""),
                "practice_name": payload.get("practice_name", ""),
                "tableau_report_area_label": payload.get("tableau_report_area_label", ""),
                "last_fetched_at": payload.get("fetched_at", ""),
                "result_file": str(written_path.relative_to(args.output_dir)),
                "survey_overall_good_percent": payload.get("survey_overall_good_percent"),
                "response_rate_percent": payload.get("response_rate_percent"),
                "number_of_responses": payload.get("number_of_responses"),
            }
            processed += 1
            manifest["processed_this_run"] = processed
            base.write_json(manifest_path, manifest)
            print(
                f"[{processed}/{len(rows)}] {canonical_code} "
                f"status={payload.get('status')} "
                f"overall={payload.get('survey_overall_good_percent')} "
                f"response_rate={payload.get('response_rate_percent')} "
                f"responses={payload.get('number_of_responses')}"
            )
    finally:
        driver.quit()

    manifest["last_run_finished_at"] = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    base.write_json(manifest_path, manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
