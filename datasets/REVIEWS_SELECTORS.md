# Google Maps Review Collection Controls

This is the current live behavior used by [collect_google_maps_reviews.py](/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/collect_google_maps_reviews.py) when driving Firefox headfully against Google Maps.

## Session setup

- Opens `https://www.google.com/maps` once and keeps that shell open for the full run.
- Uses a copied Firefox profile via `-profile`, not a fresh clean browser profile.
- Reuses the existing search box between practices instead of navigating practice URLs directly.

## Search box selectors

Search input discovery is tried in this order:

- `input#searchboxinput`
- `input[role="combobox"]`
- `input[class*="UGojuc"]`
- `input[aria-label*="Search Google Maps"]`
- `input[placeholder*="Search Google Maps"]`
- `input[aria-label*="Search"]`
- `input`

Search behavior:

- focus input
- click input
- `Ctrl+A`
- `Backspace`
- JS clear via `value = ''` plus `input` and `change` events
- type query
- `Enter`

The collector waits for one of:

- URL change
- title change
- page kind becoming `/place/` or `/search/`
- search box value matching the requested query

## Search results and place selection

Page-kind test:

- place page if URL contains `/place/`
- search page if URL contains `/search/`

If Google leaves the run on a search results page, the collector clicks the first visible place candidate matching:

- `a[href*="/place/"]`
- `a.hfpxzc`

## Overall practice metrics

Title/rating/review-count are taken from the live place page, not from raw network capture:

- title: browser title without ` - Google Maps`
- rating scan: `div[role="main"] span`, looking for text matching `[0-5]\.\d`
- review count scan: same span sweep, reading `aria-label` containing `reviews`

## Opening the reviews panel

Buttons are scanned in two passes:

1. Any visible `button` with:
- aria-label containing `More reviews`
- button text starting `More reviews`

2. Fallback visible `button` with:
- aria-label starting `Reviews for `

If those clicks are not found, the collector still treats the panel as open if review cards already exist:

- `div.jftiEf`

## Review sort control

The run tries to sort by newest on every opened reviews panel.

Sort button detection:

- visible `button` with aria-label containing `Sort reviews`
- visible `button` with text exactly `Sort`

Sort menu choice:

- `[role="menuitemradio"]`
- `[role="menuitem"]`

The first item whose text starts with `Newest` is clicked.

## Review card selectors

Review cards:

- `div.jftiEf`

Within each card:

- author: `.d4r55`
- relative date: `.rsqaWe`
- stars aria-label: `.kvMYJc`
- text candidates: `.wiI7pd`, `.MyEned`
- raw full card text: card `textContent`

Expandable review-text buttons inside each card:

- any `button` whose normalized label is exactly `more`
- exactly `full review`
- starts with `more ` and also contains `review`

## Practice reply extraction

Practice replies are stored under the review as `owner_reply`, not as standalone reviews.

Reply header detection:

- XPath: `.//*[contains(normalize-space(.), 'Response from the owner')]`

Reply date pattern:

- `today`
- `yesterday`
- `a/an/<n> minute(s)/hour(s)/day(s)/week(s)/month(s)/year(s) ago`
- optional `Edited`

Reply text sources:

- second extracted text block from the card when present
- fallback parse from raw card text after `Response from the owner`

## Review feed container selectors

Full-feed scrolling tries these containers in order:

- `div[role="feed"]`
- `div.m6QErb.DxyBCb.kA9KIf.dS8AEf[tabindex="-1"]`
- `div.m6QErb.DxyBCb.kA9KIf.dS8AEf`
- `div.m6QErb[tabindex="-1"]`
- `div.m6QErb`
- `div.m6QErb[aria-label*="review"]`
- `div.m6QErb[aria-label*="Review"]`

Fallback:

- first `div.jftiEf`
- then nearest ancestor `div` with class containing `m6QErb`

## Full-feed scrolling behavior

When `--full-reviews all` is active:

- scroll feed to top first
- inspect all currently loaded `div.jftiEf` cards each round
- only click expanders in the last 24 cards for speed
- scroll by `max(clientHeight * 1.2, 800)` each round
- after stagnation, force `scrollTop = scrollHeight`
- wait briefly for either:
  - more `div.jftiEf` cards
  - feed `scrollHeight` growth

Stop conditions:

- reached explicit `--full-review-limit`
- reached expected total review count from the page
- 3 stagnant rounds and 2 end-of-feed rounds
- hard cap of 90 rounds

## Raw review transport capture

Raw capture is installed in-page with JS wrappers around:

- `window.fetch`
- `XMLHttpRequest.prototype.open/send`

Only requests whose URL contains this substring are retained:

- `/maps/rpc/listugcposts`

For each captured response the sidecar stores:

- sequence and capture time
- source: `fetch` or `xhr`
- method
- URL
- HTTP status
- content type
- request body
- raw response body
- capture error if body extraction failed

This is written to:

- `datasets/output/gtd-greater-manchester-gp-practice-reviews-2026-03-09/google-review-raw/*.json`

## Main outputs

Processed practice results are written into:

- `datasets/output/gtd-greater-manchester-gp-practice-reviews-2026-03-09/google_maps_recent_reviews.json`

Per-practice text exports are written into:

- `datasets/output/gtd-greater-manchester-gp-practice-reviews-2026-03-09/google-review-texts/*.txt`

Important markers to check during long runs:

- `review_collection_mode = full_feed`
- `raw_review_responses_captured > 0`
- `review_cards_collected` roughly matching `google_review_count` on full feeds
- `google_maps_title` matching the intended practice rather than a sidebar detour
