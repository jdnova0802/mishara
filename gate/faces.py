"""Chewable buyer faces — display layers on existing SKUs/desks.

Prices always resolve from commerce ladder. Do not invent mid-ladder SKUs here.
"""
from __future__ import annotations

from typing import Any

try:
    from gate import commerce as commerce_mod
except ImportError:
    import commerce as commerce_mod  # type: ignore


def _price_for(face: dict[str, Any]) -> str:
    sku_id = face.get("sku_id")
    if sku_id:
        return commerce_mod.price_label(str(sku_id))
    return str(face.get("price_label") or "")


def resolve(face: dict[str, Any], *, public_url: str = "", mishara_url: str = "") -> dict[str, Any]:
    """Copy a face row and attach resolved price + absolute proof/CTA URLs."""
    out = dict(face)
    out["price_label"] = _price_for(face)
    host = face.get("host") or "gate"
    hosts = commerce_mod.hosts().get("canonical") or {}
    gate = (public_url or hosts.get("gate") or "").rstrip("/")
    mishara = (mishara_url or hosts.get("mishara") or "").rstrip("/")
    base = mishara if host == "mishara" else gate

    def abs_path(path: str | None) -> str | None:
        if not path:
            return None
        if str(path).startswith("http://") or str(path).startswith("https://"):
            return str(path)
        return f"{base}{path}"

    proof = dict(face.get("proof") or {})
    if proof.get("path"):
        proof["url"] = abs_path(str(proof["path"]))
    out["proof"] = proof

    cta = dict(face.get("cta") or {})
    if cta.get("path"):
        cta["url"] = abs_path(str(cta["path"]))
    out["cta"] = cta

    secondary = dict(face.get("secondary") or {})
    if secondary.get("href"):
        secondary["url"] = str(secondary["href"])
    elif secondary.get("path"):
        secondary["url"] = abs_path(str(secondary["path"]))
    out["secondary"] = secondary

    out["page_url"] = abs_path(str(face.get("path") or ""))
    out["canonical_product_url"] = abs_path(str(face.get("canonical_product_path") or ""))
    return out


def all_faces(*, public_url: str = "", mishara_url: str = "") -> list[dict[str, Any]]:
    rows = commerce_mod.faces_raw().get("faces") or []
    return [resolve(row, public_url=public_url, mishara_url=mishara_url) for row in rows]


def gate_faces(*, public_url: str = "") -> list[dict[str, Any]]:
    return [f for f in all_faces(public_url=public_url) if f.get("host") == "gate"]


def mishara_faces(*, mishara_url: str = "") -> list[dict[str, Any]]:
    return [f for f in all_faces(mishara_url=mishara_url) if f.get("host") == "mishara"]


def face_by_id(face_id: str, *, public_url: str = "", mishara_url: str = "") -> dict[str, Any]:
    for row in all_faces(public_url=public_url, mishara_url=mishara_url):
        if row.get("id") == face_id:
            return row
    raise KeyError(face_id)


def face_by_path(path: str, *, public_url: str = "", mishara_url: str = "") -> dict[str, Any]:
    for row in all_faces(public_url=public_url, mishara_url=mishara_url):
        if row.get("path") == path:
            return row
    raise KeyError(path)


def manifest(*, public_url: str = "", mishara_url: str = "") -> dict[str, Any]:
    raw = commerce_mod.faces_raw()
    base = (public_url or "").rstrip("/")
    return {
        "spec": raw.get("spec") or "nisaba-commerce-faces-v1",
        "note": raw.get("note"),
        "faces": all_faces(public_url=public_url, mishara_url=mishara_url),
        "links": {
            "index": f"{base}/faces" if base else "/faces",
            "json": f"{base}/.well-known/faces.json" if base else "/.well-known/faces.json",
            "commerce": f"{base}/.well-known/commerce.json" if base else None,
        },
    }
