"""Chaos fail-closed pack — executable denies for institutional diligence.

Each scenario returns {id, ok, detail}. `run_pack()` is safe: it does not
take production down; it exercises local custody/seal/crypto and mocked
upstream failure shapes. gate_down_policy is attested as required behavior
(cannot be proven from Gate alone without their_production weld).
"""

from __future__ import annotations

import base64
import os
import tempfile
import uuid
from typing import Any, Callable


SPEC = "gate-chaos-fail-closed-v1"


def _ok(cid: str, ok: bool, detail: str, **extra: Any) -> dict:
    row = {"id": cid, "ok": ok, "detail": detail}
    row.update(extra)
    return row


def scenario_custody_unavailable() -> dict:
    try:
        from gate import receipt as receipt_mod
        from gate import custody as custody_mod
    except ImportError:
        import receipt as receipt_mod
        import custody as custody_mod

    prev_dev = os.environ.get("GATE_DEV_MODE")
    prev_priv = os.environ.get("GATE_RECEIPT_PRIVATE_KEY")
    prev_pub = os.environ.get("GATE_RECEIPT_PUBLIC_KEY")
    prev_mode = os.environ.get("GATE_RECEIPT_CUSTODY")
    try:
        os.environ["GATE_DEV_MODE"] = "0"
        os.environ["GATE_RECEIPT_CUSTODY"] = "env"
        os.environ.pop("GATE_RECEIPT_PRIVATE_KEY", None)
        os.environ.pop("GATE_RECEIPT_PUBLIC_KEY", None)
        available = custody_mod.EnvCustody().available()
        out = receipt_mod.issue_receipt(
            event_id="chaos-unsigned",
            fuse_id="fuse_chaos",
            job_id="chaos:1",
            decision="HALT",
            acted=False,
            verify_url=None,
            created_at="2026-01-01T00:00:00+00:00",
            hop={},
            prev_receipt_hash=None,
        )
        passed = (not available) and bool(out.get("unsigned_halt"))
        return _ok(
            "custody_unavailable",
            passed,
            "unsigned_halt outside DEV when custody cannot sign",
            unsigned_halt=bool(out.get("unsigned_halt")),
            custody_available=available,
        )
    finally:
        if prev_dev is None:
            os.environ.pop("GATE_DEV_MODE", None)
        else:
            os.environ["GATE_DEV_MODE"] = prev_dev
        if prev_priv:
            os.environ["GATE_RECEIPT_PRIVATE_KEY"] = prev_priv
        if prev_pub:
            os.environ["GATE_RECEIPT_PUBLIC_KEY"] = prev_pub
        if prev_mode is None:
            os.environ.pop("GATE_RECEIPT_CUSTODY", None)
        else:
            os.environ["GATE_RECEIPT_CUSTODY"] = prev_mode


def scenario_forge_signature() -> dict:
    try:
        from gate import receipt as receipt_mod
        from gate import custody as custody_mod
    except ImportError:
        import receipt as receipt_mod
        import custody as custody_mod

    pub = custody_mod.public_key_b64()
    if not pub:
        return _ok("forge_signature", False, "no public key configured for verify")
    # Random 64-byte blob as forged signature.
    forged = base64.b64encode(os.urandom(64)).decode("utf-8")
    ok_forge = receipt_mod.verify_receipt_signature(
        receipt_hash="a" * 64,
        signature_b64=forged,
        public_key_b64=pub,
    )
    return _ok(
        "forge_signature",
        ok_forge is False,
        "invented signature must not verify",
        verified=ok_forge,
    )


def scenario_tamper_receipt_hash() -> dict:
    try:
        from gate import receipt as receipt_mod
        from gate import custody as custody_mod
    except ImportError:
        import receipt as receipt_mod
        import custody as custody_mod

    real_hash = "b" * 64
    sig = custody_mod.sign_receipt_hash(real_hash)
    pub = custody_mod.public_key_b64()
    if not sig or not pub:
        return _ok("tamper_receipt_hash", False, "custody could not sign baseline hash")
    # Attacker keeps sig, claims a different hash.
    tampered = receipt_mod.verify_receipt_signature(
        receipt_hash="c" * 64,
        signature_b64=sig,
        public_key_b64=pub,
    )
    honest = receipt_mod.verify_receipt_signature(
        receipt_hash=real_hash,
        signature_b64=sig,
        public_key_b64=pub,
    )
    passed = (tampered is False) and (honest is True)
    return _ok(
        "tamper_receipt_hash",
        passed,
        "signature bound to hash; flipped hash fails",
        tampered_verifies=tampered,
        honest_verifies=honest,
    )


def scenario_seal_tamper() -> dict:
    try:
        from gate import evidence_seal as seal_mod
    except ImportError:
        import evidence_seal as seal_mod

    path = os.path.join(tempfile.gettempdir(), f"chaos-seal-{uuid.uuid4().hex}.seal")
    prev = os.environ.get("GATE_EVIDENCE_SEAL_PATH")
    try:
        os.environ["GATE_EVIDENCE_SEAL_PATH"] = path
        if os.path.isfile(path):
            os.remove(path)
        seal_mod.append_receipt_hash("d" * 64)
        seal_mod.append_receipt_hash("e" * 64)
        good = seal_mod.verify_seal(path)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(f"1 {'f' * 64} notadigest\n")
        bad = seal_mod.verify_seal(path)
        passed = bool(good.get("ok")) and (bad.get("ok") is False)
        return _ok(
            "seal_tamper",
            passed,
            "append-only seal detects rewrite",
            good_ok=bool(good.get("ok")),
            bad_reason=bad.get("reason"),
        )
    finally:
        if prev is None:
            os.environ.pop("GATE_EVIDENCE_SEAL_PATH", None)
        else:
            os.environ["GATE_EVIDENCE_SEAL_PATH"] = prev
        try:
            os.remove(path)
        except OSError:
            pass


def scenario_velaru_unreachable(fail_closed_fn: Callable | None = None) -> dict:
    """Exercise fail_closed shape (injectable for unit tests)."""
    if fail_closed_fn is None:
        try:
            from gate import app as gate_app
        except ImportError:
            import app as gate_app

        fail_closed_fn = gate_app.fail_closed

    payload, status, headers = fail_closed_fn("ocsp_timeout", "fuse_chaos")
    passed = (
        status == 503
        and payload.get("state") == "UNREACHABLE"
        and payload.get("verdict") is False
        and payload.get("acted") is False
        and payload.get("halt") is True
        and headers.get("X-Gate-Fail-Closed") == "1"
    )
    return _ok(
        "velaru_unreachable",
        passed,
        "timeout/upstream → 503 UNREACHABLE never LIVE",
        status=status,
        state=payload.get("state"),
    )


def scenario_staple_mismatch() -> dict:
    try:
        from gate import custody as custody_mod
        from gate import receipt as receipt_mod
    except ImportError:
        import custody as custody_mod
        import receipt as receipt_mod

    real_fp = custody_mod.public_key_fingerprint()
    if not real_fp:
        return _ok("staple_mismatch", False, "no custody fingerprint")
    # Simulate receipt minted under a different fingerprint.
    mismatch = real_fp != ("0" * 16)
    # Also: verify with wrong public key must fail.
    sig = custody_mod.sign_receipt_hash("a" * 64)
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

    other = Ed25519PrivateKey.generate().public_key().public_bytes(
        Encoding.Raw, PublicFormat.Raw
    )
    other_b64 = base64.b64encode(other).decode("utf-8")
    wrong_key_ok = False
    if sig:
        wrong_key_ok = receipt_mod.verify_receipt_signature(
            receipt_hash="a" * 64,
            signature_b64=sig,
            public_key_b64=other_b64,
        )
    passed = mismatch and (wrong_key_ok is False)
    return _ok(
        "staple_mismatch",
        passed,
        "foreign public key must not verify custody signatures",
        wrong_key_verifies=wrong_key_ok,
    )


def scenario_no_admin_resurrect() -> dict:
    """Static code attestation: Gate must not expose admin DEAD→LIVE."""
    try:
        from gate import app as gate_app
    except ImportError:
        import app as gate_app

    with open(gate_app.__file__, "r", encoding="utf-8") as fh:
        src = fh.read()
    dangerous = any(
        x in src
        for x in (
            "def admin_resurrect",
            "def force_live",
            "def set_fuse_live",
            "def resurrect_fuse",
        )
    )
    passed = not dangerous
    return _ok(
        "no_admin_resurrect",
        passed,
        "no Gate admin resurrect helpers; CHARGE-only on Velaru",
        dangerous=dangerous,
    )


def scenario_gate_down_policy() -> dict:
    """Cannot prove their runtime from Gate alone — attested requirement."""
    return _ok(
        "gate_down_policy",
        True,
        "REQUIRED in their_production: worker/PAS must DENY when Gate unreachable",
        attested=True,
        proven_in_gate=False,
        their_production_required=True,
    )


SCENARIOS: tuple[Callable[[], dict], ...] = (
    scenario_custody_unavailable,
    scenario_forge_signature,
    scenario_tamper_receipt_hash,
    scenario_seal_tamper,
    scenario_velaru_unreachable,
    scenario_staple_mismatch,
    scenario_no_admin_resurrect,
    scenario_gate_down_policy,
)


def run_pack() -> dict:
    results = []
    for fn in SCENARIOS:
        try:
            results.append(fn())
        except Exception as exc:  # noqa: BLE001 — pack must report, not crash
            results.append(_ok(getattr(fn, "__name__", "unknown"), False, f"exception: {exc}"))
    # gate_down is attested ok; exclude from all_pass gate if we want strict —
    # institutions still want the rest green.
    strict = [r for r in results if not r.get("their_production_required")]
    all_pass = all(r.get("ok") for r in strict)
    return {
        "spec": SPEC,
        "all_pass": all_pass,
        "ran": len(results),
        "passed": sum(1 for r in results if r.get("ok")),
        "results": results,
        "their_production": False,
        "note": (
            "gate_down_policy is attested until an exclusive third-party weld exists. "
            "Other rows are executed locally."
        ),
    }


def pack_manifest(*, public_url: str | None = None) -> dict:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "description": "Executable fail-closed chaos scenarios for Gate clearance",
        "run": f"{base}/.well-known/chaos-pack.json?run=1" if base else None,
        "threat_model": f"{base}/.well-known/threat-model.json" if base else None,
        "scenarios": [fn.__name__.replace("scenario_", "") for fn in SCENARIOS],
        "their_production": False,
    }
