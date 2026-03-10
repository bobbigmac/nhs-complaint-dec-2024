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
- `management_company_*` fields in the CSV/JSON: conservative operator identification where supported by the NHS-listed website or GTD source data

Source basis:

- GTD Healthcare GP practices page: https://www.gtdhealthcare.co.uk/patient-services/gp-practices
- NHS Find a GP search results and profile pages: https://www.nhs.uk/service-search/find-a-gp
- Postcode geocoding: https://api.postcodes.io/
- Google review mirror used when exact matches were found: https://justvisits.co.uk/
- Supplemental broader Greater Manchester search centres: M21 8AU, M22 5RX, M23 9JH, M25 1BT, M26 1LS, M27 4AA, M28 0BQ, M31 4FL, M32 0JG, M33 7ZF, M45 8WF, M50 3UB

Coverage snapshot:

- total rows: 355
- GTD-managed rows: 13
- non-GTD nearby rows: 342
- Google review coverage rows: 322
- Google Maps direct coverage rows: 320
- Review text files written: 282
- Practices with management company identified: 49
- Distinct management companies identified: 13
- Google Maps scans completed: 355
- Google Maps manual review queue: 3

Caveats:

- Google review fields are partial. They were only populated when a high-confidence public mirror match could be identified.
- `management_company_*` fields should remain blank unless the operator is identifiable from GTD source data or a clear NHS-listed website-domain grouping.
- Trustpilot fields are blank in this run because a reliable per-practice public source was not found.
- GTD's Lindley Medical Practice was matched to the NHS profile currently published as `Lindley House Health Centre` at the same Oldham site.
