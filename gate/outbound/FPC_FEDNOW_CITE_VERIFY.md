# Primary-source verify — May 2026 “FPC” FedNow/RTP APP gap

**Ask:** Confirm the load-bearing cite behind ranking FedNow/RTP #1 “Best new.”  
**Verdict:** **Holds.** Body was misreadable as UK Financial Policy Committee — it is the **U.S. Faster Payments Council**. Quote is on the live PDF.

---

## Body (disambiguation)

| Ambiguous “FPC” | Actual source |
|-----------------|---------------|
| ❌ UK Bank of England **Financial Policy Committee** | Not this document |
| ✅ **U.S. Faster Payments Council** (industry membership org) | This document |

Press release title uses “U.S. Faster Payments Council (FPC)” — https://fasterpaymentscouncil.org/blog/17139/U-S-Faster-Payments-Council-Releases-Guiding-Principles-for-Instant-Payments-Fraud-Dispute-Resolution  
**For Immediate Release — May 15, 2026**

---

## Primary PDF

**Title:** Instant Payments Fraud Dispute Resolution: Guiding Principles for the U.S.  
**File:** `FSWG_Instant Payments Fraud Dispute Resolution_05-15-2026 Final.pdf`  
**URL:** https://fasterpaymentscouncil.org/userfiles/2080/FSWG_Instant%20Payments%20Fraud%20Dispute%20Resolution_05-15-2026%20Final.pdf  
**Local copy:** `/opt/cursor/artifacts/fpc-primary/FPC_Instant_Payments_Fraud_Dispute_Resolution_05-15-2026_Final.pdf`

---

## Depth pass (2026-09-24) — Layer below FPC

**Sibling primary (not a substitute):** The Clearing House *RTP Rules Interpretation — Fraud Reporting and Acting on Alerts* (issued Oct 29, 2025) under Operating Rule II.G. Creates reason code **UAPA** for fraudulently induced RTP-native payments (impersonation / social engineering / deceptive tactics), effective **Mar 31, 2026**; reporting timing tightens **Mar 1, 2027**. Local: `/opt/cursor/artifacts/depth-layer/fednow/`. Full write-up: `DEPTH_LAYER_PASS.md`.

**Bar:** UAPA = **post-send network reporting**. Does **not** close the pre-push Clear/Seal gap FPC describes. Cite both: FPC (gap) + TCH UAPA (taxonomy).

---

## Load-bearing verbatim (Context: Why Dispute Capabilities Matter)

> Instant payments are credit-push and irrevocable. These characteristics support many valuable use cases but limit the types of recourse familiar from credit cards and other payment channels. Unauthorized fraud is addressed in the RTP® Network and the FedNow® Service rules, including application of Reg E where a consumer is involved. **Fraudulently induced authorized payments fall into regulatory gaps, and dispute handling across providers varies widely.**

Also in Scope: disputes include “Authorized but fraudulently induced payments (APP scams)” limited to **RTP Network and FedNow Service**.

---

## Nuance for outbound (GC bar)

- Document is **industry guiding principles** (“directional — not prescriptive”), **not** a Fed/BoE regulatory order.
- Safe cite: **“U.S. Faster Payments Council, Instant Payments Fraud Dispute Resolution (May 15, 2026)”**
- Unsafe: bare “May 2026 FPC” (reads as UK Financial Policy Committee).

Gap fact = **confirmed**. Abbreviation = **must be spelled out** in any Plan B email.
