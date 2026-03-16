#!/usr/bin/env python3
"""Inspect classifier output with full review text for each cluster.

Outputs a markdown report matching what the client sees (grouped by cluster)
but with raw review text included for tuning and label drafting.

Usage:
  python inspect_classifier.py [--output report.md] [--top N]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
CLASSIFIER_INPUT = OUTPUT_DIR / ".classifier_input.json"
CLASSIFICATIONS = OUTPUT_DIR / "review_classifications.json"
CLASSIFIER_CONFIG = Path(__file__).resolve().parent / "classifier_config.json"
DEFAULT_REPORT = OUTPUT_DIR / "classifier_inspection_report.md"


def _build_review_lookup(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Map review_id -> full review dict (author, date, rating, text, practice_name, etc)."""
    lookup: dict[str, dict[str, Any]] = {}
    for p in data.get("practices") or []:
        code = str(p.get("canonical_code", ""))
        practice_name = p.get("practice_name", "")
        for r in p.get("reviews") or []:
            idx = r.get("_index", len(lookup))
            rid = f"{code}:{idx}"
            lookup[rid] = {
                **r,
                "practice_name": practice_name,
                "canonical_code": code,
            }
    for i, r in enumerate(data.get("recent_reviews_across_manchester") or []):
        rid = f"_across:{r.get('_index', i)}"
        lookup[rid] = {
            **r,
            "practice_name": r.get("practice_name", ""),
            "canonical_code": r.get("canonical_code", "_across"),
        }
    return lookup




def _load_config() -> dict:
    if CLASSIFIER_CONFIG.exists():
        return json.loads(CLASSIFIER_CONFIG.read_text(encoding="utf-8"))
    return {}


def _flag_words(text: str, watch: list[str], warn: list[str]) -> tuple[list[str], list[str]]:
    lower = text.lower()
    found_watch = [w for w in watch if w.lower() in lower]
    found_warn = [w for w in warn if w.lower() in lower]
    return found_watch, found_warn


def run(
    *,
    output_path: Path = DEFAULT_REPORT,
    top_n: int | None = None,
    min_reviews: int = 1,
) -> None:
    input_data = json.loads(CLASSIFIER_INPUT.read_text(encoding="utf-8"))
    classifications_data = json.loads(CLASSIFICATIONS.read_text(encoding="utf-8"))
    config = _load_config()
    watch_words = config.get("watch_words", [])
    warn_words = config.get("warn_words", [])
    lookup = _build_review_lookup(input_data)
    cls_map = classifications_data.get("classifications", {})
    auto_labels = classifications_data.get("cluster_labels", {})

    by_cluster: dict[str, list[str]] = {}
    for rid, c in cls_map.items():
        cid = c.get("cluster_id", "uncategorised")
        by_cluster.setdefault(cid, []).append(rid)

    clusters_sorted = sorted(
        by_cluster.keys(),
        key=lambda c: (c == "uncategorised", -len(by_cluster[c]), c),
    )
    if top_n:
        clusters_sorted = [c for c in clusters_sorted if len(by_cluster[c]) >= min_reviews][:top_n]

    lines: list[str] = []
    lines.append("# Classifier inspection report")
    lines.append("")
    lines.append("Same grouping as client-side, with full review text for tuning.")
    lines.append("")
    lines.append("---")
    lines.append("")

    for cid in clusters_sorted:
        rids = by_cluster[cid]
        if len(rids) < min_reviews:
            continue
        label = auto_labels.get(cid, cid)
        lines.append(f"## {cid}: {label}")
        lines.append("")
        lines.append(f"*Reviews:* {len(rids)}")
        ratings = []
        for rid in rids:
            r = lookup.get(rid, {})
            s = r.get("rating_stars")
            if s is not None and s > 0:
                ratings.append(s)
        if ratings:
            avg = sum(ratings) / len(ratings)
            lines.append(f"*Avg rating:* {avg:.1f}")
        lines.append("")
        lines.append("### Sample reviews")
        lines.append("")
        for rid in rids[:15]:
            r = lookup.get(rid, {})
            author = r.get("author", "—")
            stars = r.get("rating_stars") or "?"
            date = r.get("date_raw", "")
            practice = r.get("practice_name", "")
            text = (r.get("text") or "").strip()
            watch_found, warn_found = _flag_words(text, watch_words, warn_words)
            flags = []
            if watch_found:
                flags.append(f"watch:{','.join(watch_found)}")
            if warn_found:
                flags.append(f"warn:{','.join(warn_found)}")
            flag_str = f" [{'] ['.join(flags)}]" if flags else ""
            lines.append(f"**{author}** · {stars}★ · {date} · {practice}{flag_str}")
            lines.append("")
            lines.append(f"> {text[:600]}{'…' if len(text) > 600 else ''}")
            lines.append("")
        if len(rids) > 15:
            lines.append(f"*…and {len(rids) - 15} more*")
            lines.append("")
        lines.append("---")
        lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {output_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect classifier clusters with full review text")
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT, help="Output markdown path")
    parser.add_argument("--top", type=int, default=None, help="Only show top N clusters by size")
    parser.add_argument("--min-reviews", type=int, default=1, help="Min reviews per cluster to include")
    args = parser.parse_args()

    if not CLASSIFIER_INPUT.exists():
        print(f"Input not found: {CLASSIFIER_INPUT}", flush=True)
        return 1
    if not CLASSIFICATIONS.exists():
        print(f"Classifications not found: {CLASSIFICATIONS}. Run build_classifier_graph.py first.", flush=True)
        return 1

    run(output_path=args.output, top_n=args.top, min_reviews=args.min_reviews)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
