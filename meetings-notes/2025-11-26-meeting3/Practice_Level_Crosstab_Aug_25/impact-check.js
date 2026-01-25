// impact-check.js
// Usage:
//   node impact-check.js <file1.csv> [file2.csv ...] --ods Y02960 [--scope subicb|pcn|supplier|all]
// Notes:
//   Expects columns exactly as in your sample. Handles multiple months.
//   Runs the 4 requested tests and adds extra mined insights.

import fs from "node:fs";
import { parse } from "csv-parse/sync";

// ---------- args ----------
const argv = process.argv.slice(2);
if (!argv.length) die("usage: node impact-check.js <file1.csv> [file2.csv ...] --ods Y02960 [--scope subicb|pcn|supplier|all]");
const odsIdx = argv.indexOf("--ods");
if (odsIdx === -1 || odsIdx + 1 >= argv.length) die("missing --ods <CODE>");
const TARGET_ODS = argv[odsIdx + 1].trim().toUpperCase();
const scopeArg = (() => {
  const i = argv.indexOf("--scope");
  return i !== -1 && i + 1 < argv.length ? argv[i + 1].toLowerCase() : "subicb";
})();
const files = argv.filter((a, i) => i !== odsIdx && i !== odsIdx + 1 && a !== "--scope" && a !== scopeArg);

// ---------- utils ----------
const norm = s => String(s ?? "").trim();
const lc = s => norm(s).toLowerCase();
const toNum = v => {
  if (v == null) return 0;
  const n = Number(String(v).replace(/[, ]/g, ""));
  return Number.isFinite(n) ? n : 0;
};
function die(msg){ console.error(msg); process.exit(1); }
const monthKey = s => {
  // "01AUG2025" -> YYYYMM as number for ordering
  const m = norm(s);
  const mon = m.slice(2,5).toUpperCase();
  const y = m.slice(5);
  const months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"];
  const mi = months.indexOf(mon);
  if (mi === -1) return NaN;
  return Number(y)*100 + (mi+1);
};
const monthsOrder = (a,b)=> monthKey(a) - monthKey(b);
const mean = xs => xs.length ? xs.reduce((a,b)=>a+b,0)/xs.length : 0;
const std = xs => {
  if (xs.length < 2) return 0;
  const m = mean(xs);
  return Math.sqrt(mean(xs.map(x => (x - m) ** 2)));
};
const percentileRank = (xs, v) => {
  const n = xs.length; if (!n) return 0;
  const less = xs.filter(x => x < v).length;
  const eq = xs.filter(x => x === v).length;
  return ((less + 0.5*eq) / n) * 100;
};
function corrPearson(x, y, w=null) {
  const n = x.length;
  if (!n || y.length !== n) return NaN;
  if (w && w.length !== n) w = null;
  let wsum=0, sx=0, sy=0;
  for (let i=0;i<n;i++){ const wi=w?w[i]:1; wsum+=wi; sx+=wi*x[i]; sy+=wi*y[i]; }
  const mx = sx/wsum, my=sy/wsum;
  let num=0, dx2=0, dy2=0;
  for (let i=0;i<n;i++){ const wi=w?w[i]:1; const dx=x[i]-mx, dy=y[i]-my; num+=wi*dx*dy; dx2+=wi*dx*dx; dy2+=wi*dy*dy; }
  return (dx2>0 && dy2>0) ? num/Math.sqrt(dx2*dy2) : NaN;
}
const timeMap = new Map([
  ["same day",0], ["1 day",1],
  ["2  to 7 days",4.5], ["2 to 7 days",4.5],
  ["8  to 14 days",11], ["8 to 14 days",11],
  ["15  to 21 days",18], ["15 to 21 days",18],
  ["22  to 28 days",25], ["22 to 28 days",25],
  ["more than 28 days",35],
]);

// ---------- load ----------
const rows = [];
for (const f of files) {
  const text = fs.readFileSync(f, "utf8");
  const recs = parse(text, { columns: true, skip_empty_lines: true });
  for (const r of recs) {
    const status = (() => {
      const s = lc(r["APPT_STATUS"]);
      if (s === "dna" || s === "did not attend") return "DNA";
      if (s === "attended") return "Attended";
      if (s === "unknown") return "Unknown";
      if (s === "patient cancelled") return "Patient cancelled";
      if (s === "practice cancelled") return "Practice cancelled";
      return norm(r["APPT_STATUS"]);
    })();
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
      status
    });
  }
}
if (!rows.length) die("no rows loaded");

// ---------- identify target + scope ----------
const targetRows = rows.filter(r => r.ods === TARGET_ODS);
if (!targetRows.length) die(`ODS ${TARGET_ODS} not found in provided files`);

const meta = (() => {
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
  if (scopeArg === "pcn") return r.pcn_code && r.pcn_code === meta.pcn_code;
  if (scopeArg === "supplier") return r.supplier && r.supplier === meta.supplier;
  // default sub-ICB
  return r.subicb_code && r.subicb_code === meta.subicb_code;
}
const cohortRows = rows.filter(inScope);

// ---------- helpers ----------
function agg(filter) {
  let total=0, dna=0;
  for (const r of rows) if (filter(r)){ total += r.count; if (r.status==="DNA") dna += r.count; }
  return { dna, total, rate: total>0 ? dna/total : 0 };
}
function aggCohortPerPractice(filter) {
  const m = new Map();
  for (const r of cohortRows) if (filter(r)) {
    const k = r.ods;
    const cur = m.get(k) || {dna:0,total:0};
    cur.total += r.count;
    if (r.status==="DNA") cur.dna += r.count;
    m.set(k, cur);
  }
  const arr = [];
  for (const [ods, v] of m) if (v.total>0) arr.push({ ods, rate: v.dna / v.total });
  return arr;
}
function monthAgg(filter) {
  const m = new Map();
  for (const r of rows) if (filter(r)) {
    const k = r.month;
    const cur = m.get(k) || {dna:0,total:0};
    cur.total += r.count;
    if (r.status==="DNA") cur.dna += r.count;
    m.set(k, cur);
  }
  return [...m.entries()].map(([month, v]) => ({ month, ...v, rate: v.total>0 ? v.dna/v.total : 0 }))
                        .sort((a,b)=> monthsOrder(a.month,b.month));
}
function sum(arr, k){ return arr.reduce((a,b)=>a+(b[k]||0),0); }

// ---------- define windows ----------
const monthsAvail = [...new Set(targetRows.map(r => r.month))].sort(monthsOrder);
// pre = all months strictly before Aug-2025; aug = Aug-2025; post = Sep-2025 if present
const AUG = "01AUG2025";
const SEP = "01SEP2025";
const preMonths = monthsAvail.filter(m => monthKey(m) < monthKey(AUG));
const haveAug = monthsAvail.includes(AUG);
const haveSep = monthsAvail.includes(SEP);

// ---------- TEST 1: Pre(Jun+Jul) vs Aug for PHONE ----------
const t1_pre = agg(r => r.ods===TARGET_ODS && r.mode==="Telephone" && preMonths.includes(r.month));
const t1_aug = haveAug ? agg(r => r.ods===TARGET_ODS && r.mode==="Telephone" && r.month===AUG) : null;

// ---------- TEST 2: Placebo (Same-day PHONE) ----------
const t2_pre = agg(r => r.ods===TARGET_ODS && r.mode==="Telephone" && lc(r.ttb)==="same day" && preMonths.includes(r.month));
const t2_aug = haveAug ? agg(r => r.ods===TARGET_ODS && r.mode==="Telephone" && lc(r.ttb)==="same day" && r.month===AUG) : null;

// ---------- TEST 3: Control group (other EMIS in same scope) PHONE, same windows ----------
function changeDist(mode, fltSameDay=false){
  const pre = aggCohortPerPractice(r =>
    r.mode===mode &&
    preMonths.includes(r.month) &&
    r.supplier===meta.supplier &&
    !(r.ods===TARGET_ODS) // exclude target
  );
  const aug = aggCohortPerPractice(r =>
    r.mode===mode &&
    r.month===AUG &&
    r.supplier===meta.supplier &&
    !(r.ods===TARGET_ODS)
  );

  // join by practice ods to compute delta rate (Aug - Pre)
  const preMap = new Map(pre.map(d => [d.ods, d.rate]));
  const augMap = new Map(aug.map(d => [d.ods, d.rate]));
  const keys = new Set([...preMap.keys(), ...augMap.keys()]);
  const deltas = [];
  for (const k of keys) {
    const a = augMap.get(k);
    const p = preMap.get(k);
    if (a!=null && p!=null) deltas.push(a - p);
  }
  return deltas;
}
const t3_deltas_phone = haveAug ? changeDist("Telephone") : [];
const t3_target_delta_phone = (t1_aug && preMonths.length) ? (t1_aug.rate - t1_pre.rate) : null;
const t3_percentile = (t3_deltas_phone.length && t3_target_delta_phone!=null)
  ? percentileRank(t3_deltas_phone, t3_target_delta_phone) : null;

// ---------- TEST 4: Hotspot cooling (Planned* & 2–7 days) ----------
function aggHot(categoryLike){
  const pre = agg(r => r.ods===TARGET_ODS && r.category.startsWith(categoryLike) && normBucket(r.ttb)==="2 to 7 days" && preMonths.includes(r.month));
  const aug = haveAug ? agg(r => r.ods===TARGET_ODS && r.category.startsWith(categoryLike) && normBucket(r.ttb)==="2 to 7 days" && r.month===AUG) : null;
  return { pre, aug };
}
function normBucket(ttb){
  const t = lc(ttb).replace(/\s+/g," ").trim();
  if (t==="2 to 7 days" || t==="2  to 7 days") return "2 to 7 days";
  return t;
}
const t4_planned_clinics = aggHot("Planned Clinics");
const t4_planned_proc    = aggHot("Planned Clinical Procedure");

// ---------- Extras ----------
const targetMonthlyPhone = monthAgg(r => r.ods===TARGET_ODS && r.mode==="Telephone");
const waitCorrByMonthPhone = (() => {
  const months = monthsAvail;
  const out = [];
  for (const m of months) {
    const rowsM = targetRows.filter(r => r.month===m && r.mode==="Telephone");
    if (!rowsM.length) continue;
    const buckets = groupBuckets(rowsM);
    const xs=[], ys=[], ws=[];
    for (const b of buckets){
      const x = timeMap.get(lc(b.bucket)) ?? null;
      if (x==null) continue;
      xs.push(x); ys.push(b.rate); ws.push(b.total);
    }
    out.push({ month: m, corr: Number.isFinite(corrPearson(xs, ys, ws)) ? corrPearson(xs, ys, ws) : null });
  }
  return out.sort((a,b)=> monthsOrder(a.month,b.month));
})();
function groupBuckets(rowsM){
  const m = new Map();
  for (const r of rowsM){
    const k = normBucket(r.ttb);
    const cur = m.get(k) || { bucket:k, dna:0, total:0 };
    cur.total += r.count;
    if (r.status==="DNA") cur.dna += r.count;
    m.set(k, cur);
  }
  return [...m.values()].map(v => ({...v, rate: v.total>0 ? v.dna/v.total : 0}));
}

// ---------- Sep (post) if present ----------
const postPhone = haveSep ? agg(r => r.ods===TARGET_ODS && r.mode==="Telephone" && r.month===SEP) : null;
const postSameDayPhone = haveSep ? agg(r => r.ods===TARGET_ODS && r.mode==="Telephone" && lc(r.ttb)==="same day" && r.month===SEP) : null;

// ---------- Output ----------
const out = {
  meta: {
    target: meta,
    months: monthsAvail
  },
  tests: {
    pre_vs_aug_phone: haveAug ? {
      pre: t1_pre,
      aug: t1_aug,
      delta_rate: (t1_aug.rate - t1_pre.rate)
    } : null,
    placebo_same_day_phone: haveAug ? {
      pre: t2_pre,
      aug: t2_aug,
      delta_rate: (t2_aug.rate - t2_pre.rate)
    } : null,
    control_group_emis_phone_delta: haveAug ? {
      members: t3_deltas_phone.length,
      target_delta: t3_target_delta_phone,
      peers_delta_mean: mean(t3_deltas_phone),
      peers_delta_sd: std(t3_deltas_phone),
      target_delta_percentile: t3_percentile
    } : null,
    hotspot_2to7_days: haveAug ? {
      planned_clinics: {
        pre: t4_planned_clinics.pre,
        aug: t4_planned_clinics.aug,
        delta_rate: (t4_planned_clinics.aug.rate - t4_planned_clinics.pre.rate)
      },
      planned_procedure: {
        pre: t4_planned_proc.pre,
        aug: t4_planned_proc.aug,
        delta_rate: (t4_planned_proc.aug.rate - t4_planned_proc.pre.rate)
      }
    } : null
  },
  extras: {
    monthly_phone_series: targetMonthlyPhone, // [{month,dna,total,rate}]
    phone_waittime_correlation_by_month: waitCorrByMonthPhone, // [{month,corr}]
    three_month_totals: (() => {
      const tAll = agg(r => r.ods===TARGET_ODS && monthsAvail.includes(r.month));
      const tPhone = agg(r => r.ods===TARGET_ODS && r.mode==="Telephone" && monthsAvail.includes(r.month));
      const tF2F = agg(r => r.ods===TARGET_ODS && r.mode==="Face-to-Face" && monthsAvail.includes(r.month));
      const tOtherStaff = agg(r => r.ods===TARGET_ODS && r.hcp==="Other Practice staff" && monthsAvail.includes(r.month));
      const tGP = agg(r => r.ods===TARGET_ODS && r.hcp==="GP" && monthsAvail.includes(r.month));
      return { all: tAll, phone: tPhone, face_to_face: tF2F, gp: tGP, other_staff: tOtherStaff };
    })(),
  },
  post_september_if_present: haveSep ? {
    phone: postPhone,
    same_day_phone: postSameDayPhone,
    deltas_vs_pre: {
      phone_rate_delta: postPhone.rate - t1_pre.rate,
      same_day_phone_rate_delta: postSameDayPhone.rate - t2_pre.rate
    }
  } : null
};

console.log(JSON.stringify(out, null, 2));
