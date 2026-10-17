"""Match pledged VINs across lender tapes the originator cannot edit.

Each tape is a separate input. Nothing in this module trusts a delinquency
flag. It looks for the same VIN twice, a one-character VIN edit, or a VIN
missing from a dealer-system export.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable


def hamming(a: str, b: str) -> int:
    if len(a) != len(b):
        return max(len(a), len(b))
    return sum(x != y for x, y in zip(a, b))


def flatten(tapes: dict[str, list[dict]]) -> list[dict]:
    rows = []
    for facility, tape in tapes.items():
        for row in tape:
            rows.append({**row, "facility": facility})
    return rows


def _public_row(row: dict) -> dict:
    return {
        "facility": row["facility"],
        "row_id": row["row_id"],
        "account_id": row["account_id"],
        "vin": row["vin"],
        "principal_reported": row["principal_reported"],
        "delinquency_reported": row["delinquency_reported"],
        "provenance": row["provenance"],
        "year": row["year"],
        "make": row["make"],
        "model": row["model"],
        "mileage": row["mileage"],
    }


def within_tape(rows: Iterable[dict]) -> list[dict]:
    """Same VIN more than once on one facility's own file."""
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        grouped[(row["facility"], row["vin"])].append(row)
    hits = []
    for (facility, vin), group in sorted(grouped.items()):
        if len(group) < 2:
            continue
        hits.append(
            {
                "kind": "within_tape_vin",
                "facility": facility,
                "vin": vin,
                "pledge_count": len(group),
                "account_ids": [r["account_id"] for r in group],
                "rows": [_public_row(r) for r in group],
            }
        )
    return hits


def exact_vin(rows: Iterable[dict]) -> list[dict]:
    """Same VIN on more than one pledge row, including across facilities."""
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["vin"]].append(row)
    hits = []
    for vin, group in sorted(grouped.items()):
        if len(group) < 2:
            continue
        facilities = sorted({r["facility"] for r in group})
        hits.append(
            {
                "kind": "exact_vin",
                "vin": vin,
                "pledge_count": len(group),
                "facilities": facilities,
                "across_facilities": len(facilities) > 1,
                "account_ids": [r["account_id"] for r in group],
                "distinct_vehicles_if_vin_is_truthful": 1,
                "rows": [_public_row(r) for r in group],
            }
        )
    return hits


def near_vin(rows: Iterable[dict], max_distance: int = 1) -> list[dict]:
    """VINs that differ by a small number of characters. Default is one."""
    by_vin: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_vin[row["vin"]].append(row)
    vins = sorted(by_vin)
    hits = []
    for i, left in enumerate(vins):
        for right in vins[i + 1 :]:
            distance = hamming(left, right)
            if distance <= 0 or distance > max_distance:
                continue
            hits.append(
                {
                    "kind": "near_vin",
                    "distance": distance,
                    "vin_a": left,
                    "vin_b": right,
                    "facilities_a": sorted({r["facility"] for r in by_vin[left]}),
                    "facilities_b": sorted({r["facility"] for r in by_vin[right]}),
                    "rows_a": [_public_row(r) for r in by_vin[left]],
                    "rows_b": [_public_row(r) for r in by_vin[right]],
                }
            )
    return hits


def absent_from_dealer(rows: Iterable[dict], dealer_vins: set[str]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        if row["vin"] not in dealer_vins:
            grouped[row["vin"]].append(row)
    hits = []
    for vin, group in sorted(grouped.items()):
        hits.append(
            {
                "kind": "absent_from_dealer",
                "vin": vin,
                "facilities": sorted({r["facility"] for r in group}),
                "pledge_count": len(group),
                "rows": [_public_row(r) for r in group],
            }
        )
    return hits


def analyze(ledger: dict, max_distance: int = 1) -> dict:
    rows = flatten(ledger["tapes"])
    dealer_vins = {row["vin"] for row in ledger["dealer_system"]}
    exact = exact_vin(rows)
    near = near_vin(rows, max_distance=max_distance)
    absent = absent_from_dealer(rows, dealer_vins)
    caught = {hit["vin"] for hit in exact}
    caught.update(hit["vin"] for hit in absent)
    for hit in near:
        caught.add(hit["vin_a"])
        caught.add(hit["vin_b"])
    unflagged = []
    seen = set()
    for row in rows:
        if row["vin"] in caught or row["vin"] in seen:
            continue
        seen.add(row["vin"])
        unflagged.append(
            {
                "vin": row["vin"],
                "facilities": sorted(
                    {r["facility"] for r in rows if r["vin"] == row["vin"]}
                ),
                "row_ids": [r["row_id"] for r in rows if r["vin"] == row["vin"]],
                "provenance": row["provenance"],
                "note": row["note"],
            }
        )
    return {
        "pledge_rows": len(rows),
        "distinct_vins_on_tapes": len({r["vin"] for r in rows}),
        "within_tape": within_tape(rows),
        "exact": exact,
        "near": near,
        "absent_from_dealer": absent,
        "unflagged": unflagged,
    }


def solo_exceptions(ledger: dict) -> dict[str, list[dict]]:
    """What each facility would see if it deduped only its own file."""
    out = {}
    for facility, tape in ledger["tapes"].items():
        rows = [{**row, "facility": facility} for row in tape]
        out[facility] = within_tape(rows)
    return out
