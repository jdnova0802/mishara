/**
 * Closed-world edge: hop before origin. If halt/DEAD, do not fetch.
 * Cloudflare Worker — weld this in front of any origin you refuse to side-door.
 *
 * wrangler secret put GATE_KEY
 * [vars] GATE_URL must be the LIVE https origin — never localhost.
 */
function isLocal(url) {
  const u = (url || "").toLowerCase();
  return !u || /localhost|127\.0\.0\.1|0\.0\.0\.0|\[::1\]/.test(u);
}

export default {
  async fetch(request, env) {
    const gate = (env.GATE_URL || "").replace(/\/$/, "");
    if (!gate || !env.GATE_KEY) {
      return new Response(JSON.stringify({ halt: true, acted: false, reason: "gate_not_configured" }), {
        status: 503,
        headers: { "content-type": "application/json", "x-gate-welded": "1" },
      });
    }
    if (isLocal(gate) && env.ALLOW_LOCAL !== "1") {
      return new Response(JSON.stringify({ halt: true, acted: false, reason: "gate_url_is_local" }), {
        status: 503,
        headers: { "content-type": "application/json", "x-gate-welded": "1" },
      });
    }
    const fuseId = env.FUSE_ID || "fuse_velaru_drill";
    const hop = await fetch(`${gate}/v1/act`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${env.GATE_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ fuse_id: fuseId, action: request.method + " " + new URL(request.url).pathname }),
    });
    const body = await hop.json().catch(() => ({ halt: true, fail_closed: true }));
    if (!hop.ok || body.halt || body.acted === false) {
      return new Response(JSON.stringify(body), {
        status: hop.status === 503 ? 503 : 403,
        headers: { "content-type": "application/json", "x-gate-welded": "1" },
      });
    }
    return fetch(request);
  },
};
