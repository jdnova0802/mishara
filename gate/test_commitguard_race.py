"""CommitGuard-style mid-flight invalidation against Gate redeem.

Method (arXiv:2607.10487 Temporary Authority, Permanent Effects):
  Pass the authorizing check, invalidate the authorizing condition before the
  durable write, observe whether the write still completes.

Here the authorizing check is license_fuse.require_live() inside ticket.redeem().
The durable write is db.consume_bind_ticket() (ticket consumed → allow_bind=True).
consume_bind_ticket does not re-check parent LIVE (see gate/db.py).

This file reports the measured outcome. It does not self-grade significance.
"""
from __future__ import annotations

import os
import tempfile
import unittest
import uuid
from datetime import datetime, timezone
from unittest import mock

_fd, _DB = tempfile.mkstemp(suffix="-commitguard.db")
os.close(_fd)
os.environ["GATE_DB_PATH"] = _DB
os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "commitguard-test-secret")

import db  # noqa: E402
import license_fuse as license_fuse_mod  # noqa: E402
import ticket as ticket_mod  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class CommitGuardRaceTests(unittest.TestCase):
    def setUp(self):
        db.init_db()
        self.lid = f"lic:CG-{uuid.uuid4().hex[:10]}"
        self.job = f"pc:CG-{uuid.uuid4().hex[:10]}"
        db.upsert_license_parent(license_id=self.lid, state="LIVE", charge_id="chg_cg_seed")
        path = f"/job/v1/jobs/{self.job}/bind-only"
        pack = ticket_mod.issue(
            job_id=self.job,
            fuse_id="fuse_velaru_drill",
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            receipt_hash=f"rh_{uuid.uuid4().hex}",
            redeem_url="https://gate.test/v1/pas/bind-ticket/redeem",
            spend_write={
                "method": "POST",
                "path": path,
                "job_id": self.job,
                "spend_kind": "bind",
            },
            license_id=self.lid,
        )
        self.assertIsNotNone(pack)
        self.bearer = pack["bearer"]
        self.path = path

    def tearDown(self):
        try:
            os.remove(_DB)
        except OSError:
            pass

    def _redeem(self):
        return ticket_mod.redeem(
            ticket_id=self.bearer["ticket_id"],
            token=self.bearer["token"],
            job_id=self.job,
            method="POST",
            path=self.path,
            spend_kind="bind",
            now=_now(),
            license_id=self.lid,
        )

    def test_control_dead_before_redeem_halts(self):
        """Baseline: parent DEAD before redeem starts → must not allow_bind."""
        killed = license_fuse_mod.dead(license_id=self.lid)
        self.assertEqual(killed.get("state"), "DEAD")
        out = self._redeem()
        self.assertFalse(out.get("ok"), out)
        self.assertFalse(out.get("allow_bind"), out)
        self.assertEqual(out.get("reason"), license_fuse_mod.REASON_NOT_LIVE)

    def test_midflight_parent_dead_after_require_live_before_consume(self):
        """CommitGuard race: require_live passes, parent flips DEAD, then consume runs.

        Injection point mirrors the paper's mid-flight invalidation: authorizing
        condition was true at check time and false before the durable write.
        """
        real_require_live = license_fuse_mod.require_live
        flipped = {"done": False}

        def require_live_then_kill(license_id):
            result = real_require_live(license_id)
            if result.get("ok") and not flipped["done"]:
                flipped["done"] = True
                dead = license_fuse_mod.dead(license_id=license_id)
                assert dead.get("state") == "DEAD", dead
                # Confirm stored state is DEAD before redeem continues to consume.
                snap = license_fuse_mod.snapshot(license_id)
                assert snap.get("stored") == "DEAD", snap
            return result

        with mock.patch.object(ticket_mod.license_fuse_mod, "require_live", side_effect=require_live_then_kill):
            out = self._redeem()

        self.assertTrue(flipped["done"], "mid-flight DEAD injection did not run")

        # Measured outcome — do not soft-pass. Print for the night's evidence bar.
        print(
            "COMMITGUARD_RACE_RESULT",
            {
                "ok": out.get("ok"),
                "allow_bind": out.get("allow_bind"),
                "reason": out.get("reason"),
                "parent_stored_after": license_fuse_mod.snapshot(self.lid).get("stored"),
                "ticket_consumed": bool(
                    (db.get_bind_ticket(self.bearer["ticket_id"]) or {}).get("consumed_at")
                ),
            },
        )

        # Gap is open if durable consume succeeded while parent is DEAD.
        parent_dead = license_fuse_mod.snapshot(self.lid).get("stored") == "DEAD"
        write_completed = bool(out.get("ok")) and bool(out.get("allow_bind"))
        self.assertTrue(parent_dead)

        # Explicit boolean the night can cite: race_write_completed_while_parent_dead
        if write_completed:
            self.assertTrue(
                write_completed and parent_dead,
                "durable redeem completed after mid-flight parent DEAD — CommitGuard-shaped gap",
            )
        else:
            self.assertFalse(
                write_completed,
                "redeem halted after mid-flight DEAD — race closed at this boundary",
            )
            self.assertNotEqual(out.get("reason"), None)

        # Documents the open race in current code. If this assertion ever fails
        # because write_completed is False, the gap at this boundary was closed —
        # update this expectation deliberately; do not soft-pass.
        self.assertTrue(
            write_completed,
            msg=(
                "OPEN GAP (CommitGuard-shaped): after require_live OK, parent flipped "
                "DEAD, yet consume_bind_ticket still succeeded (allow_bind=True). "
                f"actual={out}"
            ),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
