# Practice Patterns Notes

This folder is a manual evidence dump about how GP practices actually handle access through their public websites.

## Purpose

- map the patient-facing front door for each practice
- record the platforms actually exposed to patients, even when there are several
- capture friction, dead ends, stale routes, complaints handling, and the overall feel of the site without laundering guesswork into hard data
- build a rough per-practice pattern file that future automation can use as a starting spec

## What Counts As Good Evidence

- a live public page that clearly tells patients what to do
- a direct route that resolves to a working platform such as `patchs.ai`, `accurx.nhs.uk`, `askmygp`, `patientaccess`, or a local form route
- a route found by manually driving the browser through the same clicks a patient would use
- source-code or response-header clues that identify the site stack
- NHS profile URLs and search results used to confirm the real patient-facing website
- repo evidence such as GP Patient Survey JSON and captured Google review text, used as supporting context rather than proof of a workflow

## What Counts As Weak Evidence

- a vague footer mention without an actual working route
- a platform name only mentioned in stale or contradictory copy
- guessed common paths that 404
- review text that implies a workflow but does not show the actual public route
- broad vibes not tied to a page, statement, or working link

## Anti-Bullshit Rules

- do not treat a management-company domain as "wrong" if it is clearly the site patients are sent to
- do not treat a management-company domain as "right" unless NHS/search/live evidence points patients there
- do not collapse several live systems into one fake canonical platform
- do not count phone or in-person as a meaningful route unless the site actually presents them as active intake routes
- do not call a complaints route "working" if the page is only Friends and Family, generic feedback, or a broken form
- do not force every site into the same access-model boxes when the real story is messier
- do not overstate confidence; use `probably_true` and `needs_follow_up` when the reading is sensible but not locked down

## Review Heuristics

- start by confirming the patient-facing website via NHS profile plus a quick search cross-check
- do a fresh exploratory pass for every practice unless the live patient-facing site is literally the same site and path as one already reviewed
- use a real browser session and explore the site interactively, choosing the next step based on what the page shows
- read homepage, appointments, online services, prescriptions, contact, and complaints or feedback pages
- check source or headers for platform clues, but trust live patient instructions over hidden tech traces
- use Firefox with a copied local profile when browser behavior matters or the site is hostile to simpler fetches
- treat any scripted browser walk as a logging aid or replay aid, not the primary reviewer
- record multiple platforms when the site genuinely exposes several
- separate direct digital routes from staff-assisted handling like phone triage or receptionist booking
- treat contradictions, stale pages, and mixed suppliers as findings, not noise

## Pattern Files

Each practice report should function as a rough pattern file:

- what site the patient actually lands on
- what recurring tasks the site appears to support
- what routes were discovered manually
- what the patient is asked for first
- what breaks, conflicts, redirects, or appears gated
- what future automation should try to replay

This does not need to be exhaustive.
It does need to be useful.
Similarity between two practices is not enough to skip the pass.
Only exact shared patient-facing sites should be treated as one pattern with several practice identities.

## Good Signals

- clear language about what each route is for
- explicit response times or service windows
- direct working links for appointments, prescriptions, admin queries, and complaints
- consistent wording across pages
- low-friction online access that does not immediately bounce patients back to phone or reception
- survey and review patterns that line up with the public workflow

## Bad Signals

- hidden or contradictory access routes
- supplier overlap that looks accidental rather than intentional
- pages that still mention old systems
- complaints buried behind feedback funnels
- punitive or patient-blaming wording around missed appointments or access requests
- contact pages that imply online access without showing a real route
- dead domains, empty placeholder sites, or obvious 404-heavy public navigation

## Survey Use

- GP Patient Survey is useful for `overall_good`, `contact_good`, `phone_easy`, `website_easy`, `app_easy`, and `needs_met`
- compare practice scores to the ICS benchmark, not just raw percentages
- small reviewed samples are exploratory only; avoid making supplier-wide claims too early
- platform alone is unlikely to explain performance; workflow, wording, and route design matter too

## Task Battery

These are the recurring patient tasks worth testing manually:

- urgent same-day help
- routine GP appointment or medical query
- repeat prescription request
- admin query such as fit note, update details, or test-result follow-up
- complaint or formal negative feedback

For each task, try to answer:

- can a logged-out patient find the route from the homepage or obvious nav?
- how many user-visible steps does it take to reach the first actionable page?
- is the route live out of hours, visibly closed, or only explained in office-hours language?
- does the route require registration, login, NHS App setup, or another precondition before a normal user can proceed?
- what initial inputs are requested before submission, without actually submitting anything?
- does the task stay online, or does it quickly dump the user back to phone or reception?
- what rough replay steps would let a non-LLM runner attempt this same check later?

## Patient Profiles

The same site may feel different depending on the starting point. Keep these simple profiles in mind:

- a normal logged-out patient who just lands on the homepage
- a patient comfortable with digital tools but not already logged in anywhere
- a patient who can browse but may not understand NHS platform jargon
- a patient trying out of hours when the route may be visible but not actually open

## What To Log

- `discovered_at` for important routes, blocks, and failures
- route status now: live, visibly closed, stale, broken, or account-gated
- basic runtime checks for a few top-level routes such as homepage, appointments, prescriptions, complaints, and the main online request route
- first form fields or first required choices, without submitting
- step count from homepage to the first actionable task page
- cognitive burden: whether the user has to interpret jargon, choose between overlapping suppliers, or guess which route applies
- manual burden: clicks, repeated data entry, registration walls, callback dependence, or forced phone fallback
- replay hints: start URL, the visible link or page used next, and the expected destination or gate
- dates of encountered issues and dates of discovered useful paths

## Automation Role

Future automation should mostly reuse what the manual review already discovered.

- the manual review decides what matters on the site
- the saved replay hints help later runners attempt the same checks headlessly
- simple runtime probes can also compare whether the top-level routes still load at all
- those later runners will fail often, and that is acceptable
- the stored pattern file is both a research note and a bootstrap spec for later testing

## Update Discipline

- keep adding lessons here as they become obvious from real reviews
- prefer sharper judgement over larger schemas
- if a new field starts appearing in several reports and feels useful, keep it
- if a field is just creating noise, stop using it
