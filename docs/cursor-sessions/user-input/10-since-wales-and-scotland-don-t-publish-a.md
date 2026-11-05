---
cursor_session: 3f051ea0-100d-4e65-a5fe-1c2182188a09
source: cursor
cursor_project: home-bobbigmac-projects-nhs-complaint-dec-2024
user_entries: 9
source_file: /home/bobbigmac/.cursor/projects/home-bobbigmac-projects-nhs-complaint-dec-2024/agent-transcripts/3f051ea0-100d-4e65-a5fe-1c2182188a09/3f051ea0-100d-4e65-a5fe-1c2182188a09.jsonl
---

# user input — since-wales-and-scotland-don-t-publish-a

## 1

since wales and scotland don't publish a catchments dataset, our practice-finder's catchment filter should just fallback to nearest few, and a note should be added on the UI to briefly expalin this (at the bottom, after the list of suggested practices). In theory patients could be searching cross-border, so that's also fine, if catcments exist (in england), use them, but if not, just by distance (within the set limit) are eligible but trigger the footnote.

## 2

for the practice finder's UI, The extra/add-place button shouldn't appear until a home place has been placed.

## 3

Also the miles number picker is still underflowing itself, just remove the miles text and make sure the container isn't squeezing it down any more.

## 4

nearest 3 is far too few, we should consider any practices within the miles set by the user/default, so the user is seeing what they're getting. This is essentially the same pool as the catchment-present options but we just don't do the catchment check for properties in the scottish or welsh (or ni) sets, they only need to meet the distance requirement. There are several good  diagnostic properties on the record already to detect scotland/wales/ni practices vs english ones, so the underlying data doesn't need to change to support all nations, even at the borders.

## 5

if a practice has no catchment lookup, and is in england, we should probably still consider it a maybe if it's within the distance.

## 6

the marker texts should consider maybes from non-catchment-having practices in their count. Also the label "Distance only" isn't useful to the user. For matches from non-catchment-having nations, the 'maybe' match isn't a warning specific to the practice, it applies to all practice so should have a single warning 'footnote' info box, something like our existing footnote, but readable, like "Welsh/Scottish/NI practices don't publish catchments centrally, so nearer practices still may not accept your registration". 

The out of area number picker is still fucking stupidly layed out. Can you just do that control normally and stop trying to crunch it into a tiny box. Relayout the ui for finder tools, into proper buttons, a bit like a toolbar with polish, not just badly placed text labels.

## 7

does the client get practice websites for nhs wales, scotland and northern ireland? the results entries for these countries don't link to their website, and the register link doesn't appear, but I'm sure they're in our datatset somewhere, if not we need to collect it.

## 8

Integrate the one provided by the backend (I think some come from cqc, but again, england only), falling back through the links we know if present, to the ods_org_link and let's see where that leads people.

## 9

that ods link goes to a raw data page, nothing like the practice website... see: https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/W91036 , can we adapt it to a nice 'real' page? if not, the google maps places link is probably the better fallback than ods.
