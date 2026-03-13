# NHS Integrated Patient App

#### You:
workflow/security/opsec/political-connections aside, talking only about the tech/, mostly about the code and apis/available-infra.... if I wanted to build a ship a fully nhs-integrated patient-facing app where the patients login viw their nhs login, and so do the doctors or staff (ideally integrated into their normal network/working-pattern, no outright 'new systems') which has the aim of making 'radical support' easy for practices, with the general principle of not just making GP access as easy as possible (within the law, nhs rules, operating environment limits, etc), but with a system that actively chases both sides of any patient input, so for example: "patient wants appointment, clicks I want an appointment, appointment is created at the next available slot" is about as easy as it could technically be, but doctors need info, so that form has to have some input for 'why do you want an appointment'? Right now, the design is such that every possible input is displayed at once (my base 'poor experience' example is PATCHS, and is kinda what we're looking to replace, because PATCHS fucking sucks, as every user sees the same process, despite some decision tree stuff, that informs the doctor, the patient onboarding is poor, and it has no active 'keep in touch' mechanism, no automated chase "are you better now?" follow-ups or similar.). Technically speaking, if I wanted to provide a better platform that does this 10x more conveniently for patients (I don't want to put LLMs in the system, but I _could_. We're not opposed to it, but it's not really at the infrastructure layers that we're concered with here. Essentially I supose I'm asking how complex is a fully integrated NHS app's patient-facing 'website' now that we can adopt NHS-login and NHS-app support by default, instead of plugging it on as an afterthought to a cheap as fuck, barely designed, former-academic side-project like PATCHS. Gimme a good sense of that, with no waffle.

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
I’m checking the current NHS integration surface rather than relying on memory: NHS login, NHS App messaging/integration, GP clinical system hooks, and the current API/assurance constraints. Then I’ll map that to what’s actually hard in code versus what’s hard because of access, onboarding, and NHS platform boundaries.


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
The login side is relatively civil now. The harder parts are still the clinical-system writes, practice workflow fit, and which national channels you can actually use for outbound follow-up without inventing a parallel comms stack.


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
It’s a lot less grim than it was a few years ago, but it still is not “just build a nice web app and plug into the NHS”.

On the patient side, auth is basically solved. NHS login is standard OIDC over the public internet, and the verification level split is clear: P5 is enough for things like contacting a GP or receiving notifications, while P9 is needed for access to records or other personal clinical data. Surfacing your service inside the NHS App is also now a normal pattern: the NHS App web integration is literally a responsive website embedded in the app. The catch is the integration process around it: product assessment, sandpit, AOS, SCAL, connection agreement, post-live reporting, annual review. The frontend is normal web work; acceptance into the NHS wrapper is the slower part. citeturn403116view3turn331434view2turn403116view5

On the staff side, same story. CIS2 is also OIDC, works over the internet, supports the existing NHS identity world, and gives you SSO with smartcards or newer authenticators like Windows Hello, security keys, Microsoft Authenticator and iPad-based flows. GP practices already live in CIS, so you can fit normal sign-in patterns instead of creating a separate clinician identity silo. That part is genuinely much better now. citeturn403116view2

The hard bit is not login. It is GP-system transactionality and workflow fit. For patient-facing actions that actually touch the practice system, you are still basically in IM1/pairing land against the principal GP systems, currently EMIS Web and TPP SystmOne. The IM1 patient API surface is broad enough for the shape you want — view/book/amend/cancel appointments, repeat prescriptions, record viewing, and communication with the practice — but it is still supplier-paired, not a single clean national write API. That means dual integration, behaviour differences, and a lot of “works in principle, depends on the supplier/practice setup in reality”. citeturn403116view1turn403116view0

And GP Connect does not magically remove that for a third-party patient app. GP Connect’s patient-facing record/prescription APIs are live, but NHS England says they are currently only available for New Market Entrant suppliers as data providers and are in use with the NHS App as the consumer; they were not onboarding extra consumer suppliers at the time of writing. GP Connect Appointment Management new supplier development is also paused. So if your mental model is “national patient API for records/prescriptions/appointments, done”, that is not the current shape of the platform. citeturn444935view0turn853096search1

Your “actively chase both sides” idea is where the platform is actually better than PATCHS-era products. NHS Notify now gives you a proper outbound layer across NHS App messages, email, SMS and letters, and NHS App messaging supports notifications, delivery/read receipts, fallback logic, and for some message types keyword or free-text replies. So timed follow-ups, nudges, “are you better now?”, reminders after no-read, escalation after no-reply, and closure prompts are all straightforward workflow-engine problems. You do not need an LLM for that. You need a decent rules engine, state machine, scheduler, audit log, and a way to turn replies into staff tasks without dumping raw message sludge into reception. citeturn403116view4turn331434view0turn331434view1

The other thing to keep in your head is that NHS login does not grant access by itself. Practice-held permissions still govern what a patient can see and do. GP Connect’s patient-facing docs are explicit that permissions and service access are maintained by the GP practice, and record sections can be restricted or redacted at practice or patient level. So you can absolutely build a much better adaptive front door than PATCHS, but the backend rights model is still practice-controlled, not app-controlled. citeturn331434view3turn579089search0turn579089search3

If “radical support” includes carers, parents, or trusted helpers, proxy is not a side quest. The National proxy service is still in private beta, with a national proxy data store planned through 2027; today many practices still manage proxy locally. There is now an IM1 PFS Auth API for proxy auth, but you are building across a transition period rather than a finished national model. citeturn231140view0turn231140view1

Then there’s the boring-but-real part: assurance. DCB0129/0160 clinical safety are mandatory, DSPT is required for organisations with access to NHS patient data and systems, DTAC is current and has a 2026 form refresh, and the NHS App/NHS login onboarding stack still wants conformance evidence and ongoing review. This is real delivery work, not garnish. citeturn509061search11turn509061search3turn509061search2turn509061search13turn403116view5

So the honest answer is: the patient-facing website itself is medium difficulty. A good team can build that bit cleanly. A fully NHS-integrated product that lets patients do real things, lets staff stay close to normal working patterns, and keeps chasing both sides of the interaction is high difficulty, because the work is in the integration boundaries and operating constraints, not the UI.

If you scope it as NHS login + NHS App web surfacing + CIS2 for staff + IM1 pairings for GP transactions + NHS Notify-driven follow-up workflows, it is a serious but very buildable product.

If you scope it as “single national integration, no supplier quirks, no extra operational surface for staff, no practice-level variance”, that product still does not exist because the platform underneath still is not that clean.


#### You:
that was a LOT of TLAs. Write the same info again, but without the acronyms. 

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
I’m recasting it in plain English and trimming the alphabet soup. Same substance, just the parts that matter in normal words.


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
In plain English: the patient sign-in side is no longer the nasty part. NHS login is a standard web sign-in integration, you can choose how strongly a person has to prove who they are, and the NHS App can host your service as a connected responsive web service. The real cost is the onboarding and assurance process around it, not the front-end code. citeturn450635search0turn450635search1turn873135search0

Staff sign-in is also in decent shape now. The NHS staff identity service is a standard browser-based sign-in flow and supports the existing NHS identity world, including smartcards and newer methods like Windows Hello, security keys, Microsoft Authenticator and iPads. So you can fit into normal working patterns instead of inventing a separate clinician login system. citeturn515203search0turn515203search3turn515203search13

The hard part is still writing into GP systems and doing it in a way practices will actually tolerate. The older GP integration layer still means pairing separately with the main GP system suppliers, currently EMIS Web and SystmOne. That layer does cover the things you care about — appointments, repeat prescriptions, record viewing, and messaging the practice — but what the patient can actually do is still governed by the practice setup, and supporting NHS login does not magically remove the GP-side linking and supplier-specific behaviour. citeturn515203search1turn515203search4turn515203search6turn450635search6turn450635search1

There are some more national interfaces, but they do not give you a single clean write path for everything. The national GP sharing programme has patient-facing record and prescription interfaces live, but the appointment part has paused new supplier development, and the overall patient-facing side is still not a full replacement for supplier-paired GP integrations. So the product is buildable, but the integration shape is still messy under the hood. citeturn515203search2turn450635search8turn450635search9turn166297search11

Your “keep chasing both sides” model is much more feasible now than it was in the old online-consultation world. NHS Notify can send through the NHS App, email, text, or letter, and the NHS App messaging rules explicitly support app-first with fallback to another channel if needed. That makes “are you better now?”, “you haven’t replied”, reminders, nudges, and escalation mostly a workflow-engine problem, not a machine-learning problem. citeturn166297search0turn166297search1turn166297search12turn360777search1

Where this still bites is proxy access and governance. If you want carers, parents, or trusted helpers to act for patients, the national proxy service exists but is still rolling out in stages, with local practice handling still common for now. And if you are touching NHS patient data and systems, you are in the world of mandatory clinical safety, security, and technical assurance requirements from day one. citeturn360777search2turn450635search11turn360777search3turn966078search3

So the blunt version is: the patient-facing website itself is not the difficult bit anymore. A good team can build that well. The hard bit is the last 30 percent — real GP-system writes, practice-by-practice variance, staff workflow fit, proxy handling, and passing the NHS entry checks. That is why most of the current products still feel like form dumps with a logo on top.


#### You:
Design the codebase for using ```NHS Notify now gives you a proper outbound layer across NHS App messages, email, SMS and letters, and NHS App messaging supports notifications, delivery/read receipts, fallback logic, and for some message types keyword or free-text replies. So timed follow-ups, nudges, “are you better now?”, reminders after no-read, escalation after no-reply, and closure prompts are all straightforward workflow-engine problems. You do not need an LLM for that. You need a decent rules engine, state machine, scheduler, audit log, and a way to turn replies into staff tasks without dumping raw message sludge into reception.``` to its absolute best. If we perfect NHS Login and use of Notify to actively chase patients until we know for a fact they're as 'better' as possible. The main practice I am interested in (New Bank health Centre and other GTD Healthcare managed practices) has PATCHS (so do most gtd practices by now) so presumably already has 'nhs login permissions' understanding within the org. The thing they _keep_ mentioning about PATCHs is that "it has AI in it" or maybe more like "it's part of our diagnostic pathway" (mainly for automated triage flags), which we can definitely compare to technically with even very minor LLM usage and a good log and some heirstic fallbacks for additional safety). 
The proxy service is new to me but yes, integrating that would be essential. Messaging the person and their carer would often be appropriate and very useful (I've seen google reviews complaining about this). "IM1 PFS Auth API for proxy auth" I'm okay with a transition period if we're able to handle both, great.

No idea what DSPT/DTAC are, I'm well aware it would need to be NHS-passed for safety/security etc, and I'd open-source it for a start (with pluginable LLM by the deployment manager, if they want those features, they can configure any api key).

I know there are operating constraints beyond tthe tech, but I'm kinda trynna figure out if I can even build the tech in the first place. If I can convince a company to try and even back the idea of 'radical patient support' instead of 'tightly managed workflows that make people sicker'. 

scope it as NHS login + NHS App web surfacing + CIS2 for staff + IM1 pairings for GP transactions + NHS Notify-driven follow-up workflows and give me a good sense for what this project looks like. I prefer nodejs as a basis, but let's avoid having an opinion on the UI/framework (what's normal in NHS-supported projects today, not 10 years ago? React/Vue presumably still around, but I've been out of it since jQuery was a day-to-day-driver, so obvs I'm out of touch.

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
I’m pulling the live NHS platform shape first, then I’ll turn it into a concrete Node codebase design: system boundaries, service split, workflow engine, message handling, proxy model, GP write paths, and what you can realistically ship first.


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
The shape is clear now. You can build the tech. The real design move is to treat the product as an event-driven care-workflow system with GP-system adapters, not as “a better online form”. The rest is mostly careful boundary work around sign-in, messaging, proxy, and audit.


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### You:
it would also be useful to know if I can deploy against dev/test/staging NHS tech (or at least an official local replica/lib that is known to provide exactly the same interface for mocks/builds) as a member of the public with zero connected business relationship.

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
That changes one important part: whether you can get your hands on the real interfaces before you have an NHS backer. I’m checking that directly now, because it affects whether this is a build-first project or a partnership-first project.


#### ChatGPT:
\[Unsupported Content]


#### You:
this is always a build-first project, I'm good at that bit. With a good product I can sell an idea, but the closer I can prototype it to the final state, the better.

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
Yes. You can build a near-final prototype first.

What you can and cannot hit for real, before you have an NHS buyer:

You can create a public developer account on the NHS developer platform. NHS login has a sandpit and explicitly requires a proof of concept in that sandpit during discovery; the sandpit is described as a copy of production code, and test data is supplied when your test account is set up. General NHS API development and integration environments also exist behind the developer account flow. citeturn282069view5turn282069view3turn282069view7turn282069view4

CIS for staff is even friendlier for prototyping: the mock authorisation service is self-service and does not require registration. Real path-to-live and production access are different; those require application registration, and the path-to-live environments are described as being for suppliers. citeturn282069view1turn282069view2

The national messaging layer has a sandbox too, but it is not a perfect replica. The published API docs say the sandbox is for early developer testing, only covers a limited set of scenarios, and is stateless. So it is useful for contract work, not for proving your whole chase-engine end to end. citeturn568166search10

The awkward bit is GP writes. The GP pairing route is supplier onboarding, not “random developer downloads a mock and gets going”. NHS England’s pairing docs say access to the provider mock API comes after the product is confirmed viable and the interface licence is executed with each provider supplier. Right now the live provider side is still basically the two major GP system lines. citeturn519837view0turn519837view3

So the honest build-first answer is:

- yes for public developer account, NHS login sandpit, some NHS API dev and integration environments, staff auth mock, and the messaging sandbox
- no for “full official end-to-end replica of the whole stack as a member of the public with no relationship”
- definitely no for full GP transaction integration without becoming a paired supplier

Also, live use of NHS login is not open to any random app. NHS England says services using it must be commissioned or sponsored by an NHS organisation. Existing use of another product at a practice does not transfer that approval to you. citeturn568166search3turn815288view2

Given that, the right build-first project is this.

## What the product actually is

Not “an online consultation form”.\
It is a care-workflow platform with four hard boundaries:

1. identity
2. messaging
3. GP-system adapters
4. audit and safety

Everything else is product logic.

Your closure condition is not “know for a fact they are better”. Don’t design around that fiction. Design around explicit closure states:

- self-reported resolved
- clinician-closed resolved
- needs more information
- needs appointment
- needs prescription or admin follow-up
- urgent escalation
- unreachable
- proxy-only communication
- withdrawn / declined

That is a real system.

## Codebase shape

Node, TypeScript, monorepo.

```text
/apps
  /patient-web
  /staff-web
  /ops-admin

/services
  /edge-api
  /identity-broker
  /workflow-engine
  /message-orchestrator
  /reply-ingest
  /task-router
  /gp-adapter-emis
  /gp-adapter-tpp
  /proxy-resolver
  /audit-timeline
  /search-reporting

/workers
  /workflow-workers
  /message-workers
  /receipt-workers
  /sync-workers

/packages
  /domain
  /contracts
  /event-schemas
  /rules-dsl
  /clinical-heuristics
  /ui-design
  /test-fixtures
```

Core choices I’d make:

- Fastify for service edges
- PostgreSQL as system of record
- Temporal for long-running workflows, timers, retries, durable state
- OpenTelemetry everywhere
- object storage for uploads and rendered message artefacts
- outbox pattern for every external send
- strict event schemas with versioning

Do not split into microservices too early. Split by deployment boundary only when you need to. The monorepo matters more than service count at first.

## The main domain model

You want first-class entities for the thing PATCHS largely smears together:

```ts
type CareEpisode = {
  id: string
  patientId: string
  proxyContextId?: string
  practiceId: string
  workflowDefinitionId: string
  status:
    | "open"
    | "awaiting-patient"
    | "awaiting-proxy"
    | "awaiting-staff"
    | "escalated"
    | "closed"
  closureState?:
    | "self_reported_resolved"
    | "clinician_closed_resolved"
    | "needs_appointment"
    | "unreachable"
    | "urgent_escalation"
    | "withdrawn"
  currentStep: string
  createdAt: string
  updatedAt: string
}

type MessageAttempt = {
  id: string
  episodeId: string
  recipient: "patient" | "proxy" | "both"
  templateId: string
  channelPlan: Array<"nhs_app" | "email" | "sms" | "letter">
  status:
    | "queued"
    | "submitted"
    | "delivered"
    | "read"
    | "replied"
    | "fallback_sent"
    | "failed"
  externalRefs: Record<string, string>
}

type StaffTask = {
  id: string
  episodeId: string
  queue: "reception" | "duty_doctor" | "pharmacist" | "admin" | "safeguarding"
  kind:
    | "review_reply"
    | "book_appointment"
    | "approve_prescription_path"
    | "call_patient"
    | "call_proxy"
    | "safety_check"
  priority: "low" | "normal" | "high" | "urgent"
  summary: string
  rawReplyRef?: string
}
```

Every state transition emits an immutable audit event. Every message send, receipt, read, reply, escalation, rule decision, and GP writeback lands on the episode timeline.

## Workflow engine, not form engine

The NHS App and national messaging stack now support notifications, read receipts, fallback behaviour, and for some message types keyword or free-text replies. NHS Notify handles multi-channel routing and contact lookup from the national demographics service using NHS numbers, and it suppresses sends for restricted or deceased records. That is exactly enough to build an active chase system. citeturn815288view0turn308841search1turn308841search2turn308841search0

Your workflow layer should be data-driven.

```ts
const workflow = {
  id: "acute-minor-illness-v1",
  trigger: "intake_submitted",
  steps: [
    {
      id: "initial_ack",
      action: "send_message",
      template: "thanks_we_got_this",
      channels: ["nhs_app", "sms"],
    },
    {
      id: "await_reply_4h",
      waitUntil: { after: "4h" },
      ifNot: ["patient_replied", "proxy_replied", "staff_closed"],
      action: "send_message",
      template: "checking_in_are_you_ok",
      channels: ["nhs_app", "sms"],
    },
    {
      id: "no_read_24h",
      waitUntil: { after: "24h" },
      ifAll: ["message_unread"],
      action: "create_task",
      task: { queue: "admin", kind: "call_patient", priority: "normal" },
    },
    {
      id: "symptoms_worse",
      onEvent: "reply_received",
      ifAnyReplyFlags: ["worsening", "red_flag", "new_severe_pain"],
      action: "create_task",
      task: { queue: "duty_doctor", kind: "safety_check", priority: "urgent" },
    }
  ]
}
```

Keep rules deterministic. Version them. A care episode always knows which rule version decided each action.

## GP integration

The GP side is still paired supplier integration with the provider systems, not one clean national write interface. The pairing docs are explicit about the current provider side and the licence / conformance process. citeturn519837view0turn519837view3

So your core app must never know about a supplier directly. It talks to an internal adapter contract:

```ts
interface GpAdapter {
  getPatientCapabilities(patientId: string, practiceId: string): Promise<Capabilities>
  listBookableSlots(args: SlotQuery): Promise<Slot[]>
  bookSlot(args: BookSlot): Promise<BookingResult>
  createConsultationMessage(args: MessageToPractice): Promise<WriteResult>
  getRecordSummary(args: RecordQuery): Promise<RecordSummary>
  createTaskOrFlag(args: PracticeTask): Promise<WriteResult>
}
```

The patient product can be almost final before those adapters are live. You build the real product against a local “practice simulator” adapter, then replace only the adapter package when pairing lands.

## Proxy handling

Proxy matters enough that I would not leave it for later. National proxy is still in private beta, and GP practice review and setup in the GP system still sit in the loop; broader direct integration is coming rather than finished. There is a national route for authenticating proxies, but you are building across a transition period. citeturn815288view5turn871012search3turn871012search4turn871012search2

So the proxy resolver should merge three sources:

- local practice-managed proxy relationships
- national proxy verification when available
- explicit episode-level consent / communication preferences

Never model proxy as a boolean on patient. Model it as a relationship with scope.

## Staff UX

Keep the staff surface tiny.

CIS sign-in is standard browser-based sign-on with modern authenticators and is meant to support single sign-on across applications. Use that, but do not build a parallel clinical workstation. citeturn815288view4

The staff app should be:

- queue view
- episode timeline
- quick actions
- escalation controls
- template override
- write-through actions to GP system

No giant inbox. No raw message sludge landing in reception.

Patient free-text replies should go through a reply normaliser:

- parse keywords and structured answers first
- heuristic extraction for symptom worsening / admin asks / medication issues
- optional LLM summariser behind a feature flag
- raw text always retained, but staff sees structured summary first

## AI

If you add LLM features, keep them outside the hard path.

Use them only for:

- drafting follow-up questions
- summarising patient replies
- suggesting non-clinical routing
- detecting missing info for staff review

Never let them:

- assign urgency alone
- book slots alone
- close episodes
- suppress escalation
- change coded facts

That is the sane line anyway, and the GP pairing docs now explicitly say the pairing process reviews the whole product documentation, but does not do AI-specific technical assurance; that responsibility stays with the deploying organisation. citeturn519837view1

## Front end

The NHS App web route is just a responsive website surfaced in the NHS App, and it has to follow the NHS digital service manual. There is an NHS frontend library, and there is a maintained React component port under the NHS organisation. Framework is not the main question anymore. citeturn282069view6turn815288view7turn591018search0turn591018search2

So:

- React is the practical default
- server-render forms or progressive enhancement for the patient side
- keep the UI shell thin and dumb
- push state, rules, and integrations into services

Vue would be fine too. I would not optimise for framework ideology here.

## Build-first path

If you want the closest possible prototype before any buyer:

1. Build real patient and staff apps.
2. Use real NHS login sandpit if they’ll accept the application; otherwise keep a local OIDC shim with the same claims shape.
3. Use the self-service staff auth mock.
4. Use the real messaging sandbox for contract and error-path work.
5. Build a high-fidelity local GP practice simulator behind your adapter contract.
6. Build proxy as local-first plus national-ready.
7. Make every workflow deterministic and replayable.
8. Only after that, go get a commissioning partner and start real GP pairing.

That gets you a product demo that is close enough to final state to sell, without blocking the whole project on the one part you cannot get as a member of the public: live GP system pairing.

The short version on access is: you can get enough official test surface to build the real product shell and the hard orchestration logic, but not enough to finish the GP transaction layer without becoming a real supplier. That is still plenty for a build-first strategy.


#### You:
you mentioned a couple of times that "NHS Proxy" is in development/beta, and that has me wondering, what's the ongoing/released/to-release state of apis or endpoints/systems or official-patterns in this space? Like what _is_ the current state of NHS patient-to-practice infrastructure, where has it been historically and where is it going in future. Like if we adopt these handful of endpoints, are they going to change tomorrow because they're 10 years old, or are they pretty new and actively used by enough providers to keep them in service/stable for the longer term?

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
I’m mapping the stack by age, current adoption, and likely stability: old GP-system interfaces, newer national identity/messaging layers, and the proxy transition. Then I’ll separate “safe to build on” from “still moving underneath you”.


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
The short answer is: no, the important bits are not likely to vanish tomorrow. But the stack is split between a newer national layer that looks like the future, and an older GP-system layer that still does most of the real work.

Right now the patient-to-practice stack is basically this. Identity is national and mature: NHS login is live, launched in 2018, has more than 46 million users, and more than 120 live apps and services. The NHS App is the national shell, and a web integration is just a responsive site surfaced inside it. Messaging is moving national too: NHS Notify is live, runs as a silver service, has sent 212 million messages across 19 services, and is explicitly the platform for app messages, email, text and letters. Those are the bits I would treat as durable. citeturn470601view0turn238847view1turn308152view4

The bit underneath is still much messier. GP practices remain the data controller for their records, the NHS App cannot amend those records, and patient online access is still tied to GP system behaviour and practice permissions. When a patient moves practice, their old GP online account is deleted and a new one is created at the new practice when they next use the NHS App, which tells you a lot about where authority still lives. citeturn238847view8turn881698view0

Historically, that older layer was the whole game: practice-local online services, supplier-specific portals, supplier-paired integration, local proxy handling, local record-access decisions. That world is still there. The GP pairing route explicitly says there are no current plans to decommission the older integration mechanism, though alternatives may replace it later and there are no confirmed timescales. So if you build on that path, it is old, but not about to disappear. It is the opposite problem: stable enough to stay, awkward enough to keep. citeturn356968view2

The newer national direction is pretty obvious now. The NHS App roadmap says they are pushing digital-first messaging with NHS Notify, working towards a single inbox, raising read rates, and improving support for parents and carers. NHS England’s 2025 messaging blog is even blunter: the NHS is shifting toward the NHS App as the primary communication channel, then text, email and letters. That is strategic direction, not a side experiment. citeturn238847view5turn356968view4

Proxy is the clearest example of something genuinely in transition. The National proxy service is still in private beta and only bronze-grade today, but the roadmap is not vague hand-waving. Between 2025 and 2027 it plans a national store of proxy relationships, migration of locally held proxy relationships, GP system integration, cross-practice proxy support, and a new information standard. It also says that from 2027 GP practices in England will be required to use the national proxy service to award proxy access, and that all proxy-access providers will need to comply with the new proxy standard coming into effect in 2026. So proxy is not “done”, but it is very clearly where the platform is going. citeturn271697view4

GP Connect sits in the middle. It is national, live, integrated with all major GP software providers, and access to patient records through it is mandated for all GP practices in England, with the replacement GP commercial framework also expected to mandate it. That makes GP Connect itself a safe long-term bet. But the patient-facing part is not yet an open market. The patient-facing record and prescription interfaces are currently only available with new-market-entry suppliers as data providers and the NHS App as the consumer, and no extra consumer suppliers were being onboarded at the time of writing. Appointment management is also in flux: new supplier development has been paused while responsibility moves to a broader appointments strategy. So GP Connect is stable as national plumbing, but unstable as a route for your own patient-facing app to consume directly. citeturn749854view0turn238847view9

Online consultation is another “national shell over mixed local products” area. From October 2025, GP practices in England are required to keep online consultation tools open during working hours, and the NHS App is integrating more online consultation services so more users can contact their GP that way. That tells you the direction is not “replace every supplier tomorrow”; it is “standardise access and front-door behaviour while supplier diversity remains underneath.” citeturn238847view6turn238847view5

For messaging, the nuance matters. NHS Notify itself is live and solid. NHS App messaging, as a feature set, is still public beta and the docs explicitly say it does not yet support every scenario that text messages can, including some time-critical cases. The same docs also describe delivery receipts and fallback to another channel, which is why your chase-engine idea fits the platform well: build your own workflow logic, but never assume the app channel alone is complete enough for everything. citeturn308152view4turn356968view3

The other stable national bit worth caring about is demographics. The national demographics service is the master patient index for NHS numbers, GP registration and contact details, and there is a newer FHIR interface plus notifications for change of address and change of GP. That is useful because a patient-support product needs to survive people moving practice and changing contact details. This part is old infrastructure, but still actively modernising rather than being retired. citeturn930457search3turn533618view1turn533618view0

So, if you want the practical answer about adopting endpoints:

Build hard against NHS login, the NHS App web integration model, staff sign-in, NHS Notify, the national demographics service, and your own workflow engine. Those are the strongest long-term bets. citeturn470601view0turn238847view1turn308152view4turn930457search3

Wrap the GP transaction side behind adapters. The old GP pairing mechanism is still the practical write path and there are no decommission plans, but it is not the strategic future and it will remain supplier-shaped for a while. citeturn356968view2turn749854view0

Treat proxy as a dual-mode subsystem for the next couple of years: local practice relationships now, national proxy when available, with a migration path. That is the one area where the future is clear but the present is still mid-rollout. citeturn271697view4

Treat GP Connect patient-facing consumption as a maybe, not a foundation. It is promising, real, and live in limited form, but not open enough yet to be the base assumption for an independent product. citeturn238847view9turn749854view0

If you want the blunt framing: the risk is not “these endpoints are 10 years old so they’ll disappear next week”. The risk is “the NHS keeps old interfaces alive for ages while adding new national layers beside them, so you have to build for coexistence”. That is annoying, but it is buildable. And it means the safest architecture is a national-core product with ugly GP-side adapters and a proxy subsystem that can straddle local and national worlds for a while.


#### You:
"get a commissioning partner" ?

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
I’m pinning that to the actual NHS meaning, not using it as a vague business euphemism. In this context it’s about who can sponsor, buy, or formally back a service so you can move from prototype to real integration.


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
I meant: an NHS organisation willing to formally back, buy, or deploy your product.

In practice that could be a GP practice, a primary care network, an integrated care board, an NHS provider, or sometimes a local authority, depending on the service. For NHS login, NHS England says the service must be commissioned or sponsored by an NHS organisation. The NHS App integration form asks whether the service is commissioned by one or more NHS bodies in England, including an integrated care board, healthcare provider, primary care network, or GP surgery. citeturn757079search0turn757079search9

So “get a commissioning partner” was not me saying “find an investor”. I meant “find the NHS body that will say yes, we are backing this service for our population / practices / patients, and we will stand behind the onboarding, contracts, governance, and deployment”. That partner is usually what turns a prototype into something the NHS platform will let into live use. citeturn757079search0turn757079search11

There are a few flavours of this:

A sponsor says “we support this service and want it connected”.
A commissioner says “we are procuring or funding this for our organisations or patients”.
A deployment site says “we will actually use it in practice”.

Sometimes those are all the same organisation. Sometimes not. In your world, the first realistic ones are probably a GP practice group, a primary care network, or a provider like GTD Healthcare, because they can say “we want this used here” long before anything national happens. The NHS App and NHS login processes are built around that sort of relationship, not around solo public hobby access to live production systems. citeturn757079search0turn757079search2turn757079search9

So the sequence is basically:

build the product first,\
prove it against the public and mock environments,\
then get an NHS organisation to adopt or sponsor it,\
then use that relationship to move into live onboarding and real deployment. citeturn757079search2turn757079search9

That was all I meant.


#### You:
69.3 million population of Britain, vs 46 million users is BIIIIIG gap to rely on. We absolutely need to do better on sms/phone and especially vast improvements to face-to-face. Automated messages that stay unread or are ignored (even if they don't 'need' a response, we should ask for confirmation on state-changes, like click this link to say fine, or this link to follow-up, with sensible slugs so it's easy) should also result in staff tasks like a queue of people you might want to check on manually, by priority. Given the main patient group we're trying to be sure to reach are deprived communities, with difficult comms, multiple languages, competing life-pressures and demands, the idea is that people won't get healthier if it's even remotely hard, because people with hard lives put others first, we should be making sure every registered patient is at least telling us they're fine at least once a year. The 'trick' is that we make servicing that extra layer of care cheap (or even nearly free) for practices, who we recognise are under far too many competing pressures to expect them to put substantial resources into checking people are fine (where currently they're using the patient survey to ignore and forget patients who are NOT fine). 

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
I’m checking the numbers and the current official messaging pattern, because the coverage argument matters to the product shape. Then I’ll turn it into the concrete service model you actually want: app-first where possible, but never app-only.


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
The coverage point is real, with one correction: the 46 million figure is account/users for an England service, not “46 million active reachable app users in Britain”. The practical takeaway still goes your way: treat the app as the cheapest good channel, never as the only channel.


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
Yes. Design it on the assumption that the app channel is useful but incomplete.

Also, that 46 million number is the wrong thing to lean on either way. NHS login is for patients registered at a GP practice in England or receiving NHS services in England, not “all of Britain”, and the stronger live-usage signal is the NHS App activity: in December 2025 it had about 13.2 million distinct monthly users, and across 2025 about 25.7 million distinct users logged in at least once. That is big, but it is nowhere near “you can safely run the service as app-only”. citeturn846222search0turn518070search7turn518070search1

The platform direction already matches your instinct. NHS policy is to offer NHS App first whenever possible, but the official messaging guidance explicitly says to use routing plans with fallback to text, email or letter if the app message stays unread, often within a few hours depending on the supplier. NHS Notify itself is the national API for app, email, text and letter. Notice what is missing there: voice calls. If you want phone outreach, that is your own workflow and telephony layer, not something the national messaging service will do for you. citeturn272176search0turn518070search2turn518070search10

So the right product model is not “digital-first”. It is “best-channel-first, then keep chasing until closed”.

I’d make contactability a first-class domain object. Not just a mobile number and a couple of consent flags. A real, computed thing per patient and proxy: app reachable, text reachable, email reachable, letter-only, needs interpreter, prefers proxy, often unread, repeated no-response, requires manual call, requires face-to-face prompt. Every outbound step updates that profile. Over time the system learns the cheapest reliable route for each person without pretending everyone is digitally equal.

The workflow then looks like this:

A state change or clinical/admin trigger opens an episode.\
The workflow picks the cheapest likely-successful route.\
If unread, undelivered, or unanswered, it falls through the next route.\
At defined points it creates a staff task instead of sending another message.\
If the person is hard to reach, future episodes start from the proven route, not from the app again.

That is the key difference from current junk systems. They mostly optimise form capture. You want to optimise successful closure.

For your population, I’d build four queue types into the staff side from day one.

A “check they got this” queue. That is for unread or undelivered important messages after the digital cascade has failed.

A “needs human nudge” queue. That is for people who read but do not act, or repeatedly half-complete flows.

A “support barrier” queue. That is for language, carer contact, safeguarding, homelessness, chaotic contact details, repeated missed care steps.

A “worsening / uncertainty” queue. That is for replies or patterns suggesting clinical deterioration, confusion, or inability to self-manage.

That keeps reception from getting a sludge inbox. Staff see prioritised work, not raw messages.

On the patient side, every important message should have a lowest-friction state confirmation. Not “open app, log in, fill a form”. More like:

I’m fine now\
I still need help\
Please call me\
Please contact my carer\
I need this in another language

Whether the click lands inside the NHS App, on a secure web handoff, or through a short code reply depends on the channel, but the product principle is the same: every message tries to collapse ambiguity, not just broadcast information.

You’re also right about annual “are you okay?” style outreach, but I would not frame it as “prove every patient is fine once a year”. That sounds stronger than the system can honestly know. I’d frame it as a rolling support and contact-confirmation programme:

confirm contact route\
confirm proxy / carer details\
confirm support needs\
confirm whether any ongoing issue needs review\
surface non-responders into a low-cost outreach queue

That is realistic, auditable, and clinically defensible.

There is another reason not to rely on NHS login or the app alone: the setup itself excludes some people unless the practice helps them. The NHS login setup flow requires an email address and a mobile or landline even at the lowest level, and the GP practice guidance explicitly says some patients still need practice-issued online-registration details because they do not have acceptable photo ID, their identity check failed, they moved practice, or they are children who need the practice to assess competence for access. That is exactly the kind of population where your fallback and human-support model matters. citeturn846222search1turn846222search2

So the cheap-for-practice version is:

automate the boring chase,\
measure which channels actually work per person,\
turn failures into prioritised human tasks,\
treat proxy and carer communication as normal not exceptional,\
keep face-to-face as the last-mile safety net instead of pretending digital solved it.

Technically that is very buildable. The expensive part is not the messaging API. It is getting the rules, thresholds, and staff queue design right so that you reduce missed care without generating pointless work.

The product line I’d hold onto is this: the system is not trying to send more messages. It is trying to reduce the number of patients who quietly drop out of contact. That is a much better optimisation target.

If you want, I’ll turn that into a concrete Node domain model and workflow schema for contactability scoring, escalation thresholds, and staff-queue generation.


#### You:
what can we reasonably put into this platform that acts as a PPG enabler? More practice feedback and review cycle (no voting, change is still to be owned by the practice, but maybe we can create a workflow for exposing parts of that, let patients participate and communicate (very carefully) openly. This is an extra layer of major concerns that risk over-complicating our core, but patient engagement does need to be easier than it currently is (PPGs sometimes seem like they're designed to be slow and ineefective, but we have a lot of research on how to make PPGs work well, which can inform our design/implementaiton of those features)

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
I’m checking the current official expectations around patient participation groups and digital engagement, then I’ll translate that into what belongs in your product versus what should stay out to avoid contaminating the core care workflow.


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
Yes, but keep it as a separate bounded context, not mixed into the patient-care workflow.

The current rules actually help you here. Practices are required to have and maintain a patient participation group, make reasonable efforts to keep it representative, gather feedback in an appropriate and accessible way, review that feedback with the group, and make reasonable efforts to implement agreed improvements. The regulator also says this does **not** have to be a traditional committee with fixed members and formal meetings; it can be broader, including different groups and different ways of gathering views. NHS England’s current general-practice guidance also says the practice website should explain how patients can join and how they can give feedback. citeturn638723view0turn215213view3turn215213view0turn215213view1

That means the platform can do more than “host a PPG mailing list”. It can become the practice’s patient-participation operating layer.

What fits well:

A clean join-and-profile flow.\
Let patients or carers join the participation group, choose topics they care about, choose language, contact method, accessibility needs, whether they can do in-person, remote, or async-only, and whether they are willing to be contacted for quick consultations. That directly helps with the representativeness problem the regulations push on practices. The current practical toolkits also emphasise diversity, outreach, virtual participation, and underrepresented groups. citeturn638723view0turn215213view4

Structured feedback, not free-for-all chat.\
Give people a way to submit feedback tagged to themes like appointments, access, continuity, prescriptions, reception experience, language support, carers, online journeys, premises. Then separate three paths automatically:

- personal complaint or individual care issue
- service improvement suggestion
- participation topic for wider discussion

That matches the current NHS England direction that routine feedback can go via the practice, Healthwatch, or the local commissioning body, while complaints stay complaints. citeturn215213view1turn215213view0

Small consultations instead of giant surveys.\
The practice posts a proposed change, like “new appointment-booking wording”, “self-check-in trial”, “branch reception hours”, “new reminder style”, and the platform runs a short, time-boxed consultation with targeted cohorts. BMA guidance is explicit that practices should consult patient groups and use them to explain changes and pressures. citeturn215213view2

A “you said, we did / we didn’t, because…” register.\
This is probably the highest-value PPG feature. Every consultation or recurring issue gets:

- summary of what patients said
- practice response
- owner
- status
- public-safe outcome note

That turns participation from symbolic to legible. It also prevents the usual black hole where people assume nothing happened.

Hybrid participation support.\
Not just meetings. Support:

- async comment windows
- periodic live sessions
- pop-up outreach at vaccine clinics or waiting rooms
- targeted outreach through carers and community groups
- printable packs / poster QR codes / simple text shortlinks

This lines up with the regulator’s “accessible manner” language and with current local PPG toolkits that recommend virtual engagement, community organisations, social channels, questionnaires, events, and outreach methods beyond a meeting room. citeturn638723view0turn215213view4

Representation dashboard.\
The practice should be able to see whether the participation pool is missing groups it serves: younger adults, carers, people with limited English, digitally excluded patients, people in temporary housing, high-contact but low-response patients. Don’t overdo demographics, but enough to show whether the current PPG is just six articulate retirees.

Careflow-driven invitations.\
After someone completes a care interaction, you can ask a tiny service-design question later, not in the moment of illness. Not “rate your doctor”, more “did the appointment-booking process make sense?”, “was the reminder useful?”, “should this have been easier by phone / text / in person?”. That gives you service feedback tied to real journeys without poisoning the care experience.

Carer and proxy inclusion.\
Where appropriate, allow a carer or proxy to join participation activity separately from the patient’s clinical account. For deprived populations this matters a lot because the person managing the friction is often not the patient.

What I would not build:

No public forum.\
No open thread where patients argue with each other about individual cases. That becomes moderation hell, confidentiality risk, and a magnet for the loudest users.

No voting engine that binds practice decisions.\
The rules are about gathering views and agreeing improvements, not turning practice operations into a referendum. Use ranked priorities or sentiment summaries internally if you want, but keep ownership with the practice.

No direct handling of personal complaints inside PPG space.\
If a submission is really “my blood result was lost”, that should route into complaints, safety, admin recovery, or care follow-up, not a participation board. Several PPG guides make the same basic distinction: service improvement yes, individual medical issues and complaints no. citeturn638723view0turn837673search9

No giant “patient democracy” subsystem in your core domain.\
Keep a hard wall between:

- care episodes
- operational messaging
- patient participation

Shared identity, shared messaging, shared audit. Separate workflows, separate permissions, separate UI.

The product shape I’d use:

```text
/core-care
  episodes
  messaging
  tasks
  gp-adapters
  proxy

/participation
  membership
  consultations
  feedback
  moderation
  action-register
  representation
  publishing
```

The bridge between them is event-based and thin:

- care journey completed -> eligible for service-feedback ask
- repeated friction on same step -> suggest participation topic to practice owner
- practice launches consultation -> target cohorts via existing messaging layer
- participation finding approved -> publish improvement item / operational change note

That keeps the extra layer powerful without contaminating the main care engine.

If you want the sharpest version of this: don’t try to “build a better PPG”. Build a practice-owned participation system that can support a formal PPG, a virtual PPG, targeted mini-consultations, outreach to underrepresented groups, and a public improvement log. That fits the current rules better than the old “committee plus minutes” model anyway. citeturn215213view3turn638723view0

I can sketch the actual Node domain model for that next.


#### You:
who around the UK is trying to solve these same problems? (across the entire chat), I assume a bunch of devs/agencies are probably tryiNHS Notify itself is the national API for app, email, text and letter. Notice what is missing there: voice calls. If you want phone outreach, that is your own workflow and telephony layer, not something the national messaging service will do for young to cram 'AI' in the NHS (the government are spending like a billion quid on it), but I'd like to know what actual ongoing work here is known about.

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
I’m mapping this in two layers: actual product competitors or adjacent suppliers, and national NHS programmes that are moving the ground underneath them. The second group matters as much as the first, because half the “competition” is really infrastructure catching up.


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
Because your target stack is NHS login, the NHS App, the national messaging service and GP system pairings, the market that really matters is mostly **England**, not “the whole UK” in a generic sense. NHS login itself is for patients registered at a GP practice in England or receiving NHS services in England, and the national messaging service is explicitly an NHS England service. citeturn717390view3turn811253search1

The closest direct competitors today are the online-consultation and total-triage suppliers already live inside the NHS App: **Accurx Patient Triage, Anima, Patchs, eConsult/Web-GP, Rapid Health Smart Triage, iPlato MyGP Triage, Engage Consult, V-Consult, and Virtually Healthcare**. That is the visible front-door layer for “patient asks the practice for something online”. citeturn231314view0

Then there is the messaging and follow-up layer. The NHS App’s live messaging integrations in primary care include **Accurx, Anima, Patchs, iPLATO, MJOG, Hero Health, Abtrace, Engage Health, Liberate AI, Medlink and Appt Health**, with real-time read receipts listed for those integrations. Since January 2024 those app messaging integrations have been managed as part of the wider national messaging onboarding process, so this is not a side alley now; it is part of the main platform direction. citeturn231314view0

There are adjacent players too. **Patients Know Best** is the obvious one if you care about a broader patient portal, shared messaging, care plans, trackers and documents rather than just GP request intake. It is less “replace Patchs” and more “own the patient record / portal / care-plan relationship”. citeturn231314view0

On the AI side, the real work in general practice is not one giant national “AI GP” programme. It is lots of supplier-led products in a few repeating categories. An NHS England South East review published in October 2025 says it contacted **46 suppliers**, analysed **32 AI products**, and found strongest deployment in **triage and routing, ambient transcription, document automation, admin chatbots, and call/recall automation**. In that regional snapshot it counted **282 triage-and-routing deployments**, **222 ambient-scribe deployments**, and **192 automated letter-filing-and-coding deployments** across six integrated care boards. That is a real market, not hype, but the same report says only **13%** of tools were confirmed as implemented across multiple practices and most remained targeted rollouts or pilots. citeturn931111view0

If you want named examples from that report, the triage/routing bucket includes **Anima, Patchs AI Triage, Rapid Health, Klinik Access, eConsult + AI, InTouchNow AI Voice Receptionist and Voice Connect**. The ambient-scribe bucket includes **Accurx Scribe, Tortus, Heidi, Nabla and Medloop**. That is where most current “AI in primary care” energy is actually showing up. citeturn931111view0

National NHS work is also changing the ground underneath those suppliers. From **1 October 2025**, practices in England have had to keep online consultation tools open throughout core hours for at least non-urgent appointment requests, medication queries and admin requests, while patients must still be able to contact the practice by phone or by walking in. Integrated care boards are now expected to fund usable digital tools, including online consultation, appointment booking, messaging and demand/capacity tools, from core allocations. So the market is not shrinking; it has been baked harder into normal primary-care operating expectations. citeturn717390view0turn717390view1

The national platform work that matters most to your idea is not especially “AI” at all. The NHS App roadmap says NHS England is working with the national messaging service to increase message reads in the app. Current messaging guidance says NHS policy is app-first where possible, with routing plans that can fall back to text, email or letter, and it explicitly says digital-first is not digital-only. The national proxy service is still in rollout, but NHS England now says all proxy-access providers will have to comply with a new proxy standard in 2026 and that using the national proxy service to award proxy access will become mandatory for GP practices in England from 2027 when the national proxy data store is available. citeturn547119search1turn717390view2turn547119search2

On the “government is spending a billion quid on AI” point: that is broadly true in the sense that the UK compute roadmap commits **over £1 billion** to expand the national AI research resource and **up to £2 billion** for the wider public compute ecosystem, but that is not the same as “a billion is being spent on GP access products”. The more concrete NHS-wide AI move you can point to right now is the **January 2026** national registry of **19** ambient note-taking suppliers, plus the diagnostic fund work in imaging. That is real central backing, but it is backing documentation and diagnostics much more clearly than the kind of proactive patient-support system you are describing. citeturn717390view5turn717390view4turn649192search0

So the honest competitive picture is this. The crowded bits are **intake, triage, messaging shells, document handling and note-taking**. The less-crowded bit, at least visibly, is the thing you actually care about: **persistent follow-up to closure, proxy-aware outreach, multilingual / deprivation-aware contactability logic, and automatic escalation from unread or ignored digital contact into prioritised human work and face-to-face recovery**. That is not absent from the market, but it is not what the market is mostly optimising for. That conclusion is an inference from where the live integrations and AI deployments are concentrated today. citeturn231314view0turn931111view0turn717390view2

If you want, I’ll do the next cut as a sharper map: **incumbents, adjacent players, likely acquirers/partners, and where your product could be 10x better instead of just “another online consultation tool.”**


#### You:
looking not just to technical solutions, but how do _good_ practices and groups manage this aside from software-tool solutions? All practices/doctors/unions complain about mundane work eating up clinical/care time, but often neglect that mundane work IS care time, because it's mundane interactions that catch problems before they become unfixable. Do better practices actively understand and communicate with their patients better? what systems do they use that _do_ improve otcomes that GTD just can't afford as a social-enterprisie constantly on the edge of poverty themselves. 

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
I’m checking this as practice design and evidence, not just software. The useful cut here is: what high-performing GP organisations actually do with people, roles, routines and outreach, and which of those are cheap enough to matter for a stretched provider.


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
Yes. The better practices are usually better at **organising care around relationships, follow-through and outreach**, not just faster at processing demand.

The strongest pattern is continuity. NHS England’s patient-safety work says continuity improves trust and understanding, can reduce appointments for frequent consulters, and can avoid hospital admission. The college guidance is even blunter: continuity is linked with better outcomes, higher satisfaction, better preventive care, lower admissions and lower overall cost. So the good practices do not treat every contact as an isolated ticket; they deliberately preserve continuity for the people who most need it. citeturn221131view0turn129488view0

That means they usually have some version of this operating model:
a small set of patients are recognised as needing relationship-based care, staff know who those patients are, front-desk staff are trained to route them safely, and the practice protects some continuity rather than maximising interchangeable throughput. NHS England’s current care-navigation guidance explicitly says all staff should be trained for consistent care navigation, and the college guidance says reception and other non-clinical staff are part of continuity, not separate from it. citeturn129488view1turn129488view0

The other big pattern is proactive caseload work. Better places do not wait for the same vulnerable people to keep bouncing in. NHS England has built formal roles around this: care coordinators, social prescribing link workers and health and wellbeing coaches working with multidisciplinary teams, especially for people at risk of unplanned admission because of psychosocial need. The national guidance frames this as proactive, personalised care, not admin. citeturn221131view2turn221131view1

Some of that is not supposed to come out of a single practice’s own pocket. In England, primary care networks can reclaim salaries and some on-costs for 17 additional roles, and the national workforce pot for 2025/26 is about £1.71 billion. So part of the answer to “what can a stretched organisation not afford?” is: some of the better systems are meant to be funded at network level, not by an individual practice or social enterprise trying to do everything alone. citeturn221131view3turn221131view4

Where the better places differ culturally is that they treat access and admin as part of care delivery. NHS England’s access plan now says patients should not be told to call back another day, and they should know on the day how their request will be handled. The telephony guidance says phone and online journeys should integrate with care navigation and admin processes. In other words, the phone queue, receptionist script, callback discipline and follow-up list are not overhead; they are the front edge of clinical safety. citeturn129488view2turn129488view4

For deprived populations, the practices that do better usually go beyond the building. The national inclusion-health framework says poor experiences are often created by service design, which then leads people to avoid future care. Its practical advice is cross-sector partnership, trauma-informed working, co-design with lived experience, better local insight, and making sure navigators, care coordinators and link workers are actually available. That is much closer to your instinct than the usual “put up a website and wait”. citeturn221131view6

There are concrete UK models behind this. The Bromley by Bow model is the classic one: primary care working alongside public health, social care and non-clinical community support, built around local community needs rather than forcing people to fit a narrow medical pathway. The message from that case is not “buy a fancy tool”; it is “join up care, social support and community relationships around the person”. citeturn221131view7

There is also a deprivation-specific lesson. The Royal College has been arguing this year for ring-fenced support for “Deep End” practices and projects in poorer areas, precisely because workforce shortages and need are worse there. That is basically an official admission that the standard model under-serves deprived communities unless you fund extra structure around them. citeturn221131view5

So, what actually improves outcomes aside from software?

Protected continuity for the patients who are complex, vulnerable, traumatised, or repeatedly reattending. That is low-tech and high-value. citeturn129488view0turn221131view0

Named proactive roles for people who fall through the cracks: care coordinators, link workers, coaches, pharmacists, mental health workers. Those roles exist because a lot of “mundane” repeat demand is really unmet coordination, social need, medication confusion or inability to navigate the system. citeturn221131view2turn221131view3

Deliberate multidisciplinary review for the highest-need cohorts. The Fuller stocktake gives examples of anticipatory care where frail patients get holistic assessment, multidisciplinary review and interventions like medication review, falls prevention, nutrition advice, social prescribing and referrals into community and voluntary support, all documented in a shared record. citeturn129488view8

Good telephone and walk-in handling, not just digital front doors. NHS England’s own modern-general-practice guidance treats telephony as a core enabler, and the access plan still requires same-day handling for urgent need and a clear management plan for everyone else. citeturn129488view2turn129488view4

Working with trusted community organisations and lived-experience groups, especially where language, housing, migration status, trauma or distrust make normal practice access fail. The inclusion-health framework is explicit that services should use trusted community partners and co-design, not just routine datasets. citeturn221131view6

What GTD probably cannot easily afford on its own is not the idea, but the slack. Continuity needs protected appointment design. Proactive outreach needs people with caseload headroom. Community-facing work needs partnerships and time. A community-hub model like Bromley by Bow is not cheap to replicate. Deep deprivation work generally needs more staff time per patient, not less. citeturn221131view7turn221131view5

What *is* relatively affordable is the operating discipline:

make a high-risk / high-need register,\
protect continuity for that group,\
train all front-desk staff in safe navigation,\
run callback / no-response / no-read lists every day,\
use network-funded coordinator or link-worker roles where available,\
track whether people were actually reached, not just whether a message was sent,\
and publish a small “you said / we changed” loop so the practice learns from repeated friction. Those moves are much cheaper than building a whole extra service line, and they line up with national guidance rather than fighting it. citeturn129488view1turn221131view2turn221131view6

So yes, the better places do actively understand and communicate with their patients better. But the mechanism is not “nicer doctors” or “more AI”. It is boring, intentional practice design: continuity, trained navigation, proactive caseloads, strong phone handling, community links, and a willingness to count follow-through as clinical work rather than as admin clutter. citeturn221131view0turn129488view0turn221131view6

If you want, I can turn that into a product strategy matrix: which parts software can genuinely automate, which parts need funded human roles, and which parts are really contract / commissioning problems rather than engineering.


#### You:
How much is the typical practice (and/or a distribution across real practices) actually pay for the use of the available tools you mentioned (Accurx Patient Triage, Anima, Patchs, eConsult/Web-GP, Rapid Health Smart Triage, iPlato MyGP Triage, Engage Consult, V-Consult, and Virtually Healthcare, Accurx, Anima, Patchs, iPLATO, MJOG, Hero Health, Abtrace, Engage Health, Liberate AI, Medlink and Appt Health,Patients Know Best. and so on, basically anyone who interacts with the space we're talking about)? 

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
I’m checking public list prices, framework catalogue entries, and tender/award records. A lot of this market hides pricing behind sales calls, so the useful answer is usually “public list”, “known NHS contract”, and “what that implies per practice / per patient”, not a single neat sticker price.


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
There’s a pretty hard split emerging already: some products have usable public list prices on Digital Marketplace, others only leak through regional awards or framework docs. The other big thing is that a lot of practices don’t buy these directly at all; an integrated care board or similar body buys on their behalf, so “practice price” and “contract value” are often different numbers.


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


#### You:
"An NHS England South East review published in October 2025 says it contacted 46 suppliers, analysed 32 AI products, and found strongest deployment in triage and routing, ambient transcription, document automation, admin chatbots, and call/recall automation. In that regional snapshot it counted 282 triage-and-routing deployments, 222 ambient-scribe deployments, and 192 automated letter-filing-and-coding deployments across six integrated care boards" I'd like the full details on who is doing what in that entire group. They look to have the tech, but everyone's focussing on making it patient-facing (put the AI 'between' the patient and the doctor, which seems insane to me. The AI should be a facilitator, an assistant, not a wall the patient has to try and get through (let's not make this like the silent-rejection of AI-based job boards). 13% implemented across multiple practices needs context, mainly of what that is a percentage, lol. Are any of these tools open-source? I'd rather ship as open-source but plug-in your own api keys, than manage it for practcies (I actively don't want to get paid, which I know is going to make 'appearing like a real business' seem hard) so i also wonder about the common use of open-source (but from outside the org) in the nhs. Seems sparse

#### ChatGPT:
I’m pulling the South East review itself and the bits that matter: the actual vendor list by function, what “13% implemented across multiple practices” is a percentage of, and whether any of the primary-care tools in that scan are open-source or just “AI vendor + private SaaS”.


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


#### You:
"where our product could be 10x better instead of just “another online consultation tool." is important, but we have to be wary, GPs don't like change, and do FEAR _more work_, so we need to be very clear that radical support shouldn't be expensive (time or money), and comparing the cost of our radical approach (active pursuit, not just passive form routing and shitty but slightly customisable forms, but custom-per-patient inputs/routing as determined by our complex system). 

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


#### You:
ah, our practice just got a "social prescriber"... Are you saying part of their role is 'managing difficult patients'? (briefly) "unplanned admission because of psychosocial need" is doublespeak for "they might suddenly kill themselves or turn up pissed and violent?". So the practice hiring a social prescriber is kinda like a national safety valve where central pays a little to help deal with complex patients? Is that about a right way of lookin at it?

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
Roughly yes, but not “managing difficult patients” in the crude sense.

The role is closer to: dealing with the non-medical stuff that keeps turning into medical demand. NHS England describes social prescribing link workers as people who work on “what matters to me”, helping with practical, social and emotional needs, and connecting people to community, welfare, debt, housing and other support that affects health. They are meant especially for people with long-term conditions, low-level mental health issues, loneliness, isolation, or complex social needs. citeturn874613view4turn857504search6

And yes, the “unplanned admission because of psychosocial need” language is basically about people whose risk is being driven by things like poverty, chaos, addiction, isolation, mental distress, inability to cope, or repeated crisis use of services. NHS England’s own guidance says these roles are part of proactive support for people at higher risk of hospital admission due to psychosocial needs, and that the point is to reduce avoidable urgent use by addressing wider social, practical and financial problems earlier. citeturn874613view2

So your framing is mostly right: it is a centrally supported pressure-release role. These link workers sit in primary care networks as part of the Additional Roles Reimbursement Scheme, which is national money for extra non-GP roles. The idea is to buy a bit of capacity outside the classic GP appointment model so practices are not trying to solve every social crisis inside a 10-minute clinical slot. citeturn874613view3turn874613view2

What it is not supposed to mean is “we hired someone to handle violent or suicidal patients instead of clinicians”. Those people still need proper clinical, safeguarding, mental health, crisis or security responses. The social prescriber is the person for the adjacent mess that keeps making people unwell or repeatedly crashing into the practice. citeturn874613view2turn874613view4


#### You:
"The national inclusion-health framework says poor experiences are often created by service design, which then leads people to avoid future care." more on this would be useful to me. Facts and citations please.

"The Bromley by Bow model" sounds like wider community engagement. Just a thought, what about making another role in the system for community figures. This might be drug response or homeless shelter admins, who can use the platform for some shared admin/outreach. I think our practice only really works with the library, but it's worth considering for a future feature for practices who do have more sophisticated social (to the admin layer, not to the crowd layer) or business links  that this could potentially facilitate for some.

in "The Royal College has been arguing this year for ring-fenced support for “Deep End” practices and projects in poorer areas, precisely because workforce shortages and need are worse there." this means money for practices, right? Anyone actually seeing that in reality or is it just an academic paper?

"Continuity" keeps coming up, how much do practices actually value it, or is it like a 'nice to have'. I feel like GTD don't value continuity at all, because their system expects the worst possible input at any point, it's intentionally frictioned/frictionful.

Then go back to software pricing. You said it's "often different numbers", but get me a ballpark for these paid tools, and find any open source alternatives that are in service.

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
I’m pulling this in three chunks so it stays grounded: inclusion-health and continuity from official guidance, whether “Deep End” money is real or mostly rhetoric, then current pricing and any credible open-source angle.


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
I’ve got enough to answer this cleanly: inclusion-health and continuity are well-evidenced; “Deep End” money is real in Scotland and much fuzzier in England; pricing is partly public, partly buried in procurement docs. The open-source picture is basically “encouraged in policy, sparse in this exact product niche.”


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
On inclusion health, the important point is not just “some patients have extra needs”. The national framework says people in inclusion-health groups often get **poor experiences because of barriers created by service design**, and those bad experiences can make them **avoid future NHS contact**, which then drives worse outcomes and earlier death. It also says services should not rely only on routine data; they should use trusted community partners, voluntary groups and lived-experience input to understand why people are falling out of care. citeturn265894search0turn245906view0turn245906view1

That is not abstract. The same framework gives local examples where practices and systems found barriers like poor understanding of how to access care, misinformation, language and technology barriers, poor trust, weak transparency, and broader mental-health or health-literacy problems. The response was not “launch another form”. It was outreach through trusted community sources, targeted access changes, and practical interventions like alternative clinics and direct call-based follow-up. citeturn245906view2

So yes, a tightly-scoped **community partner role** in your platform makes sense. Not a public-facing “crowd” feature, and not a free-for-all record viewer. More like: approved partner users from a homeless service, drug service, refuge, library, community hub or shelter can receive narrowly-scoped outreach/admin tasks, confirm contact, help arrange attendance, or flag practical barriers. That is very close to current inclusion-health thinking, which explicitly pushes trusted community partners and voluntary-sector organisations into co-design and delivery. citeturn245906view0turn245906view1

I would keep that role extremely constrained:
patient-consented or explicitly lawful basis only,\
episode-scoped access,\
no general record browsing,\
no clinical decision rights,\
full audit trail,\
clear separation between “helped contact / helped attend / helped support” and actual care decisions.\
That is product advice rather than a published standard, but it lines up with the policy direction above.

On “Deep End” support: yes, that means **money or ring-fenced resource for practices serving poorer populations**. But the reality is uneven. In **Scotland**, this is real enough to point to actual funding lines: the Scottish Government said it is funding the Scottish Deep End Project with **£124,371 in 2025–26**, and separate Deep End-linked work such as Family Wellbeing Workers in 12 Deep End practices has also been funded. Scotland has also rolled out community link workers at scale, with more than 300 reported, backed through primary-care improvement funding. citeturn756016search2turn756016search11turn756016search17turn756016search8

In **England**, it is much less clean. The Royal College’s line this year is still an argument that governments should commit ring-fenced funding for Deep End practices and projects. That is advocacy, not proof that England has already built a national Deep End funding stream. What England does have is broader primary-care investment and a funding-formula review explicitly expected to address inequalities, but that is not the same as a named, ring-fenced Deep End pot landing on practices today. citeturn756016search4turn756016search9turn894588search5

On continuity: it is not a fluffy “nice to have”. The evidence base and official strategy both treat it as a real safety and outcomes issue. NHS England’s patient-safety work says continuity improves trust and understanding and, for people with repeated consultations, could save about **5.2% of GP appointments** and avoid hospital admission. The Royal College says continuity is linked with better outcomes, higher satisfaction, better preventive care, lower admissions, lower cost, and even mortality effects. citeturn265894search2turn382095search2

But in practice, continuity is often **valued in principle and traded away operationally**. The Health Foundation said continuity is valued by patients and GPs alike, yet appears to be in decline in England; it fell steadily from April 2018 to September 2020 before some recovery. The safety investigation into online consultation also found that badly designed digital access can create inequitable access, mislead patients about how to get care, and make holistic care harder. So the real picture is: continuity is strongly valued in evidence and policy, but a lot of operational models optimise speed, queue handling and generic intake instead. citeturn382095search11turn382095search3turn396619view0

I cannot tell you GTD’s internal attitude from the outside. I can say this: systems built around worst-case generic input, pooled routing and heavily standardised intake usually weaken continuity unless they deliberately add it back in.

On software pricing, the biggest thing to know is that a **practice often is not the direct buyer**. From 2025/26, integrated care boards are expected to fund online consultation, booking, messaging and similar digital tools from core allocations, so the sticker price, the framework price and the effective practice cost are often different. citeturn186286search5turn186286search13

Public ballparks from current public procurement listings and pricing docs look like this.

**Accurx** has unusually visible pricing. On the current cloud framework, its general-practice toolkit sits around **£0.53 / £0.85 / £1.07 per patient per year** for bronze / silver / gold at the smallest size band, with cheaper rates at larger scale; a 10,000-patient practice is roughly **£5.3k / £8.5k / £10.7k per year** on those list prices. Individual modules sit lower, for example online consultation around **£0.30 per patient**, two-way messaging around **£0.27**, questionnaires around **£0.21**. citeturn776379view3

**Patchs** is publicly listed at about **£0.90 per patient per year** at the smaller population band, dropping to **£0.70** and then **£0.45** at larger scales, plus some training extras and a minimum 36-month term. That makes a 10,000-patient practice roughly **£9k a year** on list price. citeturn551571view1

**eConsult / WebGP** shows a public framework price around **£0.29 to £0.35 per licence**; in practice people usually read that as roughly **£2.9k–£3.5k a year** for a 10,000-patient practice, though the public page is less explicit than some others. citeturn448575view0

**iPLATO MyGP Triage** shows **£0.10 to £0.20 per person per year**, so roughly **£1k–£2k a year** for 10,000 patients on the public listing. citeturn790525view0

**Hero Health** has a public pricing snippet at about **£0.50 per patient per year plus SMS costs**, so roughly **£5k a year plus messaging** for 10,000 patients. citeturn519282view1turn151422search2

**Abtrace**’s proactive monitoring/CDSS pricing is public at **£0.66 per patient per year**, with stated discounts at network/system level, so roughly **£6.6k a year** for 10,000 patients before those discounts. citeturn551571view3turn886211view8

**MedLink**’s published tier mentions **11 pence per patient** for the smallest tier under 30,000 patients, which is roughly **£1.1k a year** for 10,000 patients if that tier applies. citeturn429092search3

**Patients Know Best** is not really a small per-practice triage tool price. Its public cloud-framework pricing is more like a service/department licence starting around **£35,459 a year** for the first department or service, then lower for additional ones. citeturn187884search3turn551571view2

**C the Signs** is public at around **£0.20 to £0.33 per unit per year**. It is not the same product category as Patchs, but it lives in the same broader primary-care tooling economy. citeturn519282view0

For several others you named, I did **not** find a clean public list price in current public sources that I would trust enough to quote as fact: **Anima, Rapid Health, MJOG, Appt Health, Engage Consult, Virtually Healthcare, Liberate AI**. Some of them appear in public product listings, tenders or regional deployment docs, but not with a straightforward public price I’d stand behind. The absence of a clean public price is itself normal in this market. citeturn770836view0turn886211view1

The practical ballpark, then, is that a lot of these tools are roughly **10 pence to £1 per patient per year**, with some broader portal/platform products sitting far above that. So for a normal 8k–15k practice, a lot of the market lands somewhere from **low thousands to low tens of thousands per year**, depending on feature bundle, scale and who is doing the buying. citeturn776379view3turn551571view1turn790525view0turn551571view3

On open source: the NHS line on principle is actually favourable. The service standard says new code should be open and reusable unless there is a good reason not to, and NHS developer docs point to public repositories for a number of newer national services and components. So “open source from outside the organisation” is not alien to the NHS. citeturn984862search2turn984862search15

But in the exact niche you care about — GP front door, patient-to-practice workflow, messaging, login, triage/follow-up — I could **not** find a credible mature open-source product in active NHS service that is the equivalent of Patchs / Accurx triage / eConsult. The live market there is overwhelmingly private SaaS. That is the sparse bit you are noticing. citeturn984862search2turn448575view0turn551571view1turn776379view3

There **are** NHS-used open-source systems, just mostly in other parts of the stack. **OpenEyes** is an open-source ophthalmology record system used in live NHS settings, including national eyecare work in Scotland. **OpenSAFELY** is open-source and heavily used for NHS-scale analytics and research, though it is not a patient-facing workflow product. So the NHS absolutely can use outside open source in serious service, just not much in the exact primary-care patient-engagement category you are targeting. citeturn842518search0turn842518search10turn842518search1turn842518search4

The gap is real: policy likes open code, real NHS usage includes some major open-source systems, but the patient-front-door primary-care market is still mostly proprietary vendor software.

If you want the next useful cut, I’d do two things together: a price-and-feature map of the named vendors, and a design for an open-source deployment model that still looks “real enough” for NHS buyers.


#### You:
let's also consider the 'education' aspect of how deprivation affects healthcare outcomes... like a poor & undereducated person doesn't necessarily know what a social prescriber is, or even to ask for one. I'm sure the same is also obvious from many others. Like at my practice, I know they have one, and there is a form fielf where in theory I could ask for one, but I'd have to know to ask that. Our platform should probably visualise/surface what help is actually available, and make that like role-first (and even goal-first, that cover multipel roles) process-starts, so we actually tell patients what help/who is even available before they even ask for help, so they a) know they exist and b) can immediately ask for them (that role's handlers can of course retask as/if needed). You make a good point of not being able to "solve every social crisis inside a 10-minute clinical slot" so our system should allow for a lot more outcomes than just "here's your slot, come back then and maybe we'll listen for a couple of minutes while we're actually hurrying your obvious low-risk (or not high risk yet) needs to get to the next appointment slot"

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
I’m checking the current official role mix and access guidance so this doesn’t turn into hand-wavy UX chat. Then I’ll turn it into a concrete product pattern: role-first and goal-first entry points, but without becoming a confusing directory.


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
Yes. This is exactly one of the places the product can be **materially better** than current GP front doors.

The official direction already supports it. NHS England says there are three personalised-care roles in primary care networks: **care coordinators, health and wellbeing coaches, and social prescribing link workers**. Care coordinators help patients prepare for and follow up clinical conversations and manage a caseload; health and wellbeing coaches help people build skills, confidence and behaviour change around health goals; social prescribing link workers connect people to community groups and practical and emotional support. ([england.nhs.uk](https://www.england.nhs.uk/gp/expanding-our-workforce/)) NHS England also says **20% of GP consultations are for problems that are non-clinical or social in nature**, and that it is expanding self-referral routes for some services instead of forcing everything through a GP appointment first. citeturn802495view3turn895297search17

So the patient should **not** have to know the job title. That is bad service design.

The system should be goal-first, not role-first internally, but role-aware underneath. The patient sees things like:

- I need help with stress, loneliness, debt, housing, benefits, caring, or getting support
- I want help sticking to a plan, changing habits, or managing a long-term condition
- I keep getting lost between services / appointments / medicines
- I need a clinician
- I need something practical: fit note, prescription issue, test result follow-up, referral chase
- I need this in another language / easier format / with a carer

Then, after the patient picks a goal, the platform says **who can help with this here**, in plain English, with a real action at the end. Not a dead glossary.

That matches current NHS access thinking. NHS England’s care-navigation guidance is explicitly about getting people to the **right person first time**, making better use of the wider team, and helping practices integrate online consultation, messaging and booking into one workflow. citeturn802495view2

So I’d model it like this:

```ts
type HelpOffer = {
  id: string
  practiceId: string
  name: string // "Help with money, housing, loneliness or support"
  internalRole: 
    | "social_prescribing_link_worker"
    | "care_coordinator"
    | "health_and_wellbeing_coach"
    | "gp"
    | "nurse"
    | "pharmacist"
    | "community_partner"
    | "admin"
  goals: string[]
  eligibilityRules: Rule[]
  route:
    | { kind: "self_referral"; endpoint: string }
    | { kind: "practice_task"; queue: string }
    | { kind: "book_slot"; slotType: string }
    | { kind: "message_team"; templateId: string }
    | { kind: "community_handoff"; partnerId: string }
  patientCopy: {
    title: string
    description: string
    what_happens_next: string
    when_to_use: string[]
    when_not_to_use: string[]
  }
  accessibility: {
    languages: string[]
    easyRead: boolean
    interpreterSupported: boolean
    proxyAllowed: boolean
  }
}
```

That lets each practice or network define its real local help landscape without forcing patients to decode NHS org charts.

The other big thing is **communication support**. NHS England’s accessible information standard requires services to identify, record, flag, share, meet and review people’s information and communication needs, including needs of families and carers involved in care. citeturn802495view4turn895297search18 And the GP website guidance is pretty blunt: write in plain English, use short words and paragraphs, avoid jargon, prefer HTML over PDFs, and aim for roughly a **9 to 11** reading age. citeturn802495view5

So this should be in the platform, not left to chance:

- preferred language
- interpreter needed
- easy-read / low-literacy mode
- proxy / carer involvement
- phone-first / text-first / letter-only / app-capable
- homelessness / unstable address / no private phone / no email
- community-partner-supported contact, where lawful and consented

That profile should then affect every journey automatically. Same task, different wording and channel.

The important design move is: **do not build a directory**. Build an **actionable offer layer**.

Bad:
“Social prescribing link worker available.”

Good:
“Need help with debt, housing, benefits, loneliness, carers, or practical support? We can connect you with someone who helps with that. You usually do not need a doctor first.”

Bad:
“Health and wellbeing coach.”

Good:
“Want support changing habits, sticking to a plan, losing weight, becoming more active, or managing stress? Someone here can work with you over a few sessions.”

If a service supports direct access, surface it directly. NHS England is explicitly expanding self-referral for selected services like musculoskeletal care, audiology for older people, weight management, podiatry, and wheelchair / community equipment services. citeturn802495view3turn895297search2 So your engine should know whether the best next step is:

- self-refer now
- ask the practice to connect me
- book with a clinician
- send to community pharmacy first
- create a care-coordinator task
- ask a social prescriber / coach / pharmacist
- request a face-to-face call-back because digital won’t work here

That last point matters. The platform should support many more outcomes than “book GP slot”:

```ts
type EpisodeOutcome =
  | "booked_gp"
  | "booked_nurse"
  | "sent_to_pharmacy_first"
  | "self_referred"
  | "sent_to_social_prescribing"
  | "sent_to_health_coach"
  | "sent_to_care_coordinator"
  | "community_partner_outreach"
  | "awaiting_manual_call"
  | "proxy_contacted"
  | "face_to_face_support_needed"
  | "monitoring_path_started"
  | "admin_resolved"
  | "urgent_escalation"
```

That is where the system starts to reduce pointless GP demand without turning into an obstruction layer.

The community-partner idea is good, but only as a later, tightly-scoped admin feature. A library, shelter, drug service, refugee support hub, or housing worker could be a **community partner** with very limited powers: confirm contact, help a person complete a step, help arrange attendance, receive outreach tasks, or flag “this person is hard to reach / needs in-person help”. Not general record access, not clinical routing authority. That lines up with the inclusion-health direction of using trusted community partners to improve access. citeturn802495view4turn895297search2

So the core product idea here is strong:

patients should not need to know what services exist,\
the system should tell them what help exists in their practice or network,\
in language they can understand,\
with the right communication support already applied,\
and with a real next step that reaches the right role first time.

That is better for deprived patients, and it is also more acceptable to practices because it shifts work to the wider team instead of dumping everything into GP appointments.

The simplest version of this to ship first would be a **local help graph** per practice/network plus a **goal-to-route engine**. That alone would be a big step up from today’s “choose from a generic form and hope”.

I can sketch the actual Node schema and routing logic for that layer next.


#### You:
"the Scottish Government said it is funding the Scottish Deep End Project with £124,371 in 2025–26" that's fuck all, literally. I suspect you've irrelevantly imported this issue and made a biggger deal of it than is necessary. Either get it right or leave it a footnote.

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
You’re right to push back. That specific Scottish figure is tiny and, on its own, not evidence of meaningful system support. I’m checking the distinction between “funding a project/network” and “funding extra capacity in practices”, because those are completely different claims.


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
You’re right. I overstated that point.

That **£124,371** is funding for the **Scottish Deep End Project** itself in **2025–26**. It is not meaningful operating money for deprived practices at system scale, and it should have been treated as a footnote, not evidence that “Deep End funding” is a serious answer to the problem. citeturn306931search0

The more relevant distinction is:

- **project / network funding**: tiny, symbolic, supports meetings, advocacy, shared work
- **practice capacity funding**: actual extra people or protected time inside practices

I blurred those. You were right to call it out.

Where Scotland has had more material support, it has been through things like **community link workers** and specific inequality programmes, not that £124k line. Scottish Government documents describe a rollout from **51 to 189 community link workers** by March 2021, and earlier commitments talked about recruiting **at least 250** link workers into GP surgeries. Scotland has also funded **Inclusion Health Action in General Practice**, where individual practices in very deprived areas got funding for specific work. Those are much more relevant than the Deep End project grant. citeturn261943search2turn261943search6turn261943search9

For **England**, the important correction is even simpler: “ring-fenced support for Deep End practices” is mostly still **an advocacy ask**, not a well-established national funding stream. The Royal College is arguing for it; that is not the same thing as practices already seeing a dedicated Deep End pot in routine reality. citeturn306931search1turn306931search6

So the clean version is:

Deep End is worth knowing about as a **policy and organising idea** around deprivation.\
It is **not** something I should have presented as a major live funding answer for your problem.\
For your purposes, it belongs as a footnote unless we are specifically talking about deprivation-policy history.

That was a fair correction.


#### You:
"good continuity saves 5.2% of appointments" is a soft claim that needs thorough follow-up, but I'm interested in finding out more about that. "continuity is often valued in principle and traded away operationally" is an important perspective because at new bank/gtd, we're saying "you think website-only access is solving a problem, but it's actually making it worse"

```I cannot tell you GTD’s internal attitude from the outside. I can say this: systems built around worst-case generic input, pooled routing and heavily standardised intake usually weaken continuity unless they deliberately add it back in.``` can we find case studies (or even mainstream reporting) of other practices or groups or authorities/etc who have done/tried this, and use their outcomes to shine a light on our outcomes?


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
I’m pulling three things: where that 5.2% number actually comes from, what evidence exists that pooled digital intake/total triage can weaken continuity or worsen access, and concrete practice/system examples rather than just theory.


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
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
Yes. There is enough out there to make this argument properly, and the evidence is better than “patients like seeing the same doctor”.

The 5.2% figure is real, but it is narrower than the slogan. It comes from a peer-reviewed study in *Management Science* using more than 10 million **face-to-face GP consultations** across **381 English practices** over **2007–2017**. The authors found that when patients saw their regular doctor, the interval to the next consultation was longer, and they modelled that if all practices had offered **well-targeted continuity** at a level similar to the top decile, overall consultation demand in that sample would have been **5.2% lower**. They also say that should be read as an **upper bound**, because real practices have trade-offs and spillovers the model cannot fully capture. So it is not “continuity always saves 5.2%”; it is “there is credible large-scale evidence that continuity can cut repeat demand, especially for patients who consult often.” citeturn176627search0turn720312view4

The wider continuity evidence is stronger than that one number. An East London study covering **126 practices** found average measured continuity was only **0.52** on the usual-provider index, with **larger practices showing lower continuity**, and it notes continuity in England had already been declining, with lower levels in **urban and deprived populations**. The Care Quality Commission’s 2025 readout of the GP Patient Survey adds that continuity is still not normal in practice: among patients with a preferred professional, **43%** said they only got them **“sometimes”**, **18%** said **“never”** or **“almost never”**, and people in the **most deprived areas** were less likely than those in the **least deprived areas** to get their preferred professional often (**36% vs 43%**). citeturn904499view1turn705507view1

On your actual concern — website-first, pooled, standardised intake weakening care — the evidence is very much not imaginary. The 2024 safety investigation into online consultation tools found that while these tools can help access and demand management, they also contributed to patient-safety incidents; harm can occur when patients cannot use them because of their personal circumstances; practices may not understand their population’s digital capability; some practices cap daily online requests to protect safety; and there are concerns that an online-consultation model can reduce opportunities for **holistic care**, **health promotion**, and **long-term condition management**. That is very close to your “you think this solves access, but it may be making care worse” point. citeturn720312view0

There is a second, even sharper safety finding. The 2023 continuity investigation found that **many practices do not operate a formal continuity system**, there is **no standard framework** for doing it, and GP IT does not have to **surface repeated unresolving symptoms** to the next clinician. The same report says practices that *did* have a continuity system reported more time to process information and carry out follow-on actions, plus **better staff welfare and retention** and fewer recruitment problems. That is a very direct rebuttal to the idea that continuity is just a luxury add-on. citeturn426909search0turn426909search2

The most useful case studies are the ones that did **not** go “website-only”. The Nuffield Trust’s own examples of large-scale access models all keep continuity carve-outs. AT Group’s digital hub still had about **50%** of consultations requested **online** and **50% by phone or in person**; if continuity was needed, appointments could be booked with the patient’s **usual GP**, and patients with ongoing or complex problems could be routed back to that usual GP. St Austell split **acute care** from **continuity care** and had reception allocate according to **need, not demand**, with complex patients steered back to their usual clinician where possible. Quay Health Solutions only used its extended hub for patients booked there **after clinician triage from their own practice**, and explicitly set it up for **minor acute illness** so the patient’s own GP could focus on **complex ongoing problems**. In other words, even the “modern access” exemplars are not pure pooled-routing systems; they all preserve continuity deliberately. citeturn685668view0

That is also the policy trajectory now. Older access policy was much more visibly about access than continuity; Nuffield noted that plainly in 2018. More recently, the contract direction has started to move: the 2025–26 changes encouraged practices to identify patients who would benefit most from continuity, and the 2026–27 contract makes it a **core requirement** for primary care networks to identify and prioritise **risk-stratified cohorts** for continuity of care. So the official system is slowly admitting that “fastest route for everyone” is not enough. citeturn720312view3turn520105search10turn520105search5

There is also a really practical deprivation angle. In the 2025 GP Patient Survey, only **53%** of respondents who tried calling their GP said it was easy; **22%** said they either could not contact the practice or did not know what the next step would be; and **6.6%** of that group went to **A\&E** instead, rising to **8%** for people in the **most deprived areas**. So if a practice is making contact more abstract, more pooled, or less legible, the cost is not just annoyance. It leaks into urgent care, and it does so more for deprived groups. citeturn705507view1

So yes, you can absolutely use external evidence to shine a light on what is happening locally. The fairest way is not to scream “Patchs bad” in the abstract. It is to ask whether New Bank/GTD looks more like the **safety concerns** and **discontinuity patterns** in the HSSIB/CQC work, or more like the **blended models with explicit continuity protection** in the Nuffield case studies. citeturn720312view0turn426909search0turn685668view0turn705507view1

The local scorecard I’d use is:

Does the practice still preserve meaningful **phone and walk-in** routes, or is digital acting as a gate?\
Can people with repeat, complex, mental-health, frailty, or unresolved issues be routed to a **known clinician**, or are they re-pooled each time?\
What share of contacts end with “patient did not know next step” or “try again tomorrow”?\
How often do repeat contacts for the **same unresolved issue** land with different clinicians and no surfacing?\
What is the local rate of seeing a **preferred professional**, especially in deprived groups?\
How many online requests become avoidable rework because the first step collected the wrong information or lost context?

That is the comparison that matters. Not “do they have a website”, but “did the operating model preserve continuity, alternatives, and follow-through”.

If you want, I’ll turn that into a one-page evaluation framework you could actually apply to GTD/New Bank: external benchmark, local data request, and what outcomes would count as “this access model is harming continuity”.


#### You:
on the competing software platforms (accurx, etc), we should put togtehr a dataset to compare their cost to their quality. Not entirely sure where we find reviews for that, but I know trustpilot has a LOT of reviews for PATCHS, so put togther a sources list that might be useful to inform "how good are the existing tools, really?" question. New bank moved from eConsult to Patchs under the new management but GTD staff have mentioned being on accurx too (I think it's one of the routes on the pateint website), so is a hyrbid mix of platfroms (or all of them) a common experience for practice staff, like lots of competing systems or do they work together well? What's this ux like for staff?

Pricing and feature lists would be useful.

The per-patient cost on existing tools is highly variable across the market, so presumably it's more about "the platform you have" rather than the platform you necessarily want. If I was shipping this to actually help, a per-patient cost model makes zero sense, because digital scale isn't linear (you can even see it in how some offer bulk pricing where it's cheaper for more patients, and others offer bulk surcharges, where to satisfy more patients cost you more). Data/storage/workflow is basically free to service now, in infrastructure at least... it's 'cycles' that became expensive. Open source can do that, but it's onboously not a pattern in nhs to adopt open source, so it's probably got a management wall (I had a similar discussion when I worked for NICE, and they were NOT open to it at all, except in the principle of nodding heads in a meeting of managers, then ignoring what technical staff tried to do, instead paying contracts to consultants and contractors so they didn't have to make real long-term decisions).

Note to look into OpenEyes and OpenSAFELY don't seem very relevant, but I'll have a look. "mostly proprietary vendor software" is absolutely atrocious situation for a publicly owned institution like the NHS to have not even tried to do OPEN open front doors, if you'll pardon the pun ;)



#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
I’m gathering this as a comparison pack rather than a random vendor list: public review sources, staff-experience evidence, pricing docs, and where mixed-tool setups show up in real practice. Then I’ll turn it into a dataset shape you can actually use.


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
Yes. Build a proper comparison dataset, not a vibes spreadsheet.

Use this shape:

```csv
vendor,product,category,practice_scope,pricing_model,public_list_price_min,public_list_price_max,contract_term,min_contract,nhs_login,nhs_app,message_channels,booking,triage,questionnaires,record_view,video,shared_inbox,workflow_mgmt,automation_ai,api_public,practice_level_supplier_data_available,patient_review_source_count,patient_review_score,staff_safety_source,local_healthwatch_source,public_contract_source,notes
```

For “how good are the existing tools, really?”, I’d pull from five source classes.

First, **official market and usage data**. NHS England now publishes machine-readable practice-level online-consultation data with each practice’s supplier name, submission counts, submission rates, and it explicitly says it can identify practices with **more than one supplier**. It also warns that functionality, workflow coverage and data quality vary a lot by supplier and practice implementation, which is exactly why you want this in the dataset rather than guessing. citeturn795730view0

Second, **public commercial docs**. The Crown Commercial Service marketplace is the best clean source for public list pricing, feature claims, support terms, onboarding, and contract minima. It is not “what every practice actually pays”, but it is the most normalised public baseline you’ll get. For example, Patchs, Accurx, eConsult, iPLATO, Abtrace and Patients Know Best all have public marketplace entries with pricing and feature summaries. citeturn907091view0turn186064view5turn186064view0turn990217view1turn186064view2turn530144search1

Third, **patient sentiment**. Trustpilot is useful, but only as one noisy signal. Patchs currently shows about **2,138 reviews** and a **4.5/5 TrustScore**; Patients Animahealth shows about **1,286 reviews** and a **4.5/5 TrustScore**; eConsult shows about **493 reviews** and a **1.5/5 TrustScore**. Trustpilot itself says it does **not fact-check specific claims**, and reviews can be unverified or invitation-driven, so treat it as sentiment, not truth. citeturn417154view1turn417154view3turn181873view1

Fourth, **staff and safety evidence**. The single best source here is the 2024 HSSIB investigation. It found online consultation tools can help, but also found safety incidents, inequitable access where patients cannot use the tools, staff concerns about making decisions from limited information, practices capping daily requests for safety, and concern that these tools can reduce opportunities for holistic care and long-term-condition management. That is the best mainstream evidence source for “what does this feel like for staff and where does it break?”. citeturn547654view2

Fifth, **local implementation evidence**. Practice websites, local Healthwatch reports, Contracts Finder and Find a Tender give you the missing bit: what people are actually live on, what mixed setups look like, and sometimes what commissioners or health boards are really paying. The New Bank appointments page is a perfect example: it routes NHS App requests into **Accurx**, also offers a direct **Patchs** form, and then says **Patchs is our online system** and that all requests go through it. That is a real mixed-access presentation, whether or not the backend plumbing is elegant. citeturn547654view0

On the “hybrid mix” question: yes, that looks common enough to treat as normal. NHS England’s own online-consultation dataset says it can identify practices with **more than one supplier**, and its practice-level file includes supplier names per practice. The NHS App integration page also says some suppliers have **multiple NHS App integrations**. At the practice level, New Bank is already exposing at least an Accurx route, a Patchs route and phone; other practice websites plainly show multiple vendor cards on the same site. citeturn795730view0turn135965search2turn547654view0turn547654view1

The likely staff UX is therefore not “one neat tool”. It is usually a stack. Best case, that stack is mostly one suite: Accurx is pitching messaging, questionnaires, triage, video, booking, reminders, record view and NHS App integration in one platform, while iPLATO pitches triage plus myGP/NHS App/web intake, signposting, self-booking and audit logging. Worst case, it is multiple partial tools, multiple inboxes or worklists, inconsistent patient wording, and messy implementation. HSSIB’s point was basically that the safety problem is not just the tool, it is the whole local socio-technical implementation. citeturn186064view5turn990217view1turn547654view2

A good starter price/feature sheet from public sources looks like this:

- **Accurx**: bundled GP toolkits. Bronze includes patient/clinician messaging, reminders, questionnaires and record view; Silver adds online consultation and video; Gold adds appointment booking. Outside the temporary flash-sale appendix, public list pricing for smaller GP populations is **£0.53 / £0.85 / £1.07 per patient per year** for Bronze / Silver / Gold. Public module pricing outside the sale period includes two-way patient messaging **£0.27**, patient triage **£0.30**, video **£0.20**, appointment booking **£0.34**, with clinician messaging and record view listed as free. citeturn299510view0turn764374view1turn764374view2turn764374view3

- **Patchs**: online consultation with clinical-system integration, uploads, automatic coding, two-way messaging, custom questionnaires, AI triage/workflow, analytics, booking, EPS integration and video consultation. Public list price is **£0.45 to £0.90** per unit per year on the marketplace, and the pricing PDF shows **£0.90 / £0.70 / £0.45 per patient per year** by band, with a **36-month minimum contract**. citeturn907091view0turn299510view1

- **eConsult**: structured data collection “mirroring” a face-to-face consultation, with deployment/support included. Public marketplace list price is **£0.29 to £0.35 a licence**. The wording is the marketplace’s, so I would record it exactly like that rather than pretending it is clean per-patient pricing. citeturn186064view0

- **iPLATO Triage**: accepts requests via web, **myGP** or the **NHS App**; can cap capacity by request type; signpost; assign to teams; offer self-book; record outcomes; respond with questionnaires; and claims an audit log into the patient record. Public list price is **£0.10 to £0.20 per person per year**. citeturn990217view1

- **Abtrace CDSS Proactive Monitoring**: more proactive-monitoring/workflow than classic front-door triage. Public marketplace price is **£2,000 a licence a year**, while the pricing PDF also describes **£0.66 per patient per year** for the software and unlimited users. citeturn186064view2turn151531search2

- **Patients Know Best**: this is not a cheap GP front-door form tool; it is a broader patient record/portal/engagement platform. Features include multi-provider records, NHS login and NHS App integration, letters, appointments, messaging, care plans, forms, questionnaires and self-management. Public entry-level departmental pricing is **£35,459 a year**, with higher organisational and regional models above that. citeturn530144search1turn530144search0

- **Hero Health**: older public G-Cloud documentation described **£0.50 per patient per year plus SMS costs** for patient-led booking and batch booking links, including hub/clinic booking patterns and support for social prescribers to view diaries and send notes back. I would mark this as an **older public price point**, not current confirmed pricing. citeturn542775search2

- **MedLink**: publicly visible feature sheet is questionnaires, automated communication, booking and automated clinical coding for chronic-condition management and back-office release. I did **not** find a clean current public price page I’d trust enough to quote. citeturn186064view3

The biggest pricing takeaway is the one you already spotted: this market is sold mostly as **procurement bundles and pathway coverage**, not as marginal infrastructure cost. Accurx, Patchs and iPLATO all use per-patient style pricing in public docs, while Patients Know Best is openly saying a per-patient model would be the wrong commercial model for its service and prices at service / organisation / region level instead. That is a commercial shape, not a technical necessity. citeturn764374view1turn299510view1turn990217view1turn530144search0

On whether practices get “the platform they have” rather than the platform they want: often yes. NHS England’s data notes some systems are commissioned at integrated-care-board level, practices can have different suppliers, and coverage is not uniform. A board-level award notice from Betsi Cadwaladr said Accurx had been **free to general practices** there until March 2021 and then moved into a health-board contract worth **£204,910**, which is a good example of how the practice experience can be “this is what our system bought for us” rather than an individual surgery shopping calmly on merit. citeturn795730view0turn394037search0

On open source: the NHS service standard is still explicit that new source code should be **open and reusable unless there is a good reason not to**. But in this exact GP front-door / triage / patient-messaging niche, I did **not** find a credible mature open-source product in live NHS use that is the equivalent of Patchs / Accurx / eConsult / Anima. In practice this space still looks overwhelmingly proprietary. citeturn154711search3turn154711search7

If you want the next useful step, I’ll turn this into a scored comparison matrix with weighted dimensions: patient sentiment, staff burden, continuity risk, accessibility, multilingual support, openness, and public price.


#### You:
so our USP isn't "better quality open-source open front door", it's "the only continuity system" that exists, if we integrate properly with NHS systems? My UI/UX for this is starting to make sense too, is you don't treat the patient as interacting with the computer, but as if they're chatting in a chat/slack room with any other staff tagged onto their case/issue/ticket/cycle. The staff only really see their relevant parts, so it doesn't need to bother them constantly, but we keep the presentation as if all those people are accessible, not always-on live-chat (that would be insane for any practice over a handful of patients), but at least to a reviewable queue of events raised, that has some basic safeguards (including optional LLM back-check, given the trivial cost of having an llm just answer some basic questions of a chat log reliably). I'd want it to foster the idea to the patient of a healthcare team, and like that practices can obviously see the value in patients understanding the shape of their team, and who does what. It absolutely has to be as easy to use as the easiest features of apps like instagram, like no fucking about, with a personal/community touch. Integrating automatic ppg-enrollement and updates also means patients who are interested can engage further from the same place they manage their healthcare, not a separate route around the system, but built in to it. There is this offhand thing in the NHS constitution about how it is the responsibility of patients to pursue care, but I'd like to think we can identify enough performance improvement through smart systems design that keeps everyone involved, but never nags anyone unless they absolutely need to be nagged, makes a lot of sense, as a response to over-load.



#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
I’m sanity-checking the “continuity as the USP” framing against current NHS wording and the platform direction, then I’ll sharpen the product position and the chat-style UI idea into something practices could actually tolerate.


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
Not “the only continuity system”. That’s too absolute and easy to knock down.

The better framing is something like: **a continuity and closure engine for primary care**, or **relationship-preserving access**. The gap is real: the safety investigation into GP continuity found there is **no standard framework** for continuity in English general practice, many practices have **no formal continuity system**, and GP IT is not required to surface “unresolved symptoms” or continuity cues to the next clinician. At the same time, the online-consultation investigation found digital front doors can create inequitable access, reduce opportunities for holistic care and long-term-condition management, and generate safety risk when patients can’t use them well. That is a very defensible product space. citeturn381292view2turn381292view3

So the product claim is not “we’re open source and nicer”. It is more like: **we make access preserve context, preserve ownership, and drive to closure instead of repeatedly re-triaging the same person from scratch**. That also gives you a cleaner answer to the “GPs fear more work” problem, because you are not selling more chat, more inbox, or more noise. You are selling less duplicated history, fewer dropped threads, fewer unresolved repeats, and fewer patients silently falling out of contact. The workload case is not fake either: the Cambridge/INSEAD work found continuity was associated with longer intervals to the next consultation, and modelled an **upper-bound 5.2% reduction** in consultation demand if practices reached top-decile continuity while targeting the patients most likely to benefit. citeturn661096search1turn661096search10

Your UI instinct is good, with one important correction: don’t build “chat”. Build a **threaded care timeline that feels like chat to the patient** and feels like **queues + tasks + ownership** to staff.

Patient side:
a single thread per issue,
named owner or owning team,
plain status like “waiting for you”, “waiting for us”, “booked”, “we’ll review by tomorrow”,
tiny reply actions,
clear next step,
visible team roles in human language.

Staff side:
filtered worklists,
role-specific tasks,
summary first,
thread on demand,
no expectation of live response,
hard escalation rules,
merge/link repeated contacts about the same unresolved issue.

That gives the patient the feeling of an accessible care team without turning the practice into Slack. The clinician never sees “a chat app”. They see the small subset of events that matter to them.

The other bit I’d keep is **episode ownership**. Every issue has:

- an owner
- a current state
- a next review time
- a “waiting on” field
- a continuity link to past related episodes

That is where you get the actual continuity value. Without that, you just made a prettier intake form.

The “team” framing is strong too. HSSIB’s continuity work explicitly distinguished between **personal continuity** and **informational continuity**. You will not always get the same doctor, but you can still make it feel like one joined-up team if the context, ownership and unresolved-history are carried forward properly. citeturn381292view2

I would keep the key patient actions brutally simple:

I’m fine now\
I still need help\
This got worse\
Please call me\
Please contact my carer\
I need another language / easier format\
This is about the same issue as before

That is the “Instagram-easy” bit, not visual gimmicks. Minimal friction, obvious state changes, almost no typing unless needed.

On the NHS Constitution point, I’d be careful. The current public wording is much narrower than “patients must pursue care”. The patient responsibility being strengthened in the review is basically about **keeping, cancelling or rearranging appointments**, while the NHS side is also being pushed to communicate appointment information **clearly, timely and accessibly**. That actually supports your design instinct: make the next step obvious, lightweight and easy to act on. citeturn381292view1

For PPG and wider engagement, same shell is fine, same domain is not. I’d put participation in the same product home, but as a separate lane with separate consent and notifications. The care thread is about getting help. The participation lane is about shaping services. Shared identity, shared messaging layer, separate purpose.

And yes, this can be sold as an overload response rather than a change-for-change’s-sake system. The pitch is:

current tools optimise capture and routing;\
this optimises continuity, ownership and closure;\
patients feel held by a team;\
staff get fewer repeated dead-end contacts;\
the practice gets less hidden failure.

That’s a much stronger USP than “better open front door”.

The shortest version is: **don’t call it chat, don’t call it triage, don’t call it a portal. Call it the continuity layer the current stack is missing.**


#### You:
okay, this chat needs to move into review. Break down the entire chat into sectors/interests/concerns and gimme a one/two-page summary of this entire chat, so I can use it as a backbone to break it out into specific folders

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
## Sector / interest / concern map

### 1. Core product thesis

- This is not “another online consultation form”.
- The real gap is continuity, closure, and active follow-up.
- Product goal: preserve context, preserve ownership, and keep chasing until a safe closure state exists.
- Better framing than “open-source front door”: a continuity and closure engine for primary care.

### 2. NHS integration surface

- Patient sign-in via NHS login.
- NHS App as a surfaced responsive web experience.
- Staff sign-in via the NHS staff identity system.
- GP transactions through supplier-paired GP integrations.
- Outbound and follow-up through the national messaging service.
- Proxy support is essential and currently transitional: local practice-managed proxy now, national proxy later.

### 3. Platform maturity / stability

- National identity and messaging layers are the future-facing, relatively durable parts.
- GP transaction layers are older, awkward, still heavily used, and unlikely to disappear soon.
- Proxy is clearly going national, but current implementation is mid-rollout.
- Safe architecture: stable national core, ugly GP-side adapters, proxy subsystem that can straddle both worlds.

### 4. Access model critique

- Current tools optimise intake and routing, not continuity or resolution.
- Standardised pooled routing often weakens continuity unless continuity is deliberately reintroduced.
- Website-only or form-heavy access can look efficient while making access worse for deprived or chaotic patients.
- The key problem is not “digital exists”, it is “digital becomes a wall”.

### 5. Workflow / engine thinking

- The product should be a workflow engine, not a form engine.
- Core components:
  - rules engine
  - state machine
  - scheduler
  - message orchestration
  - receipt / reply handling
  - task routing
  - audit timeline
  - GP adapter layer
- Every issue becomes a care episode with explicit states, owners, timers, and closure conditions.

### 6. Messaging and follow-up

- App-first is fine, app-only is stupid.
- The patient group you care about needs SMS, phone, proxy, community support, and sometimes face-to-face.
- Key design principle: best-channel-first, then keep chasing until closed.
- Unread / ignored messages should become prioritised staff tasks, not passive silence.
- Important messages should always offer tiny state-confirmation actions:
  - I’m fine now
  - I still need help
  - Please call me
  - Contact my carer
  - Another language / easier format

### 7. Deprivation / inclusion / communication barriers

- Poor service design itself creates poor outcomes.
- Patients with hard lives often cannot afford friction, ambiguity, jargon, or dead ends.
- The platform should surface available help clearly before patients need to know the right role names.
- Communication profile should be first-class:
  - language
  - literacy / easy-read
  - interpreter needs
  - proxy / carer
  - reliable contact route
  - unstable housing / difficult contact patterns

### 8. Wider team / role-first support

- Patients should not need to know what a social prescriber, care coordinator, or wellbeing coach is.
- UX should be goal-first:
  - help with debt / housing / support
  - help changing habits / sticking to a plan
  - help navigating appointments / referrals / medicines
  - help from a clinician
- Underneath, the system routes to the right local role.
- The platform should support more outcomes than “book GP slot”.

### 9. Staff workflow reality

- Staff do not want “more chat” or “another inbox”.
- Patient side can feel like a thread / room / conversation.
- Staff side should be queues, tasks, summaries, ownership, escalation rules.
- Patients should feel held by a team; staff should only see what matters to them.

### 10. Continuity

- Continuity is not a luxury. It is linked to better outcomes, fewer admissions, lower repeat demand, and safer care.
- It is valued in principle and often traded away operationally.
- A lot of current digital access models weaken continuity by default.
- The product opportunity is to reintroduce continuity systematically, not nostalgically.

### 11. Community / non-practice partners

- Potential future feature: tightly-scoped community partner roles.
- Examples: library, shelter, drug service, refugee support, local community hub.
- Use case: contact support, attendance support, practical barrier resolution, outreach.
- Strict limits: no broad record access, no clinical decision authority, full audit.

### 12. Patient participation / PPG

- This should be a separate bounded context, not mixed into care workflows.
- Useful features:
  - easier joining
  - representative participation profiles
  - structured feedback
  - targeted mini-consultations
  - “you said / we did” action log
  - hybrid and async participation
- Avoid public forums and anything that turns practice operations into a referendum.

### 13. Competitor / market landscape

- Existing market clusters around:
  - online consultation / intake
  - triage and routing
  - messaging
  - transcription / scribing
  - document automation
  - admin chatbots / call-recall
- Less obvious market focus on what you want: continuity, closure, proxy-aware follow-up, deprivation-aware access recovery.
- Mixed-tool environments appear normal. Practices often run multiple systems or overlapping routes.

### 14. Commercial / procurement reality

- Public pricing exists for some tools, but actual buying often happens at commissioner or regional level.
- Per-patient pricing dominates, even where it makes poor technical sense.
- Effective practice cost and public list price are often different.
- Your instinct is that a continuity platform should not be sold like marginal infrastructure is linearly expensive.

### 15. Open-source angle

- NHS policy rhetoric is pro-open code.
- In this exact patient-front-door / triage / workflow niche, the live market is mostly proprietary.
- There does not appear to be a serious open-source equivalent in routine NHS use.
- Open-source remains strategically interesting, but “we are open source” is not enough as a core proposition.

### 16. Evidence / policy / external comparison

- Important external benchmark themes:
  - continuity reduces repeat demand and improves outcomes
  - online consultation tools can create inequity and safety problems
  - deprived populations get worse continuity and worse access
  - better practices preserve continuity and multiple routes, even when modernising access
- This is the lens for comparing GTD / New Bank to broader evidence.

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

- `00-product-thesis`
- `01-nhs-platform-and-integrations`
- `02-gp-system-adapters`
- `03-workflow-engine-and-state-model`
- `04-messaging-followup-and-contactability`
- `05-proxy-carers-and-access-needs`
- `06-continuity-and-safety-evidence`
- `07-deprivation-inclusion-and-communication`
- `08-role-first-service-routing`
- `09-staff-ux-and-queues`
- `10-patient-ux-and-thread-model`
- `11-community-partners`
- `12-ppg-and-participation`
- `13-competitors-pricing-and-market`
- `14-open-source-and-deployment-model`
- `15-gtd-new-bank-comparison-and-local-evidence`

If you want, I can turn that folder spine into a fuller outline with subfolders and doc names.
