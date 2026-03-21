#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "output" / "reviews_index.sqlite"
OLDER_YEARS = (2016, 2017, 2018, 2019)
RECENT_YEARS = (2022, 2023, 2024, 2025, 2026)


CATEGORY_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "persistent_8am_rush": [
        re.compile(r"\b8\s*am\b", re.I),
        re.compile(r"\b8am\b", re.I),
    ],
    "persistent_phone_no_answer": [
        re.compile(r"\bnever answer(?:s|ed)? the phone\b", re.I),
        re.compile(r"\b(can'?t|couldn'?t) get through\b", re.I),
        re.compile(r"\bphone\b.{0,30}\b(rings? out|engaged|busy|not answered|no answer)\b", re.I),
    ],
    "persistent_no_appointment": [
        re.compile(r"\b(can'?t|couldn'?t|never|unable to)\b.{0,30}\b(get|book|make)\b.{0,20}\bappointment\b", re.I),
        re.compile(r"\bno appointments? (left|available)\b", re.I),
        re.compile(r"\ball appointments? (gone|full)\b", re.I),
    ],
    "persistent_rude_reception": [
        re.compile(r"\breception(?:ist|ists)?\b.{0,35}\b(rude|unhelpful|dismissive|hostile|condescending|arrogant)\b", re.I),
        re.compile(r"\brude\b.{0,20}\breception(?:ist|ists)?\b", re.I),
    ],
    "older_walk_in_centre": [
        re.compile(r"\bwalk[\s-]?in centre\b", re.I),
        re.compile(r"\bwalk[\s-]?in\b.{0,20}\bappointment\b", re.I),
    ],
    "older_waiting_room_delay": [
        re.compile(r"\bwait(?:ed|ing)?\b.{0,25}\b(waiting room|reception|surgery)\b", re.I),
        re.compile(r"\bwaiting room\b", re.I),
        re.compile(r"\bsat (there|for)\b.{0,25}\b(hour|hours|minutes)\b", re.I),
    ],
    "recent_online_form": [
        re.compile(r"\bonline form\b", re.I),
        re.compile(r"\bform\b.{0,25}\b(not working|closed|turned off|unavailable|doesn'?t work|full)\b", re.I),
        re.compile(r"\bwebsite\b.{0,25}\bform\b", re.I),
    ],
    "recent_named_digital_systems": [
        re.compile(r"\baskmygp\b", re.I),
        re.compile(r"\bpatchs\b", re.I),
        re.compile(r"\beconsult\b", re.I),
        re.compile(r"\baccurx\b", re.I),
        re.compile(r"\bnhs app\b", re.I),
    ],
    "recent_triage": [
        re.compile(r"\btriage\b", re.I),
    ],
    "recent_telephone_consultation": [
        re.compile(r"\btelephone consultation\b", re.I),
        re.compile(r"\bphone consultation\b", re.I),
        re.compile(r"\bcall back from (a )?(gp|doctor)\b", re.I),
    ],
    "recent_face_to_face_access": [
        re.compile(r"\bface[- ]to[- ]face appointment\b", re.I),
        re.compile(r"\bface[- ]to[- ]face\b", re.I),
        re.compile(r"\bin person appointment\b", re.I),
    ],
}


def strip_practice_response(text: str) -> str:
    return (text or "").split("Practice response date:")[0].strip()


def clean_text(text: str) -> str:
    return " ".join((text or "").split())


def snippet(text: str, max_chars: int = 240) -> str:
    value = clean_text(text)
    if len(value) <= max_chars:
        return value
    return value[: max_chars - 3].rstrip() + "..."


def era_for_year(year: int | None) -> str | None:
    if year in OLDER_YEARS:
        return "older"
    if year in RECENT_YEARS:
        return "recent"
    return None


def analyze(db_path: Path = DB_PATH) -> dict[str, object]:
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    try:
        rows = con.execute(
            """
            SELECT id, canonical_code, practice_name, rating_stars, author, date_raw, estimated_year, estimated_months_ago, text
            FROM reviews
            WHERE rating_stars IN (1, 2)
            ORDER BY id
            """
        ).fetchall()

        older_total = 0
        recent_total = 0
        category_summary: dict[str, dict[str, object]] = {
            key: {"older": 0, "recent": 0, "older_examples": [], "recent_examples": []}
            for key in CATEGORY_PATTERNS
        }

        for row in rows:
            era = era_for_year(row["estimated_year"])
            if era is None:
                continue
            if era == "older":
                older_total += 1
            else:
                recent_total += 1

            text = strip_practice_response(str(row["text"] or ""))
            if not text:
                continue

            item = {
                "practice_name": str(row["practice_name"]),
                "canonical_code": str(row["canonical_code"]),
                "author": str(row["author"]),
                "date_raw": str(row["date_raw"]),
                "estimated_year": row["estimated_year"],
                "estimated_months_ago": row["estimated_months_ago"],
                "quote": snippet(text),
            }

            for category, patterns in CATEGORY_PATTERNS.items():
                if not any(pattern.search(text) for pattern in patterns):
                    continue
                summary = category_summary[category]
                summary[era] += 1
                summary[f"{era}_examples"].append(item)

        for summary in category_summary.values():
            summary["older_share"] = round((summary["older"] / older_total) * 100, 1) if older_total else 0.0
            summary["recent_share"] = round((summary["recent"] / recent_total) * 100, 1) if recent_total else 0.0
            summary["older_examples"] = sorted(
                summary["older_examples"],
                key=lambda item: (
                    item["estimated_year"] is None,
                    -(item["estimated_year"] or 0),
                    item["estimated_months_ago"] if item["estimated_months_ago"] is not None else 10**9,
                ),
            )[:8]
            summary["recent_examples"] = sorted(
                summary["recent_examples"],
                key=lambda item: (
                    item["estimated_months_ago"] is None,
                    item["estimated_months_ago"] if item["estimated_months_ago"] is not None else 10**9,
                ),
            )[:8]

        return {
            "older_low_star_reviews": older_total,
            "recent_low_star_reviews": recent_total,
            "categories": category_summary,
        }
    finally:
        con.close()


def main() -> int:
    print(json.dumps(analyze(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
