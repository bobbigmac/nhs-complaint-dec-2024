(function () {
  const embed = window.__RATING_CHANGE_EMBED__ || {};
  const months = embed.months || [];
  const series = embed.practice_series || [];
  const summaryEl = document.getElementById("summary");
  const listEl = document.getElementById("chart-list");

  function linePath(points, xScale, yScale) {
    let path = "";
    points.forEach((value, index) => {
      if (value === null || !Number.isFinite(value)) return;
      const command = path ? "L" : "M";
      path += `${command}${xScale(index).toFixed(2)} ${yScale(value).toFixed(2)} `;
    });
    return path.trim();
  }

  function formatDelta(delta) {
    if (delta === null || delta === undefined || !Number.isFinite(delta)) return "—";
    const sign = delta > 0 ? "+" : "";
    return `${sign}${delta.toFixed(2)}`;
  }

  function deltaClass(delta) {
    if (delta === null || delta === undefined || !Number.isFinite(delta)) return "is-flat";
    if (delta > 0.0005) return "is-up";
    if (delta < -0.0005) return "is-down";
    return "is-flat";
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  if (summaryEl) {
    const n = embed.practices_with_review_history ?? series.length;
    const total = embed.dataset_practice_count ?? 0;
    const parsed = embed.parsed_review_count ?? 0;
    const anchor = embed.anchor_date || "";
    const missing = (embed.missing_practices || []).length;
    summaryEl.textContent = `${n} of ${total} Manchester-dataset practices have enough dated Google reviews to plot a cumulative average trajectory (${parsed} dated reviews parsed; scrape anchor ${anchor}). Charts share the same month axis (widest span in this dataset). Sorted by change in cumulative average (latest minus first month with data), largest improvement first.${missing ? ` ${missing} practices have no usable dated history yet.` : ""}`;
  }

  if (!listEl) return;

  if (!months.length || !series.length) {
    listEl.innerHTML =
      '<p class="empty-state">No reconstructed review-month history yet. Merge Google Maps captures into <code>google_maps_recent_reviews.json</code> and rebuild the dataset.</p>';
    return;
  }

  const width = 1000;
  const height = 44;
  const margin = { top: 5, right: 6, bottom: 14, left: 6 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const yMin = 1;
  const yMax = 5;
  const yScale = (value) => margin.top + plotHeight - ((value - yMin) / (yMax - yMin)) * plotHeight;
  const xScale = (index) =>
    margin.left +
    (months.length <= 1 ? plotWidth / 2 : (index / (months.length - 1)) * plotWidth);

  const TREND_EPS = 1e-4;
  const FILL_UP = "rgba(76, 154, 82, 0.18)";
  const FILL_DOWN = "rgba(195, 71, 47, 0.16)";

  function edgeTrendDir(points, k) {
    const prev = points[k - 1];
    const curr = points[k];
    if (prev === null || curr === null || !Number.isFinite(prev) || !Number.isFinite(curr)) return null;
    const d = curr - prev;
    if (d > TREND_EPS) return "up";
    if (d < -TREND_EPS) return "down";
    return "same";
  }

  /** Merge consecutive month edges with the same up/down trend into one background span (per practice). */
  function buildTrendRuns(points) {
    const n = points.length;
    if (n < 2) return [];
    const step = n <= 1 ? plotWidth : plotWidth / (n - 1);
    const runs = [];
    let k = 1;
    while (k < n) {
      const dir = edgeTrendDir(points, k);
      if (dir !== "up" && dir !== "down") {
        k += 1;
        continue;
      }
      const startK = k;
      let endK = k;
      k += 1;
      while (k < n) {
        const d2 = edgeTrendDir(points, k);
        if (d2 !== dir) break;
        endK = k;
        k += 1;
      }
      const x1 = Math.max(margin.left, xScale(startK) - step / 2);
      const x2 = Math.min(width - margin.right, xScale(endK) + step / 2);
      if (x2 > x1) runs.push({ dir, x1, x2 });
    }
    return runs;
  }

  listEl.innerHTML = series
    .map((row) => {
      const points = row.points || [];
      const path = linePath(points, xScale, yScale);
      const stroke = row.gtd_managed ? "#0f5e9c" : "rgba(26,28,26,0.55)";
      const delta = row.delta;
      const codeAttr = escapeHtml(row.code || "");
      const label = escapeHtml(row.name || row.code || "");
      const gridLines = [1, 2, 3, 4, 5]
        .map(
          (tick) =>
            `<line x1="${margin.left}" y1="${yScale(tick).toFixed(2)}" x2="${width - margin.right}" y2="${yScale(tick).toFixed(2)}" stroke="rgba(26,28,26,0.06)" />`
        )
        .join("");
      const trendRuns = buildTrendRuns(points);
      const trendRects = trendRuns
        .map((run) => {
          const fill = run.dir === "up" ? FILL_UP : FILL_DOWN;
          const y1 = margin.top;
          const y2 = height - margin.bottom;
          return `<rect x="${run.x1.toFixed(2)}" y="${y1.toFixed(2)}" width="${(run.x2 - run.x1).toFixed(2)}" height="${(y2 - y1).toFixed(2)}" fill="${fill}" />`;
        })
        .join("");
      const pathMarkup = path
        ? `<path d="${path}" fill="none" stroke="${stroke}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />`
        : "";
      return `
        <div class="rating-row" data-code="${codeAttr}">
          <div class="rating-row-name">
            <div class="rating-row-title">${label}</div>
            <div class="rating-row-delta ${deltaClass(delta)}">Δ ${formatDelta(delta)}</div>
          </div>
          <div class="rating-row-chart">
            <svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="none" role="img" aria-label="Cumulative Google rating over time for ${label}">
              <title>Cumulative Google rating by month (reconstructed)</title>
              ${gridLines}
              ${trendRects}
              ${pathMarkup}
            </svg>
          </div>
        </div>`;
    })
    .join("");
})();
