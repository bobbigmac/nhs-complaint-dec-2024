#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import random
import subprocess
import sys
import time
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "gtd-greater-manchester-gp-practice-reviews-2026-03-09"
DEFAULT_INPUT = OUTPUT_DIR / "gtd_greater_manchester_gp_practices.csv"
DEFAULT_GOOGLE_JSON = OUTPUT_DIR / "google_maps_recent_reviews.json"
DEFAULT_COLLECTOR_PYTHON = BASE_DIR / ".venv-google-reviews" / "bin" / "python"


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open() as handle:
        return list(csv.DictReader(handle))


def load_scanned_codes(path: Path) -> set[str]:
    if not path.exists():
        return set()
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {str(item.get("canonical_code", "")).strip() for item in payload if item.get("canonical_code")}


def remaining_rows(rows: list[dict[str, str]], scanned_codes: set[str]) -> list[dict[str, str]]:
    return [row for row in rows if row.get("canonical_code", "").strip() not in scanned_codes]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Google Maps review capture in cautious randomized batches until all target practices are scanned.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--google-json", type=Path, default=DEFAULT_GOOGLE_JSON)
    parser.add_argument("--collector-python", type=Path, default=DEFAULT_COLLECTOR_PYTHON)
    parser.add_argument("--batch-size-min", type=int, default=5)
    parser.add_argument("--batch-size-max", type=int, default=8)
    parser.add_argument("--practice-pause-min", type=float, default=2.5)
    parser.add_argument("--practice-pause-max", type=float, default=4.5)
    parser.add_argument("--practice-jitter-min", type=float, default=0.8)
    parser.add_argument("--practice-jitter-max", type=float, default=2.0)
    parser.add_argument("--batch-wait-min", type=float, default=45.0)
    parser.add_argument("--batch-wait-max", type=float, default=120.0)
    parser.add_argument("--recent-reviews", type=int, default=10)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--max-batches", type=int, default=0, help="Stop after this many batches; 0 means run until complete")
    args = parser.parse_args()

    if args.batch_size_min <= 0 or args.batch_size_max < args.batch_size_min:
        raise SystemExit("Invalid batch size range")

    batch_number = 0
    while True:
        rows = load_rows(args.input)
        scanned_codes = load_scanned_codes(args.google_json)
        remaining = remaining_rows(rows, scanned_codes)
        if not remaining:
            print("No remaining practices to scan.")
            return 0
        if args.max_batches and batch_number >= args.max_batches:
            print(f"Stopped after {batch_number} batches with {len(remaining)} practices still unscanned.")
            return 0

        batch_number += 1
        batch_size = min(random.randint(args.batch_size_min, args.batch_size_max), len(remaining))
        pause_seconds = random.uniform(args.practice_pause_min, args.practice_pause_max)
        pause_jitter = random.uniform(args.practice_jitter_min, args.practice_jitter_max)
        print(f"Batch {batch_number}: scanning {batch_size} practices, {len(remaining)} remaining before batch")
        print(f"Per-practice pause {pause_seconds:.2f}s + up to {pause_jitter:.2f}s jitter")

        collect_cmd = [
            str(args.collector_python),
            str(BASE_DIR / "collect_google_maps_reviews.py"),
            "--input",
            str(args.input),
            "--resume",
            "--limit",
            str(batch_size),
            "--recent-reviews",
            str(args.recent_reviews),
            "--pause-seconds",
            f"{pause_seconds:.2f}",
            "--pause-jitter-seconds",
            f"{pause_jitter:.2f}",
            "--output",
            str(args.google_json),
        ]
        if args.headless:
            collect_cmd.append("--headless")
        subprocess.run(collect_cmd, check=True, cwd=BASE_DIR)

        merge_cmd = [sys.executable, str(BASE_DIR / "merge_google_maps_reviews.py")]
        subprocess.run(merge_cmd, check=True, cwd=BASE_DIR)

        rows = load_rows(args.input)
        scanned_codes = load_scanned_codes(args.google_json)
        remaining_after = remaining_rows(rows, scanned_codes)
        print(f"Batch {batch_number} complete: {len(remaining_after)} practices remain unscanned")
        if not remaining_after:
            return 0

        batch_wait = random.uniform(args.batch_wait_min, args.batch_wait_max)
        print(f"Waiting {batch_wait:.1f}s before next batch")
        time.sleep(batch_wait)


if __name__ == "__main__":
    raise SystemExit(main())
