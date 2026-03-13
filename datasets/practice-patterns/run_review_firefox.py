#!/usr/bin/env python3
"""
Run a practice-pattern review using Firefox with a copied local profile.

Essential: Uses a profile copy so Google and other sites treat the session as a real user,
avoiding captchas and bot blocks that would distort the patient experience.

Usage:
  python run_review_firefox.py G3K4Y              # headful, opens browser for manual drive
  python run_review_firefox.py G3K4Y --capture   # headful, automates traversal and captures
  python run_review_firefox.py G3K4Y --headless  # route probes only; not for full review
"""
from __future__ import annotations

import argparse
import configparser
import json
import re
import shutil
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


PROFILE_ROOT = Path.home() / ".mozilla" / "firefox"
PROFILE_COPY_DIR = Path(__file__).resolve().parent.parent / ".tooling" / "firefox-profile-copy"

PRACTICE_CONFIG = {
    "G3K4Y": {
        "name": "Corkland Road Medical Practice",
        "nhs_profile": "https://www.nhs.uk/services/gp-surgery/corkland-road-medical-practice/G3K4Y",
        "known_parent_site": "https://chorltonfamilypractice.nhs.uk/",
    },
}


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
    profile_copy_dir.parent.mkdir(parents=True, exist_ok=True)
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


def capture_page(driver: webdriver.Firefox) -> dict:
    """Capture title, URL, and main text content from current page."""
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        text = body.text[:8000] if body.text else ""
    except Exception:
        text = ""
    return {
        "url": driver.current_url,
        "title": driver.title,
        "body_preview": text[:2000],
    }


def run_g3k4y_capture(driver: webdriver.Firefox, wait: WebDriverWait) -> dict:
    """Traverse G3K4Y / Chorlton routes and capture observations."""
    cfg = PRACTICE_CONFIG["G3K4Y"]
    captured = {"nhs_profile": [], "parent_site": [], "discovered_paths": []}

    # 1. NHS profile
    driver.get(cfg["nhs_profile"])
    time.sleep(2)
    captured["nhs_profile"].append(capture_page(driver))

    # 2. NHS contact page
    driver.get(cfg["nhs_profile"] + "/contact-details-and-opening-times")
    time.sleep(2)
    captured["nhs_profile"].append(capture_page(driver))

    # 3. Parent site homepage
    driver.get(cfg["known_parent_site"])
    time.sleep(2)
    captured["parent_site"].append(capture_page(driver))

    # 4. Try appointments link
    try:
        appointments = wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Appointments"))
        )
        appointments.click()
        time.sleep(2)
        captured["discovered_paths"].append(
            {"label": "Appointments", **capture_page(driver)}
        )
    except Exception as e:
        captured["discovered_paths"].append(
            {"label": "Appointments", "error": str(e), "url": driver.current_url}
        )

    # 5. Back to home, try Prescriptions
    driver.get(cfg["known_parent_site"])
    time.sleep(2)
    try:
        prescriptions = wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Prescriptions"))
        )
        prescriptions.click()
        time.sleep(2)
        captured["discovered_paths"].append(
            {"label": "Prescriptions", **capture_page(driver)}
        )
    except Exception as e:
        captured["discovered_paths"].append(
            {"label": "Prescriptions", "error": str(e), "url": driver.current_url}
        )

    # 6. Contact us
    driver.get(cfg["known_parent_site"])
    time.sleep(2)
    try:
        contact = wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Contact us"))
        )
        contact.click()
        time.sleep(2)
        captured["discovered_paths"].append(
            {"label": "Contact us", **capture_page(driver)}
        )
    except Exception as e:
        captured["discovered_paths"].append(
            {"label": "Contact us", "error": str(e), "url": driver.current_url}
        )

    # 7. Feedback, Complaints and Compliments
    driver.get(cfg["known_parent_site"] + "services/")
    time.sleep(2)
    try:
        feedback = wait.until(
            EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Feedback"))
        )
        feedback.click()
        time.sleep(2)
        captured["discovered_paths"].append(
            {"label": "Feedback/complaints", **capture_page(driver)}
        )
    except Exception as e:
        captured["discovered_paths"].append(
            {"label": "Feedback/complaints", "error": str(e), "url": driver.current_url}
        )

    # 8. PATCHS link from patient notice
    driver.get(cfg["known_parent_site"])
    time.sleep(2)
    try:
        patchs = wait.until(
            EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "PATCHS"))
        )
        patchs.click()
        time.sleep(2)
        captured["discovered_paths"].append(
            {"label": "PATCHS", **capture_page(driver)}
        )
    except Exception as e:
        captured["discovered_paths"].append(
            {"label": "PATCHS", "error": str(e), "url": driver.current_url}
        )

    return captured


def main() -> None:
    parser = argparse.ArgumentParser(description="Run practice review with Firefox profile copy")
    parser.add_argument("ods_code", help="ODS code e.g. G3K4Y")
    parser.add_argument("--headless", action="store_true", help="Headless mode (route probes only)")
    parser.add_argument("--capture", action="store_true", help="Automate traversal and capture")
    parser.add_argument("--profile-copy", type=Path, default=PROFILE_COPY_DIR)
    parser.add_argument("-o", "--output", type=Path, help="Write capture JSON here")
    args = parser.parse_args()

    if args.ods_code not in PRACTICE_CONFIG:
        print(f"Unknown ODS code. Supported: {list(PRACTICE_CONFIG)}")
        return

    print("1. Discovering default Firefox profile...")
    source_profile = discover_default_firefox_profile()
    print(f"   Source: {source_profile}")

    print("2. Refreshing profile copy...")
    profile_copy = refresh_profile_copy(source_profile, args.profile_copy)
    print(f"   Copy: {profile_copy}")

    print("3. Launching Firefox...")
    driver = build_driver(profile_copy, headless=args.headless)
    wait = WebDriverWait(driver, 15)

    try:
        if args.capture and args.ods_code == "G3K4Y":
            print("4. Running G3K4Y capture...")
            captured = run_g3k4y_capture(driver, wait)
            out = args.output or Path(__file__).parent / "capture_G3K4Y.json"
            out.write_text(json.dumps(captured, indent=2))
            print(f"   Wrote {out}")
        else:
            cfg = PRACTICE_CONFIG[args.ods_code]
            driver.get(cfg["nhs_profile"])
            print("   Browser ready. Drive the session manually for full review.")
            input("   Press Enter when done to close...")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
