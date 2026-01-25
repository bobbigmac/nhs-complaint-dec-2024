# New Bank Health Centre – Access Issues: Worse Than Ever
*(Prepared for meeting on ~~12~~ 26 Nov)* - Robert (Bob) Davies: admin@bobbigmac.com

## Key Concerns

- Website is less usable: offline out of hours and often down in hours (even after 1 Oct).
- No clear offline way to get an appointment.
- Phone triage is mandatory and unscheduled; missed calls block care.
- Reviews are mostly negative (only one positive seen).
- PATCHS setup and public reviews show recurring problems.
- Receptionist job ad looks low paid; was it only advertised online?

## Protocol questions

- What happens after this meeting?
- Who is responsible for change at GTD?

## Current condition of access issues

* **After-hours blackout:** site shuts when the office shuts, so shift workers/carers are locked out. PATCHS already allows 24/7 admin/non-urgent intake; it just needs switching on.
	- This is a configuration choice you can make now.
* **Unscheduled calls:** patients wait all day; a missed call forces a restart. Missed unscheduled calls should not erase a request.
* **Complex forms and logins:** long forms, repeat questions and “NHS Login” steps drive drop-offs.
* **Confusing routes:** multiple branches and unclear wording; the path gets harder, not clearer.
* **Reality vs metrics:** appointment counts rose slightly June–Aug, but reviews and complaints say access is still poor.

> **Case:** Works 8–6. Form is closed when they try. They wrestle with a long form on a phone, miss a triage call while working, are told to start again, then the site is down. By Friday they give up and get sicker. These reports appear in GTD reviews, including New Bank.

## Scope of problem

* **Patient survey:** 39% had difficulties getting an appointment.
	- Survey undercounts harm; it misses people who gave up at the front door.
	- PATCHS set to office-hours only makes this worse.
* **Public feedback:** Hundreds of 1–2★ Trustpilot complaints on PATCHS about downtime, confusion, restarts, avoidable errors.
	- Google reviews on GTD practices already show bad feedback on the new system.
* **Spot checks:** intake is offline out of hours; error pages appear in hours. The service feels unreliable.

------------

## Bare minimum expectation

* **Always a way to start** 24/7 for non-urgent/admin.
	- Websites enable non-synchronous comms; use them.
* **Fewer restarts** (don't make people repeat themselves).
* **Don't count missed, unscheduled calls as DNAs**. That's a system failure, not a patient failure.
	- "Appointments in General Practice" monthly data shows **1 in 18 (~6%)** appointments are missed.
		- Phone DNAs fell **90 → 69 → 48** (Jun→Jul→Aug).
		- Controlling for phone volume: **6% → 4.2% → 3.5%**.
	- The drop (about half) in phone DNAs suggests fewer missed calls are logged as DNAs, but how much time is lost to unreported missed unscheduled calls each day? How big is the problem?
	- If those requests are deleted, how are lost/dropped/closed requests filed? If PATCHS replaces the backend, this may have changed.

Switching back to always-on intake and cutting restarts is the bare minimum people will notice. A better flow is “Use the website, get a call, or book to come in?”. Turning admin into a blocker harms patients.

## Notes

- New Bank is recruiting a receptionist on Indeed at ~£22k for a high-responsibility role. Can pay be higher to attract and keep good staff?
	- Do receptionists have tools and freedom to fix simple issues, or are they stuck in the same broken flows? Why are so many people having trouble with more than just the same receptionist?

- NHS “goals” of office-hours-only online access are a low bar.
	- What other sector takes its website offline when the office shuts?
	- GP access should be more open and human, not less.
	- NHS App login would be fine, but the site keeps adding other logins and is often down.
	- This is not a training issue: the process itself is weak. Even a confident digital user can’t get through because it’s offline or dead-ends.
		- PATCHS Trustpilot reviews show the same problems.
		- Causes: weak infrastructure, over-complex controls, poor metrics, poor integration, little design input, legacy systems.

## Repository Link

- [https://github.com/bobbigmac/nhs-complaint-dec-2024](https://github.com/bobbigmac/nhs-complaint-dec-2024)