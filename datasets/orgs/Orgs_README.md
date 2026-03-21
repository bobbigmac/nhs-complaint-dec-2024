# NHS Orgs Prep

This folder is a staging area for raw organisation / relationship datasets that may later help with national practice grouping, ownership-adjacent context, PCN / commissioner linkage, and provider-location joins.

It is intentionally separate from [`datasets/management_companies`](/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/management_companies), because that folder currently holds curated, claim-bearing outputs. This orgs bundle is much broader and more ambiguous: useful for exploration and cautious linking, but not something we should push straight into the core build.

Files:

- `fetch_nhs_gp_org_data.sh`: imported example fetch script from `/home/bobbigmac/Downloads/fetch_nhs_gp_org_data.sh`

Current status:

- Not wired into the main dataset build
- Not downloaded yet
- Intended as a raw prep bundle to inspect first, then selectively import later

What the script wants to pull:

- England `ods_gp`: `8` GP / branch / PCN / commissioner relationship CSV exports
- England `ods_orgs`: `13` organisation / site / partner files
- England `cqc`: `5` care-directory / rating / deactivated-location files, scraped from the CQC data page
- England `performance`: `6` workforce / payments / QOF / contract files
- Wales `statswales`: `12` files across `3` dataset codes, each with zip + XML + dimensions + dimension items
- Scotland `open-data`: `2+` scraped GP practice contact/list-size CSVs
- Northern Ireland `ods`: `5` ODS reference files
- Northern Ireland `opendatani`: `1+` scraped GP practice list-size CSVs

So the fallback minimum is about `52` data files plus `_meta` logs / source indexes and a generated bundle README. Real runs can be a little larger because the CQC, Scotland, and Northern Ireland sections scrape whatever current files are on their official pages.

Rough size signal from a few obvious large fixed files:

- `Core-GP-Contract-2024-25-csv-files.zip`: about `11.6 MB`
- `QOF2425.zip`: about `8.3 MB`
- `GPWPracticeCSV.012026.zip`: about `5.8 MB`
- `GPWIndividualCSV.012026.zip`: about `3.9 MB`
- `18_March_2026_CQC_directory.zip`: about `4.4 MB`
- `nhspaymentsgp-23-24-prac-csv.csv`: about `3.3 MB`

That means this is not a tiny helper fetch. Even before scraped extras and decompression, it is already a multi-tens-of-megabytes bundle.

What is probably useful later:

- ODS GP / branch / PCN / commissioner relationships
- ODS organisation tables for trusts, sites, independent providers, and partner mappings
- CQC provider/location linkage and historical re-registration trails
- England workforce / payments / QOF / contract context
- Wales / Scotland / NI practice population and national-structure context

What we should be careful about:

- “Associated with org X” is not the same as “managed by org X”
- PCN / commissioner / trust / provider / site links can all be real but mean different things
- Correlations at org level may be interesting without supporting any clean causal claim
- If an org attracts poorer-performing practices, that still does not by itself show the org is causing poor performance

Likely next step:

1. Run the script into a throwaway output folder when we are ready to inspect the raw bundle.
2. Inventory the columns and stable keys that actually join to our practice rows.
3. Promote only the useful slices into a narrower import step, instead of dumping the whole bundle into the main build.
