# Management Company Watchlist

This folder is a small watchlist for non-GTD operators and similar groups that keep coming up around the Greater Manchester work.

The goal is not to widen the catchment automatically. The goal is to:

- keep a named list of tender competitors and similar operators worth tracking
- check whether they already appear inside the current dataset catchment
- separate confident matches from "needs investigation" cases
- avoid burying that knowledge inside one enrichment script

## Files

- `watchlist.json` - manually curated companies, tender notes and the specific practices or lots we want to keep checking.
- `build_company_watchlist.py` - reads the current enriched dataset and writes a watchlist report.
- `output/company_watchlist_report.md` - human-readable summary of which watchlist companies are already in the current catchment dataset.
- `output/company_watchlist_report.json` - machine-readable version of the same report.

## Current workflow

1. Refresh company enrichment:
   `python3 datasets/enrich_management_companies.py`
2. Rebuild the watchlist report:
   `python3 datasets/management_companies/build_company_watchlist.py`

## Notes

- `management_company_name` is for the best current guess at the core operator.
- `affiliated_group_name` is separate and is used for federations, network operators or related groups that may coexist with another core operator.
- Some tender references are still unresolved at exact-practice level. Those stay in the watchlist until we can pin them down cleanly.
