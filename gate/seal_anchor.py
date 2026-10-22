"""Scheduled public anchor for the seal Merkle root.

This process is the only place a root is published. GET /v1/seal/job reads the
last broadcast row and the cached leaf proofs. It does not hash the tree again
and it does not talk to Base or OpenTimestamps.

Default mode is off. Base Sepolia or Base mainnet broadcast also requires
GATE_SEAL_ANCHOR_SPEND=1 and GATE_SEAL_ANCHOR_PRIVATE_KEY. A commit whose gas
estimate is above 30,000, or whose base fee is above the cap, is not sent.

Run from gate/ every 15 minutes, as its own process:

    python3 seal_anchor.py
    python3 seal_anchor.py --loop
    python3 seal_anchor.py --estimate
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
import urllib.error
import urllib.request
import uuid
from typing import Any

try:
    from gate import anchor_chain
    from gate import db
    from gate import evidence_log
except ImportError:
    import anchor_chain
    import db
    import evidence_log

SPEC = "gate-seal-anchor-v1"
CADENCE_SECONDS = 15 * 60
OTS_CALENDARS = (
    "https://alice.btc.calendar.opentimestamps.org",
    "https://bob.btc.calendar.opentimestamps.org",
)

VERIFY_STEPS = [
    "Hash the receipt you were given — sha256 of its canonical JSON — and check it equals leaf_hash.",
    "Fold leaf_hash with siblings using sha256. At an even index hash(leaf || sibling); at an odd index hash(sibling || leaf). Then integer-divide the index by 2 and repeat. The digest must equal root_hash.",
    "Fetch published.locator from a public Base explorer for published.chain_id. Do not fetch it from this host. The transaction must have succeeded, and its SealRoot log data must be tree_size, root_hash, prev_root_hash in that order, each a 32-byte word.",
    "Rebuild the statement as JSON with sorted keys and no spaces: prev_root_hash, prev_tree_size, root_hash, spec, tree_size. sha256 of those bytes must equal published.statement_hash.",
    "If published.ots_locator is present, fetch it from the OpenTimestamps calendar. That URL is a Bitcoin time witness of statement_hash. The Base log is what makes a second root at the same tree size visible.",
    "On a later check, prev_root_hash must equal the root_hash you already accepted, and tree_size must be greater than or equal to the tree_size you already accepted.",
    "covers_latest_print is false when the newest print on the job is not in the last published root. Do not treat that print as anchored. A print with leaf_index null is not in that root either.",
]


def ensure_schema() -> None:
    with db.db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS seal_anchors (
                id TEXT PRIMARY KEY,
                tree_size INTEGER NOT NULL,
                root_hash TEXT NOT NULL,
                prev_tree_size INTEGER NOT NULL,
                prev_root_hash TEXT NOT NULL,
                statement_json TEXT NOT NULL,
                statement_hash TEXT NOT NULL,
                leaves_blob BLOB NOT NULL,
                chain_id INTEGER,
                l2_tx_hash TEXT,
                l2_contract TEXT,
                gas_limit INTEGER,
                max_fee_wei TEXT,
                ots_locator TEXT,
                ots_proof TEXT,
                ots_status TEXT,
                status TEXT NOT NULL,
                anchored_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_seal_anchors_status
                ON seal_anchors(status, tree_size);
            CREATE TABLE IF NOT EXISTS seal_anchor_leaves (
                leaf_index INTEGER PRIMARY KEY,
                receipt_hash TEXT NOT NULL,
                siblings_json TEXT NOT NULL,
                tree_size INTEGER NOT NULL,
                root_hash TEXT NOT NULL,
                anchor_id TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_seal_anchor_leaves_hash
                ON seal_anchor_leaves(receipt_hash);
            CREATE TABLE IF NOT EXISTS seal_anchor_meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )


def canonical_statement(*, tree_size: int, root_hash: str, prev_tree_size: int, prev_root_hash: str) -> tuple[str, str]:
    body = {
        "prev_root_hash": prev_root_hash,
        "prev_tree_size": prev_tree_size,
        "root_hash": root_hash,
        "spec": SPEC,
        "tree_size": tree_size,
    }
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(encoded.encode()).hexdigest()
    return encoded, digest


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    empty = evidence_log.EMPTY_LEAF.hex()
    return {
        "spec": SPEC,
        "cadence_seconds": CADENCE_SECONDS,
        "default_mode": "off",
        "process": "python3 seal_anchor.py — its own process. The web process does not publish.",
        "event": anchor_chain.EVENT_SIG,
        "event_topic": "0x" + anchor_chain.event_topic().hex(),
        "commit": anchor_chain.COMMIT_SIG,
        "empty_root": empty,
        "empty_root_preimage": "sha256(ascii gate-evidence-empty)",
        "chain_id": anchor_chain.BASE_CHAIN_ID,
        "test_chain_id": anchor_chain.BASE_SEPOLIA_CHAIN_ID,
        "explorers": {
            "base": "https://basescan.org/tx/",
            "base-sepolia": "https://sepolia.basescan.org/tx/",
        },
        "gas": {
            "memo_commit_gas": anchor_chain.MEMO_COMMIT_GAS,
            "commit_ceiling": anchor_chain.COMMIT_GAS_CEILING,
            "deploy_ceiling": anchor_chain.DEPLOY_GAS_CEILING,
            "max_fee_per_gas_wei_default": anchor_chain.DEFAULT_MAX_FEE_WEI,
        },
        "job": f"{base}/v1/seal/job?job_id=",
        "verify": VERIFY_STEPS,
        "spend": "Broadcast requires GATE_SEAL_ANCHOR_MODE=base or base-sepolia plus GATE_SEAL_ANCHOR_SPEND=1. Default mode is off.",
    }


def latest_broadcast() -> dict | None:
    ensure_schema()
    with db.db() as conn:
        row = conn.execute(
            """
            SELECT * FROM seal_anchors
            WHERE status = 'broadcast' AND l2_tx_hash IS NOT NULL
            ORDER BY tree_size DESC
            LIMIT 1
            """
        ).fetchone()
    return dict(row) if row else None


def annotate(body: dict[str, Any], rows: list[dict] | None) -> dict[str, Any]:
    """Attach cached inclusion data. Reads sqlite. Does not recompute the tree."""
    prints = body.get("prints") or []
    by_id = {r.get("id"): r for r in (rows or []) if r.get("id")}
    hashes: list[str] = []
    for print_row in prints:
        receipt_hash = (by_id.get(print_row.get("event_id")) or {}).get("receipt_hash")
        print_row["leaf_hash"] = receipt_hash
        print_row["leaf_index"] = None
        print_row["siblings"] = []
        if receipt_hash:
            hashes.append(receipt_hash)
    head = latest_broadcast()
    located = _leaves_for(hashes) if head and hashes else {}
    cursors: dict[str, int] = {}
    for print_row in prints:
        receipt_hash = print_row.get("leaf_hash")
        bucket = located.get(receipt_hash) or []
        cursor = cursors.get(receipt_hash, 0)
        if receipt_hash and cursor < len(bucket):
            found = bucket[cursor]
            cursors[receipt_hash] = cursor + 1
            print_row["leaf_index"] = found["leaf_index"]
            print_row["siblings"] = found["siblings"]
    body["anchor"] = _anchor_object(prints, head)
    return body


def run_once(*, mode: str | None = None, chain: Any = None, ots_submitter: Any = None) -> dict[str, Any]:
    selected = (mode if mode is not None else os.getenv("GATE_SEAL_ANCHOR_MODE", "off")).strip().lower()
    if selected in ("", "off", "0", "false"):
        return {"ok": True, "spec": SPEC, "status": "off", "cadence_seconds": CADENCE_SECONDS}
    db.init_db()
    ensure_schema()
    if selected == "dry_run":
        return _prepare(chain=None, ots_submitter=None, publish=False)
    if selected == "injected":
        if chain is None:
            return {"ok": False, "spec": SPEC, "status": "error", "error": "injected mode needs a chain"}
        return _prepare(chain=chain, ots_submitter=ots_submitter, publish=True)
    if selected in ("base", "base-sepolia"):
        if os.getenv("GATE_SEAL_ANCHOR_SPEND", "").strip() != "1":
            return {
                "ok": False,
                "spec": SPEC,
                "status": "spend_disabled",
                "error": "Set GATE_SEAL_ANCHOR_SPEND=1 to broadcast. Default is off.",
            }
        try:
            live = chain or _load_chain(selected)
        except Exception as exc:
            return {"ok": False, "spec": SPEC, "status": "error", "error": str(exc)}
        pending = _resume_deploy(live)
        if pending is not None:
            return pending
        return _prepare(chain=live, ots_submitter=ots_submitter or submit_ots, publish=True)
    return {"ok": False, "spec": SPEC, "status": "error", "error": f"unknown mode {selected}"}


def submit_ots(statement_hash: bytes) -> dict[str, Any]:
    last_error = "no calendar answered"
    for calendar in OTS_CALENDARS:
        request = urllib.request.Request(
            calendar + "/digest",
            data=statement_hash,
            headers={
                "Content-Type": "application/octet-stream",
                "Accept": "application/vnd.opentimestamps.v1",
                "User-Agent": "gate-seal-anchor/1",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                proof = response.read()
                status = getattr(response, "status", 200)
            if status != 200 or not proof:
                last_error = f"{calendar} status {status}"
                continue
            return {
                "status": "submitted",
                "locator": f"{calendar}/timestamp/{statement_hash.hex()}",
                "proof_hex": proof[:65536].hex(),
            }
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            last_error = str(exc)
    return {"status": "error", "locator": None, "error": last_error}


def _prepare(*, chain: Any, ots_submitter: Any, publish: bool) -> dict[str, Any]:
    resumed = _resume_pending(chain, ots_submitter) if publish and chain is not None else None
    rows = db.list_bind_events_chronological(limit=1_000_000)
    leaves = evidence_log.log_from_rows(rows)
    if resumed is not None and resumed.get("status") != "broadcast":
        return resumed
    if not leaves:
        return {"ok": True, "spec": SPEC, "status": "empty", "cadence_seconds": CADENCE_SECONDS}
    root = evidence_log.merkle_root(leaves)
    prev = latest_broadcast()
    prev_size = int(prev["tree_size"]) if prev else 0
    prev_root = prev["root_hash"] if prev else evidence_log.EMPTY_LEAF.hex()
    if prev and prev_size == len(leaves) and prev["root_hash"] == root:
        if resumed is not None and resumed.get("status") == "broadcast" and resumed.get("tree_size") == len(leaves):
            return resumed
        return {
            "ok": True,
            "spec": SPEC,
            "status": "skipped",
            "tree_size": len(leaves),
            "root_hash": root,
            "cadence_seconds": CADENCE_SECONDS,
        }
    if prev and prev_size > len(leaves):
        return _record_refusal(leaves, root, prev_size, prev_root, "tree_shrank")
    if not evidence_log.verify_consistency(
        old_size=prev_size,
        old_root=prev_root,
        new_root=root,
        leaf_hashes_hex=leaves,
    ):
        return _record_refusal(leaves, root, prev_size, prev_root, "not_an_append")
    encoded, statement_hash = canonical_statement(
        tree_size=len(leaves),
        root_hash=root,
        prev_tree_size=prev_size,
        prev_root_hash=prev_root,
    )
    blob = b"".join(bytes.fromhex(leaf) for leaf in leaves)
    if not publish:
        prior = _latest_with_status("dry_run")
        if prior and int(prior["tree_size"]) == len(leaves) and prior["root_hash"] == root:
            return {
                "ok": True,
                "spec": SPEC,
                "status": "skipped",
                "tree_size": len(leaves),
                "root_hash": root,
                "cadence_seconds": CADENCE_SECONDS,
            }
        _insert(
            {
                "tree_size": len(leaves),
                "root_hash": root,
                "prev_tree_size": prev_size,
                "prev_root_hash": prev_root,
                "statement_json": encoded,
                "statement_hash": statement_hash,
                "leaves_blob": blob,
                "status": "dry_run",
                "ots_status": "skipped",
            }
        )
        return {
            "ok": True,
            "spec": SPEC,
            "status": "dry_run",
            "tree_size": len(leaves),
            "root_hash": root,
            "prev_tree_size": prev_size,
            "prev_root_hash": prev_root,
            "statement_hash": statement_hash,
            "cadence_seconds": CADENCE_SECONDS,
        }
    root_b = bytes.fromhex(root)
    prev_b = bytes.fromhex(prev_root)
    calldata = anchor_chain.encode_commit(len(leaves), root_b, prev_b)
    static_gas = anchor_chain.commit_gas(len(leaves), root_b, prev_b)
    try:
        plan = _fee_plan(chain)
    except Exception as exc:
        return {"ok": False, "spec": SPEC, "status": "error", "error": str(exc)}
    if plan is None:
        _insert(
            {
                "tree_size": len(leaves),
                "root_hash": root,
                "prev_tree_size": prev_size,
                "prev_root_hash": prev_root,
                "statement_json": encoded,
                "statement_hash": statement_hash,
                "leaves_blob": b"",
                "status": "fee_capped",
                "chain_id": getattr(chain, "chain_id", None),
            }
        )
        return {
            "ok": True,
            "spec": SPEC,
            "status": "fee_capped",
            "tree_size": len(leaves),
            "static_gas": static_gas,
            "cadence_seconds": CADENCE_SECONDS,
        }
    try:
        remote_gas = int(chain.estimate_commit(calldata))
    except Exception as exc:
        return {"ok": False, "spec": SPEC, "status": "error", "error": str(exc), "static_gas": static_gas}
    if static_gas > anchor_chain.COMMIT_GAS_CEILING or remote_gas > anchor_chain.COMMIT_GAS_CEILING:
        return {
            "ok": False,
            "spec": SPEC,
            "status": "gas_above_memo",
            "static_gas": static_gas,
            "remote_gas": remote_gas,
            "ceiling": anchor_chain.COMMIT_GAS_CEILING,
        }
    gas_limit = min(anchor_chain.COMMIT_GAS_CEILING, max(static_gas, remote_gas) + 2_000)
    try:
        tx_hash = chain.broadcast_commit(calldata, gas_limit, plan["max_fee"], plan["priority"])
    except Exception as exc:
        return {"ok": False, "spec": SPEC, "status": "error", "error": str(exc)}
    anchor_id = _insert(
        {
            "tree_size": len(leaves),
            "root_hash": root,
            "prev_tree_size": prev_size,
            "prev_root_hash": prev_root,
            "statement_json": encoded,
            "statement_hash": statement_hash,
            "leaves_blob": blob,
            "chain_id": getattr(chain, "chain_id", None),
            "l2_tx_hash": tx_hash,
            "l2_contract": getattr(chain, "contract", None),
            "gas_limit": gas_limit,
            "max_fee_wei": str(plan["max_fee"]),
            "status": "pending",
        }
    )
    return _finish_pending(anchor_id, chain, ots_submitter, static_gas=static_gas, remote_gas=remote_gas)


def _finish_pending(anchor_id: str, chain: Any, ots_submitter: Any, *, static_gas: int | None = None, remote_gas: int | None = None) -> dict[str, Any]:
    row = _row(anchor_id)
    if row is None:
        return {"ok": False, "spec": SPEC, "status": "error", "error": "pending anchor missing"}
    try:
        status = chain.receipt_status(row["l2_tx_hash"])
    except Exception as exc:
        return {"ok": False, "spec": SPEC, "status": "error", "error": str(exc), "l2_tx_hash": row["l2_tx_hash"]}
    if status is None:
        return {
            "ok": True,
            "spec": SPEC,
            "status": "pending",
            "l2_tx_hash": row["l2_tx_hash"],
            "tree_size": row["tree_size"],
            "statement_hash": row["statement_hash"],
            "cadence_seconds": CADENCE_SECONDS,
        }
    if status != 1:
        _set_status(anchor_id, "failed")
        return {"ok": False, "spec": SPEC, "status": "failed", "l2_tx_hash": row["l2_tx_hash"]}
    ots = {"status": "skipped", "locator": None, "proof_hex": None}
    if ots_submitter is not None and not row.get("ots_locator"):
        try:
            ots = ots_submitter(bytes.fromhex(row["statement_hash"])) or ots
        except Exception as exc:
            ots = {"status": "error", "locator": None, "error": str(exc)}
    elif row.get("ots_locator"):
        ots = {"status": row.get("ots_status") or "submitted", "locator": row.get("ots_locator"), "proof_hex": row.get("ots_proof")}
    _promote(row, ots)
    return {
        "ok": True,
        "spec": SPEC,
        "status": "broadcast",
        "tree_size": row["tree_size"],
        "root_hash": row["root_hash"],
        "prev_tree_size": row["prev_tree_size"],
        "prev_root_hash": row["prev_root_hash"],
        "statement_hash": row["statement_hash"],
        "l2_tx_hash": row["l2_tx_hash"],
        "ots_locator": ots.get("locator"),
        "ots_status": ots.get("status"),
        "gas_limit": row.get("gas_limit"),
        "static_gas": static_gas,
        "remote_gas": remote_gas,
        "cadence_seconds": CADENCE_SECONDS,
    }


def _resume_pending(chain: Any, ots_submitter: Any) -> dict[str, Any] | None:
    ensure_schema()
    with db.db() as conn:
        row = conn.execute(
            "SELECT id FROM seal_anchors WHERE status = 'pending' ORDER BY anchored_at DESC LIMIT 1"
        ).fetchone()
    if not row:
        return None
    submitter = ots_submitter if ots_submitter is not None else (submit_ots if _ots_enabled() else None)
    return _finish_pending(row["id"], chain, submitter)


def _promote(row: dict, ots: dict) -> None:
    leaves = _blob_leaves(row.get("leaves_blob") or b"")
    root = evidence_log.merkle_root(leaves)
    if root != row["root_hash"]:
        _set_status(row["id"], "corrupt")
        raise RuntimeError("anchored leaves do not hash to the stored root")
    proofs = evidence_log.inclusion_proofs(leaves)
    with db.db() as conn:
        conn.execute("DELETE FROM seal_anchor_leaves")
        conn.executemany(
            """
            INSERT INTO seal_anchor_leaves
                (leaf_index, receipt_hash, siblings_json, tree_size, root_hash, anchor_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    proof["index"],
                    proof["leaf_hash"],
                    json.dumps(proof["siblings"]),
                    proof["tree_size"],
                    proof["root_hash"],
                    row["id"],
                )
                for proof in proofs
            ],
        )
        conn.execute(
            """
            UPDATE seal_anchors
            SET status = 'broadcast', ots_locator = ?, ots_proof = ?, ots_status = ?
            WHERE id = ?
            """,
            (ots.get("locator"), ots.get("proof_hex"), ots.get("status"), row["id"]),
        )


def _record_refusal(leaves: list[str], root: str, prev_size: int, prev_root: str, reason: str) -> dict[str, Any]:
    encoded, statement_hash = canonical_statement(
        tree_size=len(leaves),
        root_hash=root,
        prev_tree_size=prev_size,
        prev_root_hash=prev_root,
    )
    _insert(
        {
            "tree_size": len(leaves),
            "root_hash": root,
            "prev_tree_size": prev_size,
            "prev_root_hash": prev_root,
            "statement_json": encoded,
            "statement_hash": statement_hash,
            "leaves_blob": b"",
            "status": "refused",
            "ots_status": reason,
        }
    )
    return {
        "ok": False,
        "spec": SPEC,
        "status": "refused",
        "reason": reason,
        "tree_size": len(leaves),
        "root_hash": root,
        "prev_tree_size": prev_size,
        "prev_root_hash": prev_root,
    }


def _fee_plan(chain: Any) -> dict[str, int] | None:
    cap = int(os.getenv("GATE_SEAL_ANCHOR_MAX_FEE_WEI", str(anchor_chain.DEFAULT_MAX_FEE_WEI)))
    base = int(chain.base_fee_wei())
    if base > cap:
        return None
    priority = min(anchor_chain.DEFAULT_PRIORITY_WEI, cap - base)
    max_fee = min(cap, base * 2 + priority)
    if max_fee < base:
        return None
    return {"base": base, "priority": priority, "max_fee": max_fee}


def _insert(fields: dict) -> str:
    anchor_id = str(uuid.uuid4())
    now = db.utc_now()
    with db.db() as conn:
        conn.execute(
            """
            INSERT INTO seal_anchors (
                id, tree_size, root_hash, prev_tree_size, prev_root_hash,
                statement_json, statement_hash, leaves_blob, chain_id, l2_tx_hash,
                l2_contract, gas_limit, max_fee_wei, ots_locator, ots_proof, ots_status,
                status, anchored_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                anchor_id,
                fields["tree_size"],
                fields["root_hash"],
                fields["prev_tree_size"],
                fields["prev_root_hash"],
                fields["statement_json"],
                fields["statement_hash"],
                fields.get("leaves_blob") or b"",
                fields.get("chain_id"),
                fields.get("l2_tx_hash"),
                fields.get("l2_contract"),
                fields.get("gas_limit"),
                fields.get("max_fee_wei"),
                fields.get("ots_locator"),
                fields.get("ots_proof"),
                fields.get("ots_status"),
                fields["status"],
                now,
            ),
        )
    return anchor_id


def _latest_with_status(status: str) -> dict | None:
    with db.db() as conn:
        row = conn.execute(
            """
            SELECT * FROM seal_anchors
            WHERE status = ?
            ORDER BY tree_size DESC, anchored_at DESC
            LIMIT 1
            """,
            (status,),
        ).fetchone()
    return dict(row) if row else None


def _row(anchor_id: str) -> dict | None:
    with db.db() as conn:
        row = conn.execute("SELECT * FROM seal_anchors WHERE id = ?", (anchor_id,)).fetchone()
    return dict(row) if row else None


def _set_status(anchor_id: str, status: str) -> None:
    with db.db() as conn:
        conn.execute("UPDATE seal_anchors SET status = ? WHERE id = ?", (status, anchor_id))


def _leaves_for(hashes: list[str]) -> dict[str, list[dict]]:
    if not hashes:
        return {}
    ensure_schema()
    unique = list(dict.fromkeys(hashes))
    placeholders = ",".join("?" for _ in unique)
    with db.db() as conn:
        rows = conn.execute(
            f"""
            SELECT leaf_index, receipt_hash, siblings_json
            FROM seal_anchor_leaves
            WHERE receipt_hash IN ({placeholders})
            ORDER BY leaf_index ASC
            """,
            unique,
        ).fetchall()
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        grouped.setdefault(row["receipt_hash"], []).append(
            {"leaf_index": row["leaf_index"], "siblings": json.loads(row["siblings_json"])}
        )
    return grouped


def _anchor_object(prints: list[dict], head: dict | None) -> dict[str, Any]:
    covered = [item for item in prints if item.get("leaf_index") is not None]
    latest_covered = bool(prints) and prints[-1].get("leaf_index") is not None
    proved = prints[-1] if latest_covered else (covered[-1] if covered else None)
    published = None
    if head and head.get("l2_tx_hash"):
        published = {
            "target": _target_name(head.get("chain_id")),
            "locator": head["l2_tx_hash"],
            "statement_hash": head["statement_hash"],
            "anchored_at": head["anchored_at"],
            "chain_id": head.get("chain_id"),
            "contract": head.get("l2_contract"),
            "ots_locator": head.get("ots_locator"),
            "ots_status": head.get("ots_status"),
        }
    return {
        "spec": SPEC,
        "leaf_hash": None if proved is None else proved.get("leaf_hash"),
        "leaf_index": None if proved is None else proved.get("leaf_index"),
        "tree_size": None if head is None else head["tree_size"],
        "root_hash": None if head is None else head["root_hash"],
        "siblings": [] if proved is None else list(proved.get("siblings") or []),
        "prev_tree_size": None if head is None else head["prev_tree_size"],
        "prev_root_hash": None if head is None else head["prev_root_hash"],
        "covers_latest_print": latest_covered,
        "published": published,
    }


def _target_name(chain_id: int | None) -> str:
    if chain_id == anchor_chain.BASE_CHAIN_ID:
        return "base"
    if chain_id == anchor_chain.BASE_SEPOLIA_CHAIN_ID:
        return "base-sepolia"
    return "base"


def _blob_leaves(blob: bytes) -> list[str]:
    raw = bytes(blob or b"")
    if len(raw) % 32:
        raise ValueError("leaf blob")
    return [raw[i : i + 32].hex() for i in range(0, len(raw), 32)]


def _ots_enabled() -> bool:
    return os.getenv("GATE_SEAL_ANCHOR_OTS", "1").strip() != "0"


def _meta_get(key: str) -> str | None:
    ensure_schema()
    with db.db() as conn:
        row = conn.execute("SELECT value FROM seal_anchor_meta WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else None


def _meta_set(key: str, value: str) -> None:
    ensure_schema()
    with db.db() as conn:
        conn.execute(
            "INSERT INTO seal_anchor_meta (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )


def _load_chain(selected: str) -> Any:
    key_text = os.getenv("GATE_SEAL_ANCHOR_PRIVATE_KEY", "")
    if not key_text.strip():
        raise RuntimeError("GATE_SEAL_ANCHOR_PRIVATE_KEY missing")
    private_key = anchor_chain.parse_private_key(key_text)
    if selected == "base":
        chain_id = anchor_chain.BASE_CHAIN_ID
        rpc = os.getenv("GATE_SEAL_ANCHOR_RPC_URL") or anchor_chain.BASE_RPC
    else:
        chain_id = anchor_chain.BASE_SEPOLIA_CHAIN_ID
        rpc = os.getenv("GATE_SEAL_ANCHOR_RPC_URL") or anchor_chain.BASE_SEPOLIA_RPC
    contract = (os.getenv("GATE_SEAL_ANCHOR_CONTRACT") or "").strip() or _meta_get(f"contract:{chain_id}")
    return anchor_chain.BaseAnchor(
        chain_id=chain_id,
        rpc_url=rpc,
        private_key=private_key,
        contract=contract,
    )


def _resume_deploy(chain: Any) -> dict[str, Any] | None:
    """Finish or start contract deployment. None means a contract is ready."""
    if getattr(chain, "contract", None):
        return None
    chain_id = chain.chain_id
    stored = _meta_get(f"contract:{chain_id}")
    if stored:
        chain.contract = stored
        return None
    deploy_tx = _meta_get(f"deploy_tx:{chain_id}")
    if deploy_tx:
        status = chain.receipt_status(deploy_tx)
        if status is None:
            return {"ok": True, "spec": SPEC, "status": "deploy_pending", "l2_tx_hash": deploy_tx}
        if status != 1:
            _meta_set(f"deploy_tx:{chain_id}", "")
            return {"ok": False, "spec": SPEC, "status": "deploy_failed", "l2_tx_hash": deploy_tx}
        address = chain.receipt_contract(deploy_tx)
        if not address:
            return {"ok": False, "spec": SPEC, "status": "deploy_failed", "l2_tx_hash": deploy_tx}
        _meta_set(f"contract:{chain_id}", address)
        chain.contract = address
        return None
    plan = _fee_plan(chain)
    if plan is None:
        return {"ok": True, "spec": SPEC, "status": "fee_capped", "phase": "deploy"}
    remote = chain.estimate_deploy()
    if remote > anchor_chain.DEPLOY_GAS_CEILING:
        return {
            "ok": False,
            "spec": SPEC,
            "status": "gas_above_memo",
            "phase": "deploy",
            "remote_gas": remote,
            "ceiling": anchor_chain.DEPLOY_GAS_CEILING,
        }
    tx_hash = chain.deploy(remote, plan["max_fee"], plan["priority"])
    _meta_set(f"deploy_tx:{chain_id}", tx_hash)
    status = chain.receipt_status(tx_hash)
    if status is None:
        return {"ok": True, "spec": SPEC, "status": "deploy_pending", "l2_tx_hash": tx_hash}
    if status != 1:
        return {"ok": False, "spec": SPEC, "status": "deploy_failed", "l2_tx_hash": tx_hash}
    address = chain.receipt_contract(tx_hash)
    if not address:
        return {"ok": False, "spec": SPEC, "status": "deploy_failed", "l2_tx_hash": tx_hash}
    _meta_set(f"contract:{chain_id}", address)
    chain.contract = address
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish the Gate seal Merkle root. Default mode is off.")
    parser.add_argument("--loop", action="store_true", help="Run every 15 minutes in this process")
    parser.add_argument("--estimate", action="store_true", help="Estimate commit gas on Base Sepolia. Does not spend.")
    parser.add_argument("--mode", default=None, help="off, dry_run, base-sepolia, or base")
    args = parser.parse_args()
    if args.estimate:
        print(json.dumps(anchor_chain.estimate_commit_remote(), indent=2))
        return
    if not args.loop:
        result = run_once(mode=args.mode)
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if result.get("ok") else 2)
    while True:
        started = time.monotonic()
        try:
            result = run_once(mode=args.mode)
        except Exception as exc:
            result = {"ok": False, "spec": SPEC, "status": "error", "error": str(exc)}
        print(json.dumps(result), flush=True)
        remaining = CADENCE_SECONDS - (time.monotonic() - started)
        if remaining > 0:
            time.sleep(remaining)


if __name__ == "__main__":
    main()
