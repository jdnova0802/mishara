"""Regulator-facing adjacency surface — not Bind Room, not diligence, not pricing.

Maps NAIC Supplement v5.0 four asks + HM Treasury Q15 onto live Gate mechanisms
a stranger can check without login. Honest about money_real, empty evidence trees,
and OTS deploy status.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

SPEC = "gate-regulator-v1"
FUSE_ID = "fuse_velaru_drill"
JOB_PREFIX = "regulator-verify"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _naic_asks(base: str) -> list[dict[str, Any]]:
    """Exact language of the four asks from the Supplement v5.0 written comment."""
    return [
        {
            "id": "agentic_irreversible",
            "source": "NAIC AI Risk Evaluation Supplement v5.0",
            "ask": (
                "Keep the definition of agentic AI tied to irreversible action "
                "authority — not model-architecture labels."
            ),
            "mechanism": (
                "Issuing auth mouth: every agent card authorization hits Gate Clear "
                "before settlement; workflow category miss → signed NO_GO with claim_scope."
            ),
            "live": {
                "page": f"{base}/issuing-mouth",
                "manifest": f"{base}/.well-known/issuing-mouth.json",
                "webhook": f"{base}/v1/issuing/authorization",
                "dogfood": f"{base}/demo/issuing/mouth",
            },
            "check": (
                "POST /demo/issuing/mouth with allowed_categories=['fuel'] and "
                "merchant_category='software' → approved:false, "
                "claim_scope.boundary=gate_issuing_workflow_category_lock."
            ),
        },
        {
            "id": "exhibit_b_3p",
            "source": "NAIC Exhibit B question 3p",
            "ask": (
                "Third-party AI oversight must be provable artifacts a stranger can "
                "check — not vendor self-attestation alone."
            ),
            "mechanism": (
                "Signed claim_scope + Ed25519 receipt + Merkle inclusion vs published "
                "evidence-head. Seal word HOLDS/BROKEN/UNSIGNED/MISSING."
            ),
            "live": {
                "evidence_head": f"{base}/.well-known/evidence-head.json",
                "seal": f"{base}/seal",
                "receipt_template": f"{base}/.well-known/receipt/{{event_id}}.json",
                "proof_template": f"{base}/.well-known/receipt/{{event_id}}/proof.json",
                "packet_template": f"{base}/.well-known/evidence-packet/{{event_id}}.json",
            },
            "check": (
                "Mint a regulator sample below, then open proof.json and recompute "
                "root from leaf_hash + siblings against evidence-head.root_hash."
            ),
        },
        {
            "id": "materiality_enforceable",
            "source": "NAIC self-specified materiality thresholds",
            "ask": (
                "Disclosed materiality thresholds must be operational and reconcilable "
                "to production records — not ornamental PDF thresholds."
            ),
            "mechanism": (
                "Prefinality mandate caps + Issuing workflow allowlists encoded in "
                "card metadata; breach/deny leaves a timestamped signed claim."
            ),
            "live": {
                "go": f"{base}/go",
                "prefinality": f"{base}/.well-known/prefinality.json",
                "issuing": f"{base}/.well-known/issuing-mouth.json",
            },
            "check": (
                "force_breach:true on Issuing dogfood → NO_GO signal amount_exceeds_cap "
                "with signed claim_scope at evaluation time."
            ),
        },
        {
            "id": "exhibit_a_decision_paths",
            "source": "NAIC Exhibit A Model Inventory",
            "ask": (
                "Model inventories must be exportable and linked to real decision / "
                "write-paths — not nicknames detached from irreversible outcomes."
            ),
            "mechanism": (
                "Mouth manifests enumerate live write-paths (Issuing webhook, Clear, "
                "Go, Never) with machine-readable .well-known JSON."
            ),
            "live": {
                "gate": f"{base}/.well-known/gate.json",
                "issuing": f"{base}/.well-known/issuing-mouth.json",
                "clear": f"{base}/.well-known/clear.json",
                "regulator_json": f"{base}/.well-known/regulator.json",
            },
            "check": (
                "Walk /.well-known/gate.json → issuing_webhook / clear_api / go_api; "
                "each path is a decision surface, not a model nickname."
            ),
        },
    ]


def _hmt_q15(base: str) -> dict[str, Any]:
    return {
        "id": "hmt_q15",
        "source": "HM Treasury — Modernising Payment Services Regulation",
        "question": (
            "Question 15: How does existing payment services regulation need to "
            "adapt to support agentic payments? For example, do provisions relating "
            "to authentication and consent of payments transactions, and liability "
            "for unauthorised payment transactions, need updating?"
        ),
        "deadline": "2026-10-06T23:59:00+01:00",
        "deadline_label": "11:59pm on 6 October 2026",
        "submit_email": "Modernisingpaymentservices@hmtreasury.gov.uk",
        "consultation_url": (
            "https://www.gov.uk/government/consultations/modernising-payment-services-regulation"
        ),
        "mechanism": (
            "Agent authentication before settlement is live on the Issuing mouth: "
            "Stripe issuing_authorization.request → Gate AUTHORIZE/DECLINE with "
            "stranger-verifiable claim_scope. Consent is the mandate + workflow "
            "allowlist checked at auth time; liability trail is the signed receipt."
        ),
        "live": {
            "issuing_page": f"{base}/issuing-mouth",
            "webhook": f"{base}/v1/issuing/authorization",
            "dogfood": f"{base}/demo/issuing/mouth",
            "manifest": f"{base}/.well-known/issuing-mouth.json",
        },
        "check": (
            "Live dogfood refuse outside allowed_categories → approved:false before "
            "any settlement; signed claim_scope is the auth/consent/liability artifact."
        ),
        "gap_closeable": True,
        "honest_limit": (
            "Issuing mouth money_real reflects Stripe+enabled config, not that a "
            "specific demo call moved funds. Demo responses set demo:true."
        ),
    }


def _docket_links(base: str) -> list[dict[str, Any]]:
    """Filed / draft comments a regulator can independently confirm.

    Honest: no Sept 14 filed copy in this tree; NAIC written comment is the
    Sept 29 COB draft carrying the four asks. GAAIA channel is public; no
    Gate-filed copy is checked into this repository.
    """
    return [
        {
            "id": "naic_v5_written",
            "label": "NAIC AI Risk Evaluation Supplement v5.0 — written comment (four asks)",
            "status": "draft_in_repo",
            "deadline": "COB Tuesday, September 29, 2026",
            "to": ["ssobel@naic.org", "mromero@naic.org"],
            "path": "docs/naic/NAIC_AI_RISK_EVAL_SUPPLEMENT_V5_COMMENT_DRAFT.md",
            "url": None,
            "plain": (
                "Four asks live in this draft. Do not treat as filed until a dated "
                "copy exists under docs/naic/submitted/. There is no Sept 14 filed "
                "letter in this repository — verbal Oct 8 reiterates these same asks."
            ),
        },
        {
            "id": "naic_oct8_verbal",
            "label": "NAIC BDAIWG Oct 8, 2026 public Webex — verbal comment",
            "status": "draft_ready",
            "session": "Thursday, October 8, 2026, 11:00 a.m. ET (secondary + timeline sources)",
            "path": "docs/naic/NAIC_OCT8_2026_VERBAL_COMMENT.md",
            "url": "https://content.naic.org/committees/h/big-data-artificial-intelligence-wg",
            "plain": (
                "Reverify Webex link on the NAIC BDAIWG page before speaking. "
                "Aug 31 materials timeline + secondary reporting place the comment "
                "meeting on Oct 8; official events dump may lag."
            ),
        },
        {
            "id": "hmt_q15",
            "label": "HM Treasury Q15 — agentic authentication / consent / liability",
            "status": "draft_ready",
            "deadline": "11:59pm on 6 October 2026",
            "path": "docs/hmt/HMT_Q15_AGENTIC_PAYMENTS_RESPONSE.md",
            "url": (
                "https://www.gov.uk/government/consultations/modernising-payment-services-regulation"
            ),
            "plain": "Submit to Modernisingpaymentservices@hmtreasury.gov.uk before close.",
        },
        {
            "id": "gaaia",
            "label": "Great American AI Act (GAAIA) discussion-draft feedback",
            "status": "channel_open_no_filed_copy_in_repo",
            "submit_email": "GAAIA@mail.house.gov",
            "url": "https://trahan.house.gov/news/documentsingle.aspx?DocumentID=3783",
            "path": None,
            "plain": (
                "Public feedback channel exists. No Gate/Nisaba filed GAAIA letter is "
                "checked into this repository — do not claim one from this page."
            ),
        },
        {
            "id": "regulator_page",
            "label": "This page — stranger-verifiable mapping",
            "status": "live_when_deployed",
            "url": f"{base}/regulator",
            "path": "gate/templates/regulator.html",
            "plain": "Separate from Bind Room, diligence, and pricing.",
        },
    ]


def live_status(base: str) -> dict[str, Any]:
    """Probe what a stranger can hit right now (best-effort; never invents)."""
    try:
        from gate import issuing_mouth as issuing_mouth_mod
    except ImportError:
        import issuing_mouth as issuing_mouth_mod

    try:
        from gate import db
    except ImportError:
        import db

    try:
        from gate import evidence_log as evidence_log_mod
    except ImportError:
        import evidence_log as evidence_log_mod

    try:
        rows = db.list_bind_events_chronological()
    except Exception:
        rows = []
    leaves = evidence_log_mod.log_from_rows(rows)
    head = evidence_log_mod.signed_tree_head(leaves)
    cfg = issuing_mouth_mod.config()

    ots = _probe_ots(base)

    return {
        "evidence_head": {
            "url": f"{base}/.well-known/evidence-head.json",
            "tree_size": head.get("tree_size"),
            "root_hash": head.get("root_hash"),
            "public_key_fingerprint": head.get("public_key_fingerprint"),
            "witness_configured": bool((head.get("witness") or {}).get("configured")),
        },
        "ots": ots,
        "issuing": {
            "money_real": bool(cfg.get("money_real")),
            "issuing_enabled": bool(cfg.get("issuing_enabled")),
            "webhook_secret_configured": bool(cfg.get("webhook_secret_configured")),
            "page": f"{base}/issuing-mouth",
            "plain": (
                "money_real is true only when GATE_ISSUING_ENABLED and Stripe secret "
                "are set — not a claim that a demo call moved money."
            ),
        },
        "inclusion_ready": int(head.get("tree_size") or 0) > 0,
    }


def _probe_ots(base: str) -> dict[str, Any]:
    """OTS status without inventing a live well-known.

    Prefer in-process module when present (this deploy). Otherwise best-effort
    HTTP probe of /.well-known/evidence-ots.json — 404 means not deployed.
    """
    url = f"{base.rstrip('/')}/.well-known/evidence-ots.json"
    try:
        try:
            from gate import ots_anchor as ots_anchor_mod
        except ImportError:
            import ots_anchor as ots_anchor_mod  # type: ignore

        body = ots_anchor_mod.status_payload(base)
        return {
            "url": url,
            "deployed": True,
            "status": body.get("status") or body.get("state") or "present",
            "body": body,
            "plain": "OTS module loaded on this process — well-known should match.",
        }
    except ImportError:
        pass
    except Exception as exc:  # module present but status failed
        return {
            "url": url,
            "deployed": True,
            "status": "error",
            "plain": f"OTS module present but status_payload failed: {exc}",
            "pr": "https://github.com/jdnova0802/mishara/pull/137",
        }

    # No ots_anchor in this tree — probe remote only when base looks public.
    if "example" in base or "localhost" in base or "127.0.0.1" in base:
        return {
            "url": url,
            "deployed": False,
            "status": "not_in_tree",
            "plain": (
                "ots_anchor not imported in this process. "
                "OTS well-known ships via PR #137; offline BTC attestation at height 968706."
            ),
            "offline_proof_note": "gate/outbound/ots-proofs/ (Bitcoin block 968706)",
            "pr": "https://github.com/jdnova0802/mishara/pull/137",
        }

    try:
        req = Request(url, headers={"Accept": "application/json", "User-Agent": "gate-regulator/1"})
        with urlopen(req, timeout=3) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return {
            "url": url,
            "deployed": True,
            "status": body.get("status") or body.get("state") or "present",
            "body": body,
            "plain": "OTS well-known is reachable on this origin.",
        }
    except HTTPError as exc:
        return {
            "url": url,
            "deployed": False,
            "status": "not_found" if exc.code == 404 else f"http_{exc.code}",
            "plain": (
                "OTS endpoint not on this origin yet (open PR #137). "
                "Empty-tree BitcoinBlockHeaderAttestation exists offline at "
                "height 968706 — not inventing a live well-known."
            ),
            "offline_proof_note": "gate/outbound/ots-proofs/ (Bitcoin block 968706)",
            "pr": "https://github.com/jdnova0802/mishara/pull/137",
        }
    except (URLError, TimeoutError, json.JSONDecodeError, ValueError):
        return {
            "url": url,
            "deployed": False,
            "status": "unreachable",
            "plain": "Could not reach OTS well-known from this process — check manually.",
            "pr": "https://github.com/jdnova0802/mishara/pull/137",
        }


def mint_sample(*, public_url: str, job_id: str | None = None) -> dict[str, Any]:
    """Mint one public NO_GO bind event a stranger can verify end-to-end."""
    try:
        from gate import db
    except ImportError:
        import db

    try:
        from gate import claim_scope as claim_scope_mod
    except ImportError:
        import claim_scope as claim_scope_mod

    try:
        from gate import evidence_log as evidence_log_mod
    except ImportError:
        import evidence_log as evidence_log_mod

    jid = (job_id or "").strip() or f"{JOB_PREFIX}-{_utc_now().replace(':', '').replace('+', 'z')}"
    scope = claim_scope_mod.build(
        boundary="gate_regulator_sample",
        logs=[
            "bind_events (receipt_hash, receipt_signature)",
            "gate-evidence-log-v1 Merkle inclusion vs published evidence head",
            "regulator page stranger-verify path",
        ],
        plain=(
            "Regulator sample NO_GO — clearance artifact only, no money moved. "
            "Minted so a stranger can check receipt signature + inclusion proof "
            "without login."
        ),
        keys_checked={"job_id": jid, "audience": "regulator", "money_moved": False},
        counterparties=None,
        time_window={"kind": "mint_instant", "from": None, "to": _utc_now()},
        extra={"audience": "regulator", "money_real": False},
    )
    hop = {
        "state": "DEAD",
        "halt": True,
        "verdict": False,
        "message": "Regulator sample — NO_GO, no write executed.",
        "claim_scope": scope,
        "money_real": False,
        "demo": True,
        "audience": "regulator",
    }
    body = {
        "spec": SPEC,
        "word": "NO_GO",
        "decision": "NO_GO",
        "job_id": jid,
        "rail": "regulator_sample",
        "claim_scope": scope,
    }
    signed = claim_scope_mod.sign_claim(body)
    hop["signed_claim"] = signed.get("signed_claim")

    base = public_url.rstrip("/")
    event_id = db.record_bind_event(
        fuse_id=FUSE_ID,
        job_id=jid,
        account_id=None,
        decision="NO_GO",
        acted=False,
        verify_url=f"{base}/regulator",
        hop=hop,
    )
    rows = db.list_bind_events_chronological()
    bundle = evidence_log_mod.proof_bundle(rows, event_id)
    row = db.get_bind_event(event_id) or {}

    out = {
        "spec": SPEC,
        "minted": True,
        "money_real": False,
        "demo": True,
        "event_id": event_id,
        "job_id": jid,
        "decision": "NO_GO",
        "acted": False,
        "receipt_hash": row.get("receipt_hash"),
        "receipt_signature": row.get("receipt_signature"),
        "claim_scope": scope,
        "signed_claim": signed.get("signed_claim"),
        "inclusion": (bundle or {}).get("inclusion"),
        "tree_head": (bundle or {}).get("tree_head"),
        "urls": {
            "page": f"{base}/regulator?event_id={event_id}",
            "receipt": f"{base}/.well-known/receipt/{event_id}.json",
            "proof": f"{base}/.well-known/receipt/{event_id}/proof.json",
            "packet": f"{base}/.well-known/evidence-packet/{event_id}.json",
            "seal": f"{base}/v1/seal?event_id={event_id}",
            "evidence_head": f"{base}/.well-known/evidence-head.json",
            "evidence_ots": f"{base}/.well-known/evidence-ots.json",
            "issuing_dogfood": f"{base}/demo/issuing/mouth",
        },
        "plain": (
            "Sample minted. Pull receipt JSON, check inclusion against evidence-head, "
            "probe OTS status. No funds moved (money_real:false)."
        ),
    }
    return out


def verify_bundle(*, public_url: str, event_id: str) -> dict[str, Any]:
    """Server-side stranger check: signature + inclusion + OTS probe."""
    try:
        from gate import db
    except ImportError:
        import db

    try:
        from gate import receipt as receipt_mod
    except ImportError:
        import receipt as receipt_mod

    try:
        from gate import evidence_log as evidence_log_mod
    except ImportError:
        import evidence_log as evidence_log_mod

    try:
        from gate import seal_ui as seal_mod
    except ImportError:
        import seal_ui as seal_mod

    eid = (event_id or "").strip()
    base = public_url.rstrip("/")
    if not eid:
        return {"ok": False, "error": "event_id_required", "spec": SPEC}

    row = db.get_bind_event(eid)
    if not row:
        return {"ok": False, "error": "event_not_found", "event_id": eid, "spec": SPEC}

    rows = db.list_bind_events_chronological()
    bundle = evidence_log_mod.proof_bundle(rows, eid)
    sig_ok = receipt_mod.verify_receipt_signature(
        receipt_hash=row.get("receipt_hash") or "",
        signature_b64=row.get("receipt_signature"),
    )
    inclusion_ok = False
    if bundle:
        inclusion_ok = evidence_log_mod.verify_inclusion(
            leaf_hash=bundle["receipt_hash"],
            root_hash=bundle["tree_head"]["root_hash"],
            proof=bundle["inclusion"],
        )
    seal = seal_mod.seal_event(eid, rows=rows)
    ots = _probe_ots(base)
    head = evidence_log_mod.signed_tree_head(evidence_log_mod.log_from_rows(rows))

    return {
        "spec": SPEC,
        "ok": bool(sig_ok and inclusion_ok),
        "event_id": eid,
        "money_real": False,
        "checks": {
            "receipt_signature": sig_ok,
            "inclusion_proof": inclusion_ok,
            "seal_word": seal.get("word"),
            "ots_deployed": bool(ots.get("deployed")),
            "ots_status": ots.get("status"),
        },
        "evidence_head": {
            "tree_size": head.get("tree_size"),
            "root_hash": head.get("root_hash"),
            "url": f"{base}/.well-known/evidence-head.json",
        },
        "inclusion": (bundle or {}).get("inclusion"),
        "ots": ots,
        "urls": {
            "receipt": f"{base}/.well-known/receipt/{eid}.json",
            "proof": f"{base}/.well-known/receipt/{eid}/proof.json",
            "packet": f"{base}/.well-known/evidence-packet/{eid}.json",
            "seal": f"{base}/v1/seal?event_id={eid}",
            "page": f"{base}/regulator?event_id={eid}",
        },
        "plain": (
            "All green means signature + Merkle inclusion hold on this origin. "
            "OTS may still be pending/not deployed — read checks.ots_* honestly."
        ),
    }


def manifest(base: str) -> dict[str, Any]:
    base = (base or "").rstrip("/")
    status = live_status(base)
    return {
        "spec": SPEC,
        "name": "Gate — regulator verify",
        "audience": "regulators_and_policy_staff",
        "not": ["bind_room", "diligence", "pricing", "commercial_cta"],
        "page": f"{base}/regulator",
        "mint": f"{base}/demo/regulator/mint",
        "verify": f"{base}/v1/regulator/verify",
        "promise": (
            "Map NAIC's four asks and HM Treasury Q15 to live Gate mechanisms. "
            "One click mints a stranger-verifiable NO_GO receipt."
        ),
        "naic_asks": _naic_asks(base),
        "hmt_q15": _hmt_q15(base),
        "docket": _docket_links(base),
        "live": status,
        "updated": _utc_now(),
    }
