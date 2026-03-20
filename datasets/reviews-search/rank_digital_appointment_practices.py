#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import re
import sqlite3
from collections import defaultdict
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "output" / "reviews_index.sqlite"


PLATFORM_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "generic_online_or_website": [
        re.compile(r"\bonline\b", re.I),
        re.compile(r"\bwebsite\b", re.I),
        re.compile(r"\bsite\b", re.I),
        re.compile(r"\bonline form\b", re.I),
        re.compile(r"\bonline booking\b", re.I),
        re.compile(r"\bonline triage\b", re.I),
        re.compile(r"\bbook online\b", re.I),
        re.compile(r"\bthe app\b", re.I),
        re.compile(r"\bthe system\b", re.I),
    ],
    "patchs": [re.compile(r"\bpatchs\b", re.I)],
    "askmygp": [re.compile(r"\baskmygp\b", re.I)],
    "accurx": [re.compile(r"\baccurx\b", re.I), re.compile(r"\bflorey\.accurx\.com\b", re.I)],
    "econsult": [re.compile(r"\beconsult\b", re.I), re.compile(r"\be-consult\b", re.I)],
    "nhs_app": [re.compile(r"\bnhs app\b", re.I)],
}


APPOINTMENT_CONTEXT_PATTERNS = [
    re.compile(r"\bappointment\b", re.I),
    re.compile(r"\bbook(?:ing)?\b", re.I),
    re.compile(r"\brequest\b", re.I),
    re.compile(r"\bsubmit\b", re.I),
    re.compile(r"\brespond(?:ed|ing)?\b", re.I),
    re.compile(r"\bresponse\b", re.I),
    re.compile(r"\bcallback\b", re.I),
    re.compile(r"\bcall back\b", re.I),
    re.compile(r"\btelephone appointment\b", re.I),
    re.compile(r"\bsame day\b", re.I),
    re.compile(r"\bface to face\b", re.I),
    re.compile(r"\bf2f\b", re.I),
    re.compile(r"\boffer(?:ed|ing)?\b", re.I),
    re.compile(r"\binvited in\b", re.I),
    re.compile(r"\burgent\b", re.I),
    re.compile(r"\bsee (?:a|the|my)? ?doctor\b", re.I),
    re.compile(r"\bspeak to (?:a|the|my)? ?doctor\b", re.I),
    re.compile(r"\btriage\b", re.I),
]


NEGATIVE_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "online_only_gatekeeping": [
        re.compile(r"\btold to use\b.{0,50}\b(website|online|form|app|patchs|askmygp|econsult|accurx)\b", re.I),
        re.compile(r"\b(can'?t|couldn'?t) speak to anyone\b.{0,50}\b(website|online|form|app)\b", re.I),
        re.compile(r"\bmust\b.{0,30}\bdo it\b.{0,20}\bonline\b", re.I),
        re.compile(r"\b(go|use|do it) (on|via) the\b.{0,20}\b(website|site|app)\b", re.I),
    ],
    "form_closed_or_fills_up": [
        re.compile(r"\b(closed|shut|full|filled up|fills? up|offline|not open)\b.{0,40}\b(online|form|askmygp|patchs|website|app)\b", re.I),
        re.compile(r"\b(askmygp|patchs)\b.{0,30}\b(closed|full|offline)\b", re.I),
        re.compile(r"\bby 8(?::?00)?\b.{0,40}\b(full|filled|closed)\b", re.I),
        re.compile(r"\b(only opens?|open at)\b.{0,20}\b(6pm|8am|7:?30|10:?00)\b", re.I),
        re.compile(r"\bnot available throughout the day\b", re.I),
        re.compile(r"\bnot available at (night|nights|weekends?)\b", re.I),
        re.compile(r"\bavailable 24 hours\b", re.I),
        re.compile(r"\brequests? (are )?currently unavailable\b", re.I),
    ],
    "no_reply_or_lost_request": [
        re.compile(r"\bno response\b", re.I),
        re.compile(r"\bno record of submission\b", re.I),
        re.compile(r"\bnever heard back\b", re.I),
        re.compile(r"\bnot replied\b", re.I),
        re.compile(r"\bno callback\b", re.I),
        re.compile(r"\bsubmitted\b.{0,40}\bno reply\b", re.I),
        re.compile(r"\b(ignore it|ignored it|ignored my (form|request|e-?form|submission))\b", re.I),
    ],
    "usability_or_instruction_failure": [
        re.compile(r"\b(no instructions|hard to use|difficult to use|confusing|hard to find|struggle to locate|don't know how)\b", re.I),
        re.compile(r"\bhow to sign up\b", re.I),
        re.compile(r"\bwebsite not good\b", re.I),
        re.compile(r"\bunable to work the website\b", re.I),
        re.compile(r"\bworst website\b", re.I),
        re.compile(r"\bcouldn'?t find the relevant option\b", re.I),
        re.compile(r"\bpick a similar option\b", re.I),
        re.compile(r"\bcut me off as i was writing\b", re.I),
    ],
    "triage_burden_or_self_diagnosis": [
        re.compile(r"\bself diagnos\w*\b", re.I),
        re.compile(r"\btoo many questions\b", re.I),
        re.compile(r"\bai\b.{0,30}\basking\b", re.I),
        re.compile(r"\b20 mins? to complete\b", re.I),
        re.compile(r"\bfill in\b.{0,30}\bform\b.{0,40}\bappointment\b", re.I),
    ],
    "digital_exclusion_or_accessibility": [
        re.compile(r"\b(not everyone|older people|elderly|disabled|disability|learning disability)\b.{0,60}\b(online|website|app|form)\b", re.I),
        re.compile(r"\bnot good with computers\b", re.I),
        re.compile(r"\bno smartphone\b", re.I),
        re.compile(r"\bcan'?t use\b.{0,30}\b(website|app|online form)\b", re.I),
    ],
    "confusing_platform_setup": [
        re.compile(r"\bno longer used\b", re.I),
        re.compile(r"\bphone line says\b", re.I),
        re.compile(r"\bwebsite says\b", re.I),
        re.compile(r"\blinked to\b", re.I),
        re.compile(r"\bnot obvious\b", re.I),
        re.compile(r"\bonline consultation was abandoned\b", re.I),
        re.compile(r"\bstill have to fill in\b.{0,30}\be-?consult\b", re.I),
        re.compile(r"\bgo on (their )?e-?consult at 6pm\b", re.I),
    ],
}


POSITIVE_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "quick_response_or_same_day": [
        re.compile(r"\b(within|in)\b.{0,20}\b(20 minutes|30 minutes|few hours|same day)\b", re.I),
        re.compile(r"\bsame day appointment\b", re.I),
        re.compile(r"\bquick response\b", re.I),
        re.compile(r"\brespond(?:s|ed)? fast\b", re.I),
        re.compile(r"\bgot\b.{0,20}\bappointment\b.{0,20}\b(same day|quickly)\b", re.I),
        re.compile(r"\bcall(?:ed)? back\b.{0,20}\b(10 minutes|within|same day)\b", re.I),
        re.compile(r"\boffer(?:ed)?\b.{0,20}\b(face to face|same day appointment|appointment)\b", re.I),
        re.compile(r"\bseen\b.{0,20}\b(same day|that afternoon|this evening)\b", re.I),
    ],
    "easy_or_smooth_to_use": [
        re.compile(r"\bworks well\b", re.I),
        re.compile(r"\beasy to use\b", re.I),
        re.compile(r"\beasy to (book|get|request)\b", re.I),
        re.compile(r"\bstraightforward\b", re.I),
        re.compile(r"\buser friendly\b", re.I),
        re.compile(r"\bquick and easy\b", re.I),
        re.compile(r"\beasy and accessible website\b", re.I),
        re.compile(r"\bbooking system (is )?(easy|great)\b", re.I),
        re.compile(r"\bnever had (an )?issue booking (an )?appointment\b", re.I),
        re.compile(r"\bno problem getting an appointment\b", re.I),
    ],
    "named_platform_praise": [
        re.compile(r"\bexcellent\b.{0,30}\b(askmygp|patchs|online form|econsult|accurx)\b", re.I),
        re.compile(r"\b(askmygp|patchs|econsult|accurx)\b.{0,40}\b(great|good|excellent|easy|quick)\b", re.I),
        re.compile(r"\bcontacted gp via patchs\b", re.I),
        re.compile(r"\bsubmitted a triage form online\b", re.I),
        re.compile(r"\bsent online triage form\b", re.I),
        re.compile(r"\bonline triage\b.{0,30}\b(fast|efficient|great)\b", re.I),
        re.compile(r"\btriaged and invited in\b", re.I),
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
    return {key for key, group in patterns.items() if any(pattern.search(text) for pattern in group)}


def has_appointment_context(text: str) -> bool:
    return any(pattern.search(text) for pattern in APPOINTMENT_CONTEXT_PATTERNS)


def rank_score(positive: int, negative: int) -> float:
    strong = positive + negative
    if strong == 0:
        return 0.0
    return (positive - negative) / (strong + 2)


def evidence_weight(positive: int, negative: int) -> float:
    return math.log1p(positive + negative)


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

        corpus_positive = 0
        corpus_negative = 0
        corpus_mixed = 0
        corpus_relevant = 0

        practice_summary: dict[tuple[str, str], dict[str, object]] = defaultdict(
            lambda: {
                "review_ids": set(),
                "positive": 0,
                "negative": 0,
                "mixed": 0,
                "explicit_positive": 0,
                "explicit_negative": 0,
                "fallback_positive": 0,
                "fallback_negative": 0,
                "positive_tags": defaultdict(int),
                "negative_tags": defaultdict(int),
                "platforms": defaultdict(int),
                "positive_examples": [],
                "negative_examples": [],
                "mixed_examples": [],
            }
        )

        for row in rows:
            text = strip_practice_response(str(row["text"] or ""))
            if not text:
                continue

            platforms = match_keys(text, PLATFORM_PATTERNS)
            if not platforms:
                continue

            negative_tags = match_keys(text, NEGATIVE_PATTERNS)
            positive_tags = match_keys(text, POSITIVE_PATTERNS)
            appointment_context = has_appointment_context(text)

            if not appointment_context and not negative_tags and not positive_tags:
                continue

            if not appointment_context:
                # Do not include generic digital mentions unless the review explicitly reads
                # like appointment access or a strong digital praise/complaint pattern.
                if not (negative_tags or positive_tags):
                    continue

            stars = int(row["rating_stars"] or 0)
            explicit_positive = bool(positive_tags)
            explicit_negative = bool(negative_tags)

            if explicit_positive and explicit_negative:
                bucket = "mixed"
            elif explicit_positive:
                bucket = "mixed" if stars <= 2 else "positive"
            elif explicit_negative:
                bucket = "mixed" if stars >= 4 else "negative"
            elif stars >= 4:
                bucket = "positive"
            elif stars <= 2:
                bucket = "negative"
            else:
                bucket = "mixed"

            corpus_relevant += 1
            if bucket == "positive":
                corpus_positive += 1
            elif bucket == "negative":
                corpus_negative += 1
            else:
                corpus_mixed += 1

            practice_key = (str(row["canonical_code"]), str(row["practice_name"]))
            practice = practice_summary[practice_key]
            practice["review_ids"].add(int(row["id"]))
            practice[bucket] += 1
            if bucket == "positive":
                if explicit_positive:
                    practice["explicit_positive"] += 1
                else:
                    practice["fallback_positive"] += 1
            elif bucket == "negative":
                if explicit_negative:
                    practice["explicit_negative"] += 1
                else:
                    practice["fallback_negative"] += 1
            for platform in platforms:
                practice["platforms"][platform] += 1
            for tag in positive_tags:
                practice["positive_tags"][tag] += 1
            for tag in negative_tags:
                practice["negative_tags"][tag] += 1

            example = {
                "author": str(row["author"]),
                "date_raw": str(row["date_raw"]),
                "rating_stars": stars,
                "quote": snippet(text),
            }
            if bucket == "positive" and len(practice["positive_examples"]) < 3:
                practice["positive_examples"].append(example)
            if bucket == "negative" and len(practice["negative_examples"]) < 3:
                practice["negative_examples"].append(example)
            if bucket == "mixed" and len(practice["mixed_examples"]) < 2:
                practice["mixed_examples"].append(example)

        ranked = []
        for (code, name), item in practice_summary.items():
            total_practice_reviews = int(
                con.execute("SELECT COUNT(*) FROM reviews WHERE canonical_code = ?", (code,)).fetchone()[0] or 0
            )
            positive = int(item["positive"])
            negative = int(item["negative"])
            mixed = int(item["mixed"])
            strong = positive + negative
            if strong == 0:
                continue
            ranked.append(
                {
                    "canonical_code": code,
                    "practice_name": name,
                    "positive_digital_access_reviews": positive,
                    "negative_digital_access_reviews": negative,
                    "mixed_digital_access_reviews": mixed,
                    "explicit_positive_reviews": int(item["explicit_positive"]),
                    "explicit_negative_reviews": int(item["explicit_negative"]),
                    "fallback_positive_reviews": int(item["fallback_positive"]),
                    "fallback_negative_reviews": int(item["fallback_negative"]),
                    "strong_digital_access_reviews": strong,
                    "all_relevant_reviews": len(item["review_ids"]),
                    "share_of_all_reviews": round((len(item["review_ids"]) / total_practice_reviews) * 100, 1)
                    if total_practice_reviews
                    else 0.0,
                    "positive_share": round((positive / strong) * 100, 1) if strong else 0.0,
                    "net_score": round(rank_score(positive, negative), 4),
                    "evidence_weight": round(evidence_weight(positive, negative), 4),
                    "platforms": dict(sorted(item["platforms"].items(), key=lambda kv: (-kv[1], kv[0]))),
                    "positive_tags": dict(sorted(item["positive_tags"].items(), key=lambda kv: (-kv[1], kv[0]))),
                    "negative_tags": dict(sorted(item["negative_tags"].items(), key=lambda kv: (-kv[1], kv[0]))),
                    "positive_examples": list(item["positive_examples"]),
                    "negative_examples": list(item["negative_examples"]),
                    "mixed_examples": list(item["mixed_examples"]),
                }
            )

        top_ranked = sorted(
            ranked,
            key=lambda row: (
                -float(row["net_score"]),
                -int(row["strong_digital_access_reviews"]),
                -int(row["positive_digital_access_reviews"]),
                row["practice_name"],
            ),
        )
        bottom_ranked = sorted(
            ranked,
            key=lambda row: (
                float(row["net_score"]),
                -int(row["strong_digital_access_reviews"]),
                -int(row["negative_digital_access_reviews"]),
                row["practice_name"],
            ),
        )

        return {
            "total_reviews": len(rows),
            "relevant_review_count": corpus_relevant,
            "positive_review_count": corpus_positive,
            "negative_review_count": corpus_negative,
            "mixed_review_count": corpus_mixed,
            "practice_count": len(ranked),
            "top_50": top_ranked[:50],
            "bottom_50": bottom_ranked[:50],
        }
    finally:
        con.close()


def main() -> int:
    print(json.dumps(analyze(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
