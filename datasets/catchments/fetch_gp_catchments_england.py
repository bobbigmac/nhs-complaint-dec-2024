#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Iterable
from urllib.parse import urlencode, urljoin

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_OUTDIR = BASE_DIR / ".cache" / "gp-catchments-england"

OFFICIAL_PAGE = "https://gp-catchments-data-download-nhsgisscw.hub.arcgis.com/"
ARCGIS_ITEM_JSON = "https://www.arcgis.com/sharing/rest/content/items/52edc9271d6d41d182a7f5524385f490?f=json"
HARDCODED_SERVICE_URL = "https://services3.arcgis.com/Bb8lfThdhugyc4G3/arcgis/rest/services/GP_catchment_areas_(England)/FeatureServer"
USER_AGENT = "nhs-gp-catchments-england-fetch/1.0"
TIMEOUT = (30, 300)


def log(*args: object) -> None:
    print(*args, file=sys.stderr)


def make_curl_base() -> list[str]:
    return [
        "curl",
        "-L",
        "--silent",
        "--show-error",
        "--fail",
        "--connect-timeout",
        str(TIMEOUT[0]),
        "--max-time",
        str(TIMEOUT[1]),
        "-A",
        USER_AGENT,
    ]


def http_get_bytes(url: str, params: dict[str, str] | None = None) -> bytes:
    request_url = url
    if params:
        request_url = f"{url}?{urlencode(params)}"
    command = make_curl_base() + [request_url]
    result = subprocess.run(command, capture_output=True, check=True)
    return result.stdout


def http_get_text(url: str, params: dict[str, str] | None = None) -> str:
    return http_get_bytes(url, params).decode("utf-8", errors="replace")


def http_get_json(url: str, params: dict[str, str] | None = None) -> dict:
    return json.loads(http_get_text(url, params))


def safe_json_load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(obj, handle, ensure_ascii=False, indent=2)


def reset_dir(path: Path) -> None:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        return
    for child in sorted(path.rglob("*"), reverse=True):
        if child.is_file() or child.is_symlink():
            child.unlink()
        elif child.is_dir():
            try:
                child.rmdir()
            except OSError:
                pass
    path.mkdir(parents=True, exist_ok=True)


def discover_zip_urls(html: str, base_url: str) -> list[str]:
    text = html.replace("\\/", "/").replace("\\u002F", "/")
    candidates: list[str] = []
    patterns = [
        r'https?://[^"\']+?\.zip(?:\?[^"\']*)?',
        r'["\']([^"\']+?\.zip(?:\?[^"\']*)?)["\']',
        r'"downloadUrl"\s*:\s*"([^"]+?\.zip[^"]*)"',
        r'"url"\s*:\s*"([^"]+?\.zip[^"]*)"',
    ]

    for pattern in patterns:
        for match in re.findall(pattern, text, flags=re.IGNORECASE):
            url = match.strip().strip('"').strip("'")
            if not url:
                continue
            if url.startswith("/"):
                url = urljoin(base_url, url)
            elif not url.startswith(("http://", "https://")):
                url = urljoin(base_url, url)
            candidates.append(url)

    ranked: list[tuple[int, str]] = []
    seen: set[str] = set()
    for url in candidates:
        if url in seen:
            continue
        seen.add(url)
        lower = url.lower()
        score = 0
        if "gp" in lower:
            score += 2
        if "catch" in lower:
            score += 2
        if "nhs" in lower:
            score += 2
        if "arcgis" in lower:
            score += 1
        ranked.append((score, url))

    ranked.sort(key=lambda item: (-item[0], item[1]))
    return [url for _, url in ranked]


def download_file(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    if tmp.exists():
        tmp.unlink()

    command = make_curl_base() + ["-o", str(tmp), url]
    subprocess.run(command, check=True)

    tmp.replace(dest)
    return dest


def fetch_official_zip(outdir: Path) -> tuple[Path, Path]:
    log("trying official NHS catchments download page")
    html = http_get_text(OFFICIAL_PAGE)

    zip_urls = discover_zip_urls(html, OFFICIAL_PAGE)
    if not zip_urls:
        raise RuntimeError("could not find any .zip URL on the official page")

    zip_path = outdir / "official" / "gp_catchments_england_official.zip"
    extract_dir = outdir / "official" / "extracted"

    for url in zip_urls:
        try:
            log(f"trying zip url: {url}")
            download_file(url, zip_path)
            if not zipfile.is_zipfile(zip_path):
                zip_path.unlink(missing_ok=True)
                continue

            reset_dir(extract_dir)
            with zipfile.ZipFile(zip_path) as archive:
                archive.extractall(extract_dir)

            geojson_files = list(extract_dir.rglob("*.geojson"))
            if not geojson_files:
                raise RuntimeError("zip downloaded but no .geojson files were found after extraction")

            return zip_path, extract_dir
        except Exception as exc:
            log(f"zip url failed: {url} ({exc})")
            zip_path.unlink(missing_ok=True)

    raise RuntimeError("failed to download or validate any zip from the official page")


def get_feature_service_url() -> str:
    data = http_get_json(ARCGIS_ITEM_JSON)
    return data.get("url") or HARDCODED_SERVICE_URL


def query_json(url: str, params: dict[str, str]) -> dict:
    return http_get_json(url, params)


def fetch_feature_service_geojson(outdir: Path) -> Path:
    service_url = get_feature_service_url().rstrip("/")
    layer_query_url = f"{service_url}/0/query"

    count = query_json(
        layer_query_url,
        {"where": "1=1", "returnCountOnly": "true", "f": "json"},
    )["count"]
    log(f"feature service row count: {count}")

    page_size = 2000
    offset = 0
    all_features: list[dict] = []

    while True:
        data = query_json(
            layer_query_url,
            {
                "where": "1=1",
                "outFields": "*",
                "returnGeometry": "true",
                "outSR": "4326",
                "f": "geojson",
                "orderByFields": "FID ASC",
                "resultOffset": str(offset),
                "resultRecordCount": str(page_size),
            },
        )

        features = data.get("features", [])
        if not features:
            break
        all_features.extend(features)
        offset += len(features)
        log(f"downloaded {len(all_features)}/{count} features")
        if len(features) < page_size:
            break

    if not all_features:
        raise RuntimeError("feature service returned no features")

    out_path = outdir / "fallback_feature_service" / "gp_catchments_england.geojson"
    write_json(out_path, {"type": "FeatureCollection", "features": all_features})
    return out_path


def iter_geojson_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*.geojson")):
        if path.is_file():
            yield path


def feature_list_from_geojson(obj: dict) -> list[dict]:
    kind = obj.get("type")
    if kind == "FeatureCollection":
        return obj.get("features", [])
    if kind == "Feature":
        return [obj]
    raise ValueError(f"unsupported GeoJSON top-level type: {kind!r}")


def practice_code_from_name(name: object) -> str:
    text = str(name or "").strip()
    match = re.match(r"^([A-Z0-9]{5,10})\s*-\s*", text)
    return match.group(1) if match else ""


def practice_name_from_name(name: object) -> str:
    text = str(name or "").strip()
    match = re.match(r"^[A-Z0-9]{5,10}\s*-\s*(.+)$", text)
    return match.group(1).strip() if match else text


def practice_code_for_feature(feature: dict) -> str:
    props = feature.get("properties") or {}
    direct_code = str(props.get("PracticeCd") or props.get("practice_code") or "").strip()
    if direct_code:
        return direct_code
    name_code = practice_code_from_name(props.get("Name"))
    if name_code:
        return name_code
    return Path(props.get("_source_file", "UNKNOWN")).stem


def merge_geojson_files(geojson_files: Iterable[Path], out_path: Path) -> tuple[Path, list[dict]]:
    merged: list[dict] = []
    for path in geojson_files:
        obj = safe_json_load(path)
        features = feature_list_from_geojson(obj)
        for feature in features:
            props = feature.setdefault("properties", {})
            props.setdefault("_source_file", path.name)
            props.setdefault("_source_path", str(path))
            merged.append(feature)

    write_json(out_path, {"type": "FeatureCollection", "features": merged})
    return out_path, merged


def split_by_practice(features: list[dict], outdir: Path) -> None:
    grouped: dict[str, list[dict]] = {}
    for feature in features:
        code = practice_code_for_feature(feature)
        grouped.setdefault(code, []).append(feature)

    split_dir = outdir / "by_practice"
    split_dir.mkdir(parents=True, exist_ok=True)
    for code, feats in sorted(grouped.items()):
        write_json(split_dir / f"{code}.geojson", {"type": "FeatureCollection", "features": feats})


def write_manifest(features: list[dict], out_csv: Path) -> None:
    rows: dict[str, dict[str, object]] = {}
    for feature in features:
        props = feature.get("properties") or {}
        code = practice_code_for_feature(feature)
        name = (
            props.get("PracticeNm")
            or props.get("practice_name")
            or practice_name_from_name(props.get("Name"))
            or props.get("Name")
            or ""
        )
        area_km2 = props.get("Area_Km2")
        row = rows.setdefault(
            code,
            {
                "practice_code": code,
                "practice_name": name,
                "feature_count": 0,
                "area_km2_sum": 0.0,
            },
        )
        row["feature_count"] = int(row["feature_count"]) + 1
        if name and not row["practice_name"]:
            row["practice_name"] = name
        try:
            if area_km2 not in (None, ""):
                row["area_km2_sum"] = float(row["area_km2_sum"]) + float(area_km2)
        except (TypeError, ValueError):
            pass

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["practice_code", "practice_name", "feature_count", "area_km2_sum"],
        )
        writer.writeheader()
        for row in sorted(rows.values(), key=lambda item: str(item["practice_code"])):
            writer.writerow(row)


def write_source_metadata(outdir: Path, payload: dict) -> None:
    write_json(outdir / "source.json", payload)


def fetch_auto(outdir: Path) -> tuple[str, Path, Path | None]:
    try:
        zip_path, extract_dir = fetch_official_zip(outdir)
        merged_path, features = merge_geojson_files(
            iter_geojson_files(extract_dir),
            outdir / "merged" / "gp_catchments_england_merged.geojson",
        )
        split_by_practice(features, outdir)
        write_manifest(features, outdir / "merged" / "manifest.csv")
        write_source_metadata(
            outdir,
            {
                "mode_used": "official",
                "official_page": OFFICIAL_PAGE,
                "zip_path": str(zip_path),
                "extract_dir": str(extract_dir),
                "merged_geojson": str(merged_path),
            },
        )
        return "official", merged_path, zip_path
    except Exception as exc:
        log(f"official download failed, falling back to feature service: {exc}")

    merged_path = fetch_feature_service_geojson(outdir)
    merged_obj = safe_json_load(merged_path)
    features = feature_list_from_geojson(merged_obj)
    split_by_practice(features, outdir)
    write_manifest(features, outdir / "merged" / "manifest.csv")
    write_source_metadata(
        outdir,
        {
            "mode_used": "feature-service",
            "item_json": ARCGIS_ITEM_JSON,
            "service_url_fallback": HARDCODED_SERVICE_URL,
            "merged_geojson": str(merged_path),
        },
    )
    return "feature-service", merged_path, None


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch England GP catchment polygons into a local cache.")
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR, help="Local cache/output directory")
    parser.add_argument(
        "--mode",
        choices=["auto", "official", "feature-service"],
        default="auto",
        help="Source mode to use",
    )
    args = parser.parse_args()

    outdir = args.outdir
    outdir.mkdir(parents=True, exist_ok=True)
    if args.mode == "auto":
        mode_used, merged_path, zip_path = fetch_auto(outdir)
        print(
            json.dumps(
                {
                    "mode_used": mode_used,
                    "merged_geojson": str(merged_path),
                    "zip_path": str(zip_path) if zip_path else None,
                    "manifest_csv": str(outdir / "merged" / "manifest.csv"),
                    "by_practice_dir": str(outdir / "by_practice"),
                    "source_metadata": str(outdir / "source.json"),
                },
                indent=2,
            )
        )
        return 0

    if args.mode == "official":
        zip_path, extract_dir = fetch_official_zip(outdir)
        merged_path, features = merge_geojson_files(
            iter_geojson_files(extract_dir),
            outdir / "merged" / "gp_catchments_england_merged.geojson",
        )
        split_by_practice(features, outdir)
        write_manifest(features, outdir / "merged" / "manifest.csv")
        write_source_metadata(
            outdir,
            {
                "mode_used": "official",
                "official_page": OFFICIAL_PAGE,
                "zip_path": str(zip_path),
                "extract_dir": str(extract_dir),
                "merged_geojson": str(merged_path),
            },
        )
        print(
            json.dumps(
                {
                    "mode_used": "official",
                    "zip_path": str(zip_path),
                    "extract_dir": str(extract_dir),
                    "merged_geojson": str(merged_path),
                    "manifest_csv": str(outdir / "merged" / "manifest.csv"),
                    "by_practice_dir": str(outdir / "by_practice"),
                    "source_metadata": str(outdir / "source.json"),
                },
                indent=2,
            )
        )
        return 0

    merged_path = fetch_feature_service_geojson(outdir)
    merged_obj = safe_json_load(merged_path)
    features = feature_list_from_geojson(merged_obj)
    split_by_practice(features, outdir)
    write_manifest(features, outdir / "merged" / "manifest.csv")
    write_source_metadata(
        outdir,
        {
            "mode_used": "feature-service",
            "item_json": ARCGIS_ITEM_JSON,
            "service_url_fallback": HARDCODED_SERVICE_URL,
            "merged_geojson": str(merged_path),
        },
    )
    print(
        json.dumps(
            {
                "mode_used": "feature-service",
                "merged_geojson": str(merged_path),
                "manifest_csv": str(outdir / "merged" / "manifest.csv"),
                "by_practice_dir": str(outdir / "by_practice"),
                "source_metadata": str(outdir / "source.json"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
