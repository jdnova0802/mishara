// Nisaba — item 133: population-level anomaly detection
//
// Flags vs the live cohort distribution. Never dispositions.
// MIN_SAMPLE_SIZE gates eligibility. Mean/stddev is the specced
// baseline; a severe outlier inflates stddev and can mask a milder
// one (same shape as item 139 Sybil baseline-shift, from honest stats).
// Median+MAD is a follow-on, not a silent change here.

import { ReceiptRecord, PopulationBaseline, AnomalyFlag, Metric } from "./types.js";

export const MIN_SAMPLE_SIZE = 20;
export const DEVIATION_THRESHOLD_SIGMA = 3.0;

function mean(values: number[]): number {
  return values.reduce((sum, v) => sum + v, 0) / values.length;
}

function stddev(values: number[], avg: number): number {
  const variance = mean(values.map((v) => (v - avg) ** 2));
  return Math.sqrt(variance);
}

export class AnomalyDetector {
  constructor(private receipts: ReceiptRecord[]) {}

  computeBaseline(
    cohortVertical: string,
    metric: Metric,
    periodStart: string,
    periodEnd: string,
  ): PopulationBaseline | null {
    const inWindow = this.receipts.filter(
      (r) =>
        r.cohortVertical === cohortVertical &&
        r.createdAt >= periodStart &&
        r.createdAt <= periodEnd &&
        r.metrics?.[metric] !== undefined,
    );
    if (inWindow.length === 0) return null;
    const values = inWindow.map((r) => r.metrics![metric] as number);
    const avg = mean(values);
    return {
      baselineId: `baseline:${cohortVertical}:${metric}:${periodStart}:${periodEnd}`,
      cohortVertical,
      metric,
      periodStart,
      periodEnd,
      mean: avg,
      stddev: stddev(values, avg),
      sampleSize: inWindow.length,
    };
  }

  flagAnomalies(baseline: PopulationBaseline): AnomalyFlag[] {
    if (baseline.sampleSize < MIN_SAMPLE_SIZE) return [];
    if (baseline.stddev === 0) return [];
    const inWindow = this.receipts.filter(
      (r) =>
        r.cohortVertical === baseline.cohortVertical &&
        r.createdAt >= baseline.periodStart &&
        r.createdAt <= baseline.periodEnd &&
        r.metrics?.[baseline.metric] !== undefined,
    );
    const flags: AnomalyFlag[] = [];
    const seenOperators = new Set<string>();
    for (const r of inWindow) {
      if (seenOperators.has(r.operatorId)) continue;
      const value = r.metrics![baseline.metric] as number;
      const sigma = Math.abs(value - baseline.mean) / baseline.stddev;
      if (sigma >= DEVIATION_THRESHOLD_SIGMA) {
        seenOperators.add(r.operatorId);
        flags.push({
          flagId: `flag:${baseline.baselineId}:${r.operatorId}`,
          operatorId: r.operatorId,
          baselineId: baseline.baselineId,
          observedValue: value,
          deviationSigma: sigma,
          flaggedAt: new Date().toISOString(),
          reviewed: false,
          disposition: null,
        });
      }
    }
    return flags.sort((a, b) => b.deviationSigma - a.deviationSigma);
  }
}
