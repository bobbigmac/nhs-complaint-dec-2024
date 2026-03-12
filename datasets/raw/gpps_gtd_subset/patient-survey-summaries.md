# GP Patient Survey – GTD practices subset

Overall-experience-as-good % for the 13 GTD Healthcare practices, extracted from NHS GP Patient Survey practice-level data.

## Contents

- `gtd_gpps_YYYY.json` – per-year records (code, name, overall_good_percent)
- `gtd_gpps_all_years.json` – combined by year
- Map chart timeseries: `../output/.../gtd_gpps_timeseries.json`

## Source

Bulk GPPS CSVs in `~/Downloads/nhs-gpps-stats/`. Run `python datasets/scripts/import_gpps_gtd_subset.py` to refresh.

## Practice codes

Y02586, Y02325, Y02849, Y02663, P89011, Y02713, P89013, Y02875, Y02936, P89612, Y02960, Y02520, P89602
