/**
 * Bind-path only. Intercept bind-and-issue / issue. Everything else passes through.
 * wrangler secret put GATE_KEY
 * GATE_URL = live https Gate — never localhost.
 */
function isLocal(url) {
  const u = (url || "").toLowerCase();
  return !u || /localhost|127\.0\.0\.1|0\.0\.0\.0|\[::1\]/.test(u);
}

function isBindWrite(path) {
  // bind-only is already a legally Bound contract. Catch it, not only bind-and-issue.
  return /bind-and-issue|bind-only|\/bind\b|\/issue\b/i.test(path);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method !== "POST" || !isBindWrite(url.pathname)) {
      return fetch(request);
    }
    const gate = (env.GATE_URL || "").replace(/\/$/, "");
    if (!gate || !env.GATE_KEY || (isLocal(gate) && env.ALLOW_LOCAL !== "1")) {
      return new Response(JSON.stringify({ halt: true, allow_bind: false, reason: "gate_not_public" }), {
        status: 503,
        headers: { "content-type": "application/json", "x-gate-welded": "1" },
      });
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
      return new Response(JSON.stringify(body), {
        status: hop.status === 503 ? 503 : 403,
        headers: { "content-type": "application/json", "x-gate-welded": "1" },
      });
    }
    return fetch(request);
  },
};
