# Practice Patterns Notes

This folder is a manual evidence dump about how GP practices actually handle access through their public websites.

## Purpose

- map the patient-facing front door for each practice
- record the platforms actually exposed to patients, even when there are several
- capture friction, dead ends, stale routes, complaints handling, and the overall feel of the site without laundering guesswork into hard data
- build a rough per-practice pattern file that future automation can use as a starting spec

## Primary Review Mode

The primary review instrument is an interactive Firefox session that behaves like a normal patient browser.

- prefer interactive Firefox over `curl`, raw HTML fetches, or one-off scrapers
- use a copied local Firefox profile when browser behavior matters, so the site is more likely to behave as it would for a real user
- keep the reviewer mentally in a logged-out patient state unless the task specifically needs an account wall to be observed
- treat the browser session as the ground truth for what a normal patient is likely to encounter

This work is not a technical website audit.
It is a patient-experience review.

That means:

- a route that works in Firefox but looks odd in `curl` is usually still a live patient route
- a route that fails only for simple fetches is usually a secondary technical note, not the main finding
- browser-visible wording, buttons, dead ends, branch confusion and account barriers matter more than low-level server quirks

Use `curl`, `urllib`, or similar tools only as support:

- to confirm runtime on a small set of top-level routes
- to inspect page source for platform clues
- to confirm whether a site is dead, merely hostile to simple fetches, or behaving differently outside a browser
- to pull structured metadata from platforms like Accurx when the browser path is already known

Do not let command-line fetches override what the browser shows a patient unless there is strong evidence that the browser result is misleading.

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
- begin from the homepage and act like a patient who does not already know which supplier or route the practice prefers
- read homepage, appointments, online services, prescriptions, contact, and complaints or feedback pages
- click through visible patient routes rather than guessing URL paths first
- check source or headers for platform clues, but trust live patient instructions over hidden tech traces
- use Firefox with a copied local profile when browser behavior matters or the site is hostile to simpler fetches
- if a site resets or rejects simpler programmatic requests but is still visible through search results or a browser-like fetch, record it as hostile to simple fetches rather than dead
- treat any scripted browser walk as a logging aid or replay aid, not the primary reviewer
- record multiple platforms when the site genuinely exposes several
- do not force a rich local forms hub into a single platform label if the site clearly separates no-account local forms from account-based tools like NHS account or myGP
- if two NHS identities share the exact same site and path, record that shared pattern explicitly and note when the live digital routes still key off only one of the identities
- separate direct digital routes from staff-assisted handling like phone triage or receptionist booking
- treat contradictions, stale pages, and mixed suppliers as findings, not noise

## What The Reviewer Actually Tests

Every review should try to answer the same broad patient questions, even if the exact site structure is different.

### 1. Website identification

- what is the real patient-facing website for this NHS identity?
- does the NHS profile point to the same site patients would discover via search?
- is this a practice-specific domain, a shared group site, or an exact shared site/path used by several identities?

### 2. Front-door routes

- from the homepage, what visible routes are offered for appointments, health problems, prescriptions, admin, and complaints?
- are there one or several competing front doors?
- does the site clearly privilege one platform, or leave several old routes exposed?

### 3. Patient tasks

For each common task, try to reach the first genuinely actionable page:

- urgent same-day medical help
- routine medical request or GP appointment
- repeat prescription
- admin query such as fit note, referral follow-up, test result, change of details, or doctor letter
- complaint or formal negative feedback

### 4. Workflow burden

- how many visible clicks from homepage to the first actionable page?
- what first questions or required inputs are shown before submission?
- does the patient get a real online route, or only a phone number, registration wall, or callback promise?
- does the site expect the patient to understand supplier jargon to pick the right route?

### 5. Availability and gating

- is the route visibly available out of hours?
- if visible, is it actually open, admin-only, suspended, or redirected to NHS 111?
- does the platform show opening windows, triage cutoffs, or response-time promises?

### 6. Identity consistency

- do the phone number, postcode, branch name and request platform all point to the same practice identity?
- does the site quietly route patients into another branch's or parent organisation's code?
- are complaints, contact and appointments all aligned to the same place?

### 7. Quality and trust signals

- is the wording clear or jargon-heavy?
- are there stale pages, wrong-practice links, contradictory instructions, or obviously neglected sections?
- does the complaints route look real, or just generic feedback?

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

## Concrete Browsing Workflow

When generating a report, follow something close to this order unless the site immediately reveals a better path:

1. Open the NHS profile and confirm the official website link.
2. Search the practice name plus postcode if the official link looks wrong, dead, or too corporate.
3. Open the live website in Firefox.
4. Read the homepage top area, hero, cards, notices, and main navigation.
5. Try the obvious patient links in roughly this order:
   - appointments or get help
   - prescriptions
   - online services
   - contact us
   - feedback or complaints
6. For each task route, stop at the first page where a patient can actually begin the task.
7. Record:
   - the URL
   - what visible label got you there
   - steps from home
   - whether it is live, stale, broken, redirected, suspended, or account-gated
8. Only then use source inspection or targeted fetches to identify stack or supplier details.

Do not start by spidering the site.
Do not start by manufacturing guessed endpoints.
Start with what a patient would naturally click.

## Interactive Firefox Expectations

The Firefox session should usually be used to observe:

- page titles and main labels
- nav wording
- supplier links opened from visible patient buttons
- redirects to external platforms
- obvious warning banners
- account or registration barriers
- first form screens and first input requests
- whether mobile-looking or SPA routes behave differently from raw fetches

The Firefox session should also be preferred for checking:

- askmyGP, Accurx, PATCHS and other JS-heavy routes
- sites protected by anti-bot or CDN behavior
- pages that look dead in `curl` but normal in a browser
- branch-switching or location-switching behavior

## Supporting Command-Line Checks

Supporting command-line checks are useful, but secondary.

Use them for:

- basic runtime timings on a handful of stable routes
- HTML inspection for WordPress, Silicon Practice, Concrete CMS, GPsurgery.net, My Surgery Website, or other stack clues
- extracting structured metadata from Accurx or similar platforms after the route is known
- confirming redirects, final URLs, or HTTP-level failure modes

Do not use them as the main source for:

- route discovery
- deciding whether a platform is what patients are told to use
- deciding whether a site is usable in practice

## Route Status Language

Use route-status language consistently:

- `live`: a patient can reach the route and it appears usable now
- `visibly_closed`: the route is presented, but clearly says it is not open at the moment
- `stale`: the route exists but appears outdated, contradictory, or superseded
- `broken`: the patient route fails or lands on an obvious error or dead end
- `account_gated`: the route exists but requires registration, login, or NHS App setup before normal progress
- `hostile_to_simple_fetch`: the site or route looks dead to scripts but works in a browser

## How To Treat Weird Cases

Common weird cases now seen in the reviewed set:

- shared group sites that are still genuinely the patient front door
- exact shared sites used by multiple NHS identities
- sites that expose two or three live suppliers at once
- branch identities whose website now routes into a parent or sibling code
- complaints pages that are real but stale
- sites that say one thing on the homepage and another on appointments or NHS App instructions

In those cases:

- describe the mess directly
- preserve the conflicting evidence
- do not force a neat single-platform answer if the patient experience is not neat
- do not over-index on the NHS profile if the live site shows something else
- do not over-index on the live site if the route is clearly stale and contradicted by stronger current wording

## What Makes Two Reviewers Comparable

If different models or reviewers follow this file well, their reports should broadly agree on:

- the real patient-facing website
- the main visible request platforms
- whether there are several live or stale platforms
- the click path and step count to major tasks
- the first visible gating or form burden
- whether routes are open, suspended, stale, or broken
- where complaints actually go
- the main contradictions or weird identity issues

They do not need to use identical wording.
They do need to observe the same patient-visible facts.

## Good Signals

- clear language about what each route is for
- explicit response times or service windows
- direct working links for appointments, prescriptions, admin queries, and complaints
- a visible distinction between no-account website forms and account-based services, so patients can tell what they can do immediately
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
- domains that look dead to simple fetches but only prove live after NHS or search cross-checks and a more browser-like fetch

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
