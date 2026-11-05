## 1

Take a look at @datasets/reviews-analysis , we're going to work on the classifier. The dataset currently tries to heuristically bucket items, but I think that's kinda the wrong way to do it. Instead we should build a basic graph data structure that uses the review texts and word-meaning similarities (synonyms, NLP, I think compromise has stuff for this) to allocate each review as how similar it is to other reviews (and maybe other metrics like sentiment), then from that map we can extract the closest clusters, bucket those dynamically and catch the rest with either heuristics (which can be improved with further analysis of the rejects/leftovers). Write a script that can build the dataset for that and query it to see if what that can give us is interesting. Do NOT predefine a dictionary of keywords that shape our dataset, the idea is we broaden what we are capable of understanding from our source data by not forcing a shape onto it). Write this up as CLASSIFIER_MODEL.md and then implement it. This might not be _as portable_ to the front end for recomputes, so we will probably instead have this output to a stable json that has assigned classes logged in a way the browser can use them to change presentations without  a lot of bloat or duplication.

## 2

no stdlib-only fallback. What we want to work has to work, in an environment where the scikit-learn cannot be used, we should have committed a usable copy of the last output generated on the dev-machine to use as a fallback. Also, don't hardcode a stopwords list, import one. Our input is from natural reviews, whcih does not use formal writing at all, so we need to treat it as messy and work a little harder to understand the real text, not fake a model over it.

## 3

okay run it for me, then a build

## 4

inspect the output (I think you need a helper to get back basically the same information the client-side is seeing, but with the raw reviews raw text included for your own perusal of group members), so you can tweak the clustering algorthm, maybe add/remove some watch/warn-words and tune it a little, and so you can write up some sensible category titles that accurately represent/summarise their composited/consolidated-list-titles.

## 5

label_overrides can very quickly be misleading when the indexes change, we can't include that approach, it's too easily wrong. Keep the literal labels for now.

## 6

run it a few times and inspect the underlying sources, iterate on the classifier a few times based of a pretty thorough examination of the unerlying data

## 7

`Result: 3726 uncategorised, 649 clustered, largest cluster c5=262 ("thank, staff, friendly, helpful")` is unacceptable. Every review that can be categorised with some confidence should be, the entire point of indexing against the free-text is to catch what's lost, so you can do much better here.

## 8

ah, you're not actually parsing reviews to user/text/review, but should be. Look earlier in the chain and imporve the importer. You can't rerun the collector, so you need to improve the importer within reviews-analysis, not th eoriginal recorder/scraper.

## 9

ah, you're not actually parsing reviews to user/text/review, but should be. Look earlier in the chain and imporve the importer. You can't rerun the collector, so you need to improve the importer within reviews-analysis, not th eoriginal recorder/scraper.

## 10

okay, now run the classifier iteration and try to catch any review that has meaningful content and assign it to its most likely bucket based on our various available analysis methods.

## 11

can we use this? Does it have any reputation for  being useful or distracting? is this a good library for this task?https://datasciencecampus.ons.gov.uk/projects/optimus-a-natural-language-processing-pipeline-for-turning-free-text-lists-into-hierarchical-datasets/ I feel like this would solve our 'lots of groups of 1-2' problem, and might help us bucket things so they make a lot more sense to regular people as related areas, because they can refer to different layers.

## 12

I don't want users to have to drill down, I want the tree to be able to present itself in useful chunks organically. Keep our current approach we have now, but I think some of the clusters can be collapsed or grown based on number of found matches (I suspect there is a fixed distance for cluster allocation, but it should probably grow until it has at least n matches for a tunable n). This kinda lets us accept that issues at various scales express slightly differently (an example might be 'absolutely disgusting' and 'absolute disgrace' don't get bucketed together, but they're probably pretty close in our graph's vector coords).

## 13

what about this library? https://github.com/datasciencecampus/classifai  that org seems to have a bunch of stuff that might be useful for us... poke around and see if their Optimus project or similar can be useful for us here.

## 14

@CLASSIFIER_MODEL.md (11-539)

## 15

positive feedback shouldn't be a category unless it has no other category to go into, in which case it should be treated as gratitude

## 16

gratitude is a bit too opinionated, can we dry that out a little, it's more 'grateful/positive vibes/cheering/gratefulness' but I need a professional word

## 17

put the views toggles in their own row, not on the same row as stats/span/sort (also lose the squares from sort squares)

## 18

found an obvious miscategorised, presumably bucketing error ```Hattersley Group Practice · Ash Ford · 1 star · a year ago
×
Had bloods done. Did bloods for the wrong thing and they tried to get me in for my iron. I’m ALLERGIC!! Taking iron supplement etc causes me anaphylaxis !!
Positive feedback › Appreciation | helpful efficient, efficient, helpful, rang, neede...```

## 19

There should be toggle for "Exclude Non-GTD" which exlcludes those not within the gtd-takeover period, i.e. those reviews made under other operators/management. This really only affects a few practices with recent takeovers, but it is relevant so we should support hiding those non-gtd-events (disabled by default).

## 20

lol, good, but a bug, my review [REDACTED] is being detected twice, probably cos our dataset has both recent reviews from one file and recent reviews in all reviews for others, so we're porbably duplicating some (maybe all) recent reviews. The earlier steps of this process should probable be sure to dedupe reviews where possible.

## 21

lol, good, but a bug, my review [REDACTED] is being detected twice, probably cos our dataset has both recent reviews from one file and recent reviews in all reviews for others, so we're porbably duplicating some (maybe all) recent reviews. The earlier steps of this process should probable be sure to dedupe reviews where possible.

## 22

on hover a review square, update the title bar of the panel that contains it to the name and review text of the review (with tex-overflow set so longer ones dont resize the container), just as a quick preview. Also make the squares and their font a bit bigger.

## 23

reviews like this are being bundled into clinical care, but are about much more than that. We should a) reprioritise what category is considered the primary category based on detected claims, and b) support a flag that shows each review as multiple squares, one in each category it has any assignment for, like so we get an idea of total bulk about that, even where it's also about other things. I'm not sure if our classifier actually saves multiple categories though. What do you think?
```Gordon Street Medical Centre · S · 1 star · 6 years ago
×
Very hard to get an appointment when you phone in the morning it's engaged when you get through they say they are fully booked but won't make an appointment for another day you have to phone and try again the following morning and it's always the same can't get through and when you do all full.
Clinical care › Clinical quality | staff, helpful, service, doctors, thank```

## 24

does this have anything relevant for us? https://arxiv.org/html/2410.01305v1

## 25

show in all categories has no change, but not sure if it's down tot he ui or the data. Rerun the build and check

## 26

when teh panel title is filled with review text, it should be the actual text of the review, no name needed, and should use the full width of the panel avialable to it, not an artificially clipped region

## 27

lol, that forces the parent to grow, reflowing the doc

## 28

that still forces some (if th container is less width than its parent) to reflow.

## 29

our dataset has a few reviews that are actually responses to reviews made by people. That have been misparsed on the way in. Can you check our dataset for them (they usually say something like "thank you [name] for your [kind] feedback", or sometims "sorry you had that experience", with some extra bullshit. I don't want to remove them, but I do want to find them in our dataset and tag them with a meta property as 'practice-replies' so we don't intgrate their scores (and can hide them by default). Can you have a poke around our dataset and find the cases i'm refeerring to, and special-case them in our code to categorise them differently, as they are not real reviews)

## 30

I don't want you to try and heiristically detect them. I want you to flag those exact cases that YOU found, from a refernce file, that can be updated after future runs. No heuristic.

## 31

I don't want you to try and heiristically detect them. I want you to flag those exact cases that YOU found, from a refernce file, that can be updated after future runs. No heuristic.

## 32

add to our dataset builder's code a todo that should detect and explicitly store/report practice replies as not really reviews.

## 33

date_raw shouldnt be in the comparison/assigner, as it will change with every scan (it's not the date, it's an ago).

## 34

@/home/bobbigmac/.cursor/projects/home-bobbigmac-projects-nhs-complaint-dec-2024/terminals/1.txt:542-594 bug in the classifier?

## 35

scikit-learn shouldn't be missing, if it is, it should be falling back to the cached file that was most recently produced on a system (dev machine) where it wasn't missing.

## 36

that's stupid. Don't make the build handle packages (we discussed way earlier) just install it so it can use it, and make sure it works.

## 37

Remove the Squares view, keep only the Treemap view (and remove the View label) since we don't need a toggle anymore, and it's not really a treemap anyway. That row now starts with group.

## 38

this should still run on github actions right? even with the lib? or will you need to tweak the action and make sure to fallback to the safe last-dev-machine-generated copy so we don't have to do the full work on the action if we can't?

## 39

"Show in all categories" doesn't apply when in "Cluster evidence" theme. Just hide the check then.

## 40

When in Consolidated Operational view and Show in all categories is selected, each group panel should have an AI written summary of the issues raised based off the collection of reviews allocated to that set. This applies to the GTD-consolidated set of panels only. You will need to query this from our dataset and write your commentary for each of access, reception and front desk, clinical care, and so on, for groups with more than 1 member reviews. You can write these summaries based on the set slug to a markdown file, for a single source of truth in /datasets/reviews-analysis/ that the build can use to write json that the front-end can use to decorate each of those panels with the summary. It probably makes sense to first write out a md manifest for those slugs and then for each, query our model used to form the ui elements, and write the summaries into that after querying each subset. Think like a one-off generated summary of that particular state's set of reviews, which you need to group and query one group at a time to write a pretty decent summary of issues and an indication of prevalence in the set for issues raised across that kind for that gtd-consolidated group of panels.

## 41

don't call openai. Thats not what I said to do.

## 42

now build that dataset outline and manually write it for each gtd operational issue group's actual review.

## 43

I'm not convinced you gave each of those groups due prcoessing because you still didn't do what I fucking said. Consider/ingest the entire group of reviews for that set and write up a summary of their actual contents... not a vague/sporadic sub-sampling. Do the work.

## 44

it should only be for the GTD reviews, excluding non-GTD era reviews. Not all reviews in the dataset

## 45

rather than work those into the panels WITH the reviews... add a toggle for Summaries (enabled by default) that has a formal report output instead of just a list of review squares. Keep the styling consistent, but this is basically switching review squares for the text summary produced, output in a consisten format for the group panels. It's okay if they change size/shape. Treat this like a bit of a plugin, since we might want to remove this step if it's not informative enough later.

## 46

Okay, now to address the summaries themselves. They have a useful statistical review, but I want to understand and feel what patients are complaining about really, not just a stats report. It should be less about our specific dataset and more about what issues and concerns are affecting patients in each group, what they like and don't like or say helps and doesn't help.

## 47

you cant just script that out of stats, you need to, for each file, evaluate its source reviews in-depth, not just a sample.

## 48

every group summary shouldn't follow the same fixed format. I#m asking for the sumarry to be human-readable, and customised to the contents of its actual underlying reviews. Totally manually written, not automated or scripted.

## 49

don't try and do more than one set at a time, you can't... fcus on summariisng a single set at a time

## 50

I think you just wrote a load of generic bullshit because almost none of the things you mentioned are actually in our reviews except maybe in passing mentions. I'm saying ingest the entire set for one group, then summarise it into a human readable form that covers the issues raised effectively.

## 51

okay, I'm happy with access.md now, as it has footnotes so every claim is connected to something. Make sure these footnotes show their text as tooltips on hover of each claim's prior text, so the user sees the real review quote if they hover any claim. All summaries except access.md are now irrelevant, delete them, and I'll make a new one for each, so it should still build even if some are missing, outputting 'no [filename.md] found for summary' instead.

## 52

okay, I'm happy with access.md now, as it has footnotes so every claim is connected to something. Make sure these footnotes show their text as tooltips on hover of each claim's prior text, so the user sees the real review quote if they hover any claim. All summaries except access.md are now irrelevant, delete them, and I'll make a new one for each, so it should still build even if some are missing, outputting 'no [filename.md] found for summary' instead.

## 53

I said make the footnote apply to the preceeding text (until the previous footnote/line-break or 3 words, whichever is lesser), and show it like a tooltip, in-place near the claim

## 54

let the floating panel be outside the parent, it's clipping.

## 55

The footnotes section should be closed/collapsed behind a details toggle, that updates to show like Show/Hide Cited Reviews.

## 56

For each group panel, before the markdown output, display some stats about how many reviews in the group, and their distribution (use a coloured bar, split to show proportion of reviews in the set (not from the summary, but in the source set)) to give the reader a sense of how many reviews are being talking about in this panel's summary.

## 57

the positive reviews summary file has bad formatting, without changin the content, just fix the footnote formatting for our tools

## 58

never mind. I did it the easy way. Make the stats bar taller, the height of the usual squares, and don't round it off.

## 59

make sure the page supports a hash on the url to activate that view automatically.

## 60

Add this after GTD panel, but before other panels, like a TL;DR: e.

Across reviews of GTD-managed practices, the main pattern is cumulative failure rather than one isolated complaint. Reviewers describe practices that are hard to reach, hard to navigate, and often hard to rely on once contact is made. Problems with access, front-desk handling, admin follow-through, referrals, medicines, tests, and continuity tend to stack together, so frustration is often described not as delay alone but as a service that feels obstructive, fragmented, and unreliable.

Some themes carry particular weight. Front-desk interactions are a major source of distrust because reviewers often feel blocked, dismissed, or embarrassed at the very point they are trying to enter care. Admin and referral problems matter because they appear to distort care after contact, with patients describing lost paperwork, missed follow-up, and having to coordinate the system themselves. Medicines, tests, and parts of clinical care push the concern further, because the reviews there are often about risk as much as inconvenience.

The positive reviews do not really overturn that picture. They mostly praise individual staff for kindness, reassurance, listening, and professionalism, rather than suggesting the wider systems work consistently well. So the overall impression from the reviews is that GTD practices do still generate gratitude at the level of individual encounters, but the dominant reputation is of services where weak systems repeatedly wear down confidence, continuity, and, in some cases, safety.

## 61

that didn't seem to make it into the code because you added a weird condition. Check the code of the build/page, then wire it in properly.

## 62

there is no condition is my point

## 63

in consolidated summaries view, the other fully reviewed good and bad and other recents panels should show a distribution bar, like the main groups, and basic category report of those reviews. Keep it brief, we just want to get some basic undrstanding of what's in each of those groups in this view, without outputting a square for every review.

## 64

let's also display our TLDR before the GTD practices consolidation panel, and before the options, not after it. Collapse the TLDR in all views except consolidated summary, and make consolidated summary the default view for this page.

## 65

I said the tldr should be before the options/pickers/etc

## 66

something is wrong with ```Management and system change · 1.0 avg
2 reviews
Management and change
This file is about failure being attributed to how practices are run, not just to day-to-day pressure.1 Reviewers repeatedly say standards worsened after a takeover, a permanent contract, a management change, or the introduction of a ``` 2 reviews but a big breakdown? What's wrong with this?

## 67

I think that's we wrong solution. Those reviews were considered, but many reviews came from the set of entries categorised as if "Show in all categories" is checked, so the totals considered for the proportioned bars should come from that view, because that's more accurate. Essentially, summaries mode requires show in all categories to make sense, so let's have summaries enforce it, and in summaries mode, grey out the show in all categories force checked on.

## 68

"showSummaries is not defined" in the client

## 69

the coloured/stacked bars should have some style when printed. let's go with coloured, but like dash it or something, so it doesn't eat all my ink

## 70

in the tldr panel, when Summaries is on, include a line like "Toggle Summaries off to browse individual reviews" is its own line, with the "Toggle Summaries off" as an obvious button that duplicates turning out of that mode.

## 71

[REDACTED — injected IDE context, not user input]

## 72

in the tldr panel, when Summaries is on, include a line like "Toggle Summaries off to browse individual reviews" is its own line, with the "Toggle Summaries off" as an obvious button that duplicates turning out of that mode.

## 73

the stacked bars still don't display when printing. Just an empty space.

## 74

put a corresponding "Toggle summaries on" in the same place in the tldr panel when summaries are off

## 75

"Toggle summaries on" should affect whatever modes need to be set for that view to come back. It's more than just that one checkbox.
