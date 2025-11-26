// deep-compare-dna.js
// Usage:
//   node deep-compare-dna.js <file1.csv> [file2.csv ...] --ods Y02960 [--scope subicb|pcn|supplier|all]
//
// Outputs JSON with:
// - Overall + per-month DNA rates for the target practice
// - By HCP_TYPE, APPT_MODE, NATIONAL_CATEGORY
// - Time-to-appt DNA profile + correlation with waiting time
// - Cohort comparisons (distribution, percentile, z-scores) within chosen scope and per-APPT_MODE
//
// Notes: expects columns exactly as shown in your sample; APPT_STATUS normalised (DNA / Did not attend).
// Scope chooses which practices to benchmark target against: sub-ICB (default), PCN, Supplier, or All.

import fs from "node:fs";
import { parse } from "csv-parse/sync";

const argv = process.argv.slice(2);
if (!argv.length) bail("usage: node deep-compare-dna.js <file1.csv> [file2.csv ...] --ods Y02960 [--scope subicb|pcn|supplier|all]");
const odsIdx = argv.indexOf("--ods");
if (odsIdx === -1 || odsIdx + 1 >= argv.length) bail("missing --ods <CODE>");
const TARGET_ODS = argv[odsIdx + 1].trim().toUpperCase();
const scopeArg = (() => {
  const i = argv.indexOf("--scope");
  return i !== -1 && i + 1 < argv.length ? argv[i + 1].toLowerCase() : "subicb";
})();
const files = argv.filter((a, i) => i !== odsIdx && i !== odsIdx + 1 && a !== "--scope" && a !== scopeArg);

// ---------------- utils ----------------
const norm = s => String(s ?? "").trim();
const lc = s => norm(s).toLowerCase();
const toNum = v => {
  if (v == null) return 0;
  const n = Number(String(v).replace(/[, ]/g,""));
  return Number.isFinite(n) ? n : 0;
};
const add = (o,k,v)=>{o[k]=(o[k]||0)+v;};
const groupBy = (arr, keyFn) => {
  const m = new Map();
  for (const x of arr) {
    const k = keyFn(x);
    const a = m.get(k); if (a) a.push(x); else m.set(k,[x]);
  }
  return m;
};
const mean = xs => xs.length ? xs.reduce((a,b)=>a+b,0)/xs.length : 0;
const std = xs => {
  if (xs.length < 2) return 0;
  const m = mean(xs);
  const v = mean(xs.map(x => (x - m) ** 2));
  return Math.sqrt(v);
};
const percentileRank = (xs, v) => {
  const n = xs.length;
  if (!n) return 0;
  const less = xs.filter(x => x < v).length;
  const equal = xs.filter(x => x === v).length;
  return ((less + 0.5*equal) / n) * 100;
};

// time bucket ordering + numeric proxy for correlation
const timeOrder = [
  "same day","1 day","2  to 7 days","8  to 14 days","15  to 21 days","22  to 28 days","more than 28 days"
];
const timeMid = new Map([
  ["same day", 0],
  ["1 day", 1],
  ["2  to 7 days", 4.5],
  ["8  to 14 days", 11],
  ["15  to 21 days", 18],
  ["22  to 28 days", 25],
  ["more than 28 days", 35],
]);
function corrPearson(x, y, w=null) {
  const n = x.length;
  if (n === 0 || y.length !== n) return NaN;
  if (w && w.length !== n) w = null;
  let wx=0, wy=0, wsum=0;
  for (let i=0;i<n;i++){
    const wi = w ? w[i] : 1;
    wsum += wi; wx += wi*x[i]; wy += wi*y[i];
  }
  const mx = wx/wsum, my = wy/wsum;
  let num=0, dx2=0, dy2=0;
  for (let i=0;i<n;i++){
    const wi = w ? w[i] : 1;
    const dx = x[i]-mx, dy=y[i]-my;
    num += wi*dx*dy; dx2 += wi*dx*dx; dy2 += wi*dy*dy;
  }
  return (dx2>0 && dy2>0) ? (num/Math.sqrt(dx2*dy2)) : NaN;
}

// ---------------- load ----------------
const rows = [];
for (const f of files) {
  const text = fs.readFileSync(f, "utf8");
  const recs = parse(text, { columns: true, skip_empty_lines: true });
  for (const r of recs) {
    rows.push({
      month: norm(r["APPOINTMENT_MONTH_START_DATE"]),
      ods: norm(r["GP_CODE"]).toUpperCase(),
      name: norm(r["GP_NAME"]),
      supplier: norm(r["SUPPLIER"]),
      pcn_code: norm(r["PCN_CODE"]),
      pcn_name: norm(r["PCN_NAME"]),
      subicb_code: norm(r["SUB_ICB_LOCATION_CODE"]),
      subicb_name: norm(r["SUB_ICB_LOCATION_NAME"]),
      hcp: norm(r["HCP_TYPE"]),
      mode: norm(r["APPT_MODE"]),
      category: norm(r["NATIONAL_CATEGORY"]),
      ttb: norm(r["TIME_BETWEEN_BOOK_AND_APPT"]),
      count: toNum(r["COUNT_OF_APPOINTMENTS"]),
      status: (() => {
        const s = lc(r["APPT_STATUS"]);
        if (s === "dna" || s === "did not attend") return "DNA";
        if (s === "attended") return "Attended";
        if (s === "unknown") return "Unknown";
        if (s === "patient cancelled") return "Patient cancelled";
        if (s === "practice cancelled") return "Practice cancelled";
        return norm(r["APPT_STATUS"]); // fallback
      })()
    });
  }
}

if (!rows.length) bail("no rows loaded");

// ---------------- identify target + cohort ----------------
const targetRows = rows.filter(r => r.ods === TARGET_ODS);
if (!targetRows.length) bail(`ODS ${TARGET_ODS} not found in provided files`);

const targetMeta = (() => {
  const any = targetRows[0];
  return {
    ods: TARGET_ODS,
    name: any.name,
    supplier: any.supplier,
    pcn_code: any.pcn_code, pcn_name: any.pcn_name,
    subicb_code: any.subicb_code, subicb_name: any.subicb_name,
  };
})();

function inScope(r) {
  if (scopeArg === "all") return true;
  if (scopeArg === "pcn") return r.pcn_code && r.pcn_code === targetMeta.pcn_code;
  if (scopeArg === "supplier") return r.supplier && r.supplier === targetMeta.supplier;
  // default sub-ICB:
  return r.subicb_code && r.subicb_code === targetMeta.subicb_code;
}
const cohortRows = rows.filter(inScope);

// ---------------- aggregations ----------------
function aggBy(keys, filt = null) {
  const m = new Map();
  for (const r of (filt ? rows.filter(filt) : rows)) {
    const k = keys.map(k => r[k] ?? "").join("¦");
    let rec = m.get(k);
    if (!rec) {
      rec = { key: k, total:0, dna:0, attended:0, unknown:0, pcancel:0, pracancel:0 };
      m.set(k, rec);
    }
    rec.total += r.count;
    if (r.status === "DNA") rec.dna += r.count;
    else if (r.status === "Attended") rec.attended += r.count;
    else if (r.status === "Unknown") rec.unknown += r.count;
    else if (r.status === "Patient cancelled") rec.pcancel += r.count;
    else if (r.status === "Practice cancelled") rec.pracancel += r.count;
  }
  return m;
}

function toRate(dna, total){ return total>0 ? dna/total : 0; }

// Target: overall, per month
const targAll = aggBy(["ods"], r => r.ods === TARGET_ODS).get(TARGET_ODS);
const targByMonth = aggBy(["month"], r => r.ods === TARGET_ODS);
const months = [...targByMonth.entries()].map(([k,v]) => ({ month:k, dna:v.dna, total:v.total, rate: toRate(v.dna,v.total) }))
  .sort((a,b)=>a.month.localeCompare(b.month));

// Target by HCP, Mode, Category
const targByHcp = aggBy(["hcp"], r => r.ods === TARGET_ODS);
const targByMode = aggBy(["mode"], r => r.ods === TARGET_ODS);
const targByCat  = aggBy(["category"], r => r.ods === TARGET_ODS);

// Target by time-to-book buckets + correlation
const targByTTB = aggBy(["ttb"], r => r.ods === TARGET_ODS);
const ttbRows = [...targByTTB.entries()].map(([k,v]) => {
  const key = k.toLowerCase();
  const ord = timeOrder.indexOf(key);
  const days = timeMid.has(key) ? timeMid.get(key) : (ord >=0 ? ord : null);
  return { bucket: k, days, dna: v.dna, total: v.total, rate: toRate(v.dna,v.total) };
}).filter(r => r.total>0);
const corr = (() => {
  const xs = ttbRows.filter(r => r.days != null).map(r => r.days);
  const ys = ttbRows.filter(r => r.days != null).map(r => r.rate);
  const ws = ttbRows.filter(r => r.days != null).map(r => r.total);
  return Number.isFinite(corrPearson(xs, ys, ws)) ? corrPearson(xs, ys, ws) : null;
})();

// Cohort distributions (per practice), overall + per APPT_MODE
function perPracticeRates(srcRows, modeFilter = null) {
  const byPractice = new Map();
  for (const r of srcRows) {
    if (modeFilter && r.mode !== modeFilter) continue;
    const k = r.ods;
    let rec = byPractice.get(k);
    if (!rec) rec = { ods: k, total:0, dna:0 };
    rec.total += r.count;
    if (r.status === "DNA") rec.dna += r.count;
    byPractice.set(k, rec);
  }
  const out = [];
  for (const v of byPractice.values()) {
    if (v.total > 0) out.push(v.dna / v.total);
  }
  return out;
}

const cohortRatesOverall = perPracticeRates(cohortRows);
const targetRateOverall = toRate(targAll.dna, targAll.total);
const cohortStatsOverall = (() => {
  const dist = cohortRatesOverall;
  const m = mean(dist), s = std(dist);
  return {
    mean: m, sd: s,
    z: s>0 ? (targetRateOverall - m)/s : null,
    percentile: percentileRank(dist, targetRateOverall)
  };
})();

// Per-mode comparison
const modes = [...new Set(targetRows.map(r => r.mode))].filter(Boolean);
const perMode = modes.map(mode => {
  const targ = targByMode.get(mode);
  const tRate = toRate(targ?.dna||0, targ?.total||0);
  const dist = perPracticeRates(cohortRows, mode);
  const m = mean(dist), s = std(dist);
  return {
    mode,
    target: { dna: targ?.dna||0, total: targ?.total||0, rate: tRate },
    cohort: {
      members: dist.length,
      mean_rate: m,
      sd_rate: s,
      z: s>0 ? (tRate - m)/s : null,
      percentile: percentileRank(dist, tRate)
    }
  };
}).sort((a,b)=> (b.target.rate - a.target.rate));

// Supplier-only slice (helpful for “is it the system?”) — practice-level distribution within same supplier in scope
const supplier = targetMeta.supplier;
const supplierRows = cohortRows.filter(r => r.supplier === supplier);
const supplierRatesOverall = perPracticeRates(supplierRows);
const supplierStatsOverall = (() => {
  const dist = supplierRatesOverall;
  if (!dist.length) return null;
  const m = mean(dist), s = std(dist);
  return {
    supplier,
    mean: m, sd: s,
    z: s>0 ? (targetRateOverall - m)/s : null,
    percentile: percentileRank(dist, targetRateOverall),
    members: dist.length
  };
})();

// build nice tables
function mapMapToTable(m, labelKey) {
  return [...m.entries()].map(([k,v]) => ({
    [labelKey]: k,
    dna: v.dna, total: v.total, rate: toRate(v.dna,v.total)
  })).sort((a,b)=> b.rate - a.rate);
}

const out = {
  target: targetMeta,
  scope: scopeArg,
  overall: {
    months,
    totals: { dna: targAll.dna, total: targAll.total, rate: toRate(targAll.dna, targAll.total) },
    cohort_vs_scope: cohortStatsOverall,
    supplier_only_vs_scope: supplierStatsOverall
  },
  breakdowns: {
    by_hcp_type: mapMapToTable(targByHcp, "hcp_type"),
    by_mode: mapMapToTable(targByMode, "appt_mode"),
    by_category: mapMapToTable(targByCat, "national_category"),
    time_to_booking: {
      buckets: ttbRows.sort((a,b)=> (timeOrder.indexOf(a.bucket.toLowerCase()) - timeOrder.indexOf(b.bucket.toLowerCase()))),
      weighted_corr_wait_vs_dna: corr // positive => longer waits associated with higher DNA rate
    },
    per_mode_cohort_compare: perMode
  }
};

console.log(JSON.stringify(out, null, 2));

// --------------- helpers ---------------
function bail(msg){ console.error(msg); process.exit(1); }
