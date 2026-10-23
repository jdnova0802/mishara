# PASTE — Grey / aggressive crime programs × Gate (the hidden fit)

**Hunt date:** 27 Sep 2026  
**Ask:** Dig past public tip-bounty posters. Find something grey, aggressive, exciting.  
**Hit:** **USA PATRIOT Act § 314(b)** — FinCEN’s voluntary FI↔FI information-sharing **safe harbor**, refreshed **June 12, 2026** to push **real-time fraud** sharing (instant payments / FedNow-shaped). Not a bounty. Better than a bounty for Gate.

Prior hunts (#146 FinCEN/IRS WB, #147 crime-program map) remain: tip awards do not pay Gate. This hunt finds the **institutional** program that matches Gate’s prevention artifacts.

---

## The find (exciting + hidden)

### What § 314(b) actually is
- Statute: USA PATRIOT Act § 314(b); rule **31 C.F.R. § 1010.540**
- FinCEN page: https://www.fincen.gov/resources/section-314b  
- Fact sheet (June 12, 2026): https://fincen.gov/sites/default/files/shared/314bfactsheet.pdf  
- FDIC follow-on FIL (July 2026) tells supervised banks to use it for **fraud prevention**, not only classic AML

**Safe harbor:** registered financial institutions (and **associations of financial institutions**) may share information with each other to identify possible money laundering / terrorist activity — which FinCEN now expressly reads to include **fraud and other SUAs** — **without** the liability scare that usually freezes FI legal teams.

**Hard rule:** you may **not** share a SAR or reveal that a SAR exists. You **may** share underlying facts (transactions, typology, device/IP, newly added payee + large transfer, monitoring alerts, etc.).

**Why compliance people whisper about it:** it is not a glamorous “get paid 30%” poster. It is the grey pipe banks use (or under-use) to stop mule / BEC / instant-payment fraud **across institutions** before the next FI pays. June 2026 guidance is FinCEN telling them to stop being shy.

### Why Gate fits (for real)
Gate already mints the exact **underlying facts** an FI would share under 314(b):

| Gate artifact | 314(b) shareable? |
|---|---|
| `deny_registry` payout_hash (destination fingerprint, no PII) | Yes — typology / transaction identity without raw account |
| Issuing / prefinality `claim_scope` NO_GO (workflow lock, cap breach) | Yes — clearance refuse facts |
| FedNow sealed-payee / first-time-payee Never chips | Yes — “new payee + push” indicator FinCEN called out |
| Scenario 3 flag classification | Yes — fraud typology chips (not a SAR) |
| evidence-head / receipt signatures | Supporting custody of the refuse |

FedNow/RTP move in seconds — Gate’s pre-push Never + Issuing NO_GO are the facts FI-A would shove to FI-B under 314(b) **before** FI-B settles. That is the aggressive use-case the June 2026 sheet is aimed at.

### Who can stand in the safe harbor
| Actor | 314(b)? |
|---|---|
| BSA financial institution (bank, MSB, broker-dealer, insurer w/ AML program, …) registered on FinCEN FI Portal | **Yes** |
| Association whose members are only BSA FIs | **Yes** (FinCEN has blessed association structures; non-FI vendors may *operate* such an association — counsel required) |
| Gate LLC as bare SaaS vendor (not an FI, not an FI-only association) | **No** — not the registrant |
| Natural-person tipster chasing a bounty | **Wrong program** |

So: Gate does **not** collect a whistleblower check. Gate becomes the **pack / (later) hub** for FIs who already have the safe harbor.

### Grey association path (bigger, counsel-led)
FinCEN commentary / association rulings: a company that is **not** itself an FI can form and operate an association whose **membership is only FIs**, and that association can participate in 314(b). That is the aggressive product: Gate-operated association for welded FI customers sharing deny fingerprints / sealed-payee misses under safe harbor.

**Not shipped tonight.** Requires counsel, membership contracts, FI Portal registration as association, safeguards. Documented as the upside path.

---

## Other grey/aggressive programs — still empty for Gate-as-claimer

| Program | Why it looked exciting | Score |
|---|---|---|
| **Moiety / 19 U.S.C. § 1619** (customs informant, ≤25% / $250k cap) | Oldest aggressive U.S. informant statute; customs FCA adjacent | **EMPTY** — tip about customs fraud; Gate Never ≠ duty evasion |
| **Customs reverse FCA** (Island Industries / Sigma 9th Cir. 2025) | Qui tam on tariff evasion, treble | **EMPTY** for Gate product — needs relator with original import-fraud knowledge |
| **USSS Most Wanted rewards** (card shops, laundering rails, $1–10M) | Payment-crime adjacent posters | **EMPTY** — needs human intel on named platforms |
| **USPS Inspection Poster 296** | Mail fraud / money order rewards | **EMPTY** |
| **Kleptocracy Asset Recovery Rewards** (up to $5M) | Hidden Treasury program | **EMPTY / LAPSED** Jan 1 2024 (reauth bills pending — not live) |
| SEC / CFTC / FinCEN WB / DOJ CWA / IRS 211 | Covered in #146–#147 | **EMPTY** for Gate |

---

## What we built (small, honest)

Mouth **`/314b-share`** — same standard as DSP reject:

- Classifies SHAREABLE / NOT THIS / HOLD from chips  
- Packs a **share packet checklist** of Gate facts an FI may hand to a verified peer  
- **`gate_transmits_to_peers: false`** — Gate never sends  
- **`gate_registers_for_you: false`** — FI registers on FinCEN FI Portal  
- Blocks SAR / SAR-existence in packet  
- Labels **`not_a_bounty: true`**

```bash
curl -sS -X POST https://gate.velaru.xyz/v1/314b-share \
  -H 'content-type: application/json' \
  -d '{"sharer_is_bsa_fi":"yes","sharer_314b_registered":"yes","peer_314b_verified":"yes","purpose_fraud_or_ml":"yes","includes_sar_or_sar_existence":"no","has_underlying_facts":"yes"}'
# → word SHAREABLE + share_pack (after deploy)
```

---

## Build ladder (if we double down)

| Step | What | Risk |
|---|---|---|
| **0 (this PR)** | `/314b-share` pack mouth | Low — advisory, no transmit |
| **1** | Export helper: event_id → 314(b)-shaped JSON from deny/claim_scope | Low — customer-owned |
| **2** | Counsel memo: Gate as operator of FI-only association | Medium — legal |
| **3** | Association registration + peer verify against FI Portal list + encrypted share | High — real 314(b) hub |

Do not skip counsel on steps 2–3. Do not pretend step 0 earns awards.

---

## Bottom line

| Question | Answer |
|---|---|
| Hidden aggressive program that fits Gate? | **Yes — § 314(b) FI fraud-sharing safe harbor (June 2026 refresh)** |
| Is it a bounty? | **No — better: liability shield + real-time cross-FI interrupt** |
| Does Gate collect government $$? | **No** |
| What’s exciting? | Instant-payment fraud facts Gate already mints are exactly what FIs may now share under safe harbor |
| What’s next if hungry? | Association hub (counsel) — not tip hunting |

Prevention stays Gate. 314(b) is how Gate’s refuses become **sharable weapons** between banks without becoming a whistleblower skid.
