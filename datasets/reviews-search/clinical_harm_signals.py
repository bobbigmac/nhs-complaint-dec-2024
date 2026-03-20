#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sqlite3
from collections import defaultdict
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "output" / "reviews_index.sqlite"


CATEGORY_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "misdiagnosis_or_wrong_diagnosis": [
        re.compile(r"\bmisdiagnos\w*\b", re.I),
        re.compile(r"\bwrong diagnos\w*\b", re.I),
        re.compile(r"\bdiagnosed\b.{0,40}\bturned out to be\b", re.I),
    ],
    "wrong_or_unsafe_medication": [
        re.compile(r"\bwrong medication\b", re.I),
        re.compile(r"\bwrong dose\b", re.I),
        re.compile(r"\bprescrib\w*\b.{0,25}\bwrong\b", re.I),
        re.compile(r"\bgiven\b.{0,25}\bwrong medication\b", re.I),
        re.compile(r"\bmedication\b.{0,30}\bmade me\b.{0,20}\b(very )?poorly\b", re.I),
    ],
    "negligence_or_danger_language": [
        re.compile(r"\bnegligen\w*\b", re.I),
        re.compile(r"\bcareless\b", re.I),
        re.compile(r"\bdangerous\b", re.I),
        re.compile(r"\bunsafe\b", re.I),
    ],
    "dismissed_or_not_listened_with_outcome": [
        re.compile(r"\b(ignore[sd]?|dismiss\w*|didn[’']?t listen|not listen\w*|wouldn[’']?t listen|sent me home)\b", re.I),
    ],
    "hospital_or_urgent_escalation": [
        re.compile(r"\bA\s*&\s*E\b", re.I),
        re.compile(r"\ba\+e\b", re.I),
        re.compile(r"\bambulance\b", re.I),
        re.compile(r"\b999\b"),
        re.compile(r"\bhospitali[sz]\w*\b", re.I),
        re.compile(r"\bended up in hospital\b", re.I),
        re.compile(r"\bended up in\b.{0,12}\bA\s*&\s*E\b", re.I),
    ],
    "severe_outcome_or_condition": [
        re.compile(r"\bnearly died\b", re.I),
        re.compile(r"\bcould have died\b", re.I),
        re.compile(r"\bdied\b", re.I),
        re.compile(r"\bsepsis\b", re.I),
        re.compile(r"\bappendicitis\b", re.I),
        re.compile(r"\bmeningitis\b", re.I),
        re.compile(r"\bcancer\b", re.I),
        re.compile(r"\bliver failure\b", re.I),
        re.compile(r"\bheart failure\b", re.I),
        re.compile(r"\bheart attack\b", re.I),
        re.compile(r"\bstroke\b", re.I),
        re.compile(r"\bpneumonia\b", re.I),
        re.compile(r"\brsv\b", re.I),
    ],
}


OUTCOME_CONTEXT_PATTERNS = [
    re.compile(r"\b(worsen\w*|worse|deteriorat\w*|collapsed|collapse|faint\w*|bleed\w*|infection|pain)\b", re.I),
]


CLINICAL_CONTEXT_PATTERNS = [
    re.compile(
        r"\b(doctor|gp|nurse|consultation|diagnos\w*|prescrib\w*|medication|treatment|symptom\w*|condition|infection|fever|pain|chest pain|appendicitis|cancer|meningitis|sepsis)\b",
        re.I,
    ),
]


OUTCOME_BUCKET_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "got_sicker_or_deteriorated": [
        re.compile(r"\b(got sicker|got worse|became worse|more unwell|deteriorat\w*|worsen\w*|collapsed|faint\w*)\b", re.I),
        re.compile(r"\b(resultantly|as a result)\b.{0,30}\b(worse|worsened|deteriorated)\b", re.I),
    ],
    "delayed_or_postponed_care_with_harm": [
        re.compile(r"\b(waited|waiting|delay\w*|delayed|postpon\w*|too late|for days|for weeks|for months)\b", re.I),
        re.compile(r"\b(couldn[’']?t get|unable to get|refused)\b.{0,40}\b(appointment|antibiotics|treatment|referral|test|scan)\b", re.I),
    ],
    "made_sicker_by_treatment_or_missed_treatment": [
        re.compile(r"\b(wrong medication|wrong dose|underprescrib\w*|overprescrib\w*)\b", re.I),
        re.compile(r"\b(made me|made my)\b.{0,30}\b(very )?poorly\b", re.I),
        re.compile(r"\b(reaction|side effect)\b", re.I),
    ],
    "hospital_or_emergency_escalation": [
        re.compile(r"\bA\s*&\s*E\b", re.I),
        re.compile(r"\ba\+e\b", re.I),
        re.compile(r"\bambulance\b", re.I),
        re.compile(r"\b999\b"),
        re.compile(r"\bhospitali[sz]\w*\b", re.I),
        re.compile(r"\bended up in hospital\b", re.I),
        re.compile(r"\bwent to (the )?hospital\b", re.I),
        re.compile(r"\blife support\b", re.I),
    ],
    "serious_condition_or_near_miss": [
        re.compile(r"\bnearly died\b", re.I),
        re.compile(r"\bcould have died\b", re.I),
        re.compile(r"\bwe nearly lost\b", re.I),
        re.compile(r"\blife support\b", re.I),
        re.compile(r"\bsepsis\b", re.I),
        re.compile(r"\bappendicitis\b", re.I),
        re.compile(r"\bmeningitis\b", re.I),
        re.compile(r"\bcancer\b", re.I),
        re.compile(r"\bliver failure\b", re.I),
        re.compile(r"\bheart failure\b", re.I),
        re.compile(r"\bheart attack\b", re.I),
        re.compile(r"\bstroke\b", re.I),
        re.compile(r"\bpneumonia\b", re.I),
        re.compile(r"\brsv\b", re.I),
        re.compile(r"\bemergency surgery\b", re.I),
        re.compile(r"\boperation\b", re.I),
    ],
}


def _strip_practice_response(text: str) -> str:
    return (text or "").split("Practice response date:")[0].strip()


def _snippet(text: str, *, max_chars: int = 260) -> str:
    value = " ".join((text or "").split())
    if len(value) <= max_chars:
        return value
    return value[: max_chars - 3].rstrip() + "..."


def _match_categories(text: str) -> set[str]:
    matches: set[str] = set()
    for category, patterns in CATEGORY_PATTERNS.items():
        if any(pattern.search(text) for pattern in patterns):
            matches.add(category)

    has_outcome_context = any(pattern.search(text) for pattern in OUTCOME_CONTEXT_PATTERNS)
    has_clinical_context = any(pattern.search(text) for pattern in CLINICAL_CONTEXT_PATTERNS)

    # Only keep dismissed/not-listened when there is a connected harm signal.
    if "dismissed_or_not_listened_with_outcome" in matches:
        if not (
            has_outcome_context
            or "hospital_or_urgent_escalation" in matches
            or "severe_outcome_or_condition" in matches
            or "misdiagnosis_or_wrong_diagnosis" in matches
        ):
            matches.discard("dismissed_or_not_listened_with_outcome")

    # Only keep hospital escalation when it sounds clinically connected.
    if "hospital_or_urgent_escalation" in matches:
        if not (
            has_clinical_context
            or "misdiagnosis_or_wrong_diagnosis" in matches
            or "wrong_or_unsafe_medication" in matches
            or "negligence_or_danger_language" in matches
            or "dismissed_or_not_listened_with_outcome" in matches
        ):
            matches.discard("hospital_or_urgent_escalation")

    # Severe outcome terms need some clinical or failure context too.
    if "severe_outcome_or_condition" in matches:
        if not (
            has_clinical_context
            or "misdiagnosis_or_wrong_diagnosis" in matches
            or "wrong_or_unsafe_medication" in matches
            or "negligence_or_danger_language" in matches
            or "dismissed_or_not_listened_with_outcome" in matches
            or "hospital_or_urgent_escalation" in matches
        ):
            matches.discard("severe_outcome_or_condition")
    return matches


def _match_outcomes(text: str, categories: set[str]) -> set[str]:
    outcomes: set[str] = set()
    has_clinical_context = any(pattern.search(text) for pattern in CLINICAL_CONTEXT_PATTERNS)

    if any(pattern.search(text) for pattern in OUTCOME_BUCKET_PATTERNS["got_sicker_or_deteriorated"]):
        outcomes.add("got_sicker_or_deteriorated")

    if any(pattern.search(text) for pattern in OUTCOME_BUCKET_PATTERNS["made_sicker_by_treatment_or_missed_treatment"]):
        if has_clinical_context or "wrong_or_unsafe_medication" in categories:
            outcomes.add("made_sicker_by_treatment_or_missed_treatment")

    if any(pattern.search(text) for pattern in OUTCOME_BUCKET_PATTERNS["hospital_or_emergency_escalation"]):
        if (
            has_clinical_context
            or "misdiagnosis_or_wrong_diagnosis" in categories
            or "wrong_or_unsafe_medication" in categories
            or "dismissed_or_not_listened_with_outcome" in categories
            or "negligence_or_danger_language" in categories
        ):
            outcomes.add("hospital_or_emergency_escalation")

    if any(pattern.search(text) for pattern in OUTCOME_BUCKET_PATTERNS["serious_condition_or_near_miss"]):
        if has_clinical_context or outcomes or categories:
            outcomes.add("serious_condition_or_near_miss")

    if any(pattern.search(text) for pattern in OUTCOME_BUCKET_PATTERNS["delayed_or_postponed_care_with_harm"]):
        if (
            "got_sicker_or_deteriorated" in outcomes
            or "hospital_or_emergency_escalation" in outcomes
            or "serious_condition_or_near_miss" in outcomes
            or "made_sicker_by_treatment_or_missed_treatment" in outcomes
            or "misdiagnosis_or_wrong_diagnosis" in categories
            or "wrong_or_unsafe_medication" in categories
            or "dismissed_or_not_listened_with_outcome" in categories
        ):
            outcomes.add("delayed_or_postponed_care_with_harm")

    return outcomes


def analyze(db_path: Path = DB_PATH) -> dict[str, object]:
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    try:
        rows = con.execute(
            """
            SELECT id, canonical_code, practice_name, rating_stars, author, date_raw, text
            FROM reviews
            WHERE rating_stars IN (1, 2)
            ORDER BY practice_name ASC, id ASC
            """
        ).fetchall()

        total_reviews = int(con.execute("SELECT COUNT(*) FROM reviews").fetchone()[0] or 0)
        low_star_reviews = int(con.execute("SELECT COUNT(*) FROM reviews WHERE rating_stars IN (1,2)").fetchone()[0] or 0)

        flagged_reviews: list[dict[str, object]] = []
        by_category: dict[str, dict[str, object]] = {
            category: {"count": 0, "examples": []} for category in CATEGORY_PATTERNS
        }
        by_outcome: dict[str, dict[str, object]] = {
            outcome: {"count": 0, "examples": []} for outcome in OUTCOME_BUCKET_PATTERNS
        }
        by_practice: dict[tuple[str, str], dict[str, object]] = defaultdict(
            lambda: {
                "review_ids": set(),
                "categories": defaultdict(int),
                "outcomes": defaultdict(int),
                "examples": [],
            }
        )

        for row in rows:
            text = _strip_practice_response(str(row["text"] or ""))
            if not text:
                continue
            categories = _match_categories(text)
            if not categories:
                continue
            outcomes = _match_outcomes(text, categories)

            review_id = int(row["id"])
            practice_key = (str(row["canonical_code"]), str(row["practice_name"]))
            item = {
                "review_id": review_id,
                "canonical_code": practice_key[0],
                "practice_name": practice_key[1],
                "rating_stars": int(row["rating_stars"] or 0),
                "author": str(row["author"]),
                "date_raw": str(row["date_raw"]),
                "categories": sorted(categories),
                "outcomes": sorted(outcomes),
                "text": text,
            }
            flagged_reviews.append(item)

            practice_info = by_practice[practice_key]
            practice_info["review_ids"].add(review_id)
            if len(practice_info["examples"]) < 4:
                practice_info["examples"].append(_snippet(text))
            for category in categories:
                practice_info["categories"][category] += 1
                cat = by_category[category]
                cat["count"] = int(cat["count"]) + 1
                if len(cat["examples"]) < 5:
                    cat["examples"].append(
                        {
                            "practice_name": practice_key[1],
                            "canonical_code": practice_key[0],
                            "quote": _snippet(text),
                        }
                    )
            for outcome in outcomes:
                practice_info["outcomes"][outcome] += 1
                bucket = by_outcome[outcome]
                bucket["count"] = int(bucket["count"]) + 1
                if len(bucket["examples"]) < 6:
                    bucket["examples"].append(
                        {
                            "practice_name": practice_key[1],
                            "canonical_code": practice_key[0],
                            "quote": _snippet(text),
                        }
                    )

        practice_rows = []
        for (code, name), info in by_practice.items():
            review_count = len(info["review_ids"])
            total_practice_reviews = int(
                con.execute("SELECT COUNT(*) FROM reviews WHERE canonical_code = ?", (code,)).fetchone()[0] or 0
            )
            practice_rows.append(
                {
                    "canonical_code": code,
                    "practice_name": name,
                    "signal_review_count": review_count,
                    "signal_share_of_all_reviews": round((review_count / total_practice_reviews) * 100, 1)
                    if total_practice_reviews
                    else 0.0,
                    "total_reviews": total_practice_reviews,
                    "categories": dict(sorted(info["categories"].items(), key=lambda item: (-item[1], item[0]))),
                    "outcomes": dict(sorted(info["outcomes"].items(), key=lambda item: (-item[1], item[0]))),
                    "examples": info["examples"],
                }
            )

        practice_rows.sort(
            key=lambda item: (
                -int(item["signal_review_count"]),
                -float(item["signal_share_of_all_reviews"]),
                item["practice_name"],
            )
        )

        return {
            "total_reviews": total_reviews,
            "low_star_reviews": low_star_reviews,
            "flagged_review_count": len(flagged_reviews),
            "flagged_review_share_of_all_reviews": round((len(flagged_reviews) / total_reviews) * 100, 1)
            if total_reviews
            else 0.0,
            "flagged_review_share_of_low_star_reviews": round((len(flagged_reviews) / low_star_reviews) * 100, 1)
            if low_star_reviews
            else 0.0,
            "categories": by_category,
            "outcomes": by_outcome,
            "top_practices": practice_rows[:20],
        }
    finally:
        con.close()


def main() -> int:
    print(json.dumps(analyze(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
