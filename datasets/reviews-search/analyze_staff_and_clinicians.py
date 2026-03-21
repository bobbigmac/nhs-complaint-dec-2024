#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "output" / "reviews_index.sqlite"


POSITIVE_THEME_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "kind_listening_care": [
        re.compile(r"\bhelpful\b", re.I),
        re.compile(r"\bcaring\b", re.I),
        re.compile(r"\bkind\b", re.I),
        re.compile(r"\blistened\b", re.I),
        re.compile(r"\breassur\w*\b", re.I),
        re.compile(r"\bprofessional\b", re.I),
        re.compile(r"\bthorough\b", re.I),
        re.compile(r"\bcompassion\w*\b", re.I),
    ],
    "friendly_front_desk": [
        re.compile(r"\bfriendly\b", re.I),
        re.compile(r"\bwelcoming\b", re.I),
        re.compile(r"\blovely\b", re.I),
        re.compile(r"\bpolite\b", re.I),
        re.compile(r"\brespectful\b", re.I),
    ],
    "practical_problem_solving": [
        re.compile(r"\b(sorted|sorting|arranged|managed|resolved|chased|called back|got back to me|went the extra mile)\b", re.I),
        re.compile(r"\bmade me feel at ease\b", re.I),
    ],
}


NEGATIVE_THEME_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "rude_or_dismissive_staff": [
        re.compile(r"\brude\b", re.I),
        re.compile(r"\bunhelpful\b", re.I),
        re.compile(r"\bdismissive\b", re.I),
        re.compile(r"\bhostile\b", re.I),
        re.compile(r"\bcondescend\w*\b", re.I),
        re.compile(r"\barrogant\b", re.I),
        re.compile(r"\battitude\b", re.I),
        re.compile(r"\bjobsworth\w*\b", re.I),
    ],
    "not_listened_to_or_brushed_off": [
        re.compile(r"\bdidn['’]?t listen\b", re.I),
        re.compile(r"\bwouldn['’]?t listen\b", re.I),
        re.compile(r"\bnot taken seriously\b", re.I),
        re.compile(r"\bignored\b", re.I),
        re.compile(r"\bfobbed off\b", re.I),
        re.compile(r"\bbrushed off\b", re.I),
        re.compile(r"\brushed me off\b", re.I),
        re.compile(r"\bdismiss\w*\b", re.I),
    ],
    "clinical_judgment_or_safety_concern": [
        re.compile(r"\bmisdiagnos\w*\b", re.I),
        re.compile(r"\bwrong medication\b", re.I),
        re.compile(r"\bwrong dose\b", re.I),
        re.compile(r"\bunsafe\b", re.I),
        re.compile(r"\bnegligen\w*\b", re.I),
        re.compile(r"\bdangerous\b", re.I),
        re.compile(r"\bwould have died\b", re.I),
        re.compile(r"\bended up in hospital\b", re.I),
    ],
    "rigid_or_unreasonable_handling": [
        re.compile(r"\bcall back tomorrow\b", re.I),
        re.compile(r"\btold to use\b.{0,20}\b(website|online|form|app)\b", re.I),
        re.compile(r"\bcan'?t book in advance\b", re.I),
        re.compile(r"\brefused\b.{0,25}\bappointment\b", re.I),
        re.compile(r"\bno flexibility\b", re.I),
        re.compile(r"\bsent me to\b.{0,20}\bpharmacy\b", re.I),
    ],
}


POSITIVE_NAME_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("doctor", re.compile(r"\bDr\.?\s+([A-Z][A-Za-z'’-]+(?:\s+[A-Z][A-Za-z'’-]+)?)")),
    ("doctor", re.compile(r"\bdoctor\s+([A-Z][A-Za-z'’-]+(?:\s+[A-Z][A-Za-z'’-]+)?)", re.I)),
    ("nurse", re.compile(r"\bnurse\s+([A-Z][A-Za-z'’-]+(?:\s+[A-Z][A-Za-z'’-]+)?)", re.I)),
    ("reception", re.compile(r"\breception(?:ist)?\s+([A-Z][A-Za-z'’-]+(?:\s+[A-Z][A-Za-z'’-]+)?)", re.I)),
    ("staff", re.compile(r"\bthank(?:s| you)? to\s+([A-Z][A-Za-z'’-]+(?:\s+[A-Z][A-Za-z'’-]+)?)", re.I)),
    ("staff", re.compile(r"\bespecially\s+([A-Z][A-Za-z'’-]+(?:\s+[A-Z][A-Za-z'’-]+)?)", re.I)),
    ("staff", re.compile(r"\b([A-Z][A-Za-z'’-]+)\s+on reception\b")),
]


PRAISE_CONTEXT = [
    re.compile(r"\b(thank you|thanks|helpful|kind|caring|wonderful|amazing|brilliant|professional|lovely|reassuring|thorough|friendly|welcoming|attentive|supportive)\b", re.I)
]


NAME_STOP = {
    "Dr",
    "Doctor",
    "Nurse",
    "Reception",
    "Receptionist",
    "Team",
    "Staff",
    "Today",
    "Everyone",
    "Practice",
    "Manager",
    "Service",
    "Care",
    "Was",
    "Very",
    "Great",
    "Lovely",
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


def normalize_name(raw: str) -> str | None:
    value = " ".join(raw.replace("’", "'").replace("–", "-").split()).strip(" ,.;:!?'\"")
    if not value:
        return None
    value = value.title() if value.islower() else value
    parts = value.split()
    if len(parts) > 3:
        return None
    if any(part in NAME_STOP for part in parts):
        return None
    if any(len(part) < 2 for part in parts):
        return None
    return value


def has_praise_context(text: str) -> bool:
    return any(pattern.search(text) for pattern in PRAISE_CONTEXT)


def analyze(db_path: Path = DB_PATH) -> dict[str, object]:
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    try:
        rows = con.execute(
            """
            SELECT id, canonical_code, practice_name, rating_stars, author, date_raw, estimated_months_ago, text
            FROM reviews
            ORDER BY id
            """
        ).fetchall()

        high_star_total = 0
        low_star_total = 0
        positive_themes = {key: {"count": 0, "examples": []} for key in POSITIVE_THEME_PATTERNS}
        negative_themes = {key: {"count": 0, "examples": []} for key in NEGATIVE_THEME_PATTERNS}
        named_positive: dict[tuple[str, str], dict[str, object]] = defaultdict(
            lambda: {
                "practice_name": "",
                "canonical_code": "",
                "name": "",
                "review_ids": set(),
                "ratings": [],
                "roles": Counter(),
                "examples": [],
            }
        )

        for row in rows:
            text = strip_practice_response(str(row["text"] or ""))
            if not text:
                continue
            stars = int(row["rating_stars"] or 0)

            item = {
                "practice_name": str(row["practice_name"]),
                "canonical_code": str(row["canonical_code"]),
                "author": str(row["author"]),
                "date_raw": str(row["date_raw"]),
                "estimated_months_ago": row["estimated_months_ago"],
                "quote": snippet(text),
            }

            if stars >= 4:
                high_star_total += 1
                for theme, patterns in POSITIVE_THEME_PATTERNS.items():
                    if any(pattern.search(text) for pattern in patterns):
                        positive_themes[theme]["count"] += 1
                        positive_themes[theme]["examples"].append(item)

                if has_praise_context(text):
                    review_id = int(row["id"])
                    found_names: set[tuple[str, str]] = set()
                    for role, pattern in POSITIVE_NAME_PATTERNS:
                        for match in pattern.finditer(text):
                            name = normalize_name(match.group(1))
                            if not name:
                                continue
                            key = (str(row["practice_name"]), name)
                            if key in found_names:
                                continue
                            found_names.add(key)
                            record = named_positive[key]
                            record["practice_name"] = str(row["practice_name"])
                            record["canonical_code"] = str(row["canonical_code"])
                            record["name"] = name
                            record["review_ids"].add(review_id)
                            record["ratings"].append(stars)
                            record["roles"][role] += 1
                            record["examples"].append(item)

            if stars <= 2:
                low_star_total += 1
                for theme, patterns in NEGATIVE_THEME_PATTERNS.items():
                    if any(pattern.search(text) for pattern in patterns):
                        negative_themes[theme]["count"] += 1
                        negative_themes[theme]["examples"].append(item)

        for bucket in positive_themes.values():
            bucket["examples"] = sorted(
                bucket["examples"],
                key=lambda item: (
                    item["estimated_months_ago"] is None,
                    item["estimated_months_ago"] if item["estimated_months_ago"] is not None else 10**9,
                ),
            )[:8]

        for bucket in negative_themes.values():
            bucket["examples"] = sorted(
                bucket["examples"],
                key=lambda item: (
                    item["estimated_months_ago"] is None,
                    item["estimated_months_ago"] if item["estimated_months_ago"] is not None else 10**9,
                ),
            )[:8]

        named_rows: list[dict[str, object]] = []
        for record in named_positive.values():
            review_count = len(record["review_ids"])
            if review_count < 3:
                continue
            examples = sorted(
                record["examples"],
                key=lambda item: (
                    item["estimated_months_ago"] is None,
                    item["estimated_months_ago"] if item["estimated_months_ago"] is not None else 10**9,
                ),
            )[:5]
            named_rows.append(
                {
                    "practice_name": record["practice_name"],
                    "canonical_code": record["canonical_code"],
                    "name": record["name"],
                    "review_count": review_count,
                    "avg_rating": round(sum(record["ratings"]) / len(record["ratings"]), 2),
                    "roles": dict(record["roles"]),
                    "examples": examples,
                }
            )

        named_rows.sort(key=lambda item: (-int(item["review_count"]), -float(item["avg_rating"]), item["practice_name"], item["name"]))

        return {
            "high_star_reviews": high_star_total,
            "low_star_reviews": low_star_total,
            "positive_themes": positive_themes,
            "negative_themes": negative_themes,
            "named_positive_people": named_rows[:40],
        }
    finally:
        con.close()


def main() -> int:
    print(json.dumps(analyze(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
