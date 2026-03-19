# Access Issues In The Review Corpus

This note uses the local fulltext review index over `16,293` plaintext Google reviews.

I counted a review as access-related if it mentions one or more of these main front-door problems:

- getting an appointment
- getting through by phone
- reception blocking or worsening access
- online forms or website routes not working well
- delays with callbacks, results, or referrals

This is a straight fulltext pass over the review text, not NLP. One review can hit more than one issue, so the issue counts below overlap.

## Headline

Access is not a small side problem in this corpus.

A broad pass finds `8,680` reviews, `53.3%` of all reviews, using main access language at all.

If I narrow that to `1` and `2` star reviews, `5,028` reviews, `30.9%` of all reviews, read as clear access complaints. That is the stronger number for judging how big the problem is, because it strips out a lot of mixed or positive reviews that still mention phones, appointments, or online forms in passing.

Put simply: about `1` in `3` reviews in the whole corpus is a low-rated review that raises a main access problem.

## What Patients Mostly Raise

### 1. Phone access

Phone access is the biggest single issue in the low-star access set.

`2,962` low-star reviews, `18.2%` of all reviews, mention phones, busy lines, long waits, dropped calls, or calls not being answered.

The same pattern shows up again and again: patients say they start with the phone because that is the route they are told to use, then hit an engaged tone, a long queue, or no answer at all. In many reviews the phone problem is the first failure that then leads to no appointment.

Practices with especially high low-star phone counts include:

- `Cheetham Hill Medical Centre`: `98`
- `The Robert Darbishire Practice`: `69`
- `The Arch Medical Practice`: `63`
- `Bolton Medical Centre`: `61`
- `The Bolton Family Practice`: `61`

Examples:

> "Never answer the phone"  
> Adam Crawford, `Droylsden Medical Practice`, `1` star

> "The surgery opens phone line 8 but the line be engaged till 845 when they answer say sorrry no available appointments left"  
> Saghir Akhtar, `Halliwell Surgery 2`, `1` star

> "not once did the staff answer the phone ... your phone lines are constantly busy throughout the whole day"  
> Georgia Mottershead, `Peel GPs`, `1` star

### 2. Appointment problems

Appointment access is almost as common as phone access.

`2,909` low-star reviews, `17.9%` of all reviews, mention appointment problems.

Patients do not just say appointments are hard to get. They often describe a cycle: try to call, fail to get through, finally get through, then get told there is nothing left. Some reviews talk about waits of weeks. Others say the only choice is to try again the next day and start over.

Practices with especially high low-star appointment counts include:

- `Cheetham Hill Medical Centre`: `72`
- `Chorlton Family Practice`: `71`
- `The Arch Medical Practice`: `64`
- `Rock Healthcare Limited`: `60`
- `Dickenson Road Medical Centre`: `57`

Examples:

> "Can never get an appointment"  
> David Chatterton, `Gordon Street Medical Centre`, `1` star

> "cant get appointment ... still can't get an early appointment, I been given one after one month"  
> Yamato K, `Kingsway Medical Practice`, `1` star

> "can't get through on the phone can't get an appointment they say use AskmyGp"  
> Liam, `Ashville Surgery`, `1` star

### 3. Reception as a barrier

Reception comes through as a major part of the access problem, not just a manners problem.

`2,279` low-star reviews, `14.0%` of all reviews, mention reception or receptionists.

These reviews often say the front desk feels rude, dismissive, or hard to deal with. More than that, patients often link reception behaviour to being blocked from care. In the review text, reception is where the access system becomes personal.

Practices with especially high low-star reception counts include:

- `Hawthorn MC`: `69`
- `Cheetham Hill Medical Centre`: `51`
- `The Robert Darbishire Practice`: `48`
- `Wellfield Medical Centre`: `47`
- `The Arch Medical Practice`: `45`

Examples:

> "Very rude, unprofessional reception staff"  
> Beth Richmond, `Mandalay Medical Centre`, `1` star

> "Reception staff so rude and unhelpful!!!!"  
> Hayley Ingham, `Mandalay Medical Centre`, `1` star

> "extremely rude reception staff"  
> Poopy Rosa, `Blackford House Medical Centre`, `1` star

### 4. Online forms and website routes

Online access is a smaller bucket than phones or appointments, but it is still a real and repeated problem.

`706` low-star reviews, `4.3%` of all reviews, mention online forms, websites, PATCHS, eConsult, or being pushed onto a digital route that does not work.

These reviews often read like patients are being bounced from one route to another. They are told to go online, but the form is shut, there is no reply, or the website route just pushes the same problem into a different queue.

Practices with especially high low-star online counts include:

- `The Robert Darbishire Practice`: `86`
- `Chorlton Family Practice`: `25`
- `Kingsway Medical Practice`: `25`
- `The Arch Medical Practice`: `23`
- `New Bank Health`: `21`

Examples:

> "Have to fill the forms in now to book an appointment."  
> Vladislav Miasnikov, `Heaton Medical Centre`, `1` star

> "ever since they stopped the online forms it is IMPOSSIBLE to get an appointment."  
> suzie sheep, `West Gorton Medical Practice`, `1` star

> "Never pick the phone and the website no give access for appointment"  
> mª cristina rodriguez morales, `Gorton Medical Centre`, `1` star

### 5. Follow-up, results, and referrals

This is the smallest of the five main buckets, but it may be the sharpest in its effect on patients.

`532` low-star reviews, `3.3%` of all reviews, mention waiting for results, callbacks, tests, or referrals.

These reviews are often about being left hanging after the first contact. The patient gets through one barrier, but the next step stalls: no callback, no result, no clear answer on a referral, or a long wait that seems to go nowhere.

Practices with especially high low-star follow-up counts include:

- `The Robert Darbishire Practice`: `19`
- `The Arch Medical Practice`: `17`
- `Chorlton Family Practice`: `14`
- `Guide Bridge Medical Practice`: `14`
- `New Bank Health`: `14`

Examples:

> "did not ring me although waiting blood and scan results"  
> nicola cooper, `Dr Y Loomba & Partner`, `1` star

> "Waited 6 months for a referral to be told it has not even been acknowledged."  
> Umer Raja, `West Point Medical Centre`, `1` star

> "they try to convince you by saying referrals are sent again where you have to wait more for a few months."  
> Saif Syed, `New Bank Health`, low-star review

## What The Pattern Looks Like In Practice

The access complaints are not neatly separated in real life. Patients often describe the same chain:

1. they try the phone and cannot get through
2. when they do get through, appointments have gone
3. they are told to use an online form instead
4. the online route does not solve it
5. they feel brushed off by reception
6. after that, even results, callbacks, or referrals can drift

That is why the issue counts overlap so much. Patients are not usually talking about one bad moment. They are describing a front door that feels hard to enter, hard to stay in, and hard to trust.

## GTD Context

The same pattern is strong in the GTD-managed slice too.

Across GTD-managed practices in this indexed set, `501` out of `830` reviews, `60.4%`, are low-star reviews that hit at least one of the main access buckets above.

`New Bank Health` fits that pattern. `77` of its `138` indexed reviews, `55.8%`, fall into the low-star access set. Within that:

- `49` mention appointment problems
- `39` mention phone access
- `34` mention reception
- `21` mention online routes
- `14` mention follow-up, results, or referrals

Examples from `New Bank Health`:

> "I had Alex hang up the phone on me ... when I hang up and call straight back with another number she'd answer"  
> Hafsa Bakari, low-star review

> "the admin/reception team here are something else, I totally agree with every complaint made against them in the reviews"  
> Hafsa Bakari, low-star review

> "if you have a complaint to fill in a feedback form or alternatively call to book an appointment, but when I called I was told the only way was to fill in a form"  
> Hafsa Bakari, low-star review

## Bottom Line

Access looks like one of the biggest problems in the whole review corpus.

On a broad mention basis, it shows up in just over half of all reviews. On a stricter complaint basis, it still shows up in nearly a third of the whole corpus.

The most common problems are:

- phones not being answered, being engaged, or dropping
- appointments being unavailable even after patients get through
- reception staff being described as rude, dismissive, or blocking
- online forms and website routes replacing older routes without working well enough
- weak follow-up on results, callbacks, and referrals

Read together, the reviews suggest that patients are not mainly saying "I had one bad appointment." They are saying it is hard to get in, hard to get heard, and hard to know what happens next.
