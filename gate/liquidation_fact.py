"""Aave V3 liquidation fact file. Ethereum mainnet, Pool.liquidationCall only.

One transaction hash in. One gate-receipt-v1 file out, signed with the same
Ed25519 key as every other Gate receipt. The file records what the chain and
one public candle said. It does not score the liquidation and it does not say
the sale was commercially reasonable.

The April 16, 2024 USDP liquidations, and the AIP 55 reimbursements, were Aave
V2. A transaction receipt is read when its LiquidationCall comes from one of
the Ethereum mainnet instances in the Aave address book: Core, Prime (Lido),
EtherFi, or Horizon. Each instance has its own pool, oracle, and data provider.
The public week list stays on Core.
"""

from __future__ import annotations

import json
import os
import tempfile
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable
from urllib.parse import urlencode

import requests
from Crypto.Hash import keccak

try:
    from gate import receipt as receipt_mod
except ImportError:
    import receipt as receipt_mod

@dataclass(frozen=True)
class Instance:
    """One Aave V3 Ethereum market from aave-dao/aave-address-book."""

    name: str
    address_book: str
    pool: str
    oracle: str
    data_provider: str


def _instance(name: str, address_book: str, pool: str, oracle: str, data_provider: str) -> Instance:
    return Instance(name, address_book, pool.lower(), oracle.lower(), data_provider.lower())


# Pool, oracle, and data provider are per instance. Prime is the Lido market.
# Calling Core's oracle for a Prime liquidation would price the wrong feed.
_INSTANCE_LIST = (
    _instance(
        "core",
        "AaveV3Ethereum",
        "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2",
        "0x54586be62e3c3580375ae3723c145253060ca0c2",
        "0x0a16f2fcc0d44fae41cc54e079281d84a363becd",
    ),
    _instance(
        "prime",
        "AaveV3EthereumLido",
        "0x4e033931ad43597d96d6bcc25c280717730b58b1",
        "0xe3c061981870c0c7b1f3c4f4bb36b95f1f260be6",
        "0xb85b2bfebec4f5f401dbf92ac147a3076391fcd5",
    ),
    _instance(
        "etherfi",
        "AaveV3EthereumEtherFi",
        "0x0aa97c284e98396202b6a04024f5e2c65026f3c0",
        "0x43b64f28a678944e0655404b0b98e443851cc34f",
        "0x7c8509591f9693d21280d96e149a08a3bf69cd0c",
    ),
    _instance(
        "horizon",
        "AaveV3EthereumHorizon",
        "0xae05cd22df81871bc7cc2a04becfb516bfe332c8",
        "0x985bcfab7e0f4ef2606cc5b64fc1a16311880442",
        "0x53519c32f73fe1797d10210c4950ffeba3b21504",
    ),
)
INSTANCES = {item.pool: item for item in _INSTANCE_LIST}
CORE = INSTANCES["0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"]
PRIME = INSTANCES["0x4e033931ad43597d96d6bcc25c280717730b58b1"]
ETHERFI = INSTANCES["0x0aa97c284e98396202b6a04024f5e2c65026f3c0"]
HORIZON = INSTANCES["0xae05cd22df81871bc7cc2a04becfb516bfe332c8"]
# Core aliases. The week scan and older callers use these.
POOL = CORE.pool
ORACLE = CORE.oracle
DATA_PROVIDER = CORE.data_provider
CHAIN_ID = 1
CHAIN_NAME = "ethereum"

# aave-v3-origin LiquidationLogic. Not an event field.
CLOSE_FACTOR_HF_THRESHOLD = 95 * 10**16  # 0.95e18
MIN_BASE_MAX_CLOSE_FACTOR_THRESHOLD = 2000 * 10**8  # 2000e8
DEFAULT_LIQUIDATION_CLOSE_FACTOR_BPS = 5000
MAX_LIQUIDATION_CLOSE_FACTOR_BPS = 10000

DEBT_REPAID_MIN_BASE = 1000 * 10**8  # $1,000 in Aave base currency (1e8 = $1)
WEEK_BLOCKS = 7 * 24 * 300  # 12-second blocks, one week
LOG_CHUNK = 2000
PAGE_LIMIT = 20
DOCUMENT_PRICE_USD = 49

# Alchemy's own pricing page: $0.525 / 1M CU. eth_getTransactionReceipt and
# eth_getBlockByNumber are 20 CU. eth_call is 26 CU. Archive state is on the
# free plan. Trace is not, and this file does not use a trace.
# One document: 1 receipt + 1 block + 12 eth_calls
# (account twice, base unit, four prices, two reserve configs, two user reserves, eMode).
RPC_CU_PER_DOCUMENT = 20 + 20 + 26 * 12
ALCHEMY_USD_PER_CU = 0.525 / 1_000_000

# address -> (symbol, binance spot, coinbase product). No pair means no candle.
# A feed is not substituted for a different asset.
_MARKETS: dict[str, tuple[str, str | None, str | None]] = {
    "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": ("WETH", "ETHUSDT", "ETH-USD"),
    "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599": ("WBTC", "BTCUSDT", "BTC-USD"),
    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": ("USDC", "USDCUSDT", "USDC-USD"),
    "0xdac17f958d2ee523a2206206994597c13d831ec7": ("USDT", None, "USDT-USD"),
    "0x6b175474e89094c44da98b954eedeac495271d0f": ("DAI", "DAIUSDT", "DAI-USD"),
    "0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9": ("AAVE", "AAVEUSDT", "AAVE-USD"),
    "0x514910771af9ca656af840dff83e8264ecf986ca": ("LINK", "LINKUSDT", "LINK-USD"),
    "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984": ("UNI", "UNIUSDT", "UNI-USD"),
    "0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0": ("wstETH", None, None),
    "0xae78736cd615f374d3085123a210448e74fc6393": ("rETH", None, None),
    "0xbe9895146f7af43049ca1c1ae358b0541ea49704": ("cbETH", None, None),
    "0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee": ("weETH", None, None),
    "0x40d16fc0246ad3160ccc09b8d0d3a2cd28ae6c2f": ("GHO", None, None),
    "0x83f20f44975d03b1b09e64809b757c47f942beea": ("sDAI", None, None),
    "0xd533a949740bb3306d119cc777fa900ba034cd52": ("CRV", "CRVUSDT", "CRV-USD"),
    "0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2": ("MKR", "MKRUSDT", "MKR-USD"),
    "0x5a98fcbea516cf06857215779fd812ca3bef1b32": ("LDO", "LDOUSDT", "LDO-USD"),
    "0xc00e94cb662c3520282e6f5717214004a7f26888": ("COMP", "COMPUSDT", "COMP-USD"),
    "0xba100000625a3754423978a60c9317c58a424e3d": ("BAL", "BALUSDT", "BAL-USD"),
    "0x111111111117dc0aa78b770fa6a738034120c302": ("1INCH", "1INCHUSDT", "1INCH-USD"),
    "0x4c9edd5852cd905f086c759e8383e09bff1e68b3": ("USDe", "USDEUSDT", "USDE-USD"),
}

# These answered an eth_call against state ~2,800 blocks old on 2026-11-05.
# PublicNode, Llama, Ankr, and 1RPC refused that call without a paid archive key.
_RPC_FALLBACKS = (
    "https://eth.drpc.org",
    "https://eth-mainnet.public.blastapi.io",
    "https://mainnet.gateway.tenderly.co",
    "https://rpc.mevblocker.io",
)

_cache_lock = threading.Lock()
_record_cache: dict[str, tuple[float, list]] = {}
_call_cache: dict[tuple, list[int]] = {}
_week_cache: dict[str, Any] = {"at": 0.0, "body": None}
_week_refreshing = False
_transport: Callable[[str, str, list], Any] | None = None
_http_get: Callable[[str], Any] | None = None

# Serve the last snapshot immediately. Rebuild in the background.
WEEK_MEMORY_TTL_SECONDS = 300
WEEK_REFRESH_SECONDS = 300

HF_READ_NOTE = (
    "eth_call at block N is the post-state of that block (after every transaction). "
    "getUserAccountData at block-1 is the position at the end of the previous block. "
    "Aave liquidates only when health factor is below 1. A reading above 1 at block-1 "
    "is not an off-by-one: the crossing can sit inside the liquidation block after an "
    "oracle update, then liquidationCall. eth_call at the liquidation block is after "
    "that call, so the health factor there is usually healthier, not the mid-block trigger. "
    "This file does not trace."
)

BONUS_UNITS_NOTE = (
    "Aave PercentageMath factor: 10000 is par (collateral seized equals debt covered). "
    "10450 is a 4.5% bonus (450 bps over par), not a 104.5% bonus. "
    "bonus_above_par_bps is the figure to read."
)


class LiquidationFactError(Exception):
    def __init__(self, code: str, detail: str):
        super().__init__(detail)
        self.code = code
        self.detail = detail


def set_transport(fn: Callable[[str, str, list], Any] | None) -> None:
    global _transport
    _transport = fn


def set_http_get(fn: Callable[[str], Any] | None) -> None:
    global _http_get
    _http_get = fn


def snapshot_path() -> str:
    override = (os.getenv("GATE_LIQ_SNAPSHOT_PATH") or "").strip()
    if override:
        return override
    db_path = (os.getenv("GATE_DB_PATH") or "").strip()
    if db_path:
        parent = os.path.dirname(os.path.abspath(db_path))
        if parent:
            return os.path.join(parent, "aave_v3_week_snapshot.json")
    return os.path.join(tempfile.gettempdir(), "gate-aave-v3-week.json")


_recent_lookups: list[str] = []
_RECENT_LIMIT = 12


def clear_caches() -> None:
    with _cache_lock:
        _record_cache.clear()
        _call_cache.clear()
        _week_cache["at"] = 0.0
        _week_cache["body"] = None
        _recent_lookups.clear()
    path = snapshot_path()
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
    except OSError:
        pass


def _load_week_snapshot() -> tuple[float, dict] | None:
    with _cache_lock:
        body = _week_cache["body"]
        at = _week_cache["at"]
        if body:
            return at, body
    path = snapshot_path()
    try:
        with open(path, encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError, TypeError):
        return None
    if not isinstance(payload, dict) or not isinstance(payload.get("body"), dict):
        return None
    try:
        at = float(payload.get("at") or 0)
    except (TypeError, ValueError):
        return None
    body = payload["body"]
    with _cache_lock:
        _week_cache["at"] = at
        _week_cache["body"] = body
    return at, body


def _save_week_snapshot(at: float, body: dict) -> None:
    path = snapshot_path()
    parent = os.path.dirname(os.path.abspath(path))
    try:
        os.makedirs(parent, exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as handle:
            json.dump({"at": at, "body": body}, handle, separators=(",", ":"))
        os.replace(tmp, path)
    except OSError:
        return
    with _cache_lock:
        _week_cache["at"] = at
        _week_cache["body"] = body


def _decorate_week_snapshot(body: dict, at: float, *, now: float) -> dict:
    out = dict(body)
    out["snapshot"] = True
    out["snapshot_at_unix"] = str(int(at))
    out["snapshot_age_seconds"] = str(max(0, int(now - at)))
    return out


def _kick_week_refresh() -> None:
    global _week_refreshing
    with _cache_lock:
        if _week_refreshing:
            return
        _week_refreshing = True

    def _run() -> None:
        global _week_refreshing
        try:
            public_week(force=True)
        except Exception:
            pass
        finally:
            with _cache_lock:
                _week_refreshing = False

    threading.Thread(target=_run, name="gate-liq-week-refresh", daemon=True).start()


def schedule_week_refresh() -> None:
    """Rebuild the week snapshot off the request path. Safe to call at process start."""
    _kick_week_refresh()


def keccak256(data: bytes) -> bytes:
    digest = keccak.new(digest_bits=256)
    digest.update(data)
    return digest.digest()


def selector(signature: str) -> bytes:
    return keccak256(signature.encode("ascii"))[:4]


def topic0(signature: str) -> str:
    return "0x" + keccak256(signature.encode("ascii")).hex()


LIQUIDATION_TOPIC = topic0(
    "LiquidationCall(address,address,address,uint256,uint256,address,bool)"
)
SEL_ACCOUNT = selector("getUserAccountData(address)")
SEL_EMODE = selector("getUserEMode(address)")
SEL_PRICE = selector("getAssetPrice(address)")
SEL_BASE_UNIT = selector("BASE_CURRENCY_UNIT()")
SEL_CONFIG = selector("getReserveConfigurationData(address)")
SEL_USER_RESERVE = selector("getUserReserveData(address,address)")


def _addr(word: bytes) -> str:
    return "0x" + word[-20:].hex()


def _hex_qty(n: int) -> str:
    return hex(n)


def _pad_addr(address: str) -> bytes:
    raw = bytes.fromhex(address.lower().removeprefix("0x"))
    if len(raw) != 20:
        raise LiquidationFactError("bad_address", address)
    return raw.rjust(32, b"\x00")


def _calldata(sel: bytes, *addrs: str) -> str:
    return "0x" + (sel + b"".join(_pad_addr(a) for a in addrs)).hex()


def _words(data_hex: str) -> list[int]:
    raw = bytes.fromhex(data_hex.removeprefix("0x"))
    if len(raw) % 32 != 0:
        raise LiquidationFactError("bad_abi", "eth_call result is not 32-byte words")
    return [int.from_bytes(raw[i : i + 32], "big") for i in range(0, len(raw), 32)]


def _rpc_urls() -> list[str]:
    chosen = (os.getenv("GATE_ETH_RPC_URL") or "").strip()
    urls = [chosen] if chosen else []
    for url in _RPC_FALLBACKS:
        if url not in urls:
            urls.append(url)
    return urls


def _rpc(method: str, params: list) -> Any:
    errors: list[str] = []
    for url in _rpc_urls():
        try:
            if _transport is not None:
                return _transport(url, method, params)
            response = requests.post(
                url,
                json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
                timeout=25,
            )
            body = response.json()
        except (requests.RequestException, ValueError) as exc:
            errors.append(f"{url}: {exc}")
            continue
        if isinstance(body, dict) and body.get("error"):
            errors.append(f"{url}: {body['error']}")
            continue
        if not isinstance(body, dict) or "result" not in body:
            errors.append(f"{url}: no result")
            continue
        return body["result"]
    raise LiquidationFactError("rpc_failed", "; ".join(errors)[:500])


def _eth_call(to: str, data: str, block: int) -> list[int]:
    key = (to.lower(), data.lower(), block)
    with _cache_lock:
        cached = _call_cache.get(key)
    if cached is not None:
        return cached
    result = _rpc("eth_call", [{"to": to, "data": data}, _hex_qty(block)])
    if not isinstance(result, str) or result == "0x":
        raise LiquidationFactError("eth_call_empty", f"{to} at {block}")
    words = _words(result)
    with _cache_lock:
        _call_cache[key] = words
    return words


def _block(number: int | str) -> dict:
    tag = number if isinstance(number, str) else _hex_qty(number)
    block = _rpc("eth_getBlockByNumber", [tag, False])
    if not isinstance(block, dict):
        raise LiquidationFactError("block_missing", str(number))
    return block


def asset_label(address: str) -> dict:
    key = address.lower()
    symbol, binance, coinbase = _MARKETS.get(key, (None, None, None))
    return {
        "address": key,
        "symbol": symbol,
        "binance_symbol": binance,
        "coinbase_product": coinbase,
    }


def percent_mul(value: int, bps: int) -> int:
    """Aave PercentageMath.percentMul, half up."""
    return (value * bps + 5000) // 10000


def mul_div_ceil(a: int, b: int, den: int) -> int:
    product = a * b
    if product == 0 or den == 0:
        return 0
    return (product + den - 1) // den


UINT256_MAX = 2**256 - 1


def health_factor_text(wad: int, debt_base: int) -> str | None:
    """Aave reports 2**256-1 when the position has no debt. That is not a health factor."""
    if debt_base == 0 or wad == UINT256_MAX:
        return None
    return _decimal(wad, 10**18)


def _decimal(value: int, scale: int) -> str:
    sign = "-" if value < 0 else ""
    value = abs(value)
    whole, frac = divmod(value, scale)
    text = f"{frac:0{len(str(scale - 1))}d}".rstrip("0")
    return sign + (str(whole) if not text else f"{whole}.{text}")


def _gap_bps(oracle_base: int, candle_close: str) -> str | None:
    try:
        negative = candle_close.startswith("-")
        text = candle_close[1:] if negative else candle_close
        if "." in text:
            left, right = text.split(".", 1)
            right = (right + "00000000")[:8]
        else:
            left, right = text, "00000000"
        scaled = int(left or "0") * 10**8 + int(right)
        if negative:
            scaled = -scaled
    except ValueError:
        return None
    if scaled <= 0:
        return None
    return str((oracle_base - scaled) * 10000 // scaled)


def decode_liquidation_log(log: dict) -> dict | None:
    topics = log.get("topics") or []
    if len(topics) < 4 or (topics[0] or "").lower() != LIQUIDATION_TOPIC:
        return None
    instance = INSTANCES.get((log.get("address") or "").lower())
    if instance is None:
        return None
    words = _words(log.get("data") or "0x")
    if len(words) < 4:
        return None
    return {
        "instance": instance,
        "tx_hash": (log.get("transactionHash") or "").lower(),
        "log_index": int(log.get("logIndex"), 16),
        "block_number": int(log.get("blockNumber"), 16),
        "collateral_asset": asset_label(_addr(bytes.fromhex(topics[1].removeprefix("0x")))),
        "debt_asset": asset_label(_addr(bytes.fromhex(topics[2].removeprefix("0x")))),
        "borrower": _addr(bytes.fromhex(topics[3].removeprefix("0x"))),
        "debt_to_cover": str(words[0]),
        "liquidated_collateral_amount": str(words[1]),
        "liquidator": _addr(words[2].to_bytes(32, "big")),
        "receive_a_token": bool(words[3]),
    }


def _account(user: str, block: int, instance: Instance = CORE) -> dict:
    words = _eth_call(instance.pool, _calldata(SEL_ACCOUNT, user), block)
    if len(words) < 6:
        raise LiquidationFactError("account_data_short", f"block {block}")
    return {
        "block": str(block),
        "call": "Pool.getUserAccountData(borrower)",
        "total_collateral_base": str(words[0]),
        "total_debt_base": str(words[1]),
        "available_borrows_base": str(words[2]),
        "current_liquidation_threshold_bps": str(words[3]),
        "ltv_bps": str(words[4]),
        "health_factor_wad": str(words[5]),
        "health_factor": health_factor_text(words[5], words[1]),
        "no_debt": words[1] == 0 or words[5] == UINT256_MAX,
        "below_one": words[1] > 0 and words[5] < 10**18,
    }


def _prices(assets: list[str], block: int, instance: Instance = CORE) -> dict[str, str]:
    out: dict[str, str] = {}
    for asset in assets:
        words = _eth_call(instance.oracle, _calldata(SEL_PRICE, asset), block)
        out[asset.lower()] = str(words[0])
    return out


def _base_unit(block: int, instance: Instance = CORE) -> int:
    words = _eth_call(instance.oracle, "0x" + SEL_BASE_UNIT.hex(), block)
    return words[0]


def _reserve_config(asset: str, block: int, instance: Instance = CORE) -> dict:
    words = _eth_call(instance.data_provider, _calldata(SEL_CONFIG, asset), block)
    if len(words) < 4:
        raise LiquidationFactError("reserve_config_short", asset)
    bonus = words[3]
    above = bonus - 10000 if bonus >= 10000 else bonus
    return {
        "block": str(block),
        "call": "AaveProtocolDataProvider.getReserveConfigurationData(collateral)",
        "decimals": str(words[0]),
        "ltv_bps": str(words[1]),
        "liquidation_threshold_bps": str(words[2]),
        "liquidation_bonus_bps": str(bonus),
        "aave_percent_factor": str(bonus),
        "par_factor": "10000",
        "bonus_above_par_bps": str(above),
        "bonus_percent": _decimal(above, 100),
        "reserve_factor_bps": str(words[4]) if len(words) > 4 else None,
        "note": BONUS_UNITS_NOTE,
    }


def _user_reserve(asset: str, user: str, block: int, instance: Instance = CORE) -> dict:
    words = _eth_call(instance.data_provider, _calldata(SEL_USER_RESERVE, asset, user), block)
    if len(words) < 3:
        raise LiquidationFactError("user_reserve_short", asset)
    return {
        "a_token_balance": str(words[0]),
        "stable_debt": str(words[1]),
        "variable_debt": str(words[2]),
    }


def _e_mode(user: str, block: int, instance: Instance = CORE) -> str:
    words = _eth_call(instance.pool, _calldata(SEL_EMODE, user), block)
    return str(words[0] if words else 0)


def close_factor_at_block(
    *,
    health_factor_wad: int,
    total_debt_base: int,
    collateral_balance: int,
    collateral_price: int,
    collateral_decimals: int,
    debt_stable: int,
    debt_variable: int,
    debt_price: int,
    debt_decimals: int,
    e_mode: int,
) -> dict:
    """Non-eMode cap from aave-v3-origin, applied to one block's state."""
    debt = debt_stable + debt_variable
    debt_unit = 10**debt_decimals
    coll_unit = 10**collateral_decimals
    reserve_debt_base = mul_div_ceil(debt, debt_price, debt_unit) if debt_price else 0
    reserve_coll_base = (collateral_balance * collateral_price) // coll_unit if collateral_price else 0
    half_total = percent_mul(total_debt_base, DEFAULT_LIQUIDATION_CLOSE_FACTOR_BPS)
    capped = (
        reserve_coll_base >= MIN_BASE_MAX_CLOSE_FACTOR_THRESHOLD
        and reserve_debt_base >= MIN_BASE_MAX_CLOSE_FACTOR_THRESHOLD
        and health_factor_wad > CLOSE_FACTOR_HF_THRESHOLD
    )
    if capped:
        max_bps = DEFAULT_LIQUIDATION_CLOSE_FACTOR_BPS
        if reserve_debt_base > half_total and debt_price:
            max_debt = (half_total * debt_unit) // debt_price
        else:
            max_debt = debt
    else:
        max_bps = MAX_LIQUIDATION_CLOSE_FACTOR_BPS
        max_debt = debt
    return {
        "state": "block_before",
        "applies": e_mode == 0,
        "e_mode": str(e_mode),
        "note": (
            "Computed from aave-v3-origin LiquidationLogic at the block before the transaction. "
            "The event does not store a close factor. eMode can change the bonus and which collateral counts, "
            "so applies is false when getUserEMode is not zero. This is not a trace of the call."
        ),
        "health_factor_wad": str(health_factor_wad),
        "reserve_collateral_base": str(reserve_coll_base),
        "reserve_debt_base": str(reserve_debt_base),
        "half_total_debt_base": str(half_total),
        "min_base_threshold": str(MIN_BASE_MAX_CLOSE_FACTOR_THRESHOLD),
        "health_factor_threshold_wad": str(CLOSE_FACTOR_HF_THRESHOLD),
        "max_debt_to_liquidate": str(max_debt),
        "max_close_factor_bps": str(max_bps),
    }


def _http_json(url: str) -> Any:
    if _http_get is not None:
        return _http_get(url)
    response = requests.get(url, timeout=15, headers={"User-Agent": "gate-liquidation-fact"})
    response.raise_for_status()
    return response.json()


def _binance_candle(symbol: str, minute: int) -> dict:
    query = urlencode(
        {"symbol": symbol, "interval": "1m", "startTime": minute * 1000, "limit": 1}
    )
    url = f"https://api.binance.com/api/v3/klines?{query}"
    rows = _http_json(url)
    if not isinstance(rows, list) or not rows or int(rows[0][0]) != minute * 1000:
        return {"venue": "binance", "symbol": symbol, "url": url, "error": "candle_missing"}
    row = rows[0]
    return {
        "venue": "binance",
        "symbol": symbol,
        "interval": "1m",
        "open_time_unix": str(minute),
        "open": str(row[1]),
        "high": str(row[2]),
        "low": str(row[3]),
        "close": str(row[4]),
        "url": url,
    }


def _coinbase_candle(product: str, minute: int) -> dict:
    start = datetime.fromtimestamp(minute, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    end = datetime.fromtimestamp(minute + 60, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    query = urlencode({"granularity": 60, "start": start, "end": end})
    url = f"https://api.exchange.coinbase.com/products/{product}/candles?{query}"
    rows = _http_json(url)
    match = None
    if isinstance(rows, list):
        for row in rows:
            if int(row[0]) == minute:
                match = row
                break
    if match is None:
        return {"venue": "coinbase", "product": product, "url": url, "error": "candle_missing"}
    out = {
        "venue": "coinbase",
        "product": product,
        "interval": "1m",
        "open_time_unix": str(minute),
        "low": str(match[1]),
        "high": str(match[2]),
        "open": str(match[3]),
        "close": str(match[4]),
        "url": url,
    }
    if product == "ETH-USD":
        out["note"] = "WETH candle is the ETH-USD market. weETH is not substituted."
    return out


def candle(asset: dict, timestamp: int) -> dict:
    """One public 1-minute candle containing the block timestamp. No paid feed.

    Binance is tried first. A blocked or empty response falls through to Coinbase
    when that asset has a product. A missing product is recorded, not filled in.
    """
    minute = timestamp - (timestamp % 60)
    attempts: list[tuple[str, str]] = []
    if asset.get("binance_symbol"):
        attempts.append(("binance", asset["binance_symbol"]))
    if asset.get("coinbase_product"):
        attempts.append(("coinbase", asset["coinbase_product"]))
    if not attempts:
        return {
            "venue": None,
            "error": "no_public_kline_for_asset",
            "symbol": asset.get("symbol"),
            "address": asset.get("address"),
        }
    errors: list[dict] = []
    for venue, symbol in attempts:
        try:
            if venue == "binance":
                found = _binance_candle(symbol, minute)
            else:
                found = _coinbase_candle(symbol, minute)
        except (requests.RequestException, ValueError, IndexError, TypeError) as exc:
            errors.append({"venue": venue, "symbol": symbol, "error": str(exc)[:180]})
            continue
        if not found.get("error"):
            if errors:
                found["prior_errors"] = errors
            return found
        errors.append(found)
    return {"venue": None, "error": "candle_unavailable", "tried": errors}


def _base_amount(token_amount: int, price: int, decimals: int, base_unit: int) -> int | None:
    if price <= 0 or base_unit <= 0:
        return None
    return token_amount * price // (10**decimals)


def reconstruct_log(decoded: dict, *, block_timestamp: int | None = None) -> dict:
    block = decoded["block_number"]
    before = block - 1
    if block_timestamp is None:
        header = _block(block)
        block_timestamp = int(header["timestamp"], 16)
    borrower = decoded["borrower"]
    collateral = decoded["collateral_asset"]["address"]
    debt = decoded["debt_asset"]["address"]
    instance = decoded.get("instance") or CORE
    account_before = _account(borrower, before, instance)
    account_after = _account(borrower, block, instance)
    unit = _base_unit(block, instance)
    prices_before = _prices([collateral, debt], before, instance)
    prices_at = _prices([collateral, debt], block, instance)
    config = _reserve_config(collateral, before, instance)
    debt_config = _reserve_config(debt, before, instance)
    coll_pos = _user_reserve(collateral, borrower, before, instance)
    debt_pos = _user_reserve(debt, borrower, before, instance)
    e_mode = int(_e_mode(borrower, before, instance))
    close = close_factor_at_block(
        health_factor_wad=int(account_before["health_factor_wad"]),
        total_debt_base=int(account_before["total_debt_base"]),
        collateral_balance=int(coll_pos["a_token_balance"]),
        collateral_price=int(prices_before[collateral]),
        collateral_decimals=int(config["decimals"]),
        debt_stable=int(debt_pos["stable_debt"]),
        debt_variable=int(debt_pos["variable_debt"]),
        debt_price=int(prices_before[debt]),
        debt_decimals=int(debt_config["decimals"]),
        e_mode=e_mode,
    )
    coll_candle = candle(decoded["collateral_asset"], block_timestamp)
    debt_candle = candle(decoded["debt_asset"], block_timestamp)
    debt_base = _base_amount(
        int(decoded["debt_to_cover"]),
        int(prices_at[debt]),
        int(debt_config["decimals"]),
        unit,
    )
    coll_base = _base_amount(
        int(decoded["liquidated_collateral_amount"]),
        int(prices_at[collateral]),
        int(config["decimals"]),
        unit,
    )
    return {
        "spec": "aave-v3-liquidation-fact-v1",
        "chain_id": CHAIN_ID,
        "chain": CHAIN_NAME,
        "protocol": "aave-v3",
        "instance": instance.name,
        "address_book": instance.address_book,
        "pool": instance.pool,
        "oracle": instance.oracle,
        "data_provider": instance.data_provider,
        "function": "Pool.liquidationCall",
        "score": None,
        "commercially_reasonable": None,
        "tx_hash": decoded["tx_hash"],
        "log_index": decoded["log_index"],
        "block_number": str(block),
        "block_timestamp_unix": str(block_timestamp),
        "block_timestamp_utc": datetime.fromtimestamp(block_timestamp, timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "borrower": borrower,
        "liquidator": decoded["liquidator"],
        "collateral_asset": decoded["collateral_asset"],
        "debt_asset": decoded["debt_asset"],
        "debt_to_cover": decoded["debt_to_cover"],
        "liquidated_collateral_amount": decoded["liquidated_collateral_amount"],
        "receive_a_token": decoded["receive_a_token"],
        "debt_repaid_base": None if debt_base is None else str(debt_base),
        "debt_repaid_usd": None if debt_base is None else _decimal(debt_base, unit),
        "collateral_seized_base": None if coll_base is None else str(coll_base),
        "collateral_seized_usd": None if coll_base is None else _decimal(coll_base, unit),
        "base_currency_unit": str(unit),
        "health_factor_block_before": account_before,
        "health_factor_liquidation_block": account_after,
        "health_factor_read": {
            "eth_call_block_tag": "post-state of that block, after every transaction",
            "block_before": str(before),
            "liquidation_block": str(block),
            "block_before_below_one": bool(account_before.get("below_one")),
            "liquidation_block_post_state_below_one": bool(account_after.get("below_one")),
            "mid_block_trigger_not_traced": True,
            "debt_oracle_higher_at_liquidation_block": int(prices_at[debt])
            > int(prices_before[debt]),
            "note": HF_READ_NOTE,
        },
        "oracle_price_base": {
            "unit": str(unit),
            "note": (
                "getAssetPrice returns the price of one whole token in base currency. "
                "at_block_before is the state before this block. "
                "at_liquidation_block is an eth_call at that block number, which is the state after the block, "
                "not a trace of this transaction. The event does not store the price."
            ),
            "collateral_at_block_before": prices_before[collateral],
            "debt_at_block_before": prices_before[debt],
            "collateral_at_liquidation_block": prices_at[collateral],
            "debt_at_liquidation_block": prices_at[debt],
        },
        "configured_bonus": config,
        "close_factor": close,
        "positions_block_before": {"collateral": coll_pos, "debt": debt_pos},
        "independent_price": {
            "collateral": coll_candle,
            "debt": debt_candle,
            "collateral_oracle_minus_candle_close_bps": _gap_bps(
                int(prices_at[collateral]), str(coll_candle.get("close") or "")
            ),
            "debt_oracle_minus_candle_close_bps": _gap_bps(
                int(prices_at[debt]), str(debt_candle.get("close") or "")
            ),
        },
        "recompute": {
            "event_topic0": LIQUIDATION_TOPIC,
            "instance": instance.name,
            "pool": instance.pool,
            "oracle": instance.oracle,
            "data_provider": instance.data_provider,
            "get_user_account_data": _calldata(SEL_ACCOUNT, borrower),
            "get_asset_price_collateral": _calldata(SEL_PRICE, collateral),
            "get_asset_price_debt": _calldata(SEL_PRICE, debt),
            "get_reserve_configuration_data": _calldata(SEL_CONFIG, collateral),
            "block_before": str(before),
            "liquidation_block": str(block),
            "collateral_candle_url": coll_candle.get("url"),
            "debt_candle_url": debt_candle.get("url"),
        },
    }


def logs_for_tx(tx_hash: str) -> list[dict]:
    receipt = _rpc("eth_getTransactionReceipt", [tx_hash])
    if not isinstance(receipt, dict):
        raise LiquidationFactError("tx_not_found", tx_hash)
    found = []
    other_pool = False
    for log in receipt.get("logs") or []:
        topics = log.get("topics") or []
        if not topics or (topics[0] or "").lower() != LIQUIDATION_TOPIC:
            continue
        if INSTANCES.get((log.get("address") or "").lower()) is None:
            other_pool = True
            continue
        decoded = decode_liquidation_log(log)
        if decoded:
            found.append(decoded)
    if not found:
        if other_pool:
            known = "; ".join(f"{item.name} {item.pool}" for item in _INSTANCE_LIST)
            raise LiquidationFactError(
                "not_aave_v3_pool",
                "This transaction emits LiquidationCall from a different contract. "
                "The April 16, 2024 USDP liquidations were Aave V2. This file reads "
                f"Aave V3 Ethereum pools: {known}.",
            )
        raise LiquidationFactError("no_liquidation", "No Aave V3 LiquidationCall in this transaction.")
    return found


def build_signed_document(records: list[dict], *, created_at: str) -> dict:
    canonical = {
        "spec": "gate-receipt-v1",
        "id": "liq-" + records[0]["tx_hash"].removeprefix("0x"),
        "gate": "Nisaba LLC",
        "created_at": created_at,
        "time_is_utc": True,
        "created_at_format": "iso-8601",
        "prev_receipt_hash": None,
        "fuse_id": None,
        "job_id": records[0]["tx_hash"],
        "decision": "FACT",
        "acted": None,
        "verify_url": None,
        "state": "aave-v3-liquidation-fact",
        "halt": None,
        "verdict": None,
        "record": {
            "spec": "aave-v3-liquidation-fact-v1",
            "price_usd": DOCUMENT_PRICE_USD,
            "rpc_cu_estimate": RPC_CU_PER_DOCUMENT,
            "rpc_usd_estimate_alchemy_payg": f"{RPC_CU_PER_DOCUMENT * ALCHEMY_USD_PER_CU:.6f}",
            "liquidations": records,
        },
    }
    canonical_json = receipt_mod.canonical_dumps(canonical)
    receipt_hash = receipt_mod.compute_receipt_hash(canonical_json)
    signature = receipt_mod.sign_receipt_hash(receipt_hash)
    document = {
        "spec": "gate-receipt-payload-v1",
        "canonical_receipt": canonical,
        "canonical_receipt_json": canonical_json,
        "receipt_hash": receipt_hash,
        "receipt_signature": signature,
        "receipt_public_key_fingerprint": receipt_mod.receipt_public_key_fingerprint(),
    }
    if receipt_mod.signing_required() and not signature:
        document["unsigned_halt"] = True
    return document


def records_for_tx(tx_hash: str) -> list[dict]:
    moment = time.time()
    with _cache_lock:
        hit = _record_cache.get(tx_hash)
        if hit and moment - hit[0] < 600:
            return hit[1]
    records = [reconstruct_log(item) for item in logs_for_tx(tx_hash)]
    with _cache_lock:
        _record_cache[tx_hash] = (moment, records)
    return records


def require_tx_hash(tx_hash: str) -> str:
    tx_hash = (tx_hash or "").strip().lower()
    if not tx_hash.startswith("0x") or len(tx_hash) != 66 or any(
        c not in "0123456789abcdef" for c in tx_hash[2:]
    ):
        raise LiquidationFactError("bad_tx_hash", "Expected 0x plus 64 hex characters.")
    return tx_hash


def cached_records(tx_hash: str) -> list[dict] | None:
    """Records already reconstructed for this hash, if the ten-minute cache still holds them."""
    try:
        tx_hash = require_tx_hash(tx_hash)
    except LiquidationFactError:
        return None
    moment = time.time()
    with _cache_lock:
        hit = _record_cache.get(tx_hash)
        if hit and moment - hit[0] < 600:
            return hit[1]
    return None


def document_for_tx(tx_hash: str, *, created_at: str | None = None) -> dict:
    tx_hash = require_tx_hash(tx_hash)
    created_at = created_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return build_signed_document(records_for_tx(tx_hash), created_at=created_at)


def with_lookup(document: dict, base_url: str) -> dict:
    """Envelope fields a forwarded file carries. They sit outside the signature."""
    tx_hash = document["canonical_receipt"]["job_id"]
    url = base_url.rstrip("/") + "/liquidations?tx=" + tx_hash
    out = dict(document)
    out["lookup_url"] = url
    out["share_line"] = "Aave V3 liquidation fact, no score: " + url
    out["lookup_url_not_signed"] = (
        "lookup_url and share_line sit outside the signed canonical receipt. "
        "They are how a forwarded file points at the next lookup."
    )
    return out


def summary_line(document: dict) -> str:
    rows = document["canonical_receipt"]["record"]["liquidations"]
    if not rows:
        return "Aave V3 liquidation fact. No score."
    row = rows[0]
    hf = (row.get("health_factor_block_before") or {}).get("health_factor") or "unread"
    bonus = (row.get("configured_bonus") or {}).get("bonus_above_par_bps") or "?"
    instance = row.get("instance") or "aave-v3"
    extra = f" {len(rows)} events in this transaction." if len(rows) > 1 else ""
    return (
        f"{instance} · health factor {hf} at the previous block · "
        f"bonus {bonus} bps over par · no score.{extra}"
    )


def note_public_lookup(tx_hash: str) -> None:
    tx_hash = require_tx_hash(tx_hash)
    with _cache_lock:
        if tx_hash in _recent_lookups:
            _recent_lookups.remove(tx_hash)
        _recent_lookups.insert(0, tx_hash)
        del _recent_lookups[_RECENT_LIMIT:]


def recent_public_lookups() -> list[str]:
    with _cache_lock:
        return list(_recent_lookups)


def etherscan_bookmarklet(base_url: str) -> str:
    """Drag this to the bookmark bar. On an Etherscan /tx/ page it opens the fact file."""
    base = base_url.rstrip("/") + "/liquidations?tx="
    return (
        "javascript:(function(){var m=location.pathname.match(/\\/tx\\/(0x[a-fA-F0-9]{64})/);"
        "if(!m){window.alert('Open an Etherscan transaction page first.');return;}"
        "location.href=" + json.dumps(base) + "+m[1];})();"
    )


def _get_logs(from_block: int, to_block: int) -> list[dict]:
    if from_block > to_block:
        return []
    try:
        chunk = _rpc(
            "eth_getLogs",
            [
                {
                    "fromBlock": _hex_qty(from_block),
                    "toBlock": _hex_qty(to_block),
                    "address": POOL,
                    "topics": [LIQUIDATION_TOPIC],
                }
            ],
        )
    except LiquidationFactError:
        if to_block - from_block < 1:
            raise
        mid = (from_block + to_block) // 2
        return _get_logs(from_block, mid) + _get_logs(mid + 1, to_block)
    if not isinstance(chunk, list):
        return []
    if len(chunk) >= 10000 and to_block > from_block:
        mid = (from_block + to_block) // 2
        return _get_logs(from_block, mid) + _get_logs(mid + 1, to_block)
    return chunk


def public_week(*, now: float | None = None, force: bool = False) -> dict:
    """This week's V3 liquidations at or above $1,000 of debt repaid, facts only."""
    moment = time.time() if now is None else now
    if not force:
        with _cache_lock:
            cached = _week_cache["body"]
            cached_at = _week_cache["at"]
        if cached and moment - cached_at < WEEK_MEMORY_TTL_SECONDS:
            return cached
        snap = _load_week_snapshot()
        if snap and moment - snap[0] < WEEK_MEMORY_TTL_SECONDS:
            return snap[1]
    head = _block("latest")
    head_n = int(head["number"], 16)
    head_ts = int(head["timestamp"], 16)
    from_block = max(0, head_n - WEEK_BLOCKS)
    raw_logs = _get_logs(from_block, head_n)
    decoded = [item for item in (decode_liquidation_log(log) for log in raw_logs) if item]
    enriched: list[dict] = []
    errors: list[str] = []
    # Price debt once per (block, asset), then keep rows at or above the threshold.
    priced: list[tuple[int, dict, int]] = []
    unit = _base_unit(head_n)
    for item in decoded:
        try:
            debt_cfg = _reserve_config(item["debt_asset"]["address"], item["block_number"])
            price = int(_prices([item["debt_asset"]["address"]], item["block_number"])[item["debt_asset"]["address"]])
            base = _base_amount(int(item["debt_to_cover"]), price, int(debt_cfg["decimals"]), unit)
        except LiquidationFactError as exc:
            errors.append(f"{item['tx_hash']}: {exc.code}")
            continue
        if base is None or base < DEBT_REPAID_MIN_BASE:
            continue
        priced.append((base, item, price))
    priced.sort(key=lambda row: row[0], reverse=True)
    shown = priced[:PAGE_LIMIT]
    for base, item, _price in shown:
        try:
            record = reconstruct_log(item)
            enriched.append(record)
        except LiquidationFactError as exc:
            errors.append(f"{item['tx_hash']}: {exc.code}")
    body = {
        "spec": "aave-v3-liquidation-week-v1",
        "ok": True,
        "chain_id": CHAIN_ID,
        "instance": CORE.name,
        "pool": POOL,
        "from_block": str(from_block),
        "to_block": str(head_n),
        "head_timestamp_utc": datetime.fromtimestamp(head_ts, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "min_debt_repaid_base": str(DEBT_REPAID_MIN_BASE),
        "min_debt_repaid_usd": "1000",
        "matched": len(priced),
        "shown": len(enriched),
        "truncated": len(priced) > len(enriched),
        "events_seen": len(decoded),
        "score": None,
        "commercially_reasonable": None,
        "document_price_usd": DOCUMENT_PRICE_USD,
        "rpc_usd_estimate_alchemy_payg": f"{RPC_CU_PER_DOCUMENT * ALCHEMY_USD_PER_CU:.6f}",
        "rows": enriched,
        "row_errors": errors[:10],
    }
    _save_week_snapshot(moment, body)
    return body


def public_week_or_error() -> tuple[dict, int]:
    now = time.time()
    snap = _load_week_snapshot()
    if snap:
        at, body = snap
        if now - at >= WEEK_REFRESH_SECONDS:
            _kick_week_refresh()
        return _decorate_week_snapshot(body, at, now=now), 200
    try:
        body = public_week(now=now, force=True)
        return _decorate_week_snapshot(body, now, now=now), 200
    except LiquidationFactError as exc:
        return {
            "spec": "aave-v3-liquidation-week-v1",
            "ok": False,
            "error": exc.code,
            "detail": exc.detail,
            "pool": POOL,
            "score": None,
            "commercially_reasonable": None,
            "document_price_usd": DOCUMENT_PRICE_USD,
            "rows": [],
        }, 503


def lookup_cost_note() -> str:
    usd = RPC_CU_PER_DOCUMENT * ALCHEMY_USD_PER_CU
    return (
        f"Alchemy Pay As You Go lists $0.525 per million compute units, archive included, "
        f"eth_call at 26 units. One document is about {RPC_CU_PER_DOCUMENT} units, ${usd:.6f}. "
        f"The document is ${DOCUMENT_PRICE_USD}. Checkout is not wired."
    )
