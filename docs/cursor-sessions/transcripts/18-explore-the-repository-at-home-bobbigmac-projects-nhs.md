---
cursor_session: fe2db677-41d1-47b8-a4c3-e1b8382252d2
source: cursor-composer
cursor_hint: ?
user_entries: 1
---

# transcript — explore-the-repository-at-home-bobbigmac-projects-nhs

### assistant

I’m mapping the existing review-processing pipeline first, then I’ll trace where plaintext inputs become outputs so I can suggest a safe separate integration point.

### assistant

I’ve identified the likely pipeline entrypoints; next I’m reading the collection, merge, dataset-build, and review-analysis scripts to pin down input/output formats and separation boundaries.

### assistant

I’ve confirmed the collector/merge/analysis split. Now I’m checking the main dataset builder and any “query/group” helpers to see what outputs are treated as canonical versus downstream-only.

### assistant

I’ve got the core data path. I’m doing one last pass over review-query/grouping entrypoints so the recommendation is grounded in what already behaves like a browser/search layer versus a build-time pipeline stage.

### you

Explore the repository at /home/bobbigmac/projects/nhs-complaint-dec-2024 to find existing review-processing code, especially under datasets/ and any scripts related to querying/grouping reviews. Focus on plaintext review inputs, existing output formats, and where a new non-NLP fulltext index/query tool could live without modifying the existing NLP/graph grouping pipeline. Return: 1) relevant files/paths, 2) summary of current review data flow, 3) recommended integration point for a new separate tool, 4) any risks/constraints to avoid breaking existing behavior.

### assistant

I’m mapping the existing review-processing pipeline first, then I’ll trace where plaintext inputs become outputs so I can suggest a safe separate integration point.

### assistant

I’ve identified the likely pipeline entrypoints; next I’m reading the collection, merge, dataset-build, and review-analysis scripts to pin down input/output formats and separation boundaries.

### assistant

I’ve confirmed the collector/merge/analysis split. Now I’m checking the main dataset builder and any “query/group” helpers to see what outputs are treated as canonical versus downstream-only.

### assistant

I’ve got the core data path. I’m doing one last pass over review-query/grouping entrypoints so the recommendation is grounded in what already behaves like a browser/search layer versus a build-time pipeline stage.

### assistant

I haven’t found any existing full-text index/search stack in the repo, which is good for separation. I’m reading one sample review text export and one raw capture sidecar now so I can describe the actual on-disk formats precisely.

### assistant

## 1) Relevant files / paths

Core collection + merge:
- `/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/collect_google_maps_reviews.py`
- `/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/merge_google_maps_reviews.py`
- `/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/run_google_maps_collection_batches.py`
- `/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/build_gtd_gp_practice_dataset.py`
- `/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/AGENTS.md`

Review-analysis / grouping / query-like layers:
- `/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/reviews-analysis/build_reviews_evidence.py`
- `/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/reviews-analysis/build_classifier_graph.py`
- `/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/reviews-analysis/inspect_classifier.py`
- `/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/reviews-analysis/generate_gtd_summaries.py`
- `/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/reviews-analysis/reviews_evidence.html`
- `/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/reviews-analysis/REVIEWS_ANALYSIS.md`
- `/home/bobbigmac/projects/nhs-complaint-dec-2024/site/build.py`

Current review data outputs:
- `/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/output/gtd-greater-manchester-gp-practice-reviews-2026-03-09/google_maps_recent_reviews.json`
- `/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/output/gtd-greater-manchester-gp-practice-reviews-2026-03-09/google-review-texts/`
- `/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/output/gtd-greater-manchester-gp-practice-reviews-2026-03-09/google-review-raw/`
- `/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/output/gtd-greater-manchester-gp-practice-reviews-2026-03-09/gtd_greater_manchester_gp_practices.json`
- `/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/output/gtd-greater-manchester-gp-practice-reviews-2026-03-09/gtd_greater_manchester_gp_practices.csv`
- `/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/output/gtd-greater-manchester-gp-practice-reviews-2026-03-09/google_maps_manual_review.md`

Analysis outputs:
- `/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/reviews-analysis/output/raw_reviews_extended.json`
- `/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/reviews-analysis/output/review_classifications.json`

Sample current formats:
- `/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/output/gtd-greater-manchester-gp-practice-reviews-2026-03-09/google-review-texts/P82013001-dr-y-loomba-and-partner.txt`
- `/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/output/gtd-greater-manchester-gp-practice-reviews-2026-03-09/google-review-raw/P82013001-dr-y-loomba-and-partner.json`

## 2) Summary of current review data flow

Current flow is:

1. `collect_google_maps_reviews.py` scrapes Google Maps and writes:
   - one big structured JSON: `google_maps_recent_reviews.json`
   - one plaintext file per practice: `google-review-texts/*.txt`
   - one raw transport sidecar per practice: `google-review-raw/*.json`

2. `merge_google_maps_reviews.py` joins those capture results back into the main dataset by `canonical_code`, but only merges summary fields plus file references, not the full review bodies.

3. `build_gtd_gp_practice_dataset.py` treats `google_maps_recent_reviews.json` as an input for derived reporting/timeseries and keeps `google_review_text_file` as a pointer in the main CSV/JSON.

4. `datasets/reviews-analysis/build_reviews_evidence.py` is a separate downstream analysis layer. It reads the plaintext `.txt` review exports and/or `google_maps_recent_reviews.json`, filters for `review_collection_mode == "full_feed"`, dedupes/normalizes, then runs `build_classifier_graph.py`.

5. `generate_gtd_summaries.py` and `reviews_evidence.html` consume the classified output for grouped browsing.

Plaintext input format is already stable and human-readable:

```1045:1111:/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/collect_google_maps_reviews.py
def write_review_text_file(text_dir: Path, result: dict[str, object]) -> str:
    ...
    header_lines = [
        f"Practice: {result.get('practice_name', '')}",
        f"Canonical code: {result.get('canonical_code', '')}",
        ...
        f"Review collection mode: {result.get('review_collection_mode', '')}",
        ...
        "Captured reviews",
        "================",
```

The analysis pipeline explicitly parses those `.txt` files and uses `full_feed` as the “extended reviews” signal:

```63:69:/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/reviews-analysis/build_reviews_evidence.py
def parse_reviews_from_txt(content: str, *, require_full_feed: bool = True) -> list[dict[str, Any]]:
    """Parse review blocks from a google-review-texts .txt file."""
    lines = content.splitlines()
    header = parse_txt_header(lines)
    if require_full_feed and header.get("review_collection_mode") != "full_feed":
        return []
```

## 3) Recommended integration point for a new separate tool

Best fit: add a new sibling feature directory under `datasets/`, not inside `datasets/reviews-analysis/`.

Recommended location:
- `/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/reviews-search/`
or
- `/home/bobbigmac/projects/nhs-complaint-dec-2024/datasets/reviews-index/`

Why:
- `datasets/reviews-analysis/` is already the NLP/graph/classifier pipeline.
- `build_reviews_evidence.py` and `build_classifier_graph.py` assume analysis/grouping semantics, not neutral document indexing.
- A separate sibling directory matches the existing project shape better, like `datasets/practice-patterns/` versus `datasets/reviews-analysis/`.
- Your new tool can consume `google-review-texts/*.txt` directly as the primary corpus, optionally enriching with `google_maps_recent_reviews.json` metadata, without changing merge/build behavior.

Recommended contract for the new tool:
- Read from `datasets/output/.../google-review-texts/*.txt` as primary plaintext source.
- Optionally join on `canonical_code` via `gtd_greater_manchester_gp_practices.json` or `google_maps_recent_reviews.json`.
- Write its own outputs to its own folder, e.g.:
  - `datasets/reviews-search/output/review_documents.jsonl`
  - `datasets/reviews-search/output/review_index.sqlite`
  - `datasets/reviews-search/output/search_results/...`
- Do not write back into:
  - `google_maps_recent_reviews.json`
  - `gtd_greater_manchester_gp_practices.json`
  - `raw_reviews_extended.json`
  - `review_classifications.json`

If you want a browser UI later, `site/build.py` already publishes sibling artifacts cleanly, so the search tool could later be copied into a separate site section the same way `reviews-evidence` is.

## 4) Risks / constraints to avoid breaking existing behavior

- Do not change the existing `google-review-texts/*.txt` header/body format. `build_reviews_evidence.py` parses it directly.
- Do not repurpose `review_collection_mode`; analysis relies on `full_feed` versus `visible_cards`.
- Do not treat `raw_reviews_extended.json` as source-of-truth input for indexing if you want to stay outside NLP/grouping. That file is already deduped, filtered, classified, and partially opinionated.
- Do not change `google_maps_recent_reviews.json` structure unless you also update:
  - `merge_google_maps_reviews.py`
  - `build_gtd_gp_practice_dataset.py`
  - `build_reviews_evidence.py`
- Be careful with owner replies. Collector stores them nested under `owner_reply`; downstream code mostly expects patient-review-centric fields.
- Some `.txt` bodies still contain metadata spill or empty review text; current analysis code already has cleanup/dedupe logic, so a raw fulltext index may surface noisier text unless you add light normalization.
- `merge_google_maps_reviews.py` only merges summary fields and file paths into the main dataset. Keeping your new tool sidecar-only avoids destabilizing the dataset build.
- There is no existing fulltext engine in the repo. I found no current `sqlite FTS`, `Whoosh`, `BM25`, `tantivy`, or similar stack, so introducing one would be net new and should stay isolated.

If useful, I can next sketch a minimal read-only design for `datasets/reviews-search/` around the existing `.txt` corpus and metadata joins.
