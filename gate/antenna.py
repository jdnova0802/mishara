"""Stranger Antenna — verify as public xenoreceiver: anyone can listen, no PII.

Alien beacons are for whoever arrives. Gate's verify URL + restraint
inventory is an antenna, not a customer portal. If only insiders can
hear CHARGE, it is not hardware — it is a club. Copycats hide evidence
behind login. Gate broadcasts the no.

Gatekeep only to ourselves: SETI beacon / public antenna → stranger verify.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

SPEC = "gate-stranger-antenna-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def listen(
    *,
    verify_url: str | None = None,
    login_walled: bool | None = None,
    pii_on_antenna: bool | None = None,
) -> dict[str, Any]:
    url = bool((verify_url or "").strip())
    walled = bool(login_walled)
    pii = bool(pii_on_antenna)
    if pii:
        posture = "contaminated_beacon"
        claim = "pii_on_antenna_is_not_a_public_no"
    elif walled:
        posture = "club_not_antenna"
        claim = "login_wall_kills_stranger_listen"
    elif url:
        posture = "antenna_live"
        claim = "stranger_can_fetch_the_occasion"
    else:
        posture = "silent"
        claim = "no_verify_url_no_beacon"
    return {
        "spec": SPEC,
        "name": "Stranger Antenna",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "SETI / public beacon — evidence for whoever arrives",
            "Gate stranger verify — no PII on PAS/restraint",
        ],
        "verify_present": url,
        "login_walled": walled,
        "pii_on_antenna": pii,
        "posture": posture,
        "claim": claim,
        "thesis": "If a stranger cannot fetch the receipt, you built a club, not an antenna.",
        "gatekeep": "Proprietary stranger-antenna doctrine. Ours.",
        "their_production": False,
    }


def attach_to_receipt_payload(payload: Mapping[str, Any], row: Mapping[str, Any]) -> dict[str, Any]:
    out = dict(payload)
    out["stranger_antenna"] = listen(verify_url=row.get("verify_url"), login_walled=False, pii_on_antenna=False)
    return out


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Stranger Antenna",
        "inventor": INVENTOR,
        "example_live": listen(verify_url="https://velaru.xyz/verify"),
        "example_club": listen(verify_url="https://x", login_walled=True),
        "live": f"{base}/.well-known/stranger-antenna.json",
        "receipt": f"{base}/.well-known/receipt/{{event_id}}.json",
        "their_production": False,
    }
