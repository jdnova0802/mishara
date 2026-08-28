# Commit-time authorization — Claude pressure test

**Not mountain.** Honest answers on Bind Ticket / epoch / exclusion before public pitch.  
**Spec:** `gate-commit-auth-v1` · `/.well-known/commit-auth.json`

## Front-page sentence (keep)

> Signatures prove a hop occurred. Tickets prove the hop is still allowed to spend, right now, once, for this job and this write.

Ed25519 is still the **ink**. Tickets / epoch are **authorization** (stranger-grade today). We do **not** claim better crypto than Ed25519.

JSON key: `authorization_vs_attestation` (was `greater_than_ed25519` — renamed so security readers don't hear "we beat Ed25519").

---

## Competitive survey (Aug 28) — honest map

**Lane is populated.** Pre-execution proof, non-execution proof, and FRE-shaped receipts are **contested**, not empty.

| Actor | What they claim | vs Gate |
|-------|-----------------|--------|
| **Authproof Cloud** | Receipt before act; RFC 3161 chain; HIPAA / managed-AI verticals; **shipping product + pricing** | Same *attestation* lane — **not** insurance bind + epoch lock |
| **Proof-Carrying Agent Actions** (arXiv 2606.04104, Jun 2026) | `non_execution_proof` alongside execution/pending/partial | Names our restraint receipt — **prior art exists** |
| **CertNode** | ES256 JWS, RFC 3161, Bitcoin anchor, FRE 902(13)/(14), EU AI Act 12/14 | **FRE angle taken** — we don't lead FRE |
| **IBCT / AIP** (Prakash, arXiv 2603.24775, Mar 2026) | Identity + attenuated auth + provenance; Biscuit/JWT; 0.049ms verify; 600/600 adversarial reject | **Capability-token shape** — see diff below |
| **Parakhin** (arXiv 2603.09875, Mar 2026) | TTL lease revocation scales **O(v · TTL)** at agent speed; proposes **execution-count** RCC | **Threat to TTL-as-revocation** — see answer below |
| **IETF drafts** | signed-receipts, compliance-receipts, attestation-receipts, aiagent-auth (multiple v07+) | **Standards consolidating** — we **extend** for bind + epoch, not replace |

**Do not lead:** “pre-execution proof” (crowded). **Do lead:** epoch lock → ticket-vs-signature → BYOK → **insurance bind moment**.

**Survives (pitch core):**
1. **Epoch lock** — HALT until real CHARGE; no admin resurrect (trust property, not token shape)
2. **Insurance bind path** — carrier PAS/PolicyCenter/Duck Creek; NAIC/Exhibit D; nobody else at bind-and-issue
3. **GAAIA letter / federal record (Jul 27, 2026)** — regulatory seed, not replicated in survey

---

## Parakhin (arXiv 2603.09875) — TTL answer (CALL-CRITICAL)

**Their claim:** At agent execution velocity *v*, TTL-based lease revocation exposes **O(v · TTL)** unauthorized operations before coherence catches up. Shorter TTL does not fix it — only shifts overhead. They propose **execution-count budgets** (RCC) capped at **D ≤ n**, independent of *v*.

**Our read:** Correct for **general agent credentials** reused across many API calls (JWT lease, cached capability, MCP mesh at 100+ ops/tick).

**Gate Bind Ticket is not that primitive:**

| Parakhin lease/TTL | Gate Bind Ticket |
|--------------------|------------------|
| Reusable until expiry | **Single-use** atomic consume (`single_use: true`) |
| Many ops per credential | **One** married spend fingerprint per ticket |
| Revocation = shorten TTL | Revocation = **epoch HALT**, **license fuse**, **consume** |
| Agent-speed mesh | **Human/PAS bind** — one irreversible bind write |
| Exposure ∝ v · TTL | Successful unauthorized bind **≤ 1 per issued ticket** (consume is atomic) |

**Verbatim for engineers:**  
> TTL bounds **freshness**, not **multi-call revocation**. We use a **15s default TTL** as a museum timer (stale hop cannot spend), not as the sole revocation story. **Single-use redeem + spend fingerprint + server clock + epoch lock** is the bind-path answer. Parakhin’s impossibility applies to **TTL-as-lease for high-velocity reusable tokens** — we do not sell that.

**Honest gap:** Failed redeem **attempts** inside TTL can repeat (retryable by design). That is not a successful bind. If we ever issue **multi-spend** tickets for agent fleets, we must add **execution-count budget** (Parakhin RCC) or eager invalidation — **not shipped; Mouth Ceiling.**

**Patent / prose:** Claim **commit-time single-use authorization at bind** + **epoch lock**, not “we invented TTL revocation.”

---

## Redeem endpoint availability (second engineer question)

**Server redeem is revocation.** If redeem is unreachable, there is no offline bind grant — the ticket is not a bearer credential the PAS can spend locally.

**Our pick: fail-closed.** Already wired:

| Condition | Behavior | Ticket consumed? |
|-----------|----------|------------------|
| Redeem HTTP error / timeout / partition | Bind **blocked** (403 from scanner; 503 if upstream hop unreachable) | **No** — consume is atomic server-side only on success |
| Redeem returns `halt` / validation fail | Bind blocked; `radiation_abort` on clock/skew/mismatch | **No** |
| Redeem returns `ok` | Bind may proceed (scanner forwards) | **Yes** — single-use burn |

**Ops tradeoff (say it out loud):** Gate or redeem outage **stops real binds** until service returns. We do **not** fail-open (no “LIVE hop = bind anyway”). Epoch lock has **no hole** through redeem bypass on the bind path — there is no cached offline YES.

**Implementor contract:** `gate-spend-protocol-v1` → `redeem.fail_closed: true`. Cloudflare worker: redeem failure → `haltResponse` (403); hop 503 → 503. See `cloudflare-worker-bind.js`.

**Verbatim for engineers:**  
> Revocation lives at redeem. Redeem down means bind down — by design. Retry when Gate is back; ticket stays valid until TTL if not yet consumed.

---

## Availability posture (third engineer question — Stavan / renewal day)

Fail-closed makes **our uptime your bind uptime.** Say the ops cost in the same breath as the security win.

**Today (honest):**
| Topic | Posture |
|-------|---------|
| **Topology** | Single region (Render); persistent disk `/var/data/gate.db` |
| **SLA** | **No five-nines claim today** — best-effort with `/health` fail-closed if misconfigured |
| **Gate down** | Bind **blocked**; redeem unreachable; tickets **not** consumed; carrier retries when Gate returns |
| **3am renewal batch** | Same rule — no silent bypass. Coordinate maintenance windows; queue retries after restore |
| **Manual override** | **No admin resurrect.** Epoch HALT lifts only on real Velaru **CHARGE** webhook — not ops console, not UW chat yes |
| **Partition** | Scanner/worker treats redeem failure as halt (403/503); PAS cannot spend ticket locally |

**Roadmap (post–Gate 1 / production weld — name it, don't hedge):**
1. **Cold Standby Mirror** — read-only witness: proves last HALT + epoch state during outage; **cannot mint LIVE** (availability without fail-open hole)
2. **Multi-region redeem** — active/passive or regional failover; RPO/RTO in weld contract
3. **Bind Weather** — carrier-facing public dashboard: uptime, redeem latency, HALT depth, maintenance windows

**Verbatim for Stavan:**  
> Single region today, fail-closed by design — your bind stops when we stop, and we don't pretend otherwise. There is no override that breaks epoch lock; CHARGE-only resurrection. Roadmap is cold standby witness plus multi-region in the production weld, with maintenance windows on renewal batches. We'd rather lose a night of binds than mint a ghost bind.

---

## IBCT / Biscuit / macaroons / UCAN — what's actually novel

**Overlap (do not claim alone):**
- TTL / not-before / not-after
- Single-hop JWT or Biscuit attenuation (IBCT compact/chained)
- Spend / request fingerprint (macaroons, Biscuit caveats)
- Append-only provenance chain (IBCT, UCAN)

| Piece | Patent lane | GTM lane |
|-------|-------------|----------|
| **Epoch lock** — HALT until Velaru CHARGE; `not_admin_charge: true` | **Primary claim candidate** — non-resurrecting operator HALT | Pitch lead |
| **Commit-time authorization** — LIVE hop ≠ bind grant; redeem-at-commit + married write | **Secondary claim** — single-use commit authorization at bind | Pitch #2 (ticket vs signature) |
| **Insurance bind surface** — PAS/PolicyCenter, BlocksBind UW, NAIC/Exhibit D | Prior art on tokens; **not patentable alone** | Vertical moat — carrier bind choke |
| **BYOK twin** — Velaru cannot forge alone | Supporting (dual-control) | Pitch #3 |
| **Burn policy (verbatim)** — burn on success only; failed redeem retryable | Supporting detail | Ops honesty |

**Do not patent the vertical.** Patent the **epoch lock** and **commit-time single-use bind authorization**; sell the **carrier bind moment**.

IBCT wins benchmarks on **MCP delegation mesh**. Gate wins on **carrier bind choke + non-resurrecting HALT**.

---

## Claim grades (do not mix voices)

| Primitive | Grade today | Buyer / stranger voice? |
|-----------|-------------|-------------------------|
| Epoch lock | **stranger** | **Yes — pitch lead** |
| Bind Ticket | **stranger** | Yes — with Parakhin scope note |
| Exclusion | **map honesty** | **No** — until TSA/root |

**Verbatim hold:** *Map honesty today, not stranger-grade absence.*

---

## IETF / NIST posture (pick one: extend)

Drafts named in survey: `draft-farley-acta-signed-receipts`, `draft-marques-asqav-compliance-receipts`, `draft-chueayen-attestation-receipts`, `draft-klrc-aiagent-auth`; NIST AI Agent Standards Initiative (Feb 2026); NCCoE identity/auth concept paper.

**Named extension target:** `draft-marques-asqav-compliance-receipts` (**v07** at survey) — closest compliance-receipts profile to our lane (structured compliance artifact, not raw hop log).

**What we extend (not replace):**
- ASQAV compliance-receipt envelope where a bind decision receipt applies
- **Add:** `gate-epoch-v1` non-resurrecting HALT semantics
- **Add:** `gate-commit-auth-v1` bind-ticket redeem-at-commit + spend-protocol married write
- **Add:** insurance bind profile (PAS/PolicyCenter bind-only; refusal of bind-and-issue/issue)

**Artifacts:**
| Now (shipped) | Next (post–Gate 1) |
|---------------|-------------------|
| `gate-commit-auth-v1` cites ASQAV as upstream profile; `/.well-known/commit-auth.json` | Individual draft **`draft-velaru-gate-bind-commit-profile`** referencing ASQAV + epoch lock extensions |
| RFC 3161 timestamping earn-keep on exclusion (when TSA lands) | Contribute bind-commit profile to ASQAV WG or ACTA signed-receipts chain |

**Stance without artifact is not enough.** GAAIA letter worked because it was a **record**. IETF posture works when **`gate-commit-auth-v1` names ASQAV** and the bind-commit profile draft is filed — not when we only say "extend."

**We are not** claiming to own the compliance-receipts draft. **We are** claiming the **non-resurrecting HALT** and **bind-path commit semantics** as extensions atop it.

---

## Pitch + outbound (Aug 28 order)

1. **Epoch lock** — you can't quietly undo the block either  
2. **Ticket vs signature** — attestation + authorization at commit (scope: bind, not agent mesh)  
3. **BYOK / stranger verify** — Velaru cannot forge alone  
4. **Insurance bind moment** — NAIC/PAS/Exhibit D (vertical, not CISO SaaS)

**Cut as lead:** pre-execution proof, FRE 902 hero, generic AI governance.

**Outbound moment (verbatim):** *What can't run once the ticket's gone — the withdraw that didn't run, and the ticket that's already burned.*

---

## Public check (ship day)

```bash
curl -sS https://gate.velaru.xyz/.well-known/commit-auth.json | jq .
curl -sS https://gate.velaru.xyz/.well-known/claim-grades.json | jq .
```
