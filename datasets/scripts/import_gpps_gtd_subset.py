#!/usr/bin/env python3
"""
Extract GTD practices' overall-good % from GPPS practice-level CSV files.
Reads from Downloads/nhs-gpps-stats (and archive-from-repo), outputs to datasets/raw/gpps_gtd_subset/.
Handles multiple CSV formats: ad_practicecode/overallexp.pcteval (2024+) and Practice_Code/Q28_12pct (pre-2024).
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DOWNLOADS_GPPS = Path.home() / "Downloads" / "nhs-gpps-stats"
OUTPUT_DIR = BASE_DIR / "raw" / "gpps_gtd_subset"
TIMESERIES_OUTPUT = BASE_DIR / "output" / "gtd-greater-manchester-gp-practice-reviews-2026-03-09" / "gtd_gpps_timeseries.json"
GTD_TAKEOVER_JSON = BASE_DIR / "config" / "gtd_takeover_dates.json"

GTD_CODES = {
    "Y02586", "Y02325", "Y02849", "Y02663", "P89011", "Y02713", "P89013",
    "Y02875", "Y02936", "P89612", "Y02960", "Y02520", "P89602",
}


def detect_csv_format(fieldnames: list[str]) -> tuple[str, str] | None:
    """Return (code_col, overall_col) or None if unsupported."""
    code_col = None
    for c in ("ad_practicecode", "Practice_Code", "Practice_code"):
        if c in fieldnames:
            code_col = c
            break
    if not code_col:
        return None

    if "overallexp.pcteval" in fieldnames:
        return (code_col, "overallexp.pcteval")
    if "Q28_12pct" in fieldnames:
        return (code_col, "Q28_12pct")
    return None


def extract_year_from_path(path: Path) -> int | None:
    """Extract survey year from filename."""
    name = path.stem
    # GPPS_2025_Practice_data, GPPS 2018 Practice data
    m = re.search(r"(?:GPPS[_ ])?(20\d{2})", name, re.I)
    if m:
        return int(m.group(1))
    m = re.search(r"(?:January|July|June|Dec)[a-z]*\s+(20\d{2})", name, re.I)
    if m:
        return int(m.group(1))
    m = re.search(r"(20\d{2})", name)
    if m:
        return int(m.group(1))
    return None


def load_gpps_csv(path: Path) -> list[dict]:
    """Load GTD practice rows from a GPPS CSV. Returns list of {code, name, overall_good_percent, year}."""
    rows = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fmt = detect_csv_format(reader.fieldnames or [])
        if not fmt:
            return []
        code_col, overall_col = fmt
        name_col = "ad_practicename" if "ad_practicename" in (reader.fieldnames or []) else "Practice_Name"

        year = extract_year_from_path(path)
        for row in reader:
            code = (row.get(code_col) or "").strip().upper()
            if not code or code not in GTD_CODES:
                continue
            raw = row.get(overall_col, "")
            try:
                val = float(raw) if raw else None
            except (TypeError, ValueError):
                val = None
            if val is None:
                continue
            # Normalise to 0-100: newer format uses 0-1 proportion, older may use 0-100
            pct = val * 100 if val <= 1 else val
            rows.append({
                "code": code,
                "name": (row.get(name_col) or "").strip(),
                "overall_good_percent": round(pct, 2),
                "year": year,
            })
    return rows


def collect_all_gpps_files() -> list[Path]:
    """Collect GPPS CSV paths from Downloads (including archive-from-repo)."""
    paths = []
    for base in (DOWNLOADS_GPPS, DOWNLOADS_GPPS / "archive-from-repo"):
        if not base.exists():
            continue
        for p in base.glob("*.csv"):
            if "Practice" in p.name and ("weighted" in p.name.lower() or "Practice_data" in p.name):
                paths.append(p)
    return sorted(paths, key=lambda p: (extract_year_from_path(p) or 0, p.name))


def load_gtd_names_from_markers() -> dict[str, str]:
    """Get practice names from built dataset if available."""
    markers_path = BASE_DIR / "output" / "gtd-greater-manchester-gp-practice-reviews-2026-03-09" / "gtd_greater_manchester_gp_practices.json"
    if not markers_path.exists():
        return {}
    data = json.loads(markers_path.read_text(encoding="utf-8"))
    return {str(r.get("canonical_code", "")): str(r.get("practice_name", "")) for r in data if r.get("gtd_managed")}


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    paths = collect_all_gpps_files()
    if not paths:
        print(f"No GPPS CSV files found in {DOWNLOADS_GPPS}")
        return 1

    by_code_year: dict[str, dict[int, dict]] = {c: {} for c in GTD_CODES}
    all_records: list[dict] = []

    for path in paths:
        year = extract_year_from_path(path)
        loaded = load_gpps_csv(path)
        for r in loaded:
            code = r["code"]
            yr = r.get("year") or year
            if yr:
                by_code_year.setdefault(code, {})[yr] = r  # later file overwrites if same year
            all_records.append({**r, "year": yr, "source_file": path.name})
    years = sorted({r["year"] for r in all_records if r["year"]})
    takeover = {}
    if GTD_TAKEOVER_JSON.exists():
        takeover = json.loads(GTD_TAKEOVER_JSON.read_text(encoding="utf-8"))
    gtd_names = load_gtd_names_from_markers()

    # Write per-year GTD subset (compact)
    for year in years:
        year_records = []
        for code in sorted(GTD_CODES):
            data = by_code_year.get(code, {}).get(year)
            if data:
                year_records.append({
                    "code": code,
                    "name": data.get("name") or gtd_names.get(code) or code,
                    "overall_good_percent": data["overall_good_percent"],
                })
        if year_records:
            out_path = OUTPUT_DIR / f"gtd_gpps_{year}.json"
            out_path.write_text(json.dumps(year_records, indent=2), encoding="utf-8")
            print(f"  {out_path.name}: {len(year_records)} practices")

    # Build timeseries for map chart
    practice_series = []
    for code in sorted(GTD_CODES):
        data = by_code_year.get(code, {})
        points = [data.get(y, {}).get("overall_good_percent") for y in years]
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

    average_series = []
    for i, y in enumerate(years):
        vals = [s["points"][i] for s in practice_series if s["points"][i] is not None]
        average_series.append(round(sum(vals) / len(vals), 2) if vals else None)

    timeseries = {
        "years": [str(y) for y in years],
        "practice_series": practice_series,
        "average_series": average_series,
        "gtd_practice_count": len(GTD_CODES),
        "practices_with_survey_history": len(practice_series),
    }
    TIMESERIES_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    TIMESERIES_OUTPUT.write_text(json.dumps(timeseries, indent=2), encoding="utf-8")

    # Write combined GTD subset (all years, one file)
    by_year_records = {}
    for y in years:
        recs = []
        for c in sorted(GTD_CODES):
            d = by_code_year.get(c, {}).get(y)
            if d:
                recs.append({"code": c, "name": d.get("name", ""), "overall_good_percent": d["overall_good_percent"]})
        by_year_records[str(y)] = recs
    combined = {"years": years, "by_year": by_year_records, "practice_codes": sorted(GTD_CODES)}
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "gtd_gpps_all_years.json").write_text(json.dumps(combined, indent=2), encoding="utf-8")

    print(f"\nWrote {OUTPUT_DIR}/ ({len(years)} years)")
    print(f"Wrote {TIMESERIES_OUTPUT} (map chart timeseries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
