# GP Patient Survey (GPPS) – historical practice-level data

Official NHS GP Patient Survey practice-level results for building time-series of patient satisfaction (e.g. overall experience “good” %) to compare with Google reviews over time.

## Contents

| File | Year | Format | Source |
|------|------|--------|--------|
| `GPPS_2025_Practice_data.csv` | 2025 | CSV | [gp-patient.co.uk](https://gp-patient.co.uk/latest-survey/results) |
| `GPPS_2025_Practice_results.xlsx` | 2025 | Excel | Same |
| `GPPS_2024_Practice_data.csv` | 2024 | CSV | [gp-patient.co.uk/downloads/2024/](https://gp-patient.co.uk/downloads/2024/) |
| `GPPS_2024_Practice_results.xlsx` | 2024 | Excel | Same |

**Note:** 2018–2023 practice-level files are not available at the same direct URLs. Use the [Surveys and Reports](https://www.gp-patient.co.uk/SurveysAndReports) → “Past survey results and materials” section, or the [Analysis Tool](https://gp-patient.co.uk/analysistool) (trend view since 2018), to obtain older years.

## Key columns

- **`ad_practicecode`** – ODS practice code (e.g. `P87019`, `Y02960`)
- **`ad_practicename`** – Practice name
- **`overallexp.pcteval`** – % describing overall experience as “good” (very good + fairly good)
- **`overallexp_1.pct`**, **`overallexp_2.pct`** – Very good / fairly good breakdown

## Time-series comparability

- **2024–2025:** New methodology (online-first, questionnaire changes). Comparable with each other.
- **2018–2023:** Comparable across years for most questions.
- **2018–2023 vs 2024+:** Not directly comparable due to methodology changes.

## Source URLs

- Main site: https://www.gp-patient.co.uk/
- Surveys and Reports: https://www.gp-patient.co.uk/SurveysAndReports
- Analysis Tool (trends since 2018): https://gp-patient.co.uk/analysistool
- NHS England statistics: https://www.england.nhs.uk/statistics/statistical-work-areas/patient-surveys/gp-patient-survey/

## Usage with GTD practices

Match `ad_practicecode` to your practice ODS codes (e.g. from `datasets/raw/gp_patient_survey/*.json` `canonical_code`). Use `overallexp.pcteval` as the survey “overall good %” for charts alongside Google review trends.
