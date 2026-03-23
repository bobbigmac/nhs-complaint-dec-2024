#!/usr/bin/env python3
from __future__ import annotations

import argparse
import configparser
import csv
import json
import math
import random
import re
import shutil
import time
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATASET = BASE_DIR / "output" / "gtd-greater-manchester-gp-practice-reviews-2026-03-09" / "gtd_greater_manchester_gp_practices.csv"
PROFILE_ROOT = Path.home() / ".mozilla" / "firefox"
PROFILE_COPY_DIR = BASE_DIR / ".tooling" / "firefox-profile-copy"
DEFAULT_OUTPUT = BASE_DIR / "output" / "gtd-greater-manchester-gp-practice-reviews-2026-03-09" / "google_maps_recent_reviews.json"
DEFAULT_TEXT_DIR = BASE_DIR / "output" / "gtd-greater-manchester-gp-practice-reviews-2026-03-09" / "google-review-texts"
DEFAULT_RAW_REVIEW_DIR = BASE_DIR / "output" / "gtd-greater-manchester-gp-practice-reviews-2026-03-09" / "google-review-raw"
DEFAULT_QUERY_OVERRIDES = BASE_DIR / "config" / "google_maps_query_overrides.json"
RAW_REVIEW_CAPTURE_SCRIPT = r"""
return (() => {
  const existing = window.__gmReviewCapture;
  if (existing && existing.version === 1 && existing.clear && existing.snapshot) {
    return "already_installed";
  }

  const capture = window.__gmReviewCapture = existing || {};
  capture.version = 1;
  capture.entries = Array.isArray(capture.entries) ? capture.entries : [];
  capture.sequence = Number.isFinite(capture.sequence) ? capture.sequence : capture.entries.length;
  capture.maxEntries = 400;
  capture.matcher = function(url) {
    return typeof url === "string" && url.indexOf("/maps/rpc/listugcposts") !== -1;
  };
  capture.push = function(entry) {
    if (!entry || !capture.matcher(entry.url || "")) {
      return;
    }
    const normalized = {
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
    };
    capture.entries.push(normalized);
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
      this.__gmReviewCaptureMethod = method || "GET";
      this.__gmReviewCaptureUrl = url || "";
      return originalOpen.apply(this, arguments);
    };

    window.XMLHttpRequest.prototype.send = function(body) {
      const trackedUrl = this.__gmReviewCaptureUrl || "";
      if (capture.matcher(trackedUrl)) {
        const trackedMethod = this.__gmReviewCaptureMethod || "GET";
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


def build_wait(driver: webdriver.Firefox, timeout_seconds: int = 25) -> WebDriverWait:
    return WebDriverWait(driver, timeout_seconds)


def normalize_text(value: str) -> str:
    value = (value or "").replace("\xa0", " ")
    value = re.sub(r"[\ue000-\uf8ff]", "", value)
    return " ".join(value.split())


def normalize_name(value: str) -> str:
    value = (value or "").lower().replace("&", " and ")
    value = re.sub(r"[’']", "", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def parse_google_maps_coordinates(url: str) -> tuple[float, float] | None:
    if not url:
        return None
    for pattern in (
        r"!3d(-?\d+(?:\.\d+)?)!4d(-?\d+(?:\.\d+)?)",
        r"@(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)",
    ):
        match = re.search(pattern, url)
        if not match:
            continue
        try:
            return float(match.group(1)), float(match.group(2))
        except ValueError:
            continue
    return None


def query_friendly_name(value: str) -> str:
    value = (value or "").strip()
    # NHS branch names sometimes start with numeric prefixes like "1/" or "3/".
    # Google Maps can collapse these into useless single-character searches.
    value = re.sub(r"^\d+\s*/\s*", "", value)
    return " ".join(value.split())


def token_set(value: str) -> set[str]:
    return {
        token
        for token in normalize_name(value).split()
        if token not in {"the", "and", "of", "medical", "practice", "centre", "center", "surgery", "group", "health"}
        and not any(char.isdigit() for char in token)
    }


def title_similarity(left: str, right: str) -> float:
    left_tokens = token_set(left)
    right_tokens = token_set(right)
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / max(len(left_tokens), len(right_tokens))


HEALTHCARE_HINT_TOKENS = {
    "clinic",
    "doctor",
    "doctors",
    "dr",
    "gp",
    "health",
    "medical",
    "partners",
    "practice",
    "surgery",
}

GENERIC_PLACE_TITLES = {
    normalize_name("Medical Centre"),
    normalize_name("Medical Center"),
    normalize_name("The Surgery"),
    normalize_name("Doctors"),
    normalize_name("Doctor"),
}


def normalized_postcode(value: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", (value or "").upper())


def outward_postcode(value: str) -> str:
    normalized = normalized_postcode(value)
    match = re.match(r"^([A-Z]{1,2}\d[A-Z\d]?)", normalized)
    return match.group(1) if match else ""


def text_hint_tokens(value: str) -> set[str]:
    return {
        token
        for token in normalize_name(value).split()
        if token not in {"the", "and", "of", "road", "street", "lane", "close", "avenue", "high", "st"}
        and len(token) >= 3
    }


def has_healthcare_hint(value: str) -> bool:
    normalized = normalize_name(value)
    if not normalized:
        return False
    tokens = set(normalized.split())
    return any(token in HEALTHCARE_HINT_TOKENS for token in tokens)


def contextual_text_bonus(label: str, postcode: str, street_address: str) -> float:
    bonus = 0.0
    postcode_full = normalized_postcode(postcode)
    postcode_outward = outward_postcode(postcode)
    normalized_label_compact = normalized_postcode(label)
    if postcode_full and postcode_full in normalized_label_compact:
        bonus += 0.4
    elif postcode_outward and postcode_outward in normalized_label_compact:
        bonus += 0.1

    address_tokens = text_hint_tokens(street_address)
    label_tokens = text_hint_tokens(label)
    overlap = len(address_tokens & label_tokens)
    if overlap:
        bonus += min(0.3, overlap * 0.12)

    if has_healthcare_hint(label):
        bonus += 0.08

    if normalize_name(label) in GENERIC_PLACE_TITLES:
        bonus -= 0.12
    return bonus


def parse_optional_float(value: object) -> float | None:
    try:
        if value is None or str(value).strip() == "":
            return None
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def expected_coordinates_for_row(row: dict[str, str]) -> tuple[float, float] | None:
    latitude = parse_optional_float(row.get("latitude"))
    longitude = parse_optional_float(row.get("longitude"))
    if latitude is None or longitude is None:
        return None
    return latitude, longitude


def coordinate_distance_miles(left: tuple[float, float], right: tuple[float, float]) -> float:
    lat1, lon1 = map(math.radians, left)
    lat2, lon2 = map(math.radians, right)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return 3958.7613 * c


def place_contextually_matches(
    expected_practice_name: str,
    place_title: str,
    place_address_text: str,
    postcode: str,
    street_address: str,
    expected_coordinates: tuple[float, float] | None,
    chosen_search_result_label: str = "",
    current_url: str = "",
) -> bool:
    if title_similarity(expected_practice_name, place_title) >= 0.25:
        return True

    normalized_address = normalize_text(place_address_text or "")
    exact_postcode_match = False
    postcode_full = normalized_postcode(postcode)
    if postcode_full:
        address_compact = normalized_postcode(normalized_address)
        exact_postcode_match = postcode_full in address_compact

    contextual_blob = " ".join(part for part in [place_title, chosen_search_result_label, normalized_address] if part).strip()
    street_overlap = len(text_hint_tokens(contextual_blob) & text_hint_tokens(street_address)) > 0
    healthcare_hint = has_healthcare_hint(contextual_blob)

    near_expected = False
    parsed_coords = parse_google_maps_coordinates(current_url or "")
    if parsed_coords is not None and expected_coordinates is not None:
        near_expected = coordinate_distance_miles(parsed_coords, expected_coordinates) <= 0.2

    return healthcare_hint and exact_postcode_match and (street_overlap or near_expected)


def slugify(value: str) -> str:
    value = normalize_name(value).replace(" ", "-")
    return value.strip("-")


def parse_reviews_count(label: str) -> int | None:
    match = re.search(r"([0-9,]+)\s+reviews", label, flags=re.I)
    return int(match.group(1).replace(",", "")) if match else None


def is_truthy(value: object) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def is_gtd_managed_row(row: dict[str, str]) -> bool:
    if is_truthy(row.get("gtd_managed", "")):
        return True
    return normalize_name(str(row.get("management_company_name", ""))) == "gtd healthcare"


BLOCKED_PLACE_TITLES = {
    normalize_name("The Range Medical Centre"),
    normalize_name("The Brooke Surgery"),
}


def is_blocked_place_title(title: str) -> bool:
    return normalize_name(title) in BLOCKED_PLACE_TITLES


def element_or_ancestor_mentions_sponsored(driver: webdriver.Firefox, element, max_levels: int = 5) -> bool:
    try:
        snippets = driver.execute_script(
            """
            const out = [];
            let node = arguments[0];
            const maxLevels = arguments[1];
            for (let i = 0; node && i < maxLevels; i += 1, node = node.parentElement) {
              out.push([
                node.textContent || '',
                node.getAttribute('aria-label') || '',
                node.getAttribute('title') || '',
              ].join(' '));
            }
            return out;
            """,
            element,
            max_levels,
        )
    except Exception:
        return False
    for snippet in snippets or []:
        if "sponsored" in normalize_name(str(snippet)):
            return True
    return False


def page_has_sponsored_marker(driver: webdriver.Firefox) -> bool:
    try:
        candidates = driver.find_elements(By.XPATH, "//*[contains(normalize-space(.), 'Sponsored')]")
    except Exception:
        return False
    for candidate in candidates[:25]:
        try:
            if candidate.is_displayed():
                return True
        except StaleElementReferenceException:
            continue
    return False


def extract_overall_metrics(driver: webdriver.Firefox) -> tuple[str, float | None, int | None]:
    title = driver.title.removesuffix(" - Google Maps").strip()
    rating = None
    review_count = None
    spans = driver.find_elements(By.CSS_SELECTOR, 'div[role="main"] span')
    for span in spans:
        try:
            text = normalize_text(span.text)
            aria = normalize_text(span.get_attribute("aria-label") or "")
        except StaleElementReferenceException:
            continue
        if rating is None and re.fullmatch(r"[0-5]\.\d", text):
            rating = float(text)
        if review_count is None and "reviews" in aria.lower():
            parsed = parse_reviews_count(aria)
            if parsed is not None:
                review_count = parsed
        if rating is not None and review_count is not None:
            break
    return title, rating, review_count


def extract_place_address_text(driver: webdriver.Firefox) -> str:
    selectors = [
        'button[data-item-id*="address"]',
        'div[data-item-id*="address"]',
        'button[aria-label*="Address"]',
        'div[aria-label*="Address"]',
    ]
    for selector in selectors:
        for element in driver.find_elements(By.CSS_SELECTOR, selector):
            try:
                text = normalize_text(
                    element.text
                    or element.get_attribute("aria-label")
                    or element.get_attribute("data-item-id")
                    or ""
                )
            except StaleElementReferenceException:
                continue
            if not text:
                continue
            if text.lower().startswith("address:"):
                return normalize_text(text.split(":", 1)[1])
            if "address" not in text.lower():
                return text
    return ""


def find_search_input(driver: webdriver.Firefox):
    selectors = [
        "input#searchboxinput",
        'input[role="combobox"]',
        'input[class*="UGojuc"]',
        'input[aria-label*="Search Google Maps"]',
        'input[placeholder*="Search Google Maps"]',
        'input[aria-label*="Search"]',
        "input",
    ]
    for selector in selectors:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        for element in elements:
            try:
                if element.is_displayed():
                    return element
            except StaleElementReferenceException:
                continue
    return None


def current_search_value(driver: webdriver.Firefox) -> str:
    search_input = find_search_input(driver)
    if search_input is None:
        return ""
    return normalize_text(search_input.get_attribute("value") or "")


def ensure_maps_shell(driver: webdriver.Firefox, wait: WebDriverWait) -> None:
    if "google.com/maps" not in driver.current_url:
        driver.get("https://www.google.com/maps")
    wait.until(lambda d: find_search_input(d) is not None)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    install_review_network_capture(driver)
    time.sleep(2)


def set_search_query(driver: webdriver.Firefox, search_input, query: str) -> None:
    driver.execute_script("arguments[0].focus();", search_input)
    try:
        search_input.click()
    except Exception:
        driver.execute_script("arguments[0].click();", search_input)
    time.sleep(0.2)
    search_input.send_keys(Keys.CONTROL, "a")
    time.sleep(0.1)
    search_input.send_keys(Keys.BACKSPACE)
    time.sleep(0.2)
    driver.execute_script(
        (
            "arguments[0].value = '';"
            "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));"
            "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));"
        ),
        search_input,
    )
    time.sleep(0.1)
    search_input.send_keys(query)
    time.sleep(0.4)


def search_google_maps(driver: webdriver.Firefox, wait: WebDriverWait, query: str) -> None:
    ensure_maps_shell(driver, wait)
    previous_url = driver.current_url
    previous_title = driver.title
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            search_input = wait.until(lambda d: find_search_input(d))
            set_search_query(driver, search_input, query)
            search_input.send_keys(Keys.ENTER)
            wait.until(
                lambda d: d.current_url != previous_url
                or d.title != previous_title
            )
            wait.until(
                lambda d: google_page_kind(d.current_url) in {"place", "search"}
                or current_search_value(d) == normalize_text(query)
            )
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="main"]')))
            time.sleep(3)
            return
        except Exception as exc:
            last_error = exc
            if attempt == 2:
                break
            driver.get("https://www.google.com/maps")
            wait.until(lambda d: find_search_input(d) is not None)
            time.sleep(2)
    if last_error is not None:
        raise last_error


def search_result_match_score(row: dict[str, str], label: str) -> float:
    practice_name = row.get("practice_name", "")
    score = title_similarity(practice_name, label)
    normalized_practice = normalize_name(practice_name)
    normalized_label = normalize_name(label)
    if normalized_practice and normalized_practice in normalized_label:
        score += 0.35
    score += contextual_text_bonus(
        label,
        str(row.get("postcode", "")),
        str(row.get("street_address", "")),
    )
    return score


def collect_search_result_candidates(driver: webdriver.Firefox, row: dict[str, str]) -> list[dict[str, object]]:
    candidates: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()
    for element in driver.find_elements(By.CSS_SELECTOR, 'a[href*="/place/"], a.hfpxzc'):
        try:
            href = element.get_attribute("href") or ""
            label = normalize_text(element.text or element.get_attribute("aria-label") or element.get_attribute("title") or "")
        except StaleElementReferenceException:
            continue
        if "/place/" not in href:
            continue
        key = (href, label)
        if key in seen:
            continue
        seen.add(key)
        candidates.append(
            {
                "element": element,
                "href": href,
                "label": label,
                "sponsored": element_or_ancestor_mentions_sponsored(driver, element),
                "blocked_title": is_blocked_place_title(label),
                "match_score": search_result_match_score(row, label),
            }
        )
    return candidates


def click_best_search_result(
    driver: webdriver.Firefox,
    wait: WebDriverWait,
    row: dict[str, str],
    minimum_score: float = 0.25,
) -> tuple[bool, list[dict[str, object]], dict[str, object] | None]:
    candidates = collect_search_result_candidates(driver, row)
    eligible = [
        candidate
        for candidate in candidates
        if not candidate["sponsored"] and not candidate["blocked_title"]
    ]
    chosen = None
    if eligible:
        chosen = max(
            eligible,
            key=lambda candidate: (
                float(candidate["match_score"]),
                len(normalize_name(str(candidate["label"]))),
            ),
        )
        if float(chosen["match_score"]) < minimum_score:
            chosen = None
    if chosen is None:
        return False, candidates, None

    element = chosen["element"]
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    time.sleep(0.5)
    try:
        element.click()
    except Exception:
        driver.execute_script("arguments[0].click();", element)
    try:
        wait.until(lambda d: "/place/" in d.current_url)
    except TimeoutException:
        return False, candidates, chosen
    time.sleep(2)
    return True, candidates, chosen


def google_page_kind(current_url: str) -> str:
    if "/place/" in current_url:
        return "place"
    if "/search/" in current_url:
        return "search"
    return "other"


def find_reviews_entrypoint_button(driver: webdriver.Firefox):
    for button in driver.find_elements(By.CSS_SELECTOR, "button"):
        try:
            label = normalize_text(button.get_attribute("aria-label") or "")
            text = normalize_text(button.text)
        except StaleElementReferenceException:
            continue
        if "More reviews" in label or text.startswith("More reviews"):
            return button
    for button in driver.find_elements(By.CSS_SELECTOR, "button"):
        try:
            label = normalize_text(button.get_attribute("aria-label") or "")
        except StaleElementReferenceException:
            continue
        if label.startswith("Reviews for "):
            return button
    return None


def has_visible_review_cards(driver: webdriver.Firefox) -> bool:
    try:
        cards = driver.find_elements(By.CSS_SELECTOR, "div.jftiEf")
    except Exception:
        return False
    for card in cards:
        try:
            if card.is_displayed():
                return True
        except StaleElementReferenceException:
            continue
    return False


def reviews_entrypoint_present(driver: webdriver.Firefox) -> bool:
    return find_reviews_entrypoint_button(driver) is not None or has_visible_review_cards(driver)


def open_reviews_panel(driver: webdriver.Firefox, wait: WebDriverWait) -> bool:
    button = find_reviews_entrypoint_button(driver)
    if button is not None:
        try:
            button.click()
            time.sleep(2)
            return True
        except StaleElementReferenceException:
            pass
    if has_visible_review_cards(driver):
        return True
    try:
        WebDriverWait(driver, 2, poll_frequency=0.2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.jftiEf")))
        return True
    except TimeoutException:
        return False


def sort_reviews_newest(driver: webdriver.Firefox) -> bool:
    for button in driver.find_elements(By.CSS_SELECTOR, "button"):
        try:
            label = normalize_text(button.get_attribute("aria-label") or "")
            text = normalize_text(button.text)
        except StaleElementReferenceException:
            continue
        if "Sort reviews" in label or text == "Sort":
            try:
                button.click()
                time.sleep(1)
                break
            except StaleElementReferenceException:
                continue
    else:
        return False

    for item in driver.find_elements(By.CSS_SELECTOR, '[role="menuitemradio"], [role="menuitem"]'):
        try:
            text = normalize_text(item.text)
        except StaleElementReferenceException:
            continue
        if text.lower().startswith("newest"):
            try:
                item.click()
                time.sleep(2)
                return True
            except StaleElementReferenceException:
                continue
    return False


def review_button_label(button) -> str:
    return normalize_text(
        button.text
        or button.get_attribute("aria-label")
        or button.get_attribute("title")
        or ""
    ).lower()


def should_expand_review_button(label: str) -> bool:
    if not label:
        return False
    if label in {"more", "full review"}:
        return True
    return label.startswith("more ") and "review" in label


def install_review_network_capture(driver: webdriver.Firefox) -> bool:
    try:
        driver.execute_script(RAW_REVIEW_CAPTURE_SCRIPT)
        return True
    except Exception:
        return False


def clear_review_network_capture(driver: webdriver.Firefox) -> None:
    try:
        driver.execute_script(
            "if (window.__gmReviewCapture && window.__gmReviewCapture.clear) { window.__gmReviewCapture.clear(); }"
        )
    except Exception:
        return


def pull_review_network_capture(driver: webdriver.Firefox) -> list[dict[str, object]]:
    try:
        payload = driver.execute_script(
            "if (window.__gmReviewCapture && window.__gmReviewCapture.snapshot) { return window.__gmReviewCapture.snapshot(); } return [];"
        )
    except Exception:
        return []
    if not isinstance(payload, list):
        return []
    entries: list[dict[str, object]] = []
    seen_entries: set[str] = set()
    for item in payload:
        if not isinstance(item, dict):
            continue
        url = normalize_text(str(item.get("url", "")))
        if "/maps/rpc/listugcposts" not in url:
            continue
        entry = {
            "seq": int(item.get("seq", 0) or 0),
            "captured_at_ms": int(item.get("captured_at_ms", 0) or 0),
            "source": normalize_text(str(item.get("source", ""))),
            "method": normalize_text(str(item.get("method", ""))),
            "url": url,
            "status": int(item.get("status", 0) or 0),
            "ok": bool(item.get("ok", False)),
            "content_type": normalize_text(str(item.get("content_type", ""))),
            "request_body": str(item.get("request_body", "") or ""),
            "body": str(item.get("body", "") or ""),
            "error": normalize_text(str(item.get("error", ""))),
        }
        serialized = json.dumps(entry, sort_keys=True, ensure_ascii=False)
        if serialized in seen_entries:
            continue
        seen_entries.add(serialized)
        entries.append(entry)
    return entries


def click_review_expanders(driver: webdriver.Firefox, cards: list, click_limit: int = 0) -> int:
    clicks = 0
    for card in cards:
        try:
            buttons = card.find_elements(By.CSS_SELECTOR, "button")
        except StaleElementReferenceException:
            continue
        for button in buttons:
            label = review_button_label(button)
            if not should_expand_review_button(label):
                continue
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                time.sleep(0.03)
                driver.execute_script("arguments[0].click();", button)
                clicks += 1
                time.sleep(0.08)
            except Exception:
                continue
            if click_limit and clicks >= click_limit:
                return clicks
    return clicks


def extract_text_candidates(card) -> list[str]:
    texts: list[str] = []
    seen: set[str] = set()
    for css in [".wiI7pd", ".MyEned"]:
        try:
            elements = card.find_elements(By.CSS_SELECTOR, css)
        except StaleElementReferenceException:
            continue
        for element in elements:
            try:
                text = normalize_text(element.get_attribute("textContent") or "")
            except StaleElementReferenceException:
                continue
            if not text or text in seen:
                continue
            seen.add(text)
            texts.append(text)
    return texts


OWNER_REPLY_DATE_PATTERN = re.compile(
    r"(?:Edited\s+)?(?:today|yesterday|(?:a|an|\d+)\s+(?:minute|hour|day|week|month|year)s?\s+ago)",
    flags=re.I,
)

RELATIVE_YEARS_PATTERN = re.compile(r"(\d+|a|an)\s+year", flags=re.I)
RELATIVE_MONTHS_PATTERN = re.compile(r"(\d+|a|an)\s+month", flags=re.I)
RELATIVE_WEEKS_PATTERN = re.compile(r"(\d+|a|an)\s+week", flags=re.I)


def extract_owner_reply_header(card) -> str:
    candidates: list[str] = []
    try:
        elements = card.find_elements(
            By.XPATH,
            ".//*[contains(normalize-space(.), 'Response from the owner')]",
        )
    except StaleElementReferenceException:
        return ""
    for element in elements:
        try:
            text = normalize_text(element.get_attribute("textContent") or element.text or "")
        except StaleElementReferenceException:
            continue
        if "Response from the owner" not in text:
            continue
        candidates.append(text)
    if not candidates:
        return ""
    return min(candidates, key=len)


def parse_owner_reply_from_raw(raw_card_text: str) -> dict[str, str] | None:
    raw = normalize_text(raw_card_text)
    if "Response from the owner" not in raw:
        return None
    marker = raw.split("Response from the owner", 1)[1].strip()
    date_match = OWNER_REPLY_DATE_PATTERN.match(marker)
    if not date_match:
        return {
            "relative_date": "",
            "text": marker,
            "raw_text": marker,
        } if marker else None
    relative_date = normalize_text(date_match.group(0))
    reply_text = normalize_text(marker[date_match.end():])
    if not relative_date and not reply_text:
        return None
    return {
        "relative_date": relative_date,
        "text": reply_text,
        "raw_text": marker,
    }


def extract_owner_reply(card, raw_card_text: str, text_candidates: list[str]) -> dict[str, str] | None:
    header_text = extract_owner_reply_header(card)
    relative_date = ""
    if header_text:
        match = OWNER_REPLY_DATE_PATTERN.search(header_text)
        if match:
            relative_date = normalize_text(match.group(0))
    reply_text = ""
    if header_text and len(text_candidates) >= 2:
        reply_text = text_candidates[-1]
    raw_reply = parse_owner_reply_from_raw(raw_card_text)
    if raw_reply:
        if not relative_date:
            relative_date = raw_reply.get("relative_date", "")
        if not reply_text:
            reply_text = raw_reply.get("text", "")
    reply_text = normalize_text(reply_text)
    if not relative_date and not reply_text and not raw_reply:
        return None
    return {
        "relative_date": relative_date,
        "text": reply_text,
        "raw_text": normalize_text((raw_reply or {}).get("raw_text", "")),
    }


def relative_date_age_years(relative_date: str) -> float | None:
    value = normalize_text(relative_date).lower()
    if not value:
        return None

    def parse_amount(match: re.Match[str] | None) -> float | None:
        if not match:
            return None
        token = match.group(1).lower()
        if token in {"a", "an"}:
            return 1.0
        try:
            return float(token)
        except ValueError:
            return None

    years = parse_amount(RELATIVE_YEARS_PATTERN.search(value))
    if years is not None:
        return years
    months = parse_amount(RELATIVE_MONTHS_PATTERN.search(value))
    if months is not None:
        return months / 12.0
    weeks = parse_amount(RELATIVE_WEEKS_PATTERN.search(value))
    if weeks is not None:
        return weeks / 52.0
    if "today" in value or "yesterday" in value:
        return 0.0
    if "day" in value:
        return 0.0
    return None


def extract_review_from_card(card) -> dict[str, object] | None:
    try:
        author = normalize_text(card.find_element(By.CSS_SELECTOR, ".d4r55").get_attribute("textContent") or "")
    except (NoSuchElementException, StaleElementReferenceException):
        author = ""
    try:
        relative_date = normalize_text(card.find_element(By.CSS_SELECTOR, ".rsqaWe").get_attribute("textContent") or "")
    except (NoSuchElementException, StaleElementReferenceException):
        relative_date = ""
    try:
        star_label = normalize_text(card.find_element(By.CSS_SELECTOR, ".kvMYJc").get_attribute("aria-label") or "")
    except (NoSuchElementException, StaleElementReferenceException):
        star_label = ""
    try:
        raw_card_text = normalize_text(card.get_attribute("textContent") or "")
    except StaleElementReferenceException:
        raw_card_text = ""
    text_candidates = extract_text_candidates(card)
    owner_reply = extract_owner_reply(card, raw_card_text, text_candidates)
    review_text = text_candidates[0] if text_candidates else ""
    if owner_reply and review_text and review_text == owner_reply.get("text", "") and len(text_candidates) >= 2:
        review_text = next(
            (candidate for candidate in text_candidates if candidate != owner_reply.get("text", "")),
            review_text,
        )
    if not any([author, relative_date, star_label, review_text, raw_card_text]):
        return None
    review: dict[str, object] = {
        "author": author,
        "relative_date": relative_date,
        "star_label": star_label,
        "text": review_text,
        "raw_card_text": raw_card_text,
    }
    if owner_reply:
        review["owner_reply"] = owner_reply
    return review


def review_key(review: dict[str, object]) -> str:
    fields = [
        normalize_text(review.get("author", "")),
        normalize_text(review.get("relative_date", "")),
        normalize_text(review.get("star_label", "")),
        normalize_text(review.get("text", "")),
        normalize_text(review.get("raw_card_text", "")),
    ]
    return " | ".join(fields)


def extract_recent_reviews(driver: webdriver.Firefox, limit: int) -> list[dict[str, object]]:
    reviews: list[dict[str, object]] = []
    cards = driver.find_elements(By.CSS_SELECTOR, "div.jftiEf")
    selected_cards = cards if limit <= 0 else cards[:limit]
    click_review_expanders(driver, selected_cards)
    for card in selected_cards:
        review = extract_review_from_card(card)
        if review:
            reviews.append(review)
    return reviews


def find_reviews_feed(driver: webdriver.Firefox):
    selectors = [
        'div[role="feed"]',
        'div.m6QErb.DxyBCb.kA9KIf.dS8AEf[tabindex="-1"]',
        'div.m6QErb.DxyBCb.kA9KIf.dS8AEf',
        'div.m6QErb[tabindex="-1"]',
        'div.m6QErb',
        'div.m6QErb[aria-label*="review"]',
        'div.m6QErb[aria-label*="Review"]',
    ]
    for selector in selectors:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        for element in elements:
            try:
                if element.find_elements(By.CSS_SELECTOR, "div.jftiEf"):
                    return element
            except StaleElementReferenceException:
                continue
    cards = driver.find_elements(By.CSS_SELECTOR, "div.jftiEf")
    if cards:
        try:
            return cards[0].find_element(By.XPATH, "./ancestor::div[contains(@class, 'm6QErb')][1]")
        except NoSuchElementException:
            return None
    return None


def scroll_reviews_feed(driver: webdriver.Firefox, feed, cards: list | None = None, force_to_bottom: bool = False) -> tuple[float, float, float]:
    try:
        before_top, before_height, before_client = driver.execute_script(
            "const el = arguments[0]; return [el.scrollTop, el.scrollHeight, el.clientHeight];",
            feed,
        )
    except StaleElementReferenceException:
        feed = find_reviews_feed(driver)
        if feed is None:
            return (0.0, 0.0, 0.0)
        before_top, before_height, before_client = driver.execute_script(
            "const el = arguments[0]; return [el.scrollTop, el.scrollHeight, el.clientHeight];",
            feed,
        )
    before_count = len(cards) if cards is not None else len(driver.find_elements(By.CSS_SELECTOR, "div.jftiEf"))
    if cards:
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'end'});", cards[-1])
            time.sleep(0.08)
        except Exception:
            pass
    driver.execute_script(
        (
            "const el = arguments[0];"
            "el.scrollTop = el.scrollHeight;"
            if force_to_bottom
            else
            "const el = arguments[0];"
            "el.scrollTop = Math.min(el.scrollHeight, el.scrollTop + Math.max(el.clientHeight * 1.2, 800));"
        ),
        feed,
    )
    wait_timeout = 1.1 if force_to_bottom else 0.8
    try:
        WebDriverWait(driver, wait_timeout, poll_frequency=0.12).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, "div.jftiEf")) > before_count
            or d.execute_script("return arguments[0].scrollHeight;", find_reviews_feed(d) or feed) > before_height
        )
    except TimeoutException:
        time.sleep(0.15 if force_to_bottom else 0.08)
    current_feed = find_reviews_feed(driver) or feed
    try:
        after_top, after_height, after_client = driver.execute_script(
            "const el = arguments[0]; return [el.scrollTop, el.scrollHeight, el.clientHeight];",
            current_feed,
        )
    except StaleElementReferenceException:
        return (0.0, 0.0, 0.0)
    return (
        float(after_top) - float(before_top),
        float(after_height) - float(before_height),
        float(after_client),
    )


def extract_full_reviews(
    driver: webdriver.Firefox,
    limit: int,
    expected_total: int | None,
) -> tuple[list[dict[str, object]], str, bool]:
    feed = find_reviews_feed(driver)
    if feed is None:
        return extract_recent_reviews(driver, limit), "no_feed_found", False

    try:
        driver.execute_script("arguments[0].scrollTop = 0;", feed)
        time.sleep(0.5)
    except Exception:
        pass

    reviews: list[dict[str, object]] = []
    seen_keys: set[str] = set()
    stagnant_rounds = 0
    end_of_feed_rounds = 0
    max_rounds = 90
    large_feed_soft_cap_applied = bool(expected_total and expected_total > 500 and limit <= 0)
    soft_stop_reason = ""

    for _ in range(max_rounds):
        cards = driver.find_elements(By.CSS_SELECTOR, "div.jftiEf")
        cards_to_expand = cards if len(cards) <= 24 else cards[-24:]
        click_review_expanders(driver, cards_to_expand)
        new_reviews = 0
        for card in cards:
            review = extract_review_from_card(card)
            if not review:
                continue
            key = review_key(review)
            if key in seen_keys:
                continue
            seen_keys.add(key)
            reviews.append(review)
            new_reviews += 1
            if limit > 0 and len(reviews) >= limit:
                return reviews[:limit], "explicit_limit", large_feed_soft_cap_applied
        if expected_total and len(reviews) >= expected_total:
            return reviews[:expected_total], "expected_total_reached", large_feed_soft_cap_applied
        if large_feed_soft_cap_applied and len(reviews) >= 400:
            return reviews[:400], "soft_cap_400_reviews", True
        if large_feed_soft_cap_applied:
            ages = [
                age
                for review in reviews
                if isinstance(review, dict)
                for age in [relative_date_age_years(str(review.get("relative_date", "")))]
                if age is not None
            ]
            oldest_age_years = max(ages) if ages else None
            if oldest_age_years is not None and oldest_age_years >= 5.0:
                soft_stop_reason = "soft_cap_5_years"
                break

        scroll_delta, height_delta, _ = scroll_reviews_feed(
            driver,
            feed,
            cards=cards,
            force_to_bottom=stagnant_rounds >= 1,
        )
        if new_reviews == 0:
            stagnant_rounds += 1
        else:
            stagnant_rounds = 0
        if scroll_delta <= 1 and height_delta <= 1:
            end_of_feed_rounds += 1
        else:
            end_of_feed_rounds = 0
        if stagnant_rounds >= 3 and end_of_feed_rounds >= 2:
            break

    return reviews, (soft_stop_reason or "feed_exhausted"), large_feed_soft_cap_applied


def scrape_place(
    driver: webdriver.Firefox,
    query: str,
    recent_limit: int,
    expected_practice_name: str = "",
    expected_postcode: str = "",
    expected_street_address: str = "",
    expected_coordinates: tuple[float, float] | None = None,
    full_reviews_requested: bool = False,
    full_review_limit: int = 0,
    skip_over_review_count: int = 0,
    capture_review_network: bool = True,
) -> dict[str, object]:
    wait = build_wait(driver, 25)
    row_context = {
        "practice_name": expected_practice_name or query,
        "postcode": expected_postcode,
        "street_address": expected_street_address,
    }
    search_google_maps(driver, wait, query)

    place_title, rating, review_count = extract_overall_metrics(driver)
    place_address_text = extract_place_address_text(driver)
    clicked_first_result = False
    search_result_candidates: list[dict[str, object]] = []
    chosen_search_result: dict[str, object] | None = None
    if google_page_kind(driver.current_url) == "search":
        clicked_first_result, search_result_candidates, chosen_search_result = click_best_search_result(
            driver,
            wait,
            row_context,
        )
        place_title, rating, review_count = extract_overall_metrics(driver)
        place_address_text = extract_place_address_text(driver)
    blocked_place_match = is_blocked_place_title(place_title)
    sponsored_place_match = page_has_sponsored_marker(driver)
    review_entrypoint_found = reviews_entrypoint_present(driver)
    if blocked_place_match and google_page_kind(driver.current_url) == "search":
        clicked_again, search_result_candidates, chosen_search_result = click_best_search_result(
            driver,
            wait,
            row_context,
        )
        clicked_first_result = clicked_again or clicked_first_result
        place_title, rating, review_count = extract_overall_metrics(driver)
        place_address_text = extract_place_address_text(driver)
        blocked_place_match = is_blocked_place_title(place_title)
        sponsored_place_match = page_has_sponsored_marker(driver)
        review_entrypoint_found = reviews_entrypoint_present(driver)
    review_count_skip = bool(
        skip_over_review_count > 0
        and isinstance(review_count, int)
        and review_count > skip_over_review_count
        and not blocked_place_match
        and not sponsored_place_match
    )
    reviews_opened = open_reviews_panel(driver, wait) if review_entrypoint_found else False
    if not blocked_place_match and not sponsored_place_match and not review_count_skip and not reviews_opened and google_page_kind(driver.current_url) == "search":
        clicked_again, search_result_candidates, chosen_search_result = click_best_search_result(
            driver,
            wait,
            row_context,
        )
        clicked_first_result = clicked_again or clicked_first_result
        place_title, rating, review_count = extract_overall_metrics(driver)
        place_address_text = extract_place_address_text(driver)
        blocked_place_match = is_blocked_place_title(place_title)
        sponsored_place_match = page_has_sponsored_marker(driver)
        review_entrypoint_found = reviews_entrypoint_present(driver)
        reviews_opened = open_reviews_panel(driver, wait) if review_entrypoint_found else False
    chosen_search_result_label = str((chosen_search_result or {}).get("label", ""))
    chosen_search_result_score = float((chosen_search_result or {}).get("match_score", 0.0) or 0.0)
    wrong_place_match = (
        google_page_kind(driver.current_url) == "place"
        and not blocked_place_match
        and not sponsored_place_match
        and not review_entrypoint_found
        and not place_contextually_matches(
            expected_practice_name or query,
            place_title,
            place_address_text,
            expected_postcode,
            expected_street_address,
            expected_coordinates,
            chosen_search_result_label,
            current_url=driver.current_url,
        )
    ) or (
        google_page_kind(driver.current_url) == "place"
        and not blocked_place_match
        and not sponsored_place_match
        and not place_contextually_matches(
            expected_practice_name or query,
            place_title,
            place_address_text,
            expected_postcode,
            expected_street_address,
            expected_coordinates,
            chosen_search_result_label,
            current_url=driver.current_url,
        )
        and chosen_search_result_score < 0.25
    )
    sponsored_search_results_only = (
        google_page_kind(driver.current_url) == "search"
        and not clicked_first_result
        and bool(search_result_candidates)
        and all(bool(candidate.get("sponsored")) for candidate in search_result_candidates)
    )
    reviews_sorted = False
    recent_reviews: list[dict[str, object]] = []
    no_review_panel = google_page_kind(driver.current_url) == "place" and not blocked_place_match and not sponsored_place_match and not review_entrypoint_found
    review_collection_mode = (
        "blocked_place" if blocked_place_match else
        ("review_count_skip" if review_count_skip else (
            "sponsored_place" if sponsored_place_match else (
            "sponsored_search_results_only" if sponsored_search_results_only else (
                "wrong_place_match" if wrong_place_match else (
                    "no_review_panel" if no_review_panel else "visible_cards"
                )
            )
        )))
    )
    full_reviews_attempted = False
    full_review_stop_reason = ""
    full_review_soft_cap_applied = False
    raw_review_capture_enabled = False
    raw_review_responses: list[dict[str, object]] = []
    if capture_review_network and not blocked_place_match and not sponsored_place_match and not no_review_panel and not wrong_place_match and not review_count_skip:
        raw_review_capture_enabled = install_review_network_capture(driver)
        if raw_review_capture_enabled:
            clear_review_network_capture(driver)
    if reviews_opened and not blocked_place_match and not sponsored_place_match and not no_review_panel and not wrong_place_match and not review_count_skip:
        reviews_sorted = sort_reviews_newest(driver)
        time.sleep(1.5)
        if full_reviews_requested:
            full_reviews_attempted = True
            recent_reviews, full_review_stop_reason, full_review_soft_cap_applied = extract_full_reviews(
                driver,
                full_review_limit,
                review_count,
            )
            if recent_reviews:
                review_collection_mode = "full_feed"
        if not recent_reviews:
            recent_reviews = extract_recent_reviews(driver, recent_limit)
    if raw_review_capture_enabled:
        raw_review_responses = pull_review_network_capture(driver)

    current_url = driver.current_url
    page_kind = google_page_kind(current_url)

    manual_review_required = page_kind != "place" or blocked_place_match or sponsored_place_match or sponsored_search_results_only or wrong_place_match
    if blocked_place_match:
        scan_status = "blocked_place_match"
    elif review_count_skip:
        scan_status = "skipped_review_count_threshold"
    elif sponsored_place_match:
        scan_status = "sponsored_place_match"
    elif sponsored_search_results_only:
        scan_status = "sponsored_search_results_only"
    elif wrong_place_match:
        scan_status = "wrong_place_match"
    elif no_review_panel:
        scan_status = "ok_no_review_panel"
    elif manual_review_required:
        scan_status = "manual_review_search_result_only"
    elif rating is None:
        scan_status = "no_rating_found"
    elif reviews_opened and recent_reviews:
        scan_status = "ok_with_visible_reviews"
    elif reviews_opened:
        scan_status = "ok_reviews_opened_no_visible_text"
    else:
        scan_status = "ok_rating_only"

    parsed_coords = parse_google_maps_coordinates(current_url)

    owner_replies_collected = sum(
        1
        for review in recent_reviews
        if isinstance(review, dict) and review.get("owner_reply")
    )

    return {
        "query": query,
        "google_maps_title": place_title,
        "google_maps_url": current_url,
        "google_maps_address_text": place_address_text,
        "latitude": parsed_coords[0] if parsed_coords else None,
        "longitude": parsed_coords[1] if parsed_coords else None,
        "google_rating": rating,
        "google_review_count": review_count,
        "blocked_place_match": blocked_place_match,
        "review_count_skip": review_count_skip,
        "skip_over_review_count": skip_over_review_count,
        "sponsored_place_match": sponsored_place_match,
        "sponsored_search_results_only": sponsored_search_results_only,
        "wrong_place_match": wrong_place_match,
        "reviews_entrypoint_found": review_entrypoint_found,
        "clicked_first_search_result": clicked_first_result,
        "search_results_inspected": [
            {
                "label": str(candidate.get("label", "")),
                "href": str(candidate.get("href", "")),
                "sponsored": bool(candidate.get("sponsored")),
                "blocked_title": bool(candidate.get("blocked_title")),
                "match_score": round(float(candidate.get("match_score", 0.0) or 0.0), 3),
            }
            for candidate in search_result_candidates[:8]
        ],
        "chosen_search_result_label": chosen_search_result_label,
        "chosen_search_result_score": round(chosen_search_result_score, 3),
        "page_kind": page_kind,
        "scan_status": scan_status,
        "manual_review_required": manual_review_required,
        "retry_recommended": False,
        "reviews_opened": reviews_opened,
        "reviews_sorted_newest": reviews_sorted,
        "review_collection_mode": review_collection_mode,
        "full_reviews_requested": full_reviews_requested,
        "full_reviews_attempted": full_reviews_attempted,
        "full_review_stop_reason": full_review_stop_reason,
        "full_review_soft_cap_applied": full_review_soft_cap_applied,
        "review_cards_collected": len(recent_reviews),
        "visible_review_cards_collected": len(recent_reviews),
        "owner_replies_collected": owner_replies_collected,
        "raw_review_capture_enabled": raw_review_capture_enabled,
        "raw_review_responses_captured": len(raw_review_responses),
        "raw_review_responses": raw_review_responses,
        "recent_reviews": recent_reviews,
    }


def load_rows(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open() as handle:
        return list(csv.DictReader(handle))


def load_existing_results(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return payload if isinstance(payload, list) else []


TERMINAL_REVIEW_COLLECTION_MODES = {
    "full_feed",
    "no_review_panel",
    "blocked_place",
    "sponsored_place",
    "sponsored_search_results_only",
    "shared_place_alias",
    "review_count_skip",
    "wrong_place_match",
}


def find_shared_place_alias(
    collected: list[dict[str, object]],
    canonical_code: str,
    google_maps_url: str,
) -> dict[str, object] | None:
    target_url = normalize_text(google_maps_url)
    if not target_url:
        return None
    for item in collected:
        other_code = str(item.get("canonical_code", "")).strip()
        other_mode = str(item.get("review_collection_mode", "")).strip()
        other_url = normalize_text(str(item.get("google_maps_url", "")))
        if not other_code or other_code == canonical_code:
            continue
        if other_mode not in TERMINAL_REVIEW_COLLECTION_MODES:
            continue
        if other_url and other_url == target_url:
            return item
    return None


def load_query_overrides(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def resolve_query(row: dict[str, str], query_overrides: dict[str, str]) -> str:
    prebuilt_query = str(row.get("google_maps_query", "")).strip()
    if prebuilt_query:
        return prebuilt_query
    keys = [
        row.get("canonical_code", "").strip(),
        row.get("practice_name", "").strip(),
    ]
    for key in keys:
        if key and key in query_overrides:
            return str(query_overrides[key]).strip()
    return f"{query_friendly_name(row['practice_name'])} {row['postcode']}".strip()


def build_review_text_path(text_dir: Path, canonical_code: str, practice_name: str) -> Path:
    stem = canonical_code.strip() or slugify(practice_name) or "unknown-practice"
    suffix = slugify(practice_name) or "practice"
    return text_dir / f"{stem}-{suffix}.txt"


def build_raw_review_path(raw_dir: Path, canonical_code: str, practice_name: str) -> Path:
    stem = canonical_code.strip() or slugify(practice_name) or "unknown-practice"
    suffix = slugify(practice_name) or "practice"
    return raw_dir / f"{stem}-{suffix}.json"


def write_raw_review_capture_file(raw_dir: Path, result: dict[str, object]) -> str:
    raw_entries = result.get("raw_review_responses") or []
    if not raw_entries:
        return ""
    raw_dir.mkdir(parents=True, exist_ok=True)
    output_path = build_raw_review_path(
        raw_dir,
        str(result.get("canonical_code", "")),
        str(result.get("practice_name", "")),
    )
    payload = {
        "practice_name": result.get("practice_name", ""),
        "canonical_code": result.get("canonical_code", ""),
        "postcode": result.get("postcode", ""),
        "query_used": result.get("query_used", result.get("query", "")),
        "google_maps_title": result.get("google_maps_title", ""),
        "google_maps_url": result.get("google_maps_url", ""),
        "latitude": result.get("latitude", None),
        "longitude": result.get("longitude", None),
        "google_review_count": result.get("google_review_count", ""),
        "review_collection_mode": result.get("review_collection_mode", ""),
        "raw_review_responses_captured": result.get("raw_review_responses_captured", len(raw_entries)),
        "raw_review_responses": raw_entries,
    }
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(output_path)


def write_review_text_file(text_dir: Path, result: dict[str, object]) -> str:
    reviews = result.get("recent_reviews") or []
    review_blocks: list[str] = []
    for review in reviews:
        if not isinstance(review, dict):
            continue
        parts = []
        if review.get("author"):
            parts.append(f"Author: {review['author']}")
        if review.get("relative_date"):
            parts.append(f"Date: {review['relative_date']}")
        if review.get("star_label"):
            parts.append(f"Rating: {review['star_label']}")
        review_blocks.append("\n".join(parts))
        text = normalize_text(str(review.get("text", "")))
        raw = normalize_text(str(review.get("raw_card_text", "")))
        if text:
            review_blocks.append(text)
        elif raw:
            review_blocks.append(raw)
        owner_reply = review.get("owner_reply")
        if isinstance(owner_reply, dict):
            reply_parts = []
            if owner_reply.get("relative_date"):
                reply_parts.append(f"Practice response date: {owner_reply['relative_date']}")
            if reply_parts:
                review_blocks.append("\n".join(reply_parts))
            reply_text = normalize_text(str(owner_reply.get("text", "")))
            reply_raw = normalize_text(str(owner_reply.get("raw_text", "")))
            if reply_text:
                review_blocks.append("Practice response:")
                review_blocks.append(reply_text)
            elif reply_raw:
                review_blocks.append("Practice response:")
                review_blocks.append(reply_raw)
        review_blocks.append("")

    if not review_blocks:
        return ""

    text_dir.mkdir(parents=True, exist_ok=True)
    output_path = build_review_text_path(
        text_dir,
        str(result.get("canonical_code", "")),
        str(result.get("practice_name", "")),
    )
    header_lines = [
        f"Practice: {result.get('practice_name', '')}",
        f"Canonical code: {result.get('canonical_code', '')}",
        f"Postcode: {result.get('postcode', '')}",
        f"Google Maps title: {result.get('google_maps_title', '')}",
        f"Google rating: {result.get('google_rating', '')}",
        f"Google review count: {result.get('google_review_count', '')}",
        f"Google Maps URL: {result.get('google_maps_url', '')}",
        f"Title match score: {result.get('title_match_score', '')}",
        f"Review collection mode: {result.get('review_collection_mode', '')}",
        f"Review cards collected: {result.get('review_cards_collected', '')}",
        f"Owner replies collected: {result.get('owner_replies_collected', '')}",
        f"Raw review responses captured: {result.get('raw_review_responses_captured', '')}",
        f"Raw review capture file: {result.get('raw_review_capture_file', '')}",
        "",
        "Captured reviews",
        "================",
        "",
    ]
    output_path.write_text("\n".join(header_lines + review_blocks).strip() + "\n", encoding="utf-8")
    return str(output_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect Google Maps ratings plus either visible snippets or a scrolled review feed for GP practices.")
    parser.add_argument("--input", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--limit", type=int, default=10, help="Maximum number of practices to scrape after filtering and resume handling")
    parser.add_argument("--recent-reviews", type=int, default=10, help="Newest visible review cards to keep per practice; use 0 to keep all currently visible cards")
    parser.add_argument("--headless", action="store_true", help="Run Firefox headlessly (the normal/manual mode is visible Firefox)")
    parser.add_argument("--profile-copy", type=Path, default=PROFILE_COPY_DIR)
    parser.add_argument(
        "--canonical-code",
        action="append",
        default=[],
        help="Only scrape these canonical codes; may be passed multiple times or as comma-separated values",
    )
    parser.add_argument("--practice-filter", default="", help="Only scrape practices whose names contain this text")
    parser.add_argument("--pause-seconds", type=float, default=2.0, help="Pause between practices")
    parser.add_argument("--pause-jitter-seconds", type=float, default=1.0, help="Random extra pause added between practices")
    parser.add_argument("--resume", action="store_true", help="Skip rows already present in the output file")
    parser.add_argument("--only-missing-google", action="store_true", help="Only scrape practices missing a Google score in the input CSV")
    parser.add_argument("--reviews-text-dir", type=Path, default=DEFAULT_TEXT_DIR, help="Directory for one text file per practice with captured visible review text")
    parser.add_argument("--raw-review-dir", type=Path, default=DEFAULT_RAW_REVIEW_DIR, help="Directory for per-practice raw Google Maps review-response dumps captured from the page")
    parser.add_argument("--query-overrides", type=Path, default=DEFAULT_QUERY_OVERRIDES, help="JSON map of canonical_code or practice_name to an alternate Google Maps query")
    parser.add_argument(
        "--capture-review-network",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Capture raw Google Maps review fetch/XHR responses from the page and dump them per practice.",
    )
    parser.add_argument(
        "--full-reviews",
        choices=("none", "new", "gtd", "all"),
        default="new",
        help="Scroll the full Google Maps reviews feed for newly created records, GTD rows, or all rows instead of only keeping visible cards.",
    )
    parser.add_argument(
        "--full-review-limit",
        type=int,
        default=0,
        help="Maximum reviews to keep when full-review mode is active; 0 keeps scrolling until Google stops loading more cards.",
    )
    parser.add_argument(
        "--skip-over-review-count",
        type=int,
        default=0,
        help="If the matched Google listing reports more than this many reviews, record a terminal skip state instead of opening the review feed. 0 disables the skip.",
    )
    args = parser.parse_args()

    source_profile = discover_default_firefox_profile()
    profile_copy = refresh_profile_copy(source_profile, args.profile_copy)
    rows = load_rows(args.input)
    requested_codes = {
        part.strip()
        for value in args.canonical_code
        for part in str(value).split(",")
        if part.strip()
    }
    if requested_codes:
        rows = [row for row in rows if row.get("canonical_code", "").strip() in requested_codes]
    if args.only_missing_google:
        rows = [row for row in rows if not row.get("google_review_score")]
    if args.practice_filter:
        needle = args.practice_filter.lower()
        rows = [row for row in rows if needle in row["practice_name"].lower()]

    existing_results = load_existing_results(args.output)
    existing_result_indexes = {
        str(item.get("canonical_code", "")).strip(): index
        for index, item in enumerate(existing_results)
        if item.get("canonical_code")
    }
    existing_codes = {str(item.get("canonical_code", "")) for item in existing_results if item.get("canonical_code")}
    if args.resume:
        rows = [row for row in rows if row.get("canonical_code", "") not in existing_codes]
    rows = rows[: args.limit]
    query_overrides = load_query_overrides(args.query_overrides)

    driver = build_driver(profile_copy, headless=args.headless)
    collected: list[dict[str, object]] = list(existing_results)
    try:
        wait = build_wait(driver, 25)
        ensure_maps_shell(driver, wait)
        total = len(rows)
        for index, row in enumerate(rows, start=1):
            query = resolve_query(row, query_overrides)
            print(f"[{index}/{total}] {query}")
            existing_index = existing_result_indexes.get(row["canonical_code"], None)
            collect_full_reviews = (
                args.full_reviews == "all"
                or (args.full_reviews == "gtd" and is_gtd_managed_row(row))
                or (args.full_reviews == "new" and existing_index is None)
            )
            try:
                result = scrape_place(
                    driver,
                    query,
                    args.recent_reviews,
                    expected_practice_name=row["practice_name"],
                    expected_postcode=row.get("postcode", ""),
                    expected_street_address=row.get("street_address", ""),
                    expected_coordinates=expected_coordinates_for_row(row),
                    full_reviews_requested=collect_full_reviews,
                    full_review_limit=args.full_review_limit,
                    skip_over_review_count=args.skip_over_review_count,
                    capture_review_network=args.capture_review_network,
                )
            except Exception as exc:
                result = {
                    "query": query,
                    "google_maps_title": "",
                    "google_maps_url": driver.current_url,
                    "google_rating": None,
                    "google_review_count": None,
                    "clicked_first_search_result": False,
                    "page_kind": "error",
                    "scan_status": "error",
                    "manual_review_required": True,
                    "retry_recommended": True,
                    "reviews_opened": False,
                    "reviews_sorted_newest": False,
                    "review_collection_mode": "error",
                    "full_reviews_requested": collect_full_reviews,
                    "full_reviews_attempted": collect_full_reviews,
                    "review_cards_collected": 0,
                    "visible_review_cards_collected": 0,
                    "raw_review_capture_enabled": False,
                    "raw_review_responses_captured": 0,
                    "raw_review_responses": [],
                    "recent_reviews": [],
                    "scan_error": normalize_text(str(exc)),
                }
            result["practice_name"] = row["practice_name"]
            result["postcode"] = row["postcode"]
            result["canonical_code"] = row["canonical_code"]
            result["nhs_profile_url"] = row["nhs_profile_url"]
            result["query_used"] = query
            result["title_match_score"] = round(title_similarity(row["practice_name"], str(result.get("google_maps_title", ""))), 3)
            shared_alias = find_shared_place_alias(
                collected,
                row["canonical_code"],
                str(result.get("google_maps_url", "")),
            )
            if shared_alias is not None and str(result.get("review_collection_mode", "")).strip() not in TERMINAL_REVIEW_COLLECTION_MODES:
                result["review_collection_mode"] = "shared_place_alias"
                result["scan_status"] = "shared_place_alias"
                result["manual_review_required"] = False
                result["retry_recommended"] = False
                result["shared_place_with_canonical_code"] = shared_alias.get("canonical_code", "")
                result["shared_place_with_practice_name"] = shared_alias.get("practice_name", "")
                result["shared_place_with_review_mode"] = shared_alias.get("review_collection_mode", "")
            raw_review_payload = dict(result)
            result["raw_review_capture_file"] = write_raw_review_capture_file(args.raw_review_dir, raw_review_payload)
            result.pop("raw_review_responses", None)
            result["review_text_file"] = write_review_text_file(args.reviews_text_dir, result)
            if existing_index is None:
                collected.append(result)
                existing_result_indexes[row["canonical_code"]] = len(collected) - 1
            else:
                collected[existing_index] = result
            args.output.write_text(json.dumps(collected, indent=2), encoding="utf-8")
            pause_for = args.pause_seconds + random.uniform(0.0, max(args.pause_jitter_seconds, 0.0))
            time.sleep(pause_for)
    finally:
        driver.quit()

    print(f"Wrote {len(collected)} Google Maps review records to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
