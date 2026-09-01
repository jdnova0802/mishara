"""Time-source attestation — the chain proves order; it does not prove when.

Every folio already stamps a wall-clock. If that clock is GNSS, the claim
an adjuster cares about — this was recorded before the loss, not after —
sits on a spoofable signal with no institutional fallback.

Merkle anchoring fixes existence-by-a-point. It does not fix the timestamp
inside the entry.

This is a stamp on packs we already sell. Not a /time page. Not eLoran.
Not a timing network. Not a sixth sibling. Not Being.
On GNSS loss or suspected spoof: HALT any claim of recorded-before-loss.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-time-source-v1"
FAMILY_SIBLINGS_REMAIN = 5
L2_MODULE = False
CLEVERER_LAYER = None

IDENTITY = "the chain proves order; it does not prove when"


def attest() -> dict[str, Any]:
    """Diligence stamp. We do not claim recorded-before-loss."""
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return {
        "spec": SPEC,
        "kind": "time_source_attestation",
        "identity": IDENTITY,
        "clock": "host_utc",
        "path": "process wall-clock on the mouth that sealed this pack",
        "proves": "order on this host",
        "does_not_prove": "that this timestamp predates a loss against a spoofed GNSS",
        "on_gnss_loss": "HALT claim of recorded-before-loss",
        "on_suspected_spoof": "HALT claim of recorded-before-loss",
        "merkle_fixes": "existence-by-a-point",
        "merkle_does_not_fix": "the timestamp inside the entry",
        "claims_before_loss": False,
        "utc_note": "CGPM 2018 recommended international now — not a GNSS attestation",
        "not_a_timing_network": True,
        "not_eloran": True,
        "stamped_at": now,
        "cleverer_layer": CLEVERER_LAYER,
        "l2_module": L2_MODULE,
        "their_production": False,
        "family_siblings_remain": FAMILY_SIBLINGS_REMAIN,
        "not": [
            "eLoran",
            "a timing network",
            "a GNSS backup",
            "a sixth sibling",
            "Being",
        ],
    }
