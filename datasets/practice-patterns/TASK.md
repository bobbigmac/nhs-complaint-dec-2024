# Practice Report Task Prompt

Use this prompt when assigning a future model to build a single manual practice-pattern report.

The goal is to get a patient-experience report, not a technical site audit.
The reviewer should behave like a logged-out patient using a normal browser, mainly via interactive Firefox.

## Prompt

You are reviewing one GP practice website to build a manual patient-access report.

Your job is to find out how a real patient is likely to experience the practice's digital front door.
You are not auditing website engineering quality in the abstract.
You are not trying to crawl everything.
You are trying to understand the patient-facing routes, platforms, burdens, contradictions, and failure points.

Work on one practice only.
Finish that practice's report before moving on.

## Essential Pre-Review Steps

Before starting, complete these steps (see AGENTS.md for detail):

1. Copy the local Firefox profile into a disposable directory.
2. Launch Firefox with that profile copy (headful).
3. Use that Firefox session as the primary review instrument.

Skipping the profile copy leads to captchas on Google and other sites, distorting the patient experience.

## Core Rules

- Use interactive Firefox as the primary instrument.
- Prefer what a normal patient sees in Firefox over what `curl` or simple fetches say.
- Treat command-line fetches, HTML inspection, and platform metadata as supporting evidence only.
- Start from the NHS profile and the live homepage.
- Follow visible patient routes rather than guessing URL paths first.
- Do a fresh exploratory pass for this practice unless the patient-facing site is literally the exact same site and path as a previously reviewed identity.
- Do not force a neat single-platform answer if the site really exposes several.
- Do not mistake a management-company site for irrelevant corporate fluff if it is clearly the real patient microsite.
- Do not mistake a management-company site for the right answer unless NHS, search, and live browsing suggest patients are actually sent there.
- Record patient-visible contradictions directly.
- Do not submit real forms.

## Patient Perspective

Assume:

- logged-out patient
- no supplier account already open
- no prior knowledge of NHS platform jargon
- patient may be browsing out of hours

Care most about:

- what route the patient would click first
- how many clicks it takes to reach a real actionable page
- what the patient is told to do
- what platform actually handles the task
- what first inputs or gates appear
- whether the route is open, suspended, stale, broken, or account-gated

## What To Test

Try to answer these for the practice:

1. What is the real patient-facing website?
2. What platforms are visibly used on the site?
3. How does a patient request:
   - urgent same-day help
   - routine medical help or appointment
   - repeat prescription
   - admin help such as fit note, referral follow-up, test result, or contact-details change
   - complaint or formal negative feedback
4. Are there multiple competing suppliers or stale old routes?
5. Are routes open out of hours, visibly closed, or misleadingly present?
6. Does the site look clear and coherent, or confusing and contradictory?

## Review Workflow

Follow roughly this order:

1. Open the NHS profile for the practice.
2. Confirm the website linked there.
3. If the linked site looks dead, wrong, or too generic, cross-check via search and live browsing.
4. Open the live patient-facing site in Firefox.
5. Read the homepage top area, key notices, and navigation.
6. Click through likely patient routes:
   - appointments or get help
   - prescriptions
   - online services
   - contact us
   - feedback or complaints
7. For each core patient task, stop at the first genuinely actionable page.
8. Record what visible link got you there, how many clicks it took, and what happened.
9. Only after browsing, use supporting fetches or source inspection to identify stack and platform clues.

## Supporting Checks

Supporting checks are allowed after the browser pass for:

- confirming top-level route availability
- checking final URLs and redirects
- inspecting source for WordPress, Silicon Practice, Concrete CMS, GPsurgery.net, My Surgery Website, or similar platform clues
- reading platform metadata from Accurx or similar systems once the patient-facing route is already known

Do not let supporting checks override the browser result unless the browser result is clearly misleading.

## Route Status Labels

Use these ideas consistently:

- `live`: reachable and looks usable now
- `visibly_closed`: shown to the patient but clearly not currently open
- `stale`: present but apparently outdated or contradicted by stronger current wording
- `broken`: obvious error, dead end, or unusable failure
- `account_gated`: real route but blocked behind login, registration, or NHS App setup
- `hostile_to_simple_fetch`: works in browser but looks dead or broken to simpler scripts

## What To Notice

Pay attention to:

- exact site identity and whether it is standalone or shared
- whether multiple NHS identities share the same exact site/path
- whether digital routes use the same branch identity as the NHS profile
- whether the site routes into another ODS code or sibling practice identity
- whether complaints are real or just generic feedback
- whether old suppliers are still mentioned
- whether the site bundles admin and clinical tasks in one route
- whether the patient must guess between PATCHS, Accurx, askmyGP, NHS App, local forms, phone, or reception
- whether the wording feels clear, jargon-heavy, punitive, or stale
- cookie/consent popups or viewport blockers (count when encountered; minimal note, not a critique)

## Report Output

Write one JSON report to `datasets/practice-patterns/reports/`.

Use the current report style already present in this folder.
The fields do not need to be identical every time, but the report should usually include:

- `report_version`
- `practice`
- `investigation`
- `headline`
- `website_stack`
- `discovered_paths`
- `basic_runtime_checks`
- `task_checks`
- `replay_hints`
- `encountered_issues`
- `analyst_notes`
- `source_pages`
- `cookie_popups_encountered` (optional; from crawl when available)

Useful principles for the JSON:

- keep patient-visible facts separate from judgement
- preserve contradictions instead of flattening them
- record multiple live platforms if needed
- include dates for discovered paths and encountered issues
- keep the report useful rather than exhaustive

## Style Expectations

- Be concrete.
- Be sceptical of easy neat answers.
- Prefer observed behavior over generic assumptions.
- If something is only a guess, label it in `analyst_notes` rather than presenting it as fact.
- Do not bloat the report with irrelevant crawl noise.

## Done Condition

The task is complete when:

- the practice's real patient-facing site has been checked
- the major patient tasks have been explored
- the main platforms and contradictions have been identified
- the JSON report has been written
- the JSON validates
- the manual queue can be updated if appropriate

## Invocation Template

Fill in the placeholders below when running the task:

```text
Build a manual practice-pattern report for:

- practice name: <PRACTICE_NAME>
- ods code: <ODS_CODE>
- nhs profile: <NHS_PROFILE_URL>
- expected website from dataset: <WEBSITE_URL>

Use the practice-patterns method in AGENTS.md.
Use interactive Firefox as the main review method.
Write or update:

- datasets/practice-patterns/reports/<REPORT_FILENAME>.json

If you learn a genuinely reusable lesson from this practice, update:

- datasets/practice-patterns/AGENTS.md

If the practice is part of the tracked queue, update:

- datasets/practice-patterns/TODO.md
```
