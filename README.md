# Digital Access Failures - New Bank Health Centre (NHS GP Practice, Manchester)

This repo documents ongoing concerns about **patient access, digital systems, and front‑door process** at New Bank Health Centre (run by GTD Healthcare).

It contains only publicly available data so that the evidence and reasoning are transparent to patients, staff, GTD, and anyone else trying to improve access. These issues pre-date GTD's control of New Bank, but have continued since their take-over in April 2025, with only very minor improvements.

  - Patients are being excluded by the practice requiring a mandatory unscheduled office-hours phone call, forcing them to start over
  - Patients are being treated as if they are to blame, wherever the practice's flawed 'efficiency' decisions are excluding them in ways that are hard to measure the impact
  - Some patients are being excluded completely by 'digital-only' process, poor workflow choices and reception stiffness

## What’s in this repository?

- **Complaint details and meeting prep**
  - [ORIGINAL_COMPLAINT.md](./ORIGINAL_COMPLAINT.md) - initial long‑form complaint about the appointment system. Dec 2024, updated Aug 2025.
  - [OBJECTIVES.md](./OBJECTIVES.md) - Shorter form summary of issues.
  - [meetings-notes/](./meetings-notes/) - Documentation for each meeting, and my prep/issues and received handouts with my notes.
  - [meeting4-goals.md](./meetings-notes/2026-01-04-meeting4/meeting4-goals.md) - Meeting 4 (Feb 2026) prep
  - [My Patient Experience at New Bank](./My-new-bank-experience.md)
- **Data and analysis**
  - `patient-survey-breakdown/` - breakdown of GP Patient Survey results for New Bank and further research.
  - `reviews/` - Google review HTML/text, parsing scripts, and parsed outputs.
  - `messages/` - Log of sent messages (mostly emails, complaint-related only).
  - `healthwatch-reports/` - Healthwatch reports from around the UK sharing these concerns.
  - `ppg-terms-review/` - What is a PPG for? and how can it do that effectively? 
- [My own experience](./My-new-bank-experience.md) trying (and failing) to see my doctor, as a patient who works nights.
- [Notes](#Notes) - My notes that don't fit anywhere else.
- [Ongoing/further Research](#ongoingfurther-research) - What's next.
  - [Reviewing the updated draft PPG terms docs](./PPG-terms-review/PPG-terms-review.md)
  - [Exclusion questions - Is exclusion a problem here?](./Exclusion-questions.md)
- **Produced reports/evidence packs**
  - [General GP practice stats and scope/environment notes](./meetings-notes/2025-09-10-meeting2/benchmarks-summary-sept-10.md)
  - [PATCHS trustpilot reviews for lots of useful patient input](./reviews/PATCHS/output%20reports/PATCHS%201-2-3%20Star%20Reviews%20with%20Summary%20Panel%20Landscape.pdf)
  - [Patient blaming evidence pack](./meetings-notes/2026-01-04-meeting4/PatientBlaming-README.md)
  - [Affected patients estimates and Healthwatch overview](./meetings-notes/2026-01-04-meeting4/GP%20Access%20Evidence%20-%20Websites%20triage%20and%20digital%20barriers.md)
  - [Poor NHS access and political extremism](./meetings-notes/2026-01-04-meeting4/GP%20Access%20Evidence%20-%20Immigration%20blame%20and%20far-right.md)
  - [Google reviews management and good response patterns](./meetings-notes/2026-01-04-meeting4/reviews-management.md)

The focus throughout is **patient access**, not clinical care quality.

## Main concerns

1. **Digital‑only booking and exclusion**
  - Access is effectively **digital‑only**
    - No simple “walk in and make an appointment” route and impossible to book by phone without being sent back online.
  - Excludes patients without stable internet/devices, no daytime availability, lacking confidence with forms, and adds friction even for confident users.

2. **Unscheduled missed calls cause deletion/resubmission loop**
  - If the doctor calls for triage OR the receptionist calls to arrange an appointment, and the patient misses two **unscheduled** calls, with no route to schedule or bypass the call, the **request is closed** and the patient must start over.
    - PPG agreed SMS support will be added as fallback instead of deletion (expected by end of Feb 2026)
    - This _should_ somewhat mitigate the problem, but could be improved upon with a bookable slot picker (PATCHS supports this)
  - Current system excludes patients who work nights/shifts and [other groups](./meetings-notes/2026-01-04-meeting4/GP%20Access%20Evidence%20-%20Websites%20triage%20and%20digital%20barriers.md)

3. **Reception**
  - Reviews describe **rude, dismissive, or blocking behaviour** at reception, especially with distressed/complex patients.
    - Some severe recent reviews, but general tone seems to be improving as reception restaffed. Monitor. 

4. **Can't start appointment process outside office hours**
  - Partially progress, admin requests are now open out of hours (since 14th Jan)
  - but... Appointments cannot be requested.
    - This is only enabled when the office is open
      - Doctor claims it avoids missing urgent/emergency contacts
      - Should be possible to start appointment requests out of hours

5. **Metrics vs reality**
   - Please investigate lost/excluded patients
   - No active complaints procedure beyond PPG
    - [Contact the practice](https://newbank.nhs.uk/form/contact-the-practice/) shows `Form Unavailable`
    
---

### Main Issues

Logged [My Patient Experience at New Bank](./My-new-bank-experience.md)

<details>
<summary>Out-of-hours access and mandatory phone steps</summary>

- The workflow assumes "**a doctor MUST be present and online at the moment someone requests an appointment**".
- Appointment requests remain unavailable outside office hours
  - The office-hours phone step is still (currently) mandatory to progress.
- A key benefit of online systems is **decoupling clinician availability from request submission**, with appropriate urgent-care safeguards.
- Clarify who owns these workflow decisions and what constraints apply (clinical risk, staffing/backlog management, contractual/legislative requirements).
- Consider measuring overnight demand during a time-limited trial to quantify impact and identify excluded patients.

</details>

<details>
<summary>Survey metrics may understate access barriers</summary>

- The current patient survey status shows 22% of patients report it being hard to get an appointment.
- This is an improvement on last year's 39%, though this isn't directly comparable:
  - the 39% is the inverse of people who found it easy to contact the practice by phone
  - it also excludes the "I haven't tried" contingent
- The real number may be higher if the survey wording (unintentionally) allows some access issues to fall between available answers.

</details>

<details>
<summary>Diagnostic delay / premature closure, compounded by access</summary>

- On the diagnostic issue, I don't think it reaches clinical negligence (it hasn't resulted in the worsening of my condition).
- Premature diagnostic closure or diagnostic delay (made more severe by poor access) seems a more appropriate label.
- At least one other PPG patient mentioning this suggests it may not be uncommon to close conditions without full investigation or identification of causes.
- Operationally, repeated request closure/deletion can force patients to restart, compounding delay.

</details>

### Ongoing/further research

<details>
<summary>Request deletion and forced “start over” workflows [PENDING IMPLEMENTATION]</summary>

- Staff have claimed "everyone does this" regarding making patients 'start over' (deleting requests for missed calls, or multiple daily submissions/second after deletion on same day). How many practices have systems that delete patient requests?
- PATCHS reviews suggest that it does not solve this.
- Confirmed myself, 2 missed calls results in no further action, ticket is closed, cannot be reopened.

</details>

<details>
<summary>Review patterns and “everyone has bad reviews”</summary>

- Staff have claimed 'of course reviews are bad' (as if ALL reviews are bad, because 'nobody writes good reviews') in the PPG.
- Many local practices have bad reviews for similar reasons, but others have strong reviews (including 1 under GTD).
- If the pattern holds in some places, how common is it, and what are the common drivers?
- Research suggests more bad reviews than good is normal, but it should be much less negative than current

</details>


<details>
<summary>Unclear request types (clinical vs admin; urgency)</summary>

- The language around request types is confusing.
- Many patients don't know if what they need to see a doctor about falls under clinical or admin, or what is a non-pressing issue or what's urgent.
  - If I have some pain, or a meds question, is that clinical? Who knows? Where to find out?
  - There's several layers of website, and none of them seem to say the same thing. These are presumably different layers of NHS/practice infrastructure?
  - Maybe better visibility of the organisational model would be useful on the site. It's not clear who is responsible for what.
- The categories seem to be emergency (call 999), urgent (a doctor will try and get you in asap) or normal (usually within 3 days)

</details>

<details>
<summary>PPG terms review, patient burden, and complaint routes</summary>

- PPG Terms & rules, patient burden and what is the objective of the the PPG?
- GTD are updating the documentation that patients must agree to operate within, mostly as a personal and legal safety valve
  - Shares a lot of features with other PPG membership documents from practices around the UK
  - How effective/performative are PPGs?
- What is the recourse for a patient who wants to complain, but doesn't agree to every single term in the documentation? Like what if the 'unknown' (what am I agreeing to keep confidential? what if I don't want to be on a database? what if I don't want to, or can't sit in a meeting with strangers on an irregular schedule?)
  - Are there still functional feedback/complaint mechanisms? What are they?
  - PPG results are SLOW (6 months and still no change on even very small issues), for small or transient PPGs, continuity over time is going to be hard as patients become discouraged by no change, or at least by no immediate change.
  - Without an organising platform or more regular contact, how are patients expected to co-ordinate individual concerns and identify shared problems?
- The documents being available for review is good, but most patients are not well versed in legal speech or procedural jargon, especially where language barriers exist, might be better supported with much less legalese, and instead sticking to a one-page (or maybe 2) that keeps a group casual.
- See [Reviewing PPG terms docs](./PPG-terms-review/PPG-terms-review.md)

</details>

<details>
<summary>GP Patient Survey: question design and why is New Bank's reply rate barely 10%?</summary>

- Further work to do on the GP Patient Survey
- The patient survey (national, written by a couple of major universities) has some pretty obvious oversights, that _might_ be unintentionally hiding the scale of some access problems, and subtly patient-blame
  - Framing a lack of options as preferences, and framing systemic failure as personal decisions
  - The young/comfortable students writing/setting the questions in Cambridge and Exeter unis may not have the same access issues/limitations as many other patients.
- I have the full patient survey questions for follow-up
- Very low ~10% reply rate on New Bank's Patient Survey, way below national average of ~25%.
  - Why so few replies to the survey? Have people lost hope the practice can improve?

</details>

<details>
<summary>Benchmarking vs nearby practices (GTD and non-GTD)</summary>

- Comparing to local/regional practices
  - Next step: compare New Bank and **other GTD sites** to **nearby non‑GTD practices**, and practices of similar sizes/catchments.
  - Early observation: most GTD‑run practices in Manchester cluster around **~2★** overall on Google, with very similar complaint patterns: rudeness/mistreatment, access issues, procedural failings, and a lack of understanding/help from staff.
  - How common **complex access / phone‑blocking / web‑off** models are.
  - Quantify how many GTD practices, and how many local/regional/national practices, **switch their websites/online forms off** outside office hours.
    - May be able to gather this automatically via a simple monitoring script that pulls practice websites from NHS listings.

</details>

### Escalation routes beyond GTD

- Map escalation routes beyond GTD (ICB, NHS England, CQC, ombudsman) specifically for **access and digital exclusion** rather than individual clinical events.
- Escalation is outlined in [ESCALATION.md](./ESCALATION.md).
  - Will be revised before action, but that's the general idea.

The aim is not to “name and shame” a single surgery/company, but to show where **process and tools are systematically failing patients**, especially at New Bank and GTD. Many [Healthwatch groups are tracking these same issues](./meetings-notes/2025-11-26-meeting4/send-to-gtd-team-pre-nov26/GP%20Access%20Issues%20-%20Evidence%20Pack%20-%2026%20Nov%202025%20Bob%20Davies.pdf) all over the country, this is one part of that, and will escalate to Healthwatch Manchester as needed, to encourage them to join the other groups in trying to get these problems fixed everywhere.
