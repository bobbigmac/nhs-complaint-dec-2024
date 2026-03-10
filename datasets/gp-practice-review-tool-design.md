# GP Practice Review Tool Design

Last updated: 2026-03-10

## Goal

Build a reproducible dataset and map for Greater Manchester GP practices that can answer two related questions:

1. Are review outcomes more associated with management companies or provider groups?
2. Are review outcomes more associated with local area conditions outside management control?

The current tool already captures:

- NHS GP practice entries and coordinates
- GTD-managed practice tagging
- partial Google review scores
- recent visible Google review text snippets
- a static Leaflet map

The next phase should add:

- public area-level overlays
- management-company attribution for all practices
- a cleaner analysis layer for group-vs-place comparisons

## Current map and why overlays are feasible

The current frontend is a generated static Leaflet map in [map.html](/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/gtd-greater-manchester-gp-practice-reviews-2026-03-09/map.html). That makes public overlays straightforward.

There are two practical ways to add them:

1. Enrich each practice row with area metrics and keep the map point-based.
2. Add polygon overlays for LSOA/MSOA/ward areas and render choropleths in Leaflet.

Recommendation:

- Start with per-practice enrichment first.
- Add polygons second.

Reason:

- It is much lighter in the browser.
- It keeps the current map simple.
- It is enough for early analysis and report writing.
- We can still add choropleths later once we have stable area joins.

## Recommended public overlays

These are the highest-value overlays that are public, official, and practical to join.

### Boundary and lookup source for overlays

Recommended source:

- ONS statistical geographies guidance and Open Geography portal lookup products.
- Source: https://www.ons.gov.uk/methodology/geography/ukgeographies/statisticalgeographies
- Lookup guidance: https://www.ons.gov.uk/methodology/geography/geographicalproducts/namescodesandlookups/lookups

Why it matters:

- This is the cleanest way to get current `LSOA 2021` and `MSOA 2021` names, codes and boundaries.
- It supports both offline joins and later choropleth overlays.

### 1. Deprivation

Recommended unit: `LSOA`

Recommended source:

- English Indices of Deprivation 2025, published 30 October 2025, with updated collection page on 30 October 2025 and spatial resources available.
- Source: https://www.gov.uk/government/collections/english-indices-of-deprivation
- Latest release page: https://www.gov.uk/government/statistics/english-indices-of-deprivation-2025

Why it matters:

- Best single small-area summary of structural disadvantage.
- Likely strongest candidate for regional explanation of poor reviews.
- Also has useful domains, not just overall IMD rank/decile.

Fields to keep:

- `imd_2025_rank`
- `imd_2025_decile`
- `income_deprivation_rank`
- `employment_deprivation_rank`
- `health_deprivation_rank`
- `education_deprivation_rank`
- `crime_deprivation_rank`
- `housing_barriers_rank`
- `living_environment_rank`

### 2. Population density

Recommended unit: `LSOA`

Recommended source:

- ONS Lower layer Super Output Area population density dataset, release dated 07 November 2025.
- Source: https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/lowersuperoutputareapopulationdensity

Why it matters:

- Useful proxy for urban intensity and demand pressure.
- Easy to explain on maps.
- Small-area and current enough for this use.

Fields to keep:

- `lsoa_population_density_latest`
- `lsoa_population_latest`
- `lsoa_area_sq_km`

### 3. Income

Recommended unit: `MSOA`

Recommended source:

- ONS Income estimates for small areas, England and Wales: financial year ending 2023, released 10 December 2025.
- Source: https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/smallareamodelbasedincomeestimates/financialyearending2023

Why it matters:

- Stronger direct economic signal than deprivation alone.
- Better for separating affluence from service quality perception.

Important caveat:

- ONS notes these are model-based estimates and rankings are more reliable than exact values at extremes.

Fields to keep:

- `msoa_mean_equivalised_income_bhc`
- `msoa_mean_equivalised_income_ahc`
- `msoa_income_source_year`

### 4. House prices

Recommended unit: derived `LSOA`, `MSOA`, or rolling postcode-area aggregates

Recommended source:

- HM Land Registry Price Paid Data, updated monthly on the 20th working day of the month.
- Source: https://www.gov.uk/government/statistical-data-sets/price-paid-data-downloads

Why it matters:

- Useful market proxy for affluence and urban change.
- Can be summarised locally even if no direct official ready-made LSOA file is used.

Recommended derived metrics:

- `median_sale_price_3y_lsoa_or_nearby`
- `sale_count_3y_lsoa_or_nearby`
- `price_source_window_start`
- `price_source_window_end`

Recommendation:

- Do not try to load raw nationwide price paid data in the browser.
- Precompute local medians offline.

## Other relevant public data worth adding later

These are not essential for the first overlay pass but are likely relevant to the group-vs-place question.

### Practice-scale operational data

- GP Patient Survey 2025 practice results
  Source: https://www.england.nhs.uk/statistics/statistical-work-areas/patient-surveys/gp-patient-survey/
- General Practice Workforce statistics
  Source: https://digital.nhs.uk/data-and-information/publications/statistical/general-and-personal-medical-services
- NHS Payments to General Practice
  Source: https://digital.nhs.uk/data-and-information/publications/statistical/nhs-payments-to-general-practice
- Patients registered at a GP practice / list size
  Use current NHS practice-level registration statistics if added in a later pass

Why these matter:

- They provide demand, staffing and financial context.
- They may explain review outcomes better than area factors alone.

### Demographic context

- Census 2021 age structure
- long-term illness / disability
- ethnicity
- car access
- housing tenure

These are useful but should be added after the first overlay pass because they increase scope quickly.

## Management-company attribution

This is the most important missing dataset after broader practice coverage.

### Recommended primary source

- CQC provider and location data
- CQC says its API includes active and inactive providers and locations, linked organisations, service types and latest ratings, and that the API data is updated daily.
- CQC also publishes a complete list of regulated locations weekly and ratings files monthly.
- Source: https://www.cqc.org.uk/about-us/transparency/using-cqc-data

Why this should be primary:

- CQC provider is usually the legal entity running the service.
- This is closer to the management-company concept than public-facing practice brand names.
- It also gives takeover/history context.

Recommended output fields:

- `cqc_location_id`
- `cqc_provider_id`
- `cqc_provider_name`
- `cqc_provider_type`
- `cqc_location_name`
- `cqc_location_rating`
- `cqc_provider_rating`
- `cqc_last_inspection_date`
- `cqc_location_url`

### Recommended secondary source

- NHS Organisation Data Service
- Preferred current route: Organisation Data Terminology FHIR R4 API
- ODS API guidance: https://digital.nhs.uk/services/organisation-data-service/news-and-alerts/latest-news
- ORD API catalogue page: https://digital.nhs.uk/developer/api-catalogue/organisation-data-service-ord

Why it is still useful:

- ODS is the canonical organisational identifier layer.
- NHS England is encouraging migration toward the Organisation Data Terminology FHIR R4 API, which now combines content previously split across older ODS APIs.
- ORD remains useful where existing tooling already depends on it.
- ODS data is still the right place for practice code resolution, succession and joins to other NHS datasets.

Recommended output fields:

- `ods_code`
- `ods_name`
- `ods_status`
- `ods_org_type`
- `ods_parent_org_code`
- `ods_relationship_summary`

### Management-group normalisation

We will need a derived field because legal provider names are often inconsistent.

Recommended derived fields:

- `manager_entity_name_raw`
- `manager_entity_name_normalized`
- `manager_group_id`
- `manager_group_name`
- `manager_group_source`
- `manager_group_confidence`

### Current repo field contract

Until a fuller CQC/ODS pipeline is added, this repo should populate these practice-level fields:

- `management_company_name`
- `management_company_source`
- `management_company_confidence`
- `management_company_domain`
- `management_company_group_size`

Current conservative precedence:

1. explicit GTD anchor match
2. shared NHS-listed website domain that clearly identifies a multi-practice group
3. later CQC/ODS provider mapping

Rules for future dataset enrichments:

- prefer blank over guessed
- always set `management_company_source`
- always set `management_company_confidence`
- if the value comes from the NHS-listed website, keep the domain in `management_company_domain`
- recompute `management_company_group_size` after every enrichment pass
- do not overwrite a higher-confidence source with a lower-confidence one

Examples:

- one provider may appear with `Ltd`, `Limited`, partnership wording, or slightly different punctuation
- location names may differ from provider legal names

This should be handled in a small normalization table checked by hand.

## Data model

Keep the model split into three layers.

### 1. Practice table

One row per NHS GP practice entry.

Core fields:

- practice identity
- coordinates
- NHS URLs
- Google review metrics
- management attribution
- joined area codes

Recommended new geography fields:

- `lsoa21_code`
- `lsoa21_name`
- `msoa21_code`
- `msoa21_name`
- `lad_code`
- `lad_name`
- `icb_code`
- `icb_name`

### 2. Area tables

Separate tables keyed by area code.

Recommended tables:

- `lsoa_metrics.csv`
- `msoa_metrics.csv`

This avoids repeating the same deprivation and density numbers hundreds of times in every downstream export.

### 3. Review text corpus

Keep review texts outside the main CSV, as already started.

Recommended additions:

- one metadata index file listing review text files
- simple derived complaint tags later

## Joining strategy

Recommended order:

1. Practice postcode and lat/lon
2. Use postcode lookup or point-in-polygon to assign `LSOA` and `MSOA`
3. Join area metrics
4. Join management-company fields
5. Derive grouped analytics

Practical note:

- `postcodes.io` already exposes postcode geography fields including `lsoa`
- for robust long-term joining, storing official 2021 area codes is better than only storing names

## Frontend design direction

The existing map should become a small exploration interface, not just a marker plot.

### Minimum useful additions

- layer switcher for `Google rating`, `IMD`, `income`, `population density`, `house prices`
- toggle between `point colouring` and `area choropleth`
- filters for `management group`, `GTD only`, `manual review only`, `has Google text`, `postcode area`
- popup showing practice, management group, key area metrics, Google metrics, CQC rating if available

### Recommended visual rules

- keep practice markers visible above overlays
- use muted polygons and stronger point markers
- area overlays should be optional, not always on
- default view should remain understandable without any overlay enabled

### Performance recommendation

- first pass: no browser-side shapefile parsing
- pre-export GeoJSON clipped to the Greater Manchester study area
- if needed later, move to vector tiles

## Analysis approach for management vs area effects

Do not jump straight to one regression and treat it as definitive.

Use a staged approach.

### Stage 1. Descriptive

- average review score by management group
- average review score by LSOA/MSOA deprivation decile
- review count distribution by management group
- complaint-term frequencies by group and by area decile

### Stage 2. Cross-tabs that reduce obvious confounding

- compare management groups within similar deprivation bands
- compare practices within the same borough or ICB
- compare same management group across higher- and lower-deprivation areas

### Stage 3. Hierarchical modelling

Candidate model:

- outcome: Google rating, low-star share, or complaint-topic prevalence
- fixed effects: deprivation, income, density, house prices, list size, staffing, contract type
- random effects: management group and area

This is the point where we can start estimating whether group effects remain after area adjustment.

## Risks and caveats

- Google review coverage is partial and non-random.
- Low-review practices can produce noisy averages.
- Reviewers are a selected population, not all patients.
- Area measures are contextual, not patient-specific.
- Management structure changes over time.
- CQC provider and NHS ODS organisation may not align perfectly one-to-one.
- Some branch/site entries may not reflect the same operational unit for all datasets.

## Recommended next implementation steps

1. Add geography fields to the practice dataset: `LSOA`, `MSOA`, `LAD`, `ICB`.
2. Add an `area_metrics` build step using IMD 2025, ONS density, ONS income, and derived house-price metrics.
3. Add CQC provider/location ingestion for GP services.
4. Build a small management-group normalization table.
5. Extend the map with one overlay toggle and one popup summary first.
6. Add a first analytical export:
   `practice_with_context.csv`
7. Add a second grouped export:
   `management_group_summary.csv`

## Initial decision log

- Use official public datasets wherever possible.
- Prefer offline joins over live browser calls.
- Keep review text outside the main CSV.
- Treat CQC provider as the leading candidate for management company.
- Treat ODS as the canonical organisation key layer.
- Start with per-practice overlay fields before full choropleth rendering.
