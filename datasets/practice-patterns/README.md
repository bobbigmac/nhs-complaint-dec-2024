# Practice Patterns

This folder holds manual practice-by-practice investigations of how GP websites and access routes actually work.

The reports are intentionally semi-structured. Different practices expose different combinations of:

- public website platforms
- whether the patient-facing site is a standalone practice domain or a shared management-company microsite
- online consultation suppliers
- NHS App paths
- legacy forms that still render
- staff-assisted intake routes by phone or in person
- complaints and feedback routes
- stale or broken pages

The point is not to force every practice into the same schema too early. The point is to capture useful evidence without laundering weak guesses into hard data.

## Working approach

- treat each practice as a manual investigation
- separate what is live now from what the site merely claims
- distinguish a standalone practice domain from a shared management-company host that is being used as a patient microsite
- if a shared host keeps surfacing via NHS listings and search results, record it as the patient-facing microsite rather than dismissing it as just a corporate site
- distinguish direct routes from staff-assisted intake
- capture stale, broken, or contradictory pages explicitly
- if a listed domain looks dead, broken, or hostile to scripted requests, do a quick search and NHS-profile cross-check before concluding there is no live replacement
- keep analyst judgement, but label it as judgement rather than fact

## Report shape

Reports are JSON, but they do not need identical fields.

Common sections are likely to include:

- `practice`
- `investigation`
- `headline`
- `current_picture`
- `historical_repo_evidence`
- `analyst_notes`

Useful status language:

- `live`: directly reachable now
- `claimed_by_website`: stated on the website, not independently verified
- `stale`: present but obviously out of date
- `broken_or_suspect`: present but malformed, contradictory, or likely not working as intended
- `historical_repo_evidence`: supported by files already in this repo, not necessarily re-verified live today

## Tracking

Use [TODO.md](/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/practice-patterns/TODO.md) as the manual queue.
