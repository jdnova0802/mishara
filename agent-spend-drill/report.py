"""Stranger-facing GO / NEVER page. Not a memo."""
from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


def public_word(decision: str | None) -> str:
    d = (decision or "").upper()
    if d == "GO":
        return "GO"
    return "NEVER"


def build_report(
    *,
    fixture: dict[str, Any],
    mouth_url: str,
    mouth_config: dict[str, Any],
    body: dict[str, Any],
) -> dict[str, Any]:
    gate = body.get("gate") if isinstance(body.get("gate"), dict) else {}
    word = public_word(body.get("decision"))
    expected = (fixture.get("expected_word") or "NEVER").upper()
    return {
        "spec": "gate-agent-spend-drill-report-v1",
        "word": word,
        "pass": word == expected,
        "expected_word": expected,
        "approved": bool(body.get("approved")),
        "decision": body.get("decision"),
        "halt": bool(body.get("halt")),
        "demo": bool(body.get("demo")),
        "money_real": bool(mouth_config.get("money_real")),
        "write_executed": bool(body.get("write_executed")),
        "gate_holds_funds": bool(body.get("gate_holds_funds")),
        "mouth_url": mouth_url,
        "mouth_spec": body.get("spec") or mouth_config.get("spec"),
        "agent_id": body.get("agent_id") or fixture.get("agent_id"),
        "signals": list(gate.get("signals") or []),
        "evaluation_id": gate.get("evaluation_id"),
        "verify_url": gate.get("verify_url"),
        "receipt": gate.get("receipt"),
        "fingerprint": gate.get("fingerprint"),
        "message": gate.get("message"),
        "elapsed_ms": body.get("elapsed_ms"),
        "fixture": {
            "agent_id": fixture.get("agent_id"),
            "amount_cents": (fixture.get("goal") or {}).get("amount_cents"),
            "max_amount": (fixture.get("limit") or {}).get("max_amount"),
            "expected_word": expected,
        },
    }


def render_html(report: dict[str, Any]) -> str:
    word = report["word"]
    tone = "#0d7a4f" if word == "NEVER" else "#1d4ed8"
    if word == "GO" and not report.get("pass"):
        tone = "#b42318"
    verify = report.get("verify_url") or ""
    receipt = report.get("receipt") or ""
    signals = ", ".join(report.get("signals") or []) or "—"
    eval_id = html.escape(str(report.get("evaluation_id") or "—"))
    fp = html.escape(str(report.get("fingerprint") or "—"))
    msg = html.escape(str(report.get("message") or "—"))
    fixture = report.get("fixture") or {}
    pass_line = "fixture matched" if report.get("pass") else "fixture mismatch"
    verify_block = (
        f'<p class="meta"><a href="{html.escape(verify)}">POST {html.escape(verify)}</a> with the receipt JWT.</p>'
        if verify
        else ""
    )
    receipt_block = (
        f"<pre>{html.escape(str(receipt))}</pre>" if receipt else "<p class=\"meta\">No JWT on this response.</p>"
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(word)} — agent spend drill</title>
  <style>
    :root {{ --ink:#12141a; --mute:#5c6573; --line:#d5dae3; }}
    body {{ margin:0; font-family: Figtree, ui-sans-serif, system-ui, sans-serif;
           background:#f7f8fb; color:var(--ink); }}
    main {{ max-width: 40rem; margin: 0 auto; padding: 3.5rem 1.25rem 5rem; }}
    .word {{ font-family: Syne, ui-sans-serif, system-ui, sans-serif; font-weight: 800;
             font-size: clamp(4rem, 16vw, 7rem); letter-spacing: -0.05em; line-height: 0.9;
             color: {tone}; margin: 0 0 0.75rem; }}
    .kicker {{ text-transform: uppercase; letter-spacing: 0.14em; font-size: 0.72rem;
               color: var(--mute); margin: 0 0 0.4rem; }}
    .lede {{ color: var(--mute); margin: 0 0 2rem; line-height: 1.45; }}
    dl {{ display: grid; grid-template-columns: 9rem 1fr; gap: 0.45rem 1rem; margin: 0 0 2rem; }}
    dt {{ color: var(--mute); font-size: 0.78rem; }}
    dd {{ margin: 0; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.78rem; word-break: break-all; }}
    pre {{ white-space: pre-wrap; word-break: break-all; background: #fff; border: 1px solid var(--line);
           padding: 0.85rem; font-size: 0.7rem; }}
    a {{ color: var(--ink); }}
    .meta {{ color: var(--mute); font-size: 0.85rem; }}
  </style>
</head>
<body>
<main>
  <p class="kicker">agent spend drill · issuing mouth</p>
  <h1 class="word">{html.escape(word)}</h1>
  <p class="lede">The executor tried to spend ${int(fixture.get("amount_cents") or 0)/100:.2f} against a ${html.escape(str(fixture.get("max_amount") or ""))} cap. {html.escape(pass_line)}. No login. money_real={html.escape(str(report.get("money_real")).lower())}. write_executed={html.escape(str(report.get("write_executed")).lower())}.</p>
  <dl>
    <dt>approved</dt><dd>{html.escape(str(report.get("approved")).lower())}</dd>
    <dt>decision</dt><dd>{html.escape(str(report.get("decision") or "—"))}</dd>
    <dt>signals</dt><dd>{html.escape(signals)}</dd>
    <dt>evaluation_id</dt><dd>{eval_id}</dd>
    <dt>fingerprint</dt><dd>{fp}</dd>
    <dt>agent_id</dt><dd>{html.escape(str(report.get("agent_id") or "—"))}</dd>
    <dt>mouth</dt><dd>{html.escape(str(report.get("mouth_url") or "—"))}</dd>
    <dt>message</dt><dd>{msg}</dd>
  </dl>
  {verify_block}
  <p class="kicker">receipt</p>
  {receipt_block}
</main>
</body>
</html>
"""


def write_report(report: dict[str, Any], out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "latest.json"
    html_path = out_dir / "latest.html"
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    html_path.write_text(render_html(report), encoding="utf-8")
    return json_path, html_path
