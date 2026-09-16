"""Emit and verify a fail-closed evidence pack.

A chat summary is not a pack. Missing fields never print YES.
Two people hashing the same body get the same pack_sha256.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from typing import Any

SPEC = "check-pack-v1"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
KEYS = (
    "spec",
    "task",
    "git_sha_before",
    "git_sha_after",
    "commands_run",
    "tests_run",
    "tests_pass",
    "files_touched",
    "claims",
    "what_it_did_not_do",
)


def _die(msg: str, code: int = 2) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def canonical_body(pack: dict[str, Any]) -> bytes:
    body = {k: pack[k] for k in KEYS if k in pack}
    return json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "utf-8"
    )


def pack_sha256(pack: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_body(pack)).hexdigest()


def _str_list(v: Any) -> bool:
    return isinstance(v, list) and all(isinstance(x, str) and x.strip() for x in v)


def _commands_ok(v: Any) -> bool:
    if not isinstance(v, list) or not v:
        return False
    for item in v:
        if not isinstance(item, dict):
            return False
        argv = item.get("argv")
        exit_code = item.get("exit_code")
        extra = set(item) - {"argv", "exit_code"}
        if extra:
            return False
        if not isinstance(argv, list) or not argv or not all(isinstance(a, str) for a in argv):
            return False
        if not isinstance(exit_code, int):
            return False
    return True


def _tests_ok(v: Any) -> bool:
    if not isinstance(v, list) or not v:
        return False
    for item in v:
        if not isinstance(item, dict):
            return False
        name = item.get("name")
        passed = item.get("passed")
        extra = set(item) - {"name", "passed"}
        if extra:
            return False
        if not isinstance(name, str) or not name.strip():
            return False
        if not isinstance(passed, bool):
            return False
    return True


def reasons_not_yes(pack: dict[str, Any]) -> list[str]:
    """Why this pack must not print YES. Empty list means YES."""
    why: list[str] = []
    if not isinstance(pack, dict):
        return ["pack is not an object"]
    extra = set(pack) - set(KEYS) - {"pack_sha256"}
    if extra:
        why.append("unknown fields: " + ",".join(sorted(extra)))
    missing = [k for k in KEYS if k not in pack]
    if missing:
        why.append("missing: " + ",".join(missing))
        return why
    if pack.get("spec") != SPEC:
        why.append("spec must be " + SPEC)
    task = pack.get("task")
    if not isinstance(task, str) or not task.strip():
        why.append("task blank")
    for key in ("git_sha_before", "git_sha_after"):
        val = pack.get(key)
        if not isinstance(val, str) or not SHA_RE.match(val):
            why.append(key + " not 40-hex")
    if not _commands_ok(pack.get("commands_run")):
        why.append("commands_run blank or malformed")
    if not _tests_ok(pack.get("tests_run")):
        why.append("tests_run blank or malformed")
    tests = pack.get("tests_run") if _tests_ok(pack.get("tests_run")) else []
    all_passed = bool(tests) and all(t["passed"] for t in tests)
    if pack.get("tests_pass") is not True:
        why.append("tests_pass is not true")
    elif not all_passed:
        why.append("tests_pass true but a test failed")
    files = pack.get("files_touched")
    if not _str_list(files) and files != []:
        why.append("files_touched malformed")
    before = pack.get("git_sha_before")
    after = pack.get("git_sha_after")
    if isinstance(files, list) and SHA_RE.match(str(before) or "") and SHA_RE.match(str(after) or ""):
        if before != after and not files:
            why.append("commit moved but files_touched empty")
        if before == after and files:
            why.append("files_touched set but git did not move")
    if not _str_list(pack.get("claims")):
        why.append("claims blank")
    if not _str_list(pack.get("what_it_did_not_do")):
        why.append("what_it_did_not_do blank")
    stated = pack.get("pack_sha256")
    if not isinstance(stated, str) or len(stated) != 64:
        why.append("pack_sha256 missing")
    else:
        expect = pack_sha256(pack)
        if stated != expect:
            why.append("pack_sha256 mismatch")
    return why


def attach_hash(pack: dict[str, Any]) -> dict[str, Any]:
    out = {k: pack[k] for k in KEYS if k in pack}
    out["pack_sha256"] = pack_sha256(out)
    return out


def verdict(pack: dict[str, Any]) -> str:
    return "YES" if not reasons_not_yes(pack) else "NO"


def emit_from_dict(raw: dict[str, Any]) -> dict[str, Any]:
    return attach_hash(raw)


def load(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        _die("pack is not an object")
    return data


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ("-h", "--help"):
        print("usage: python -m check.pack emit <in.json> <out.json>")
        print("       python -m check.pack verify <pack.json>")
        print("YES only when the pack is complete, hashed, and tests_pass.")
        return 2
    cmd = args[0]
    if cmd == "emit":
        if len(args) != 3:
            _die("usage: python -m check.pack emit <in.json> <out.json>")
        raw = load(args[1])
        raw.pop("pack_sha256", None)
        out = emit_from_dict(raw)
        with open(args[2], "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, sort_keys=True)
            f.write("\n")
        print(verdict(out))
        for line in reasons_not_yes(out):
            print(line, file=sys.stderr)
        return 0 if verdict(out) == "YES" else 1
    if cmd == "verify":
        if len(args) != 2:
            _die("usage: python -m check.pack verify <pack.json>")
        pack = load(args[1])
        why = reasons_not_yes(pack)
        print("YES" if not why else "NO")
        for line in why:
            print(line, file=sys.stderr)
        return 0 if not why else 1
    _die("unknown command: " + cmd)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
