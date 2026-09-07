# DESKTOP CURSOR HANDOFF — Nisaba hustles + Gate pay live

Paste this whole file (or point Desktop at it). Do the pay/deploy work first. Do not rebuild the cosmic map unless asked.

**Renewal / money:** Founder waiting until payday (~Fri). Cloud agent usage renews ~Sept 14. Prefer Desktop + Render Dashboard until then.

---

## 0. Identity (do not regress)

- Nisaba LLC = Action OS company, **not** a holdco
- Scarcity = **DENY that holds**
- Language: payout, bind, trip, print, release, settle, kill, reclaim — **not** “agents”
- Gate = commercial mouth · Velaru = proof
- `their_production` stays false until a real exclusive third-party weld
- Legal only — never drain / self-bounty / grey hold-funds theater

---

## 1. Already shipped (Cloud PR)

- Branch: `cursor/hustle-diligence-bind-room-c1dd`
- PR: https://github.com/jdnova0802/mishara/pull/39

### Surfaces

| What | Path | Price |
|---|---|---|
| Hustle 1 — Finality diligence | `/diligence` | **$2,500 deposit** → $5,000 72h review |
| One-pager (outreach) | `/diligence/one-pager.txt` | — |
| Offer JSON | `/diligence/offer.json` | — |
| Hustle 2 — Bind Room | `/bind-room` | **$1,750** due now |

Code: `gate/diligence.py`, `gate/templates/diligence.html`, tightened `gate/templates/bind_room.html`, checkout + webhook `diligence_deposit` in `gate/app.py`.

---

## 2. YOUR JOB — make pay LIVE (no secrets in chat/git)

### A. Merge / deploy
1. Review + merge PR #39 (or deploy the branch)
2. Confirm production Gate URL loads `/diligence` and `/bind-room`

### B. Stripe (Dashboard — paste values only into Render, never commit)
1. Create product **Finality diligence deposit** — **$2,500** one-time → copy `price_...`
2. Confirm Bind Room **$1,750** price exists → `price_...` (or keep Payment Link)

### C. Render env (Environment tab)
Set / confirm:

```
STRIPE_DILIGENCE_DEPOSIT_PRICE_ID=price_...
# OR:
VELARU_DILIGENCE_PAYMENT_LINK=https://buy.stripe.com/...

STRIPE_BIND_ROOM_PRICE_ID=price_...
# AND/OR (app has a default fallback link already):
VELARU_BIND_ROOM_PAYMENT_LINK=https://buy.stripe.com/...

STRIPE_SECRET_KEY=...
STRIPE_WEBHOOK_SECRET=...
GATE_DEV_MODE=0
GATE_PUBLIC_URL=https://YOUR_GATE_HOST
```

Webhook: `https://YOUR_GATE_HOST/billing/webhook` must receive `checkout.session.completed`  
Products handled: `bind_room`, `diligence_deposit`, install, weld, etc.

### D. Smoke test
- [ ] GET `/diligence` — Pay deposit CTA works (Checkout or Payment Link)
- [ ] GET `/diligence/one-pager.txt` — plain text offer
- [ ] GET `/bind-room` — Pay $1,750 CTA works
- [ ] Test-mode pay → success page + notify webhook if configured
- [ ] **Never** paste secret keys into Cursor chat or commit `.env`

---

## 3. Hustles-only quit sprint (founder plan)

**H1** = mouth/finality diligence (quit money)  
**H2** = Bind Room packs  
**Gym** = scoped bounty only (optional)  
**Primary** = Nisaba weld/bind path (fortune — parallel, not blocker for quit)

### Week loop
1. Send `/diligence` + `/bind-room` links
2. Pitch A: Bind Room **$1,750** now  
3. Pitch B: **$5k–$8k** review / **$2.5k deposit today** · 72h  
4. **Deposit before free work**
5. First **cleared** payment → give notice on 9-5

### Targets
Bridges · peg-outs · payouts · custody · BaaS sponsors · carriers/MGAs (Bind Room)

### Quit rule
Cleared deposit **or** Bind Room payment **or** ≥1 month living costs — then notice. Not on “maybe.”

---

## 4. After Thursday (product spine — later)

Only when founder unlocks build week:

1. eprint **2026/1685** × `exclusion.py` × `license_fuse.py` break memo  
2. Use-time Finality Sink (atomic redeem + fuse recheck)  
3. Weld contract: no soft `license_id` omit on chosen mouth  
4. One exclusive door (payout clear and/or lab shutter)  
5. Dual-gate CHARGE  
6. Bind language: coverage fails closed on trip/DEAD  
7. PQ hybrid receipts / mind-bender priors = backlog  

FTO: US **12,671,589** Effector Truth Rail = same genus — counsel, don’t cosplay.

---

## 5. Do NOT

- Rebuild full underground atlas / ratings cosplay
- Center “agent gateway” homepage language
- Stand up MGA/captive before a welded mouth
- Ask founder for raw keys in chat — Render UI / local CLI only
- Grey Liquid-style self-bounty paths

---

## 6. One-liners

- Proof lifts deploy. Weld flips production.
- Nisaba owns the week. Hustles fund exit.
- CAN ≠ MAY. Mouth on the spend/finality edge.
- Software sells dashboards. You sell MAY — charge like finality.

---

## 7. Done when

1. PR merged / deployed  
2. Diligence + Bind Room **take real (or test) card payments** on prod URL  
3. Founder has both links ready for outreach paste  

END HANDOFF
