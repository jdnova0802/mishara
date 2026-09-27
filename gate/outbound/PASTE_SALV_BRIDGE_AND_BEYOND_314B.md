# PASTE — Beyond §314(b): Salv Bridge check + nearest grey/aggressive share rail

**Hunt date:** 27 Sep 2026  
**Ask:** Same standard as DSP / PSFA / 314(b). Find a real aggressive grey-zone information-sharing or fraud-prevention program **beyond §314(b)** that Gate could plug into, nearest to build. Confirm **Salv Bridge** specifically.  
**Verdict:** Salv Bridge is **real and live** — but it is **not a Gate network seat**. Nearest shippable fit past 314(b) is **FedNow OC-8 Appendix C fraud reporting** (+ Network Intelligence API as FedLine ladder).

---

## 1. Salv Bridge — confirmed

| Claim in the search lead | Verdict | Cite |
|---|---|---|
| Live cross-institution real-time intelligence platform | **TRUE** | https://salv.com/product/salv-bridge/ — 100+ FIs, 16+ EU/UK jurisdictions; product claims **60,000+** lawful exchanges **since 2021** (~four+ years) |
| Encrypted FI↔FI RFIs in the suspicion phase (APP fraud, mules, sanctions RFIs) | **TRUE** (vendor product) | Same; Fraud RFIs use-case brochure at salv.com / HubSpot product PDFs |
| Public AML API for customers | **TRUE** | https://docs.salv.com/api/ — OAuth2 client-credentials; alert types include `BRIDGE` / `MANUAL`; Bridge-specific partner docs are gated behind customer UI |
| Regulators “mandating cross-institution intelligence sharing starting 2027” | **HALF-TRUE / OVERSOLD** | See §2 below — do not treat Salv marketing as the statute |

### Can Gate join Salv Bridge as a peer?
**No** — not as bare SaaS. Bridge membership is for **banks / PSPs / other obliged financial entities** exchanging case intelligence with each other. Gate is not an FI/PSP peer on that network.

### Can Gate supply artifacts *to* Bridge members?
**Yes, in principle** — same shape as 314(b) pack: deny hash, claim_scope, sealed-payee Never facts could feed a Bridge RFI / manual alert **that the FI customer sends**. That requires (a) EU/UK FI customers on Bridge and (b) a customer-owned Salv credential. **Not shipped as a Salv mouth tonight** — would be a fake SKU without a partner agreement and field map from gated Bridge API docs.

**Bottom line on Salv:** live commercial network / competitor-channel for EU Art 75 partnerships. Exciting. Hidden from U.S. tip-bounty hunters. **Not** a program Gate plugs into as itself.

---

## 2. The “2027 mandate” — split the statute from the brochure

| Instrument | What it actually says | Status (27 Sep 2026) |
|---|---|---|
| **AMLR Art 75** — Reg. (EU) **2024/1624** | Obliged entities **may** share in notified **partnerships for information sharing**, subject to DPIA, supervisory verify, strictly-necessary limits, STR onward-share FIU consent, etc. | In force; **applies from 10 July 2027** (Art 90). Permissive framework + conditions — **not** “must join Salv.” ELI: https://eur-lex.europa.eu/eli/reg/2024/1624/oj |
| **PSR Art 83 / 83a** (fraud data sharing) | Political agreement Nov 2025; **not yet** published in Official Journal as of this hunt. Industry expects application ~**2028**. | Forward-looking. Commission proposal COM(2023) 367 is not the final text. |
| **EPC FRIDA** (Fraud Information Distribution Arrangement) | SEPA scheme rulebook **v0.1** (EPC108-26, 9 Sep 2026) — public consultation **11 Sep–10 Dec 2026**; v1.0 target May/Jun 2027; **effect with PSR ~Q4 2028**. | **Not live.** https://www.europeanpaymentscouncil.eu/what-we-do/other-schemes/fraud-information-distribution-arrangement |

Salv’s blog/regtech pieces correctly point at Art 75 + PSR deadlines; the shorthand “regulators mandate sharing in 2027 via Salv Bridge” collapses a **permissive AML partnership rule (2027)** with a **forthcoming PSR fraud-sharing duty (~2028)** and a **commercial network that already exists**. Honesty keeps them apart.

---

## 3. Other greys checked — empty or farther than FedNow App C

| Program | Real? | Gate fit |
|---|---|---|
| **Early Warning / Zelle fraud consortium** | Yes — bank-owned National Shared Database; daily fraud file exchange among members | **EMPTY for Gate-as-peer.** Closed FI consortium. EWS’s own Sep 2025 payments-fraud RFI asks Congress for a 314(b)-like **safe harbor** (GLBA gap) — i.e. not the grey statute itself. |
| **TMNL (NL)** | Yes — five Dutch banks’ joint monitoring utility | Bank-only; redesigning under AMLR; no public Gate-join API |
| **FRIDA** | Scheme draft only | Not live until ~2028 |
| **FinCEN 314(a)** | Live FI Portal government→FI list | Wrong direction (respond to LE lists); not a prevention share rail for Gate artifacts |
| **§314(b)** | Already hunted / shipped separately | Out of scope for this ask (“beyond”) |

---

## 4. The hit beyond 314(b) — FedNow OC-8 Appendix C (+ NI ladder)

### What it is
- **Operating Circular No. 8, Appendix C — Fraud Reporting Procedures** (Reserve Banks; public redline among FRBservices OC-8 PDFs).
- FedNow **Participants shall** investigate Unusual Payment Orders and report **Reportable Transfers** (good-faith fraud) to the **FedNow Service** and to the **other Participant** party to the transfer.
- Public message paths (Operating Procedures): **camt.056 reason FRAD** (sender) / **pacs.004 reason FR01** (receiver).
- Companion live tool: **FedNow Network Intelligence API** — launched **28 Apr 2026** for early adopters; sending FIs **and Service Providers** pull receiver-account data insights before pacs.008 (FedLine Advantage/Direct + API cert). Press: https://www.frbservices.org/news/press-releases/042326-fednow-network-intelligence-api-empowers-participants-payments-confidence · Fed360 14 May 2026 · Operating Procedures §10.5.

### Why this is nearer than Salv for Gate
| | Salv Bridge | FedNow OC-8 App C |
|---|---|---|
| Geography | EU/UK | **U.S. rail Gate already mouths** (`/fednow-prepush`) |
| Legal form | Commercial network under Art 75 lane | **Contractual Participant duty** + ISO messages |
| Gate as peer? | No | No (Gate ≠ Participant) |
| Gate packs for FI customer? | Possible later | **Yes — shipped tonight** |
| Service-provider path named in primary docs? | Customer of Salv | **Yes — FedLine Service Provider** for NI API / profile |

Aggressive? Instant-payment fraud interrupt across institutions. Grey? Less “whisper safe harbor” than 314(b) — it is an OC duty — but the **FI↔FI + Reserve Bank report pipe** is the live U.S. cross-institution fraud-prevention program that matches Gate’s deny / claim_scope artifacts without inventing a bounty.

### What we built
Mouth **`/fednow-fraud-report`** — DSP / 314(b) standard:

- Classifies REPORTABLE / NOT THIS / HOLD  
- Packs App C checklist + suggested ISO path (FRAD / FR01)  
- **`gate_transmits_to_fednow: false`** — no camt.056 send  
- **`gate_is_not_fedline_endpoint: true`** — no fake FedLine client  
- Labels Network Intelligence as **FedLine ladder**, not this mouth  
- **`not_a_bounty: true`**

```bash
curl -sS -X POST https://gate.velaru.xyz/v1/fednow-fraud-report \
  -H 'content-type: application/json' \
  -d '{"caller_is_fednow_participant":"yes","report_role":"sender","investigated_unusual_payment_order":"yes","good_faith_fraud_reportable":"yes","has_underlying_facts":"yes"}'
# → word REPORTABLE + report_pack (after deploy)
```

### Build ladder
| Step | What | Risk |
|---|---|---|
| **0 (this PR)** | `/fednow-fraud-report` pack mouth | Low — advisory |
| **1** | Export helper: event_id → App C / camt.056-shaped JSON from deny + fednow-prepush | Low — customer-owned |
| **2** | FedLine Service Provider path + Network Intelligence API client for welded send Participants | High — connectivity, certs, OC agreements |
| **3** | EU twin: Art 75 partnership pack + optional Salv Bridge field map under customer credential | Medium/High — counsel + partner |

Do not ship a Salv-branded mouth without partner docs. Do not claim Gate is a FedNow Participant. Do not conflate Art 75 (2027 may-share) with PSR/FRIDA (later must-share scheme).

---

## Bottom line

| Question | Answer |
|---|---|
| Is Salv Bridge real? | **Yes — live EU/UK FI intelligence network since ~2021** |
| Is it a network Gate joins? | **No** — FI/PSP peers only; Gate can at most supply artifacts to members |
| Is the 2027 “mandate” real as stated? | **Art 75 applies 10 Jul 2027 (permissive partnerships). PSR fraud-share + FRIDA ~2028. Salv is not the mandated network.** |
| Real program beyond 314(b), nearest to build? | **FedNow OC-8 Appendix C fraud reporting** (+ Network Intelligence FedLine ladder) |
| Shipped? | **`/fednow-fraud-report` pack mouth + this pastable** |

Prevention stays Gate. Salv is the EU commercial whisper. FedNow App C is the U.S. rail duty that already wants the facts Gate mints.
