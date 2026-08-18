"""Cash-event notify — Discord/Slack webhook so you know when money hits."""
import os
import requests

NOTIFY_URL = os.getenv("GATE_NOTIFY_WEBHOOK", "").strip()


def money(title: str, body: str, extra: dict | None = None):
    if not NOTIFY_URL:
        return
    text = f"**{title}**\n{body}"
    if extra:
        text += "\n" + "\n".join(f"{k}: {v}" for k, v in extra.items() if v)
    payload = {"content": text, "text": text}
    try:
        requests.post(NOTIFY_URL, json=payload, timeout=8)
    except requests.RequestException:
        pass
