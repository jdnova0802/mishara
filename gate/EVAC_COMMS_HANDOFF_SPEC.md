# Evac Comms Handoff Spec — Invention Sketch

**Status:** invention sketch only — **not** product roadmap, **not** counsel packet, **not** shippable until Gate 1 + latch.  
**Purpose:** Name the **unseen gap** (crisis handoff clearing) and map Gate primitives onto **evac / NTN comms handoff** — DTCC shape × Iridium medium × epoch/redeem physics.  
**Companion:** `SHADOW_CHOKEPOINT_DOCTRINE.md` · `COMMIT_AUTH.md` · `NORTH_STAR.md` · `PATENT_COUNSEL_BRIEF.md`

**Do not send to patent counsel with Sep 1 email.** Non-provisional conversion stays on **two claim families** in `PATENT_COUNSEL_BRIEF.md`. This file is **field-definition + continuation seed** for post-latch counsel.

---

## One sentence

> **Crisis Handoff Clearinghouse (CHC):** federated members clear **cross-gateway / cross-constellation evac comms handoffs** through **single-use bind consume + epoch HALT + tombstone chain** — pipes plan routes; **we clear commits.**

---

## 1. The gap (documented — not invented)

| Source | What exists | What's missing |
|--------|-------------|----------------|
| **IMO / GMDSS** | Iridium + Inmarsat + multi-RMSS; MSI per-provider agreements; manual broadcast monitoring | **Unified federated bind** for safety/evac promulgation across providers |
| **EU GOVSATCOM / GEXTRECS** | Hub, Dynamic Planner, capacity optimization prototypes | **Commit finality** at handoff — not “best satellite,” but “handoff **counted**” |
| **3GPP NTN (Rel-18)** | Xn/N2 handover research; DAPS **not** supported for NTN; interruption on sat switch | **Consumable authorization** at handoff finality |
| **FCC (2020)** | Withdrew public maritime-satellite **accounting authority**; private fragmented settlement | **Clearing** for crisis routing commits (billing ≠ bind) |
| **RCC ↔ LES (COMSAR)** | Bilateral distress-priority arrangements per Land Earth Station | **Scheme-level** handoff grammar, not N custom leases |
| **ETAP / emission-finality (academia, 2026)** | Authorize at RF emission / execution boundary | **Federation + clearinghouse + tombstone** — theory, not deployed scheme |

**Nisaba claim:** nobody merges **DTCC governance + crisis comms medium + Gate epoch/redeem**. Pieces live in separate universes.

---

## 2. Core inventions (sketch)

### 2.1 Crisis Handoff Clearinghouse (CHC)

Industry-owned **clearing** for evac/crisis comms handoffs — not a constellation operator, not a planner.

| DTCC analog | CHC analog |
|-------------|------------|
| Member participants | OEM / integrator / gateway operators |
| Central counterparty feel | **Bind counterparty** — handoff doesn't **count** until cleared |
| CSDR / tombstone | **Comms tombstone chain** (§2.4) |
| User governance | **Federation table** — members vote scheme; **states observe** |
| Fees on cleared flow | Rent on **cleared handoff volume** (MAR / bps / per-handoff) |

**Not:** replacing IMO, FCC, GOVSATCOM Hub, or Iridium. **Interpose** at **handoff commit** only.

---

### 2.2 Evac Bind Ticket (EBT)

Single-use authorization **consumed at handoff finality**.

```
Issue (member) → Hold (in-flight handoff) → Redeem (at gateway/node) → Tombstone (immutable ACK)
                      ↑
                 Epoch HALT blocks all redeems in theater until defined resurrection
```

| Property | Spec intent |
|----------|-------------|
| **Single-use** | Same as Gate bind ticket — atomic consume; replay = deny |
| **Spend fingerprint** | Married to `{crisis_id, route_id, source_gateway, target_gateway, payload_class, priority_class}` |
| **TTL** | Freshness timer — stale ticket cannot handoff (museum timer, not sole revocation) |
| **Fail-closed** | Redeem unreachable ⇒ handoff **blocked**, not auto-forward |
| **Attestation insufficient** | Signature proves hop occurred; **ticket proves hop may complete now, once** |

**Field mapping from insurance foothill:** `job/epoch` → `crisis_epoch`; `bind write` → `handoff complete`; `form edition pin` → `routing edition / gateway profile pin`.

---

### 2.3 Crisis Epoch HALT

Regional/theater coordinator (member, not throne) may declare **crisis epoch**. While latched:

- All EBT redeems in theater require **active epoch match**
- Operator-console resurrect **excluded** — only defined **non-admin resurrection** (e.g. verified stand-down event)
- Loss of bind contact ⇒ **DENY** (Perimeter on orbital — no auto-LIVE forward)

**Distinction from Iridium priority preemption:** priority ≠ **commit proof**. HALT is **authorization geometry**, not QoS.

---

### 2.4 Comms Tombstone Chain

Append-only record binding:

```
Ω (issued EBT) → handoff attempt → redeem ACK | ρ deny → sealed tombstone
```

**Job:** after-action proof for coordinators — “this evac routing **happened** / **was refused** / **never attempted**.” DTCC CSDR shape for **crisis comms**, not securities.

Insider myth target: tombstones cited in regional after-action without TikTok.

---

### 2.5 Cross-RMSS SafetyCast bind (mid-horizon)

Registry + edition pin so MSI/SAR/evac broadcasts crossing **Iridium | Inmarsat | other RMSS** share **one scheme grammar** — members implement; observers monitor.

Does **not** replace per-provider RF. Replaces **N bilateral bind stacks** with **one clearing spec**.

---

### 2.6 Grammar-on-node (far-horizon)

Handoff node firmware / gateway appliance: **will not relay** without valid redeem at finality gate cluster (pre-RF / pre-ISL / pre-downlink — emission-finality adjacency).

**Interim:** grammar on member gateway software. **End state:** owned/controlled satellite/handoff nodes per doctrine §0.

---

### 2.7 Contingent Handoff Arrangements (CHA)

Pre-negotiated failover paths between members — invoked under cyber/outage/cascade; still **clears through CHC**; contingent ≠ bypass.

DTCC contingent-service concept applied to **comms handoff**, not ledger.

---

## 3. Federation (locked)

| Seat | Role |
|------|------|
| **Members** | OEMs, integrators, gateway operators — capital, fees, scheme votes |
| **Observers** | States / coordinators — visibility, exercise invoke, **no throne** — **anti-cult legibility**, not co-rule |
| **CHC operator** | Nisaba OpCo class — runs clearing, meter, registry; IP in HoldCo |
| **Pact enforcement** | **Legal** (scheme rules, NDAs) + **economic** (core routes through bind) |

---

## 4. Proof ladder (regional, not local)

| Stage | Receipt |
|-------|---------|
| **Gate 1** | Stranger paid + proved on **digital bind** (insurance foothill) |
| **Latch** | Production cite — partner can't ship without Gate grammar |
| **Regional invoke** | Theater-scale evac comms handoff cleared + tombstoned — **any geography**, multi-state / FEMA-region class |
| **S-tier** | Rent only; never sell choke |

Local/city pilot = insufficient for identity proof per doctrine.

---

## 5. Gate primitive map

| Gate today | CHC / EBT |
|------------|-----------|
| Epoch lock | Crisis epoch HALT |
| Bind ticket issue | EBT issue |
| Redeem at commit | Redeem at handoff finality |
| Spend fingerprint | Handoff fingerprint |
| License fuse | Member scheme fuse |
| Verify / stranger drill | Handoff tombstone verify |
| `redeem.fail_closed` | Handoff fail-closed |

Same physics — **new field definition**. Insurance = first foothill; evac comms = ceiling choke name.

---

## 6. Prior-art lanes to avoid leading

| Crowded | CHC leads instead |
|---------|-------------------|
| “Pre-execution proof” (Authproof, CertNode, IETF receipts) | **Handoff clearing + single-use consume at NTN finality** |
| Dynamic Planner / capacity optimization (GEXTRECS) | **Commit counted**, not route optimized |
| TTL lease revocation (Parakhin) | **Single-use EBT** — not reusable agent lease |
| Generic AI agent admission (SAB, PoE papers) | **Crisis federation scheme** — not agent mesh |
| Starlink/Iridium as operator | **Clearinghouse** — rent the bind, not the photons |

Continuation counsel **after** non-provisional + Gate 1 — not Sep 1 packet.

---

## 7. Open questions (honest)

1. **Regulatory home** — IMO adjunct vs GOVSATCOM supplier vs FCC Part 25 gateway class — counsel + domain expert required.
2. **First member** — gateway OEM vs MSS integrator vs regional coordinator exercise — GTM choice post-latch.
3. **Capital** — owned nodes vs leased gateway embed — doctrine says owned end state; path is staged.
4. **Defense adjacency** — accepted per doctrine; export/control counsel before classified embed.
5. **Patent continuation** — EBT/CHC as divisional or CIP off 64/124,027 — **after** primary non-provisional filed.

---

## 8. Suspicions (internal — read before building)

| Suspicion | Why it matters |
|-----------|----------------|
| **Planner cosplay** | If CHC becomes “smart router,” you lose DTCC shape — become GEXTRECS with extra steps |
| **Node capex fantasy** | Satellites/handoff nodes need capital/partners you don't have at Gate 0 — grammar-first or die waiting |
| **Sovereignty drift** | Crisis epoch + federation can slide into **throne** if states aren't observers only |
| **Insurance foothill trap** | PAS success can seduce you into Verisk-only life — insurance is on-ramp, not ceiling |
| **Academic collision** | ETAP/emission-finality Zenodo disclosures exist — prosecution must **diff** federation + clearing + epoch |
| **“No whistleblowers”** | Economic/legal pact ≠ suppressing lawful disclosure — scheme law must not ask for illegal silence |
| **Multi-planetary prose** | Grammar may travel; **don't** fund Mars nodes before regional tombstone |
| **Doc > latch** | This file is invention; **value = tombstone in production**, not spec elegance |

---

## 9. Sequence (unchanged)

```
Counsel week → non-provisional → Gate 1 → latch/spec cite → regional EBT invoke → nodes → S-tier rent
```

Mouth Ceiling, wealth apparatus, and Gate 1 outbound locks **still apply**. This spec **does not** authorize new L2 modules or skip counsel calendar.

---

*Nisaba LLC · Wyoming · Gate · Aug 28, 2026 · Invention sketch — not legal advice · not for Sep 1 counsel email*
