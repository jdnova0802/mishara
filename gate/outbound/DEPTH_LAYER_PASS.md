# Depth pass — Layer 2–4 on three already-verified finds

**Date:** 2026-09-24  
**Mode:** Depth over breadth. No new verticals.  
**Picks:** (1) FedNow/RTP · (2) vendor bank-change/BEC · (3) Future bets FB-1 ADMT + FB-2 *xAI* stay  

Artifacts: `/opt/cursor/artifacts/depth-layer/`

---

## 1) FedNow / RTP — below the FPC blog layer

### Already had (Layer 1)
U.S. Faster Payments Council *Instant Payments Fraud Dispute Resolution* (May 15, 2026) — “Fraudulently induced authorized payments fall into **regulatory gaps**.”

### One layer deeper (Layer 1 network rule + Layer 4 interpretation)

**Primary:** The Clearing House **RTP Rules Interpretation — Fraud Reporting and Acting on Alerts** (issued **Oct 29, 2025**; implements Operating Rule **II.G**).  
PDF: https://www.theclearinghouse.org/-/media/New/TCH/Documents/Payment-Systems/Fraud-Reporting-and-Acting-on-Alerts-Rules-Interpretation----issued-10292025.pdf  
Local: `depth-layer/fednow/Fraud-Reporting-Rules-Interpretation-10292025.pdf`  
Companion: *RTP Operating Rules Effective June 1, 2026* § II.G (Participant Response and Fraud Reporting Obligations) — local `RTP-Operating-Rules-Effective-June-1-2026.pdf`

**Verbatim chart (System Message Reports / camt.056):**

| Category | Code | Effective |
|----------|------|-----------|
| Unauthorized RTP-native Payment | **FRAD** | (existing) |
| **Fraudulently Induced** RTP-native Payment — Sender induced under false pretenses (impersonation, social engineering, other deceptive tactics) | **UAPA** | **Mar 31, 2026** |
| Fraudulently induced RTP-native Payment meeting RfP warranty claim prerequisites | **UPAY** | **Mar 31, 2026** |
| Timing: System Message Reports ≤ **two business days** after determination / OBO fraud report | — | **Mar 1, 2027** |

**What this adds beyond FPC:** FPC names the **regulatory gap** (directional industry principles). TCH **operationalizes** the same APP typology as a **required reason code (UAPA)** — post-send **reporting**, not pre-push Seal. Gate mouth still empty: stranger-verifiable Clear/Seal **before** the irrevocable send; UAPA is after-the-fact taxonomy.

**Outbound-safe cite stack:**
1. FPC May 15, 2026 Guiding Principles (gap language)  
2. TCH RTP Rules Interpretation Oct 29, 2025 — UAPA effective Mar 31, 2026  
3. RTP Operating Rules eff. June 1, 2026 § II.G  

**Do not claim:** TCH/UAPA closes the verification gap — it **labels** fraudulently induced sends for network reporting.

---

## 2) Vendor bank-change / BEC — FinCEN Scenario 3 (underlying typology)

### Already had
Wedge memo + industry BEC loss stats. Mouth: Seal before bank-detail write / ACH release.

### One layer deeper (Layer 1 FinCEN primary — the “exhibit” typology)

**Primary:** FinCEN Advisory **FIN-2016-A003** (Sep 6, 2016) — still cited as live red-flag baseline by FinCEN’s **2019 update** (FIN-2019 update PDF).  
https://www.fincen.gov/resources/advisories/fincen-advisory-fin-2016-a003  
2019 update PDF: https://fincen.gov/sites/default/files/advisory/2019-07-16/Updated%20BEC%20Advisory%20FINAL%20508.pdf  

**Verbatim — SCENARIO 3 – CRIMINAL IMPERSONATES A SUPPLIER:**

> A criminal impersonates one of Company C’s suppliers to e-mail and inform Company C that future invoice payments should be sent to a **new account number and location**. Based on this fraudulent e-mailed information, Company C **updates its supplier’s payment information on record** and submits the new wire transfer instructions to its financial institution that direct payments to an account controlled by the criminal.

**Red flag (same advisory):** beneficiary account info **different from what was previously used**; victim sends to “new account number, provided by a criminal impersonating a known supplier/vendor.”

**2019 update adds:** vendor impersonation as dominant typology in education/construction; fraudulent vendor invoices; foreign intermediary beneficiaries — still points back to 2016 red flags.

**What this adds:** Gate’s vendor-bank halt is not a metaphor — it is **literally FinCEN Scenario 3** as a Clear/Seal/Never control (out-of-band callback + dual approve receipt **before** the master-data write). Outbound can cite Scenario 3 by name without inventing a new fraud story.

**Still missing (next depth if needed):** a public complaint **exhibit** (actual forged bank-change email PDF attached to a civil filing). Not opened this pass — Scenario 3 is already primary enough for Plan B.

---

## 3) Future bets — CPPA comment record + *xAI* stipulation (not the stay headline)

### FB-1 CA ADMT — Layer 3 (rulemaking comments)

**Primary:** CPPA Final Statement of Reasons **Appendix A** (45-day comment summaries/responses) — 339 pp.  
https://www.cppa.ca.gov/regulations/pdf/ccpa_updates_cyber_risk_admt_fsor_appen_a.pdf  
Local: `depth-layer/cppa-comments/fsor_appen_a.pdf`

**Why § 7200(b) / Jan 1, 2027 exists (Agency response, not a blog):**

Comment asked to delay Article 11 until “24 months after final regulations are published” / non-retroactive. Agency **disagreed** with that framing, then:

> The Agency has **added § 7200(b)** to provide businesses until **January 1, 2027** to come into compliance with Article 11.

Elsewhere: Agency **revised § 7200(b)** to provide a specific date “to simplify implementation for businesses,” after narrowing Article 11 to ADMT for **significant decisions**.

**What this adds:** Jan 1, 2027 is not an arbitrary website date — it is the Agency’s **documented compromise** in the FSOR against a longer postponement ask. Strengthens FB-1 as clean Tier 1 vs FB-2.

### FB-2 *xAI v. Weiser* — Layer 2 full stipulation (beyond Doc 24 headline)

**Docket:** D. Colo. **1:26-cv-01515-DDD-CYC**  
Timeline from RECAP + AI Challenge Watch (primary PDFs local under `depth-layer/xai-docket/`):

| Date | Doc | What |
|------|-----|------|
| Apr 9, 2026 | Doc 1 | Complaint — challenges **SB24-205** |
| Apr 24, 2026 | Docs 12/16/17 | United States **intervenes** |
| Apr 24, 2026 | Doc 22 | **Revised** Joint Motion + Stipulation to Temporarily Stay Enforcement |
| Apr 27, 2026 | Doc 24 | Minute Order **grants** Doc 22 |
| May 14, 2026 | — | **SB 26-189** signed (replacement) — case still suspended pending rulemaking + PI |

**Doc 22 stipulation (verbatim substance) — deeper than the Minute Order alone:**

> the Colorado Attorney General **does not intend to promulgate rules** implementing SB24-205 or any legislation replacing or amending SB24-205 until the legislative session concludes. Further, the Colorado Attorney General **does not intend to enforce** SB24-205 or any legislation replacing or amending SB24-205 **until after the rulemaking process has concluded**.

Plus court-ordered stay through **14 days after PI ruling**; PI due within **28 days after final rulemaking** on the successor statute.

**What this adds:** Two clouds, not one — (a) **court stay** (Doc 24) and (b) **AG’s own non-enforcement-until-rulemaking** stipulation (Doc 22). Jan 1, 2027 effective date can arrive with **neither rules nor enforcement** yet. Confirms Tier 1-contested tagging.

---

## What we did *not* open (discipline)

- New verticals  
- Bounded Autonomy insurance deep-dive this pass (left for a later Layer-1 ISO CG 40 47 / SB 1120 primary pull)  
- CMS WISeR EFF FOIA exhibit re-pull (already cited earlier; not re-dug)  
- Forged bank-change email as civil-complaint exhibit (optional next Layer 4)

---

## Memo / outbound impact

| Find | Change |
|------|--------|
| FedNow/RTP | Add TCH UAPA (Mar 31, 2026) as **sibling cite** under FPC — reporting ≠ Seal |
| Vendor-bank | Cite **FinCEN FIN-2016-A003 Scenario 3** in Plan B / Diligence pain line |
| FB-1 | Jan 2027 clock grounded in **FSOR Appendix A** Agency response |
| FB-2 | Stay caveat now dual: **Doc 24 order + Doc 22 AG non-enforcement-until-rulemaking** |

**Cadence unchanged:** Fri bumps → Tue 10. Depth strengthens cites; does not expand send list.
