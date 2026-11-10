"""Public corrections ledger for this mouth (bugs 7, 11)."""
from __future__ import annotations

ENTRIES = (
    {
        "date": "2026-08-17",
        "id": "verra-name-retired",
        "status": "open_until_demo_copy_clears",
        "claim": "Public name is Velaru. Gate is the commercial mouth. The name Verra is retired.",
        "live_contradiction": (
            "velaru.xyz/demo/bind-room still mints session ids prefixed verra- and "
            "downloads verra-bind-room-*.json. Gate's demo uses bind- prefixes."
        ),
        "resolution": (
            "Bind Room is the live product name. /verra on velaru is an alias, not a sixth brand. "
            "Kudurru (consumer card) is a later brand and is not Verra revived."
        ),
    },
    {
        "date": "2026-08-26",
        "id": "verra-route-retired",
        "status": "resolved_on_gate",
        "claim": "The Bind Room door is gate.velaru.xyz/bind-room (paid officer pack) and /demo/bind-room (free vertical demo).",
        "live_contradiction": None,
        "resolution": "Gate /trust/corrections is this ledger. It does not redirect.",
    },
    {
        "date": "2026-11-10",
        "id": "mandate-registry-was-insurance",
        "status": "resolved_on_gate",
        "claim": "/compliance/mandate-registry is a registry of mandates, not the insurance marketing page.",
        "live_contradiction": "velaru.xyz/compliance/mandate-registry currently 301s to /insurance.",
        "resolution": "Gate serves /compliance/mandate-registry as a list. Velaru site still needs the same fix.",
    },
)
