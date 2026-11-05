## 1

in datasets/ manchester map build tweak the 'Gap' display in the map's main chart, currently the gap is determined as the absolute difference between patient survey score and google review score, but I think the sign matters for our use case... If a google review is better than the patient survey score, that's a sign the practice is better than we official recorded (so the map marker in gap view should be green), but if the google rating is worse than the (mapped) patient survey, that's clearly worse (the practice doesn't know it's doing worse than it thinks it is). Familiarise yourself with this area of the codebase, and implement this change, as the next step will involve it too.

## 2

on 'gap' reporting, we want to add a chart that integrates the rating/survey/gap into a chart with a deprivation comparison. I'm not sure what type of chart/display does this best though. We're trying to identify, for each our metrics, if, and by how much worse, it is as deprivation increases, but I'm not sure how to query our deprivation data. It probably makes more sense to have the server-side/action build generate a json file that compiles deprivation from our complex dataset into  single file lookup the client-side-page/chart/parser/etc can use to reference deprivation per-practice.  Try to keep it self contained in each layer, as I don't want to make a mess and Im not sure what we're looking for here, so it might be easier to change in its own file that you should then import into the build and use.

## 3

I'm not seeing the deprivation chart in the page. renderDeprivationChart isn't run?

## 4

yarn build should do that right?

## 5

then it's not changing anything, cos that's what im doing

## 6

no chart is making it into the page. No errors from the build

## 7

Uncaught SyntaxError: Unexpected token ':' (at map.html:2099:59)

## 8

on Score vs Deprivation chart, this is kinda the right way to look at it, but rather than fixing the dots to the axis line, it might make more sense to treat each grid/box as a container that displays them as simply small squares, allocated to that box/block, putting the axis label at the middle rather than on the line. This would help us see visually how many practices are actually in that zone (because currently they overlap eachother which makes the real impact hard to see

## 9

﻿
map.html:2005 Uncaught ReferenceError: cellMarkup is not defined
    at renderScatterplot (map.html:2005:7)
    at rerenderAll (map.html:2603:3)
    at map.html:2650:1

## 10

﻿
map.html:2134 Uncaught ReferenceError: pointMarkup is not defined
    at renderDeprivationChart (map.html:2134:7)
    at rerenderAll (map.html:2604:3)
    at map.html:2650:1

thinka bout what you're d oing

## 11

﻿
map.html:2005 Uncaught ReferenceError: cellMarkup is not defined
    at renderScatterplot (map.html:2005:7)
    at rerenderAll (map.html:2603:3)
    at map.html:2650:1

can you read your own code and make sure you're not doing lazy dumb shit please

## 12

﻿
map.html:2134 Uncaught ReferenceError: pointMarkup is not defined
    at renderDeprivationChart (map.html:2134:7)
    at rerenderAll (map.html:2604:3)
    at map.html:2650:1

## 13

you changed the same thing back and forth fucking twice. Reread the fucking code

## 14

okay good. Now put the squares in the middle of the column, not on the edge, and the axis labels too.

## 15

Our 'gap' markers on the map  exclude -1-to-+1 (iirc) but this chart should include them.

## 16

squares in this chart should have a fixed size (since they represent count) but it will need to be dynamic enough that sizes of the grid are not distorted, you kinda need to figure out a max fittable and min fittable and size everything to the max fittable

## 17

you need to make them pretty much fit the grid size, they're way too small right now. Don't just guess, but your logic should be able to figure it out (so it updates on resize too).

## 18

good. The "Completion Rate vs Score" also needs to be slightly adapted to handle conversion to absolute itself, so positive and negative appear in the same scale for that chart only.

## 19

include the greyed out entries between -1 and 1 there too

## 20

i don't think "raw signed gap" is survey/20 elsewhere in our datatset, can you check what logic were doing for this elsewhere?

## 21

does it make more sense to normalise survey and reviews before raw signed gap instead of against 100% but from its min to its max? then use that comparison for raw gap everyhwre in our dataset? Maybe a toggle would be a good option, simply "Normalise" with the other option toggles, that afffects the entire page. What do you think?

## 22

You might be able to deal with this better.

```does it make more sense to normalise survey and reviews before raw signed gap instead of against 100% but from its min to its max? then use that comparison for raw gap everyhwre in our dataset? Maybe a toggle would be a good option, simply "Normalise" with the other option toggles, that afffects the entire page. What do you think?``` I was kinda thinking percentiles, but they're really quite different numbers, what _should_ be the best and most standard approach to deal with normalising our subtly (but importantly) different scales, because while 80% kinda does mean 4 stars, 20% doesn't exist against 1 star because the survey doesn't go below 40%

## 23

okay, implement the normalise toggle as per your recommendations. What's the difference between z-score and rank-based? I'm cautious of rank-based because scores are not measurements, ratings and surveys are very very soft catchments given the huge dependence on reply rates (so ranks of very similar practices can be very different due to very different numbers of replies), basically high variability can make rankings less accurate

## 24

Normalise toggle button should be only displayed in Gap mode, and should be selected by default. It should also be styled like a check, with a short description of what it's doign.

## 25

The header of each of these charts should also very clearly include "- Showing [Reviews|Patient Survey|Normalised Gap], since the button toggles are so far away, it'd be easy to forget what's being displayed.

## 26

the normalised gap 'map' shhould ignore -1 to +1 gaps (from the normalised set, not from the raw set) if in normalised mode.

## 27

on "Quick comparisons - Showing Normalised Gap" panel for New Bank health, it shows as unknown I think because New Bank isn't in the normalised filtered set, but it should be able to get the value from new bank anyway

## 28

Can we make the Google/GP Survey/Gap selector sticky to the top of the viewport on scroll? I want it to maintain exactly the same panel and location, but just stick to the top of the screen when it's not in the viewport. No width or relayout issues please, just wherever it is now along the horizontal axis, should be maintained as its sticky without affecting the rest of the page in any way.

## 29

that's not remotely how sticky works. You need to look up how to do it properly.

## 30

good, but it doesn't need the score-source or additional text, just the switcher is fine.

## 31

going back to Score vs Deprivation table... let cells with lots of entries use a wider per-column-count, like the fuller cells are currently taller than they should be wider. The rest are fine.

## 32

in Score vs Deprivation views, how do we represent if there is a similar distribution between columns? I'd like to be annotate that with some kind of visual indicator of whether the distribution of reviews/survey/gap is similar from deprivation level to deprivation level, or do like wealthier regions have more good reviews/survey and poor areas have a worse distribution (more poor reviews), which I think we can indicate by a colour selection for the column that shows how close to the average distribution for that metric for that column.

## 33

do it

## 34

good but it doesn't need to be mostly transparent. Make it a fully opaque background-colour. It might also be useful to put an avg header for each column that shows where the true centre of the distribution lies as a single number.

## 35

put the header above the chart cells, not below them

## 36

map.html:2414 Uncaught ReferenceError: headerBandY is not defined
    at map.html:2414:47
    at Array.map (<anonymous>)
    at renderDeprivationChart (map.html:2378:36)
    at rerenderAll (map.html:2963:3)
    at map.html:3065:1
client:733 [vite] connecting...
client:827 [vite] connected.
map.html:2414 Uncaught ReferenceError: headerBandY is not defined
    at map.html:2414:47
    at Array.map (<anonymous>)
    at renderDeprivationChart (map.html:2378:36)
    at map.html:2995:5

## 37

I'm not sure the z-based normaliser is 'correct', I think our high-noise set is causing a weird effect and a lot more things are ending up in the high set than should be (basically we uplifted half our dataset by combning/comparing sets at the wrong time, either too early or too late, not sure). Can you investigate our normaliser and check it's doing what it should be when the results are being actually used.

## 38

do it, let's see how it looks.

## 39

did you update the map to use the new figures? It looks to have updated in the deporvation table/chart but not in the map.

## 40

Add a conclusions panel below all the other panels, that sums up what we demonstrated/learned on this page... That GTD is the worst performing group, but its negative reviews are at the bottom of even its deprived groups' performances, greater gap between google reviews and patients survey scores than typical practices, low (but not lowest) survery return rates, and that while there is definitely a dataset-wide lean (deprived areas DO have slightly worse reviews and surveys, but perhaps you would expect this range to emerge (additional wider regional/national sampling can test for this, as I expect a bit of a london bump and a north east dip)). Our data does NOT suggest the entire NHS is failing only poorer people, but does suggest it's not delivering quite as well, so our position is essentially that GTD are doing badly on patient satisfaction in both metrics, but there is not a national problem of poor areas _only_ having poor quality GPs, but that our GTD sample has far too many poor performing practices, so the national situation can be improved, but focus on local is probably more likely to give real positive benefits intead of just trying to move the national goalposts. Basically our interest group 'GTD' and New Bank especially, is doing much worse than most of the sample set, essentially off-curve for the normal pattern (at the bottom of all its groups), so we need change across GTD, which will be mainly felt by improved health, especially in the more deprived areas where it's even more important that access is easy, not just possible.

## 41

bump our body font size in this doc a little, it's tough to read.

## 42

where's the /1.4 thing coming from? what's the cause for the modifier?

## 43

next, I want to show registered patient count over time per practice related to google reviews/patient-survey. How can we add a chart that visualises this? A map view would make it clear visually, but I'm more interested in visualising the effect alone (its own chart), with an assumption that most patients leaving a practice join a practice nearby (not exactly realistic, but I would like to simulate this visually somehow, even if we consider some gain to the pool and some leaving the pool) mainly because I want to answer the question... "Do patients actually leave failing practices? and if so, do practices that are getting better scores over time see similar increasing patient counts?" essentially, this panel/chart wants to test that patients disatisied with a practice actually do go elsewhere. It might be worth looking up Manchester's general population over this period for a kinda benchmark growth/shrink that we would expect from the average practice as a kinda 'expected growth' that represents the normal 'everythign is fine' pattern.

## 44

yeah, that sounds good. Implement that

## 45

we already have the data you need around the datasets folder, just find it, and if needed, use a build step to form a json file (I _think_ it's mostly in th epage, but maybe not historical counts, which have been compiled, but should proabbly just use an object of practice coded yearly counts standardised that the client can read for exactly what it needed.

## 46

our ntire dataset is manchester, you don't need to filter it specifically.

## 47

[REDACTED — injected IDE context, not user input]

## 48

we have a few to many rows in that table to be able to read its axis values. It also has a few 'rapid growth' minor examples as outliers that make it hard to read the core data. Review history windows are not the same, and they have vague timespan tags, not dates, so we can't filter it reliably, so for the vast majority practices we only have recent reviews.. Only GTD practices and a couple of others have full reviews, so I guess we can't correctly index for that. Let's just show it as registerd patients vs time, coloured/numbered by current google review/survey score.

## 49

it might be a lot to ask, but what if we treat this like a treemap, so we can visually indicate the patient count by size (even grouped by known groups as they're available for our map filter anyway), and by label as like [rating]/[patients], and attach a play button that lets the viewer see how they grow/shrink over time. I'm not sure how to do this without a constant relyout of the treemap though. Maybe add this as a new panel (as it uses basically the same data) so I can view them both on the same page and assess if either works to communicate well.

## 50

in the treemap... Independent/other should probably subgroup by review score, since they represent whether patients went to better or worse practices is our objective, and as a single row for each practice it just doesn't tell us anything at all. The relative pixels per unit of patient count should be stable across all groups/times, and we should be able to report n patients per pixel for our current output.

## 51

check our dataset for population, is the population up like 30% on the timespan we have? That's quite a lot. We probably want to put that total population as a short graph (not much height, use the width) below the treemap to show a graph of that global change.

## 52

the items in the independent buckets should be squares/rects, not rows.

## 53

number text in boxes shouldn't be literally in [brakcets] that was my exmaple, it should have what is in the label, and scale-friendly padded with text that gets small enough to read if you squint

## 54

Now we need a 'Normalise for change' checkbox below the checkbox that flattens the global change for our dataset (i.e. the boxes individually change for each scale depending on their pct of the datatset, not the absolute figures, so essentially the global change is eliminated, and we get a sense in that mode for how population shifted between practices, rather than to the pool

## 55

Don't have normalise for change use the full width except in narrow viewports. Make it off by dfeault and call it just "Flatten Global"

## 56

"Registered Patients Over Time..." chart is useful, but it's hard to tell the scores of the coloured rows because the grey lines distort the total scale. Display only the group/score avg lines, not every line.

## 57

and scope to that, obviously

## 58

we need to obey flatten global on that too, which also switches the vertical axis to variance from the mean, as we're trying to learn whether patients are going to better or worse practices over time, not how many patients are going there

## 59

then note in our conclusion that practices sampled have seen (growth amount) growth over (period), which is substantial, so its not surprising.

## 60

You kinda twisted what I said... It's not that the growth patterns are unsurprising, but It's worth noting there, that a 20% population increase is a significant resource pressure, so I want to be clear that this overall pattern 'suggests' a region responding surprisingly well to new/increased demand, especially through these years of reduced funding, some didn't just maintain their scores but improved.

## 61

The flatten global toggle doesn't cause the patients over time chart to toggle.

## 62

put the flatten global on the right side of the "patient count treemap" header, so it's accessible to a viewer both/either chart, as they're next to eachother.

## 63

enable flatten global by default

## 64

gtd-score-trend-legend don't need takeover date or 'latest...' keep the name, so the panels can be shorter with less content.They should also be selectable (same outcome as on-hover, I just want to be able to keep that state until I move the cursor over or click a different one (I will move sideways off if I want to keep onne live after clicking it)),

## 65

make the gtd mean line red

## 66

clicked-state is not being kept still. There must be a side-effect resetting it elsewhere on the panel. Click state should probably just unbind the hover change effect

## 67

click still does nothing, and leaving hover state still resets to the default.

## 68

in print mode, is it possible to make the map fixed height to a single 'sheet''s height? Like I want page 1 to be the map's height, then NOT extend the map's container (and controls) to a further page, like I want the entire map and controls to exactly fill page 1, whatever settings are chosen? Page 2 would ideally always open on quick comparisons panel

## 69

page 1 clips properly, but a fake/blank page 2 is iserted

## 70

also, because you defined a narrower page than our actual page, it causes wrapping between controls that previousy didn't (so we could hav 2 benchmarks panels per page, which now we can't).

## 71

when normalising the gap, on the map, show only negative scored items (we don't care if some practices are better than the survey thinks they are, only about those that are worse, because we need to know where they are)

## 72

for the "Registered Patients Over Time" add a global-flatten-linked footnote saying that both sets show VERY slight gains to practices with positive surveys/ratings and VERY slight slower gains of patients to worse performing GPs, suggesting patients ARE moving to better doctors (potentially justifying the choice of bad access to drive away patients who need more access/convenience/support and depending on the free market to solve the problem), but the movement is INCREDIBLY slow. There's probably a death rate linked directly to that very slow movement, like a poor patient stuck behind a bad system, who a) believes "they're all the same" so doesn't bother to switch, is probably going to be sicker (and die earlier) compared to other patients who understand they have a choicre, and take it.
