#!/usr/bin/env python3
"""Build graph-based review classifier.

Uses TF-IDF + cosine similarity to build a similarity graph, clusters reviews
without predefined keywords, derives labels from top terms per cluster.
Outputs review_classifications.json for browser consumption.

Requires: pip install scikit-learn
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_INPUT = Path(__file__).resolve().parent / "output" / ".classifier_input.json"
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "output" / "review_classifications.json"
CLASSIFIER_CONFIG = Path(__file__).resolve().parent / "classifier_config.json"

# Emoji/symbol ranges to strip from messy review text
_EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001F9FF"  # misc symbols, emoticons, etc.
    "\U00002600-\U000027BF"
    "\U0001F600-\U0001F64F"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\u200d\u23cf\u23e9\u231a\ufe0f\u3030"
    "]+",
    re.UNICODE,
)


def flatten_reviews(data: dict[str, Any]) -> list[tuple[str, str, int]]:
    """Yield (review_id, text, rating_stars) for all reviews."""
    out: list[tuple[str, str, int]] = []
    for p in data.get("practices") or []:
        code = str(p.get("canonical_code", ""))
        for r in p.get("reviews") or []:
            idx = r.get("_index", len(out))
            rid = f"{code}:{idx}"
            text = (r.get("text") or "").strip()
            stars = int(r.get("rating_stars") or 0)
            out.append((rid, text, stars))
    for i, r in enumerate(data.get("recent_reviews_across_manchester") or []):
        rid = f"_across:{r.get('_index', i)}"
        text = (r.get("text") or "").strip()
        stars = int(r.get("rating_stars") or 0)
        out.append((rid, text, stars))
    return out


def _clean_messy_text(text: str) -> str:
    """Normalise messy natural-language review text for analysis."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = _EMOJI_PATTERN.sub(" ", text)
    text = re.sub(r"[\u200b-\u200d\ufeff]", "", text)
    text = re.sub(r"[^\w\s'\-.,!?;:]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\.{2,}", " ", text)
    text = re.sub(r"[!?]{2,}", " ", text)
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text[:8000]


def sentiment_from_rating(stars: int) -> str:
    if stars <= 2:
        return "negative"
    if stars >= 4:
        return "positive"
    return "neutral"


def build_classifier(input_path: Path, output_path: Path) -> dict[str, Any]:
    """Build graph classifier and write review_classifications.json."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.cluster import DBSCAN
    import numpy as np

    data = json.loads(input_path.read_text(encoding="utf-8"))
    reviews = flatten_reviews(data)
    if not reviews:
        print("No reviews found", file=sys.stderr)
        raise SystemExit(1)

    ids = [r[0] for r in reviews]
    texts = [_clean_messy_text(r[1]) for r in reviews]
    ratings = [r[2] for r in reviews]

    config: dict[str, Any] = {}
    if CLASSIFIER_CONFIG.exists():
        config = json.loads(CLASSIFIER_CONFIG.read_text(encoding="utf-8"))
    min_text_len = config.get("min_text_len", 50)
    eps = config.get("dbscan_eps", 0.7)
    min_samples = config.get("dbscan_min_samples", 2)

    def _is_metadata_spillage(text: str) -> bool:
        """Exclude reviews that are purely author/metadata (e.g. 'Name3 reviews4 months ago')."""
        if len(text) < 20:
            return True
        words = text.lower().split()
        if len(words) < 4:
            return True
        meta_keywords = ("reviews", "review", "ago", "months", "weeks", "years", "days", "photos", "photo")
        meta = sum(
            1
            for w in words
            if w in meta_keywords
            or "review" in w
            or (len(w) <= 2 and w.isdigit())
            or (w.isdigit() and len(w) <= 3)
        )
        return meta >= len(words) * 0.65

    valid = [
        i
        for i, t in enumerate(texts)
        if len(t) >= min_text_len and not _is_metadata_spillage(t)
    ]
    if len(valid) < 2:
        print("Too few reviews with sufficient text", file=sys.stderr)
        raise SystemExit(1)

    vec = TfidfVectorizer(
        max_features=5000,
        min_df=config.get("min_df", 2),
        max_df=config.get("max_df", 0.88),
        ngram_range=(1, 2),
        strip_accents="unicode",
        stop_words="english",
        token_pattern=r"(?u)\b[a-z][a-z0-9']{1,}\b",
        analyzer="word",
    )
    X_valid = vec.fit_transform([texts[i] for i in valid])
    X = X_valid
    sim = cosine_similarity(X_valid, X_valid)
    dist = 1 - np.clip(sim, 0, 1)
    np.fill_diagonal(dist, 0)
    clusterer = DBSCAN(eps=eps, min_samples=min_samples, metric="precomputed")
    labels = clusterer.fit_predict(dist)
    feature_names = vec.get_feature_names_out()

    id_to_cluster: dict[str, str] = {}
    for vi, lab in enumerate(labels):
        rid = ids[valid[vi]]
        id_to_cluster[rid] = "uncategorised" if lab == -1 else f"c{lab}"
    for i, rid in enumerate(ids):
        if i not in valid:
            id_to_cluster[rid] = "uncategorised"

    soft_threshold = config.get("soft_assignment_min_sim", 0.2)
    noise_indices = [vi for vi, lab in enumerate(labels) if lab == -1]
    if noise_indices and soft_threshold > 0:
        cluster_indices: dict[int, list[int]] = {}
        for vi, lab in enumerate(labels):
            if lab >= 0:
                cluster_indices.setdefault(lab, []).append(vi)
        for vi in noise_indices:
            row_sim = sim[vi]
            best_cid = None
            best_sim = 0.0
            for lab, members in cluster_indices.items():
                max_sim_to_cluster = float(np.max(row_sim[members]))
                if max_sim_to_cluster >= soft_threshold and max_sim_to_cluster > best_sim:
                    best_sim = max_sim_to_cluster
                    best_cid = f"c{lab}"
            if best_cid:
                rid = ids[valid[vi]]
                id_to_cluster[rid] = best_cid

    cluster_terms: dict[str, list[tuple[str, float]]] = {}
    for vi, lab in enumerate(labels):
        if lab == -1:
            continue
        cid = id_to_cluster.get(ids[valid[vi]], f"c{lab}")
        if cid == "uncategorised":
            continue
        row = X[vi].toarray().ravel()
        for j, w in enumerate(row):
            if w > 0 and feature_names[j] and len(feature_names[j]) > 2:
                cluster_terms.setdefault(cid, []).append((feature_names[j], float(w)))

    cluster_labels: dict[str, str] = {"uncategorised": "Other"}
    for cid, terms in cluster_terms.items():
        agg: dict[str, float] = {}
        for t, w in terms:
            agg[t] = agg.get(t, 0) + w
        sorted_terms = sorted(agg.items(), key=lambda x: -x[1])[:5]
        if sorted_terms:
            label = ", ".join(t[0] for t in sorted_terms)
            cluster_labels[cid] = label[:50] + ("..." if len(label) > 50 else "")
        else:
            cluster_labels[cid] = cid

    # Fallback: assign excluded (short/metadata) reviews to nearest cluster by centroid similarity
    fallback_min_sim = config.get("fallback_min_sim", 0.12)
    fallback_min_text = config.get("fallback_min_text", 10)
    excluded = [i for i in range(len(ids)) if i not in valid]
    if excluded and fallback_min_sim > 0:
        cluster_indices: dict[str, list[int]] = {}
        for vi, lab in enumerate(labels):
            if lab >= 0:
                cid = f"c{lab}"
                cluster_indices.setdefault(cid, []).append(vi)
        centroids: dict[str, Any] = {}
        for cid, members in cluster_indices.items():
            rows = X_valid[members].toarray()
            centroids[cid] = rows.mean(axis=0)
        for i in excluded:
            t = texts[i]
            if len(t) < fallback_min_text:
                continue
            if len(t) >= 20 and _is_metadata_spillage(t):
                continue
            try:
                x = vec.transform([t])
            except Exception:
                continue
            arr = x.toarray().ravel()
            if arr.max() == 0:
                continue
            best_cid = None
            best_sim = 0.0
            for cid, cent in centroids.items():
                s = float(cosine_similarity([arr], [cent])[0, 0])
                if s >= fallback_min_sim and s > best_sim:
                    best_sim = s
                    best_cid = cid
            if best_cid:
                id_to_cluster[ids[i]] = best_cid

    # Keyword fallback: map watch_words to clusters; assign uncategorised with matching terms
    watch_words = [w.lower() for w in config.get("watch_words", [])]
    if watch_words:
        word_to_clusters: dict[str, list[str]] = {}
        for cid, terms in cluster_terms.items():
            term_set = {t[0].lower() for t in terms}
            label_lower = cluster_labels.get(cid, "").lower()
            for w in watch_words:
                if w in term_set or w in label_lower or any(w in t for t in term_set):
                    word_to_clusters.setdefault(w, []).append(cid)
        for i, rid in enumerate(ids):
            if id_to_cluster.get(rid) != "uncategorised":
                continue
            t = texts[i]
            if len(t) < fallback_min_text:
                continue
            words = set(t.lower().split())
            for w in watch_words:
                if w not in word_to_clusters:
                    continue
                if w in words or any(w in word for word in words):
                    id_to_cluster[rid] = word_to_clusters[w][0]
                    break

    classifications: dict[str, dict[str, Any]] = {}
    for rid, text, stars in reviews:
        cid = id_to_cluster.get(rid, "uncategorised")
        classifications[rid] = {
            "cluster_id": cid,
            "primary_bucket": cid,
            "buckets": [cid],
            "sentiment": sentiment_from_rating(stars),
        }

    out = {
        "meta": {
            "generated_date": data.get("generated_date", ""),
            "model": "graph",
            "cluster_count": len([v for v in set(id_to_cluster.values()) if v != "uncategorised"]),
        },
        "cluster_labels": cluster_labels,
        "classifications": classifications,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {output_path} ({len(classifications)} reviews, {len(cluster_labels)} labels)")
    return out


def query_classifier(classifications_path: Path) -> None:
    """Interactive exploration of classifier output."""
    data = json.loads(classifications_path.read_text(encoding="utf-8"))
    labels = data.get("cluster_labels", {})
    classifications = data.get("classifications", {})

    by_cluster: dict[str, list[str]] = {}
    for rid, c in classifications.items():
        cid = c.get("cluster_id", "uncategorised")
        by_cluster.setdefault(cid, []).append(rid)

    print("\n=== Cluster summary ===")
    for cid in sorted(by_cluster.keys(), key=lambda x: (x == "uncategorised", x)):
        count = len(by_cluster[cid])
        label = labels.get(cid, cid)
        print(f"  {cid}: {label} ({count} reviews)")

    print("\n=== Sample queries ===")
    print("  Enter cluster id (e.g. c0) to see review IDs")
    print("  Enter 'uncategorised' for leftovers")
    print("  Enter 'q' to quit")

    while True:
        try:
            q = input("\n> ").strip().lower()
        except EOFError:
            break
        if q in ("q", "quit", ""):
            break
        if q in by_cluster:
            rids = by_cluster[q][:10]
            print(f"  {len(by_cluster[q])} reviews. Sample: {rids}")
        else:
            print("  Unknown cluster. Use c0, c1, ... or uncategorised")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build graph-based review classifier")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Classifier input JSON")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output classifications JSON")
    parser.add_argument("--query", action="store_true", help="Run interactive query after build")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Input not found: {args.input}", file=sys.stderr)
        return 1

    build_classifier(args.input, args.output)
    if args.query:
        query_classifier(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
