# Digital Access Failures - New Bank Health Centre (NHS GP Practice, Manchester)

This repo documents ongoing concerns about **patient access, digital systems, and front‑door process** at New Bank Health Centre (run by GTD Healthcare).  
It contains only publicly available data so that the evidence and reasoning are transparent to patients, staff, GTD, and anyone else trying to improve access.

[Current meeting files ➔ `meeting-ppg-nov26/`](./meeting-ppg-nov26/)

## Immediate feedback post Nov 26th PPG...

- 2 new doctors and new staff coming soon.
- Complaints about reception seem to be improving, less reliance on agency staff.
- The website will be switched to 24hr accessible. 
  - Doctor has concerns over missing incorrectly logged urgent messages
  - Needs clear communication out of office hours.
- Bookable looks pretty good (but only works for non-registered patients for some unknown reason):
  - See [New Bank Health Centre on Bookable: https://bookable.health/booking/gp-surgery/loc_9a5qmmx644zv](https://bookable.health/booking/gp-surgery/loc_9a5qmmx644zv)

## Progress on making an appointment - Dec 4th 2025
  - Had a day off, and transient pain, so tried again...
  - Previous improvement of 'suggested callback time' input field, has not been kept in the move to PATCHS. Still cannot request an appointment for anything, still dependent on unscheduled calls, despite stating in message that I cannot receive calls in the day as I work nights.
  - Form has "when should we _not_ contact you" question, but it's pointless if the answer is 'do not phone me, ever', or 'I work nights and sleep days (or cannot use my phone at work, or I don't have a phone), so will not see your phone call'.
  - Staff _really_ need to deal with this, I've brought it up at the PPG several times now. LOTS of people work nights/shifts, or otherwise cannot access their phone in work, and are being actively excluded (no wonder so many 1 star reviews).
  - Asked staff who phoned me (reaching me on the second attempt, with 41 minutes between calls, staring at my phone the entire time, because last time I tried to call back after missing 2 calls, I was told to "ask _really_ nicely and _maybe_ a doctor _would consider_ trying again") if they read my mention that I was probably not accessible via phone and she said "I didn't see that", then scrolled down the page, and confirmed my message was indeed present (she did not say outright, but had clearly not read it), but that...
  - She cannot make an appointment (or propose/suggest/start an appointment process) via PATCHs without a phone call anyway. 
  - Request was not deleted, but no response has been made online. Cannot attach further notes, or reactivate the ticket. I 'have' an appointment scheduled, but PATCHS doesn't surface that, or update the ticket.
  - Request status updated to 'Completed'. Cannot reopen or attach any info. Appointment info is NOT added anywhere in the system. 
  - Don't know what would happen if I missed that second call again. Can't afford to risk it, I only have one day off and awake in the day.
  - PATCHS UX sucks. 
  - The 'AI' questions are barely coherent, and as repetitive as the old eConsult route, maybe more so.
  - PATCHS (or elsewhere on the site) _really_ needs a non-phone-based roundtrip (message/chat/booking slot picker) to solve this problem. It's ridiculous that I STILL _must_ be able to answer an unscheduled phone call within business hours, to get an appointment.

## What’s in this repo (brief)

- **Complaint drafts and meeting prep**
  - `ORIGINAL_COMPLAINT.md` - first long‑form complaint about the appointment system (Dec 2024/Aug 2025).
  - `meeting-ppg-nov26/Meeting3-goals.md` - current preparation for the Nov 2025 PPG meeting on access.
  - `meetings-notes/` - Documentation for each meeting, and my prep/issues and received handouts with my notes.
- **Data and analysis**
  - `PatientSurveyBreakdown.md` - breakdown of GP Patient Survey results for New Bank.
  - `reviews/` - Google review HTML/text, parsing scripts, and parsed outputs.
  - `healthwatch-reports/` - Healthwatch reports from around the UK sharing these concerns.

The focus throughout is **patient access**, not clinical care quality.

## Current concerns (Nov 2025 snapshot)

1. **PATCHS website off outside office hours**
   - New Bank has switched online access from eConsult to **PATCHS**.
   - The PATCHS entry point on the practice website is **switched off outside office hours**, and on several checks has also been **down during office hours** when attempting to use it.
   - Since 1 October 2024, NHS rules require practices to provide access to online request routes during core hours; routinely switching the system off appears to fall short of that expectation.
   - PATCHS itself supports a **24/7 non‑urgent/admin route** (config option in their guidance), but it is disabled here.
   - It says "this service closes when we are full", but have not been able to check in office hours, so it may not even meet the current NHS requirement of remaining accessible for admin/non-urgent requests at least during office hours (itself, a low bar).

2. **Digital‑only booking and exclusion**
   - Access is effectively **digital‑only**: no simple “walk in and make an appointment” route and limited scope to book by phone without being sent back online.
   - This excludes people without stable internet, devices, availability or confidence with forms, and adds friction even for confident users.
   - Current system also excludes anyone who can't take a day off for a *chance* at an appointment, anyone who works nights or other weird times, and is directly harmful to the health of the community.

3. **Missed‑call deletion and resubmission loop**
   - If the clinician calls and the patient misses an **unscheduled** call, the **request is deleted** and the patient must start again another day.
   - There is **no same‑day resubmission**, even when the first call was early in the day.
   - Patients are not always notified that their request was deleted and may only discover it by digging through message threads (this might be mitigated by PATCHS but have been unable to check).
   - Unscheduled calls are sometimes labelled as **“missed appointments”**, which is misleading and may distort DNA statistics.
        - This practice appears to have been reduced significantly in August's practice stats (halving reported phone DNAs relative to other DNA types)

4. **Reception**
   - Reviews over several years describe **rude, dismissive, or blocking behaviour** at reception, especially towards distressed or complex patients.
   - 'Rude reception' is a very common complaint, and some reported incidents have been severe.
   - Once patients get through to a GP or nurse, experiences are often positive; the problem is getting through the door. 

5. **Metrics vs reality**
   - Internal appointment metrics can look “fine” or improving, while:
     - GP Patient Survey results still show **39%** finding it hard to get appointments.
     - Google and PATCHS reviews include **many 1★ complaints** about access, downtime, confusion, and reception.
        - The practice/GTD should examine these complaints as issues like these are already appearing as reviews on GTD-managed practices (including New Bank).
   - The concern is that **what is measured** (e.g., completed appointments) hides those who are driven away or give up, because only a small proportion of those then go on to write reviews on any platform (some simply can't, the quietest contingent are those most lost).

### Open questions for further research

- Staff have claimed "everyone does this" regarding making patients 'start over' (deleting requests for missed calls, or multiple daily submissions/second after deletion on same day). How many practices have systems that delete patient requests? 
    - PATCHS reviews suggest that it does not solve this.

- Staff have claimed 'of course reviews are bad' (as if ALL reviews are bad, because 'nobody writes good reviews') in the PPG, but I don't see why this is an excuse. A LOT of local practices have bad reviews, often for very similar reasons, but there are also a lot of practices with great reviews (including 1 under GTD), so the pattern doesn't hold for ALL practices, but how many does it hold for, and what are their common threads?

- From a design perspective, the way PATCHS handles limits seems crazy. It's so lazy and hostile to patients, but the PPG isn't really 'systems design and UX' meeting.
    - It might be useful to know if/when GTD _do_ discuss these issues, with whom and how often? Is there anyone in the room who has even the faintest consideration of the patient workflow through their systems? Do they accessibility-test themselves?

- The language around request types is confusing. I don't know if what I need to see a doctor about falls under clinical or admin, or what is a non-pressing issue or what's urgent. If I have some pain, or a meds question, is that clinical? Who knows? Where to find out? There's several layers of website, and none of them seem to say the same thing. These are presumably different layers of NHS infrastructure?

---

## Ongoing work

1. **Summarised New Bank’s own reviews**
   - Parsing and clustering **1★ and 2★ reviews** to understand themes (access, reception, repeat failures, etc.)
2. **Comparing across GTD Healthcare practices**
   - Early observation: most GTD‑run practices in Manchester cluster around **~2★** overall on Google, with very similar complaint patterns.
   - Next step: compare New Bank and **other GTD sites** to **nearby non‑GTD practices**, and practices of similar sizes/catchments.
3. **Looking wider**
   - Using national NHS data to see:
     - How common **complex access / phone‑blocking / web‑off** models are.
     - How New Bank’s access and DNA patterns compare with regional and national baselines.
     - Several local/regional Healthwatch groups already reporting upon this, see our evidence report in nov26 meeting.

The aim is not to “name and shame” a single surgery, but to show where **process and tools are systematically failing patients**.

---

## Original appointment‑system complaint (Dec 2024) - in brief

This section summarises the original complaint that started the project; the full text lives in `ORIGINAL_COMPLAINT.md`.

- **Unpredictable availability**
  - Patients cannot wait by the phone all day for an unscheduled call. Jobs, caring responsibilities, signal problems, or simply stepping away for 5 minutes mean missed calls are often not the patient’s fault.
- **Deleted requests create barriers**
  - Deleting requests after failed calls forces a **daily resubmission loop**, delaying care with no guarantee of success.
- **Vulnerable patients suffer most**
  - Elderly, disabled, or digitally excluded patients struggle with long forms, short windows, and phone‑only call‑backs.
- **Misleading “missed appointment” label**
  - Labeling unscheduled calls as “missed appointments” inflates DNA statistics and shifts blame to patients. 
    - (this may have been mitigated by workflow change, awaiting future monthly stats from the practice)
- **No or poor notification**
  - Requests can be deleted without clear notification; patients only find out if they proactively check.
    - (this may have been mitigated by switch to PATCHS, but as of yet have been unable to check because it's always offline)

These themes still apply under PATCHS - in some respects, the move has **made access worse** by turning off 24/7 intake.

---

## Proposed improvements (high level)

These are the recurring asks across complaints, meetings, and notes in this repo:

- **Always‑on intake**
  - Keep an online route open **24/7** for non‑urgent/admin requests, with clear messaging about when a response will come.
  - For PATCHS specifically: enable the documented 24‑hour mode by default (and ideally make it the product default, not opt‑in).
  - Nobody expects doctors to reply outside of office hours, but the whole point of a website is to eliminate the concurrency requirement. Time-gating the website is *professionally incompetent*.
- **Predictable, scheduled contact**
  - Offer **time windows or booked call times** instead of “sometime today”.
  - Allow patients to **reschedule the same request** without re‑entering everything from scratch. 
    - PATCHS *might* support these, but it's unclear in the FAQs and I can't test myself because the site is down or offline
- **Multiple access routes**
  - Ensure there is a **viable non‑digital path** (walk‑in or phone) that does not simply send people back to the website.
  - The receptionist tells people "You have to use the website" (often rudely, with no concept that this might not be a viable solution for the patient)
    - In previous meetings staff have assured the group that this should not happen, yet it still does. Patients do not want to put undue burdens on staff, but it shouldn't be the responsibility of patients to guard staff from doing their job.
- **Reception support and accountability**
  - Invest in pay, training, and support for reception.
  - Give reception enough **autonomy and tools** to help instead of just defending the system.
  - Consider bumping the wage to attract skill where it matters most (advertised locally?).

## Professional whining

- This seems to be a pattern at the moment, with practices [claiming](https://www.oakwoodlanemedical.nhs.uk/2025/10/07/availability-of-online-consultations-from-1-october-2025/) things like "The new requirement to allow patients unlimited online access for non- urgent medical requests, throughout core hours, could make it more likely that we will have no choice but to create hospital-style waiting lists to meet patient need. We do not believe that this is a solution that anyone wants." or "GPs and their teams are under huge pressure – caring for more people with fewer resources."
    - This is patient-blaming (and a false dichotomy), there's nothing wrong with queues if you're actively working them.
    - People are much less stable if they have no idea whether they can even ask for help today, or if they have to wait till tomorrow to try and fail again.
    - Falling back to blocking the patient completely is _poor_.

It's failure as a feature, not a bug, staff are choosing to outright reject patients before they can even start, then failing to measure the effect because angry reviews don't drive policy.

---

## TODOs / Next Steps / Escalation (for this project)

- [ ] Locate and link the **PATCHS user manual / guidance page** that describes enabling 24/7 admin/non‑urgent mode.
    - I already found the other pages, but I can't find this one.
- [ ] Quantify how many GTD practices, and how many local/regional/national practices, **switch their websites/online forms off** outside office hours.
    - May be able to gather this automatically via a simple monitoring script that pulls practice websites from NHS listings.
- [ ] Quantify how often “bad reception” appears in reviews across GTD vs local comparators.
- [ ] Map escalation routes beyond GTD (ICB, NHS England, CQC, ombudsman) specifically for **access and digital exclusion** rather than individual clinical events.
