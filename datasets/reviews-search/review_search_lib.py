from __future__ import annotations

import json
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATASET_OUTPUT_DIR = REPO_ROOT / "datasets" / "output"
REPORT_GLOB = "gtd-greater-manchester-gp-practice-reviews-*"
DEFAULT_DB_PATH = Path(__file__).resolve().parent / "output" / "reviews_index.sqlite"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "output"

REVIEW_SECTION_MARKERS = ("Captured reviews", "Recent visible reviews")
QUERY_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "been",
    "but",
    "by",
    "for",
    "from",
    "had",
    "has",
    "have",
    "how",
    "i",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "me",
    "my",
    "not",
    "of",
    "on",
    "or",
    "our",
    "so",
    "that",
    "the",
    "their",
    "them",
    "they",
    "this",
    "to",
    "was",
    "we",
    "were",
    "what",
    "when",
    "where",
    "who",
    "why",
    "with",
    "you",
    "your",
}


def normalize_ws(text: str) -> str:
    return " ".join((text or "").split())


def find_latest_report_dir() -> Path:
    candidates = sorted(
        [path for path in DATASET_OUTPUT_DIR.glob(REPORT_GLOB) if path.is_dir()],
        key=lambda path: path.name,
    )
    if not candidates:
        raise FileNotFoundError(f"No report dirs under {DATASET_OUTPUT_DIR}")
    return candidates[-1]


def parse_txt_header(lines: list[str]) -> dict[str, str]:
    header: dict[str, str] = {}
    for line in lines:
        stripped = line.strip()
        if stripped in REVIEW_SECTION_MARKERS or (stripped and set(stripped) <= {"="}):
            break
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        header[key.strip().lower().replace(" ", "_")] = value.strip()
    return header


def _find_reviews_start(lines: list[str]) -> int:
    for index, line in enumerate(lines):
        if line.strip() not in REVIEW_SECTION_MARKERS:
            continue
        start_idx = index + 1
        if start_idx < len(lines) and set(lines[start_idx].strip()) <= {"="}:
            start_idx += 1
        return start_idx
    return 0


def _tokenize(text: str) -> list[str]:
    value = (text or "").lower()
    value = re.sub(r"[’']", "", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return [token for token in value.split() if token]


def index_text(text: str) -> str:
    return " ".join(token for token in _tokenize(text) if len(token) > 1)


def query_terms(text: str) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for token in _tokenize(text):
        if len(token) <= 1 or token in QUERY_STOPWORDS or token in seen:
            continue
        seen.add(token)
        out.append(token)
    if out:
        return out
    seen.clear()
    out = []
    for token in _tokenize(text):
        if len(token) <= 1 or token in seen:
            continue
        seen.add(token)
        out.append(token)
    return out


def parse_int(value: str) -> int | None:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def parse_float(value: str) -> float | None:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def extract_canonical_code_from_filename(name: str) -> str:
    return name.split("-", 1)[0].replace(".txt", "").strip()


def strip_metadata_from_review_text(text: str, author: str, date_raw: str) -> str:
    del date_raw
    if not text or not isinstance(text, str):
        return ""
    value = text.strip()
    if not value:
        return ""

    prefix_parts: list[str] = []
    if author:
        prefix_parts.append(re.escape(author))
    prefix_parts.append(
        r"(?:Local\s+Guide\s*(?:\·\s*)?)?"
        r"(?:\d+\s*reviews?\s*(?:\·\s*\d+\s*photos?\s*a?)?\s*)?"
        r"(?:\d+\s*(?:weeks?|months?|years?|days?)\s+ago|a?\s*(?:week|month|year|day)s?\s+ago)\s*"
    )
    prefix_parts.append(r"(?:New\s*)?")
    prefix_re = re.compile(r"^\s*" + "".join(prefix_parts), re.I)
    value = prefix_re.sub("", value)
    value = re.sub(r"^\s*(?:Local\s+Guide\s*|Edited\s+)+", "", value, flags=re.I)
    value = re.sub(r"\s+", " ", value).strip()
    return value if len(value) > 2 else ""


def normalize_review_text(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def parse_reviews_from_txt(content: str) -> list[dict[str, Any]]:
    lines = content.splitlines()
    start_idx = _find_reviews_start(lines)
    reviews: list[dict[str, Any]] = []
    index = start_idx

    while index < len(lines):
        author_match = re.match(r"^Author:\s*(.*)$", lines[index].strip())
        if not author_match:
            index += 1
            continue

        author = author_match.group(1).strip()
        date_raw = ""
        rating_label = ""
        text_parts: list[str] = []
        cursor = index + 1

        while cursor < len(lines):
            stripped = lines[cursor].strip()
            if re.match(r"^Author:\s", stripped):
                break
            date_match = re.match(r"^Date:\s*(.*)$", stripped)
            rating_match = re.match(r"^Rating:\s*(.*)$", stripped)
            if date_match:
                date_raw = date_match.group(1).strip()
            elif rating_match:
                rating_label = rating_match.group(1).strip()
            else:
                text_parts.append(lines[cursor].rstrip())
            cursor += 1

        stars = 0
        star_match = re.search(r"(\d)\s*star", rating_label, re.I)
        if star_match:
            stars = int(star_match.group(1))

        raw_text = "\n".join(text_parts)
        clean_text = normalize_review_text(strip_metadata_from_review_text(raw_text, author, date_raw))
        reviews.append(
            {
                "author": author,
                "date_raw": date_raw,
                "rating_label": rating_label,
                "rating_stars": stars,
                "text": clean_text,
            }
        )
        index = cursor

    return reviews


def _author_date_key(review: dict[str, Any]) -> tuple[str, str]:
    return (
        str(review.get("author") or "").strip(),
        str(review.get("date_raw") or review.get("relative_date") or "").strip(),
    )


def _text_matches_for_dedup(text_a: str, text_b: str) -> bool:
    a = text_a.strip()
    b = text_b.strip()
    if a == b:
        return True
    if a.startswith(b) or b.startswith(a):
        return True
    if a.endswith("...") and b.startswith(a[:-3].rstrip()):
        return True
    if b.endswith("...") and a.startswith(b[:-3].rstrip()):
        return True
    if a.endswith("…") and b.startswith(a[:-1].rstrip()):
        return True
    if b.endswith("…") and a.startswith(b[:-1].rstrip()):
        return True
    return False


def dedupe_reviews(reviews: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for review in reviews:
        grouped[_author_date_key(review)].append(review)

    out: list[dict[str, Any]] = []
    for group in grouped.values():
        sorted_group = sorted(group, key=lambda item: len(str(item.get("text") or "").strip()), reverse=True)
        kept: list[dict[str, Any]] = []
        for review in sorted_group:
            text = str(review.get("text") or "").strip()
            if any(_text_matches_for_dedup(str(existing.get("text") or "").strip(), text) for existing in kept):
                continue
            kept.append(review)
        out.extend(kept)
    return out


def parse_months_ago(date_raw: str) -> int | None:
    if not date_raw:
        return None
    normalized = re.sub(r"^Edited\s+", "", date_raw, flags=re.I).strip()
    match = re.search(r"\b(\d+)\s*year", normalized, re.I)
    if match:
        return int(match.group(1)) * 12
    match = re.search(r"\b(\d+)\s*month", normalized, re.I)
    if match:
        return int(match.group(1))
    match = re.search(r"\b(\d+)\s*week", normalized, re.I)
    if match:
        return max(0, int(match.group(1)) // 4)
    if re.search(r"\b\d+\s*day", normalized, re.I):
        return 0
    if re.search(r"\ba\s+year", normalized, re.I):
        return 12
    if re.search(r"\ba\s+month", normalized, re.I):
        return 1
    if re.search(r"\ba\s+week", normalized, re.I):
        return 0
    if re.search(r"\ba\s+day", normalized, re.I):
        return 0
    return None


def estimate_review_year(date_raw: str, reference_date: str) -> int | None:
    months_ago = parse_months_ago(date_raw)
    if months_ago is None:
        return None
    ref_year = 2026
    ref_month = 1
    parts = str(reference_date or "").split("-")
    if len(parts) >= 2:
        try:
            ref_year = int(parts[0])
            ref_month = int(parts[1])
        except ValueError:
            pass
    total_months = ref_year * 12 + ref_month - months_ago
    return max(2015, total_months // 12)


def load_practices(report_dir: Path) -> dict[str, dict[str, Any]]:
    practices_path = report_dir / "gtd_greater_manchester_gp_practices.json"
    if not practices_path.exists():
        return {}
    practices = json.loads(practices_path.read_text(encoding="utf-8"))
    return {
        str(practice.get("canonical_code") or "").strip(): practice
        for practice in practices
        if practice.get("canonical_code")
    }


def load_generated_date(report_dir: Path) -> str:
    summary_path = report_dir / "summary.json"
    if not summary_path.exists():
        return ""
    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ""
    return str(summary.get("generated_date") or "").strip()


def build_review_documents(report_dir: Path, *, include_visible_cards: bool = False) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    txt_dir = report_dir / "google-review-texts"
    if not txt_dir.exists():
        raise FileNotFoundError(f"No review text dir at {txt_dir}")

    practices = load_practices(report_dir)
    generated_date = load_generated_date(report_dir)
    review_docs: list[dict[str, Any]] = []
    practice_count = 0
    full_feed_practice_count = 0

    for txt_path in sorted(txt_dir.glob("*.txt")):
        content = txt_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        header = parse_txt_header(lines)
        review_collection_mode = str(header.get("review_collection_mode") or "").strip()
        if review_collection_mode == "full_feed":
            full_feed_practice_count += 1
        elif not include_visible_cards:
            continue

        reviews = dedupe_reviews(parse_reviews_from_txt(content))
        if not reviews:
            continue

        canonical_code = str(header.get("canonical_code") or "").strip() or extract_canonical_code_from_filename(txt_path.name)
        practice_row = practices.get(canonical_code, {})
        practice_name = (
            str(header.get("practice") or "").strip()
            or str(practice_row.get("practice_name") or "").strip()
            or txt_path.stem
        )
        postcode = str(header.get("postcode") or practice_row.get("postcode") or "").strip()
        google_review_score = parse_float(str(practice_row.get("google_review_score") or header.get("google_rating") or ""))
        google_review_count = parse_int(str(practice_row.get("google_review_count") or header.get("google_review_count") or ""))
        gtd_takeover_date = str(practice_row.get("gtd_takeover_date") or "").strip()
        gtd_managed = bool(practice_row.get("gtd_managed", False))
        source_file = str(txt_path.relative_to(report_dir))
        review_order = 0
        reviews_added = 0

        for review in reviews:
            date_raw = str(review.get("date_raw") or "").strip()
            text = str(review.get("text") or "").strip()
            if not text:
                continue
            review_docs.append(
                {
                    "source_file": source_file,
                    "canonical_code": canonical_code,
                    "practice_name": practice_name,
                    "postcode": postcode,
                    "gtd_managed": 1 if gtd_managed else 0,
                    "google_review_score": google_review_score,
                    "google_review_count": google_review_count,
                    "gtd_takeover_date": gtd_takeover_date,
                    "review_collection_mode": review_collection_mode,
                    "review_order": review_order,
                    "author": str(review.get("author") or "").strip(),
                    "date_raw": date_raw,
                    "estimated_months_ago": parse_months_ago(date_raw),
                    "estimated_year": estimate_review_year(date_raw, generated_date),
                    "rating_stars": int(review.get("rating_stars") or 0),
                    "rating_label": str(review.get("rating_label") or "").strip(),
                    "text": text,
                    "text_index": index_text(text),
                }
            )
            review_order += 1
            reviews_added += 1

        if reviews_added > 0:
            practice_count += 1

    metadata = {
        "report_dir": str(report_dir),
        "generated_date": generated_date,
        "practice_count": practice_count,
        "full_feed_practice_count": full_feed_practice_count,
        "review_count": len(review_docs),
        "include_visible_cards": bool(include_visible_cards),
    }
    return review_docs, metadata


def _ensure_schema(con: sqlite3.Connection) -> None:
    con.execute("PRAGMA journal_mode=WAL;")
    con.execute("PRAGMA synchronous=NORMAL;")
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS meta (
          key TEXT PRIMARY KEY,
          value TEXT NOT NULL
        );
        """
    )
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS reviews (
          id INTEGER PRIMARY KEY,
          source_file TEXT NOT NULL,
          canonical_code TEXT NOT NULL,
          practice_name TEXT NOT NULL,
          postcode TEXT NOT NULL,
          gtd_managed INTEGER NOT NULL,
          google_review_score REAL,
          google_review_count INTEGER,
          gtd_takeover_date TEXT NOT NULL,
          review_collection_mode TEXT NOT NULL,
          review_order INTEGER NOT NULL,
          author TEXT NOT NULL,
          date_raw TEXT NOT NULL,
          estimated_months_ago INTEGER,
          estimated_year INTEGER,
          rating_stars INTEGER NOT NULL,
          rating_label TEXT NOT NULL,
          text TEXT NOT NULL,
          text_index TEXT NOT NULL
        );
        """
    )
    con.execute("CREATE INDEX IF NOT EXISTS idx_reviews_code ON reviews(canonical_code);")
    con.execute("CREATE INDEX IF NOT EXISTS idx_reviews_practice ON reviews(practice_name);")
    con.execute("CREATE INDEX IF NOT EXISTS idx_reviews_rating ON reviews(rating_stars);")
    con.execute("CREATE INDEX IF NOT EXISTS idx_reviews_year ON reviews(estimated_year);")
    con.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS reviews_fts
        USING fts5(
          text_index,
          practice_name,
          author,
          canonical_code,
          tokenize = 'unicode61 remove_diacritics 2'
        );
        """
    )


def _meta_set(con: sqlite3.Connection, key: str, value: Any) -> None:
    con.execute(
        "INSERT INTO meta(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, json.dumps(value)),
    )


def _meta_get(con: sqlite3.Connection, key: str, default: Any = None) -> Any:
    row = con.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
    if not row:
        return default
    try:
        return json.loads(row[0])
    except json.JSONDecodeError:
        return default


def rebuild_review_index(
    *,
    db_path: Path = DEFAULT_DB_PATH,
    report_dir: Path | None = None,
    include_visible_cards: bool = False,
) -> dict[str, Any]:
    report_dir = report_dir or find_latest_report_dir()
    review_docs, metadata = build_review_documents(report_dir, include_visible_cards=include_visible_cards)

    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(db_path))
    try:
        _ensure_schema(con)
        with con:
            con.execute("DELETE FROM reviews_fts")
            con.execute("DELETE FROM reviews")
            con.executemany(
                """
                INSERT INTO reviews(
                  source_file, canonical_code, practice_name, postcode, gtd_managed,
                  google_review_score, google_review_count, gtd_takeover_date,
                  review_collection_mode, review_order, author, date_raw,
                  estimated_months_ago, estimated_year, rating_stars, rating_label,
                  text, text_index
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        doc["source_file"],
                        doc["canonical_code"],
                        doc["practice_name"],
                        doc["postcode"],
                        int(doc["gtd_managed"]),
                        doc["google_review_score"],
                        doc["google_review_count"],
                        doc["gtd_takeover_date"],
                        doc["review_collection_mode"],
                        int(doc["review_order"]),
                        doc["author"],
                        doc["date_raw"],
                        doc["estimated_months_ago"],
                        doc["estimated_year"],
                        int(doc["rating_stars"]),
                        doc["rating_label"],
                        doc["text"],
                        doc["text_index"],
                    )
                    for doc in review_docs
                ],
            )
            con.execute(
                """
                INSERT INTO reviews_fts(rowid, text_index, practice_name, author, canonical_code)
                SELECT id, text_index, practice_name, author, canonical_code
                FROM reviews
                ORDER BY id ASC
                """
            )
            _meta_set(con, "report_dir", metadata["report_dir"])
            _meta_set(con, "generated_date", metadata["generated_date"])
            _meta_set(con, "practice_count", metadata["practice_count"])
            _meta_set(con, "full_feed_practice_count", metadata["full_feed_practice_count"])
            _meta_set(con, "review_count", metadata["review_count"])
            _meta_set(con, "include_visible_cards", metadata["include_visible_cards"])
        return {
            **metadata,
            "db_path": str(db_path),
        }
    finally:
        con.close()


def resolve_report_dir(report_dir: str | Path | None) -> Path:
    if not report_dir:
        return find_latest_report_dir()
    return Path(report_dir).resolve()


def _build_fts_query_variants(q: str, *, phrase: bool = False) -> list[str]:
    raw_tokens = _tokenize(q)
    terms = query_terms(q)
    phrases = []
    for match in re.findall(r'"([^"]+)"', q or ""):
        tokens = _tokenize(match)
        if tokens:
            phrases.append(f'"{" ".join(tokens)}"')

    variants: list[str] = []
    if phrase and raw_tokens:
        variants.append(f'"{" ".join(raw_tokens)}"')
    if phrases and terms:
        variants.append(" AND ".join(phrases + terms[: min(4, len(terms))]))
    if phrases:
        variants.extend(phrases)
    if terms:
        top_terms = sorted(terms, key=len, reverse=True)
        variants.append(" AND ".join(top_terms[: min(4, len(top_terms))]))
        if len(top_terms) >= 3:
            variants.append(" AND ".join(top_terms[:3]))
        if len(top_terms) >= 2:
            variants.append(" AND ".join(top_terms[:2]))
        variants.append(" OR ".join(top_terms[: min(8, len(top_terms))]))
    elif raw_tokens:
        variants.append(" OR ".join(raw_tokens[: min(8, len(raw_tokens))]))

    out: list[str] = []
    seen: set[str] = set()
    for variant in variants:
        value = normalize_ws(variant).strip()
        if not value or value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out


def _quoted_phrases(q: str) -> list[str]:
    return [normalize_ws(match) for match in re.findall(r'"([^"]+)"', q or "") if normalize_ws(match)]


def _sentence_candidates(text: str) -> list[str]:
    candidates = re.split(r"(?<=[.!?])\s+|\n+", text or "")
    return [candidate.strip() for candidate in candidates if candidate.strip()]


def pick_verified_quote(text: str, q: str, *, max_chars: int = 220) -> str:
    original = normalize_ws(text or "")
    if not original:
        return ""

    lowered = original.lower()
    for phrase in _quoted_phrases(q):
        idx = lowered.find(phrase.lower())
        if idx >= 0:
            return original[idx : idx + len(phrase)]

    best_sentence = ""
    best_score = -1
    terms = set(query_terms(q))
    for sentence in _sentence_candidates(original):
        sentence_lower = sentence.lower()
        score = sum(1 for term in terms if term in sentence_lower)
        if score > best_score or (score == best_score and len(sentence) > len(best_sentence)):
            best_score = score
            best_sentence = sentence

    if best_sentence:
        return best_sentence[:max_chars].rstrip()
    return original[:max_chars].rstrip()


def snippet_for_query(text: str, q: str, *, max_chars: int = 260) -> str:
    original = normalize_ws(text or "")
    if len(original) <= max_chars:
        return original

    lowered = original.lower()
    positions: list[int] = []
    for phrase in _quoted_phrases(q):
        idx = lowered.find(phrase.lower())
        if idx >= 0:
            positions.append(idx)
    for term in query_terms(q):
        idx = lowered.find(term.lower())
        if idx >= 0:
            positions.append(idx)

    if not positions:
        return original[: max_chars - 1].rstrip() + "..."

    start = max(0, min(positions) - (max_chars // 3))
    end = min(len(original), start + max_chars)
    snippet = original[start:end].strip()
    if start > 0:
        snippet = "..." + snippet
    if end < len(original):
        snippet = snippet.rstrip() + "..."
    return snippet


def _search_sql_filters(
    *,
    practice: str,
    min_rating: int | None,
    max_rating: int | None,
    gtd_only: bool,
    non_gtd_only: bool,
) -> tuple[str, list[Any]]:
    clauses: list[str] = []
    params: list[Any] = []
    if practice:
        clauses.append("(r.canonical_code = ? OR lower(r.practice_name) = lower(?) OR lower(r.practice_name) LIKE lower(?))")
        params.extend([practice, practice, f"%{practice}%"])
    if min_rating is not None:
        clauses.append("r.rating_stars >= ?")
        params.append(int(min_rating))
    if max_rating is not None:
        clauses.append("r.rating_stars <= ?")
        params.append(int(max_rating))
    if gtd_only:
        clauses.append("r.gtd_managed = 1")
    if non_gtd_only:
        clauses.append("r.gtd_managed = 0")
    if not clauses:
        return "", params
    return " AND " + " AND ".join(clauses), params


def search_reviews(
    *,
    db_path: Path = DEFAULT_DB_PATH,
    q: str,
    limit: int = 12,
    candidates: int = 200,
    practice: str = "",
    min_rating: int | None = None,
    max_rating: int | None = None,
    gtd_only: bool = False,
    non_gtd_only: bool = False,
    phrase: bool = False,
) -> dict[str, Any]:
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    try:
        _ensure_schema(con)
        variants = _build_fts_query_variants(q, phrase=phrase)
        if not variants:
            return {"query": q, "fts": "", "fts_variants": [], "results": [], "error": "empty-query"}

        where_sql, filter_params = _search_sql_filters(
            practice=practice,
            min_rating=min_rating,
            max_rating=max_rating,
            gtd_only=gtd_only,
            non_gtd_only=non_gtd_only,
        )

        rows: list[sqlite3.Row] = []
        used_fts = ""
        for variant in variants:
            rows = con.execute(
                f"""
                SELECT r.*, bm25(reviews_fts, 1.0, 0.25, 0.15, 0.05) AS bm25
                FROM reviews_fts
                JOIN reviews r ON r.id = reviews_fts.rowid
                WHERE reviews_fts MATCH ?{where_sql}
                ORDER BY bm25
                LIMIT ?
                """,
                [variant, *filter_params, int(max(1, candidates))],
            ).fetchall()
            if rows:
                used_fts = variant
                break

        results: list[dict[str, Any]] = []
        for row in rows:
            text = str(row["text"] or "")
            bm25 = float(row["bm25"] or 0.0)
            base = max(0.0, -bm25)
            quote = pick_verified_quote(text, q)
            bonus = 0.0
            if quote:
                bonus += 2.0
            for phrase_text in _quoted_phrases(q):
                if phrase_text.lower() in normalize_ws(text).lower():
                    bonus += 4.0
            overlap = 0
            text_lower = normalize_ws(text).lower()
            for term in query_terms(q):
                if term in text_lower:
                    overlap += 1
            bonus += min(3.0, overlap * 0.35)
            score = base + bonus

            results.append(
                {
                    "review_id": int(row["id"]),
                    "score": score,
                    "bm25": bm25,
                    "canonical_code": str(row["canonical_code"]),
                    "practice_name": str(row["practice_name"]),
                    "postcode": str(row["postcode"]),
                    "gtd_managed": bool(row["gtd_managed"]),
                    "review_collection_mode": str(row["review_collection_mode"]),
                    "author": str(row["author"]),
                    "date_raw": str(row["date_raw"]),
                    "estimated_year": row["estimated_year"],
                    "rating_stars": int(row["rating_stars"] or 0),
                    "rating_label": str(row["rating_label"]),
                    "source_file": str(row["source_file"]),
                    "snippet": snippet_for_query(text, q),
                    "quote": quote,
                }
            )

        results.sort(key=lambda item: (float(item["score"]), int(item["rating_stars"])), reverse=True)
        return {
            "query": q,
            "fts": used_fts or variants[0],
            "fts_variants": variants,
            "results": results[: int(max(1, limit))],
        }
    finally:
        con.close()


def load_review_context(
    *,
    db_path: Path = DEFAULT_DB_PATH,
    review_id: int,
    before: int = 1,
    after: int = 1,
) -> dict[str, Any]:
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    try:
        _ensure_schema(con)
        row = con.execute("SELECT * FROM reviews WHERE id = ?", (int(review_id),)).fetchone()
        if not row:
            return {"review_id": int(review_id), "error": "not-found"}

        context_rows = con.execute(
            """
            SELECT *
            FROM reviews
            WHERE canonical_code = ?
              AND review_order BETWEEN ? AND ?
            ORDER BY review_order ASC
            """,
            (
                str(row["canonical_code"]),
                max(0, int(row["review_order"]) - int(max(0, before))),
                int(row["review_order"]) + int(max(0, after)),
            ),
        ).fetchall()

        return {
            "review_id": int(row["id"]),
            "canonical_code": str(row["canonical_code"]),
            "practice_name": str(row["practice_name"]),
            "source_file": str(row["source_file"]),
            "context": [
                {
                    "review_id": int(item["id"]),
                    "review_order": int(item["review_order"]),
                    "author": str(item["author"]),
                    "date_raw": str(item["date_raw"]),
                    "rating_stars": int(item["rating_stars"] or 0),
                    "text": str(item["text"]),
                }
                for item in context_rows
            ],
        }
    finally:
        con.close()


def corpus_stats(
    *,
    db_path: Path = DEFAULT_DB_PATH,
    q: str = "",
    practice: str = "",
    min_rating: int | None = None,
    max_rating: int | None = None,
    gtd_only: bool = False,
    non_gtd_only: bool = False,
    phrase: bool = False,
    max_matches: int = 10000,
) -> dict[str, Any]:
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    try:
        _ensure_schema(con)
        rows: list[sqlite3.Row]
        used_fts = ""
        variants: list[str] = []
        where_sql, filter_params = _search_sql_filters(
            practice=practice,
            min_rating=min_rating,
            max_rating=max_rating,
            gtd_only=gtd_only,
            non_gtd_only=non_gtd_only,
        )

        if q.strip():
            variants = _build_fts_query_variants(q, phrase=phrase)
            if not variants:
                return {"query": q, "fts": "", "error": "empty-query"}
            rows = []
            for variant in variants:
                rows = con.execute(
                    f"""
                    SELECT r.*
                    FROM reviews_fts
                    JOIN reviews r ON r.id = reviews_fts.rowid
                    WHERE reviews_fts MATCH ?{where_sql}
                    ORDER BY r.practice_name ASC, r.review_order ASC
                    LIMIT ?
                    """,
                    [variant, *filter_params, int(max(1, max_matches))],
                ).fetchall()
                if rows:
                    used_fts = variant
                    break
        else:
            rows = con.execute(
                f"""
                SELECT r.*
                FROM reviews r
                WHERE 1 = 1{where_sql}
                ORDER BY r.practice_name ASC, r.review_order ASC
                LIMIT ?
                """,
                [*filter_params, int(max(1, max_matches))],
            ).fetchall()

        rating_counts = Counter(str(int(row["rating_stars"] or 0)) for row in rows)
        year_counts = Counter(str(int(row["estimated_year"])) for row in rows if row["estimated_year"] is not None)
        practice_counts: dict[tuple[str, str], list[int]] = defaultdict(list)
        gtd_count = 0
        non_gtd_count = 0
        for row in rows:
            if int(row["gtd_managed"] or 0):
                gtd_count += 1
            else:
                non_gtd_count += 1
            practice_counts[(str(row["canonical_code"]), str(row["practice_name"]))].append(int(row["rating_stars"] or 0))

        top_practices = []
        for (code, name), ratings in sorted(practice_counts.items(), key=lambda item: len(item[1]), reverse=True)[:10]:
            nonzero_ratings = [rating for rating in ratings if rating > 0]
            avg_rating = (sum(nonzero_ratings) / len(nonzero_ratings)) if nonzero_ratings else 0.0
            top_practices.append(
                {
                    "canonical_code": code,
                    "practice_name": name,
                    "review_count": len(ratings),
                    "avg_rating": round(avg_rating, 2),
                }
            )

        rating_values = [int(row["rating_stars"] or 0) for row in rows if int(row["rating_stars"] or 0) > 0]
        avg_rating = (sum(rating_values) / len(rating_values)) if rating_values else 0.0

        return {
            "query": q,
            "fts": used_fts,
            "fts_variants": variants,
            "review_count": len(rows),
            "practice_count": len(practice_counts),
            "gtd_review_count": gtd_count,
            "non_gtd_review_count": non_gtd_count,
            "avg_rating": round(avg_rating, 2),
            "rating_counts": {key: rating_counts.get(key, 0) for key in sorted(rating_counts)},
            "year_counts": {key: year_counts[key] for key in sorted(year_counts)},
            "top_practices": top_practices,
            "report_dir": _meta_get(con, "report_dir", ""),
        }
    finally:
        con.close()


def grounded_report(
    *,
    db_path: Path = DEFAULT_DB_PATH,
    q: str,
    limit: int = 8,
    candidates: int = 300,
    practice: str = "",
    min_rating: int | None = None,
    max_rating: int | None = None,
    gtd_only: bool = False,
    non_gtd_only: bool = False,
    phrase: bool = False,
) -> dict[str, Any]:
    search_payload = search_reviews(
        db_path=db_path,
        q=q,
        limit=limit,
        candidates=candidates,
        practice=practice,
        min_rating=min_rating,
        max_rating=max_rating,
        gtd_only=gtd_only,
        non_gtd_only=non_gtd_only,
        phrase=phrase,
    )
    stats_payload = corpus_stats(
        db_path=db_path,
        q=q,
        practice=practice,
        min_rating=min_rating,
        max_rating=max_rating,
        gtd_only=gtd_only,
        non_gtd_only=non_gtd_only,
        phrase=phrase,
    )
    return {
        "query": q,
        "search": search_payload,
        "stats": stats_payload,
        "quotes": [
            {
                "review_id": result["review_id"],
                "practice_name": result["practice_name"],
                "canonical_code": result["canonical_code"],
                "rating_stars": result["rating_stars"],
                "date_raw": result["date_raw"],
                "author": result["author"],
                "quote": result["quote"],
            }
            for result in search_payload.get("results", [])[: min(5, limit)]
            if result.get("quote")
        ],
    }
