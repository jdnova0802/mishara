# PASTE — AI Kill Switch Act × Gate (policy positioning, not a SKU)

**26 Sep 2026.** Real bill. Real unresolved debate. No glaze.

---

## The live question

**H.R. 9917 — AI Kill Switch Act** (119th Congress).  
Introduced **23 Jul 2026** by Reps. **Ted Lieu** (D-CA) and **Nathaniel Moran** (R-TX).  
Referred to House Homeland Security; **24 Jul 2026** → Subcommittee on Cybersecurity and Infrastructure Protection.  
**Status: Introduced — not law.**

Primary sources:
- https://www.congress.gov/bill/119th-congress/house-bill/9917
- Text (GPO): https://www.govinfo.gov/content/pkg/BILLS-119hr9917ih/html/BILLS-119hr9917ih.htm
- Sponsor release: https://lieu.house.gov/media-center/press-releases/reps-lieu-and-moran-introduce-bill-require-kill-switch-ai-systems-can

The unresolved public question is not “should AI be powerful.” It is:

> When an AI system (especially agentic) can cause catastrophic harm,  
> who must maintain a **technical capability to throttle / suspend / shut down**,  
> who may **order** that capability used,  
> and what **proof** exists that the halt actually happened —  
> without the halt itself becoming a captured, forgeable, or silent maybe?

That is the same metaphysics Gate already occupies for irreversible writes — applied to a different mouth: **kill / NEVER as a first-class, scoped, publication-hard act**.

---

## What the bill actually requires (cite, don’t paraphrase into fiction)

From introduced text, new HSA § 2220F:

| Requirement | Bill hook |
|-------------|-----------|
| Covered entities maintain technical capability to **stop inference**, **terminate user access**, **suspend** account/use-pattern risk, and **shut down** covered technology | (b)(1)(A) |
| Graduated deployment-corrections: throttle inference/access/compute → disable capability → suspend → shut down → fall back to backup/earlier version | (b)(2)(A) |
| **Covered incident** report to DHS within **15 days** | (b)(1)(B) |
| DHS (w/ Commerce + DNI consult) may **order** proportionate action; entity must preserve **model weights + telemetry**, notify users, confirm | (c) |
| Audit/forensic verify of compliance after confirmation | (c)(3) |
| Civil penalties up to **$2M/day** general; **$20M/day** for emergency-order violations | (d)(2) |

Coverage thresholds (as introduced — rulemaking can update annually):
- **Covered technology:** AI system developed with compute cost **> $100,000,000** (US cloud market price, Secretary-determined)
- **Covered entity:** operates/incorporates covered tech, makes it available to third parties (API/hosted), and **≥ $500,000,000** gross revenue from that tech (with affiliates) in prior calendar year
- Personal/academic/non-commercial exemption

**Covered incident** includes: sabotage of shutdown instruction; unintended conduct causing ≥10 deaths or ≥$100M damage; concealment from monitoring/shutdown; **loss-of-control** (incl. subverting a shutdown mechanism).

Gate is **not** claiming to be a covered entity under those revenue/compute thresholds. Positioning is about the **shape of the missing infrastructure** the debate keeps assuming exists.

---

## The gap the debate has not closed

Everyone arguing the Act assumes a kill switch is:

1. **Technically real** (not a dashboard button that the model can route around)
2. **Provably used** when ordered (not “we think we halted”)
3. **Not silently rewriteable** after the fact (forensic record survives the operator who wants to look clean)
4. **Scoped** (not a Moody’s-style global “this AI is bad” opinion product)

The bill gestures at (3) via weights/telemetry preservation and DHS audit. It does **not** specify stranger-verifiable publication of the halt artifact, nor a may-scarce spend map for “permission to keep inferencing,” nor an apophatic primary export (signed NEVER / SHUTDOWN with claim_scope).

That is Gate’s lane — **without selling may**, without becoming the oracle of which models are safe.

---

## Precise Gate mapping (existing mouths → Act language)

| Act concept | Gate already-shipped analog | Honest limit |
|-------------|----------------------------|--------------|
| Technical capability to shut down / suspend | **NEVER** mouth + spend exclusion; epoch **HALT** until CHARGE; fail-closed 503 on upstream death | Gate mouths halt *irreversible writes / spend*, not GPU inference at a frontier lab |
| Graduated corrections (throttle → suspend → shutdown) | HOLD / NO_GO / NEVER / license fuse / command radiation | Not a compute governor; do not claim cluster kill |
| Incident reporting + forensic preserve | Evidence log + Merkle head + (now) OTS Bitcoin anchor; claim_scope on negatives | Not a DHS filing product |
| Order must be confirmed + audited | Signed receipt + inclusion proof + witness capacity + OTS | Confirmation is cryptographic/publication, not statutory DHS confirm |
| Subversion of shutdown = covered incident | Exclusion / spend-map: prove leaf absent or present; cannot double-spend may | Different threat model than model-weight exfiltration |
| “Will not sell may” | Commercial vow + non-oracle metaphysics | Must stay married to code |

**One sentence for the debate:**  
The Kill Switch Act needs a **publication-hard, scope-bound halt artifact** — not only a capability affidavit. Gate’s NEVER + claim_scope + evidence-head (+ OTS) is that artifact class for irreversible agent actions; frontier labs still need the inference-plane twin.

---

## What to say publicly (and what not to)

**Say:**
- The Act correctly treats shutdown as infrastructure, not vibes.
- The hard problem after “maintain capability” is **proving the halt, with scope, under rewrite pressure**.
- Gate already ships apophatic halt words for payment/write rails agents use; Bitcoin-anchored evidence-head makes those words expensive to rewrite.
- We will not sell “this model is safe” grades.

**Do not say:**
- “Gate is the AI Kill Switch Act compliance product.”
- “We shut down frontier models.”
- “OTS means the halt was correct about the world.” (publication time ≠ worldly fact)
- Anything that invents co-sponsors, markups, or hearings that have not happened.

---

## Optional next moves (still not SKUs)

1. **One-pager to Lieu/Moran offices or Homeland Security staff** — “halt artifact” framing; cite § 2220F(c)(3) audit gap; offer NEVER+evidence-head as reference architecture for *agent-tooling* kill switches (payment, wire, bind), not model weights.
2. **Bind the OTS evidence-head** (tonight’s build) so any NEVER/HALT packet can point at a Bitcoin-anchored tree — strengthens the forensic half of the Act’s intuition.
3. **Stay out of covered-entity LARPing** until revenue/compute reality matches the statute.

---

## One-liner

**H.R. 9917 asks who can kill a dangerous AI system. The unfinished half is how the kill becomes a stranger-verifiable, scope-bound, non-oracle artifact — the same may-gap Gate closes for irreversible writes. Position there; do not sell a fake compliance SKU.**
