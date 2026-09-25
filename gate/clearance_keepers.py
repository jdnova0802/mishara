"""Clearance keepers — Gate-shaped mining on foreign vaults.

Bitcoin: hash until the protocol pays you.
Gate: watch vault-locked escrow until breach — Never/NO_GO prove — liquidate — bounty.

Atoms: VAULT (not Gate) · MANDATE · CLEAR/NEVER · KEEPER · BOUNTY(from vault).
Demo ledger is index-only — not real money. Massive ingress = on-chain USDC /
Issuing / sponsor vault that accepts Gate execution packets.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import threading
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

try:
    from gate import prefinality as prefinality_mod
except ImportError:
    import prefinality as prefinality_mod

try:
    from gate import foreign_custody as custody_mod
except ImportError:
    import foreign_custody as custody_mod

SPEC = "gate-clearance-keepers-v1"
DEFAULT_BOUNTY_BPS = 500  # 5% of escrow residual to first correct keeper
DEFAULT_TTL_SECONDS = 86_400
MIN_ESCROW_UNITS = 1  # micro-units (1e6 = 1.00)
SCALE = 1_000_000

_LOCK = threading.Lock()

STATUSES = ("OPEN", "BREACHED", "LIQUIDATED", "RELEASED", "EXPIRED")


def _db_path() -> str:
    base = os.getenv("GATE_DB_PATH", "").strip()
    if base:
        if base.endswith(".db"):
            return base[:-3] + ".keepers.db"
        return base + ".keepers.db"
    return os.path.join("/tmp", "gate-clearance-keepers.db")


def _conn() -> sqlite3.Connection:
    path = _db_path()
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    c = sqlite3.connect(path, check_same_thread=False, timeout=30)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS clearance_positions (
            id TEXT PRIMARY KEY,
            principal_id TEXT NOT NULL,
            agent_id TEXT,
            rail TEXT NOT NULL,
            mandate_json TEXT NOT NULL,
            escrow_units INTEGER NOT NULL,
            bounty_bps INTEGER NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            residual_units INTEGER,
            meta_json TEXT,
            custody_json TEXT
        )
        """
    )
    cols = {row[1] for row in c.execute("PRAGMA table_info(clearance_positions)").fetchall()}
    if "custody_json" not in cols:
        c.execute("ALTER TABLE clearance_positions ADD COLUMN custody_json TEXT")
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS clearance_observations (
            id TEXT PRIMARY KEY,
            position_id TEXT NOT NULL,
            transfer_json TEXT NOT NULL,
            fingerprint TEXT NOT NULL,
            decision TEXT NOT NULL,
            signals_json TEXT NOT NULL,
            executed INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (position_id) REFERENCES clearance_positions(id)
        )
        """
    )
    c.execute(
        "CREATE INDEX IF NOT EXISTS idx_ck_obs_pos ON clearance_observations(position_id)"
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS clearance_liquidations (
            id TEXT PRIMARY KEY,
            position_id TEXT NOT NULL UNIQUE,
            keeper_id TEXT NOT NULL,
            observation_id TEXT NOT NULL,
            bounty_units INTEGER NOT NULL,
            residual_to_principal_units INTEGER NOT NULL,
            evidence_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (position_id) REFERENCES clearance_positions(id)
        )
        """
    )
    return c


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat()


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def units_from_amount(amount: str | float | int | None) -> int | None:
    if amount is None:
        return None
    try:
        v = float(str(amount).strip())
    except (TypeError, ValueError):
        return None
    if v < 0:
        return None
    return int(round(v * SCALE))


def amount_from_units(units: int | None) -> str:
    if units is None:
        return "0"
    return f"{units / SCALE:.6f}".rstrip("0").rstrip(".") or "0"


def _row_position(row: sqlite3.Row) -> dict[str, Any]:
    mandate = json.loads(row["mandate_json"] or "{}")
    meta = json.loads(row["meta_json"] or "null")
    custody_raw = None
    try:
        custody_raw = json.loads(row["custody_json"] or "null")
    except (TypeError, KeyError, json.JSONDecodeError):
        custody_raw = None
    if not isinstance(custody_raw, dict):
        custody_raw = custody_mod.normalize_custody(
            None, escrow_units=int(row["escrow_units"])
        )
    return {
        "spec": SPEC,
        "position_id": row["id"],
        "principal_id": row["principal_id"],
        "agent_id": row["agent_id"],
        "rail": row["rail"],
        "mandate": mandate,
        "escrow": amount_from_units(row["escrow_units"]),
        "escrow_units": row["escrow_units"],
        "bounty_bps": row["bounty_bps"],
        "status": row["status"],
        "created_at": row["created_at"],
        "expires_at": row["expires_at"],
        "residual": amount_from_units(row["residual_units"])
        if row["residual_units"] is not None
        else None,
        "custody": custody_raw,
        "money_real": bool(custody_raw.get("money_real")),
        "gate_holds_funds": False,
        "meta": meta,
        "their_production": False,
    }


def _expire_if_needed(c: sqlite3.Connection, row: sqlite3.Row) -> sqlite3.Row:
    if row["status"] not in ("OPEN", "BREACHED"):
        return row
    now = _iso(_utc_now())
    if row["expires_at"] <= now:
        c.execute(
            "UPDATE clearance_positions SET status=? WHERE id=? AND status IN ('OPEN','BREACHED')",
            ("EXPIRED", row["id"]),
        )
        c.commit()
        refreshed = c.execute(
            "SELECT * FROM clearance_positions WHERE id=?", (row["id"],)
        ).fetchone()
        return refreshed or row
    return row


def evaluate_breach(*, rail: str, transfer: dict, mandate: dict) -> dict[str, Any]:
    """Reuse prefinality policy as the hash — Gate Clear/Never DNA."""
    decision, signals = prefinality_mod._policy_signals(
        rail=rail,
        transfer=transfer if isinstance(transfer, dict) else {},
        mandate=mandate if isinstance(mandate, dict) else {},
        context={},
    )
    fingerprint = prefinality_mod.transfer_fingerprint(
        rail=rail,
        transfer=transfer if isinstance(transfer, dict) else {},
    )
    liquidatable = decision in ("NO_GO", "HOLD")
    return {
        "decision": decision,
        "signals": list(signals),
        "fingerprint": fingerprint,
        "liquidatable": liquidatable,
        "word": "NO GO" if decision == "NO_GO" else ("HOLD" if decision == "HOLD" else "GO"),
    }


def open_position(
    *,
    principal_id: str,
    escrow_amount: str | float,
    mandate: dict,
    rail: str = "x402",
    agent_id: str | None = None,
    bounty_bps: int | None = None,
    ttl_seconds: int | None = None,
    meta: dict | None = None,
    custody: dict | None = None,
) -> dict[str, Any]:
    principal = (principal_id or "").strip()
    if not principal:
        return {"ok": False, "error": "principal_id_required", "spec": SPEC}
    rail_n = (rail or "x402").strip().lower()
    if rail_n not in prefinality_mod.RAILS:
        return {"ok": False, "error": "unsupported_rail", "spec": SPEC, "rails": list(prefinality_mod.RAILS)}
    units = units_from_amount(escrow_amount)
    if units is None or units < MIN_ESCROW_UNITS:
        return {"ok": False, "error": "invalid_escrow", "spec": SPEC}
    bps = int(bounty_bps if bounty_bps is not None else DEFAULT_BOUNTY_BPS)
    if bps < 0 or bps > 10_000:
        return {"ok": False, "error": "invalid_bounty_bps", "spec": SPEC}
    ttl = int(ttl_seconds if ttl_seconds is not None else DEFAULT_TTL_SECONDS)
    if ttl < 60 or ttl > 30 * 86_400:
        return {"ok": False, "error": "invalid_ttl", "spec": SPEC}
    mand = mandate if isinstance(mandate, dict) else {}
    if not mand:
        return {"ok": False, "error": "mandate_required", "spec": SPEC}
    aid = (agent_id or mand.get("agent_id") or "").strip() or None
    custody_binding = custody_mod.normalize_custody(custody, escrow_units=units)
    now = _utc_now()
    position_id = "ck_" + uuid.uuid4().hex[:20]
    created = _iso(now)
    expires = _iso(now + timedelta(seconds=ttl))
    with _LOCK:
        c = _conn()
        try:
            c.execute(
                """INSERT INTO clearance_positions
                   (id, principal_id, agent_id, rail, mandate_json, escrow_units,
                    bounty_bps, status, created_at, expires_at, residual_units,
                    meta_json, custody_json)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    position_id,
                    principal,
                    aid,
                    rail_n,
                    _canonical(mand),
                    units,
                    bps,
                    "OPEN",
                    created,
                    expires,
                    None,
                    _canonical(meta) if meta is not None else None,
                    _canonical(custody_binding),
                ),
            )
            c.commit()
            row = c.execute(
                "SELECT * FROM clearance_positions WHERE id=?", (position_id,)
            ).fetchone()
        finally:
            c.close()
    pos = _row_position(row)
    return {
        "ok": True,
        "spec": SPEC,
        "position": pos,
        "money_real": pos["money_real"],
        "gate_holds_funds": False,
        "mining": {
            "hash": "Clear/Never over mandate",
            "reward": "first correct liquidate() wins bounty_bps of residual",
            "payer": (
                "foreign vault (real USDC/bank)"
                if pos["money_real"]
                else "demo ledger only — not real money"
            ),
            "vault": custody_binding.get("venue"),
        },
        "their_production": False,
    }


def get_position(position_id: str) -> dict[str, Any] | None:
    pid = (position_id or "").strip()
    if not pid:
        return None
    with _LOCK:
        c = _conn()
        try:
            row = c.execute(
                "SELECT * FROM clearance_positions WHERE id=?", (pid,)
            ).fetchone()
            if not row:
                return None
            row = _expire_if_needed(c, row)
            return _row_position(row)
        finally:
            c.close()


def observe(
    *,
    position_id: str,
    transfer: dict,
    executed: bool = True,
) -> dict[str, Any]:
    """Index an observed agent transfer against an open escrow mandate."""
    pid = (position_id or "").strip()
    if not pid:
        return {"ok": False, "error": "position_id_required", "spec": SPEC}
    if not isinstance(transfer, dict) or not transfer:
        return {"ok": False, "error": "transfer_required", "spec": SPEC}
    with _LOCK:
        c = _conn()
        try:
            row = c.execute(
                "SELECT * FROM clearance_positions WHERE id=?", (pid,)
            ).fetchone()
            if not row:
                return {"ok": False, "error": "position_not_found", "spec": SPEC}
            row = _expire_if_needed(c, row)
            if row["status"] not in ("OPEN", "BREACHED"):
                return {
                    "ok": False,
                    "error": "position_not_open",
                    "status": row["status"],
                    "spec": SPEC,
                }
            mandate = json.loads(row["mandate_json"] or "{}")
            verdict = evaluate_breach(
                rail=row["rail"], transfer=transfer, mandate=mandate
            )
            obs_id = "obs_" + uuid.uuid4().hex[:18]
            created = _iso(_utc_now())
            c.execute(
                """INSERT INTO clearance_observations
                   (id, position_id, transfer_json, fingerprint, decision,
                    signals_json, executed, created_at)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (
                    obs_id,
                    pid,
                    _canonical(transfer),
                    verdict["fingerprint"],
                    verdict["decision"],
                    _canonical(verdict["signals"]),
                    1 if executed else 0,
                    created,
                ),
            )
            # Breach = would-have-been NO_GO/HOLD *and* the spend was (or is being) executed.
            if verdict["liquidatable"] and executed and row["status"] == "OPEN":
                c.execute(
                    "UPDATE clearance_positions SET status=? WHERE id=? AND status=?",
                    ("BREACHED", pid, "OPEN"),
                )
            c.commit()
            pos = _row_position(
                c.execute(
                    "SELECT * FROM clearance_positions WHERE id=?", (pid,)
                ).fetchone()
            )
        finally:
            c.close()
    return {
        "ok": True,
        "spec": SPEC,
        "observation_id": obs_id,
        "verdict": verdict,
        "position": pos,
        "liquidatable": bool(
            verdict["liquidatable"] and executed and pos["status"] in ("BREACHED", "OPEN")
        ),
        "their_production": False,
    }


def _latest_breach_observation(c: sqlite3.Connection, position_id: str) -> sqlite3.Row | None:
    return c.execute(
        """SELECT * FROM clearance_observations
           WHERE position_id=? AND decision IN ('NO_GO','HOLD') AND executed=1
           ORDER BY created_at DESC LIMIT 1""",
        (position_id,),
    ).fetchone()


def scan(*, limit: int = 50) -> dict[str, Any]:
    """Permissionless mempool: positions a keeper can liquidate."""
    lim = max(1, min(int(limit or 50), 200))
    with _LOCK:
        c = _conn()
        try:
            rows = c.execute(
                """SELECT * FROM clearance_positions
                   WHERE status IN ('OPEN','BREACHED')
                   ORDER BY created_at ASC"""
            ).fetchall()
            out = []
            for row in rows:
                row = _expire_if_needed(c, row)
                if row["status"] not in ("OPEN", "BREACHED"):
                    continue
                obs = _latest_breach_observation(c, row["id"])
                if not obs:
                    continue
                bounty = (int(row["escrow_units"]) * int(row["bounty_bps"])) // 10_000
                out.append(
                    {
                        "position_id": row["id"],
                        "status": row["status"],
                        "rail": row["rail"],
                        "escrow": amount_from_units(row["escrow_units"]),
                        "bounty": amount_from_units(bounty),
                        "bounty_bps": row["bounty_bps"],
                        "agent_id": row["agent_id"],
                        "observation_id": obs["id"],
                        "decision": obs["decision"],
                        "signals": json.loads(obs["signals_json"] or "[]"),
                        "fingerprint": obs["fingerprint"],
                        "expires_at": row["expires_at"],
                    }
                )
                if len(out) >= lim:
                    break
        finally:
            c.close()
    return {
        "spec": SPEC,
        "count": len(out),
        "liquidatable": out,
        "plain": "First correct liquidate() wins. Same race as mining a block.",
        "their_production": False,
    }


def liquidate(
    *,
    position_id: str,
    keeper_id: str,
    observation_id: str | None = None,
) -> dict[str, Any]:
    """Permissionless reclaim. First correct keeper wins the bounty."""
    pid = (position_id or "").strip()
    kid = (keeper_id or "").strip()
    if not pid:
        return {"ok": False, "error": "position_id_required", "spec": SPEC}
    if not kid:
        return {"ok": False, "error": "keeper_id_required", "spec": SPEC}
    with _LOCK:
        c = _conn()
        try:
            existing = c.execute(
                "SELECT * FROM clearance_liquidations WHERE position_id=?", (pid,)
            ).fetchone()
            if existing:
                return {
                    "ok": False,
                    "error": "already_liquidated",
                    "winner": existing["keeper_id"],
                    "liquidation_id": existing["id"],
                    "spec": SPEC,
                }
            row = c.execute(
                "SELECT * FROM clearance_positions WHERE id=?", (pid,)
            ).fetchone()
            if not row:
                return {"ok": False, "error": "position_not_found", "spec": SPEC}
            row = _expire_if_needed(c, row)
            if row["status"] == "LIQUIDATED":
                return {"ok": False, "error": "already_liquidated", "spec": SPEC}
            if row["status"] not in ("OPEN", "BREACHED"):
                return {
                    "ok": False,
                    "error": "not_liquidatable",
                    "status": row["status"],
                    "spec": SPEC,
                }
            oid = (observation_id or "").strip()
            if oid:
                obs = c.execute(
                    """SELECT * FROM clearance_observations
                       WHERE id=? AND position_id=?""",
                    (oid, pid),
                ).fetchone()
            else:
                obs = _latest_breach_observation(c, pid)
            if not obs:
                return {
                    "ok": False,
                    "error": "no_breach_evidence",
                    "plain": "Observe a mandate-breaking executed transfer first.",
                    "spec": SPEC,
                }
            if obs["decision"] not in ("NO_GO", "HOLD") or not obs["executed"]:
                return {"ok": False, "error": "observation_not_breach", "spec": SPEC}

            escrow = int(row["escrow_units"])
            bounty = (escrow * int(row["bounty_bps"])) // 10_000
            residual = escrow - bounty
            try:
                custody = json.loads(row["custody_json"] or "null")
            except (TypeError, KeyError, json.JSONDecodeError):
                custody = None
            if not isinstance(custody, dict):
                custody = custody_mod.normalize_custody(None, escrow_units=escrow)
            evidence = {
                "spec": SPEC,
                "type": "mandate_breach_liquidation",
                "claim": "agent_executed_transfer_that_clear_would_have_blocked",
                "decision": obs["decision"],
                "signals": json.loads(obs["signals_json"] or "[]"),
                "fingerprint": obs["fingerprint"],
                "transfer": json.loads(obs["transfer_json"] or "{}"),
                "mandate": json.loads(row["mandate_json"] or "{}"),
                "never_shaped": True,
                "word": "NEVER should have cleared — liquidated",
                "money_real": bool(custody.get("money_real")),
                "gate_holds_funds": False,
            }
            evidence_hash = hashlib.sha256(
                _canonical(evidence).encode("utf-8")
            ).hexdigest()
            evidence["evidence_hash"] = evidence_hash

            liq_id = "liq_" + uuid.uuid4().hex[:18]
            created = _iso(_utc_now())
            try:
                c.execute(
                    """INSERT INTO clearance_liquidations
                       (id, position_id, keeper_id, observation_id, bounty_units,
                        residual_to_principal_units, evidence_json, created_at)
                       VALUES (?,?,?,?,?,?,?,?)""",
                    (
                        liq_id,
                        pid,
                        kid,
                        obs["id"],
                        bounty,
                        residual,
                        _canonical(evidence),
                        created,
                    ),
                )
            except sqlite3.IntegrityError:
                winner = c.execute(
                    "SELECT keeper_id, id FROM clearance_liquidations WHERE position_id=?",
                    (pid,),
                ).fetchone()
                return {
                    "ok": False,
                    "error": "already_liquidated",
                    "winner": winner["keeper_id"] if winner else None,
                    "liquidation_id": winner["id"] if winner else None,
                    "spec": SPEC,
                }
            c.execute(
                """UPDATE clearance_positions
                   SET status=?, residual_units=?
                   WHERE id=?""",
                ("LIQUIDATED", residual, pid),
            )
            c.commit()
            pos = _row_position(
                c.execute(
                    "SELECT * FROM clearance_positions WHERE id=?", (pid,)
                ).fetchone()
            )
        finally:
            c.close()
    packet = custody_mod.execution_packet(
        custody=custody,
        position_id=pid,
        keeper_id=kid,
        bounty_units=bounty,
        residual_units=residual,
        evidence=evidence,
    )
    onchain = None
    if custody.get("venue") == custody_mod.VENUE_ONCHAIN_USDC:
        onchain = custody_mod.onchain_liquidate_calldata(packet)
    return {
        "ok": True,
        "spec": SPEC,
        "word": "LIQUIDATED",
        "plain": (
            "Breach proven. Foreign vault must pay the keeper."
            if pos["money_real"]
            else "Breach proven on demo ledger only — bounty is not real money."
        ),
        "liquidation_id": liq_id,
        "keeper_id": kid,
        "bounty": amount_from_units(bounty),
        "bounty_units": bounty,
        "residual_to_principal": amount_from_units(residual),
        "evidence": evidence,
        "execution_packet": packet,
        "onchain_call": onchain,
        "money_real": pos["money_real"],
        "gate_holds_funds": False,
        "position": pos,
        "mining": {
            "analogy": "block found",
            "payer": "foreign vault" if pos["money_real"] else "demo_ledger",
            "competition": "other keepers — first correct tx wins",
        },
        "their_production": False,
    }


def release_on_clear(
    *,
    position_id: str,
    transfer: dict,
    go_receipt: str | None = None,
) -> dict[str, Any]:
    """Principal/agent path: valid GO-shaped transfer releases escrow (no bounty)."""
    pid = (position_id or "").strip()
    if not pid:
        return {"ok": False, "error": "position_id_required", "spec": SPEC}
    with _LOCK:
        c = _conn()
        try:
            row = c.execute(
                "SELECT * FROM clearance_positions WHERE id=?", (pid,)
            ).fetchone()
            if not row:
                return {"ok": False, "error": "position_not_found", "spec": SPEC}
            row = _expire_if_needed(c, row)
            if row["status"] != "OPEN":
                return {
                    "ok": False,
                    "error": "not_open",
                    "status": row["status"],
                    "spec": SPEC,
                }
            mandate = json.loads(row["mandate_json"] or "{}")
            verdict = evaluate_breach(
                rail=row["rail"],
                transfer=transfer if isinstance(transfer, dict) else {},
                mandate=mandate,
            )
            if verdict["decision"] != "GO":
                return {
                    "ok": False,
                    "error": "not_cleared",
                    "verdict": verdict,
                    "plain": "Only a GO-shaped transfer releases. Else keepers hunt.",
                    "spec": SPEC,
                }
            if go_receipt:
                verified = prefinality_mod.verify_receipt_jwt(
                    go_receipt,
                    expected_fingerprint=verdict["fingerprint"],
                )
                if not verified.get("valid"):
                    return {
                        "ok": False,
                        "error": "invalid_go_receipt",
                        "verify": verified,
                        "spec": SPEC,
                    }
            c.execute(
                """UPDATE clearance_positions
                   SET status=?, residual_units=?
                   WHERE id=? AND status=?""",
                ("RELEASED", row["escrow_units"], pid, "OPEN"),
            )
            c.commit()
            pos = _row_position(
                c.execute(
                    "SELECT * FROM clearance_positions WHERE id=?", (pid,)
                ).fetchone()
            )
        finally:
            c.close()
    return {
        "ok": True,
        "spec": SPEC,
        "word": "RELEASED",
        "plain": "Clear held. Escrow released. No keeper bounty.",
        "position": pos,
        "verdict": verdict,
        "their_production": False,
    }


def dogfood_drill(*, keeper_id: str = "keeper_dogfood") -> dict[str, Any]:
    """Mechanics drill on demo ledger. Not real money. Not mining income."""
    payto = "0x00000000000000000000000000000000000000aa"
    wrong = "0x00000000000000000000000000000000000000bb"
    opened = open_position(
        principal_id="principal_dogfood",
        agent_id="agent_dogfood",
        escrow_amount="100.00",
        rail="x402",
        bounty_bps=500,
        mandate={
            "agent_id": "agent_dogfood",
            "max_amount": "10.00",
            "expected_payto": payto,
        },
        custody={"venue": custody_mod.VENUE_DEMO_LEDGER},
        meta={"drill": True, "money_real": False},
    )
    if not opened.get("ok"):
        return opened
    pid = opened["position"]["position_id"]
    observed = observe(
        position_id=pid,
        executed=True,
        transfer={
            "amount": "25.00",
            "currency": "USDC",
            "counterparty": wrong,
        },
    )
    claimed = liquidate(position_id=pid, keeper_id=keeper_id)
    return {
        "spec": SPEC,
        "drill": "dogfood",
        "money_real": False,
        "gate_holds_funds": False,
        "plain": (
            "DEMO ONLY. Locked demo-100, breached, liquidated, demo-bounty 5. "
            "No dollars moved. Massive money enters via foreign vault (on-chain USDC / Issuing)."
        ),
        "open": opened,
        "observe": observed,
        "liquidate": claimed,
        "massive_ingress": custody_mod.massive_ingress_rank(),
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Clearance Keepers",
        "promise": (
            "Foreign vault holds money. Gate Clear/Never is the hash. "
            "Keepers liquidate breaches. Vault pays bounty. Gate never holds funds."
        ),
        "mining": {
            "bitcoin": "hash until protocol pays",
            "gate": "watch foreign vault → Never/NO_GO prove → liquidate → vault pays",
            "hash": "Clear/Never over mandate",
            "farm": "you run keepers; vault is the protocol payer",
        },
        "atoms": custody_mod.catalog()["atoms"],
        "money": {
            "demo_dogfood_is_real": False,
            "gate_holds_funds": False,
            "real_path": "onchain_usdc | stripe_issuing | sponsor_bank",
        },
        "custody": custody_mod.catalog(),
        "words": ["OPEN", "BREACHED", "LIQUIDATED", "RELEASED", "EXPIRED"],
        "page": f"{base}/keepers",
        "api": {
            "open": f"{base}/demo/keepers/open",
            "observe": f"{base}/demo/keepers/observe",
            "scan": f"{base}/demo/keepers/scan",
            "liquidate": f"{base}/demo/keepers/liquidate",
            "release": f"{base}/demo/keepers/release",
            "dogfood": f"{base}/demo/keepers/dogfood",
            "position": f"{base}/demo/keepers/position",
            "custody": f"{base}/.well-known/foreign-custody.json",
        },
        "default_bounty_bps": DEFAULT_BOUNTY_BPS,
        "rails": list(prefinality_mod.RAILS),
        "not": [
            "token emissions as mining",
            "SaaS checkout",
            "Gate holding customer funds",
            "demo ledger as real TVL",
        ],
        "their_production": False,
    }
