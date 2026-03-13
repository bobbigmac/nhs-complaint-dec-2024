#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import statistics
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


def mean_or_none(values: list[float | int | None]) -> float | None:
    clean = [float(value) for value in values if value is not None]
    if not clean:
        return None
    return round(statistics.fmean(clean), 2)


def survey_metric_percent(row: dict[str, Any], metric_name: str) -> float | None:
    metric = (((row.get("survey") or {}).get("metrics") or {}).get(metric_name) or {})
    value = metric.get("practice_percent")
    if value is None:
        return None
    return float(value)


def subjective_score(report: dict[str, Any], metric_name: str) -> float | None:
    value = (report.get("subjective_scores") or {}).get(metric_name)
    if value is None:
        return None
    return float(value)


def report_relative_link(row: dict[str, Any]) -> str:
    report_path = Path(str(row.get("report_path", "")))
    return f"../reports/{report_path.name}"


def average_user_visible_interactions(report: dict[str, Any]) -> float | None:
    checks = report.get("task_checks", [])
    values = [item.get("user_visible_interactions") for item in checks if isinstance(item.get("user_visible_interactions"), (int, float))]
    return mean_or_none(values)


def average_friction_points(report: dict[str, Any]) -> float | None:
    checks = report.get("task_checks", [])
    values = [len(item.get("friction", [])) for item in checks]
    return mean_or_none(values)


def encountered_issue_count(report: dict[str, Any]) -> int:
    return len(report.get("encountered_issues", []))


def stale_or_conflicting_stack_count(report: dict[str, Any]) -> int:
    count = 0
    for item in report.get("website_stack", {}).get("items", []):
        status = str(item.get("status", "")).lower()
        if any(token in status for token in ("stale", "conflict", "broken", "suspect")):
            count += 1
    return count


def median_runtime_ms(report: dict[str, Any]) -> float | None:
    values = [
        float(item["load_ms"])
        for item in report.get("basic_runtime_checks", {}).get("checks", [])
        if isinstance(item.get("load_ms"), (int, float))
    ]
    if not values:
        return None
    return round(statistics.median(values), 1)


RANK_SIGNAL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "key": "overall_good",
        "label": "GPPS overall experience",
        "weight": 2.5,
        "include_in_relative_score": False,
        "higher_is_better": True,
        "extract": lambda row, report: survey_metric_percent(row, "overall_good"),
        "format": lambda value: f"{value:.1f}%",
    },
    {
        "key": "website_easy",
        "label": "GPPS website ease",
        "weight": 2.0,
        "include_in_relative_score": False,
        "higher_is_better": True,
        "extract": lambda row, report: survey_metric_percent(row, "website_easy"),
        "format": lambda value: f"{value:.1f}%",
    },
    {
        "key": "contact_good",
        "label": "GPPS contact experience",
        "weight": 2.0,
        "include_in_relative_score": False,
        "higher_is_better": True,
        "extract": lambda row, report: survey_metric_percent(row, "contact_good"),
        "format": lambda value: f"{value:.1f}%",
    },
    {
        "key": "needs_met",
        "label": "GPPS needs met",
        "weight": 2.0,
        "include_in_relative_score": False,
        "higher_is_better": True,
        "extract": lambda row, report: survey_metric_percent(row, "needs_met"),
        "format": lambda value: f"{value:.1f}%",
    },
    {
        "key": "google_review_score",
        "label": "Google review score",
        "weight": 1.0,
        "include_in_relative_score": False,
        "higher_is_better": True,
        "extract": lambda row, report: float(row["google_review_score"]) if row.get("google_review_score") is not None else None,
        "format": lambda value: f"{value:.1f} / 5",
    },
    {
        "key": "front_door_clarity",
        "label": "Subjective front-door clarity",
        "weight": 2.0,
        "include_in_relative_score": True,
        "higher_is_better": True,
        "extract": lambda row, report: subjective_score(report, "front_door_clarity"),
        "format": lambda value: f"{int(value)} / 5",
    },
    {
        "key": "digital_task_coverage",
        "label": "Subjective digital task coverage",
        "weight": 1.5,
        "include_in_relative_score": True,
        "higher_is_better": True,
        "extract": lambda row, report: subjective_score(report, "digital_task_coverage"),
        "format": lambda value: f"{int(value)} / 5",
    },
    {
        "key": "journey_ease",
        "label": "Subjective journey ease",
        "weight": 2.0,
        "include_in_relative_score": True,
        "higher_is_better": True,
        "extract": lambda row, report: subjective_score(report, "journey_ease"),
        "format": lambda value: f"{int(value)} / 5",
    },
    {
        "key": "trust_and_maintenance",
        "label": "Subjective trust and maintenance",
        "weight": 1.5,
        "include_in_relative_score": True,
        "higher_is_better": True,
        "extract": lambda row, report: subjective_score(report, "trust_and_maintenance"),
        "format": lambda value: f"{int(value)} / 5",
    },
    {
        "key": "complaints_and_fallbacks",
        "label": "Subjective complaints and fallbacks",
        "weight": 1.0,
        "include_in_relative_score": True,
        "higher_is_better": True,
        "extract": lambda row, report: subjective_score(report, "complaints_and_fallbacks"),
        "format": lambda value: f"{int(value)} / 5",
    },
    {
        "key": "overall_patient_usability",
        "label": "Subjective overall patient usability",
        "weight": 2.5,
        "include_in_relative_score": True,
        "higher_is_better": True,
        "extract": lambda row, report: subjective_score(report, "overall_patient_usability"),
        "format": lambda value: f"{int(value)} / 5",
    },
    {
        "key": "avg_user_visible_interactions",
        "label": "Average clicks to first actionable page",
        "weight": 1.5,
        "include_in_relative_score": False,
        "higher_is_better": False,
        "extract": lambda row, report: average_user_visible_interactions(report),
        "format": lambda value: f"{value:.2f}",
    },
    {
        "key": "avg_friction_points",
        "label": "Average friction notes per task",
        "weight": 1.5,
        "include_in_relative_score": False,
        "higher_is_better": False,
        "extract": lambda row, report: average_friction_points(report),
        "format": lambda value: f"{value:.2f}",
    },
    {
        "key": "encountered_issue_count",
        "label": "Encountered issues recorded",
        "weight": 1.5,
        "include_in_relative_score": False,
        "higher_is_better": False,
        "extract": lambda row, report: float(encountered_issue_count(report)),
        "format": lambda value: f"{int(value)}",
    },
    {
        "key": "stale_or_conflicting_stack_count",
        "label": "Stale or conflicting stack signals",
        "weight": 1.0,
        "include_in_relative_score": False,
        "higher_is_better": False,
        "extract": lambda row, report: float(stale_or_conflicting_stack_count(report)),
        "format": lambda value: f"{int(value)}",
    },
]


SUBJECTIVE_SCORE_FIELDS: list[dict[str, str]] = [
    {
        "key": "front_door_clarity",
        "label": "Front-door clarity",
        "description": "How obvious the main digital entry route feels to a patient.",
    },
    {
        "key": "digital_task_coverage",
        "label": "Task coverage",
        "description": "How many common jobs have a usable digital route.",
    },
    {
        "key": "journey_ease",
        "label": "Journey ease",
        "description": "How much friction the patient hits before reaching action.",
    },
    {
        "key": "trust_and_maintenance",
        "label": "Trust and maintenance",
        "description": "How coherent, current, and trustworthy the public site feels.",
    },
    {
        "key": "complaints_and_fallbacks",
        "label": "Complaints and fallbacks",
        "description": "How legible the complaint route and offline fallbacks are.",
    },
    {
        "key": "overall_patient_usability",
        "label": "Overall usability",
        "description": "Overall judgement of the website experience as a patient.",
    },
]


def compute_rank_metadata(values: list[float], value: float, higher_is_better: bool) -> dict[str, Any]:
    if higher_is_better:
        rank = 1 + sum(1 for other in values if other > value)
    else:
        rank = 1 + sum(1 for other in values if other < value)
    out_of = len(values)
    if out_of <= 1:
        percentile = 100.0
    else:
        percentile = round((out_of - rank) / (out_of - 1) * 100, 1)
    return {
        "rank": rank,
        "out_of": out_of,
        "percentile": percentile,
    }


def relative_band(score: float) -> str:
    if score >= 75:
        return "top quartile"
    if score >= 50:
        return "upper-middle"
    if score >= 25:
        return "lower-middle"
    return "bottom quartile"


def describe_signal(signal_score: dict[str, Any]) -> str:
    rank = signal_score["rank"]
    out_of = signal_score["out_of"]
    return f"{signal_score['label']} {rank}/{out_of}"


def shorten_url(url: str, limit: int = 72) -> str:
    if len(url) <= limit:
        return url
    return f"{url[: limit - 1]}…"


def format_runtime(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:.1f} ms"


def json_script(value: Any) -> str:
    return html.escape(json.dumps(value, indent=2))


def build_svg_line_path(points: list[tuple[float, float] | None]) -> str:
    commands: list[str] = []
    open_segment = False
    for point in points:
        if point is None:
            open_segment = False
            continue
        x, y = point
        command = "L" if open_segment else "M"
        commands.append(f"{command} {x:.1f} {y:.1f}")
        open_segment = True
    return " ".join(commands)


def practice_brief(practice: dict[str, Any]) -> dict[str, Any]:
    return {
        "ods_code": practice["ods_code"],
        "practice_name": practice["practice_name"],
        "relative_rank": practice["relative_rank"],
        "relative_score": practice["relative_score"],
    }


def task_overview(report: dict[str, Any]) -> list[dict[str, Any]]:
    overview: list[dict[str, Any]] = []
    for item in report.get("task_checks", []):
        first_url = item.get("first_actionable_page")
        friction = item.get("friction", [])
        overview.append(
            {
                "task": item.get("task"),
                "route_found": bool(item.get("route_found")),
                "user_visible_interactions": item.get("user_visible_interactions"),
                "first_actionable_page": first_url,
                "first_actionable_host": urlparse(first_url).netloc if isinstance(first_url, str) and first_url else None,
                "first_friction": friction[0] if friction else None,
            }
        )
    return overview


def build_relative_rankings(rows: list[dict[str, Any]], reports_by_ods: dict[str, dict[str, Any]], generated_at: str) -> dict[str, Any]:
    practices: list[dict[str, Any]] = []
    cohort_values: dict[str, list[float]] = {definition["key"]: [] for definition in RANK_SIGNAL_DEFINITIONS}

    for row in rows:
        ods_code = row["ods_code"]
        report = reports_by_ods[ods_code]
        raw_signals: dict[str, float] = {}
        for definition in RANK_SIGNAL_DEFINITIONS:
            value = definition["extract"](row, report)
            if value is None:
                continue
            raw_signals[definition["key"]] = float(value)
            cohort_values[definition["key"]].append(float(value))

        practices.append(
            {
                "ods_code": ods_code,
                "practice_name": row.get("practice_name"),
                "display_name": row.get("practice_name"),
                "headline": report.get("headline"),
                "website_url": row.get("website_url"),
                "website_identity": row.get("website_identity"),
                "website_stack": row.get("website_stack"),
                "request_platforms": row.get("request_platforms", []),
                "google_review_score": row.get("google_review_score"),
                "google_review_count": row.get("google_review_count"),
                "report_path": row.get("report_path"),
                "report_link": report_relative_link(row),
                "survey_metrics": (row.get("survey") or {}).get("metrics") or {},
                "subjective_scores": report.get("subjective_scores") or {},
                "raw_signals": raw_signals,
                "report_signals": {
                    "avg_user_visible_interactions": average_user_visible_interactions(report),
                    "avg_friction_points": average_friction_points(report),
                    "encountered_issue_count": encountered_issue_count(report),
                    "stale_or_conflicting_stack_count": stale_or_conflicting_stack_count(report),
                    "median_runtime_ms": median_runtime_ms(report),
                    "discovered_path_count": len(report.get("discovered_paths", [])),
                    "source_page_count": len(report.get("source_pages", [])),
                    "task_count": len(report.get("task_checks", [])),
                },
                "task_overview": task_overview(report),
                "encountered_issues": report.get("encountered_issues", []),
                "probably_true": report.get("analyst_notes", {}).get("probably_true", []),
                "needs_follow_up": report.get("analyst_notes", {}).get("needs_follow_up", []),
                "source_pages": report.get("source_pages", []),
                "replay_hints": report.get("replay_hints", []),
            }
        )

    for practice in practices:
        signal_scores: list[dict[str, Any]] = []
        relative_total_weight = 0.0
        relative_total_percentile = 0.0
        for definition in RANK_SIGNAL_DEFINITIONS:
            key = definition["key"]
            if key not in practice["raw_signals"]:
                continue
            values = cohort_values[key]
            signal_value = practice["raw_signals"][key]
            rank_metadata = compute_rank_metadata(values, signal_value, definition["higher_is_better"])
            signal_score = {
                "key": key,
                "label": definition["label"],
                "raw_value": signal_value,
                "display_value": definition["format"](signal_value),
                "include_in_relative_score": definition["include_in_relative_score"],
                "higher_is_better": definition["higher_is_better"],
                "weight": definition["weight"],
                **rank_metadata,
            }
            signal_scores.append(signal_score)
            if definition["include_in_relative_score"]:
                relative_total_weight += float(definition["weight"])
                relative_total_percentile += float(definition["weight"]) * float(rank_metadata["percentile"])

        relative_score = round(relative_total_percentile / relative_total_weight, 1) if relative_total_weight else 0.0
        practice["signal_scores"] = sorted(signal_scores, key=lambda item: item["percentile"], reverse=True)
        practice["relative_score"] = relative_score
        practice["relative_band"] = relative_band(relative_score)

        ranking_signals = [item for item in practice["signal_scores"] if item["include_in_relative_score"]]
        strengths = ranking_signals[:3] if ranking_signals else practice["signal_scores"][:3]
        strength_keys = {item["key"] for item in strengths}
        caution_pool = (
            [item for item in sorted(ranking_signals, key=lambda item: item["percentile"]) if item["key"] not in strength_keys]
            if ranking_signals
            else [item for item in sorted(practice["signal_scores"], key=lambda item: item["percentile"]) if item["key"] not in strength_keys]
        )
        cautions = caution_pool[:3]
        practice["strengths"] = [describe_signal(item) for item in strengths]
        practice["cautions"] = [describe_signal(item) for item in cautions]

    practices.sort(
        key=lambda item: (
            -float(item["relative_score"]),
            item.get("practice_name") or "",
        )
    )

    for index, practice in enumerate(practices, start=1):
        practice["relative_rank"] = index
        practice["relative_rank_out_of"] = len(practices)
        if len(practices) <= 1:
            relative_percentile = 100.0
        else:
            relative_percentile = round((len(practices) - index) / (len(practices) - 1) * 100, 1)
        practice["relative_percentile"] = relative_percentile
        practice["relative_band"] = relative_band(relative_percentile)

    return {
        "generated_at": generated_at,
        "practice_count": len(practices),
        "methodology": {
            "kind": "report-only weighted percentile blend",
            "summary": "Default ordering is based on the subjective report scores now stored in each practice JSON: front-door clarity, digital task coverage, journey ease, trust and maintenance, complaints and fallbacks, and overall patient usability. GP Patient Survey, Google scores, click counts and issue counts are shown beside that ordering as comparison columns, not as inputs to the rank itself.",
            "signals": [
                {
                    "key": definition["key"],
                    "label": definition["label"],
                    "weight": definition["weight"],
                    "include_in_relative_score": definition["include_in_relative_score"],
                    "higher_is_better": definition["higher_is_better"],
                }
                for definition in RANK_SIGNAL_DEFINITIONS
            ],
        },
        "practices": practices,
        "top_five": [practice_brief(item) for item in practices[:5]],
        "bottom_five": [practice_brief(item) for item in practices[-5:]],
    }


def render_relative_rankings_html(rankings: dict[str, Any]) -> str:
    def render_practice_list(items: list[dict[str, Any]]) -> str:
        return (
            "<ol class=\"summary-list\">"
            + "".join(
                f"<li><span>{html.escape(item['practice_name'])}</span>"
                f"<span class=\"meta\">#{item['relative_rank']} · {item['relative_score']:.1f}</span></li>"
                for item in items
            )
            + "</ol>"
        )

    practices = rankings["practices"]

    def render_comparison_chart() -> str:
        if not practices:
            return ""

        width = 1180
        height = 360
        left = 66
        right = 24
        top = 26
        bottom = 48
        plot_width = width - left - right
        plot_height = height - top - bottom
        denominator = max(len(practices) - 1, 1)

        def x_for_index(index: int) -> float:
            return left + (plot_width * index / denominator)

        def y_for_percent(value: float) -> float:
            return top + plot_height - ((max(0.0, min(100.0, value)) / 100.0) * plot_height)

        series_definitions = [
            {
                "key": "google",
                "label": "Google review x20",
                "stroke": "#7c402a",
                "value": lambda practice: (
                    float(practice["google_review_score"]) * 20.0
                    if practice.get("google_review_score") is not None
                    else None
                ),
            },
            {
                "key": "overall",
                "label": "GPPS overall",
                "stroke": "#0e5a46",
                "value": lambda practice: (
                    float((((practice.get("survey_metrics") or {}).get("overall_good") or {}).get("practice_percent")))
                    if (((practice.get("survey_metrics") or {}).get("overall_good") or {}).get("practice_percent")) is not None
                    else None
                ),
            },
            {
                "key": "website",
                "label": "GPPS website",
                "stroke": "#355c7d",
                "value": lambda practice: (
                    float((((practice.get("survey_metrics") or {}).get("website_easy") or {}).get("practice_percent")))
                    if (((practice.get("survey_metrics") or {}).get("website_easy") or {}).get("practice_percent")) is not None
                    else None
                ),
            },
        ]

        grid_lines = "".join(
            (
                f'<line x1="{left}" y1="{y_for_percent(value):.1f}" x2="{width - right}" y2="{y_for_percent(value):.1f}" class="chart-grid" />'
                f'<text x="{left - 10}" y="{y_for_percent(value) + 4:.1f}" text-anchor="end" class="chart-axis-label">{value}</text>'
            )
            for value in (0, 25, 50, 75, 100)
        )

        x_ticks = [0]
        if len(practices) > 2:
            x_ticks.append(len(practices) // 2)
        if len(practices) > 1:
            x_ticks.append(len(practices) - 1)
        x_ticks = sorted(set(x_ticks))
        x_labels = "".join(
            (
                f'<line x1="{x_for_index(index):.1f}" y1="{height - bottom}" x2="{x_for_index(index):.1f}" y2="{height - bottom + 6}" class="chart-axis" />'
                f'<text x="{x_for_index(index):.1f}" y="{height - bottom + 22}" text-anchor="middle" class="chart-axis-label">#{index + 1}</text>'
            )
            for index in x_ticks
        )

        series_paths: list[str] = []
        point_groups: list[str] = []
        legend_items: list[str] = []

        for series in series_definitions:
            points: list[tuple[float, float] | None] = []
            for index, practice in enumerate(practices):
                value = series["value"](practice)
                if value is None:
                    points.append(None)
                    continue
                points.append((x_for_index(index), y_for_percent(float(value))))

            path = build_svg_line_path(points)
            if path:
                series_paths.append(
                    f'<path d="{path}" fill="none" stroke="{series["stroke"]}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />'
                )

            point_markup = []
            for index, practice in enumerate(practices):
                value = series["value"](practice)
                if value is None:
                    continue
                raw_display = (
                    f'{float(practice["google_review_score"]):.1f} / 5'
                    if series["key"] == "google"
                    else f"{float(value):.1f}%"
                )
                point_markup.append(
                    f'<circle cx="{x_for_index(index):.1f}" cy="{y_for_percent(float(value)):.1f}" r="4.5" fill="{series["stroke"]}" class="chart-point">'
                    f"<title>{html.escape(str(practice['practice_name']))} · rank #{practice['relative_rank']} · {series['label']}: {raw_display}</title>"
                    "</circle>"
                )
            point_groups.append("".join(point_markup))

            legend_items.append(
                "<li>"
                f'<span class="legend-swatch" style="background:{series["stroke"]};"></span>'
                f"{html.escape(series['label'])}"
                "</li>"
            )

        return (
            '<section class="chart-shell">'
            '<div class="chart-copy">'
            "<h2>Comparison Chart</h2>"
            "<p>The x-axis follows the default report-usability order. The three lines show whether Google review score, GP Patient Survey overall, and GP Patient Survey website ease broadly rise and fall with that report-led ordering.</p>"
            "</div>"
            '<div class="chart-wrap">'
            f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Comparison chart of report order versus Google review score, GP Patient Survey overall, and GP Patient Survey website ease.">'
            f"{grid_lines}"
            f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height - bottom}" class="chart-axis" />'
            f'<line x1="{left}" y1="{height - bottom}" x2="{width - right}" y2="{height - bottom}" class="chart-axis" />'
            f"{x_labels}"
            f"{''.join(series_paths)}"
            f"{''.join(point_groups)}"
            f'<text x="{left}" y="{top - 8}" class="chart-axis-title">comparison score</text>'
            f'<text x="{width - right}" y="{height - 12}" text-anchor="end" class="chart-axis-title">report usability order</text>'
            "</svg>"
            "</div>"
            f'<ul class="chart-legend">{"".join(legend_items)}</ul>'
            "</section>"
        )

    header_tooltips = {
        "rank": "Composite cohort position across the reviewed practice set. Click to sort.",
        "practice": "Practice name and site identity summary. Click to sort alphabetically.",
        "score": "Weighted report-only website usability score derived from the subjective report scoring fields. Higher is better. Click to sort.",
        "overall": "GP Patient Survey overall experience score for the practice. Click to sort.",
        "website": "GP Patient Survey website-contact ease score for the practice. Click to sort.",
        "clicks": "Average visible interactions from homepage to first actionable page across checked tasks. Lower is better. Click to sort.",
        "issues": "Count of encountered issues explicitly logged in the source report. Lower is better. Click to sort.",
        "platforms": "Derived request platforms surfaced in the source report, such as PATCHS or Accurx. Click to sort alphabetically.",
        "google": "Google review score captured in the source report. Click to sort.",
    }

    practice_rows: list[str] = []
    for practice in practices:
        ods_code = practice["ods_code"]
        detail_id = f"detail-{ods_code}"
        platforms = ", ".join(practice.get("request_platforms") or []) or "mixed / unclear"
        issues = practice["report_signals"]["encountered_issue_count"]
        clicks = practice["report_signals"]["avg_user_visible_interactions"]
        clicks_display = f"{clicks:.2f}" if isinstance(clicks, (int, float)) else "-"
        google_score = practice.get("google_review_score")
        google_display = f"{float(google_score):.1f}" if google_score is not None else "-"
        overall_good = (((practice.get("survey_metrics") or {}).get("overall_good") or {}).get("practice_percent"))
        website_easy = (((practice.get("survey_metrics") or {}).get("website_easy") or {}).get("practice_percent"))
        overall_display = f"{float(overall_good):.1f}%" if overall_good is not None else "-"
        website_display = f"{float(website_easy):.1f}%" if website_easy is not None else "-"

        task_rows: list[str] = []
        for task in practice["task_overview"]:
            url = task.get("first_actionable_page")
            task_rows.append(
                "<tr>"
                f"<td>{html.escape(str(task.get('task') or '-'))}</td>"
                f"<td>{html.escape(str(task.get('user_visible_interactions') or '-'))}</td>"
                "<td>"
                + (
                    f'<a href="{html.escape(str(url))}" target="_blank" rel="noreferrer">{html.escape(shorten_url(str(url)))}</a>'
                    if url
                    else "-"
                )
                + "</td>"
                f"<td>{html.escape(str(task.get('first_friction') or '-'))}</td>"
                "</tr>"
            )

        issue_items = "".join(
            f"<li><strong>{html.escape(str(item.get('issue_type') or 'issue'))}</strong>: {html.escape(str(item.get('details') or ''))}</li>"
            for item in practice.get("encountered_issues", [])
        ) or "<li>No explicit issues logged in the source report.</li>"

        note_items = "".join(
            f"<li>{html.escape(note)}</li>" for note in practice.get("probably_true", [])
        ) or "<li>No analyst summary notes captured.</li>"

        follow_up_items = "".join(
            f"<li>{html.escape(note)}</li>" for note in practice.get("needs_follow_up", [])
        ) or "<li>No follow-up items captured.</li>"

        signal_items = "".join(
            (
                "<li>"
                f"<strong>{html.escape(signal['label'])}</strong> "
                f"<span class=\"mono\">{html.escape(signal['display_value'])}</span> "
                f"<span class=\"meta\">({signal['rank']}/{signal['out_of']})</span>"
                "</li>"
            )
            for signal in practice["signal_scores"]
        )
        subjective_scores = practice.get("subjective_scores", {}) or {}
        subjective_items = "".join(
            (
                "<div class=\"subjective-metric\">"
                f"<div class=\"subjective-label\" title=\"{html.escape(field['description'], quote=True)}\">{html.escape(field['label'])}</div>"
                f"<div class=\"subjective-value\">{html.escape(str(subjective_scores.get(field['key']) or '-'))}<span>/5</span></div>"
                "</div>"
            )
            for field in SUBJECTIVE_SCORE_FIELDS
        )
        subjective_scored_on = html.escape(str(subjective_scores.get("scored_on") or "-"))

        practice_rows.append(
            "<tr "
            f'class="practice-row" data-target="{detail_id}" tabindex="0" aria-expanded="false"'
            f' data-rank="{practice["relative_rank"]}"'
            f' data-practice="{html.escape((practice["practice_name"] or "").lower(), quote=True)}"'
            f' data-score="{practice["relative_score"]}"'
            f' data-overall="{float(overall_good) if overall_good is not None else -1}"'
            f' data-website="{float(website_easy) if website_easy is not None else -1}"'
            f' data-clicks="{float(clicks) if isinstance(clicks, (int, float)) else -1}"'
            f' data-issues="{issues}"'
            f' data-platforms="{html.escape(platforms.lower(), quote=True)}"'
            f' data-google="{float(google_score) if google_score is not None else -1}">'
            f"<td class=\"rank\">{practice['relative_rank']}</td>"
            f"<td><div class=\"practice-name\">{html.escape(practice['practice_name'])}</div><div class=\"practice-sub\">{html.escape(practice['website_identity'] or '-')}</div></td>"
            f"<td><span class=\"score\">{practice['relative_score']:.1f}</span><div class=\"practice-sub\">{html.escape(practice['relative_band'])}</div></td>"
            f"<td>{overall_display}</td>"
            f"<td>{website_display}</td>"
            f"<td>{clicks_display}</td>"
            f"<td>{issues}</td>"
            f"<td>{html.escape(platforms)}</td>"
            f"<td>{google_display}</td>"
            "</tr>"
            f"<tr id=\"{detail_id}\" class=\"detail-row\" hidden>"
            "<td colspan=\"9\">"
            "<div class=\"detail-shell\">"
            f"<p class=\"headline\">{html.escape(practice.get('headline') or '')}</p>"
            "<div class=\"detail-grid\">"
            "<section class=\"detail-card\">"
            "<h3>Relative Standing</h3>"
            f"<p><strong>#{practice['relative_rank']} of {practice['relative_rank_out_of']}</strong> on the composite relative score.</p>"
            f"<p class=\"compact\">Judgement summary: {html.escape(str(practice.get('subjective_scores', {}).get('summary') or '-'))}</p>"
            f"<p class=\"compact\">Strengths: {html.escape('; '.join(practice['strengths']) or '-')}</p>"
            f"<p class=\"compact\">Cautions: {html.escape('; '.join(practice['cautions']) or '-')}</p>"
            "</section>"
            "<section class=\"detail-card\">"
            "<h3>Subjective Scorecard</h3>"
            "<p class=\"compact\">These are the six judgement fields added directly to the source report and used to drive the default report usability ordering.</p>"
            f"<div class=\"subjective-grid\">{subjective_items}</div>"
            f"<p class=\"compact meta\">Scored on {subjective_scored_on} using a 1-5 scale where higher is better.</p>"
            "</section>"
            "<section class=\"detail-card\">"
            "<h3>Source Signals</h3>"
            "<ul class=\"compact-list\">"
            f"<li>Median runtime: <span class=\"mono\">{html.escape(format_runtime(practice['report_signals']['median_runtime_ms']))}</span></li>"
            f"<li>Discovered paths: <span class=\"mono\">{practice['report_signals']['discovered_path_count']}</span></li>"
            f"<li>Task checks: <span class=\"mono\">{practice['report_signals']['task_count']}</span></li>"
            f"<li>Source pages: <span class=\"mono\">{practice['report_signals']['source_page_count']}</span></li>"
            "</ul>"
            "</section>"
            "<section class=\"detail-card\">"
            "<h3>Links</h3>"
            "<ul class=\"compact-list\">"
            f"<li><a href=\"{html.escape(str(practice.get('website_url') or '#'))}\" target=\"_blank\" rel=\"noreferrer\">Public website</a></li>"
            f"<li><a href=\"{html.escape(practice['report_link'])}\" target=\"_blank\" rel=\"noreferrer\">Source report JSON</a></li>"
            "</ul>"
            "</section>"
            "</div>"
            "<div class=\"detail-grid wide\">"
            "<section class=\"detail-card wide\">"
            "<h3>Signal Breakdown</h3>"
            f"<ul class=\"signal-list\">{signal_items}</ul>"
            "</section>"
            "<section class=\"detail-card wide\">"
            "<h3>Task Overview</h3>"
            "<div class=\"table-wrap\">"
            "<table class=\"nested-table\">"
            "<thead><tr><th>Task</th><th>Clicks</th><th>First actionable page</th><th>First friction note</th></tr></thead>"
            f"<tbody>{''.join(task_rows)}</tbody>"
            "</table>"
            "</div>"
            "</section>"
            "<section class=\"detail-card\">"
            "<h3>Encountered Issues</h3>"
            f"<ul class=\"compact-list\">{issue_items}</ul>"
            "</section>"
            "<section class=\"detail-card\">"
            "<h3>Analyst View</h3>"
            f"<ul class=\"compact-list\">{note_items}</ul>"
            "</section>"
            "<section class=\"detail-card\">"
            "<h3>Needs Follow-up</h3>"
            f"<ul class=\"compact-list\">{follow_up_items}</ul>"
            "</section>"
            "</div>"
            "<details class=\"payload\">"
            "<summary>Raw ranking payload</summary>"
            f"<pre>{json_script(practice)}</pre>"
            "</details>"
            "</div>"
            "</td>"
            "</tr>"
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Practice Relative Rankings</title>
  <style>
    :root {{
      --bg: #f4efe6;
      --panel: rgba(255, 252, 246, 0.92);
      --ink: #1d2428;
      --muted: #5d686f;
      --line: #d5c8b4;
      --accent: #0e5a46;
      --accent-soft: #dff1e6;
      --warning: #7c402a;
      --warning-soft: #f5e3d7;
      --mono: "IBM Plex Mono", "SFMono-Regular", Consolas, monospace;
      --serif: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", Palatino, Georgia, serif;
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      color: var(--ink);
      font-family: var(--serif);
      background:
        radial-gradient(circle at top left, rgba(14, 90, 70, 0.10), transparent 32%),
        radial-gradient(circle at top right, rgba(124, 64, 42, 0.12), transparent 28%),
        linear-gradient(180deg, #f7f1e7 0%, var(--bg) 100%);
    }}

    main {{
      max-width: 1440px;
      margin: 0 auto;
      padding: 32px 20px 64px;
    }}

    h1, h2, h3, th, .score, .rank, .practice-name {{
      font-family: var(--mono);
    }}

    h1 {{
      margin: 0 0 10px;
      font-size: clamp(2rem, 3.2vw, 3.5rem);
      letter-spacing: 0.03em;
      text-transform: uppercase;
    }}

    .lede {{
      max-width: 880px;
      color: var(--muted);
      font-size: 1.05rem;
      line-height: 1.6;
      margin: 0 0 24px;
    }}

    .summary-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 14px;
      margin-bottom: 28px;
    }}

    .summary-card,
    .table-shell,
    .detail-shell {{
      background: var(--panel);
      backdrop-filter: blur(8px);
      border: 1px solid var(--line);
      box-shadow: 0 18px 44px rgba(36, 38, 31, 0.08);
    }}

    .summary-card {{
      padding: 18px;
      border-radius: 18px;
    }}

    .summary-card h2 {{
      font-size: 0.8rem;
      margin: 0 0 10px;
      color: var(--muted);
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}

    .summary-card p {{
      margin: 0;
      font-size: 1.8rem;
    }}

    .summary-card.summary-card-plain p {{
      font-size: 1rem;
      line-height: 1.6;
      font-family: var(--serif);
      color: var(--ink);
    }}

    .summary-list {{
      margin: 0;
      padding-left: 18px;
      line-height: 1.55;
    }}

    .summary-list li {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 8px;
      font-size: 0.95rem;
    }}

    .summary-card .small {{
      margin-top: 8px;
      color: var(--muted);
      font-size: 0.95rem;
      line-height: 1.5;
    }}

    .summary-card .small p {{
      margin: 0 0 10px;
    }}

    .summary-card .small p:last-child {{
      margin-bottom: 0;
    }}

    .chart-shell {{
      margin-bottom: 28px;
      padding: 22px;
      border-radius: 24px;
      background: var(--panel);
      border: 1px solid var(--line);
      box-shadow: 0 18px 44px rgba(36, 38, 31, 0.08);
    }}

    .chart-copy {{
      max-width: 860px;
      margin-bottom: 14px;
    }}

    .chart-copy h2 {{
      margin: 0 0 8px;
      font-size: 0.92rem;
      color: var(--muted);
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}

    .chart-copy p {{
      margin: 0;
      line-height: 1.6;
      color: var(--muted);
    }}

    .chart-wrap {{
      overflow-x: auto;
      border-radius: 18px;
      background: linear-gradient(180deg, rgba(255, 255, 255, 0.65), rgba(246, 239, 229, 0.9));
      border: 1px solid rgba(29, 36, 40, 0.08);
      padding: 10px;
    }}

    .chart-wrap svg {{
      width: 100%;
      min-width: 900px;
      height: auto;
      display: block;
    }}

    .chart-grid {{
      stroke: rgba(29, 36, 40, 0.1);
      stroke-dasharray: 4 6;
    }}

    .chart-axis {{
      stroke: rgba(29, 36, 40, 0.22);
      stroke-width: 1.2;
    }}

    .chart-axis-label,
    .chart-axis-title {{
      fill: var(--muted);
      font-family: var(--mono);
      font-size: 12px;
      letter-spacing: 0.03em;
      text-transform: uppercase;
    }}

    .chart-point {{
      transition: transform 140ms ease;
    }}

    .chart-point:hover {{
      transform: scale(1.18);
    }}

    .chart-legend {{
      display: flex;
      flex-wrap: wrap;
      gap: 14px 20px;
      margin: 14px 0 0;
      padding: 0;
      list-style: none;
      color: var(--muted);
      font-family: var(--mono);
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}

    .chart-legend li {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }}

    .legend-swatch {{
      display: inline-block;
      width: 18px;
      height: 3px;
      border-radius: 999px;
    }}

    .warning-bar {{
      margin: 0 0 28px;
      padding: 16px 20px;
      border-radius: 18px;
      background:
        linear-gradient(135deg, rgba(235, 135, 59, 0.92), rgba(201, 92, 34, 0.94));
      color: #fff8f1;
      box-shadow: 0 18px 44px rgba(146, 74, 29, 0.2);
    }}

    .warning-bar p {{
      margin: 0;
      font-size: 1rem;
      line-height: 1.65;
    }}

    .warning-bar strong {{
      font-family: var(--mono);
      text-transform: uppercase;
      letter-spacing: 0.06em;
      font-size: 0.82rem;
    }}

    .caveat-card {{
      position: relative;
      overflow: hidden;
      background:
        linear-gradient(135deg, rgba(124, 64, 42, 0.10), rgba(255, 252, 246, 0.92) 35%),
        var(--panel);
      border-color: rgba(124, 64, 42, 0.28);
    }}

    .caveat-card::before {{
      content: "Experimental";
      position: absolute;
      top: 16px;
      right: 18px;
      padding: 5px 9px;
      border-radius: 999px;
      background: var(--warning-soft);
      color: var(--warning);
      font-family: var(--mono);
      font-size: 0.72rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}

    .caveat-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}

    .caveat-note {{
      padding: 14px;
      border-radius: 14px;
      background: rgba(255, 255, 255, 0.68);
      border: 1px solid rgba(124, 64, 42, 0.14);
    }}

    .caveat-note strong {{
      display: block;
      margin-bottom: 6px;
      font-family: var(--mono);
      font-size: 0.8rem;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: var(--warning);
    }}

    .table-shell {{
      overflow: hidden;
      border-radius: 24px;
    }}

    .table-wrap {{
      overflow-x: auto;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
    }}

    thead {{
      background: rgba(29, 36, 40, 0.04);
    }}

    th, td {{
      padding: 14px 12px;
      border-bottom: 1px solid rgba(29, 36, 40, 0.08);
      text-align: left;
      vertical-align: top;
    }}

    th {{
      font-size: 0.76rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
    }}

    .sort-button {{
      border: 0;
      background: transparent;
      padding: 0;
      width: 100%;
      text-align: left;
      color: inherit;
      font: inherit;
      text-transform: inherit;
      letter-spacing: inherit;
      cursor: pointer;
    }}

    .sort-button::after {{
      content: "";
      margin-left: 6px;
    }}

    .sort-button[data-sort-direction="asc"]::after {{
      content: "▲";
    }}

    .sort-button[data-sort-direction="desc"]::after {{
      content: "▼";
    }}

    .practice-row {{
      cursor: pointer;
      transition: background-color 140ms ease, transform 140ms ease;
    }}

    .practice-row:hover,
    .practice-row:focus {{
      background: rgba(14, 90, 70, 0.07);
      outline: none;
    }}

    .practice-row[aria-expanded="true"] {{
      background: rgba(14, 90, 70, 0.09);
    }}

    .rank {{
      width: 60px;
      font-size: 1.1rem;
      color: var(--accent);
    }}

    .score {{
      display: inline-block;
      min-width: 3.5ch;
      font-size: 1.15rem;
      color: var(--accent);
    }}

    .practice-name {{
      font-size: 0.95rem;
      margin-bottom: 4px;
    }}

    .practice-sub {{
      color: var(--muted);
      font-size: 0.86rem;
      line-height: 1.45;
    }}

    .detail-row td {{
      padding: 0;
      background: rgba(255, 250, 241, 0.92);
    }}

    .detail-shell {{
      padding: 22px;
      border-radius: 0;
      border-left: 0;
      border-right: 0;
      border-bottom: 0;
    }}

    .headline {{
      margin: 0 0 18px;
      font-size: 1.02rem;
      line-height: 1.65;
    }}

    .detail-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 14px;
      margin-bottom: 14px;
    }}

    .detail-grid.wide {{
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    }}

    .detail-card {{
      background: rgba(255, 255, 255, 0.66);
      border: 1px solid rgba(29, 36, 40, 0.08);
      border-radius: 16px;
      padding: 16px;
    }}

    .detail-card.wide {{
      grid-column: span 2;
    }}

    .detail-card h3 {{
      margin: 0 0 10px;
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
    }}

    .subjective-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: 10px;
      margin: 12px 0;
    }}

    .subjective-metric {{
      padding: 14px;
      border-radius: 14px;
      background:
        linear-gradient(180deg, rgba(14, 90, 70, 0.1), rgba(255, 255, 255, 0.8)),
        rgba(255, 255, 255, 0.72);
      border: 1px solid rgba(14, 90, 70, 0.14);
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.75);
    }}

    .subjective-label {{
      margin-bottom: 8px;
      color: var(--muted);
      font-family: var(--mono);
      font-size: 0.76rem;
      line-height: 1.4;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }}

    .subjective-value {{
      font-family: var(--mono);
      display: flex;
      align-items: baseline;
      gap: 4px;
      font-size: 1.45rem;
      color: var(--accent);
    }}

    .subjective-value span {{
      margin-left: 4px;
      font-size: 0.85rem;
      color: var(--muted);
    }}

    .compact {{
      margin: 0 0 8px;
      line-height: 1.55;
    }}

    .compact-list,
    .signal-list {{
      margin: 0;
      padding-left: 18px;
      line-height: 1.55;
    }}

    .signal-list li,
    .compact-list li {{
      margin-bottom: 6px;
    }}

    .nested-table th,
    .nested-table td {{
      padding: 10px 8px;
      font-size: 0.92rem;
    }}

    a {{
      color: var(--accent);
    }}

    .meta,
    .mono {{
      font-family: var(--mono);
    }}

    .meta {{
      color: var(--muted);
      font-size: 0.86rem;
    }}

    .payload {{
      margin-top: 14px;
      border-top: 1px dashed var(--line);
      padding-top: 14px;
    }}

    .payload summary {{
      cursor: pointer;
      font-family: var(--mono);
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--muted);
    }}

    pre {{
      margin: 12px 0 0;
      padding: 14px;
      overflow: auto;
      background: #1d2428;
      color: #f5efe3;
      border-radius: 14px;
      font-size: 0.8rem;
      line-height: 1.5;
    }}

    @media (max-width: 900px) {{
      main {{
        padding: 24px 12px 48px;
      }}

      th,
      td {{
        padding: 12px 8px;
      }}

      .detail-card.wide {{
        grid-column: auto;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <h1>Practice Relative Rankings</h1>
    <p class="lede">
      Exploratory relative standing across the {rankings["practice_count"]} reviewed practice reports generated on {html.escape(rankings["generated_at"])}.
      Click any practice row to expand a mined overview from the source JSON, including task routes, issue notes, analyst observations, and the signal breakdown used in the cohort ranking.
    </p>
    <section class="summary-grid">
      <article class="summary-card">
        <h2>Coverage</h2>
        <p>{rankings["practice_count"]}</p>
        <div class="small">
          <p>Reviewed practices in this cohort.</p>
          <p><strong>Conclusion:</strong> A technically poor website <em>doesn't guarantee</em> bad reviews or bad survey results, at least not to the degree we could measure it here.</p>
        </div>
      </article>
      <article class="summary-card summary-card-plain">
        <h2>Method</h2>
        <p>Report-only ranking</p>
        <div class="small">
          <p>{html.escape(rankings["methodology"]["summary"])}</p>
          <p>The default order is driven by six subjective report fields: front-door clarity, task coverage, journey ease, trust and maintenance, complaints and fallbacks, and overall patient usability.</p>
        </div>
      </article>
      <article class="summary-card">
        <h2>Top Five</h2>
        {render_practice_list(rankings["top_five"])}
        <div class="small">Highest current cohort positions by composite relative score.</div>
      </article>
      <article class="summary-card">
        <h2>Bottom Five</h2>
        {render_practice_list(rankings["bottom_five"])}
        <div class="small">Current cohort tail positions, not an absolute quality judgement.</div>
      </article>
    </section>
    <section class="warning-bar">
      <p><strong>Measurement limits</strong> Lack of clarity is probably down to our measurement method being unable to effectively copy real user behaviour because of captchas, redirects and basic limits of what an LLM can convert into meaningful signals. We will try revisiting this in future.</p>
    </section>
    {render_comparison_chart()}
    <section class="table-shell">
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th><button type="button" class="sort-button" data-sort-key="rank" data-sort-type="number" data-sort-direction="asc" title="{html.escape(header_tooltips['rank'], quote=True)}" aria-label="{html.escape(header_tooltips['rank'], quote=True)}">#</button></th>
              <th><button type="button" class="sort-button" data-sort-key="practice" data-sort-type="text" title="{html.escape(header_tooltips['practice'], quote=True)}" aria-label="{html.escape(header_tooltips['practice'], quote=True)}">Practice</button></th>
              <th><button type="button" class="sort-button" data-sort-key="score" data-sort-type="number" title="{html.escape(header_tooltips['score'], quote=True)}" aria-label="{html.escape(header_tooltips['score'], quote=True)}">Report usability score</button></th>
              <th><button type="button" class="sort-button" data-sort-key="overall" data-sort-type="number" title="{html.escape(header_tooltips['overall'], quote=True)}" aria-label="{html.escape(header_tooltips['overall'], quote=True)}">GPPS overall</button></th>
              <th><button type="button" class="sort-button" data-sort-key="website" data-sort-type="number" title="{html.escape(header_tooltips['website'], quote=True)}" aria-label="{html.escape(header_tooltips['website'], quote=True)}">GPPS website</button></th>
              <th><button type="button" class="sort-button" data-sort-key="clicks" data-sort-type="number" title="{html.escape(header_tooltips['clicks'], quote=True)}" aria-label="{html.escape(header_tooltips['clicks'], quote=True)}">Avg clicks</button></th>
              <th><button type="button" class="sort-button" data-sort-key="issues" data-sort-type="number" title="{html.escape(header_tooltips['issues'], quote=True)}" aria-label="{html.escape(header_tooltips['issues'], quote=True)}">Issues</button></th>
              <th><button type="button" class="sort-button" data-sort-key="platforms" data-sort-type="text" title="{html.escape(header_tooltips['platforms'], quote=True)}" aria-label="{html.escape(header_tooltips['platforms'], quote=True)}">Platforms</button></th>
              <th><button type="button" class="sort-button" data-sort-key="google" data-sort-type="number" title="{html.escape(header_tooltips['google'], quote=True)}" aria-label="{html.escape(header_tooltips['google'], quote=True)}">Google</button></th>
            </tr>
          </thead>
          <tbody>
            {''.join(practice_rows)}
          </tbody>
        </table>
      </div>
    </section>
    <section class="summary-grid">
      <article class="summary-card caveat-card" style="grid-column: 1 / -1;">
        <h2>Caveats</h2>
        <div class="small">
          <p>This page is an exploratory first pass. The ordering is meant to answer one narrow question: if we rank practices only by what the auto-reports say about website usability, do the Google review and GP Patient Survey columns end up in roughly the places we would expect if there is any correlation at all?</p>
          <div class="caveat-grid">
            <div class="caveat-note">
              <strong>Weak signal</strong>
              Within this small sample the current report-only ranking does show some apparent relationship between lower Google scores and more issues found, but that could still be noise, prompt bias, or coincidence.
            </div>
            <div class="caveat-note">
              <strong>Click counts look flat</strong>
              Average click counts near 1.0, or similarly round fractional values, suggest either the patterns really are very flat or our click capture and summarisation are compressing differences too aggressively.
            </div>
            <div class="caveat-note">
              <strong>LLM caveat</strong>
              The issue counts and friction notes are not a clean ground-truth audit. The model may have picked issues that fit an apparent pattern instead of measuring how many issues actually exist on each real website.
            </div>
            <div class="caveat-note">
              <strong>Likely next use</strong>
              The fuller per-practice review payloads may still let us compare recurring issue types across practices more usefully than this simple ranking can.
            </div>
          </div>
          <p>The current read is that basic website quality or reliability alone, whether pages load fast enough or whether the route technically works, is probably not the main driver here. What may matter more is the design choice layer: whether the route is clear, coherent, and actually effective for patients once they arrive.</p>
          <p>Use this only for this specific process. It should not be trusted as a general ranking, a causal claim, or a reliable count of real website problems outside this experimental workflow.</p>
        </div>
      </article>
    </section>
  </main>
  <script>
    const rows = document.querySelectorAll(".practice-row");
    const tbody = document.querySelector("tbody");
    const sortButtons = document.querySelectorAll(".sort-button");
    function toggleRow(row) {{
      const targetId = row.getAttribute("data-target");
      const detail = document.getElementById(targetId);
      const expanded = row.getAttribute("aria-expanded") === "true";
      row.setAttribute("aria-expanded", expanded ? "false" : "true");
      detail.hidden = expanded;
    }}
    function sortTable(key, type, direction) {{
      const pairs = Array.from(document.querySelectorAll(".practice-row")).map((row) => {{
        const detail = document.getElementById(row.getAttribute("data-target"));
        return {{ row, detail }};
      }});
      pairs.sort((left, right) => {{
        const leftValue = left.row.dataset[key] ?? "";
        const rightValue = right.row.dataset[key] ?? "";
        let comparison = 0;
        if (type === "number") {{
          comparison = Number(leftValue) - Number(rightValue);
        }} else {{
          comparison = leftValue.localeCompare(rightValue);
        }}
        return direction === "asc" ? comparison : -comparison;
      }});
      for (const pair of pairs) {{
        tbody.appendChild(pair.row);
        tbody.appendChild(pair.detail);
      }}
    }}
    rows.forEach((row) => {{
      row.addEventListener("click", (event) => {{
        if (event.target.closest("a")) {{
          return;
        }}
        toggleRow(row);
      }});
      row.addEventListener("keydown", (event) => {{
        if (event.key === "Enter" || event.key === " ") {{
          event.preventDefault();
          toggleRow(row);
        }}
      }});
    }});
    sortButtons.forEach((button) => {{
      button.addEventListener("click", () => {{
        const current = button.getAttribute("data-sort-direction");
        const next = current === "asc" ? "desc" : "asc";
        sortButtons.forEach((item) => item.removeAttribute("data-sort-direction"));
        button.setAttribute("data-sort-direction", next);
        sortTable(button.dataset.sortKey, button.dataset.sortType, next);
      }});
    }});
  </script>
</body>
</html>
"""
