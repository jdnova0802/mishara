/**
 * wrapWithPrefinality — fail-closed pre-sign gate for x402 fetch flows.
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
  failOpen = false,
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
    if (failOpen) return { decision: "GO", fail_open: true, error: String(err) };
    throw new PrefinalityBlockedError("Prefinality gate unreachable — fail closed", {
      decision: "NO_GO",
      reason: "gate_unreachable",
    });
  }

  const data = await res.json().catch(() => ({}));
  if (!res.ok && data?.decision !== "HOLD") {
    if (failOpen) return { decision: "GO", fail_open: true, evaluation: data };
  }
  return data;
}

/**
 * Wrap an x402-enabled fetch. Before the underlying fetch pays/signs, calls Gate evaluate.
 */
export function wrapWithPrefinality(fetchWithPayment, config = {}) {
  if (typeof fetchWithPayment !== "function") {
    throw new TypeError("fetchWithPayment must be a function");
  }

  const {
    gateUrl,
    apiKey,
    agentId,
    mandate = {},
    failOpen = false,
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

    const transfer = {
      amount: amount != null ? String(amount) : mandate.amount || "0",
      currency: "USDC",
      counterparty: payTo || mandate.expected_payto || "",
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
      failOpen,
    });

    if (evaluation.decision !== "GO") {
      throw new PrefinalityBlockedError(
        `Prefinality ${evaluation.decision}: ${(evaluation.signals || []).join(", ") || evaluation.message || "blocked"}`,
        evaluation,
      );
    }

    const nextInit = { ...(init || {}) };
    const hdrs = new Headers(nextInit.headers || {});
    if (evaluation.receipt) {
      hdrs.set("X-Gate-Prefinality-Receipt", evaluation.receipt);
    }
    nextInit.headers = hdrs;

    return fetchWithPayment(input, nextInit);
  };
}

export default wrapWithPrefinality;
