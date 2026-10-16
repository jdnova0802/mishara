"""Cash-event notify. A paid order must reach a person, not only the database."""
import os

import requests

NTFY_BASE = (os.getenv("GATE_NTFY_BASE") or "https://ntfy.sh").rstrip("/")


def _text(title: str, body: str, extra: dict | None) -> str:
    text = f"{title}\n{body}"
    if extra:
        text += "\n" + "\n".join(f"{k}: {v}" for k, v in extra.items() if v)
    return text


def configured() -> dict:
    token = (os.getenv("GATE_NTFY_TOKEN") or "").strip()
    topic = (os.getenv("GATE_NTFY_TOPIC") or "").strip()
    email = (os.getenv("GATE_NOTIFY_EMAIL") or "").strip()
    webhook = (os.getenv("GATE_NOTIFY_WEBHOOK") or "").strip()
    return {
        "webhook": bool(webhook),
        "email": bool(token and topic and email),
    }


def money(title: str, body: str, extra: dict | None = None) -> dict:
    """Post to Slack/Discord and email the operator. Never raises."""
    text = _text(title, body, extra)
    result = {"webhook": None, "email": None}

    webhook = (os.getenv("GATE_NOTIFY_WEBHOOK") or "").strip()
    if webhook:
        try:
            resp = requests.post(webhook, json={"content": text, "text": text}, timeout=8)
            result["webhook"] = resp.status_code < 400
        except requests.RequestException:
            result["webhook"] = False

    token = (os.getenv("GATE_NTFY_TOKEN") or "").strip()
    topic = (os.getenv("GATE_NTFY_TOPIC") or "").strip()
    email = (os.getenv("GATE_NOTIFY_EMAIL") or "").strip()
    if token and topic and email:
        try:
            result["email"] = _ntfy_email(topic, token, title, text, email)
        except Exception as exc:
            print(f"notify failed {type(exc).__name__}: {exc}", flush=True)
            result["email"] = False
        print(f"notify email={result['email']} title={_latin1_header(title)[:80]}", flush=True)
    return result


def _latin1_header(value: str) -> str:
    """HTTP headers are latin-1. An em dash in a title 500s the webhook."""
    cleaned = (
        value.replace("\u2014", "-")
        .replace("\u2013", "-")
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
    )
    return cleaned.encode("latin-1", "replace").decode("latin-1")


def _ntfy_email(topic: str, token: str, title: str, text: str, email: str) -> bool:
    url = f"{NTFY_BASE}/{topic}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Title": _latin1_header(title)[:200],
        "Content-Type": "text/plain",
        "Email": _latin1_header(email),
    }
    try:
        resp = requests.post(url, data=text.encode(), headers=headers, timeout=8)
    except (requests.RequestException, UnicodeError) as exc:
        print(f"ntfy email error {type(exc).__name__}", flush=True)
        return False
    if resp.status_code < 400:
        return True
    print(f"ntfy email status {resp.status_code} {resp.text[:180]}", flush=True)
    # Literal address not verified on the ntfy account. Fall back to the
    # account's primary verified address so the alert is still mailed.
    if resp.status_code == 400 and email.lower() != "yes":
        headers["Email"] = "yes"
        try:
            resp = requests.post(url, data=text.encode(), headers=headers, timeout=8)
        except (requests.RequestException, UnicodeError) as exc:
            print(f"ntfy email fallback error {type(exc).__name__}", flush=True)
            return False
        if resp.status_code >= 400:
            print(f"ntfy email fallback status {resp.status_code} {resp.text[:180]}", flush=True)
        return resp.status_code < 400
    return False
