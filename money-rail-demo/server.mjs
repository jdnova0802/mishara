import { createServer } from "node:http";
import { ensureKeys, mintReceipt, verifyReceipt } from "./receipt.mjs";

const PORT = Number(process.env.PORT || 8787);
const { privateKey, publicKeyPem } = ensureKeys();

function json(res, status, body) {
  const raw = JSON.stringify(body, null, 2);
  res.writeHead(status, {
    "content-type": "application/json; charset=utf-8",
    "access-control-allow-origin": "*",
  });
  res.end(raw);
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on("data", (c) => chunks.push(c));
    req.on("end", () => resolve(Buffer.concat(chunks)));
    req.on("error", reject);
  });
}

function parseJson(buf) {
  if (!buf.length) return {};
  return JSON.parse(buf.toString("utf8"));
}

createServer(async (req, res) => {
  try {
    if (req.method === "OPTIONS") {
      res.writeHead(204, {
        "access-control-allow-origin": "*",
        "access-control-allow-methods": "GET,POST,OPTIONS",
        "access-control-allow-headers": "content-type",
      });
      return res.end();
    }

    if (req.method === "GET" && req.url === "/") {
      return json(res, 200, {
        name: "money-rail-demo",
        offer: "I fix Stripe webhooks & payment automations. Setup + monthly care.",
        endpoints: {
          "POST /webhook/stripe": "Simulate Stripe event → signed receipt",
          "POST /issuing/decide": "Approve/deny toy (workflow lock) → signed receipt",
          "POST /receipt/verify": "Verify a receipt signature",
          "GET /health": "ok",
        },
      });
    }

    if (req.method === "GET" && req.url === "/health") {
      return json(res, 200, { ok: true, port: PORT });
    }

    if (req.method === "GET" && req.url === "/pubkey") {
      return json(res, 200, { publicKeyPem });
    }

    const buf = await readBody(req);

    // Demo 1: Stripe-shaped webhook → signed decision receipt
    if (req.method === "POST" && req.url === "/webhook/stripe") {
      const event = parseJson(buf);
      const type = event.type || "payment_intent.succeeded";
      const obj = event.data?.object || event.object || {};
      const amount = obj.amount ?? event.amount ?? 0;
      const currency = obj.currency || event.currency || "usd";
      const id = obj.id || event.id || `evt_demo_${Date.now()}`;

      const approved = amount > 0 && amount <= 50000; // demo rule: max $500
      const receipt = mintReceipt(
        {
          mouth: "stripe_webhook",
          event_type: type,
          stripe_id: id,
          amount,
          currency,
          approved,
          reason: approved ? "within_demo_cap" : "over_demo_cap_or_zero",
          claim_scope: {
            boundary: "money_rail_demo_webhook_cap",
            max_amount_cents: 50000,
            note: "demo only — replace with client rules",
          },
        },
        privateKey
      );

      return json(res, 200, {
        received: true,
        approved,
        receipt,
        verify_hint: "POST /receipt/verify with { receipt }",
      });
    }

    // Demo 2: Issuing-style workflow lock
    if (req.method === "POST" && req.url === "/issuing/decide") {
      const body = parseJson(buf);
      const amount = Number(body.amount ?? body.pending_request?.amount ?? 0);
      const mcc = String(body.merchant_category || body.mcc || "");
      const allowed = (body.allowed_categories || body.allowed || []).map(String);
      const max = Number(body.max_amount ?? 10000);

      let approved = true;
      let reason = "ok";
      if (allowed.length && mcc && !allowed.includes(mcc)) {
        approved = false;
        reason = "mcc_not_in_allowlist";
      } else if (amount <= 0) {
        approved = false;
        reason = "bad_amount";
      } else if (amount > max) {
        approved = false;
        reason = "over_max_amount";
      }

      const receipt = mintReceipt(
        {
          mouth: "issuing_workflow_lock",
          amount,
          merchant_category: mcc,
          allowed_categories: allowed,
          max_amount: max,
          approved,
          reason,
          claim_scope: {
            boundary: "money_rail_demo_issuing_lock",
            checks: ["allowlist", "max_amount"],
          },
        },
        privateKey
      );

      return json(res, 200, {
        approved,
        reason,
        receipt,
      });
    }

    if (req.method === "POST" && req.url === "/receipt/verify") {
      const body = parseJson(buf);
      const receipt = body.receipt || body;
      const ok = verifyReceipt(receipt, publicKeyPem);
      return json(res, ok ? 200 : 400, { valid: ok, decision_id: receipt.decision_id });
    }

    json(res, 404, { error: "not_found" });
  } catch (err) {
    json(res, 500, { error: String(err?.message || err) });
  }
}).listen(PORT, () => {
  console.log(`money-rail-demo on http://127.0.0.1:${PORT}`);
  console.log(`GET  /`);
  console.log(`POST /webhook/stripe`);
  console.log(`POST /issuing/decide`);
  console.log(`npm run demo  # fires both demos`);
});
