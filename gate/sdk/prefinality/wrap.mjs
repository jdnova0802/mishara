/**
 * wrapWithPrefinality — fail-closed pre-sign gate for x402 fetch flows.
 *
 * failOpen is intentionally absent. Gate unreachable / non-GO / missing receipt
 * / failed one-shot verify always blocks. There is no production case where
 * "sign anyway when the gate is down" is compatible with pre-commit clearance.
 *
 * GO receipts are single-use. After evaluate returns GO, this wrapper redeems
 * the receipt via POST /v1/prefinality/verify (server consume=True by default)
 * before the paid retry. If the paid fetch then fails on the network, call
 * evaluate again for a new jti — replaying the same receipt is rejected.
 *
 * Usage:
 *   import { wrapWithPrefinality } from "./wrap.mjs";
 *   const secureFetch = wrapWithPrefinality(fetchWithPayment, {
 *     gateUrl: "https://gate.velaru.xyz",
 *     agentId: "researcher-01",
 *     mandate: { max_amount: "1.00", expected_payto: "0x..." },
 *   });
 */

export class PrefinalityBlockedError extends Error {
  constructor(message, evaluation) {
    super(message);
    this.name = "PrefinalityBlockedError";
    this.evaluation = evaluation;
  }
}

function pickPayTo(paymentRequired) {
  if (!paymentRequired || typeof paymentRequired !== "object") return null;
  const accepts = paymentRequired.accepts || paymentRequired.paymentRequirements || [];
  const first = Array.isArray(accepts) ? accepts[0] : null;
  if (!first) return paymentRequired.payTo || paymentRequired.payto || null;
  return first.payTo || first.payto || first.destination || null;
}

function pickAmount(paymentRequired) {
  if (!paymentRequired || typeof paymentRequired !== "object") return null;
  const accepts = paymentRequired.accepts || paymentRequired.paymentRequirements || [];
  const first = Array.isArray(accepts) ? accepts[0] : null;
  if (!first) return paymentRequired.amount || paymentRequired.maxAmountRequired || null;
  return first.maxAmountRequired || first.amount || first.price || null;
}

async function evaluatePrefinality({
  gateUrl,
  apiKey,
  agentId,
  mandate,
  transfer,
  context,
}) {
  const base = (gateUrl || "https://gate.velaru.xyz").replace(/\/$/, "");
  const path = apiKey ? "/v1/prefinality/evaluate" : "/demo/prefinality/evaluate";
  const headers = { "Content-Type": "application/json" };
  if (apiKey) headers.Authorization = `Bearer ${apiKey}`;

  let res;
  try {
    res = await fetch(`${base}${path}`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        rail: "x402",
        transfer,
        mandate: { ...(mandate || {}), agent_id: agentId || mandate?.agent_id },
        context,
      }),
    });
  } catch (err) {
    throw new PrefinalityBlockedError("Prefinality gate unreachable — fail closed", {
      decision: "NO_GO",
      reason: "gate_unreachable",
      error: String(err),
    });
  }

  const data = await res.json().catch(() => ({}));
  if (!res.ok && data?.decision !== "HOLD" && data?.decision !== "GO" && data?.decision !== "NO_GO") {
    throw new PrefinalityBlockedError("Prefinality gate returned an error — fail closed", {
      decision: "NO_GO",
      reason: "gate_http_error",
      status: res.status,
      evaluation: data,
    });
  }
  return data;
}

/**
 * Redeem (consume) the GO receipt before paying. Server verify defaults to
 * consume=True, so this is the one-shot commit gate for x402 wrap.
 */
async function redeemPrefinalityReceipt({
  gateUrl,
  apiKey,
  receipt,
  transfer,
}) {
  const base = (gateUrl || "https://gate.velaru.xyz").replace(/\/$/, "");
  const headers = { "Content-Type": "application/json" };
  if (apiKey) headers.Authorization = `Bearer ${apiKey}`;

  let res;
  try {
    res = await fetch(`${base}/v1/prefinality/verify`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        receipt,
        rail: "x402",
        transfer,
        // Informative for operators; server verify_receipt_jwt defaults consume=True.
        consume: true,
      }),
    });
  } catch (err) {
    throw new PrefinalityBlockedError(
      "Prefinality receipt redeem unreachable — fail closed",
      { decision: "NO_GO", reason: "redeem_unreachable", error: String(err) },
    );
  }

  const data = await res.json().catch(() => ({}));
  if (!res.ok || !data?.valid || data?.decision !== "GO") {
    throw new PrefinalityBlockedError(
      `Prefinality receipt redeem blocked: ${data?.reason || data?.decision || res.status}`,
      { decision: "NO_GO", reason: data?.reason || "redeem_rejected", verification: data },
    );
  }
  return data;
}

/**
 * Wrap an x402-enabled fetch. Before the paid/sign retry, calls Gate evaluate
 * and redeems the GO receipt (one-shot).
 */
export function wrapWithPrefinality(fetchWithPayment, config = {}) {
  if (typeof fetchWithPayment !== "function") {
    throw new TypeError("fetchWithPayment must be a function");
  }

  for (const banned of ["failOpen", "fail_open", "fail-open"]) {
    if (Object.prototype.hasOwnProperty.call(config, banned)) {
      throw new TypeError(
        `${banned} is not supported. Prefinality is fail-closed; remove it from config.`,
      );
    }
  }

  const {
    gateUrl,
    apiKey,
    agentId,
    mandate = {},
    extractPayment = null,
  } = config;

  return async function secureFetch(input, init) {
    const url = typeof input === "string" ? input : input?.url;
    const response = await fetchWithPayment(input, init);

    if (response.status !== 402) {
      return response;
    }

    let paymentRequired = null;
    try {
      const clone = response.clone();
      paymentRequired = await clone.json();
    } catch {
      paymentRequired = null;
    }

    const payTo = extractPayment?.(paymentRequired)?.payTo ?? pickPayTo(paymentRequired);
    const amount = extractPayment?.(paymentRequired)?.amount ?? pickAmount(paymentRequired);

    if (!payTo || amount == null) {
      throw new PrefinalityBlockedError(
        "Prefinality cannot clear — 402 challenge missing payTo/amount",
        { decision: "NO_GO", reason: "incomplete_402_challenge" },
      );
    }

    const transfer = {
      amount: String(amount),
      currency: "USDC",
      counterparty: payTo,
      resource_url: url,
    };

    const evaluation = await evaluatePrefinality({
      gateUrl,
      apiKey,
      agentId,
      mandate,
      transfer,
      context: {
        resource_url: url,
        untrusted_text: init?.headers?.["X-Untrusted-Context"] || config.untrustedText,
        intended: mandate.intent,
      },
    });

    if (evaluation.decision !== "GO") {
      throw new PrefinalityBlockedError(
        `Prefinality ${evaluation.decision}: ${(evaluation.signals || []).join(", ") || evaluation.message || "blocked"}`,
        evaluation,
      );
    }

    if (!evaluation.receipt) {
      throw new PrefinalityBlockedError(
        "Prefinality GO without receipt — fail closed",
        { decision: "NO_GO", reason: "missing_receipt", evaluation },
      );
    }

    // One-shot redeem before signing/paying. Replay or verify failure blocks.
    await redeemPrefinalityReceipt({
      gateUrl,
      apiKey,
      receipt: evaluation.receipt,
      transfer,
    });

    const nextInit = { ...(init || {}) };
    const hdrs = new Headers(nextInit.headers || {});
    hdrs.set("X-Gate-Prefinality-Receipt", evaluation.receipt);
    nextInit.headers = hdrs;

    return fetchWithPayment(input, nextInit);
  };
}

export default wrapWithPrefinality;
