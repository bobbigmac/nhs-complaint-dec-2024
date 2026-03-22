#!/usr/bin/env python3
from __future__ import annotations

import argparse
import configparser
import csv
import json
import re
import shutil
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = BASE_DIR / "output" / "scotland_gp_practices.csv"
DEFAULT_OUTPUT_DIR = BASE_DIR / "output" / "scotland-hace-tableau"
PROFILE_ROOT = Path.home() / ".mozilla" / "firefox"
PROFILE_COPY_DIR = BASE_DIR / ".tooling" / "firefox-profile-copy-scotland-hace"
VIEW_URL = (
    "https://public.tableau.com/views/3_HACE202324-DetailedExperienceRatings-Results/"
    "PNN?:embed=y&:showVizHome=no&publish=yes"
)
TABLEAU_CAPTURE_SCRIPT = r"""
return (() => {
  const existing = window.__scotlandHaceCapture;
  if (existing && existing.version === 1 && existing.clear && existing.snapshot) {
    return "already_installed";
  }

  const capture = window.__scotlandHaceCapture = existing || {};
  capture.version = 1;
  capture.entries = Array.isArray(capture.entries) ? capture.entries : [];
  capture.sequence = Number.isFinite(capture.sequence) ? capture.sequence : capture.entries.length;
  capture.maxEntries = 400;
  capture.matcher = function(url) {
    return typeof url === "string" && url.indexOf("/vizql/") !== -1;
  };
  capture.push = function(entry) {
    if (!entry || !capture.matcher(entry.url || "")) {
      return;
    }
    capture.entries.push({
      seq: ++capture.sequence,
      captured_at_ms: Date.now(),
      source: entry.source || "",
      method: entry.method || "",
      url: entry.url || "",
      status: Number.isFinite(entry.status) ? entry.status : null,
      ok: Boolean(entry.ok),
      content_type: entry.content_type || "",
      request_body: typeof entry.request_body === "string" ? entry.request_body : "",
      body: typeof entry.body === "string" ? entry.body : "",
      error: entry.error || "",
    });
    if (capture.entries.length > capture.maxEntries) {
      capture.entries = capture.entries.slice(-capture.maxEntries);
    }
  };
  capture.clear = function() {
    capture.entries = [];
    capture.sequence = 0;
  };
  capture.snapshot = function() {
    return capture.entries.slice();
  };

  if (!capture.fetchWrapped && typeof window.fetch === "function") {
    const originalFetch = window.fetch.bind(window);
    window.fetch = function(resource, init) {
      const responsePromise = originalFetch(resource, init);
      let url = "";
      if (typeof resource === "string") {
        url = resource;
      } else if (resource && typeof resource.url === "string") {
        url = resource.url;
      }
      if (capture.matcher(url)) {
        const method = (init && init.method) || (resource && resource.method) || "GET";
        const requestBody = init && typeof init.body === "string" ? init.body : "";
        responsePromise.then((response) => {
          const contentType = response && response.headers ? (response.headers.get("content-type") || "") : "";
          response.clone().text().then((bodyText) => {
            capture.push({
              source: "fetch",
              method: method,
              url: url,
              status: response.status,
              ok: response.ok,
              content_type: contentType,
              request_body: requestBody,
              body: bodyText,
            });
          }).catch((error) => {
            capture.push({
              source: "fetch",
              method: method,
              url: url,
              status: response.status,
              ok: response.ok,
              content_type: contentType,
              request_body: requestBody,
              error: String(error),
            });
          });
        }).catch((error) => {
          capture.push({
            source: "fetch",
            method: method,
            url: url,
            request_body: requestBody,
            error: String(error),
          });
        });
      }
      return responsePromise;
    };
    capture.fetchWrapped = true;
  }

  if (!capture.xhrWrapped && window.XMLHttpRequest && window.XMLHttpRequest.prototype) {
    const originalOpen = window.XMLHttpRequest.prototype.open;
    const originalSend = window.XMLHttpRequest.prototype.send;

    window.XMLHttpRequest.prototype.open = function(method, url) {
      this.__scotlandHaceMethod = method || "GET";
      this.__scotlandHaceUrl = url || "";
      return originalOpen.apply(this, arguments);
    };

    window.XMLHttpRequest.prototype.send = function(body) {
      const trackedUrl = this.__scotlandHaceUrl || "";
      if (capture.matcher(trackedUrl)) {
        const trackedMethod = this.__scotlandHaceMethod || "GET";
        const requestBody = typeof body === "string" ? body : "";
        this.addEventListener("loadend", () => {
          let responseBody = "";
          try {
            responseBody = typeof this.responseText === "string" ? this.responseText : "";
          } catch (error) {
            responseBody = "";
          }
          capture.push({
            source: "xhr",
            method: trackedMethod,
            url: trackedUrl,
            status: Number.isFinite(this.status) ? this.status : null,
            ok: this.status >= 200 && this.status < 400,
            content_type: this.getResponseHeader("content-type") || "",
            request_body: requestBody,
            body: responseBody,
          });
        }, { once: true });
      }
      return originalSend.apply(this, arguments);
    };
    capture.xhrWrapped = true;
  }

  return "installed";
})();
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Dev-only Scotland HACE collector. Uses one persistent Firefox session to step through "
            "the live Tableau dashboard and capture per-practice raw responses."
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
    parser.add_argument("--pause-seconds", type=float, default=1.0)
    return parser.parse_args()


def discover_default_firefox_profile() -> Path:
    profiles_ini = PROFILE_ROOT / "profiles.ini"
    if not profiles_ini.exists():
        raise RuntimeError("Firefox profiles.ini not found")
    parser = configparser.ConfigParser()
    parser.read(profiles_ini)

    install_sections = [name for name in parser.sections() if name.startswith("Install")]
    for section in install_sections:
        default_name = parser.get(section, "Default", fallback="")
        if default_name:
            candidate = PROFILE_ROOT / default_name
            if candidate.exists():
                return candidate

    for section in parser.sections():
        if not section.startswith("Profile"):
            continue
        if parser.getboolean(section, "Default", fallback=False):
            path = parser.get(section, "Path", fallback="")
            if path:
                candidate = PROFILE_ROOT / path
                if candidate.exists():
                    return candidate
    raise RuntimeError("Could not determine default Firefox profile")


def refresh_profile_copy(source_profile: Path, profile_copy_dir: Path) -> Path:
    if profile_copy_dir.exists():
        shutil.rmtree(profile_copy_dir)
    shutil.copytree(
        source_profile,
        profile_copy_dir,
        ignore=shutil.ignore_patterns(
            "parent.lock",
            "lock",
            ".parentlock",
            "lock.json",
            "minidumps",
            "crashes",
            "Pending Pings",
        ),
    )
    return profile_copy_dir


def build_driver(profile_dir: Path, headless: bool) -> webdriver.Firefox:
    opts = Options()
    if headless:
        opts.add_argument("-headless")
    opts.add_argument("-profile")
    opts.add_argument(str(profile_dir))
    opts.set_preference("browser.shell.checkDefaultBrowser", False)
    opts.set_preference("browser.aboutConfig.showWarning", False)
    opts.set_preference("dom.webnotifications.enabled", False)
    driver = webdriver.Firefox(options=opts)
    driver.set_page_load_timeout(90)
    return driver


def normalize_text(value: str) -> str:
    value = (value or "").replace("\xa0", " ")
    return " ".join(value.split())


def normalize_choice_text(value: str) -> str:
    value = normalize_text(value)
    if value.startswith("(") and value.endswith(")"):
        value = value[1:-1].strip()
    return value


def normalize_name(value: str) -> str:
    value = normalize_text(value).lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def slugify(value: str) -> str:
    return normalize_name(value) or "unknown"


def canonical_suffix(canonical_code: str) -> str:
    match = re.search(r"(\d+)$", canonical_code or "")
    return match.group(1) if match else ""


def xpath_literal(value: str) -> str:
    if "'" not in value:
        return f"'{value}'"
    if '"' not in value:
        return f'"{value}"'
    pieces = value.split("'")
    return "concat(" + ", \"'\", ".join(f"'{piece}'" for piece in pieces) + ")"


def build_wait(driver: webdriver.Firefox, timeout_seconds: int = 40) -> WebDriverWait:
    return WebDriverWait(driver, timeout_seconds)


def wait_for_dashboard_ready(driver: webdriver.Firefox, wait: WebDriverWait) -> None:
    driver.get(VIEW_URL)
    wait.until(lambda drv: "Select report level:" in drv.find_element(By.TAG_NAME, "body").text)
    wait.until(lambda drv: "Select specific report:" in drv.find_element(By.TAG_NAME, "body").text)
    wait.until(lambda drv: "Select survey section:" in drv.find_element(By.TAG_NAME, "body").text)


def install_capture(driver: webdriver.Firefox) -> str:
    return str(driver.execute_script(TABLEAU_CAPTURE_SCRIPT))


def clear_capture(driver: webdriver.Firefox) -> None:
    driver.execute_script(
        "if (window.__scotlandHaceCapture && window.__scotlandHaceCapture.clear) { window.__scotlandHaceCapture.clear(); }"
    )


def snapshot_capture(driver: webdriver.Firefox) -> list[dict[str, object]]:
    payload = driver.execute_script(
        "if (window.__scotlandHaceCapture && window.__scotlandHaceCapture.snapshot) { return window.__scotlandHaceCapture.snapshot(); } return [];"
    )
    return payload if isinstance(payload, list) else []


def capture_has_practice_filter_response(driver: webdriver.Firefox) -> bool:
    entries = snapshot_capture(driver)
    for entry in reversed(entries):
        if not isinstance(entry, dict):
            continue
        url = normalize_text(str(entry.get("url", "")))
        if "categorical-filter-by-index" not in url:
            continue
        if int(entry.get("status", 0) or 0) != 200:
            continue
        return True
    return False


def wait_for_glass_to_clear(driver: webdriver.Firefox, wait: WebDriverWait) -> None:
    try:
        wait.until(
            lambda drv: not any(
                element.is_displayed() for element in drv.find_elements(By.CSS_SELECTOR, ".tab-glass")
            )
        )
    except TimeoutException:
        return


def click_element(driver: webdriver.Firefox, wait: WebDriverWait, element) -> None:
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
    wait_for_glass_to_clear(driver, wait)
    try:
        element.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", element)


def option_texts_in_open_dropdown(driver: webdriver.Firefox) -> list[str]:
    payload = driver.execute_script(
        """
        return [...document.querySelectorAll('[role="option"]')]
          .map(el => (el.innerText || el.textContent || '').trim())
          .filter(Boolean);
        """
    )
    return [normalize_text(item) for item in payload if isinstance(item, str)]


def click_open_option_by_text(driver: webdriver.Firefox, option_text: str) -> bool:
    return bool(
        driver.execute_script(
            """
            const wanted = arguments[0];
            const option = [...document.querySelectorAll('[role="option"]')]
              .find(el => ((el.innerText || el.textContent || '').trim()) === wanted);
            if (!option) {
              return false;
            }
            option.scrollIntoView({block: 'center'});
            option.click();
            return true;
            """,
            option_text,
        )
    )


def find_combo(driver: webdriver.Firefox, label: str):
    xpath = (
        f"//span[normalize-space()={xpath_literal(label)}]"
        "//ancestor::div[contains(@class,'tab-zone')][1]"
        "//span[@role='combobox']"
    )
    return driver.find_element(By.XPATH, xpath)


def set_combo_to_option(
    driver: webdriver.Firefox,
    wait: WebDriverWait,
    label: str,
    option_text: str,
    post_wait_seconds: float = 1.5,
    strict: bool = True,
) -> bool:
    combo = find_combo(driver, label)
    if normalize_choice_text(combo.text) == normalize_choice_text(option_text):
        return False
    click_element(driver, wait, combo)
    try:
        wait.until(lambda drv: option_text in option_texts_in_open_dropdown(drv))
    except TimeoutException:
        if strict:
            raise
        return normalize_choice_text(find_combo(driver, label).text) == normalize_choice_text(option_text)
    if not click_open_option_by_text(driver, option_text):
        if strict:
            raise TimeoutException(f"Could not find dropdown option {option_text!r} for {label!r}")
        return normalize_choice_text(find_combo(driver, label).text) == normalize_choice_text(option_text)
    wait.until(lambda drv: normalize_choice_text(find_combo(drv, label).text) == normalize_choice_text(option_text))
    time.sleep(post_wait_seconds)
    return True


def ensure_general_practice_context(driver: webdriver.Firefox, wait: WebDriverWait) -> None:
    changed_level = set_combo_to_option(driver, wait, "Select report level:", "General Practice", post_wait_seconds=5.0)
    if changed_level:
        time.sleep(2)
    set_combo_to_option(
        driver,
        wait,
        "Select survey section:",
        "Your General Practice",
        post_wait_seconds=2.0,
        strict=False,
    )


def build_practice_option_map(driver: webdriver.Firefox, wait: WebDriverWait) -> dict[str, str]:
    combo = find_combo(driver, "Select specific report:")
    click_element(driver, wait, combo)
    wait.until(lambda drv: len(option_texts_in_open_dropdown(drv)) > 100)
    mapping: dict[str, str] = {}
    for text in option_texts_in_open_dropdown(driver):
        match = re.search(r"\((\d+)\)$", text)
        if match:
            mapping[match.group(1)] = text
    click_element(driver, wait, find_combo(driver, "Select specific report:"))
    time.sleep(1)
    return mapping


def read_zone_lines(driver: webdriver.Firefox, zone_id: str) -> list[str]:
    try:
        zone = driver.find_element(By.ID, f"tabZoneId{zone_id}")
    except NoSuchElementException:
        return []
    text = normalize_text(zone.text)
    if not text:
        return []
    return [line for line in (normalize_text(part) for part in zone.text.splitlines()) if line]


def read_zone_snapshot(driver: webdriver.Firefox, zone_id: str) -> dict[str, object]:
    lines = read_zone_lines(driver, zone_id)
    return {
        "zone_id": zone_id,
        "lines": lines,
    }


def extract_question_tiles(rag_lines: list[str]) -> list[dict[str, str]]:
    if not rag_lines:
        return []
    codes: list[str] = []
    index = 0
    while index < len(rag_lines) and re.fullmatch(r"\d{2}[a-z]?", rag_lines[index], flags=re.I):
        codes.append(rag_lines[index])
        index += 1
    if not codes:
        return []

    positive_index = None
    for idx, line in enumerate(rag_lines):
        if line == "Positive":
            positive_index = idx
            break

    if positive_index is None:
        values = rag_lines[-len(codes):]
        question_lines = rag_lines[index:-len(codes)]
    else:
        values_start = positive_index - len(codes)
        if values_start < index:
            return []
        values = rag_lines[values_start:positive_index]
        question_lines = rag_lines[index:values_start]

    questions: list[str] = []
    current: list[str] = []
    for line in question_lines:
        current.append(line)
        if line.endswith("?"):
            questions.append(" ".join(current))
            current = []
    if current:
        questions.append(" ".join(current))

    if len(questions) != len(codes) or len(values) != len(codes):
        return []

    return [
        {
            "question_code": code,
            "question_text": question,
            "visible_chart_value": value,
        }
        for code, question, value in zip(codes, questions, values, strict=True)
    ]


def extract_simple_metric_map(lines: list[str]) -> dict[str, str]:
    metrics: dict[str, str] = {}
    if len(lines) < 2:
        return metrics
    for idx, line in enumerate(lines[:-1]):
        next_line = lines[idx + 1]
        if line.lower().startswith("response rate") and (re.fullmatch(r"\d+%?", next_line) or "%" in next_line):
            metrics["response_rate"] = next_line
        if line.lower().startswith("number of responses") and re.fullmatch(r"\d[\d,]*", next_line):
            metrics["number_of_responses"] = next_line
    return metrics


def extract_vql_response(captures: list[dict[str, object]]) -> dict[str, object] | None:
    for entry in reversed(captures):
        if not isinstance(entry, dict):
            continue
        if int(entry.get("status", 0) or 0) != 200:
            continue
        url = normalize_text(str(entry.get("url", "")))
        if "categorical-filter-by-index" not in url:
            continue
        body = entry.get("body")
        if not isinstance(body, str) or not body.strip():
            continue
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return None
    return None


def load_manifest(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"practices": {}}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"practices": {}}


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def should_skip_recent(
    manifest_entry: dict[str, object] | None,
    raw_path: Path,
    max_age_days: int,
    force: bool,
) -> bool:
    if force or not manifest_entry or not raw_path.exists():
        return False
    fetched_at = manifest_entry.get("last_fetched_at")
    if not isinstance(fetched_at, str) or not fetched_at:
        return False
    try:
        fetched_at_dt = datetime.fromisoformat(fetched_at.replace("Z", "+00:00"))
    except ValueError:
        return False
    return datetime.now(UTC) - fetched_at_dt < timedelta(days=max_age_days)


def load_rows(input_path: Path, canonical_codes: set[str], limit: int) -> list[dict[str, str]]:
    with input_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    rows = [row for row in rows if normalize_text(row.get("nation", "")).lower() == "scotland"]
    if canonical_codes:
        rows = [row for row in rows if row.get("canonical_code", "") in canonical_codes]
    if limit > 0:
        rows = rows[:limit]
    return rows


def collect_one_practice(
    driver: webdriver.Firefox,
    wait: WebDriverWait,
    row: dict[str, str],
    report_label: str,
    output_dir: Path,
    pause_seconds: float,
) -> tuple[dict[str, object], Path]:
    clear_capture(driver)
    set_combo_to_option(driver, wait, "Select specific report:", report_label, post_wait_seconds=0.5)
    wait.until(lambda drv: capture_has_practice_filter_response(drv))
    time.sleep(pause_seconds)

    captures = snapshot_capture(driver)
    body_text = driver.find_element(By.TAG_NAME, "body").text
    rag_zone = read_zone_snapshot(driver, "23")
    response_rate_zone = read_zone_snapshot(driver, "257")
    location_zone = read_zone_snapshot(driver, "175")
    vql_response = extract_vql_response(captures)
    fetched_at = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    normalized = {
        "report_level": normalize_text(find_combo(driver, "Select report level:").text),
        "report_area": normalize_text(find_combo(driver, "Select specific report:").text),
        "survey_section": normalize_text(find_combo(driver, "Select survey section:").text),
        "question_tiles": extract_question_tiles(rag_zone["lines"]),
        "response_rate_metrics": extract_simple_metric_map(response_rate_zone["lines"]),
        "rag_chart_zone_lines": rag_zone["lines"],
        "response_rate_zone_lines": response_rate_zone["lines"],
        "location_zone_lines": location_zone["lines"],
        "captured_command_urls": [normalize_text(str(entry.get("url", ""))) for entry in captures if isinstance(entry, dict)],
    }

    payload = {
        "fetched_at": fetched_at,
        "source_url": VIEW_URL,
        "canonical_code": row.get("canonical_code", ""),
        "practice_name": row.get("practice_name", ""),
        "tableau_report_area_label": report_label,
        "input_row": row,
        "visible_state": {
            "body_text": body_text,
            "rag_chart_zone": rag_zone,
            "response_rate_zone": response_rate_zone,
            "location_zone": location_zone,
        },
        "normalized": normalized,
        "captures": captures,
        "practice_filter_vql_response": vql_response,
    }

    raw_dir = output_dir / "raw"
    raw_name = f"{row.get('canonical_code', '').lower()}-{slugify(row.get('practice_name', ''))}.json"
    raw_path = raw_dir / raw_name
    write_json(raw_path, payload)
    return payload, raw_path


def main() -> int:
    args = parse_args()
    input_path = args.input.resolve()
    output_dir = args.output_dir.resolve()
    manifest_path = output_dir / "manifest.json"
    canonical_codes = set(args.canonical_code)

    rows = load_rows(input_path, canonical_codes, args.limit)
    if not rows:
        raise SystemExit("No Scotland practice rows matched the requested filters.")

    manifest = load_manifest(manifest_path)
    practices_manifest = manifest.setdefault("practices", {})

    source_profile = discover_default_firefox_profile()
    profile_copy = refresh_profile_copy(source_profile, args.profile_copy.resolve())
    driver = build_driver(profile_copy, headless=args.headless)
    wait = build_wait(driver)

    try:
        wait_for_dashboard_ready(driver, wait)
        install_capture(driver)
        ensure_general_practice_context(driver, wait)
        practice_map = build_practice_option_map(driver, wait)
        manifest["source_url"] = VIEW_URL
        manifest["max_age_days"] = args.max_age_days
        manifest["last_run_started_at"] = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

        for index, row in enumerate(rows, start=1):
            canonical_code = row.get("canonical_code", "")
            suffix = canonical_suffix(canonical_code)
            report_label = practice_map.get(suffix)
            raw_name = f"{canonical_code.lower()}-{slugify(row.get('practice_name', ''))}.json"
            raw_path = output_dir / "raw" / raw_name
            manifest_entry = practices_manifest.get(canonical_code)

            if not report_label:
                print(f"[{index}/{len(rows)}] {canonical_code}: no Tableau dropdown label found for suffix {suffix}")
                practices_manifest[canonical_code] = {
                    "canonical_code": canonical_code,
                    "practice_name": row.get("practice_name", ""),
                    "status": "missing_dropdown_option",
                    "tableau_suffix": suffix,
                    "last_attempted_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                }
                write_json(manifest_path, manifest)
                continue

            if should_skip_recent(manifest_entry if isinstance(manifest_entry, dict) else None, raw_path, args.max_age_days, args.force):
                print(f"[{index}/{len(rows)}] {canonical_code}: skip recent ({report_label})")
                continue

            print(f"[{index}/{len(rows)}] {canonical_code}: fetch {report_label}")
            try:
                payload, written_raw_path = collect_one_practice(
                    driver=driver,
                    wait=wait,
                    row=row,
                    report_label=report_label,
                    output_dir=output_dir,
                    pause_seconds=args.pause_seconds,
                )
                practices_manifest[canonical_code] = {
                    "canonical_code": canonical_code,
                    "practice_name": row.get("practice_name", ""),
                    "tableau_report_area_label": report_label,
                    "status": "ok",
                    "last_fetched_at": payload["fetched_at"],
                    "raw_file": str(written_raw_path.relative_to(output_dir)),
                    "question_tile_count": len(payload["normalized"]["question_tiles"]),
                    "captured_response_count": len(payload["captures"]),
                }
            except (NoSuchElementException, StaleElementReferenceException, TimeoutException) as exc:
                print(f"[{index}/{len(rows)}] {canonical_code}: failed ({type(exc).__name__})")
                practices_manifest[canonical_code] = {
                    "canonical_code": canonical_code,
                    "practice_name": row.get("practice_name", ""),
                    "tableau_report_area_label": report_label,
                    "status": "failed",
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "last_attempted_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                }
            write_json(manifest_path, manifest)
    finally:
        driver.quit()

    manifest["last_run_finished_at"] = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    write_json(manifest_path, manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
