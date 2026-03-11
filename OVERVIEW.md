# Project Report (Repo Contents + Progress)

This file is a working map of what’s in this repository, how the pieces relate, what looks “older/orphaned”, and what to do next to actually get the access problems fixed.

Repo intent (as reflected in `README.md` / `OBJECTIVES.md`): evidence-led documentation of GP access barriers at New Bank Health Centre (GTD Healthcare), with materials suitable for meetings, escalation, and public scrutiny.

---

## 1) Top-Level “Source of Truth” Docs

These define the narrative, goals, and escalation path.

- `README.md` — primary public-facing overview: what’s in the repo, main concerns, personal timeline/experience, notes, ongoing research.
- `OBJECTIVES.md` — compact statement of aims (“fix local”, “use local case for systemic change”) + what success should look like.
- `ORIGINAL_COMPLAINT.md` — original Dec 2024 complaint / talking points (useful as baseline “what started this”).
- `ESCALATION.md` — escalation ladder with “policy hooks” (core hours online access requirement, equity in access, AIS, etc.) and target bodies.
  
Supporting / utility:
- `.gitignore` — standard ignore rules (minimal).
- `site/tools/markdown-print-viewer.html` — standalone HTML utility to load a markdown file and print it nicely (handy for creating meeting printouts without a full build step).

---

## 2) Meetings (Core Chronology + Meeting Packs)

This is the “project timeline” in practice. Each meeting folder tends to include prep notes, outputs, and supporting evidence.

### 2.1 Aug 2025 — first meeting notes capture

Folder:
- `meetings-notes/2025-08-06-meeting1/`

Key files:
- `meetings-notes/2025-08-06-meeting1/extracted-meeting-1-notes.md` — extracted notes from meeting artefacts (agenda + sticky notes + immediate observations, including “reception training/mystery shoppers”).
- `meetings-notes/2025-08-06-meeting1/IMG20250806185018.jpg` (+ other JPGs) — photos used as the source for extraction.

### 2.2 Sept 2025 — structured “meeting pack” and GTD response capture

Folder:
- `meetings-notes/2025-09-10-meeting2/`

Key authored notes:
- `meetings-notes/2025-09-10-meeting2/meeting-prep-sept-10.md` — prep notes framing issues/questions for the meeting.
- `meetings-notes/2025-09-10-meeting2/gtd-response-summary-and-questions-re-warren-tuite.md` — summary of GTD’s response points and the follow-up questions you want answered.
- `meetings-notes/2025-09-10-meeting2/Training-Challenge-Diplomatic.md` — “training theatre vs root causes” worksheet; a tool for keeping management honest about what fixes actually change outcomes.
- `meetings-notes/2025-09-10-meeting2/benchmarks-summary-sept-10.md` — benchmark reference sheet (practice sizes, access stats, etc.) for contextual comparisons.

Meeting artefacts:
- `meetings-notes/2025-09-10-meeting2/agenda-and-handwritten-notes/ocrd-handwritten-notes-and-agenda.md` — OCR’d agenda + handwritten notes; captures meeting process/tooling ideas and follow-ups.
- `meetings-notes/2025-09-10-meeting2/print-offs/` — PDFs and derived summaries used for the meeting (GP Patient Survey, “You said we did” poster, etc.).
  - `meetings-notes/2025-09-10-meeting2/print-offs/PatientSurveyBreakdown.md` — written breakdown of GP Patient Survey metrics (gateway failures like phone/website/app access, “what happens next”, etc.).

Chat research outputs (semi-orphaned but content-rich):
- `meetings-notes/2025-09-10-meeting2/chats/ChatGPT-GP_Practice_Reviews_Summary.md` — long synthesis of review themes (large).
- `meetings-notes/2025-09-10-meeting2/chats/ChatGPT-GP_Appointment_System_Issues.md` — earlier “issue framing” text.
- `meetings-notes/2025-09-10-meeting2/chats/ChatGPT-GP_practice_benchmarks_UK.md` — benchmarks context (feeds into the benchmark sheet).
- `meetings-notes/2025-09-10-meeting2/chats/ChatGPT-Appointment_service_confusion.*` — specific analysis of inconsistent “same day” vs “within 1 working day” messaging.
- `meetings-notes/2025-09-10-meeting2/chats/ChatGPT-GTD_Healthcare_summary.*` — background on GTD (size, footprint, themes).
- `meetings-notes/2025-09-10-meeting2/chats/chatgpt-export-to-md.js` — tool to convert ChatGPT export JSON into a sourced markdown representation (duplicated elsewhere).

### 2.3 Nov 2025 — later meeting evidence bundle (largest “pack”)

Folders:
- `meetings-notes/2025-11-26-meeting3/` — photos only (notes captured as images).
- `meetings-notes/2025-11-26-meeting3/` — full evidence bundle: policy docs, vendor docs, data extracts, screenshots, and pack PDFs.

Key authored notes:
- `meetings-notes/2025-11-26-meeting3/Meeting3-goals.md` — structured pre-meeting framing for Nov 26 (site down/out-of-hours, missed calls, complexity, survey signal, PATCHS criticism, receptionist pay, etc.).
- `meetings-notes/2025-11-26-meeting3/Meeting Outcomes.md` — short post-meeting “what changed / what’s next” note.
  - Note: contains a link to `meeting-ppg-nov26/` which does not exist (likely a rename/move happened).
- `meetings-notes/2025-11-26-meeting3/Archived README parts.md` — archived/removed README sections (important for “lost context”; worth mining back into main docs or into `REPORT.md`/a future `timeline.md`).

Key evidence subfolders:
- `meetings-notes/2025-11-26-meeting3/send-to-gtd-team-pre-nov26/` — the “ready-to-send” PDFs: evidence pack, Nov deck, Nov reviews, PATCHS review summary panel.
- `meetings-notes/2025-11-26-meeting3/rubbish website -  down and offline out of hours/` — screenshots/PDFs demonstrating outages, out-of-hours closure, inability to book online, etc.
- `meetings-notes/2025-11-26-meeting3/access rights and escalation/` — local governance/scrutiny context PDFs (Manchester access rights + scrutiny committee guide).
- `meetings-notes/2025-11-26-meeting3/PATCHS-support/` — PATCHS vendor PDFs describing configuration options and request limiter settings (useful for “this is configurable” arguments).
- `meetings-notes/2025-11-26-meeting3/PATCHS-dr-brown-papers/` — academic/press papers on online consultation systems and AI in primary care (useful to back “known failure modes” claims).

Quant analysis (appointments/DNAs):
- `meetings-notes/2025-11-26-meeting3/Practice_Level_Crosstab_Aug_25/` — large NHS appointment CSV extracts (Jun/Jul/Aug 2025), plus JS scripts for comparing DNA rates and estimating impacts.
  - `meetings-notes/2025-11-26-meeting3/Practice_Level_Crosstab_Aug_25/compare-dna.js` — streams CSV and benchmarks one practice vs cohort (sub-ICB/PCN/supplier/all).
  - `meetings-notes/2025-11-26-meeting3/Practice_Level_Crosstab_Aug_25/deep-compare-dna.js` — deeper breakdowns by mode/category/HCP type and correlation with waiting-time buckets.
  - `meetings-notes/2025-11-26-meeting3/Practice_Level_Crosstab_Aug_25/impact-check.js` — specific “impact tests” and additional mined insights across months.
  - Note: these scripts import `csv-parse`; there is no `package.json` in the repo to make running them reproducible out of the box.
- `meetings-notes/2025-11-26-meeting3/Did Not Attends data/` — derived outputs (New Bank-only CSV slice and exported JSON summaries), likely produced using the above scripts.

Additional chat research outputs:
- `meetings-notes/2025-11-26-meeting3/chats/ChatGPT-UK_GP_DNA_statistics.md` — background on published practice-level DNA data.
- `meetings-notes/2025-11-26-meeting3/chats/ChatGPT-GP_online_hours_practice.md` — analysis of time-gating/online-hours norms and the Oct 2025 core-hours rule.
- `meetings-notes/2025-11-26-meeting3/chats/ChatGPT-Fairly_framing_complaints.md` — “how to frame respectfully without losing the substance” guidance.

---

## 3) Reviews and Review Parsing / Analysis

This is the other “major pillar”: qualitative evidence from public feedback.

### 3.1 Practice reviews (Google etc.)

Folder:
- `reviews/`

Primary parsed outputs:
- `reviews/parsed-reviews-usable.json` — cleaned/usable review dataset.
- `reviews/parsed-reviews-og.json` — original scrape/parse output.
- `reviews/parsed-reviews-og-parsed-2yrs.md` / `reviews/parsed-reviews-og-parsed-2yrs.txt` — human-readable extracts.
- `reviews/parsed-reviews-og-parsing.txt` — notes/artefacts from parsing.

Raw sources and parsers:
- `reviews/raw-reviews/New Bank Health Centre-reviews.html` — large captured HTML dump (source evidence).
- `reviews/raw-reviews/New Bank Health Centre-reviews.txt` — plain text export.
- `reviews/raw-reviews/review-parser.user.js` — in-browser user script used to parse Google Maps reviews.
- `reviews/raw-reviews/bad-parser/` — older “offline parsing” attempts (Node scripts + parsed outputs); useful for reference, but looks like an earlier iteration.

Meeting-specific review snapshots:
- `reviews/reviews-between-aug-sept-meetings.txt` — extracted review sample used around the Sept meeting.
- `meetings-notes/2025-11-26-meeting3/reviews/november-google-reviews.txt` — review snapshot used for the Nov pack.

### 3.2 PATCHS product reviews (Trustpilot/Google) and analysis

Folder:
- `reviews/PATCHS/`

Analyses:
- `reviews/PATCHS/ChatGPT-PATCHS_system_overview.md` — long “what is PATCHS” and critique thread; includes “Unsupported Content” blocks (not fully self-contained).
- `reviews/PATCHS/ChatGPT-Re-framing_patient_feedback.md` — reframing feedback for constructive use.
- `reviews/PATCHS/ChatGPT-Summary_of_trustpilot_reviews.md` — summarised Trustpilot review themes.
- `reviews/PATCHS/Grok_2025-09-16_23-49-25_PATCHS Access Issues Analysis - Grok.md` — analysis of 1–3★ Trustpilot review text (useful to show “known failure modes”).

Outputs/printables:
- `reviews/PATCHS/output reports/` — PDF outputs for printing/sharing.

Review browser prototype:
- `reviews/PATCHS/reviews-browser/` — `index.html`, `main.js`, `style.css`, and embedded review text modules.
  - Note: `main.js` imports CSS as a module (`import './style.css'`), which usually implies a bundler workflow (e.g. Vite). There’s no repo-level build config/lockfile, so this currently looks like a “prototype snapshot” rather than a runnable tool as-is.

---

## 4) Survey / Benchmark Evidence

These are used to quantify the “gateway failures” and show “this isn’t just one person”.

- `patient survey breakdown/GP Patient Survey - New Bank Summary.pdf` — the New Bank specific survey summary.
- `patient survey breakdown/GP Patient Survey - Analysis Tool - FULL.pdf` — reference workbook/pdf for broader comparisons.
- `patient survey breakdown/GP Patient Survey - Analysis Tool - Reception.pdf` — reception-related view.
- `patient survey breakdown/GPPS 2024 Questionnaire_PUBLIC.pdf` — survey instrument itself (good for pointing out question design limitations).
- `patient survey breakdown/ChatGPT-GP_Survey_Questions.md` — large question dump / exploration.

Note: `README.md` refers to `patient-survey-breakdown/` but the actual folder name is `patient survey breakdown/` (space). The report and README should agree.

---

## 5) Healthwatch / Wider Context Reports

Folder:
- `healthwatch-reports/`

Contents:
- Multiple Healthwatch / scrutiny / usability PDFs showing that “digital front door” and triage/access problems are widespread.
- `healthwatch-reports/ChatGPT-UK_NHS_GP_data.md` — exploratory attempt to find UK-level counts for “sites closed out of hours” etc., but includes many “Unsupported Content” placeholders (treat as partial notes, not a clean citation source).

---

## 6) Messages / Comms Trail

Folder:
- `messages/`

Contents:
- `messages/2025-08-26-email-for-takeover-dates-and-context.md` — your outgoing “background information request” draft.
- `.eml` threads and `.txt` exports — captured correspondence (useful evidence trail, but contains personal/identifying data).
- `messages/Example - New health problem.txt` — example narrative; likely a template for writing a patient case cleanly.
- Screenshot(s) of correspondence artefacts.

---

## 7) Feb Meeting Pack (Older, But Not “Dead”)

Folder:
- `meeting-ppg-feb4/`

Why it matters:
- This is “fringe” relative to the top-level README, but contains some of the strongest broader narrative framing and curated evidence lists that could materially improve the repo’s main storyline and escalation packs.

Key files:
- `meeting-ppg-feb4/PatientBlaming-README.md` — strong narrative framing around “patient blame” and friction-as-rationing; policy-history framing; useful for tone and “why this matters”.
- `meeting-ppg-feb4/GP Access Evidence - Websites triage and digital barriers.md` — structured index of external evidence sources, with “who is affected” estimates and grouped sources.
- `meeting-ppg-feb4/GP Access Evidence - Immigration blame and far-right.md` — argument for improving access as a way to undercut scapegoating narratives.
- `meeting-ppg-feb4/chats/ChatGPT-Access_to_Healthcare_First.sourced.md` — sourced chat export (long).
- `meeting-ppg-feb4/chats/chatgpt-export-to-md.js` — same export-to-md tool seen elsewhere.
- `meeting-ppg-feb4/Jan15_2026_00-22am-no-appointment-request-out-of-hours.png` — evidence of out-of-hours closure.

---

## 8) “Orphan / Drift / Broken Reference” Checklist

These are either broken links, missing files, or content that exists but is not discoverable from the main docs.

- `meetings-notes/2025-11-26-meeting3/Meeting Outcomes.md` links to `meeting-ppg-nov26/` which does not exist.
- `README.md` references `patient-survey-breakdown/` but folder is `patient survey breakdown/`.
- Multiple tool scripts imply build/dependency requirements (`csv-parse`, CSS module imports) but repo lacks an installable/tooling scaffold (`package.json`, etc.).
- `meetings-notes/2025-11-26-meeting3/Archived README parts.md` likely contains important arguments removed from `README.md` and currently has no “why archived / what to reuse” signposting from top-level docs.

---

## 9) TODO / Next Steps (Author-Focused)

### 9.1 Repo hygiene (make the evidence easier to use)

- Fix broken links and naming drift:
  - Update `README.md` to point to the real `patient survey breakdown/` folder (or rename the folder to match the README).
  - Fix the `meeting-ppg-nov26/` link in `meetings-notes/2025-11-26-meeting3/Meeting Outcomes.md` to the correct folder.
- Add a small “Index” section to `README.md` linking the best/most reusable meeting packs:
  - Sept meeting pack, Nov meeting pack, Feb pack (patient-blame framing), PATCHS support PDFs, DNA analysis scripts.

### 9.2 Build a reusable “escalation bundle” (so you can send fast)

- Produce a stable “evidence pack” structure (folder + naming) that always contains:
  - `summary.md`, `timeline.md`, “minimum fixes” checklist, key screenshots, and 2–3 short case vignettes.
- Pull the strongest external evidence index points from:
  - `meeting-ppg-feb4/GP Access Evidence - Websites triage and digital barriers.md`
  - `healthwatch-reports/` (pick 3–5 PDFs you actually cite repeatedly; avoid citing “Unsupported Content” blocks).

### 9.3 Action-oriented next steps (to get the access issues fixed)

Practice/GTD asks (make them measurable and hard to wriggle out of):
- Always-on intake for at least non-urgent/admin (with clear “processed next working day” messaging).
- Replace unscheduled-callback-as-gate with scheduled windows and/or message-first handling; remove deletion/restart loops.
- Guarantee a real non-digital route (walk-in/phone) that results in an appointment/request being created without sending patients online.
- Publish a simple “what happens next” flow and response-time expectations; measure “restarts” and “closed-without-contact”.

Commissioner/regulator escalation (if local fixes stall):
- Use `ESCALATION.md` Step 2+ with a tight bundle: one-page summary, timeline, screenshots, and a small number of “representative” patient stories (no jargon).
- Consider FOI requests for contract-management / access-policy documentation if needed (keep it narrow and tactical).

### 9.4 Evidence improvements (make your strongest claims harder to dismiss)

- Turn the Sept + Nov meeting packs into a clear timeline (what was observed, what changed, what didn’t).
- If you keep using DNA/appointment stats:
  - Document exactly what the CSVs are and how the scripts were run (inputs/outputs), so the outputs are auditable.
  - Optionally add a minimal `package.json` (or a “how to run” note) so other people can reproduce results.

### 9.5 Personal safety + privacy hygiene (if publishing/share widely)

- Decide what is “public” vs “private” evidence:
  - `messages/` and some screenshots/emails may contain personal data; keep out of public packs unless redacted.
- Create redacted copies of any evidence you intend to share beyond the PPG.
