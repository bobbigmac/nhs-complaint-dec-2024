# Graph-Based Review Classifier Model

## Overview

The classifier replaces heuristic keyword bucketing with a **data-driven graph model**. Reviews are nodes; edges represent semantic similarity. Clusters emerge from the graph; leftover reviews are handled by fallback heuristics that can be refined by analysing rejects.

**Principle:** Do not predefine a dictionary of keywords. Let the source data shape the taxonomy.

---

## Architecture

### 1. Graph Construction

- **Nodes:** Each review (identified by `{practice_code}:{review_index}` or `_across:{index}`).
- **Node features:** Text embedding (TF-IDF or sentence embedding) + optional metadata (rating, sentiment proxy).
- **Edges:** Similarity between reviews above a threshold. Similarity is computed from:
  - Text meaning (TF-IDF cosine similarity, or sentence-transformers if available)
  - Optional: rating/sentiment as a soft tie-breaker (reviews with similar ratings may be slightly favoured)

No predefined keywords. Similarity is purely from the text and metadata.

### 2. Clustering

- **Method:** Community detection (e.g. Louvain) or hierarchical/spectral clustering on the similarity graph.
- **Output:** Each review gets a `cluster_id` (e.g. `c0`, `c1`, …).

### 3. Cluster Labelling

- **Derived from data:** For each cluster, extract the most distinctive terms (e.g. top TF-IDF terms within cluster vs. corpus).
- **Human-readable label:** Short phrase from those terms (e.g. "appointments, phone, booking" → "Appointments & access").
- Labels are generated, not predefined.

### 4. Leftovers / Rejects

- Reviews that do not fit well into any cluster (low connectivity, singleton clusters, or below similarity threshold) go to a catch-all.
- These can be:
  - Labelled `uncategorised` and analysed later to improve heuristics or thresholds
  - Optionally passed through a lightweight heuristic (e.g. sentiment-only) for presentation

---

## Data Flow

```
.classifier_input.json (or raw reviews)
        │
        ▼
┌───────────────────────────────────────┐
│  build_classifier_graph.py             │
│  - Flatten reviews → (id, text, rating) │
│  - TF-IDF / embeddings                 │
│  - Similarity graph                    │
│  - Cluster extraction                  │
│  - Label derivation (top terms)        │
└───────────────────────────────────────┘
        │
        ▼
review_classifications.json
  - Map: review_id → { cluster_id, primary_bucket, buckets, sentiment }
  - cluster_labels: cluster_id → human label
```

---

## Text Preprocessing

Reviews are informal, messy natural language. Preprocessing:

- Unicode normalisation (NFKC)
- Strip emojis and decorative symbols
- Collapse repeated punctuation
- Preserve apostrophes for contractions (don't, can't)
- Stopwords from `sklearn.feature_extraction.text.ENGLISH_STOP_WORDS` (imported, not hardcoded)

---

## Output Format (Stable JSON for Browser)

### `review_classifications.json`

```json
{
  "meta": {
    "generated_date": "2026-03-16",
    "model": "graph",
    "cluster_count": 12
  },
  "cluster_labels": {
    "c0": "Appointments & phone access",
    "c1": "Reception & staff",
    "c2": "Referrals & admin",
    "uncategorised": "Other"
  },
  "classifications": {
    "Y02960:0": {
      "cluster_id": "c0",
      "primary_bucket": "c0",
      "buckets": ["c0"],
      "sentiment": "neutral"
    },
    "_across:42": {
      "cluster_id": "c1",
      "primary_bucket": "c1",
      "buckets": ["c1"],
      "sentiment": "negative"
    }
  }
}
```

- `primary_bucket` and `buckets` use cluster IDs (e.g. `c0`) so the browser can look up labels from `cluster_labels`.
- This keeps the payload small: no duplication of labels per review.

### Integration with `raw_reviews_extended.json`

At build time, `build_reviews_evidence.py` (or a post-step) merges `review_classifications.json` into the review objects:

- Each review gets `primary_bucket`, `buckets` from the graph classifier.
- The browser continues to use `primary_bucket` and `buckets` as before.
- `BUCKET_LABELS` in the front end is replaced by loading `cluster_labels` from the classifications meta, so dynamic labels work without code changes.

---

## Portability

- **Build-time only:** The graph construction and clustering run in Python at build time. They are not portable to the browser.
- **Browser:** Loads `raw_reviews_extended.json` (with merged classifications) and optionally `review_classifications.json` for label lookup. No recompute in the browser.
- **Stable JSON:** Classifications are written to a stable file; the browser uses them for presentation only.

---

## Tuning (classifier_config.json)

- **min_text_len:** 40 – exclude very short reviews
- **min_df / max_df:** filter rare and ubiquitous terms
- **dbscan_eps:** 0.64 – similarity threshold (lower = stricter, more uncategorised)
- **dbscan_min_samples:** 3 – require 3+ neighbours to form cluster
- **Metadata filter:** excludes reviews that are mostly "Name N reviews N ago" spillage

## Dependencies

- **Python:** `scikit-learn` (TF-IDF, cosine similarity, clustering). Required on dev; no stdlib fallback.
- **Fallback when sklearn unavailable:** Commit `output/review_classifications.json` from a dev run. The build uses this committed copy when the classifier cannot run (e.g. CI without sklearn).

---

## Query / Exploration Script

A companion script `query_classifier.py` (or flags on `build_classifier_graph.py`) can:

- Load the graph and classifications
- Query: "Which reviews are most similar to review X?"
- Query: "Show cluster c3 contents"
- Export: cluster summaries, leftover analysis for heuristic tuning

---

## Future Improvements

- Analyse `uncategorised` reviews to tune similarity threshold or add targeted heuristics
- Experiment with sentence-transformers for better semantic similarity
- Optional Compromise-based sentiment for text when rating is missing
