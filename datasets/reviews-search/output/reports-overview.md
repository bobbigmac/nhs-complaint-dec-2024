# Reviews Reports Overview

This note maps the review reports in `datasets/reviews-search/output` back to the original prompts that asked for them.

It is a working overview for the expanded corpus refresh. The summaries below describe what each report currently found in the earlier, smaller run, so they can be checked and rewritten against the larger dataset now in the index.

## 1. Access Issues In The Review Corpus

**Prompt**

> good work. Using our new tool, tell me how many reviews as a percentage of all reviews mention main access-related issues, and the most common access issues raised. Output to a new md file as an example of what this tool can do, including examples by practice and issues, not a data structure as such, but a report on meaning, that tries to use real examples and their prevalance to evaluate how big of an issue access is, with enough context to understand the problems patients face. Use a reading ease level about the same as the source reviews, avoid jargon except where reviewers use it.

**Current file**

- `access-issues-report.md`

**Current source basis**

- ad hoc fulltext/index queries
- later extended with an exclusion section

**Current discoveries**

- Access was the biggest issue in the earlier corpus.
- The report framed broad access language as just over half of reviews, with a stricter low-star access complaint share closer to a third.
- Phone access, appointment scarcity, reception barriers, digital front-door failures, and weak follow-up were the core recurring issues.
- Later extension: access problems can turn into exclusion, with reviews describing failed attempts to move practice, catchment barriers, and occasional reports of things improving after leaving.

## 2. What The Review Corpus Shows

**Prompt**

> great work. Write another report, aside from access issues, how do our reviews look across the board? gimme like a full professional analysis of what's in our dataset, good and bad, using our new tools to explore. Think of this as the overview of exactly what patients complain about, and how they talk/write about it. Like set out what we're going to need to know to begin representing the needs of these patients more clearly than the patient survey usually can (you might even want to look at our google reviews datatset from the perspective of the real questions from the national patient survey, which does have some pretty narrow interests, so seeing where the real google reviews diverge from the patient survey, and how they look at problems in different ways) is useful.

**Current file**

- `reviews-corpus-overview-report.md`

**Current source basis**

- ad hoc fulltext/index queries
- manual bucket scans for positive and negative themes

**Current discoveries**

- The earlier corpus looked sharply polarised, with a very large `1`-star block and a very large `5`-star block, and very little middle ground.
- Access dominated complaints, but staff attitude, follow-through, prescriptions/referrals, and clinical trust also stood out.
- Positive reviews clustered around kindness, being listened to, thorough clinicians, and staff who actually sorted things out.
- The report argued that reviews often show route, sequence, emotional cost, and exclusion more clearly than the national patient survey.

## 3. Older Reviews Versus Recent Reviews

**Prompt**

> the next report, we want to explore is what is common in older reviews (since our corpus has quite a lot of entries approaching 10 years old) that never occur in recent/post-pandemic reviews, and vice-versa what's common now, but never used to be complained about in older reviews.

**Current file**

- `older-vs-recent-complaints-report.md`

**Current source basis**

- ad hoc era-split analysis over indexed reviews
- low-star complaint-focused comparison

**Current discoveries**

- Core complaints like appointments, phones, rude reception, and being sent round in circles did not disappear.
- The stronger change was on the recent side: digital front-door complaints, online triage, web forms, and callback-driven access became much more visible.
- The report treated `2020` and `2021` as transition years and compared older (`2016`-`2019`) against recent (`2022`-`2026`) complaint-heavy windows.

## 4. How Patients Talk About Staff And Clinicians

**Prompt**

> we should also do a pretty thorough check of positive reviews to try and identify when specific staff are named, what exactly was written about in particularly glowing terms (or if individuals are called out for failures), like let's write a report about how patients feel about the staff, doctors, etc in practices who actually handle their care, good and bad. We don't want to build a list of good/bad doctors, but it might be useful to look at where named individuals are doing very well compared to the rest of the corpus, but for doing badly, avoid names and stick to issues, complaints, specific mistakes or decisions that patients don't like (i.e. we can name the good doctors, but for bad doctors we should stick to the issues, rather than their names).

**Current file**

- `staff-and-clinician-experience-report.md`

**Current source basis**

- ad hoc review mining
- manual extraction of positive named-staff praise

**Current discoveries**

- Patients often talk about people, not just the abstract practice.
- Positive reviews repeatedly praised clinicians who listened, explained, reassured, and followed through.
- Reception could swing both ways: warm and helpful in positive reviews, or cold, rude, and obstructive in negative ones.
- The negative side was kept issue-focused rather than naming individual clinicians.

## 5. Clinical Harm Warning Signs In Google Reviews

**Prompt**

> since misdiagnoses are so important, can we do a pretty thorough check for a new report on warning signs, red flags or direct mentions of clear clinical failures and connected outcomes, avoiding admin, day to day process, but looking for specifically clinical harm issues reported via reviews, again not to witch-hunt but to flag practices for checks that the patient survey don't even try to check for (there are literally no questions about clinical care and whether patients feel healthier after their process)

**Extension prompt**

> whilour last major report, we want to thoroughly dig up every sign where a patient clearly either got sicker, postponed or delayed care/attention, were actvely made sicker or directly harmed, not just through clinical care or process issues, but through any other issues that might not initially look like they made people sicker, but this is the more serious end (these are logged accusations essentially) and I want to know across our corpus how serious are these errors for real patient health. While the previous report was about practice workflow, this should be about real patients and real outcomes reported in their reviews, not practice decisions but basically a shitlist of every unquestionable fuckup we can find that siginifcantly harmed a patient. This is probably an extension to the previous report, rather than a new document.

**Current file**

- `clinical-harm-warning-signs-report.md`

**Current source basis**

- `clinical_harm_signals.py`

**Current discoveries**

- The earlier run found a smaller but serious slice of reviews with misdiagnosis, unsafe medication, negligence/danger language, hospital escalation, or severe outcomes.
- The extension shifted from warning signs to reported harm outcomes: deterioration, delayed care with harm, treatment-linked illness, emergency escalation, and serious condition or near-miss language.
- The report positioned this as a part of patient experience almost untouched by the national patient survey.

## 6. Practice Responses To Reviews

**Prompt**

> and I suppose we need a report about practice responses, distinguishing between repsonses to positiv reviews or responses to negative reviews. Patient blaming is partcualrly prevalent and I want to know the various ways in which patient-blaming langage appears in responses from practices to patients, and if you can figure it out, which practices reply promptly to reviews with genuinely useful responses that are not just "contact the front desk" or like "use the website", which is very common. Who does good responses and who does bad ones, and what are the charcateristics of those groups?

**Current file**

- `practice-responses-report.md`

**Current source basis**

- `analyze_practice_responses.py`

**Current discoveries**

- Practices were much more likely to reply to praise than criticism.
- Most responses were thanks, apology, or boilerplate signposting rather than public evidence of specific action.
- Publicly useful responses were rare.
- The report also pulled out patient-blaming and deflecting modes in reply language.

## 7. Online, Website, And Software Platform Experience

**Prompt**

> good work. Another report, I need an in-depth exploration of the online/web experience and the various software platforms either metnioned or inferred from the platform, starting with anlysing generic coverage of things like "the website" or "the site" or "online" etc. I know patients mention PATCHs quite a lot, but accurx, econsult, and maybe a few others do turn up, tho usually not by name because the practice usually doesn't expose the name. It's hard to make real like-for-like comparisons because of no tags, but try to get a sense for the quality and distribution of issues specific to the website and software, good and bad.

**Current files**

- `online-web-platform-experience-report.md`
- later follow-on work:
  - `digital-appointment-practice-ranking-report.md`
  - `digital-platform-allocation-report.md`

**Current source basis**

- `analyze_digital_experience.py`
- `rank_digital_appointment_practices.py`
- `infer_digital_platforms_by_practice.py`

**Current discoveries**

- Digital access became a substantial theme in the wider corpus, but most patients still described it generically rather than by product name.
- Generic website/form/app language was far more common than explicit product naming.
- Follow-on ranking and allocation work widened this further into practice-level digital appointment rankings and a first-pass platform allocation layer.
- The current platform-allocation pass can name a platform for a substantial minority of digitally relevant practices, but most still remain generic/unknown from review wording alone.

## 8. GTD-Managed Practices Review Report For PPG Discussion

**Prompt**

> for all of our MD reports in reviews-search/output, I'd like you to write a new report looking at the same issues for only GTD managed practices, using only examples from GTD practice reviews, and in its context. Basically Rather than many reports on the entire corpus, I want a single report looking at the same issues from scratch for only GTD practices (it's about 13 practices iirc) in depth with named/~dated real reviews included. This version will be taken to the practice PPG.

**Current file**

- `gtd-managed-practices-ppg-report.md`

**Current source basis**

- consolidated GTD-only reruns of the earlier themes

**Current discoveries**

- The GTD slice looked much harsher than the wider corpus, with a much heavier low-star skew.
- Access, staff tone, digital front-door problems, weak follow-up, exclusion language, and public response behaviour all showed up strongly in GTD-managed practice reviews.
- The report was written as a single GTD-only synthesis rather than many separate GTD-only notes.

## 9. Activism, Community Response, And Public-Warning Reviews

**Prompt**

> a fringe issue that is worth checking in the broader corpus and writing up a new specific short report about is activism/community-response/busy-bodies presence in the dataset, like on the whole patients are reasonably angry (and often clearly angry but trying to be reasonable) but I'm looking for reviewers that might be from or about people trying to change the systems, and how they're doing, community integration or support and anywhere people seem to be trying to communicate _about_ practices in this context, not stindividual health-related issues, but basically I want to know if our corpus has any obvious 'weekend warriors' or 'chatgpt activists' (I know there is at least 1 in the dataset, me, so I'm curious if you can turn up more, or even if you miss that one, btu I think you'll spot it)

**Current file**

- `activism-community-response-report.md`

**Current source basis**

- `analyze_activism_presence.py`

**Current discoveries**

- Activism-style reviewing was a real but fringe layer rather than a dominant one.
- The biggest bucket was public-warning language aimed at other patients.
- Smaller groups involved regulator escalation, review-about-review writing, authority-positioning, and community framing.
- The report argued this looked more like scattered public warning and escalation than sustained local organising.

## Refresh Notes

- The earlier reports were written against a much smaller indexed corpus.
- The current rebuilt index is much larger, so most of these notes should now be treated as version-one readings rather than the final word.
- The reports with the strongest helper-script basis today are:
  - `clinical-harm-warning-signs-report.md`
  - `practice-responses-report.md`
  - `online-web-platform-experience-report.md`
  - `digital-appointment-practice-ranking-report.md`
  - `digital-platform-allocation-report.md`
  - `activism-community-response-report.md`
- The reports most likely to need a fresh from-scratch analytical pass are:
  - `access-issues-report.md`
  - `reviews-corpus-overview-report.md`
  - `older-vs-recent-complaints-report.md`
  - `staff-and-clinician-experience-report.md`
  - `gtd-managed-practices-ppg-report.md`
