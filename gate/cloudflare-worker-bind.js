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
  return /bind-and-issue|\/bind\b|\/issue\b/i.test(path);
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
    const jobId = url.pathname.split("/").filter(Boolean).slice(-2, -1)[0] || env.JOB_ID || "unknown";
    const hop = await fetch(`${gate}/v1/pas/policycenter/pre-bind`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${env.GATE_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        fuse_id: env.FUSE_ID || "fuse_velaru_drill",
        job_id: jobId,
        action: "bind-and-issue",
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
