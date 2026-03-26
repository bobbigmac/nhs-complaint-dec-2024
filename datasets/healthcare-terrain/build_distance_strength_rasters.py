#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import struct
import sys
import zlib
from array import array
from collections import Counter, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DATASETS_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "output" / "distance-strength"
BUILD_MODULE_PATH = DATASETS_DIR / "build_gtd_gp_practice_dataset.py"
DEFAULT_REGISTRATION_FLAGS_PATH = DATASETS_DIR / "catchments" / ".cache" / "gp-registration-flags-england" / "flags_by_practice.json"
EARTH_RADIUS_KM = 6_371.0088
TILE_SIZE = 256


@dataclass(frozen=True)
class NationConfig:
    slug: str
    label: str
    near_miles: float
    far_miles: float
    nation: str


@dataclass(frozen=True)
class StrengthBand:
    label: str
    minimum: float
    maximum: float | None
    color_rgba: tuple[int, int, int, int]

    def contains(self, value: float) -> bool:
        if value < self.minimum:
            return False
        if self.maximum is None:
            return True
        return value <= self.maximum

    def color_hex(self) -> str:
        red, green, blue, alpha = self.color_rgba
        return f"#{red:02x}{green:02x}{blue:02x}{alpha:02x}"


NATION_CONFIGS = [
    NationConfig("england_out_of_area", "England out-of-area", 3.0, 10.0, "england"),
    NationConfig("scotland", "Scotland", 3.0, 12.0, "scotland"),
    NationConfig("wales", "Wales", 3.0, 10.0, "wales"),
    NationConfig("northern_ireland", "Northern Ireland", 3.0, 10.0, "northern_ireland"),
]
POINT_SOURCE_NATIONS = {config.nation for config in NATION_CONFIGS}

DEFAULT_BANDS = [
    StrengthBand("0", 0.0, 0.0, (165, 0, 38, 204)),
    StrengthBand("0-1", 0.000001, 1.0, (244, 109, 67, 188)),
    StrengthBand("1-2.5", 1.0, 2.5, (253, 174, 97, 184)),
    StrengthBand("2.5-5", 2.5, 5.0, (254, 224, 139, 176)),
    StrengthBand("5-10", 5.0, 10.0, (166, 217, 106, 184)),
    StrengthBand("10+", 10.0, None, (26, 150, 65, 192)),
]


def log(*args: object) -> None:
    print(*args)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build distance-strength terrain rasters for nations without published England-style catchments. "
            "Practice points contribute full strength inside the near radius and taper to zero at the far radius."
        )
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Root output directory")
    parser.add_argument("--width", type=int, default=1024, help="Raster width per nation")
    parser.add_argument("--padding-degrees", type=float, default=0.15, help="Extra lon/lat padding around each nation bbox")
    parser.add_argument("--tile-min-zoom", type=int, default=4, help="Lowest XYZ zoom to generate")
    parser.add_argument("--tile-max-zoom", type=int, default=8, help="Highest XYZ zoom to generate")
    parser.add_argument("--nations", nargs="*", default=[config.slug for config in NATION_CONFIGS], help="Nation slugs to build")
    return parser.parse_args()


def load_build_module():
    if str(DATASETS_DIR) not in sys.path:
        sys.path.insert(0, str(DATASETS_DIR))
    spec = importlib.util.spec_from_file_location("build_gtd_gp_practice_dataset", BUILD_MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import build module from {BUILD_MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


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


def miles_to_km(value: float) -> float:
    return value * 1.609344


def load_rows_by_nation(module: Any) -> dict[str, list[dict[str, Any]]]:
    rows_by_nation = {nation: [] for nation in POINT_SOURCE_NATIONS}
    rows_by_code_by_nation: dict[str, dict[str, dict[str, Any]]] = {nation: {} for nation in POINT_SOURCE_NATIONS}

    def add_row(nation: str, payload: dict[str, Any], *, prefer_existing: bool = False) -> None:
        if nation not in rows_by_code_by_nation:
            return
        code = str(payload.get("code") or "").strip()
        if not code:
            return
        existing = rows_by_code_by_nation[nation].get(code)
        if existing is not None and prefer_existing:
            return
        rows_by_code_by_nation[nation][code] = payload

    for row in module.build_national_map_supplementals():
        nation = str(row.get("nation") or "").strip().lower()
        if nation == "england":
            continue
        if nation not in rows_by_code_by_nation:
            continue
        try:
            lat = float(row.get("lat"))
            lon = float(row.get("lon"))
        except (TypeError, ValueError):
            continue
        if not (math.isfinite(lat) and math.isfinite(lon)):
            continue
        add_row(
            nation,
            {
                "code": str(row.get("code") or "").strip(),
                "name": str(row.get("name") or "").strip(),
                "lat": round(lat, 6),
                "lon": round(lon, 6),
                "registered_patient_count": row.get("registered_patient_count", ""),
                "accepting_new_patients": bool(row.get("accepting_new_patients")),
                "source": "national_supplemental",
            },
        )

    # England distance terrain is a separate out-of-area-support layer built from the local
    # registration-flag cache plus the reviewed Manchester-area practice coordinates.
    core_dataset_path = module.OUTPUT_DIR / "gtd_greater_manchester_gp_practices.json"
    flags_path = DEFAULT_REGISTRATION_FLAGS_PATH
    if core_dataset_path.exists() and flags_path.exists():
        try:
            core_rows = json.loads(core_dataset_path.read_text(encoding="utf-8"))
            flags_by_practice = json.loads(flags_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            core_rows = []
            flags_by_practice = {}
        if isinstance(core_rows, list) and isinstance(flags_by_practice, dict):
            for row in core_rows:
                code = str(row.get("canonical_code") or "").strip()
                if not code:
                    continue
                flag_payload = flags_by_practice.get(code) if isinstance(flags_by_practice, dict) else None
                if not isinstance(flag_payload, dict):
                    continue
                if not bool(flag_payload.get("accepts_out_of_area_registrations")):
                    continue
                if not bool(flag_payload.get("accepting_new_patients")):
                    continue
                try:
                    lat = float(row.get("latitude"))
                    lon = float(row.get("longitude"))
                except (TypeError, ValueError):
                    continue
                if not (math.isfinite(lat) and math.isfinite(lon)):
                    continue
                add_row(
                    "england",
                    {
                        "code": code,
                        "name": str(row.get("practice_name") or "").strip(),
                        "lat": round(lat, 6),
                        "lon": round(lon, 6),
                        "registered_patient_count": row.get("registered_patient_count", ""),
                        "accepting_new_patients": bool(row.get("accepting_new_patients")),
                        "source": "england_out_of_area_flag_cache",
                    },
                )

    for nation, rows_by_code in rows_by_code_by_nation.items():
        rows_by_nation[nation] = sorted(rows_by_code.values(), key=lambda row: (row["lat"], row["lon"], row["code"]))
    return rows_by_nation


def projected_dimensions(bbox: dict[str, float], width: int) -> tuple[int, dict[str, float]]:
    min_x = mercator_x(bbox["min_lon"])
    max_x = mercator_x(bbox["max_lon"])
    min_y = mercator_y(bbox["max_lat"])
    max_y = mercator_y(bbox["min_lat"])
    aspect = (max_y - min_y) / (max_x - min_x)
    height = max(1, round(width * aspect))
    return height, {"min_x": min_x, "max_x": max_x, "min_y": min_y, "max_y": max_y}


def nation_bbox(rows: list[dict[str, Any]], padding_degrees: float, far_miles: float) -> dict[str, float]:
    min_lon = min(row["lon"] for row in rows)
    max_lon = max(row["lon"] for row in rows)
    min_lat = min(row["lat"] for row in rows)
    max_lat = max(row["lat"] for row in rows)
    lat_pad = (far_miles / 69.0) + padding_degrees
    mid_lat = math.radians((min_lat + max_lat) / 2.0)
    cos_lat = max(0.2, math.cos(mid_lat))
    lon_pad = (far_miles / (69.0 * cos_lat)) + padding_degrees
    return {
        "min_lon": round(min_lon - lon_pad, 6),
        "min_lat": round(min_lat - lat_pad, 6),
        "max_lon": round(max_lon + lon_pad, 6),
        "max_lat": round(max_lat + lat_pad, 6),
    }


def strength_band_for_value(value: float, bands: list[StrengthBand]) -> StrengthBand:
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
    pixel_width_km = EARTH_RADIUS_KM * math.radians(abs(east - west)) * math.cos(mid_lat)
    pixel_height_km = EARTH_RADIUS_KM * math.radians(abs(north - south))
    return pixel_width_km * pixel_height_km


def png_chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    )


def write_png_rgba(path: Path, width: int, height: int, rows: list[bytes]) -> None:
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


def build_exterior_zero_mask(strength_rows: list[array], width: int, height: int) -> list[bytearray]:
    if not strength_rows or width <= 0 or height <= 0:
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
        if float(strength_rows[y][x]) > 0.0 or mask_rows[y][x]:
            continue
        mask_rows[y][x] = 1
        queue.append((x, y))
    if not queue:
        for x in range(width):
            for y in (0, height - 1):
                if float(strength_rows[y][x]) <= 0.0 and not mask_rows[y][x]:
                    mask_rows[y][x] = 1
                    queue.append((x, y))
        for y in range(height):
            for x in (0, width - 1):
                if float(strength_rows[y][x]) <= 0.0 and not mask_rows[y][x]:
                    mask_rows[y][x] = 1
                    queue.append((x, y))

    while queue:
        x, y = queue.popleft()
        if x > 0 and not mask_rows[y][x - 1] and float(strength_rows[y][x - 1]) <= 0.0:
            mask_rows[y][x - 1] = 1
            queue.append((x - 1, y))
        if x + 1 < width and not mask_rows[y][x + 1] and float(strength_rows[y][x + 1]) <= 0.0:
            mask_rows[y][x + 1] = 1
            queue.append((x + 1, y))
        if y > 0 and not mask_rows[y - 1][x] and float(strength_rows[y - 1][x]) <= 0.0:
            mask_rows[y - 1][x] = 1
            queue.append((x, y - 1))
        if y + 1 < height and not mask_rows[y + 1][x] and float(strength_rows[y + 1][x]) <= 0.0:
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


def sample_strength(
    strength_rows: list[array],
    exterior_mask_rows: list[bytearray],
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
    if exterior_mask_rows and exterior_mask_rows[src_y][src_x]:
        return None
    return float(strength_rows[src_y][src_x])


def tile_ranges(mercator_bbox: dict[str, float], zoom: int) -> tuple[range, range]:
    tiles = 1 << zoom
    min_x = max(0, math.floor(mercator_bbox["min_x"] * tiles))
    max_x = min(tiles - 1, math.floor(mercator_bbox["max_x"] * tiles))
    min_y = max(0, math.floor(mercator_bbox["min_y"] * tiles))
    max_y = min(tiles - 1, math.floor(mercator_bbox["max_y"] * tiles))
    return range(min_x, max_x + 1), range(min_y, max_y + 1)


def write_tiles(
    nation_dir: Path,
    strength_rows: list[array],
    exterior_mask_rows: list[bytearray],
    mercator_bbox: dict[str, float],
    width: int,
    height: int,
    bands: list[StrengthBand],
    min_zoom: int,
    max_zoom: int,
) -> dict[str, Any]:
    tiles_dir = nation_dir / "tiles"
    total_tiles = 0
    for zoom in range(min_zoom, max_zoom + 1):
        x_range, y_range = tile_ranges(mercator_bbox, zoom)
        zoom_tiles = len(x_range) * len(y_range)
        total_tiles += zoom_tiles
        log(f"writing {zoom_tiles} tiles for z{zoom}")
        scale = 1 << zoom
        for tile_x in x_range:
            for tile_y in y_range:
                tile_rows: list[bytes] = []
                y_samples = [(tile_y + ((py + 0.5) / TILE_SIZE)) / scale for py in range(TILE_SIZE)]
                x_samples = [(tile_x + ((px + 0.5) / TILE_SIZE)) / scale for px in range(TILE_SIZE)]
                for sample_y in y_samples:
                    row = bytearray(TILE_SIZE * 4)
                    for pixel_x, sample_x in enumerate(x_samples):
                        value = sample_strength(strength_rows, exterior_mask_rows, mercator_bbox, sample_x, sample_y, width, height)
                        if value is None:
                            continue
                        red, green, blue, alpha = strength_band_for_value(value, bands).color_rgba
                        offset = pixel_x * 4
                        row[offset : offset + 4] = bytes((red, green, blue, alpha))
                    tile_rows.append(bytes(row))
                write_png_rgba(tiles_dir / str(zoom) / str(tile_x) / f"{tile_y}.png", TILE_SIZE, TILE_SIZE, tile_rows)
    return {
        "directory": str(tiles_dir),
        "tile_size": TILE_SIZE,
        "min_zoom": min_zoom,
        "max_zoom": max_zoom,
        "tile_count": total_tiles,
        "template": "tiles/{z}/{x}/{y}.png",
    }


def rasterize_strength(
    rows: list[dict[str, Any]],
    bbox: dict[str, float],
    width: int,
    height: int,
    near_miles: float,
    far_miles: float,
) -> tuple[list[array], dict[str, float]]:
    height, mercator_bbox = projected_dimensions(bbox, width)
    strength_rows = [array("f", [0.0]) * width for _ in range(height)]
    row_lat_rads = []
    col_lon_rads = []
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
    near_km = miles_to_km(near_miles)
    far_km = miles_to_km(far_miles)
    falloff_span = max(0.001, far_km - near_km)

    for index, row in enumerate(rows, start=1):
        if index % 200 == 0 or index == len(rows):
            log(f"rasterizing {index}/{len(rows)} practice points")
        lat = float(row["lat"])
        lon = float(row["lon"])
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
                dx = (col_lon_rads[col_index] - lon_rad) * cos_mid
                distance_km = EARTH_RADIUS_KM * math.sqrt((dx * dx) + (dy * dy))
                if distance_km > far_km:
                    continue
                if distance_km <= near_km:
                    weight = 1.0
                else:
                    weight = (far_km - distance_km) / falloff_span
                target_row[col_index] += weight

    return strength_rows, mercator_bbox


def build_preview_and_summary(
    strength_rows: list[array],
    width: int,
    height: int,
    mercator_bbox: dict[str, float],
    bands: list[StrengthBand],
) -> tuple[list[bytes], dict[str, Any]]:
    band_pixels: Counter[str] = Counter()
    band_sq_km: Counter[str] = Counter()
    max_strength = 0.0
    total_sq_km = 0.0
    positive_sq_km = 0.0
    positive_pixels = 0
    preview_rows: list[bytes] = []
    max_bin = Counter[int]()

    for row_index, source_row in enumerate(strength_rows):
        row_area_sq_km = row_pixel_area_sq_km(row_index, width, height, mercator_bbox)
        total_sq_km += row_area_sq_km * width
        preview = bytearray(width * 4)
        for col_index, value in enumerate(source_row):
            numeric = max(0.0, float(value))
            if numeric > max_strength:
                max_strength = numeric
            band = strength_band_for_value(numeric, bands)
            band_pixels[band.label] += 1
            band_sq_km[band.label] += row_area_sq_km
            if numeric > 0.0:
                positive_pixels += 1
                positive_sq_km += row_area_sq_km
            max_bin[int(numeric)] += 1
            offset = col_index * 4
            preview[offset : offset + 4] = bytes(band.color_rgba)
        preview_rows.append(bytes(preview))

    summary = {
        "max_strength": round(max_strength, 4),
        "positive_pixels": positive_pixels,
        "positive_pixel_ratio": round(positive_pixels / (width * height), 6),
        "total_bbox_sq_km": round(total_sq_km, 3),
        "positive_sq_km": round(positive_sq_km, 3),
        "bands": [
            {
                "label": band.label,
                "minimum": band.minimum,
                "maximum": band.maximum,
                "color": band.color_hex(),
                "pixel_count": int(band_pixels[band.label]),
                "pixel_ratio": round(band_pixels[band.label] / (width * height), 6),
                "approx_sq_km": round(float(band_sq_km[band.label]), 3),
            }
            for band in bands
        ],
        "top_integer_bins": [
            {"strength_floor": value, "pixel_count": count}
            for value, count in sorted(max_bin.items(), key=lambda item: (-item[1], item[0]))[:12]
        ],
    }
    return preview_rows, summary


def write_summary_text(path: Path, nation: NationConfig, row_count: int, width: int, height: int, summary: dict[str, Any]) -> None:
    lines = [
        f"{nation.label} Distance-Strength Terrain Summary",
        "",
        f"Practice points used: {row_count}",
        f"Raster size: {width} x {height}",
        f"Near radius: {nation.near_miles} miles",
        f"Far radius: {nation.far_miles} miles",
        f"Exterior transparent mask: {summary['exterior_mask']['masked_pixels']:,} pixels / {summary['exterior_mask']['approx_sq_km']:,} sq km",
        f"Max cumulative strength: {summary['max_strength']}",
        f"Approx bbox area: {summary['total_bbox_sq_km']:,} sq km",
        f"Approx positive-strength area: {summary['positive_sq_km']:,} sq km",
        f"Positive pixel share: {summary['positive_pixel_ratio']:.2%}",
        "",
        "Band distribution:",
    ]
    for band in summary["bands"]:
        lines.append(
            f"  {band['label']:>7}  pixels={band['pixel_count']:,}  share={band['pixel_ratio']:.2%}  approx_area={band['approx_sq_km']:,} sq km  color={band['color']}"
        )
    lines.extend(["", "Top integer-strength bins:"])
    for item in summary["top_integer_bins"]:
        lines.append(f"  {item['strength_floor']:>3}  pixels={item['pixel_count']:,}")
    lines.extend(
        [
            "",
            "Interpretation: this is not a literal catchment count. Each practice contributes full strength inside the near radius and then tapers to zero at the far radius.",
            "Preview PNGs and XYZ tiles flood-fill the contiguous zero-value exterior from the raster edge and make only that outside area transparent.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def build_nation_distance_strength(
    nation: NationConfig,
    rows: list[dict[str, Any]],
    output_root: Path,
    width: int,
    padding_degrees: float,
    tile_min_zoom: int,
    tile_max_zoom: int,
) -> dict[str, Any]:
    nation_dir = output_root / nation.slug
    nation_dir.mkdir(parents=True, exist_ok=True)
    bbox = nation_bbox(rows, padding_degrees, nation.far_miles)
    height, _mercator_bbox = projected_dimensions(bbox, width)
    strength_rows, mercator_bbox = rasterize_strength(rows, bbox, width, height, nation.near_miles, nation.far_miles)
    preview_rows, summary = build_preview_and_summary(strength_rows, width, height, mercator_bbox, DEFAULT_BANDS)
    exterior_mask_rows = build_exterior_zero_mask(strength_rows, width, height)
    summary["exterior_mask"] = summarize_exterior_mask(exterior_mask_rows, width, height, mercator_bbox)
    preview_rows = apply_exterior_mask_to_preview(preview_rows, exterior_mask_rows)

    preview_png = nation_dir / "distance-strength-bands.png"
    write_png_rgba(preview_png, width, height, preview_rows)
    summary_txt = nation_dir / "summary.txt"
    summary_json = nation_dir / "summary.json"
    metadata_json = nation_dir / "metadata.json"
    write_summary_text(summary_txt, nation, len(rows), width, height, summary)
    tile_manifest = write_tiles(nation_dir, strength_rows, exterior_mask_rows, mercator_bbox, width, height, DEFAULT_BANDS, tile_min_zoom, tile_max_zoom)

    notes = [
        "This layer is built from practice point distance strength, not published catchment polygons.",
        "Each practice contributes full weight inside the near radius and linearly tapers to zero at the far radius.",
        "Preview PNGs and tiles flood-fill the contiguous zero-value exterior from the raster edge and make only that outside area transparent.",
        "Values approximate cumulative accessibility strength, not confirmed registration eligibility.",
    ]
    if nation.nation == "england":
        notes.insert(
            1,
            "England out-of-area uses only locally logged practices flagged as accepting out-of-area registrations and currently accepting new patients.",
        )

    metadata = {
        "nation": nation.slug,
        "overlay_id": nation.slug,
        "overlay_nation": nation.nation,
        "label": nation.label,
        "mode": "distance_strength",
        "practice_count": len(rows),
        "near_miles": nation.near_miles,
        "far_miles": nation.far_miles,
        "bbox": bbox,
        "raster": {
            "width": width,
            "height": height,
            "preview_png": str(preview_png),
        },
        "bands": [
            {
                "label": band.label,
                "minimum": band.minimum,
                "maximum": band.maximum,
                "color": band.color_hex(),
            }
            for band in DEFAULT_BANDS
        ],
        "tile_manifest": tile_manifest,
        "notes": notes,
    }
    summary_payload = {
        **summary,
        "nation": nation.slug,
        "overlay_id": nation.slug,
        "overlay_nation": nation.nation,
        "label": nation.label,
        "mode": "distance_strength",
        "practice_count": len(rows),
        "near_miles": nation.near_miles,
        "far_miles": nation.far_miles,
        "bbox": bbox,
        "raster": metadata["raster"],
        "tile_manifest": tile_manifest,
        "bands": metadata["bands"],
    }
    metadata_json.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    summary_json.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")
    return {
        "nation": nation.slug,
        "slug": nation.slug,
        "overlay_nation": nation.nation,
        "label": nation.label,
        "directory": str(nation_dir),
        "summary_json": str(summary_json),
        "metadata_json": str(metadata_json),
        "preview_png": str(preview_png),
        "practice_count": len(rows),
        "max_strength": summary["max_strength"],
        "width": width,
        "height": height,
    }


def main() -> int:
    args = parse_args()
    requested = {item.strip().lower() for item in args.nations}
    selected_configs = [config for config in NATION_CONFIGS if config.slug in requested]
    if not selected_configs:
        raise RuntimeError(f"No matching nation configs for {sorted(requested)}")

    output_root: Path = args.output_dir
    output_root.mkdir(parents=True, exist_ok=True)

    module = load_build_module()
    rows_by_nation = load_rows_by_nation(module)

    manifest = []
    for nation in selected_configs:
        rows = rows_by_nation.get(nation.nation, [])
        if not rows:
            log(f"skipping {nation.slug}: no coordinate rows")
            continue
        log(f"building {nation.label} from {len(rows)} practice points")
        manifest.append(
            build_nation_distance_strength(
                nation,
                rows,
                output_root,
                max(64, args.width),
                args.padding_degrees,
                args.tile_min_zoom,
                args.tile_max_zoom,
            )
        )

    manifest_path = output_root / "manifest.json"
    manifest_path.write_text(json.dumps({"nations": manifest}, indent=2), encoding="utf-8")
    print(json.dumps({"manifest_json": str(manifest_path), "nations": manifest}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
