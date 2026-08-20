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
) -> None:
    with db() as conn:
        conn.execute(
            """INSERT INTO bind_tickets
               (id, job_id, fuse_id, event_id, receipt_hash, token_hash,
                not_before, not_after, spend_fingerprint, license_id,
                counterpart_fingerprint, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
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


def has_dogfood_weld() -> bool:
    """First-party dogfood weld — never flips their_production."""
    with db() as conn:
        _ensure_dogfood_table(conn)
        row = conn.execute("SELECT COUNT(*) AS n FROM dogfood_welds").fetchone()
    return bool(row and row["n"] > 0)


def has_gate_production_weld() -> bool:
    """Third-party production weld only. Dogfood rows must not flip this."""
    with db() as conn:
        cols = _table_cols(conn, "production_welds")
        if not cols:
            return False
        if "dogfood" in cols:
            # Legacy table: only non-dogfood rows count as their_production
            row = conn.execute(
                "SELECT COUNT(*) AS n FROM production_welds WHERE COALESCE(dogfood, 0) = 0"
            ).fetchone()
            return bool(row and row["n"] > 0)
        if "counterparty" in cols:
            row = conn.execute("SELECT COUNT(*) AS n FROM production_welds").fetchone()
            return bool(row and row["n"] > 0)
        # Unknown legacy shape — refuse to claim production
        return False


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


def latest_dogfood_weld() -> dict | None:
    with db() as conn:
        _ensure_dogfood_table(conn)
        row = conn.execute(
            """SELECT id, write_path, operator, note, created_at
               FROM dogfood_welds ORDER BY created_at DESC LIMIT 1"""
        ).fetchone()
    return dict(row) if row else None

