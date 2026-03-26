#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import struct
import zlib
from array import array
from collections import Counter, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_INPUT_DIR = BASE_DIR / "catchments" / ".cache" / "gp-catchments-england" / "by_practice"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "output" / "england-catchment-availability"
DEFAULT_CORE_DATASET_GLOB = "gtd-greater-manchester-gp-practice-reviews-*/gtd_greater_manchester_gp_practices.json"
EARTH_RADIUS_M = 6_378_137.0
TILE_SIZE = 256


@dataclass(frozen=True)
class CountBand:
    label: str
    minimum: int
    maximum: int | None
    color_rgba: tuple[int, int, int, int]

    def contains(self, value: int) -> bool:
        if value < self.minimum:
            return False
        if self.maximum is None:
            return True
        return value <= self.maximum

    def color_hex(self) -> str:
        red, green, blue, alpha = self.color_rgba
        return f"#{red:02x}{green:02x}{blue:02x}{alpha:02x}"


DEFAULT_BANDS = [
    CountBand("0", 0, 0, (178, 24, 43, 204)),
    CountBand("1-2", 1, 2, (239, 138, 98, 188)),
    CountBand("3-5", 3, 5, (253, 219, 127, 176)),
    CountBand("6-9", 6, 9, (209, 229, 139, 176)),
    CountBand("10-19", 10, 19, (102, 189, 99, 184)),
    CountBand("20+", 20, None, (27, 120, 55, 192)),
]


def log(*args: object) -> None:
    print(*args)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Rasterize England GP catchment overlaps into a banded availability surface. "
            "This is an offline analysis generator, not a client-side map build."
        )
    )
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR, help="Directory of per-practice GeoJSON catchments")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for PNG, tiles, and summaries")
    parser.add_argument("--width", type=int, default=2048, help="Raster width in projected pixels")
    parser.add_argument("--padding-degrees", type=float, default=0.02, help="Small lon/lat padding around the data bbox")
    parser.add_argument("--limit", type=int, default=0, help="Only process the first N practice files for quick tests")
    parser.add_argument("--tile-min-zoom", type=int, default=4, help="Lowest XYZ zoom to generate")
    parser.add_argument("--tile-max-zoom", type=int, default=9, help="Highest XYZ zoom to generate")
    parser.add_argument(
        "--core-fallback-json",
        type=Path,
        default=None,
        help="Optional Manchester-core dataset JSON used to add a small point fallback for reviewed practices that lack cached catchment polygons",
    )
    parser.add_argument(
        "--core-fallback-radius-miles",
        type=float,
        default=2.5,
        help="Radius for the reviewed-practice point fallback when a Manchester core row has no cached catchment polygon",
    )
    parser.add_argument(
        "--out-of-area-flags-json",
        type=Path,
        default=None,
        help="Optional England registration-flag cache used to add soft out-of-area support halos around flagged practices",
    )
    parser.add_argument(
        "--out-of-area-near-miles",
        type=float,
        default=0.0,
        help="Full-strength England out-of-area support radius",
    )
    parser.add_argument(
        "--out-of-area-far-miles",
        type=float,
        default=0.0,
        help="England out-of-area support falloff radius",
    )
    return parser.parse_args()


def mercator_x(lon: float) -> float:
    return (lon + 180.0) / 360.0


def mercator_y(lat: float) -> float:
    bounded_lat = max(min(lat, 85.05112878), -85.05112878)
    radians_lat = math.radians(bounded_lat)
    return (1.0 - math.log(math.tan((math.pi / 4.0) + (radians_lat / 2.0))) / math.pi) / 2.0


def inverse_mercator_x(value: float) -> float:
    return (value * 360.0) - 180.0


def inverse_mercator_y(value: float) -> float:
    return math.degrees(math.atan(math.sinh(math.pi * (1.0 - (2.0 * value)))))


def iter_geojson_paths(input_dir: Path, limit: int = 0) -> list[Path]:
    paths = sorted(input_dir.glob("*.geojson"))
    if limit > 0:
        return paths[:limit]
    return paths


def load_geojson(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_core_dataset_path(explicit_path: Path | None) -> Path | None:
    if explicit_path is not None:
        return explicit_path if explicit_path.exists() else None
    output_root = BASE_DIR / "output"
    matches = sorted(output_root.glob(DEFAULT_CORE_DATASET_GLOB))
    if matches:
        return matches[-1]
    legacy = BASE_DIR / "archive" / "legacy-root-exports" / "gtd_greater_manchester_gp_practices.json"
    return legacy if legacy.exists() else None


def geojson_features(payload: dict[str, Any]) -> list[dict[str, Any]]:
    item_type = payload.get("type")
    if item_type == "FeatureCollection":
        return [feature for feature in payload.get("features", []) if isinstance(feature, dict)]
    if item_type == "Feature":
        return [payload]
    return []


def iter_polygon_rings(geometry: dict[str, Any]) -> Iterable[list[list[list[float]]]]:
    geometry_type = geometry.get("type")
    coordinates = geometry.get("coordinates")
    if geometry_type == "Polygon" and isinstance(coordinates, list):
        yield coordinates
    elif geometry_type == "MultiPolygon" and isinstance(coordinates, list):
        for polygon in coordinates:
            if isinstance(polygon, list):
                yield polygon


def ring_points(ring: list[Any]) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for point in ring:
        if not isinstance(point, (list, tuple)) or len(point) < 2:
            continue
        try:
            lon = float(point[0])
            lat = float(point[1])
        except (TypeError, ValueError):
            continue
        points.append((lon, lat))
    if len(points) >= 2 and points[0] != points[-1]:
        points.append(points[0])
    return points


def compute_source_stats(paths: list[Path], padding_degrees: float) -> dict[str, Any]:
    min_lon = math.inf
    min_lat = math.inf
    max_lon = -math.inf
    max_lat = -math.inf
    polygon_parts = 0
    vertex_count = 0

    for path in paths:
        payload = load_geojson(path)
        for feature in geojson_features(payload):
            for polygon in iter_polygon_rings(feature.get("geometry", {})):
                polygon_parts += 1
                for ring in polygon:
                    points = ring_points(ring)
                    vertex_count += len(points)
                    for lon, lat in points:
                        min_lon = min(min_lon, lon)
                        min_lat = min(min_lat, lat)
                        max_lon = max(max_lon, lon)
                        max_lat = max(max_lat, lat)

    if not math.isfinite(min_lon):
        raise RuntimeError(f"No polygon geometry found in {len(paths)} catchment files")

    padded_bbox = {
        "min_lon": round(min_lon - padding_degrees, 6),
        "min_lat": round(min_lat - padding_degrees, 6),
        "max_lon": round(max_lon + padding_degrees, 6),
        "max_lat": round(max_lat + padding_degrees, 6),
    }
    return {
        "file_count": len(paths),
        "polygon_parts": polygon_parts,
        "vertex_count": vertex_count,
        "bbox": padded_bbox,
        "data_bbox": {
            "min_lon": round(min_lon, 6),
            "min_lat": round(min_lat, 6),
            "max_lon": round(max_lon, 6),
            "max_lat": round(max_lat, 6),
        },
    }


def projected_dimensions(bbox: dict[str, float], width: int) -> tuple[int, dict[str, float]]:
    min_x = mercator_x(bbox["min_lon"])
    max_x = mercator_x(bbox["max_lon"])
    min_y = mercator_y(bbox["max_lat"])
    max_y = mercator_y(bbox["min_lat"])
    aspect = (max_y - min_y) / (max_x - min_x)
    height = max(1, round(width * aspect))
    return height, {"min_x": min_x, "max_x": max_x, "min_y": min_y, "max_y": max_y}


def scanline_intervals(projected_ring: list[tuple[float, float]], scan_y: float) -> list[tuple[float, float]]:
    intersections: list[float] = []
    for index in range(len(projected_ring) - 1):
        x1, y1 = projected_ring[index]
        x2, y2 = projected_ring[index + 1]
        if y1 == y2:
            continue
        if (y1 <= scan_y < y2) or (y2 <= scan_y < y1):
            t = (scan_y - y1) / (y2 - y1)
            intersections.append(x1 + (t * (x2 - x1)))
    intersections.sort()
    return [(intersections[index], intersections[index + 1]) for index in range(0, len(intersections) - 1, 2)]


def rasterize(paths: list[Path], width: int, height: int, mercator_bbox: dict[str, float]) -> list[array]:
    diff_rows = [array("i", [0]) * (width + 1) for _ in range(height)]
    min_x = mercator_bbox["min_x"]
    max_x = mercator_bbox["max_x"]
    min_y = mercator_bbox["min_y"]
    max_y = mercator_bbox["max_y"]
    x_span = max_x - min_x
    y_span = max_y - min_y

    for index, path in enumerate(paths, start=1):
        if index % 500 == 0 or index == len(paths):
            log(f"rasterizing {index}/{len(paths)} catchment files")
        payload = load_geojson(path)
        for feature in geojson_features(payload):
            for polygon in iter_polygon_rings(feature.get("geometry", {})):
                for ring_index, ring in enumerate(polygon):
                    points = ring_points(ring)
                    if len(points) < 4:
                        continue
                    projected_ring = [
                        (
                            ((mercator_x(lon) - min_x) / x_span) * (width - 1),
                            ((mercator_y(lat) - min_y) / y_span) * (height - 1),
                        )
                        for lon, lat in points
                    ]
                    min_row = max(0, math.floor(min(y for _x, y in projected_ring)))
                    max_row = min(height - 1, math.ceil(max(y for _x, y in projected_ring)))
                    sign = 1 if ring_index == 0 else -1
                    for row in range(min_row, max_row + 1):
                        row_center = row + 0.5
                        for x0, x1 in scanline_intervals(projected_ring, row_center):
                            left = max(0, math.ceil(min(x0, x1) - 0.5))
                            right = min(width - 1, math.floor(max(x0, x1) - 0.5))
                            if left <= right:
                                diff_rows[row][left] += sign
                                diff_rows[row][right + 1] -= sign
    return diff_rows


def load_missing_core_practice_points(core_dataset_path: Path | None, catchment_codes: set[str]) -> list[dict[str, Any]]:
    if core_dataset_path is None or not core_dataset_path.exists():
        return []
    try:
        payload = json.loads(core_dataset_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if not isinstance(payload, list):
        return []

    points_by_code: dict[str, dict[str, Any]] = {}
    for row in payload:
        if not isinstance(row, dict):
            continue
        code = str(row.get("canonical_code") or "").strip()
        if not code or code in catchment_codes:
            continue
        try:
            lat = float(row.get("latitude"))
            lon = float(row.get("longitude"))
        except (TypeError, ValueError):
            continue
        if not (math.isfinite(lat) and math.isfinite(lon)):
            continue
        points_by_code[code] = {
            "code": code,
            "name": str(row.get("practice_name") or "").strip(),
            "lat": round(lat, 6),
            "lon": round(lon, 6),
        }
    return sorted(points_by_code.values(), key=lambda item: (item["lat"], item["lon"], item["code"]))


def load_out_of_area_support_points(core_dataset_path: Path | None, flags_path: Path | None) -> list[dict[str, Any]]:
    if core_dataset_path is None or not core_dataset_path.exists():
        return []
    if flags_path is None or not flags_path.exists():
        return []
    try:
        core_payload = json.loads(core_dataset_path.read_text(encoding="utf-8"))
        flags_payload = json.loads(flags_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if not isinstance(core_payload, list) or not isinstance(flags_payload, dict):
        return []

    flagged_codes = {
        code
        for code, payload in flags_payload.items()
        if isinstance(payload, dict)
        and bool(payload.get("accepts_out_of_area_registrations"))
        and bool(payload.get("accepting_new_patients"))
    }
    if not flagged_codes:
        return []

    points_by_code: dict[str, dict[str, Any]] = {}
    for row in core_payload:
        if not isinstance(row, dict):
            continue
        code = str(row.get("canonical_code") or "").strip()
        if not code or code not in flagged_codes:
            continue
        try:
            lat = float(row.get("latitude"))
            lon = float(row.get("longitude"))
        except (TypeError, ValueError):
            continue
        if not (math.isfinite(lat) and math.isfinite(lon)):
            continue
        points_by_code[code] = {
            "code": code,
            "name": str(row.get("practice_name") or "").strip(),
            "lat": round(lat, 6),
            "lon": round(lon, 6),
        }
    return sorted(points_by_code.values(), key=lambda item: (item["lat"], item["lon"], item["code"]))


def rasterize_point_fallbacks(
    diff_rows: list[array],
    points: list[dict[str, Any]],
    width: int,
    height: int,
    mercator_bbox: dict[str, float],
    radius_miles: float,
) -> None:
    if not points or radius_miles <= 0:
        return
    min_x = mercator_bbox["min_x"]
    max_x = mercator_bbox["max_x"]
    min_y = mercator_bbox["min_y"]
    max_y = mercator_bbox["max_y"]
    x_span = max_x - min_x
    y_span = max_y - min_y
    row_lats = [inverse_mercator_y(min_y + (((row + 0.5) / height) * y_span)) for row in range(height)]

    for index, point in enumerate(points, start=1):
        if index % 100 == 0 or index == len(points):
            log(f"adding point fallbacks {index}/{len(points)}")
        lat = float(point["lat"])
        lon = float(point["lon"])
        delta_lat = radius_miles / 69.0
        min_row = max(0, math.floor(((mercator_y(lat + delta_lat) - min_y) / y_span) * (height - 1)))
        max_row = min(height - 1, math.ceil(((mercator_y(lat - delta_lat) - min_y) / y_span) * (height - 1)))
        for row in range(min_row, max_row + 1):
            row_lat = row_lats[row]
            dy_miles = abs(row_lat - lat) * 69.0
            if dy_miles > radius_miles:
                continue
            dx_miles = math.sqrt(max(0.0, (radius_miles * radius_miles) - (dy_miles * dy_miles)))
            cos_mid = max(0.2, math.cos(math.radians((row_lat + lat) / 2.0)))
            lon_delta = dx_miles / (69.0 * cos_mid)
            left_x = ((mercator_x(lon - lon_delta) - min_x) / x_span) * (width - 1)
            right_x = ((mercator_x(lon + lon_delta) - min_x) / x_span) * (width - 1)
            left = max(0, math.ceil(min(left_x, right_x) - 0.5))
            right = min(width - 1, math.floor(max(left_x, right_x) - 0.5))
            if left <= right:
                diff_rows[row][left] += 1
                diff_rows[row][right + 1] -= 1


def rasterize_support_strength(
    points: list[dict[str, Any]],
    width: int,
    height: int,
    mercator_bbox: dict[str, float],
    near_miles: float,
    far_miles: float,
) -> list[array]:
    strength_rows = [array("f", [0.0]) * width for _ in range(height)]
    if not points or far_miles <= 0.0:
        return strength_rows
    min_x = mercator_bbox["min_x"]
    max_x = mercator_bbox["max_x"]
    min_y = mercator_bbox["min_y"]
    max_y = mercator_bbox["max_y"]
    x_span = max_x - min_x
    y_span = max_y - min_y
    row_lats = [inverse_mercator_y(min_y + (((row + 0.5) / height) * y_span)) for row in range(height)]
    col_lons = [inverse_mercator_x(min_x + (((col + 0.5) / width) * x_span)) for col in range(width)]
    row_lat_rads = [math.radians(lat) for lat in row_lats]
    col_lon_rads = [math.radians(lon) for lon in col_lons]
    near_m = max(0.0, near_miles) * 1609.344
    far_m = max(near_m, far_miles * 1609.344)
    falloff_span = max(1.0, far_m - near_m)

    for point in points:
        lat = float(point["lat"])
        lon = float(point["lon"])
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        delta_lat = far_miles / 69.0
        delta_lon = far_miles / (69.0 * max(0.2, math.cos(lat_rad)))
        min_row = max(0, math.floor(((mercator_y(lat + delta_lat) - min_y) / y_span) * (height - 1)))
        max_row = min(height - 1, math.ceil(((mercator_y(lat - delta_lat) - min_y) / y_span) * (height - 1)))
        min_col = max(0, math.floor(((mercator_x(lon - delta_lon) - min_x) / x_span) * (width - 1)))
        max_col = min(width - 1, math.ceil(((mercator_x(lon + delta_lon) - min_x) / x_span) * (width - 1)))

        for row_index in range(min_row, max_row + 1):
            row_lat_rad = row_lat_rads[row_index]
            cos_mid = math.cos((row_lat_rad + lat_rad) / 2.0)
            dy = row_lat_rad - lat_rad
            target_row = strength_rows[row_index]
            for col_index in range(min_col, max_col + 1):
                dx = (math.radians(col_lons[col_index]) - lon_rad) * cos_mid
                distance_m = EARTH_RADIUS_M * math.sqrt((dx * dx) + (dy * dy))
                if distance_m > far_m:
                    continue
                if distance_m <= near_m:
                    weight = 1.0
                else:
                    weight = (far_m - distance_m) / falloff_span
                if weight > target_row[col_index]:
                    target_row[col_index] = weight
    return strength_rows


def band_for_value(value: int, bands: list[CountBand]) -> CountBand:
    for band in bands:
        if band.contains(value):
            return band
    return bands[-1]


def row_pixel_area_sq_km(row: int, width: int, height: int, mercator_bbox: dict[str, float]) -> float:
    min_x = mercator_bbox["min_x"]
    max_x = mercator_bbox["max_x"]
    min_y = mercator_bbox["min_y"]
    max_y = mercator_bbox["max_y"]
    x_span = max_x - min_x
    y_span = max_y - min_y
    west = inverse_mercator_x(min_x)
    east = inverse_mercator_x(min_x + (x_span / width))
    north = inverse_mercator_y(min_y + ((row / height) * y_span))
    south = inverse_mercator_y(min_y + (((row + 1) / height) * y_span))
    mid_lat = math.radians((north + south) / 2.0)
    pixel_width_m = EARTH_RADIUS_M * math.radians(abs(east - west)) * math.cos(mid_lat)
    pixel_height_m = EARTH_RADIUS_M * math.radians(abs(north - south))
    return (pixel_width_m * pixel_height_m) / 1_000_000.0


def png_chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    )


def write_png_rgba(path: Path, width: int, height: int, rows: list[bytes]) -> None:
    if len(rows) != height:
        raise ValueError(f"expected {height} rows, got {len(rows)}")
    raw = b"".join(b"\x00" + row for row in rows)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    png = b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            png_chunk(b"IHDR", ihdr),
            png_chunk(b"IDAT", zlib.compress(raw, level=9)),
            png_chunk(b"IEND", b""),
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)


def build_exterior_zero_mask(counts_rows: list[array], support_rows: list[array], width: int, height: int) -> list[bytearray]:
    if not counts_rows or width <= 0 or height <= 0:
        return []
    mask_rows = [bytearray(width) for _ in range(height)]
    queue: deque[tuple[int, int]] = deque()
    seed_candidates = [
        (min(1, width - 1), min(1, height - 1)),
        (0, 0),
        (width - 1, 0),
        (0, height - 1),
        (width - 1, height - 1),
    ]
    seen_candidates: set[tuple[int, int]] = set()
    for candidate in seed_candidates:
        if candidate in seen_candidates:
            continue
        seen_candidates.add(candidate)
        x, y = candidate
        if int(counts_rows[y][x]) != 0 or float(support_rows[y][x]) > 0.0 or mask_rows[y][x]:
            continue
        mask_rows[y][x] = 1
        queue.append((x, y))
    if not queue:
        for x in range(width):
            for y in (0, height - 1):
                if int(counts_rows[y][x]) == 0 and float(support_rows[y][x]) <= 0.0 and not mask_rows[y][x]:
                    mask_rows[y][x] = 1
                    queue.append((x, y))
        for y in range(height):
            for x in (0, width - 1):
                if int(counts_rows[y][x]) == 0 and float(support_rows[y][x]) <= 0.0 and not mask_rows[y][x]:
                    mask_rows[y][x] = 1
                    queue.append((x, y))

    while queue:
        x, y = queue.popleft()
        if x > 0 and not mask_rows[y][x - 1] and int(counts_rows[y][x - 1]) == 0 and float(support_rows[y][x - 1]) <= 0.0:
            mask_rows[y][x - 1] = 1
            queue.append((x - 1, y))
        if x + 1 < width and not mask_rows[y][x + 1] and int(counts_rows[y][x + 1]) == 0 and float(support_rows[y][x + 1]) <= 0.0:
            mask_rows[y][x + 1] = 1
            queue.append((x + 1, y))
        if y > 0 and not mask_rows[y - 1][x] and int(counts_rows[y - 1][x]) == 0 and float(support_rows[y - 1][x]) <= 0.0:
            mask_rows[y - 1][x] = 1
            queue.append((x, y - 1))
        if y + 1 < height and not mask_rows[y + 1][x] and int(counts_rows[y + 1][x]) == 0 and float(support_rows[y + 1][x]) <= 0.0:
            mask_rows[y + 1][x] = 1
            queue.append((x, y + 1))
    return mask_rows


def summarize_exterior_mask(
    mask_rows: list[bytearray],
    width: int,
    height: int,
    mercator_bbox: dict[str, float],
) -> dict[str, Any]:
    masked_pixels = 0
    masked_sq_km = 0.0
    for row_index, mask_row in enumerate(mask_rows):
        row_masked = sum(mask_row)
        if not row_masked:
            continue
        masked_pixels += row_masked
        masked_sq_km += row_pixel_area_sq_km(row_index, width, height, mercator_bbox) * row_masked
    total_pixels = width * height
    return {
        "masked_pixels": masked_pixels,
        "masked_pixel_ratio": round((masked_pixels / total_pixels) if total_pixels else 0.0, 6),
        "approx_sq_km": round(masked_sq_km, 3),
    }


def build_preview_rows(
    counts_rows: list[array],
    support_rows: list[array],
    mask_rows: list[bytearray],
    bands: list[CountBand],
) -> list[bytes]:
    preview_rows: list[bytes] = []
    support_band = next((band for band in bands if band.label == "1-2"), bands[1] if len(bands) > 1 else bands[0])
    for counts_row, support_row, mask_row in zip(counts_rows, support_rows, mask_rows):
        row = bytearray(len(counts_row) * 4)
        for column, value in enumerate(counts_row):
            if mask_row[column]:
                continue
            offset = column * 4
            if value > 0:
                red, green, blue, alpha = band_for_value(int(value), bands).color_rgba
                row[offset : offset + 4] = bytes((red, green, blue, alpha))
                continue
            support = max(0.0, min(1.0, float(support_row[column])))
            if support <= 0.0:
                red, green, blue, alpha = band_for_value(0, bands).color_rgba
                row[offset : offset + 4] = bytes((red, green, blue, alpha))
                continue
            red, green, blue, base_alpha = support_band.color_rgba
            alpha = max(32, round(base_alpha * support))
            row[offset : offset + 4] = bytes((red, green, blue, alpha))
        preview_rows.append(bytes(row))
    return preview_rows


def summarize_support_strength(
    support_rows: list[array],
    width: int,
    height: int,
    mercator_bbox: dict[str, float],
) -> dict[str, Any]:
    positive_pixels = 0
    approx_sq_km = 0.0
    weighted_pixel_sum = 0.0
    for row_index, support_row in enumerate(support_rows):
        row_area_sq_km = row_pixel_area_sq_km(row_index, width, height, mercator_bbox)
        for value in support_row:
            support = max(0.0, min(1.0, float(value)))
            if support <= 0.0:
                continue
            positive_pixels += 1
            approx_sq_km += row_area_sq_km
            weighted_pixel_sum += support
    total_pixels = width * height
    return {
        "positive_pixels": positive_pixels,
        "positive_pixel_ratio": round((positive_pixels / total_pixels) if total_pixels else 0.0, 6),
        "approx_sq_km": round(approx_sq_km, 3),
        "weighted_pixel_sum": round(weighted_pixel_sum, 3),
    }


def apply_exterior_mask_to_preview(preview_rows: list[bytes], mask_rows: list[bytearray]) -> list[bytes]:
    if not mask_rows:
        return preview_rows
    output_rows: list[bytes] = []
    for row_bytes, mask_row in zip(preview_rows, mask_rows):
        if not any(mask_row):
            output_rows.append(row_bytes)
            continue
        row = bytearray(row_bytes)
        for column, masked in enumerate(mask_row):
            if masked:
                offset = column * 4
                row[offset : offset + 4] = b"\x00\x00\x00\x00"
        output_rows.append(bytes(row))
    return output_rows


def build_counts_and_preview(
    diff_rows: list[array],
    width: int,
    height: int,
    mercator_bbox: dict[str, float],
    bands: list[CountBand],
) -> tuple[list[array], list[bytes], dict[str, Any]]:
    counts_rows: list[array] = []
    preview_rows: list[bytes] = []
    histogram: Counter[int] = Counter()
    band_pixels: Counter[str] = Counter()
    band_sq_km: Counter[str] = Counter()
    total_sq_km = 0.0
    covered_sq_km = 0.0
    max_overlap = 0

    for row_index, diff_row in enumerate(diff_rows):
        row_area_sq_km = row_pixel_area_sq_km(row_index, width, height, mercator_bbox)
        total_sq_km += row_area_sq_km * width
        running = 0
        counts_row = array("H")
        preview_row = bytearray(width * 4)
        for column in range(width):
            running += diff_row[column]
            value = max(0, running)
            counts_row.append(value)
            histogram[value] += 1
            if value > max_overlap:
                max_overlap = value
            band = band_for_value(value, bands)
            band_pixels[band.label] += 1
            band_sq_km[band.label] += row_area_sq_km
            if value > 0:
                covered_sq_km += row_area_sq_km
            offset = column * 4
            red, green, blue, alpha = band.color_rgba
            preview_row[offset : offset + 4] = bytes((red, green, blue, alpha))
        counts_rows.append(counts_row)
        preview_rows.append(bytes(preview_row))

    summary = {
        "histogram": {str(value): count for value, count in sorted(histogram.items())},
        "max_overlap": max_overlap,
        "total_bbox_sq_km": round(total_sq_km, 3),
        "covered_sq_km": round(covered_sq_km, 3),
        "coverage_ratio": round((covered_sq_km / total_sq_km) if total_sq_km else 0.0, 6),
        "bands": [
            {
                "label": band.label,
                "minimum": band.minimum,
                "maximum": band.maximum,
                "color": band.color_hex(),
                "pixel_count": int(band_pixels[band.label]),
                "pixel_ratio": round((band_pixels[band.label] / (width * height)) if width and height else 0.0, 6),
                "approx_sq_km": round(float(band_sq_km[band.label]), 3),
            }
            for band in bands
        ],
    }
    return counts_rows, preview_rows, summary


def write_summary_text(path: Path, summary: dict[str, Any], stats: dict[str, Any], width: int, height: int) -> None:
    lines = [
        "Catchment Availability Raster Summary",
        "",
        f"Files processed: {stats['file_count']}",
        f"Polygon parts: {stats['polygon_parts']}",
        f"Vertices: {stats['vertex_count']}",
        f"Reviewed-practice point fallbacks: {stats['point_fallback_count']}",
        f"Point fallback radius: {stats['point_fallback_radius_miles']} miles",
        f"Out-of-area support practices: {stats['out_of_area_support_count']}",
        f"Out-of-area support radius: {stats['out_of_area_support_near_miles']} to {stats['out_of_area_support_far_miles']} miles",
        f"Out-of-area support footprint: {summary['out_of_area_support']['positive_pixels']:,} pixels / {summary['out_of_area_support']['approx_sq_km']:,} sq km",
        f"Exterior transparent mask: {summary['exterior_mask']['masked_pixels']:,} pixels / {summary['exterior_mask']['approx_sq_km']:,} sq km",
        f"Raster size: {width} x {height}",
        f"Max overlap count: {summary['max_overlap']}",
        f"Approx bbox area: {summary['total_bbox_sq_km']:,} sq km",
        f"Approx covered area (>0): {summary['covered_sq_km']:,} sq km",
        f"Coverage ratio: {summary['coverage_ratio']:.2%}",
        "",
        "Band distribution:",
    ]
    for band in summary["bands"]:
        lines.append(
            f"  {band['label']:>5}  pixels={band['pixel_count']:,}  share={band['pixel_ratio']:.2%}  approx_area={band['approx_sq_km']:,} sq km  color={band['color']}"
        )
    lines.extend(
        [
            "",
            "Top exact overlap counts:",
        ]
    )
    histogram_items = sorted(
        ((int(key), value) for key, value in summary["histogram"].items()),
        key=lambda item: (-item[1], item[0]),
    )[:12]
    for value, count in histogram_items:
        lines.append(f"  {value:>3}  pixels={count:,}")
    lines.extend(
        [
            "",
            "Note: the zero band is measured across the raster bbox, so coastal sea and outside-land cells are still zero unless a separate England land/population mask is added.",
            "England overlap counts are primarily polygon-derived, with a small local point fallback only for reviewed Manchester-core practices that have coordinates but no cached catchment polygon.",
            "Practices flagged as accepting out-of-area registrations add a soft visual halo outside hard catchments; those halos affect the preview and tiles, not the raw overlap histogram.",
            "Preview PNGs and XYZ tiles now flood-fill the contiguous zero-value exterior from the raster edge and make only that outside area transparent.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def tile_ranges(mercator_bbox: dict[str, float], zoom: int) -> tuple[range, range]:
    tiles = 1 << zoom
    min_x = max(0, math.floor(mercator_bbox["min_x"] * tiles))
    max_x = min(tiles - 1, math.floor(mercator_bbox["max_x"] * tiles))
    min_y = max(0, math.floor(mercator_bbox["min_y"] * tiles))
    max_y = min(tiles - 1, math.floor(mercator_bbox["max_y"] * tiles))
    return range(min_x, max_x + 1), range(min_y, max_y + 1)


def sample_count(
    counts_rows: list[array],
    support_rows: list[array],
    exterior_mask_rows: list[bytearray],
    mercator_bbox: dict[str, float],
    sample_x: float,
    sample_y: float,
    width: int,
    height: int,
) -> int | None:
    if sample_x < mercator_bbox["min_x"] or sample_x >= mercator_bbox["max_x"]:
        return None
    if sample_y < mercator_bbox["min_y"] or sample_y >= mercator_bbox["max_y"]:
        return None
    src_x = int(((sample_x - mercator_bbox["min_x"]) / (mercator_bbox["max_x"] - mercator_bbox["min_x"])) * width)
    src_y = int(((sample_y - mercator_bbox["min_y"]) / (mercator_bbox["max_y"] - mercator_bbox["min_y"])) * height)
    src_x = min(max(src_x, 0), width - 1)
    src_y = min(max(src_y, 0), height - 1)
    if exterior_mask_rows and exterior_mask_rows[src_y][src_x]:
        return None
    return int(counts_rows[src_y][src_x])


def sample_support(
    support_rows: list[array],
    mercator_bbox: dict[str, float],
    sample_x: float,
    sample_y: float,
    width: int,
    height: int,
) -> float | None:
    if sample_x < mercator_bbox["min_x"] or sample_x >= mercator_bbox["max_x"]:
        return None
    if sample_y < mercator_bbox["min_y"] or sample_y >= mercator_bbox["max_y"]:
        return None
    src_x = int(((sample_x - mercator_bbox["min_x"]) / (mercator_bbox["max_x"] - mercator_bbox["min_x"])) * width)
    src_y = int(((sample_y - mercator_bbox["min_y"]) / (mercator_bbox["max_y"] - mercator_bbox["min_y"])) * height)
    src_x = min(max(src_x, 0), width - 1)
    src_y = min(max(src_y, 0), height - 1)
    return float(support_rows[src_y][src_x])


def write_tiles(
    output_dir: Path,
    counts_rows: list[array],
    support_rows: list[array],
    exterior_mask_rows: list[bytearray],
    mercator_bbox: dict[str, float],
    width: int,
    height: int,
    bands: list[CountBand],
    min_zoom: int,
    max_zoom: int,
) -> dict[str, Any]:
    if max_zoom < min_zoom:
        raise ValueError("--tile-max-zoom must be >= --tile-min-zoom")

    tiles_dir = output_dir / "tiles"
    support_band = next((band for band in bands if band.label == "1-2"), bands[1] if len(bands) > 1 else bands[0])
    total_tiles = 0
    for zoom in range(min_zoom, max_zoom + 1):
        x_range, y_range = tile_ranges(mercator_bbox, zoom)
        zoom_tiles = len(x_range) * len(y_range)
        total_tiles += zoom_tiles
        log(f"writing {zoom_tiles} tiles for z{zoom}")
        tiles = 1 << zoom
        for tile_x in x_range:
            for tile_y in y_range:
                row_map: list[bytes] = []
                y_samples = [
                    (tile_y + ((pixel_y + 0.5) / TILE_SIZE)) / tiles
                    for pixel_y in range(TILE_SIZE)
                ]
                x_samples = [
                    (tile_x + ((pixel_x + 0.5) / TILE_SIZE)) / tiles
                    for pixel_x in range(TILE_SIZE)
                ]
                for sample_y in y_samples:
                    row = bytearray(TILE_SIZE * 4)
                    for pixel_x, sample_x in enumerate(x_samples):
                        value = sample_count(counts_rows, support_rows, exterior_mask_rows, mercator_bbox, sample_x, sample_y, width, height)
                        if value is None:
                            continue
                        if value > 0:
                            red, green, blue, alpha = band_for_value(value, bands).color_rgba
                        else:
                            support = max(0.0, min(1.0, sample_support(support_rows, mercator_bbox, sample_x, sample_y, width, height) or 0.0))
                            if support <= 0.0:
                                red, green, blue, alpha = band_for_value(0, bands).color_rgba
                            else:
                                red, green, blue, base_alpha = support_band.color_rgba
                                alpha = max(32, round(base_alpha * support))
                        offset = pixel_x * 4
                        row[offset : offset + 4] = bytes((red, green, blue, alpha))
                    row_map.append(bytes(row))
                write_png_rgba(tiles_dir / str(zoom) / str(tile_x) / f"{tile_y}.png", TILE_SIZE, TILE_SIZE, row_map)
    return {
        "directory": str(tiles_dir),
        "tile_size": TILE_SIZE,
        "min_zoom": min_zoom,
        "max_zoom": max_zoom,
        "tile_count": total_tiles,
        "template": "tiles/{z}/{x}/{y}.png",
    }


def main() -> int:
    args = parse_args()
    paths = iter_geojson_paths(args.input_dir, args.limit)
    if not paths:
        raise RuntimeError(f"No .geojson files found in {args.input_dir}")

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    log(f"scanning {len(paths)} catchment files")
    source_stats = compute_source_stats(paths, args.padding_degrees)
    source_stats["point_fallback_count"] = 0
    source_stats["point_fallback_radius_miles"] = round(max(0.0, float(args.core_fallback_radius_miles)), 3)
    source_stats["out_of_area_support_count"] = 0
    source_stats["out_of_area_support_near_miles"] = round(max(0.0, float(args.out_of_area_near_miles)), 3)
    source_stats["out_of_area_support_far_miles"] = round(max(0.0, float(args.out_of_area_far_miles)), 3)
    width = max(8, args.width)
    height, mercator_bbox = projected_dimensions(source_stats["bbox"], width)
    log(f"raster size will be {width} x {height}")

    diff_rows = rasterize(paths, width, height, mercator_bbox)
    core_dataset_path = resolve_core_dataset_path(args.core_fallback_json)
    fallback_points = load_missing_core_practice_points(core_dataset_path, {path.stem for path in paths})
    source_stats["point_fallback_count"] = len(fallback_points)
    if fallback_points:
        log(
            f"adding {len(fallback_points)} reviewed-practice point fallbacks from {core_dataset_path}"
        )
        rasterize_point_fallbacks(
            diff_rows,
            fallback_points,
            width,
            height,
            mercator_bbox,
            max(0.0, float(args.core_fallback_radius_miles)),
        )
    counts_rows, _preview_rows, summary = build_counts_and_preview(diff_rows, width, height, mercator_bbox, DEFAULT_BANDS)
    if max(0.0, float(args.out_of_area_far_miles)) > 0.0 and args.out_of_area_flags_json is not None:
        out_of_area_support_points = load_out_of_area_support_points(core_dataset_path, args.out_of_area_flags_json)
    else:
        out_of_area_support_points = []
    source_stats["out_of_area_support_count"] = len(out_of_area_support_points)
    support_rows = rasterize_support_strength(
        out_of_area_support_points,
        width,
        height,
        mercator_bbox,
        max(0.0, float(args.out_of_area_near_miles)),
        max(0.0, float(args.out_of_area_far_miles)),
    )
    summary["out_of_area_support"] = summarize_support_strength(support_rows, width, height, mercator_bbox)
    exterior_mask_rows = build_exterior_zero_mask(counts_rows, support_rows, width, height)
    summary["exterior_mask"] = summarize_exterior_mask(exterior_mask_rows, width, height, mercator_bbox)
    preview_rows = build_preview_rows(counts_rows, support_rows, exterior_mask_rows, DEFAULT_BANDS)

    preview_png = output_dir / "availability-bands.png"
    write_png_rgba(preview_png, width, height, preview_rows)
    summary_txt = output_dir / "summary.txt"
    summary_json = output_dir / "summary.json"
    metadata_json = output_dir / "metadata.json"
    write_summary_text(summary_txt, summary, source_stats, width, height)

    tile_manifest = write_tiles(
        output_dir,
        counts_rows,
        support_rows,
        exterior_mask_rows,
        mercator_bbox,
        width,
        height,
        DEFAULT_BANDS,
        args.tile_min_zoom,
        args.tile_max_zoom,
    )

    metadata = {
        "source": {
            "input_dir": str(args.input_dir),
            **source_stats,
        },
        "raster": {
            "width": width,
            "height": height,
            "mercator_bbox": {key: round(value, 9) for key, value in mercator_bbox.items()},
            "lonlat_bbox": source_stats["bbox"],
            "preview_png": str(preview_png),
        },
        "tile_manifest": tile_manifest,
        "bands": [
            {
                "label": band.label,
                "minimum": band.minimum,
                "maximum": band.maximum,
                "color": band.color_hex(),
            }
            for band in DEFAULT_BANDS
        ],
        "notes": [
            "Counts are polygon-derived England catchment overlaps, with a small local point fallback for reviewed Manchester-core practices that lack cached catchment polygons.",
            "Practices flagged as accepting out-of-area registrations add a soft visual halo outside hard catchments, using the configured England out-of-area radii.",
            "The zero band covers the raster bbox, so coastline/sea cells are still zero until a land or population mask is added.",
            "Preview PNGs and tiles flood-fill the contiguous zero-value exterior from the raster edge and make only that outside area transparent.",
            "Tiles are sampled from the projected raster with nearest-neighbour resampling, so they stay intentionally blocky at higher zooms.",
        ],
    }

    summary_payload = {
        **summary,
        "source": metadata["source"],
        "raster": metadata["raster"],
        "tile_manifest": tile_manifest,
    }

    summary_json.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")
    metadata_json.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "preview_png": str(preview_png),
                "summary_txt": str(summary_txt),
                "summary_json": str(summary_json),
                "metadata_json": str(metadata_json),
                "tile_dir": str(output_dir / "tiles"),
                "width": width,
                "height": height,
                "max_overlap": summary["max_overlap"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
