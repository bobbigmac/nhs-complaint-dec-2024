---
cursor_session: ee006d46-9414-44f9-a790-c98b7cbec1e9
source: cursor
cursor_project: home-bobbigmac-projects-nhs-complaint-dec-2024
user_entries: 15
source_file: /home/bobbigmac/.cursor/projects/home-bobbigmac-projects-nhs-complaint-dec-2024/agent-transcripts/ee006d46-9414-44f9-a790-c98b7cbec1e9/ee006d46-9414-44f9-a790-c98b7cbec1e9.jsonl
---

# user input — in-our-reviews-analysis-html-builder-there-is

## 1

in our reviews-analysis html builder, there is a section/group for the top 'good' practices and bottom 'bad' practices, but it currently pulls the entire dataset into the page (which bloats it a lot since we started importing full reviews for all practices), we instead want to show/use just the top 5 and bottom 5 non-gtd practices, so all reviews don't need to go directly into the site/build for non-gtd practices, as we're mainly collecting them to put an average review across the entire dataset on the population growth chart (i.e. the average per year for all practices in the dataset with data for that year), so you can implement that too. Our main build is currently extremely slow, but I think limiting the non-gtd groups to 5 each keeps us sensibly scoped, and we will come along and do more with this area later (put that per-year avg reviews line on the population chart though).

## 2

ah sci-kit learn is failing in the build, can you just install it to the venv and that will work?

## 3

can you make that the default in yarn build? or is that going to affect our currently running (and do not want to intterupt) extended reviews scanner?

## 4

06:41:37 [vite] (client) page reload chronology/index.html
06:41:37 [vite] (client) page reload map/map.html
11:09:53 [vite] (client) page reload map/map.html (x2)
^C~./p./nhs-complaint-dec-2024(main)$ yarn dev
Wrote /home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/practice-patterns/output/reviewed_practice_platform_survey_merge.json
Wrote /home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/practice-patterns/output/reviewed_practice_platform_survey_summary.md
Wrote /home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/practice-patterns/output/reviewed_practice_relative_rankings.html
Graph classifier failed (scikit-learn required); using committed fallback
Wrote /home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/reviews-analysis/output/raw_reviews_extended.json (23 practices)
site/.vite-src

  VITE v7.3.1  ready in 3060 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.1.174:5173/
  ➜  press h + enter to show help
^C~./p./nhs-complaint-dec-2024(main)$

## 5

wasn't there a 4th group in the consolidated reviews-browser there that got removed, or am I thinking of a different view?

## 6

ah I see. Yes, I want the Manchester Region GPs panel, I didn't tell you to remove it. It should however always be the overview/summary stacked bar, as it's contextualising what's 'normal' across our datatset

## 7

have it use the effective width of the page, like the other summary bars. come on dude,

## 8

that has had no effect, and I''m not sure that's related at all. Check the code for this area and do it right.

## 9

I have no idea where you put the average review per year line, but it's not visible on the "whole dataset total" population line chart, where it should be

## 10

I still can't find/see it, pretty sure its not just cached. It should be in all modes, since it's not affected by anything, it's just avg review across all practices for each year (that chart is abasically showing population in the entire dataset AND avg reviews over the years)

## 11

does the main build actually update the map build? cos I'm still not seeing it

## 12

it should call it

## 13

put the reviews label and axis on the left, so it doesn't overlap the population label and axis. An addition to the footnote that it's surprising that reviews overall improve across Manchester despite a rrapidly growing poplation

## 14

I see you're feeling lazy today, I obviously meant the footnote in the correct panel, not one across the page

## 15

I didn't say "striking" did I?
