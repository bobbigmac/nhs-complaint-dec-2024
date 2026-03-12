# GP Patient Survey (GPPS) – GTD subset

Bulk GPPS practice-level CSVs have been moved to `~/Downloads/nhs-gpps-stats/` (including `archive-from-repo/` for files previously in this folder). Zip that folder for archive.

**GTD subset** (13 practices, overall-good % only) is in:
- `datasets/raw/gpps_gtd_subset/` – per-year JSON and combined `gtd_gpps_all_years.json`
- `datasets/output/.../gtd_gpps_timeseries.json` – map chart timeseries

To refresh: run `python datasets/scripts/import_gpps_gtd_subset.py` (reads from `~/Downloads/nhs-gpps-stats`).
