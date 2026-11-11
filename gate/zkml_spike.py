"""Item 153 — zkML feasibility spike, not a shipped prover.

EZKL is the cited track. This module records measurements if a human
supplies them. It does not generate proofs, invent drift, or treat a
schema as a passing eval.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SPEC = "gate-zkml-spike-v1"
BACKEND = "halo2"


def _iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _path() -> Path:
    return Path(os.getenv("GATE_ZKML_PATH") or Path(__file__).resolve().parent / "data" / "zkml_spike.json")


def _load() -> dict[str, Any]:
    path = _path()
    if not path.exists():
        return {"spec": SPEC, "measurements": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"spec": SPEC, "measurements": []}
    if not isinstance(data, dict):
        return {"spec": SPEC, "measurements": []}
    data.setdefault("measurements", [])
    return data


def _save(store: dict[str, Any]) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2), encoding="utf-8")


def ezkl_present() -> bool:
    try:
        import ezkl  # noqa: F401
    except Exception:
        return False
    return True


def catalog() -> dict[str, Any]:
    store = _load()
    present = ezkl_present()
    return {
        "spec": SPEC,
        "proof_backend": BACKEND,
        "ezkl_imported": present,
        "proof_generation_shipped": False,
        "quantization_drift_unmeasured_until_posted": True,
        "gpu_cutoff_unmeasured_until_posted": True,
        "measurements": store["measurements"],
        "plain": (
            "Spike only. No Halo2 proof is minted here. Post the three measurements from a real ONNX run."
        ),
        "blocked_on": (
            None
            if store["measurements"]
            else "proof_generation_time_ms, output_drift, gpu_acceleration_cleared"
        ),
    }


def record_measurement(
    *,
    classifier_model_id: str,
    proof_generation_time_ms: float | int | None,
    output_drift: float | None,
    gpu_acceleration_cleared: bool | None,
    notes: str | None = None,
) -> dict[str, Any]:
    mid = (classifier_model_id or "").strip()
    if not mid:
        return {"spec": SPEC, "ok": False, "error": "classifier_model_id_required"}
    if proof_generation_time_ms is None or output_drift is None or gpu_acceleration_cleared is None:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "three_numbers_required",
            "plain": "Do not invent proof time, drift, or GPU cutoff. Measure against a real 136 ONNX export.",
        }
    try:
        time_ms = float(proof_generation_time_ms)
        drift = float(output_drift)
    except (TypeError, ValueError):
        return {"spec": SPEC, "ok": False, "error": "measurements_numeric"}
    rec = {
        "spec": SPEC,
        "ok": True,
        "measurement_id": "zk_" + uuid.uuid4().hex[:12],
        "classifier_model_id": mid,
        "proof_generation_time_ms": time_ms,
        "output_drift": drift,
        "gpu_acceleration_cleared": bool(gpu_acceleration_cleared),
        "proof_backend": BACKEND,
        "notes": (notes or "").strip() or None,
        "recorded_at": _iso(),
        "ships_prover": False,
        "plain": "Logged. Shipping a prover is a later decision on these numbers, not a schema.",
    }
    store = _load()
    store["measurements"].append(rec)
    _save(store)
    return rec


def attach_proof(
    *,
    receipt_id: str,
    classifier_model_id: str,
    public_output: str | None = None,
    private_input_commitment: str | None = None,
    proof_blob_ref: str | None = None,
) -> dict[str, Any]:
    return {
        "spec": SPEC,
        "ok": False,
        "error": "prover_not_shipped",
        "receipt_id": (receipt_id or "").strip() or None,
        "classifier_model_id": (classifier_model_id or "").strip() or None,
        "public_output": public_output,
        "private_input_commitment": private_input_commitment,
        "proof_backend": BACKEND,
        "proof_blob_ref": proof_blob_ref,
        "verified_by": [],
        "plain": "Feasibility spike. A proof_blob_ref is not accepted until EZKL measurements decide the build.",
    }
