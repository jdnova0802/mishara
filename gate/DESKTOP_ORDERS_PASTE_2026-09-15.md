# Desktop orders — paste this into Cursor

**Date:** 2026-09-15  
**Branch/context:** `gate/` on mishara — cloud proved lab spines; you extend toward weld shape.  
**Law:** logos-before-actus. Fail-closed. Stranger-verifiable receipt on every DENY/ALLOW. `their_production: false` always. No dashboard theater. No real money, court, EDGAR, county, KYC, grief UX, or biometric production.

**Next intelligences (S10/S16/S13 + museum + Claude paste):** `INTELLIGENCE_PASS_2026-09-15.md`

---

## PASTE — full desktop run order

```
You are extending Nisaba Gate lab mouths already proved in-repo under gate/sims/.
Do NOT re-discover or rebuild the cores. Extend toward weld shape. Prove DENY first.

Cloud already green (run to confirm):
  python3 -m gate.sims.prove_all
  # includes prove_mouth_watch + prove_actus_s9_wire + prove_lab_invariant (required)

Shared spine every mouth:
  CONSEQUENTIAL_ACTION proposed
    → require LIVE logos/mandate/seal bound to digest
    → missing / stale / mismatch / over-scope / uncertainty ⇒ DENY + receipt_url
    → valid ⇒ ALLOW + receipt_url linking logos ↔ digest ↔ result
    → their_production: false always (stamp_lab_flag + assert_all_receipts_lab)

Receipt must be fetchable by a stranger (HTTP verify route or signed JSON) without trusting the actor UI.

HARD INVARIANT (CommitGuard-class):
  THEIR_PRODUCTION is identically False on every module and every receipt.
  Mutating it to True must raise at stamp time (prove_lab_invariant catches this).
  Treat missing/True their_production as a ship-blocker.

RECEIPT CLASSES (bank-branchable — confirmed before S1 extend done):
  clearance   → mouth DENY/ALLOW ("this actus authorized?")
  threat      → S9-only object (canary | session_integrity | trajectory)
  watch_clear → S9 sense-layer clear
  On S9 block: S1 returns clearance DENY with watch_block=true + threat_receipt_id
  linking to a SEPARATE threat receipt. Never overload reason strings for this.

S9 TRIP EFFECT (pinned — not a SOC):
  deny_this_actus: true | session_lockout: false | alert_fanout: false | quarantine: false
  Broader only if a later actus re-queries Watch.

STANDARD PROVE TEMPLATE (every future mouth — not optional bolt-on):
  python3 -m gate.sims.prove_<mouth>
  python3 -m gate.sims.prove_mouth_watch      # REQUIRED
  python3 -m gate.sims.prove_lab_invariant    # REQUIRED
  Or: python3 -m gate.sims.prove_all
  See gate/sims/PROVE_SEQUENCE.md

S1↔S9 WIRE (separate scenarios — both green before S1 extend called done):
  python3 -m gate.sims.prove_actus_s9_wire
  A) canary trip alone (clean session) → threat_class=canary; next actus still ALLOW
  B) hostile session alone (no canary) → threat_class=session_integrity
  Do not merge A+B into one checkmark.

=== ORDER 1 — P0 — S1 Actus Fence (extend) ===
Files: gate/sims/actus_fence.py, prove_actus_fence.py
Gate: prove_actus_s9_wire must already be green (A and B separate).
Do:
- Local HTTP stranger-verify for receipts (GET by receipt_id) — clearance AND linked threat
- FedNow/RTP-shaped bank-send DENY fixtures (not real rails)
- Keep non-pay consequential actus (prod_mutate etc.)
- README honesty: not Fidacy/IntentFence or Visa TAP head-on
Prove: bank-send-shaped DENY; stranger fetch clearance + threat; prove_actus_s9_wire still OK.

=== ORDER 2 — P0 — S3 Performative Seal (extend) ===
Files: gate/sims/performative_seal.py, prove_performative_seal.py
Do:
- EFSP-shaped block-transmit: no LIVE seal ⇒ cannot transmit/file
- Plant fake cite ⇒ seal DENY ⇒ file DENY
- Stranger seal/file receipt via HTTP verify
Prove: fake cite cannot file; no-seal cannot transmit; prior proves OK.

Do NOT start S2/S4/S5 until Orders 1–2 are green.

=== ORDER 3 — P0′ — S9 Mouth Watch (defensive intel) ===
Files: gate/sims/mouth_watch.py, prove_mouth_watch.py, prove_actus_s9_wire.py
Pastes: gate/S_TIER_PLUS_THREE_2026-09-15.md (S9)
Why: lock without watchman = blind. Industry split = recognize (Visa) / gate (you) / sense (this).
Do:
- Keep canary + trajectory + session score threat receipts (already proved)
- Wire already in S1 execute (hostile session OR canary ⇒ clearance DENY linking threat)
- Wire session score into S8 attest path (synthetic/unknown ⇒ REFUSE with threat receipt linked)
- HTTP stranger-verify for threat receipts (distinct URL/object from clearance)
- README: not a SOC; trip = deny-this-actus only; not Visa TAP
Prove: prove_mouth_watch; prove_actus_s9_wire (A canary ≠ B hostile); prove_lab_invariant green.

=== ORDER 4 — S7 EDGAR Disclose Seal (weld-shape) ===
Files: gate/sims/edgar_disclose_seal.py, prove_edgar_disclose_seal.py
Do: submit mouth weld-shape; HTTP stranger receipt; still lab — no real EDGAR.
Prove: hallucinated quantity DENY; no-seal submit DENY; grounded ALLOW + receipt.

=== ORDER 5 — S6 Deed Record Gate (weld-shape) ===
Files: gate/sims/deed_record_gate.py, prove_deed_record_gate.py
Do: record-accept mouth; optional S9 session feed; still lab — no real county.
Prove: inject_suspect DENY; owner_lock without unlock DENY; LIVE ALLOW + receipt.
Not title insurance.

=== ORDER 6 — S8 RON Attest Refuse (weld-shape) ===
Files: gate/sims/ron_attest_refuse.py, prove_ron_attest_refuse.py
Do: refuse mouth + S9 session feed already from Order 3; still lab — no real commission.
Prove: synthetic_suspect REFUSE; unknown REFUSE; live ALLOW + receipt.
Not a notary marketplace.

=== DEFER (do not build) ===
- S2 Presence Threshold — no liveness R&D
- S4 Afterlife Mandate — no grief UX
- S5 Body Archive Gate — no biometric matcher

=== HARD TRAPS ===
- Do not beat Visa at checkout. Adjacent: non-pay actus + bank push + stranger receipt.
- Do not build title insurance / Workiva / notary marketplace / SOC dashboard.
- Do not invent greenfield grants theater where Fidacy/Visa already own recognition.
- Mouth Watch is threat receipts into mouths — not a monitoring product UI.

=== OUTBOUND (human, not more sim scroll) ===
After P0 green: EFSP/AmLaw-shaped outbound for S3; bank agent-pay adjacent for S1;
title/RON detection partners for S9↔S8/S6. Lab fixtures only unless a real weld partner exists.

Detailed paste blocks: gate/DESKTOP_PASTES_S_TIER_2026-09-15.md
S6–S9 paste blocks: gate/S_TIER_PLUS_THREE_2026-09-15.md
Edge pass / crowding: gate/EDGE_PASS_2026-09-15.md
```

---

## One-liner for chat

> Extend gate/sims P0: S1 HTTP verify + bank-send DENY, S3 EFSP block-transmit, then S9 Mouth Watch wired into S1/S8. Then weld-shape S7→S6→S8. Defer S2/S4/S5. Fail-closed + stranger receipts. `their_production: false`. Watchman + lock, not dashboard.
