# Practices With The Strongest And Weakest Digital Appointment Access Signals

This report rebuilds the reviews-search index with the widened corpus, then looks for reviews that talk about **websites, online forms, apps, online triage, or named digital systems** in a way that is clearly tied to **getting an appointment, submitting a request, getting a callback, or being seen by a clinician**.

The rebuilt index used here contains `36,676` reviews across the widened corpus. From that, this pass found `1,737` reviews across `278` practices that look specifically relevant to digital appointment access.

## Headline

- `774` reviews read as mainly positive about the digital route into care
- `864` reviews read as mainly negative about the digital route into care
- `99` reviews are mixed, usually because the review praises one part of the digital route but still describes friction, closure, or a weak next step

So the digital front door is not a small side topic. In this wider corpus, it produces a large enough body of review language to rank practices and create a serious manual follow-up list.

## What I Looked For

I did not rely on the first narrow tag set. I mined the index again for the language patients actually use around digital access and then widened the measurement.

A review was counted as digitally relevant here if it mentioned one or more of these:

- `website`, `online`, `site`, `app`, `system`, `online form`, `online booking`, `online triage`
- named systems such as `AskMyGP`, `PATCHS`, `eConsult`, `Accurx`, or `NHS App`
- and also linked that digital route to an appointment, request, callback, triage, being seen, or getting through to a clinician

Then I widened the review-level signals using wording that actually turns up in the corpus.

Positive digital wording commonly includes:

- `same day appointment`
- `quick and easy`
- `online triage is so fast and efficient`
- `triaged and invited in for an appointment`
- `contacted GP via Patchs, got sent an appointment`
- `easy to get an appointment through the online form`

Negative digital wording commonly includes:

- `impossible to get an appointment`
- `fill in an online form but it is not available`
- `only opens at 6pm` or `between 8am and 10am`
- `ignored my form` or `never heard back`
- `couldn't find the relevant option on e-consult`
- `cut me off as I was writing`

Where a review was clearly about digital appointment access but did not use one of those sharper phrases, I used the review rating as a fallback signal. That means this ranking is broader than a pure keyword tagger, but still tied to the digital route into booking, triage, callbacks, and appointments.

## What This Ranking Is Good For

This is meant as a **candidate list** for the next step: checking which software or access setup each practice actually uses, and then comparing the better and worse performers more directly. It is not a final verdict on which software product is best.

A lot of patients still say only `the website`, `the online form`, or `the system`, so the named-platform signal is weaker than the experience signal.

Across the top 50 practices, named platform mentions appear in this many practices:

- `NHS App`: 14
- `AskMyGP`: 6
- `PATCHS`: 7
- `eConsult`: 4
- `Accurx`: 2
- `unknown only`: 22

Across the bottom 50 practices, named platform mentions appear in this many practices:

- `NHS App`: 17
- `AskMyGP`: 7
- `eConsult`: 4
- `PATCHS`: 4
- `Accurx`: 1
- `unknown only`: 20

So the named product alone is not enough. The workflow around it still seems to matter a lot.

## Grounding Examples

Stronger digital-access positives in the corpus look like this:

- > "Submitted my medical request online and two hours later saw a GP. Excellent service. Could not be happier"  
  > Sandris Vilcans, `LADYBARN GROUP PRACTICE`, `3 months ago`
- > "Yesterday, within 2 hours I had registered for the surgery online, been accepted, triaged and invited in for an appointment"  
  > Nathaniel Hicks, `Manor House Surgery`, `8 months ago`
- > "The online portal made it easy to get an appointment/call from the Team. Who told me to come straight away"  
  > Hilps, `Handforth Health Centre`, `2 years ago`

Stronger digital-access negatives in the corpus look like this:

- > "Three times in the past year i have tried to get an appointment and failed using the triage system. The reception just fob you off with a link then no appointment"  
  > `Kearsley Medical Centre`, low-star review
- > "Impossible to get an appointment and have not implemented new government policy of online appointment booking being available 24 hours"  
  > `The Lakeside Surgery`, low-star review
- > "Filled out their system online, was told I needed to be seen urgently"  
  > `Molyneux House Surgery`, low-star review

## Top 50 Practices

These are the strongest practices in this pass for digitally linked appointment access, ranked by the balance of positive vs negative digital-access reviews, with stronger evidence weighted above very thin evidence.

| Rank | Practice | Code | Positive | Negative | Mixed | All relevant | Positive share | Named platform markers |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | LADYBARN GROUP PRACTICE | `P84017` | 23 | 2 | 0 | 25 | 92.0% | NHS App 1 |
| 2 | Handforth Health Centre | `N81070` | 5 | 0 | 0 | 5 | 100.0% | mostly generic website/online wording |
| 3 | Manor House Surgery | `C81081` | 5 | 0 | 1 | 6 | 100.0% | mostly generic website/online wording |
| 4 | The Sides Medical Practice | `P87016` | 28 | 4 | 0 | 32 | 87.5% | NHS App 2 |
| 5 | The Range Medical Centre | `P84039` | 16 | 2 | 0 | 18 | 88.9% | NHS App 3 |
| 6 | The Brooke Surgery | `P89002` | 52 | 9 | 0 | 61 | 85.2% | AskMyGP 24 |
| 7 | The Poplars Medical Practice | `P87002` | 9 | 1 | 0 | 10 | 90.0% | mostly generic website/online wording |
| 8 | Bowland Medical Practice | `P84024` | 4 | 0 | 0 | 4 | 100.0% | NHS App 1 |
| 9 | Cornbrook Medical Practice | `P84669` | 4 | 0 | 0 | 4 | 100.0% | mostly generic website/online wording |
| 10 | The Alexandra Practice | `P84650` | 13 | 2 | 0 | 15 | 86.7% | AskMyGP 1 |
| 11 | Conway Road Medical Practice | `P91035` | 3 | 0 | 1 | 4 | 100.0% | AskMyGP 1 |
| 12 | Marple Medical Practice | `P88021` | 3 | 0 | 0 | 3 | 100.0% | mostly generic website/online wording |
| 13 | Withington Medical Practice | `P84665` | 3 | 0 | 0 | 3 | 100.0% | mostly generic website/online wording |
| 14 | Ashville Surgery | `P84038` | 17 | 4 | 1 | 22 | 81.0% | AskMyGP 15 |
| 15 | Millgate Healthcare Partnership | `P89015002` | 56 | 15 | 1 | 72 | 78.9% | NHS App 2 |
| 16 | The Borchardt Medical Centre | `P84010` | 9 | 2 | 2 | 13 | 81.8% | NHS App 2 |
| 17 | Millgate Healthcare Partnership | `P89015` | 55 | 16 | 1 | 72 | 77.5% | NHS App 2 |
| 18 | Ancoats Urban Village Medical Practice | `P84673` | 15 | 4 | 0 | 19 | 78.9% | mostly generic website/online wording |
| 19 | Harwood Medical Centre | `P82016` | 5 | 1 | 0 | 6 | 83.3% | eConsult 1 |
| 20 | Hazeldene Medical Centre | `P84067` | 5 | 1 | 0 | 6 | 83.3% | mostly generic website/online wording |
| 21 | Lambgates Health Centre | `C81106` | 5 | 1 | 1 | 7 | 83.3% | Accurx 1 |
| 22 | Woodlands Medical Practice | `P85010` | 5 | 1 | 0 | 6 | 83.3% | eConsult 1, NHS App 1 |
| 23 | City Health Centre | `Y02849` | 2 | 0 | 0 | 2 | 100.0% | mostly generic website/online wording |
| 24 | Lockside Medical Centre | `P89005` | 2 | 0 | 0 | 2 | 100.0% | mostly generic website/online wording |
| 25 | Townside Surgery | `P83005` | 2 | 0 | 0 | 2 | 100.0% | AskMyGP 1 |
| 26 | New Islington Medical Centre | `P84064` | 16 | 5 | 0 | 21 | 76.2% | NHS App 1 |
| 27 | Chorlton Family Practice | `P84068` | 38 | 13 | 13 | 64 | 74.5% | PATCHS 6, NHS App 1 |
| 28 | Norden Branch Surgery | `P86006001` | 12 | 4 | 0 | 16 | 75.0% | PATCHS 4, NHS App 1 |
| 29 | Jalal Practice | `P85601` | 4 | 1 | 1 | 6 | 80.0% | Accurx 1 |
| 30 | Holes Lane Medical Ltd. | `N81007` | 7 | 3 | 0 | 10 | 70.0% | PATCHS 2, eConsult 5 |
| 31 | Family Surgery | `P88005` | 3 | 1 | 1 | 5 | 75.0% | PATCHS 4 |
| 32 | Heywood Health | `P86016` | 3 | 1 | 0 | 4 | 75.0% | PATCHS 1, NHS App 1 |
| 33 | Park View Group Practice | `P88018` | 3 | 1 | 0 | 4 | 75.0% | NHS App 1 |
| 34 | The Reddish Family Practices | `P88005001` | 3 | 1 | 1 | 5 | 75.0% | PATCHS 4 |
| 35 | WASHWAY ROAD MEDICAL CENTRE | `P91014` | 3 | 1 | 0 | 4 | 75.0% | AskMyGP 3 |
| 36 | Archwood Medical Practice | `P88625` | 1 | 0 | 0 | 1 | 100.0% | mostly generic website/online wording |
| 37 | Ardwick Medical Practice | `P84037` | 1 | 0 | 0 | 1 | 100.0% | mostly generic website/online wording |
| 38 | Ashcroft Surgery | `P84053` | 1 | 0 | 1 | 2 | 100.0% | mostly generic website/online wording |
| 39 | Astley General Practice | `P92637` | 1 | 0 | 0 | 1 | 100.0% | mostly generic website/online wording |
| 40 | Bolton Community Practice CIC - Ladybridge Surgery | `Y03079001` | 1 | 0 | 0 | 1 | 100.0% | mostly generic website/online wording |
| 41 | Bosden Moor Surgery | `P88026005` | 1 | 0 | 0 | 1 | 100.0% | mostly generic website/online wording |
| 42 | Brinnington Surgery | `P88043` | 1 | 0 | 0 | 1 | 100.0% | mostly generic website/online wording |
| 43 | Brunswick Medical Practice | `P84611` | 1 | 0 | 0 | 1 | 100.0% | mostly generic website/online wording |
| 44 | Caritas General Practice Partnership | `P88013` | 1 | 0 | 0 | 1 | 100.0% | mostly generic website/online wording |
| 45 | Cottage Lane Surgery | `C81615` | 1 | 0 | 0 | 1 | 100.0% | mostly generic website/online wording |
| 46 | Crompton View Surgery | `P82607` | 1 | 0 | 0 | 1 | 100.0% | mostly generic website/online wording |
| 47 | David Medical Centre | `P84066` | 1 | 0 | 0 | 1 | 100.0% | mostly generic website/online wording |
| 48 | Durnford Medical Centre | `P86019` | 1 | 0 | 0 | 1 | 100.0% | mostly generic website/online wording |
| 49 | Eastholme Surgery now incorporated in Heaton Moor | `P88026003` | 1 | 0 | 0 | 1 | 100.0% | mostly generic website/online wording |
| 50 | Grosvenor Medical Centre | `P89026` | 1 | 0 | 0 | 1 | 100.0% | mostly generic website/online wording |

## Bottom 50 Practices

These are the weakest practices in this pass for digitally linked appointment access, again ranked by the balance of positive vs negative digital-access reviews with evidence weighting.

| Rank | Practice | Code | Positive | Negative | Mixed | All relevant | Positive share | Named platform markers |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | Dickenson Road Medical Centre | `P84026` | 0 | 10 | 0 | 10 | 0.0% | mostly generic website/online wording |
| 2 | Kearsley Medical Centre | `P82007` | 0 | 9 | 0 | 9 | 0.0% | eConsult 1 |
| 3 | Bolton Medical Centre | `Y02790` | 0 | 7 | 1 | 8 | 0.0% | NHS App 2 |
| 4 | The Bolton Family Practice | `P82013` | 0 | 7 | 1 | 8 | 0.0% | NHS App 2 |
| 5 | Guide Bridge Medical Practice | `Y02713` | 0 | 6 | 0 | 6 | 0.0% | NHS App 1 |
| 6 | Stockport Medical Group (Delamere Practice) | `P88632001` | 0 | 6 | 0 | 6 | 0.0% | mostly generic website/online wording |
| 7 | The Leigh Family Practice | `Y02322001` | 0 | 6 | 0 | 6 | 0.0% | NHS App 1 |
| 8 | Culcheth Medical Centre | `N81059` | 0 | 5 | 0 | 5 | 0.0% | eConsult 1, NHS App 1 |
| 9 | Davyhulme Medical Centre | `P91009` | 0 | 5 | 0 | 5 | 0.0% | AskMyGP 1 |
| 10 | Hattersley Group Practice | `P89013` | 0 | 5 | 0 | 5 | 0.0% | PATCHS 2 |
| 11 | Littletown Family Med Pract | `P85605` | 0 | 5 | 0 | 5 | 0.0% | mostly generic website/online wording |
| 12 | Longfield Medical Practice | `P83623` | 0 | 5 | 0 | 5 | 0.0% | PATCHS 1 |
| 13 | The Dunstan Partnership | `P82001` | 0 | 5 | 1 | 6 | 0.0% | NHS App 1 |
| 14 | Valentine Medical Centre | `P84019` | 0 | 5 | 0 | 5 | 0.0% | mostly generic website/online wording |
| 15 | Ailsa Craig Medical Centre | `P84009` | 1 | 9 | 1 | 11 | 10.0% | mostly generic website/online wording |
| 16 | Greenbank Medical Practice | `P85021` | 0 | 4 | 0 | 4 | 0.0% | mostly generic website/online wording |
| 17 | HEALEY SURGERY | `P86013` | 0 | 4 | 0 | 4 | 0.0% | mostly generic website/online wording |
| 18 | Hawthorn MC | `Y02890` | 0 | 4 | 0 | 4 | 0.0% | NHS App 1 |
| 19 | John Street Medical Practice | `Y02827` | 0 | 4 | 0 | 4 | 0.0% | mostly generic website/online wording |
| 20 | Monarch Medical Centre | `P83010` | 0 | 4 | 0 | 4 | 0.0% | AskMyGP 1 |
| 21 | Peel GPs | `P83021` | 0 | 4 | 0 | 4 | 0.0% | NHS App 1 |
| 22 | Rock Healthcare Limited | `Y02755` | 0 | 4 | 3 | 7 | 0.0% | AskMyGP 1 |
| 23 | Simpson Medical Practice | `Y02520` | 0 | 4 | 0 | 4 | 0.0% | NHS App 1 |
| 24 | The Whitswood Practice | `P84635` | 0 | 4 | 0 | 4 | 0.0% | mostly generic website/online wording |
| 25 | West Gorton Medical Practice | `P84052` | 0 | 4 | 0 | 4 | 0.0% | mostly generic website/online wording |
| 26 | Wilmslow Road Surgery | `P84626` | 0 | 4 | 0 | 4 | 0.0% | mostly generic website/online wording |
| 27 | Woodside Medical Centre | `P86012` | 0 | 4 | 0 | 4 | 0.0% | NHS App 1 |
| 28 | New Bank Health | `Y02960` | 2 | 11 | 2 | 15 | 15.4% | PATCHS 1, NHS App 1 |
| 29 | Lime Square Medical Centre | `P84059` | 1 | 7 | 0 | 8 | 12.5% | mostly generic website/online wording |
| 30 | Alkrington Junction Practice | `P86010001` | 0 | 3 | 0 | 3 | 0.0% | NHS App 1 |
| 31 | Ashworth Street Surgery | `P86006` | 0 | 3 | 1 | 4 | 0.0% | mostly generic website/online wording |
| 32 | Conran Medical Centre | `P84040` | 0 | 3 | 0 | 3 | 0.0% | mostly generic website/online wording |
| 33 | Droylsden Medical Practice | `Y02663` | 0 | 3 | 1 | 4 | 0.0% | PATCHS 1 |
| 34 | Eastlands Medical Centre | `P84051` | 0 | 3 | 0 | 3 | 0.0% | NHS App 1 |
| 35 | Gorton Medical Centre | `P84028` | 0 | 3 | 1 | 4 | 0.0% | mostly generic website/online wording |
| 36 | Kingsway Medical Practice | `P84022` | 0 | 3 | 0 | 3 | 0.0% | mostly generic website/online wording |
| 37 | Pikes Lane 1 | `P82002` | 0 | 3 | 0 | 3 | 0.0% | eConsult 1 |
| 38 | Salford Primary Care Together - Eccles Gateway | `Y00445001` | 0 | 3 | 0 | 3 | 0.0% | mostly generic website/online wording |
| 39 | Salford Primary Care Together - Little Hulton | `Y00445002` | 0 | 3 | 1 | 4 | 0.0% | mostly generic website/online wording |
| 40 | West End Medical Centre | `P89030` | 0 | 3 | 0 | 3 | 0.0% | mostly generic website/online wording |
| 41 | Heaton Norris Medical Practice | `P88011` | 1 | 6 | 0 | 7 | 14.3% | mostly generic website/online wording |
| 42 | WEST TIMPERLEY MEDICAL CENTRE | `P91016` | 1 | 6 | 0 | 7 | 14.3% | AskMyGP 2 |
| 43 | Boothstown Medical Centre | `P92605` | 2 | 9 | 0 | 11 | 18.2% | AskMyGP 5 |
| 44 | Limelight Health and Wellbeing Hub | `P91020` | 3 | 12 | 1 | 16 | 20.0% | AskMyGP 7, Accurx 1 |
| 45 | The Lakeside Surgery | `N81108` | 2 | 8 | 2 | 12 | 20.0% | eConsult 6 |
| 46 | Albion Medical Practice | `P89003` | 1 | 5 | 0 | 6 | 16.7% | NHS App 3 |
| 47 | Cornishway Group Practice | `P84043` | 1 | 5 | 0 | 6 | 16.7% | NHS App 1 |
| 48 | Tower Family Healthcare | `P83012` | 1 | 5 | 0 | 6 | 16.7% | AskMyGP 1 |
| 49 | Alexandra Group Med Pract | `P85015` | 0 | 2 | 0 | 2 | 0.0% | NHS App 1 |
| 50 | Bolton Community Practice | `Y03079` | 0 | 2 | 0 | 2 | 0.0% | mostly generic website/online wording |

## Reading This List Carefully

- A practice can rank well here and still have some bad digital reviews. `LADYBARN GROUP PRACTICE`, `The Sides Medical Practice`, and `The Brooke Surgery` all still have some negative digital-access reviews in the corpus.
- A practice can rank badly on only a modest number of digital reviews. That still matters for the manual follow-up step, but it is weaker evidence than a practice with a larger pile of consistently bad digital-access reviews.
- Generic wording still dominates. In many reviews the patient does not name the software, so the next step really is to check the actual appointment/access stack practice by practice.
- This ranking is specifically about the digital route into appointments, requests, callbacks, and being seen. It is not a full ranking of overall practice quality.

## Platform Allocation Outro

The practice tables above now include the best platform allocation I could make from explicit review wording for each practice. In many cases that is still only a weak hint, because patients often say just `the website`, `the online form`, or `the app`. But where a named system does appear, it is now surfaced directly in the `Named platform markers` column.

Across the full digitally relevant practice set, the wider allocation pass found:

- `282` practices with at least one digitally relevant appointment/access review
- `114` practices with at least one explicit named platform mention
- `168` practices that still stay `unknown only`
- `19` practices that show more than one named platform

So the corpus currently lets us allocate about `40.4%` of the digitally relevant practices to at least one named system, while `59.6%` still remain unnamed.

For the full set, the most common allocations are:

- `NHS App` only: `53` practices
- `AskMyGP` only: `22` practices
- `PATCHS` only: `10` practices
- `eConsult` only: `8` practices
- `Accurx` only: `2` practices
- `unknown only`: `168` practices

The mixed-platform cases are small but important:

- `AskMyGP + NHS App`: `7` practices
- `eConsult + NHS App`: `5` practices
- `PATCHS + NHS App`: `5` practices
- `Accurx + AskMyGP`: `1` practice
- `eConsult + PATCHS`: `1` practice

That means the review corpus is already good enough to support a first-pass platform comparison, but not good enough to replace manual checking. The top and bottom 50 are still the best shortlist for that follow-up work, while the full-set allocation gives the wider picture of what is known and what is still unresolved.

# Named Digital Platform Allocation Across The Digitally Relevant Practice Set

This note takes the widened digital-appointment review set and asks a simpler follow-up question: **for each practice in that set, do the reviews ever explicitly name the platform being used?**

The aim is not to prove the full appointment stack from reviews alone. It is to see how far the corpus lets us allocate practices to named systems such as `AskMyGP`, `PATCHS`, `eConsult`, `Accurx`, or `NHS App`, and how much still stays generic as just `the website`, `the online form`, `the app`, or `the system`.

## Coverage

- `282` practices have at least one digitally relevant appointment/access review
- `114` of those can be allocated to at least one named platform from explicit review wording
- `168` remain `unknown only`, meaning the reviews talk about digital access but never name the software
- `19` show more than one named platform, usually suggesting a changed system, multiple routes, or reviewers naming both a practice front door and the `NHS App`

Put simply: this review corpus lets us allocate about **`40.4%`** of the digitally relevant practices to at least one named system, but about **`59.6%`** still stay unnamed.

## Distribution Of Known Versus Unknown

| Allocation bucket | Practices |
| --- | ---: |
| unknown only | 168 |
| NHS App | 53 |
| AskMyGP | 22 |
| PATCHS | 10 |
| eConsult | 8 |
| AskMyGP + NHS App | 7 |
| eConsult + NHS App | 5 |
| NHS App + PATCHS | 5 |
| Accurx | 2 |
| Accurx + AskMyGP | 1 |
| eConsult + PATCHS | 1 |

The biggest single bucket by far is still `unknown only`. After that, the most common named allocations are:

- `NHS App` only: `53` practices
- `AskMyGP` only: `22` practices
- `PATCHS` only: `10` practices
- `eConsult` only: `8` practices
- `Accurx` only: `2` practices

## What The Mixed Cases Look Like

Most multiple-platform cases are small in number, but they matter because they are likely to be system changes or overlapping routes rather than clean one-platform practices.

Recurring combinations:

- `AskMyGP + NHS App`: `7` practices
- `eConsult + NHS App`: `5` practices
- `PATCHS + NHS App`: `5` practices
- `Accurx + AskMyGP`: `1` practice
- `eConsult + PATCHS`: `1` practice

Examples of multi-platform practices in the reviews include:

- `Chorlton Family Practice`: NHS App 1, PATCHS 6
- `Culcheth Medical Centre`: eConsult 1, NHS App 1
- `Dalefield Surgery`: eConsult 2, NHS App 1
- `Fairfax Group Practice`: AskMyGP 1, NHS App 1
- `Heaton Medical Centre`: eConsult 1, NHS App 1
- `Heywood Health`: NHS App 1, PATCHS 1
- `Holes Lane Medical Ltd.`: eConsult 5, PATCHS 2
- `Limelight Health and Wellbeing Hub`: Accurx 1, AskMyGP 7
- `Medlock Medical Practice`: eConsult 1, NHS App 1
- `New Bank Health`: NHS App 1, PATCHS 1

## Satisfaction By System

There are two useful ways to read the system-level numbers:

- `Any-use`: every practice where that named system appears at least once in the reviews, even if the practice also shows another named system
- `Single-only`: only practices where the reviews point to that one named system and no other named system

The single-only view is cleaner if you want a rougher software comparison without as much contamination from system changes or mixed routes.

| System | Practices any-use | Practices single-only | Positive reviews any-use | Negative reviews any-use | Weighted positive share any-use | Positive reviews single-only | Negative reviews single-only | Weighted positive share single-only |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| AskMyGP | 30 | 22 | 126 | 119 | 51.4% | 110 | 80 | 57.9% |
| PATCHS | 16 | 10 | 83 | 69 | 54.6% | 17 | 32 | 34.7% |
| eConsult | 14 | 8 | 38 | 61 | 38.4% | 20 | 40 | 33.3% |
| Accurx | 3 | 2 | 12 | 14 | 46.2% | 9 | 2 | 81.8% |
| NHS App | 70 | 53 | 379 | 327 | 53.7% | 296 | 248 | 54.4% |

## What Those System Numbers Suggest

- `AskMyGP`: `30` practices mention it at all. The any-use review balance is `126` positive vs `119` negative (`51.4%` positive). In the cleaner single-only slice it is `110` positive vs `80` negative (`57.9%` positive).
- `PATCHS`: `16` practices mention it at all. The any-use review balance is `83` positive vs `69` negative (`54.6%` positive). In the cleaner single-only slice it is `17` positive vs `32` negative (`34.7%` positive).
- `eConsult`: `14` practices mention it at all. The any-use review balance is `38` positive vs `61` negative (`38.4%` positive). In the cleaner single-only slice it is `20` positive vs `40` negative (`33.3%` positive).
- `Accurx`: `3` practices mention it at all. The any-use review balance is `12` positive vs `14` negative (`46.2%` positive). In the cleaner single-only slice it is `9` positive vs `2` negative (`81.8%` positive).
- `NHS App`: `70` practices mention it at all. The any-use review balance is `379` positive vs `327` negative (`53.7%` positive). In the cleaner single-only slice it is `296` positive vs `248` negative (`54.4%` positive).

Read cautiously, the current review corpus suggests:

- `NHS App` is the most commonly allocatable named route in this dataset, but it appears in both the stronger and weaker practice groups, so it is not a clean quality marker on its own
- `AskMyGP` looks roughly balanced overall and somewhat better in the single-only slice than in the mixed any-use slice
- `PATCHS` looks middling in the any-use view but weaker in the single-only slice
- `eConsult` looks weaker than the others in both any-use and single-only review balance
- `Accurx` looks better in the tiny single-only slice, but that is based on just `2` single-only practices and should not be over-read

## How Much Of The Ranked Set Is Still Unknown

Even inside the ranked practices, unknowns remain a huge share. In the earlier top and bottom 50 practice lists:

- top 50 practices with no named platform in reviews: `22`
- bottom 50 practices with no named platform in reviews: `20`

So the next manual step is still necessary. Reviews get us a long way, but they do not solve the whole allocation problem.

## Bottom Line

The reviews are good enough to allocate a substantial minority of the digitally relevant practices to named systems, but not most of them. The biggest bucket is still unnamed website/form/app language.

That means the review corpus can already support a first-pass software comparison, but only with caution:

- use `single-only` practices when you want the cleanest software read
- keep `any-use` practices when you want more coverage and more real-world messiness
- treat the `unknown only` group as a large unresolved block that still needs direct checking practice by practice

This is enough to start building a real quality/satisfaction picture by platform, but not enough to stop doing manual allocation work.
