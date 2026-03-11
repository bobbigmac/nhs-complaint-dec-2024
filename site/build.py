#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable


SITE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SITE_DIR.parent
DATASET_OUTPUT_DIR = REPO_ROOT / "datasets" / "output"
REPORT_GLOB = "gtd-greater-manchester-gp-practice-reviews-*"
DEFAULT_OUT_DIR = SITE_DIR / "dist"


def find_latest_report_dir() -> Path:
    candidates = sorted(
        [path for path in DATASET_OUTPUT_DIR.glob(REPORT_GLOB) if path.is_dir()],
        key=lambda path: path.name,
    )
    if not candidates:
        raise FileNotFoundError(f"No report directories found under {DATASET_OUTPUT_DIR}")
    return candidates[-1]


def load_summary(report_dir: Path) -> dict[str, object]:
    summary_path = report_dir / "summary.json"
    return json.loads(summary_path.read_text(encoding="utf-8"))


def render_inline_markdown(text: str) -> str:
    escaped = html.escape(text, quote=False)
    escaped = re.sub(
        r"`([^`]+)`",
        lambda match: f"<code>{match.group(1)}</code>",
        escaped,
    )
    escaped = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda match: f'<a href="{html.escape(match.group(2), quote=True)}">{match.group(1)}</a>',
        escaped,
    )
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)
    return escaped


def markdown_to_html(markdown_text: str) -> str:
    blocks: list[str] = []
    paragraph_lines: list[str] = []
    list_items: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph_lines
        if not paragraph_lines:
            return
        text = " ".join(line.strip() for line in paragraph_lines)
        blocks.append(f"<p>{render_inline_markdown(text)}</p>")
        paragraph_lines = []

    def flush_list() -> None:
        nonlocal list_items
        if not list_items:
            return
        items = "".join(f"<li>{render_inline_markdown(item)}</li>" for item in list_items)
        blocks.append(f"<ul>{items}</ul>")
        list_items = []

    for raw_line in markdown_text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            flush_paragraph()
            flush_list()
            continue

        if stripped == "---":
            flush_paragraph()
            flush_list()
            blocks.append("<hr>")
            continue

        heading_match = re.match(r"^(#{1,3})\s+(.*)$", stripped)
        if heading_match:
            flush_paragraph()
            flush_list()
            level = len(heading_match.group(1))
            blocks.append(f"<h{level}>{render_inline_markdown(heading_match.group(2))}</h{level}>")
            continue

        if stripped.startswith("- "):
            flush_paragraph()
            list_items.append(stripped[2:].strip())
            continue

        if stripped.startswith("> "):
            flush_paragraph()
            flush_list()
            blocks.append(f"<blockquote><p>{render_inline_markdown(stripped[2:].strip())}</p></blockquote>")
            continue

        paragraph_lines.append(stripped)

    flush_paragraph()
    flush_list()
    return "\n".join(blocks)


def format_number(value: object) -> str:
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, float):
        return f"{value:,.1f}"
    return str(value)


def build_stat_cards(summary: dict[str, object]) -> str:
    cards = [
        ("Practices in scope", summary.get("row_count", "?")),
        ("GTD-managed practices", summary.get("gtd_managed_count", "?")),
        ("Google-scored practices", summary.get("google_review_coverage_count", "?")),
        ("Takeover dates documented", summary.get("gtd_takeover_date_count", "?")),
        ("Registered-patient matches", summary.get("registered_patient_count_coverage", "?")),
        ("Postcode areas covered", summary.get("postcode_area_count", "?")),
    ]
    return "\n".join(
        f"""
        <article class="stat-card">
          <span class="stat-value">{format_number(value)}</span>
          <span class="stat-label">{html.escape(label)}</span>
        </article>
        """.strip()
        for label, value in cards
    )


def build_evidence_cards(report_dir_name: str) -> str:
    links = [
        ("Interactive map", "Explore the latest map, comparison panels, takeover markers and practice popups.", "map/map.html"),
        ("Summary JSON", "Quick machine-readable snapshot of scope, coverage and counts.", "map/summary.json"),
        ("Practice CSV", "Flattened dataset for spreadsheet work or offline review.", "map/gtd_greater_manchester_gp_practices.csv"),
        ("Practice JSON", "Structured dataset for scripting, filtering and reuse.", "map/gtd_greater_manchester_gp_practices.json"),
        ("Download bundle", f"Zip archive of the full {report_dir_name} report bundle.", f"downloads/{report_dir_name}.zip"),
    ]
    return "\n".join(
        f"""
        <article class="evidence-card">
          <h3><a href="{html.escape(href, quote=True)}">{html.escape(title)}</a></h3>
          <p>{html.escape(description)}</p>
        </article>
        """.strip()
        for title, description, href in links
    )


def load_template() -> str:
    return (SITE_DIR / "templates" / "base.html").read_text(encoding="utf-8")


def replace_tokens(template: str, values: dict[str, str]) -> str:
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def zip_directory(source_dir: Path, destination_zip: Path) -> None:
    destination_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source_dir.rglob("*")):
            if path.is_dir():
                continue
            archive.write(path, arcname=f"{source_dir.name}/{path.relative_to(source_dir)}")


def copy_static_assets(out_dir: Path) -> None:
    assets_src = SITE_DIR / "assets"
    assets_dst = out_dir / "assets"
    if assets_dst.exists():
        shutil.rmtree(assets_dst)
    shutil.copytree(assets_src, assets_dst)


def write_page(out_dir: Path, report_dir: Path, summary: dict[str, object]) -> None:
    template = load_template()
    report_dir_name = report_dir.name
    updated_value = summary.get("generated_date") or datetime.now(UTC).date().isoformat()
    home_markdown = (SITE_DIR / "content" / "home.md").read_text(encoding="utf-8")
    body_html = markdown_to_html(home_markdown)
    page_html = replace_tokens(
        template,
        {
            "PAGE_TITLE": "NHS Access Evidence and Recovery",
            "UPDATED_DATE": html.escape(str(updated_value)),
            "REPORT_NAME": html.escape(report_dir_name),
            "MAP_HREF": "map/map.html",
            "DOWNLOAD_HREF": f"downloads/{html.escape(report_dir_name)}.zip",
            "STAT_CARDS": build_stat_cards(summary),
            "BODY_HTML": body_html,
            "EVIDENCE_CARDS": build_evidence_cards(report_dir_name),
        },
    )
    (out_dir / "index.html").write_text(page_html, encoding="utf-8")


def write_redirect_file(out_dir: Path, target: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="0; url={html.escape(target, quote=True)}">
  <title>Redirecting…</title>
</head>
<body>
  <p><a href="{html.escape(target, quote=True)}">Continue</a></p>
</body>
</html>
""",
        encoding="utf-8",
    )


def build_site(out_dir: Path) -> Path:
    report_dir = find_latest_report_dir()
    summary = load_summary(report_dir)

    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    copy_static_assets(out_dir)
    write_page(out_dir, report_dir, summary)

    map_out_dir = out_dir / "map"
    shutil.copytree(report_dir, map_out_dir)

    downloads_dir = out_dir / "downloads"
    zip_directory(report_dir, downloads_dir / f"{report_dir.name}.zip")

    (out_dir / ".nojekyll").write_text("", encoding="utf-8")
    write_redirect_file(out_dir / "latest-map", "../map/map.html")
    return out_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the project landing page and package the latest map bundle.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT_DIR, help="Output directory for the generated static site.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    build_site(args.out)
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
