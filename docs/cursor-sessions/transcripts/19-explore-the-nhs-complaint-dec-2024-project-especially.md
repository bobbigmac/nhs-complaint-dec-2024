---
cursor_session: 4d1f9b00-9fff-464f-86fa-22b972597af0
source: cursor-composer
cursor_hint: ?
user_entries: 1
---

# transcript — explore-the-nhs-complaint-dec-2024-project-especially

### you

Explore the nhs-complaint-dec-2024 project (especially the datasets folder) to identify all data sources. Find where practice names, addresses, NHS identifiers, and management company names are stored. List the key files and their structure.

### assistant

# nhs-complaint-dec-2024 – Data sources and structure

## Data sources overview

| Data source | Location | Key identifiers |
|-------------|----------|-----------------|
| **Main practice dataset** | `gtd_greater_manchester_gp_practices.json` / `.csv` | `canonical_code` (ODS), `practice_name`, `postcode`, `street_address`, `management_company_name` |
| **Google Maps reviews** | `google_maps_recent_reviews.json` | `canonical_code`, `practice_name`, `postcode` |
| **Low-confidence Google captures** | `google_maps_low_confidence_records.json` | `canonical_code`, `practice_name`, `postcode` |
| **GP Patient Survey** | `gp_patient_survey_raw/*.json` | `canonical_code`, `practice_name_dataset`, `management_company_name` |
| **GTD Manchester list** | `GTD_Manchester-area_practices__postcode-first.csv` | `practice_name`, `postcode`, `pcn_name`, `borough_group`, `gtd_managed` |
| **Local practice reviews** | `some-local-practice-reviews/longsight_gp_practices_radiusish.csv` | `ods_code`, `practice_name`, `site_name`, `postcode` |

---

## 1. Main practice dataset

**Files:**  
`datasets/gtd-greater-manchester-gp-practice-reviews-2026-03-09/gtd_greater_manchester_gp_practices.json`  
`datasets/gtd-greater-manchester-gp-practice-reviews-2026-03-09/gtd_greater_manchester_gp_practices.csv`

**Fields:**

| Field | Description |
|-------|-------------|
| `practice_name` | NHS page title / practice name |
| `canonical_code` | ODS code (e.g. Y02849, P89612) |
| `nhs_profile_url` | NHS.uk GP surgery profile URL |
| `street_address` | Full street address |
| `postcode` | Postcode |
| `latitude`, `longitude` | Coordinates |
| `telephone`, `website_url` | Contact details |
| `accepting_new_patients` | Boolean |
| `gtd_managed` | Whether GTD Healthcare manages the practice |
| `gtd_site_name`, `gtd_site_url` | GTD site name and URL (if GTD-managed) |
| `management_company_name` | Operator name (GTD, SSP Health, etc.) |
| `management_company_source` | `gtd_anchor_match`, `nhs_website_domain_known_group`, `nhs_website_domain_shared` |
| `management_company_confidence` | `high` or `medium` |
| `management_company_domain` | Website domain used for identification |
| `management_company_group_size` | Number of practices under that operator |
| `google_review_score`, `google_review_count` | Google rating and count |
| `google_review_text_file` | Path to review text file (e.g. `google-review-texts/Y02849-city-health-centre.txt`) |

**Source:** Built by `build_gtd_gp_practice_dataset.py` from NHS Find a GP, GTD anchors, and supplemental search centres. Management company enrichment is done by `enrich_management_companies.py`.

---

## 2. Google Maps reviews

**File:**  
`datasets/gtd-greater-manchester-gp-practice-reviews-2026-03-09/google_maps_recent_reviews.json`

**Structure:** Array of objects, each with:

| Field | Description |
|-------|-------------|
| `practice_name` | Practice name |
| `canonical_code` | ODS code |
| `postcode` | Postcode |
| `nhs_profile_url` | NHS profile URL |
| `query` / `query_used` | Search query used |
| `google_maps_title` | Title from Google Maps |
| `google_maps_url` | Google Maps place URL |
| `google_rating`, `google_review_count` | Rating and count |
| `recent_reviews` | Array of `{author, relative_date, star_label, text, raw_card_text}` |
| `review_text_file` | Path to extracted review text file |

**Source:** Produced by `collect_google_maps_reviews.py` (Selenium/Google Maps).

---

## 3. Low-confidence Google captures

**File:**  
`datasets/gtd-greater-manchester-gp-practice-reviews-2026-03-09/google_maps_low_confidence_records.json`

Same structure as `google_maps_recent_reviews.json`, but for captures that need manual review (`manual_review_required: true` or `scan_status: manual_review_search_result_only`).

---

## 4. Google review text files

**Directory:**  
`datasets/gtd-greater-manchester-gp-practice-reviews-2026-03-09/google-review-texts/`

**Naming:** `{canonical_code}-{slugified-name}.txt` (e.g. `P91629001-north-trafford-group-practice.txt`)

**Content:** Plain text with header (practice name, code, postcode, Google Maps title, rating, count, URL) and recent reviews.

---

## 5. GP Patient Survey

**Directory:**  
`datasets/gp_patient_survey_raw/`

**Naming:** `{canonical_code}-{slugified-name}.json`

**Fields:**

| Field | Description |
|-------|-------------|
| `canonical_code` | ODS code |
| `practice_name_dataset` | Practice name |
| `practice_name_gpps`, `practice_address` | From GPPS (often empty) |
| `management_company_name` | Operator name (e.g. SSP Health) |
| `gpps_url` | GP Patient Survey results URL |
| `key_questions` | Survey metrics (e.g. `overallexp`, `lastgpapptcare`) with `practice_percent`, `ics_percent`, `national_percent` |
| `surveys_sent_out`, `surveys_sent_back`, `completion_rate_percent` | Response stats |

**Source:** Fetched by `collect_gp_patient_survey_markdown.py` from GP Patient Survey.

---

## 6. GTD Manchester practices

**File:**  
`datasets/GTD_Manchester-area_practices__postcode-first.csv`

**Fields:** `practice_name`, `postcode`, `postcode_district`, `pcn_name`, `borough_group`, `gtd_managed`

No ODS codes; used for GTD vs non-GTD classification.

---

## 7. Local practice reviews (Longsight)

**File:**  
`datasets/some-local-practice-reviews/longsight_gp_practices_radiusish.csv`

**Fields:** `practice_name`, `site_name`, `ods_code`, `address_1`, `locality`, `city`, `postcode`, `latitude`, `longitude`, `practice_website`, `cqc_overall_rating`, `healthsay_score_100`, `gpps_overall_experience_pct`, `google_review_score_estimate`, `distance_miles_from_new_bank`, etc.

---

## 8. Summary and metadata

**File:**  
`datasets/gtd-greater-manchester-gp-practice-reviews-2026-03-09/summary.json`

Contains counts (e.g. `row_count`, `gtd_managed_count`, `management_company_identified_count`), postcode areas, source URLs, and notes.

---

## Data pipeline scripts

| Script | Role |
|--------|------|
| `build_gtd_gp_practice_dataset.py` | Builds main dataset from NHS Find a GP and GTD anchors |
| `enrich_management_companies.py` | Adds management company from website domains |
| `collect_google_maps_reviews.py` | Collects Google Maps reviews via Selenium |
| `merge_google_maps_reviews.py` | Merges Google review data into main dataset |
| `collect_gp_patient_survey_markdown.py` | Fetches GP Patient Survey data |

---

## Identifiers summary

| Identifier | Primary location | Also in |
|------------|------------------|---------|
| **Practice name** | `practice_name` in main JSON/CSV | All datasets |
| **Address** | `street_address`, `postcode` in main JSON/CSV | Google reviews, GPPS (sometimes) |
| **NHS/ODS code** | `canonical_code` in main JSON/CSV | Google reviews, GPPS, `longsight_gp_practices_radiusish.csv` (`ods_code`) |
| **Management company** | `management_company_name` in main JSON/CSV | GP Patient Survey JSON files |
