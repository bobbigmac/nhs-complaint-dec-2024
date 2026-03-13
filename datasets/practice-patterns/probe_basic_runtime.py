#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
import time
from configparser import ConfigParser
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait


FIREFOX_DIR = Path.home() / ".mozilla" / "firefox"
PROFILE_IGNORE = {
    "lock",
    ".parentlock",
    "parent.lock",
    "lockfile",
    "singletonCookie",
    "singletonLock",
    "singletonSocket",
    "sessionstore*",
    "recovery.jsonlz4",
    "recovery.baklz4",
    "sessionCheckpoints.json",
    "startupCache",
    "cache2",
    "minidumps",
}


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_default_profile() -> Path:
    profiles_ini = FIREFOX_DIR / "profiles.ini"
    parser = ConfigParser()
    parser.read(profiles_ini)

    default_path = None
    for section in parser.sections():
        if section.startswith("Install") and parser.get(section, "Default", fallback=""):
            default_path = parser.get(section, "Default")
            break
    if not default_path:
        raise RuntimeError(f"Could not determine a default Firefox profile from {profiles_ini}")
    return FIREFOX_DIR / default_path


def copy_profile(source: Path) -> Path:
    temp_root = Path(tempfile.mkdtemp(prefix="practice-patterns-runtime-"))
    target = temp_root / "profile"
    shutil.copytree(source, target, ignore=shutil.ignore_patterns(*PROFILE_IGNORE))
    return target


def make_driver(profile_path: Path, headless: bool, timeout_seconds: int) -> webdriver.Firefox:
    options = Options()
    options.binary_location = shutil.which("firefox") or "/usr/bin/firefox"
    options.profile = str(profile_path)
    options.page_load_strategy = "eager"
    options.set_preference("browser.startup.page", 0)
    options.set_preference("browser.sessionstore.resume_from_crash", False)
    options.set_preference("browser.sessionstore.resume_session_once", False)
    options.set_preference("startup.homepage_welcome_url", "about:blank")
    options.set_preference("startup.homepage_welcome_url.additional", "")
    if headless:
        options.add_argument("-headless")
    driver = webdriver.Firefox(options=options, service=Service())
    driver.set_page_load_timeout(timeout_seconds)
    return driver


def wait_until_ready(driver: webdriver.Firefox, timeout_seconds: int) -> None:
    WebDriverWait(driver, timeout_seconds).until(
        lambda d: d.execute_script("return document.readyState") in ("interactive", "complete")
    )


def run_check(driver: webdriver.Firefox, label: str, url: str, timeout_seconds: int) -> dict[str, Any]:
    started_at = iso_now()
    start = time.perf_counter()
    error = None
    final_url = url
    title = ""
    status = "live"
    try:
        driver.get(url)
        wait_until_ready(driver, timeout_seconds)
        final_url = driver.current_url
        title = driver.title
    except (TimeoutException, WebDriverException) as exc:
        status = "timeout_or_error"
        error = f"{type(exc).__name__}: {exc}"
        try:
            final_url = driver.current_url
            title = driver.title
        except Exception:
            final_url = url
            title = ""
    load_ms = round((time.perf_counter() - start) * 1000, 1)
    return {
        "checked_at": started_at,
        "label": label,
        "url": url,
        "final_url": final_url,
        "title": title,
        "status": status,
        "load_ms": load_ms,
        "error": error,
    }


def parse_checks(values: list[str]) -> list[tuple[str, str]]:
    checks: list[tuple[str, str]] = []
    for value in values:
        if "=" not in value:
            raise ValueError(f"Invalid --check value: {value!r}. Expected label=url")
        label, url = value.split("=", 1)
        checks.append((label.strip(), url.strip()))
    return checks


def main() -> None:
    parser = argparse.ArgumentParser(description="Run simple top-level runtime checks for selected practice URLs.")
    parser.add_argument("--check", action="append", default=[], help="label=url")
    parser.add_argument("--profile", help="Firefox profile directory to copy before launch")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=25)
    parser.add_argument("--output")
    args = parser.parse_args()

    checks = parse_checks(args.check)
    source_profile = Path(args.profile).expanduser() if args.profile else read_default_profile()
    copied_profile = copy_profile(source_profile)

    driver = None
    payload: dict[str, Any] = {
        "generated_at": iso_now(),
        "headless": args.headless,
        "timeout_seconds": args.timeout_seconds,
        "checks": [],
    }
    try:
        driver = make_driver(copied_profile, args.headless, args.timeout_seconds)
        for label, url in checks:
            payload["checks"].append(run_check(driver, label, url, args.timeout_seconds))
    finally:
        if driver is not None:
            driver.quit()
        shutil.rmtree(copied_profile.parent, ignore_errors=True)

    text = json.dumps(payload, indent=2)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
