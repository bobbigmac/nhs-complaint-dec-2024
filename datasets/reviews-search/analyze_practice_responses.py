#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "output" / "reviews_index.sqlite"


RESPONSE_SPLIT_RE = re.compile(
    r"Practice response date:\s*(?P<date>.*?)\s*Practice response:\s*(?P<response>.*)$",
    re.IGNORECASE | re.DOTALL,
)

MONTH_PATTERNS: list[tuple[re.Pattern[str], int]] = [
    (re.compile(r"\bjust now\b", re.I), 0),
    (re.compile(r"\ba month ago\b", re.I), 1),
    (re.compile(r"\b(\d+)\s+months?\s+ago\b", re.I), -1),
    (re.compile(r"\ba year ago\b", re.I), 12),
    (re.compile(r"\b(\d+)\s+years?\s+ago\b", re.I), -12),
    (re.compile(r"\ba week ago\b", re.I), 0),
    (re.compile(r"\b(\d+)\s+weeks?\s+ago\b", re.I), 0),
    (re.compile(r"\ba day ago\b", re.I), 0),
    (re.compile(r"\b(\d+)\s+days?\s+ago\b", re.I), 0),
    (re.compile(r"\ban hour ago\b", re.I), 0),
    (re.compile(r"\b(\d+)\s+hours?\s+ago\b", re.I), 0),
]

BOILERPLATE_PATTERNS = [
    re.compile(r"\bcontact (the )?(practice|surgery|reception|front desk|practice manager|complaints team)\b", re.I),
    re.compile(r"\bplease contact us\b", re.I),
    re.compile(r"\bcall (the )?(practice|surgery|reception)\b", re.I),
    re.compile(r"\bvisit (our )?website\b", re.I),
    re.compile(r"\buse (our )?(website|online form|patchs|askmygp|econsult)\b", re.I),
    re.compile(r"\bspeak to reception\b", re.I),
    re.compile(r"\bget in touch\b", re.I),
]

POSITIVE_THANKS_PATTERNS = [
    re.compile(r"\bthank you\b", re.I),
    re.compile(r"\bglad\b", re.I),
    re.compile(r"\bpleased\b", re.I),
    re.compile(r"\bappreciate\b", re.I),
]

SPECIFIC_ACTION_PATTERNS = [
    re.compile(r"\bwe (have )?(reviewed|review|investigated|looked into|discussed|shared)\b", re.I),
    re.compile(r"\bwe (have )?(changed|updated|improved|introduced|trained|spoken to|reminded)\b", re.I),
    re.compile(r"\bthis has been (fed back|raised|escalated)\b", re.I),
    re.compile(r"\bour (system|process|website|phone lines?) (has|have) been\b", re.I),
    re.compile(r"\bappointment(s)? (has|have) been\b", re.I),
]

PATIENT_BLAME_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "attendance_or_lateness": [
        re.compile(r"\b(did not attend|dna|late for (your|the) appointment|arrived late|missed (your|the) appointment)\b", re.I),
    ],
    "wrong_route_or_process": [
        re.compile(r"\b(you need to|you must|you should have|please use)\b.{0,50}\b(website|online|form|app|111|reception|front desk|econsult|patchs|askmygp)\b", re.I),
        re.compile(r"\bfollow(ing)? our process\b", re.I),
    ],
    "eligibility_or_policy": [
        re.compile(r"\b(out of catchment|outside our catchment|not in our catchment|not eligible|in line with policy|practice policy)\b", re.I),
        re.compile(r"\bour policy is\b", re.I),
    ],
    "records_based_denial": [
        re.compile(r"\bour records (show|indicate|confirm)\b", re.I),
        re.compile(r"\bafter reviewing your records\b", re.I),
        re.compile(r"\bthis is not an accurate reflection\b", re.I),
    ],
    "capacity_defence": [
        re.compile(r"\b(high demand|unprecedented demand|understaffed|limited appointments|huge catchment area)\b", re.I),
    ],
}


def clean_text(value: str) -> str:
    return " ".join((value or "").replace("\u00a0", " ").split())


def estimate_months_ago(raw: str) -> int | None:
    text = clean_text(raw)
    for pattern, multiplier in MONTH_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        if multiplier >= 0:
            return multiplier
        return int(match.group(1)) * abs(multiplier)
    return None


def extract_response(text: str) -> tuple[str, str] | None:
    match = RESPONSE_SPLIT_RE.search(text or "")
    if not match:
        return None
    response = clean_text(match.group("response"))
    if not response:
        return None
    return clean_text(match.group("date")), response


def rating_bucket(stars: int) -> str:
    if stars >= 4:
        return "positive"
    if stars <= 2:
        return "negative"
    return "mixed"


def classify_response(review_stars: int, response_text: str) -> dict[str, object]:
    text = clean_text(response_text)
    words = len(text.split())
    categories: set[str] = set()
    blame_modes: set[str] = set()

    if any(pattern.search(text) for pattern in BOILERPLATE_PATTERNS):
        categories.add("boilerplate_signpost")
    if any(pattern.search(text) for pattern in SPECIFIC_ACTION_PATTERNS):
        categories.add("specific_action")
    if any(pattern.search(text) for pattern in POSITIVE_THANKS_PATTERNS):
        categories.add("thanks_or_praise")
    if re.search(r"\b(apolog(y|ise|ize|etic|ise for|ize for)|sorry)\b", text, re.I):
        categories.add("apology")
    if re.search(r"\b(confidentiality|cannot discuss publicly|can't discuss publicly|private details)\b", text, re.I):
        categories.add("privacy_defence")

    for mode, patterns in PATIENT_BLAME_PATTERNS.items():
        if any(pattern.search(text) for pattern in patterns):
            blame_modes.add(mode)
    if blame_modes:
        categories.add("patient_blaming_or_deflecting")

    useful_negative = (
        review_stars <= 2
        and "specific_action" in categories
        and "boilerplate_signpost" not in categories
        and "patient_blaming_or_deflecting" not in categories
    )
    bad_negative = (
        review_stars <= 2
        and (
            "patient_blaming_or_deflecting" in categories
            or ("boilerplate_signpost" in categories and "specific_action" not in categories)
        )
    )
    useful_positive = review_stars >= 4 and words >= 8 and "thanks_or_praise" in categories

    return {
        "word_count": words,
        "categories": sorted(categories),
        "blame_modes": sorted(blame_modes),
        "useful_negative": useful_negative,
        "bad_negative": bad_negative,
        "useful_positive": useful_positive,
    }


def analyze(db_path: Path = DB_PATH) -> dict[str, object]:
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    try:
        rows = con.execute(
            """
            SELECT canonical_code, practice_name, rating_stars, date_raw, estimated_months_ago, text
            FROM reviews
            ORDER BY canonical_code, practice_name, rating_stars
            """
        ).fetchall()

        total_reviews = len(rows)
        response_rows = []
        by_practice: dict[tuple[str, str], dict[str, object]] = defaultdict(
            lambda: {
                "review_count": 0,
                "response_count": 0,
                "negative_review_count": 0,
                "negative_response_count": 0,
                "positive_review_count": 0,
                "positive_response_count": 0,
                "mixed_review_count": 0,
                "mixed_response_count": 0,
                "useful_negative": 0,
                "bad_negative": 0,
                "useful_positive": 0,
                "boilerplate": 0,
                "negative_boilerplate": 0,
                "specific_action": 0,
                "negative_specific_action": 0,
                "patient_blaming": 0,
                "negative_patient_blaming": 0,
                "blame_modes": Counter(),
                "response_word_total": 0,
                "response_delay_values": [],
                "examples": defaultdict(list),
            }
        )

        summary = {
            "total_reviews": total_reviews,
            "response_count": 0,
            "positive_reviews": 0,
            "positive_responses": 0,
            "negative_reviews": 0,
            "negative_responses": 0,
            "mixed_reviews": 0,
            "mixed_responses": 0,
        }
        blame_counts = Counter()
        category_counts = Counter()

        for row in rows:
            stars = int(row["rating_stars"] or 0)
            bucket = rating_bucket(stars)
            practice_key = (str(row["canonical_code"]), str(row["practice_name"]))
            practice = by_practice[practice_key]
            practice["review_count"] += 1
            summary[f"{bucket}_reviews"] += 1
            practice[f"{bucket}_review_count"] += 1

            response = extract_response(str(row["text"] or ""))
            if not response:
                continue
            response_date_raw, response_text = response
            classification = classify_response(stars, response_text)
            response_months = estimate_months_ago(response_date_raw)
            review_months = row["estimated_months_ago"]
            delay = None
            if isinstance(review_months, int) and isinstance(response_months, int):
                delay = max(review_months - response_months, 0)

            summary["response_count"] += 1
            summary[f"{bucket}_responses"] += 1
            practice["response_count"] += 1
            practice[f"{bucket}_response_count"] += 1
            practice["response_word_total"] += int(classification["word_count"])
            if delay is not None:
                practice["response_delay_values"].append(delay)

            categories = classification["categories"]
            blame_modes = classification["blame_modes"]
            for category in categories:
                category_counts[category] += 1
            for mode in blame_modes:
                blame_counts[mode] += 1
                practice["blame_modes"][mode] += 1

            if "boilerplate_signpost" in categories:
                practice["boilerplate"] += 1
                if bucket == "negative":
                    practice["negative_boilerplate"] += 1
            if "specific_action" in categories:
                practice["specific_action"] += 1
                if bucket == "negative":
                    practice["negative_specific_action"] += 1
            if "patient_blaming_or_deflecting" in categories:
                practice["patient_blaming"] += 1
                if bucket == "negative":
                    practice["negative_patient_blaming"] += 1

            if classification["useful_negative"]:
                practice["useful_negative"] += 1
                if len(practice["examples"]["useful_negative"]) < 3:
                    practice["examples"]["useful_negative"].append(response_text)
            if classification["bad_negative"]:
                practice["bad_negative"] += 1
                if len(practice["examples"]["bad_negative"]) < 3:
                    practice["examples"]["bad_negative"].append(response_text)
            if classification["useful_positive"]:
                practice["useful_positive"] += 1
                if len(practice["examples"]["useful_positive"]) < 3:
                    practice["examples"]["useful_positive"].append(response_text)
            if "patient_blaming_or_deflecting" in categories and len(practice["examples"]["patient_blaming"]) < 3:
                practice["examples"]["patient_blaming"].append(response_text)
            if "boilerplate_signpost" in categories and len(practice["examples"]["boilerplate"]) < 3:
                practice["examples"]["boilerplate"].append(response_text)

            response_rows.append(
                {
                    "practice_name": practice_key[1],
                    "canonical_code": practice_key[0],
                    "review_stars": stars,
                    "review_bucket": bucket,
                    "response_date_raw": response_date_raw,
                    "response_delay_months": delay,
                    "response_text": response_text,
                    **classification,
                }
            )

        practice_rows = []
        for (code, name), practice in by_practice.items():
            response_count = int(practice["response_count"])
            negative_response_count = int(practice["negative_response_count"])
            positive_response_count = int(practice["positive_response_count"])
            avg_words = round(practice["response_word_total"] / response_count, 1) if response_count else 0.0
            avg_delay = (
                round(sum(practice["response_delay_values"]) / len(practice["response_delay_values"]), 1)
                if practice["response_delay_values"]
                else None
            )
            practice_rows.append(
                {
                    "canonical_code": code,
                    "practice_name": name,
                    "review_count": int(practice["review_count"]),
                    "response_count": response_count,
                    "response_rate": round((response_count / int(practice["review_count"])) * 100, 1)
                    if practice["review_count"]
                    else 0.0,
                    "negative_review_count": int(practice["negative_review_count"]),
                    "negative_response_count": negative_response_count,
                    "negative_response_rate": round((negative_response_count / int(practice["negative_review_count"])) * 100, 1)
                    if practice["negative_review_count"]
                    else 0.0,
                    "positive_review_count": int(practice["positive_review_count"]),
                    "positive_response_count": positive_response_count,
                    "positive_response_rate": round((positive_response_count / int(practice["positive_review_count"])) * 100, 1)
                    if practice["positive_review_count"]
                    else 0.0,
                    "mixed_review_count": int(practice["mixed_review_count"]),
                    "mixed_response_count": int(practice["mixed_response_count"]),
                    "useful_negative": int(practice["useful_negative"]),
                    "bad_negative": int(practice["bad_negative"]),
                    "useful_positive": int(practice["useful_positive"]),
                    "boilerplate": int(practice["boilerplate"]),
                    "negative_boilerplate": int(practice["negative_boilerplate"]),
                    "specific_action": int(practice["specific_action"]),
                    "negative_specific_action": int(practice["negative_specific_action"]),
                    "patient_blaming": int(practice["patient_blaming"]),
                    "negative_patient_blaming": int(practice["negative_patient_blaming"]),
                    "avg_response_words": avg_words,
                    "avg_response_delay_months": avg_delay,
                    "blame_modes": dict(practice["blame_modes"]),
                    "examples": {key: list(values) for key, values in practice["examples"].items()},
                }
            )

        practice_rows.sort(key=lambda item: (-item["response_count"], item["practice_name"]))

        return {
            "summary": {
                **summary,
                "response_rate": round((summary["response_count"] / total_reviews) * 100, 1) if total_reviews else 0.0,
                "positive_response_rate": round((summary["positive_responses"] / summary["positive_reviews"]) * 100, 1)
                if summary["positive_reviews"]
                else 0.0,
                "negative_response_rate": round((summary["negative_responses"] / summary["negative_reviews"]) * 100, 1)
                if summary["negative_reviews"]
                else 0.0,
                "mixed_response_rate": round((summary["mixed_responses"] / summary["mixed_reviews"]) * 100, 1)
                if summary["mixed_reviews"]
                else 0.0,
            },
            "category_counts": dict(category_counts),
            "patient_blaming_modes": dict(blame_counts),
            "practices": practice_rows,
            "sample_responses": response_rows[:200],
        }
    finally:
        con.close()


def main() -> int:
    print(json.dumps(analyze(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
