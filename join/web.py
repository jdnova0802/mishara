"""Tiny join booth. Same pack as the CLI. Not a harbor. Not Palantir."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from join.pack import SPEC, attach_join, reasons_not_go

ROOT = Path(__file__).resolve().parent
PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Join — toy boom</title>
<style>
  :root { --bg:#07090c; --ink:#e8e0d0; --mute:#8a8478; --yes:#c4a35a; --no:#8f3a32; --line:#2a2620; }
  * { box-sizing: border-box; }
  body { margin:0; font-family: ui-sans-serif, system-ui, sans-serif; background:var(--bg); color:var(--ink); }
  main { max-width: 720px; margin: 0 auto; padding: 32px 20px 64px; }
  h1 { font-weight: 500; letter-spacing: .12em; text-transform: uppercase; font-size: 13px; color: var(--yes); }
  p.lead { color: var(--mute); line-height: 1.5; }
  label { display:block; font-size: 12px; color: var(--mute); margin: 14px 0 6px; }
  input { width:100%; padding: 12px 14px; background:#10141a; border:1px solid var(--line); color:var(--ink); border-radius: 2px; }
  .row { display:grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  button { margin-top: 22px; width:100%; padding: 16px; border:0; background: var(--yes); color:#111; font-weight: 600; letter-spacing:.16em; text-transform:uppercase; cursor:pointer; }
  #out { margin-top: 28px; padding: 28px; text-align:center; border:1px solid var(--line); font-size: 42px; letter-spacing:.2em; }
  #out.go { border-color: var(--yes); color: var(--yes); }
  #out.no { border-color: var(--no); color: var(--no); }
  #why { color: var(--mute); font-size: 13px; white-space: pre-wrap; min-height: 3em; }
</style>
</head>
<body>
<main>
  <h1>Join booth</h1>
  <p class="lead">Two halves. A window. Draft is not go. Toy boom — not a real harbor.</p>
  <div class="row">
    <div>
      <label>Starter half</label>
      <input id="starter_half" value="starter-half-alpha"/>
    </div>
    <div>
      <label>Sealer half</label>
      <input id="sealer_half" value="sealer-half-bravo"/>
    </div>
  </div>
  <div class="row">
    <div>
      <label>Starter id</label>
      <input id="starter_id" value="watch-a"/>
    </div>
    <div>
      <label>Sealer id</label>
      <input id="sealer_id" value="watch-b"/>
    </div>
  </div>
  <label>What may go</label>
  <input id="what" value="boom"/>
  <div class="row">
    <div>
      <label>Window opens</label>
      <input id="not_before" value="2026-01-01T00:00:00+00:00"/>
    </div>
    <div>
      <label>Window dies</label>
      <input id="not_after" value="2026-12-31T23:59:59+00:00"/>
    </div>
  </div>
  <button id="go" type="button">Join</button>
  <div id="out">WAIT</div>
  <p id="why"></p>
</main>
<script>
async function run() {
  const body = {};
  for (const id of ["starter_half","sealer_half","starter_id","sealer_id","what","not_before","not_after"]) {
    body[id] = document.getElementById(id).value;
  }
  const r = await fetch("/boom", {method:"POST", headers:{"content-type":"application/json"}, body: JSON.stringify(body)});
  const j = await r.json();
  const out = document.getElementById("out");
  out.textContent = j.verdict;
  out.className = j.verdict === "GO" ? "go" : "no";
  document.getElementById("why").textContent = (j.reasons || []).join("\n");
}
document.getElementById("go").onclick = run;
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: object) -> None:
        return

    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("content-type", ctype)
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if urlparse(self.path).path != "/":
            self._send(404, b"no", "text/plain")
            return
        self._send(200, PAGE.encode("utf-8"), "text/html; charset=utf-8")

    def do_POST(self) -> None:  # noqa: N802
        if urlparse(self.path).path != "/boom":
            self._send(404, b"no", "text/plain")
            return
        n = int(self.headers.get("content-length") or "0")
        raw = json.loads(self.rfile.read(n).decode("utf-8") or "{}")
        starter = str(raw.get("starter_half") or "")
        sealer = str(raw.get("sealer_half") or "")
        body = {
            "spec": SPEC,
            "what": raw.get("what") or "",
            "not_before": raw.get("not_before") or "",
            "not_after": raw.get("not_after") or "",
            "starter_id": raw.get("starter_id") or "",
            "sealer_id": raw.get("sealer_id") or "",
        }
        draft = not sealer.strip()
        pack = body if draft else attach_join(body, starter, sealer)
        why = reasons_not_go(pack, starter, sealer, datetime.now(timezone.utc))
        payload = json.dumps({"verdict": "GO" if not why else "NO", "reasons": why}).encode()
        self._send(200, payload, "application/json")


def main() -> None:
    port = 8765
    print(f"join booth http://127.0.0.1:{port}/  (toy boom, not a harbor)", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
