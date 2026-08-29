import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone

DB_PATH = os.getenv("GATE_DB_PATH", os.path.join(os.path.dirname(__file__), "gate.db"))

FREE_HOPS_PER_MONTH = int(os.getenv("GATE_FREE_HOPS", "1000"))
PRO_HOPS_PER_MONTH = int(os.getenv("GATE_PRO_HOPS", "1000000"))


def _connect():
    db_dir = os.path.dirname(os.path.abspath(DB_PATH))
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                plan TEXT NOT NULL DEFAULT 'free',
                stripe_customer_id TEXT,
                stripe_subscription_id TEXT,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS api_keys (
                id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                key_prefix TEXT NOT NULL,
                key_hash TEXT NOT NULL,
                label TEXT NOT NULL DEFAULT 'default',
                created_at TEXT NOT NULL,
                revoked INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            );
            CREATE TABLE IF NOT EXISTS usage (
                account_id TEXT NOT NULL,
                period TEXT NOT NULL,
                hops INTEGER NOT NULL DEFAULT 0,
                checks INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (account_id, period)
            );
            CREATE TABLE IF NOT EXISTS install_orders (
                id TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                stripe_session_id TEXT UNIQUE,
                amount_cents INTEGER NOT NULL DEFAULT 250000,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS bind_events (
                id TEXT PRIMARY KEY,
                account_id TEXT,
                fuse_id TEXT NOT NULL,
                job_id TEXT,
                decision TEXT NOT NULL,
                acted INTEGER,
                verify_url TEXT,
                hop_json TEXT,
                prev_receipt_hash TEXT,
                receipt_hash TEXT,
                receipt_signature TEXT,
                receipt_public_key_fingerprint TEXT,
                created_at TEXT NOT NULL
            );
            """
        )
        cols = {row[1] for row in conn.execute("PRAGMA table_info(install_orders)").fetchall()}
        if "product" not in cols:
            conn.execute(
                "ALTER TABLE install_orders ADD COLUMN product TEXT NOT NULL DEFAULT 'install_sprint'"
            )

        # bind_events: receipt chain columns (added after the initial bootstrap).
        bind_cols = {row[1] for row in conn.execute("PRAGMA table_info(bind_events)").fetchall()}
        if "prev_receipt_hash" not in bind_cols:
            conn.execute("ALTER TABLE bind_events ADD COLUMN prev_receipt_hash TEXT")
        if "receipt_hash" not in bind_cols:
            conn.execute("ALTER TABLE bind_events ADD COLUMN receipt_hash TEXT")
        if "receipt_signature" not in bind_cols:
            conn.execute("ALTER TABLE bind_events ADD COLUMN receipt_signature TEXT")
        if "receipt_public_key_fingerprint" not in bind_cols:
            conn.execute("ALTER TABLE bind_events ADD COLUMN receipt_public_key_fingerprint TEXT")
        if "charge_id" not in bind_cols:
            conn.execute("ALTER TABLE bind_events ADD COLUMN charge_id TEXT")

        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS bind_tickets (
                id TEXT PRIMARY KEY,
                job_id TEXT NOT NULL,
                fuse_id TEXT,
                event_id TEXT,
                receipt_hash TEXT,
                token_hash TEXT NOT NULL,
                not_before TEXT NOT NULL,
                not_after TEXT NOT NULL,
                consumed_at TEXT,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_bind_tickets_job ON bind_tickets(job_id);
            CREATE INDEX IF NOT EXISTS idx_bind_events_job ON bind_events(job_id, created_at);
            """
        )
        ticket_cols = {row[1] for row in conn.execute("PRAGMA table_info(bind_tickets)").fetchall()}
        if "spend_fingerprint" not in ticket_cols:
            conn.execute("ALTER TABLE bind_tickets ADD COLUMN spend_fingerprint TEXT")
        if "license_id" not in ticket_cols:
            conn.execute("ALTER TABLE bind_tickets ADD COLUMN license_id TEXT")
        if "counterpart_fingerprint" not in ticket_cols:
            conn.execute("ALTER TABLE bind_tickets ADD COLUMN counterpart_fingerprint TEXT")
        if "holder_id" not in ticket_cols:
            conn.execute("ALTER TABLE bind_tickets ADD COLUMN holder_id TEXT")

        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS pvp_windows (
                id TEXT PRIMARY KEY,
                side_a_ticket TEXT NOT NULL,
                side_b_ticket TEXT NOT NULL,
                side_a_job TEXT NOT NULL,
                side_b_job TEXT NOT NULL,
                state TEXT NOT NULL,
                side_a_offered_at TEXT,
                side_b_offered_at TEXT,
                side_a_now TEXT,
                side_b_now TEXT,
                settled_at TEXT,
                void_reason TEXT,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_pvp_a ON pvp_windows(side_a_ticket);
            CREATE INDEX IF NOT EXISTS idx_pvp_b ON pvp_windows(side_b_ticket);
            """
        )

        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS license_parents (
                license_id TEXT PRIMARY KEY,
                state TEXT NOT NULL,
                charge_id TEXT,
                updated_at TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_bind_tickets_license ON bind_tickets(license_id);
            """
        )

        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS settlement_members (
                member_id TEXT PRIMARY KEY,
                state TEXT NOT NULL DEFAULT 'ACTIVE',
                risk_limit_cents INTEGER NOT NULL DEFAULT 0,
                margin_rate_bps INTEGER NOT NULL DEFAULT 500,
                default_fund_weight INTEGER NOT NULL DEFAULT 1,
                posted_collateral_cents INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_settlement_members_state ON settlement_members(state);

            -- Optional: store settlement windows so auditors can refer to finality by id.
            CREATE TABLE IF NOT EXISTS settlement_windows (
                id TEXT PRIMARY KEY,
                state TEXT NOT NULL,
                opened_at TEXT NOT NULL,
                cutoff_at TEXT,
                settled_at TEXT,
                finality_hash TEXT,
                window_duration_minutes INTEGER NOT NULL DEFAULT 60,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_settlement_windows_opened_at ON settlement_windows(opened_at);

            CREATE TABLE IF NOT EXISTS settlement_net_positions (
                window_id TEXT NOT NULL,
                member_id TEXT NOT NULL,
                asset_class TEXT NOT NULL,
                gross_pay_cents INTEGER NOT NULL DEFAULT 0,
                gross_receive_cents INTEGER NOT NULL DEFAULT 0,
                net_cents INTEGER NOT NULL DEFAULT 0,
                obligation_count INTEGER NOT NULL DEFAULT 0,
                settled INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (window_id, member_id, asset_class),
                FOREIGN KEY (window_id) REFERENCES settlement_windows(id)
            );

            CREATE TABLE IF NOT EXISTS settlement_waterfall_steps (
                window_id TEXT NOT NULL,
                layer INTEGER NOT NULL,
                source TEXT NOT NULL,
                available_cents INTEGER NOT NULL DEFAULT 0,
                consumed_cents INTEGER NOT NULL DEFAULT 0,
                remaining_loss_cents INTEGER NOT NULL DEFAULT 0,
                allocations_json TEXT,
                PRIMARY KEY (window_id, layer, source),
                FOREIGN KEY (window_id) REFERENCES settlement_windows(id)
            );

            -- Idempotency keys: prevents duplicate checkout submissions
            -- (common with retries / double-click / flaky network).
            CREATE TABLE IF NOT EXISTS idempotency_keys (
                scope TEXT NOT NULL,
                idempotency_key TEXT NOT NULL,
                request_fingerprint TEXT NOT NULL,
                redirect_url TEXT,
                install_order_id TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (scope, idempotency_key)
            );
            CREATE INDEX IF NOT EXISTS idx_idempotency_scope_key ON idempotency_keys(scope, idempotency_key);
            """
        )

        # Seed a default member so the public registry is never empty.
        row = conn.execute("SELECT COUNT(*) AS n FROM settlement_members").fetchone()
        if row and row["n"] == 0:
            conn.execute(
                """
                INSERT INTO settlement_members (
                    member_id, state, risk_limit_cents, margin_rate_bps,
                    default_fund_weight, posted_collateral_cents, created_at, updated_at
                ) VALUES (?, 'ACTIVE', ?, ?, ?, ?, ?, ?)
                """,
                (
                    "gate",
                    0,
                    500,
                    1,
                    0,
                    utc_now(),
                    utc_now(),
                ),
            )


@contextmanager
def db():
    conn = _connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def current_period():
    return datetime.now(timezone.utc).strftime("%Y-%m")


def create_account(email: str, password_hash: str) -> str:
    account_id = str(uuid.uuid4())
    with db() as conn:
        conn.execute(
            "INSERT INTO accounts (id, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (account_id, email.lower().strip(), password_hash, utc_now()),
        )
    return account_id


def get_account_by_email(email: str):
    with db() as conn:
        return conn.execute(
            "SELECT * FROM accounts WHERE email = ?", (email.lower().strip(),)
        ).fetchone()


def get_account(account_id: str):
    with db() as conn:
        return conn.execute("SELECT * FROM accounts WHERE id = ?", (account_id,)).fetchone()


def create_api_key(account_id: str, key_hash: str, key_prefix: str, label: str = "default") -> str:
    key_id = str(uuid.uuid4())
    with db() as conn:
        conn.execute(
            """INSERT INTO api_keys (id, account_id, key_prefix, key_hash, label, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (key_id, account_id, key_prefix, key_hash, label, utc_now()),
        )
    return key_id


def get_api_key_by_hash(key_hash: str):
    with db() as conn:
        row = conn.execute(
            """SELECT k.*, a.plan, a.email, a.id AS account_id
               FROM api_keys k JOIN accounts a ON a.id = k.account_id
               WHERE k.key_hash = ? AND k.revoked = 0""",
            (key_hash,),
        ).fetchone()
        return row


def list_api_keys(account_id: str):
    with db() as conn:
        return conn.execute(
            "SELECT id, key_prefix, label, created_at FROM api_keys WHERE account_id = ? AND revoked = 0",
            (account_id,),
        ).fetchall()


def hop_limit(plan: str) -> int:
    return PRO_HOPS_PER_MONTH if plan == "pro" else FREE_HOPS_PER_MONTH


def increment_usage(account_id: str, field: str = "hops") -> dict:
    period = current_period()
    with db() as conn:
        conn.execute(
            f"""INSERT INTO usage (account_id, period, {field}, checks)
                VALUES (?, ?, 1, 0)
                ON CONFLICT(account_id, period) DO UPDATE SET {field} = {field} + 1""",
            (account_id, period),
        )
        row = conn.execute(
            "SELECT hops, checks FROM usage WHERE account_id = ? AND period = ?",
            (account_id, period),
        ).fetchone()
    return {"period": period, "hops": row["hops"], "checks": row["checks"]}


def get_usage(account_id: str):
    period = current_period()
    with db() as conn:
        row = conn.execute(
            "SELECT hops, checks FROM usage WHERE account_id = ? AND period = ?",
            (account_id, period),
        ).fetchone()
    if not row:
        return {"period": period, "hops": 0, "checks": 0}
    return {"period": period, "hops": row["hops"], "checks": row["checks"]}


def set_plan(account_id: str, plan: str, stripe_customer_id=None, stripe_subscription_id=None):
    with db() as conn:
        conn.execute(
            """UPDATE accounts SET plan = ?, stripe_customer_id = COALESCE(?, stripe_customer_id),
               stripe_subscription_id = COALESCE(?, stripe_subscription_id) WHERE id = ?""",
            (plan, stripe_customer_id, stripe_subscription_id, account_id),
        )


INSTALL_SLOTS = int(os.getenv("GATE_INSTALL_SLOTS", "2"))


def install_slots_remaining() -> int:
    period = current_period()
    with db() as conn:
        cols = {row[1] for row in conn.execute("PRAGMA table_info(install_orders)").fetchall()}
        if "product" in cols:
            row = conn.execute(
                """SELECT COUNT(*) AS n FROM install_orders
                   WHERE status = 'paid' AND product = 'install_sprint' AND created_at LIKE ?""",
                (f"{period}%",),
            ).fetchone()
        else:
            row = conn.execute(
                """SELECT COUNT(*) AS n FROM install_orders
                   WHERE status = 'paid' AND created_at LIKE ?""",
                (f"{period}%",),
            ).fetchone()
    booked = row["n"] if row else 0
    return max(0, INSTALL_SLOTS - booked)


def create_install_order(
    email: str, stripe_session_id: str, amount_cents: int = 250000, product: str = "install_sprint"
) -> str:
    order_id = str(uuid.uuid4())
    with db() as conn:
        cols = {row[1] for row in conn.execute("PRAGMA table_info(install_orders)").fetchall()}
        if "product" in cols:
            conn.execute(
                """INSERT INTO install_orders (id, email, stripe_session_id, amount_cents, status, created_at, product)
                   VALUES (?, ?, ?, ?, 'pending', ?, ?)""",
                (order_id, email.lower().strip(), stripe_session_id, amount_cents, utc_now(), product),
            )
        else:
            conn.execute(
                """INSERT INTO install_orders (id, email, stripe_session_id, amount_cents, status, created_at)
                   VALUES (?, ?, ?, ?, 'pending', ?)""",
                (order_id, email.lower().strip(), stripe_session_id, amount_cents, utc_now()),
            )
    return order_id


def record_bind_event(
    *,
    fuse_id: str,
    decision: str,
    job_id: str | None = None,
    account_id: str | None = None,
    acted: bool | None = None,
    verify_url: str | None = None,
    hop: dict | None = None,
    charge_id: str | None = None,
) -> str:
    import json

    event_id = str(uuid.uuid4())
    created_at = utc_now()

    with db() as conn:
        # Append-only chain: the previous receipt_hash becomes the pointer.
        prev = conn.execute(
            "SELECT receipt_hash FROM bind_events ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
        prev_receipt_hash = prev["receipt_hash"] if prev and prev["receipt_hash"] else None

        # Mint signed receipt (hash-chained, no PII).
        try:
            from gate import receipt as receipt_mod
        except ImportError:
            import receipt as receipt_mod

        receipt_issue = receipt_mod.issue_receipt(
            event_id=event_id,
            fuse_id=fuse_id,
            job_id=job_id,
            decision=decision,
            acted=acted,
            verify_url=verify_url,
            created_at=created_at,
            hop=hop,
            prev_receipt_hash=prev_receipt_hash,
        )
        if receipt_issue.get("unsigned_halt"):
            raise RuntimeError(
                "receipt_unsigned_halt: GATE_RECEIPT_PRIVATE_KEY required outside GATE_DEV_MODE"
            )

        conn.execute(
            """INSERT INTO bind_events
               (id, account_id, fuse_id, job_id, decision, acted, verify_url, hop_json,
                prev_receipt_hash, receipt_hash, receipt_signature, receipt_public_key_fingerprint,
                created_at, charge_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                event_id,
                account_id,
                fuse_id,
                job_id,
                decision,
                None if acted is None else (1 if acted else 0),
                verify_url,
                json.dumps(hop) if hop is not None else None,
                prev_receipt_hash,
                receipt_issue.get("receipt_hash"),
                receipt_issue.get("receipt_signature"),
                receipt_issue.get("receipt_public_key_fingerprint"),
                created_at,
                charge_id,
            ),
        )
    return event_id


def list_bind_events(account_id: str | None, limit: int = 50) -> list:
    import json

    with db() as conn:
        if account_id:
            rows = conn.execute(
                """SELECT * FROM bind_events WHERE account_id = ?
                   ORDER BY created_at DESC LIMIT ?""",
                (account_id, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT * FROM bind_events WHERE account_id IS NULL
                   ORDER BY created_at DESC LIMIT ?""",
                (limit,),
            ).fetchall()
    out = []
    for r in rows:
        item = dict(r)
        if item.get("hop_json"):
            try:
                item["hop"] = json.loads(item["hop_json"])
            except ValueError:
                item["hop"] = None
        item.pop("hop_json", None)
        if item.get("acted") is not None:
            item["acted"] = bool(item["acted"])
        out.append(item)
    return out


def list_bind_events_chronological(limit: int = 10000) -> list:
    """All bind events with receipt hashes, oldest first (Merkle evidence log order)."""
    import json

    with db() as conn:
        rows = conn.execute(
            """SELECT * FROM bind_events
               WHERE receipt_hash IS NOT NULL
               ORDER BY created_at ASC, id ASC
               LIMIT ?""",
            (limit,),
        ).fetchall()
    out = []
    for r in rows:
        item = dict(r)
        if item.get("hop_json"):
            try:
                item["hop"] = json.loads(item["hop_json"])
            except ValueError:
                item["hop"] = None
        item.pop("hop_json", None)
        if item.get("acted") is not None:
            item["acted"] = bool(item["acted"])
        out.append(item)
    return out


def latest_bind_event_for_job(job_id: str) -> dict | None:
    jid = (job_id or "").strip()
    if not jid:
        return None
    with db() as conn:
        row = conn.execute(
            """SELECT * FROM bind_events WHERE job_id = ?
               ORDER BY created_at DESC, id DESC LIMIT 1""",
            (jid,),
        ).fetchone()
    if not row:
        return None
    item = dict(row)
    if item.get("acted") is not None:
        item["acted"] = bool(item["acted"])
    return item


def latest_bind_event_any() -> dict | None:
    import json

    with db() as conn:
        row = conn.execute(
            "SELECT * FROM bind_events ORDER BY created_at DESC, id DESC LIMIT 1"
        ).fetchone()
    if not row:
        return None
    item = dict(row)
    if item.get("hop_json"):
        try:
            item["hop"] = json.loads(item["hop_json"])
        except ValueError:
            item["hop"] = None
    item.pop("hop_json", None)
    if item.get("acted") is not None:
        item["acted"] = bool(item["acted"])
    return item


def list_license_parents(limit: int = 50) -> list:
    cap = max(1, min(int(limit or 50), 200))
    with db() as conn:
        rows = conn.execute(
            """SELECT license_id, state, charge_id, updated_at, created_at
               FROM license_parents
               ORDER BY updated_at DESC LIMIT ?""",
            (cap,),
        ).fetchall()
    return [dict(r) for r in rows]


def _ensure_bypass_canaries(conn) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS bypass_canaries (
            id TEXT PRIMARY KEY,
            write_path TEXT NOT NULL,
            job_id TEXT,
            reporter TEXT NOT NULL,
            note TEXT,
            license_id TEXT,
            bypass_suspected INTEGER NOT NULL DEFAULT 0,
            killed_parent INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
        """
    )


def record_bypass_canary(
    *,
    write_path: str,
    job_id: str | None,
    reporter: str,
    note: str = "",
    license_id: str | None = None,
    bypass_suspected: bool = False,
    killed_parent: bool = False,
) -> dict:
    cid = str(uuid.uuid4())
    ts = utc_now()
    with db() as conn:
        _ensure_bypass_canaries(conn)
        conn.execute(
            """INSERT INTO bypass_canaries
               (id, write_path, job_id, reporter, note, license_id,
                bypass_suspected, killed_parent, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                cid,
                (write_path or "").strip(),
                (job_id or "").strip() or None,
                (reporter or "").strip(),
                (note or "").strip(),
                (license_id or "").strip() or None,
                1 if bypass_suspected else 0,
                1 if killed_parent else 0,
                ts,
            ),
        )
    return {
        "id": cid,
        "write_path": write_path,
        "job_id": job_id,
        "reporter": reporter,
        "note": note,
        "license_id": license_id,
        "bypass_suspected": bool(bypass_suspected),
        "killed_parent": bool(killed_parent),
        "created_at": ts,
    }


def list_bypass_canaries(limit: int = 25) -> list:
    cap = max(1, min(int(limit or 25), 200))
    with db() as conn:
        _ensure_bypass_canaries(conn)
        rows = conn.execute(
            """SELECT * FROM bypass_canaries
               ORDER BY created_at DESC LIMIT ?""",
            (cap,),
        ).fetchall()
    out = []
    for r in rows:
        item = dict(r)
        item["bypass_suspected"] = bool(item.get("bypass_suspected"))
        item["killed_parent"] = bool(item.get("killed_parent"))
        out.append(item)
    return out


def insert_bind_ticket(
    *,
    ticket_id: str,
    job_id: str,
    fuse_id: str | None,
    event_id: str | None,
    receipt_hash: str | None,
    token_hash: str,
    not_before: str,
    not_after: str,
    spend_fingerprint: str | None = None,
    license_id: str | None = None,
    counterpart_fingerprint: str | None = None,
    holder_id: str | None = None,
) -> None:
    with db() as conn:
        conn.execute(
            """INSERT INTO bind_tickets
               (id, job_id, fuse_id, event_id, receipt_hash, token_hash,
                not_before, not_after, spend_fingerprint, license_id,
                counterpart_fingerprint, holder_id, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                ticket_id,
                job_id,
                fuse_id,
                event_id,
                receipt_hash,
                token_hash,
                not_before,
                not_after,
                spend_fingerprint,
                license_id,
                counterpart_fingerprint,
                holder_id,
                utc_now(),
            ),
        )


def get_bind_ticket(ticket_id: str) -> dict | None:
    tid = (ticket_id or "").strip()
    if not tid:
        return None
    with db() as conn:
        row = conn.execute("SELECT * FROM bind_tickets WHERE id = ?", (tid,)).fetchone()
    return dict(row) if row else None


def tickets_for_job(job_id: str) -> list[dict]:
    """Issued tickets for one job — opening of the remaining folio."""
    jid = (job_id or "").strip()
    if not jid:
        return []
    with db() as conn:
        rows = conn.execute(
            """SELECT * FROM bind_tickets WHERE job_id = ?
               ORDER BY created_at ASC, id ASC""",
            (jid,),
        ).fetchall()
    return [dict(r) for r in rows]


def consume_bind_ticket(
    *,
    ticket_id: str,
    token_hash: str,
    job_id: str,
    now: str,
    spend_fingerprint: str | None = None,
    counterpart_fingerprint: str | None = None,
) -> dict:
    with db() as conn:
        row = conn.execute("SELECT * FROM bind_tickets WHERE id = ?", (ticket_id,)).fetchone()
        if not row:
            return {"ok": False, "reason": "ticket_not_found"}
        if row["token_hash"] != token_hash:
            return {"ok": False, "reason": "ticket_token_mismatch"}
        if row["job_id"] != job_id:
            return {"ok": False, "reason": "ticket_job_mismatch"}
        issued_fp = ""
        try:
            issued_fp = (row["spend_fingerprint"] or "").strip()
        except (IndexError, KeyError):
            issued_fp = ""
        presented_fp = (spend_fingerprint or "").strip()
        if issued_fp:
            if not presented_fp:
                return {"ok": False, "reason": "ticket_spend_mismatch"}
            if issued_fp.lower() != presented_fp.lower():
                return {"ok": False, "reason": "ticket_spend_mismatch"}
        issued_cp = ""
        try:
            issued_cp = (row["counterpart_fingerprint"] or "").strip()
        except (IndexError, KeyError):
            issued_cp = ""
        presented_cp = (counterpart_fingerprint or "").strip()
        if issued_cp:
            if not presented_cp:
                return {"ok": False, "reason": "counterpart_mismatch"}
            if issued_cp.lower() != presented_cp.lower():
                return {"ok": False, "reason": "counterpart_mismatch"}
        if row["consumed_at"]:
            return {"ok": False, "reason": "ticket_replay"}
        if row["not_after"] < now:
            return {"ok": False, "reason": "ticket_expired"}
        if row["not_before"] > now:
            return {"ok": False, "reason": "ticket_not_yet_valid"}
        cur = conn.execute(
            """UPDATE bind_tickets SET consumed_at = ?
               WHERE id = ? AND consumed_at IS NULL AND token_hash = ?""",
            (now, ticket_id, token_hash),
        )
        if cur.rowcount != 1:
            return {"ok": False, "reason": "ticket_replay"}
    return {"ok": True}


def pvp_open(
    *,
    window_id: str,
    side_a_ticket: str,
    side_b_ticket: str,
    side_a_job: str,
    side_b_job: str,
) -> dict:
    now = utc_now()
    with db() as conn:
        conn.execute(
            """INSERT INTO pvp_windows
               (id, side_a_ticket, side_b_ticket, side_a_job, side_b_job,
                state, created_at)
               VALUES (?, ?, ?, ?, ?, 'OPEN', ?)""",
            (window_id, side_a_ticket, side_b_ticket, side_a_job, side_b_job, now),
        )
    return {"ok": True, "window_id": window_id, "state": "OPEN"}


def pvp_get(window_id: str) -> dict | None:
    wid = (window_id or "").strip()
    if not wid:
        return None
    with db() as conn:
        row = conn.execute("SELECT * FROM pvp_windows WHERE id = ?", (wid,)).fetchone()
    return dict(row) if row else None


def pvp_lock_for_ticket(ticket_id: str) -> dict | None:
    tid = (ticket_id or "").strip()
    if not tid:
        return None
    with db() as conn:
        row = conn.execute(
            """SELECT * FROM pvp_windows
               WHERE (side_a_ticket = ? OR side_b_ticket = ?)
                 AND state IN ('OPEN', 'ARMED')
               ORDER BY created_at DESC LIMIT 1""",
            (tid, tid),
        ).fetchone()
    return dict(row) if row else None


def pvp_record_offer(*, window_id: str, side: str, offered_at: str, presented_now: str) -> dict:
    col_off = "side_a_offered_at" if side == "a" else "side_b_offered_at"
    col_now = "side_a_now" if side == "a" else "side_b_now"
    with db() as conn:
        conn.execute(
            f"UPDATE pvp_windows SET {col_off} = ?, {col_now} = ?, state = 'ARMED' WHERE id = ? AND state IN ('OPEN', 'ARMED')",
            (offered_at, presented_now, window_id),
        )
        row = conn.execute("SELECT * FROM pvp_windows WHERE id = ?", (window_id,)).fetchone()
    return dict(row) if row else {}


def pvp_settle(
    *,
    window_id: str,
    now: str,
    a_ticket: str,
    a_token_hash: str,
    a_job: str,
    a_spend: str | None,
    b_ticket: str,
    b_token_hash: str,
    b_job: str,
    b_spend: str | None,
) -> dict:
    """Atomic: both tickets consume or neither does."""
    with db() as conn:
        win = conn.execute("SELECT * FROM pvp_windows WHERE id = ?", (window_id,)).fetchone()
        if not win or win["state"] not in ("OPEN", "ARMED"):
            return {"ok": False, "reason": "pvp_window_not_open"}
        for tid, tok, jid, fp in (
            (a_ticket, a_token_hash, a_job, a_spend),
            (b_ticket, b_token_hash, b_job, b_spend),
        ):
            row = conn.execute("SELECT * FROM bind_tickets WHERE id = ?", (tid,)).fetchone()
            if not row:
                return {"ok": False, "reason": "ticket_not_found"}
            if row["token_hash"] != tok:
                return {"ok": False, "reason": "ticket_token_mismatch"}
            if row["job_id"] != jid:
                return {"ok": False, "reason": "ticket_job_mismatch"}
            if row["consumed_at"]:
                return {"ok": False, "reason": "ticket_replay"}
            issued_fp = (row["spend_fingerprint"] or "").strip() if "spend_fingerprint" in row.keys() else ""
            presented_fp = (fp or "").strip()
            if issued_fp and issued_fp.lower() != presented_fp.lower():
                return {"ok": False, "reason": "ticket_spend_mismatch"}
        cur_a = conn.execute(
            """UPDATE bind_tickets SET consumed_at = ?
               WHERE id = ? AND consumed_at IS NULL AND token_hash = ?""",
            (now, a_ticket, a_token_hash),
        )
        cur_b = conn.execute(
            """UPDATE bind_tickets SET consumed_at = ?
               WHERE id = ? AND consumed_at IS NULL AND token_hash = ?""",
            (now, b_ticket, b_token_hash),
        )
        if cur_a.rowcount != 1 or cur_b.rowcount != 1:
            conn.rollback()
            return {"ok": False, "reason": "pvp_atomic_abort"}
        conn.execute(
            """UPDATE pvp_windows SET state = 'SETTLED', settled_at = ? WHERE id = ?""",
            (now, window_id),
        )
    return {"ok": True, "state": "SETTLED"}


def pvp_void(*, window_id: str, reason: str) -> dict:
    with db() as conn:
        conn.execute(
            """UPDATE pvp_windows SET state = 'VOID', void_reason = ?
               WHERE id = ? AND state IN ('OPEN', 'ARMED')""",
            (reason, window_id),
        )
    return {"ok": True, "state": "VOID", "reason": reason}


def get_license_parent(license_id: str) -> dict | None:
    lid = (license_id or "").strip()
    if not lid:
        return None
    with db() as conn:
        row = conn.execute(
            "SELECT * FROM license_parents WHERE license_id = ?", (lid,)
        ).fetchone()
    return dict(row) if row else None


def upsert_license_parent(*, license_id: str, state: str, charge_id: str | None = None) -> None:
    lid = (license_id or "").strip()
    st = (state or "").strip().upper()
    if not lid or st not in {"UNSIGNED", "LIVE", "DEAD"}:
        raise ValueError("license parent requires license_id and UNSIGNED|LIVE|DEAD")
    now = utc_now()
    with db() as conn:
        conn.execute(
            """INSERT INTO license_parents (license_id, state, charge_id, updated_at, created_at)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(license_id) DO UPDATE SET
                 state = excluded.state,
                 charge_id = excluded.charge_id,
                 updated_at = excluded.updated_at""",
            (lid, st, charge_id, now, now),
        )


def count_unconsumed_tickets_for_license(license_id: str) -> int:
    lid = (license_id or "").strip()
    if not lid:
        return 0
    with db() as conn:
        row = conn.execute(
            """SELECT COUNT(*) AS n FROM bind_tickets
               WHERE license_id = ? AND consumed_at IS NULL""",
            (lid,),
        ).fetchone()
    return int(row["n"] if row else 0)


def list_restraint_events(limit: int = 200) -> list:
    """Production HALT/BLOCK only. Metered account, not demo, no hop body in the query result beyond reason extraction."""
    import json

    cap = max(1, min(int(limit or 200), 500))
    with db() as conn:
        rows = conn.execute(
            """SELECT * FROM bind_events
               WHERE account_id IS NOT NULL
                 AND UPPER(decision) IN ('HALT', 'BLOCK')
                 AND (acted IS NULL OR acted = 0)
               ORDER BY created_at DESC, id DESC
               LIMIT ?""",
            (cap,),
        ).fetchall()
    out = []
    for r in rows:
        item = dict(r)
        if item.get("hop_json"):
            try:
                item["hop"] = json.loads(item["hop_json"])
            except ValueError:
                item["hop"] = None
        item.pop("hop_json", None)
        if item.get("acted") is not None:
            item["acted"] = bool(item["acted"])
        out.append(item)
    return out


def consumed_spend_job_ids() -> list[str]:
    with db() as conn:
        rows = conn.execute(
            """SELECT DISTINCT job_id FROM bind_tickets
               WHERE consumed_at IS NOT NULL AND job_id IS NOT NULL
               ORDER BY job_id ASC"""
        ).fetchall()
    return [r["job_id"] for r in rows]


def get_bind_event(event_id: str) -> dict | None:
    import json

    with db() as conn:
        row = conn.execute(
            "SELECT * FROM bind_events WHERE id = ?",
            (event_id,),
        ).fetchone()
    if not row:
        return None
    item = dict(row)
    if item.get("hop_json"):
        try:
            item["hop"] = json.loads(item["hop_json"])
        except ValueError:
            item["hop"] = None
    item.pop("hop_json", None)
    if item.get("acted") is not None:
        item["acted"] = bool(item["acted"])
    return item


def mark_install_paid(stripe_session_id: str):
    with db() as conn:
        conn.execute(
            "UPDATE install_orders SET status = 'paid' WHERE stripe_session_id = ?",
            (stripe_session_id,),
        )
    # Close checkout → delivery ledger loop (not production claim).
    ensure_weld_order_from_session(stripe_session_id)


def _ensure_prefinality_table(conn) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS prefinality_evaluations (
            id TEXT PRIMARY KEY,
            account_id TEXT,
            rail TEXT NOT NULL,
            decision TEXT NOT NULL,
            fingerprint TEXT NOT NULL,
            agent_id TEXT,
            signals_json TEXT,
            receipt_jwt TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_prefinality_created ON prefinality_evaluations(created_at DESC)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_prefinality_agent ON prefinality_evaluations(agent_id, created_at DESC)"
    )


def record_prefinality_evaluation(
    *,
    evaluation_id: str,
    account_id: str | None,
    rail: str,
    decision: str,
    fingerprint: str,
    agent_id: str | None,
    signals: list,
    receipt_jwt: str | None,
    created_at: str,
) -> None:
    import json

    with db() as conn:
        _ensure_prefinality_table(conn)
        conn.execute(
            """INSERT INTO prefinality_evaluations
               (id, account_id, rail, decision, fingerprint, agent_id, signals_json, receipt_jwt, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                evaluation_id,
                account_id,
                rail,
                decision.upper(),
                fingerprint,
                agent_id,
                json.dumps(signals or []),
                receipt_jwt,
                created_at,
            ),
        )


def get_prefinality_evaluation(evaluation_id: str) -> dict | None:
    import json

    eid = (evaluation_id or "").strip()
    if not eid:
        return None
    with db() as conn:
        _ensure_prefinality_table(conn)
        row = conn.execute(
            "SELECT * FROM prefinality_evaluations WHERE id = ?", (eid,)
        ).fetchone()
    if not row:
        return None
    item = dict(row)
    if item.get("signals_json"):
        try:
            item["signals"] = json.loads(item["signals_json"])
        except ValueError:
            item["signals"] = []
    item.pop("signals_json", None)
    return item


def _ensure_charge_authority_table(conn) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS charge_authority_used (
            charge_id TEXT PRIMARY KEY,
            purpose TEXT NOT NULL,
            subject TEXT,
            consumed_at TEXT NOT NULL
        )
        """
    )


def charge_authority_consumed(charge_id: str) -> bool:
    cid = (charge_id or "").strip()
    if not cid:
        return False
    with db() as conn:
        _ensure_charge_authority_table(conn)
        row = conn.execute(
            "SELECT 1 FROM charge_authority_used WHERE charge_id = ?", (cid,)
        ).fetchone()
    return bool(row)


def consume_charge_authority(*, charge_id: str, purpose: str, subject: str = "") -> None:
    cid = (charge_id or "").strip()
    if not cid:
        raise ValueError("charge_id required")
    with db() as conn:
        _ensure_charge_authority_table(conn)
        conn.execute(
            """INSERT INTO charge_authority_used (charge_id, purpose, subject, consumed_at)
               VALUES (?, ?, ?, ?)""",
            (cid, (purpose or "").strip()[:64], (subject or "").strip()[:128], utc_now()),
        )


def _ensure_cleared_flow_table(conn) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS cleared_flow_ledger (
            id TEXT PRIMARY KEY,
            weld_order_id TEXT,
            install_session_id TEXT,
            cleared_cents INTEGER NOT NULL,
            hop_count INTEGER NOT NULL DEFAULT 0,
            note TEXT,
            created_at TEXT NOT NULL
        )
        """
    )


def _ensure_weld_orders_table(conn) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS weld_orders (
            id TEXT PRIMARY KEY,
            install_order_id TEXT,
            stripe_session_id TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL,
            write_kind TEXT,
            amount_cents INTEGER NOT NULL,
            status TEXT NOT NULL,
            their_production INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
        """
    )


def ensure_weld_order_from_session(stripe_session_id: str) -> dict | None:
    """Link a paid install/operator checkout to a weld_orders delivery row."""
    sid = (stripe_session_id or "").strip()
    if not sid:
        return None
    order = get_install_order_by_session(sid)
    if not order:
        return None
    order = dict(order)
    if (order.get("status") or "") != "paid":
        return None
    with db() as conn:
        _ensure_weld_orders_table(conn)
        existing = conn.execute(
            "SELECT * FROM weld_orders WHERE stripe_session_id = ?", (sid,)
        ).fetchone()
        if existing:
            return dict(existing)
        wid = str(uuid.uuid4())
        conn.execute(
            """INSERT INTO weld_orders
               (id, install_order_id, stripe_session_id, email, write_kind, amount_cents,
                status, their_production, created_at)
               VALUES (?, ?, ?, ?, ?, ?, 'paid_delivery', 0, ?)""",
            (
                wid,
                order["id"],
                sid,
                order["email"],
                None,
                int(order["amount_cents"] or 0),
                utc_now(),
            ),
        )
        row = conn.execute("SELECT * FROM weld_orders WHERE id = ?", (wid,)).fetchone()
    return dict(row) if row else None


def record_cleared_flow(
    *,
    cleared_cents: int,
    hop_count: int = 0,
    weld_order_id: str | None = None,
    install_session_id: str | None = None,
    note: str = "",
) -> dict:
    cents = int(cleared_cents or 0)
    hops = max(0, int(hop_count or 0))
    if cents < 0:
        raise ValueError("cleared_cents must be >= 0")
    if not weld_order_id and not install_session_id:
        raise ValueError("weld_order_id or install_session_id required")
    eid = str(uuid.uuid4())
    with db() as conn:
        _ensure_cleared_flow_table(conn)
        conn.execute(
            """INSERT INTO cleared_flow_ledger
               (id, weld_order_id, install_session_id, cleared_cents, hop_count, note, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                eid,
                (weld_order_id or "").strip() or None,
                (install_session_id or "").strip() or None,
                cents,
                hops,
                (note or "").strip()[:500],
                utc_now(),
            ),
        )
    return {
        "id": eid,
        "cleared_cents": cents,
        "hop_count": hops,
        "weld_order_id": weld_order_id,
        "install_session_id": install_session_id,
        "their_production": False,
    }


def cleared_flow_totals() -> dict:
    with db() as conn:
        _ensure_cleared_flow_table(conn)
        row = conn.execute(
            """SELECT COALESCE(SUM(cleared_cents), 0) AS cents,
                      COALESCE(SUM(hop_count), 0) AS hops,
                      COUNT(*) AS n
               FROM cleared_flow_ledger"""
        ).fetchone()
    return {
        "cleared_cents": int(row["cents"] if row else 0),
        "hop_count": int(row["hops"] if row else 0),
        "entries": int(row["n"] if row else 0),
    }


def get_install_order_by_session(stripe_session_id: str):
    with db() as conn:
        return conn.execute(
            "SELECT * FROM install_orders WHERE stripe_session_id = ?",
            (stripe_session_id,),
        ).fetchone()


def get_idempotency_record(scope: str, idempotency_key: str) -> dict | None:
    with db() as conn:
        row = conn.execute(
            """SELECT scope, idempotency_key, request_fingerprint, redirect_url,
                      install_order_id, created_at, updated_at
               FROM idempotency_keys
               WHERE scope = ? AND idempotency_key = ?""",
            (scope, idempotency_key),
        ).fetchone()
    return dict(row) if row else None


def create_idempotency_record(
    *,
    scope: str,
    idempotency_key: str,
    request_fingerprint: str,
    redirect_url: str,
    install_order_id: str,
) -> None:
    # Insert-if-absent. If it exists, we rely on request_fingerprint checks in the caller.
    with db() as conn:
        conn.execute(
            """INSERT OR IGNORE INTO idempotency_keys
               (scope, idempotency_key, request_fingerprint, redirect_url, install_order_id, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                scope,
                idempotency_key,
                request_fingerprint,
                redirect_url,
                install_order_id,
                utc_now(),
                utc_now(),
            ),
        )


def count_accounts() -> int:
    with db() as conn:
        row = conn.execute("SELECT COUNT(*) AS n FROM accounts").fetchone()
    return row["n"] if row else 0


def total_hops_period() -> int:
    period = current_period()
    with db() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(hops), 0) AS n FROM usage WHERE period = ?",
            (period,),
        ).fetchone()
    return row["n"] if row else 0


def paid_installs_period() -> int:
    period = current_period()
    with db() as conn:
        row = conn.execute(
            """SELECT COUNT(*) AS n FROM install_orders
               WHERE status = 'paid' AND created_at LIKE ?""",
            (f"{period}%",),
        ).fetchone()
    return row["n"] if row else 0


def list_paid_installs(limit: int = 50):
    with db() as conn:
        return conn.execute(
            """SELECT id, email, amount_cents, status, created_at, stripe_session_id
               FROM install_orders WHERE status = 'paid'
               ORDER BY created_at DESC LIMIT ?""",
            (limit,),
        ).fetchall()


def list_settlement_members(limit: int = 50) -> list[dict]:
    """Public-ish registry view for settlement risk committee semantics."""
    with db() as conn:
        rows = conn.execute(
            """SELECT member_id, state, risk_limit_cents, margin_rate_bps,
                      default_fund_weight, posted_collateral_cents,
                      created_at, updated_at
               FROM settlement_members
               ORDER BY created_at DESC
               LIMIT ?""",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def list_settlement_windows(limit: int = 20) -> list[dict]:
    """Settlement windows recorded by the settlement engine (audit trail)."""
    with db() as conn:
        rows = conn.execute(
            """SELECT id, state, opened_at, cutoff_at, settled_at,
                      finality_hash, window_duration_minutes, created_at
               FROM settlement_windows
               ORDER BY opened_at DESC
               LIMIT ?""",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def _table_cols(conn, name: str) -> set[str]:
    exists = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    ).fetchone()
    if not exists:
        return set()
    return {r[1] for r in conn.execute(f"PRAGMA table_info({name})").fetchall()}


def _ensure_dogfood_table(conn) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS dogfood_welds (
            id TEXT PRIMARY KEY,
            write_path TEXT NOT NULL,
            operator TEXT NOT NULL,
            note TEXT,
            created_at TEXT NOT NULL
        )
        """
    )


def _ensure_third_party_welds(conn) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS third_party_welds (
            id TEXT PRIMARY KEY,
            write_path TEXT NOT NULL,
            counterparty TEXT NOT NULL,
            note TEXT,
            stripe_session_id TEXT,
            exclusive_door_url TEXT,
            door_kind TEXT,
            worker_fingerprint TEXT,
            exclusivity_attested INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
        """
    )
    cols = {row[1] for row in conn.execute("PRAGMA table_info(third_party_welds)").fetchall()}
    for col, decl in (
        ("exclusive_door_url", "TEXT"),
        ("door_kind", "TEXT"),
        ("worker_fingerprint", "TEXT"),
        ("exclusivity_attested", "INTEGER NOT NULL DEFAULT 0"),
    ):
        if col not in cols:
            conn.execute(f"ALTER TABLE third_party_welds ADD COLUMN {col} {decl}")


def has_dogfood_weld() -> bool:
    """First-party dogfood weld — never flips their_production."""
    with db() as conn:
        _ensure_dogfood_table(conn)
        row = conn.execute("SELECT COUNT(*) AS n FROM dogfood_welds").fetchone()
    return bool(row and row["n"] > 0)


def has_gate_production_weld() -> bool:
    """Third-party production weld with exclusivity attestation only."""
    with db() as conn:
        _ensure_third_party_welds(conn)
        row = conn.execute(
            """SELECT COUNT(*) AS n FROM third_party_welds
               WHERE COALESCE(exclusivity_attested, 0) = 1
                 AND exclusive_door_url IS NOT NULL
                 AND TRIM(exclusive_door_url) != ''"""
        ).fetchone()
    return bool(row and row["n"] > 0)


def record_dogfood_weld(*, write_path: str, operator: str, note: str = "") -> dict:
    wid = str(uuid.uuid4())
    ts = datetime.now(timezone.utc).isoformat()
    path = (write_path or "").strip()
    op = (operator or "").strip()
    if not path or not op:
        raise ValueError("write_path and operator required")
    with db() as conn:
        _ensure_dogfood_table(conn)
        conn.execute(
            """INSERT INTO dogfood_welds (id, write_path, operator, note, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (wid, path, op, (note or "").strip(), ts),
        )
    return {
        "id": wid,
        "write_path": path,
        "operator": op,
        "note": note,
        "created_at": ts,
        "their_production": False,
    }


def record_production_weld(
    *,
    write_path: str,
    counterparty: str,
    note: str = "",
    stripe_session_id: str | None = None,
    exclusive_door_url: str | None = None,
    door_kind: str | None = None,
    worker_fingerprint: str | None = None,
) -> dict:
    """Record a third-party production weld. Requires exclusivity attestation fields."""
    wid = str(uuid.uuid4())
    ts = datetime.now(timezone.utc).isoformat()
    path = (write_path or "").strip()
    party = (counterparty or "").strip()
    door = (exclusive_door_url or "").strip()
    kind = (door_kind or "").strip().lower()
    fingerprint = (worker_fingerprint or "").strip()[:128]
    if not path or not party:
        raise ValueError("write_path and counterparty required")
    if not door:
        raise ValueError("exclusive_door_url required — the only mouth on their irreversible write")
    low = door.lower()
    if low.startswith("http://localhost") or "127.0.0.1" in low or "0.0.0.0" in low:
        raise ValueError("exclusive_door_url must not be localhost")
    if not low.startswith("https://"):
        raise ValueError("exclusive_door_url must be https")
    if kind not in ("cloudflare_worker", "gosu", "inline_proxy", "other"):
        raise ValueError("door_kind must be cloudflare_worker|gosu|inline_proxy|other")
    with db() as conn:
        _ensure_third_party_welds(conn)
        conn.execute(
            """INSERT INTO third_party_welds
               (id, write_path, counterparty, note, stripe_session_id,
                exclusive_door_url, door_kind, worker_fingerprint, exclusivity_attested, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?)""",
            (
                wid,
                path,
                party,
                (note or "").strip(),
                (stripe_session_id or "").strip() or None,
                door,
                kind,
                fingerprint or None,
                ts,
            ),
        )
    return {
        "id": wid,
        "write_path": path,
        "counterparty": party,
        "note": note,
        "stripe_session_id": stripe_session_id,
        "exclusive_door_url": door,
        "door_kind": kind,
        "worker_fingerprint": fingerprint or None,
        "exclusivity_attested": True,
        "created_at": ts,
        "their_production": True,
        "dogfood": False,
    }


def latest_dogfood_weld() -> dict | None:
    with db() as conn:
        _ensure_dogfood_table(conn)
        row = conn.execute(
            """SELECT id, write_path, operator, note, created_at
               FROM dogfood_welds ORDER BY created_at DESC LIMIT 1"""
        ).fetchone()
    return dict(row) if row else None


def latest_production_weld() -> dict | None:
    with db() as conn:
        _ensure_third_party_welds(conn)
        row = conn.execute(
            """SELECT id, write_path, counterparty, note, stripe_session_id,
                      exclusive_door_url, door_kind, worker_fingerprint,
                      exclusivity_attested, created_at
               FROM third_party_welds ORDER BY created_at DESC LIMIT 1"""
        ).fetchone()
    return dict(row) if row else None

