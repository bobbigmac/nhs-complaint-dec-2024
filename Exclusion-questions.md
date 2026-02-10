
# Patient exclusion at New Bank and GTD

TODO: Still have a little repetition to rewrite out

We're exploring how to identify access-based patient exclusion, primarily as a result of a seemingly minor exclusionary step in the practice workflow. 

Unscheduled daytime calls, and a digital-only front-door have been a mandatory blocker to appointments for a few years, and included regular closure and deletion of patient-submitted request forms. 

Admin/management have stated this gap will be fixed/mitigated (currently pending implementation), but should also look into related effects, especially those that drive patients away, or make them choose to get sicker (which is mentioned in several patient reviews). 

How to identify and reconnect with patients who might/would prefer to be registered/treated here, but simply cannot access care?

---

## Testable areas

Some relatively easy to check systems that might identify these groups. If you can answer most of these questions with the answer 'actually, that looks okay' (even with just occasional vibe checks), the scale of the problem might be acceptable. If any one of them raises red flags, you might want to consider expanding access, rather than further formalising it.

### Urgency pressure inside the practice

* Does this practice see more urgent care than they’d expect, or about average for similar practices?
	* Is this practice quietly overwhelmed by “urgent” care requests, hence the repeated messaging about not using the form for urgent care? How many urgent care requests per registered patient is normal?
* Are doctors seeing a lot of urgency (massive red flag) where they should be seeing easy-to-fix regular issues?
* Patients are often guilt-tripped (unintentionally, mostly) into not making appointments for seemingly low-importance issues (not the fault of the practice) and may postpone care if they’re always told the NHS is 'under pressure' (“I don’t want to pressure them, *cough cough*”). 
	- Do patients say “I know you’re busy but…”, “I don’t want to be a pain but…”, or just seem rushed/anxious in appointments?

This is the “demand distortion” group: if routine stuff is missing and everything arrives late and hot, your pathway is training people to delay, self-triage badly, or try to sound urgent just to get through the queue they can only imagine has formed ahead of them.

---

### A&E spillover and “where did primary care go?”

* Do more patients from New Bank end up at A&E than similar practices?
* Does the practice know how many of its patients attended A&E? Can we ask A&E (or the system/ICB) to tell us the practice breakdown of attenders? If “avoidable complaints in A&E” is a known problem, why aren’t they dealt with here first?

If these look high, it’s hard to argue the access route is merely “inconvenient”; it’s acting like a diversion valve. The value is that it ties exclusion to visible downstream cost and risk.

---

### Funnelling and friction

* What percentage of website submissions that are invited to make an appointment do not result in an appointment?
	- Practice staff stated “70% of first phone calls are missed” but didn’t state for second phone calls; if it’s also ~70% (because conditions only changed slightly), 
	- That would suggest **~49% of contact attempts fail**
		- 2 missed calls lead to closure, except if flagged by the triaging doctor as urgent
		- Reception do not fully read the submitted text for every person they try to contact, there may be further losses here from dropped urgent requests, is there a check for these?
* Is “closed without contact” the right name of this metric inside NHS systems? Or what is it called in New Bank/GTD?
* [stats] How many requests do patients submit before seeing a doctor? 
	- Total non-admin form submissions per year divided by patients attended
	- Might be hard to filter, not sure if "patient needs appointment" is logged distinct from "patient asked for appointment" because of closures/deletions.

How many people ask for help and never reach a two-way interaction, plus how much repeat-attempt churn the system creates before one appointment actually happens.

---

### Who shows up, who doesn’t, and what’s missing in the room

* Is the makeup of the waiting room the same as the people passing outside (who are here anyway)? What about people who aren’t passing outside because they’re somewhere else... who are they, and why aren’t they here? Are they 'on the books' at all?
* Are requests for a translator, signer, and further service types around average? If not, where are your deaf or foreign speakers.
* How are completed types of tests different here to other practices? If you run 30% more (or less) of one type of test than a similar practice, what does that say about who is able to attend? If you never run tests that would be common for your region (lots of students → relatively high sexual health enquiries; young people → mental health issues).
* The website supports carers having some admin access on behalf of patients, but are carers being lost to missed calls and office-hours-only website too? Are rates of part/full-time-care patients about average, or are carers registering them elsewhere? 
* Why is the waiting room never full? [subjective, my own experience] You wouldn’t expect it to be rammed constantly, but occasional backlogs are normal; If it’s almost always empty, it looks “efficient”, but utilisation might show actual throughput.

If the patient mix and the kinds of work you do don’t resemble the local population, there might be a filter. “Empty waiting room” isn’t a win by itself; it can just mean suppressed demand. This is a highly visible practice with a lot of passing foot traffic, with very strong demand. The waiting room should reflect that unless you can prove the system is so efficient that it's just running smoothly.

---

### Signals from silence: complaints and churn

* What *is* the complaints process at this practice since the takeover?
* What complaints are there a lot (if any), and if none why not? What complaints are *not* there because it would seem pointless to complain about if nothing would change? How many complaints does this practice recieve, and how are they usually resolved? 
* Simply how long do patients stay registered here? Is that about as long as people typically live in the area?

This is the “people disappear quietly” group: excluded patients often don’t complain, especially where other practices are accessible, they just churn, give up, or reappear later as crisis care. Low complaints __can__ be a red flag.

---

### Quick spot-checks for on-the-ground staff (non-statty)

Some potential tools for doctors to consider testing exclusion quickly: 
- “Have I seen this same issue a lot today?” (some group has easier access)
- “What conditions did I see a lot at my old practice that I never see here?”
- “There’s mainly young patients here”
- “They’re always asking the same misinformed questions because they all saw the same bad source”

None of these questions prove much alone, and maybe exlusion isn't a critical issue where there is a relatively high 'choice' of practices available (for a debatable value of the word choice), but it's worth smoke-testing who IS at the practice to look for opportunities to reach people who would prefer to be here, but can't make it work with your specific process decisions.
