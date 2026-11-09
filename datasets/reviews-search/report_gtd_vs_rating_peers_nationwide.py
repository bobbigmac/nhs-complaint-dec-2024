#!/usr/bin/env python3
"""
Nationwide comparison: GTD-managed practices vs non-GTD practices matched on
listed Google score (and review-volume floor). Uses the same access-theme
patterns as analyze_access_issues plus a few takeover/operator phrases.

Caveat: GTD flags exist only for the Manchester report slice in this DB; those
reviews are mostly full_feed. Peers are drawn UK-wide (Manchester + national)
with similar google_review_score — capture depth still differs by row.
"""
from __future__ import annotations

import json
import re
import sqlite3
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from analyze_access_issues import ACCESS_PATTERNS, match_categories, snippet, strip_practice_response
from review_search_lib import DEFAULT_DB_PATH as DB_PATH

OUT_DIR = Path.home() / ".local" / "share" / "nhs-complaint-2024"

# Extra themes: where GTD roll-ups often show up in free text
EXTRA_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "gtd_or_brand_mentioned": [
        re.compile(r"\bGTD\b", re.I),
        re.compile(r"\bgtd\b"),
    ],
    "takeover_merger_or_new_owners": [
        re.compile(r"\b(take\s*over|taken\s*over|takeover)\b", re.I),
        re.compile(r"\b(merger|merged|new\s+management|new\s+owners?)\b", re.I),
        re.compile(r"\bsince\s+.{0,25}\b(took\s*over|bought|merged)\b", re.I),
    ],
    "lost_usual_doctor_or_continuity": [
        re.compile(r"\b(my|the)\s+(usual|own|regular)\s+(doctor|gp)\b", re.I),
        re.compile(r"\b(doctor|gp)\s+.{0,20}\b(left|gone|retired|no\s+longer)\b", re.I),
        re.compile(r"\bcontinuity\b", re.I),
        re.compile(r"\bnever\s+see\s+the\s+same\b", re.I),
    ],
    "confidentiality_or_desk_privacy": [
        re.compile(r"\bconfidential\b", re.I),
        re.compile(r"\b(privacy|private)\b.{0,30}\b(reception|desk|counter|waiting)\b", re.I),
        re.compile(r"\bheard\s+.{0,20}\b(name|dob|date\s+of\s+birth|address)\b", re.I),
    ],
}


def match_extra(text: str) -> set[str]:
    return {k for k, pats in EXTRA_PATTERNS.items() if any(p.search(text) for p in pats)}


def all_themes(text: str) -> set[str]:
    return match_categories(text) | match_extra(text)


def practice_table(con: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = con.execute(
        """
        SELECT
          canonical_code,
          MAX(practice_name) AS practice_name,
          MAX(CAST(gtd_managed AS INT)) AS gtd,
          MAX(google_review_score) AS gscore,
          MAX(google_review_count) AS gcount,
          COUNT(*) AS review_n,
          AVG(rating_stars) AS avg_stars,
          SUM(CASE WHEN rating_stars IN (1, 2) THEN 1 ELSE 0 END) AS low_star_n,
          SUM(CASE WHEN source_file LIKE '%national-practices%' THEN 1 ELSE 0 END) AS national_n,
          SUM(CASE WHEN source_file NOT LIKE '%national-practices%' THEN 1 ELSE 0 END) AS manchester_n
        FROM reviews
        GROUP BY canonical_code
        """
    ).fetchall()
    out = []
    for r in rows:
        out.append(
            {
                "canonical_code": str(r["canonical_code"]),
                "practice_name": str(r["practice_name"] or ""),
                "gtd": bool(r["gtd"]),
                "google_review_score": float(r["gscore"]) if r["gscore"] is not None else None,
                "google_review_count": int(r["gcount"] or 0) if r["gcount"] is not None else None,
                "review_n": int(r["review_n"] or 0),
                "avg_stars": float(r["avg_stars"] or 0),
                "low_star_n": int(r["low_star_n"] or 0),
                "national_n": int(r["national_n"] or 0),
                "manchester_n": int(r["manchester_n"] or 0),
            }
        )
    return out


def pick_peers(
    practices: list[dict[str, Any]],
    *,
    gtd_rows: list[dict[str, Any]],
    min_reviews: int = 25,
    band_pad: float = 0.25,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    gtd_scores = [p["google_review_score"] for p in gtd_rows if p["google_review_score"] is not None]
    if not gtd_scores:
        return [], {"error": "no GTD practices with google_review_score"}
    lo = min(gtd_scores) - band_pad
    hi = max(gtd_scores) + band_pad
    med = float(statistics.median(gtd_scores))
    peers = [
        p
        for p in practices
        if not p["gtd"]
        and p["review_n"] >= min_reviews
        and p["google_review_score"] is not None
        and lo <= p["google_review_score"] <= hi
    ]
    meta = {
        "gtd_practice_count": len(gtd_rows),
        "peer_practice_count": len(peers),
        "google_score_band": [round(lo, 2), round(hi, 2)],
        "gtd_google_score_median": round(med, 3),
        "min_reviews_for_peer": min_reviews,
    }
    return peers, meta


def cohort_reviews(con: sqlite3.Connection, codes: set[str]) -> list[sqlite3.Row]:
    if not codes:
        return []
    qmarks = ",".join("?" * len(codes))
    return con.execute(
        f"""
        SELECT id, canonical_code, practice_name, rating_stars, text, source_file, gtd_managed
        FROM reviews
        WHERE canonical_code IN ({qmarks})
        ORDER BY id
        """,
        tuple(codes),
    ).fetchall()


def analyze_cohort(rows: list[sqlite3.Row], *, low_star_only: bool) -> dict[str, Any]:
    theme_hits = 0
    theme_counts: dict[str, int] = defaultdict(int)
    review_n = 0
    examples: dict[str, list[str]] = defaultdict(list)

    for row in rows:
        stars = int(row["rating_stars"] or 0)
        if low_star_only and stars not in (1, 2):
            continue
        text = strip_practice_response(str(row["text"] or ""))
        if not text.strip():
            continue
        review_n += 1
        themes = all_themes(text)
        if themes:
            theme_hits += 1
        for t in themes:
            theme_counts[t] += 1
            if len(examples[t]) < 3:
                examples[t].append(snippet(text, 220))

    return {
        "reviews_used": review_n,
        "reviews_with_any_theme": theme_hits,
        "theme_counts": dict(sorted(theme_counts.items(), key=lambda x: -x[1])),
        "examples": {k: v for k, v in examples.items()},
    }


def rate_per_1k(count: int, reviews: int) -> float:
    if reviews <= 0:
        return 0.0
    return round(1000.0 * count / reviews, 2)


def compare_themes(gtd: dict[str, Any], peer: dict[str, Any]) -> list[dict[str, Any]]:
    g_n = gtd["reviews_used"]
    p_n = peer["reviews_used"]
    keys = set(gtd["theme_counts"]) | set(peer["theme_counts"])
    rows = []
    for k in keys:
        gc = int(gtd["theme_counts"].get(k, 0))
        pc = int(peer["theme_counts"].get(k, 0))
        gr = rate_per_1k(gc, g_n)
        pr = rate_per_1k(pc, p_n)
        lift = round(gr / pr, 3) if pr > 0 else None
        rows.append(
            {
                "theme": k,
                "gtd_count": gc,
                "peer_count": pc,
                "gtd_per_1k": gr,
                "peer_per_1k": pr,
                "lift_vs_peer": lift,
            }
        )
    rows.sort(key=lambda r: (-(r["lift_vs_peer"] or 0), -r["gtd_per_1k"]))
    return rows


def write_markdown(
    path: Path,
    *,
    peer_meta: dict[str, Any],
    gtd_practices: list[dict[str, Any]],
    gtd_all: dict[str, Any],
    peer_all: dict[str, Any],
    gtd_low: dict[str, Any],
    peer_low: dict[str, Any],
    cmp_all: list[dict[str, Any]],
    cmp_low: list[dict[str, Any]],
    manchester_sensitivity: dict[str, Any] | None,
) -> None:
    lines: list[str] = []
    lines.append("# GTD-managed vs rating-matched non-GTD peers (nationwide peer pool)")
    lines.append("")
    lines.append(f"Generated: `{datetime.now(timezone.utc).isoformat()}`")
    lines.append("")
    lines.append("## What this is")
    lines.append("")
    lines.append(
        "- **GTD cohort**: practices with `gtd_managed=1` in the SQLite index (from the Manchester "
        "GTD report JSON; reviews are almost all **Manchester full_feed** rows in this dataset)."
    )
    lines.append(
        "- **Peer cohort**: non-GTD practices **UK-wide** (Manchester + national visible_cards) whose "
        "**listed Google score** falls in the same band as GTD practices (min−0.25 … max+0.25), "
        "with at least **25** reviews in the index — i.e. similarly poor **headline** ratings, not matched on text volume."
    )
    lines.append(
        "- **Themes**: access/issue regex buckets from `analyze_access_issues.py` plus takeover / GTD mention / "
        "continuity / confidentiality add-ons. Rates are **hits per 1,000 reviews**; **lift** = GTD rate ÷ peer rate."
    )
    lines.append("")
    lines.append("## Caveats")
    lines.append("")
    lines.append("- GTD **N is small** (on the order of hundreds of reviews); lifts bounce.")
    lines.append("- National peers only have **visible_cards** snippets; GTD corpus is mostly **full_feed** — "
                 "themes can be easier to hit in longer text.")
    lines.append("- Correlation ≠ causation; GTD practices may differ on unobserved factors.")
    lines.append("")

    lines.append("## Matching parameters")
    lines.append("")
    lines.append(f"- Database: `{DB_PATH}`")
    for k, v in peer_meta.items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")

    lines.append("## GTD practices (indexed)")
    lines.append("")
    lines.append("| Code | Name | Reviews | Google ★ | Avg review ★ | Low-star n |")
    lines.append("|------|------|---------|----------|--------------|------------|")
    for p in sorted(gtd_practices, key=lambda x: -x["review_n"]):
        gs = p["google_review_score"]
        lines.append(
            f"| {p['canonical_code']} | {p['practice_name'][:42]} | {p['review_n']} | "
            f"{gs if gs is not None else '—'} | {round(p['avg_stars'], 2)} | {p['low_star_n']} |"
        )
    lines.append("")

    def cohort_block(title: str, g: dict[str, Any], p: dict[str, Any], cmp_rows: list[dict[str, Any]], top_n: int = 18):
        lines.append(f"## {title}")
        lines.append("")
        lines.append(f"- GTD reviews in slice: **{g['reviews_used']}** (themes in **{g['reviews_with_any_theme']}**)")
        lines.append(f"- Peer reviews in slice: **{p['reviews_used']}** (themes in **{p['reviews_with_any_theme']}**)")
        lines.append("")
        lines.append("| Theme | GTD /1k | Peer /1k | Lift | GTD n | Peer n |")
        lines.append("|-------|---------|----------|------|-------|--------|")
        for r in cmp_rows[:top_n]:
            lift = r["lift_vs_peer"]
            lift_s = f"{lift}" if lift is not None else "—"
            lines.append(
                f"| {r['theme']} | {r['gtd_per_1k']} | {r['peer_per_1k']} | {lift_s} | "
                f"{r['gtd_count']} | {r['peer_count']} |"
            )
        lines.append("")
        lines.append("**Largest GTD lifts (interpret with caveats):**")
        for r in cmp_rows[:5]:
            if not r["lift_vs_peer"] or r["lift_vs_peer"] < 1.15:
                continue
            ex = (g.get("examples") or {}).get(r["theme"]) or []
            if not ex:
                continue
            lines.append(f"- **{r['theme']}** (lift {r['lift_vs_peer']}) — e.g. “{ex[0]}”")
        lines.append("")

    cohort_block("All star ratings", gtd_all, peer_all, cmp_all)
    cohort_block("Low star only (1–2★)", gtd_low, peer_low, cmp_low)

    if manchester_sensitivity:
        lines.append("## Sensitivity: peers restricted to Greater Manchester (non-GTD)")
        lines.append("")
        lines.append(
            f"Same GTD cohort vs **{manchester_sensitivity['peer_practice_count']}** non-GTD Manchester practices "
            f"in the Google-score band (full_feed + visible_cards)."
        )
        lines.append("")
        mg = manchester_sensitivity["cmp_low"][:12]
        lines.append("| Theme | GTD /1k | MCR peer /1k | Lift |")
        lines.append("|-------|---------|--------------|------|")
        for r in mg:
            lift = r["lift_vs_peer"]
            lines.append(
                f"| {r['theme']} | {r['gtd_per_1k']} | {r['peer_per_1k']} | {lift if lift is not None else '—'} |"
            )
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    con = sqlite3.connect(str(DB_PATH))
    con.row_factory = sqlite3.Row
    try:
        practices = practice_table(con)
        gtd_rows = [p for p in practices if p["gtd"]]
        peers, peer_meta = pick_peers(practices, gtd_rows=gtd_rows)
        if peer_meta.get("error"):
            raise SystemExit(peer_meta["error"])

        gtd_codes = {p["canonical_code"] for p in gtd_rows}
        peer_codes = {p["canonical_code"] for p in peers}

        gtd_rev = cohort_reviews(con, gtd_codes)
        peer_rev = cohort_reviews(con, peer_codes)

        gtd_all = analyze_cohort(gtd_rev, low_star_only=False)
        peer_all = analyze_cohort(peer_rev, low_star_only=False)
        gtd_low = analyze_cohort(gtd_rev, low_star_only=True)
        peer_low = analyze_cohort(peer_rev, low_star_only=True)

        cmp_all = compare_themes(gtd_all, peer_all)
        cmp_low = compare_themes(gtd_low, peer_low)

        # Manchester-only peers for sensitivity
        mcr_peer_codes = {
            p["canonical_code"]
            for p in peers
            if p["manchester_n"] > 0 and p["national_n"] == 0
        }
        manchester_sensitivity = None
        if len(mcr_peer_codes) >= 5:
            mcr_rev = cohort_reviews(con, mcr_peer_codes)
            mcr_low = analyze_cohort(mcr_rev, low_star_only=True)
            manchester_sensitivity = {
                "peer_practice_count": len(mcr_peer_codes),
                "cmp_low": compare_themes(gtd_low, mcr_low),
            }

        payload: dict[str, Any] = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "db_path": str(DB_PATH),
            "peer_matching": peer_meta,
            "gtd_practices": gtd_rows,
            "peer_practice_count": len(peers),
            "all_stars": {"gtd": gtd_all, "peer": peer_all, "comparison": cmp_all},
            "low_star": {"gtd": gtd_low, "peer": peer_low, "comparison": cmp_low},
            "manchester_peer_sensitivity": manchester_sensitivity,
        }

        OUT_DIR.mkdir(parents=True, exist_ok=True)
        json_path = OUT_DIR / "report-gtd-vs-rating-peers-nationwide.json"
        md_path = OUT_DIR / "report-gtd-vs-rating-peers-nationwide.md"
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        write_markdown(
            md_path,
            peer_meta=peer_meta,
            gtd_practices=gtd_rows,
            gtd_all=gtd_all,
            peer_all=peer_all,
            gtd_low=gtd_low,
            peer_low=peer_low,
            cmp_all=cmp_all,
            cmp_low=cmp_low,
            manchester_sensitivity=manchester_sensitivity,
        )
        print(str(md_path))
        print(str(json_path))
    finally:
        con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
