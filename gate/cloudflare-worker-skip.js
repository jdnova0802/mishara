/**
 * Skip-path scanner. Same Job API family as bind-only.
 * Intercept oos-conflicts/resolve and handle-preemptions.
 * Winner-only resolve HALTs. Skip remaining must exist for every discarded value.
 * Missing Signed Remaining Timestamp HALTs even if CASP would pass.
 * wrangler secret put GATE_KEY
 * GATE_URL = live https Gate — never localhost.
 * This is not a production weld. their_production stays false.
 */
function isLocal(url) {
  const u = (url || "").toLowerCase();
  return !u || /localhost|127\.0\.0\.1|0\.0\.0\.0|\[::1\]/.test(u);
}

function isSkipWrite(path) {
  return /oos-conflicts\/resolve|handle-preemptions/i.test(path);
}

function haltResponse(body, env, extra, status) {
  const src = body && typeof body === "object" ? body : {};
  const payload = Object.assign({ halt: true, allow: false, their_production: false }, src, extra || {});
  return new Response(JSON.stringify(payload), {
    status: status || 403,
    headers: { "content-type": "application/json", "x-gate-skip-welded": "1" },
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method !== "POST" || !isSkipWrite(url.pathname)) {
      return fetch(request);
    }
    const gate = (env.GATE_URL || "").replace(/\/$/, "");
    if (!gate || !env.GATE_KEY || (isLocal(gate) && env.ALLOW_LOCAL !== "1")) {
      return haltResponse(null, env, { reason: "gate_not_public" }, 503);
    }
    const parts = url.pathname.split("/").filter(Boolean);
    const jobId = parts.includes("jobs") ? parts[parts.indexOf("jobs") + 1] : env.JOB_ID || "unknown";
    let incoming = {};
    try {
      incoming = await request.clone().json();
    } catch (e) {
      incoming = {};
    }
    const hop = await fetch(`${gate}/v1/skip/dated-write`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${env.GATE_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        job_id: jobId,
        method: request.method,
        path: url.pathname,
        conflicts: incoming.conflicts,
        preempted_job_id: incoming.preemptedJobId || incoming.preempted_job_id,
        preempting_job_id: incoming.preemptingJobId || incoming.preempting_job_id,
        mint_skips: incoming.mint_skips === true || env.MINT_SKIPS === "1",
      }),
    });
    const body = await hop.json().catch(() => ({ halt: true, allow: false }));
    if (!hop.ok || body.halt || body.allow === false) {
      return haltResponse(body, env, null, hop.status === 503 ? 503 : 403);
    }
    if (!body.srt || !body.srt.signature) {
      return haltResponse(body, env, { reason: "srt_missing", casp_passed: !!body.casp }, 403);
    }
    return fetch(request);
  },
};
