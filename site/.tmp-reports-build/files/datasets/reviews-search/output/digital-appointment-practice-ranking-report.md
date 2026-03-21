# Practices With The Strongest And Weakest Digital Appointment Access Signals

This report uses the rebuilt review index and looks only at reviews that talk about the digital route into care in a way that is clearly tied to appointments, requests, callbacks, triage, or being seen by a clinician.

In the rebuilt `40,506`-review corpus, this pass finds `1,839` digitally appointment-relevant reviews across `291` practices.

## Headline

- `831` reviews read as mainly positive about the digital route into care
- `902` read as mainly negative
- `106` are mixed

So the digital front door is not a fringe issue. It is large enough to rank practices and produce a real shortlist for manual checking.

## What I Looked For

A review was counted here if it mentioned a digital route such as:

- `website`, `online`, `online form`, `online booking`, `app`, `system`, `online triage`
- or named systems such as `AskMyGP`, `PATCHS`, `eConsult`, `Accurx`, or `NHS App`

and also linked that route to:

- getting an appointment
- sending a request
- waiting for a callback
- triage
- or actually being seen

Where a review was clearly about digital appointment access but did not use one of the sharper positive or negative phrases, the review rating was used as a fallback signal. So this is broader than a pure keyword tagger, but it is still tied to the digital route into care.

## What This Ranking Is Good For

This is a candidate list for the next step: checking what each practice actually uses and how the better and worse digital-access setups compare. It is not a final verdict on any one software product.

Named platform mentions in the top 50 practices:

- `NHS App`: `15`
- `AskMyGP`: `6`
- `PATCHS`: `6`
- `eConsult`: `3`
- `Accurx`: `3`
- `unknown only`: `23`

Named platform mentions in the bottom 50 practices:

- `NHS App`: `16`
- `AskMyGP`: `7`
- `PATCHS`: `4`
- `eConsult`: `4`
- `Accurx`: `1`
- `unknown only`: `21`

So the named product alone is still not enough. The workflow around it still matters a lot.

## Grounding Examples

Stronger digital-access positives in the corpus look like this:

- > "Submitted my medical request online and two hours later saw a GP. Excellent service. Could not be happier"  
  > Sandris Vilcans, `LADYBARN GROUP PRACTICE`, `3 months ago`
- > "The reception staff are absolutely fantastic. It’s one of the best GPs I’ve been to. I get a appointment next day. I do a lot of online bookings. They’re really good digital and on the phone as well."  
  > Bryan Fashion, `The Quays Practice`, `10 months ago`
- > "The online portal made it easy to get an appointment/call from the Team. Who told me to come straight away"  
  > Hilps, `Handforth Health Centre`, `2 years ago`

Stronger digital-access negatives look like this:

- > "Three times in the past year i have tried to get an appointment and failed using the triage system. The reception just fob you off with a link then no appointment"  
  > Stephen Hughes, `Kearsley Medical Centre`, `7 months ago`
- > "Most horrible place ever ... fill in the online form ... the number needed to be changed ... she wouldn't change it"  
  > Selina Faizi, `Dickenson Road Medical Centre`, `3 months ago`
- > "Elderly mum unable to get an appointment not able to use online form and won’t book an appointment over the phone."  
  > Sam Rothwell, `Kearsley Medical Centre`, `a year ago`

## Top 50 Practices

These are the strongest practices in this pass for digitally linked appointment access, ranked by the balance of positive vs negative digital-access reviews, with stronger evidence weighted above very thin evidence.

| Rank | Practice | Code | Positive | Negative | Mixed | All relevant | Positive share | Named platform markers |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | LADYBARN GROUP PRACTICE | `P84017` | `23` | `2` | `0` | `25` | `92.0%` | NHS App 1 |
| 2 | The Quays Practice | `D5B9D` | `7` | `0` | `0` | `7` | `100.0%` | NHS App 1 |
| 3 | Handforth Health Centre | `N81070` | `5` | `0` | `0` | `5` | `100.0%` | mostly generic website/online wording |
| 4 | Manor House Surgery | `C81081` | `5` | `0` | `1` | `6` | `100.0%` | mostly generic website/online wording |
| 5 | The Sides Medical Practice | `P87016` | `28` | `4` | `0` | `32` | `87.5%` | NHS App 2 |
| 6 | The Range Medical Centre | `P84039` | `16` | `2` | `0` | `18` | `88.9%` | NHS App 3 |
| 7 | The Brooke Surgery | `P89002` | `52` | `9` | `0` | `61` | `85.2%` | AskMyGP 24 |
| 8 | The Poplars Medical Practice | `P87002` | `9` | `1` | `0` | `10` | `90.0%` | mostly generic website/online wording |
| 9 | Bowland Medical Practice | `P84024` | `4` | `0` | `0` | `4` | `100.0%` | NHS App 1 |
| 10 | Cornbrook Medical Practice | `P84669` | `4` | `0` | `0` | `4` | `100.0%` | mostly generic website/online wording |
| 11 | The Alexandra Practice | `P84650` | `13` | `2` | `0` | `15` | `86.7%` | AskMyGP 1 |
| 12 | Conway Road Medical Practice | `P91035` | `3` | `0` | `1` | `4` | `100.0%` | AskMyGP 1 |
| 13 | Marple Medical Practice | `P88021` | `3` | `0` | `0` | `3` | `100.0%` | mostly generic website/online wording |
| 14 | Withington Medical Practice | `P84665` | `3` | `0` | `0` | `3` | `100.0%` | mostly generic website/online wording |
| 15 | Ashville Surgery | `P84038` | `17` | `4` | `1` | `22` | `81.0%` | AskMyGP 15 |
| 16 | Millgate Healthcare Partnership | `P89015002` | `56` | `15` | `1` | `72` | `78.9%` | NHS App 2 |
| 17 | The Borchardt Medical Centre | `P84010` | `9` | `2` | `2` | `13` | `81.8%` | NHS App 2 |
| 18 | Millgate Healthcare Partnership | `P89015` | `55` | `16` | `1` | `72` | `77.5%` | NHS App 2 |
| 19 | Ancoats Urban Village Medical Practice | `P84673` | `15` | `4` | `0` | `19` | `78.9%` | mostly generic website/online wording |
| 20 | Cheadle Medical Practice | `P88020` | `27` | `8` | `4` | `39` | `77.1%` | NHS App 2, Accurx 1 |
| 21 | Harwood Medical Centre | `P82016` | `5` | `1` | `0` | `6` | `83.3%` | eConsult 1 |
| 22 | Hazeldene Medical Centre | `P84067` | `5` | `1` | `0` | `6` | `83.3%` | mostly generic website/online wording |
| 23 | Lambgates Health Centre | `C81106` | `5` | `1` | `1` | `7` | `83.3%` | Accurx 1 |
| 24 | Woodlands Medical Practice | `P85010` | `5` | `1` | `0` | `6` | `83.3%` | eConsult 1, NHS App 1 |
| 25 | City Health Centre | `Y02849` | `2` | `0` | `0` | `2` | `100.0%` | mostly generic website/online wording |
| 26 | Lockside Medical Centre | `P89005` | `2` | `0` | `0` | `2` | `100.0%` | mostly generic website/online wording |
| 27 | Townside Surgery | `P83005` | `2` | `0` | `0` | `2` | `100.0%` | AskMyGP 1 |
| 28 | New Islington Medical Centre | `P84064` | `16` | `5` | `0` | `21` | `76.2%` | NHS App 1 |
| 29 | Chorlton Family Practice | `P84068` | `38` | `13` | `13` | `64` | `74.5%` | PATCHS 6, NHS App 1 |
| 30 | Norden Branch Surgery | `P86006001` | `12` | `4` | `0` | `16` | `75.0%` | PATCHS 4, NHS App 1 |
| 31 | Jalal Practice | `P85601` | `4` | `1` | `1` | `6` | `80.0%` | Accurx 1 |
| 32 | Holes Lane Medical Ltd. | `N81007` | `7` | `3` | `0` | `10` | `70.0%` | eConsult 5, PATCHS 2 |
| 33 | Family Surgery | `P88005` | `3` | `1` | `1` | `5` | `75.0%` | PATCHS 4 |
| 34 | Heywood Health | `P86016` | `3` | `1` | `0` | `4` | `75.0%` | NHS App 1, PATCHS 1 |
| 35 | Park View Group Practice | `P88018` | `3` | `1` | `0` | `4` | `75.0%` | NHS App 1 |
| 36 | The Reddish Family Practices | `P88005001` | `3` | `1` | `1` | `5` | `75.0%` | PATCHS 4 |
| 37 | WASHWAY ROAD MEDICAL CENTRE | `P91014` | `3` | `1` | `0` | `4` | `75.0%` | AskMyGP 3 |
| 38 | Archwood Medical Practice | `P88625` | `1` | `0` | `0` | `1` | `100.0%` | mostly generic website/online wording |
| 39 | Ardwick Medical Practice | `P84037` | `1` | `0` | `0` | `1` | `100.0%` | mostly generic website/online wording |
| 40 | Ashcroft Surgery | `P84053` | `1` | `0` | `1` | `2` | `100.0%` | mostly generic website/online wording |
| 41 | Astley General Practice | `P92637` | `1` | `0` | `0` | `1` | `100.0%` | mostly generic website/online wording |
| 42 | BARRINGTON MEDICAL CENTRE | `P91603` | `1` | `0` | `0` | `1` | `100.0%` | mostly generic website/online wording |
| 43 | Bolton Community Practice CIC - Ladybridge Surgery | `Y03079001` | `1` | `0` | `0` | `1` | `100.0%` | mostly generic website/online wording |
| 44 | Bosden Moor Surgery | `P88026005` | `1` | `0` | `0` | `1` | `100.0%` | mostly generic website/online wording |
| 45 | Brinnington Surgery | `P88043` | `1` | `0` | `0` | `1` | `100.0%` | mostly generic website/online wording |
| 46 | Brunswick Medical Practice | `P84611` | `1` | `0` | `0` | `1` | `100.0%` | mostly generic website/online wording |
| 47 | Caritas General Practice Partnership | `P88013` | `1` | `0` | `0` | `1` | `100.0%` | mostly generic website/online wording |
| 48 | Cottage Lane Surgery | `C81615` | `1` | `0` | `0` | `1` | `100.0%` | mostly generic website/online wording |
| 49 | Crompton View Surgery | `P82607` | `1` | `0` | `0` | `1` | `100.0%` | mostly generic website/online wording |
| 50 | David Medical Centre | `P84066` | `1` | `0` | `0` | `1` | `100.0%` | mostly generic website/online wording |

## Bottom 50 Practices

These are the weakest practices in this pass for digitally linked appointment access, again ranked by the balance of positive vs negative digital-access reviews with evidence weighting.

| Rank | Practice | Code | Positive | Negative | Mixed | All relevant | Positive share | Named platform markers |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | Dickenson Road Medical Centre | `P84026` | `0` | `10` | `0` | `10` | `0.0%` | mostly generic website/online wording |
| 2 | Kearsley Medical Centre | `P82007` | `0` | `9` | `0` | `9` | `0.0%` | eConsult 1 |
| 3 | Bolton Medical Centre | `Y02790` | `0` | `7` | `1` | `8` | `0.0%` | NHS App 2 |
| 4 | The Bolton Family Practice | `P82013` | `0` | `7` | `1` | `8` | `0.0%` | NHS App 2 |
| 5 | Guide Bridge Medical Practice | `Y02713` | `0` | `6` | `0` | `6` | `0.0%` | NHS App 1 |
| 6 | Stockport Medical Group (Delamere Practice) | `P88632001` | `0` | `6` | `0` | `6` | `0.0%` | mostly generic website/online wording |
| 7 | The Leigh Family Practice | `Y02322001` | `0` | `6` | `0` | `6` | `0.0%` | NHS App 1 |
| 8 | Culcheth Medical Centre | `N81059` | `0` | `5` | `0` | `5` | `0.0%` | eConsult 1, NHS App 1 |
| 9 | Davyhulme Medical Centre | `P91009` | `0` | `5` | `0` | `5` | `0.0%` | AskMyGP 1 |
| 10 | Hattersley Group Practice | `P89013` | `0` | `5` | `0` | `5` | `0.0%` | PATCHS 2 |
| 11 | Littletown Family Med Pract | `P85605` | `0` | `5` | `0` | `5` | `0.0%` | mostly generic website/online wording |
| 12 | Longfield Medical Practice | `P83623` | `0` | `5` | `0` | `5` | `0.0%` | PATCHS 1 |
| 13 | The Dunstan Partnership | `P82001` | `0` | `5` | `1` | `6` | `0.0%` | NHS App 1 |
| 14 | Valentine Medical Centre | `P84019` | `0` | `5` | `0` | `5` | `0.0%` | mostly generic website/online wording |
| 15 | Ailsa Craig Medical Centre | `P84009` | `1` | `9` | `1` | `11` | `10.0%` | mostly generic website/online wording |
| 16 | Greenbank Medical Practice | `P85021` | `0` | `4` | `0` | `4` | `0.0%` | mostly generic website/online wording |
| 17 | HEALEY SURGERY | `P86013` | `0` | `4` | `0` | `4` | `0.0%` | mostly generic website/online wording |
| 18 | Hawthorn MC | `Y02890` | `0` | `4` | `0` | `4` | `0.0%` | NHS App 1 |
| 19 | John Street Medical Practice | `Y02827` | `0` | `4` | `0` | `4` | `0.0%` | mostly generic website/online wording |
| 20 | Monarch Medical Centre | `P83010` | `0` | `4` | `0` | `4` | `0.0%` | AskMyGP 1 |
| 21 | Peel GPs | `P83021` | `0` | `4` | `0` | `4` | `0.0%` | NHS App 1 |
| 22 | Rock Healthcare Limited | `Y02755` | `0` | `4` | `3` | `7` | `0.0%` | AskMyGP 1 |
| 23 | Simpson Medical Practice | `Y02520` | `0` | `4` | `0` | `4` | `0.0%` | NHS App 1 |
| 24 | The Whitswood Practice | `P84635` | `0` | `4` | `0` | `4` | `0.0%` | mostly generic website/online wording |
| 25 | West Gorton Medical Practice | `P84052` | `0` | `4` | `0` | `4` | `0.0%` | mostly generic website/online wording |
| 26 | Wilmslow Road Surgery | `P84626` | `0` | `4` | `0` | `4` | `0.0%` | mostly generic website/online wording |
| 27 | Woodside Medical Centre | `P86012` | `0` | `4` | `0` | `4` | `0.0%` | NHS App 1 |
| 28 | New Bank Health | `Y02960` | `2` | `11` | `2` | `15` | `15.4%` | NHS App 1, PATCHS 1 |
| 29 | Lime Square Medical Centre | `P84059` | `1` | `7` | `0` | `8` | `12.5%` | mostly generic website/online wording |
| 30 | Alkrington Junction Practice | `P86010001` | `0` | `3` | `0` | `3` | `0.0%` | NHS App 1 |
| 31 | Ashworth Street Surgery | `P86006` | `0` | `3` | `1` | `4` | `0.0%` | mostly generic website/online wording |
| 32 | Conran Medical Centre | `P84040` | `0` | `3` | `0` | `3` | `0.0%` | mostly generic website/online wording |
| 33 | Droylsden Medical Practice | `Y02663` | `0` | `3` | `1` | `4` | `0.0%` | PATCHS 1 |
| 34 | Eastlands Medical Centre | `P84051` | `0` | `3` | `0` | `3` | `0.0%` | NHS App 1 |
| 35 | Gorton Medical Centre | `P84028` | `0` | `3` | `1` | `4` | `0.0%` | mostly generic website/online wording |
| 36 | Kingsway Medical Practice | `P84022` | `0` | `3` | `0` | `3` | `0.0%` | mostly generic website/online wording |
| 37 | Pikes Lane 1 | `P82002` | `0` | `3` | `0` | `3` | `0.0%` | eConsult 1 |
| 38 | Salford Primary Care Together | `Y00445` | `0` | `3` | `0` | `3` | `0.0%` | mostly generic website/online wording |
| 39 | Salford Primary Care Together - Eccles Gateway | `Y00445001` | `0` | `3` | `0` | `3` | `0.0%` | mostly generic website/online wording |
| 40 | Salford Primary Care Together - Little Hulton | `Y00445002` | `0` | `3` | `1` | `4` | `0.0%` | mostly generic website/online wording |
| 41 | West End Medical Centre | `P89030` | `0` | `3` | `0` | `3` | `0.0%` | mostly generic website/online wording |
| 42 | Heaton Norris Medical Practice | `P88011` | `1` | `6` | `0` | `7` | `14.3%` | mostly generic website/online wording |
| 43 | WEST TIMPERLEY MEDICAL CENTRE | `P91016` | `1` | `6` | `0` | `7` | `14.3%` | AskMyGP 2 |
| 44 | Boothstown Medical Centre | `P92605` | `2` | `9` | `0` | `11` | `18.2%` | AskMyGP 5 |
| 45 | Limelight Health and Wellbeing Hub | `P91020` | `3` | `12` | `1` | `16` | `20.0%` | AskMyGP 7, Accurx 1 |
| 46 | The Lakeside Surgery | `N81108` | `2` | `8` | `2` | `12` | `20.0%` | eConsult 6 |
| 47 | Albion Medical Practice | `P89003` | `1` | `5` | `0` | `6` | `16.7%` | NHS App 3 |
| 48 | Cornishway Group Practice | `P84043` | `1` | `5` | `0` | `6` | `16.7%` | NHS App 1 |
| 49 | Tower Family Healthcare | `P83012` | `1` | `5` | `0` | `6` | `16.7%` | AskMyGP 1 |
| 50 | Alexandra Group Med Pract | `P85015` | `0` | `2` | `0` | `2` | `0.0%` | NHS App 1 |

## Reading This List Carefully

- A practice can rank well here and still have some bad digital reviews. `LADYBARN GROUP PRACTICE`, `The Sides Medical Practice`, and `The Brooke Surgery` all still have some negative digital-access reviews in the corpus.
- A practice can rank badly on only a modest number of digitally relevant reviews. That still matters for the manual follow-up step, but it is weaker evidence than a bigger pile of consistently bad digital-access reviews.
- Generic wording still dominates. In many reviews the patient does not name the software, so the next step is still to check the actual appointment/access stack practice by practice.
- This ranking is specifically about the digital route into appointments, requests, callbacks, and being seen. It is not a full ranking of overall practice quality.

## Related Allocation Note

The platform-allocation follow-on now sits in its own note: `digital-platform-allocation-report.md`.

That separate report covers the wider named-platform question across the digitally relevant practice set, while this note stays focused on the top and bottom appointment-access experience ranking.
