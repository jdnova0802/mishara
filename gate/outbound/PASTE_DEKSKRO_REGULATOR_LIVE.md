# PASTE — Tell dekskro: make regulator verify LIVE

**26 Sep 2026.** Ops only. No new SKU. No new secrets. Track 1 drafts stay human-sent.

---

## Message (copy below the line)

---

Make live — regulator verify page

**PR:** https://github.com/jdnova0802/mishara/pull/145  
**What:** Public `/regulator` for policy staff (not Bind Room / diligence / pricing). Maps NAIC four asks + HMT Q15 to live Issuing / claim_scope / evidence-head. Stranger can mint a NO_GO receipt and check signature + Merkle inclusion + OTS status with no login.

### Deploy

1. Mark PR **#145** ready for review (undraft) if needed, then **merge into `main`**.
2. Confirm Render **gate-api** (`srv-dai3n0u1egvs73dbd94g`) auto-deploys from `main`. If not → Manual Deploy → latest commit.
3. **No new env vars.** Receipt signing keys already on prod. OTS well-known is **not** this PR (#137 separate).

### Verify (after deploy green)

```bash
curl -sS https://gate.velaru.xyz/.well-known/regulator.json \
  | python3 -c "import sys,json; m=json.load(sys.stdin); print(m['spec'], len(m['naic_asks']), m['hmt_q15']['submit_email']); print(m['page']); print(m['live']['ots']['status'])"
```

Expect:
- `gate-regulator-v1 4 Modernisingpaymentservices@hmtreasury.gov.uk`
- page ends with `/regulator`
- OTS status honest (`not_found` / `not_in_tree` until #137) — not dressed as confirmed

```bash
curl -sS -o /dev/null -w '%{http_code}\n' https://gate.velaru.xyz/regulator
```

Expect: `200`

```bash
# Mint one stranger-checkable sample (money_real:false)
curl -sS -X POST https://gate.velaru.xyz/demo/regulator/mint \
  -H 'content-type: application/json' -d '{}' \
  | python3 -c "import sys,json; b=json.load(sys.stdin); print(b['event_id'], b['money_real'], b['decision'], b['claim_scope']['boundary']); open('/tmp/reg_eid.txt','w').write(b['event_id'])"
```

Expect: `<uuid> False NO_GO gate_regulator_sample`

```bash
EID=$(cat /tmp/reg_eid.txt)
curl -sS "https://gate.velaru.xyz/v1/regulator/verify?event_id=$EID" \
  | python3 -c "import sys,json; b=json.load(sys.stdin); print(b['ok'], b['checks'])"
curl -sS "https://gate.velaru.xyz/.well-known/receipt/$EID/proof.json" \
  | python3 -c "import sys,json; b=json.load(sys.stdin); print(b['spec'], b['inclusion']['tree_size'])"
```

Expect: `True` with `receipt_signature` + `inclusion_proof` true; proof `gate-evidence-proof-v1` and `tree_size >= 1`.

Open in browser: `https://gate.velaru.xyz/regulator?event_id=$EID` → word should land on **HOLDS**.

**Done when:** mint + verify return `ok: true` and `/regulator` loads without login.

### Honesty

- Sample is **money_real:false** / `demo:true` — clearance artifact only.
- OTS well-known may still be pending (#137) — page must label pending, not confirmed.
- Does **not** send NAIC / HMT / GAAIA filings — drafts only; Demond submits.
- Does **not** invent a Sept 14 filed letter.

### Not this deploy

- **#137** OTS Bitcoin anchor — separate; needs `GATE_OTS_DIR` + stamp cron
- Track 1 outbound emails / Oct 8 Webex — human, not Render

---

## File refs

- Code: `gate/regulator.py`, `gate/templates/regulator.html`, routes in `gate/app.py`
- Detail: `gate/outbound/PASTE_REGULATOR_ADJACENCY.md`
- Drafts: `docs/naic/NAIC_OCT8_2026_VERBAL_COMMENT.md`, `docs/hmt/HMT_Q15_AGENTIC_PAYMENTS_RESPONSE.md`
