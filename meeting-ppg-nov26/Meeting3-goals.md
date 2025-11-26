# New Bank Health Centre – Access Issues: Worse Than Ever
*(Prepared for meeting on ~~12~~ 26 Nov)* - Robert (Bob) Davies: admin@bobbigmac.com

## Current condition of access issues

* **After-hours blackout:** the website shuts when the office shuts → shift workers/carers are locked out entirely *(PATCHS already has an option to stay online, must be activated)*.
	- This is a configuration choice already available to you.
	- PATCHS lets practices keep an admin/non-urgent route open 24/7.
	- Such an obvious error, _somebody_ on your team **should** have prevented this simple mistake, but I see there's a trend for this decision in practices.
* **Unscheduled calls:** patients wait all day; a missed call = start over.
	* Missed, unscheduled calls must not nuke the request.
* **Redundant/complex forms + multiple logins:** high friction and drop-offs; “NHS Login” complexity makes it worse.
* **Confusing process/wording:** unclear routes, multiple branches, no rationale; the path forward gets harder, not clearer.
* **Reality vs metrics:** appointment numbers look “fine” (slight improvement june-august), but reviews and complaints still don't agree with the numbers.

> **Case:** Works 8–6, form is always closed. Tries on a phone browser from work, struggles through complex forms, misses a triage call (they're working), told to start again, site is down. By Friday they give up, get sicker. Most don't bother to leave a review—because “nothing changes.”
	> To _try_ and resolve this (so far I have failed for a year), patient has to take a day off, hope the website is open, submit a request, hope it is actioned today, and hope not to miss the call, so they don't have to start over again next time they have a day off, and have the call result in an appointment today (if time sensitive but not 'an emergency', which would send them to A&E for 12 hours) and/or book another day off for the appointment. 

## Scope of problem

* **Patient survey:** 39% said it's hard to get an appointment.
	- Survey undercounts harm. Missing the people driven away at the front door. Real access failure is likely worse.
	- PATCHS being set to office-hours only, made this even worse.
* **Public feedback:** Hundreds of 1–2★ Trustpilot complaints on PATCHS calling out downtime, confusion, restarts, bad process choices, repeating cycles of simple/avoidable errors. 
	- Google reviews on GTD practices already seeing bad reviews for new system.
* **Spot checks:** intake always **offline out of hours**; **error pages in hours** → the service feels unreliable.

------------

## Bare minimum expectation

* **Always a way to start** 24/7 for non-urgent/admin. 
	- Websites enable non-synchronous comms, don't waste it.
* **Fewer restarts** (don't make people repeat themselves).
* **Don't count missed, unscheduled calls as DNAs**. [ongoing] That's a system failure, not a patient failure.
	- I checked the "Appointments in General Practice" monthly data
		- Shows **1 in 18 (~6%)** appointments are missed.
		- Phone DNAs fell **90 → 69 → 48** (Jun→Jul→Aug).
		- Controlling for phone volume: **6.07% → 4.28% → 3.54%**.
	- The reduction (~halving) in phone DNAs suggest reduced recording of missed calls as official DNAs, but how much time IS lost to unreported missed unscheduled calls each day? 
	- If those requests are deleted, how are lost/dropped/closed requests filed? 
	- Where are unsatisfied appointment/triage requests going now? 
		- Closed and forgotten? Does anyone look at closed appointment request starts that didn't result in an appointment?

**Bottom line:** This isn't just software—it's process. Simple barriers creating avoidable harm. 

Switching to always-on intake, and fewer restarts is the minimum bar patients can feel. Ideal interaction for getting an appointment should go something more like "Would you rather use the website, have us phone you for a health chat, or just make an appointment to come in?"

------------

## Notes

- Noticed New Bank recruiting for a receptionist on Indeed. Pretty low salary (~22k, barely living wage, with a lot of responsibilities). Any chance of paying more to get someone good at it, someone who cares about patients?
	- Are support systems in place to help reception help patients? 
	- Do they have enough autonomy to handle simple everyday issues? 
	- Do they have enough power to respond to issues dynamically, or are they stuck filling in the same bad forms/workflows as patients?

- The NHS 'goals' (only online during office hours, poor access minimums) are absolutely rock-bottom standards compared to the real world
	- Can you name one other industry whose website goes offline when their office is shut? 
	- Healthcare/GP systems should be _better_ than other areas, more accessible, more human-friendly, not worse. 
	- The NHS app as login would be fine, but it says it needs some other logins
		- Have been unable to test further, as it's always been down/offline or out of hours/offline.
	- Not a 'training' problem. The process is poor.  I'm a programmer and system designer, confident and highly competent computer user, and just can't access it because it's offline, and still confusing, as all 3 paths dead-end. 
		- See PATCHS trustpilot reviews, very clear issues
		- There are understandable/fair technical reasons... bad infrastructure, overly complex system controls, blind metrics, poor integration, lack of proper use case analytics during specification, and barely (if any) input from a professional designer (either at New Bank, GTD or PATCHS), competing priorities, legacy systems.
