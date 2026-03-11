# GTD Greater Manchester GP Practice Reviews Dataset

Generated on 2026-03-09.

This folder contains a postcode-and-coordinates dataset for:

- all GTD Healthcare GP practice anchors listed on the GTD Healthcare GP practices page
- the broader NHS Find a GP result set returned around each GTD anchor

Files:

- `gtd_greater_manchester_gp_practices.csv`: tabular export
- `gtd_greater_manchester_gp_practices.json`: JSON export
- `summary.json`: dataset counts and source notes
- `map.html`: Leaflet map for local viewing
- `google_maps_recent_reviews.json`: raw structured Google Maps capture output
- `google_maps_manual_review.md`: ambiguous or failed captures queued for manual review
- `google-review-texts/`: per-practice text files for any captured visible Google review text
- `gtd_takeover_*` fields in the CSV/JSON: documented current-tenure GTD takeover dates plus source notes for GTD-managed practices
- `management_company_*` fields in the CSV/JSON: conservative operator identification where supported by the NHS-listed website or GTD source data
- `affiliated_group_*` fields in the CSV/JSON: separate network/federation/operator links that should not be treated as the core management company
- `registered_patient_count` in the CSV/JSON: NHS monthly registered patient total matched by ODS code
- `registered_patient_count_candidate_*` fields: advisory branch/site reconciliation matches where the direct ODS code is absent from the NHS monthly list-size file

Source basis:

- GTD Healthcare GP practices page: https://www.gtdhealthcare.co.uk/patient-services/gp-practices
- NHS Find a GP search results and profile pages: https://www.nhs.uk/service-search/find-a-gp
- Postcode geocoding: https://api.postcodes.io/
- Google review mirror used when exact matches were found: https://justvisits.co.uk/
- Registered patients totals: https://digital.nhs.uk/data-and-information/publications/statistical/patients-registered-at-a-gp-practice/february-2026
- Supplemental broader Greater Manchester search centres: M21 8AU, M22 5RX, M23 9JH, M25 1BT, M26 1LS, M27 4AA, M28 0BQ, M31 4FL, M32 0JG, M33 7ZF, M45 8WF, M50 3UB

Coverage snapshot:

- total rows: 424
- GTD-managed rows: 13
- non-GTD nearby rows: 411
- Google review coverage rows: 32
- Google Maps direct coverage rows: 0
- Review text files written: 0
- GTD takeover dates documented: 13
- Practices with management company identified: 13
- Distinct management companies identified: 1
- Practices with affiliated group identified: 0
- Distinct affiliated groups identified: 0
- Practices with registered patient count: 360
- Practices with registered patient count candidate: 0
- Google Maps scans completed: 0
- Google Maps manual review queue: 0

Caveats:

- Google review fields are partial. They were only populated when a high-confidence public mirror match could be identified.
- `gtd_takeover_*` fields reflect GTD's current-tenure start date for the GTD practices in this bundle and may use month-level precision where only month/year was published.
- `management_company_*` fields should remain blank unless the operator is identifiable from GTD source data or a clear NHS-listed website-domain grouping.
- `affiliated_group_*` fields may capture a federation, enhanced-hours operator, or similar network relationship even where the core management company is still blank.
- `registered_patient_count_candidate_*` fields should be treated as branch/site hints and should not be summed as if they were additional registered patients.
- Trustpilot fields are blank in this run because a reliable per-practice public source was not found.
- GTD's Lindley Medical Practice was matched to the NHS profile currently published as `Lindley House Health Centre` at the same Oldham site.
