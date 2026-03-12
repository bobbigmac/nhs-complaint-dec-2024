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
    {
        "title": "Operating environment note",
        "description": "The source note for the provider, commissioner, alliance and competitor landscape around GTD.",
        "files": [
            {"label": "Markdown", "source": OPERATING_ENVIRONMENT_SOURCE},
        ],
        "links": [
            {"label": "Open page", "href": "environment/", "variant": "primary"},
        ],
    },
    {
        "title": "Management company method",
        "description": "The short note explaining how the watchlist and operator-profile layer are maintained under datasets.",
        "files": [
            {"label": "Markdown", "source": ORG_METHOD_SOURCE},
        ],
        "links": [
            {"label": "Org navigator", "href": "org-navigator/", "variant": "primary"},
        ],
    },
    {
        "title": "Map notes",
        "description": "Read the generated README for the current map if you want the data notes before opening it.",
        "links": [
            {"label": "Markdown", "href": "map/README.md", "variant": "primary"},
            {"label": "Print view", "href": f"{TOOL_VIEWER_PATH}?source=../map/README.md", "variant": "secondary"},
        ],
    },
]

VIEW_CARDS: list[dict[str, object]] = [
    {
        "title": "Interactive map",
        "description": "Open the latest Greater Manchester comparison map with review, survey and takeover context.",
        "links": [("Open map", "map/map.html", "primary")],
    },
    {
        "title": "GTD chronology",
        "description": "Browse the dated working log that ties procurement, governance, takeover and trend notes together.",
        "links": [("Open chronology", "chronology/", "primary")],
        "source": CHRONOLOGY_SOURCE,
    },
    {
        "title": "Operating environment",
        "description": "Read the role map for commissioners, providers, federations, alliances and public decision-makers around GTD.",
        "links": [("Open environment", "environment/", "primary")],
        "source": OPERATING_ENVIRONMENT_SOURCE,
    },
    {
        "title": "Org navigator",
        "description": "Open the operator-profile view for GTD, peers, previous providers and management-company clusters.",
        "links": [("Open org navigator", "org-navigator/", "primary")],
        "source": ORG_NAVIGATOR_SOURCE,
    },
]

PAGE_DOCS: list[dict[str, object]] = [
    {
        "id": "chronology",
        "site_dir": "chronology",
        "title": "GTD Chronology",
        "kicker": "Context log",
        "summary": "A browsable dated log of public facts, working inferences and missing records around GTD, New Bank and the wider commissioner-provider environment.",
        "source": CHRONOLOGY_SOURCE,
        "extra_sources": [
            {"label": "Link dump", "source": INQUIRY_LINK_DUMP_SOURCE},
            {"label": "Inquiry source note", "source": "ChatGPT-GTD_Healthcare_Procurement_Inquiry.md"},
        ],
        "related_page_ids": ["environment", "org-navigator"],
    },
    {
        "id": "environment",
        "site_dir": "environment",
        "title": "Operating Environment Around GTD",
        "kicker": "Organisation map",
        "summary": "A source-of-truth note on who sits around GTD, which organisations collaborate or compete, and which pressures shape the operating model.",
        "source": OPERATING_ENVIRONMENT_SOURCE,
        "extra_sources": [
            {"label": "Operator profiles", "source": ORG_NAVIGATOR_SOURCE},
            {"label": "Watchlist JSON", "source": ORG_WATCHLIST_SOURCE},
            {"label": "Enrichment script", "source": "datasets/enrich_management_companies.py"},
        ],
        "related_page_ids": ["chronology", "org-navigator"],
    },
    {
        "id": "org-navigator",
        "site_dir": "org-navigator",
        "title": "Org Navigator: Known Operators",
        "kicker": "Industry shape",
        "summary": "A readable profile view of the management companies, federations, peers and previous providers that keep recurring around GTD.",
        "source": ORG_NAVIGATOR_SOURCE,
        "extra_sources": [
            {"label": "Method note", "source": ORG_METHOD_SOURCE},
            {"label": "Watchlist JSON", "source": ORG_WATCHLIST_SOURCE},
            {"label": "Operating environment", "source": OPERATING_ENVIRONMENT_SOURCE},
        ],
        "related_page_ids": ["environment", "chronology"],
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


def render_inline_markdown(text: str, link_resolver: Callable[[str], str] | None = None) -> str:
    replacements: list[tuple[str, str]] = []

    def stash(fragment: str) -> str:
        token = f"INLINE_TOKEN_{len(replacements)}"
        replacements.append((token, fragment))
        return token

    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda match: stash(
            f'<a href="{html.escape((link_resolver or (lambda href: href))(match.group(2)), quote=True)}">{html.escape(match.group(1))}</a>'
        ),
        text,
    )
    text = re.sub(
        r"`([^`]+)`",
        lambda match: stash(f"<code>{html.escape(match.group(1))}</code>"),
        text,
    )

    escaped = html.escape(text, quote=False)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)
    for token, fragment in replacements:
        escaped = escaped.replace(token, fragment)
    return escaped


def slugify_heading(text: str, seen: dict[str, int]) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "section"
    count = seen.get(base, 0)
    seen[base] = count + 1
    return base if count == 0 else f"{base}-{count + 1}"


def markdown_to_html(
    markdown_text: str,
    *,
    link_resolver: Callable[[str], str] | None = None,
    drop_first_h1: bool = False,
) -> tuple[str, list[tuple[int, str, str]]]:
    blocks: list[str] = []
    paragraph_lines: list[str] = []
    list_items: list[str] = []
    list_type: str | None = None
    headings: list[tuple[int, str, str]] = []
    seen_heading_ids: dict[str, int] = {}
    skipped_h1 = False

    def flush_paragraph() -> None:
        nonlocal paragraph_lines
        if not paragraph_lines:
            return
        text = " ".join(line.strip() for line in paragraph_lines)
        blocks.append(f"<p>{render_inline_markdown(text, link_resolver=link_resolver)}</p>")
        paragraph_lines = []

    def flush_list() -> None:
        nonlocal list_items, list_type
        if not list_items:
            return
        tag = list_type or "ul"
        items = "".join(f"<li>{render_inline_markdown(item, link_resolver=link_resolver)}</li>" for item in list_items)
        blocks.append(f"<{tag}>{items}</{tag}>")
        list_items = []
        list_type = None

    for raw_line in markdown_text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            flush_paragraph()
            flush_list()
            continue

        if stripped == ">":
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
            heading_text = heading_match.group(2).strip()
            if drop_first_h1 and level == 1 and not skipped_h1:
                skipped_h1 = True
                continue
            anchor = slugify_heading(heading_text, seen_heading_ids)
            headings.append((level, heading_text, anchor))
            blocks.append(f'<h{level} id="{anchor}">{render_inline_markdown(heading_text, link_resolver=link_resolver)}</h{level}>')
            continue

        unordered_match = re.match(r"^[-*]\s+(.*)$", stripped)
        ordered_match = re.match(r"^\d+\.\s+(.*)$", stripped)
        if unordered_match or ordered_match:
            flush_paragraph()
            next_type = "ul" if unordered_match else "ol"
            if list_type and list_type != next_type:
                flush_list()
            list_type = next_type
            list_items.append((unordered_match or ordered_match).group(1).strip())
            continue

        if list_items and line.startswith(("  ", "\t")):
            list_items[-1] = f"{list_items[-1]} {stripped}"
            continue

        if stripped.startswith("> "):
            flush_paragraph()
            flush_list()
            blocks.append(
                f"<blockquote><p>{render_inline_markdown(stripped[2:].strip(), link_resolver=link_resolver)}</p></blockquote>"
            )
            continue

        paragraph_lines.append(stripped)

    flush_paragraph()
    flush_list()
    return "\n".join(blocks), headings


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


def markdown_print_href_from(current_site_path: str, target_site_path: str) -> str:
    tool_href = relative_site_href(current_site_path, TOOL_VIEWER_PATH)
    return f"{tool_href}?source={quote('../' + target_site_path, safe='/')}"


def relative_site_href(from_site_path: str, to_site_path: str) -> str:
    from_dir = posixpath.dirname(from_site_path) or "."
    return quote(posixpath.relpath(to_site_path, start=from_dir), safe="/#")


def resolve_source_path(source: str) -> Path:
    return (REPO_ROOT / source).resolve()


def build_page_lookup() -> dict[Path, dict[str, object]]:
    return {resolve_source_path(str(spec["source"])): spec for spec in PAGE_DOCS}


def iter_page_source_paths() -> Iterable[Path]:
    for spec in PAGE_DOCS:
        yield resolve_source_path(str(spec["source"]))
        for extra_source in spec.get("extra_sources", []):
            yield resolve_source_path(str(extra_source["source"]))


def collect_published_sources() -> list[Path]:
    sources: dict[str, Path] = {}
    for section in ISSUE_SECTIONS:
        for resource in section["resources"]:
            for file_meta in resource["files"]:
                source = resolve_source_path(str(file_meta["source"]))
                sources[str(source)] = source
    for resource in REFERENCE_DOCS:
        for file_meta in resource.get("files", []):
            source = resolve_source_path(str(file_meta["source"]))
            sources[str(source)] = source
    for source in iter_page_source_paths():
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
        for file_meta in resource.get("files", []):
            source_key = str(file_meta["source"])
            site_path = published_files[source_key]
            links.append((str(file_meta["label"]), href_for_site_path(site_path), "primary"))
            if site_path.endswith(".md"):
                links.append(("Print view", markdown_print_href(site_path), "secondary"))
        for link_meta in resource.get("links", []):
            links.append(
                (
                    str(link_meta["label"]),
                    str(link_meta["href"]),
                    str(link_meta.get("variant", "secondary")),
                )
            )
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


def build_action_cards(published_files: dict[str, str]) -> str:
    cards = []
    for card in VIEW_CARDS:
        links = list(card["links"])
        source = card.get("source")
        if source:
            site_path = published_files[str(source)]
            links.append(("Source", href_for_site_path(site_path), "secondary"))
            if site_path.endswith(".md"):
                links.append(("Print view", markdown_print_href(site_path), "secondary"))
        cards.append(
            {
                "title": str(card["title"]),
                "description": str(card["description"]),
                "links": links,
            }
        )
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


def load_template(name: str) -> str:
    return (SITE_DIR / "templates" / name).read_text(encoding="utf-8")


def replace_tokens(template: str, values: dict[str, str]) -> str:
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def resolve_markdown_href(
    href: str,
    *,
    source_path: Path,
    current_site_path: str,
    published_files: dict[str, str],
    page_lookup: dict[Path, dict[str, object]],
) -> str:
    if href.startswith(("http://", "https://", "mailto:", "#")):
        return href

    path_part, fragment = href, ""
    if "#" in href:
        path_part, fragment = href.split("#", 1)

    candidate = (source_path.parent / path_part).resolve() if path_part else source_path
    destination: str | None = None
    page_spec = page_lookup.get(candidate)
    if page_spec is not None and candidate.suffix == ".md":
        destination = f'{page_spec["site_dir"]}/index.html'
    else:
        try:
            relative = candidate.relative_to(REPO_ROOT).as_posix()
        except ValueError:
            relative = ""
        destination = published_files.get(relative)

    if destination is None:
        return href

    resolved = relative_site_href(current_site_path, destination)
    return f"{resolved}#{quote(fragment)}" if fragment else resolved


def build_toc_links(headings: Iterable[tuple[int, str, str]]) -> str:
    toc_items = [
        (
            level,
            f'<a class="toc-link toc-level-{level}" href="#{html.escape(anchor, quote=True)}">{html.escape(title)}</a>',
        )
        for level, title, anchor in headings
        if level in {2, 3}
    ]
    if not toc_items:
        return '<p class="toc-empty">No section headings found.</p>'
    return "".join(item for _, item in toc_items)


def build_doc_source_links(
    source_items: Iterable[dict[str, str]],
    *,
    current_site_path: str,
    published_files: dict[str, str],
) -> str:
    links: list[tuple[str, str, str]] = []
    for source_item in source_items:
        source_key = str(source_item["source"])
        site_path = published_files[source_key]
        links.append((str(source_item["label"]), relative_site_href(current_site_path, site_path), "primary"))
        if site_path.endswith(".md"):
            links.append((f'{source_item["label"]} print', markdown_print_href_from(current_site_path, site_path), "secondary"))
    return build_link_pills(links)


def build_related_page_links(
    related_page_ids: Iterable[str],
    *,
    current_site_path: str,
) -> str:
    page_specs = {str(spec["id"]): spec for spec in PAGE_DOCS}
    links: list[str] = []
    for page_id in related_page_ids:
        spec = page_specs[page_id]
        href = relative_site_href(current_site_path, f'{spec["site_dir"]}/index.html')
        links.append(
            f'<a class="doc-nav-link" href="{html.escape(href, quote=True)}"><strong>{html.escape(str(spec["title"]))}</strong><span>{html.escape(str(spec["summary"]))}</span></a>'
        )
    return "".join(links)


def write_document_page(
    out_dir: Path,
    spec: dict[str, object],
    *,
    published_files: dict[str, str],
    page_lookup: dict[Path, dict[str, object]],
) -> None:
    source_path = resolve_source_path(str(spec["source"]))
    current_site_path = f'{spec["site_dir"]}/index.html'
    markdown_text = source_path.read_text(encoding="utf-8")
    body_html, headings = markdown_to_html(
        markdown_text,
        link_resolver=lambda href: resolve_markdown_href(
            href,
            source_path=source_path,
            current_site_path=current_site_path,
            published_files=published_files,
            page_lookup=page_lookup,
        ),
        drop_first_h1=True,
    )
    source_items = [{"label": "Source markdown", "source": str(spec["source"])}]
    source_items.extend(spec.get("extra_sources", []))
    template = load_template("document.html")
    page_html = replace_tokens(
        template,
        {
            "PAGE_TITLE": html.escape(str(spec["title"])),
            "DOC_KICKER": html.escape(str(spec["kicker"])),
            "DOC_TITLE": html.escape(str(spec["title"])),
            "DOC_SUMMARY": html.escape(str(spec["summary"])),
            "DOC_TOC": build_toc_links(headings),
            "DOC_SOURCE_LINKS": build_doc_source_links(
                source_items,
                current_site_path=current_site_path,
                published_files=published_files,
            ),
            "DOC_RELATED_LINKS": build_related_page_links(
                spec.get("related_page_ids", []),
                current_site_path=current_site_path,
            ),
            "DOC_BODY": body_html,
            "HOME_HREF": relative_site_href(current_site_path, "index.html"),
            "MAP_HREF": relative_site_href(current_site_path, "map/map.html"),
            "PRINT_TOOL_HREF": relative_site_href(current_site_path, TOOL_VIEWER_PATH),
        },
    )
    doc_out_dir = out_dir / str(spec["site_dir"])
    doc_out_dir.mkdir(parents=True, exist_ok=True)
    (doc_out_dir / "index.html").write_text(page_html, encoding="utf-8")


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
    template = load_template("base.html")
    updated_value = summary.get("generated_date") or datetime.now(UTC).date().isoformat()
    published_files = publish_supporting_files(out_dir)
    page_html = replace_tokens(
        template,
        {
            "PAGE_TITLE": "New Bank Access Evidence",
            "UPDATED_DATE": html.escape(str(updated_value)),
            "REPORT_NAME": html.escape(report_dir.name),
            "MAP_HREF": "map/map.html",
            "REPO_HREF": "https://github.com/bobbigmac/nhs-complaint-dec-2024",
            "STAT_CARDS": build_stat_cards(summary),
            "ACTION_CARDS": build_action_cards(published_files),
            "REFERENCE_CARDS": build_reference_cards(published_files),
            "ISSUE_PANELS": build_issue_panels(published_files),
            "PRINT_TOOL_HREF": TOOL_VIEWER_PATH,
        },
    )
    (out_dir / "index.html").write_text(page_html, encoding="utf-8")

    page_lookup = build_page_lookup()
    for spec in PAGE_DOCS:
        write_document_page(out_dir, spec, published_files=published_files, page_lookup=page_lookup)


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
