# Reviews Analysis – Evidence Page & Classifier

This document captures the spec and implementation plan for the reviews evidence page: a tool to explore raw Google reviews from practices that have had **extended (full-feed) reviews** gathered, grouped by practice, classified by theme/type, and displayed as an interactive overview with common-theme cross-linking.

Treat this as a peer to the map page: a wide-reaching tool, properly integrated into the build.

---

## Source of Truth: Extended Reviews

**Property:** `review_collection_mode: "full_feed"`

- **Where it lives:**
  - Per-practice `.txt` files: header line `Review collection mode: full_feed` in `google-review-texts/{canonical_code}-{slug}.txt`
  - `google_maps_recent_reviews.json`: each capture record has `review_collection_mode` (`"full_feed"` or `"visible_cards"`)
- **Scope:** Mostly GTD-run practices (13), plus some non-GTD practices intentionally gathered with full reviews (e.g. via `--full-reviews all` or manual runs). We intend to add more.
- **Dataset gap:** The main `gtd_greater_manchester_gp_practices.json` does not expose `review_collection_mode`. We must either parse the `.txt` header or join with `google_maps_recent_reviews.json` to identify practices with extended reviews.

---

## Implementation TODOs

### Build & Data Pipeline

- [x] **Compile raw-reviews JSON** – Build step that produces a single JSON file from the datasets' raw reviews, **only for practices with extended reviews** (`review_collection_mode: full_feed`). Parse `.txt` files under `google-review-texts/` or use `google_maps_recent_reviews.json` to determine which practices qualify.
- [x] **Add `has_extended_reviews` (or equivalent) to dataset** – Derived from `.txt` header; no separate index needed.
- [x] **Own build file for reviews analysis** – `build_reviews_evidence.py` under `datasets/reviews-analysis/`.
- [x] **Integrate into site build** – Called from `site/build.py`; outputs to `reviews-evidence/`. Use `--skip-reviews-evidence` to exclude.

### Classifier & Summariser

- [x] **Lite-NLP classifier (heuristics)** – `classifier.js` with keyword-based buckets: reception, appointments, prescriptions, referrals, continuity, staff, digital, results, waiting_room, positive.
- [x] **Special-case overrides** – `classifier_overrides.json` keyed by `{canonical_code}:{reviewIndex}`.
- [x] **Classifier in JavaScript** – Runs in Node at build time; same logic available for browser (filtering uses precomputed buckets).
- [ ] **Keyword/phrase summary table** – Cross-practice theme aggregation; deferred for exploration phase.

**Classifier limitations (needs work):** The current classifier is very crude. A major problem is that making "positive" its own category tends to suck the warm/positive energy out of other categories (e.g. a review praising reception gets bucketed as "positive" instead of "reception"). The classifier should be rewritten with more solid, stable rules.

### Evidence Page UI

- [x] **Header with practice stats** – Practice count, review count; updates when filtered.
- [x] **Review squares** – Coloured by rating (1–5 stars), numbered; click opens full text in panel below.
- [x] **GTD pre-takeover greying** – Reviews with `estimated_year < gtd_takeover_date` year are greyed (opacity 0.5).
- [x] **Year filter dropdown** – Max-year filter; "Filtered by year" badge when active.
- [x] **Load JSON client-side** – Fetches `raw_reviews_extended.json`.
- [x] **Display by class/type/kind** – Grouped by `primary_bucket`; full text in expand panel.
- [x] **Recent Reviews across Manchester** – Table below practice sections showing reviews from non-extended practices (from `google_maps_recent_reviews.json`). Each row shows practice name, code, rating, date, theme, and text preview; click to expand full text. Respects timespan and sort filters.
- [x] **Treemap view** – Toggle between Squares (column layout) and Treemap. Treemap shows each bucket/theme as a proportional block with coloured header; blocks are sized by review count; squares remain clickable for popover.

### Future / Deferred

- [ ] **Text search** – Consider adding text search as a later feature. Do not implement yet.
- [x] **Exclude from build** – `--skip-reviews-evidence` flag; homepage card hidden when skipped.

---

## Interpretation Notes

| Requirement | Interpretation |
|-------------|----------------|
| "Extended reviews" | Practices with `review_collection_mode: full_feed` (from txt header or `google_maps_recent_reviews.json`). |
| "Property somewhere" | Currently in `.txt` header and `google_maps_recent_reviews.json`; not in main practice JSON. We should add or derive a clear property. |
| "Compile a JSON file" | Single JSON bundling all reviews from extended-review practices, with practice metadata, review text, date, rating, and classification. |
| "Table of keywords/phrases" | Summary view: extracted themes per practice, with counts, linked to rating/sentiment. |
| "Common themes between practices" | Cross-practice aggregation of classifier buckets; show which themes recur and how they correlate with good/bad reviews. |
| "Class/type/kind/systems" | Classifier buckets (e.g. reception, appointments, prescriptions, continuity, digital). |
| "Classifier in JS" | Same JS module runs at build time (Node) and in the browser for client-side filtering. |
| "Coloured/numbered square" | Compact visual representation; colour = rating or bucket, number = order. |
| "Panel below" | Expandable area showing full review text on click. |
| "Slightly greyed out" | CSS opacity or similar for pre-takeover GTD reviews. |
| "Max-time dropdown" | Filter by year (or date range); updates overview and shows "filtered" state. |

---

## File Layout (Proposed)

```
datasets/reviews-analysis/
├── REVIEWS_ANALYSIS.md          # This file
├── build_reviews_evidence.py    # Orchestrates: parse txt, call classifier, emit JSON
├── classifier.js                # Shared classifier + summariser (Node + browser)
├── classifier_overrides.json    # Optional LLM-tweakable overrides
├── output/
│   ├── raw_reviews_extended.json   # Compiled reviews for extended-review practices
│   └── reviews_evidence_summary.json  # Precomputed keyword/theme summary 
└── (evidence page HTML/JS, or in site/? Should go into the build like all our other pages, linked via a homepage panel)
```

---

## Data Flow

1. **Build time:** `build_reviews_evidence.py` reads report dir, identifies practices with `full_feed`, parses `.txt` files, aggregates recent reviews from `google_maps_recent_reviews.json` for all non-extended practices into `recent_reviews_across_manchester`, runs `classifier.js` (Node) on both `practices` and `recent_reviews_across_manchester`, optionally applies overrides, writes `raw_reviews_extended.json`.
2. **Site build:** Copies `raw_reviews_extended.json` and evidence page assets into site output (e.g. `reviews-evidence/`).
3. **Runtime:** Evidence page loads JSON, renders practice squares + panel, applies year filter and GTD greying; below that, renders "Recent Reviews across Manchester" table with reviews from non-extended practices (same timespan/sort filters).

### Output JSON structure

- `practices`: array of extended-practice objects with `reviews`, `canonical_code`, `practice_name`, etc.
- `recent_reviews_across_manchester`: flat array of reviews from practices *not* in the extended set. Each item has `author`, `date_raw`, `rating_stars`, `rating_label`, `text`, `practice_name`, `canonical_code`, `estimated_year`, `estimated_months_ago`, `buckets`, `primary_bucket`. Source: `google_maps_recent_reviews.json` (`recent_reviews` per practice).

---

## References

- Map page: `datasets/output/.../map.html`, copied to `site/.vite-src/map/`
- Practice patterns: `datasets/practice-patterns/` – sibling feature with own build script
- Takeover dates: `datasets/config/gtd_takeover_dates.json`
- Raw review format: `google-review-texts/{code}-{slug}.txt` (Author, Date, Rating, text blocks)
- `google_maps_recent_reviews.json`: has `review_collection_mode`, `canonical_code`, `recent_reviews`
