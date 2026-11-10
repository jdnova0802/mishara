// Nisaba — item 132: cross-receipt link graph
//
// Node identity is a typed registry. Receipt IDs contain underscores
// (and may contain colons). Never reconstruct type/id by splitting a
// concatenated string.

import {
  ReceiptRecord,
  LinkGraphQuery,
  LinkGraphResult,
  LinkGraphNode,
  LinkGraphEdge,
  EdgeType,
  EntityType,
} from "./types.js";

function nodeId(entityType: EntityType, entityId: string): string {
  return `${entityType}:${entityId}`;
}

class NodeRegistry {
  private byId = new Map<string, LinkGraphNode>();

  intern(entityType: EntityType, entityId: string): LinkGraphNode {
    const id = nodeId(entityType, entityId);
    const existing = this.byId.get(id);
    if (existing) return existing;
    const node: LinkGraphNode = { nodeId: id, entityType, entityRef: entityId };
    this.byId.set(id, node);
    return node;
  }

  get(id: string): LinkGraphNode | undefined {
    return this.byId.get(id);
  }
}

export class LinkGraphBuilder {
  constructor(private receipts: Map<string, ReceiptRecord>) {}

  private edgesFromReceipt(receipt: ReceiptRecord, registry: NodeRegistry): LinkGraphEdge[] {
    const edges: LinkGraphEdge[] = [];
    const receiptNode = registry.intern("receipt_id", receipt.receiptId);
    for (const ing of receipt.ingredients) {
      const ingredientNode = registry.intern("receipt_id", ing.ingredientReceiptId);
      edges.push({
        edgeId: `ingredient:${ingredientNode.nodeId}->${receiptNode.nodeId}`,
        fromNodeId: ingredientNode.nodeId,
        toNodeId: receiptNode.nodeId,
        edgeType: "ingredient",
        sourceReceiptId: receipt.receiptId,
      });
    }
    for (const coSigner of receipt.coSigners ?? []) {
      const actorNode = registry.intern("actor", coSigner);
      edges.push({
        edgeId: `co_signer:${actorNode.nodeId}->${receiptNode.nodeId}`,
        fromNodeId: actorNode.nodeId,
        toNodeId: receiptNode.nodeId,
        edgeType: "co_signer",
        sourceReceiptId: receipt.receiptId,
      });
    }
    return edges;
  }

  private cohortEdges(
    registry: NodeRegistry,
    operatorCohort: Map<string, string>,
    cohortOf: string,
  ): LinkGraphEdge[] {
    const edges: LinkGraphEdge[] = [];
    const members = Array.from(operatorCohort.entries()).filter(([, c]) => c === cohortOf);
    for (let i = 0; i < members.length; i++) {
      for (let j = i + 1; j < members.length; j++) {
        const aId = members[i]?.[0];
        const bId = members[j]?.[0];
        if (!aId || !bId) continue;
        const a = registry.intern("actor", aId);
        const b = registry.intern("actor", bId);
        edges.push({
          edgeId: `shared_cohort:${a.nodeId}<->${b.nodeId}`,
          fromNodeId: a.nodeId,
          toNodeId: b.nodeId,
          edgeType: "shared_cohort",
          // population-derived — blank rather than a faked receipt_id
          sourceReceiptId: "",
        });
      }
    }
    return edges;
  }

  expand(query: LinkGraphQuery, operatorCohort?: Map<string, string>): LinkGraphResult {
    const registry = new NodeRegistry();
    const root = registry.intern(query.rootEntityType, query.rootEntityId);
    const nodes = new Map<string, LinkGraphNode>([[root.nodeId, root]]);
    const edges = new Map<string, LinkGraphEdge>();

    const allEdges: LinkGraphEdge[] = [];
    for (const receipt of this.receipts.values()) {
      allEdges.push(...this.edgesFromReceipt(receipt, registry));
    }
    if (operatorCohort && query.edgeTypes.includes("shared_cohort") && query.rootEntityType === "actor") {
      const rootCohort = operatorCohort.get(query.rootEntityId);
      if (rootCohort) allEdges.push(...this.cohortEdges(registry, operatorCohort, rootCohort));
    }

    const relevant = allEdges.filter((e) => query.edgeTypes.includes(e.edgeType as EdgeType));
    let frontier = new Set<string>([root.nodeId]);
    const visited = new Set<string>(frontier);

    for (let hop = 0; hop < query.maxHops; hop++) {
      const nextFrontier = new Set<string>();
      for (const edge of relevant) {
        const touches = frontier.has(edge.fromNodeId) || frontier.has(edge.toNodeId);
        if (!touches) continue;
        edges.set(edge.edgeId, edge);
        for (const side of [edge.fromNodeId, edge.toNodeId] as const) {
          if (!visited.has(side)) {
            visited.add(side);
            nextFrontier.add(side);
            const registered = registry.get(side);
            if (!registered) {
              throw new Error(`link graph node ${side} was never interned — refuse to parse identity from the string`);
            }
            nodes.set(side, registered);
          }
        }
      }
      if (nextFrontier.size === 0) break;
      frontier = nextFrontier;
    }

    return { query, nodes: Array.from(nodes.values()), edges: Array.from(edges.values()) };
  }
}
