---
cursor_session: eaed43a6-aaa3-4f36-a26e-7bbbf7fad4d1
source: cursor-composer
cursor_hint: ?
user_entries: 4
---

# transcript — update-this-find-matches-py-to-run-locally

### you

update this @find-matches.py  to run locally, point it at the right files, and run it, fix any bugs, then run it again to make the final list. It should take ./gutenberg-titles.json (sample it for content) and @next-ebooks-interesting.md  (period separated) and output a file like @next-ebooks-withcodes.txt that would do

### you

it takes forever to run. You can definitely significantly improve performance.

### assistant

- Updated `find-matches.py` to load `gutenberg-titles.json`, index titles for fast lookup, and match recommendations by PG IDs with a high-threshold fuzzy fallback.  
- Converted `gutenberg-titles.js` → `gutenberg-titles.json` for local use and sampled entries while testing.  
- Ran `python3 find-matches.py`; regenerated `next-ebooks-withcodes.txt` with the current matches (placeholder titles remain where the catalog only lists “Lovecraft”).

### you

okay good, now using a small on-the-fly script, use wget to download (skipping dedupe on id) the project gutenberg text.utf-8 (renAMINg to .txt on save) file for each book https://www.gutenberg.org/ebooks/[#].txt.utf-8

### you

you got about halfway (to 8395) but then stalled. Continue from where you left off.

### assistant

- Continued the download run from id `8395`.  
- Script pulled the remaining Gutenberg `*.txt.utf-8` files into `texts/` (skipping dedupe).  
- Interruption resolved; all listed ids now have corresponding `.txt` files.
