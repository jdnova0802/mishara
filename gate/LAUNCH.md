# Gate API — Launch copy

Replace `YOUR_GATE_URL` with your deployed URL (e.g. `https://gate-api.onrender.com`).

---

## Pinned tweet / X bio

**Bio:** Agent mortality fuse · DEAD = can't act · verify every hop  
**Link:** YOUR_GATE_URL/install  
**Pinned:**

> Built a kill switch for agents.
>
> DEAD fuse → verdict:false + signed receipt.
> Anyone verifies free.
>
> DIY: free API key (1k hops/mo)
> Done-for-you: $2,500 · 48hr install · 2 slots
>
> YOUR_GATE_URL

---

## Launch thread (post in order)

**1/** Your agent has no kill switch.

I built one. DEAD = it cannot act. Every hop → receipt strangers verify.

Free API key. Or I wire it in 48hr for $2,500.

🧵

**2/** One question: *Can this agent still act right now?*

Four states only:
LIVE · ARMED · DEAD · UNSIGNED

Not a compliance score. Public existence proof.

**3/** Hop demo (copy-paste):

```bash
curl -s -X POST YOUR_GATE_URL/v1/fuse/hop \
  -H "Authorization: Bearer gate_sk_live_..." \
  -H "Content-Type: application/json" \
  -d '{"fuse_id":"fuse_velaru_drill"}'
```

DEAD → `verdict: false` + `verify_url`

**4/** Post the verify link in replies. That's the proof flex — not a dashboard screenshot.

Stranger confirms at velaru.xyz/verify

**5/** Two paths:

→ DIY: YOUR_GATE_URL (free tier, 402 when you hit 1k hops)
→ Done-for-you: YOUR_GATE_URL/install ($2,500, 2 slots, 48hr)

**6/** Engine: Velaru (Patent #64/124,027)

I spent a year on internal architecture. External layer is meter + price + proof.

Feedback welcome.

---

## Show HN title

Show HN: Gate API – metered agent fuse hop (DEAD = fail closed)

---

## DM auto-reply (if someone DMs "FUSE")

> 48hr install — $2,500 prepay, non-refundable, one agent path.
> Book: YOUR_GATE_URL/install
> DIY free: YOUR_GATE_URL/signup

---

## After first payment screenshot

Post Stripe notification (blur email) with caption:

> First 48hr fuse install booked.
> DEAD → fail closed → stranger verify.
> YOUR_GATE_URL/install — [N] slots left

That's your external reflection post — real money, real proof.
