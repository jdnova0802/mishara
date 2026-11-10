// Nisaba — items 132/133 shared types
// Matches docs/kudurru/schemas/132_135_synthesis.json.

export type EntityType = "actor" | "org" | "receipt_id";
export type EdgeType = "ingredient" | "co_signer" | "shared_cohort" | "shared_counterparty";
export type Metric = "brier_score" | "block_rate" | "severity_weighted_load";
export type Disposition = "ESCALATE" | "MONITOR" | "CLOSE_NON_ACTIONABLE" | null;

/**
 * Subset of an existing Nisaba receipt that 132/133 read.
 * Not a new table — typed over item 114 ingredients plus cohort/operator fields.
 */
export interface ReceiptRecord {
  receiptId: string;
  operatorId: string;
  orgId: string;
  cohortVertical: string;
  ingredients: { ingredientReceiptId: string; ingredientHash: string }[];
  coSigners?: string[];
  metrics?: Partial<Record<Metric, number>>;
  createdAt: string;
}

export interface LinkGraphQuery {
  queryId: string;
  rootEntityType: EntityType;
  rootEntityId: string;
  maxHops: number;
  edgeTypes: EdgeType[];
  generatedAt: string;
}

export interface LinkGraphNode {
  nodeId: string;
  entityType: EntityType;
  entityRef: string;
}

export interface LinkGraphEdge {
  edgeId: string;
  fromNodeId: string;
  toNodeId: string;
  edgeType: EdgeType;
  sourceReceiptId: string;
}

export interface LinkGraphResult {
  query: LinkGraphQuery;
  nodes: LinkGraphNode[];
  edges: LinkGraphEdge[];
}

export interface PopulationBaseline {
  baselineId: string;
  cohortVertical: string;
  metric: Metric;
  periodStart: string;
  periodEnd: string;
  mean: number;
  stddev: number;
  sampleSize: number;
}

export interface AnomalyFlag {
  flagId: string;
  operatorId: string;
  baselineId: string;
  observedValue: number;
  deviationSigma: number;
  flaggedAt: string;
  reviewed: boolean;
  disposition: Disposition;
}
