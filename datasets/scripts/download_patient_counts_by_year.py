#!/usr/bin/env python3
"""
Download NHS 'Patients Registered at a GP Practice' data for multiple years.
Extract patient counts for practices in our dataset (interest area).
Output: datasets/raw/registered_patients/patient_counts_by_year.json
"""
from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_JSON = BASE_DIR / "output" / "gtd-greater-manchester-gp-practice-reviews-2026-03-09" / "gtd_greater_manchester_gp_practices.json"
OUTPUT_JSON = BASE_DIR / "raw" / "registered_patients" / "patient_counts_by_year.json"
DOWNLOADS_DIR = Path.home() / "Downloads" / "nhs-patient-registration"
NHS_BASE = "https://digital.nhs.uk/data-and-information/publications/statistical/patients-registered-at-a-gp-practice"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"


def get_practice_codes() -> set[str]:
    """Load practice codes from our dataset (interest area)."""
    if not DATASET_JSON.exists():
        return set()
    data = json.loads(DATASET_JSON.read_text(encoding="utf-8"))
    return {str(r.get("canonical_code", "")).strip() for r in data if r.get("canonical_code")}


def fetch_page(month_slug: str) -> str:
    """Fetch publication page HTML."""
    url = f"{NHS_BASE}/{month_slug}"
    result = subprocess.run(
        ["curl", "-LfsS", "-A", USER_AGENT, "--max-time", "30", url],
        capture_output=True,
        text=True,
        timeout=35,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to fetch {url}")
    return result.stdout


def extract_download_url(html: str) -> str | None:
    """Extract gp-reg-pat-prac-all download URL from page."""
    # New: href="...gp-reg-pat-prac-all.zip" or .csv
    # Old: href="...gp-reg-pat-prac-all-jan-18.csv" etc
    m = re.search(r'href="(https://files\.digital\.nhs\.uk/[^"]*gp-reg-pat-prac-all(?:-[a-z0-9-]+)?\.(?:csv|zip))"', html)
    return m.group(1) if m else None


def download_file(url: str, dest: Path) -> bool:
    """Download file, extract CSV from zip if needed."""
    import zipfile

    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".tmp")
    result = subprocess.run(
        ["curl", "-LfsS", "-A", USER_AGENT, "--max-time", "180", "-o", str(tmp), url],
        capture_output=True,
        timeout=190,
    )
    if result.returncode != 0 or tmp.stat().st_size < 50_000:
        tmp.unlink(missing_ok=True)
        return False
    if url.endswith(".zip"):
        with zipfile.ZipFile(tmp) as zf:
            for name in zf.namelist():
                if name.lower().endswith(".csv"):
                    dest.write_bytes(zf.read(name))
                    break
            else:
                tmp.unlink(missing_ok=True)
                return False
        tmp.unlink(missing_ok=True)
    else:
        tmp.rename(dest)
    return True


def load_patient_counts_from_csv(path: Path, codes: set[str]) -> dict[str, int]:
    """Load patient counts for our practices from CSV."""
    counts = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if str(row.get("TYPE", "")).strip() != "GP":
                continue
            if str(row.get("SEX", "")).strip() != "ALL":
                continue
            if str(row.get("AGE", "")).strip() != "ALL":
                continue
            code = str(row.get("CODE", "")).strip()
            if code not in codes:
                continue
            try:
                counts[code] = int(row.get("NUMBER_OF_PATIENTS", "0") or "0")
            except (TypeError, ValueError):
                pass
    return counts


def main() -> int:
    codes = get_practice_codes()
    if not codes:
        print("No practice codes from dataset. Run build first or check DATASET_JSON.")
        return 1
    print(f"Interest area: {len(codes)} practices")

    # January snapshot per year (annual)
    years = list(range(2015, 2027))  # 2015-2026
    by_year: dict[int, dict[str, int]] = {}
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

    for year in years:
        slug = f"january-{year}"
        csv_path = DOWNLOADS_DIR / f"gp-reg-pat-prac-all-{year}.csv"
        if csv_path.exists() and csv_path.stat().st_size > 100_000:
            print(f"  {year}: using cached {csv_path.name}")
        else:
            print(f"  {year}: fetching...", end=" ", flush=True)
            try:
                html = fetch_page(slug)
                url = extract_download_url(html)
                if not url:
                    print("no gp-reg-pat link")
                    continue
                if download_file(url, csv_path):
                    print("ok")
                else:
                    print("download failed")
                    continue
            except Exception as e:
                print(f"error: {e}")
                continue

        counts = load_patient_counts_from_csv(csv_path, codes)
        by_year[year] = counts
        print(f"    -> {len(counts)} practices in our dataset")

    # Build output structure
    output = {
        "source": "NHS Digital Patients Registered at a GP Practice (January snapshot)",
        "years": sorted(by_year.keys()),
        "by_year": {str(y): by_year[y] for y in sorted(by_year.keys())},
        "practice_codes": sorted(codes),
        "practice_count": len(codes),
    }
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"\nWrote {OUTPUT_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
