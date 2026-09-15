"""Hard lab invariant: their_production must be False — never aspirational.

Every mouth module exposes THEIR_PRODUCTION = False and stamps it on every
receipt via stamp_lab / stamp_lab_flag. Proves call assert_all_receipts_lab()
so a mutated flag fails CI, not docs.
"""

from __future__ import annotations

from typing import Any, Protocol


class LabMouth(Protocol):
    THEIR_PRODUCTION: bool
    STORE: Any


class LabInvariantError(AssertionError):
    pass


def stamp_lab_flag(flag: bool, *, module: str) -> bool:
    """Value written on receipts — raises if flag was mutated away from False."""
    if flag is not False:
        raise LabInvariantError(
            f"{module}.THEIR_PRODUCTION must be identically False, got {flag!r}"
        )
    return False


def lab_flag(module: LabMouth) -> bool:
    name = getattr(module, "__name__", str(module))
    return stamp_lab_flag(getattr(module, "THEIR_PRODUCTION", None), module=name)


def assert_module_lab(module: LabMouth) -> None:
    lab_flag(module)


def assert_payload_lab(payload: dict[str, Any], *, where: str = "payload") -> None:
    if "their_production" not in payload:
        raise LabInvariantError(f"{where}: missing their_production")
    if payload["their_production"] is not False:
        raise LabInvariantError(
            f"{where}: their_production must be False, got {payload['their_production']!r}"
        )


def assert_all_receipts_lab(module: LabMouth) -> None:
    """Fail if any stored receipt is missing or not identically False."""
    assert_module_lab(module)
    store = getattr(module, "STORE", None)
    if store is None:
        raise LabInvariantError(f"{module.__name__}: no STORE")
    receipts = getattr(store, "receipts", None)
    if receipts is None:
        raise LabInvariantError(f"{module.__name__}: STORE has no receipts")
    if len(receipts) == 0:
        raise LabInvariantError(f"{module.__name__}: no receipts to audit (prove never fired?)")
    for rid, receipt in receipts.items():
        assert_payload_lab(receipt, where=f"{module.__name__}.receipts[{rid}]")


def stamp_lab(module: LabMouth) -> bool:
    """Value to write on every receipt — re-checks invariant at stamp time."""
    return lab_flag(module)
