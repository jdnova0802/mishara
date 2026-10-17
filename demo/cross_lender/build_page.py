"""Write index.html with the ledger and the match report embedded."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ledger import build
from match import analyze, solo_exceptions

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "page_template.html"
OUT = ROOT / "index.html"


def main() -> None:
    ledger = build()
    payload = {
        "ledger": ledger,
        "report": analyze(ledger),
        "solo": solo_exceptions(ledger),
    }
    html = TEMPLATE.read_text()
    blob = json.dumps(payload, indent=2)
    if "__PAYLOAD__" not in html:
        raise SystemExit("page template is missing __PAYLOAD__")
    OUT.write_text(html.replace("__PAYLOAD__", blob))
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
