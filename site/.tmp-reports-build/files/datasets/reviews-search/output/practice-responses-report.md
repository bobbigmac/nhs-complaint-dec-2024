# Practice Responses To Reviews

This report looks at how practices reply to Google reviews, and how those replies differ between positive and negative reviews.

It is based on a rule-based pass over the review text in the local index. I split out review text from `Practice response date:` and `Practice response:` where present, then looked at:

- whether a response was attached at all
- whether the original review was positive (`4` or `5` star) or negative (`1` or `2` star)
- whether the response was mainly thanks, apology, boilerplate signposting, or something more specific
- whether the response used patient-blaming or deflecting language
- whether the response appeared quick or delayed, using the relative review and response dates where those could be roughly compared

This is not NLP and it is not a perfect legal reading of tone. But it is enough to show the main response patterns in the corpus.

## Headline

Practice responses are common, but uneven.

- `6,568` reviews in the corpus include a practice response
- that is `40.3%` of all `16,293` reviews
- `52.0%` of positive reviews got a response
- only `24.1%` of negative reviews got a response
- `35.3%` of `3` star reviews got a response

So practices are much more likely to answer praise than criticism.

That split is one of the clearest findings in the whole response layer.

## What Most Responses Look Like

The response layer is dominated by thanks and polite formulae, not by detailed public explanations.

Across all responses, my scan found:

- `5,459` with simple thanks or praise language
- `1,230` with apology language
- `808` with boilerplate signposting like "please contact the surgery", "fill in the form", or "use the website"
- only `22` with clear public signs of specific action such as "we reviewed", "we changed", "we updated", "we reminded staff", or similar
- `34` with stricter patient-blaming or deflecting markers

That last number is important. Direct blame is not the main response problem if you define it narrowly. The bigger issue is softer deflection: apology plus signposting, apology plus "contact us privately", apology plus "use the online route", apology plus "high demand".

So the bad response style is often not openly hostile. It is polite, managerial, and empty.

## Positive Reviews Versus Negative Reviews

### Positive review responses

Positive review responses are often fast, polite, and high volume.

Some practices answer almost every positive review:

| Practice | Positive response rate | Positive reviews responded to |
| --- | ---: | ---: |
| `LADYBARN GROUP PRACTICE` | `100.0%` | `265` |
| `The Sides Medical Practice` | `100.0%` | `257` |
| `The Arch Medical Practice` | `100.0%` | `114` |
| `Cornbrook Medical Practice` | `100.0%` | `72` |
| `Cherry Medical Practice` | `97.7%` | `42` |
| `Octagon Medical Centre` | `94.3%` | `182` |
| `The Range Medical Centre` | `92.6%` | `1,123` |

The good side of this is that some practices are clearly present and engaged in public.

The weak side is that many positive responses are very thin. A lot are just:

- thank you
- glad you had a positive experience
- I will pass this on to the team
- thanks for the 5 stars

That is not necessarily bad. It is just not very informative.

### Negative review responses

Negative review responses are much rarer, and much more likely to be defensive or generic.

Practices with high negative-response coverage include:

| Practice | Negative response rate | Negative reviews responded to |
| --- | ---: | ---: |
| `The Sides Medical Practice` | `100.0%` | `26` |
| `The Arch Medical Practice` | `100.0%` | `113` |
| `LADYBARN GROUP PRACTICE` | `98.0%` | `97` |
| `The Range Medical Centre` | `89.4%` | `84` |
| `Dickenson Road Medical Centre` | `82.4%` | `103` |
| `Octagon Medical Centre` | `77.0%` | `47` |
| `The Robert Darbishire Practice` | `75.2%` | `106` |

But high negative-response coverage does not mean high-quality response.

In practice, the negative review replies usually split into four types:

1. apology plus "contact us privately"
2. apology plus "use the website/form/front desk"
3. apology plus defence of capacity, policy, or process
4. rarer, genuinely useful explanation of what changed

## Patient-Blaming Language

Direct patient-blaming appears in a minority of responses, but softer blame and deflection appear much more often.

The strict blame patterns I found were:

- `16` responses using capacity-defence language like high demand, limited appointments, or NHS pressure
- `7` using eligibility or policy language
- `6` referring to lateness, attendance, or appointment behaviour
- `5` pushing the patient back onto the "correct" route or process

### What patient-blaming looks like here

It usually does not read like "this is your fault". It reads more like:

- your problem is the policy
- your problem is the route you used
- your condition was stable so next-day was safe
- you should have used the online form or another route
- we are under pressure like the rest of the NHS
- our records/policy do not support your version

That still matters, because it shifts the centre of gravity away from the patient’s account and back onto rules, systems, or the patient’s own behaviour.

### Examples of blame or deflection

`West Point Medical Centre`:

> "We have received a lot of positive feedback recently about our team ... NHS services can experience longer waiting times because of high demand."

This is not openly rude, but it clearly weakens the patient complaint by invoking other positive feedback and system pressure.

`The Robert Darbishire Practice`:

> "The fact that your appointment could be scheduled for the next day indicates your condition was stable and it was safe to do so."

This is one of the clearest examples of a response reinterpreting the patient’s urgency rather than engaging with the failure they described.

`Dickenson Road Medical Centre`:

> "if you need to order prescriptions you can order these online or drop the request off in the box in reception then you don’t need to wait in the telephone queue."

This is a common softer move in the corpus: the response turns the complaint back into instructions for the patient.

`The Arch Medical Practice`:

Some replies are highly detailed but still contain elements of patient correction, for example laying out why a letter could not be provided, why a sample could not be accepted, or why a certain route was appropriate. These are more substantial than generic replies, but they can still feel defensive.

## Boilerplate And Signposting

This is the most common failure mode in negative replies.

I found `808` responses with boilerplate signposting language. That includes replies such as:

- "please contact the surgery"
- "speak to the practice manager"
- "use the website"
- "fill in the feedback form"
- "we have a complaints process"

These replies often sound serious, but they do not answer the public complaint in any real way.

### Practices where boilerplate is especially strong

On the face of the response text, these practices stand out for high-volume but generic negative replies:

| Practice | Negative responses | Negative boilerplate replies | Bad negative replies |
| --- | ---: | ---: | ---: |
| `Dickenson Road Medical Centre` | `103` | `84` | `84` |
| `Bolton Medical Centre` | `66` | `27` | `27` |
| `The Bolton Family Practice` | `66` | `27` | `27` |
| `The Arch Medical Practice` | `113` | `43` | `43` |
| `Cheetham Hill Medical Centre` | `73` | `28` | `28` |
| `Droylsden Medical Practice` | `27` | `26` | `26` |
| `Spring View Medical Centre` | `26` | `10` | `10` |
| `Guide Bridge Medical Practice` | `18` | `18` | `18` |

What these have in common is not silence. It is response without resolution.

## Who Does Better Responses

Truly good negative responses are rare in this corpus. My scan only found `9` responses across the whole dataset that clearly acknowledged the issue and publicly described a concrete action or improvement without dropping into blame or boilerplate.

That is tiny.

The best examples I found were:

### `Chorlton Family Practice`

This practice does not answer most negative reviews, but the better replies it does give are among the more useful in the corpus.

Examples:

> "we have changed our appointment system recently and improved our telephone system"

> "We have introduced a dedicated online booking window (3 hours in the morning) to manage the high volume of online requests"

That is useful because it tells the public what changed.

### `The Sides Medical Practice`

This practice replies to everything, and one of its stronger negative responses openly admitted delay and described a process review:

> "We have reviewed our processes to ensure clearer communication about flu clinics and appointment scheduling for our elderly patients."

This is the kind of sentence that is too rare across the corpus.

### `Cherry Medical Practice`

Smaller volume, but some signs of clearer action language rather than pure signposting.

### `The Arch Medical Practice`

This is the most mixed case.

On the good side, it has some of the longest and most specific responses in the corpus. In its best replies it explains what happened, what signage or systems changed, and what staff were reminded about.

On the bad side, it also produces long defensive replies that read like a public rebuttal. So it is engaged, but not always well-balanced.

## Who Does Worse Responses

The weaker group is easier to describe.

### Prompt but generic

Some practices reply fast, including to negative reviews, but mainly with managerial templates:

- `Bolton Medical Centre`
- `The Bolton Family Practice`
- `Guide Bridge Medical Practice`
- `Gordon Street Medical Centre`
- `Droylsden Medical Practice`

The characteristic wording is:

- sorry you felt this way
- please contact the surgery
- speak to the assistant practice manager
- we will investigate if you contact us

These practices are present, but not very open in public.

### High-volume but delayed

Some practices answer huge numbers of reviews but seem to do so later:

| Practice | Approx average response delay |
| --- | ---: |
| `The Birches Medical Centre` | `14.1` months |
| `Dickenson Road Medical Centre` | `11.1` months |
| `The Range Medical Centre` | `8.5` months |
| `LADYBARN GROUP PRACTICE` | `5.1` months |
| `The Sides Medical Practice` | `5.0` months |

This delay estimate is rough because it is based on relative date strings, but it is still enough to show a difference between fast-turnaround responders and later catch-up responders.

### Defensive and patient-correcting

These practices stand out more for deflecting or patient-blaming language:

- `West Point Medical Centre`
- `The Robert Darbishire Practice`
- `Barlow Medical Centre`
- `Eastlands Medical Centre`
- `Brooklands Medical Practice`

The shared pattern here is not always harsh language. It is a tendency to answer criticism by:

- citing high demand
- invoking policy
- explaining why the practice route was reasonable
- implying the patient should have used another route
- reframing the event as stable, non-urgent, or properly handled

## Practices That Reply To Praise More Than Criticism

Some practices show a very large gap between response rates to positive and negative reviews:

| Practice | Positive response rate | Negative response rate | Gap |
| --- | ---: | ---: | ---: |
| `Middleton Health Centre` | `85.6%` | `22.9%` | `62.7` points |
| `The Park Medical Centre` | `67.2%` | `10.6%` | `56.6` points |
| `Peel Hall Medical Centre` | `89.1%` | `45.7%` | `43.4` points |
| `Cheetham Hill Medical Centre` | `87.5%` | `44.2%` | `43.3` points |
| `West Point Medical Centre` | `89.3%` | `47.2%` | `42.1` points |

This kind of gap matters because it suggests some practices are using review replies more as reputation management than as a balanced public conversation.

## Characteristics Of The Better Group

The better responses tend to have these features:

- they reply to negative reviews as well as positive ones
- they say what changed, not just who to contact
- they name a process, system, or communication change
- they do not tell the patient to simply re-enter the same route that already failed
- they do not lean heavily on high demand as the main answer
- they often sound written by a named person, not a template

## Characteristics Of The Worse Group

The weaker responses tend to have these features:

- very high use of apology-plus-signposting
- lots of "please contact the surgery" with no public substance
- website, form, or complaints-process redirection
- capacity-defence language like "high demand", "limited appointments", or "NHS pressures"
- occasional correction of the patient’s account or public reinterpretation of urgency
- much stronger engagement with praise than with criticism

## Bottom Line

The response layer is active, but not especially accountable.

Practices are much more likely to answer positive reviews than negative ones. Where they do answer criticism, the common pattern is not abuse but polite deflection: apology, private contact, website form, complaints process, or explanation of pressure.

Direct patient-blaming exists, but the bigger issue is softer blame and route-defence. The public message often becomes: use the correct channel, understand the pressure we are under, contact us privately, and we will look into it.

Truly useful public responses are rare. The best ones explain what changed. Most do not.
