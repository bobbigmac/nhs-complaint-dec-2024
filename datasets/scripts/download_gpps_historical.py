#!/usr/bin/env python3
"""
Attempt to download GPPS practice-level data for 2018-2023.
Known working: 2024, 2025. Older years may require manual download from
https://www.gp-patient.co.uk/SurveysAndReports → Past survey results.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = BASE_DIR / "raw" / "gpps_historical"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"

URLS = [
    # downloads/ path (works for 2024)
    ("{year}", "https://gp-patient.co.uk/downloads/{year}/GPPS_{year}_Practice_data_(weighted)_(csv)_PUBLIC.csv"),
    # FileDownload redirect (works for 2025)
    ("{year}_fd", "https://gp-patient.co.uk/FileDownload/Download?fileRedirect={year}%2Fsurvey-results%2Fpractice-results%2Fpractice-data-csv%2FGPPS_{year}_Practice_data_(weighted)_(csv)_PUBLIC.csv"),
]


def download(url: str, dest: Path) -> bool:
    result = subprocess.run(
        ["curl", "-LfsS", "-A", USER_AGENT, "-o", str(dest), url],
        capture_output=True,
        timeout=120,
    )
    if result.returncode != 0:
        return False
    if dest.stat().st_size < 5000:
        return False
    text = dest.read_text(encoding="utf-8", errors="replace")[:500]
    if "<!DOCTYPE" in text or "<html" in text.lower():
        return False
    return True


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for year in range(2023, 2017, -1):
        dest = OUT_DIR / f"GPPS_{year}_Practice_data.csv"
        if dest.exists() and dest.stat().st_size > 100_000:
            print(f"{year}: already have {dest.name} ({dest.stat().st_size:,} bytes)")
            continue
        for suffix, template in URLS:
            url = template.format(year=year)
            print(f"{year}: trying {suffix}...", end=" ")
            if download(url, dest):
                print(f"OK ({dest.stat().st_size:,} bytes)")
                break
            print("404 or invalid")
        else:
            print(f"{year}: not found. Manual: Surveys and Reports → Past → {year}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
