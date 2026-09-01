"""Foothill Max Pack — remaining software-demoable mouth seeds.

Doctrine ceiling companion (`MOUTH_CEILING.md`). Completes foothill layer for
cells that were mountain-named but can demo on bind / payout / agent / PLC
paths this year without hardware forge.

Inventions:
  1. Tool Throat          — agent tool pre-hook
  2. Time Lock Envelope   — LIVE only inside / after window
  3. Charisma Nullifier   — boss/chat/synthetic yes ⇒ CHOKE
  4. Sabbath Latch        — calendar DENY window
  5. May Quarantine       — principal/edge cannot receive LIVE
  6. Branch Tombstone     — restraint receipt across declared branches
  7. Secure Write Macro   — only pre-approved irreversible classes
  8. Dose Throat          — body/infusion commit mouth (care medium)
  9. Jubilee Clock        — scheduled may-retirement
 10. Antimay Detector     — forged authority / fake sheath
 11. Senate Socket Soft   — N-of-M software quorum socket
 12. Receipt Stone        — immutable stranger receipt anchor

Under coordinators. Never sovereign. Not MGA outbound copy.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

SPEC_PACK = "gate-foothill-max-v1"
FAMILY = "applicable_now"
POSTURE = (
    "Under coordinators. Foothill max — every demoable mouth cell seeded. "
    "Hardware sheath / Senate metal / forge HIL stay mountain."
)


def _now(ts: str | None = None) -> datetime:
    if ts:
        t = ts.strip().replace("Z", "+00:00")
        dt = datetime.fromisoformat(t)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


# --- 1. Tool Throat ---
def tool_throat_evaluate(
    *,
    tool_name: str | None = None,
    irreversible: bool | None = None,
    live_cleared: bool | None = None,
    soft_prompt_yes: bool | None = None,
    timeout: bool | None = None,
) -> dict[str, Any]:
    irr = bool(irreversible)
    if not irr:
        return {
            "spec": "gate-tool-throat-v1",
            "invention": "Tool Throat",
            "verdict": "TOOL_NOT_IRREVERSIBLE",
            "may_proceed": True,
            "tool_name": tool_name,
            "detail": "Tool marked reversible — Tool Throat idle.",
            "rule": "Irreversible agent tools need LIVE; soft prompt ≠ LIVE.",
        }
    if timeout or soft_prompt_yes:
        return {
            "spec": "gate-tool-throat-v1",
            "invention": "Tool Throat",
            "verdict": "TOOL_CHOKE",
            "may_proceed": False,
            "tool_name": tool_name,
            "detail": "Timeout or soft-prompt yes on irreversible tool — CHOKE.",
            "rule": "Irreversible agent tools need LIVE; soft prompt ≠ LIVE.",
        }
    if live_cleared:
        return {
            "spec": "gate-tool-throat-v1",
            "invention": "Tool Throat",
            "verdict": "TOOL_OPEN",
            "may_proceed": True,
            "tool_name": tool_name,
            "detail": "LIVE cleared for irreversible tool.",
            "rule": "Irreversible agent tools need LIVE; soft prompt ≠ LIVE.",
        }
    return {
        "spec": "gate-tool-throat-v1",
        "invention": "Tool Throat",
        "verdict": "TOOL_CLOSED",
        "may_proceed": False,
        "tool_name": tool_name,
        "detail": "Irreversible tool without LIVE — DENY.",
        "rule": "Irreversible agent tools need LIVE; soft prompt ≠ LIVE.",
    }


# --- 2. Time Lock Envelope ---
def time_lock_evaluate(
    *,
    now: str | None = None,
    unlock_at: str | None = None,
    window_start: str | None = None,
    window_end: str | None = None,
    premature_attempt: bool | None = None,
) -> dict[str, Any]:
    now_dt = _now(now)
    if unlock_at:
        try:
            u = _now(unlock_at)
            if now_dt < u:
                return {
                    "spec": "gate-time-lock-v1",
                    "invention": "Time Lock Envelope",
                    "verdict": "TIME_LOCKED",
                    "may_proceed": False,
                    "unlock_at": unlock_at,
                    "detail": "LIVE sealed until unlock_at — premature is forged.",
                    "rule": "Offense without panic: LIVE only when the envelope opens.",
                }
        except ValueError:
            return {
                "spec": "gate-time-lock-v1",
                "invention": "Time Lock Envelope",
                "verdict": "TIME_LOCK_CHOKE",
                "may_proceed": False,
                "detail": "Unparseable unlock_at — CHOKE.",
                "rule": "Offense without panic: LIVE only when the envelope opens.",
            }
    if window_start and window_end:
        try:
            a, b = _now(window_start), _now(window_end)
            inside = a <= now_dt <= b
            if not inside or premature_attempt and now_dt < a:
                return {
                    "spec": "gate-time-lock-v1",
                    "invention": "Time Lock Envelope",
                    "verdict": "OUTSIDE_WINDOW",
                    "may_proceed": False,
                    "window_start": window_start,
                    "window_end": window_end,
                    "detail": "Outside LIVE window — DENY.",
                    "rule": "Offense without panic: LIVE only when the envelope opens.",
                }
        except ValueError:
            return {
                "spec": "gate-time-lock-v1",
                "invention": "Time Lock Envelope",
                "verdict": "TIME_LOCK_CHOKE",
                "may_proceed": False,
                "detail": "Unparseable window — CHOKE.",
                "rule": "Offense without panic: LIVE only when the envelope opens.",
            }
    return {
        "spec": "gate-time-lock-v1",
        "invention": "Time Lock Envelope",
        "verdict": "TIME_OPEN",
        "may_proceed": True,
        "detail": "Envelope open under declared time conditions.",
        "rule": "Offense without panic: LIVE only when the envelope opens.",
    }


# --- 3. Charisma Nullifier ---
def charisma_nullifier_evaluate(
    *,
    boss_said_yes: bool | None = None,
    chat_yes: bool | None = None,
    synthetic_voice: bool | None = None,
    emoji_quorum: bool | None = None,
    hardware_live: bool | None = None,
    quorum_ok: bool | None = None,
    charge_present: bool | None = None,
) -> dict[str, Any]:
    soft = bool(boss_said_yes or chat_yes or synthetic_voice or emoji_quorum)
    hard = bool(hardware_live or (quorum_ok and charge_present))
    if soft and not hard:
        return {
            "spec": "gate-charisma-nullifier-v1",
            "invention": "Charisma Nullifier",
            "verdict": "CHARISMA_FORGED",
            "may_proceed": False,
            "forged": True,
            "detail": "Verbal/chat/synthetic/emoji yes without hardware/quorum+CHARGE — forged.",
            "rule": "Charisma never mints LIVE. Quorum/CHARGE/hardware only.",
        }
    return {
        "spec": "gate-charisma-nullifier-v1",
        "invention": "Charisma Nullifier",
        "verdict": "CHARISMA_CLEAR" if not soft else "CHARISMA_HARDENED",
        "may_proceed": True,
        "forged": False,
        "detail": "No soft charisma path — or hardened by quorum/CHARGE/hardware.",
        "rule": "Charisma never mints LIVE. Quorum/CHARGE/hardware only.",
    }


# --- 4. Sabbath Latch ---
def sabbath_latch_evaluate(
    *,
    now: str | None = None,
    sabbath_weekday: int | None = None,  # 0=Mon ... 6=Sun
    sabbath_active: bool | None = None,
    would_commit: bool | None = None,
) -> dict[str, Any]:
    if sabbath_active is None and sabbath_weekday is not None:
        sabbath_active = _now(now).weekday() == int(sabbath_weekday)
    active = bool(sabbath_active)
    if active and would_commit:
        return {
            "spec": "gate-sabbath-latch-v1",
            "invention": "Sabbath Latch",
            "verdict": "SABBATH_DENY",
            "may_proceed": False,
            "detail": "Sabbath latch active — scheduled DENY on irreversible writes.",
            "rule": "Calendar DENY windows — authority rests without panic LIVE.",
        }
    return {
        "spec": "gate-sabbath-latch-v1",
        "invention": "Sabbath Latch",
        "verdict": "SABBATH_OPEN" if not active else "SABBATH_IDLE",
        "may_proceed": True,
        "detail": "Sabbath latch idle or no commit attempted.",
        "rule": "Calendar DENY windows — authority rests without panic LIVE.",
    }


# --- 5. May Quarantine ---
def may_quarantine_evaluate(
    *,
    quarantined: bool | None = None,
    principal_id: str | None = None,
    edge_id: str | None = None,
    requesting_live: bool | None = None,
) -> dict[str, Any]:
    if quarantined and requesting_live:
        return {
            "spec": "gate-may-quarantine-v1",
            "invention": "May Quarantine",
            "verdict": "QUARANTINE_DENY",
            "may_proceed": False,
            "principal_id": principal_id,
            "edge_id": edge_id,
            "detail": "Principal/edge quarantined — cannot receive LIVE.",
            "rule": "Exile from may without killing the body — quarantine is EXILE runtime.",
        }
    return {
        "spec": "gate-may-quarantine-v1",
        "invention": "May Quarantine",
        "verdict": "QUARANTINE_CLEAR",
        "may_proceed": True,
        "principal_id": principal_id,
        "edge_id": edge_id,
        "detail": "Not quarantined — may path open under other mouths.",
        "rule": "Exile from may without killing the body — quarantine is EXILE runtime.",
    }


# --- 6. Branch Tombstone ---
def branch_tombstone_evaluate(
    *,
    halted: bool | None = None,
    acted: bool | None = None,
    branch_id: str | None = None,
    coordinator_set: list | None = None,
) -> dict[str, Any]:
    if halted and acted is not True:
        tid = f"tomb_{uuid4().hex[:12]}"
        return {
            "spec": "gate-branch-tombstone-v1",
            "invention": "Branch Tombstone",
            "verdict": "TOMBSTONE_MINTED",
            "may_proceed": False,
            "tombstone_id": tid,
            "branch_id": branch_id or "default",
            "coordinator_set": list(coordinator_set or []),
            "claim": "restraint_recognized_across_declared_branches",
            "detail": "Branch tombstone minted — restraint proved on this branch.",
            "rule": "Multiverse-class restraint receipt for coordinators who recognize the branch set.",
        }
    return {
        "spec": "gate-branch-tombstone-v1",
        "invention": "Branch Tombstone",
        "verdict": "TOMBSTONE_IDLE",
        "may_proceed": True,
        "detail": "No counterfactual halt — tombstone idle.",
        "rule": "Multiverse-class restraint receipt for coordinators who recognize the branch set.",
    }


# --- 7. Secure Write Macro ---
def secure_write_macro_evaluate(
    *,
    command_class: str | None = None,
    approved_classes: list | None = None,
    would_write: bool | None = None,
) -> dict[str, Any]:
    approved = {str(c).strip().lower() for c in (approved_classes or ["status_read", "heartbeat"])}
    cls = (command_class or "").strip().lower()
    if would_write and cls and cls not in approved:
        return {
            "spec": "gate-secure-write-macro-v1",
            "invention": "Secure Write Macro",
            "verdict": "MACRO_DENY",
            "may_proceed": False,
            "command_class": cls,
            "detail": "Command class not in pre-approved irreversible set — DENY.",
            "rule": "Only pre-cleared irreversible classes may write plant/twin reality.",
        }
    return {
        "spec": "gate-secure-write-macro-v1",
        "invention": "Secure Write Macro",
        "verdict": "MACRO_OK",
        "may_proceed": True,
        "command_class": cls or None,
        "approved_classes": sorted(approved),
        "detail": "Command class permitted or no write attempted.",
        "rule": "Only pre-cleared irreversible classes may write plant/twin reality.",
    }


# --- 8. Dose Throat ---
def dose_throat_evaluate(
    *,
    dose_irreversible: bool | None = None,
    live_cleared: bool | None = None,
    cosign_ok: bool | None = None,
    panic_push: bool | None = None,
) -> dict[str, Any]:
    if not dose_irreversible:
        return {
            "spec": "gate-dose-throat-v1",
            "invention": "Dose Throat",
            "verdict": "DOSE_NOT_IRREVERSIBLE",
            "may_proceed": True,
            "detail": "Dose not marked irreversible — Dose Throat idle.",
            "rule": "Bloodstream is sacred medium — LIVE + cosign; panic push forged.",
        }
    if panic_push and not (live_cleared and cosign_ok):
        return {
            "spec": "gate-dose-throat-v1",
            "invention": "Dose Throat",
            "verdict": "DOSE_CHOKE",
            "may_proceed": False,
            "detail": "Panic push on irreversible dose without LIVE+cosign — CHOKE.",
            "rule": "Bloodstream is sacred medium — LIVE + cosign; panic push forged.",
        }
    if live_cleared and cosign_ok:
        return {
            "spec": "gate-dose-throat-v1",
            "invention": "Dose Throat",
            "verdict": "DOSE_OPEN",
            "may_proceed": True,
            "detail": "Dose LIVE cleared with cosign.",
            "rule": "Bloodstream is sacred medium — LIVE + cosign; panic push forged.",
        }
    return {
        "spec": "gate-dose-throat-v1",
        "invention": "Dose Throat",
        "verdict": "DOSE_CLOSED",
        "may_proceed": False,
        "detail": "Irreversible dose without LIVE+cosign — DENY.",
        "rule": "Bloodstream is sacred medium — LIVE + cosign; panic push forged.",
    }


# --- 9. Jubilee Clock ---
def jubilee_clock_evaluate(
    *,
    now: str | None = None,
    jubilee_at: str | None = None,
    may_retired: bool | None = None,
) -> dict[str, Any]:
    if not jubilee_at:
        return {
            "spec": "gate-jubilee-clock-v1",
            "invention": "Jubilee Clock",
            "verdict": "JUBILEE_UNSCHEDULED",
            "may_proceed": True,
            "detail": "No jubilee scheduled.",
            "rule": "Scheduled may-retirement — authority reset without panic LIVE.",
        }
    try:
        due = _now(now) >= _now(jubilee_at)
    except ValueError:
        return {
            "spec": "gate-jubilee-clock-v1",
            "invention": "Jubilee Clock",
            "verdict": "JUBILEE_CHOKE",
            "may_proceed": False,
            "detail": "Unparseable jubilee_at — CHOKE.",
            "rule": "Scheduled may-retirement — authority reset without panic LIVE.",
        }
    if due and not may_retired:
        return {
            "spec": "gate-jubilee-clock-v1",
            "invention": "Jubilee Clock",
            "verdict": "JUBILEE_DUE",
            "may_proceed": False,
            "jubilee_at": jubilee_at,
            "detail": "Jubilee due — may must retire/re-clear before further LIVE.",
            "rule": "Scheduled may-retirement — authority reset without panic LIVE.",
        }
    return {
        "spec": "gate-jubilee-clock-v1",
        "invention": "Jubilee Clock",
        "verdict": "JUBILEE_CLEAR",
        "may_proceed": True,
        "jubilee_at": jubilee_at,
        "detail": "Jubilee not due or may already retired/re-cleared.",
        "rule": "Scheduled may-retirement — authority reset without panic LIVE.",
    }


# --- 10. Antimay Detector ---
def antimay_evaluate(
    *,
    fake_sheath: bool | None = None,
    forged_command: bool | None = None,
    spoofed_live: bool | None = None,
    genealogy_break: bool | None = None,
) -> dict[str, Any]:
    hit = bool(fake_sheath or forged_command or spoofed_live or genealogy_break)
    if hit:
        return {
            "spec": "gate-antimay-v1",
            "invention": "Antimay Detector",
            "verdict": "ANTIMAY_TRIPPED",
            "may_proceed": False,
            "tripped": True,
            "detail": "Forged sheath/command/LIVE or genealogy break — Antimay trip.",
            "rule": "Detect counterfeit authority — antimay is forged may wearing a sheath costume.",
        }
    return {
        "spec": "gate-antimay-v1",
        "invention": "Antimay Detector",
        "verdict": "ANTIMAY_CLEAR",
        "may_proceed": True,
        "tripped": False,
        "detail": "No antimay signals.",
        "rule": "Detect counterfeit authority — antimay is forged may wearing a sheath costume.",
    }


# --- 11. Senate Socket Soft ---
def senate_socket_soft_evaluate(
    *,
    required_n: int = 2,
    seats: list | None = None,
    approvals: list | None = None,
    mass_class: str | None = None,
) -> dict[str, Any]:
    need = max(1, int(required_n))
    if (mass_class or "").lower() == "light":
        return {
            "spec": "gate-senate-socket-soft-v1",
            "invention": "Senate Socket Soft",
            "verdict": "SENATE_NOT_REQUIRED",
            "may_proceed": True,
            "detail": "Light mass — Senate socket not required.",
            "rule": "N-of-M software quorum for heavy/sacred — hardware Senate stays mountain.",
        }
    got = len(approvals or [])
    ok = got >= need
    return {
        "spec": "gate-senate-socket-soft-v1",
        "invention": "Senate Socket Soft",
        "verdict": "SENATE_OK" if ok else "SENATE_SHORT",
        "may_proceed": ok,
        "required_n": need,
        "got_n": got,
        "seats": list(seats or []),
        "approvals": list(approvals or []),
        "detail": "Senate quorum satisfied." if ok else "Senate short — non-unilateral settlement required.",
        "rule": "N-of-M software quorum for heavy/sacred — hardware Senate stays mountain.",
    }


# --- 12. Receipt Stone ---
def receipt_stone_stamp(
    *,
    event_id: str | None = None,
    verify_url: str | None = None,
    desk_id: str | None = None,
    program_id: str | None = None,
) -> dict[str, Any]:
    stone_id = f"stone_{uuid4().hex[:12]}"
    return {
        "spec": "gate-receipt-stone-v1",
        "invention": "Receipt Stone",
        "verdict": "STONE_SET",
        "stone_id": stone_id,
        "event_id": event_id,
        "verify_url": verify_url,
        "desk_id": desk_id,
        "program_id": program_id,
        "outside_operator_trust": True,
        "detail": "Receipt stone set — stranger anchor outside operator trust boundary.",
        "rule": "Immutable stranger receipt anchor for desk/program — Bind Room verify_url is foothill form.",
    }


INVENTIONS = (
    ("tool_throat", "Tool Throat", "gate-tool-throat-v1"),
    ("time_lock", "Time Lock Envelope", "gate-time-lock-v1"),
    ("charisma_nullifier", "Charisma Nullifier", "gate-charisma-nullifier-v1"),
    ("sabbath_latch", "Sabbath Latch", "gate-sabbath-latch-v1"),
    ("may_quarantine", "May Quarantine", "gate-may-quarantine-v1"),
    ("branch_tombstone", "Branch Tombstone", "gate-branch-tombstone-v1"),
    ("secure_write_macro", "Secure Write Macro", "gate-secure-write-macro-v1"),
    ("dose_throat", "Dose Throat", "gate-dose-throat-v1"),
    ("jubilee_clock", "Jubilee Clock", "gate-jubilee-clock-v1"),
    ("antimay", "Antimay Detector", "gate-antimay-v1"),
    ("senate_socket_soft", "Senate Socket Soft", "gate-senate-socket-soft-v1"),
    ("receipt_stone", "Receipt Stone", "gate-receipt-stone-v1"),
)


def evaluate(name: str, **kwargs: Any) -> dict[str, Any]:
    n = (name or "").strip().lower().replace("-", "_")
    table = {
        "tool_throat": tool_throat_evaluate,
        "time_lock": time_lock_evaluate,
        "time_lock_envelope": time_lock_evaluate,
        "charisma_nullifier": charisma_nullifier_evaluate,
        "sabbath_latch": sabbath_latch_evaluate,
        "may_quarantine": may_quarantine_evaluate,
        "branch_tombstone": branch_tombstone_evaluate,
        "secure_write_macro": secure_write_macro_evaluate,
        "dose_throat": dose_throat_evaluate,
        "jubilee_clock": jubilee_clock_evaluate,
        "antimay": antimay_evaluate,
        "antimay_detector": antimay_evaluate,
        "senate_socket_soft": senate_socket_soft_evaluate,
        "senate_socket": senate_socket_soft_evaluate,
        "receipt_stone": lambda **k: receipt_stone_stamp(**k),
    }
    fn = table.get(n)
    if not fn:
        return {"error": "unknown_invention", "known": [i[0] for i in INVENTIONS]}
    return fn(**kwargs)


def attach(plan: dict, *, public_url: str = "") -> dict:
    base = (public_url or "").rstrip("/")
    mt = plan.get("mass_tag") if isinstance(plan.get("mass_tag"), dict) else {}
    sm = plan.get("stick_meter") if isinstance(plan.get("stick_meter"), dict) else {}
    mass = mt.get("mass_class") or mt.get("tag") or sm.get("mass_class")
    pack: dict[str, Any] = {"spec": SPEC_PACK, "family": FAMILY, "inventions": {}}

    if plan.get("tool_name") or plan.get("agent_tool"):
        pack["inventions"]["tool_throat"] = tool_throat_evaluate(
            tool_name=plan.get("tool_name") or plan.get("agent_tool"),
            irreversible=plan.get("tool_irreversible", True),
            live_cleared=plan.get("live_cleared") or (plan.get("decision") or "").upper() in ("ALLOW", "LIVE"),
            soft_prompt_yes=plan.get("soft_prompt_yes") or plan.get("chat_yes"),
            timeout=plan.get("timeout"),
        )
    if plan.get("unlock_at") or plan.get("window_start"):
        pack["inventions"]["time_lock"] = time_lock_evaluate(
            unlock_at=plan.get("unlock_at"),
            window_start=plan.get("window_start"),
            window_end=plan.get("window_end"),
            premature_attempt=plan.get("premature_attempt"),
        )
    pack["inventions"]["charisma_nullifier"] = charisma_nullifier_evaluate(
        boss_said_yes=plan.get("boss_said_yes"),
        chat_yes=plan.get("chat_yes"),
        synthetic_voice=plan.get("synthetic_voice"),
        emoji_quorum=plan.get("emoji_quorum"),
        hardware_live=plan.get("hardware_live"),
        quorum_ok=(plan.get("desk_quorum_fob") or {}).get("may_proceed")
        if isinstance(plan.get("desk_quorum_fob"), dict)
        else plan.get("quorum_ok"),
        charge_present=bool(plan.get("charge_id") or plan.get("charge_present")),
    )
    if plan.get("sabbath_active") is not None or plan.get("sabbath_weekday") is not None:
        pack["inventions"]["sabbath_latch"] = sabbath_latch_evaluate(
            sabbath_weekday=plan.get("sabbath_weekday"),
            sabbath_active=plan.get("sabbath_active"),
            would_commit=plan.get("allow_bind") or plan.get("acted") or plan.get("would_commit"),
        )
    if plan.get("quarantined"):
        pack["inventions"]["may_quarantine"] = may_quarantine_evaluate(
            quarantined=True,
            principal_id=plan.get("principal_id"),
            edge_id=plan.get("edge_id"),
            requesting_live=plan.get("allow_bind") or (plan.get("decision") or "").upper() in ("ALLOW", "LIVE"),
        )
    if plan.get("halt") or (plan.get("decision") or "").upper() in ("HALT", "BLOCK"):
        pack["inventions"]["branch_tombstone"] = branch_tombstone_evaluate(
            halted=True,
            acted=plan.get("acted"),
            branch_id=plan.get("branch_id"),
            coordinator_set=plan.get("coordinator_set") if isinstance(plan.get("coordinator_set"), list) else None,
        )
    if plan.get("command_class") or plan.get("plc_write"):
        pack["inventions"]["secure_write_macro"] = secure_write_macro_evaluate(
            command_class=plan.get("command_class") or plan.get("plc_write"),
            approved_classes=plan.get("approved_classes")
            if isinstance(plan.get("approved_classes"), list)
            else None,
            would_write=True,
        )
    if plan.get("dose_irreversible") or plan.get("dose"):
        pack["inventions"]["dose_throat"] = dose_throat_evaluate(
            dose_irreversible=plan.get("dose_irreversible", True),
            live_cleared=plan.get("live_cleared"),
            cosign_ok=plan.get("cosign_ok"),
            panic_push=plan.get("panic_push") or plan.get("panic_mode"),
        )
    if plan.get("jubilee_at"):
        pack["inventions"]["jubilee_clock"] = jubilee_clock_evaluate(
            jubilee_at=plan.get("jubilee_at"),
            may_retired=plan.get("may_retired"),
        )
    pack["inventions"]["antimay"] = antimay_evaluate(
        fake_sheath=plan.get("fake_sheath"),
        forged_command=plan.get("forged_command"),
        spoofed_live=plan.get("spoofed_live"),
        genealogy_break=plan.get("genealogy_break"),
    )
    pack["inventions"]["senate_socket_soft"] = senate_socket_soft_evaluate(
        required_n=int(plan.get("senate_n") or 2),
        seats=plan.get("senate_seats") if isinstance(plan.get("senate_seats"), list) else None,
        approvals=plan.get("senate_approvals") if isinstance(plan.get("senate_approvals"), list) else None,
        mass_class=mass,
    )
    pack["inventions"]["receipt_stone"] = receipt_stone_stamp(
        event_id=plan.get("event_id"),
        verify_url=plan.get("verify_url"),
        desk_id=plan.get("desk_id"),
        program_id=plan.get("program_id"),
    )

    blockers = []
    for key, inv in pack["inventions"].items():
        if inv.get("may_proceed") is False and inv.get("verdict") not in (
            "TOOL_NOT_IRREVERSIBLE",
            "TOMBSTONE_IDLE",
            "SABBATH_IDLE",
            "JUBILEE_UNSCHEDULED",
            "SENATE_NOT_REQUIRED",
            "DOSE_NOT_IRREVERSIBLE",
            "CHARISMA_CLEAR",
            "ANTIMAY_CLEAR",
            "MACRO_OK",
            "QUARANTINE_CLEAR",
            "TIME_OPEN",
            "STONE_SET",
        ):
            blockers.append(key)
        if inv.get("forged") or inv.get("tripped"):
            blockers.append(key)
    pack["blockers"] = sorted(set(blockers))
    pack["foothill_max_score"] = len(INVENTIONS)
    pack["active_count"] = len(pack["inventions"])
    if base:
        pack["well_known"] = f"{base}/.well-known/foothill-max.json"
        pack["ceiling_doc"] = "gate/MOUTH_CEILING.md"
    plan["foothill_max"] = pack

    for key in pack["blockers"]:
        inv = pack["inventions"].get(key) or {}
        if inv.get("may_proceed") is False:
            if plan.get("allow_bind") or plan.get("acted"):
                plan["allow_bind"] = False
                if "bind_allowed" in plan:
                    plan["bind_allowed"] = False
                plan["halt"] = True
                if not plan.get("decision") or plan.get("decision") == "ALLOW":
                    plan["decision"] = "HALT"
                plan["reason"] = plan.get("reason") or f"foothill_max:{key}"
            break
    return plan


def manifest(public_url: str, name: str | None = None) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    catalog = [
        {
            "slug": slug,
            "invention": title,
            "spec": spec,
            "well_known": f"{base}/.well-known/{slug.replace('_', '-')}.json",
            "demo": f"POST {base}/demo/pas/foothill-max",
        }
        for slug, title, spec in INVENTIONS
    ]
    if name:
        slug = name.strip().lower().replace("-", "_")
        for c in catalog:
            if c["slug"] == slug:
                return {**c, "family": FAMILY, "pack": SPEC_PACK, "posture": POSTURE}
    return {
        "spec": SPEC_PACK,
        "invention": "Foothill Max Pack",
        "family": FAMILY,
        "one_liner": "Twelve remaining software foothills — tool, time, charisma, sabbath, quarantine, tombstone, macro, dose, jubilee, antimay, senate-soft, receipt stone.",
        "count": len(INVENTIONS),
        "inventions": catalog,
        "demo": f"POST {base}/demo/pas/foothill-max",
        "well_known": f"{base}/.well-known/foothill-max.json",
        "ceiling_doc": "gate/MOUTH_CEILING.md",
        "stop_rule": "After this pack: stop inventing until a paid weld hangs on the mouth.",
        "posture": POSTURE,
    }


def manifest_one(public_url: str, slug: str) -> dict[str, Any]:
    return manifest(public_url, name=slug)
