"""Isolate the drill from production mouths and from live money credentials.

Staging, for this repo, is a Gate process with money_real=false. There is no
separate staging hostname in-tree. Production hosts are refused by name.
"""
from __future__ import annotations

from urllib.parse import urlparse

PRODUCTION_HOSTS = frozenset(
    {
        "velaru.xyz",
        "www.velaru.xyz",
        "gate.velaru.xyz",
        "api.velaru.xyz",
        "mishara.app",
        "www.mishara.app",
        "dashboard.stripe.com",
        "api.stripe.com",
    }
)

FORBIDDEN_ENV = (
    "STRIPE_SECRET_KEY",
    "STRIPE_ISSUING_WEBHOOK_SECRET",
    "STRIPE_WEBHOOK_SECRET",
    "STRIPE_PRICE_ID",
    "GATE_RECEIPT_PRIVATE_KEY",
)

LOOPBACK = frozenset({"localhost", "127.0.0.1", "::1", "host.docker.internal", "0.0.0.0"})


class SandboxError(RuntimeError):
    pass


def origin(url: str) -> str:
    p = urlparse(url)
    if p.scheme not in ("http", "https") or not p.netloc:
        raise SandboxError(f"mouth URL is not http(s): {url!r}")
    return f"{p.scheme}://{p.netloc}"


def host_of(url: str) -> str:
    return (urlparse(url).hostname or "").lower()


def is_production_host(host: str) -> bool:
    h = (host or "").lower().rstrip(".")
    if h in PRODUCTION_HOSTS:
        return True
    if h.endswith(".velaru.xyz"):
        return True
    if h.endswith(".stripe.com"):
        return True
    return False


def assert_executor_env_clean(environ: dict[str, str]) -> None:
    present = [k for k in FORBIDDEN_ENV if (environ.get(k) or "").strip()]
    if present:
        raise SandboxError(
            "executor process has live-money env set: "
            + ", ".join(present)
            + ". Unset them. The drill never inherits Stripe or receipt private keys."
        )


def assert_mouth_allowed(url: str, *, extra_hosts: frozenset[str] | set[str] = frozenset()) -> None:
    h = host_of(url)
    if is_production_host(h):
        raise SandboxError(
            f"refusing production mouth host {h!r}. "
            "Point GATE_DRILL_MOUTH at a local Gate (http://127.0.0.1:5001/demo/issuing/mouth)."
        )
    allowed = LOOPBACK | {x.lower() for x in extra_hosts}
    if h not in allowed:
        raise SandboxError(
            f"mouth host {h!r} is not loopback and not in GATE_DRILL_ALLOW_HOSTS. "
            "This drill does not call an unknown public Gate."
        )
    if urlparse(url).scheme == "https" and h in LOOPBACK:
        # https to loopback is unusual; allow. Production https is already blocked by host.
        pass


def assert_not_money_real(config: dict) -> None:
    if config.get("money_real") is True:
        raise SandboxError(
            "issuing-mouth.json reports money_real=true. "
            "The drill only talks to a mouth that cannot move Stripe funds."
        )
