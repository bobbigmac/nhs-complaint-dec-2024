# Management company watchlist report

In the Manchester tender, New Bank had 7 bids, Charlestown 6, Simpson 8, City Health Centre 11; GTD won four Manchester lots, Northern Health GPPO won Victoria Mill, Hope Citadel won Droylsden and Hawthorn, and Rochdale Health Alliance won the Bolton and HMR lots.

Dataset checked: `datasets/output/gtd-greater-manchester-gp-practice-reviews-2026-03-09/gtd_greater_manchester_gp_practices.json`

Rows in current dataset: **424**

## Known operator profiles

### GTD Healthcare

- Kind: `anchor_operator`
- Source strength: `profiled_from_repo_notes`
- Direct management matches in current dataset: **14**
- Affiliated-group matches in current dataset: **0**
- Summary: Main anchor operator for this project: a not-for-profit, social-enterprise-style provider with GP practices, urgent care, central triage/co-ordination functions, and wider commissioned services.
- Legal / organisational shape: Publicly presented as a not-for-profit, values-led organisation with a social enterprise ethos; Our People's Trust is presented as the single shareholder.
- Relationship to GTD: Anchor entry.
- Why it matters: This is the provider running New Bank and the main reference point for the org navigator, competitor comparison and pressure mapping work.
- Note: The repo-local inquiry and operating-environment notes show GTD as more than a surgery chain: it also has a 24/7 clinical/co-ordination layer, referral triage functions and rapid-mobilisation work.
- Note: The same notes also place GTD inside GMUPCA and wider regional procurement / risk-bearing patterns.

Direct management-company examples in current dataset:
- `Y02849` - City Health Centre (M1 1PL) via management_company_name
- `Y02960` - New Bank Health (M12 4JE) via management_company_name
- `Y02713` - Guide Bridge Medical Practice (M34 5HY) via management_company_name
- `Y02520` - Simpson Medical Practice (M40 9NB) via management_company_name
- `Y02663` - Droylsden Medical Practice (M43 7NP) via management_company_name
- `Y02325` - Charlestown MD (M9 7ED) via management_company_name
- `Y02875` - Lindley House Health Centre (OL1 1NL) via management_company_name
- `P89612` - Mossley Medical Practice (OL5 9AB) via management_company_name
- ... plus **6** more direct matches

Key sources:
- https://www.gtdhealthcare.co.uk/about-us
- https://www.gtdhealthcare.co.uk/about-us/our-peoples-trust
- https://www.gtdhealthcare.co.uk/about-us/leadership-team
- https://www.gtdhealthcare.co.uk/corporate
- https://www.gtdhealthcare.co.uk/corporate/referral-gateway-clinical-triage-service
- https://www.gtdhealthcare.co.uk/corporate/patient-safety-incident-response-framework

### GoToDoc Limited

- Kind: `provider_shell`
- Source strength: `profiled_from_repo_notes`
- Direct management matches in current dataset: **0**
- Affiliated-group matches in current dataset: **0**
- Summary: Registered-provider shell used in the public record for GTD-run services even where procurement documents name GTD Healthcare Ltd as contract holder.
- Legal / organisational shape: Active company / provider shell visible in Companies House and CQC records.
- Relationship to GTD: Corporate delivery entity / registered-provider layer inside the GTD structure.
- Why it matters: The New Bank trail repeatedly splits contract award, CQC registration and corporate identity across GTD Healthcare Ltd and GoToDoc Ltd.
- Note: This is part of why 'who won the contract?' and 'who runs the service?' are not always answered by the same legal entity in public records.

Key sources:
- https://find-and-update.company-information.service.gov.uk/company/06504010
- https://www.cqc.org.uk/location/1-2373622046

### Better Health Manchester

- Kind: `previous_operator`
- Source strength: `repo_local_context_only`
- Direct management matches in current dataset: **0**
- Affiliated-group matches in current dataset: **0**
- Summary: Previous operator context for New Bank before the April 2025 move to GTD.
- Legal / organisational shape: Previous provider context in repo-local handover notes; external profile is not yet fully curated in this folder.
- Relationship to GTD: Outgoing provider at New Bank.
- Why it matters: The org navigator will need to show that New Bank's current issues sit inside a longer operator history rather than starting from zero on 1 April 2025.
- Note: Useful mainly as handover context and for separating pre-GTD from post-GTD evidence.

### Northern Health GPPO Limited

- Kind: `federation_provider_peer`
- Source strength: `profiled_from_repo_notes`
- Direct management matches in current dataset: **0**
- Affiliated-group matches in current dataset: **4**
- Summary: North Manchester GP federation and not-for-profit membership organisation that appears both as a federation layer and as a real peer / tender actor.
- Legal / organisational shape: Not-for-profit GP federation / membership organisation.
- Relationship to GTD: Competitor in Manchester APMS / SAS contexts; collaborator-adjacent in the wider Manchester provider ecosystem.
- Why it matters: It won Victoria Mill in the Manchester APMS round and later took over Manchester SAS work from GTD.
- Note: In the current dataset it appears as an affiliated group rather than a direct management-company match.
- Note: This is one of the clearest examples of a body that is not just 'near GTD' but is an actual substitute / alternative operator in some commissioner decisions.

Affiliated-group examples in current dataset:
- `P84004` - Five Oaks Family Practice (M11 3BB) via affiliated_group_name
- `P84673` - Ancoats Urban Village Medical Practice (M4 6EE) via affiliated_group_name
- `P84064` - New Islington Medical Centre (M4 6EE) via affiliated_group_name
- `Y01695` - MP Victoria Mill (M40 7LH) via affiliated_group_name

Tracked practice checks:
- `Y01695` found as MP Victoria Mill (M40 7LH) - management=`-`; affiliated=`Northern Health GPPO Limited`

Key sources:
- https://www.nhgppo.co.uk/
- https://manchesterpcp.co.uk/members.php/1000
- https://gmintegratedcare.org.uk/wp-content/uploads/2025/05/20250522-manchester-primary-care-commissioning-committee.pdf

### Primary Care Manchester Ltd

- Kind: `federation_provider_peer`
- Source strength: `profiled_from_repo_notes`
- Direct management matches in current dataset: **0**
- Affiliated-group matches in current dataset: **2**
- Summary: Central Manchester GP-practice company/federation layer that sits underneath Manchester Primary Care Partnership.
- Legal / organisational shape: Company of Central Manchester GP practices / shareholder-style federation structure.
- Relationship to GTD: Part of the same city-scale provider environment rather than a simple one-to-one competitor.
- Why it matters: It helps explain how Manchester's provider world is built from practice-backed federations and scale vehicles rather than only direct operator chains.
- Note: In the current dataset it appears as an affiliated group rather than a direct management-company label.

Affiliated-group examples in current dataset:
- `P84009` - Ailsa Craig Medical Centre (M13 0YL) via affiliated_group_name
- `P84068` - Chorlton Family Practice (M21 9NJ) via affiliated_group_name

Key sources:
- https://www.cmgppo.org.uk/
- https://www.cmgppo.org.uk/aboutus.html
- https://manchesterpcp.co.uk/about.php

### South Manchester GP Federation Limited

- Kind: `federation_provider_peer`
- Source strength: `profiled_from_repo_notes`
- Direct management matches in current dataset: **0**
- Affiliated-group matches in current dataset: **4**
- Summary: South Manchester membership/shareholder federation with visible service-delivery activity as well as representative/federation functions.
- Legal / organisational shape: Membership organisation where South Manchester practices are shareholders.
- Relationship to GTD: Peer federation / potential collaborator-competitor inside the same Manchester provider landscape.
- Why it matters: It is one of the three federations behind Manchester Primary Care Partnership and appears in the dataset as an affiliated-group signal.

Affiliated-group examples in current dataset:
- `P84034` - Barlow Medical Centre (M20 2RN) via affiliated_group_name
- `P84043` - Cornishway Group Practice (M22 5RX) via affiliated_group_name
- `P84021` - THE MAPLES MEDICAL CENTRE (M23 2SY) via affiliated_group_name
- `P84045` - The Park Medical Centre (M23 9AB) via affiliated_group_name

Key sources:
- https://smgpf.ltd/about-us
- https://smgpf.ltd/services
- https://manchesterpcp.co.uk/about.php

### Manchester Primary Care Partnership

- Kind: `city_scale_vehicle`
- Source strength: `profiled_from_repo_notes`
- Direct management matches in current dataset: **0**
- Affiliated-group matches in current dataset: **0**
- Summary: Manchester-wide not-for-profit provider vehicle owned by the three Manchester GP federations.
- Legal / organisational shape: Not-for-profit scale/service-delivery vehicle.
- Relationship to GTD: Not a direct GTD subsidiary or direct rival in a simple sense; part of the city-scale structure around Manchester primary care.
- Why it matters: Important for the org navigator because it shows how city-wide service capacity and contract capability can sit above federation level.

Key sources:
- https://manchesterpcp.co.uk/about.php
- https://manchesterpcp.co.uk/members.php/1000

### Salford Primary Care Together

- Kind: `peer_operator`
- Source strength: `profiled_from_repo_notes`
- Direct management matches in current dataset: **4**
- Affiliated-group matches in current dataset: **0**
- Summary: CIC-style membership/service provider that appears both as a direct operator in the current dataset and as a GMUPCA-linked peer.
- Legal / organisational shape: Community Interest Company / membership organisation / service provider.
- Relationship to GTD: Peer urgent/community/primary-care operator and GMUPCA partner.
- Why it matters: One of the clearest non-GTD peers that crosses from organisational-shape notes into current-dataset management-company matches.

Direct management-company examples in current dataset:
- `Y00445002` - Salford Primary Care Together - Little Hulton (M28 0AY) via management_company_name
- `Y00445` - Salford Primary Care Together (M28 0BB) via management_company_name
- `Y00445001` - Salford Primary Care Together - Eccles Gateway (M30 0TU) via management_company_name
- `Y00445003` - SPCT - Inclusion Service (M6 5PL) via management_company_name

Key sources:
- https://find-and-update.company-information.service.gov.uk/company/07227455
- https://www.salfordprimarycaretogether.co.uk/about
- https://gmupca.co.uk/about-us/

### Mastercall Healthcare

- Kind: `peer_operator`
- Source strength: `profiled_from_repo_notes`
- Direct management matches in current dataset: **0**
- Affiliated-group matches in current dataset: **0**
- Summary: Greater Manchester social-enterprise-style urgent/community care peer with a long co-operative history.
- Legal / organisational shape: Publicly described as a social enterprise; public material also describes it as a company limited by guarantee.
- Relationship to GTD: Urgent/community care peer and GMUPCA partner.
- Why it matters: Useful for showing that GTD sits among other risk-bearing, not-for-profit / social-enterprise operators rather than only against classic private chains.

Key sources:
- https://mastercall.org.uk/about-us/
- https://mastercall.org.uk/
- https://gmupca.co.uk/meet-the-team/

### Bardoc

- Kind: `peer_operator`
- Source strength: `profiled_from_repo_notes`
- Direct management matches in current dataset: **0**
- Affiliated-group matches in current dataset: **0**
- Summary: Long-established Greater Manchester urgent/community care provider positioned as a community-benefit, not-for-profit social enterprise.
- Legal / organisational shape: Community Benefit Society / not-for-profit social enterprise.
- Relationship to GTD: Peer urgent/community care operator and GMUPCA partner.
- Why it matters: Another important comparator for the 'industry shape' page because it shows the same non-profit/community-benefit layer that sits around GTD.

Key sources:
- https://www.bardoc.co.uk/
- https://www.bardoc.co.uk/who-we-are/
- https://gmupca.co.uk/meet-the-team/

### Wigan GP Alliance

- Kind: `peer_operator`
- Source strength: `profiled_from_repo_notes`
- Direct management matches in current dataset: **0**
- Affiliated-group matches in current dataset: **0**
- Summary: Borough-wide alliance layer in Wigan that shows up in the same wider urgent/community provider network as GTD.
- Legal / organisational shape: Alliance layer; public privacy material ties the website to Wigan GP Alliance LLP.
- Relationship to GTD: GMUPCA partner / peer operator layer.
- Why it matters: Useful in the org navigator as another example of alliance-led, borough-scale provider shape.

Key sources:
- https://www.wigangpalliance.org/home
- https://www.wigangpalliance.org/privacypolicy
- https://gmupca.co.uk/about-us/

### Hope Citadel Healthcare

- Kind: `peer_operator`
- Source strength: `mixed_repo_notes_and_dataset`
- Direct management matches in current dataset: **10**
- Affiliated-group matches in current dataset: **0**
- Summary: Direct multi-practice comparator already visible as a strong management-company cluster in the current dataset and named in the Manchester tender outcome discussion.
- Legal / organisational shape: External organisational profile is thinner in this folder than GTD/NHGPPO/SPCT, but it is a clearly recurring operator label in the current dataset and repo notes.
- Relationship to GTD: Tender competitor and current-dataset comparator cluster.
- Why it matters: It won Hawthorn and Droylsden in the cited Manchester tender context and provides one of the closest non-GTD comparison groups in the current dataset.
- Note: The current dataset already has strong direct management-company matches for this group.

Direct management-company examples in current dataset:
- `Y02890` - Hawthorn MC (M14 6FS) via management_company_name
- `Y02795` - Middleton Health Centre (M24 4EL) via management_company_name
- `Y02718` - Birtle View Medical Practice (OL10 4PW) via management_company_name
- `Y02721` - Kirkholt Medical Practice (OL11 2JG) via management_company_name
- `Y02720` - The Kingsway Practice (OL16 4AT) via management_company_name
- `P85614` - Village Medical Practice (OL2 8BF) via management_company_name
- `P85622` - Glodwick Medical Practice (OL4 1YN) via management_company_name
- `Y02827` - John Street Medical Practice (OL8 1DF) via management_company_name
- ... plus **2** more direct matches

Tracked practice checks:
- `Y02890` found as Hawthorn MC (M14 6FS) - management=`Hope Citadel Healthcare`; affiliated=`-`
- `Y02663` found as Droylsden Medical Practice (M43 7NP) - management=`GTD Healthcare`; affiliated=`-`

### Rochdale Health Alliance

- Kind: `peer_operator`
- Source strength: `tender_quote_plus_partial_repo_notes`
- Direct management matches in current dataset: **0**
- Affiliated-group matches in current dataset: **0**
- Summary: Named in the inquiry/tender synthesis as a winner for Bolton and HMR lots, but still thinly resolved in the current dataset work.
- Legal / organisational shape: Public peer/provider layer; exact local mapping still needs pinning down in this repo.
- Relationship to GTD: Tender competitor / alternate provider layer.
- Why it matters: Important because it shows the Manchester-area contract market is not just GTD versus one rival; there is a wider repeat-operator field.
- Note: Exact practice mapping for the quoted Bolton and HMR lots still needs cleaning up.

Tracked practice checks:
- `Bolton lot - exact practices unresolved` not found in the current catchment dataset.
- `HMR lot - exact practices unresolved` not found in the current catchment dataset.

### SSP Health

- Kind: `dataset_multi_practice_group`
- Source strength: `dataset_cluster_only`
- Direct management matches in current dataset: **10**
- Affiliated-group matches in current dataset: **0**
- Summary: Large non-GTD multi-practice management-company cluster already visible inside the current dataset.
- Legal / organisational shape: External organisational profile not yet curated in this folder; current knowledge is primarily from the enriched dataset and scattered repo mentions.
- Relationship to GTD: Comparator cluster rather than a heavily profiled GTD-adjacent institution in repo notes.
- Why it matters: It is one of the largest non-GTD management-company clusters in the current catchment, so the org navigator should expose it even before the external profile is deepened.
- Note: Keep this visible, but avoid overstating organisational claims until the external profile is fleshed out.

Direct management-company examples in current dataset:
- `Y02319` - Bolton General Practice (BL1 4TH) via management_company_name
- `P82613` - Spring View Medical Centre (BL3 1HQ) via management_company_name
- `P82609` - Shanti Medical Centre (BL3 3PH) via management_company_name
- `Y00186` - 3D Medical Centre (BL3 5DP) via management_company_name
- `Y02790` - Bolton Medical Centre (BL3 6PY) via management_company_name
- `P92637` - Astley General Practice (M29 7BY) via management_company_name
- `Y02321` - Poplar Street Surgery (M29 8AX) via management_company_name
- `Y02767` - The Height General Practice (M6 7NJ) via management_company_name
- ... plus **2** more direct matches

### Tower Family Healthcare

- Kind: `dataset_multi_practice_group`
- Source strength: `dataset_cluster_only`
- Direct management matches in current dataset: **4**
- Affiliated-group matches in current dataset: **0**
- Summary: Distinct multi-site operator cluster visible in the current dataset.
- Legal / organisational shape: External organisational profile not yet curated in this folder.
- Relationship to GTD: Comparator cluster in the same broad regional practice-management space.
- Why it matters: Useful for showing that the dataset contains more than one repeat operator footprint beyond GTD and Hope Citadel.

Direct management-company examples in current dataset:
- `P83012` - Tower Family Healthcare (BL8 4AD) via management_company_name
- `P83012002` - Tower Family Healthcare - Greenmount (BL8 4DR) via management_company_name
- `W4J3Q` - Tower Family Healthcare Minden (BL9 0NJ) via management_company_name
- `P83012001` - Tower Family Healthcare - Spring Lane (M26 2TQ) via management_company_name

### HMMG

- Kind: `dataset_multi_practice_group`
- Source strength: `dataset_cluster_only`
- Direct management matches in current dataset: **5**
- Affiliated-group matches in current dataset: **0**
- Summary: Distinct multi-practice group label already visible in the current dataset.
- Legal / organisational shape: Current repo knowledge is mainly the dataset label and practice footprint; external organisational profile remains to be curated.
- Relationship to GTD: Comparator cluster.
- Why it matters: Should appear in the navigator because it is one of the stronger non-GTD management-company clusters in the catchment.

Direct management-company examples in current dataset:
- `P88026004` - Little Moor Surgery (SK2 5AR) via management_company_name
- `P88026005` - Bosden Moor Surgery (SK2 5JL) via management_company_name
- `P88026006` - Adswood Road Surgery (SK3 8PN) via management_company_name
- `P88026` - Heaton Moor Medical Group (SK4 4NX) via management_company_name
- `P88026002` - Dean Lane Medical Centre (SK7 6EJ) via management_company_name

## Tender watchlist

### Northern Health GPPO Limited

- Kind: `tender_competitor`
- Direct management matches in current dataset: **0**
- Affiliated-group matches in current dataset: **4**
- Note: Named in the tender quote as the winner for Victoria Mill.
- Note: In the current dataset this group shows up as an affiliated group, not a core management-company match.

Affiliated-group examples in current dataset:
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

Direct management-company examples in current dataset:
- `Y02890` - Hawthorn MC (M14 6FS) via management_company_name
- `Y02795` - Middleton Health Centre (M24 4EL) via management_company_name
- `Y02718` - Birtle View Medical Practice (OL10 4PW) via management_company_name
- `Y02721` - Kirkholt Medical Practice (OL11 2JG) via management_company_name
- `Y02720` - The Kingsway Practice (OL16 4AT) via management_company_name
- `P85614` - Village Medical Practice (OL2 8BF) via management_company_name
- `P85622` - Glodwick Medical Practice (OL4 1YN) via management_company_name
- `Y02827` - John Street Medical Practice (OL8 1DF) via management_company_name
- ... plus **2** more direct matches

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
