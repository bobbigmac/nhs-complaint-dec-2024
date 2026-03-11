#!/usr/bin/env python3
"""
Extract GTD practices' overall-good % from GPPS practice-level CSV files.
Produces gtd_gpps_timeseries.json for the map chart when in survey mode.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
GPPS_HISTORICAL_DIR = BASE_DIR / "raw" / "gpps_historical"
OUTPUT_PATH = BASE_DIR / "output" / "gtd-greater-manchester-gp-practice-reviews-2026-03-09" / "gtd_gpps_timeseries.json"
GTD_TAKEOVER_JSON = BASE_DIR / "config" / "gtd_takeover_dates.json"

# GTD practice ODS codes (from takeover config + anchors)
GTD_CODES = {
    "Y02586", "Y02325", "Y02849", "Y02663", "P89011", "Y02713", "P89013",
    "Y02875", "Y02936", "P89612", "Y02960", "Y02520", "P89602",
}

# Map GPPS CSV column to our field; overallexp.pcteval = % describing overall experience as good
OVERALL_COL = "overallexp.pcteval"
PRACTICE_CODE_COL = "ad_practicecode"
PRACTICE_NAME_COL = "ad_practicename"


def load_gtd_names_from_markers() -> dict[str, str]:
    """Get practice names from built dataset if available."""
    markers_path = BASE_DIR / "output" / "gtd-greater-manchester-gp-practice-reviews-2026-03-09" / "gtd_greater_manchester_gp_practices.json"
    if not markers_path.exists():
        return {}
    data = json.loads(markers_path.read_text(encoding="utf-8"))
    return {str(r.get("canonical_code", "")): str(r.get("practice_name", "")) for r in data if r.get("gtd_managed")}


def extract_year_from_filename(path: Path) -> int | None:
    """e.g. GPPS_2025_Practice_data.csv -> 2025"""
    name = path.stem
    if "GPPS_" in name and "_Practice" in name:
        parts = name.replace("GPPS_", "").split("_")
        if parts:
            try:
                return int(parts[0])
            except ValueError:
                pass
    return None


def load_gpps_csv(path: Path) -> list[dict[str, str | float]]:
    rows = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if OVERALL_COL not in reader.fieldnames:
            return []
        for row in reader:
            code = (row.get(PRACTICE_CODE_COL) or "").strip()
            if not code or code not in GTD_CODES:
                continue
            raw = row.get(OVERALL_COL, "")
            try:
                val = float(raw) if raw else None
            except (TypeError, ValueError):
                val = None
            if val is not None:
                # CSV stores proportion (0-1); we use percentage (0-100)
                pct = val * 100 if val <= 1 else val
                rows.append({
                    "code": code,
                    "name": (row.get(PRACTICE_NAME_COL) or "").strip(),
                    "overall_good_percent": round(pct, 2),
                })
    return rows


def build_timeseries() -> dict:
    """Build gtd_gpps_timeseries structure for the map chart."""
    csv_files = sorted(GPPS_HISTORICAL_DIR.glob("GPPS_*_Practice_data*.csv"))
    years: list[int] = []
    by_code_year: dict[str, dict[int, float]] = {c: {} for c in GTD_CODES}
    gtd_names = load_gtd_names_from_markers()

    for path in csv_files:
        year = extract_year_from_filename(path)
        if year is None:
            continue
        rows = load_gpps_csv(path)
        if not rows:
            continue
        years.append(year)
        for r in rows:
            code = r["code"]
            by_code_year.setdefault(code, {})[year] = r["overall_good_percent"]

    years = sorted(set(years))
    takeover = {}
    if GTD_TAKEOVER_JSON.exists():
        takeover = json.loads(GTD_TAKEOVER_JSON.read_text(encoding="utf-8"))

    practice_series = []
    for code in sorted(GTD_CODES):
        data = by_code_year.get(code, {})
        points = [data.get(y) for y in years]
        if not any(p is not None for p in points):
            continue
        t = takeover.get(code, {})
        practice_series.append({
            "code": code,
            "name": gtd_names.get(code) or code,
            "points": [round(p, 2) if p is not None else None for p in points],
            "takeover_date": t.get("takeover_date", ""),
            "takeover_precision": t.get("date_precision", ""),
        })

    # Average series (mean of available practices per year)
    average_series: list[float | None] = []
    for i, y in enumerate(years):
        vals = [s["points"][i] for s in practice_series if s["points"][i] is not None]
        average_series.append(round(sum(vals) / len(vals), 2) if vals else None)

    return {
        "years": [str(y) for y in years],
        "practice_series": practice_series,
        "average_series": average_series,
        "gtd_practice_count": len(GTD_CODES),
        "practices_with_survey_history": len(practice_series),
    }


def main() -> int:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = build_timeseries()
    OUTPUT_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH} ({len(data['practice_series'])} practices, {len(data['years'])} years)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
