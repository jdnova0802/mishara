"""Join pack: two halves, a live window, draft is not go.

Stranger recomputes join_sha256 from the public body plus both halves.
Same halves + same body → same hash. Missing sealer, same half twice,
or now outside the window → never GO.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from typing import Any

SPEC = "join-pack-v1"
KEYS = (
    "spec",
    "what",
    "not_before",
    "not_after",
    "starter_id",
    "sealer_id",
)


def _die(msg: str, code: int = 2) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def canonical_body(pack: dict[str, Any]) -> bytes:
    body = {k: pack[k] for k in KEYS if k in pack}
    return json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "utf-8"
    )


def join_sha256(pack: dict[str, Any], starter_half: str, sealer_half: str) -> str:
    material = (
        starter_half.encode("utf-8")
        + b"\n"
        + sealer_half.encode("utf-8")
        + b"\n"
        + canonical_body(pack)
    )
    return hashlib.sha256(material).hexdigest()


def _parse_utc(s: Any) -> datetime | None:
    if not isinstance(s, str) or not s.strip():
        return None
    raw = s.strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def reasons_not_go(
    pack: dict[str, Any],
    starter_half: str,
    sealer_half: str,
    now: datetime | None = None,
) -> list[str]:
    why: list[str] = []
    if not isinstance(pack, dict):
        return ["pack is not an object"]
    extra = set(pack) - set(KEYS) - {"join_sha256"}
    if extra:
        why.append("unknown fields: " + ",".join(sorted(extra)))
    missing = [k for k in KEYS if k not in pack]
    if missing:
        why.append("missing: " + ",".join(missing))
        return why
    if pack.get("spec") != SPEC:
        why.append("spec must be " + SPEC)
    what = pack.get("what")
    if not isinstance(what, str) or not what.strip():
        why.append("what blank")
    for key in ("starter_id", "sealer_id"):
        val = pack.get(key)
        if not isinstance(val, str) or not val.strip():
            why.append(key + " blank")
    if (
        isinstance(pack.get("starter_id"), str)
        and isinstance(pack.get("sealer_id"), str)
        and pack.get("starter_id", "").strip()
        and pack.get("starter_id").strip() == pack.get("sealer_id", "").strip()
    ):
        why.append("starter_id and sealer_id must differ")
    if not isinstance(starter_half, str) or not starter_half.strip():
        why.append("starter half blank")
    if not isinstance(sealer_half, str) or not sealer_half.strip():
        why.append("sealer half blank")
    if starter_half.strip() and sealer_half.strip() and starter_half.strip() == sealer_half.strip():
        why.append("halves must differ (starter cannot seal own)")
    start = _parse_utc(pack.get("not_before"))
    end = _parse_utc(pack.get("not_after"))
    if start is None:
        why.append("not_before not a time")
    if end is None:
        why.append("not_after not a time")
    if start is not None and end is not None and end <= start:
        why.append("window empty")
    clock = now if now is not None else datetime.now(timezone.utc)
    if start is not None and end is not None:
        if clock < start:
            why.append("window not open yet")
        if clock > end:
            why.append("window dead")
    stated = pack.get("join_sha256")
    if not isinstance(stated, str) or len(stated) != 64:
        why.append("join_sha256 missing (draft is not go)")
    elif starter_half.strip() and sealer_half.strip():
        expect = join_sha256(pack, starter_half.strip(), sealer_half.strip())
        if stated != expect:
            why.append("join_sha256 mismatch")
    return why


def attach_join(pack: dict[str, Any], starter_half: str, sealer_half: str) -> dict[str, Any]:
    out = {k: pack[k] for k in KEYS if k in pack}
    out["join_sha256"] = join_sha256(out, starter_half.strip(), sealer_half.strip())
    return out


def verdict(
    pack: dict[str, Any],
    starter_half: str,
    sealer_half: str,
    now: datetime | None = None,
) -> str:
    return "GO" if not reasons_not_go(pack, starter_half, sealer_half, now) else "NO"


def load(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        _die("pack is not an object")
    return data


def _read_half(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read().strip()


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ("-h", "--help"):
        print("usage: python3 -m join.pack seal <starter.half> <sealer.half> <in.json> <out.json>")
        print("       python3 -m join.pack verify <starter.half> <sealer.half> <pack.json>")
        print("       python3 -m join.pack boom <starter.half> <sealer.half> <pack.json>")
        print("GO only when both halves fit, ids differ, and now is inside the window.")
        print("Toy boom: prints GO/NO. Not a real harbor.")
        return 2
    cmd = args[0]
    if cmd == "seal":
        if len(args) != 5:
            _die("usage: python3 -m join.pack seal <starter.half> <sealer.half> <in.json> <out.json>")
        starter = _read_half(args[1])
        sealer = _read_half(args[2])
        raw = load(args[3])
        raw.pop("join_sha256", None)
        out = attach_join(raw, starter, sealer)
        with open(args[4], "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, sort_keys=True)
            f.write("\n")
        why = reasons_not_go(out, starter, sealer)
        print("GO" if not why else "NO")
        for line in why:
            print(line, file=sys.stderr)
        return 0 if not why else 1
    if cmd in ("verify", "boom"):
        if len(args) != 4:
            _die("usage: python3 -m join.pack " + cmd + " <starter.half> <sealer.half> <pack.json>")
        starter = _read_half(args[1])
        sealer = _read_half(args[2])
        pack = load(args[3])
        why = reasons_not_go(pack, starter, sealer)
        print("GO" if not why else "NO")
        for line in why:
            print(line, file=sys.stderr)
        return 0 if not why else 1
    _die("unknown command: " + cmd)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
