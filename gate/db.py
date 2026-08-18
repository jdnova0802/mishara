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
                created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
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
