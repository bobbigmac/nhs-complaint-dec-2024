#!/usr/bin/env python3
"""Build raw-reviews JSON for practices with extended (full_feed) reviews.

Reads .txt files from the latest report dir, parses reviews, runs classifier.js,
and emits raw_reviews_extended.json. Also aggregates recent reviews from
google_maps_recent_reviews.json for all other practices (small subset per practice)
into a "Recent Reviews across Manchester" table. Run from repo root.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATASET_OUTPUT_DIR = REPO_ROOT / "datasets" / "output"
REPORT_GLOB = "gtd-greater-manchester-gp-practice-reviews-*"
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
CLASSIFIER_JS = Path(__file__).resolve().parent / "classifier.js"


def find_latest_report_dir() -> Path:
    candidates = sorted(
        [p for p in DATASET_OUTPUT_DIR.glob(REPORT_GLOB) if p.is_dir()],
        key=lambda p: p.name,
    )
    if not candidates:
        raise FileNotFoundError(f"No report dirs under {DATASET_OUTPUT_DIR}")
    return candidates[-1]


REVIEW_SECTION_MARKERS = ("Captured reviews", "Recent visible reviews")


def parse_txt_header(lines: list[str]) -> dict[str, str]:
    header: dict[str, str] = {}
    for line in lines:
        stripped = line.strip()
        if stripped in REVIEW_SECTION_MARKERS or (stripped and set(stripped) <= {"="}):
            break
        if ":" in line:
            key, _, val = line.partition(":")
            header[key.strip().lower().replace(" ", "_")] = val.strip()
    return header


def _find_reviews_start(lines: list[str]) -> int:
    for i, line in enumerate(lines):
        if line.strip() in REVIEW_SECTION_MARKERS:
            start_idx = i + 1
            if start_idx < len(lines) and set(lines[start_idx].strip()) <= {"="}:
                start_idx += 1
            return start_idx
    return 0


def parse_reviews_from_txt(content: str, *, require_full_feed: bool = True) -> list[dict[str, Any]]:
    """Parse review blocks from a google-review-texts .txt file."""
    lines = content.splitlines()
    header = parse_txt_header(lines)
    if require_full_feed and header.get("review_collection_mode") != "full_feed":
        return []

    start_idx = _find_reviews_start(lines)

    reviews: list[dict[str, Any]] = []
    i = start_idx
    while i < len(lines):
        line = lines[i]
        author_match = re.match(r"^Author:\s*(.*)$", line.strip())
        if author_match:
            author = author_match.group(1).strip()
            date_str = ""
            rating_str = ""
            text_parts: list[str] = []
            j = i + 1

            while j < len(lines):
                next_line = lines[j]
                stripped = next_line.strip()
                if re.match(r"^Author:\s", stripped):
                    break
                date_m = re.match(r"^Date:\s*(.*)$", stripped)
                rating_m = re.match(r"^Rating:\s*(.*)$", stripped)
                if date_m:
                    date_str = date_m.group(1).strip()
                elif rating_m:
                    rating_str = rating_m.group(1).strip()
                else:
                    text_parts.append(next_line.rstrip())
                j += 1

            stars = 0
            star_m = re.search(r"(\d)\s*star", rating_str, re.I)
            if star_m:
                stars = int(star_m.group(1))

            reviews.append({
                "author": author,
                "date_raw": date_str,
                "rating_stars": stars,
                "rating_label": rating_str,
                "text": normalize_review_text("\n".join(text_parts)),
            })
            i = j
        else:
            i += 1

    return reviews


def normalize_review_text(text: str) -> str:
    """Trim externally and internally; collapse multiple newlines to single."""
    if not text or not isinstance(text, str):
        return ""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def _parse_months_ago(date_raw: str) -> int | None:
    """Parse relative date to approximate months ago. None if unparseable."""
    if not date_raw:
        return None
    normalized = re.sub(r"^Edited\s+", "", date_raw, flags=re.I).strip()
    if re.search(r"\b(\d+)\s*year", normalized, re.I):
        m = re.search(r"(\d+)\s*year", normalized, re.I)
        return (int(m.group(1)) if m else 1) * 12
    if re.search(r"\b(\d+)\s*month", normalized, re.I):
        m = re.search(r"(\d+)\s*month", normalized, re.I)
        return int(m.group(1)) if m else 1
    if re.search(r"\b(\d+)\s*week", normalized, re.I):
        m = re.search(r"(\d+)\s*week", normalized, re.I)
        return max(0, (int(m.group(1)) if m else 1) // 4)
    if re.search(r"\b(\d+)\s*day", normalized, re.I):
        return 0
    return None


def estimate_review_year(date_raw: str, reference_date: str = "2026-03-16") -> int | None:
    """Estimate approximate year from relative date like '2 months ago', 'Edited a year ago'."""
    months_ago = _parse_months_ago(date_raw)
    if months_ago is None:
        return None
    ref_year, ref_month = 2026, 3
    if reference_date:
        parts = reference_date.split("-")
        if len(parts) >= 2:
            ref_year, ref_month = int(parts[0]), int(parts[1])
    total_months = ref_year * 12 + ref_month - months_ago
    return max(2015, total_months // 12)


def extract_canonical_code_from_filename(name: str) -> str:
    """Y02960-new-bank-health.txt -> Y02960"""
    return name.split("-")[0] if "-" in name else name.replace(".txt", "")


def main() -> int:
    report_dir = find_latest_report_dir()
    txt_dir = report_dir / "google-review-texts"
    practices_path = report_dir / "gtd_greater_manchester_gp_practices.json"
    summary_path = report_dir / "summary.json"

    if not txt_dir.exists():
        print("No google-review-texts dir", file=sys.stderr)
        return 1

    practices_data = json.loads(practices_path.read_text(encoding="utf-8"))
    practices_by_code: dict[str, dict[str, Any]] = {
        str(p["canonical_code"]): p for p in practices_data if p.get("canonical_code")
    }

    generated_date = "2026-03-16"
    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        generated_date = str(summary.get("generated_date", generated_date))

    practices_with_reviews: list[dict[str, Any]] = []

    for txt_path in sorted(txt_dir.glob("*.txt")):
        content = txt_path.read_text(encoding="utf-8")
        header = parse_txt_header(content.splitlines())
        if header.get("review_collection_mode") != "full_feed":
            continue

        code = extract_canonical_code_from_filename(txt_path.name)
        practice = practices_by_code.get(code, {})
        practice_name = header.get("practice", practice.get("practice_name", txt_path.stem))
        gtd_managed = bool(practice.get("gtd_managed", False))
        gtd_takeover_date = practice.get("gtd_takeover_date") or ""

        reviews = parse_reviews_from_txt(content)
        for i, r in enumerate(reviews):
            r["_index"] = i
            r["estimated_year"] = estimate_review_year(r["date_raw"], generated_date)
            r["estimated_months_ago"] = _parse_months_ago(r["date_raw"])

        inclusion_reason: str | None = None
        if not gtd_managed and reviews:
            ratings = [r.get("rating_stars") for r in reviews if r.get("rating_stars")]
            avg = sum(ratings) / len(ratings) if ratings else 0
            inclusion_reason = "positive" if avg >= 4 else "negative"

        practices_with_reviews.append({
            "canonical_code": code,
            "practice_name": practice_name,
            "gtd_managed": gtd_managed,
            "gtd_takeover_date": gtd_takeover_date,
            "review_count": len(reviews),
            "reviews": reviews,
            "inclusion_reason": inclusion_reason,
        })

    # Add 2 worst and 2 best non-GTD practices (by google_review_score) that have review txt files
    included_codes = {p["canonical_code"] for p in practices_with_reviews}
    non_gtd_with_txt = [
        p
        for p in practices_data
        if not p.get("gtd_managed")
        and p.get("google_review_text_file")
        and str(p.get("canonical_code", "")) not in included_codes
    ]
    non_gtd_with_txt.sort(key=lambda p: (float(p.get("google_review_score") or 0), str(p.get("canonical_code", ""))))
    worst_two = non_gtd_with_txt[:2] if len(non_gtd_with_txt) >= 2 else non_gtd_with_txt[:1]
    best_two = non_gtd_with_txt[-2:] if len(non_gtd_with_txt) >= 2 else non_gtd_with_txt[-1:] if non_gtd_with_txt else []
    to_add = list({p["canonical_code"]: p for p in worst_two + best_two}.values())

    for practice in to_add:
        code = str(practice.get("canonical_code", ""))
        txt_rel = practice.get("google_review_text_file", "")
        if not txt_rel:
            continue
        txt_path = report_dir / txt_rel
        if not txt_path.exists():
            continue
        content = txt_path.read_text(encoding="utf-8")
        reviews = parse_reviews_from_txt(content, require_full_feed=False)
        if not reviews:
            continue
        for i, r in enumerate(reviews):
            r["_index"] = i
            r["estimated_year"] = estimate_review_year(r["date_raw"], generated_date)
            r["estimated_months_ago"] = _parse_months_ago(r["date_raw"])
        score = float(practice.get("google_review_score") or 0)
        inclusion_reason = "positive" if score >= 4 else "negative"
        practices_with_reviews.append({
            "canonical_code": code,
            "practice_name": practice.get("practice_name", ""),
            "gtd_managed": False,
            "gtd_takeover_date": "",
            "review_count": len(reviews),
            "reviews": reviews,
            "inclusion_reason": inclusion_reason,
        })
        included_codes.add(code)

    def practice_sort_key(p: dict[str, Any]) -> tuple[int, str]:
        code = str(p.get("canonical_code", ""))
        if code == "Y02960":
            return (0, code)
        if p.get("gtd_managed"):
            return (1, code)
        return (2, code)

    practices_with_reviews.sort(key=practice_sort_key)

    # Aggregate recent reviews from google_maps_recent_reviews.json for all other practices
    google_json_path = report_dir / "google_maps_recent_reviews.json"
    recent_reviews_across: list[dict[str, Any]] = []
    if google_json_path.exists():
        google_data = json.loads(google_json_path.read_text(encoding="utf-8"))
        for record in google_data:
            code = str(record.get("canonical_code", ""))
            if not code or code in included_codes:
                continue
            practice_name = record.get("practice_name", "")
            for rev in record.get("recent_reviews") or []:
                stars = 0
                star_m = re.search(r"(\d)\s*star", str(rev.get("star_label", "")), re.I)
                if star_m:
                    stars = int(star_m.group(1))
                date_raw = rev.get("relative_date", "")
                recent_reviews_across.append({
                    "author": rev.get("author", ""),
                    "date_raw": date_raw,
                    "rating_stars": stars,
                    "rating_label": rev.get("star_label", ""),
                    "text": normalize_review_text(rev.get("text") or ""),
                    "practice_name": practice_name,
                    "canonical_code": code,
                    "_index": len(recent_reviews_across),
                    "estimated_year": estimate_review_year(date_raw, generated_date),
                    "estimated_months_ago": _parse_months_ago(date_raw),
                })

    # Run classifier
    input_data = {
        "practices": practices_with_reviews,
        "recent_reviews_across_manchester": recent_reviews_across,
        "generated_date": generated_date,
    }
    classifier_input = REPO_ROOT / "datasets" / "reviews-analysis" / "output" / ".classifier_input.json"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    classifier_input.write_text(json.dumps(input_data, indent=2), encoding="utf-8")

    overrides_path = Path(__file__).resolve().parent / "classifier_overrides.json"
    overrides = {}
    if overrides_path.exists():
        overrides = json.loads(overrides_path.read_text(encoding="utf-8"))

    try:
        result = subprocess.run(
            [
                "node",
                str(CLASSIFIER_JS),
                str(classifier_input),
                json.dumps(overrides),
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=60,
        )
        if result.returncode != 0:
            print("Classifier failed:", result.stderr, file=sys.stderr)
            return 1
        classified = json.loads(result.stdout)
    except FileNotFoundError:
        print("Node not found; skipping classifier, outputting unclassified", file=sys.stderr)
        classified = input_data
    except json.JSONDecodeError as e:
        print("Classifier output invalid JSON:", e, file=sys.stderr)
        classified = input_data

    out_path = OUTPUT_DIR / "raw_reviews_extended.json"
    out_path.write_text(json.dumps(classified, indent=2), encoding="utf-8")
    print(f"Wrote {out_path} ({len(practices_with_reviews)} practices)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
