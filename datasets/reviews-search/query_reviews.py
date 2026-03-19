#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from review_search_lib import (
    DEFAULT_DB_PATH,
    corpus_stats,
    grounded_report,
    load_review_context,
    search_reviews,
)


def add_common_filters(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--db", default=str(DEFAULT_DB_PATH), help="SQLite database path.")
    parser.add_argument("--practice", default="", help="Filter by canonical code or practice name.")
    parser.add_argument("--min-rating", type=int, default=None, help="Minimum star rating filter.")
    parser.add_argument("--max-rating", type=int, default=None, help="Maximum star rating filter.")
    parser.add_argument("--gtd-only", action="store_true", help="Only include GTD-managed practices.")
    parser.add_argument("--non-gtd-only", action="store_true", help="Only include non-GTD practices.")
    parser.add_argument("--phrase", action="store_true", help="Prefer exact-phrase matching first.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query the local practice reviews fulltext index.")
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    search_parser = subparsers.add_parser("search", help="Search for relevant reviews and exact quotes.")
    add_common_filters(search_parser)
    search_parser.add_argument("--q", required=True, help="Free-text query.")
    search_parser.add_argument("--limit", type=int, default=12, help="Max reviews to return.")
    search_parser.add_argument("--candidates", type=int, default=200, help="FTS candidates before reranking.")

    context_parser = subparsers.add_parser("context", help="Show nearby reviews from the same practice.")
    context_parser.add_argument("--db", default=str(DEFAULT_DB_PATH), help="SQLite database path.")
    context_parser.add_argument("--id", type=int, required=True, help="Review id from search results.")
    context_parser.add_argument("--before", type=int, default=1, help="Reviews before the selected review.")
    context_parser.add_argument("--after", type=int, default=1, help="Reviews after the selected review.")
    context_parser.add_argument("--json", action="store_true", help="Emit JSON.")

    stats_parser = subparsers.add_parser("stats", help="Aggregate counts for the full corpus or a query slice.")
    add_common_filters(stats_parser)
    stats_parser.add_argument("--q", default="", help="Optional query to restrict the stats.")
    stats_parser.add_argument("--max-matches", type=int, default=10000, help="Max matched reviews to aggregate.")

    report_parser = subparsers.add_parser("report", help="Print a grounded human-friendly answer with quotes and counts.")
    add_common_filters(report_parser)
    report_parser.add_argument("--q", required=True, help="Free-text query.")
    report_parser.add_argument("--limit", type=int, default=8, help="Max top matches to inspect.")
    report_parser.add_argument("--candidates", type=int, default=300, help="FTS candidates before reranking.")

    return parser.parse_args()


def print_search_text(payload: dict[str, object]) -> None:
    if payload.get("error"):
        print(f'Error: {payload.get("error")}')
        return
    print(f'Query: {payload.get("query")}')
    print(f'FTS:   {payload.get("fts")}')
    print()
    results = payload.get("results") or []
    if not results:
        print("No matches.")
        return
    for index, result in enumerate(results, 1):
        item = dict(result)
        print(
            f'{index:>2}. id={item.get("review_id")} score={float(item.get("score") or 0.0):.3f} '
            f'[{item.get("rating_stars")}*] {item.get("practice_name")} ({item.get("canonical_code")})'
        )
        print(f'    {item.get("author")} | {item.get("date_raw")}')
        if item.get("quote"):
            print(f'    Quote: "{item.get("quote")}"')
        print(f'    Snip:  {item.get("snippet")}')
        print()


def print_context_text(payload: dict[str, object]) -> None:
    if payload.get("error"):
        print(f'Error: {payload.get("error")}')
        return
    print(f'{payload.get("practice_name")} ({payload.get("canonical_code")})')
    print(f'Source: {payload.get("source_file")}')
    print()
    for item in payload.get("context") or []:
        review = dict(item)
        marker = ">" if int(review.get("review_id") or 0) == int(payload.get("review_id") or 0) else " "
        print(
            f'{marker} id={review.get("review_id")} order={review.get("review_order")} '
            f'[{review.get("rating_stars")}*] {review.get("author")} | {review.get("date_raw")}'
        )
        print(f'  {review.get("text")}')
        print()


def print_stats_text(payload: dict[str, object]) -> None:
    if payload.get("error"):
        print(f'Error: {payload.get("error")}')
        return
    query = str(payload.get("query") or "").strip()
    if query:
        print(f'Query: {query}')
        print(f'FTS:   {payload.get("fts")}')
    else:
        print("Query: <entire corpus>")
    print(f'Matches:  {payload.get("review_count")} reviews across {payload.get("practice_count")} practices')
    print(f'Average:  {payload.get("avg_rating")} stars')
    print(f'GTD:      {payload.get("gtd_review_count")} reviews')
    print(f'Non-GTD:  {payload.get("non_gtd_review_count")} reviews')
    print()

    rating_counts = payload.get("rating_counts") or {}
    if rating_counts:
        print("Ratings:")
        for key in sorted(rating_counts):
            print(f"  {key}*: {rating_counts[key]}")
        print()

    top_practices = payload.get("top_practices") or []
    if top_practices:
        print("Top practices:")
        for item in top_practices:
            entry = dict(item)
            print(
                f'  {entry.get("practice_name")} ({entry.get("canonical_code")}): '
                f'{entry.get("review_count")} matches, avg {entry.get("avg_rating")}'
            )


def print_report_text(payload: dict[str, object]) -> None:
    search = dict(payload.get("search") or {})
    stats = dict(payload.get("stats") or {})
    quotes = payload.get("quotes") or []

    if search.get("error"):
        print(f'Error: {search.get("error")}')
        return

    print(f'Question: {payload.get("query")}')
    print(f'Matches: {stats.get("review_count")} reviews across {stats.get("practice_count")} practices')
    print(
        f'Ratings: avg {stats.get("avg_rating")} '
        f'(GTD {stats.get("gtd_review_count")}, non-GTD {stats.get("non_gtd_review_count")})'
    )

    top_practices = stats.get("top_practices") or []
    if top_practices:
        print()
        print("Most affected practices:")
        for item in top_practices[:5]:
            entry = dict(item)
            print(
                f'  {entry.get("practice_name")} ({entry.get("canonical_code")}): '
                f'{entry.get("review_count")} matching reviews, avg {entry.get("avg_rating")} stars'
            )

    if quotes:
        print()
        print("Grounding quotes:")
        for item in quotes:
            quote = dict(item)
            print(
                f'  [{quote.get("rating_stars")}*] {quote.get("practice_name")} '
                f'| {quote.get("author")} | {quote.get("date_raw")}'
            )
            print(f'  "{quote.get("quote")}"')


def main() -> int:
    args = parse_args()
    db_path = Path(getattr(args, "db", str(DEFAULT_DB_PATH))).resolve()

    if args.cmd == "search":
        payload = search_reviews(
            db_path=db_path,
            q=str(args.q),
            limit=int(args.limit),
            candidates=int(args.candidates),
            practice=str(args.practice or ""),
            min_rating=args.min_rating,
            max_rating=args.max_rating,
            gtd_only=bool(args.gtd_only),
            non_gtd_only=bool(args.non_gtd_only),
            phrase=bool(args.phrase),
        )
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print_search_text(payload)
        return 0

    if args.cmd == "context":
        payload = load_review_context(
            db_path=db_path,
            review_id=int(args.id),
            before=int(args.before),
            after=int(args.after),
        )
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print_context_text(payload)
        return 0

    if args.cmd == "stats":
        payload = corpus_stats(
            db_path=db_path,
            q=str(args.q or ""),
            practice=str(args.practice or ""),
            min_rating=args.min_rating,
            max_rating=args.max_rating,
            gtd_only=bool(args.gtd_only),
            non_gtd_only=bool(args.non_gtd_only),
            phrase=bool(args.phrase),
            max_matches=int(args.max_matches),
        )
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print_stats_text(payload)
        return 0

    if args.cmd == "report":
        payload = grounded_report(
            db_path=db_path,
            q=str(args.q),
            limit=int(args.limit),
            candidates=int(args.candidates),
            practice=str(args.practice or ""),
            min_rating=args.min_rating,
            max_rating=args.max_rating,
            gtd_only=bool(args.gtd_only),
            non_gtd_only=bool(args.non_gtd_only),
            phrase=bool(args.phrase),
        )
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print_report_text(payload)
        return 0

    raise SystemExit(2)


if __name__ == "__main__":
    raise SystemExit(main())
