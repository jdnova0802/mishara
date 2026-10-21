"""Already-built doors: MCP, OpenAPI, x402, CLI — not a roadmap."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ.setdefault(
    "GATE_DB_PATH", os.path.join(tempfile.gettempdir(), "gate-test-protocol-surface.db")
)

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import protocol_surface  # noqa: E402


class ProtocolSurfaceTests(unittest.TestCase):
    def test_doors_are_built_not_a_roadmap(self):
        doors = protocol_surface.doors("https://gate.example")
        ids = [d["id"] for d in doors]
        self.assertEqual(ids, ["mcp", "openapi", "x402", "cli"])
        for d in doors:
            self.assertEqual(d["status"], "built")
            self.assertNotIn("roadmap", d["plain"].lower())
        self.assertTrue(doors[0]["endpoint"].endswith("/mcp"))
        self.assertIn("openapi.json", doors[1]["href"])
        self.assertIn("x402.json", doors[2]["href"])
        self.assertTrue(doors[0]["plain"].startswith("Streamable HTTP MCP"))
        manifest = protocol_surface.manifest("https://gate.example")
        self.assertNotIn("their_production", manifest)
        self.assertIn("chatbot", manifest["note"].lower())
        self.assertEqual(manifest["spec"], "gate-already-built-v1")


if __name__ == "__main__":
    unittest.main()
