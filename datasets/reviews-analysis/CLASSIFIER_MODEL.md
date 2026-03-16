# Graph-Based Review Classifier Model

## Overview

The classifier replaces heuristic keyword bucketing with a **data-driven graph model**. Reviews are nodes; edges represent semantic similarity. Clusters emerge from the graph; leftover reviews are handled by fallback heuristics that can be refined by analysing rejects.

**Principle:** Do not predefine a dictionary of keywords. Let the source data shape the taxonomy.



## TODO: 

Use a fixed operational taxonomy as the reporting layer, and keep the graph clusters as the evidence layer underneath. That matches your current build shape cleanly because the graph already emits stable `cluster_id` values plus human labels, and the browser already groups on `primary_bucket` / `buckets`.  The UI should default to the operational expression, with a toggle to detailed view. The ingestion/processing may need some work here too.

I’d make the schema look like this.

```json
{
  "taxonomy_version": "2026-03-16-operational-v1",
  "top_level_categories": [
    {
      "id": "access",
      "label": "Access",
      "description": "Getting an appointment or getting through to the practice",
      "subcategories": [
        {
          "id": "appointment_booking",
          "label": "Appointment booking",
          "description": "Unable to book, no slots, booking process failure",
          "examples": ["can't get appointment", "no appointments", "book appointment"]
        },
        {
          "id": "telephone_access",
          "label": "Telephone access",
          "description": "Phones unanswered, long hold times, cut off calls",
          "examples": ["phone not answered", "on hold", "couldn't get through"]
        },
        {
          "id": "appointment_cancellation",
          "label": "Appointment cancellation",
          "description": "Cancelled or rearranged appointments without clear notice",
          "examples": ["appointment cancelled", "no prior notice", "rearrange"]
        },
        {
          "id": "digital_access",
          "label": "Digital access",
          "description": "Problems with PATCHS, website, forms, login, accessibility barriers",
          "examples": ["online form", "PATCHS", "website", "can't register"]
        }
      ]
    },
    {
      "id": "front_desk",
      "label": "Reception and front desk",
      "description": "Reception conduct and front-desk handling",
      "subcategories": [
        {
          "id": "reception_conduct",
          "label": "Reception conduct",
          "description": "Rude, dismissive, disrespectful, poor communication",
          "examples": ["rude receptionist", "condescending", "unprofessional"]
        },
        {
          "id": "reception_process",
          "label": "Reception process",
          "description": "Check-in, signposting, confidentiality, inconsistent advice",
          "examples": ["told different things", "confidentiality", "front desk process"]
        }
      ]
    },
    {
      "id": "clinical_care",
      "label": "Clinical care",
      "description": "Consultation quality and clinician interaction",
      "subcategories": [
        {
          "id": "listening_and_respect",
          "label": "Listening and respect",
          "description": "Not listened to, concerns dismissed, poor bedside manner",
          "examples": ["didn't listen", "fobbed off", "not taken seriously"]
        },
        {
          "id": "clinical_quality",
          "label": "Clinical quality",
          "description": "Perceived poor assessment, advice, treatment, or follow-through",
          "examples": ["wrong advice", "not checked properly", "poor care"]
        },
        {
          "id": "continuity_of_care",
          "label": "Continuity of care",
          "description": "Unable to see usual GP, fragmented ownership of case",
          "examples": ["same GP", "different doctor each time", "usual doctor"]
        }
      ]
    },
    {
      "id": "admin_and_referrals",
      "label": "Admin and referrals",
      "description": "Administrative handling beyond the consultation itself",
      "subcategories": [
        {
          "id": "referrals",
          "label": "Referrals",
          "description": "Referral not sent, delayed, lost, or needing repeated chasing",
          "examples": ["referral not sent", "chasing referral", "sent again"]
        },
        {
          "id": "documents_and_letters",
          "label": "Documents and letters",
          "description": "Forms, fit notes, letters, records and admin paperwork delays",
          "examples": ["letter", "sick note", "form not done"]
        },
        {
          "id": "complaints_and_follow_up",
          "label": "Complaints and follow-up",
          "description": "Complaint not answered, no callback, no resolution",
          "examples": ["made a complaint", "nobody got back", "no response"]
        }
      ]
    },
    {
      "id": "medicines_and_tests",
      "label": "Medicines and tests",
      "description": "Prescriptions, investigations, results, and follow-up",
      "subcategories": [
        {
          "id": "repeat_prescriptions",
          "label": "Repeat prescriptions",
          "description": "Rejected requests, ordering failures, medication delays",
          "examples": ["repeat prescription", "rejected", "medication not issued"]
        },
        {
          "id": "test_results",
          "label": "Test results",
          "description": "No results, delayed results, unclear communication of results",
          "examples": ["blood test results", "haven't got back", "no results"]
        },
        {
          "id": "investigation_follow_up",
          "label": "Investigation follow-up",
          "description": "No action after tests or scans, unclear next step",
          "examples": ["follow up", "next step", "still waiting after test"]
        }
      ]
    },
    {
      "id": "on_site_experience",
      "label": "On-site experience",
      "description": "Experience of being at the practice premises",
      "subcategories": [
        {
          "id": "waiting_room_and_delays",
          "label": "Waiting room and delays",
          "description": "Long waits after arrival, poor in-practice flow",
          "examples": ["waiting room", "waited 35 minutes", "sat waiting"]
        },
        {
          "id": "environment",
          "label": "Environment",
          "description": "Cleanliness, comfort, premises issues",
          "examples": ["dirty", "building", "waiting area"]
        }
      ]
    },
    {
      "id": "management_and_change",
      "label": "Management and system change",
      "description": "Practice-level systems, rollout changes, and leadership response",
      "subcategories": [
        {
          "id": "system_change",
          "label": "System change",
          "description": "New setup, rollout confusion, process redesign issues",
          "examples": ["new system", "new setup", "management changed"]
        },
        {
          "id": "capacity_and_staffing",
          "label": "Capacity and staffing",
          "description": "Short staffing, rota pressure, lack of practice manager",
          "examples": ["staffing", "capacity", "practice manager"]
        }
      ]
    },
    {
      "id": "positive_feedback",
      "label": "Positive feedback",
      "description": "Explicitly positive reviews or praise",
      "subcategories": [
        {
          "id": "helpful_staff",
          "label": "Helpful staff",
          "description": "Praise for reception, admin, or clinicians",
          "examples": ["helpful", "kind", "friendly"]
        },
        {
          "id": "good_access",
          "label": "Good access",
          "description": "Easy booking, prompt response, improved access",
          "examples": ["easy to get appointment", "improved", "easier online"]
        },
        {
          "id": "good_clinical_care",
          "label": "Good clinical care",
          "description": "Praise for doctors, nurses, treatment, or follow-up",
          "examples": ["great doctor", "excellent care", "felt listened to"]
        }
      ]
    },
    {
      "id": "uncategorised",
      "label": "Other",
      "description": "Low-signal or unmatched reviews",
      "subcategories": []
    }
  ]
}
```

That is the reporting taxonomy. The classifier config should then define how graph clusters map into it.

```json
{
  "taxonomy_version": "2026-03-16-operational-v1",
  "min_text_len": 20,
  "min_df": 2,
  "max_df": 0.9,
  "dbscan_eps": 0.7,
  "dbscan_min_samples": 2,
  "min_cluster_size": 5,
  "merge_similarity_threshold": 0.2,
  "soft_assignment_min_sim": 0.12,
  "fallback_min_sim": 0.08,
  "fallback_min_text": 5,

  "cluster_label_mode": "graph_first_operational_rollup",
  "default_bucket": "uncategorised",

  "operational_categories": {
    "access": {
      "label": "Access",
      "subcategories": {
        "appointment_booking": { "label": "Appointment booking" },
        "telephone_access": { "label": "Telephone access" },
        "appointment_cancellation": { "label": "Appointment cancellation" },
        "digital_access": { "label": "Digital access" }
      }
    },
    "front_desk": {
      "label": "Reception and front desk",
      "subcategories": {
        "reception_conduct": { "label": "Reception conduct" },
        "reception_process": { "label": "Reception process" }
      }
    },
    "clinical_care": {
      "label": "Clinical care",
      "subcategories": {
        "listening_and_respect": { "label": "Listening and respect" },
        "clinical_quality": { "label": "Clinical quality" },
        "continuity_of_care": { "label": "Continuity of care" }
      }
    },
    "admin_and_referrals": {
      "label": "Admin and referrals",
      "subcategories": {
        "referrals": { "label": "Referrals" },
        "documents_and_letters": { "label": "Documents and letters" },
        "complaints_and_follow_up": { "label": "Complaints and follow-up" }
      }
    },
    "medicines_and_tests": {
      "label": "Medicines and tests",
      "subcategories": {
        "repeat_prescriptions": { "label": "Repeat prescriptions" },
        "test_results": { "label": "Test results" },
        "investigation_follow_up": { "label": "Investigation follow-up" }
      }
    },
    "on_site_experience": {
      "label": "On-site experience",
      "subcategories": {
        "waiting_room_and_delays": { "label": "Waiting room and delays" },
        "environment": { "label": "Environment" }
      }
    },
    "management_and_change": {
      "label": "Management and system change",
      "subcategories": {
        "system_change": { "label": "System change" },
        "capacity_and_staffing": { "label": "Capacity and staffing" }
      }
    },
    "positive_feedback": {
      "label": "Positive feedback",
      "subcategories": {
        "helpful_staff": { "label": "Helpful staff" },
        "good_access": { "label": "Good access" },
        "good_clinical_care": { "label": "Good clinical care" }
      }
    },
    "uncategorised": {
      "label": "Other",
      "subcategories": {}
    }
  },

  "cluster_rollup_rules": [
    {
      "when_cluster_label_matches_any": ["appointment", "booking", "phone", "access"],
      "operational_category": "access",
      "subcategory": "appointment_booking",
      "confidence": 0.8
    },
    {
      "when_cluster_label_matches_any": ["phone", "hold", "ring", "get through"],
      "operational_category": "access",
      "subcategory": "telephone_access",
      "confidence": 0.85
    },
    {
      "when_cluster_label_matches_any": ["cancelled", "cancellation"],
      "operational_category": "access",
      "subcategory": "appointment_cancellation",
      "confidence": 0.9
    },
    {
      "when_cluster_label_matches_any": ["online", "website", "patchs", "form", "digital", "bookable"],
      "operational_category": "access",
      "subcategory": "digital_access",
      "confidence": 0.9
    },
    {
      "when_cluster_label_matches_any": ["reception", "rude", "condescending", "unprofessional"],
      "operational_category": "front_desk",
      "subcategory": "reception_conduct",
      "confidence": 0.9
    },
    {
      "when_cluster_label_matches_any": ["confidentiality", "front desk", "check in", "told"],
      "operational_category": "front_desk",
      "subcategory": "reception_process",
      "confidence": 0.7
    },
    {
      "when_cluster_label_matches_any": ["listen", "dismiss", "don't care", "fob"],
      "operational_category": "clinical_care",
      "subcategory": "listening_and_respect",
      "confidence": 0.8
    },
    {
      "when_cluster_label_matches_any": ["doctor", "gp", "nurse", "practitioner", "care"],
      "operational_category": "clinical_care",
      "subcategory": "clinical_quality",
      "confidence": 0.65
    },
    {
      "when_cluster_label_matches_any": ["same gp", "same doctor", "usual gp", "locum", "continuity"],
      "operational_category": "clinical_care",
      "subcategory": "continuity_of_care",
      "confidence": 0.95
    },
    {
      "when_cluster_label_matches_any": ["referral", "sent again", "chasing", "months"],
      "operational_category": "admin_and_referrals",
      "subcategory": "referrals",
      "confidence": 0.95
    },
    {
      "when_cluster_label_matches_any": ["letter", "form", "fit note", "record", "document"],
      "operational_category": "admin_and_referrals",
      "subcategory": "documents_and_letters",
      "confidence": 0.75
    },
    {
      "when_cluster_label_matches_any": ["complaint", "no response", "nobody got back", "follow up"],
      "operational_category": "admin_and_referrals",
      "subcategory": "complaints_and_follow_up",
      "confidence": 0.8
    },
    {
      "when_cluster_label_matches_any": ["prescription", "repeat", "medication", "reject"],
      "operational_category": "medicines_and_tests",
      "subcategory": "repeat_prescriptions",
      "confidence": 0.95
    },
    {
      "when_cluster_label_matches_any": ["results", "blood test", "scan"],
      "operational_category": "medicines_and_tests",
      "subcategory": "test_results",
      "confidence": 0.9
    },
    {
      "when_cluster_label_matches_any": ["follow up", "got back", "next step"],
      "operational_category": "medicines_and_tests",
      "subcategory": "investigation_follow_up",
      "confidence": 0.75
    },
    {
      "when_cluster_label_matches_any": ["waiting room", "waited", "sat waiting"],
      "operational_category": "on_site_experience",
      "subcategory": "waiting_room_and_delays",
      "confidence": 0.95
    },
    {
      "when_cluster_label_matches_any": ["new system", "new setup", "management", "change"],
      "operational_category": "management_and_change",
      "subcategory": "system_change",
      "confidence": 0.8
    },
    {
      "when_cluster_label_matches_any": ["staffed", "staffing", "practice manager", "capacity"],
      "operational_category": "management_and_change",
      "subcategory": "capacity_and_staffing",
      "confidence": 0.75
    },
    {
      "when_cluster_label_matches_any": ["helpful", "thank", "great", "excellent", "recommend", "improved"],
      "operational_category": "positive_feedback",
      "subcategory": "helpful_staff",
      "confidence": 0.7
    }
  ]
}
```

And the per-review output should be expanded slightly from your current shape.

```json
{
  "meta": {
    "generated_date": "2026-03-16",
    "model": "graph",
    "taxonomy_version": "2026-03-16-operational-v1",
    "cluster_count": 12
  },
  "cluster_labels": {
    "c0": "appointments, booking, phone, access",
    "c1": "reception, rude, staff, unprofessional",
    "c2": "referral, admin, sent, waiting",
    "uncategorised": "Other"
  },
  "classifications": {
    "Y02960:0": {
      "cluster_id": "c0",
      "primary_bucket": "c0",
      "buckets": ["c0"],
      "operational_category": "access",
      "subcategory": "appointment_booking",
      "operational_confidence": 0.84,
      "sentiment": "neutral"
    }
  }
}
```

That lets you keep the graph-native bucket IDs for evidence and filtering, but add the staff-facing rollup for analysis. Your current pipeline already separates `cluster_labels` from `primary_bucket`, so this fits without fighting the architecture. 

For the reporting UI, I’d use three levels only.

```json
{
  "reporting_ui": {
    "group_by_default": "operational_category",
    "show_subcategory": true,
    "show_cluster_evidence": true,

    "panels": [
      {
        "id": "summary_by_operational_category",
        "label": "Responsibilities / departments",
        "metrics": [
          "review_count",
          "share_of_reviews",
          "avg_rating",
          "negative_share",
          "post_takeover_delta"
        ]
      },
      {
        "id": "subcategory_breakdown",
        "label": "Issue types within each responsibility",
        "metrics": [
          "review_count",
          "avg_rating",
          "practice_spread"
        ]
      },
      {
        "id": "cluster_evidence",
        "label": "Underlying patient-language clusters",
        "metrics": [
          "cluster_label",
          "review_count",
          "avg_rating",
          "sample_reviews"
        ]
      }
    ],

    "filters": [
      "practice",
      "gtd_managed",
      "pre_post_takeover",
      "year",
      "rating",
      "operational_category",
      "subcategory"
    ],

    "badges": {
      "pre_takeover": "Pre-GTD",
      "post_takeover": "Post-GTD",
      "high_negative_share": "High concern",
      "improving": "Improving"
    }
  }
}
```

How I’d map the current themes into that structure:

* `appointments`, `phone`, `online`, `patchs`, `booking`, `cancelled` → `access`
* `reception`, `receptionist`, `rude`, `condescending`, `confidentiality` → `front_desk`
* `doctor`, `gp`, `don't listen`, `same gp`, `locum` → `clinical_care`
* `referral`, `admin`, `complaint`, `call back`, `letter` → `admin_and_referrals`
* `prescription`, `results`, `blood test`, `follow up` → `medicines_and_tests`
* `waiting room`, `waited` → `on_site_experience`
* `new system`, `management`, `practice manager`, `staffed` → `management_and_change`
* `good`, `helpful`, `excellent`, `improved`, `recommend` → `positive_feedback`

That is already visible in the current heuristic buckets and in the inspection report examples from New Bank: appointment access, online system friction, rude reception, repeat prescription rejection, referral chasing, missing results follow-up, and continuity/clinician-listening issues are all recurring operationally distinct patterns.   

The two implementation rules I’d keep tight:

1. `primary_bucket` stays as `cluster_id`
2. reporting uses `operational_category` + `subcategory`

That avoids throwing away the graph output just to get a cleaner management view.


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
