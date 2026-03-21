# Practice Responses To Reviews

This report looks at how practices reply to Google reviews, and how those replies differ between praise and criticism.

It is based on a refreshed rule-based pass over the rebuilt local index. I split review text from `Practice response date:` and `Practice response:` where present, then looked at:

- whether a response was attached at all
- whether the original review was positive, negative, or mixed
- whether the response was mainly thanks, apology, boilerplate signposting, or something more specific
- whether the response used patient-blaming or deflecting language
- whether the response appeared quick or delayed, using relative review and response dates where that could be compared

This is not NLP and it is not a perfect legal reading of tone. But it is enough to show the main response patterns in the enlarged corpus.

## Headline

Practice responses are common, but still very uneven.

In the rebuilt `40,506`-review corpus:

- `16,756` reviews include a practice response
- that is `41.4%` of all reviews
- `50.8%` of positive reviews got a response
- only `23.8%` of negative reviews got a response
- `33.0%` of mixed reviews got a response

So practices are still much more likely to answer praise than criticism.

That remains one of the clearest findings in the whole response layer.

## What Most Responses Look Like

The response layer is still dominated by thanks and polite formulae, not by detailed public explanation.

Across all responses, the refreshed scan found:

- `13,237` with thanks or praise language
- `2,400` with apology language
- `1,682` with boilerplate signposting like "please contact the surgery", "speak to the practice manager", "use the website", or "fill in the form"
- only `141` with clearer specific-action language
- `66` with stricter patient-blaming or deflecting markers
- `54` with privacy-defence language

That last number matters, but direct blame is still not the main response problem if you define it narrowly. The bigger issue is softer deflection:

- apology plus private contact
- apology plus signposting
- apology plus "use the online route"
- apology plus "high demand"

So the bad response style is usually not openly hostile. It is polite, managerial, and empty.

## Positive Reviews Versus Negative Reviews

### Positive review responses

Some practices answer virtually every positive review:

| Practice | Positive response rate | Positive reviews responded to |
| --- | ---: | ---: |
| `LADYBARN GROUP PRACTICE` | `100.0%` | `265` |
| `The Sides Medical Practice` | `100.0%` | `257` |
| `The Arch Medical Practice` | `100.0%` | `114` |
| `Cornbrook Medical Practice` | `100.0%` | `72` |
| `Whitley Road Medical Centre` | `100.0%` | `60` |
| `Culcheth Medical Centre` | `100.0%` | `44` |
| `Bredbury Medical Centre` | `99.7%` | `380` |
| `Peterloo Medical Centre` | `99.4%` | `155` |

The good side of this is obvious: some practices are very present in public.

The weak side is that many positive responses are still very thin:

- thank you
- glad you had a positive experience
- thanks for the stars
- we will pass this on to the team

That is not necessarily bad. It is just not very informative.

### Negative review responses

Negative review responses are still much rarer, and much more likely to be defensive or generic.

Practices with especially high negative-response coverage now include:

| Practice | Negative response rate | Negative reviews responded to |
| --- | ---: | ---: |
| `The Arch Medical Practice` | `100.0%` | `113` |
| `Peterloo Medical Centre` | `100.0%` | `71` |
| `Littletown Family Med Pract` | `100.0%` | `34` |
| `Whitley Road Medical Centre` | `100.0%` | `27` |
| `The Sides Medical Practice` | `100.0%` | `26` |
| `LADYBARN GROUP PRACTICE` | `98.0%` | `97` |
| `St Andrews Medical Centre` | `96.5%` | `82` |
| `The Range Medical Centre` | `89.4%` | `84` |

But high negative-response coverage still does not mean high-quality response.

In practice, the negative replies still mostly split into four types:

1. apology plus "contact us privately"
2. apology plus "use the website/form/front desk"
3. apology plus defence of capacity, policy, or process
4. rarer, genuinely useful explanation of what changed

## Patient-Blaming Language

Direct patient-blaming still appears in a minority of responses, but softer blame and route-defence appear much more often.

The stricter blame-mode counts in the refreshed scan were:

- `35` capacity-defence responses
- `11` eligibility or policy responses
- `10` wrong-route or process responses
- `8` attendance or lateness responses
- `2` records-based denials

### What patient-blaming looks like here

It usually does not read like "this is your fault". It reads more like:

- your problem is the policy
- your problem is the route you used
- you should have used the online form
- we are under pressure like the rest of the NHS
- our records do not support your version
- the fact you were seen the next day means it was safe

That still matters, because it shifts the centre of gravity away from the patient account and back onto rules, systems, or the patient’s own behaviour.

### Where it shows up most

The strongest negative patient-blaming counts in the current pass were:

- `The Robert Darbishire Practice`: `5`
- `West Point Medical Centre`: `5`
- `Cheadle Medical Practice`: `3`
- `Millgate Healthcare Partnership`: `3`
- `Barlow Medical Centre`: `2`
- `New Islington Medical Centre`: `2`

Example patterns:

`The Robert Darbishire Practice`:

> "The fact that your appointment could be scheduled for the next day indicates your condition was stable and it was safe to do so."

`West Point Medical Centre`:

> "We have received a lot of positive feedback recently about our team ... NHS services can experience longer waiting times because of high demand."

`The Brooke Surgery`:

> "If this situation ever arises again, please use our online service ..."

That last example is not overt blame, but it is a classic soft-deflection move: the complaint is turned back into instructions for the patient.

## Boilerplate And Signposting

This is still the most common failure mode in negative replies.

The refreshed scan found `1,682` responses with boilerplate signposting language.

That includes replies such as:

- please contact the surgery
- ask to speak with the practice manager
- use the website
- fill in the feedback form
- follow the complaints process

These replies can sound serious, but they usually do not answer the public complaint in any real way.

### Practices where boilerplate is especially strong

On the current response text, these practices stand out for high-volume but generic negative replies:

| Practice | Negative responses | Negative boilerplate replies | Bad negative replies |
| --- | ---: | ---: | ---: |
| `Dickenson Road Medical Centre` | `103` | `84` | `84` |
| `Shanti Medical Centre` | `82` | `46` | `46` |
| `The Arch Medical Practice` | `113` | `43` | `43` |
| `Salford Primary Care Together - Little Hulton` | `51` | `40` | `40` |
| `Cheetham Hill Medical Centre` | `73` | `28` | `28` |
| `Bolton Medical Centre` | `66` | `27` | `27` |
| `The Bolton Family Practice` | `66` | `27` | `27` |
| `Droylsden Medical Practice` | `27` | `26` | `26` |

What these have in common is not silence. It is response without resolution.

## Who Does Better Responses

Truly useful negative responses are still rare, but they do exist.

The current pass found the strongest negative specific-action signals at:

- `The Quays Practice`: `3`
- `The Arch Medical Practice`: `2`
- `Cherry Medical Practice`: `2`
- `Cheadle Medical Practice`: `2`
- `Ailsa Craig Medical Centre`: `2`
- `The Chowdhury Practice`: `2`
- `Chorlton Family Practice`: `2`

That is still small compared with the total response layer.

The useful pattern is simple. Better replies tend to:

- acknowledge the complaint
- say what changed
- name a process or communication change
- avoid simply telling the patient to re-enter the same failed route

The older best-case examples still fit the refreshed corpus:

- `Chorlton Family Practice` giving public change-language about appointment and telephone systems
- `The Sides Medical Practice` describing process review rather than pure signposting
- `The Arch Medical Practice` sometimes giving long, concrete explanations rather than just a management template

## Who Does Worse Responses

The weaker group is easier to describe.

### Prompt but generic

Some practices reply fast, including to negative reviews, but mostly with managerial templates rather than useful public substance.

`Shanti Medical Centre` is a good example of this pattern in the enlarged corpus: high coverage, quick turnaround, but heavy repetition of the same "please contact the assistant practice manager" wording.

### High-volume but delayed

Some practices answer huge numbers of reviews, but often much later:

| Practice | Approx average response delay |
| --- | ---: |
| `Peterloo Medical Centre` | `18.4` months |
| `The Birches Medical Centre` | `14.1` months |
| `Conway Road Medical Practice` | `12.8` months |
| `BARRINGTON MEDICAL CENTRE` | `12.7` months |
| `Whitley Road Medical Centre` | `12.5` months |
| `Dickenson Road Medical Centre` | `11.1` months |
| `The Range Medical Centre` | `8.5` months |

This delay estimate is rough because it is based on relative date strings, but it is still enough to show the difference between fast-turnaround responders and later catch-up responders.

### Replies to praise much more than criticism

Some practices still show very large positive-versus-negative response gaps:

| Practice | Positive response rate | Negative response rate | Gap |
| --- | ---: | ---: | ---: |
| `Conway Road Medical Practice` | `97.7%` | `14.8%` | `82.9` points |
| `Norden Branch Surgery` | `89.4%` | `12.5%` | `76.9` points |
| `Padgate Medical Centre` | `79.7%` | `8.8%` | `70.9` points |
| `Denton Medical Practice` | `84.1%` | `20.4%` | `63.7` points |
| `Middleton Health Centre` | `85.6%` | `22.9%` | `62.7` points |
| `The Park Medical Centre` | `67.2%` | `10.6%` | `56.6` points |

This kind of gap matters because it suggests some practices are using review replies more as reputation management than as a balanced public conversation.

## Characteristics Of The Better Group

The better responses tend to have these features:

- they reply to negative reviews as well as positive ones
- they say what changed, not just who to contact
- they name a process, system, or communication change
- they do not tell the patient to simply re-enter the same route that already failed
- they do not lean too heavily on high demand as the main answer
- they sound written by a person rather than dropped in from a template

## Characteristics Of The Worse Group

The weaker responses tend to have these features:

- very high use of apology-plus-signposting
- lots of "please contact the surgery" with no public substance
- website, form, or complaints-process redirection
- capacity-defence language like "high demand" or "NHS pressures"
- occasional public correction of the patient account or reinterpretation of urgency
- much stronger engagement with praise than with criticism

## Bottom Line

The response layer is active, but still not especially accountable.

Practices are much more likely to answer positive reviews than negative ones. Where they do answer criticism, the common pattern is still not abuse but polite deflection: apology, private contact, website form, complaints process, or explanation of pressure.

Direct patient-blaming exists, but the bigger issue is softer blame and route-defence. The public message often becomes: use the correct channel, understand the pressure we are under, contact us privately, and we will look into it.

Truly useful public responses are still rare. The better ones explain what changed. Most still do not.
