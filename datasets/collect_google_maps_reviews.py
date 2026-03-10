#!/usr/bin/env python3
from __future__ import annotations

import argparse
import configparser
import csv
import json
import random
import re
import shutil
import time
from pathlib import Path
from urllib.parse import quote

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATASET = BASE_DIR / "gtd-greater-manchester-gp-practice-reviews-2026-03-09" / "gtd_greater_manchester_gp_practices.csv"
PROFILE_ROOT = Path.home() / ".mozilla" / "firefox"
PROFILE_COPY_DIR = BASE_DIR / ".tooling" / "firefox-profile-copy"
DEFAULT_OUTPUT = BASE_DIR / "gtd-greater-manchester-gp-practice-reviews-2026-03-09" / "google_maps_recent_reviews.json"
DEFAULT_TEXT_DIR = BASE_DIR / "gtd-greater-manchester-gp-practice-reviews-2026-03-09" / "google-review-texts"
DEFAULT_QUERY_OVERRIDES = BASE_DIR / "google_maps_query_overrides.json"


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
    value = re.sub(r"[\ue000-\uf8ff]", "", value)
    return " ".join(value.split())


def normalize_name(value: str) -> str:
    value = (value or "").lower().replace("&", " and ")
    value = re.sub(r"[’']", "", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


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


def extract_overall_metrics(driver: webdriver.Firefox) -> tuple[str, float | None, int | None]:
    title = driver.title.removesuffix(" - Google Maps").strip()
    rating = None
    review_count = None
    spans = driver.find_elements(By.CSS_SELECTOR, 'div[role="main"] span')
    for span in spans:
        text = normalize_text(span.text)
        aria = normalize_text(span.get_attribute("aria-label") or "")
        if rating is None and re.fullmatch(r"[0-5]\.\d", text):
            rating = float(text)
        if review_count is None and "reviews" in aria.lower():
            parsed = parse_reviews_count(aria)
            if parsed is not None:
                review_count = parsed
        if rating is not None and review_count is not None:
            break
    return title, rating, review_count


def click_first_search_result(driver: webdriver.Firefox, wait: WebDriverWait) -> bool:
    candidates = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/place/"], a.hfpxzc')
    for candidate in candidates:
        href = candidate.get_attribute("href") or ""
        label = normalize_text(candidate.text or candidate.get_attribute("aria-label") or candidate.get_attribute("title") or "")
        if "/place/" not in href:
            continue
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", candidate)
        time.sleep(0.5)
        try:
            candidate.click()
        except Exception:
            driver.execute_script("arguments[0].click();", candidate)
        try:
            wait.until(lambda d: "/place/" in d.current_url)
        except TimeoutException:
            return False
        time.sleep(3)
        return True
    return False


def google_page_kind(current_url: str) -> str:
    if "/place/" in current_url:
        return "place"
    if "/search/" in current_url:
        return "search"
    return "other"


def open_reviews_panel(driver: webdriver.Firefox, wait: WebDriverWait) -> bool:
    for button in driver.find_elements(By.CSS_SELECTOR, "button"):
        try:
            label = normalize_text(button.get_attribute("aria-label") or "")
            text = normalize_text(button.text)
        except StaleElementReferenceException:
            continue
        if "More reviews" in label or text.startswith("More reviews"):
            try:
                button.click()
                time.sleep(2)
                return True
            except StaleElementReferenceException:
                continue
    for button in driver.find_elements(By.CSS_SELECTOR, "button"):
        try:
            label = normalize_text(button.get_attribute("aria-label") or "")
        except StaleElementReferenceException:
            continue
        if label.startswith("Reviews for "):
            try:
                button.click()
                time.sleep(2)
                return True
            except StaleElementReferenceException:
                continue
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.jftiEf")))
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
                time.sleep(0.05)
                driver.execute_script("arguments[0].click();", button)
                clicks += 1
                time.sleep(0.15)
            except Exception:
                continue
            if click_limit and clicks >= click_limit:
                return clicks
    return clicks


def extract_review_from_card(card) -> dict[str, str] | None:
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
    review_text = ""
    for css in [".wiI7pd", ".MyEned"]:
        try:
            review_text = normalize_text(card.find_element(By.CSS_SELECTOR, css).get_attribute("textContent") or "")
        except (NoSuchElementException, StaleElementReferenceException):
            continue
        if review_text:
            break
    try:
        raw_card_text = normalize_text(card.get_attribute("textContent") or "")
    except StaleElementReferenceException:
        raw_card_text = ""
    if not any([author, relative_date, star_label, review_text, raw_card_text]):
        return None
    return {
        "author": author,
        "relative_date": relative_date,
        "star_label": star_label,
        "text": review_text,
        "raw_card_text": raw_card_text,
    }


def review_key(review: dict[str, str]) -> str:
    fields = [
        normalize_text(review.get("author", "")),
        normalize_text(review.get("relative_date", "")),
        normalize_text(review.get("star_label", "")),
        normalize_text(review.get("text", "")),
        normalize_text(review.get("raw_card_text", "")),
    ]
    return " | ".join(fields)


def extract_recent_reviews(driver: webdriver.Firefox, limit: int) -> list[dict[str, str]]:
    reviews: list[dict[str, str]] = []
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
    before_top, before_height, before_client = driver.execute_script(
        "const el = arguments[0]; return [el.scrollTop, el.scrollHeight, el.clientHeight];",
        feed,
    )
    if cards:
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'end'});", cards[-1])
            time.sleep(0.2)
        except Exception:
            pass
    driver.execute_script(
        (
            "const el = arguments[0];"
            "el.scrollTop = el.scrollHeight;"
            if force_to_bottom
            else
            "const el = arguments[0];"
            "el.scrollTop = Math.min(el.scrollHeight, el.scrollTop + Math.max(el.clientHeight * 0.9, 500));"
        ),
        feed,
    )
    time.sleep(1.2 if force_to_bottom else 1.0)
    after_top, after_height, after_client = driver.execute_script(
        "const el = arguments[0]; return [el.scrollTop, el.scrollHeight, el.clientHeight];",
        feed,
    )
    return (
        float(after_top) - float(before_top),
        float(after_height) - float(before_height),
        float(after_client),
    )


def extract_full_reviews(driver: webdriver.Firefox, limit: int, expected_total: int | None) -> list[dict[str, str]]:
    feed = find_reviews_feed(driver)
    if feed is None:
        return extract_recent_reviews(driver, limit)

    try:
        driver.execute_script("arguments[0].scrollTop = 0;", feed)
        time.sleep(0.5)
    except Exception:
        pass

    reviews: list[dict[str, str]] = []
    seen_keys: set[str] = set()
    stagnant_rounds = 0
    end_of_feed_rounds = 0
    max_rounds = 120

    for _ in range(max_rounds):
        cards = driver.find_elements(By.CSS_SELECTOR, "div.jftiEf")
        click_review_expanders(driver, cards)
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
                return reviews[:limit]
        if expected_total and len(reviews) >= expected_total:
            return reviews[:expected_total]

        scroll_delta, height_delta, _ = scroll_reviews_feed(
            driver,
            feed,
            cards=cards,
            force_to_bottom=stagnant_rounds >= 2,
        )
        if new_reviews == 0:
            stagnant_rounds += 1
        else:
            stagnant_rounds = 0
        if scroll_delta <= 1 and height_delta <= 1:
            end_of_feed_rounds += 1
        else:
            end_of_feed_rounds = 0
        if stagnant_rounds >= 4 and end_of_feed_rounds >= 2:
            break

    return reviews


def scrape_place(
    driver: webdriver.Firefox,
    query: str,
    recent_limit: int,
    full_reviews_requested: bool = False,
    full_review_limit: int = 0,
) -> dict[str, object]:
    wait = WebDriverWait(driver, 25)
    driver.get("https://www.google.com/maps/search/" + quote(query))
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="main"]')))
    time.sleep(4)

    place_title, rating, review_count = extract_overall_metrics(driver)
    clicked_first_result = False
    if google_page_kind(driver.current_url) == "search":
        clicked_first_result = click_first_search_result(driver, wait)
        place_title, rating, review_count = extract_overall_metrics(driver)
    reviews_opened = open_reviews_panel(driver, wait)
    if not reviews_opened and google_page_kind(driver.current_url) == "search":
        clicked_first_result = click_first_search_result(driver, wait) or clicked_first_result
        place_title, rating, review_count = extract_overall_metrics(driver)
        reviews_opened = open_reviews_panel(driver, wait)
    reviews_sorted = False
    recent_reviews: list[dict[str, str]] = []
    review_collection_mode = "visible_cards"
    full_reviews_attempted = False
    if reviews_opened:
        reviews_sorted = sort_reviews_newest(driver)
        time.sleep(2)
        if full_reviews_requested:
            full_reviews_attempted = True
            recent_reviews = extract_full_reviews(driver, full_review_limit, review_count)
            if recent_reviews:
                review_collection_mode = "full_feed"
        if not recent_reviews:
            recent_reviews = extract_recent_reviews(driver, recent_limit)

    current_url = driver.current_url
    page_kind = google_page_kind(current_url)

    manual_review_required = page_kind != "place"
    if manual_review_required:
        scan_status = "manual_review_search_result_only"
    elif rating is None:
        scan_status = "no_rating_found"
    elif reviews_opened and recent_reviews:
        scan_status = "ok_with_visible_reviews"
    elif reviews_opened:
        scan_status = "ok_reviews_opened_no_visible_text"
    else:
        scan_status = "ok_rating_only"

    return {
        "query": query,
        "google_maps_title": place_title,
        "google_maps_url": current_url,
        "google_rating": rating,
        "google_review_count": review_count,
        "clicked_first_search_result": clicked_first_result,
        "page_kind": page_kind,
        "scan_status": scan_status,
        "manual_review_required": manual_review_required,
        "retry_recommended": False,
        "reviews_opened": reviews_opened,
        "reviews_sorted_newest": reviews_sorted,
        "review_collection_mode": review_collection_mode,
        "full_reviews_requested": full_reviews_requested,
        "full_reviews_attempted": full_reviews_attempted,
        "review_cards_collected": len(recent_reviews),
        "visible_review_cards_collected": len(recent_reviews),
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


def load_query_overrides(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def resolve_query(row: dict[str, str], query_overrides: dict[str, str]) -> str:
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
    parser.add_argument("--headless", action="store_true", help="Run Firefox headlessly")
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
    parser.add_argument("--query-overrides", type=Path, default=DEFAULT_QUERY_OVERRIDES, help="JSON map of canonical_code or practice_name to an alternate Google Maps query")
    parser.add_argument(
        "--full-reviews",
        choices=("none", "gtd", "all"),
        default="none",
        help="Optionally scroll the full Google Maps reviews feed instead of just capturing currently visible cards.",
    )
    parser.add_argument(
        "--full-review-limit",
        type=int,
        default=0,
        help="Maximum reviews to keep when full-review mode is active; 0 keeps scrolling until Google stops loading more cards.",
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
        total = len(rows)
        for index, row in enumerate(rows, start=1):
            query = resolve_query(row, query_overrides)
            print(f"[{index}/{total}] {query}")
            collect_full_reviews = args.full_reviews == "all" or (
                args.full_reviews == "gtd" and is_gtd_managed_row(row)
            )
            try:
                result = scrape_place(
                    driver,
                    query,
                    args.recent_reviews,
                    full_reviews_requested=collect_full_reviews,
                    full_review_limit=args.full_review_limit,
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
                    "recent_reviews": [],
                    "scan_error": normalize_text(str(exc)),
                }
            result["practice_name"] = row["practice_name"]
            result["postcode"] = row["postcode"]
            result["canonical_code"] = row["canonical_code"]
            result["nhs_profile_url"] = row["nhs_profile_url"]
            result["query_used"] = query
            result["title_match_score"] = round(title_similarity(row["practice_name"], str(result.get("google_maps_title", ""))), 3)
            result["review_text_file"] = write_review_text_file(args.reviews_text_dir, result)
            existing_index = existing_result_indexes.get(row["canonical_code"], None)
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
