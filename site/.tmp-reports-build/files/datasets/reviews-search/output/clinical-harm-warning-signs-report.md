# Clinical Harm Warning Signs In Google Reviews

This report looks for reviews that sound like possible clinical harm, not just bad service.

The aim is still not to prove wrongdoing from reviews alone. It is to flag where the enlarged review corpus contains warning signs that deserve checking in notes, complaints, SEA work, prescribing audit, and local quality review.

This is also still one of the clearest gaps in the national patient survey. Patients are asked about access, confidence, and experience, but not plainly whether they felt misdiagnosed, got the wrong treatment, became more unwell after contact, or ended up in hospital after being dismissed.

## What I counted

I took a cautious pass through the rebuilt indexed review corpus and focused on `1` and `2` star reviews only.

I stripped practice-response text where possible, then flagged reviews with one or more of these markers:

- direct mention of misdiagnosis or wrong diagnosis
- direct mention of wrong or unsafe medication
- negligence, dangerous, or unsafe language
- being ignored, dismissed, or not listened to when that was linked to worsening or escalation
- ending up in hospital, A&E, or emergency care in a clinically connected way
- severe outcome terms like sepsis, pneumonia, cancer, meningitis, appendicitis, stroke, heart attack, or "nearly died"

These categories overlap. One review can hit several at once.

## Headline Findings

In the rebuilt `40,506`-review corpus:

- `872` low-star reviews were flagged as clinical-harm warning signals
- that is `2.2%` of all reviews
- it is `6.4%` of all `13,615` low-star reviews

Category counts inside that flagged set:

- `57` mention misdiagnosis or wrong diagnosis
- `34` mention wrong or unsafe medication
- `236` use negligence, dangerous, or unsafe language
- `159` link dismissal or not being listened to with a bad outcome
- `363` describe hospital or urgent escalation in a clinically connected way
- `190` mention a severe condition or near-miss term

This is not the main story in the corpus. But it is far too much to write off as noise, especially because these are not ordinary complaints about phones, queues, or rude reception. These are the reviews where patients say care itself may have gone badly wrong.

## Extension: Reported Harm To Real Patients

The warning-sign pass above is about possible failure in care. The more serious extension question is outcome:

When reviewers say something went badly wrong, how often do they also say a real person got sicker, waited too long, missed needed care, ended up in hospital, or faced a serious health consequence?

Again, these are reported accusations in reviews, not proven findings. But they matter because they describe harm in patient terms rather than service terms.

### Outcome-led findings

- `143` flagged reviews describe delayed or postponed care in a way the reviewer links to harm
- `36` explicitly say the patient got worse, deteriorated, or became more unwell
- `34` say treatment, prescribing, or missed treatment actively made the patient more ill
- `366` describe hospital, A&E, ambulance, or emergency escalation in clinically connected situations
- `178` mention a serious condition, near miss, or life-threatening consequence

These buckets overlap heavily. The same review may describe delay, then deterioration, then hospital admission.

## The Main Warning-Sign Themes

### 1. Misdiagnosis and wrong diagnosis

I found `57` flagged reviews with direct misdiagnosis or wrong-diagnosis language.

These reviews are often short and blunt. Patients do not usually write in careful clinical terms. They write things like:

- misdiagnosed me twice
- refused face to face and would not listen
- kept saying it was something minor
- later it turned out to be something serious

Examples:

> "Misdiagnosed earlier in the year resulting in complications that required further treatment and discomfort"  
> Lachlan Pollock, `The Alexandra Practice`, `2 years ago`

> "Misdiagnosed for over TWO years because doctors refused face to face appointments and wouldn't listen."  
> Nicola Skinkis, `St. Andrew's House Surgery`, `2 years ago`

> "Be careful with this practice, misdiagnosed my uncle after months of going back and forth."  
> Ste Minator, `RADCLIFFE MEDICAL PRACTICE`, `3 years ago`

This is one of the clearest survey gaps. Survey tools can ask whether a patient had confidence in the clinician. They do not ask whether the patient later found out the diagnosis was wrong.

### 2. Wrong medication, wrong dose, or unsafe prescribing

I found `34` flagged reviews with direct wrong-medication or unsafe-medication language.

This is a smaller theme than access, but it is one of the sharpest.

Examples:

> "Ended up in hospital and was told by consultant that my esophagus was damaged because of wrong medication."  
> Logic Errors, `HEALEY SURGERY`, `6 years ago`

> "gave her the wrong medication and yet again she is now in hospital with sepsis"  
> Kerrie, `St Andrews Medical Centre`, `6 years ago`

> "constantly giving wrong diagnosis and medication which has lead to multiple ae trips that could have been prevented"  
> Gym Bruh, `The Park Medical Centre`, `a year ago`

This is worth separating from routine prescription-delay complaints. Delays are common admin problems. Wrong medicine, wrong dose, or medicine linked to bodily harm are different.

### 3. Dismissal, not being listened to, then something bad happening

I found `159` flagged reviews where dismissal language was tied to a harmful outcome or clinically serious consequence.

This is one of the strongest patterns in the corpus. Patients often say the main problem was not only access. It was that once they did get through, they felt waved away, told it was nothing, or pushed elsewhere without real assessment.

Examples:

> "My daughter ended up in hospital with sepsis because we weren't being listened to."  
> Jill Bamber, `The Gill Medical Practice`, `2 years ago`

> "Doctors DO NOT listen to you or follow notes from previous doctors."  
> Heather Hayes, `Gorton Medical Centre`, `a year ago`

> "Misdiagnosed for over TWO years because doctors refused face to face appointments and wouldn't listen."  
> Nicola Skinkis, `St. Andrew's House Surgery`, `2 years ago`

This is why the review corpus matters here. The patient is not just saying "I felt brushed off." They are saying "I felt brushed off and then something bad followed."

### 4. Hospital, A&E, or emergency escalation after GP contact

This is the biggest outcome signal in the whole pass.

I found `363` flagged reviews with hospital or urgent-escalation language, plus `190` with severe condition or near-miss language.

Examples:

> "ended up collapsing at home and rushed to hospital"  
> M3RITz UK, `St Andrews Medical Centre`, `3 years ago`

> "ended up in hospital for a week with heart failure"  
> Gk Saynomore, `Ashton Medical Group`, `6 days ago`

> "I ended up in hospital because I just couldn't reach anyone to get antibiotics for a simple infection."  
> Lija Harper, `Wilmslow Road Surgery`, `3 years ago`

> "Took my 3yr old and they missed an infection and ended up in hospital."  
> Laura Bath, `Chorlton Family Practice`, `8 years ago`

Even allowing for exaggeration in some reviews, this is the part of the corpus that is hardest to dismiss as ordinary frustration. The language is repeatedly about emergency rescue, serious illness, and consequences patients understood as threats to life or long-term health.

## Reported Harm To Real Patients

### Delayed care linked to harm

The current pass found `143` reviews where the complaint was not just "it took too long", but "it took too long and harm followed".

This is where admin and clinical risk blur together. A missed callback, delayed antibiotic, weeks waiting for medication, or repeated failure to arrange review may begin as a process issue. In the reviews, patients describe that delay as part of the route to becoming more unwell.

### Reviewers saying they got worse

The stricter worsening bucket found `36` reviews explicitly using "got worse", "deteriorated", or equivalent language.

That is still a tight count. Many more reviews imply worsening without using the exact words.

### Reviewers saying care or treatment made them more ill

I found `34` reviews where patients directly linked treatment, prescribing, or failure to provide the right treatment with becoming more ill.

That is one of the clearest high-risk themes in the corpus because the reviewer is not only unhappy. They are saying the intervention itself, or the failure to intervene properly, caused bodily harm.

## Repeated Practice Signals

The fairest way to use this material is not to single out one dramatic quote. It is to look for repeated warning-signal reviews across different patients.

Among the strongest repeated current clusters in the rebuilt index are:

| Practice | Flagged signal reviews | Share of all reviews |
| --- | ---: | ---: |
| Ashton Medical Group | 16 | 1.6% |
| The Robert Darbishire Practice | 14 | 5.8% |
| Chorlton Family Practice | 12 | 1.3% |
| Florence House Medical Practice | 10 | 8.3% |
| Hawthorn MC | 10 | 3.9% |
| Droylsden Road Surgery Branch | 9 | 12.7% |
| Cheetham Hill Medical Centre | 9 | 2.8% |
| Lime Square Medical Centre | 8 | 6.6% |
| Northenden Group Practice | 8 | 6.2% |
| Salford Primary Care Together - Little Hulton | 7 | 5.7% |
| Rock Healthcare Limited | 7 | 5.3% |
| STONEHILL MEDICAL CENTRE | 7 | 5.0% |

This should not be read as a league table of unsafe practices. It is a short list of where the review corpus is giving repeated enough warning signals that a human check looks justified.

## What Makes These Reviews Different From Ordinary Complaints

Most bad reviews in the dataset are still about access, rude interactions, repeat prescriptions, or call queues.

The warning-sign subset feels different in both tone and content:

- patients talk about getting worse, not just waiting longer
- patients name clinical consequences such as sepsis, appendicitis, infection, heart failure, cancer, heavy bleeding, or hospital admission
- patients often contrast the GP interaction with what happened later in A&E, hospital, private care, or after seeing another clinician
- some reviews explicitly say a serious condition was missed, the wrong medication was given, or the problem was wrongly waved away

In other words, these reviews get much closer to the question: did the care help, or did the patient feel less safe after it?

## What To Check Next

If the point is early warning rather than blame, the best next checks are still:

- review a sample of flagged cases practice by practice, especially where there are repeated signals over time
- separate pure access-to-A&E diversion from cases where the reviewer also describes missed symptoms, wrong treatment, or worsening illness
- audit repeated themes around children, infections, chest pain, heavy bleeding, cancer suspicion, and medication safety
- review safety-netting language in triage and remote consultations, especially where patients say they were dismissed or told it was anxiety
- compare these signals with complaint files, SEA records, prescribing incidents, and any hospital feedback already held locally

## Bottom Line

The enlarged review corpus still contains a meaningful clinical-harm warning-sign layer.

It is not the dominant story in the data, but it is too large to ignore: `872` low-star reviews, `2.2%` of the whole corpus and `6.4%` of all low-star reviews. The sharpest signals are not about courtesy or convenience. They are about patients saying the diagnosis was wrong, the medication was wrong, the problem was brushed off, or the real outcome only became clear once they got sicker or reached hospital.

That is exactly the kind of thing a patient survey usually does not even ask.
