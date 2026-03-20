#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sqlite3
from collections import defaultdict
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "output" / "reviews_index.sqlite"


CATEGORY_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "regulator_or_formal_escalation": [
        re.compile(r"\b(cqc|icb|pals|ombudsman|nhs england|ico|gmc|mp)\b", re.I),
        re.compile(r"\b(formal complaint|official complaint|complaint to|reported to|reporting to|emailed to raise a complaint)\b", re.I),
        re.compile(r"\b(take( it)? to court|legal action|solicitor)\b", re.I),
    ],
    "call_to_action_or_public_warning": [
        re.compile(r"\b(register elsewhere|de-register|deregister|avoid( this place)?|stay away|should be shut down|shut down)\b", re.I),
        re.compile(r"\bsubmit your review\b", re.I),
        re.compile(r"\bwe need to\b", re.I),
        re.compile(r"\bstrongly advise\b", re.I),
    ],
    "reviews_about_reviews_or_public_record": [
        re.compile(r"\b(other reviews|negative reviews|reading the reviews|in the reviews|all the reviews|these reviews)\b", re.I),
        re.compile(r"\bI never ever write reviews\b", re.I),
        re.compile(r"\bI am writing this review\b", re.I),
        re.compile(r"\bdissenting voice\b", re.I),
        re.compile(r"\bnot only me who thinks this\b", re.I),
    ],
    "authority_or_witness_positioning": [
        re.compile(r"\bas (both )?(a )?(medical doctor|doctor|healthcare professional|gp receptionist)\b", re.I),
        re.compile(r"\bI work (for|as)\b.{0,30}\b(ombudsman|nhs|gp receptionist|healthcare)\b", re.I),
        re.compile(r"\bbeing a prescriber myself\b", re.I),
        re.compile(r"\bmedical negligence\b", re.I),
    ],
    "community_or_collective_framing": [
        re.compile(r"\bcommunity\b", re.I),
        re.compile(r"\bpatients?\b.{0,40}\b(need|deserve|deserves|served|support|safety)\b", re.I),
        re.compile(r"\btaxpayers?\b", re.I),
        re.compile(r"\bNHS principles\b", re.I),
        re.compile(r"\bpublic\b.{0,30}\b(review|feedback|safety)\b", re.I),
        re.compile(r"\bserv(e|ing)\b.{0,20}\bcommunit", re.I),
    ],
}


def strip_practice_response(text: str) -> str:
    return (text or "").split("Practice response date:")[0].strip()


def clean_text(text: str) -> str:
    return " ".join((text or "").split())


def snippet(text: str, max_chars: int = 300) -> str:
    value = clean_text(text)
    if len(value) <= max_chars:
        return value
    return value[: max_chars - 3].rstrip() + "..."


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
        flagged = []
        by_category = {
            name: {"count": 0, "positive": 0, "negative": 0, "mixed": 0, "examples": [], "practices": defaultdict(int)}
            for name in CATEGORY_PATTERNS
        }
        by_practice: dict[tuple[str, str], dict[str, object]] = defaultdict(
            lambda: {
                "review_ids": set(),
                "categories": defaultdict(int),
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
            matches = {
                name
                for name, patterns in CATEGORY_PATTERNS.items()
                if any(pattern.search(text) for pattern in patterns)
            }
            if not matches:
                continue

            stars = int(row["rating_stars"] or 0)
            bucket = "mixed"
            if stars >= 4:
                bucket = "positive"
            elif stars <= 2:
                bucket = "negative"

            item = {
                "id": int(row["id"]),
                "practice_name": str(row["practice_name"]),
                "canonical_code": str(row["canonical_code"]),
                "author": str(row["author"]),
                "date_raw": str(row["date_raw"]),
                "rating_stars": stars,
                "categories": sorted(matches),
                "quote": snippet(text),
            }
            flagged.append(item)

            practice_key = (str(row["canonical_code"]), str(row["practice_name"]))
            practice = by_practice[practice_key]
            practice["review_ids"].add(item["id"])
            practice[bucket] += 1
            if len(practice["examples"]) < 4:
                practice["examples"].append(item["quote"])

            for name in matches:
                summary = by_category[name]
                summary["count"] += 1
                summary[bucket] += 1
                summary["practices"][practice_key[1]] += 1
                if len(summary["examples"]) < 6:
                    summary["examples"].append(
                        {
                            "practice_name": practice_key[1],
                            "author": item["author"],
                            "date_raw": item["date_raw"],
                            "rating_stars": stars,
                            "quote": item["quote"],
                        }
                    )
                practice["categories"][name] += 1

        practices = []
        for (code, name), item in by_practice.items():
            total_practice_reviews = int(
                con.execute("SELECT COUNT(*) FROM reviews WHERE canonical_code = ?", (code,)).fetchone()[0] or 0
            )
            practices.append(
                {
                    "canonical_code": code,
                    "practice_name": name,
                    "flagged_review_count": len(item["review_ids"]),
                    "flagged_share_of_all_reviews": round((len(item["review_ids"]) / total_practice_reviews) * 100, 1)
                    if total_practice_reviews
                    else 0.0,
                    "positive": int(item["positive"]),
                    "negative": int(item["negative"]),
                    "mixed": int(item["mixed"]),
                    "categories": dict(sorted(item["categories"].items(), key=lambda kv: (-kv[1], kv[0]))),
                    "examples": list(item["examples"]),
                }
            )
        practices.sort(key=lambda r: (-r["flagged_review_count"], -r["flagged_share_of_all_reviews"], r["practice_name"]))

        for item in by_category.values():
            item["top_practices"] = sorted(item["practices"].items(), key=lambda kv: (-kv[1], kv[0]))[:10]
            del item["practices"]

        return {
            "total_reviews": total_reviews,
            "flagged_review_count": len(flagged),
            "flagged_share_of_all_reviews": round((len(flagged) / total_reviews) * 100, 1) if total_reviews else 0.0,
            "categories": by_category,
            "top_practices": practices[:20],
        }
    finally:
        con.close()


def main() -> int:
    print(json.dumps(analyze(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
