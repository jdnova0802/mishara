# Shock tier ship — paste this

**Date:** 2026-09-15  
**Branch:** `cursor/civilizational-research-dual-track-0d63` · PR #62  
**Law:** logos-before-actus. Fail-closed. Stranger-verifiable receipt. `their_production: false` always.  
**Confirm green:**

```bash
python3 -m gate.sims.prove_all
```

---

## PASTE — what just shipped

```
Shock tier Z1–Z10 is lab-proved and stranger-fetchable on the same Gate spine
as S1/S3 (shared logos.py + verify_http.py). Not remaps of agent-pay — prestige
priesthood mouths. Lab fixtures only (real_*: false).

Run:
  python3 -m gate.sims.prove_all

=== Z1 ISDA DC Publish — headline ≠ Credit Event ===
File: gate/sims/isda_dc_publish.py
DENY: headline_only | no_resolution | draft_only | resolution_mismatch
ALLOW: dc_resolution_live (LIVE Resolution + auction_terms_hash)
Never scrape/news → ALLOW.

=== Z2 CLS Settle — matched ≠ settled PvP ===
File: gate/sims/cls_settle.py
DENY: unmatched | risk_test_failed | pay_in_shortage | member_suspended
ALLOW: settled_pvp (final + irrevocable fixture)

=== Z3 IANA Root Change — intent ≠ root-zone write ===
File: gate/sims/iana_root_change.py
DENY: tech_check_failed | maintainer_nack | unknown_tld
ALLOW: root_zone_updated (PTI/Verisign-shaped)

=== Z4 Lloyd's Bind Stamp — paperwork ≠ registered bind ===
File: gate/sims/lloyds_bind_stamp.py
DENY: no_baa | baa_not_registered | syndicate_not_on_baa | class_out_of_scope | over_authority_limit
ALLOW: bound_under_authority

=== Z5 ITU BIU/MIFR — paper filing ≠ recorded assignment ===
File: gate/sims/itu_biu_mifr.py
DENY: api_only_paper | coordination_incomplete | biu_period_insufficient | biu_evidence_missing
ALLOW: mifr_recorded (BIU ≥90 + evidence)

=== Z6 ISA Exploit — exploration ≠ exploitation ===
File: gate/sims/isa_exploit.py
DENY: mining_code_not_live (while negotiating) | no_exploration_contract | plan_of_work_incomplete
ALLOW: exploitation_contract_issued (only when Code LIVE)

=== Z7 KP Export — parcel ≠ certified export ===
File: gate/sims/kp_export.py
DENY: no_certificate | seal_tampered | shipment_mismatch | certificate_revoked | non_participant
ALLOW: kp_export_authenticated

=== Z8 Freeport Ingress — CoA/ALR ≠ licit admit ===
File: gate/sims/freeport_ingress.py
DENY: coa_or_alr_insufficient | chain_incomplete | antiquity_permits_missing | alr_hit | beneficiary_unknown
ALLOW: freeport_admitted

=== Z9 Peerage Roll — claimed title ≠ Crown recognition ===
File: gate/sims/peerage_roll.py
DENY: self_style_insufficient | evidence_insufficient | senior_line_unproven | petition_missing
ALLOW: entered_on_roll

=== Z10 College of Arms — generative crest ≠ letters patent ===
File: gate/sims/college_arms.py
DENY: generative_crest_refused | arms_not_distinct | ineligible_petitioner | kings_of_arms_refused
ALLOW: letters_patent_sealed

=== Stranger verify (all of the above) ===
gate/sims/verify_http.py — localhost GET by receipt_url:
  /v1/isda-dc/  /v1/cls-settle/  /v1/iana-root/  /v1/lloyds-bind/
  /v1/itu-biu/  /v1/isa-exploit/  /v1/kp-export/  /v1/freeport/
  /v1/peerage-roll/  /v1/college-arms/

=== Also already green (prior tonight) ===
P0 welds: S1 bank-send + S3 EFSP transmit + stranger HTTP
Tier-2: S8↔S9 wire, S6 watch feed, S7 edgar_block_no_seal
Intelligences: S9/S10/S16/S13 (Scenario X: S9 clear + S10 DENY alone)
Shared: logos.py mandate→grant→digest

=== Do NOT ===
- Treat any Z* as production DC/CLS/IANA/Lloyd's/ITU/ISA/KP/freeport/Crown
- Build recognition dashboards / crest generators / genealogy AI
- Start museum intelligences or S2/S4/S5
- Conflate binding publish with news scrape
- **Start Z11+** — shock tier sealed. Z9/Z10 = generality demo, not commercial queue.
  Empty > filler. Next = real weld/outbound/pitch, not more fixture mouths.

Hunt + crowding: gate/SHOCK_TIER_HUNT_2026-09-15.md
Prove sequence: gate/sims/PROVE_SEQUENCE.md
Stopping rule: SHOCK_TIER_HUNT § Stopping rule (pinned after Z10)
```

---

## One-liner

> Shock Z1–Z10 shipped — DENY-first, stranger-verifiable. Z9/Z10 prove the pattern isn't finance-shaped; further Z* is museum. Next = weld/outbound, not collection. `python3 -m gate.sims.prove_all`
