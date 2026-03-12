#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import posixpath
import re
import shutil
import zipfile
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Callable, Iterable
from urllib.parse import quote


SITE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SITE_DIR.parent
DATASET_OUTPUT_DIR = REPO_ROOT / "datasets" / "output"
CONTEXT_DIR = REPO_ROOT / "datasets" / "context"
REPORT_GLOB = "gtd-greater-manchester-gp-practice-reviews-*"
DEFAULT_OUT_DIR = SITE_DIR / "dist"
FILES_DIR_NAME = "files"
TOOLS_DIR_NAME = "tools"
TOOL_VIEWER_PATH = f"{TOOLS_DIR_NAME}/markdown-print-viewer.html"
TOOL_VIEWER_SOURCE = SITE_DIR / "tools" / "markdown-print-viewer.html"
CHRONOLOGY_SOURCE = "datasets/context/GTD_CHRONOLOGY.md"
OPERATING_ENVIRONMENT_SOURCE = "datasets/context/OPERATING_ENVIRONMENT.md"
INQUIRY_LINK_DUMP_SOURCE = "datasets/context/GTD_INQUIRY_LINKS.txt"
ORG_NAVIGATOR_SOURCE = "datasets/management_companies/output/company_watchlist_report.md"
ORG_METHOD_SOURCE = "datasets/management_companies/management-companies.md"
ORG_WATCHLIST_SOURCE = "datasets/management_companies/watchlist.json"


ISSUE_SECTIONS: list[dict[str, object]] = [
    {
        "number": "Issue 1",
        "title": "Digital front door and office-hours gating",
        "summary": (
            "Appointment access is still shaped by a rigid digital front door: office-hours gating, "
            "website closures and routes that are much easier for the system than for the patient."
        ),
        "work": [
            "Tracked the local blockers in meeting packs instead of treating them as one-off bad experiences.",
            "Built an external evidence pack showing that website shutoffs, capped forms and digital exclusion are wider NHS access problems.",
            "Kept printable packs ready for meetings so the ask stays focused on always-available intake and a real non-digital fallback.",
        ],
        "resources": [
            {
                "title": "Meeting 4 goals",
                "description": "The clearest current statement of the local access ask, the partial progress, and the blockers that remain.",
                "files": [
                    {"label": "Markdown", "source": "meetings-notes/2026-01-04-meeting4/meeting4-goals.md"},
                    {"label": "PDF printoff", "source": "meetings-notes/2026-01-04-meeting4/printoffs/New Bank Health Centre – PPG Meeting 4 Goals.pdf"},
                ],
            },
            {
                "title": "Wider GP access evidence pack",
                "description": "Grouped evidence on website shutoffs, phone bottlenecks and digital barriers from outside New Bank.",
                "files": [
                    {"label": "Markdown", "source": "meetings-notes/2026-01-04-meeting4/GP Access Evidence - Websites triage and digital barriers.md"},
                ],
            },
            {
                "title": "Nov 2025 printable access pack",
                "description": "A meeting-ready PDF pack covering website failures, out-of-hours closure and minimum fixes.",
                "files": [
                    {"label": "PDF pack", "source": "meetings-notes/2025-11-26-meeting3/send-to-gtd-team-pre-nov26/GP Access Issues - Evidence Pack - 26 Nov 2025 Bob Davies.pdf"},
                ],
            },
        ],
    },
    {
        "number": "Issue 2",
        "title": "Restart loops and continuity loss",
        "summary": (
            "A missed call, a closed request or a partial follow-up can dump the patient back at the start. "
            "That turns access friction into delay, churn and lost continuity."
        ),
        "work": [
            "Logged a direct patient timeline showing how unscheduled calls and incomplete follow-up create repeated failure points.",
            "Framed the problem as hidden exclusion and demand loss, not just inconvenience.",
            "Kept early and later complaint documents side by side so it is clear what changed and what did not.",
        ],
        "resources": [
            {
                "title": "Patient experience timeline",
                "description": "A first-person account of repeated failed attempts, mandatory calls and weak follow-up after tests.",
                "files": [
                    {"label": "Markdown", "source": "My-new-bank-experience.md"},
                ],
            },
            {
                "title": "Exclusion questions",
                "description": "Checks and metrics for spotting the patients who are lost before they ever show up in the usual data.",
                "files": [
                    {"label": "Markdown", "source": "Exclusion-questions.md"},
                ],
            },
            {
                "title": "Original complaint",
                "description": "The baseline complaint document from December 2024, updated as the problem continued.",
                "files": [
                    {"label": "Markdown", "source": "ORIGINAL_COMPLAINT.md"},
                ],
            },
        ],
    },
    {
        "number": "Issue 3",
        "title": "Reception pressure, patient blame and review signals",
        "summary": (
            "Review patterns point to a front door that can feel rude, dismissive or brittle under pressure. "
            "The project treats that as a workflow and management signal, not just a tone problem."
        ),
        "work": [
            "Collected and grouped review extracts from New Bank rather than relying on vague anecdotes.",
            "Wrote a longer note on patient blame, friction-as-rationing and why missed steps should not be treated as moral failure.",
            "Drafted practical guidance for responding to reviews in a way that supports learning instead of defensiveness.",
        ],
        "resources": [
            {
                "title": "Patient blame note",
                "description": "Long-form framing on access friction, patient blame and why the current model sheds the least-resourced patients first.",
                "files": [
                    {"label": "Markdown", "source": "meetings-notes/2026-01-04-meeting4/PatientBlaming-README.md"},
                ],
            },
            {
                "title": "Review extracts",
                "description": "A working markdown extract of appointment and reception-related Google review themes.",
                "files": [
                    {"label": "Markdown", "source": "reviews/parsed-reviews-og-parsed-2yrs.md"},
                ],
            },
            {
                "title": "PATCHS review printoff",
                "description": "Printable PDF summary of low-star PATCHS reviews, useful where the workflow problem is broader than one surgery.",
                "files": [
                    {"label": "PDF printoff", "source": "reviews/PATCHS/output reports/PATCHS 1-2-3 Star Reviews with Summary Panel Landscape.pdf"},
                ],
            },
            {
                "title": "Reviews management guide",
                "description": "A practical note on claiming the Google listing and turning review replies into useful operational work.",
                "files": [
                    {"label": "Markdown", "source": "meetings-notes/2026-01-04-meeting4/reviews-management.md"},
                ],
            },
        ],
    },
    {
        "number": "Issue 4",
        "title": "Benchmarking, survey gaps and portfolio pattern",
        "summary": (
            "Single complaints are easy to dismiss. The project compares New Bank with survey results, nearby practices "
            "and GTD's wider footprint to show the pattern more honestly."
        ),
        "work": [
            "Broke down GP Patient Survey gateway questions and highlighted where the survey likely misses the people who gave up.",
            "Built quick comparison material for meeting use, including workload context, local comparators and GTD portfolio signals.",
            "Published a Greater Manchester comparison map so review scores, survey data and takeover context can be read together.",
        ],
        "resources": [
            {
                "title": "Patient survey breakdown",
                "description": "A focused reading of the New Bank survey results, especially the gateway failures at the point of contact.",
                "files": [
                    {"label": "Markdown", "source": "patient survey breakdown/PatientSurveyBreakdown.md"},
                ],
            },
            {
                "title": "Benchmarks summary",
                "description": "A short reference sheet on practice size, workload, access pressures and GTD comparison points.",
                "files": [
                    {"label": "Markdown", "source": "meetings-notes/2025-09-10-meeting2/benchmarks-summary-sept-10.md"},
                    {"label": "PDF printoff", "source": "meetings-notes/2025-09-10-meeting2/nbhc-ppg_meeting-sept-10_benchmarks-summary-bobdavies.pdf"},
                ],
            },
            {
                "title": "Google vs patient survey gap",
                "description": "The portfolio-level PDF showing how public review signals and survey results diverge across Greater Manchester.",
                "files": [
                    {"label": "PDF analysis", "source": "google-vs-patient-survey/GTD Greater Manchester GP Practice Experience - Google vs Patient Survey Gap.pdf"},
                ],
            },
        ],
    },
    {
        "number": "Issue 5",
        "title": "Governance, complaint routes and change tracking",
        "summary": (
            "Some of the work is evidence-gathering, but some of it is about making sure there is a usable route for "
            "change, scrutiny and escalation when the local process stalls."
        ),
        "work": [
            "Reviewed the PPG terms as an access problem in their own right, not just an admin detail.",
            "Mapped escalation routes beyond GTD for access and digital exclusion issues.",
            "Maintained a repo-level overview so meeting packs, printouts and timelines stay linked together instead of drifting apart.",
        ],
        "resources": [
            {
                "title": "PPG terms review",
                "description": "Review of the draft PPG terms and why a harder front door can make patient participation weaker, not stronger.",
                "files": [
                    {"label": "Markdown", "source": "PPG-terms-review/PPG-terms-review.md"},
                    {"label": "PDF printoff", "source": "PPG-terms-review/PPG Terms review - Bob Davies - 2026-feb-10.pdf"},
                ],
            },
            {
                "title": "Escalation ladder",
                "description": "Practical routes beyond the practice for access barriers, digital exclusion and contract-management pressure.",
                "files": [
                    {"label": "Markdown", "source": "ESCALATION.md"},
                ],
            },
            {
                "title": "Project overview",
                "description": "A repo map and chronology showing how the evidence packs, meeting notes and tools fit together.",
                "files": [
                    {"label": "Markdown", "source": "OVERVIEW.md"},
                ],
            },
        ],
    },
]

REFERENCE_DOCS: list[dict[str, object]] = [
    {
        "title": "README",
        "description": "The wider repo overview and the longer list of packs, notes and supporting material behind this homepage.",
        "files": [
            {"label": "Markdown", "source": "README.md"},
        ],
    },
    {
        "title": "Objectives",
        "description": "The short statement of aims, success criteria and the two-track strategy behind the project.",
        "files": [
            {"label": "Markdown", "source": "OBJECTIVES.md"},
        ],
    },
]


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


def format_stat_value(value: object, approximate: bool = False) -> str:
    formatted = format_number(value)
    return f"~{formatted}" if approximate and formatted != "?" else formatted


def build_stat_cards(summary: dict[str, object]) -> str:
    cards = [
        ("Practices in scope", summary.get("row_count", "?"), False),
        ("GTD-managed practices", summary.get("gtd_managed_count", "?"), False),
        ("Google-scored practices", summary.get("google_review_coverage_count", "?"), False),
        ("Patients in scope", summary.get("registered_patient_count_total_in_scope", "?"), True),
        ("Patients with GTD", summary.get("registered_patient_count_total_gtd", "?"), True),
        ("Postcode areas covered", summary.get("postcode_area_count", "?"), False),
    ]
    return "\n".join(
        f"""
        <article class="stat-card">
          <span class="stat-value">{format_stat_value(value, approximate)}</span>
          <span class="stat-label">{html.escape(label)}</span>
        </article>
        """.strip()
        for label, value, approximate in cards
    )


def href_for_site_path(site_path: str) -> str:
    return quote(site_path, safe="/")


def markdown_print_href(site_path: str) -> str:
    return f"{TOOL_VIEWER_PATH}?source={quote('../' + site_path, safe='/')}"


def collect_published_sources() -> list[Path]:
    sources: dict[str, Path] = {}
    for section in ISSUE_SECTIONS:
        for resource in section["resources"]:
            for file_meta in resource["files"]:
                source = REPO_ROOT / str(file_meta["source"])
                sources[str(source)] = source
    for resource in REFERENCE_DOCS:
        for file_meta in resource["files"]:
            source = REPO_ROOT / str(file_meta["source"])
            sources[str(source)] = source
    return sorted(sources.values(), key=lambda path: path.as_posix())


def publish_supporting_files(out_dir: Path) -> dict[str, str]:
    published: dict[str, str] = {}
    for source in collect_published_sources():
        if not source.exists():
            raise FileNotFoundError(f"Supporting file not found: {source}")
        relative = source.relative_to(REPO_ROOT)
        site_path = f"{FILES_DIR_NAME}/{relative.as_posix()}"
        destination = out_dir / site_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        published[relative.as_posix()] = site_path

    tool_destination = out_dir / TOOL_VIEWER_PATH
    tool_destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(TOOL_VIEWER_SOURCE, tool_destination)
    return published


def build_link_pills(links: Iterable[tuple[str, str, str]]) -> str:
    return "".join(
        f'<a class="link-pill link-pill-{html.escape(variant)}" href="{html.escape(href, quote=True)}">{html.escape(label)}</a>'
        for label, href, variant in links
    )


def build_document_cards(resources: Iterable[dict[str, object]], published_files: dict[str, str]) -> str:
    cards: list[str] = []
    for resource in resources:
        links: list[tuple[str, str, str]] = []
        for file_meta in resource["files"]:
            source_key = str(file_meta["source"])
            site_path = published_files[source_key]
            links.append((str(file_meta["label"]), href_for_site_path(site_path), "primary"))
            if site_path.endswith(".md"):
                links.append(("Print view", markdown_print_href(site_path), "secondary"))
        cards.append(
            f"""
            <article class="doc-card">
              <h5>{html.escape(str(resource["title"]))}</h5>
              <p>{html.escape(str(resource["description"]))}</p>
              <div class="link-row">
                {build_link_pills(links)}
              </div>
            </article>
            """.strip()
        )
    return "\n".join(cards)


def build_issue_panels(published_files: dict[str, str]) -> str:
    panels: list[str] = []
    for section in ISSUE_SECTIONS:
        work_items = "".join(f"<li>{html.escape(str(item))}</li>" for item in section["work"])
        resources_html = build_document_cards(section["resources"], published_files)
        resource_count = len(section["resources"])
        resource_label = "document" if resource_count == 1 else "documents"
        panels.append(
            f"""
            <article class="issue-panel">
              <div class="issue-header">
                <div class="issue-topline">
                  <p class="issue-kicker">{html.escape(str(section["number"]))}</p>
                  <p class="issue-meta">{resource_count} supporting {resource_label}</p>
                </div>
                <h3>{html.escape(str(section["title"]))}</h3>
                <p class="issue-summary">{html.escape(str(section["summary"]))}</p>
              </div>
              <div class="issue-body">
                <section class="issue-block issue-work-block" aria-label="Current work">
                  <ul class="issue-work">
                    {work_items}
                  </ul>
                </section>
                <section class="issue-block issue-resources-block" aria-label="Best supporting documents">
                  <div class="resource-stack">
                    {resources_html}
                  </div>
                </section>
              </div>
            </article>
            """.strip()
        )
    return "\n".join(panels)


def build_reference_cards(published_files: dict[str, str]) -> str:
    return build_document_cards(REFERENCE_DOCS, published_files)


def build_action_cards(report_dir_name: str) -> str:
    cards = [
        {
            "title": "Interactive map",
            "description": "Open the latest Greater Manchester comparison map with review, survey and takeover context.",
            "links": [("Open map", "map/map.html", "primary")],
        },
        {
            "title": "Map notes",
            "description": "Read the generated README for the current map if you want the data notes before opening it.",
            "links": [
                ("Markdown", "map/README.md", "primary"),
                ("Print view", markdown_print_href("map/README.md"), "secondary"),
            ],
        },
    ]
    return "\n".join(
        f"""
        <article class="action-card">
          <h3>{html.escape(str(card["title"]))}</h3>
          <p>{html.escape(str(card["description"]))}</p>
          <div class="link-row">
            {build_link_pills((label, href, variant) for label, href, variant in card["links"])}
          </div>
        </article>
        """.strip()
        for card in cards
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
    published_files = publish_supporting_files(out_dir)
    page_html = replace_tokens(
        template,
        {
            "PAGE_TITLE": "New Bank Access Evidence",
            "UPDATED_DATE": html.escape(str(updated_value)),
            "REPORT_NAME": html.escape(report_dir_name),
            "MAP_HREF": "map/map.html",
            "REPO_HREF": "https://github.com/bobbigmac/nhs-complaint-dec-2024",
            "STAT_CARDS": build_stat_cards(summary),
            "ACTION_CARDS": build_action_cards(report_dir_name),
            "REFERENCE_CARDS": build_reference_cards(published_files),
            "ISSUE_PANELS": build_issue_panels(published_files),
            "PRINT_TOOL_HREF": TOOL_VIEWER_PATH,
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
    parser = argparse.ArgumentParser(description="Build the project landing page and publish the latest map output.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT_DIR, help="Output directory for the generated static site.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    build_site(args.out)
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
