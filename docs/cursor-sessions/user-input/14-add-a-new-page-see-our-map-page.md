---
cursor_session: 04cbc209-910d-4b72-bc19-53d1e66f3708
source: cursor
cursor_project: home-bobbigmac-projects-nhs-complaint-dec-2024-datasets
user_entries: 6
source_file: /home/bobbigmac/.cursor/projects/home-bobbigmac-projects-nhs-complaint-dec-2024-datasets/agent-transcripts/04cbc209-910d-4b72-bc19-53d1e66f3708/04cbc209-910d-4b72-bc19-53d1e66f3708.jsonl
---

# user input — add-a-new-page-see-our-map-page

## 1

add a new page (see our map page and other custom pages) that shows every practice (manchester region, extended/full reviews datasets, not uk/national limited sets) and output a rating over time chart for every entry (keep it simple, there will be a couple hundred lines) ordered by their total rating change + to - over time. Basically it's a list of practices ordered by how much better or worse they got over our dataset, with a simple chart beside each that shows the pattern, cos I'm looking for practices that got worse then got better, or got better then got worse. We don't need full reviews plaintext on the client, as I think we already have a reviews-over-time short-form dataset that carries gtd data, that is proably the right way to handle this too. All charts should share a max-timescale, even if the practice data doesn't go back that far, so we're basically making the time scale of every chart to the max/longest in the dataset, so the container should use the width of the page and each practice row should contain only the practice name in cell 1 and like 80% of the width of the container for the generated ratings over time chart for that practice.

## 2

make sure we're wired up to use yarn classic and to exclude node_modules and use polling files from the vite build, as there's a bug with it watching too many files

## 3

on each chart, time slices getting better should have green background and segments thet get worse should have red backgrounds.  Subtle colours are fine, but it should be over the correct timing per practice per month, not generalised. It should cover the block change, not just colour for the month of each single change, but should be grouped to better/worse/same groups (same as white is fine).

## 4

link the practice name out to the google reviews page for the practice

## 5

older reviews (previous years) should colour the year, not just the month of the change, since our dataset uses days/weeks/months/years ago, older years (no sub-month datas) should colour the year.

## 6

On the map page, instead of Trajectories, call it Timelines
