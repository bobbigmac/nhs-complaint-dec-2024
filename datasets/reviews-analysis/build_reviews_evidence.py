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
CLASSIFIER_GRAPH = Path(__file__).resolve().parent / "build_classifier_graph.py"
OPERATIONAL_TAXONOMY = Path(__file__).resolve().parent / "operational_taxonomy.json"


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

            raw_text = "\n".join(text_parts)
            stripped = strip_metadata_from_review_text(raw_text, author, date_str)
            reviews.append({
                "author": author,
                "date_raw": date_str,
                "rating_stars": stars,
                "rating_label": rating_str,
                "text": normalize_review_text(stripped),
            })
            i = j
        else:
            i += 1

    return reviews


def strip_metadata_from_review_text(text: str, author: str, date_raw: str) -> str:
    """Remove metadata spillage (author, review count, date, New) from text.
    When the scraped body is the card byline instead of real review content,
    strip known patterns from the start so we don't treat metadata as review text.
    Only strips prefix to avoid removing phrases like '2 reviews' from real content."""
    if not text or not isinstance(text, str):
        return ""
    t = text.strip()
    if not t:
        return ""
    # Build prefix pattern: author? + (Local Guide)? + (N reviews · N photos?)? + (N|a) (weeks?|...) ago + New?
    # Allow "photosa" (no space before "a" in "a month ago")
    prefix_parts: list[str] = []
    if author:
        prefix_parts.append(re.escape(author))
    prefix_parts.append(
        r"(?:Local\s+Guide\s*(?:\·\s*)?)?"
        r"(?:\d+\s*reviews?\s*(?:\·\s*\d+\s*photos?\s*a?)?\s*)?"
        r"(?:\d+\s*(?:weeks?|months?|years?|days?)\s+ago|a?\s*(?:week|month|year|day)s?\s+ago)\s*"
    )
    prefix_parts.append(r"(?:New\s*)?")
    prefix_re = re.compile(r"^\s*" + "".join(prefix_parts), re.I)
    t = prefix_re.sub("", t)
    t = re.sub(r"^\s*(?:Local\s+Guide\s*|Edited\s+)+", "", t, flags=re.I)
    t = re.sub(r"\s+", " ", t).strip()
    return t if len(t) > 2 else ""


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


def _review_dedup_key(r: dict[str, Any]) -> tuple[str, str, str]:
    """Stable key for deduplication: (author, date_raw, text_prefix)."""
    author = (r.get("author") or "").strip()
    date_raw = (r.get("date_raw") or r.get("relative_date") or "").strip()
    text = (r.get("text") or "").strip()[:300]
    return (author, date_raw, text)


def _author_date_key(r: dict[str, Any]) -> tuple[str, str]:
    author = (r.get("author") or "").strip()
    date_raw = (r.get("date_raw") or r.get("relative_date") or "").strip()
    return (author, date_raw)


def _text_matches_for_dedup(text_a: str, text_b: str) -> bool:
    """True if both texts refer to the same review (equal, prefix, or truncated with …)."""
    a, b = text_a.strip(), text_b.strip()
    if a == b:
        return True
    if a.startswith(b) or b.startswith(a):
        return True
    # Truncated form ends with …; full form starts with the content before …
    if a.endswith("…") and b.startswith(a[:-1].rstrip()):
        return True
    if b.endswith("…") and a.startswith(b[:-1].rstrip()):
        return True
    return False


def dedupe_reviews(reviews: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Remove duplicates. When one text is a prefix of another (same author+date), keep the longer."""
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for r in reviews:
        k = _author_date_key(r)
        groups.setdefault(k, []).append(r)

    out: list[dict[str, Any]] = []
    for group in groups.values():
        sorted_group = sorted(group, key=lambda r: len((r.get("text") or "").strip()), reverse=True)
        kept: list[dict[str, Any]] = []
        for r in sorted_group:
            text = (r.get("text") or "").strip()
            if any(_text_matches_for_dedup((k.get("text") or "").strip(), text) for k in kept):
                continue
            kept.append(r)
        out.extend(kept)
    return out


def _is_duplicate_of(r: dict[str, Any], others: list[dict[str, Any]]) -> bool:
    """True if r is same review as any in others (same author+date, one text prefix of other)."""
    key = _author_date_key(r)
    text = (r.get("text") or "").strip()
    for o in others:
        if _author_date_key(o) != key:
            continue
        if _text_matches_for_dedup(text, (o.get("text") or "").strip()):
            return True
    return False


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

        reviews = dedupe_reviews(parse_reviews_from_txt(content))
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
        reviews = dedupe_reviews(parse_reviews_from_txt(content, require_full_feed=False))
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
                raw_text = rev.get("text") or ""
                stripped = strip_metadata_from_review_text(
                    raw_text, rev.get("author", ""), date_raw
                )
                recent_reviews_across.append({
                    "author": rev.get("author", ""),
                    "date_raw": date_raw,
                    "rating_stars": stars,
                    "rating_label": rev.get("star_label", ""),
                    "text": normalize_review_text(stripped),
                    "practice_name": practice_name,
                    "canonical_code": code,
                    "_index": len(recent_reviews_across),
                    "estimated_year": estimate_review_year(date_raw, generated_date),
                    "estimated_months_ago": _parse_months_ago(date_raw),
                })
        recent_reviews_across = dedupe_reviews(recent_reviews_across)
        all_practice_reviews = [r for p in practices_with_reviews for r in p.get("reviews", [])]
        recent_reviews_across = [r for r in recent_reviews_across if not _is_duplicate_of(r, all_practice_reviews)]
        for i, r in enumerate(recent_reviews_across):
            r["_index"] = i

    # Run classifier
    input_data = {
        "practices": practices_with_reviews,
        "recent_reviews_across_manchester": recent_reviews_across,
        "generated_date": generated_date,
    }
    classifier_input = REPO_ROOT / "datasets" / "reviews-analysis" / "output" / ".classifier_input.json"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    classifier_input.write_text(json.dumps(input_data, indent=2), encoding="utf-8")

    # Run graph-based classifier (requires scikit-learn)
    classifier_output = OUTPUT_DIR / "review_classifications.json"
    result = subprocess.run(
        [sys.executable, str(CLASSIFIER_GRAPH), "--input", str(classifier_input), "--output", str(classifier_output)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=120,
    )
    if result.returncode != 0:
        if classifier_output.exists():
            print("Graph classifier failed (scikit-learn required); using committed fallback", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
        else:
            print("Graph classifier failed:", result.stderr, file=sys.stderr)
            print("Install scikit-learn and run on a dev machine, then commit output/review_classifications.json", file=sys.stderr)
            return 1
    try:
        classifications_data = json.loads(classifier_output.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print("Classifier output invalid JSON:", e, file=sys.stderr)
        return 1

    cls_map = classifications_data.get("classifications", {})
    cluster_labels = classifications_data.get("cluster_labels", {"uncategorised": "Other"})
    meta = classifications_data.get("meta", {})
    taxonomy_version = meta.get("taxonomy_version", "")

    def apply_classification(review: dict[str, Any], practice_code: str, idx: int) -> None:
        rid = f"{practice_code}:{idx}"
        c = cls_map.get(rid, {})
        review["primary_bucket"] = c.get("primary_bucket", "uncategorised")
        review["buckets"] = c.get("buckets", ["uncategorised"])
        review["operational_category"] = c.get("operational_category", "uncategorised")
        review["operational_categories"] = c.get("operational_categories", [c.get("operational_category", "uncategorised")])
        review["subcategory"] = c.get("subcategory", "")
        review["operational_confidence"] = c.get("operational_confidence", 0.0)

    for practice in input_data["practices"]:
        code = str(practice.get("canonical_code", ""))
        for i, r in enumerate(practice.get("reviews") or []):
            apply_classification(r, code, r.get("_index", i))

    for i, r in enumerate(input_data.get("recent_reviews_across_manchester") or []):
        rid = f"_across:{r.get('_index', i)}"
        c = cls_map.get(rid, {})
        r["primary_bucket"] = c.get("primary_bucket", "uncategorised")
        r["buckets"] = c.get("buckets", ["uncategorised"])
        r["operational_category"] = c.get("operational_category", "uncategorised")
        r["operational_categories"] = c.get("operational_categories", [c.get("operational_category", "uncategorised")])
        r["subcategory"] = c.get("subcategory", "")
        r["operational_confidence"] = c.get("operational_confidence", 0.0)

    operational_taxonomy: dict[str, Any] = {}
    if OPERATIONAL_TAXONOMY.exists():
        operational_taxonomy = json.loads(OPERATIONAL_TAXONOMY.read_text(encoding="utf-8"))

    classified = {
        **input_data,
        "cluster_labels": cluster_labels,
        "taxonomy_version": taxonomy_version,
        "operational_taxonomy": operational_taxonomy,
    }

    out_path = OUTPUT_DIR / "raw_reviews_extended.json"
    out_path.write_text(json.dumps(classified, indent=2), encoding="utf-8")
    print(f"Wrote {out_path} ({len(practices_with_reviews)} practices)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
