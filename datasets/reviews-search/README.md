# Reviews Search

Local fulltext search over the plaintext review exports in `datasets/output/.../google-review-texts/`.

This is intentionally separate from `datasets/reviews-analysis/` so the existing NLP/graph grouping flow stays untouched.

## What It Does

- indexes one document per captured review into a local SQLite FTS5 database
- reads the existing plaintext review files directly
- keeps exact review text so search results can return grounded quotes
- supports query-time filters and aggregate stats

It does not use embeddings, OpenAI APIs, or the existing classifier graph.

## Build

```bash
python3 datasets/reviews-search/index_reviews.py
```

Optional:

```bash
python3 datasets/reviews-search/index_reviews.py --include-visible-cards
```

By default it indexes the latest `datasets/output/gtd-greater-manchester-gp-practice-reviews-*` report and writes:

- `datasets/reviews-search/output/reviews_index.sqlite`

## Query

Search for relevant reviews plus quotes:

```bash
python3 datasets/reviews-search/query_reviews.py search --q "phone lines never answer"
```

Prefer phrase matching first:

```bash
python3 datasets/reviews-search/query_reviews.py search --q "\"can't get an appointment\"" --phrase
```

Get a grounded plain-text answer with counts and quotes:

```bash
python3 datasets/reviews-search/query_reviews.py report --q "reception staff rude"
```

Get aggregate stats for a slice:

```bash
python3 datasets/reviews-search/query_reviews.py stats --q "appointment" --max-rating 2
```

Inspect nearby reviews from the same practice:

```bash
python3 datasets/reviews-search/query_reviews.py context --id 42 --before 1 --after 2
```

## Useful Filters

- `--practice P82013001`
- `--practice "City Health Centre"`
- `--min-rating 4`
- `--max-rating 2`
- `--gtd-only`
- `--non-gtd-only`
- `--json`

## Notes

- default indexing mode is `full_feed` only
- `--include-visible-cards` widens the corpus to partial captures too
- quote extraction is deterministic and only returns text found in stored reviews
