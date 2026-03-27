# England Random Good Practice Chance

Generated: 2026-03-27 05:10 UTC

This report is **England only**.

Reason: the healthcare-terrain hard catchment source currently exists only for the England GP catchment cache, so this report narrows the earlier broad UK-style question to the England practice pool.

## Headline

If you model the question as **picking an England GP practice at random with no prior research**, the best simple answer in this dataset is **59.6%** if "good" means **GP Patient Survey overall-good >= 75%**.

The patient-weighted version of the same question is **55.1%**.

## Metric Notes

- Primary metric used for the headline: `survey_overall_good_percent >= 75`
- England practices in combined published dataset: `6,224`
- Survey coverage in England rows: `6,172` / `6,224` = `99.2%`
- Google score coverage in England rows: `6,135` / `6,224` = `98.6%`

## Alternative Reads

- Survey-defined good, random practice: `59.6%`
- Survey-defined good, patient-weighted: `55.1%`
- Google `>= 3.75` (the direct `75% -> 3.75 stars` mapping used in the survey/Google gap view), random practice: `27.4%`
- Google `>= 4.0` only, random practice: `21.0%`
- Google `>= 4.0` with at least `10` reviews, random practice: `19.1%`
- Survey-defined good among England practices with survey data present: `60.1%`

## Plain-English Read

Using the survey-based definition, England looks roughly like a **6-in-10** random-practice chance of landing on a good practice, or about **55%** if you weight by patient counts instead of by practice count.

The stark contrast is Google: even if you soften the Google cutoff to the direct survey-equivalent threshold of `3.75` stars, the random-practice chance is only **27.4%**. At the stricter `4.0`-star cutoff it drops to **21.0%**.

So the important directional point is not subtle: in England it looks fairly common to be structurally near (in the catchment-system sense) a practice with good patient-survey results, but much rarer to be near one that looks good on Google ratings.

