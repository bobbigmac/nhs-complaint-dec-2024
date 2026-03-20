#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sqlite3
from collections import defaultdict
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "output" / "reviews_index.sqlite"


PLATFORM_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "generic_online_or_website": [
        re.compile(r"\bonline\b", re.I),
        re.compile(r"\bwebsite\b", re.I),
        re.compile(r"\bonline form\b", re.I),
        re.compile(r"\bonline booking\b", re.I),
        re.compile(r"\bonline triage\b", re.I),
        re.compile(r"\bbook online\b", re.I),
    ],
    "patchs": [re.compile(r"\bpatchs\b", re.I)],
    "askmygp": [re.compile(r"\baskmygp\b", re.I)],
    "accurx": [re.compile(r"\baccurx\b", re.I), re.compile(r"\bflorey\.accurx\.com\b", re.I)],
    "econsult": [re.compile(r"\beconsult\b", re.I), re.compile(r"\be-consult\b", re.I)],
    "nhs_app": [re.compile(r"\bnhs app\b", re.I)],
}


ISSUE_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "online_only_gatekeeping": [
        re.compile(r"\btold to use\b.{0,40}\b(website|online|form|app|patchs|askmygp|econsult|accurx)\b", re.I),
        re.compile(r"\bcan'?t speak to anyone\b.{0,40}\bwebsite\b", re.I),
        re.compile(r"\bmust\b.{0,30}\bdo it\b.{0,20}\bonline\b", re.I),
        re.compile(r"\b(go|use|do it) (on|via) the\b.{0,20}\bwebsite\b", re.I),
    ],
    "form_closed_or_fills_up": [
        re.compile(r"\b(closed|shut|full|fills? up|filled up|not open)\b.{0,40}\b(online|form|askmygp|patchs|website)\b", re.I),
        re.compile(r"\b(askmygp|patchs)\b.{0,30}\b(closed|full|offline)\b", re.I),
        re.compile(r"\bby 8(:?00)?\b.{0,40}\b(full|filled|closed)\b", re.I),
    ],
    "no_reply_or_lost_request": [
        re.compile(r"\bno response\b", re.I),
        re.compile(r"\bno record of submission\b", re.I),
        re.compile(r"\bnever heard back\b", re.I),
        re.compile(r"\bnot replied\b", re.I),
        re.compile(r"\bno callback\b", re.I),
        re.compile(r"\bsubmitted\b.{0,40}\bno reply\b", re.I),
    ],
    "usability_or_instruction_failure": [
        re.compile(r"\b(no instructions|hard to use|difficult to use|confusing|hard to find|struggle to locate|don't know how)\b", re.I),
        re.compile(r"\bhow to sign up\b", re.I),
        re.compile(r"\bwebsite not good\b", re.I),
        re.compile(r"\bunable to work the website\b", re.I),
        re.compile(r"\bworst website\b", re.I),
    ],
    "triage_burden_or_self_diagnosis": [
        re.compile(r"\bself diagnos\w*\b", re.I),
        re.compile(r"\btoo many questions\b", re.I),
        re.compile(r"\bai\b.{0,30}\basking\b", re.I),
        re.compile(r"\b20 mins? to complete\b", re.I),
        re.compile(r"\bfill in\b.{0,30}\bform\b.{0,40}\bappointment\b", re.I),
    ],
    "digital_exclusion_or_accessibility": [
        re.compile(r"\b(not everyone|older people|elderly|disabled|disability|learning disability)\b.{0,50}\b(online|website|app|form)\b", re.I),
        re.compile(r"\bnot good with computers\b", re.I),
        re.compile(r"\bno smartphone\b", re.I),
        re.compile(r"\bcan'?t use\b.{0,30}\b(website|app|online form)\b", re.I),
    ],
    "positive_speed_or_convenience": [
        re.compile(r"\b(within|in)\b.{0,20}\b(20 minutes|30 minutes|few hours|same day)\b", re.I),
        re.compile(r"\bsame day appointment\b", re.I),
        re.compile(r"\brespond(s|ed)? fast\b", re.I),
        re.compile(r"\bworks well\b", re.I),
        re.compile(r"\bexcellent\b.{0,30}\b(askmygp|patchs|online form|econsult)\b", re.I),
        re.compile(r"\bquick response\b", re.I),
    ],
    "mixed_or_confusing_platform_setup": [
        re.compile(r"\bno longer used\b", re.I),
        re.compile(r"\bphone line says\b", re.I),
        re.compile(r"\bwebsite says\b", re.I),
        re.compile(r"\blinked to\b", re.I),
        re.compile(r"\bnot obvious\b", re.I),
    ],
}


def strip_practice_response(text: str) -> str:
    return (text or "").split("Practice response date:")[0].strip()


def clean_text(text: str) -> str:
    return " ".join((text or "").split())


def snippet(text: str, max_chars: int = 260) -> str:
    value = clean_text(text)
    if len(value) <= max_chars:
        return value
    return value[: max_chars - 3].rstrip() + "..."


def match_keys(text: str, patterns: dict[str, list[re.Pattern[str]]]) -> set[str]:
    matches: set[str] = set()
    for key, group in patterns.items():
        if any(pattern.search(text) for pattern in group):
            matches.add(key)
    return matches


def analyze(db_path: Path = DB_PATH) -> dict[str, object]:
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    try:
        rows = con.execute(
            """
            SELECT id, canonical_code, practice_name, rating_stars, author, date_raw, text
            FROM reviews
            ORDER BY id
            """
        ).fetchall()

        total_reviews = len(rows)
        flagged_reviews = []
        platform_summary = {
            key: {"count": 0, "positive": 0, "negative": 0, "mixed": 0, "examples": [], "practices": defaultdict(int)}
            for key in PLATFORM_PATTERNS
        }
        issue_summary = {
            key: {"count": 0, "positive": 0, "negative": 0, "mixed": 0, "examples": [], "practices": defaultdict(int)}
            for key in ISSUE_PATTERNS
        }
        practice_summary: dict[tuple[str, str], dict[str, object]] = defaultdict(
            lambda: {
                "review_ids": set(),
                "platforms": defaultdict(int),
                "issues": defaultdict(int),
                "positive": 0,
                "negative": 0,
                "mixed": 0,
                "examples": [],
            }
        )

        for row in rows:
            text = strip_practice_response(str(row["text"] or ""))
            if not text:
                continue

            platforms = match_keys(text, PLATFORM_PATTERNS)
            issues = match_keys(text, ISSUE_PATTERNS)

            if not platforms and not issues:
                continue

            stars = int(row["rating_stars"] or 0)
            rating_bucket = "mixed"
            if stars >= 4:
                rating_bucket = "positive"
            elif stars <= 2:
                rating_bucket = "negative"

            flagged_reviews.append(
                {
                    "id": int(row["id"]),
                    "practice_name": str(row["practice_name"]),
                    "canonical_code": str(row["canonical_code"]),
                    "rating_stars": stars,
                    "author": str(row["author"]),
                    "date_raw": str(row["date_raw"]),
                    "platforms": sorted(platforms),
                    "issues": sorted(issues),
                    "quote": snippet(text),
                }
            )

            practice_key = (str(row["canonical_code"]), str(row["practice_name"]))
            practice = practice_summary[practice_key]
            practice["review_ids"].add(int(row["id"]))
            practice[rating_bucket] += 1
            if len(practice["examples"]) < 4:
                practice["examples"].append(snippet(text))

            for platform in platforms:
                platform_summary[platform]["count"] += 1
                platform_summary[platform][rating_bucket] += 1
                platform_summary[platform]["practices"][practice_key[1]] += 1
                practice["platforms"][platform] += 1
                if len(platform_summary[platform]["examples"]) < 6:
                    platform_summary[platform]["examples"].append(
                        {"practice_name": practice_key[1], "quote": snippet(text), "rating_stars": stars}
                    )

            for issue in issues:
                issue_summary[issue]["count"] += 1
                issue_summary[issue][rating_bucket] += 1
                issue_summary[issue]["practices"][practice_key[1]] += 1
                practice["issues"][issue] += 1
                if len(issue_summary[issue]["examples"]) < 6:
                    issue_summary[issue]["examples"].append(
                        {"practice_name": practice_key[1], "quote": snippet(text), "rating_stars": stars}
                    )

        practices = []
        for (code, name), item in practice_summary.items():
            total_practice_reviews = int(
                con.execute("SELECT COUNT(*) FROM reviews WHERE canonical_code = ?", (code,)).fetchone()[0] or 0
            )
            practices.append(
                {
                    "canonical_code": code,
                    "practice_name": name,
                    "digital_review_count": len(item["review_ids"]),
                    "digital_share_of_all_reviews": round((len(item["review_ids"]) / total_practice_reviews) * 100, 1)
                    if total_practice_reviews
                    else 0.0,
                    "positive": int(item["positive"]),
                    "negative": int(item["negative"]),
                    "mixed": int(item["mixed"]),
                    "platforms": dict(sorted(item["platforms"].items(), key=lambda kv: (-kv[1], kv[0]))),
                    "issues": dict(sorted(item["issues"].items(), key=lambda kv: (-kv[1], kv[0]))),
                    "examples": list(item["examples"]),
                }
            )
        practices.sort(key=lambda r: (-r["digital_review_count"], -r["digital_share_of_all_reviews"], r["practice_name"]))

        for summary in list(platform_summary.values()) + list(issue_summary.values()):
            summary["top_practices"] = sorted(summary["practices"].items(), key=lambda kv: (-kv[1], kv[0]))[:10]
            del summary["practices"]

        return {
            "total_reviews": total_reviews,
            "flagged_review_count": len(flagged_reviews),
            "flagged_share_of_all_reviews": round((len(flagged_reviews) / total_reviews) * 100, 1) if total_reviews else 0.0,
            "platforms": platform_summary,
            "issues": issue_summary,
            "top_practices": practices[:20],
        }
    finally:
        con.close()


def main() -> int:
    print(json.dumps(analyze(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
