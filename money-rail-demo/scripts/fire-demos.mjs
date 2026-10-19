const BASE = process.env.BASE || "http://127.0.0.1:8787";

async function post(path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  const json = await res.json();
  console.log(`\n=== ${path} ===`);
  console.log(JSON.stringify(json, null, 2));
  return json;
}

const webhook = await post("/webhook/stripe", {
  type: "payment_intent.succeeded",
  data: {
    object: {
      id: "pi_demo_123",
      amount: 4200,
      currency: "usd",
    },
  },
});

await post("/receipt/verify", { receipt: webhook.receipt });

const allow = await post("/issuing/decide", {
  amount: 2500,
  merchant_category: "fuel",
  allowed_categories: ["fuel", "parking"],
  max_amount: 10000,
});

const deny = await post("/issuing/decide", {
  amount: 2500,
  merchant_category: "software",
  allowed_categories: ["fuel"],
  max_amount: 10000,
});

console.log("\nLOOM SCRIPT:");
console.log("1) Show allow.approved ===", allow.approved);
console.log("2) Show deny.approved ===", deny.approved, "reason:", deny.reason);
console.log("3) Show receipt.signature exists on both");
console.log("4) Say: setup + monthly care if Stripe/API breaks");
