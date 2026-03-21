#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sqlite3
from collections import defaultdict
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "output" / "reviews_index.sqlite"


LOOSE_ACCESS_PATTERNS = [
    re.compile(r"\bappointment\b", re.I),
    re.compile(r"\bphone\b", re.I),
    re.compile(r"\breception(?:ist|ists)?\b", re.I),
    re.compile(r"\b(website|online|form|app|patchs|askmygp|econsult|accurx|nhs app)\b", re.I),
    re.compile(r"\b(callback|call back)\b", re.I),
    re.compile(r"\b(results?|referral|prescription)\b", re.I),
]


ACCESS_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "appointment_shortage_or_delay": [
        re.compile(r"\b(can'?t|get no|never|unable to|impossible to|difficult to|hard to|struggle to)\b.{0,30}\b(get|book|make|arrange)\b.{0,20}\bappointment\b", re.I),
        re.compile(r"\bno appointments? (left|available)\b", re.I),
        re.compile(r"\b(wait|waiting)\b.{0,20}\b(weeks?|months?)\b.{0,20}\bappointment\b", re.I),
        re.compile(r"\b8\s*am\b", re.I),
        re.compile(r"\bsame day\b.{0,20}\bappointments?\b", re.I),
        re.compile(r"\bon the day appointment\b", re.I),
    ],
    "phone_access_failure": [
        re.compile(r"\b(phone|phone line|lines?)\b.{0,30}\b(busy|engaged|ringing out|never answered|not answered|unanswered)\b", re.I),
        re.compile(r"\b(on hold|hold)\b", re.I),
        re.compile(r"\b(can'?t|get|couldn'?t get)\b.{0,20}\bthrough\b", re.I),
        re.compile(r"\b(ringing|rang)\b.{0,25}\b(no answer|engaged|busy)\b", re.I),
        re.compile(r"\bqueue\b.{0,20}\b(phone|line)\b", re.I),
    ],
    "reception_barrier_or_gatekeeping": [
        re.compile(r"\breception(?:ist|ists)?\b.{0,35}\b(rude|unhelpful|dismissive|arrogant|hostile|abusive|condescending)\b", re.I),
        re.compile(r"\breception(?:ist|ists)?\b.{0,45}\b(refused|wouldn'?t|would not|told me to)\b", re.I),
        re.compile(r"\bfobbed off\b", re.I),
        re.compile(r"\bgatekeep\w*\b", re.I),
        re.compile(r"\btold to use\b.{0,30}\b(website|online|form|app)\b", re.I),
    ],
    "digital_front_door_problem": [
        re.compile(r"\b(website|online|form|app|patchs|askmygp|econsult|accurx|nhs app)\b.{0,35}\b(closed|full|offline|not available|unavailable)\b", re.I),
        re.compile(r"\b(website|online|form|app|system)\b.{0,35}\b(hard to use|confusing|doesn'?t work|not working|won'?t load|wouldn'?t load)\b", re.I),
        re.compile(r"\bfill in\b.{0,30}\bform\b.{0,40}\b(no reply|nothing|still no)\b", re.I),
        re.compile(r"\bcut me off as i was writing\b", re.I),
        re.compile(r"\b(only opens?|open at)\b.{0,20}\b(6pm|8am|7:?30|10:?00)\b", re.I),
    ],
    "follow_up_results_referrals_prescriptions": [
        re.compile(r"\b(callback|call back|called back)\b", re.I),
        re.compile(r"\b(results?|test results?)\b", re.I),
        re.compile(r"\breferral\b", re.I),
        re.compile(r"\bprescription\b", re.I),
        re.compile(r"\brepeat medication\b", re.I),
        re.compile(r"\b(letter|letters)\b.{0,25}\b(not sent|missing|lost|wrong)\b", re.I),
        re.compile(r"\bchasing\b.{0,30}\b(results?|referral|prescription|callback)\b", re.I),
        re.compile(r"\bnever heard back\b", re.I),
        re.compile(r"\bno response\b", re.I),
    ],
    "exclusion_or_leaving": [
        re.compile(r"\bcatchment\b", re.I),
        re.compile(r"\b(register elsewhere|another doctor|another gp|change doctor|change gp|changed doctors|changed gp)\b", re.I),
        re.compile(r"\bde-register|deregister\b", re.I),
        re.compile(r"\bout of area\b", re.I),
        re.compile(r"\boutside the area\b", re.I),
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


def match_categories(text: str) -> set[str]:
    return {
        key
        for key, patterns in ACCESS_PATTERNS.items()
        if any(pattern.search(text) for pattern in patterns)
    }


def analyze(db_path: Path = DB_PATH) -> dict[str, object]:
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    try:
        rows = con.execute(
            """
            SELECT
              id,
              canonical_code,
              practice_name,
              rating_stars,
              author,
              date_raw,
              estimated_months_ago,
              estimated_year,
              text
            FROM reviews
            ORDER BY id
            """
        ).fetchall()

        total_reviews = len(rows)
        low_star_total = sum(1 for row in rows if int(row["rating_stars"] or 0) <= 2)
        all_access_ids: set[int] = set()
        low_star_access_ids: set[int] = set()

        category_summary = {
            key: {
                "all_reviews": 0,
                "low_star_reviews": 0,
                "practices": defaultdict(int),
                "recent_examples": [],
                "recent_low_star_examples": [],
            }
            for key in ACCESS_PATTERNS
        }

        loose_access_ids: set[int] = set()

        for row in rows:
            text = strip_practice_response(str(row["text"] or ""))
            if not text:
                continue
            review_id = int(row["id"])
            if any(pattern.search(text) for pattern in LOOSE_ACCESS_PATTERNS):
                loose_access_ids.add(review_id)
            categories = match_categories(text)
            if not categories:
                continue

            stars = int(row["rating_stars"] or 0)
            all_access_ids.add(review_id)
            if stars <= 2:
                low_star_access_ids.add(review_id)

            example = {
                "practice_name": str(row["practice_name"]),
                "canonical_code": str(row["canonical_code"]),
                "author": str(row["author"]),
                "date_raw": str(row["date_raw"]),
                "estimated_months_ago": row["estimated_months_ago"],
                "estimated_year": row["estimated_year"],
                "rating_stars": stars,
                "quote": snippet(text),
            }

            for category in categories:
                summary = category_summary[category]
                summary["all_reviews"] += 1
                if stars <= 2:
                    summary["low_star_reviews"] += 1
                summary["practices"][str(row["practice_name"])] += 1
                summary["recent_examples"].append(example)
                if stars <= 2:
                    summary["recent_low_star_examples"].append(example)

        for summary in category_summary.values():
            summary["top_practices"] = sorted(summary["practices"].items(), key=lambda kv: (-kv[1], kv[0]))[:12]
            del summary["practices"]
            summary["recent_examples"] = sorted(
                summary["recent_examples"],
                key=lambda item: (
                    item["estimated_months_ago"] is None,
                    item["estimated_months_ago"] if item["estimated_months_ago"] is not None else 10**9,
                    -int(item["rating_stars"]),
                ),
            )[:10]
            summary["recent_low_star_examples"] = sorted(
                summary["recent_low_star_examples"],
                key=lambda item: (
                    item["estimated_months_ago"] is None,
                    item["estimated_months_ago"] if item["estimated_months_ago"] is not None else 10**9,
                    item["rating_stars"],
                ),
            )[:10]

        return {
            "total_reviews": total_reviews,
            "low_star_total": low_star_total,
            "loose_access_reviews": len(loose_access_ids),
            "loose_access_share": round((len(loose_access_ids) / total_reviews) * 100, 1) if total_reviews else 0.0,
            "broad_access_reviews": len(all_access_ids),
            "broad_access_share": round((len(all_access_ids) / total_reviews) * 100, 1) if total_reviews else 0.0,
            "low_star_access_reviews": len(low_star_access_ids),
            "low_star_access_share_of_all_reviews": round((len(low_star_access_ids) / total_reviews) * 100, 1)
            if total_reviews
            else 0.0,
            "low_star_access_share_of_low_star_reviews": round((len(low_star_access_ids) / low_star_total) * 100, 1)
            if low_star_total
            else 0.0,
            "categories": category_summary,
        }
    finally:
        con.close()


def main() -> int:
    print(json.dumps(analyze(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
