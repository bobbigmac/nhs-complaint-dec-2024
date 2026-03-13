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

The main unit of analysis is now the patient task, not just the page inventory. See [TASKS.md](/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/practice-patterns/TASKS.md) for the current manual test battery.

The primary output is a per-practice pattern file: a rough operational spec of how the site appears to handle patient access, based on interactive manual exploration.

## Working approach

- treat each practice as an interactive manual investigation in a real browser
- drive the browser task-by-task as a patient would, rather than relying on a one-off crawl to decide what matters
- separate what is live now from what the site merely claims
- distinguish a standalone practice domain from a shared management-company host that is being used as a patient microsite
- if a shared host keeps surfacing via NHS listings and search results, record it as the patient-facing microsite rather than dismissing it as just a corporate site
- distinguish direct routes from staff-assisted intake
- capture stale, broken, or contradictory pages explicitly
- if a listed domain looks dead, broken, or hostile to scripted requests, do a quick search and NHS-profile cross-check before concluding there is no live replacement
- keep analyst judgement, but label it as judgement rather than fact

## Method Stages

Break the work down like this:

1. Confirm the real patient-facing website.
2. Open the site in a normal browser session and explore it manually.
3. Test the current task battery from the point of view of a logged-out patient.
4. Record what the site says it offers, what routes are actually reachable, and where the patient hits friction.
5. Capture a rough replayable log or mini-spec of the useful paths discovered, so future non-LLM runners can attempt the same checks.

The replay log is secondary.
Its job is not to replace judgement.
Its job is to preserve what the manual exploration learned about this site well enough that automation can try again later.

## Report shape

Reports are JSON, but they do not need identical fields.

Common sections are likely to include:

- `practice`
- `investigation`
- `headline`
- `website_stack`
- `discovered_paths`
- `task_checks`
- `encountered_issues`
- `historical_repo_evidence`
- `analyst_notes`

Useful extra sections:

- `replay_hints`
- `form_entry_observations`
- `out_of_hours_checks`
- `basic_runtime_checks`

Useful status language:

- `live`: directly reachable now
- `claimed_by_website`: stated on the website, not independently verified
- `stale`: present but obviously out of date
- `broken_or_suspect`: present but malformed, contradictory, or likely not working as intended
- `historical_repo_evidence`: supported by files already in this repo, not necessarily re-verified live today

## Tracking

Use [TODO.md](/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/practice-patterns/TODO.md) as the manual queue.
