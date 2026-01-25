
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

## Sector pattern

- This seems to be a pattern at the moment, with practices [claiming](https://www.oakwoodlanemedical.nhs.uk/2025/10/07/availability-of-online-consultations-from-1-october-2025/) things like "The new requirement to allow patients unlimited online access for non- urgent medical requests, throughout core hours, could make it more likely that we will have no choice but to create hospital-style waiting lists to meet patient need. We do not believe that this is a solution that anyone wants." or "GPs and their teams are under huge pressure – caring for more people with fewer resources."
    - This is patient-blaming (and a false dichotomy), there's nothing wrong with queues if you're actively working them.
    - People are much less stable if they have no idea whether they can even ask for help today, or if they have to wait till tomorrow to try and fail again.
    - Falling back to blocking the patient completely is _poor_.

Staff are choosing to reject patients before they can even start, then failing to measure the effect because angry reviews don't drive policy.

