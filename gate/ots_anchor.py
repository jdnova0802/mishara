"""OpenTimestamps Bitcoin anchor for Gate evidence-head Merkle roots.

Closes the publication-hard gap: strangers verify "this evidence-head existed
by Bitcoin block H" without trusting Gate's clocks or keys alone.

Flow:
  1. Build canonical commitment JSON (tree_size + root_hash).
  2. Submit SHA256(commitment) to public OTS calendars → pending .ots.
  3. Periodically upgrade .ots until calendars return BitcoinBlockHeaderAttestation.
  4. Surface status on /.well-known/evidence-head.json under `opentimestamps`.

Env:
  GATE_OTS_DIR          — proof store (default: <cwd>/.cache/gate-ots)
  GATE_OTS_ENABLED      — "0" disables attach (default on when proofs exist)
  GATE_OTS_MIN_CALENDARS — calendars that must reply on stamp (default 2)
  GATE_OTS_TIMEOUT      — per-calendar HTTP timeout seconds (default 10)

Not a product SKU. Same mouth standard: real .ots or nothing.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SPEC = "gate-ots-anchor-v1"
COMMITMENT_SPEC = "gate-ots-commitment-v1"

DEFAULT_CALENDARS = (
    "https://alice.btc.calendar.opentimestamps.org",
    "https://bob.btc.calendar.opentimestamps.org",
    "https://finney.calendar.eternitywall.com",
    "https://btc.calendar.catallaxy.com",
)


def ots_dir() -> Path:
    raw = (os.getenv("GATE_OTS_DIR") or "").strip()
    if raw:
        return Path(raw)
    return Path(os.getcwd()) / ".cache" / "gate-ots"


def enabled() -> bool:
    return (os.getenv("GATE_OTS_ENABLED") or "1").strip() != "0"


def commitment_bytes(*, tree_size: int, root_hash: str) -> bytes:
    """Canonical commitment whose SHA256 is what calendars attest."""
    body = {
        "spec": COMMITMENT_SPEC,
        "tree_size": int(tree_size),
        "root_hash": (root_hash or "").strip().lower(),
    }
    return (json.dumps(body, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def commitment_digest_hex(*, tree_size: int, root_hash: str) -> str:
    return hashlib.sha256(commitment_bytes(tree_size=tree_size, root_hash=root_hash)).hexdigest()


def _slug(*, tree_size: int, root_hash: str) -> str:
    rh = (root_hash or "").strip().lower()
    return f"{int(tree_size)}-{rh[:16] if rh else 'empty'}"


def _paths(*, tree_size: int, root_hash: str) -> dict[str, Any]:
    base = ots_dir()
    slug = _slug(tree_size=tree_size, root_hash=root_hash)
    return {
        "dir": base,
        "commitment": base / "commitments" / f"{slug}.json",
        "ots": base / "proofs" / f"{slug}.ots",
        "meta": base / "proofs" / f"{slug}.meta.json",
        "state": base / "state.json",
        "slug": slug,
    }


def _write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _ots_cli() -> str | None:
    return shutil.which("ots")


def _stamp_via_cli(commitment_path: Path, ots_path: Path) -> dict[str, Any]:
    cli = _ots_cli()
    if not cli:
        return {"ok": False, "error": "ots_cli_missing"}
    timeout = float(os.getenv("GATE_OTS_TIMEOUT") or "10")
    m = int(os.getenv("GATE_OTS_MIN_CALENDARS") or "2")
    cmd = [cli, "stamp", "-m", str(m), "--timeout", str(timeout)]
    for url in DEFAULT_CALENDARS:
        cmd.extend(["-c", url])
    cmd.append(str(commitment_path))
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=max(30.0, timeout * 4))
    produced = Path(str(commitment_path) + ".ots")
    if proc.returncode != 0 and not produced.exists():
        return {
            "ok": False,
            "error": "ots_stamp_failed",
            "stderr": (proc.stderr or "")[-800:],
            "stdout": (proc.stdout or "")[-400:],
        }
    if not produced.exists():
        return {"ok": False, "error": "ots_file_not_created"}
    ots_path.parent.mkdir(parents=True, exist_ok=True)
    if produced.resolve() != ots_path.resolve():
        shutil.copy2(produced, ots_path)
        try:
            produced.unlink()
        except OSError:
            pass
    return {
        "ok": True,
        "method": "ots_cli",
        "stdout": (proc.stdout or "")[-400:],
        "calendars": list(DEFAULT_CALENDARS),
    }


def _stamp_via_library(digest: bytes, ots_path: Path) -> dict[str, Any]:
    """Submit digest to calendars with python-opentimestamps (optional)."""
    try:
        from opentimestamps.calendar import RemoteCalendar
        from opentimestamps.core.op import OpSHA256
        from opentimestamps.core.serialize import BytesSerializationContext
        from opentimestamps.core.timestamp import DetachedTimestampFile, Timestamp
    except ImportError as exc:
        return {"ok": False, "error": "opentimestamps_import_failed", "detail": str(exc)}

    timeout = float(os.getenv("GATE_OTS_TIMEOUT") or "10")
    min_c = int(os.getenv("GATE_OTS_MIN_CALENDARS") or "2")
    file_timestamp = DetachedTimestampFile(OpSHA256(), Timestamp(digest))
    stamped = 0
    errors: list[str] = []
    for url in DEFAULT_CALENDARS:
        try:
            remote = RemoteCalendar(url)
            # Calendar expects the file digest (sha256 of commitment).
            ts = remote.submit(digest, timeout=timeout)
            file_timestamp.timestamp.merge(ts)
            stamped += 1
            if stamped >= min_c:
                break
        except Exception as exc:  # noqa: BLE001 — calendar flakiness is expected
            errors.append(f"{url}: {exc}")
    if stamped < min_c:
        return {
            "ok": False,
            "error": "insufficient_calendars",
            "stamped": stamped,
            "min": min_c,
            "errors": errors[:8],
        }
    ots_path.parent.mkdir(parents=True, exist_ok=True)
    ctx = BytesSerializationContext()
    file_timestamp.serialize(ctx)
    ots_path.write_bytes(ctx.getbytes())
    return {"ok": True, "method": "python_opentimestamps", "stamped": stamped, "errors": errors}


def stamp_root(*, tree_size: int, root_hash: str, force: bool = False) -> dict[str, Any]:
    """Submit evidence-head commitment to OTS calendars. Idempotent unless force."""
    root_hash = (root_hash or "").strip().lower()
    paths = _paths(tree_size=tree_size, root_hash=root_hash)
    digest = commitment_digest_hex(tree_size=tree_size, root_hash=root_hash)
    now = datetime.now(timezone.utc).isoformat()

    if paths["ots"].exists() and not force:
        meta = _read_json(paths["meta"]) or {}
        return {
            "ok": True,
            "event": "already_stamped",
            "spec": SPEC,
            "tree_size": tree_size,
            "root_hash": root_hash,
            "commitment_digest": digest,
            "ots_path": str(paths["ots"]),
            "meta": meta,
        }

    commitment = commitment_bytes(tree_size=tree_size, root_hash=root_hash)
    paths["commitment"].parent.mkdir(parents=True, exist_ok=True)
    paths["commitment"].write_bytes(commitment)

    # Prefer CLI when present (same path strangers use); else library.
    result = _stamp_via_cli(paths["commitment"], paths["ots"])
    if not result.get("ok"):
        result = _stamp_via_library(bytes.fromhex(digest), paths["ots"])
        if not result.get("ok"):
            # Last resort: write digest-named file and stamp via CLI without custom calendars.
            with tempfile.TemporaryDirectory() as tmp:
                msg = Path(tmp) / "commitment.json"
                msg.write_bytes(commitment)
                cli = _ots_cli()
                if not cli:
                    return {**result, "spec": SPEC, "commitment_digest": digest}
                proc = subprocess.run(
                    [cli, "stamp", str(msg)],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                produced = Path(str(msg) + ".ots")
                if not produced.exists():
                    return {
                        "ok": False,
                        "spec": SPEC,
                        "error": "stamp_all_methods_failed",
                        "cli_stderr": (proc.stderr or "")[-600:],
                        "prior": result,
                        "commitment_digest": digest,
                    }
                paths["ots"].parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(produced, paths["ots"])
                result = {"ok": True, "method": "ots_cli_default_calendars"}

    meta = {
        "spec": SPEC,
        "stamped_at": now,
        "tree_size": tree_size,
        "root_hash": root_hash,
        "commitment_digest": digest,
        "commitment_path": str(paths["commitment"]),
        "ots_path": str(paths["ots"]),
        "status": "pending",
        "bitcoin": None,
        "stamp": {k: v for k, v in result.items() if k != "ok"},
    }
    _write_json(paths["meta"], meta)
    state = _read_json(paths["state"]) or {"spec": SPEC, "anchors": []}
    anchors = [a for a in state.get("anchors") or [] if a.get("slug") != paths["slug"]]
    anchors.append(
        {
            "slug": paths["slug"],
            "tree_size": tree_size,
            "root_hash": root_hash,
            "commitment_digest": digest,
            "stamped_at": now,
            "status": "pending",
        }
    )
    state["anchors"] = anchors[-50:]
    state["last_stamp"] = anchors[-1]
    state["updated_at"] = now
    _write_json(paths["state"], state)
    return {"ok": True, "event": "stamped", **meta}


def _parse_info(text: str) -> dict[str, Any]:
    """Parse `ots info` output for pending vs Bitcoin block height."""
    pending: list[str] = []
    bitcoin_heights: list[int] = []
    for line in (text or "").splitlines():
        s = line.strip()
        if "PendingAttestation" in s:
            # PendingAttestation('https://...')
            start = s.find("'")
            end = s.rfind("'")
            if start >= 0 and end > start:
                pending.append(s[start + 1 : end])
            else:
                pending.append(s)
        if "BitcoinBlockHeaderAttestation" in s:
            # verify BitcoinBlockHeaderAttestation(123456)
            paren = s.rfind("(")
            close = s.rfind(")")
            if paren >= 0 and close > paren:
                try:
                    bitcoin_heights.append(int(s[paren + 1 : close]))
                except ValueError:
                    pass
    status = "bitcoin_confirmed" if bitcoin_heights else ("pending" if pending else "unknown")
    return {
        "status": status,
        "pending_calendars": pending,
        "bitcoin_block_heights": bitcoin_heights,
        "bitcoin_block_height": min(bitcoin_heights) if bitcoin_heights else None,
    }


def upgrade_proof(*, tree_size: int, root_hash: str) -> dict[str, Any]:
    """Ask calendars to upgrade a pending .ots to a Bitcoin attestation."""
    root_hash = (root_hash or "").strip().lower()
    paths = _paths(tree_size=tree_size, root_hash=root_hash)
    if not paths["ots"].exists():
        return {"ok": False, "error": "ots_missing", "ots_path": str(paths["ots"])}
    cli = _ots_cli()
    if not cli:
        return {"ok": False, "error": "ots_cli_missing"}
    proc = subprocess.run(
        [cli, "upgrade", str(paths["ots"])],
        capture_output=True,
        text=True,
        timeout=120,
    )
    info = subprocess.run(
        [cli, "info", str(paths["ots"])],
        capture_output=True,
        text=True,
        timeout=30,
    )
    parsed = _parse_info(info.stdout or "")
    now = datetime.now(timezone.utc).isoformat()
    meta = _read_json(paths["meta"]) or {
        "spec": SPEC,
        "tree_size": tree_size,
        "root_hash": root_hash,
        "commitment_digest": commitment_digest_hex(tree_size=tree_size, root_hash=root_hash),
        "ots_path": str(paths["ots"]),
    }
    meta["upgraded_at"] = now
    meta["status"] = parsed["status"]
    meta["bitcoin"] = {
        "block_height": parsed.get("bitcoin_block_height"),
        "block_heights": parsed.get("bitcoin_block_heights") or [],
        "pending_calendars": parsed.get("pending_calendars") or [],
    }
    meta["upgrade_stdout"] = (proc.stdout or "")[-600:]
    meta["upgrade_stderr"] = (proc.stderr or "")[-400:]
    meta["info"] = (info.stdout or "")[-1200:]
    _write_json(paths["meta"], meta)

    state = _read_json(paths["state"]) or {"spec": SPEC, "anchors": []}
    for a in state.get("anchors") or []:
        if a.get("slug") == paths["slug"]:
            a["status"] = parsed["status"]
            a["bitcoin_block_height"] = parsed.get("bitcoin_block_height")
            a["upgraded_at"] = now
    state["last_upgrade"] = {
        "slug": paths["slug"],
        "status": parsed["status"],
        "bitcoin_block_height": parsed.get("bitcoin_block_height"),
        "at": now,
    }
    state["updated_at"] = now
    _write_json(paths["state"], state)

    verified = None
    if parsed["status"] == "bitcoin_confirmed" and paths["commitment"].exists():
        # Verify against Bitcoin block headers via ots verify (uses explorers if no node).
        ver = subprocess.run(
            [cli, "verify", str(paths["ots"]), "-f", str(paths["commitment"])],
            capture_output=True,
            text=True,
            timeout=120,
        )
        verified = {
            "ok": ver.returncode == 0,
            "stdout": (ver.stdout or "")[-800:],
            "stderr": (ver.stderr or "")[-400:],
        }
        meta["verify"] = verified
        _write_json(paths["meta"], meta)

    return {
        "ok": True,
        "spec": SPEC,
        "tree_size": tree_size,
        "root_hash": root_hash,
        "status": parsed["status"],
        "bitcoin_block_height": parsed.get("bitcoin_block_height"),
        "upgrade_returncode": proc.returncode,
        "verify": verified,
        "ots_path": str(paths["ots"]),
        "meta": meta,
    }


def latest_anchor() -> dict[str, Any] | None:
    state = _read_json(ots_dir() / "state.json")
    if not state:
        return None
    last = state.get("last_stamp") or (state.get("anchors") or [None])[-1]
    if not last:
        return None
    tree_size = int(last.get("tree_size") or 0)
    root_hash = (last.get("root_hash") or "").strip().lower()
    paths = _paths(tree_size=tree_size, root_hash=root_hash)
    meta = _read_json(paths["meta"]) or {}
    return {
        "spec": SPEC,
        "tree_size": tree_size,
        "root_hash": root_hash,
        "commitment_digest": last.get("commitment_digest")
        or commitment_digest_hex(tree_size=tree_size, root_hash=root_hash),
        "status": meta.get("status") or last.get("status") or "unknown",
        "bitcoin": meta.get("bitcoin"),
        "stamped_at": meta.get("stamped_at") or last.get("stamped_at"),
        "upgraded_at": meta.get("upgraded_at"),
        "ots_present": paths["ots"].exists(),
        "ots_bytes": paths["ots"].stat().st_size if paths["ots"].exists() else 0,
        "slug": paths["slug"],
        "verify": meta.get("verify"),
    }


def attach_to_tree_head(head: dict[str, Any]) -> dict[str, Any]:
    """Add `opentimestamps` capacity block to a signed tree head (mutates copy)."""
    out = dict(head)
    if not enabled():
        out["opentimestamps"] = {
            "spec": SPEC,
            "configured": False,
            "plain": "GATE_OTS_ENABLED=0",
        }
        return out

    root_hash = (out.get("root_hash") or "").strip().lower()
    tree_size = int(out.get("tree_size") or 0)
    paths = _paths(tree_size=tree_size, root_hash=root_hash)
    meta = _read_json(paths["meta"])
    latest = latest_anchor()

    # Prefer exact match for this head; else report latest known anchor.
    if meta and paths["ots"].exists():
        block = {
            "spec": SPEC,
            "configured": True,
            "matches_this_head": True,
            "tree_size": tree_size,
            "root_hash": root_hash,
            "commitment_digest": meta.get("commitment_digest"),
            "status": meta.get("status") or "pending",
            "bitcoin": meta.get("bitcoin"),
            "stamped_at": meta.get("stamped_at"),
            "upgraded_at": meta.get("upgraded_at"),
            "ots_bytes": paths["ots"].stat().st_size,
            "urls": {
                "proof": "/.well-known/evidence-head.ots",
                "commitment": "/.well-known/evidence-ots-commitment.json",
                "status": "/.well-known/evidence-ots.json",
            },
            "plain": (
                "OpenTimestamps proof over sha256(canonical commitment of "
                "tree_size+root_hash). Pending until a calendar anchors in Bitcoin; "
                "then strangers verify against block headers — Gate cannot rewrite "
                "history cheaper than reorging Bitcoin."
            ),
            "not_worldly_truth": (
                "OTS proves publication time of the commitment, not that the "
                "underlying receipts are correct about the world."
            ),
        }
    elif latest:
        block = {
            "spec": SPEC,
            "configured": True,
            "matches_this_head": False,
            "latest": latest,
            "urls": {
                "proof": "/.well-known/evidence-head.ots",
                "commitment": "/.well-known/evidence-ots-commitment.json",
                "status": "/.well-known/evidence-ots.json",
            },
            "plain": (
                "Latest OTS anchor exists but does not match this exact head "
                "(tree grew or empty head re-signed). Run periodic stamp."
            ),
            "not_worldly_truth": (
                "OTS proves publication time of the commitment, not worldly fact."
            ),
        }
    else:
        block = {
            "spec": SPEC,
            "configured": False,
            "matches_this_head": False,
            "status": "unanchored",
            "urls": {"status": "/.well-known/evidence-ots.json"},
            "plain": (
                "Bitcoin-anchor capacity: run `python3 -m gate.ots_anchor stamp` "
                "(or gate/anchor_evidence_head.py) against this head. Public "
                "calendars; no fee. Same mechanism Internet Archive used for ~750M files."
            ),
            "not_worldly_truth": (
                "OTS proves publication time of the commitment, not worldly fact."
            ),
        }
    out["opentimestamps"] = block
    return out


def read_ots_bytes_for_head(*, tree_size: int, root_hash: str) -> bytes | None:
    paths = _paths(tree_size=tree_size, root_hash=root_hash)
    if paths["ots"].exists():
        return paths["ots"].read_bytes()
    latest = latest_anchor()
    if not latest:
        return None
    p = _paths(tree_size=int(latest["tree_size"]), root_hash=latest["root_hash"])
    if p["ots"].exists():
        return p["ots"].read_bytes()
    return None


def status_payload(public_url: str = "") -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    latest = latest_anchor()
    return {
        "spec": SPEC,
        "enabled": enabled(),
        "ots_dir": str(ots_dir()),
        "calendars": list(DEFAULT_CALENDARS),
        "latest": latest,
        "urls": {
            "head": f"{base}/.well-known/evidence-head.json" if base else "/.well-known/evidence-head.json",
            "proof": f"{base}/.well-known/evidence-head.ots" if base else "/.well-known/evidence-head.ots",
            "commitment": (
                f"{base}/.well-known/evidence-ots-commitment.json"
                if base
                else "/.well-known/evidence-ots-commitment.json"
            ),
        },
        "verify_cli": "ots verify evidence-head.ots -f evidence-ots-commitment.json",
        "upgrade_cli": "python3 -m gate.ots_anchor upgrade",
        "citation": {
            "opentimestamps": "https://opentimestamps.org/",
            "internet_archive_750m": "https://petertodd.org/2017/carbon-dating-the-internet-archive-with-opentimestamps",
        },
        "their_production": False,
    }


def main(argv: list[str] | None = None) -> int:
    import argparse
    import urllib.request

    parser = argparse.ArgumentParser(description="Stamp/upgrade Gate evidence-head via OpenTimestamps")
    parser.add_argument("command", choices=["stamp", "upgrade", "status", "stamp-url"])
    parser.add_argument("--url", default="https://gate.velaru.xyz", help="Gate origin for stamp-url")
    parser.add_argument("--tree-size", type=int)
    parser.add_argument("--root-hash")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    if args.command == "status":
        print(json.dumps(status_payload(), indent=2))
        return 0

    if args.command == "stamp-url":
        head_url = args.url.rstrip("/") + "/.well-known/evidence-head.json"
        with urllib.request.urlopen(head_url, timeout=30) as resp:
            head = json.loads(resp.read().decode("utf-8"))
        tree_size = int(head.get("tree_size") or 0)
        root_hash = head.get("root_hash") or ""
        out = stamp_root(tree_size=tree_size, root_hash=root_hash, force=args.force)
        print(json.dumps(out, indent=2))
        return 0 if out.get("ok") else 2

    if args.tree_size is None or not args.root_hash:
        # Default: empty-tree EMPTY_LEAF from evidence_log if local import works.
        try:
            from gate import evidence_log as el
        except ImportError:
            import evidence_log as el  # type: ignore

        tree_size = args.tree_size if args.tree_size is not None else 0
        root_hash = args.root_hash or el.merkle_root([])
    else:
        tree_size = args.tree_size
        root_hash = args.root_hash

    if args.command == "stamp":
        out = stamp_root(tree_size=tree_size, root_hash=root_hash, force=args.force)
        print(json.dumps(out, indent=2))
        return 0 if out.get("ok") else 2

    out = upgrade_proof(tree_size=tree_size, root_hash=root_hash)
    print(json.dumps(out, indent=2))
    return 0 if out.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
