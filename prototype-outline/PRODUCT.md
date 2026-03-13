## Sector / interest / concern map

### 1. Core product thesis

* This is not “another online consultation form”.
* The real gap is continuity, closure, and active follow-up.
* Product goal: preserve context, preserve ownership, and keep chasing until a safe closure state exists.
* Better framing than “open-source front door”: a continuity and closure engine for primary care.

### 2. NHS integration surface

* Patient sign-in via NHS login.
* NHS App as a surfaced responsive web experience.
* Staff sign-in via the NHS staff identity system.
* GP transactions through supplier-paired GP integrations.
* Outbound and follow-up through the national messaging service.
* Proxy support is essential and currently transitional: local practice-managed proxy now, national proxy later.


Features: Support voice notes for patients not confident (or not wanting to be a burden) with a live phone call, that is transcribed automatically for the record and to be read, and can use a similar approach for the reverse, to said patients spoken voice notes based on written GP/staff inputs, voiced automatically for a preferred phone response (patients can even pick a voice). Maybe automatic translation too.

### 3. Platform maturity / stability

* National identity and messaging layers are the future-facing, relatively durable parts.
* GP transaction layers are older, awkward, still heavily used, and unlikely to disappear soon.
* Proxy is clearly going national, but current implementation is mid-rollout.
* Safe architecture: stable national core, ugly GP-side adapters, proxy subsystem that can straddle both worlds.

### 4. Access model critique

* Current tools optimise intake and routing, not continuity or resolution.
* Standardised pooled routing often weakens continuity unless continuity is deliberately reintroduced.
* Website-only or form-heavy access can look efficient while making access worse for deprived or chaotic patients.
* The key problem is not “digital exists”, it is “digital becomes a wall”.

### 5. Workflow / engine thinking

* The product should be a workflow engine, not a form engine.
* Core components:

  * rules engine
  * state machine
  * scheduler
  * message orchestration
  * receipt / reply handling
  * task routing
  * audit timeline
  * GP adapter layer
* Every issue becomes a care episode with explicit states, owners, timers, and closure conditions.

### 6. Messaging and follow-up

* App-first is fine, app-only is stupid.
* The patient group you care about needs SMS, phone, proxy, community support, and sometimes face-to-face.
* Key design principle: best-channel-first, then keep chasing until closed.
* Unread / ignored messages should become prioritised staff tasks, not passive silence.
* Important messages should always offer tiny state-confirmation actions:

  * I’m fine now
  * I still need help
  * Please call me
  * Contact my carer
  * Another language / easier format

### 7. Deprivation / inclusion / communication barriers

* Poor service design itself creates poor outcomes.
* Patients with hard lives often cannot afford friction, ambiguity, jargon, or dead ends.
* The platform should surface available help clearly before patients need to know the right role names.
* Communication profile should be first-class:

  * language
  * literacy / easy-read
  * interpreter needs
  * proxy / carer
  * reliable contact route
  * unstable housing / difficult contact patterns

### 8. Wider team / role-first support

* Patients should not need to know what a social prescriber, care coordinator, or wellbeing coach is.
* UX should be goal-first:

  * help with debt / housing / support
  * help changing habits / sticking to a plan
  * help navigating appointments / referrals / medicines
  * help from a clinician
* Underneath, the system routes to the right local role.
* The platform should support more outcomes than “book GP slot”.

### 9. Staff workflow reality

* Staff do not want “more chat” or “another inbox”.
* Patient side can feel like a thread / room / conversation.
* Staff side should be queues, tasks, summaries, ownership, escalation rules.
* Patients should feel held by a team; staff should only see what matters to them.

### 10. Continuity

* Continuity is not a luxury. It is linked to better outcomes, fewer admissions, lower repeat demand, and safer care.
* It is valued in principle and often traded away operationally.
* A lot of current digital access models weaken continuity by default.
* The product opportunity is to reintroduce continuity systematically, not nostalgically.

### 11. Community / non-practice partners

* Potential future feature: tightly-scoped community partner roles.
* Examples: library, shelter, drug service, refugee support, local community hub.
* Use case: contact support, attendance support, practical barrier resolution, outreach.
* Strict limits: no broad record access, no clinical decision authority, full audit.

### 12. Patient participation / PPG

* This should be a separate bounded context, not mixed into care workflows.
* Useful features:

  * easier joining
  * representative participation profiles
  * structured feedback
  * targeted mini-consultations
  * “you said / we did” action log
  * hybrid and async participation
* Avoid public forums and anything that turns practice operations into a referendum.

### 13. Competitor / market landscape

* Existing market clusters around:

  * online consultation / intake
  * triage and routing
  * messaging
  * transcription / scribing
  * document automation
  * admin chatbots / call-recall
* Less obvious market focus on what you want: continuity, closure, proxy-aware follow-up, deprivation-aware access recovery.
* Mixed-tool environments appear normal. Practices often run multiple systems or overlapping routes.

### 14. Commercial / procurement reality

* Public pricing exists for some tools, but actual buying often happens at commissioner or regional level.
* Per-patient pricing dominates, even where it makes poor technical sense.
* Effective practice cost and public list price are often different.
* Your instinct is that a continuity platform should not be sold like marginal infrastructure is linearly expensive.

### 15. Open-source angle

* NHS policy rhetoric is pro-open code.
* In this exact patient-front-door / triage / workflow niche, the live market is mostly proprietary.
* There does not appear to be a serious open-source equivalent in routine NHS use.
* Open-source remains strategically interesting, but “we are open source” is not enough as a core proposition.

### 16. Evidence / policy / external comparison

* Important external benchmark themes:

  * continuity reduces repeat demand and improves outcomes
  * online consultation tools can create inequity and safety problems
  * deprived populations get worse continuity and worse access
  * better practices preserve continuity and multiple routes, even when modernising access
* This is the lens for comparing GTD / New Bank to broader evidence.

---

## One / two-page backbone summary

This chat converged on a single main idea: the product should not be built as a better online consultation form, a prettier portal, or an “AI triage” front door. The real gap is continuity. Existing systems mostly optimise intake, routing, and workload protection. They often standardise the patient into a generic form, pool contacts away from named ownership, and treat silence or dropout as an acceptable endpoint. Your proposed system is instead a continuity and closure layer for primary care: a platform that keeps context, keeps ownership, and actively follows an issue until there is a meaningful closure state.

The NHS integration shape for that is viable. The patient side can use NHS login and be surfaced inside the NHS App. Staff can sign in through the normal NHS staff identity layer. Messaging and follow-up can use the national messaging platform, with app, email, text, and letter. GP-system transactions still sit behind awkward supplier-paired integrations, so the safe architecture is a national-core product with GP-side adapter layers. Proxy access is essential and should be treated as dual-mode for now: practice-managed proxy relationships today, national proxy integration as it matures.

The product itself wants to be an event-driven workflow engine, not a form engine. Every patient issue becomes a care episode with a current state, owner, waiting-on field, timers, next review time, and explicit closure state. Around that episode sits a rules engine, scheduler, messaging orchestrator, reply handler, task router, audit timeline, and GP adapter layer. The system should actively chase both sides of the interaction: acknowledge, follow up, escalate unread messages, escalate no-reply, convert uncertainty into structured staff tasks, and preserve issue history across repeat contacts.

A big theme through the chat was that digital access is often designed as if the patient is the problem. For deprived communities, undereducation, difficult contact patterns, multiple languages, unstable housing, care burdens, and chaotic lives all mean friction kills care. The system should therefore treat communication and support needs as first-class. It should know preferred language, literacy level, need for easy-read, interpreter requirement, proxy or carer involvement, reliable channel, and whether digital contact repeatedly fails. App-first is fine, but app-only is a mistake. The operating principle is best-channel-first, then keep chasing until closed.

This also led to a broader model of access. Patients should not need to know what a social prescriber, care coordinator, or health and wellbeing coach is in order to ask for the right help. The system should surface what support exists locally in goal-first language: help with housing, debt, loneliness, stress, benefits, long-term condition support, navigation, medicines, practical admin, or direct clinical need. Underneath, it routes to the right local role or service. In other words, the product should support many more outcomes than “book GP slot”: self-referral, pharmacist, care coordinator, social prescribing, community partner outreach, face-to-face support, proxy contact, manual callback, or clinical escalation.

Another strong theme was that the patient interface should feel like a thread with a care team, while staff should never experience it as open chat. Patients can see a simple ongoing issue thread, human-readable statuses, clear next steps, and light-touch replies like “I’m fine now”, “I still need help”, or “please call me”. Staff see role-specific queues, summaries, task lists, and escalations, not an inbox firehose. That lets the patient experience feel personal and held, while the practice experiences it as structured work rather than endless interruptions.

The chat also pulled in wider non-software lessons from better-performing practices. The evidence suggests that continuity, proactive follow-up, trained navigation, good phone handling, and wider team roles improve outcomes. Mundane work is not separate from care; it often is the care that prevents deterioration. The platform should therefore be seen as a way to make that “mundane but essential” care cheaper and more reliable, not as a flashy AI layer. Optional LLM use could exist for summarisation, drafting, or classification, but it should never sit as a wall between patient and clinician or take unsafe autonomous decisions.

You also explored two adjacent domains. First, patient participation: not as a public forum or voting system, but as a separate participation layer where patients can join, give structured feedback, take part in targeted consultations, and see a “you said / we did” action log. Second, community partners: a future, tightly-scoped admin/outreach role for trusted external organisations like libraries, shelters, or support services to help with contact and attendance barriers.

On market positioning, the conversation moved away from “better quality open-source open front door” and toward “the missing continuity layer”. Existing suppliers cluster around intake, routing, messaging, transcription, and admin automation. The more distinctive gap is persistent follow-up to closure, proxy-aware access, deprivation-aware contactability, and automatic escalation from digital failure into prioritised human action. Open-source is still strategically attractive, but in this niche it is not the mainstream NHS pattern, so it is not enough as a USP on its own.

The overall backbone, then, is this: build a primary-care continuity and closure platform that integrates with national NHS identity and messaging, wraps GP-system writes behind adapters, preserves issue context across time, supports the wider practice team, handles proxy and communication barriers properly, and actively recovers patients who would otherwise fall out of contact. The patient should experience a simple, low-friction, human-feeling thread with their care team. The practice should experience reduced hidden failure, less duplicated history, safer follow-up, and better use of the non-GP workforce.

## Suggested folder spine

* `00-product-thesis`
* `01-nhs-platform-and-integrations`
* `02-gp-system-adapters`
* `03-workflow-engine-and-state-model`
* `04-messaging-followup-and-contactability`
* `05-proxy-carers-and-access-needs`
* `06-continuity-and-safety-evidence`
* `07-deprivation-inclusion-and-communication`
* `08-role-first-service-routing`
* `09-staff-ux-and-queues`
* `10-patient-ux-and-thread-model`
* `11-community-partners`
* `12-ppg-and-participation`
* `13-competitors-pricing-and-market`
* `14-open-source-and-deployment-model`
* `15-gtd-new-bank-comparison-and-local-evidence`

If you want, I can turn that folder spine into a fuller outline with subfolders and doc names.
