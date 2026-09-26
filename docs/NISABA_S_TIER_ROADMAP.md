# Nisaba — S-Tier Roadmap (post-scorecard)

This is the "what next" file, separate from the Flawless Dimensions scorecard. That file keeps the site honest. This file is about building actual moat, not more surface. Everything below assumes the scorecard's zero-tolerance items (link liveness, institutional tone, no borrowed credibility, single source of truth) are the floor, not the ceiling — don't let any of this ship on top of a site that still fails those.

---

## ⏰ TIME-SENSITIVE — act on this one first, separate from everything else

**NAIC Big Data and AI (H) Working Group — public comment period closes Tuesday, Sept 29, 2026.**

NAIC is exposing "AI Risk Evaluation Supplement version 5.0" for written comment. Submit to Scott Sobel (ssobel@naic.org) or Miguel Romero (mromero@naic.org) by close of business Sept 29.

Separately — not the same comment window, but related and worth knowing — NAIC staff have already drafted a compliance report converting the 2023 AI Model Bulletin (adopted in 24 states + DC) into **nine disclosure components**, including a board/senior-management attestation naming an executive responsible for the AI governance program. That draft structure is close to describing, in regulatory language, the exact thing Gate/Velaru already produces: a named accountable party, a documented control environment, and a verifiable attestation trail.

**This is not a research task, it's a writing task with a deadline.** Draft actual model comment language — plain, specific, grounded in what Gate/Velaru already do (stranger-verifiable receipts, fail-closed clearance, named accountability) — that Demond can review, edit, and submit before Sept 29. Do not wait for the roadmap below to be "done" first. This clock doesn't move.

**Working draft for Demond review:** [`docs/naic/NAIC_AI_RISK_EVAL_SUPPLEMENT_V5_COMMENT_DRAFT.md`](./naic/NAIC_AI_RISK_EVAL_SUPPLEMENT_V5_COMMENT_DRAFT.md)

**Primary-source specifics to ground the comment in, not generic AI-governance language:**
- Version 5.0 of the Supplement adds a formal **definition of "agentic AI" for the first time** — the exam framework is scoping in exactly the category Gate/Velaru operate in, right now, in the document up for comment.
- **Exhibit B adds a new question (labeled "3p" in NAIC's own changelog): how does a company oversee third-party AI models.** This is the literal regulatory question your insurance-UR-vendor targets will have to answer to their carrier customers — and the honest current answer for most of them is "we take the vendor's word for it."
- **Companies now self-specify their own materiality threshold and disclose it** — a real, named self-attestation gap, in the actual clause under comment, not doctrine-level abstraction.
- **Regulators now require a Model Inventory** (Exhibit A) — a concrete, exportable artifact Gate-covered systems could help auto-populate.
- Public discussion continues at a Webex meeting **Oct 8, 2026, 11am ET** — open to the public, not just written comment.
- Direct contacts for written comment: **Scott Sobel** (ssobel@naic.org, AI Policy Advisor) and **Miguel Romero** (mromero@naic.org, Director of Innovation, Cybersecurity and Technology).
- A comment citing the actual 3p language and the self-specified-materiality-threshold pattern by name — with a concrete answer to "how would a company actually prove third-party oversight rather than assert it" — is a fundamentally different artifact than a generic "AI governance matters" submission.

Also worth tracking, same regulatory motion, no hard deadline yet: NAIC's 12-state AI Systems Evaluation Tool pilot (CO, MD, LA, VA, CT, PA, WI, FL, RI, IA, VT, CA) is running through Sept 2026 inside live market conduct exams. Results feed into whether the tool becomes permanent — worth a comment or watching brief too, lower priority than the Sept 29 deadline.

---

## S-TIER — the four that build actual monopoly power, not just a better product

These aren't Cursor tasks Cursor can close alone. Code can build the prerequisites; the actual conversion needs Demond making real calls to real humans. Don't let any of these get marked "done" on the strength of code alone.

### 1. Insurance underwriting dependency (biggest one on the list)
Goal: get one carrier or E&O underwriter to say "using Gate reduces your AI liability premium." The market is already primed for this — 2026 underwriters have explicitly drawn the line at "governed AI with a documented control environment gets priced/covered, autonomous AI without one gets excluded" (industry trade press, 2026). Gate's fail-closed receipt is a ready-made answer to exactly that underwriting question.
- **Cursor's job:** build an underwriting-ready package — a one-page risk methodology doc, a sample receipt an underwriter could actually read, and a clean mapping of Gate's guarantees to the "governed vs. autonomous AI" line underwriters already use. Make it something Demond can put in front of an underwriter cold.
- **Demond's job:** actually get it in front of one underwriter or MGA. This doesn't close from a landing page.

### 2. Legal citation / precedent
Goal: get one Velaru receipt into a real legal proceeding — cited, admitted, or relied on by a judge, not just used by a client privately.
- **Live tailwind, cite this in outreach:** the May 2026 ruling making expert witnesses' AI prompt logs discoverable, and the accelerating AI-hallucination sanctions tracker (1,598 documented cases as of June 2026, ~8 new/day, record penalties, a canceled trial) — both are courts actively deciding that AI interaction trails are evidence. That's the exact reality Velaru's receipt format is built for, and it's dated this year, not doctrine.
- **Cursor's job:** build the outreach package for litigation-adjacent targets — the spoliation/preservation counsel lane you already have live on `/trust` (Hold Pack, Kill-Clock Monitor) is the right entry point. Package one real, live receipt as a demonstrative exhibit a lawyer could actually attach to a filing.
- **Demond's job:** get one case, even a small one, to actually use it.

### 3. Regulatory rule-shaping
Goal: get language into an actual rule, not just comment on one. The NAIC Sept 29 deadline above is the first move. Longer-horizon: state insurance departments drafting their own AI rules, individual state legislative sessions.
- **Cursor's job:** after the Sept 29 comment, build a repeatable template — Demond shouldn't have to write regulatory comment language from scratch every time a new docket opens. Track dockets on the existing regulatory-watchlist cadence, flag ones with open comment windows specifically (not just ones that exist).

### 4. Open standard ownership
Goal: publish the receipt/verification format itself as an open, freely implementable spec. Anyone can build a "Velaru-compatible" verifier; you own the reference implementation and the canonical verify endpoint. This is the one Cursor can execute on unsupervised, starting now.
- **Cursor's job:** draft a public spec document (separate from the product pages) describing the receipt format, signature scheme, and verification steps in implementation-neutral terms — the way a real standard reads, not marketing copy. Publish it somewhere durable (its own subdomain or path, versioned). Cross-link it from `/verify` and `/trust` as "the open spec this implements," not folded into product copy. This becomes the artifact you can eventually cite in the NAIC comment and any future regulatory language — "here is the open format, here is our implementation of it."

### 5. Stablecoin reserve verification (GENIUS Act) — biggest scale, longest lead time
~$303B stablecoin market (Sept 2026) under a federal law barely a year old (GENIUS Act, signed July 2025, full effect Jan 2027). Issuers must reconcile on-chain supply with off-chain reserves monthly via CPA attestation — the OCC's own March 2026 proposed rule explicitly asks whether examination should run under "reasonable assurance," AICPA AT-C standards, or "some alternative framework." That's a federal regulator asking, in an open docket, "how should stranger-verification of reserves actually work" — with no real-time cryptographic answer on the table yet. This restates Nisaba's core thesis almost word for word, at nation-state-reserve scale (market cap already exceeds the FX reserves of 95 countries).
- **Reality check:** heaviest lift on this list. Buyer is a stablecoin issuer, a bank custodian, or a federal regulator — not a cold-emailable startup. Multi-quarter relationship-building, not a Bind Room deposit email. Track it, don't force it into this quarter's plan.

---

## ⏰ NEAR-TERM — live right now, buyer is assembling itself in public

### 6. Agentic payment clearance (x402 / AP2 / ACP / MPP)
As of mid-2026: x402 alone has cleared 165M+ transactions across 69,000 active agents; the x402 Foundation launched July 2026 under the Linux Foundation with Visa, Mastercard, Google, Stripe, Amex, AWS, and Circle as founding members. Every independent source describing this space converges on the same gap in different words: the rails for moving money autonomously exist and work; the layer deciding *whether this specific agent should be allowed to make this specific irreversible payment* does not. One source, describing the "metering gap," wrote almost exactly Gate's thesis without knowing it: "every automated action should leave a row saying what was done, by which process, on whose authority."
- **Why this is the closest match found to date:** Gate's own infrastructure already has a live (if unconfigured) x402 wire endpoint. This isn't a new vertical to build toward — it's the one closest to already-built.
- **Cursor's job:** get the x402 integration actually configured and working end to end (closes an existing scorecard gap — `x402.configured: false` on health — and turns this from theoretical to demonstrable in the same motion). Build one concrete demo: an agent attempts an autonomous payment, Gate evaluates it, a receipt is issued — framed explicitly around the x402/AP2 ecosystem language, not general Gate copy.
- **Demond's job:** this is a live, public, fast-moving standards fight (Visa, Mastercard, Google, Stripe, Coinbase all jockeying) — the x402 Foundation itself is a real door to walk through, not just a market to sell into.

---

## LONG-TERM — real, huge, multi-year builds

### 7. Post-quantum cryptography vendor assurance gap
Executive Order 14412 (June 22, 2026) sets federal deadlines: key-establishment algorithms migrated by Dec 31, 2030, digital signatures by Dec 31, 2031. Treasury has stood up its first-ever task force specifically for the third-party/vendor version of this problem, because — in the finding's own words — "some providers can explain their architecture but cannot give buyers a usable roadmap of protocols, certificates, or migration dates... others can state a direction but cannot tie it to a NIST-compliant baseline in a way a risk team can test." The Bank of England's July 2026 Financial Stability Report says the same thing from the UK side: firms need real assurance about counterparties' PQC posture, and no standard mechanism exists to get it. This is the issuer-pays self-attestation gap at the scale of the entire global financial system's cryptographic foundation — and a brand-new federal task force exists whose explicit job is solving exactly this.
- **Internal to-do, not just a market opportunity — flag this to Cursor directly:** Velaru's own signing scheme is Ed25519, an elliptic-curve algorithm in the exact category being deprecated by 2030 and disallowed by 2035. Add "migrate signing to ML-DSA (FIPS 204) ahead of the federal deadlines" to the actual engineering roadmap, not just the opportunity list. Being visibly ahead of your own future vulnerability here is the difference between selling quantum-readiness credibly in a few years and having to explain why you weren't.
- **Reality check:** multi-year build, buyer is banks/custodians/regulators, no near-term revenue. Track it now so you're not starting from zero when the market catches up to the 2030 deadline.

---

## High-leverage builds (not S-tier, but real progress toward Gate 1)

### A. Personalized live demo
Prospect pastes their own scenario (a claims denial, a tenant rejection, an account freeze) instead of clicking a canned demo. Gate runs a real fail-closed check against their shape and returns a real Velaru receipt with their own scenario in it. Highest-leverage build on this list short of the S-tier items — turns "trust us" into "I just watched it happen to my exact case."

### B. Pre-built adapters for named targets
Working connectors for the real target lists already identified: Cohere Health/Rialtic/Anterior (insurance UR), Entrata/AppFolio-class (tenant screening), Alloy/Sardine/Unit21 (account freeze). Ingest their actual decision-object shape, return a Gate clearance + receipt. Hand a prospect something built, not something described.

### C. Public adversarial red-team, with a real bounty attached
Build the adversarial test suite (replay attacks, malformed payloads, idempotency race conditions) and publish results as a "we tried to break our own guarantee" page. Then put real money behind a public bounty for anyone else who breaks it. The bounty is the trust-accelerant — a self-written red-team report is good, a paid public dare is better and cheap to run.

### D. Client SDKs
Python/Node packages wrapping the Gate API so integration is an afternoon, not a week reading OpenAPI docs. Friction at the exact moment someone tries to say yes kills more first sales than bad copy does.

### E. Public incident registry (AI harm with no audit trail)
Using only public records (lawsuits, regulatory actions, news), track documented cases where an AI system did something irreversible with no evidence trail after the fact. Publish as a public-interest resource. Compounds for free the longer it runs, and every entry is an implicit case for Gate without ever pitching anyone. Zero customer involvement needed to start — good Cursor-only task to run in parallel with everything else.

### F. Live public counter
Total writes evaluated, total halted, total cleared — real numbers, verifiable through the receipt chain itself, updating live. Empty now, but build the plumbing early. Once real volume exists, the number becomes the pitch.

### G. Bulletproof the money path end to end
Bind → charge → receipt → standing-write upsell, tested and idempotent start to finish. Unglamorous, but a bug at the moment someone tries to actually pay you is the worst possible time to find one.

---

## Historical pattern — what actually makes verification infrastructure permanent

This section isn't a task list. It's the strategic frame everything else in this file sits inside. Read before deciding what to prioritize.

### The template: Underwriters Laboratories (1894–present)
UL didn't start as a vendor selling to the insurance industry — it started as the "Underwriters' Electrical Bureau," a division *of* the fire insurance industry itself, because insurers needed independent, testable proof that a new, scary technology (electricity) wouldn't cause an irreversible loss (fire) before they'd underwrite it. That's the exact insurance-underwriting-dependency play (S-tier #1), already run successfully, in public record, a century ago, for a different technology going through its own anxiety cycle. Two structural lessons worth taking seriously:
1. **UL was co-founded from inside the industry it now stands apart from, not built outside and sold in.** Worth asking whether a version of Nisaba gets built *with* an MGA or carrier as a founding partner, rather than pitched to one cold after the product already exists. Historically, that's the version that became permanent.
2. **The 1906 San Francisco earthquake — a catastrophic, undeniable, public failure — is what expanded UL from a niche tester into the body that wrote actual building codes.** Crisis, not sales cycles, converted UL from vendor to infrastructure. This is the same logic behind the earlier "public incident registry" idea (item E): it's not just PR, it's positioning Nisaba to already be built and credible the moment an AI equivalent of the 1906 earthquake happens — because it will, and whoever is already the reference point when it does gets the UL outcome.

### The modern instance of the same pattern, happening right now, adjacent to you
The x402 Foundation (Linux Foundation-governed, 40 major companies as founding members, launched July 2026) is UL's playbook running again in a different category: vendor-neutral, co-founded by the industry it serves, not sold to it after the fact by one company. This validates the open-standard S-tier play (#4) directly — worth studying x402 Foundation's actual governance structure as a template for how Velaru's spec should be released, not just tracking it as an adjacent market.

### The caution worth taking as seriously as the opportunity
Credit rating agencies (Moody's, S&P) survived 2008 despite being catastrophically wrong about mortgage-backed securities, because the SEC's 1975 NRSRO designation had already written "must use an NRSRO rating" into federal regulation. Regulatory lock-in is what makes an institution nearly impossible to dislodge — including when it deserves to be dislodged. That's the dark mirror of everything in the S-tier section: the same mechanism that makes Nisaba permanent if it works also makes it unaccountable if something in it is wrong later. **Build real, independent, adversarial audit of Nisaba's own guarantees now, while it's cheap and voluntary** (this is what item C — the public bounty — is actually for, reframed: it's not just a trust-accelerant, it's insurance against becoming a Moody's-shaped liability once you're structurally hard to route around).

### One structural decision this suggests
UL is a not-for-profit; the commercial value it created for manufacturers who passed testing was entirely separate from UL's own revenue model. That split is probably correct for Nisaba too — worth deliberately keeping the open-spec/reference-verifier layer (item #4) structured differently (foundation, nonprofit, multi-stakeholder governance) from the commercial Gate product, rather than trying to make one entity be both "the neutral standard" and "the company profiting from it." Credibility as a standard and profitability as a vendor pull in different directions once you're big enough for anyone to notice the difference.

---

## Architecture — what to make customizable, and how

This section governs *how* future features get built, not what to build next. Applies to Gate/Velaru/Mishara alike.

### Core pattern: policy-as-code, not hardcoded branches
Clearance rules should be declarative, versioned policy files (Rego via Open Policy Agent, or a simpler YAML-based alternative like Cerbos) evaluated as data against a service — not `if` statements accumulating in `app.py`. This is the same single-source-of-truth principle that fixed the pricing drift, applied one layer down to the actual clearance logic. AWS shipped exactly this pattern for AI agents specifically — Cedar inside Bedrock AgentCore Policy (March 2026) intercepts every agent-tool call at the gateway boundary against a policy set — which validates the approach from a completely different direction and is worth studying as a reference architecture.

**Named failure mode to design against:** OWASP's Top 10 for Agentic Applications 2026 names "Least Agency" — a policy checkpoint that's just another AI call can be fooled the same way the agent itself can. The policy layer has to be genuinely independent evaluation, not a second opinion from the same kind of reasoning.

### What to make customizable
1. **Clearance rules per customer/vertical** — policy file swap, never a new code branch, per industry (insurance UR, tenant screening, account freeze all need different thresholds).
2. **The sink/irreversibility taxonomy** — let a customer register their own sink type against the existing scale in `sinks.json`, instead of hardcoding every new vertical yourselves.
3. **Signing backend, made pluggable now** — this is the PQC migration insurance policy. If Ed25519 sits behind a swappable interface today, migrating to ML-DSA (FIPS 204) ahead of the 2030/2031 federal deadlines (see the post-quantum crypto finding above) is a config change, not a rewrite. Build the abstraction now while it's cheap.
4. **Webhook/callback shape per integration** — named targets (Cohere Health, Entrata, Alloy) will each have different decision-object schemas; a configurable mapping layer beats a bespoke adapter per customer.
5. **Idempotency window and replay-detection sensitivity**, tunable per customer risk appetite.
6. **NAIC-exhibit-shaped exports** — grounded directly in the actual v5.0 Supplement text: a receipt export that answers Exhibit B's new "3p" third-party-model-oversight question in the regulator's own structure, a stranger-verifiable timestamp on a customer's self-set materiality threshold (since the Supplement now requires companies to disclose their own threshold with no independent check on it), a formal "agentic AI" tag matching the Supplement's new definition, and a machine-readable Model Inventory export matching Exhibit A. This turns "we're a general verification API" into "we speak the compliance document you're filling out right now" — a materially different pitch to an insurance buyer.

### The tension to design around explicitly: customizable vs. fail-closed
Every customization point is a place a misconfigured policy could accidentally fail open. Non-negotiable requirements for whatever gets built:
- **Staged rollout for policy changes, separate from code deploys.** A bad policy update is a different failure class than a bad code deploy — it can silently start failing open or wrongly denying without any code changing. Run new policies in shadow mode alongside the old one, log disagreements, before cutting over.
- **Policy files need their own test suite**, distinct from application code tests — this is the layer most likely to drift since it's the one meant to be edited most often.
- **Default-deny has to survive a missing or malformed policy, not just one that evaluates to false.** Test explicitly: corrupted file, wrong schema, deploy race condition — "no valid policy found" must resolve to DENY, never "skip the check."
- **Evaluation latency needs a hard budget.** Policy engines slow down as rule complexity grows. Decide now: clearance decisions execute under a fixed time budget (e.g., 200ms) or fail closed and flag for review — a slow policy evaluation should never become quiet unavailability for a paying customer mid-transaction.

---

## Explicit non-goals — do not spend cycles here right now

- A sixth brand
- More `.well-known` manifests nobody calls
- More doctrine pages
- More audience-segmented landing pages beyond what already exists
- Anything that produces a diff without moving a prospect closer to Gate 1

If a task doesn't fit under the ⏰ deadline, one of the S-tier items, or the high-leverage builds above, it's museum work — flag it as such rather than building it quietly.
