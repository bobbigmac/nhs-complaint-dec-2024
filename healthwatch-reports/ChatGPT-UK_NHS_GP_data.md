# UK NHS GP data

#### You:
Go and find some UK data for me. I want to know two things... How many nhs GP practices (absolute and share of) close their website when their office is closed? (there's been some recent standards changes so the govt have some data on this) and how many nhs GP practices require you to use their website to request an appointment? Less data on this probably, but look for related data to get a sense of it

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
Short version: there isn’t a clean national stat for either of the things you’re asking, but there *is* some relevant government data we can lean on. I’ll split it.

---

## 1. Practices that “close” their website when the practice is closed

There’s **no national metric** that directly says “X GP practices take their whole website down / block it out-of-hours”.

What *does* exist is:

- NHS England’s big GP website usability study and guidance.\
  It found lots of sites using pop-ups/overlays which can effectively block access to the homepage (27% of test participants could not get past an overlay when it was the first thing they saw, another 5% struggled beyond the homepage). citeturn7view0\
  That’s evidence of **pattern-level problems**, but it’s about UX, not a count of “closed sites”.

- The new **online consultation statistics** (“Submissions via Online Consultation Systems in General Practice”).\
  For **September 2025** in England: citeturn12view0turn16view0

  - 6,032 practices were known to have at least one online consultation (OC) system.
  - 5,799 of those received ≥1 submission that month (so **233 practices with a system but zero submissions**).
  - 6.5m patient submissions in the month (4.4m clinical).

  The supporting info explicitly says:

  - OC systems can be **switched on or off by practices**.
  - If a practice with an OC system has no submissions in a month, that may mean they **withdrew system availability** for that period, or that all attempts were aborted, etc., and you *must not* assume anything more granular (e.g. specific times of day). citeturn16view0

So if you really stretch it, the upper bound on “practices that may have effectively switched off online access for some/all of September 2025” is those 233 with zero submissions, i.e. about **3.9% of practices with an OC system** (233 / 6,032). But:

- that’s **not** about the *website* being down,
- it’s **monthly, not hourly**,
- and the official docs explicitly warn you not to infer availability patterns out of it. citeturn16view0

Bottom line for Q1:

- **Absolute number:** no published figure for “websites closed when practice closed”.
- **What we can say:** almost all practices have a website; almost all keep it technically available 24/7, but a non-trivial minority use overlays / pop-ups / OC toggling that can effectively shut the **digital front door** for part of the time. The only national dataset (the OC submissions collection) gives an *upper bound* (≈200–250 practices in a month that may have their OC unavailable entirely), but not a robust estimate of out-of-hours “site closed” behaviour. citeturn12view0turn16view0turn7view0

---

## 2. Practices that *require* you to use the website to request an appointment

Again, there is **no official stat** of “practices that only accept appointment requests via the website”.

In fact, the national policy framework leans the other way:

- **Covid-era “total triage” guidance** and later updates say all practices must have access to an online consultation system, but emphasise that **non-digital routes (phone/in person) must still exist** so that patients who can’t use digital aren’t excluded. citeturn8search0turn8search7turn8search25

- The 1 October 2025 contract change:\
  From that date, practices in England are required to keep their **online consultation tools running throughout core hours (typically 8:00–18:30)** for non-urgent appointment requests, admin, medication queries, etc. citeturn15search0turn15search3turn15search15

- NHS England’s September 2025 OC statistics + ministerial commentary:

  - Official stats: 6,032 practices with an OC system; 6.5m submissions in September 2025. citeturn12view0
  - Pulse’s read of the same dataset: **96.1%** of practices have an OC system; **93.8%** are receiving submissions via it. citeturn14view0

  That gives you the **scale** of “website/online-first” infrastructure: essentially *universal*.

- ONS Health Insight Survey (Wave 14, Jul–Aug 2025) on how people actually contact GPs: citeturn17view0turn14view0
  - For *urgent* appointments, **telephone** is still dominant (≈55–56% of contacts).
  - For **prescriptions**, adults were most likely to use the NHS/app route (42.9%) – here online overtakes phone – but **overall**, phone is still the most common method (\~42.1%, per Pulse quoting ONS).

So what does that give you re: “requiring” web use?

- Regulation and guidance explicitly require that **a non-digital route remains available** (phone, in person, or staff completing the online form for the patient). citeturn8search0turn8search25turn8search16
- The data show that:
  - **\~96%** of practices have an OC platform and are *supposed* to keep it open all day in core hours. citeturn12view0turn15search3turn14view0
  - A slightly smaller share (\~94%) are actually getting submissions in any given month, so a small minority are effectively not using what they have. citeturn12view0turn16view0
  - Patients’ actual behaviour is still mixed: online is huge and growing (6.5m+ submissions/month, and dominant for some use-cases like prescriptions) but **has not fully displaced phone**. citeturn12view0turn15search1turn17view0

There’s **no national dataset** that says “these N practices refuse appointment requests by phone and insist on the website”. Doing that would in fact be **out of line with national guidance** and is exactly the sort of thing the BMA and HSSIB have been pushing back on in the context of safety and access. citeturn8search6turn15search7

Realistically, combining policy + the data:

- Practically **all** practices now have a web/online route for appointment requests (≈96%+ with OC).
- A **subset** of those (unknown size) run “total triage” where *in practice* almost everything starts via an online form, but with reception staff filling it in over the phone for people who can’t.
- Explicit, hard “website only, no phone” access policies would be contractually risky and are not measured centrally – so we can’t assign a number, and it’s probably quite small in pure form, even if many sites *strongly push* you toward the online form.

---

### TL;DR in numbers / bounds

- **Total GP practices (England):** ≈6.3k (exact figure is in the list-size dataset; OC stats and Pulse’s 96.1% figure imply that ballpark). citeturn12view0turn13view0turn14view0
- **Practices with an online consultation system (Sept 2025):** 6,032 (**\~96.1%** of practices). citeturn12view0turn14view0
- **Practices with an OC system but zero submissions that month:** 233 (≈3.9% of those with OC; an upper bound on “system may have been effectively off”, but *not* robust evidence on out-of-hours behaviour). citeturn12view0turn16view0

For both things you care about (websites “closed” out-of-hours, and practices *requiring* online for appointments) the short honest answer is:

> **There’s no clean, published count.**\
> What we *do* have is strong evidence that online is now nearly universal and heavily used, that systems can be switched on/off (and sometimes are), and that policy explicitly says practices must still offer non-digital routes.

If you want to actually quantify this yourself, the only real option is to:

- pull the **practice-level OC CSV** for several months,
- and/or do your own HTTP/UX probing on a sample or the full set of practice websites,\
  then infer availability patterns. The official stats stop short of doing that for you on purpose.


#### You:
Look at recent local councils committee reports or literally anything of other patients trying to solve the access issue anywhere in England

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
Here are some very concrete, recent examples of patients + councils in England trying to fix the exact GP access / digital front door mess you’re talking about.

---

## 1. Patients pushing back on online-only / “closed” forms

### Healthwatch Hertfordshire – *Online GP Services: Patient Views and Experiences* (Feb 2025)

- 477–500 residents surveyed about using GP websites / online services. citeturn2search0turn2search1
- Big spread of experience: \~42% negative, 33% positive, 26% mixed. citeturn2search1
- Two-thirds use the **practice website** to contact the GP; most use online to book appointments/repeat scripts, so this is very much “website as front door”. citeturn2search1

Patients explicitly complain that:

- The **online consultation system is often switched off**:
  - *“The online consultation closes when they have had too many enquiries. Sometimes by 9am, then you have to wait until the next day.”* citeturn2search0
- Some practices **block submissions outside office hours**:
  - People report they “cannot submit consultation forms online outside of 9-5 Monday to Friday” and that short submission windows make the service useless if you work/care. citeturn2search0
- People ask for **24/7 form submission** with responses in surgery hours, instead of the form literally turning off out of hours. citeturn2search0

Their recommendations (which have gone to the ICB Primary Care Transformation Committee) include:

- Make forms available 24/7 (triaged next working day).
- Simplify and shorten forms; cut repetitive questions.
- Explicitly design for disabled / digitally excluded patients, with alternative routes and accessible formats. citeturn2search0turn2search1

This is basically a patient-authored blueprint for “don’t slam the digital front door shut”.

---

### Healthwatch Tower Hamlets – Patient Experience Q2 2024/25

- Regular borough-wide PER report with a dedicated section on **online consultations (apps/forms)**. citeturn0search20turn1view2
- **65% of reviews that mentioned online consultations were negative**; people report:
  - Long and complex forms.
  - Limited appointment types.
  - The system “closing” once slots are used up. citeturn0search20

They explicitly tag **“booking appointments”** and **“appointment availability”** as high-negativity themes and recommend improving booking routes (phone *and* online) and availability. citeturn1view2

---

### Healthwatch Ealing – Patient Experience Q4 2024/25

- 1,416 reviews across services; 544 about GPs. citeturn6view1
- They highlight persistent issues with:
  - Difficulty getting through on the phone (82% of related comments negative).
  - Booking systems where *“once they get through in the queue, all the appointments for the day are fully booked.”* citeturn6view1

On digital:

- They recommend PCNs **“take on an online booking system that provides more flexible online booking hours”**, because current options are constrained to specific, inconvenient times. citeturn6view1
- There’s a note from a practice manager that eConsult is centrally procured by NWL, practices can’t change the layout/length of the forms, which is exactly the “we hate it too” vibe. citeturn6view1

So you have a documented patient case for: “expand online booking hours, don’t just have a tiny window”.

---

### Healthwatch Westminster (covering NW London) – *What do patients think about access?* (Sept 2024)

- 228 people (survey + focus groups) feeding into North West London ICS’s “same day hubs” plans. citeturn3view0
- Patients report:
  - PATCHS online consultation is hard to use, **especially for older / digitally excluded** people.
  - Long waits on phones, limited options to book in advance, language barriers. citeturn3view0

The ask from patients here:

- Keep **flexible options**: online, telephone, and in-person booking.
- Ensure **triage is done by clinical staff**, not just an algorithm.
- **Meaningful consultation** with residents before access models change. citeturn3view0

So that’s another region where patients are already pushing for “multi-channel, not online-only”.

---

### Healthwatch Wandsworth – *Experiences of accessing GP practices* (2024–25)

- Project specifically set up because GP access experiences were “highly varied”, including issues **“utilising digital healthcare applications”** and understanding how primary care is changing. citeturn1view1
- Recommendations include:
  - Stronger, clearer messaging on how to access care and what your options are.
  - Making sure **patients know they can request face-to-face** if they’re only being offered phone. citeturn1view1
  - A patient charter (from the new GP contract) to be displayed on practice websites.

Again, that’s patients explicitly using Healthwatch to push for better digital comms and preserving choice of channel.

---

## 2. “Digital front door” pilots: patients interrogating the model

### Kent – *ANIMA: The Digital Front Door Project* (Healthwatch Kent / Tunbridge Wells PCN)

- 4 surgeries, before/after implementation of ANIMA. citeturn5view0
- After rollout:
  - **Typical contact method** shifts massively: 48% online via ANIMA vs 43% phone, 9% walk-in.
  - Phone usage falls by 44%; online becomes the main route. citeturn5view0
  - Waiting times for appointments improve: “same-day” becomes the most common reported wait; “a week or more” drops. citeturn5view0

But 33% rate their experience of ANIMA as **poor**, and when you read the comments you see all the familiar stuff:

- Complex, long forms; irrelevant questions.
- Crashes / resets; not sure if the request was sent.
- Accessibility issues (screen readers, older users, low digital confidence).
- Feeling **“pushed onto ANIMA”** and that it’s “another layer of bureaucracy” between patient and GP. citeturn5view0

Patients’ suggestions in this report:

- Make ANIMA simpler and more transparent.
- Ensure **real alternatives** remain (phone, receptionist completing the form).
- Address triage and urgency signalling so the system doesn’t under- or over-escalate. citeturn5view0

So Kent essentially has a detailed, patient-authored critique of a full digital front door implementation.

---

## 3. Council & scrutiny committee work on GP access

Local authorities are also leaning on this, usually via:

- **Health Overview & Scrutiny Committees (HOSCs) / Health & Adult Care Scrutiny**
- Feeding in **Healthwatch reports** and ICS data.

Some recent examples:

### Stockton-on-Tees – *Scrutiny Review of Access to GPs and Primary Medical Care* (Oct 2023)

- Adult Social Care and Health Select Committee ran a full scrutiny review. citeturn0search11turn1view4
- They look at:
  - Appointment slot mapping / capacity.
  - PCN and ICB data on access.
  - National comms campaign on GP access and care navigation.

It’s more system-level than website-specific, but it’s exactly the governance route for challenging access models locally.

---

### Barnet – *Primary Care (GP) Access Task and Finish Group* (Adults & Health Overview and Scrutiny, 2024)

- Dedicated **Task & Finish group** set up just for GP access. citeturn0search7
- Inputs include:
  - ICB reports and national GP access data.
  - Healthwatch evidence and patient feedback.

Barnet is using this to interrogate how practices are handling demand, including digital routes.

---

### Leicestershire – Health Overview & Scrutiny Committee (June 2025)

- Performance update showed **additional primary care appointments** delivered over winter 24/25; HOSC discussed variations across 150 practices. citeturn4view0
- Notable bits:
  - **All GP practices now on cloud-based telephony**, improving the call experience.
  - Members raise concerns about services being “delivered through a computer screen” instead of face-to-face and question if this is best for patients. citeturn4view0
  - ICS reps acknowledge that not everyone can access tech; they commit to a mix of online and in-person and to better triage into appropriate modes. citeturn4view0

So you have councillors explicitly challenging digital-only drift.

---

### Other councils with GP access as a standing issue

- **Kent County Council HOSC** – GP access is a recurring agenda/work-programme item in 2024/25. citeturn0search2turn0search6
- **Devon Health & Adult Care Scrutiny (Sept 2024)** – work programme explicitly includes GP access as a priority alongside waiting times, with ICS involvement. citeturn0search15
- **Inner North East London JHOSC (Waltham Forest, etc.)** – recent meeting lists “improvements to GP access” as a key topic for cross-borough scrutiny. citeturn0search14
- **Bury Health Scrutiny Committee (July 2025)** – includes “access to healthcare: pharmacy, dentistry and primary care” as an ongoing workstream, with Healthwatch Bury feeding in patient experience. citeturn0search23turn4view1

So yes, there’s a reasonably consistent pattern of councils using scrutiny powers to examine GP access, with Healthwatch supplying the patient-side data.

---

## 4. The recurring patterns / asks from patients

Across all those bits of evidence, the same themes keep popping up:

- **Digital gates that close too early**
  - Online forms that **shut once capacity is reached**, sometimes by 9am, forcing people to try again the next day. citeturn2search0turn0search20
  - Forms not available outside 9–5 or core hours, making them useless for people who work, care, or just function badly in the morning. citeturn2search0

- **Strong dislike of being forced online**
  - ANIMA users complaining they feel “pushed” onto it and that it makes life *more* difficult than just phoning. citeturn5view0
  - Westminster / NW London patients insisting on a **choice**: online, phone, and face-to-face; triage by a clinician; real engagement before big changes. citeturn3view0

- **Digital exclusion & accessibility**
  - Older and disabled patients consistently say they struggle with online systems (screen readers, small text, complex forms). citeturn5view0turn2search1turn3view0
  - Reports warn explicitly that current setups risk **entrenching health inequalities** if not fixed. citeturn2search1turn0search5

- **What patients actually ask for** (almost word-for-word across reports):
  - 24/7 ability to submit forms, with responses in core hours. citeturn2search0
  - Shorter, clearer, more targeted online questions. citeturn2search0turn5view0
  - Keeping phone lines usable (callback, more lines, better telephony). citeturn6view1turn1view2
  - Clear explanation on websites of *all* access routes, including non-digital. citeturn1view1turn3view0
  - Assisted digital – staff completing forms for those who can’t, rather than “computer says no”. citeturn5view0turn2search1

This is more or less a ready-made evidence pack that other patients in England are *already* using to argue against “website shut when we’re shut” and “website only” access models.

---

navlistRecent coverage on online GP access changesturn0news40,turn0news42


#### You:
Gimme a summary report of who's dealing with this, bucketed by their action/approach, like let's pivot so I can see a list representing who's facing the problem of being blocked by online websites that are crap or being taken down out of office hours because the nhs standard for access is a low floor, too low to improve access quality, often making it worse than the previous unregulated level. I want to demonstrate how the new rules are a step back because PATCHS doesn't enable 24hr access by default

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
### 1. Buckets: who’s actually dealing with crap / closed GP websites?

#### A. Local patient watchdogs (Healthwatch)

These are the clearest voices saying “the website is blocking me”.

**1. Healthwatch Hertfordshire (Herts & West Essex ICB)** citeturn0search4turn0search8turn0search14

- **Problem they see**
  - Online forms **switch off when capacity is reached** or only work in short windows.
  - People can’t submit outside 9–5, so “online access” is meaningless if you work or care.
  - Over half of 500 respondents would *not* recommend online GP services as first contact, many prefer phone/visit because of system problems.
- **What they’re doing**
  - Commissioned study by the ICB into online GP services.
  - Recommendations include **24/7 form submission**, shorter forms, and strong non-digital alternatives.

**2. Healthwatch Kent (ANIMA “digital front door”)** citeturn0search1turn0search5

- **Problem**
  - ANIMA becomes the main route; online now > phone.
  - A third of patients rate ANIMA as poor; forms complex, confusing; older/digitally excluded patients feel pushed out.
- **What they’re doing**
  - Detailed evaluation of ANIMA with 209 people.
  - Explicit asks for **simpler journeys** and preserving **phone/assisted-digital** routes so the front door isn’t effectively “no entry” for some groups.

**3. Healthwatch Tower Hamlets** citeturn0search12turn0search2turn0search9turn0search18

- **Problem**
  - Being **told to use e-consult** or similar when many can’t or don’t want to.
  - E-consult and other tools **only work at specific times** or close when slots run out.
  - 60–65% of online-consultation feedback is **negative** in multiple periods.
- **What they’re doing**
  - Continuous CIS trend reports on GP access “booking / online / phone”.
  - Using those data in local system work on urgent same-day access and A\&E deflection.

**What this bucket shows**

Patients, via Healthwatch, are **repeatedly** describing:

- Forms that **close early** (when demand is high).
- Forms that are **unavailable out of hours**.
- Websites that strongly push digital but are badly designed / inaccessible.

And they’re explicitly asking for **24/7 submission with next-day triage**, which the new national standard does *not* require.

---

#### B. Local NHS system bodies (ICBs, PCNs, “digital front door” programmes)

These are the commissioners trying to make the new standard work, and discovering the edge-cases.

**1. Herts & West Essex ICB** citeturn0search8turn0search4

- **Action**
  - Commissioned Healthwatch Hertfordshire to investigate online services and how to improve them.
- **Relevance**
  - Acknowledges that the push to digital has created **new barriers**; not just smoothed access.
  - ICB-level recognition that current “minimum” digital offer is not enough for quality / equity.

**2. West Kent Health and Care Partnership (ANIMA roll-out)** citeturn0search5turn0search1

- **Action**
  - PCN / partnership programme to shift contacts to ANIMA as the default front door.
- **Relevance**
  - Their own evaluation shows:
    - Online > phone after roll-out.
    - Shorter waits for some, but **new usability/exclusion problems** for others.
  - This is almost a live A/B test of “digital first + limited config options” vs reality.

---

#### C. Individual practices reacting to the October 2025 rules

These are useful because they’re forced to spell out how they interpret the new standard.

**1. Oakwood Lane Medical Practice (Leeds)** citeturn0search13turn0search22

- **What they say**
  - From 1 Oct 2025 they must allow **unlimited online access** for non-urgent requests **throughout core hours**.
  - They warn this may force **hospital-style waiting lists** because demand could exceed what they can safely handle.
- **Why it matters**
  - Shows a practice grappling with the new contract: tool **on 8–6:30**, but no commitment to 24/7.
  - The problem they fear is *too much* online access in-hours, not too little out-of-hours – so there’s a strong incentive **not** to extend beyond the minimum.

**2. Chase Meadow Health Centre (Warwickshire)** citeturn0search19turn0search22

- **What they say**
  - Explicit “Important changes from 1 October 2025”: they’re **changing how access works** to comply with the GP contract.
  - They describe online request handling in core hours; messaging implies **website/online system is time-boxed**, not 24/7.
- **Why it matters**
  - Again, the practice is fully compliant if their PATCHS / other tool is **available 8–6:30 only** and switched off outside those times.

**What this bucket shows**

- Practices are implementing the **core-hours requirement** and are worried about capacity *inside* those hours.
- There is **zero incentive** in the contract to leave PATCHS / ANIMA / e-consult open 24/7.
- Out-of-hours “service unavailable, come back later” is **completely compliant** with the new rules.

---

#### D. National standard-setters & safety bodies

These define the “low floor” that everything else hangs off.

**1. NHS England – GP contract & OC guidance** citeturn0search10turn0search3turn0search22turn0search16

- **Key rule (from 1 Oct 2025)**
  - Online consultation tools must be **switched on for the duration of core hours** (typically 8:00–18:30, Mon–Fri) for:
    - non-urgent appointment requests
    - medication queries
    - admin requests.
- **What it *doesn’t* say**
  - No requirement for **24/7 availability**.
  - No requirement to accept **urgent** clinical queries online.
- **Public framing**
  - Gov/NHSE press pushes “phone lines unclogged, online available 8–6:30 everywhere”. 24-hour access is not mentioned at all.

**2. BMA / LMCs (negotiating & interpreting the contract)** citeturn0search7turn0search22turn0news36

- Support the core-hours OC requirement as a **minimum**, but:
  - Warn that unlimited online access during core hours can **overwhelm** practices.
  - Have threatened industrial action over the policy, mainly on safety/workload grounds.
- Their advice to practices focuses on **staying safe within that 8–6:30 window**, not on extending beyond it.

**3. HSSIB & Healthwatch England – safety & exclusion** citeturn0news34turn0search17turn0search20

- HSSIB found online GP consultations have already led to **harm and deaths** in some cases, and emphasised keeping **telephone and face-to-face** routes.
- Healthwatch England and local Healthwatch repeatedly flag:
  - digital exclusion
  - inaccessible forms
  - confusing journeys.
- Collectively, they support **multi-channel access**, but the national standard still only sets a minimum of “core hours online”.

---

### 2. How this supports “the new rules are a step back”

You want to show: **PATCHS (and similar) not being 24/7 by default + new rules = worse access in practice than before.**

You can land that in three moves:

1. **The new floor is explicitly “core hours only”**

   - Contract and guidance: from 1 Oct 2025, practices must keep their online consultation tool open **during core hours, 8–6:30**. citeturn0search10turn0search3turn0search22turn0search16
   - There is **no obligation** to offer 24/7 form submission.
   - If a PATCHS instance is configured to only accept requests inside those hours (and to show a “closed” message outside them) it is **fully compliant**.

2. **Real-world evidence shows practices using config to *restrict* access**

   - Healthwatch Hertfordshire, Kent, Tower Hamlets and others all describe:
     - Forms that **shut as soon as capacity is reached** (sometimes by mid-morning). citeturn0search4turn0search12turn0search18
     - Forms that are **only available in limited hours** (e.g. 9–5 weekdays) and unavailable in evenings/weekends.
   - Individual practices like Oakwood Lane explicitly fear that “unlimited online access” across core hours will force them into **waiting lists**, not better access. citeturn0search13
   - So, if anything, local incentives are to **hug the minimum** or to add extra friction, not to make PATCHS 24/7.

3. **Previously, the “unregulated” enviroment at least allowed 24/7 experiments; now the low floor locks in something worse**

   - Before October 2025, some practices:
     - ran e-consult / PATCHS **24/7 with next-day triage**,
     - others had short windows,
     - others didn’t use online at all. It was messy, but **24/7 was allowed** where clinics and patients wanted it.
   - Now:
     - Everyone must provide **core-hours** online access – a win vs the worst laggards.
     - But there is still **no driver** for 24/7, and clear capacity/safety reasons *not* to go beyond 8–6:30.
     - Patients and Healthwatch are explicitly asking for **24/7 submission**, but the national standard enshrines something lower, and vendors/practices configure tools to match that floor. citeturn0search4turn0search5turn0search12turn0search18

Net effect you can argue:

> - **Old world**: chaotic, but some people had genuinely 24/7 digital front doors.
> - **New world**: everyone gets a digital front door, but it’s legally fine for it to say “come back tomorrow at 8am” outside core hours, and in practice that’s exactly how PATCHS/ANIMA/e-consult are often configured.

That’s the “step back” story, and the buckets above give you named actors and evidence for each side of it.

---

navlistRecent national coverage on GP online access rulesturn0news32,turn0news33,turn0news36,turn0news34


#### You:
That's just a repeat of what you said before. I'm literally looking for a list of who, grouped by what they're doing, not every item fully detailed

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
Gotcha. Here’s just **who**, grouped by **what they’re doing**.

---

### 1️⃣ Collecting evidence that online access is blocking people

**Action:** Surveys, reports, case studies documenting crap / closed GP websites & online forms.

- Healthwatch Hertfordshire
- Healthwatch Kent
- Healthwatch Tower Hamlets
- Healthwatch Ealing
- Healthwatch Wandsworth
- Healthwatch Westminster / NW London
- Healthwatch England (collating national themes across local HWs)

---

### 2️⃣ Running / tweaking “digital front door” systems

**Action:** Implementing ANIMA / PATCHS / eConsult etc and then discovering how they break access.

- Tunbridge Wells PCN / West Kent “ANIMA digital front door” project
- Herts & West Essex ICB (commissioned review of online GP services)
- Other ICS/ICB digital / access programmes using online triage at scale (e.g. NW London ICS, Kent & Medway, etc.)

---

### 3️⃣ Scrutinising GP access (including digital-only drift)

**Action:** Formal democratic scrutiny of “can people actually get in?”, using Healthwatch evidence and ICS data.

- Stockton-on-Tees Adult Social Care & Health Select Committee
- Barnet Adults & Health Overview & Scrutiny (GP Access Task & Finish Group)
- Leicestershire Health Overview & Scrutiny Committee
- Kent County Council HOSC
- Devon Health & Adult Care Scrutiny
- Inner North East London JHOSC (cross-borough)
- Bury Health Scrutiny Committee

---

### 4️⃣ Practices implementing the **minimum** standard & bumping into its limits

**Action:** Rewriting access pages to comply with Oct 2025 rules; core-hours-only online by design.

- Oakwood Lane Medical Practice (Leeds) – explicit “unlimited online 8–6:30” language, worried about waiting lists
- Chase Meadow Health Centre (Warwickshire) – “important changes from 1 Oct 2025” framing, time-boxed online requests
- Other PATCHS / eConsult / ANIMA practices updating websites to:
  - stress **online request in core hours**,
  - keep tools switched off out of hours, while still being contract-compliant

---

### 5️⃣ Policy / safety bodies defining the **low floor** (and sometimes warning about it)

**Action:** Setting or interpreting the rules that allow PATCHS etc to be off outside core hours.

- NHS England – GP contract & online consultation guidance (core-hours requirement, no 24/7 obligation)
- BMA & LMCs – negotiating the contract; advising practices to stay within safe workload (implicitly discouraging 24/7 OC)
- HSSIB – investigations into safety risks from online consultations; pushing for multi-channel not digital-only
- Healthwatch England – national voice amplifying local findings on digital exclusion & blocked access

---

### 6️⃣ People directly hitting the wall

**Action:** Complaining, feeding stories into the structures above.

- Individual patients & carers:
  - via Healthwatch surveys
  - practice complaints
  - council/MP casework, and local media
- Community orgs (carers groups, disability orgs, migrant support orgs) feeding evidence into Healthwatch / scrutiny

---

If you want next step, I can turn this into a really tight 1-pager argument: *“Here are the buckets of actors, here’s how their own evidence shows the new core-hours-only rule + PATCHS config is a step back from potential 24/7 access.”*


#### You:
Who are the actual people of healthwatch? It's this just one group of people complaining about many places, or are these independent groups discovering the same issues?

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
They’re independent groups, not one central gang doing all the moaning.

- There’s **Healthwatch England**, the national body (a statutory committee of the CQC). citeturn0search5turn0search19
- Then there are **\~150+ separate local Healthwatch organisations**, one for (essentially) every local authority area. Current counts are usually in the 150–153 range. citeturn0search11turn0search15turn0search17

Each local Healthwatch:

- Is **commissioned by its local council**, via a contract or grant. citeturn0search3turn0search14
- Has its **own staff team, board/trustees and volunteers**, and is structurally separate from the NHS and the council it critiques. citeturn0search7turn0search11turn0search19
- Collects feedback only in **its own patch** (e.g. Healthwatch Kent, Healthwatch Tower Hamlets), often with their *own* surveys, listening events, etc.

They share a brand and some support from Healthwatch England, but they’re **distinct legal orgs** discovering similar issues in parallel, then feeding them up to the national level. citeturn0search11turn0search16

So when you see reports from Hertfordshire, Kent, Tower Hamlets, Wandsworth etc, that’s **multiple independent teams** in different places all describing the same online-access pain, not one central team projecting its view everywhere.


#### You:
Who in Manchester? Gimme the lowdown locally, where to escalate this and expect people to listen?

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
Here’s the Manchester-specific map.

---

## 1. People already on your side (local patient voice)

**Healthwatch Manchester** – *your main ally*

- What they’re doing already
  - 2024 “**The Service, Online**” – reviewed **all 83 GP practice websites in Manchester** for extended/enhanced access info and usability. citeturn1view0turn1view2
  - 2024 “**The Service**” – mystery shopper calls to **all 83 practices** about Enhanced Access; found weak, inconsistent info from reception. citeturn1view1
  - 2021 work on **“How easy is it to access GP services online?”** with Manchester People First (learning disability group). citeturn5view2

- Why they’ll listen
  - Their whole recent portfolio is *exactly* about crap GP websites and access models.
  - Commissioned by **NHS Greater Manchester** to do this work, so their reports go straight into system governance. citeturn1view2

- How to get to them
  - Site: Healthwatch Manchester (“Have your say” / “Contact us”) – they explicitly invite Manchester-postcode residents to feed cases. citeturn5view0

**Healthwatch in Greater Manchester (GM-wide)**

- Umbrella for all 10 GM Healthwatch, publishing joint insight + impact reports that NHS GM actually reads. citeturn5view1

---

## 2. Local NHS decision-makers for GP access & digital

All of these are **NHS Greater Manchester Integrated Care Board (ICB)** – *Manchester Locality*.

From the “Access to General Practice” report to Health Scrutiny: citeturn3view0

- **Deputy Medical Director, NHS GM (Manchester Locality)**
  - *Dr Paul Wright* – listed report author & contact for GP access.

- **Associate / Head of Primary Care, NHS GM (Manchester Locality)**
  - *Caroline Bradley* – named as Associate Director Primary Care (2023) and previously Head of Primary Care (2021). citeturn3view0turn3view1

- **Deputy Head of Primary Care, NHS GM (Manchester Locality)**
  - *Gordon Reid* – also listed contact on the 2023 access report. citeturn3view0

These are the people who sign the formal “Access to General Practice in Manchester” papers and own primary-care digital/access programmes locally. They’re the NHS side of the table opposite Healthwatch and the Council. citeturn3view0turn3view1

---

## 3. Political oversight in the city (where system people have to answer in public)

**Manchester City Council – Health Scrutiny Committee**

- What it covers
  - Scrutinises **how the Council and NHS partners deliver health services**, including GP access and digital transformation. citeturn2view0
  - Has already taken multiple **access to GP** reports (2021 GP Access, 2023 “Access to General Practice”, plus Enhanced Access / Extended Hours work). citeturn3view1turn3view0

- Who’s in the room
  - Chaired by **Cllr Curley**, with a panel of councillors; NHS GM primary-care leads (above) attend as officers. citeturn2view0turn3view0

- How you actually get heard
  - Public can submit evidence and ask to speak; agenda pack gives a named Committee Officer (currently **Lee Walker**) with phone and email for requests. citeturn2view0

**Greater Manchester Joint Health Scrutiny Committee (GMCA)**

- GM-wide committee looking at cross-borough health issues, including **remote / virtual GP models**. citeturn0search28turn0search19
- If you want to make it a **GM-system** question (PATCHS config, ICB-wide policy, etc.), this is the political forum above the city.

---

## 4. Wider GM patient voice & evidence

If you want to show “this isn’t just Manchester city centre, it’s a GM pattern”:

- **Healthwatch Tameside – GP Experience Report (Apr 2025)** – 220 responses; highlights issues with **booking, online tool accessibility, continuity**. citeturn0search21
- Other GM Healthwatch (Salford, Bury, Trafford, etc.) are co-reporting on digital access via the **Healthwatch in Greater Manchester** insight reports. citeturn5view1

These give you extra local(ish) ammo when you’re arguing that PATCHS / OC configs + the new core-hours standard are systemically broken, not just “my practice is bad”.

---

### TL;DR: if you want people in Manchester who will actually listen

- **First stop:** Healthwatch Manchester (they’re already doing GP website and online access reviews). citeturn1view0turn5view0
- **System side:** NHS GM – Manchester Locality primary-care leads (Paul Wright, Caroline Bradley, Gordon Reid). citeturn3view0turn3view1
- **Political pressure:** Manchester City Council Health Scrutiny Committee (Chair + members, via the Committee Officer contact in the agenda packs). citeturn2view0turn3view0
- **GM-wide escalation:** Healthwatch in Greater Manchester + GM Joint Health Scrutiny for a “Greater Manchester online access standard” argument. citeturn5view1turn0search28turn0search19
