#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
import time
from collections import deque
from configparser import ConfigParser
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

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
DEFAULT_TARGETS = {
    "appointments": ["appointment", "appointments", "book an appointment"],
    "online_services": ["online service", "online services", "patchs", "accurx", "askmygp"],
    "prescriptions": ["prescription", "repeat prescription", "repeat medication"],
    "contact": ["contact", "opening hours", "opening-hour"],
    "complaints": ["complaint", "complaints", "feedback"],
}


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
        for section in parser.sections():
            if section.startswith("Profile") and parser.getboolean(section, "Default", fallback=False):
                default_path = parser.get(section, "Path", fallback="")
                if default_path:
                    break
    if not default_path:
        raise RuntimeError(f"Could not determine a default Firefox profile from {profiles_ini}")
    return FIREFOX_DIR / default_path


def copy_profile(source: Path) -> Path:
    temp_root = Path(tempfile.mkdtemp(prefix="practice-patterns-firefox-profile-"))
    target = temp_root / "profile"
    shutil.copytree(
        source,
        target,
        ignore=shutil.ignore_patterns(*PROFILE_IGNORE),
    )
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
    options.set_preference("browser.shell.checkDefaultBrowser", False)
    if headless:
        options.add_argument("-headless")
    service = Service()
    driver = webdriver.Firefox(options=options, service=service)
    driver.set_page_load_timeout(timeout_seconds)
    return driver


def wait_until_ready(driver: webdriver.Firefox, timeout_seconds: int) -> None:
    WebDriverWait(driver, timeout_seconds).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def same_host(url: str, base_netloc: str) -> bool:
    return urlparse(url).netloc == base_netloc


def normalize_url(base_url: str, href: str) -> str | None:
    if not href:
        return None
    href = href.strip()
    if href.startswith(("javascript:", "mailto:", "tel:")):
        return None
    absolute = urljoin(base_url, href)
    parsed = urlparse(absolute)
    if parsed.scheme not in {"http", "https"}:
        return None
    return absolute


def detect_cookie_popup(driver: webdriver.Firefox) -> bool:
    """Heuristic: likely cookie/consent banner visible. Minimal check, not exhaustive."""
    try:
        return driver.execute_script(
            """
            var sel = '[id*="cookie"],[class*="cookie"],[class*="consent"],[class*="gdpr"],[class*="banner"]';
            var els = document.querySelectorAll(sel);
            var body = (document.body && document.body.innerText) ? document.body.innerText.toLowerCase() : '';
            for (var i = 0; i < els.length; i++) {
                var t = ((els[i].innerText || els[i].textContent) || '').toLowerCase();
                if ((t.indexOf('accept') >= 0 || t.indexOf('reject') >= 0) && (t.indexOf('cookie') >= 0 || t.length < 500)) return true;
            }
            return body.indexOf('accept analytics cookies') >= 0 || body.indexOf('reject analytics cookies') >= 0;
            """
        )
    except Exception:
        return False


def extract_links(driver: webdriver.Firefox, current_url: str, base_netloc: str) -> list[dict[str, str]]:
    raw_links: list[dict[str, Any]] = driver.execute_script(
        """
        return Array.from(document.querySelectorAll('a[href]')).map(link => ({
          text: (link.innerText || link.textContent || '').trim(),
          href: link.getAttribute('href') || '',
          aria: (link.getAttribute('aria-label') || '').trim()
        }));
        """
    )
    links: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in raw_links:
        href = normalize_url(current_url, str(item.get("href", "")))
        if not href or not same_host(href, base_netloc):
            continue
        if href in seen:
            continue
        seen.add(href)
        text = str(item.get("text", "") or item.get("aria", "")).strip()
        links.append({"href": href, "text": text})
    return links


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def summarize_discovered_paths(page_url: str, links: list[dict[str, str]], discovered_at: str) -> list[dict[str, str]]:
    return [
        {
            "href": link["href"],
            "text": link["text"],
            "discovered_from_url": page_url,
            "discovered_at": discovered_at,
        }
        for link in links[:50]
    ]


def score_text(text: str, keywords: list[str]) -> int:
    lowered = text.lower()
    return sum(1 for keyword in keywords if keyword in lowered)


def crawl_site(
    driver: webdriver.Firefox,
    start_url: str,
    max_depth: int,
    max_pages: int,
    timeout_seconds: int,
) -> dict[str, Any]:
    base_netloc = urlparse(start_url).netloc
    visited: dict[str, dict[str, Any]] = {}
    queue: deque[tuple[str, int, list[dict[str, str]]]] = deque([(start_url, 0, [])])

    while queue and len(visited) < max_pages:
        url, depth, path = queue.popleft()
        if url in visited:
            continue
        start = time.perf_counter()
        encountered_at = iso_now()
        error = None
        cookie_popup = False
        try:
            driver.get(url)
            wait_until_ready(driver, timeout_seconds)
            title = driver.title
            current_url = driver.current_url
            load_ms = round((time.perf_counter() - start) * 1000, 1)
            cookie_popup = detect_cookie_popup(driver)
            links = extract_links(driver, current_url, base_netloc)
        except (TimeoutException, WebDriverException) as exc:
            title = ""
            current_url = url
            load_ms = round((time.perf_counter() - start) * 1000, 1)
            links = []
            error = f"{type(exc).__name__}: {exc}"

        visited[url] = {
            "url": current_url,
            "title": title,
            "depth": depth,
            "path": path,
            "encountered_at": encountered_at,
            "load_ms": load_ms,
            "error": error,
            "cookie_popup": cookie_popup,
            "links": summarize_discovered_paths(current_url, links, encountered_at),
        }

        if depth >= max_depth or error:
            continue

        # Prefer obviously useful navigation pages first.
        ranked_links = sorted(
            links,
            key=lambda link: (
                score_text(link["text"] + " " + link["href"], DEFAULT_TARGETS["appointments"])
                + score_text(link["text"] + " " + link["href"], DEFAULT_TARGETS["online_services"])
                + score_text(link["text"] + " " + link["href"], DEFAULT_TARGETS["prescriptions"])
                + score_text(link["text"] + " " + link["href"], DEFAULT_TARGETS["contact"])
                + score_text(link["text"] + " " + link["href"], DEFAULT_TARGETS["complaints"]),
                -len(link["href"]),
            ),
            reverse=True,
        )
        for link in ranked_links[:30]:
            next_url = link["href"]
            if next_url in visited:
                continue
            queue.append((next_url, depth + 1, path + [link]))

    return {"start_url": start_url, "pages": list(visited.values())}


def find_target_routes(crawl: dict[str, Any]) -> dict[str, Any]:
    routes: dict[str, Any] = {}
    for target_name, keywords in DEFAULT_TARGETS.items():
        matches: list[dict[str, Any]] = []
        for page in crawl["pages"]:
            entry_text = " ".join(
                [
                    page.get("title", ""),
                    page.get("url", ""),
                    " ".join(
                        str(step.get("text", "")) + " " + str(step.get("href", ""))
                        for step in page.get("path", [])
                    ),
                ]
            ).lower()
            if page.get("depth") == 0:
                entry_text = " ".join([page.get("title", ""), page.get("url", "")]).lower()
            if any(keyword in entry_text for keyword in keywords):
                matches.append(page)
        matches.sort(key=lambda page: (page.get("depth", 99), page.get("load_ms", 999999)))
        if matches:
            winner = matches[0]
            routes[target_name] = {
                "status": "found",
                "steps_from_home": winner.get("depth"),
                "final_url": winner.get("url"),
                "title": winner.get("title"),
                "encountered_at": winner.get("encountered_at"),
                "load_ms": winner.get("load_ms"),
                "path": winner.get("path"),
                "replay": build_replay_steps(crawl.get("start_url", ""), winner),
            }
        else:
            routes[target_name] = {
                "status": "not_found",
                "replay": {
                    "check_id": target_name,
                    "start_url": crawl.get("start_url", ""),
                    "actions": [
                        {
                            "action": "goto",
                            "url": crawl.get("start_url", ""),
                        }
                    ],
                    "expected": {
                        "kind": "discover_target_route",
                        "keywords": keywords,
                    },
                },
            }
    return routes


def build_replay_steps(start_url: str, winner: dict[str, Any]) -> dict[str, Any]:
    actions: list[dict[str, Any]] = [{"action": "goto", "url": start_url}]
    for step in winner.get("path", []):
        actions.append(
            {
                "action": "click_link",
                "href": step.get("href"),
                "text": step.get("text"),
            }
        )
    return {
        "check_id": slug_from_url_or_title(winner.get("url", ""), winner.get("title", "")),
        "start_url": start_url,
        "actions": actions,
        "expected": {
            "kind": "final_url",
            "url": winner.get("url"),
            "title": winner.get("title"),
        },
    }


def slug_from_url_or_title(url: str, title: str) -> str:
    basis = title or url
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in basis)
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-") or "route-check"


def collect_issues(crawl: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for page in crawl.get("pages", []):
        if page.get("error"):
            issues.append(
                {
                    "issue_type": "navigation_error",
                    "encountered_at": page.get("encountered_at"),
                    "url": page.get("url"),
                    "depth": page.get("depth"),
                    "details": page.get("error"),
                }
            )
        if page.get("depth") == 0 and not page.get("links"):
            issues.append(
                {
                    "issue_type": "homepage_exposed_no_internal_links",
                    "encountered_at": page.get("encountered_at"),
                    "url": page.get("url"),
                    "depth": page.get("depth"),
                    "details": "No internal links were captured from the homepage during this browser walk.",
                }
            )
    return issues


def main() -> None:
    parser = argparse.ArgumentParser(description="Walk a practice website in Firefox using a copied local profile.")
    parser.add_argument("--url", required=True, help="Homepage URL to inspect")
    parser.add_argument("--profile", help="Firefox profile directory to copy before launch")
    parser.add_argument("--headless", action="store_true", help="Run Firefox headlessly")
    parser.add_argument("--max-depth", type=int, default=2, help="Max internal link depth from homepage")
    parser.add_argument("--max-pages", type=int, default=25, help="Max internal pages to visit")
    parser.add_argument("--timeout-seconds", type=int, default=25, help="Per-page timeout")
    parser.add_argument("--output", help="Optional JSON file path")
    args = parser.parse_args()

    source_profile = Path(args.profile).expanduser() if args.profile else read_default_profile()
    copied_profile = copy_profile(source_profile)

    payload: dict[str, Any] = {
        "generated_at": iso_now(),
        "url": args.url,
        "source_profile": str(source_profile),
        "copied_profile": str(copied_profile),
        "headless": args.headless,
        "max_depth": args.max_depth,
        "max_pages": args.max_pages,
    }

    driver = None
    try:
        driver = make_driver(copied_profile, args.headless, args.timeout_seconds)
        crawl = crawl_site(driver, args.url, args.max_depth, args.max_pages, args.timeout_seconds)
        payload["crawl"] = crawl
        payload["target_routes"] = find_target_routes(crawl)
        payload["issues"] = collect_issues(crawl)
    finally:
        if driver is not None:
            driver.quit()
        shutil.rmtree(copied_profile.parent, ignore_errors=True)

    text = json.dumps(payload, indent=2)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        pages = payload.get("crawl", {}).get("pages", [])
        cookie_count = sum(1 for p in pages if p.get("cookie_popup"))
        summary = {
            "output": args.output,
            "visited_pages": len(pages),
            "cookie_popups_encountered": cookie_count,
            "target_routes": payload.get("target_routes", {}),
        }
        print(json.dumps(summary, indent=2))
    else:
        print(text)


if __name__ == "__main__":
    main()
