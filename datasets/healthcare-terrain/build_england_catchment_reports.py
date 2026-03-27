#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CATCHMENT_DIR = BASE_DIR / "catchments" / ".cache" / "gp-catchments-england" / "by_practice"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent
DEFAULT_PUBLISHED_ROOT_GLOB = "gtd-greater-manchester-gp-practice-reviews-*"
EARTH_RADIUS_M = 6_378_137.0
ODS_CODE_RE = re.compile(r"^[A-Z][0-9A-Z]{5}$")
PRIMARY_GOOD_SURVEY_THRESHOLD = 75.0
PRIMARY_GOOGLE_THRESHOLD = 4.0
PRIMARY_GOOGLE_MIN_REVIEWS = 10
SURVEY_EQUIVALENT_GOOGLE_THRESHOLD = PRIMARY_GOOD_SURVEY_THRESHOLD / 20.0
NEW_BANK_CODE = "Y02960"
AREA_BUCKET_EDGES_SQ_KM = [1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0, 500.0, 1000.0]
AREA_BUCKET_MEMBERS_TSV_NAME = "england-catchment-area-bucket-members.tsv"


@dataclass(frozen=True)
class AreaBucket:
    label: str
    minimum_exclusive: float | None
    maximum_inclusive: float | None

    def contains(self, area_sq_km: float) -> bool:
        lower_ok = self.minimum_exclusive is None or area_sq_km > self.minimum_exclusive
        upper_ok = self.maximum_inclusive is None or area_sq_km <= self.maximum_inclusive
        return lower_ok and upper_ok


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build England-only healthcare-terrain markdown reports from catchment polygons and published map datasets."
    )
    parser.add_argument("--catchment-dir", type=Path, default=DEFAULT_CATCHMENT_DIR)
    parser.add_argument("--published-dir", type=Path, default=None, help="Published dataset directory. Defaults to the latest matching output folder.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def resolve_published_dir(explicit_path: Path | None) -> Path:
    if explicit_path is not None:
        if not explicit_path.exists():
            raise FileNotFoundError(f"published dir not found: {explicit_path}")
        return explicit_path
    output_root = BASE_DIR / "output"
    matches = sorted(output_root.glob(DEFAULT_PUBLISHED_ROOT_GLOB))
    if not matches:
        raise FileNotFoundError("no published dataset directories found under datasets/output")
    return matches[-1]


def load_embed_rows(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    prefix = "window.__MAP_EMBED__ = "
    if not text.startswith(prefix):
        raise ValueError(f"unexpected map embed prefix in {path}")
    payload = text[len(prefix):].strip()
    if payload.endswith(";"):
        payload = payload[:-1]
    parsed = json.loads(payload)
    rows = parsed.get("rows")
    if not isinstance(rows, list):
        raise ValueError(f"rows missing from {path}")
    return rows


def load_national_supplementals(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    prefix = "window.NATIONAL_PRACTICE_SUPPLEMENTALS="
    if not text.startswith(prefix):
        raise ValueError(f"unexpected supplementals prefix in {path}")
    payload = text[len(prefix):].split(";\nwindow.NATIONAL_PRACTICE_SUPPLEMENTALS_COUNT=", 1)[0]
    parsed = json.loads(payload)
    if not isinstance(parsed, list):
        raise ValueError(f"supplementals missing from {path}")
    return parsed


def normalize_code(value: Any) -> str:
    return str(value or "").strip().upper()


def numeric_or_none(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def ring_area_sq_m(points: list[tuple[float, float]]) -> float:
    if len(points) < 4:
        return 0.0
    radians_points = [(math.radians(lon), math.radians(lat)) for lon, lat in points]
    if radians_points[0] != radians_points[-1]:
        radians_points.append(radians_points[0])
    total = 0.0
    for index in range(len(radians_points) - 1):
        lon1, lat1 = radians_points[index]
        lon2, lat2 = radians_points[index + 1]
        total += (lon2 - lon1) * (2.0 + math.sin(lat1) + math.sin(lat2))
    return abs(total) * (EARTH_RADIUS_M ** 2) / 2.0


def polygon_area_sq_m(polygon: list[Any]) -> float:
    area_sq_m = 0.0
    for ring_index, ring in enumerate(polygon):
        ring_points: list[tuple[float, float]] = []
        for point in ring:
            if not isinstance(point, (list, tuple)) or len(point) < 2:
                continue
            try:
                ring_points.append((float(point[0]), float(point[1])))
            except (TypeError, ValueError):
                continue
        ring_area = ring_area_sq_m(ring_points)
        area_sq_m += ring_area if ring_index == 0 else -ring_area
    return max(area_sq_m, 0.0)


def feature_area_sq_m(feature: dict[str, Any]) -> float:
    geometry = feature.get("geometry") or {}
    geometry_type = geometry.get("type")
    coordinates = geometry.get("coordinates") or []
    if geometry_type == "Polygon":
        return polygon_area_sq_m(coordinates)
    if geometry_type == "MultiPolygon":
        return sum(polygon_area_sq_m(polygon) for polygon in coordinates)
    return 0.0


def load_catchment_areas(catchment_dir: Path) -> dict[str, float]:
    if not catchment_dir.exists():
        raise FileNotFoundError(f"catchment dir not found: {catchment_dir}")
    areas_sq_km: dict[str, float] = {}
    for path in sorted(catchment_dir.glob("*.geojson")):
        code = normalize_code(path.stem)
        if not ODS_CODE_RE.match(code):
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        features = payload.get("features", [])
        total_sq_m = sum(feature_area_sq_m(feature) for feature in features if isinstance(feature, dict))
        total_sq_km = total_sq_m / 1_000_000.0
        if total_sq_km > 0.0:
            areas_sq_km[code] = total_sq_km
    return areas_sq_km


def dedupe_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        code = normalize_code(row.get("code"))
        if code and code not in deduped:
            deduped[code] = row
    return list(deduped.values())


def england_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if str(row.get("nation") or "").strip().lower() == "england"]


def patient_count(row: dict[str, Any]) -> float | None:
    count = numeric_or_none(row.get("registered_patient_count_effective"))
    if count is None:
        count = numeric_or_none(row.get("registered_patient_count"))
    return count if count and count > 0 else None


def google_score(row: dict[str, Any]) -> float | None:
    return numeric_or_none(row.get("google_score"))


def google_review_count(row: dict[str, Any]) -> float | None:
    return numeric_or_none(row.get("google_count"))


def survey_good_percent(row: dict[str, Any]) -> float | None:
    return numeric_or_none(row.get("survey_overall_good_percent"))


def percent(numerator: float, denominator: float) -> float | None:
    if denominator <= 0:
        return None
    return (100.0 * numerator) / denominator


def practice_share(rows: list[dict[str, Any]], predicate) -> float | None:
    return percent(sum(1 for row in rows if predicate(row)), len(rows))


def weighted_share(rows: list[dict[str, Any]], predicate) -> float | None:
    numerator = 0.0
    denominator = 0.0
    for row in rows:
        weight = patient_count(row)
        if weight is None:
            continue
        denominator += weight
        if predicate(row):
            numerator += weight
    return percent(numerator, denominator)


def format_pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.1f}%"


def format_sq_km(value: float) -> str:
    if value >= 100:
        return f"{value:,.1f}"
    if value >= 10:
        return f"{value:,.2f}"
    return f"{value:,.3f}"


def format_bucket_edge(value: float) -> str:
    if math.isclose(value, round(value), abs_tol=1e-9):
        return f"{round(value):,}"
    return f"{value:,.1f}"


def build_area_buckets() -> list[AreaBucket]:
    buckets: list[AreaBucket] = []
    previous_edge: float | None = None
    for edge in AREA_BUCKET_EDGES_SQ_KM:
        if previous_edge is None:
            label = f"<= {format_bucket_edge(edge)} km²"
        else:
            label = f"> {format_bucket_edge(previous_edge)} to <= {format_bucket_edge(edge)} km²"
        buckets.append(AreaBucket(label=label, minimum_exclusive=previous_edge, maximum_inclusive=edge))
        previous_edge = edge
    buckets.append(
        AreaBucket(
            label=f"> {format_bucket_edge(AREA_BUCKET_EDGES_SQ_KM[-1])} km²",
            minimum_exclusive=AREA_BUCKET_EDGES_SQ_KM[-1],
            maximum_inclusive=None,
        )
    )
    return buckets


def bucket_members(areas_sq_km: dict[str, float], buckets: list[AreaBucket]) -> list[tuple[AreaBucket, list[tuple[str, float]]]]:
    output: list[tuple[AreaBucket, list[tuple[str, float]]]] = []
    for bucket in buckets:
        members = sorted(
            [(code, area) for code, area in areas_sq_km.items() if bucket.contains(area)],
            key=lambda item: (item[1], item[0]),
        )
        output.append((bucket, members))
    return output


def ascending_rank(scope_codes: list[str], areas_sq_km: dict[str, float], code: str) -> tuple[int | None, int]:
    ranked = sorted(((scope_code, areas_sq_km[scope_code]) for scope_code in scope_codes if scope_code in areas_sq_km), key=lambda item: (item[1], item[0]))
    rank = next((index for index, (scope_code, _area) in enumerate(ranked, start=1) if scope_code == code), None)
    return rank, len(ranked)


def percentile_from_rank(rank: int | None, total: int) -> float | None:
    if rank is None or total <= 0:
        return None
    return (100.0 * rank) / total


def larger_share_from_rank(rank: int | None, total: int) -> float | None:
    if rank is None or total <= 0:
        return None
    return (100.0 * (total - rank)) / total


def write_bucket_members_tsv(bucketed_members: list[tuple[AreaBucket, list[tuple[str, float]]]], output_path: Path) -> None:
    max_members = max((len(members) for _bucket, members in bucketed_members), default=0)
    header = ["bucket_index", "bucket_label", "member_count"] + [f"code_{index}" for index in range(1, max_members + 1)]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(header)
        for index, (bucket, members) in enumerate(bucketed_members, start=1):
            writer.writerow([index, bucket.label, len(members), *[code for code, _area in members]])


def find_bucket_for_area(area_sq_km: float, buckets: list[AreaBucket]) -> AreaBucket:
    for bucket in buckets:
        if bucket.contains(area_sq_km):
            return bucket
    return buckets[-1]


def build_good_practice_report(england_all_rows: list[dict[str, Any]], output_path: Path) -> None:
    survey_scored_rows = [row for row in england_all_rows if survey_good_percent(row) is not None]
    google_scored_rows = [row for row in england_all_rows if google_score(row) is not None]
    survey_good_predicate = lambda row: (survey_good_percent(row) or -math.inf) >= PRIMARY_GOOD_SURVEY_THRESHOLD
    google_good_predicate = lambda row: (google_score(row) or -math.inf) >= PRIMARY_GOOGLE_THRESHOLD
    google_survey_equivalent_predicate = lambda row: (google_score(row) or -math.inf) >= SURVEY_EQUIVALENT_GOOGLE_THRESHOLD
    google_good_reviewed_predicate = lambda row: (
        (google_score(row) or -math.inf) >= PRIMARY_GOOGLE_THRESHOLD and (google_review_count(row) or 0) >= PRIMARY_GOOGLE_MIN_REVIEWS
    )

    practice_weighted_primary = practice_share(england_all_rows, survey_good_predicate)
    patient_weighted_primary = weighted_share(england_all_rows, survey_good_predicate)
    practice_weighted_google = practice_share(england_all_rows, google_good_predicate)
    practice_weighted_google_survey_equivalent = practice_share(england_all_rows, google_survey_equivalent_predicate)
    practice_weighted_google_reviewed = practice_share(england_all_rows, google_good_reviewed_predicate)

    lines = [
        "# England Random Good Practice Chance",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "This report is **England only**.",
        "",
        "Reason: the healthcare-terrain hard catchment source currently exists only for the England GP catchment cache, so this report narrows the earlier broad UK-style question to the England practice pool.",
        "",
        "## Headline",
        "",
        f"If you model the question as **picking an England GP practice at random with no prior research**, the best simple answer in this dataset is **{format_pct(practice_weighted_primary)}** if \"good\" means **GP Patient Survey overall-good >= {PRIMARY_GOOD_SURVEY_THRESHOLD:.0f}%**.",
        "",
        f"The patient-weighted version of the same question is **{format_pct(patient_weighted_primary)}**.",
        "",
        "## Metric Notes",
        "",
        f"- Primary metric used for the headline: `survey_overall_good_percent >= {PRIMARY_GOOD_SURVEY_THRESHOLD:.0f}`",
        f"- England practices in combined published dataset: `{len(england_all_rows):,}`",
        f"- Survey coverage in England rows: `{len(survey_scored_rows):,}` / `{len(england_all_rows):,}` = `{format_pct(percent(len(survey_scored_rows), len(england_all_rows)))}`",
        f"- Google score coverage in England rows: `{len(google_scored_rows):,}` / `{len(england_all_rows):,}` = `{format_pct(percent(len(google_scored_rows), len(england_all_rows)))}`",
        "",
        "## Alternative Reads",
        "",
        f"- Survey-defined good, random practice: `{format_pct(practice_weighted_primary)}`",
        f"- Survey-defined good, patient-weighted: `{format_pct(patient_weighted_primary)}`",
        f"- Google `>= {SURVEY_EQUIVALENT_GOOGLE_THRESHOLD:.2f}` (the direct `75% -> 3.75 stars` mapping used in the survey/Google gap view), random practice: `{format_pct(practice_weighted_google_survey_equivalent)}`",
        f"- Google `>= {PRIMARY_GOOGLE_THRESHOLD:.1f}` only, random practice: `{format_pct(practice_weighted_google)}`",
        f"- Google `>= {PRIMARY_GOOGLE_THRESHOLD:.1f}` with at least `{PRIMARY_GOOGLE_MIN_REVIEWS}` reviews, random practice: `{format_pct(practice_weighted_google_reviewed)}`",
        f"- Survey-defined good among England practices with survey data present: `{format_pct(practice_share(survey_scored_rows, survey_good_predicate))}`",
        "",
        "## Plain-English Read",
        "",
        (
            f"Using the survey-based definition, England looks roughly like a **6-in-10** random-practice chance of landing on a good practice, "
            f"or about **55%** if you weight by patient counts instead of by practice count."
        ),
        "",
        (
            f"The stark contrast is Google: even if you soften the Google cutoff to the direct survey-equivalent threshold of "
            f"`{SURVEY_EQUIVALENT_GOOGLE_THRESHOLD:.2f}` stars, the random-practice chance is only **{format_pct(practice_weighted_google_survey_equivalent)}**. "
            f"At the stricter `4.0`-star cutoff it drops to **{format_pct(practice_weighted_google)}**."
        ),
        "",
        (
            "So the important directional point is not subtle: in England it looks fairly common to be structurally near "
            "(in the catchment-system sense) a practice with good patient-survey results, but much rarer to be near one "
            "that looks good on Google ratings."
        ),
        "",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_catchment_bucket_report(
    areas_sq_km: dict[str, float],
    published_england_rows: list[dict[str, Any]],
    output_path: Path,
    members_tsv_path: Path,
) -> None:
    buckets = build_area_buckets()
    bucketed_members = bucket_members(areas_sq_km, buckets)
    write_bucket_members_tsv(bucketed_members, members_tsv_path)
    all_area_values = sorted(areas_sq_km.values())
    new_bank_area = areas_sq_km[NEW_BANK_CODE]
    new_bank_bucket = find_bucket_for_area(new_bank_area, buckets)
    all_england_codes = sorted(areas_sq_km)
    published_england_codes = sorted(
        {
            normalize_code(row.get("code"))
            for row in published_england_rows
            if normalize_code(row.get("code")) in areas_sq_km
        }
    )
    gtd_england_rows = sorted(
        (
            row
            for row in published_england_rows
            if row.get("gtd") and normalize_code(row.get("code")) in areas_sq_km
        ),
        key=lambda row: (areas_sq_km[normalize_code(row.get("code"))], normalize_code(row.get("code"))),
    )
    gtd_england_codes = [normalize_code(row.get("code")) for row in gtd_england_rows]
    global_rank, global_total = ascending_rank(all_england_codes, areas_sq_km, NEW_BANK_CODE)
    global_percentile = percentile_from_rank(global_rank, global_total)
    global_larger_share = larger_share_from_rank(global_rank, global_total)
    local_rank, local_total = ascending_rank(published_england_codes, areas_sq_km, NEW_BANK_CODE)
    local_percentile = percentile_from_rank(local_rank, local_total)
    gtd_rank, gtd_total = ascending_rank(gtd_england_codes, areas_sq_km, NEW_BANK_CODE)
    gtd_percentile = percentile_from_rank(gtd_rank, gtd_total)

    lines = [
        "# England Catchment Area Buckets",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "This report is **England only** and uses the hard polygon catchment cache under `datasets/catchments/.cache/gp-catchments-england/by_practice/`.",
        "",
        "## Area Method",
        "",
        "- Each practice area is the sum of all polygon / multipolygon feature parts in its England catchment cache file.",
        "- Area is calculated directly from lon/lat rings using a spherical polygon-area approximation with the Web Mercator Earth radius used elsewhere in the healthcare-terrain tooling.",
        "- Invalid or non-ODS cache filenames are excluded from the ranked pool.",
        "",
        "## Distribution Summary",
        "",
        f"- Valid England catchments ranked: `{len(areas_sq_km):,}`",
        f"- Minimum area: `{format_sq_km(min(all_area_values))}` km²",
        f"- Median area: `{format_sq_km(median(all_area_values))}` km²",
        f"- 90th percentile area: `{format_sq_km(all_area_values[round((len(all_area_values) - 1) * 0.9)])}` km²",
        f"- Maximum area: `{format_sq_km(max(all_area_values))}` km²",
        "",
        "## Bucket Design",
        "",
        (
            "Buckets use human-readable round-number area bands instead of equal-count splits. The aim is to show the real shape of the "
            "England catchment spread in ranges that are easy to think about, even if that means the counts are front-weighted and the long tail stays visible."
        ),
        "",
        f"Full member codes are exported separately to `{members_tsv_path.name}` as TSV cells, one row per bucket.",
        "",
        "| Bucket | Members | Share | Range |",
        "| --- | ---: | ---: | --- |",
    ]

    for index, (bucket, members) in enumerate(bucketed_members, start=1):
        lines.append(f"| {index} | {len(members):,} | {format_pct(percent(len(members), len(areas_sq_km)))} | {bucket.label} |")

    lines.extend(
        [
            "",
            "## New Bank Health",
            "",
            f"- Practice code: `{NEW_BANK_CODE}`",
            f"- Catchment area: `{format_sq_km(new_bank_area)}` km²",
            f"- Bucket: `{new_bank_bucket.label}`",
            f"- Global England rank by smallest catchment area: `{global_rank}` / `{global_total}`",
            f"- Global England area percentile, smaller-first: `{global_percentile:.1f}`" if global_percentile is not None else "- Global England area percentile, smaller-first: `n/a`",
            f"- Put plainly: `{global_larger_share:.1f}%` of England practices have larger catchments than New Bank" if global_larger_share is not None else "- Put plainly: `n/a`",
            f"- Published Manchester extended England rank by smallest catchment area: `{local_rank}` / `{local_total}`",
            f"- Published Manchester extended England percentile, smaller-first: `{local_percentile:.1f}`" if local_percentile is not None else "- Published Manchester extended England percentile, smaller-first: `n/a`",
            f"- GTD England rank by smallest catchment area: `{gtd_rank}` / `{gtd_total}`",
            f"- GTD England percentile, smaller-first: `{gtd_percentile:.1f}`" if gtd_percentile is not None else "- GTD England percentile, smaller-first: `n/a`",
            "",
            "Scope note:",
            "All catchment areas in this report come from the one England catchment cache. The only scope changes here are whether New Bank is compared with all England catchments, the published Manchester-extended England pool, or just the GTD England subset.",
            "",
            "## GTD England Practices",
            "",
            "| Practice | Code | Area | Bucket | England rank | England percentile |",
            "| --- | --- | ---: | --- | ---: | ---: |",
        ]
    )

    for row in gtd_england_rows:
        code = normalize_code(row.get("code"))
        practice_area_sq_km = areas_sq_km[code]
        bucket = find_bucket_for_area(practice_area_sq_km, buckets)
        rank, total = ascending_rank(all_england_codes, areas_sq_km, code)
        percentile = percentile_from_rank(rank, total)
        lines.append(
            f"| {row.get('name') or code} | `{code}` | `{format_sq_km(practice_area_sq_km)}` km² | {bucket.label} | `{rank}` / `{total}` | `{percentile:.1f}` |"
        )

    lines.extend(
        [
            "",
            "## Bucket Summaries",
            "",
        ]
    )

    for index, (bucket, members) in enumerate(bucketed_members, start=1):
        lines.extend(
            [
                f"### Bucket {index}: {bucket.label}",
                "",
                f"- Members: `{len(members):,}`",
                f"- Share of England catchments: `{format_pct(percent(len(members), len(areas_sq_km)))}`",
                f"- Smallest member area: `{format_sq_km(members[0][1])}` km²" if members else "- Smallest member area: `n/a`",
                f"- Largest member area: `{format_sq_km(members[-1][1])}` km²" if members else "- Largest member area: `n/a`",
                "",
            ]
        )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    published_dir = resolve_published_dir(args.published_dir)
    embed_rows = load_embed_rows(published_dir / "map-embed-data.js")
    supplemental_rows = load_national_supplementals(published_dir / "national-practice-supplementals.js")
    all_rows = dedupe_rows(embed_rows + supplemental_rows)
    england_all_rows = england_rows(all_rows)
    areas_sq_km = load_catchment_areas(args.catchment_dir)
    published_england_rows = dedupe_rows(england_rows(embed_rows))

    if NEW_BANK_CODE not in areas_sq_km:
        raise KeyError(f"{NEW_BANK_CODE} not found in England catchment area cache")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    build_good_practice_report(
        england_all_rows=england_all_rows,
        output_path=args.output_dir / "england-random-good-practice-report.md",
    )
    build_catchment_bucket_report(
        areas_sq_km=areas_sq_km,
        published_england_rows=published_england_rows,
        output_path=args.output_dir / "england-catchment-area-buckets-report.md",
        members_tsv_path=args.output_dir / AREA_BUCKET_MEMBERS_TSV_NAME,
    )


if __name__ == "__main__":
    main()
