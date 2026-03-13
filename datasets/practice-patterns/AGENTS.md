# Practice Patterns Notes

This folder is a manual evidence dump about how GP practices actually handle access through their public websites.

## Purpose

- map the patient-facing front door for each practice
- record the platforms actually exposed to patients, even when there are several
- capture friction, dead ends, stale routes, complaints handling, and the overall feel of the site without laundering guesswork into hard data

## What Counts As Good Evidence

- a live public page that clearly tells patients what to do
- a direct route that resolves to a working platform such as `patchs.ai`, `accurx.nhs.uk`, `askmygp`, `patientaccess`, or a local form route
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
- read homepage, appointments, online services, prescriptions, contact, and complaints or feedback pages
- check source or headers for platform clues, but trust live patient instructions over hidden tech traces
- when needed, use Firefox with a copied local profile to walk the site more like a real user and measure load times or click depth
- record multiple platforms when the site genuinely exposes several
- separate direct digital routes from staff-assisted handling like phone triage or receptionist booking
- treat contradictions, stale pages, and mixed suppliers as findings, not noise

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

## Update Discipline

- keep adding lessons here as they become obvious from real reviews
- prefer sharper judgement over larger schemas
- if a new field starts appearing in several reports and feels useful, keep it
- if a field is just creating noise, stop using it
