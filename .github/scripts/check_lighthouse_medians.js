/**
 * Assert the medians Lighthouse CI does not.
 *
 * `lhci assert` evaluates one representative run out of the configured
 * `numberOfRuns`. With three runs of the same artifact measuring LCP 2,333 /
 * 2,935 / 2,931 ms, that reported "found: 2332.9" and passed a 2,500 ms
 * ceiling the median misses by 431 ms. A budget that can pass on the luckiest
 * of three runs is not a budget, so this step reads every run and reports the
 * median it actually observed.
 *
 * Performance is an error below the floor (it is the gate); LCP is a warning
 * because the site breaches it today and the check is not meant to block the
 * default branch until that is decided.
 */
const fs = require("fs");
const path = require("path");

const DIR = process.argv[2] || ".lighthouseci";
const PERF_FLOOR = Number(process.argv[3] || 90);
const LCP_CEILING = Number(process.argv[4] || 2500);

const median = (values) => {
  const sorted = values.filter((v) => typeof v === "number").sort((a, b) => a - b);
  if (!sorted.length) return null;
  return sorted[Math.floor(sorted.length / 2)];
};

const runs = fs
  .readdirSync(DIR)
  .filter((name) => /^lhr-.*\.json$/.test(name))
  .map((name) => JSON.parse(fs.readFileSync(path.join(DIR, name), "utf8")));

if (!runs.length) {
  console.error("No Lighthouse reports found in " + DIR);
  process.exit(1);
}

const rows = runs.map((run) => ({
  performance: Math.round(run.categories.performance.score * 100),
  lcp: Math.round(run.audits["largest-contentful-paint"].numericValue),
  cls: Number(run.audits["cumulative-layout-shift"].numericValue.toFixed(4)),
}));

const perf = median(rows.map((r) => r.performance));
const lcp = median(rows.map((r) => r.lcp));
const cls = median(rows.map((r) => r.cls));

console.log(`Runs: ${rows.length}`);
for (const row of rows) {
  console.log(`  performance ${row.performance} | LCP ${row.lcp} ms | CLS ${row.cls}`);
}
console.log(`Median: performance ${perf} | LCP ${lcp} ms | CLS ${cls}`);

const problems = [];
if (perf < PERF_FLOOR) {
  problems.push(`median performance ${perf} is below the ${PERF_FLOOR} floor`);
}
if (lcp > LCP_CEILING) {
  console.log(
    `::warning title=LCP above budget::median LCP ${lcp} ms exceeds the ${LCP_CEILING} ms ceiling ` +
      `(runs: ${rows.map((r) => r.lcp).join(", ")})`
  );
}
if (cls > 0.1) {
  problems.push(`median CLS ${cls} exceeds 0.1`);
}

if (problems.length) {
  console.error("Median budget breaches: " + problems.join("; "));
  process.exit(1);
}
console.log(`Median budget satisfied: performance >= ${PERF_FLOOR}, CLS <= 0.1.`);
