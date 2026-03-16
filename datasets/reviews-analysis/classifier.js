/**
 * Lite-NLP classifier for GP review themes.
 * Runs in Node (build) and browser (client filtering). Same logic both places.
 *
 * Usage (Node): node classifier.js <input_json_path> <overrides_json_string>
 * Output: JSON to stdout with reviews enriched with .buckets and .primary_bucket
 */

const BUCKETS = [
  { id: "reception", label: "Reception / rudeness", keywords: ["reception", "receptionist", "reception staff", "rude", "unprofessional", "dismissive", "unhelpful", "condescending", "confidentiality", "standing there", "name dob", "address"] },
  { id: "appointments", label: "Appointments / access", keywords: ["appointment", "appointments", "can't get", "couldn't get", "waiting", "wait time", "hold time", "phone line", "8am", "ring", "booking", "booked", "cancelled", "cancellation", "no appointment", "get through", "never get"] },
  { id: "prescriptions", label: "Prescriptions", keywords: ["prescription", "repeat prescription", "medication", "reject", "rejecting", "ordered", "ordering"] },
  { id: "referrals", label: "Referrals / admin", keywords: ["referral", "referrals", "chase", "chasing", "months", "waiting for", "sent again", "never sent"] },
  { id: "continuity", label: "Continuity / same GP", keywords: ["same gp", "same doctor", "different doctor", "never see", "see the same", "usual gp", "main gp", "continuity", "rotating", "locum", "locums"] },
  { id: "staff", label: "Staff / doctors", keywords: ["doctor", "doctors", "gp", "gps", "staff", "nurse", "practitioner", "unprofessional", "rude", "don't care", "don't listen", "clueless"] },
  { id: "digital", label: "Digital / website", keywords: ["website", "online", "patchs", "digital", "system", "form", "forms", "out of hours", "24hr", "user friendly", "barrier", "disability", "disabilities"] },
  { id: "results", label: "Results / follow-up", keywords: ["blood test", "results", "haven't got back", "didn't get back", "follow up", "follow-up", "test results"] },
  { id: "waiting_room", label: "Waiting room", keywords: ["waiting room", "waited", "waiting for", "35 minutes", "30 minutes", "sat waiting"] },
  { id: "positive", label: "Positive experience", keywords: ["good", "great", "excellent", "helpful", "always", "improved", "improving", "easy", "easier", "recommend"] },
];

function classifyReview(text, ratingStars) {
  if (!text || typeof text !== "string") return { buckets: [], primary_bucket: "uncategorised" };
  const lower = text.toLowerCase();
  const buckets = [];
  for (const b of BUCKETS) {
    const matched = b.keywords.some((kw) => lower.includes(kw.toLowerCase()));
    if (matched) buckets.push(b.id);
  }
  if (buckets.length === 0) return { buckets: [], primary_bucket: "uncategorised" };
  // Prefer negative buckets for low ratings, positive for high
  if (ratingStars <= 2 && buckets.includes("positive")) {
    buckets.splice(buckets.indexOf("positive"), 1);
  }
  if (ratingStars >= 4 && buckets.includes("positive")) {
    return { buckets, primary_bucket: "positive" };
  }
  return { buckets, primary_bucket: buckets[0] };
}

function applyOverrides(review, practiceCode, reviewIndex, overrides) {
  const key = `${practiceCode}:${reviewIndex}`;
  const override = overrides[key];
  if (override && override.buckets) {
    review.buckets = override.buckets;
  }
  if (override && override.primary_bucket) {
    review.primary_bucket = override.primary_bucket;
  }
}

function runClassifier(data, overrides = {}) {
  const practices = data.practices || [];
  for (const practice of practices) {
    const code = practice.canonical_code || "";
    for (let i = 0; i < (practice.reviews || []).length; i++) {
      const r = practice.reviews[i];
      const { buckets, primary_bucket } = classifyReview(r.text, r.rating_stars || 0);
      r.buckets = buckets;
      r.primary_bucket = primary_bucket;
      applyOverrides(r, code, i, overrides);
    }
  }
  const across = data.recent_reviews_across_manchester || [];
  for (let i = 0; i < across.length; i++) {
    const r = across[i];
    const code = r.canonical_code || "_across";
    const { buckets, primary_bucket } = classifyReview(r.text, r.rating_stars || 0);
    r.buckets = buckets;
    r.primary_bucket = primary_bucket;
    applyOverrides(r, code, i, overrides);
  }
  return data;
}

// Node: read from args, write to stdout
if (typeof process !== "undefined" && process.argv && process.argv.length >= 3) {
  const fs = require("fs");
  const inputPath = process.argv[2];
  const overridesStr = process.argv[3] || "{}";
  let overrides = {};
  try {
    overrides = JSON.parse(overridesStr);
  } catch (_) {}
  const data = JSON.parse(fs.readFileSync(inputPath, "utf8"));
  const result = runClassifier(data, overrides);
  console.log(JSON.stringify(result));
}

// Browser: export for use as module or global
if (typeof window !== "undefined") {
  window.ReviewsClassifier = { runClassifier, classifyReview, BUCKETS };
}
if (typeof module !== "undefined" && module.exports) {
  module.exports = { runClassifier, classifyReview, BUCKETS };
}
