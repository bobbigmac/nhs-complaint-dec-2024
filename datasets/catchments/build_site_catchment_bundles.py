#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import shutil
import sys
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent.parent
REPORT_DIR = BASE_DIR / "output" / "gtd-greater-manchester-gp-practice-reviews-2026-03-09"
CORE_JSON = REPORT_DIR / "gtd_greater_manchester_gp_practices.json"
OUTPUT_DIR = REPORT_DIR / "catchments"
BUNDLES_DIR = OUTPUT_DIR / "bundles"
INDEX_JSON = OUTPUT_DIR / "index.json"
BUILD_MODULE_PATH = BASE_DIR / "build_gtd_gp_practice_dataset.py"


def load_build_module():
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    spec = importlib.util.spec_from_file_location("build_gtd_gp_practice_dataset", BUILD_MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import build module from {BUILD_MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def bbox_from_geometry(geometry: dict[str, Any]) -> list[float] | None:
    coords = geometry.get("coordinates")
    if coords is None:
        return None
    min_lon = math.inf
    min_lat = math.inf
    max_lon = -math.inf
    max_lat = -math.inf

    def walk(node: Any) -> None:
        nonlocal min_lon, min_lat, max_lon, max_lat
        if isinstance(node, (list, tuple)):
            if len(node) >= 2 and all(isinstance(value, (int, float)) for value in node[:2]):
                lon = float(node[0])
                lat = float(node[1])
                min_lon = min(min_lon, lon)
                min_lat = min(min_lat, lat)
                max_lon = max(max_lon, lon)
                max_lat = max(max_lat, lat)
                return
            for item in node:
                walk(item)

    walk(coords)
    if not math.isfinite(min_lon):
        return None
    return [round(min_lon, 5), round(min_lat, 5), round(max_lon, 5), round(max_lat, 5)]


def union_bbox(boxes: list[list[float] | None]) -> list[float] | None:
    valid = [box for box in boxes if box and len(box) == 4]
    if not valid:
        return None
    return [
        round(min(box[0] for box in valid), 5),
        round(min(box[1] for box in valid), 5),
        round(max(box[2] for box in valid), 5),
        round(max(box[3] for box in valid), 5),
    ]


def expand_bbox(bbox: list[float] | None, padding_degrees: float) -> list[float] | None:
    if not bbox or len(bbox) != 4:
        return None
    return [
        round(float(bbox[0]) - padding_degrees, 5),
        round(float(bbox[1]) - padding_degrees, 5),
        round(float(bbox[2]) + padding_degrees, 5),
        round(float(bbox[3]) + padding_degrees, 5),
    ]


def bboxes_intersect(left: list[float] | None, right: list[float] | None) -> bool:
    if not left or not right or len(left) != 4 or len(right) != 4:
        return False
    return not (
        float(left[2]) < float(right[0])
        or float(right[2]) < float(left[0])
        or float(left[3]) < float(right[1])
        or float(right[3]) < float(left[1])
    )


def bbox_centroid(bbox: list[float] | None) -> tuple[float, float] | None:
    if not bbox or len(bbox) != 4:
        return None
    return ((float(bbox[0]) + float(bbox[2])) / 2.0, (float(bbox[1]) + float(bbox[3])) / 2.0)


def bundle_distance(left: dict[str, Any], right: dict[str, Any]) -> float:
    left_center = bbox_centroid(left.get("bbox"))
    right_center = bbox_centroid(right.get("bbox"))
    if not left_center or not right_center:
        return math.inf
    dx = left_center[0] - right_center[0]
    dy = left_center[1] - right_center[1]
    return math.sqrt(dx * dx + dy * dy)


def load_core_rows() -> list[dict[str, Any]]:
    rows = json.loads(CORE_JSON.read_text(encoding="utf-8"))
    normalized: list[dict[str, Any]] = []
    for row in rows:
        code = str(row.get("canonical_code", "")).strip()
        if not code:
            continue
        normalized.append(
            {
                "code": code,
                "name": str(row.get("practice_name", "")).strip(),
                "lat": row.get("latitude"),
                "lon": row.get("longitude"),
                "nation": str(row.get("nation") or "england").strip().lower() or "england",
            }
        )
    return normalized


def load_england_rows(module: Any) -> list[dict[str, Any]]:
    rows_by_code: dict[str, dict[str, Any]] = {}
    for row in load_core_rows():
        if row["nation"] == "england":
            rows_by_code[row["code"]] = row
    for row in module.build_national_map_supplementals():
        code = str(row.get("code", "")).strip()
        nation = str(row.get("nation", "")).strip().lower()
        if not code or nation != "england":
            continue
        rows_by_code.setdefault(
            code,
            {
                "code": code,
                "name": str(row.get("name", "")).strip(),
                "lat": row.get("lat"),
                "lon": row.get("lon"),
                "nation": nation,
            },
        )
    return list(rows_by_code.values())


def build_groups(module: Any, rows: list[dict[str, Any]], precision: int) -> tuple[list[dict[str, Any]], list[str]]:
    groups_by_resolved_code: dict[str, dict[str, Any]] = {}
    missing_codes: list[str] = []

    for row in rows:
        code = str(row.get("code", "")).strip()
        if not code:
            continue
        direct_path = module.ENGLAND_GP_CATCHMENT_BY_PRACTICE_DIR / f"{code}.geojson"
        base_code = module.catchment_base_code(code)
        base_path = module.ENGLAND_GP_CATCHMENT_BY_PRACTICE_DIR / f"{base_code}.geojson"
        if direct_path.exists():
            resolved_code = code
            source_path = direct_path
        elif base_path.exists():
            resolved_code = base_code
            source_path = base_path
        else:
            missing_codes.append(code)
            continue

        group = groups_by_resolved_code.get(resolved_code)
        if group is None:
            payload = json.loads(source_path.read_text(encoding="utf-8"))
            source_features = module.geojson_features_from_payload(payload)
            compacted_features: list[dict[str, Any]] = []
            bboxes: list[list[float] | None] = []
            for feature in source_features:
                geometry = module.compact_geojson_geometry(feature.get("geometry", {}), digits=precision)
                compacted_features.append(
                    {
                        "type": "Feature",
                        "properties": {},
                        "geometry": geometry,
                    }
                )
                bboxes.append(bbox_from_geometry(geometry))
            group = {
                "resolved_code": resolved_code,
                "source_path": str(source_path),
                "codes": set(),
                "names": set(),
                "features": compacted_features,
                "bbox": union_bbox(bboxes),
                "centroid_points": [],
            }
            groups_by_resolved_code[resolved_code] = group

        group["codes"].add(code)
        group["codes"].add(resolved_code)
        if row.get("name"):
            group["names"].add(str(row["name"]).strip())
        try:
            lat = float(row.get("lat"))
            lon = float(row.get("lon"))
            if math.isfinite(lat) and math.isfinite(lon):
                group["centroid_points"].append((lat, lon))
        except (TypeError, ValueError):
            pass

    groups: list[dict[str, Any]] = []
    for resolved_code, group in sorted(groups_by_resolved_code.items()):
        codes = sorted(code for code in group["codes"] if code)
        names = sorted(name for name in group["names"] if name)
        label = names[0] if names else resolved_code
        bbox = group["bbox"] or [0.0, 0.0, 0.0, 0.0]
        if group["centroid_points"]:
            avg_lat = sum(point[0] for point in group["centroid_points"]) / len(group["centroid_points"])
            avg_lon = sum(point[1] for point in group["centroid_points"]) / len(group["centroid_points"])
        else:
            avg_lat = (bbox[1] + bbox[3]) / 2
            avg_lon = (bbox[0] + bbox[2]) / 2
        features = []
        for feature in group["features"]:
            props = {
                "source_code": resolved_code,
                "codes": codes,
                "label": label,
            }
            features.append(
                {
                    "type": "Feature",
                    "properties": props,
                    "geometry": feature["geometry"],
                }
            )
        feature_collection = {
            "type": "FeatureCollection",
            "features": features,
        }
        serialized = json.dumps(feature_collection, ensure_ascii=False, separators=(",", ":"))
        groups.append(
            {
                "resolved_code": resolved_code,
                "codes": codes,
                "label": label,
                "features": features,
                "bbox": bbox,
                "centroid": [round(avg_lon, 6), round(avg_lat, 6)],
                "serialized_bytes": len(serialized.encode("utf-8")),
                "feature_count": len(features),
            }
        )
    return groups, sorted(set(missing_codes))


def partition_groups(groups: list[dict[str, Any]], target_bytes: int) -> list[list[dict[str, Any]]]:
    def estimated_size(items: list[dict[str, Any]]) -> int:
        return sum(int(item.get("serialized_bytes", 0)) for item in items) + 128

    def recurse(items: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
        if len(items) <= 1 or estimated_size(items) <= target_bytes:
            return [items]
        lon_values = [float(item["centroid"][0]) for item in items]
        lat_values = [float(item["centroid"][1]) for item in items]
        split_on_lon = (max(lon_values) - min(lon_values)) >= (max(lat_values) - min(lat_values))
        axis = 0 if split_on_lon else 1
        ordered = sorted(items, key=lambda item: (float(item["centroid"][axis]), item["resolved_code"]))
        midpoint = max(1, len(ordered) // 2)
        left = ordered[:midpoint]
        right = ordered[midpoint:]
        if not left or not right:
            return [ordered]
        return recurse(left) + recurse(right)

    return recurse(groups)


def write_output(
    groups: list[dict[str, Any]],
    missing_codes: list[str],
    target_bytes: int,
    precision: int,
    neighbor_padding_degrees: float,
    min_neighbor_count: int,
) -> dict[str, Any]:
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    BUNDLES_DIR.mkdir(parents=True, exist_ok=True)

    partitions = partition_groups(groups, target_bytes)
    bundles_meta: list[dict[str, Any]] = []
    code_to_bundle: dict[str, str] = {}
    total_features = 0

    for index, partition in enumerate(partitions, start=1):
        bundle_id = f"bundle-{index:03d}"
        relative_file = f"bundles/{bundle_id}.geojson"
        bundle_path = OUTPUT_DIR / relative_file
        bundle_features: list[dict[str, Any]] = []
        bundle_boxes: list[list[float] | None] = []
        bundle_codes: list[str] = []
        for group in partition:
            bundle_features.extend(group["features"])
            bundle_boxes.append(group["bbox"])
            bundle_codes.extend(group["codes"])
            for code in group["codes"]:
                code_to_bundle[code] = bundle_id
        feature_collection = {
            "type": "FeatureCollection",
            "metadata": {
                "bundle_id": bundle_id,
                "practice_count": len(sorted(set(bundle_codes))),
                "feature_count": len(bundle_features),
            },
            "features": bundle_features,
        }
        serialized = json.dumps(feature_collection, ensure_ascii=False, separators=(",", ":"))
        bundle_path.write_text(serialized, encoding="utf-8")
        total_features += len(bundle_features)
        bundles_meta.append(
            {
                "id": bundle_id,
                "file": relative_file,
                "practice_codes": sorted(set(bundle_codes)),
                "practice_count": len(sorted(set(bundle_codes))),
                "feature_count": len(bundle_features),
                "bbox": union_bbox(bundle_boxes),
                "file_size_bytes": bundle_path.stat().st_size,
            }
        )

    for bundle in bundles_meta:
        expanded_bbox = expand_bbox(bundle.get("bbox"), neighbor_padding_degrees)
        intersecting_ids = sorted(
            other["id"]
            for other in bundles_meta
            if other["id"] != bundle["id"] and bboxes_intersect(expanded_bbox, other.get("bbox"))
        )
        if len(intersecting_ids) < min_neighbor_count:
            nearest_ids = [
                other["id"]
                for other in sorted(
                    (other for other in bundles_meta if other["id"] != bundle["id"]),
                    key=lambda other: (bundle_distance(bundle, other), other["id"]),
                )
                if other["id"] not in intersecting_ids
            ][: max(0, min_neighbor_count - len(intersecting_ids))]
            intersecting_ids.extend(nearest_ids)
        bundle["expanded_bbox"] = expanded_bbox
        bundle["neighbor_bundle_ids"] = sorted(set(intersecting_ids))

    index_payload = {
        "type": "catchment-index",
        "version": "2026-03-23",
        "target_bundle_bytes": target_bytes,
        "geometry_precision_digits": precision,
        "neighbor_padding_degrees": neighbor_padding_degrees,
        "min_neighbor_count": min_neighbor_count,
        "bundle_count": len(bundles_meta),
        "practice_count": len(code_to_bundle),
        "feature_count": total_features,
        "missing_practice_codes": missing_codes,
        "bundles": bundles_meta,
        "code_to_bundle": code_to_bundle,
    }
    INDEX_JSON.write_text(json.dumps(index_payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return index_payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Build segmented static England catchment bundles for the published map.")
    parser.add_argument("--target-bytes", type=int, default=300_000, help="Approximate max uncompressed bytes per bundle before splitting.")
    parser.add_argument("--precision", type=int, default=5, help="Coordinate decimal places to keep in output geometries.")
    parser.add_argument("--neighbor-padding-degrees", type=float, default=0.08, help="Expand each bundle bbox by this amount when deriving neighboring bundles.")
    parser.add_argument("--min-neighbor-count", type=int, default=3, help="Ensure each bundle lists at least this many neighboring bundle ids.")
    args = parser.parse_args()

    module = load_build_module()
    if not CORE_JSON.exists():
        raise FileNotFoundError(f"Core dataset JSON not found: {CORE_JSON}")

    england_rows = load_england_rows(module)
    groups, missing_codes = build_groups(module, england_rows, precision=args.precision)
    index_payload = write_output(
        groups,
        missing_codes,
        target_bytes=args.target_bytes,
        precision=args.precision,
        neighbor_padding_degrees=args.neighbor_padding_degrees,
        min_neighbor_count=args.min_neighbor_count,
    )
    print(json.dumps(
        {
            "output_dir": str(OUTPUT_DIR),
            "index_json": str(INDEX_JSON),
            "bundle_count": index_payload["bundle_count"],
            "practice_count": index_payload["practice_count"],
            "feature_count": index_payload["feature_count"],
            "missing_practice_codes": len(index_payload["missing_practice_codes"]),
        },
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
