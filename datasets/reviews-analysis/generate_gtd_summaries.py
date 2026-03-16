#!/usr/bin/env python3
"""Generate summaries for GTD consolidated operational groups.

Run after build_reviews_evidence.py. Loads raw_reviews_extended.json and review_classifications.json,
filters to GTD practices, groups by operational category (multiCategory logic). For each group with
>1 review, writes a data-derived summary (subcategory prevalence, rating distribution, cluster themes)
to markdown. No external API calls.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "output"
SUMMARIES_DIR = SCRIPT_DIR / "gtd_summaries"
OPERATIONAL_TAXONOMY = SCRIPT_DIR / "operational_taxonomy.json"
RAW_REVIEWS = OUTPUT_DIR / "raw_reviews_extended.json"
CLASSIFICATIONS = OUTPUT_DIR / "review_classifications.json"


def load_taxonomy() -> dict[str, Any]:
    if not OPERATIONAL_TAXONOMY.exists():
        return {}
    return json.loads(OPERATIONAL_TAXONOMY.read_text(encoding="utf-8"))


def get_operational_order(tax: dict[str, Any]) -> list[str]:
    cats = tax.get("top_level_categories") or []
    return [c["id"] for c in cats if c.get("id")]


def get_subcategory_label(tax: dict[str, Any], slug: str, sub: str) -> str:
    for c in tax.get("top_level_categories") or []:
        if c.get("id") != slug:
            continue
        for s in c.get("subcategories") or []:
            if s.get("id") == sub:
                return s.get("label", sub)
    return sub


def group_by_operational_multi(reviews: list[dict[str, Any]], order: list[str]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for r in reviews:
        cats = r.get("operational_categories") or [r.get("operational_category") or "uncategorised"]
        for b in cats:
            key = (b or "uncategorised").strip()
            if not groups.get(key):
                groups[key] = []
            groups[key].append(r)
    return {k: groups[k] for k in order if groups.get(k)}


def generate_summary(slug: str, label: str, reviews: list[dict[str, Any]], tax: dict[str, Any], cluster_labels: dict[str, str]) -> str:
    """Build a data-derived summary from classifier output. No API calls."""
    sub_counts: Counter[str] = Counter()
    rating_counts: Counter[int] = Counter()
    cluster_terms: list[str] = []
    excerpts: list[str] = []

    for r in reviews:
        sub = (r.get("subcategory") or "").strip() or "(general)"
        sub_counts[sub] += 1
        stars = int(r.get("rating_stars") or 0)
        rating_counts[stars] += 1
        for bid in r.get("buckets") or [r.get("primary_bucket")]:
            if bid and bid in cluster_labels:
                cluster_terms.append(cluster_labels[bid])
        t = (r.get("text") or "").strip()
        if t and len(t) > 30:
            excerpts.append(t[:150].rstrip() + ("…" if len(t) > 150 else ""))

    lines: list[str] = []
    lines.append(f"## {label}\n")
    lines.append(f"**{len(reviews)} reviews** in this category.\n")

    # Subcategory prevalence
    if sub_counts:
        lines.append("### Prevalence by subcategory\n")
        for sub, count in sub_counts.most_common():
            sub_label = get_subcategory_label(tax, slug, sub) if sub != "(general)" else "General"
            pct = 100 * count / len(reviews)
            lines.append(f"- **{sub_label}**: {count} ({pct:.0f}%)")
        lines.append("")

    # Rating distribution
    if rating_counts:
        lines.append("### Rating distribution\n")
        for s in sorted(rating_counts.keys(), reverse=True):
            n = rating_counts[s]
            pct = 100 * n / len(reviews)
            lines.append(f"- {s}★: {n} ({pct:.0f}%)")
        lines.append("")

    # Cluster themes (top terms from classifier)
    if cluster_terms:
        lines.append("### Themes (from classifier)\n")
        unique = list(dict.fromkeys(cluster_terms))[:5]
        lines.append(", ".join(unique) + "\n")

    # Representative excerpts (max 3)
    if excerpts:
        lines.append("### Sample excerpts\n")
        for ex in excerpts[:3]:
            lines.append(f"> {ex}\n")

    return "\n".join(lines)


def main() -> int:
    if not RAW_REVIEWS.exists():
        print(f"Run build_reviews_evidence.py first. Missing: {RAW_REVIEWS}", file=sys.stderr)
        return 1

    cluster_labels: dict[str, str] = {"uncategorised": "Other"}
    if CLASSIFICATIONS.exists():
        cls_data = json.loads(CLASSIFICATIONS.read_text(encoding="utf-8"))
        cluster_labels = cls_data.get("cluster_labels", cluster_labels)

    tax = load_taxonomy()
    order = get_operational_order(tax)
    if not order:
        order = ["access", "front_desk", "clinical_care", "admin_and_referrals", "medicines_and_tests", "on_site_experience", "management_and_change", "positive_feedback", "uncategorised"]

    data = json.loads(RAW_REVIEWS.read_text(encoding="utf-8"))
    gtd_reviews: list[dict[str, Any]] = []
    for p in data.get("practices") or []:
        if not p.get("gtd_managed"):
            continue
        takeover_date = (p.get("gtd_takeover_date") or "").strip()
        takeover_year = int(takeover_date[:4]) if len(takeover_date) >= 4 else None
        for r in p.get("reviews") or []:
            if r.get("is_practice_reply"):
                continue
            # Exclude non-GTD era (pre-takeover) reviews
            if takeover_year is not None:
                y = r.get("estimated_year")
                if y is not None and y < takeover_year:
                    continue
            gtd_reviews.append({**r, "practice_name": p.get("practice_name", "")})

    groups = group_by_operational_multi(gtd_reviews, order)
    manifest: list[dict[str, Any]] = []
    SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)

    for c in tax.get("top_level_categories") or []:
        slug = c.get("id")
        if not slug:
            continue
        label = c.get("label", slug)
        revs = groups.get(slug) or []
        if len(revs) <= 1:
            continue
        manifest.append({"slug": slug, "label": label, "review_count": len(revs)})
        md_path = SUMMARIES_DIR / f"{slug}.md"
        if md_path.exists() and "### Summary" in md_path.read_text(encoding="utf-8"):
            print(f"Skipping {slug} (manual summary exists)...", file=sys.stderr)
        else:
            print(f"Writing summary for {slug} ({len(revs)} reviews)...", file=sys.stderr)
            summary = generate_summary(slug, label, revs, tax, cluster_labels)
            md_path.write_text(summary, encoding="utf-8")

    manifest_path = SUMMARIES_DIR / "manifest.json"
    manifest_path.write_text(json.dumps({"slugs": [m["slug"] for m in manifest], "entries": manifest}, indent=2), encoding="utf-8")
    print(f"Wrote manifest and {len(manifest)} summaries to {SUMMARIES_DIR}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
