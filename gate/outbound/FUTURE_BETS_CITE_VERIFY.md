# Future Bets cite verify — FB-1 / FB-2 / FB-3 primary close-out

**For:** Claude (flag: two unverified citations + FB-1 pin-cite double-check)  
**Pulled:** 2026-09-24 — CPPA approved-regs PDF · Colorado Signed Act PDF · EUR-Lex consolidated OJ  

**Bar:** same as Nacha / FPC / CL7 / Incline docket — primary text, not summaries.

---

## Verdict table

| Cite | Result |
|------|--------|
| FB-1 pin `11 CCR § 7200(b)` | **Correct.** Article 11 opens at § 7200; (b) is the Jan 1, 2027 compliance clock. |
| FB-1 alternate `§ 7120` | **Wrong section for ADMT.** § 7120 = Article 9 cybersecurity audits. |
| FB-2 bill `SB 26-189` | **Correct.** Signed Act PDF caption: `SENATE BILL 26-189`. |
| FB-2 Governor signed May 14, 2026 | **Correct.** leg.colorado.gov history: `05/14/2026 · Governor · Governor Signed`. Session laws: Effective Date `05/14/2026`, Chapter `131`. |
| FB-2 “≤30 days” notice | **Mechanic correct; quote tighter.** Statute: **“WITHIN THIRTY DAYS AFTER MAKING THE DECISION”** (6-1-1704(3)). Prefer that wording over “≤30 days.” |
| FB-2 *xAI v. Weiser* enforcement stay | **Real — confirmed on RECAP Doc 24.** Downgrade FB-2 to **Tier 1-contested**. Statute clock on books; AG enforcement stayed as to SB24-205 **and replacement legislation** (SB 26-189) until 14 days after PI ruling. |
| FB-3 Reg (EU) **2026/1744** | **Correct OJ citation.** Consolidated AI Act lists ►M1: `REGULATION (EU) 2026/1744 … of 8 July 2026 \| L 1744 \| 1 \| 24.7.2026`. |
| FB-3 Dec 2, 2027 → Annex III / Art 6(2) | **Correct.** |
| FB-3 Aug 2, 2028 → Annex I / Art 6(1) | **Correct.** (Already closed on primary this session — no open spot-check gap.) |

**Outbound:** FB-1 and FB-3 may ship as settled Tier 1 clocks. **FB-2 only with stay caveat** (or hold off Plan B copy until stay clears). Soft-fix CO notice line to “within thirty days.”

---

## FB-1 — CA CCPA ADMT pin cite

**Primary PDF:** CPPA *Approved Regulations Text*  
https://www.cppa.ca.gov/regulations/pdf/ccpa_updates_cyber_risk_admt_appr_text.pdf  
(Local: `/opt/cursor/artifacts/future-bets-verify/ccpa_appr_text.pdf`)

**Verbatim (Article 11 / § 7200):**

```
ARTICLE 11. AUTOMATED DECISIONMAKING TECHNOLOGY
§ 7200. When a Business’s Use of Automated Decisionmaking Technology is
Subject to the Requirements of This Article.
(a) A business that uses ADMT to make a significant decision concerning a
consumer must comply with the requirements of this Article.
(b) A business that uses ADMT for a significant decision prior to January 1, 2027,
must be in compliance with the requirements of this Article no later than
January 1, 2027. A business that uses ADMT on or after January 1, 2027, must
be in compliance with the requirements of this Article any time it is using
ADMT for a significant decision.
```

**Why “Article 11” and “§ 7200(b)” both appear:** Article 11 is the **article title**; § 7200 is the **first section** of that article. Pin-cite for the compliance clock = **§ 7200(b)**. Safe outbound: `11 CCR § 7200(b) (Article 11 — ADMT)`.

**§ 7120 check:** Same PDF, Article 9:

```
ARTICLE 9. CYBERSECURITY AUDITS
§ 7120. Requirement to Complete a Cybersecurity Audit.
```

That is **not** the employment/ADMT clock. Whoever cited § 7120 for employment ADMT mixed articles.

---

## FB-2 — Colorado SB 26-189 (bill text, not summary)

**Primary PDF:** Signed Act — https://leg.colorado.gov/bill_files/116489/download  
Bill page: https://leg.colorado.gov/bills/sb26-189  
(Local: `/opt/cursor/artifacts/future-bets-verify/sb26-189-signed.pdf`)

**Caption (page 1):** `SENATE BILL 26-189` — concerning automated decision-making technology in consequential decisions.

**Signing (bill history, not PDF signature OCR):**

| Date | Action |
|------|--------|
| 05/14/2026 | Governor Signed |
| Session laws | Effective Date **05/14/2026** · Chapter **131** · Automated Decision-Making Technology |

**Operative clock (SECTION 5 — bill text):**

```
SECTION 5. Effective date - applicability. (1) Except as otherwise provided
in subsection (2) of this section, this act takes effect January 1, 2027.
…
(3) This act applies to consequential decisions made on or after January 1, 2027.
```

**Post-adverse notice (6-1-1704(3) — page 11 of Signed Act):**

```
(3) IF A DEPLOYER USES A COVERED ADMT TO MATERIALLY
INFLUENCE A CONSEQUENTIAL DECISION THAT RESULTS IN AN ADVERSE
OUTCOME FOR A CONSUMER, THE DEPLOYER SHALL PROVIDE WITHIN THIRTY
DAYS AFTER MAKING THE DECISION:
(a) A PLAIN LANGUAGE DESCRIPTION OF THE CONSEQUENTIAL
DECISION AND THE ROLE THE COVERED ADMT PLAYED IN THE
CONSEQUENTIAL DECISION;
```

**Memo fix:** replace “≤30 days” with **“within thirty days”** (statutory words).

### FB-2 addendum — *X. AI LLC v. Weiser* stay (2026-09-24)

**Why it matters:** Claude correctly flagged that “Tier 1 = settled clock” overstates FB-2 while AG enforcement is stayed. Core statute facts still hold; **confidence tag must not**.

**Primary:** Minute Order, Doc 24, filed **04/27/26**, D. Colo. **26-cv-01515-DDD-CYC**  
RECAP: https://storage.courtlistener.com/recap/gov.uscourts.cod.253513/gov.uscourts.cod.253513.24.0.pdf  
(Local: `/opt/cursor/artifacts/future-bets-verify/xai-weiser/doc24-minute-order.pdf`)

**Verbatim (operative ordered ¶1):**

```
1. The defendant shall not initiate enforcement, including but not limited to
the initiation of an investigation, for alleged violations of SB24-205 (or any
legislation replacing or amending SB24-205 enacted during this legislative
session) that occurred or may occur on or before 14 days after the date the
Court issues a ruling on xAI’s forthcoming motion for a preliminary injunction
in this case.
```

**Map to SB 26-189:** Signed May 14, 2026 as the repeal/replace of SB 24-205 → falls inside “any legislation replacing or amending SB24-205 enacted during this legislative session.”

**Also ordered:** xAI’s PI motion due within **28 days after final adoption of rulemaking** on the (replacement) statute — enforcement pause can outlast the Jan 1, 2027 effective date.

**Precision vs earlier proposed order (Doc 18-1, denied as moot):** Doc 18-1 limited stay language to enforcement “against Plaintiff X.AI, LLC.” **Doc 24 (granted) drops the party-only limiter** and stays AG initiation of enforcement for alleged violations of the covered statutes generally. Cite **Doc 24**, not Doc 18-1.

**Outbound:** `on the books Jan 1, 2027; AG enforcement stayed pending xAI v. Weiser (1:26-cv-01515)` — or skip CO in copy until stay lifts.

---

## FB-3 — Regulation (EU) 2026/1744 + Annex mapping

**Primary:** EUR-Lex consolidated AI Act as of **27.07.2026** (post-amendment):  
https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:02024R1689-20260727  
(Local extract: `/opt/cursor/artifacts/future-bets-verify/` + prior OJ pull `L_202601744EN`)

**Amending act identity (consolidated “Amended by” table):**

```
►M1  REGULATION (EU) 2026/1744 OF THE EUROPEAN PARLIAMENT AND OF
     THE COUNCIL of 8 July 2026    | L 1744 | 1 | 24.7.2026
```

OJ file basename from live pull: `L_202601744EN.000101.fmx.xml` — matches **L 1744 / 2026**. Title: amending Reg (EU) 2024/1689 … (Digital Omnibus on AI). Done at Strasbourg **8 July 2026**; enters into force third day after OJ publication.

**Art. 113 date map (amending point (40) / consolidated application text):**

```
Chapter III, Sections 1, 2, and 3, with the exception of Article 6(5), shall apply from:
  (i) 2 December 2027 as regards AI systems classified as high-risk pursuant to
      Article 6(2) and Annex III; and
 (ii) 2 August 2028 as regards AI systems classified as high-risk pursuant to
      Article 6(1) and Annex I;
```

| Date | Maps to |
|------|---------|
| **2 December 2027** | Art. **6(2)** + **Annex III** high-risk use cases |
| **2 August 2028** | Art. **6(1)** + **Annex I** product/safety-component systems |

Memo mapping was already correct.

---

## Outbound-safe cite strings (post-verify)

- **FB-1:** `11 CCR § 7200(b) (Article 11 ADMT); compliance by Jan 1, 2027`
- **FB-2:** `Colorado SB 26-189 (signed May 14, 2026; Ch. 131); C.R.S. 6-1-1704(3) — within thirty days; act effective Jan 1, 2027`
- **FB-3:** `Regulation (EU) 2026/1744 (OJ L 1744, 24.7.2026) amending AI Act Art. 113 — Ch. III §§1–3 from 2 Dec 2027 (Annex III / Art. 6(2)) and 2 Aug 2028 (Annex I / Art. 6(1))`
