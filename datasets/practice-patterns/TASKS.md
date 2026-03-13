# Practice Task Battery

This is the current test battery for manual practice reviews.

The point is not to exhaustively crawl every page.
The point is to test a few recurring patient jobs and describe the work a patient must do to get started on them.
The manual browser exploration comes first.
Any replayable script or browser log is a secondary output that should preserve what the manual review discovered.

## Core Tasks

1. Urgent same-day help
2. Routine medical request or appointment
3. Repeat prescription
4. Admin query
5. Complaint or formal negative feedback

## Default Patient States

1. Logged-out patient landing on the homepage
2. Patient not already registered with any online supplier
3. Patient browsing out of hours

## What To Measure

- route found or not found
- date and time encountered
- steps from homepage to first actionable page
- user-visible interactions or clicks to first actionable page
- whether the route is open, closed, hidden, or redirected
- whether login, registration, NHS App setup, or a supplier account is required
- what first inputs are demanded before submission
- whether the route appears to be clinical triage, admin messaging, feedback only, or a dead end
- whether the site pushes the user back to phone or reception
- what future replay steps would probably reproduce this check
- a few basic load timings or timeout results for the top-level routes you actually used

## Exploration Order

For each practice:

1. Confirm the website patients are actually sent to.
2. Open the homepage in a normal browser session.
3. Try the core tasks one by one as a logged-out patient.
4. Follow the most plausible next step on each page rather than crawling everything.
5. Record the first actionable point, first obvious block, and first visible input burden.
6. Save only the paths and issues that seem useful for future reruns.

## Common Failure Modes

- supplier overlap that forces the patient to guess
- homepage link exists but target page times out or fails in a real browser
- feedback page masquerades as complaints handling
- online route exists only for some tasks and silently excludes others
- route is visible out of hours but functionally closed
- form asks for too much before the patient can even explain the issue

## Reporting Style

- keep the route narrative concrete and patient-facing
- distinguish observed behavior from judgement
- note the first actionable point, not just the presence of a menu link
- note what the patient is asked for before submit, but do not submit real forms
- preserve rough replay hints, but do not let the replay format drive the investigation
