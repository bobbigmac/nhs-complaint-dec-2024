# Management company watchlist report

In the Manchester tender, New Bank had 7 bids, Charlestown 6, Simpson 8, City Health Centre 11; GTD won four Manchester lots, Northern Health GPPO won Victoria Mill, Hope Citadel won Droylsden and Hawthorn, and Rochdale Health Alliance won the Bolton and HMR lots.

Dataset checked: `datasets/output/gtd-greater-manchester-gp-practice-reviews-2026-03-09/gtd_greater_manchester_gp_practices.json`

Rows in current dataset: **424**

## Tender watchlist

### Northern Health GPPO Limited

- Kind: `tender_competitor`
- Direct management matches in current dataset: **0**
- Affiliated-group matches in current dataset: **4**
- Note: Named in the tender quote as the winner for Victoria Mill.
- Note: In the current dataset this group shows up as an affiliated group, not a core management-company match.

Affiliated-group matches:
- `P84004` - Five Oaks Family Practice (M11 3BB) via affiliated_group_name
- `P84673` - Ancoats Urban Village Medical Practice (M4 6EE) via affiliated_group_name
- `P84064` - New Islington Medical Centre (M4 6EE) via affiliated_group_name
- `Y01695` - MP Victoria Mill (M40 7LH) via affiliated_group_name

Tracked practice checks:
- `Y01695` found as MP Victoria Mill (M40 7LH) - management=`-`; affiliated=`Northern Health GPPO Limited`

Candidate investigation rows:
- `P84004` found as Five Oaks Family Practice (M11 3BB); management=`-`; affiliated=`Northern Health GPPO Limited`; reason: Already tagged to Northern Health GPPO as an affiliated group in the current dataset.
- `P84673` found as Ancoats Urban Village Medical Practice (M4 6EE); management=`-`; affiliated=`Northern Health GPPO Limited`; reason: Already tagged to Northern Health GPPO as an affiliated group in the current dataset.
- `P84064` found as New Islington Medical Centre (M4 6EE); management=`-`; affiliated=`Northern Health GPPO Limited`; reason: Already tagged to Northern Health GPPO as an affiliated group in the current dataset.

### Hope Citadel Healthcare

- Kind: `tender_competitor`
- Direct management matches in current dataset: **10**
- Affiliated-group matches in current dataset: **0**
- Note: Named in the tender quote as the winner for Droylsden and Hawthorn.
- Note: The current dataset already has strong Hope Citadel management-company matches for Hawthorn and a larger Oldham/Rochdale cluster.

Direct management-company matches:
- `Y02890` - Hawthorn MC (M14 6FS) via management_company_name
- `Y02795` - Middleton Health Centre (M24 4EL) via management_company_name
- `Y02718` - Birtle View Medical Practice (OL10 4PW) via management_company_name
- `Y02721` - Kirkholt Medical Practice (OL11 2JG) via management_company_name
- `Y02720` - The Kingsway Practice (OL16 4AT) via management_company_name
- `P85614` - Village Medical Practice (OL2 8BF) via management_company_name
- `P85622` - Glodwick Medical Practice (OL4 1YN) via management_company_name
- `Y02827` - John Street Medical Practice (OL8 1DF) via management_company_name
- `Y02753` - Hill Top Surgery (OL8 2QD) via management_company_name
- `Y02933` - Hollinwood Medical Practice (OL8 3TR) via management_company_name

Tracked practice checks:
- `Y02890` found as Hawthorn MC (M14 6FS) - management=`Hope Citadel Healthcare`; affiliated=`-`
- `Y02663` found as Droylsden Medical Practice (M43 7NP) - management=`GTD Healthcare`; affiliated=`-`

### Rochdale Health Alliance

- Kind: `tender_competitor`
- Direct management matches in current dataset: **0**
- Affiliated-group matches in current dataset: **0**
- Note: Named in the tender quote as the winner for the Bolton and HMR lots.
- Note: No exact company-name match is currently present in the enriched dataset output, so this remains a live investigation item.

Tracked practice checks:
- `Bolton lot - exact practices unresolved` not found in the current catchment dataset.
- `HMR lot - exact practices unresolved` not found in the current catchment dataset.

Candidate investigation rows:
- `Y03079` found as Bolton Community Practice (BL1 8TT); management=`-`; affiliated=`-`; reason: In-catchment Bolton multi-site provider worth checking against the quoted Bolton lot.

## Auto-detected multi-practice groups already in catchment

These come from the enriched dataset itself rather than the tender quote. They are useful for competitor/context scanning.

### Management-company groups

- **SSP Health**: 10 rows
- **Hope Citadel Healthcare**: 10 rows
- **HMMG**: 5 rows
- **Tower Family Healthcare**: 4 rows
- **Salford Primary Care Together**: 4 rows

### Affiliated groups

- **Northern Health GPPO Limited**: 4 rows
- **South Manchester GP Federation Limited**: 4 rows
