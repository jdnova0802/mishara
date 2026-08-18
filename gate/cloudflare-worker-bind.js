/**
 * Bind-path only. Intercept bind-and-issue / issue. Everything else passes through.
 * wrangler secret put GATE_KEY
 * GATE_URL = live https Gate — never localhost.
 * Halt JSON always includes verify_url and inhabitant_url so the inhabitant
 * gets a copy without asking.
 */
function isLocal(url) {
  const u = (url || "").toLowerCase();
  return !u || /localhost|127\.0\.0\.1|0\.0\.0\.0|\[::1\]/.test(u);
}

function isBindWrite(path) {
  // bind-only is already a legally Bound contract. Catch it, not only bind-and-issue.
  return /bind-and-issue|bind-only|\/bind\b|\/issue\b/i.test(path);
}

function verifyFrom(body, env) {
  const src = body && typeof body === "object" ? body : {};
  const hop = src.hop && typeof src.hop === "object" ? src.hop : {};
  return (
    src.verify_url ||
    src.restraint_permalink ||
    hop.verify_url ||
    hop.restraint_permalink ||
    env.VERIFY_URL ||
    "https://velaru.xyz/verify"
  );
}

function haltResponse(body, env, extra, status) {
  const src = body && typeof body === "object" ? body : {};
  const payload = Object.assign({ halt: true, allow_bind: false }, src, extra || {}, {
    verify_url: verifyFrom(src, env),
  });
  return new Response(JSON.stringify(payload), {
    status: status || 403,
    headers: { "content-type": "application/json", "x-gate-welded": "1" },
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method !== "POST" || !isBindWrite(url.pathname)) {
      return fetch(request);
    }
    const gate = (env.GATE_URL || "").replace(/\/$/, "");
    if (!gate || !env.GATE_KEY || (isLocal(gate) && env.ALLOW_LOCAL !== "1")) {
      return haltResponse(null, env, { reason: "gate_not_public" }, 503);
    }
    const parts = url.pathname.split("/").filter(Boolean);
    const last = (parts[parts.length - 1] || "").toLowerCase();
    const jobId = parts.slice(-2, -1)[0] || env.JOB_ID || "unknown";
    const action = /bind-only/i.test(last) ? "bind-only" : /issue/i.test(last) ? "issue" : "bind-and-issue";
    const hop = await fetch(`${gate}/v1/pas/policycenter/pre-bind`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${env.GATE_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        fuse_id: env.FUSE_ID || "fuse_velaru_drill",
        job_id: jobId,
        action,
      }),
    });
    const body = await hop.json().catch(() => ({ halt: true, allow_bind: false }));
    if (!hop.ok || body.halt || body.allow_bind === false) {
      return haltResponse(body, env, null, hop.status === 503 ? 503 : 403);
    }
    // Commit-time authorization: a LIVE hop is not a bind grant. Redeem the ticket.
    const ticket = body.bind_ticket || {};
    if (!ticket.token || !ticket.ticket_id) {
      return haltResponse(body, env, { reason: "ticket_required" }, 403);
    }
    const redeem = await fetch(`${gate}/v1/pas/bind-ticket/redeem`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${env.GATE_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ticket_id: ticket.ticket_id,
        token: ticket.token,
        job_id: jobId,
      }),
    });
    const redeemed = await redeem.json().catch(() => ({ ok: false, halt: true }));
    if (!redeem.ok || redeemed.ok === false || redeemed.halt) {
      return haltResponse(redeemed, env, { reason: redeemed.reason || "ticket_invalid" }, 403);
    }
    return fetch(request);
  },
};
