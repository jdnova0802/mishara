"""Local action gate — one computer, one allowlisted command.

An automated caller may run a command only by asking this process.
The process signs a fact record before it execs. If it cannot sign,
it does not exec. The record names the argv, the principal, the rule,
and whether the process ran the command. It does not say the command
was reasonable, correct, or explained.

No shell. argv is a list. The allowlist is exact.
"""
from __future__ import annotations

import base64
import hashlib
import json
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable

try:
    from gate import offline_verify
    from gate import receipt as receipt_mod
except ImportError:
    import offline_verify
    import receipt as receipt_mod

SPEC = "gate-receipt-v1"
BODY = "gate-local-action-v1"
# Exact argv only. Adding a command means adding a row, not a pattern.
ALLOWLIST: dict[tuple[str, ...], str] = {
    ("echo", "ok"): "echo-ok",
}
EXEC_TIMEOUT_SECONDS = 2
NOT_CLAIMED = [
    "that the command was reasonable",
    "that the command was correct",
    "that an explanation of the decision was adequate",
]


class SignerDown(Exception):
    """The signer could not produce a signature. The command must not run."""


class EphemeralSigner:
    """Process-local Ed25519 key. Not the Gate receipt key."""

    def __init__(self) -> None:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

        self._key = Ed25519PrivateKey.generate()
        self.public_bytes = self._key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)

    def sign(self, receipt_hash: str) -> str:
        return base64.b64encode(self._key.sign(receipt_hash.encode("utf-8"))).decode("utf-8")


class BrokenSigner:
    """Test double. Signing is unavailable."""

    public_bytes = b"\x00" * 32

    def sign(self, receipt_hash: str) -> str:
        raise SignerDown("signer_unavailable")


def public_key_b64(signer: EphemeralSigner | BrokenSigner) -> str:
    return base64.b64encode(signer.public_bytes).decode("utf-8")


def _fingerprint(pub: bytes) -> str:
    return hashlib.sha256(pub).hexdigest()[:16]


def _argv_error(argv: Any) -> str | None:
    if not isinstance(argv, list) or not argv:
        return "argv_not_a_list"
    for part in argv:
        if not isinstance(part, str) or part == "" or "\x00" in part or "\n" in part or "\r" in part:
            return "argv_part_invalid"
    return None


def _principal_error(principal: Any) -> str | None:
    if not isinstance(principal, str):
        return "principal_required"
    name = principal.strip()
    if not name or len(name) > 80:
        return "principal_required"
    return None


def _seal(signer: EphemeralSigner | BrokenSigner, body: dict[str, Any]) -> dict[str, Any]:
    canonical = dict(body)
    canonical["spec"] = SPEC
    raw = receipt_mod.canonical_dumps(canonical)
    digest = receipt_mod.compute_receipt_hash(raw)
    try:
        signature = signer.sign(digest)
    except SignerDown:
        raise
    except Exception as exc:
        raise SignerDown("signer_unavailable") from exc
    if not signature:
        raise SignerDown("signer_unavailable")
    return {
        "spec": SPEC,
        "canonical_receipt": canonical,
        "canonical_receipt_json": raw,
        "receipt_hash": digest,
        "receipt_signature": signature,
        "receipt_public_key_fingerprint": _fingerprint(signer.public_bytes),
    }


def decide(argv: Any, principal: Any) -> dict[str, Any]:
    """Allow or refuse. Does not exec and does not sign."""
    perr = _principal_error(principal)
    if perr:
        return {"decision": "refused", "reason": perr, "rule_id": None, "argv": None}
    aerr = _argv_error(argv)
    if aerr:
        return {"decision": "refused", "reason": aerr, "rule_id": None, "argv": None}
    key = tuple(argv)
    rule_id = ALLOWLIST.get(key)
    if rule_id is None:
        return {
            "decision": "refused",
            "reason": "not_on_allowlist",
            "rule_id": None,
            "argv": list(key),
        }
    return {
        "decision": "allow",
        "reason": None,
        "rule_id": rule_id,
        "argv": list(key),
    }


def _authorization_body(principal: str, verdict: dict[str, Any]) -> dict[str, Any]:
    return {
        "record": BODY,
        "phase": "authorization",
        "principal": principal.strip(),
        "argv": verdict["argv"],
        "rule_id": verdict["rule_id"],
        "decision": verdict["decision"],
        "refusal": verdict["reason"],
        "executed": False,
        "signed_before_exec": True,
        "not_claimed": NOT_CLAIMED,
    }


def act(
    argv: Any,
    principal: Any,
    signer: EphemeralSigner | BrokenSigner,
    *,
    runner: Callable[[list[str]], subprocess.CompletedProcess[str]] | None = None,
) -> dict[str, Any]:
    """Sign the authorization, then exec only if the rule allows and the signature exists."""
    verdict = decide(argv, principal)
    if verdict["reason"] in {"principal_required", "argv_not_a_list", "argv_part_invalid"}:
        return {
            "executed": False,
            "fail_closed": False,
            "reason": verdict["reason"],
            "authorization": None,
            "result": None,
        }
    try:
        authorization = _seal(signer, _authorization_body(str(principal), verdict))
    except SignerDown:
        return {
            "executed": False,
            "fail_closed": True,
            "reason": "signer_unavailable",
            "authorization": None,
            "result": None,
        }

    if verdict["decision"] != "allow":
        return {
            "executed": False,
            "fail_closed": False,
            "reason": verdict["reason"],
            "authorization": authorization,
            "result": None,
        }

    run = runner or _run
    completed = run(list(verdict["argv"]))
    stdout = completed.stdout or ""
    result_body = {
        "record": BODY,
        "phase": "result",
        "authorization_hash": authorization["receipt_hash"],
        "argv": verdict["argv"],
        "exit_code": completed.returncode,
        "stdout_sha256": hashlib.sha256(stdout.encode("utf-8")).hexdigest(),
        "timed_out": completed.returncode is None,
        "not_claimed": NOT_CLAIMED,
    }
    try:
        result = _seal(signer, result_body)
    except SignerDown:
        result = None
    return {
        "executed": True,
        "fail_closed": False,
        "reason": None,
        "stdout": stdout,
        "exit_code": completed.returncode,
        "authorization": authorization,
        "result": result,
        "result_sign_failed": result is None,
    }


def _run(argv: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            argv,
            shell=False,
            capture_output=True,
            text=True,
            timeout=EXEC_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout or ""
        if isinstance(out, bytes):
            out = out.decode("utf-8", errors="replace")
        return subprocess.CompletedProcess(argv, None, stdout=out, stderr="")


def verify_authorization(document: dict[str, Any], signer: EphemeralSigner | BrokenSigner) -> dict[str, Any]:
    return offline_verify.verify_document(document, signer.public_bytes)


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Local action gate</title>
<style>
  body { font-family: ui-sans-serif, system-ui, sans-serif; margin: 2rem auto; max-width: 42rem; line-height: 1.45; color: #1a1a1a; }
  button { margin: 0 0.5rem 0.5rem 0; padding: 0.4rem 0.7rem; }
  pre { background: #f4f4f4; padding: 1rem; overflow: auto; font-size: 0.85rem; }
  p.note { color: #444; }
</style>
</head>
<body>
<h1>Local action gate</h1>
<p>This process is the only door for one command on this computer: <code>echo ok</code>. It signs a record of the ask before it runs anything. If it cannot sign, it does not run the command.</p>
<p class="note">The record names the argv, who asked, and the allowlist rule. It does not say the command was reasonable or that anyone explained it.</p>
<button id="allow" type="button">Run echo ok</button>
<button id="deny" type="button">Ask for rm</button>
<button id="down" type="button">Signer down</button>
<pre id="out">Nothing has run.</pre>
<script>
async function post(path, body) {
  const res = await fetch(path, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body)});
  const data = await res.json();
  document.getElementById("out").textContent = JSON.stringify(data, null, 2);
}
document.getElementById("allow").onclick = () => post("/act", {argv: ["echo", "ok"], principal: "operator"});
document.getElementById("deny").onclick = () => post("/act", {argv: ["rm", "-rf", "/"], principal: "operator"});
document.getElementById("down").onclick = () => post("/act-signer-down", {argv: ["echo", "ok"], principal: "operator"});
</script>
</body>
</html>
"""


def make_handler(signer: EphemeralSigner):
    broken = BrokenSigner()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: Any) -> None:
            return

        def _json(self, code: int, payload: dict[str, Any]) -> None:
            raw = json.dumps(payload).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def _read(self) -> Any:
            length = int(self.headers.get("Content-Length") or "0")
            if length > 8192:
                return None
            try:
                return json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            except json.JSONDecodeError:
                return None

        def do_GET(self) -> None:  # noqa: N802
            if self.path != "/":
                self._json(404, {"reason": "not_found"})
                return
            raw = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_POST(self) -> None:  # noqa: N802
            body = self._read()
            if not isinstance(body, dict):
                self._json(400, {"reason": "body_not_json"})
                return
            which = signer if self.path == "/act" else broken if self.path == "/act-signer-down" else None
            if which is None:
                self._json(404, {"reason": "not_found"})
                return
            outcome = act(body.get("argv"), body.get("principal"), which)
            public = {
                "executed": outcome["executed"],
                "fail_closed": outcome["fail_closed"],
                "reason": outcome["reason"],
                "stdout": outcome.get("stdout"),
                "exit_code": outcome.get("exit_code"),
                "authorization": outcome["authorization"],
                "result": outcome["result"],
                "public_key_b64": public_key_b64(signer) if which is signer and outcome["authorization"] else None,
            }
            self._json(200, public)

    return Handler


def serve(host: str = "127.0.0.1", port: int = 8765) -> None:
    signer = EphemeralSigner()
    httpd = ThreadingHTTPServer((host, port), make_handler(signer))
    print(f"local action gate http://{host}:{port}", flush=True)
    print(f"public_key_b64 {public_key_b64(signer)}", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    serve()
