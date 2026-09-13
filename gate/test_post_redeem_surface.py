"""Post-redeem surface: Gate-owned bind write after ticket consume?

CommitGuard method on the window *after* redeem succeeds.
Gate contract is clearance-only (write_executed always false). The irreversible
PolicyCenter bind-only write is external. This file proves what Gate owns, and
that require_live_at_effect refuses when parent dies after redeem.
"""
from __future__ import annotations

import os
import tempfile
import unittest
import uuid
from datetime import datetime, timezone

_fd, _DB = tempfile.mkstemp(suffix="-post-redeem.db")
os.close(_fd)
os.environ["GATE_DB_PATH"] = _DB
os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "post-redeem-test-secret")

import db  # noqa: E402
import license_fuse as license_fuse_mod  # noqa: E402
import ticket as ticket_mod  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class PostRedeemSurfaceTests(unittest.TestCase):
    def setUp(self):
        db.init_db()
        self.lid = f"lic:PR-{uuid.uuid4().hex[:10]}"
        self.job = f"pc:PR-{uuid.uuid4().hex[:10]}"
        db.upsert_license_parent(license_id=self.lid, state="LIVE", charge_id="chg_pr_seed")
        self.path = f"/job/v1/jobs/{self.job}/bind-only"
        pack = ticket_mod.issue(
            job_id=self.job,
            fuse_id="fuse_velaru_drill",
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            receipt_hash=f"rh_{uuid.uuid4().hex}",
            redeem_url="https://gate.test/v1/pas/bind-ticket/redeem",
            spend_write={
                "method": "POST",
                "path": self.path,
                "job_id": self.job,
                "spend_kind": "bind",
            },
            license_id=self.lid,
        )
        self.assertIsNotNone(pack)
        self.bearer = pack["bearer"]

    def tearDown(self):
        try:
            os.remove(_DB)
        except OSError:
            pass

    def test_gate_has_no_owned_bind_write_after_redeem(self):
        """Redeem grants clearance only — Gate does not execute bind-only."""
        out = ticket_mod.redeem(
            ticket_id=self.bearer["ticket_id"],
            token=self.bearer["token"],
            job_id=self.job,
            method="POST",
            path=self.path,
            spend_kind="bind",
            now=_now(),
            license_id=self.lid,
        )
        self.assertTrue(out.get("ok"), out)
        self.assertTrue(out.get("allow_bind"), out)
        self.assertFalse(hasattr(ticket_mod, "execute_bind_only"))
        self.assertFalse(hasattr(ticket_mod, "proxy_bind_write"))
        print(
            "POST_REDEEM_SURFACE",
            {
                "redeem_ok": out.get("ok"),
                "allow_bind": out.get("allow_bind"),
                "gate_owns_bind_write": False,
                "contract": "clearance_only — write_executed always false from Gate",
            },
        )

    def test_effect_time_live_recheck_refuses_after_post_redeem_dead(self):
        """External writer must re-check LIVE at effect time; post-redeem DEAD refuses."""
        out = ticket_mod.redeem(
            ticket_id=self.bearer["ticket_id"],
            token=self.bearer["token"],
            job_id=self.job,
            method="POST",
            path=self.path,
            spend_kind="bind",
            now=_now(),
            license_id=self.lid,
        )
        self.assertTrue(out.get("ok"), out)

        dead = license_fuse_mod.dead(license_id=self.lid)
        self.assertEqual(dead.get("state"), "DEAD")

        check = license_fuse_mod.require_live_at_effect(self.lid)
        print(
            "POST_REDEEM_DEAD_THEN_EFFECT_RECHECK",
            {
                "redeem_ok": True,
                "parent_after": "DEAD",
                "effect_recheck_ok": check.get("ok"),
                "effect_recheck_reason": check.get("reason"),
            },
        )
        self.assertFalse(check.get("ok"), check)
        self.assertEqual(check.get("reason"), license_fuse_mod.REASON_NOT_LIVE)


if __name__ == "__main__":
    unittest.main(verbosity=2)
