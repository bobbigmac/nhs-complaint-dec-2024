# Datasets Notes

This folder contains the GP-practice dataset build, Google Maps review capture flow, merge/update steps, and downstream analysis inputs.

## Core Files

- `collect_google_maps_reviews.py`
  Primary Google Maps collector.
  Uses Selenium + Firefox with a copied local Firefox profile.
  Writes raw structured Google Maps capture output to `output/.../google_maps_recent_reviews.json`.
  Writes one text file per practice under `output/.../google-review-texts/`.
  Writes raw Google Maps review transport dumps under `output/.../google-review-raw/`.
- `run_google_maps_collection_batches.py`
  Wrapper that runs the collector in randomized batches and then runs the merge step.
  Useful for long unattended passes, but not the preferred mode when a human wants to watch one continuous Firefox session.
- `merge_google_maps_reviews.py`
  Merges Google Maps direct results back into the main CSV/JSON dataset and regenerates derived artifacts.
- `build_gtd_gp_practice_dataset.py`
  Main dataset builder. Also consumes `google_maps_recent_reviews.json` for some derived reporting and still contains an older TODO about practice replies.
- `reviews-analysis/build_reviews_evidence.py`
  Downstream analysis layer that flattens `recent_reviews` from the raw Google capture.

## Google Maps Capture Design

The intended review-capture flow is now:

1. Copy the user’s default Firefox profile into `datasets/.tooling/firefox-profile-copy`.
2. Launch Firefox headfully, not headlessly, with that copied profile.
3. Open Google Maps once and keep the same browser/tab/process alive across the selected practice set.
4. Move from practice to practice using the live Google Maps search control, not by repeatedly rebuilding the URL.
5. Open the reviews panel, sort to newest, and scroll the full feed when required.
6. Capture raw review transport responses from the live page session while the feed is loading.
7. Persist results after each practice so interruptions do not lose the whole pass.

Important constraint:

- When doing an observed/manual pass, do not bounce Firefox between practices. The browser session should stay alive across the whole targeted set.

## Search Box Reality

Do not assume the Maps search control is always `#searchboxinput`.

In the live Firefox/profile session inspected here, Google Maps exposed the search control as a visible `input[role="combobox"]`.

That means:

- search-box detection must tolerate current Google Maps shell variants
- shell readiness should be based on the visible search control plus the page body, not a brittle `div[role="main"]` requirement on the home shell

## Review Capture Requirements

### 1. Headful by default

- The normal/manual operating mode is visible Firefox.
- `--headless` should remain optional only for special unattended/debug use.

### 2. Persistent practice-to-practice session

- One collector run should keep one Firefox process alive across all requested practices.
- Practice changes should happen through the open Maps search box in the same tab.

### 3. Full history for new records

- New review records should default to full-feed capture, not just visible-card snippets.
- The collector now treats `--full-reviews new` as the default mode.
- The batch runner should use the same default so newly created records collect full history automatically.

### 4. Practice responses as replies, not reviews

- Google Maps owner/practice responses are distinct UI elements on the review card.
- They should be stored as a nested reply on the review record, not folded into the patient review text and not promoted to a separate top-level review object.
- Current raw review shape now supports:

```json
{
  "author": "Patient Name",
  "relative_date": "a week ago",
  "star_label": "1 star",
  "text": "Patient review text",
  "raw_card_text": "Full raw card text",
  "owner_reply": {
    "relative_date": "6 hours ago",
    "text": "Practice response text",
    "raw_text": "Raw owner-reply block"
  }
}
```

Notes:

- extraction should prefer distinct DOM content where available
- raw-card parsing can be used as a fallback when Google’s classes are unstable
- downstream consumers that only read `author`, `relative_date`, `star_label`, and `text` remain compatible

### 5. Raw review transport capture

- Firefox/WebDriver here can see request metadata through BiDi, but response bodies are more reliably available by monkeypatching the page’s own `fetch` and `XMLHttpRequest`.
- The useful Google Maps review endpoint observed in practice is `/maps/rpc/listugcposts`.
- The collector now captures those raw `listugcposts` responses from the live page session and writes them to a per-practice sidecar JSON file in `google-review-raw/`.
- The main `google_maps_recent_reviews.json` file should stay relatively lean: it keeps capture metadata such as `raw_review_capture_enabled`, `raw_review_responses_captured`, and `raw_review_capture_file`, but not the full raw response bodies.
- This gives us the raw Google payload for later parsing without bloating the main working dataset.

## Current Collector Behaviour

`collect_google_maps_reviews.py` currently does the following:

- discovers the default Firefox profile from `~/.mozilla/firefox/profiles.ini`
- refreshes a disposable copied profile directory
- launches Firefox with Selenium
- filters practice rows by canonical code, missing-Google state, practice-name filter, and resume state
- resolves the Google Maps query from practice name + postcode, with optional overrides
- writes back the raw JSON file after each practice
- writes per-practice text exports after each practice

Key fields in the raw JSON result object:

- `google_maps_title`
- `google_maps_url`
- `google_rating`
- `google_review_count`
- `page_kind`
- `scan_status`
- `reviews_opened`
- `reviews_sorted_newest`
- `review_collection_mode`
- `review_cards_collected`
- `owner_replies_collected`
- `raw_review_capture_enabled`
- `raw_review_responses_captured`
- `raw_review_capture_file`
- `recent_reviews`

## Merge/Output Contract

`merge_google_maps_reviews.py` currently merges these Google Maps capture records back into the main practice dataset by `canonical_code`.

The merge currently uses:

- the Google Maps title and title-match score
- Google rating and review count
- number of review cards captured
- relative path to the per-practice text export
- relative path to the per-practice raw review sidecar if present

The merge does not currently need structural changes for `owner_reply`, because replies stay nested inside each review in the raw JSON/text export.

## Manual Run Pattern

Preferred command shape for a watched/manual continuous session:

```bash
datasets/.venv-google-reviews/bin/python -u datasets/collect_google_maps_reviews.py \
  --canonical-code CODE1 \
  --canonical-code CODE2 \
  --canonical-code CODE3 \
  --canonical-code CODE4 \
  --canonical-code CODE5 \
  --limit 5 \
  --pause-seconds 1 \
  --pause-jitter-seconds 0 \
  --full-reviews all
```

Why this mode:

- one Firefox session
- one open Maps tab
- visible progression practice-to-practice
- raw JSON flushed after each practice

If dataset rows should be refreshed afterward, run:

```bash
python3 datasets/merge_google_maps_reviews.py
```

## Five-Practice Manual Extension Target

For the current observed pass, the chosen weak-end Manchester practices were:

- `P84026` Dickenson Road Medical Centre
- `P84644` Parkside Surgery
- `P84023` Surrey Lodge Practice
- `P84072` The Robert Darbishire Practice
- `P84046` Cheetham Hill Medical Centre

These were chosen pragmatically from the poor-performing Manchester end of the current dataset, mainly by low Google rating and useful review volume.

## Known Risks

- Google Maps DOM changes frequently; selectors must stay defensive.
- The home-shell structure is not the same as the place/reviews shell.
- Full-feed scrolling still takes time for high-volume practices, though it is now less conservative than the first implementation.
- Owner replies may still need periodic parser tuning as Google changes card markup.
- Raw transport capture currently focuses on `listugcposts`; if Google moves owner replies or hidden fields elsewhere, the capture filter may need widening.
- `run_google_maps_collection_batches.py` still restarts the collector between batches by design; use the collector directly for one continuous observed browser session.
