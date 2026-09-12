/**
 * wrapWithRightToAct — fail-closed gate before an irreversible sink call.
 *
 * Usage:
 *   import { wrapWithRightToAct } from "./wrap.mjs";
 *   const guarded = wrapWithRightToAct(doWire, {
 *     gateUrl: "https://gate.velaru.xyz",
 *     action: "wire.send",
 *     sink: "bank.rtp",
 *     policy: { max_amount: 25 },
 *   });
 *   await guarded({ amount: 10, to: "acct_1" });
 */

export class RightToActBlockedError extends Error {
  constructor(message, evaluation) {
    super(message);
    this.name = "RightToActBlockedError";
    this.evaluation = evaluation;
  }
}

async function evaluateRightToAct({
  gateUrl,
  apiKey,
  action,
  sink,
  actor,
  args,
  policy,
  context,
  mintTicket = true,
}) {
  const base = (gateUrl || "https://gate.velaru.xyz").replace(/\/$/, "");
  const path = apiKey ? "/v1/right-to-act/evaluate" : "/demo/right-to-act/evaluate";
  const headers = { "Content-Type": "application/json" };
  if (apiKey) headers.Authorization = `Bearer ${apiKey}`;

  let res;
  try {
    res = await fetch(`${base}${path}`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        action,
        sink,
        actor,
        args,
        policy,
        context,
        mint_ticket: mintTicket,
      }),
    });
  } catch (err) {
    throw new RightToActBlockedError("Right-to-Act gate unreachable — fail closed", {
      decision: "NONEXIST",
      reason: "gate_unreachable",
      error: String(err),
    });
  }

  const data = await res.json().catch(() => ({}));
  return data;
}

async function burnTicket({ gateUrl, apiKey, ticketId, fingerprint, sink }) {
  const base = (gateUrl || "https://gate.velaru.xyz").replace(/\/$/, "");
  const headers = { "Content-Type": "application/json" };
  if (apiKey) headers.Authorization = `Bearer ${apiKey}`;
  const res = await fetch(`${base}/v1/right-to-act/burn`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      ticket_id: ticketId,
      fingerprint,
      sink,
    }),
  });
  return res.json().catch(() => ({ ok: false, reason: "burn_parse_error" }));
}

/**
 * Wrap any sink function. Evaluates Right-to-Act, burns ticket, then runs fn.
 * Refusal digests are attached on NONEXIST throws.
 */
export function wrapWithRightToAct(fn, config = {}) {
  if (typeof fn !== "function") {
    throw new TypeError("fn must be a function");
  }

  const {
    gateUrl,
    apiKey,
    action,
    sink,
    actor,
    policy = {},
    context = {},
    mintTicket = true,
    mapArgs = (args) => args,
  } = config;

  if (!action || !sink) {
    throw new TypeError("action and sink are required");
  }

  return async function guarded(...callArgs) {
    const args = mapArgs(callArgs.length <= 1 ? callArgs[0] : callArgs);
    const evaluation = await evaluateRightToAct({
      gateUrl,
      apiKey,
      action,
      sink,
      actor,
      args,
      policy,
      context,
      mintTicket,
    });

    if (evaluation.decision !== "EXIST" && evaluation.go !== true) {
      throw new RightToActBlockedError(
        `Right-to-Act ${evaluation.decision || "NONEXIST"}: ${(evaluation.signals || []).join(", ") || evaluation.message || "blocked"}`,
        evaluation,
      );
    }

    if (evaluation.ticket_id) {
      const burned = await burnTicket({
        gateUrl,
        apiKey,
        ticketId: evaluation.ticket_id,
        fingerprint: evaluation.fingerprint,
        sink,
      });
      if (!burned?.ok) {
        throw new RightToActBlockedError(
          `Right-to-Act ticket burn failed: ${burned?.reason || "unknown"}`,
          { ...evaluation, burn: burned },
        );
      }
    }

    const result = await fn(...callArgs);
    return {
      result,
      right_to_act: {
        evaluation_id: evaluation.evaluation_id,
        receipt: evaluation.receipt,
        fingerprint: evaluation.fingerprint,
        ticket_id: evaluation.ticket_id,
      },
    };
  };
}

export default wrapWithRightToAct;
