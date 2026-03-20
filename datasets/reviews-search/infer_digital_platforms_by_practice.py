#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
from collections import Counter
from pathlib import Path

from rank_digital_appointment_practices import (
    DB_PATH,
    NEGATIVE_PATTERNS,
    PLATFORM_PATTERNS,
    POSITIVE_PATTERNS,
    has_appointment_context,
    match_keys,
    strip_practice_response,
)


NAMED_PLATFORMS = ("askmygp", "patchs", "econsult", "accurx", "nhs_app")


def classify_bucket(rating_stars: int, positive_tags: set[str], negative_tags: set[str]) -> str:
    explicit_positive = bool(positive_tags)
    explicit_negative = bool(negative_tags)
    if explicit_positive and explicit_negative:
        return "mixed"
    if explicit_positive:
        return "mixed" if rating_stars <= 2 else "positive"
    if explicit_negative:
        return "mixed" if rating_stars >= 4 else "negative"
    if rating_stars >= 4:
        return "positive"
    if rating_stars <= 2:
        return "negative"
    return "mixed"


def analyze(db_path: Path = DB_PATH) -> dict[str, object]:
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    try:
        practices: dict[str, dict[str, object]] = {}

        for row in con.execute(
            """
            SELECT canonical_code, practice_name, rating_stars, text
            FROM reviews
            ORDER BY canonical_code, id
            """
        ):
            text = strip_practice_response(str(row["text"] or ""))
            if not text:
                continue

            platforms = match_keys(text, PLATFORM_PATTERNS)
            if not platforms:
                continue

            positive_tags = match_keys(text, POSITIVE_PATTERNS)
            negative_tags = match_keys(text, NEGATIVE_PATTERNS)
            appointment_context = has_appointment_context(text)
            if not appointment_context and not positive_tags and not negative_tags:
                continue
            if not appointment_context and not (positive_tags or negative_tags):
                continue

            code = str(row["canonical_code"])
            item = practices.setdefault(
                code,
                {
                    "canonical_code": code,
                    "practice_name": str(row["practice_name"]),
                    "positive": 0,
                    "negative": 0,
                    "mixed": 0,
                    "named_platforms": set(),
                    "named_platform_counts": Counter(),
                    "all_platform_counts": Counter(),
                },
            )

            bucket = classify_bucket(int(row["rating_stars"] or 0), positive_tags, negative_tags)
            item[bucket] += 1
            for platform in platforms:
                item["all_platform_counts"][platform] += 1
                if platform in NAMED_PLATFORMS:
                    item["named_platforms"].add(platform)
                    item["named_platform_counts"][platform] += 1

        practice_list: list[dict[str, object]] = []
        combo_distribution: Counter[str] = Counter()
        known_count = 0
        unknown_count = 0
        multi_count = 0

        for item in practices.values():
            named_platforms = sorted(item["named_platforms"])
            if named_platforms:
                known_count += 1
                if len(named_platforms) > 1:
                    multi_count += 1
            else:
                unknown_count += 1

            combo_distribution["unknown_only" if not named_platforms else "+".join(named_platforms)] += 1

            practice_list.append(
                {
                    "canonical_code": item["canonical_code"],
                    "practice_name": item["practice_name"],
                    "positive_reviews": int(item["positive"]),
                    "negative_reviews": int(item["negative"]),
                    "mixed_reviews": int(item["mixed"]),
                    "named_platforms": named_platforms,
                    "named_platform_counts": dict(item["named_platform_counts"]),
                    "all_platform_counts": dict(item["all_platform_counts"]),
                }
            )

        practice_list.sort(key=lambda row: row["practice_name"])

        system_summary: list[dict[str, object]] = []
        for system in NAMED_PLATFORMS:
            using_any = [row for row in practice_list if system in row["named_platforms"]]
            using_single = [row for row in practice_list if row["named_platforms"] == [system]]
            if not using_any:
                continue

            def rollup(rows: list[dict[str, object]]) -> tuple[int, int, int, float, float]:
                positive = sum(int(row["positive_reviews"]) for row in rows)
                negative = sum(int(row["negative_reviews"]) for row in rows)
                mixed = sum(int(row["mixed_reviews"]) for row in rows)
                strong = positive + negative
                weighted_positive_share = round((positive / strong) * 100, 1) if strong else 0.0
                mean_positive_share = round(
                    sum(
                        (
                            int(row["positive_reviews"]) / (int(row["positive_reviews"]) + int(row["negative_reviews"]))
                            if (int(row["positive_reviews"]) + int(row["negative_reviews"]))
                            else 0.0
                        )
                        for row in rows
                    )
                    / len(rows)
                    * 100,
                    1,
                )
                return positive, negative, mixed, weighted_positive_share, mean_positive_share

            any_positive, any_negative, any_mixed, any_weighted, any_mean = rollup(using_any)
            single_positive, single_negative, single_mixed, single_weighted, single_mean = rollup(using_single) if using_single else (0, 0, 0, 0.0, 0.0)

            system_summary.append(
                {
                    "system": system,
                    "practice_count_any": len(using_any),
                    "practice_count_single_only": len(using_single),
                    "any_positive_reviews": any_positive,
                    "any_negative_reviews": any_negative,
                    "any_mixed_reviews": any_mixed,
                    "any_weighted_positive_share": any_weighted,
                    "any_mean_practice_positive_share": any_mean,
                    "single_positive_reviews": single_positive,
                    "single_negative_reviews": single_negative,
                    "single_mixed_reviews": single_mixed,
                    "single_weighted_positive_share": single_weighted,
                    "single_mean_practice_positive_share": single_mean,
                }
            )

        return {
            "practice_count_with_any_digital_signal": len(practice_list),
            "practice_count_known_named_platform": known_count,
            "practice_count_unknown_only": unknown_count,
            "practice_count_multiple_named_platforms": multi_count,
            "combo_distribution": dict(sorted(combo_distribution.items(), key=lambda kv: (-kv[1], kv[0]))),
            "systems": system_summary,
            "practices": practice_list,
        }
    finally:
        con.close()


def main() -> int:
    print(json.dumps(analyze(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
