---
cursor_session: 04cbc209-910d-4b72-bc19-53d1e66f3708
source: cursor
cursor_project: home-bobbigmac-projects-nhs-complaint-dec-2024-datasets
user_entries: 6
source_file: /home/bobbigmac/.cursor/projects/home-bobbigmac-projects-nhs-complaint-dec-2024-datasets/agent-transcripts/04cbc209-910d-4b72-bc19-53d1e66f3708/04cbc209-910d-4b72-bc19-53d1e66f3708.jsonl
---

# transcript — add-a-new-page-see-our-map-page

### you

add a new page (see our map page and other custom pages) that shows every practice (manchester region, extended/full reviews datasets, not uk/national limited sets) and output a rating over time chart for every entry (keep it simple, there will be a couple hundred lines) ordered by their total rating change + to - over time. Basically it's a list of practices ordered by how much better or worse they got over our dataset, with a simple chart beside each that shows the pattern, cos I'm looking for practices that got worse then got better, or got better then got worse. We don't need full reviews plaintext on the client, as I think we already have a reviews-over-time short-form dataset that carries gtd data, that is proably the right way to handle this too. All charts should share a max-timescale, even if the practice data doesn't go back that far, so we're basically making the time scale of every chart to the max/longest in the dataset, so the container should use the width of the page and each practice row should contain only the practice name in cell 1 and like 80% of the width of the container for the generated ratings over time chart for that practice.

### assistant

Exploring the project to find how custom pages and the map are built and where reviews-over-time data lives.

> `Glob` {"target_directory": "/home/bobbigmac/projects/nhs-complaint-dec-2024", "glob_pattern": "**/*.{html,js,tsx,ts,vue}"}

> `Grep` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024", "pattern": "map|custom.*page|reviews.*time|gtd", "glob": "*.{html,js,ts,tsx,py,md}", "-i": true}

> `Grep` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets", "pattern": "timeseries|reviews_over|google_score|rating.*time", "glob": "*.{py,js,json}"}

> `Read` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/build_gtd_gp_practice_dataset.py", "offset": 2260, "limit": 200}

> `Read` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/gtd_gp_map/map.html", "limit": 120}

> `Read` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/build_gtd_gp_practice_dataset.py", "offset": 2680, "limit": 400}

> `Grep` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/build_gtd_gp_practice_dataset.py", "pattern": "write_map|render_map|MAP_"}

> `Read` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/gtd_gp_map/map.html", "offset": 120, "limit": 200}

> `Read` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/gtd_gp_map/map-app.js", "offset": 5400, "limit": 450}

> `Grep` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/gtd_gp_map/map-app.js", "pattern": "function linePath"}

> `Read` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/build_gtd_gp_practice_dataset.py", "offset": 1, "limit": 50}

> `Read` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/gtd_gp_map/map-app.js", "offset": 5325, "limit": 40}

### assistant

Implementing `build_manchester_google_score_timeseries_all_practices` and the standalone page. Checking `iter_month_starts` and `month_start`:

> `Grep` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/build_gtd_gp_practice_dataset.py", "pattern": "def iter_month_starts|def month_start"}

### assistant

Implementing the Python builder, embed writer, standalone assets, and wiring them into `write_map`.

> `Read` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/build_gtd_gp_practice_dataset.py", "offset": 2235, "limit": 90}

### assistant

Adding the builder function and wiring it up.

> `StrReplace` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/build_gtd_gp_practice_dataset.py", "old_string": "MAP_EMBED_SCRIPT_NAME = \"map-embed-data.js\"\nMAP_ASSETS_DIR = BASE_DIR / \"gtd_gp…

> `StrReplace` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/build_gtd_gp_practice_dataset.py", "old_string": "        \"missing_practices\": missing_practices,\n    }\n\n\ndef build_dataset_goo…

> `Read` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/gtd_gp_map/map.css", "limit": 80}

> `StrReplace` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/build_gtd_gp_practice_dataset.py", "old_string": "def write_map_embed_data(path: Path, embed: dict[str, Any]) -> None:\n    path.writ…

> `StrReplace` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/build_gtd_gp_practice_dataset.py", "old_string": "    shutil.copy2(MAP_ASSETS_DIR / \"map.css\", out_dir / \"map.css\")\n    shutil.c…

### assistant

Fixing the sort key for None deltas and creating the three asset files.

> `StrReplace` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/build_gtd_gp_practice_dataset.py", "old_string": "    practice_series.sort(\n        key=lambda item: (\n            -(item[\"delta\"…

> `Write` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/gtd_gp_map/rating-change-over-time.css", "contents": ":root {\n  --bg: #f6f4ef;\n  --ink: #1a1c1a;\n  --line: rgba(26, 28, 26, 0.12);…

> `Write` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/gtd_gp_map/rating-change-over-time.js", "contents": "(function () {\n  const embed = window.__RATING_CHANGE_EMBED__ || {};\n  const m…

> `Write` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/gtd_gp_map/rating-change-over-time.html", "contents": "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n<title>…

### assistant

Escaping injected text in the JS and adding a map page link.

> `StrReplace` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/gtd_gp_map/rating-change-over-time.js", "old_string": "  function deltaClass(delta) {\n    if (delta === null || delta === undefined …

> `StrReplace` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/gtd_gp_map/rating-change-over-time.js", "old_string": "  listEl.innerHTML = series\n    .map((row) => {\n      const points = row.poi…

> `StrReplace` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/gtd_gp_map/map.html", "old_string": "      <div class=\"legend-header\">\n        <a class=\"home-link\" href=\"../index.html\" title…

> `StrReplace` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/gtd_gp_map/map.css", "old_string": ".legend-header {\n  display: flex;\n  align-items: center;\n  justify-content: space-between;\n  …

> `Shell` {"command": "cd /home/bobbigmac/projects/nhs-complaint-dec-2024/datasets && python3 -m py_compile build_gtd_gp_practice_dataset.py && python3 build_gtd_gp_practice_dataset.py", "description": "Verify …

> `Shell` {"command": "wc -c /home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/output/gtd-greater-manchester-gp-practice-reviews-2026-03-09/rating-change-over-time-embed.js && head -c 400 /home/bobbigmac…

> `Grep` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/output/gtd-greater-manchester-gp-practice-reviews-2026-03-09/map.html", "pattern": "Trajectories"}

> `ReadLints` {"paths": ["/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/build_gtd_gp_practice_dataset.py"]}

### assistant

Here is what was added:

### Behaviour
- **`build_manchester_google_rating_timeseries_all_practices`** in `build_gtd_gp_practice_dataset.py` — same cumulative monthly Google signal as the GTD trend (from `google_maps_recent_reviews.json`, no review text on the client), but for **every** Manchester CSV/JSON row with a canonical code.
- **Shared x-axis**: one global month range from the earliest review month in that scrape to the scrape month.
- **Sort**: `delta = last_value − first_value` on the forward-filled series (largest improvement first).
- **Publish**: `write_map` writes `rating-change-over-time-embed.js` and copies `rating-change-over-time.html`, `.js`, `.css` next to `map.html`.

### UI
- **`gtd_gp_map/rating-change-over-time.html`** (+ CSS/JS): name column **20%**, chart **80%**, thin row SVGs, Δ in the name column, GTD lines in blue vs grey.
- **`gtd_gp_map/map.html`**: **Trajectories** link beside **Home** to the new page.

### Output path
After `python3 build_gtd_gp_practice_dataset.py`, open:

`datasets/output/gtd-greater-manchester-gp-practice-reviews-2026-03-09/rating-change-over-time.html`

### you

make sure we're wired up to use yarn classic and to exclude node_modules and use polling files from the vite build, as there's a bug with it watching too many files

> `Glob` {"target_directory": "/home/bobbigmac/projects/nhs-complaint-dec-2024", "glob_pattern": "**/vite.config.*"}

> `Glob` {"target_directory": "/home/bobbigmac/projects/nhs-complaint-dec-2024", "glob_pattern": "**/package.json"}

> `Read` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/package.json"}

> `Grep` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024", "pattern": "vite"}

> `Glob` {"target_directory": "/home/bobbigmac/projects/nhs-complaint-dec-2024", "glob_pattern": "**/.yarnrc*"}

> `Read` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/.yarnrc.yml"}

> `Glob` {"target_directory": "/home/bobbigmac/projects/nhs-complaint-dec-2024", "glob_pattern": "**/.gitignore"}

> `Glob` {"target_directory": "/home/bobbigmac/projects/nhs-complaint-dec-2024/site", "glob_pattern": "**/vite.config.*"}

> `Read` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/.gitignore"}

> `Read` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/site/build.py", "limit": 80}

> `Glob` {"target_directory": "/home/bobbigmac/projects/nhs-complaint-dec-2024", "glob_pattern": "**/yarn.lock"}

> `Grep` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/site/build.py", "pattern": "vite|\\.vite-src|copy|shutil"}

> `Read` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/site/build.py", "offset": 1405, "limit": 200}

> `Read` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/site/finalize_vite_dist.py", "limit": 80}

### assistant

Configuring Yarn Classic (replacing Berry's `.yarnrc.yml`), adding `site/vite.config.mjs` with polling and `ignored` patterns, and updating npm scripts to use the config.

> `Delete` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/.yarnrc.yml"}

> `Write` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/.yarnrc", "contents": "# Yarn Classic (v1). Do not add .yarnrc.yml (Yarn Berry) for this repo.\n# See package.json \"packageManager\" and use:…

> `Write` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/site/vite.config.mjs", "contents": "import { defineConfig } from \"vite\";\nimport path from \"node:path\";\nimport { fileURLToPath } from \"n…

> `StrReplace` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/package.json", "old_string": "{\n  \"name\": \"nhs-complaint-local-site\",\n  \"private\": true,\n  \"scripts\": {\n    \"dev\": \".venv/bin/p…

> `Shell` {"command": "cd /home/bobbigmac/projects/nhs-complaint-dec-2024 && corepack enable 2>/dev/null; corepack prepare yarn@1.22.22 --activate 2>/dev/null; yarn --version && yarn install --ignore-engines 2>…

> `Shell` {"command": "cd /home/bobbigmac/projects/nhs-complaint-dec-2024 && yarn build 2>&1", "description": "Run full Vite build with new config", "block_until_ms": 120000}

### assistant

Changes made:

- **Removed** `.yarnrc.yml` (Yarn Berry).
- **Added** `.yarnrc` so this repo is clearly Yarn Classic–oriented.
- **Set** `"packageManager": "yarn@1.22.22"` in `package.json` (use `corepack enable` so this version is used).
- **Added** `site/vite.config.mjs`: `root` = `site/.vite-src`, `publicDir: false`, `server.watch` with `usePolling: true`, `interval: 200`, and `ignored` for `node_modules`, `.git`, `.venv`, and `venv`.
- **Updated** `dev` / `build` scripts to run Vite with `--config site/vite.config.mjs` (build output unchanged: `site/local-dist`).

`yarn build` completes successfully with this setup. `node_modules/` was already in `.gitignore`.

### you

on each chart, time slices getting better should have green background and segments thet get worse should have red backgrounds.  Subtle colours are fine, but it should be over the correct timing per practice per month, not generalised. It should cover the block change, not just colour for the month of each single change, but should be grouped to better/worse/same groups (same as white is fine).

### assistant

Updating `rating-change-over-time.js` to draw merged green/red background rectangles for consecutive month-to-month improvements/declines in cumulative rating.

> `Read` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/gtd_gp_map/rating-change-over-time.js"}

### assistant

Implementing grouped background rectangles from consecutive month-to-month cumulative changes (up → green, down → red; flat/unmeasurable → no fill).

> `StrReplace` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/gtd_gp_map/rating-change-over-time.js", "old_string": "  const yScale = (value) => margin.top + plotHeight - ((value - yMin) / (yMax …

### assistant

Using each row's `points.length` for the x-step so scaling stays consistent.

> `StrReplace` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/gtd_gp_map/rating-change-over-time.js", "old_string": "  /** Merge consecutive month edges with the same up/down trend into one backg…

> `Shell` {"command": "cp /home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/gtd_gp_map/rating-change-over-time.js /home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/output/gtd-greater-manchester-gp…

### assistant

Updates are in `datasets/gtd_gp_map/rating-change-over-time.js`:

- For each practice, each **month edge** (change from `points[k-1]` → `points[k]`) is classed as up / down / same (with `TREND_EPS`).
- **Runs** of consecutive edges with the same **up** or **down** sign are merged into a **single** rectangle from `xScale(startK) − step/2` to `xScale(endK) + step/2`.
- **Same** and **unmeasurable** edges stay clear (no fill); line stays on top of the fills and grid.
- Fill colours: green `rgba(76, 154, 82, 0.18)`, red `rgba(195, 71, 47, 0.16)`.

The same file is copied into `datasets/output/gtd-greater-manchester-gp-practice-reviews-2026-03-09/`. Re-run `build_gtd_gp_practice_dataset.py` to refresh that output on the next full build.

### you

link the practice name out to the google reviews page for the practice

> `Grep` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/build_gtd_gp_practice_dataset.py", "pattern": "google_maps|google_url|google_review_source", "glob": "*.py", "head_limit": 40}

> `Read` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/build_gtd_gp_practice_dataset.py", "offset": 2418, "limit": 120}

### assistant

Adding `google_maps_url` to the embed in Python and linking practice names in the rating page JS/CSS.

> `StrReplace` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/build_gtd_gp_practice_dataset.py", "old_string": "        delta = round(last_finite - first_finite, 4) if first_finite is not None an…

> `Read` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/gtd_gp_map/rating-change-over-time.css", "limit": 100}

> `Read` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/gtd_gp_map/rating-change-over-time.js", "offset": 115, "limit": 50}

> `StrReplace` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/gtd_gp_map/rating-change-over-time.js", "old_string": "  function escapeHtml(s) {\n    return String(s)\n      .replace(/&/g, \"&amp;…

> `StrReplace` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/gtd_gp_map/rating-change-over-time.js", "old_string": "      const codeAttr = escapeHtml(row.code || \"\");\n      const label = esca…

> `StrReplace` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/gtd_gp_map/rating-change-over-time.js", "old_string": "          <div class=\"rating-row-name\">\n            <div class=\"rating-row…

> `StrReplace` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/gtd_gp_map/rating-change-over-time.css", "old_string": ".rating-row-title {\n  font: 600 13px/1.25 \"Avenir Next\", \"Trebuchet MS\",…

> `Shell` {"command": "cd /home/bobbigmac/projects/nhs-complaint-dec-2024/datasets && python3 build_gtd_gp_practice_dataset.py 2>&1 | tail -5 && python3 -c \"import json,re; p='output/gtd-greater-manchester-gp-…

> `Grep` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/output/gtd-greater-manchester-gp-practice-reviews-2026-03-09/rating-change-over-time.js", "pattern": "titleMarkup|google_maps_url"}

### assistant

- **`build_gtd_gp_practice_dataset.py`**: each `practice_series` entry now includes `google_maps_url` from `google_url`, then `google_review_source_url`, then `google_maps_url` on the capture row.
- **`rating-change-over-time.js`**: practice name is a link when `google_maps_url` is set (`target="_blank"`, `rel="noopener noreferrer"`), otherwise a plain `<span>`.
- **`rating-change-over-time.css`**: styles for `a.rating-row-title-link`.

Regenerated output is under `datasets/output/gtd-greater-manchester-gp-practice-reviews-2026-03-09/` after `python3 build_gtd_gp_practice_dataset.py`.

### you

older reviews (previous years) should colour the year, not just the month of the change, since our dataset uses days/weeks/months/years ago, older years (no sub-month datas) should colour the year.

### assistant

Implementing per-review date precision in the dataset builder and expanding year-precision trend bands to full calendar years on the chart. Reading the relevant code sections.

> `Read` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/build_gtd_gp_practice_dataset.py", "offset": 2255, "limit": 100}

> `Read` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/gtd_gp_map/rating-change-over-time.js", "limit": 120}

### assistant

Adding a precision parser and per-bucket coarseness, serializing `bucket_precision` with each series, and updating the JS to expand year-level edges to full calendar-year bands on the shared month axis.

> `Read` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/build_gtd_gp_practice_dataset.py", "offset": 2438, "limit": 120}

### assistant

Adding `parse_google_relative_review_precision` and per-practice bucket precision tracking.

> `StrReplace` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/build_gtd_gp_practice_dataset.py", "old_string": "    if unit == \"year\":\n        return shift_months(anchor_date, -(quantity * 12)…

> `StrReplace` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/build_gtd_gp_practice_dataset.py", "old_string": "    month_values_by_practice: dict[str, dict[date, float]] = {}\n    practice_revie…

> `StrReplace` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/build_gtd_gp_practice_dataset.py", "old_string": "        for bucket in timeline:\n            if bucket in cumulative_by_month:\n   …

> `StrReplace` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/build_gtd_gp_practice_dataset.py", "old_string": "                \"google_maps_url\": google_maps_url,\n                \"points\": …

> `Read` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/build_gtd_gp_practice_dataset.py", "offset": 2525, "limit": 45}

> `StrReplace` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/gtd_gp_map/rating-change-over-time.js", "old_string": "  /** Merge consecutive month edges with the same up/down trend into one backg…

> `StrReplace` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/gtd_gp_map/rating-change-over-time.js", "old_string": "      const trendRuns = buildTrendRuns(points);", "new_string": "      const t…

> `Shell` {"command": "cd /home/bobbigmac/projects/nhs-complaint-dec-2024/datasets && python3 -m py_compile build_gtd_gp_practice_dataset.py && python3 build_gtd_gp_practice_dataset.py 2>&1 | tail -3", "descrip…

> `Shell` {"command": "head -c 800 /home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/output/gtd-greater-manchester-gp-practice-reviews-2026-03-09/rating-change-over-time-embed.js | tr ',' '\\n' | head -2…

> `Grep` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/output/gtd-greater-manchester-gp-practice-reviews-2026-03-09/rating-change-over-time-embed.js", "pattern": "bucket_precision", "head_…

> `Grep` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/output/gtd-greater-manchester-gp-practice-reviews-2026-03-09/rating-change-over-time.js", "pattern": "yearBoundsIndices"}

### assistant

Here’s what changed:

### Python (`build_gtd_gp_practice_dataset.py`)
- **`parse_google_relative_review_precision`**: maps the same relative-date patterns as the date parser to **`fine`** (minute/hour/day/week + today/yesterday), **`month`** (`N month(s) ago`), or **`year`** (`N year(s) ago`).
- **`merge_relative_date_precision`**: for each calendar month bucket, keeps the **coarsest** label when a month has several reviews (`year` > `month` > `fine`).
- While building reviews per practice, each bucket gets a merged precision map; the timeline adds **`bucket_precision`**: one entry per month (or `null` if that month had no reviews).

### JS (`rating-change-over-time.js`)
- **`edgeHorizontalSpan`**: if `bucket_precision[k] === "year"`, the band uses **`yearBoundsIndices`** so the fill runs from the first to last month index on the shared axis for that **calendar year**; otherwise it stays a **single-month** band (`fine` / `month` / missing).
- **Runs** of the same up/down direction still merge; each edge in the run contributes its span, then **min/max x** is taken so year-wide and month-wide edges combine correctly.

Rebuild with `python3 datasets/build_gtd_gp_practice_dataset.py` so `rating-change-over-time-embed.js` includes `bucket_precision`.

### you

On the map page, instead of Trajectories, call it Timelines

> `Grep` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024", "pattern": "Trajectories"}

> `StrReplace` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/gtd_gp_map/map.html", "old_string": "<a class=\"home-link\" href=\"rating-change-over-time.html\" title=\"All practices · rating traj…

> `StrReplace` {"path": "/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/output/gtd-greater-manchester-gp-practice-reviews-2026-03-09/map.html", "old_string": "<a class=\"home-link\" href=\"rating-change-ov…

### assistant

Updated the map sidebar link in `datasets/gtd_gp_map/map.html` and the generated `datasets/output/gtd-greater-manchester-gp-practice-reviews-2026-03-09/map.html`: label is **Timelines** and the title is **All practices · rating timelines**. Future `build_gtd_gp_practice_dataset.py` runs will keep copying the template from `gtd_gp_map`.
