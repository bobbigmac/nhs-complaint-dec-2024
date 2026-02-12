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
  - [meeting4-goals.md](./meeting-ppg-feb4/meeting4-goals.md) - Meeting 4 (Feb 2026) prep
- **Data and analysis**
  - `patient-survey-breakdown/` - breakdown of GP Patient Survey results for New Bank and further research.
  - `reviews/` - Google review HTML/text, parsing scripts, and parsed outputs.
  - `messages/` - Log of sent messages (mostly emails, complaint-related only).
  - `healthwatch-reports/` - Healthwatch reports from around the UK sharing these concerns.
- [My own experience](#My-patient-experience-with-New-Bank) trying (and failing) to see my doctor, as a patient who works nights (among other issues).
- [Notes](#Notes) - My notes that don't fit anywhere else.
- [Ongoing/further Research](#ongoingfurther-research) - What's next.
  - [Reviewing the updated draft PPG terms docs](./PPG-terms-review.md)
  - [Exclusion questions - Is exclusion a problem here?](./Exclusion-questions.md)
- **Produced reports/evidence packs**
  - [General GP practice stats and scope/environment notes](./meetings-notes/2025-09-10-meeting2/benchmarks-summary-sept-10.md)
  - [PATCHS trustpilot reviews for lots of useful patient input](./reviews/PATCHS/output%20reports/PATCHS%201-2-3%20Star%20Reviews%20with%20Summary%20Panel%20Landscape.pdf)
  - [Patient blaming evidence pack](./meeting-ppg-feb4/PatientBlaming-README.md)
  - [Affected patients estimates and Healthwatch overview](./meeting-ppg-feb4/GP%20Access%20Evidence%20-%20Websites%20triage%20and%20digital%20barriers.md)
  - [Poor NHS access and political extremism](./meeting-ppg-feb4/GP%20Access%20Evidence%20-%20Immigration%20blame%20and%20far-right.md)
  - [Google reviews management and good response patterns](./meeting-ppg-feb4/reviews-management.md)

The focus throughout is **patient access**, not clinical care quality.

## Main concerns

1. **Digital‑only booking and exclusion**
  - Access is effectively **digital‑only**
    - No simple “walk in and make an appointment” route and impossible to book by phone without being sent back online, and still requires unscheduled daytime callback.
  - This excludes people without stable internet, devices, availability or confidence with forms, and adds friction even for confident users.
  - Current system also excludes anyone who can't take a day off for a *chance* at an appointment, anyone who works nights or other weird times and many other groups (documented/estimated in the november meeting docs).

2. **Unscheduled missed calls cause deletion/resubmission loop**
  - Alienates patients
    - If the clinician calls for triage OR the receptionist calls to arrange an appointment, and the patient misses two **unscheduled** calls (typically, but not consistently within less than an hour, with no route to schedule or bypass the call), the **request is closed** and the patient must start again.
      - This __was__ enforced at 1 and only 1 appointment request per day but have not yet re-tested since moving to PATCHs. 
      - I have had at least 1 request placed via the old website (the second in the same day, after missing 2 calls) be deleted on the same day, with the explicit reason that it was submitted on the same day.
    - Notification issues _might_ have been fixed by PATCHs, but should re-test patients are notified correctly (in my own case, I was not in the second case).
   - Reporting of missed unscheduled calls __were__ sometimes labelled as **“missed appointments”**.
        - This practice appears to have been reduced significantly in August's practice stats
        - Phone DNAs reported halved relative to other DNA types from July to August

3. **Reception**
  - Reviews over several years describe **rude, dismissive, or blocking behaviour** at reception, especially towards distressed or complex patients.
  - 'Rude reception' is a very common complaint, and some reported incidents have been __severe__, including patients in distress, being laughed at by staff or otherwise driven to leave.
    - Reviews are subjective, but repeated instances of similar types of mistreatment from real Google users suggest a terrible pattern that needs to be fixed.
  - Once patients get through to a GP or nurse, experiences are often (tho not universally) positive...
    - TODO: As of November 2025, slight evidence this is improving, though reception/process complaints still among most common negative reviews.
  - The automated sliding front door sticks (literally blocking access)

4. **PATCHS website off outside office hours**
  - Partially solved, admin requests are now open out of hours (since 14th Jan)
  - but... Appointments cannot be requested.
    - This is only enabled when the office is open
    - Why? It wastes the benefit of a website, which is to avoid synchronous availability needs.

5. **Metrics vs reality**
   - Investigate lost/excluded patients
   - No active complaints procedure beyond PPG
    - [Contact the practice](https://newbank.nhs.uk/form/contact-the-practice/) shows `Form Unavailable`

---

## My patient experience with New Bank

I have been trying to get an appointment at New Bank since December 2024 (when I registered), but as I work nights the process has been almost impossible (the only doctor's appointment I've had took a year, and I had to take a day off and stay awake 6 hours late waiting on an unscheduled office-hours call for that to be possible). Details below...

  - Had a day off (Dec 4th 2025), and transient pain, so tried again...
  - Tried using Bookable.health first, good UI. Gets to the last step, after picking an appointment datetime, then tells me I can't book it because I'm registered at the practice. Nearly moved my registration elsewhere just so I could use Bookable because that's actually what I want the process to be.
  - Used PATCHS
    - Previous improvement of 'suggested callback time' input field, has not been kept in the move to PATCHS. Still cannot request an appointment for anything, still dependent on unscheduled calls, despite stating in message that I cannot receive calls in the day as I work nights.
    - Form has repetitive questions that barely make any sense (I think they put the 'AI' label on it, but there's no way these questions come from a modern LLM-based system).
    - Form has "when should we _not_ contact you" question, but it's pointless if the answer is 'do not phone me, ever', or 'I work nights and sleep days (or cannot use my phone at work, or I don't have a phone), so will not see your phone call'.
    - Staff _really_ need to deal with this, I've brought it up at the PPG several times now. LOTS of people work nights/shifts, or otherwise cannot access their phone in work, and are being actively excluded (no wonder so many 1 star reviews).
  - Asked staff who phoned me (reaching me on the second attempt, with 41 minutes between calls, staring at my phone the entire time, because last time I tried to call back after missing 2 calls, I was told to "ask _really_ nicely and _maybe_ a doctor _would consider_ trying again") if they read my mention that I was probably not accessible via phone and she said "I didn't see that", then scrolled down the page, and confirmed my message was indeed present (she did not say outright, but had clearly not read it), but that...
    - She cannot make an appointment (or propose/suggest/start an appointment process) via PATCHs without a phone call anyway. 
    - Request was not deleted, but no response has been made online. Cannot attach further notes, or reactivate the ticket. I 'have' an appointment scheduled, but PATCHS doesn't surface that, or update the ticket.
    - Request status updated to 'Completed'. Cannot reopen or attach any info. Appointment info is NOT added anywhere in the system. 
  - Don't know what would happen if I missed that second call again. Can't afford to risk it, I only have one day off and awake in the day.
  - PATCHS UX sucks. 
    - The 'AI' questions are barely coherent, and as repetitive as the old eConsult route, maybe more so.
    - PATCHS (or elsewhere on the site) _really_ needs a non-phone-based roundtrip (message/chat/booking slot picker) to solve this problem.
    - It's ridiculous that I STILL _must_ be able to answer an unscheduled phone call within business hours, to get an appointment.
    - The entire message/request content is squeezed into a small scrollable box within the webpage, making it hard to read (this is just really lazy web design by PATCHS). It also seems to auto-scroll itself to the bottom every few seconds, so you have to find your place again if you're rereading the content (it also does not display properly in printed form, as it prints the box, and only a little of the contents).
  - Attended appointment, good discussion with doctor, submitted samples for tests
  - Didn't have a day where the doctor was open and I would be able to answer an unscheduled call randomly in the day.
  - Tests all came back pretty much normal ~~(was not tested for calprotectin, despite asking for that test)~~ (rechecked this, it appeared a few days later, but lower in the list, reporting low end of normal), health condition in NHS app was closed on jan 6th, with no follow-up.
  - The app doesn't say which doctor closed the condition I am trying to get diagnosed, but I consider this an oversight, as the cause of my condition was not identified, only things that are NOT the cause (i.e. I am still sick, but the practice data flagged condition as PAST, pre-mature diagnosis end). 
    - Case was closed without confirmation from the patient or thorough check about the current status.
    - Process issue or lack of care?
    - This same issue was raised by another patient in the Nov 26th PPG.
      - Likely, the process/workflow encourages closing off conditions, but doesn't recognise if the patient was diagnosed/treated, only that the tests were done.
    - From the log, it reads like someone came back after new year and just ticked off whatever tests were on the list, because they clearly didn't read the patient notes about what the tests were looking for.
  - Tried to make an appointment at the front desk (Jan 9th), told "You HAVE to do it online" (still), mentioned that management had said in the PPG meetings I _should_ be able to make an appointment without going online, and reception said they can do it for me, but I would have to be able to receive an unscheduled call (still), and briefly explained I work nights and sleep days, so cannot receive a call, and was told when she checked my history "there's nothing here about that", and I briefly explained that my case had been closed prematurely, but that the doctor had told me to make an appointment to see her next time.
    - She took a note to ask (the ops manager) about it on Monday and she offered to text me Monday.
    - She was polite and seemed understanding, an improvement over last time I tried to make an appointment at the front desk.
  - Woke up monday evening to 2 missed calls (no text message) at 10:44 and 11:33.
    - Missed them because I told the receptionist I would be asleep and she told me she'd send a text message.
    - I saw the receptionist write a post-it about sending me a text message, but that turned into regular 2 phone calls, but with no entry created on the system.
  - Went to front desk, told the receptionist (different one from friday) that they rung me twice, and it should be about making an appointment, but she checked and told me it wasn't on the system, so wouldn't book me an appointment. I told her a short version of the story so far, and she still couldn't make an appointment.

### Notes

- The workflow/system decision-maker at this practice seems to believe "**a doctor MUST be present and online at the moment someone requests an appointment**".
  - This neglects/wastes the simple benefit of a web-based platform is to **decouple doctor availability from patient access**. The mandatory phone call is a decision being made, not an oversight?
  - I want to know who specifically is FORCING a workflow that keeps appointment requests offline outside of office hours, and who is mandating an in-office-hours phone call as a mandatory part of getting an appointed time for any type of meeting.
  - If the rationale is "what if someone accidentally asks about something urgent, and a doctor doesn't see it until morning" seems like something that **could** happen (and is already mitigated by several sentences on every page just to get this far about 'no urgent issues'), being used as justification to continue harm that **is already happening** (alienating/inconveniencing some people outright).
    - I suspect this is about avoiding a backlog of overnight requests to be processed each morning, which is again, a false economy. Sure, you're avoiding _some_ requests that _could_ have been made in-hours, but you're also locking out quite a lot of people from having any access at all, which just compounds the mandatory unscheduled phone call problem.
    - I'm curious about the actual numbers on this... How many requests _are_ made overnight if it is accessible? Do any of these missing people turn up if the practice trials it?
    - It _feels_ like the practice operates patient care as a production line, where each doctor focuses only on part of the process. I don't think this results in good care. ~~A person is not a Model T Ford.~~
      - Healthcare is a relationship, not a transaction.
      - How do legislative requirements have an effect here? 
- The current patient survey status shows 22% of patients report it being hard to get an appointment (an improvement on last year's 39%, tho this isn't quite comparing like to like, as the 39% is the inverse of people who found it easy to contact the practice by phone, and also excludes the "I haven't tried" contingent). I _think_ the real number is higher because the patient survey is worded (unintentionally) to 'downplay' access issues by having some access issues fall through the gaps between available answers.
- On the diagnostic issue, I don't think it reaches clinical negligence (it hasn't resulted in the worsening of my condition), but certainly premature diagnostic closure or diagnostic delay (though this is made more severe by the poor quality of access) does seem an appropriate label. At least one other PPG patient mentioning this suggests it's not uncommon here to close conditions without full investigation or identification of causes.
  - I _feel_ like staff at this practice think you will just get better if they ignore you and delete you at every opportunity, so you always have to start over with the most inaccessible/inconvenient system design choices possible. I've lost count of how many times I had to start over.
- The front door (sliding) sticks, lol. I went to get a test kit one morning at opening time, stood outside the doors for a minute or so, thinking they just hadn't unlocked them yet, but when the receptionist noticed me knocking, she just had to force the doors open. Literally a physical blockage, kinda funny, in a way.
  - Front door has been fixed as of Feb 4th meeting

### Ongoing/further research

- Staff have claimed "everyone does this" regarding making patients 'start over' (deleting requests for missed calls, or multiple daily submissions/second after deletion on same day). How many practices have systems that delete patient requests? 
    - PATCHS reviews suggest that it does not solve this.
    - Confirmed myself, 2 missed calls results in no further action, ticket is closed, cannot be reopened.

- Staff have claimed 'of course reviews are bad' (as if ALL reviews are bad, because 'nobody writes good reviews') in the PPG, but I don't see why this is an excuse. A LOT of local practices have bad reviews, often for very similar reasons, but there are also a lot of practices with great reviews (including 1 under GTD), so the pattern doesn't hold for ALL practices, but how many does it hold for, and what are their common threads?

- From a design perspective, the way PATCHS handles limits seems crazy. It's so lazy and hostile to patients, but the PPG isn't really 'systems design and UX' meeting.
    - It might be useful to know if/when GTD _do_ discuss these issues, with whom and how often? Is there anyone in the room who has even the faintest consideration of the patient workflow through their systems? Do they accessibility-test themselves? 'Mystery shop' GTD practices? 

- The language around request types is confusing. 
  - Many patients don't know if what they need to see a doctor about falls under clinical or admin, or what is a non-pressing issue or what's urgent. 
    - If I have some pain, or a meds question, is that clinical? Who knows? Where to find out? 
    - There's several layers of website, and none of them seem to say the same thing. These are presumably different layers of NHS/practice infrastructure? 
    - Maybe better visibility of the organisational model would be useful on the site. It's not clear who is responsible for what.
  - The categories seem to be emergency (call 999), urgent (a doctor will try and get you in asap) or normal (usually within 3 days)

- PPG Terms & rules, patient burden and what is the objective of the the PPG?
  - GTD are updating the documentation that patients must agree to operate within, mostly as a personal and legal safety valve
    - Shares a lot of features with other PPG membership documents from practices around the UK
    - How effective/performative are PPGs?
  - What is the recourse for a patient who wants to complain, but doesn't agree to every single term in the documentation? Like what if the 'unknown' (what am I agreeing to keep confidential? what if I don't want to be on a database? what if I don't want to, or can't sit in a meeting with strangers on an irregular schedule?)
    - Are there still functional feedback/complaint mechanisms? What are they?
    - PPG results are SLOW (6 months and still no change on even very small issues), for small or transient PPGs, continuity over time is going to be hard as patients become discouraged by no change, or at least by no immediate change.
    - Without an organising platform or more regular contact, how are patients expected to co-ordinate individual concerns and identify shared problems?
  - The documents being available for review is good, but most patients are not well versed in legal speech or procedural jargon, especially where language barriers exist, might be better supported with much less legalese, and instead sticking to a one-page (or maybe 2) that keeps a group casual.


- Further work to do on the GP Patient Survey
  - The patient survey (national, written by a couple of major universities) has some pretty obvious oversights, that _might_ be unintentionally hiding the scale of some access problems, and subtly patient-blame
    - Framing a lack of options as preferences, and framing systemic failure as personal decisions
    - The young/comfortable students writing/setting the questions in Cambridge and Exeter unis may not have the same access issues/limitations as many other patients.
  - I have the full patient survey questions for follow-up
  - Very low ~10% reply rate on New Bank's Patient Survey, way below national average of ~25%.
    - Why so few replies to the survey? Have people lost hope the practice can improve?

- Comparing to local/regional practices
    - Next step: compare New Bank and **other GTD sites** to **nearby non‑GTD practices**, and practices of similar sizes/catchments.
    - Early observation: most GTD‑run practices in Manchester cluster around **~2★** overall on Google, with very similar complaint patterns: rudeness/mistreatment, access issues, procedural failings, and a lack of understanding/help from staff.
    - How common **complex access / phone‑blocking / web‑off** models are.
    - Quantify how many GTD practices, and how many local/regional/national practices, **switch their websites/online forms off** outside office hours.
      - May be able to gather this automatically via a simple monitoring script that pulls practice websites from NHS listings.

- Map escalation routes beyond GTD (ICB, NHS England, CQC, ombudsman) specifically for **access and digital exclusion** rather than individual clinical events.
  - Escalation is outlined in [ESCALATION.md](./ESCALATION.md). 
    - Will be revised before action, but that's the general idea.

The aim is not to “name and shame” a single surgery/company, but to show where **process and tools are systematically failing patients**, especially at New Bank and GTD. Many [Healthwatch groups are tracking these same issues](./meetings-notes/2025-11-26-meeting4/send-to-gtd-team-pre-nov26/GP%20Access%20Issues%20-%20Evidence%20Pack%20-%2026%20Nov%202025%20Bob%20Davies.pdf) all over the country, this is one part of that, and will escalate to Healthwatch Manchester as needed, to encourage them to join the other groups in trying to get these problems fixed everywhere.
