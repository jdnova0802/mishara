# CURSOR HANDOFF — Nov 1 single pass (delivered)

## 1. x402 integration
**Shipped**
- Dogfood mouth: `GET /x402-mouth`, `GET /.well-known/x402-mouth.json`, `POST /demo/x402/agent`
- Module: `gate/x402_agent_demo.py` — agent attempt → prefinality evaluate → receipt, framed in x402/AP2 language
- `/health` → `x402.gaps`, `x402.dogfood`, `x402.mouth`
- Ops paste: `gate/outbound/PASTE_X402_FOUNDATION_DEMO.md`
- Full notes: `docs/handoff/X402_FOUNDATION_DEMO.md`
- Tests: dogfood GO + force_breach NO_GO + health gaps

**Still needs human ops (cannot invent from agent)**
Set on public host:
- `GATE_X402_PAYTO` = real Base USDC receiver → flips `configured: true`
- `CDP_API_KEY_ID` + `CDP_API_KEY_SECRET` → flips `facilitator_ready: true`

Dogfood demo is the Foundation **door asset** today. Live USDC settle is env, not code.

## 2. RealPage / clean-provenance
Scoping only → `docs/handoff/CLEAN_PROVENANCE_REALPAGE.md`  
Verdict: **new receipt type / separate mouth** on same signing architecture (`/v1/provenance/evaluate`), not a fork of prefinality rail. Same DENY family, different claim (CLEAN/TAINTED/UNKNOWN).

## 3. UCC Article 12
Scoping only → `docs/handoff/UCC_ARTICLE_12_CONTROL.md`  
- §12-105 control fields pulled  
- §12-104 QP / take-free pulled  
- **No Art 12 QP case law found**; Celsius/BlockFi are pre-Art-12 analogies  
- Verdict: **new receipt type** `gate-control-event-v1` on existing architecture; do not conflate with `exclusive.py`

## 4. Field-study track
Honest scores → `docs/handoff/FIELD_STUDY_TRACK.md`  
- FQAH: quarterly watch, no build  
- Speech-act: academic sources exist; keep thin shelf, **not a SKU**  
- Others tabled: young/old, trigger, buyer — none forced into commercial
