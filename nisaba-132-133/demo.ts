// Mock-data sanity test for items 132/133. Not production data.

import { ReceiptRecord } from "./types.js";
import { LinkGraphBuilder } from "./linkGraph.js";
import { AnomalyDetector, MIN_SAMPLE_SIZE } from "./anomalyDetection.js";

const graphReceipts: ReceiptRecord[] = [
  {
    receiptId: "dec_c100",
    operatorId: "op_alice",
    orgId: "org_1",
    cohortVertical: "fintech",
    ingredients: [],
    createdAt: "2026-01-01T00:00:00Z",
  },
  {
    receiptId: "dec_c200",
    operatorId: "op_alice",
    orgId: "org_1",
    cohortVertical: "fintech",
    ingredients: [{ ingredientReceiptId: "dec_c100", ingredientHash: "h1" }],
    coSigners: ["op_bob"],
    createdAt: "2026-01-02T00:00:00Z",
  },
  {
    receiptId: "dec_c300",
    operatorId: "op_bob",
    orgId: "org_2",
    cohortVertical: "fintech",
    ingredients: [{ ingredientReceiptId: "dec_c200", ingredientHash: "h2" }],
    createdAt: "2026-01-03T00:00:00Z",
  },
  {
    receiptId: "dec_c900",
    operatorId: "op_zed",
    orgId: "org_9",
    cohortVertical: "healthcare",
    ingredients: [],
    createdAt: "2026-01-01T00:00:00Z",
  },
];

const receiptsById = new Map(graphReceipts.map((r) => [r.receiptId, r]));
const builder = new LinkGraphBuilder(receiptsById);
const graphResult = builder.expand({
  queryId: "q1",
  rootEntityType: "receipt_id",
  rootEntityId: "dec_c300",
  maxHops: 3,
  edgeTypes: ["ingredient", "co_signer"],
  generatedAt: new Date().toISOString(),
});

console.log("--- 132: link graph expand from dec_c300, maxHops=3 ---");
console.log(`nodes: ${graphResult.nodes.length}, edges: ${graphResult.edges.length}`);
for (const n of graphResult.nodes) console.log(`  node: ${n.nodeId} ref=${n.entityRef}`);
for (const e of graphResult.edges)
  console.log(`  edge: ${e.edgeType} ${e.fromNodeId} -> ${e.toNodeId} (via ${e.sourceReceiptId})`);

const unrelatedNodeId = "receipt_id:dec_c900";
console.log(
  `sanity check — unrelated receipt excluded: ${!graphResult.nodes.some((n) => n.nodeId === unrelatedNodeId)}`,
);

const underscoreNode = graphResult.nodes.find((n) => n.entityRef === "dec_c300");
if (!underscoreNode || underscoreNode.entityType !== "receipt_id" || underscoreNode.entityRef !== "dec_c300") {
  throw new Error("FAIL: underscore receipt id was parsed as identity instead of interned");
}

const anomalyReceipts: ReceiptRecord[] = [];
for (let i = 0; i < 25; i++) {
  anomalyReceipts.push({
    receiptId: `dec_norm_${i}`,
    operatorId: `op_normal_${i}`,
    orgId: "org_pool",
    cohortVertical: "fintech",
    ingredients: [],
    metrics: { block_rate: 0.05 + Math.sin(i) * 0.01 },
    createdAt: "2026-02-01T00:00:00Z",
  });
}
anomalyReceipts.push({
  receiptId: "dec_outlier_1",
  operatorId: "op_outlier_1",
  orgId: "org_pool",
  cohortVertical: "fintech",
  ingredients: [],
  metrics: { block_rate: 0.95 },
  createdAt: "2026-02-01T00:00:00Z",
});
anomalyReceipts.push({
  receiptId: "dec_outlier_2",
  operatorId: "op_outlier_2",
  orgId: "org_pool",
  cohortVertical: "fintech",
  ingredients: [],
  metrics: { block_rate: 0.01 },
  createdAt: "2026-02-01T00:00:00Z",
});
for (let i = 0; i < 5; i++) {
  anomalyReceipts.push({
    receiptId: `dec_small_${i}`,
    operatorId: `op_small_${i}`,
    orgId: "org_small",
    cohortVertical: "niche_vertical",
    ingredients: [],
    metrics: { block_rate: i === 0 ? 0.99 : 0.02 },
    createdAt: "2026-02-01T00:00:00Z",
  });
}

const detector = new AnomalyDetector(anomalyReceipts);
console.log("\n--- 133: population baseline + anomaly flags (fintech, block_rate) ---");
const baseline = detector.computeBaseline("fintech", "block_rate", "2026-01-01T00:00:00Z", "2026-03-01T00:00:00Z");
if (!baseline) throw new Error("expected a baseline for fintech/block_rate");
console.log(
  `baseline: mean=${baseline.mean.toFixed(4)} stddev=${baseline.stddev.toFixed(4)} sampleSize=${baseline.sampleSize} (gate=${MIN_SAMPLE_SIZE})`,
);
const flags = detector.flagAnomalies(baseline);
console.log(`flags raised: ${flags.length}`);
for (const f of flags) {
  console.log(
    `  ${f.operatorId}: value=${f.observedValue} sigma=${f.deviationSigma.toFixed(2)} disposition=${f.disposition} reviewed=${f.reviewed}`,
  );
}

console.log("\n--- 133: undersized cohort must yield zero flags regardless of spread ---");
const smallBaseline = detector.computeBaseline(
  "niche_vertical",
  "block_rate",
  "2026-01-01T00:00:00Z",
  "2026-03-01T00:00:00Z",
);
if (!smallBaseline) throw new Error("expected a baseline object even for an undersized cohort");
console.log(`small cohort sampleSize=${smallBaseline.sampleSize} (below gate of ${MIN_SAMPLE_SIZE})`);
const smallFlags = detector.flagAnomalies(smallBaseline);
console.log(`flags raised for undersized cohort: ${smallFlags.length} (must be 0)`);

if (smallFlags.length !== 0) {
  throw new Error("FAIL: undersized cohort produced flags — MIN_SAMPLE_SIZE gate is broken");
}
if (flags.length !== 1) {
  throw new Error(`FAIL: expected exactly 1 outlier flag given non-robust stddev, got ${flags.length}`);
}
if (flags[0]?.operatorId !== "op_outlier_1") {
  throw new Error("FAIL: expected the 0.95 outlier only; milder 0.01 is masked by inflated stddev");
}
if (graphResult.nodes.some((n) => n.nodeId === unrelatedNodeId)) {
  throw new Error("FAIL: unrelated receipt leaked into link graph");
}

console.log("\nAll sanity checks passed.");
