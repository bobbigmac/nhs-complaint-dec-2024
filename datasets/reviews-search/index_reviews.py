#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from review_search_lib import DEFAULT_DB_PATH, rebuild_review_index, resolve_report_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the local SQLite fulltext index for practice review text files.")
    parser.add_argument("--report-dir", default="", help="Report dir to index. Defaults to the latest datasets/output report.")
    parser.add_argument("--db", default=str(DEFAULT_DB_PATH), help="SQLite database path.")
    parser.add_argument(
        "--include-visible-cards",
        action="store_true",
        help="Include non-full-feed text exports as well as full-feed reviews.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of a short text summary.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = rebuild_review_index(
        db_path=Path(args.db).resolve(),
        report_dir=resolve_report_dir(args.report_dir),
        include_visible_cards=bool(args.include_visible_cards),
    )
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f'Indexed {payload["review_count"]} reviews from {payload["practice_count"]} practices.')
        print(f'Database: {payload["db_path"]}')
        print(f'Report:   {payload["report_dir"]}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
