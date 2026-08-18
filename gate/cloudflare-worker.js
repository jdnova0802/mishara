/**
 * Closed-world edge: hop before origin. If halt/DEAD, do not fetch.
 * Cloudflare Worker — weld this in front of any origin you refuse to side-door.
 *
 * wrangler secret: GATE_URL, GATE_KEY
 */
export default {
  async fetch(request, env) {
    const gate = (env.GATE_URL || "").replace(/\/$/, "");
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
