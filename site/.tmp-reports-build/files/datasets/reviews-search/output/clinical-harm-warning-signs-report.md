# Clinical Harm Warning Signs In Google Reviews

This report looks for reviews that sound like possible clinical harm, not just bad service.

The aim is not to prove wrongdoing from reviews alone. It is to flag where the review corpus contains warning signs that deserve checking in notes, complaints, SEA work, prescribing audit, and local quality review. This is also an area the national patient survey barely touches. Patients are asked about access, confidence, and experience, but not plainly whether they felt misdiagnosed, got the wrong treatment, became more unwell after contact, or ended up in hospital after being dismissed.

## What I counted

I took a cautious pass through the indexed review corpus and focused on 1-star and 2-star reviews only.

I stripped practice-response text where possible, then flagged reviews with one or more of these markers:

- direct mention of misdiagnosis or wrong diagnosis
- direct mention of wrong or unsafe medication
- negligence, dangerous, or unsafe language
- being ignored, dismissed, or not listened to when that was linked to deterioration
- ending up in hospital, A&E, or emergency care in a clinically connected way
- severe outcome terms like sepsis, pneumonia, cancer, meningitis, appendicitis, stroke, heart attack, or "nearly died"

These categories overlap. A single review can hit more than one.

## Headline Findings

- `420` reviews were flagged as clinical harm warning signals.
- That is `2.6%` of all `16,293` reviews in the corpus.
- It is `6.4%` of all `6,604` low-star reviews.
- `154` low-star reviews used more direct failure language such as misdiagnosis, wrong medication, negligence, danger, or unsafe care.
- `293` low-star reviews described connected outcomes or escalation such as deterioration, hospital care, A&E, or a serious condition. There is overlap between these groups.
- `125` practices had at least one flagged review.
- `75` practices had at least three flagged reviews.
- `27` practices had at least five flagged reviews.

This is not most reviews. It is still a substantial enough slice to matter, especially because these are not ordinary complaints about phones, queues, or rude reception. These are the reviews where patients say care itself may have gone wrong.

## Extension: Reported Harm To Real Patients

The first pass above was about warning signs in clinical care. This extension shifts the focus to outcome.

Here the question is simpler: when reviewers say something went badly wrong, how often do they also say a real person got sicker, waited too long, missed needed care, ended up in hospital, or suffered a serious health consequence?

Again, these are reported accusations in reviews, not proven findings. But they are still highly important because they describe harm in patient terms rather than service terms.

### Outcome-Led Findings

- `69` flagged reviews said care was delayed or postponed in a way the reviewer linked to harm
- `19` flagged reviews explicitly said the patient got worse, deteriorated, or became more unwell
- `15` flagged reviews said treatment, prescribing, or missed treatment actively made the patient more ill
- `164` flagged reviews described hospital, A&E, ambulance, or emergency escalation in clinically connected situations
- `87` flagged reviews mentioned a serious condition, near miss, or life-threatening consequence such as sepsis, pneumonia, appendicitis, cancer, emergency surgery, or "could have died"

These buckets overlap heavily. The same review may describe delay, then deterioration, then hospital admission.

### 5. Delayed Care That Reviewers Link To Harm

I found `69` reviews where the complaint was not just "it took too long", but "it took too long and harm followed".

This is where admin and clinical risk blur together. A missed callback, no antibiotics, weeks waiting for medication, or repeated failure to arrange review may start as a process issue. In the reviews, patients describe that delay as part of the route to becoming more unwell.

Examples:

- `Ashville Surgery`: one reviewer wrote they had "stress induced heart failure" and were still "waiting a whole month" for prescription or referral follow-up
- `Barlow Medical Centre`: one reviewer described blood pressure of `204/110`, being told to go to A&E if symptoms worsened, but being given no medication to control it
- `The Robert Darbishire Practice`: reviews repeatedly link missed prescriptions, no follow-up, and late contact to hospital attendance and distress
- `Cornerstone Family Practice`: one reviewer said they waited two weeks for an appointment and then arrived to find "no doctor was around to see me"

This matters because, from the patient side, harm often does not look like one dramatic mistake. It looks like repeated delay until the person crosses into crisis.

### 6. Reviewers Saying They Got Worse

I found `19` reviews that explicitly used worsening language like "got worse", "deteriorated", or the equivalent.

This is a small count only because I kept it tight. Many other reviews imply worsening without using those exact words.

Examples:

- `West Point Medical Centre`: "misdiagnosed me twice and resultantly my situation worsened"
- `Benchill Medical Practice`: one parent described a child with a serious eye problem where the surgery was said to show "no urgency" while the condition worsened
- `Bolton Medical Centre`: one reviewer described severe stomach pain, nausea, and inability to walk, then tied the poor response to a worsening situation

When patients use this kind of language they are no longer just rating the encounter. They are giving their own before-and-after account of health.

### 7. Cases Where Reviewers Say Care Or Treatment Made Them More Ill

I found `15` reviews where patients directly linked treatment, prescribing, or failure to provide the right treatment with becoming more ill.

Examples:

- `Tower Family Healthcare Minden`: "Got given the wrong medication ... Make me very poorly and took me weeks to get off them"
- `The Park Medical Centre`: one reviewer said wrong diagnosis and medication led to "multiple ae trips that could have been prevented"
- `Hawthorn MC`: one reviewer described an allergic reaction to medication with swollen lips, ulcers, and redness
- `Gordon Street Medical Centre`: one reviewer said they were given the wrong medication three times in a row despite repeated warning

This is one of the clearest high-risk themes in the corpus because the reviewer is not only unhappy. They are saying the intervention itself, or the failure to intervene properly, caused bodily harm.

### 8. Emergency Escalation And Near-Miss Accounts

The biggest outcome signal is escalation outside the practice. I found `164` clinically connected hospital or emergency-escalation reviews, plus `87` reviews mentioning serious conditions or near misses.

These are the reviews where patients say the situation ended up in A&E, hospital, emergency surgery, sepsis, pneumonia, suspected cancer, appendicitis, or even a near-death account.

Examples:

- `Hattersley Group Practice`: one reviewer wrote they were "treated like i was hypochondriac, then ended up on life support"
- `Halliwell Surgery 2` and `Halliwell Surgery 3`: one reviewer said they were denied antibiotics, then hours later were diagnosed in hospital with severe pneumonia and "could of died"
- `STONEHILL MEDICAL CENTRE`: one review said a patient's sepsis was missed and "we nearly lost him"
- `The Poplars Medical Practice`: one reviewer said appendicitis was misdiagnosed as gastritis and they only avoided a worse outcome because they went to A&E anyway
- `Tregenna Group Practice`: one reviewer wrote their father was not tested for prostate cancer despite repeated requests and by the time it was found it was "so advanced he was inoperable"

This is the part of the corpus that is hardest to dismiss as ordinary frustration. Even allowing for exaggeration in some reviews, the language is repeatedly about danger, emergency rescue, and conditions that patients understood as serious threats to life or long-term health.

## Repeated Outcome Flags By Practice

If the question is where patient-reported harm sounds most serious, the most useful signal is not one quote but repeated outcome-led reviews.

### Most repeated serious-condition or near-miss mentions

| Practice | Serious-condition or near-miss reviews | Share of all reviews |
| --- | ---: | ---: |
| Northenden Group Practice | 4 | 6.2% |
| Cornerstone Family Practice | 3 | 8.3% |
| Lime Square Medical Centre | 3 | 6.6% |
| The Robert Darbishire Practice | 3 | 5.8% |
| Monarch Medical Centre | 2 | 10.3% |
| Woodlands Medical Practice | 2 | 8.3% |
| Tower Family Healthcare Minden | 2 | 7.8% |
| STONEHILL MEDICAL CENTRE | 2 | 5.0% |

### Most repeated emergency-escalation mentions

| Practice | Hospital or emergency-escalation reviews | Share of all reviews |
| --- | ---: | ---: |
| Florence House Medical Practice | 8 | 8.3% |
| Hawthorn MC | 7 | 3.9% |
| Droylsden Road Surgery Branch | 6 | 12.7% |
| Ashton Gp Service | 6 | 8.7% |
| The Robert Darbishire Practice | 5 | 5.8% |
| Lindley House Health Centre | 4 | 8.1% |
| STONEHILL MEDICAL CENTRE | 4 | 5.0% |
| Monarch Medical Centre | 3 | 10.3% |

### Practices that recur across several harm-outcome buckets

Some practices show up in several different ways at once:

- `The Robert Darbishire Practice`: repeated emergency escalation, delay-linked harm, and serious-condition mentions
- `Florence House Medical Practice`: a high volume of hospital or A&E escalation, plus delay-linked harm
- `Lime Square Medical Centre`: serious-condition mentions, deterioration language, and broader harm-signal density
- `Tower Family Healthcare Minden`: treatment-linked harm, serious-condition mentions, and delay-linked harm
- `STONEHILL MEDICAL CENTRE`: emergency escalation, serious-condition language, and missed-sepsis reporting

These are not proof of unsafe care. They are the clearest places in the review corpus where patient-reported outcomes sound severe enough to justify deeper case review.

## The Main Warning-Sign Themes

### 1. Misdiagnosis And Wrong Diagnosis

I found `25` low-star reviews with direct misdiagnosis or wrong-diagnosis language.

These reviews are often short and blunt. Patients do not write in clinical language. They write things like "misdiagnosed me twice", "said it was hayfever", or "told me it was anxiety". The pattern is not just that patients disagreed with a doctor. It is that they link the judgment to later deterioration, urgent treatment, or a more serious diagnosis elsewhere.

Examples:

- `The Poplars Medical Practice`: "a GP misdiagnosed my appendicitis for Gastritis. Thankfully I went to A&E anyway and didnt die"
- `Five Oaks Family Practice`: a parent wrote that a baby was told a serious infection was "a seasonal cold", "turned out to be rsv", and later "hayfever" "turns out she has a bad infection"
- `Chorlton Family Practice`: one reviewer said doctors were "blaming it on anxiety" when they had an enlarged lymph node and should have been sent for further investigation
- `Tregenna Group Practice`: one reviewer wrote their father was not tested for prostate cancer despite "classic symptoms", and when finally tested "he was right"

This is one of the clearest gaps with patient-survey style questions. Survey tools ask whether patients had confidence in the clinician. They do not ask whether the patient later found out the diagnosis was wrong.

### 2. Wrong Medication, Wrong Dose, Or Unsafe Prescribing

I found `14` low-star reviews with direct wrong-medication or unsafe-medication language.

This is a smaller theme than access, but it is a high-risk one. These reviews often describe wrong tablets, wrong dose, somebody else's prescription, or repeat medication being mishandled in a way the patient links to getting worse.

Examples:

- `The Park Medical Centre`: "constantly giving wrong diagnosis and medication which has lead to multiple ae trips that could have been prevented"
- `Tower Family Healthcare Minden`: "Got given the wrong medication ... Make me very poorly and took me weeks to get off them"
- `Charlestown MD`: one parent wrote their children had been given "wrong medication ... numerous times"
- `Blackford House Medical Centre`: one reviewer said they were prescribed "the wrong dose" for medication they had been on long term

This is worth treating separately from general prescription delays. Delays are common admin complaints. Wrong dose, wrong medicine, and medication linked to illness are different.

### 3. Dismissal, Not Being Listened To, Then Getting Worse

I found `82` low-star reviews where dismissal language was tied to a harmful outcome or worsening condition.

This is one of the strongest patterns in the corpus. Patients often say the main problem was not only access, but that once they did get through, they felt waved away, told it was nothing, or pushed elsewhere without real assessment. The bad outcome is often part of the same review.

Examples:

- `Monarch Medical Centre`: a reviewer wrote a friend was "constantly dismissed with her pain levels" and "if she didn't go private she could have died"
- `Halliwell Surgery 2`: one patient wrote they were told antibiotics were not needed, then went to hospital hours later and were diagnosed with severe pneumonia
- `Peel Hall Medical Centre`: one reviewer said heavy bleeding was treated with pills and "it turned out i was pregnant but losing it"
- `West Point Medical Centre`: one reviewer said they were "misdiagnosed twice" and "resultantly my situation worsened"

This matters because it gets closer to perceived clinical safety than normal satisfaction questions do. The patient is not just saying "I felt brushed off". They are saying "I felt brushed off and then something bad happened."

### 4. Hospital, A&E, Or Emergency Escalation After GP Contact

I found `162` low-star reviews with hospital or urgent-escalation language that looked clinically connected, and `89` with severe outcome or condition terms.

Some of these reviews are still mixed with access problems, but a repeated pattern shows up where patients say the surgery did not resolve the problem and they ended up in A&E, in hospital, or needing urgent outside care.

Examples:

- `Chorlton Family Practice`: "Took my 3yr old and they missed an infection and ended up in hospital"
- `Gorton Medical Centre`: "Was treated horrendously and ended up in hospital due to their incompetence"
- `Corkland Road Medical Practice`: one reviewer said they "deteriorated and ended up in a+e" and "basically nearly died"
- `Fairfax Group Practice`: one reviewer wrote "I end up going to ED same day with sepsis"
- `Woodlands Medical Practice`: one reviewer said a relative was sent urgently to hospital with suspected sepsis, which they felt "could have been avoided"

These reviews do not prove causation. But they are exactly the kind of safety signal a review corpus can surface and a normal access survey will miss.

## Practice Flags For Checking

The fairest way to use this material is not to single out one dramatic quote. It is to look for repeated warning-signal reviews across different patients.

### Highest repeated counts

Among practices with repeated flagged reviews, the highest counts were:

| Practice | Flagged reviews | Share of all reviews |
| --- | ---: | ---: |
| The Robert Darbishire Practice | 14 | 5.8% |
| Chorlton Family Practice | 12 | 1.3% |
| Florence House Medical Practice | 10 | 8.3% |
| Hawthorn MC | 10 | 3.9% |
| Droylsden Road Surgery Branch | 9 | 12.7% |
| Cheetham Hill Medical Centre | 9 | 2.8% |
| Lime Square Medical Centre | 8 | 6.6% |
| Northenden Group Practice | 8 | 6.2% |

### Highest concentrations among practices with at least five flagged reviews

These practices stand out more by concentration than by sheer volume:

| Practice | Flagged reviews | Share of all reviews |
| --- | ---: | ---: |
| Droylsden Road Surgery Branch | 9 | 12.7% |
| Ashton Gp Service | 6 | 8.7% |
| Florence House Medical Practice | 10 | 8.3% |
| Cornerstone Family Practice | 6 | 8.3% |
| Lindley House Health Centre | 5 | 8.1% |
| Tower Family Healthcare Minden | 6 | 7.8% |
| Beehive Surgery | 6 | 6.7% |
| Lime Square Medical Centre | 8 | 6.6% |

This should not be read as a league table of unsafe practices. It is a list of where the review corpus gives repeated enough warning signs that a human check is justified.

## What Makes These Reviews Different From Ordinary Complaints

Most bad reviews in the dataset are still about access, rude interactions, repeat prescriptions, or call queues.

The warning-sign subset feels different in tone and content:

- patients talk about getting worse, not just waiting longer
- patients name specific clinical consequences such as infection, pneumonia, sepsis, appendicitis, heavy bleeding, cancer, or hospital admission
- patients often contrast the GP interaction with what happened later in A&E, hospital, private care, or after seeing another clinician
- some reviews explicitly say a serious condition was missed, that the wrong medication was given, or that a problem was wrongly put down to anxiety

In other words, these reviews get much closer to the question: did the care help, or did the patient feel less safe after it?

## What To Check Next

If the point is early warning rather than blame, the best next checks are:

- review a sample of flagged cases practice by practice, especially where there are repeated signals over time
- separate pure access-to-A&E diversion from cases where the reviewer also describes missed symptoms, wrong treatment, or worsening illness
- audit repeated themes around children, infections, chest pain, heavy bleeding, and medication safety
- review safety-netting language in triage and remote consultations, especially where patients say they were dismissed or told it was anxiety
- compare these signals with complaint files, SEA records, prescribing incidents, and any hospital feedback already held locally

## Bottom Line

The review corpus does contain a meaningful clinical-harm warning-sign layer.

It is not the dominant story in the data, but it is too large to ignore: `420` low-star reviews, spread across `125` practices, with `27` practices showing at least five such reviews. The sharpest signals are not about courtesy or convenience. They are about patients saying the diagnosis was wrong, the medication was wrong, the problem was brushed off, or the real outcome only became clear once they got sicker or reached hospital.

That is exactly the kind of thing a patient survey usually does not even ask.
