# PASTE — Sink / OCT sponsor-BIN outreach (start the 90–120d clock)

**26 Sep 2026.** Parallel to Monday diligence. Do not block cash path.

---

## Next step (who)

**Primary:** **Column N.A.** — `sales@column.com`  
Also submit the web form: https://column.com/contact  

**Why Column first (confirmed, not vibe):**
- Public docs: Column is the **issuing bank / BIN sponsor** for card programs; launch clock **90–120 days** (https://docs.column.com/guides/intro-to-card-issuing/).
- Published economics: can deliver **100% of interchange received** to Program Manager partners (same page) — structure already verified earlier tonight.
- Gate’s Sink mouth needs a **receiving BIN with Fast Funds / OCT receive enabled**. Stripe Issuing ≠ OCT sink. Column is the shortest named sponsor path that matches prior digs.

**Parallel (same week, don’t wait on Column reply):**
- Lithic / Galileo as **issuer processor** RFQ (auth stream + BIN partnership path) — secondary.
- Do **not** lead with Marqeta if the goal is Column-style pass-through; keep as backup.

**Not the contact for this ask:** Visa Direct `USVisaDirect@visa.com` is for **acquiring / push (sender) OCT APIs**. Nisaba’s gap is **receive on our destination BIN**, not become a Visa Direct acquirer.

---

## Ready-to-send RFQ (email)

**To:** sales@column.com  
**From:** Nisaba LLC / hello@velaru.xyz (or founder address)  
**Subject:** Card program RFQ — Fast Funds / OCT *receive* on Column BIN (Program Manager)

```
Hi Column team —

Nisaba LLC (US) is requesting an intro on a card program where Column would be the BIN sponsor / issuing bank.

Use case (short):
We operate Gate (gate.velaru.xyz) — a fail-closed clearance mouth before irreversible money moves. We already run a Soft OCT / Fast Funds *receive* mouth (Clear before inbound push lands). We need a real receiving BIN with Fast Funds / Original Credit receive enabled so money_real can go true. We are not asking Column to custody float for us as a product; we need program + BIN + receive enablement.

Questions we need answered to start diligence / clock:

1) Do you sponsor debit/prepaid BINs that can *receive* Visa Original Credit / Fast Funds (inbound push to our cards), not only spend/auth?
2) What is the receive fee schedule to the issuer (or pass-through) for OCT vs Fast Funds on that BIN?
3) Typical timeline from kickoff → live Fast Funds receive (you publish 90–120 days for card programs — confirm for this receive path)?
4) Program Manager model: confirm whether “100% of interchange received” (per your card issuing guide) applies, and what bank / network / processor fees sit outside that.
5) Auth: can we run realtime approve/decline (JIT / webhook) so Gate Clear/Never sits on both spend auth and inbound OCT accept?
6) What docs / KYC / BSA package do you need from Nisaba to open the conversation (entity docs, owners, expected volume, use-case memo)?

Entity: Nisaba LLC
Product surface: https://gate.velaru.xyz/sink-mouth
Contact: [NAME] · [EMAIL] · [PHONE]

Happy to jump on a 20-minute call. Goal this week is to start the onboarding clock, not close commercials.

Thanks,
[NAME]
Nisaba LLC
```

---

## Web form fill (column.com/contact)

| Field | Suggested |
|-------|-----------|
| Stage | Early / building (honest) |
| Customers | Fintech / platforms that push payouts (payroll, gig, insurance claim OCT, marketplace) |
| Heard about | Docs / card issuing guide |
| Building | Program Manager card program: destination cards that **receive** Visa OCT / Fast Funds; Gate Clear/Never before accept. Also spend auth mouth. |
| Other | Paste the 6 questions from the email. Ask for `sales@column.com` reply + calendar link. |

---

## What Nisaba should have ready *before* the call (checklist)

| Item | Status to confirm |
|------|-------------------|
| Certificate of formation / LLC docs (Nisaba LLC) | Have / get PDF |
| EIN letter | Have / get |
| Beneficial ownership / KYC IDs for control persons | Ready to share under NDA |
| Operating agreement / ownership cap table (high level) | Ready |
| Use-case 1-pager (Sink mouth + Clear/Never; Gate never holds float) | Draft from this RFQ |
| Expected volume bands (honest, even if low Y1) | e.g. pilot: hundreds–low thousands OCT/mo; year-1 target bands TBD — **don’t invent** |
| Geography / customer type (US debit destination) | US |
| Existing bank / Stripe Issuing status (spend side live / float pending) | Disclose — separate from OCT receive |
| Compliance contact + security questionnaire willingness | Yes |
| Prefer debit vs prepaid for receive BIN | Decide before call (ask Column which Fast Funds–enables easier) |

Volume: if unknown, say **“pilot volume TBD; we will not overstate — need your minimums.”** Better than fake GMV.

---

## Clock

| Step | Owner | When |
|------|-------|------|
| Send email + form | Founder | **This week** (starts 90–120d) |
| Column first reply / intro call | Column | Usually days–2 weeks |
| DD package | Nisaba | On their ask list |
| Live Fast Funds receive | Column + network | **~90–120 days** after kickoff (their published card-program band) |
| Flip Gate `money_real` on Sink | Eng | Only after BIN + one real receive |

---

## One-liner

**Start the clock with Column `sales@column.com` + contact form; ask Fast Funds/OCT *receive* on a Column BIN (not Visa Direct acquire). 90–120d begins when they open diligence — send this week in parallel to Monday.**
