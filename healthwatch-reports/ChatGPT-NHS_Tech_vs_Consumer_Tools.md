# NHS Tech vs Consumer Tools

#### You:

I want to think about this as a problem of competing expectations, and the failure of companies that function within the NHS being completely detached from 'the modern world' of conveniences and consumer-tools. I want you to investigate how the basic offering of the NHS in terms of tools and access (not medical/clinical care, just access and connectivity) is so far behind (and document the ways) the private sector, and not just because of a lack of funds (there are plenty of free consumer available tools that could be used), an overweight baggage of regulations (the actual mandated/legally-required systems are pretty inaccessible and hard to use, but the NHS App and the tech stack is still how much out of date? and what are the other strengths and shortcomings of NHS tech? primarily interested in patient-facing, but the complexity of systems avaialble inside the staff tools affects how they can respond to patients) but also how the expectations of staff are connected to what IS available and accessible internally (and how stiff those systems are) vs patients, who can ubereats a meal for 20 to their front door in half an hour or less, and how they can manage every imaginable detail of their life in some website or other, but because the NHS functions as defacto monopoly for MOST patients (not all, and the wealthy are fine with going private anyway) and apps like betterhealth/zocdoc that are more available than ever. Basically I want to think about how to communicate to staff, in a constructive way, how and why they're so fucking crap at the patient interface, and not because it's their fault, but how the shape of the system creates a gulf between patients and staff.

I think there's a related point here too about how NHS regulations are often intentionally effortful, wasteful or encouraging of 'going private' by keeping the public owned demands at a very low floor, reduces spending, squeezes poorer and poorer patients out of public healthcare, and perhaps some expoloration of how my practice's management company can stand out compared to other management companies, despite having little to no money. Essentially, for many years, _some_ (mostly Tory, but not exclusive) MPs and other political-leaders got richer by keeping NHS service quality just low enough, and practice/management demands just onerous enough, that it was hard to provide 'great' service, because all the energy/effort was sucked up just making things almost kinda work.

This research/scoping/spotlighting side-project will also need investigation into specifics of what tech is available to practices inside the NHS, more of what's available free or near free outside (like offered by universities, hospitals or open source tools, especially those already integrated with nhs practices) and what rules, and how the rules from other influences (PCN say) affect what and how those are available. 

The best approach here is probably to intro/pitch the issue and scope clearly and in plain english for the casual reader, then break it down into areas of interest, asking questions and/or defining problems in that space. Then with some quick research, a basic evidence sheet of what can be found immediately as places to start understanding what the current thinking is on these issues in brief.



#### ChatGPT:
People don’t experience “the NHS”. They experience a front door: can I get in, can I explain what I need, can I see what’s happening, can I fix something without a phone lottery, can I trust that the system heard me.

That’s where the expectation gap lands. Patients live in a world of instant status, receipts, confirmations, rebooking, push notifications, and a single place to track things. In primary care, the patient-facing surface is often a patchwork: a national app whose features depend on what your local surgery has enabled, plus whichever online-consult supplier your practice (or ICB) happens to be on, plus phone lines and workflows that were never redesigned to match the new demand shape. Even “modernisation” can amplify the mismatch: England’s GP contract now requires online consultation tools to stay open through core hours (8am–6:30pm) from 1 Oct 2025. citeturn0search1turn0search9turn0search5turn2search7

So you get a predictable social dynamic: patients judge the interface against the rest of their lives; staff judge it against the internal tools they’re forced to use, the safety constraints they’re responsible for, and the volume they’re drowning in. Everyone is right, and everyone is furious.

### Where the gap shows up (nationally, not “your practice”)

The NHS has built real patient-facing capability, but it’s uneven, conditional, and frequently “thin” compared to consumer services.

**1) “One NHS” in marketing, local variability in reality**\
The NHS App is big and growing (over 40 million all-time registrations by end of Dec 2025; tens of millions of logins and record views monthly). citeturn1search12turn1search0\
But what a patient can actually *do* in the app depends on what their GP surgery and local services have switched on. citeturn3search15turn4search10\
Even core stuff like appointment booking is configurable at practice level. citeturn0search0turn0search4\
Messaging exists too, but again: “you may be able to…”, and rollout/integration varies. citeturn6search0turn6search1

This is the first expectation collision: patients see a national app; staff know the local toggles, the supplier limitations, and the “why can’t I see X?” tickets landing at reception.

**2) “Digital access” often means “form-first triage”, not service design**\
Nationally, policy has pushed hard on online contact. Nearly all practices in England offer some form of online access; there was a big jump in online requests after the Oct 2025 requirement landed. citeturn3search13turn0search1\
But “online access” is not the same as “good interface”. Many implementations are essentially: submit a form → wait → somebody triages in a separate system → somebody calls back (maybe) → you find out what happened by chasing.

HSSIB has been blunt that online consultation tools can introduce safety risks, and that safe implementation depends on conditions (capacity, capability, reporting, safeguards) that often aren’t there. citeturn0search2turn3search17turn3news40\
BMA guidance around the Oct 2025 change reflects the same tension: more open access without safeguards just turns the tap fully on. citeturn0search5turn4search6

So patients expect Uber-style throughput; staff get an always-open funnel into a workflow that still has bottlenecks, risk checks, and limited clinical time.

**3) The internal toolchain is one reason the interface feels “stupid”**\
A lot of what patients perceive as incompetence is really “tool fragmentation meets safety constraint”.

General practice sits on a small number of principal clinical system suppliers (notably EMIS Web and TPP SystmOne), and integration with these systems is still supplier-specific. IM1 standards explicitly require “pairing” per supplier interface. citeturn2search1turn2search5\
That’s a hidden tax on every “why don’t we just…” idea: you’re not building against one platform, you’re building against an estate with vendor boundaries, assurance processes, and local procurement choices.

On top of that, national frameworks that were meant to simplify buying and standardising primary care tooling have churned. GP IT Futures expired 31 March 2023. citeturn2search2turn2search6\
The “digital first online consultation and video consultation framework” expired 31 March 2024. citeturn3search9\
NHS England has been moving towards successor “digital primary care” procurement arrangements, but that’s another transition layer. citeturn5search1turn2search18turn5search5

What staff feel day-to-day: a brittle workflow stitched across systems; the patient sees only the final delay.

**4) It’s not *only* money; it’s assurance + accountability**\
You *can’t* solve patient access with random free consumer tools unless you’re willing to breach clinical safety, IG, accessibility, audit, retention, and integration requirements. NHS England’s DTAC pulls together the baseline expectations buyers are supposed to enforce (clinical safety, data protection, technical security, interoperability, usability/accessibility). citeturn1search1turn1search5turn1search9\
Clinical risk management standards (DCB0129/0160) are mandatory for health IT risk management across manufacture/deployment. citeturn1search10turn1search22turn1search2

This is where “the system makes you look useless” bites hardest: consumer UX is optimised for speed; NHS UX is constrained by “if this goes wrong, somebody gets harmed and someone is accountable”.

**5) The NHS App is not “ancient” — the deeper stack is where time goes**\
If you look at the NHS App’s public design system, it’s actively maintained (recent component library updates, a dedicated frontend library built on NHS.UK frontend, open repos). citeturn4search5turn4search16turn4search1\
So “out of date” isn’t mainly about UI components. It’s about what sits behind the UI: local enablement, supplier integration, and the long tail of legacy/contractual arrangements. The NAO’s view is basically: transformation is harder here because of legacy IT, complex governance, and existing commercial arrangements with technology suppliers. citeturn5search3turn0search3

### Competing expectations: what patients think they’re buying vs what staff think they’re delivering

Patients unconsciously model healthcare access as a consumer service:

- one front door
- always-on intake
- instant confirmations
- visible queue position
- easy rescheduling
- clear escalation paths
- consistent experience across geography

Staff model it as risk-managed demand triage inside a constrained system:

- multiple intake channels that aren’t equivalent
- clinical safety gates
- duty-of-care anxiety (“what if the chest pain ended up in the wrong bucket”)
- brittle systems and duplicated admin
- hard caps on human time

When the same digital change hits both sides (eg “online tool open all day”), patients interpret it as “finally, modern access”. Staff experience it as “the queue just became infinite”.

### Political economy (without turning it into a conspiracy pamphlet)

It’s reasonable to *investigate* whether policy and procurement choices have kept service quality at a low, effortful floor that nudges those who can pay towards private routes. You don’t need to overclaim; you can frame it as incentives and outcomes:

- the NHS is a de facto monopoly for most people’s core care access, so “switching away” isn’t a normal market discipline
- supplier lock-in and long contracts can outlive governments
- “digital transformation” headlines can land without fixing the underlying workflow capacity

There are also concrete, reportable links between politics, suppliers, and money that are worth including as “things to look at”, not as a single-cause explanation. Example: reporting on major NHS IT suppliers with significant political donations and large public contract income (TPP/SystmOne has been a recent flashpoint). citeturn5search0turn5news40\
And broader debates about public-sector tech procurement and lock-in (eg Microsoft/NHS criticism in Parliament). citeturn5news41

### What to say to staff that lands (and doesn’t scapegoat them)

You’re trying to get staff to feel seen *and* to accept that the patient interface is a system responsibility. The tone that works is: “you’re not failing; you’re working inside a design that makes you look like you’re failing.”

A few lines that don’t trigger defensiveness:

- Patients don’t compare you to another GP practice. They compare you to every other service they used this week.
- The NHS has expanded digital intake faster than it has rebuilt the internal workflow that should handle that intake safely. citeturn0search1turn0search2
- The app and website are national; the configuration and delivery are local, and the patient can’t see that. citeturn3search15turn0search0
- When a patient chases, they’re not being difficult — they’re doing what every other system trained them to do: “track the ticket”.
- If we can’t give them speed, we can at least give them certainty (confirmation, status, next action).

Then pivot into practical empathy: “we can’t fix national procurement, but we *can* stop creating avoidable ambiguity.”

### Low-money ways a practice/management company can stand out (mostly workflow and clarity, not new software)

Even with minimal spend, you can reduce the perception of chaos by changing what the patient sees and what staff don’t have to explain 50 times a day.

- Make one “front door” promise and keep it: the same rules across phone / walk-in / online. The Oct 2025 contract language pushes towards “equitable experience across access modes”; patients will punish you when channels contradict each other. citeturn2search15
- Replace vague waiting with explicit state: “received”, “triaged”, “needs more info”, “booked”, “sent to clinician”, “responded”. If you can’t implement a live queue, you can still implement message templates and time-window commitments.
- Use NHS-native messaging where possible, because it reduces the scatter across SMS/email and ties into patient expectations of “one inbox”. NHS App messaging is now a formal service line, and NHS England is also pushing a broader digital-first communications approach (NHS Notify sits in that ecosystem). citeturn6search1turn6search6turn6search11
- Cut down “choice overload” in appointment booking. If you expose online booking, expose only the slot types you actually want booked directly; the NHS App appointment booking capability is explicitly configurable by slot type/clinician/rota. citeturn0search0
- Write for the person who is stressed, tired, and on a broken phone. The NHS App design system and service manuals are free, and they’ll keep you out of the worst accessibility holes. citeturn4search5turn3search7
- Standardise internal handling so staff aren’t improvising policy at the front desk. HSSIB’s point, over and over, is that safety and equity depend on the conditions of implementation, not on the existence of the tool. citeturn0search2turn3search17

### A scoped research map (questions worth answering, in roughly the order you’ll want them)

**The interface gap (patient-facing reality)**

- What can patients *reliably* do across England today via the NHS App, and what varies by practice/service enablement? citeturn3search15turn1search12turn6search0
- Where does the patient journey fall off a cliff (identity checks, linking to practice, referrals, test results, messaging)? citeturn3search14turn6news41
- How often are “digital” journeys actually just a pre-form for a phone call?

**Internal workflow (why staff can’t respond the way patients expect)**

- How many systems does a request touch (OC tool → task list → clinical record → messaging → booking)? Where are the handoffs?
- Which parts are supplier-constrained (EMIS vs TPP) and which parts are process-choice? citeturn2search1turn2search5
- What are the biggest failure modes (lost requests, duplicated work, unclear ownership)? HSSIB is a starting point. citeturn0search2turn3news40

**Rules and constraints (what’s genuinely mandated vs “we do it because we’ve always done it”)**

- Which standards actually block “free consumer tools” (DTAC, DCB0129/0160, IG guidance)? citeturn1search1turn1search10turn1search22turn1search5
- Which constraints are policy choices, not law (eg how “core hours” access is interpreted, what counts as equitable access)? citeturn0search1turn3search5

**Procurement and market shape**

- How has framework churn (GP IT Futures expiry, digital-first framework expiry) affected local tool choice and continuity? citeturn2search2turn3search9turn5search1
- Where does vendor lock-in slow improvement (integration pairing, contract length, switching costs)? citeturn2search1turn5search3

**The “nudging private” hypothesis**

- What patterns show up in spending, contract awards, supplier profits, and political links? (Treat as an evidence question, not a foregone conclusion.) citeturn5search0turn5news41
- Which patient groups are most likely to exit to private digital GP services, and what exact interface features are they paying for (availability hours, instant booking, continuity, response times)? Which? is a decent baseline map. citeturn1search11turn1search3

### Quick evidence sheet (starting points you can cite immediately)

- NHS App scale and usage (Dec 2025 official stats). citeturn1search12turn1search0
- NHS App capabilities vary by local enablement; patient guidance explicitly says local variation exists. citeturn3search15turn4search10
- Appointment booking exists but is practice-configurable. citeturn0search0turn0search4
- Messaging exists in the NHS App; NHS England positions it as part of a “digital first” communications strategy. citeturn6search0turn6search1
- From 1 Oct 2025, practices in England must keep online consultation tools open through core hours for non-urgent requests/admin/medication queries (with safeguards language). citeturn0search1turn3search5turn4search2
- HSSIB findings: online consultation tools carry patient safety risks; implementation conditions matter; incident reporting and national support are gaps. citeturn0search2turn0search6turn3news40
- Interoperability tax: IM1 pairing is supplier-specific (EMIS Web, TPP SystmOne) and requires separate pairing per supplier API. citeturn2search1turn2search5
- Framework churn: GP IT Futures expired 31 Mar 2023; digital-first OC/video framework expired 31 Mar 2024; replacement “digital primary care” procurement is being shaped. citeturn2search2turn3search9turn5search1
- Assurance constraints: DTAC baseline; DCB0129/0160 clinical risk management standards. citeturn1search1turn1search10turn1search22
- Private-sector comparator: private digital GP services are widely marketed with fast access and broad hours; pricing/availability snapshots exist (Which? etc). citeturn1search11turn1search7
- National direction of travel: “online hospital” concept tied to NHS App from 2027 shows policy intent to push more care through digital front doors. citeturn1news42turn6search4
- Supplier/politics angle worth investigating: recent reporting on major NHS IT supplier profits/dividends and political donations; procurement/lock-in debates. citeturn5search0turn5news41

If you want this to read well to casual readers, the clean through-line is: **the NHS has been digitising *intake* faster than it’s digitising and resourcing the *workflow behind intake***. That’s why patients experience “rude / stupid / pointless” at the interface, and why staff experience “another channel dumping work into the same bottlenecks”.

```text
Key source URLs (grouped)

NHS App capabilities + variability
- NHS App stats (Dec 2025): https://digital.nhs.uk/data-and-information/publications/statistical/nhs-app-statistics/december-2025
- “Who can use the NHS App” (England + Isle of Man): https://www.nhs.uk/nhs-app/setting-up/who-can-use-the-nhs-app/
- “Messaging in the NHS App”: https://www.nhs.uk/nhs-app/help/messaging-in-the-nhs-app/
- NHS App messaging service (NHSE): https://digital.nhs.uk/services/nhs-app/nhs-app-features/notifications-and-messaging-in-the-nhs-app
- NHS App appointment booking (practice enablement): https://digital.nhs.uk/services/nhs-app/nhs-app-features/appointments

Policy / contract pressure on “digital access”
- GP contract changes 2025/26 (online tool open core hours): https://www.england.nhs.uk/long-read/changes-to-the-gp-contract-in-2025-26/
- Online consultations FAQ (NHSE): https://www.england.nhs.uk/long-read/online-consultations-frequently-asked-questions/
- Commons Library explainer (Jan 2026): https://commonslibrary.parliament.uk/gp-online-consultations-and-appointments/

Safety / evidence on harms + conditions
- HSSIB investigation (online consultation tools): https://www.hssib.org.uk/patient-safety-investigations/workforce-and-patient-safety/second-investigation-report/

Why integration/procurement slows everything down
- IM1 standards (supplier-specific pairing): https://digital.nhs.uk/developer/api-catalogue/interface-mechanism-1-standards
- GP IT Futures expired notice: https://digital.nhs.uk/services/gp-it-futures-systems
- Digital-first OC/video framework expired notice: https://digital.nhs.uk/services/digital-services-for-integrated-care/digital-first-online-consultation-and-video-consultation-framework

Assurance constraints (why “free tools” aren’t plug-and-play)
- DTAC: https://transform.england.nhs.uk/key-tools-and-info/digital-technology-assessment-criteria-dtac/
- Clinical risk management standards: https://digital.nhs.uk/services/clinical-safety/clinical-risk-management-standards

Private sector comparator snapshot
- Which? private GP comparison (Jan 2026): https://www.which.co.uk/reviews/private-healthcare/article/private-gps-compared-aHUVt2O3vZcW
```

navlistRecent reporting worth skimming alongside the official docsturn1news41,turn1news42,turn3news40,turn3news43,turn5news41,turn5news40


#### You:
get me a full evidence sheet of anyone else around Britain who has investigated this thoroughly. I wan tto know what everyone has to say about this. 


#### ChatGPT:

Watchdogs and regulators

* National Audit Office (NAO) — *Digital transformation in the NHS* (2020). Old kit, patchy basics (networks, devices), fragmented governance, interoperability blocked by legacy systems and supplier sprawl; “digital like banking/airlines” is explicitly used as the comparison point. ([National Audit Office (NAO)][1])
* Public Accounts Committee (PAC) — *Digital transformation in the NHS* (2020). Parliamentary follow-up to NAO: progress too slow, too many priorities, poor grip on legacy and data sharing; repeated emphasis on vendor/legacy lock-in risk. ([UK Parliament][2])
* Health and Social Care Committee (Commons) — *Digital transformation in the NHS* (Jun 2023) + Govt response (Sep 2023). Frames “digital front door” (NHS App) as central, but calls out four hard blockers: innovation adoption, interoperability, workforce/digital skills, and digital exclusion. ([UK Parliament][3])
* Health Services Safety Investigations Body (HSSIB) — investigation into online consultation tools in general practice (2024/2025 pages). Not “tech is good/bad”; it’s “sociotechnical”: workflow design, queue management, safety-netting, and failure modes when asynchronous tools become the gate. ([HSSIB][4])
* Care Quality Commission (CQC) — *State of Care* primary/community access sections (2023/24 and 2024/25). Tracks access pressure and notes that information sharing/digital maturity remains uneven; primary care access and capacity constraints show up as experience problems even when “channels” exist. ([Care Quality Commission][5])
* House of Commons Library — *GP online consultations and appointments* (Jan 2026). Plain-English summary of the 2025/26 contractual rule change: online consultation tools must be open through core hours, plus the practical implications that become part of the “expectations gap”. ([House of Commons Library][6])
* UK “state of digital government” review (Jan 2025). Not NHS-specific, but it explicitly cites wide variance in legacy tech in NHS trusts (quoted range up to ~60–70% in some orgs), which is the upstream cause of patient-facing brittleness. ([GOV.UK][7])

Big independent research / think tanks that keep returning to “access as a system”, not “a receptionist being mean”

* Nuffield Trust — *Digital primary care: improving access for all?* (evidence review). Core message: digital front doors can widen access for some and simultaneously harden exclusion for others; distributional effects matter more than averages. ([Nuffield Trust][8])
* Nuffield Trust — work on remote/digital general practice risks: loss of clinical + non-clinical info, rapport/safeguarding issues, and mismatch between a system built for in-person and new routing models. ([Nuffield Trust][9])
* Nuffield Trust (QualityWatch) — GP Patient Survey trend analysis on access and experience (updated Dec 2025). Useful as the “what patients report over time” spine for any narrative you write. ([Nuffield Trust][10])
* Health Foundation — access as process design: triage/routing, admin burden, and patient navigation friction as distinct from raw appointment supply. ([health.org.uk][11])
* Health Foundation — “time saved by tech” programme: why internal tools (EPR usability, logins, interoperability, training) determine whether patient-facing promises are deliverable. ([health.org.uk][12])
* Health Foundation — the costed “analogue to digital” infrastructure argument (£21bn/5 years across UK; includes EPRs, cyber, Wi-Fi, cloud, training/implementation). Even if you’re interested in cheap/free tools, this is the canonical “baseline plumbing” view. ([health.org.uk][13])
* Health Foundation — EPR strategy/interoperability commentary (2025): adoption isn’t the same as effective use; interface problems show up as workarounds and delays. ([health.org.uk][14])
* The King’s Fund — repeated framing that “access” is navigation and system design, not just volume; plus contract/policy explainers that shape what practices are forced to do. ([The King's Fund][15])
* NHS Confederation — leadership-facing synthesis of what “digital transformation” actually entails in NHS terms (useful for mapping stakeholders, constraints, dependencies). ([NHS Confederation][16])

Academic / NIHR work that’s directly about the staff–patient gulf created by tooling and routing

* NIHR (HSDR) — *Remote and digital services in UK general practice* (Greenhalgh et al.; published article record). This is the heavyweight programme looking at how “remote by default / total triage” changes risk, workload, continuity, and patient experience in real practices. ([journalslibrary.nihr.ac.uk][17])
* University of Oxford / NIHR — Remote by Default 2 (RBD2) study pages + award record. Useful because it treats the model as a sociotechnical system (queues, staffing, patient behaviour) rather than “an app”. ([phc.ox.ac.uk][18])
* NIHR ARC West — evaluation work on online consultation systems in GP practices (pragmatic, implementation-realist angle). ([ARC West][19])
* BJGP / BMJ ecosystem — “remote by default” critique and later analysis: relationship-based care, equity, safety-netting, and clinician stress. ([bjgp.org][20])
* BMJ Open / BMJ Open Quality — empirical studies of eConsult/total triage and user/clinician perspectives: gains in access can coincide with workflow load, demand shaping, and exclusion. ([bmjopenquality.bmj.com][21])
* Digital exclusion methods research (older adults, identification approaches). Useful if you want to move from hand-wavy “some people can’t” to operational segmentation. ([bmjopen.bmj.com][22])
* BMJ (Feb 2026) on the “dozens of logins” problem. This is the cleanest mainstream articulation of how internal friction becomes patient-facing delay and brusqueness. ([BMJ][23])

Patient voice organisations documenting the “modern life vs NHS interface” mismatch

* Healthwatch England — *Locked out* (2021). Digitally excluded patients’ experience of remote GP appointments: inability to navigate e-consult forms, reliance on family, and abandonment of care attempts. ([healthwatch.co.uk][24])
* Healthwatch England — *Closing referral black holes* (Dec 2025). Not GP access per se, but it’s the “connectivity” failure in its purest form: tracking, feedback loops, patients forced into unpaid admin chasing. ([healthwatch.co.uk][25])
* National Voices — *Unlocking the digital front door* (May 2021 plus supporting docs) and ongoing digital inclusion work. Strong on what “good” looks like when services move channel, and how VCSE props up the gaps. ([National Voices][26])
* Good Things Foundation — practical digital inclusion evidence and frameworks developed with NHS partners; also research on local authority + primary care partnership approaches. ([goodthingsfoundation.org][27])
* Patients Association / Digital Coalition commentary on NHS App usefulness vs limits and usability/access gaps. ([patients-association.org.uk][28])

Professional bodies (staff-side views of why “it feels crap” at the interface)

* BMA — *Getting IT Right* (Dec 2022): quantifies clinician time lost to inadequate IT; frames it as safety + capacity, not “nice to have”. ([BMA][29])
* BMA — earlier “vision for NHS IT” style work on infrastructure/devices/Wi-Fi/data sharing as day-to-day friction drivers. ([BMA][30])
* BMA + NHS England materials around the Oct 2025 online-consultation requirement: BMA FAQs emphasise safety/workload safeguards; NHS England FAQs set out implementation expectations; Commons Library summarises the rule for everyone else. ([BMA][31])
* RCGP — “future role of remote consultations & triage” (PDF) and policy pages on remote care; plus its Dec 2025 statement reacting to online consultation policy. ([rcgp.org.uk][32])
* RCGP toolkit for GP online services (appointments, records etc; explicitly not online consultations) — useful because it shows the “sanctioned minimum” of what practices are expected to provide and how it’s framed. ([rcgp.org.uk][33])

Devolved nations: parallel “digital front door” efforts (good for Britain-wide comparison, and for showing this isn’t a single England-only story)

* England — NHS App official stats + NHSE comms: usage and feature volumes by month; this is your hard baseline for what the “app layer” actually does at scale. ([NHS England Digital][34])
* Wales — Welsh Government statement on NHS Wales App launch (May 2025) and intended core features (repeat prescriptions, timeline, secure messaging, bilingual service). ([GOV.WALES][35])
* Scotland — Near Me video consulting final report (Dec 2023) for the “remote channel” story; and Scottish Government docs setting out the MVP rollout for the national app service (Lanarkshire first). ([learn.nes.nhs.scot][36])
* Northern Ireland — My Care patient portal (nidirect + DoH comms + DHCNI programme pages): narrower rollout by cohort/service area, but it’s a concrete “portal” implementation with identity/account dependencies. ([nidirect][37])

Stuff that’s “investigated” in the sense of policy + operating model, because it directly sets the expectation mismatch

* NHS England — “changes to the GP contract 2025/26” + “online consultations FAQs” + earlier “total triage” guidance from COVID era. This is where the system formally decides what the default patient interface is allowed to be. ([NHS England][38])
* NHS England — “delivery plan for recovering access to primary care” (the “8am rush” framing) and comms about online consultation volumes. ([NHS England][39])

If you want the sharpest “start here” stack (because it triangulates the whole problem)

* NAO + HSCC (interoperability/legacy/governance) ([National Audit Office (NAO)][1])
* HSSIB + NIHR/Oxford (online consult tools as sociotechnical risk/workflow) ([HSSIB][40])
* Healthwatch + National Voices + Good Things (what exclusion looks like in practice, and what inclusive design requires) ([healthwatch.co.uk][24])
* Health Foundation + BMA + BMJ (internal friction: EPR use, logins, time loss) ([health.org.uk][14])
* NHS App official stats (what the “front door” really does, not what people claim it does) ([NHS England Digital][34])

- [The Guardian](https://www.theguardian.com/politics/2025/jul/03/labour-nhs-app-hospital-league-tables-10-year-health-plan-wes-streeting?utm_source=chatgpt.com)
- [Financial Times](https://www.ft.com/content/81a9fcfe-dae9-4145-948f-4638670a598e?utm_source=chatgpt.com)
- [Financial Times](https://www.ft.com/content/086dee7e-efb1-4926-9da0-1f70210a5627?utm_source=chatgpt.com)
- [The Guardian](https://www.theguardian.com/society/2025/dec/07/referrals-black-hole-means-patients-in-england-miss-out-on-healthcare-finds-watchdog?utm_source=chatgpt.com)
- [The Guardian](https://www.theguardian.com/society/article/2024/jul/25/online-gp-consultations-have-led-to-harm-and-death-investigation-finds?utm_source=chatgpt.com)
- [The Guardian](https://www.theguardian.com/society/2025/sep/29/gps-doctors-england-online-appointment-booking-plan-strike-action-threat?utm_source=chatgpt.com)
- [thetimes.co.uk](https://www.thetimes.co.uk/article/nhs-app-scaled-back-dermatology-patients-7jxlz7wbt?utm_source=chatgpt.com)
- [thetimes.com](https://www.thetimes.com/uk/scotland/article/nhs-english-app-snp-six-years-t0dfwg3xp?utm_source=chatgpt.com)

[1]: https://www.nao.org.uk/wp-content/uploads/2019/05/Digital-transformation-in-the-NHS.pdf?utm_source=chatgpt.com "Digital transformation in the NHS"
[2]: https://publications.parliament.uk/pa/cm5801/cmselect/cmpubacc/680/68006.htm?utm_source=chatgpt.com "Digital transformation in the NHS"
[3]: https://publications.parliament.uk/pa/cm5803/cmselect/cmhealth/223/report.html?utm_source=chatgpt.com "Digital transformation in the NHS - Health and Social Care ..."
[4]: https://www.hssib.org.uk/news-events-blog/patient-and-staff-concerns-over-gp-online-consultation-tools/?utm_source=chatgpt.com "Patient and staff concerns over GP online consultation tools"
[5]: https://www.cqc.org.uk/publications/major-report/state-care/2023-2024/access/primary?utm_source=chatgpt.com "state of health care and adult social care in England 2023/24"
[6]: https://commonslibrary.parliament.uk/gp-online-consultations-and-appointments/?utm_source=chatgpt.com "GP online consultations and appointments"
[7]: https://www.gov.uk/government/publications/state-of-digital-government-review/state-of-digital-government-review?utm_source=chatgpt.com "State of digital government review"
[8]: https://www.nuffieldtrust.org.uk/sites/default/files/2022-02/digital-access-to-general-practice-evidence-review.pdf?utm_source=chatgpt.com "Digital primary care: Improving access for all?"
[9]: https://www.nuffieldtrust.org.uk/resource/getting-the-best-out-of-the-new-world-of-remote-and-digital-general-practice?utm_source=chatgpt.com "Getting the best out of the new world of remote and digital ..."
[10]: https://www.nuffieldtrust.org.uk/resource/access-to-gp-services?utm_source=chatgpt.com "Access to GP appointments and services"
[11]: https://www.health.org.uk/reports-and-analysis/briefings/rethinking-access-to-general-practice-it-s-not-all-about-supply?utm_source=chatgpt.com "Rethinking access to general practice: it's not all about supply"
[12]: https://www.health.org.uk/reports-and-analysis/analysis/tech-to-save-time-how-the-nhs-can-realise-the-benefits?utm_source=chatgpt.com "Tech to save time: how the NHS can realise the benefits"
[13]: https://www.health.org.uk/reports-and-analysis/analysis/digitising-the-nhs-and-adult-social-care-what-could-it-cost?utm_source=chatgpt.com "Digitising the NHS and adult social care"
[14]: https://www.health.org.uk/reports-and-analysis/analysis/electronic-patient-records-nhs-strategy?utm_source=chatgpt.com "why the NHS urgently needs a strategy to reap the benefits"
[15]: https://www.kingsfund.org.uk/insight-and-analysis/blogs/process-shapes-access-to-primary-care?utm_source=chatgpt.com "How Process Shapes Access To Primary Care"
[16]: https://www.nhsconfed.org/publications/digital-transformation-nhs-reference-guide?utm_source=chatgpt.com "Digital transformation in the NHS: a reference guide"
[17]: https://www.journalslibrary.nihr.ac.uk/hsdr/published-articles/QQTT4411?utm_source=chatgpt.com "Remote and digital services in UK general practice 2021 ..."
[18]: https://www.phc.ox.ac.uk/research/groups-and-centres/interdisciplinary-research-in-health-sciences/remote-by-default-2?utm_source=chatgpt.com "Remote by Default 2: the “new normal”?"
[19]: https://arc-w.nihr.ac.uk/research/projects/improving-access-primary-care-study/?utm_source=chatgpt.com "Evaluating an online consultation system in GP practices"
[20]: https://bjgp.org/content/71/705/149?utm_source=chatgpt.com "Remote by default general practice: must we, should ..."
[21]: https://bmjopenquality.bmj.com/content/14/3/e002741.full?utm_source=chatgpt.com "Use of an electronic consultation system in an inner city ..."
[22]: https://bmjopen.bmj.com/content/15/9/e102723?utm_source=chatgpt.com "Development of methods to identify digitally excluded older ..."
[23]: https://www.bmj.com/content/392/bmj.r2471.full.pdf?utm_source=chatgpt.com "can the NHS solve its logging-in problem?"
[24]: https://www.healthwatch.co.uk/report/2021-06-16/locked-out-digitally-excluded-peoples-experiences-remote-gp-appointments?utm_source=chatgpt.com "Locked out: Digitally excluded people's experiences of ..."
[25]: https://www.healthwatch.co.uk/sites/healthwatch.co.uk/files/20251204%20Referrals%20report_large%20print.pdf?utm_source=chatgpt.com "Closing referral black holes"
[26]: https://www.nationalvoices.org.uk/project/unlocking-the-digital-front-door/?utm_source=chatgpt.com "Unlocking the digital front door"
[27]: https://www.goodthingsfoundation.org/discover/digital-inclusion-insights/digital-inclusion-insights-2024/digitisation-and-healthcare-ensuring-equity-for-better-health?utm_source=chatgpt.com "Ensuring Equity Of Digital Access For Better Health"
[28]: https://www.patients-association.org.uk/news/patients-value-nhs-app-but-not-all-users-able-to-access-information-they-want-finds-new-report-from-the-digital-coalition?utm_source=chatgpt.com "Patients value NHS App but not all users able to access ..."
[29]: https://www.bma.org.uk/news-and-opinion/millions-of-hours-of-doctors-time-lost-each-year-to-inadequate-it-systems?utm_source=chatgpt.com "Millions of hours of doctors' time lost each year to ' ..."
[30]: https://www.bma.org.uk/media/2080/bma-vision-for-nhs-it-report-april-2019.pdf?utm_source=chatgpt.com "Technology, infrastructure and data supporting NHS staff"
[31]: https://www.bma.org.uk/media/xhoihr5f/bma-faqs-for-1-october-2025-online-consultations-v2.pdf?utm_source=chatgpt.com "Frequently Asked Questions on the 1 October 2025 ..."
[32]: https://www.rcgp.org.uk/getmedia/72f052b6-3227-48b4-87c9-b05ff90517c4/future-role-of-remote-consultations-patient-triage.pdf?utm_source=chatgpt.com "The future role of remote consultations & patient 'triage'"
[33]: https://www.rcgp.org.uk/patientonline?utm_source=chatgpt.com "GP online services toolkit: Introduction"
[34]: https://digital.nhs.uk/data-and-information/publications/statistical/nhs-app-statistics/december-2025?utm_source=chatgpt.com "NHS App Management Information - December 2025"
[35]: https://www.gov.wales/written-statement-nhs-wales-app-launch?utm_source=chatgpt.com "Written Statement: NHS Wales App Launch (9 May 2025)"
[36]: https://learn.nes.nhs.scot/73455/remote-consulting/near-me-video-consulting/near-me-final-report?utm_source=chatgpt.com "Near Me Final Report - Turas | Learn"
[37]: https://www.nidirect.gov.uk/services/view-your-medical-records-online-using-my-care?utm_source=chatgpt.com "View your medical records online using My Care"
[38]: https://www.england.nhs.uk/long-read/changes-to-the-gp-contract-in-2025-26/?utm_source=chatgpt.com "Changes to the GP Contract in 2025/26"
[39]: https://www.england.nhs.uk/long-read/delivery-plan-for-recovering-access-to-primary-care-2/?utm_source=chatgpt.com "Delivery plan for recovering access to primary care"
[40]: https://www.hssib.org.uk/patient-safety-investigations/workforce-and-patient-safety/second-investigation-report/?utm_source=chatgpt.com "Digital tools for online consultation in general practice"
