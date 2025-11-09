
# Access Issues: Worse Than Ever

## Why we’re here (human impact)

* **After-hours blackout:** the website shuts when the office shuts → shift workers/carers are locked out entirely *(PATCHS should already have an option to stay online)*.
	- This is a configuration choice already available to you.
	- PATCHS lets practices keep an admin/non-urgent route open 24/7.
	- Such an obvious error, _somebody_ on your team **should** have prevented this simple mistake.
* **Unscheduled calls:** patients wait all day; a missed call = start over.
	* Missed, unscheduled calls must not nuke the request.
* **Redundant/complex forms + multiple logins:** high friction and drop-offs; “NHS Login” complexity makes it worse.
* **No message portal/progress:** people can’t see status, can’t re-read a call, don’t know what happens next.
* **Confusing process/wording:** unclear routes, multiple branches, no rationale; the path forward gets harder, not clearer.
* **Reality vs metrics:** appointment numbers look “fine” (slight improvement june-august), but reviews and complaints still don't agree with the numbers.

> **Example:** Works 8–6, form is always closed. Tries on a phone browser from work, struggles through complex forms, misses a triage call (they're working), told to start again, site is down. By Friday they give up, get sicker. Most don’t bother to leave a review—because “nothing changes.”
	- To _try_ and resolve this (so far I have failed for a year), patient has to take a day off, hope the website is open, submit a request, hope it is actioned today, and hope not to miss the call, so they don't have to start over again next time they have a day off, and have the call result in an appointment today (if time sensitive but not 'an emergency', which would send them to A&E for 12 hours) and/or book another day off for the appointment. 
	- That's an awful lot of hope for something that should be as simple as making an appointment (even just by phone).

## Scope of problem

* **Patient survey:** 39% said it’s hard to get an appointment.
	- Survey undercounts harm. Missing the people driven away at the front door. Real access failure is likely worse.
* **Public feedback:** Hundreds of 1–2★ Trustpilot complaints on PATCHS calling out downtime, confusion, restarts, bad process choices, repeating cycles of simple/avoidable errors. 
	- Google reviews on GTD practices already seeing bad reviews for new system.
* **Spot checks:** intake always **offline out of hours**; **error pages in hours** → the service feels unreliable.

## Bare minimum expectation

* **Always a way to start** 24/7 for non-urgent/admin. 
	- Websites enable non-synchronous comms, don't waste it.
* **Fewer restarts** (don’t make people repeat themselves).
* **Don’t count missed, unscheduled calls as DNAs**. [ongoing] That’s a system failure, not a patient failure.
	- I checked the "Appointments in General Practice" monthly data
		- Shows 1 in 18 (~6%) appointments are missed.
		- Phone DNAs fell 90 → 69 → 48 (Jun→Jul→Aug).
		- Controlling for phone volume: 6.07% → 4.28% → 3.54%.
	- The reduction (~halving) in phone DNAs suggest reduced recording of missed calls as official DNAs, but how much time IS lost to unreported missed unscheduled calls each day? 
	- If those requests are deleted, how are lost/dropped/closed requests filed? 
	- Where are unsatisfied appointment/triage requests going now? 
		- Closed and forgotten? Does anyone look at closed appointment request starts that didn't result in an appointment?

**Bottom line:** This isn’t just software—it’s process. Simple barriers creating avoidable harm. 

Switching to always-on intake, and fewer restarts is the minimum bar patients can feel.

## Notes

- Noticed New Bank recruiting for a receptionist on Indeed. Pretty low salary (~22k, barely living wage, with a lot of responsibilities). Any chance of paying more to get someone good at it, someone who cares about patients?
	- Are support systems in place to help reception help patients? 
	- Do they have enough autonomy to handle simple everyday issues? 
	- Do they have enough power to respond to issues dynamically, or are they stuck filling in the same bad forms/workflows as patients?

- The NHS 'goals' (only online during office hours, poor access minimums) are absolutely rock-bottom standards compared to the real world
	- Can you name one other industry whose website goes offline when their office is shut? 
	- Healthcare/GP systems should be _better_ than other areas, more accessible, more human-friendly, not worse. 
		- Systemic failure is a pattern everyone has to choose to break.
	- The NHS app as login would be fine, but it says it needs some other logins
		- Confusing, can't you just give me a link to the form? Several paths with long explanations.
		- Have been unable to test further, as it's always been down/offline or out of hours/offline.
	- Not a 'training' problem. The process is poor. 
		- See PATCHS trustpilot reviews, very clear issues
		- I'm a programmer and system designer, confident and highly competent computer user, and just can't access it because it's offline, and still confusing, as all 3 paths dead-end. 
			- If a developer working for me shipped this, they wouldn't be working for me in future. 
		- There are understandable/fair technical reasons... bad infrastructure, overly complex system controls, blind metrics, poor integration, lack of proper use case analytics during specification, and barely (if any) input from a professional designer (either at New Bank, GTD or PATCHS), competing priorities, legacy systems.

## Case restated for clarity

We’re asking for these today...

* **24/7 start-of-care route** for non-urgent/admin (form stays open; queue if busy).
* **Phoneless access** to continue a request (SMS/email/portal reply; written by default if patient asks).
* **“Just book me” option** for routine problems (self-book slots + reception/desk-booking for people who can’t/won’t use phones).
* **No restarts** after a missed unscheduled call (or other closing state); keep the same thread alive, or allow reopening.
* **Reception civility** as a standard, not luck.

### Escalation

The practice already worsened access by switching to a form that is offline out of hours, and riddled with design problems, while claiming 'success', demonstrating a lack of competence, so this will be escalated to Manchester City Council’s Health Scrutiny Committee, copying NHS Greater Manchester Integrated Care Board (Primary Care), then Healthwatch Manchester for public reporting, and—if needed—raise it at the Greater Manchester Joint Health Scrutiny committee and with the Care Quality Commission.
