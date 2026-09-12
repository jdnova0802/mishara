"""Single source of truth for public money, doctrine, entity, and hosts.

Pages, manifests, and generators must import from here (or the JSON under
gate/commerce/). Do not hand-type public prices into a second place.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent / "commerce"


@lru_cache(maxsize=1)
def _load() -> dict[str, Any]:
    out: dict[str, Any] = {}
    for name in ("ladder", "doctrine", "entities", "hosts", "faces", "erra_sprints"):
        path = ROOT / f"{name}.json"
        with path.open(encoding="utf-8") as f:
            out[name] = json.load(f)
    return out


def reload() -> None:
    _load.cache_clear()


def ladder() -> dict[str, Any]:
    return _load()["ladder"]


def doctrine() -> dict[str, Any]:
    return _load()["doctrine"]


def entities() -> dict[str, Any]:
    return _load()["entities"]


def hosts() -> dict[str, Any]:
    return _load()["hosts"]


def faces_raw() -> dict[str, Any]:
    return _load()["faces"]


def erra_sprints() -> dict[str, Any]:
    return _load()["erra_sprints"]


def sku(sku_id: str) -> dict[str, Any]:
    for row in ladder().get("public_ladder") or []:
        if row.get("id") == sku_id:
            return dict(row)
    raise KeyError(sku_id)


def price_label(sku_id: str) -> str:
    return str(sku(sku_id)["price_label"])


def price_cents(sku_id: str) -> int:
    return int(sku(sku_id).get("price_cents") or 0)


def bps(sku_id: str = "operator_flow_bps") -> int:
    return int(sku(sku_id).get("bps") or 0)


def legal_name() -> str:
    return str(entities()["legal_name"])


def patent_display() -> str:
    return str(entities()["patent"]["display"])


def patent_short() -> str:
    return str(entities()["patent"]["short"])


def support_email() -> str:
    return str(entities()["support"]["email"])


def support_sla() -> str:
    return str(entities()["support"]["response_expectation"])


def accountability() -> str:
    return str(entities()["support"]["accountability"])


def api_policy() -> dict[str, Any]:
    return dict(entities()["api_policy"])


def brand_line(brand_id: str) -> dict[str, Any]:
    return dict((doctrine().get("brands") or {}).get(brand_id) or {})


def security_txt(*, canonical_url: str = "") -> str:
    ent = entities()
    base = (canonical_url or hosts()["canonical"]["gate"]).rstrip("/")
    return "\n".join(
        [
            f"Contact: mailto:{ent['security']['contact_email']}",
            "Expires: 2027-09-12T00:00:00.000Z",
            f"Preferred-Languages: {', '.join(ent['security']['preferred_languages'])}",
            f"Canonical: {base}/.well-known/security.txt",
            f"Policy: {ent['security']['security_txt_policy']}",
            f"Acknowledgments: {base}/trust",
            "",
        ]
    )


def manifest(public_url: str = "") -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": "nisaba-commerce-v1",
        "legal_name": legal_name(),
        "patent": entities()["patent"],
        "support": entities()["support"],
        "api_policy": api_policy(),
        "ladder": ladder()["public_ladder"],
        "rails": ladder().get("rails"),
        "doctrine": doctrine()["brands"],
        "hosts": hosts(),
        "erra_sprints": erra_sprints(),
        "hustle_board": f"{base}/outbound/HUSTLE_BOARD.md" if base else None,
        "claims_forbidden": entities().get("claims_forbidden"),
        "links": {
            "json": f"{base}/.well-known/commerce.json" if base else None,
            "ladder": f"{base}/pricing" if base else None,
            "faces": f"{base}/.well-known/faces.json" if base else None,
            "faces_index": f"{base}/faces" if base else None,
            "diligence": f"{base}/diligence" if base else None,
            "refusal": f"{base}/refusal" if base else None,
            "erra_hub": (hosts().get("canonical") or {}).get("erra"),
            "hustle_board": f"{base}/outbound/HUSTLE_BOARD.md" if base else None,
            "security_txt": f"{base}/.well-known/security.txt" if base else None,
        },
    }
