"""Aave V3 liquidation fact file. Run from gate/."""
from __future__ import annotations

import base64
import json
import os
import sys
import tempfile
import unittest
import uuid
from unittest import mock

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(
    tempfile.gettempdir(), f"gate-liq-fact-{uuid.uuid4().hex}.db"
)
os.environ["GATE_LIQ_SNAPSHOT_PATH"] = os.path.join(
    tempfile.gettempdir(), f"gate-liq-snap-{uuid.uuid4().hex}.json"
)

_priv = Ed25519PrivateKey.generate()
os.environ["GATE_RECEIPT_PRIVATE_KEY"] = base64.b64encode(
    _priv.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
).decode("ascii")
os.environ["GATE_RECEIPT_PUBLIC_KEY"] = base64.b64encode(
    _priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
).decode("ascii")

import app as gate_app  # noqa: E402
import demo_limit  # noqa: E402
import liquidation_fact as fact  # noqa: E402
import offline_verify  # noqa: E402

WETH = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
USDC = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
BORROWER = "0x1111111111111111111111111111111111111111"
LIQUIDATOR = "0x2222222222222222222222222222222222222222"
TX = "0x" + "ab" * 32
V2_POOL = "0x7d2768de32b0b80b7a3454c06bdac94a69ddc7a9"
BLOCK = 19_000_000
TS = 1_710_000_000


def _word(n: int) -> bytes:
    return n.to_bytes(32, "big")


def _topic_addr(address: str) -> str:
    return "0x" + address.removeprefix("0x").rjust(64, "0")


def _encode(words: list[int]) -> str:
    return "0x" + b"".join(_word(n) for n in words).hex()


def _log(address: str = fact.POOL) -> dict:
    data = _encode(
        [
            1_000_000_000,  # 1000 USDC
            4 * 10**17,  # 0.4 WETH
            int(LIQUIDATOR, 16),
            0,
        ]
    )
    return {
        "address": address,
        "topics": [
            fact.LIQUIDATION_TOPIC,
            _topic_addr(WETH),
            _topic_addr(USDC),
            _topic_addr(BORROWER),
        ],
        "data": data,
        "transactionHash": TX,
        "logIndex": hex(4),
        "blockNumber": hex(BLOCK),
    }


class LiquidationFactTests(unittest.TestCase):
    def setUp(self):
        fact.clear_caches()
        fact.set_transport(self.transport)
        fact.set_http_get(self.http_get)
        self.calls: list[tuple[str, str]] = []

    def tearDown(self):
        fact.set_transport(None)
        fact.set_http_get(None)
        fact.clear_caches()

    def http_get(self, url: str):
        self.calls.append(("GET", url))
        minute = (TS // 60) * 60
        if "binance.com" in url and "ETHUSDT" in url:
            return [[minute * 1000, "3001", "3010", "2990", "3002", "10"]]
        if "binance.com" in url and "USDCUSDT" in url:
            return [[minute * 1000, "0.9998", "1.0002", "0.9997", "1.0001", "10"]]
        raise AssertionError(url)

    def transport(self, url, method, params):
        self.calls.append((method, url))
        if method == "eth_getTransactionReceipt":
            return {"logs": [_log()], "blockNumber": hex(BLOCK)}
        if method == "eth_getBlockByNumber":
            number = int(params[0], 16) if params[0] != "latest" else BLOCK
            return {"number": hex(number), "timestamp": hex(TS)}
        if method == "eth_getLogs":
            return [_log()]
        if method == "eth_call":
            data = params[0]["data"]
            to = params[0]["to"].lower()
            if data.startswith("0x" + fact.SEL_ACCOUNT.hex()):
                return _encode([5000 * 10**8, 4000 * 10**8, 0, 8000, 7500, 99 * 10**16])
            if data.startswith("0x" + fact.SEL_EMODE.hex()):
                return _encode([0])
            if data.startswith("0x" + fact.SEL_BASE_UNIT.hex()):
                return _encode([10**8])
            if data.startswith("0x" + fact.SEL_PRICE.hex()):
                asset = "0x" + data[-40:]
                price = 3000 * 10**8 if asset == WETH else 10**8
                return _encode([price])
            if data.startswith("0x" + fact.SEL_CONFIG.hex()):
                asset = "0x" + data[-40:]
                decimals = 18 if asset == WETH else 6
                bonus = 10500 if asset == WETH else 10400
                return _encode([decimals, 8000, 8300, bonus, 1000, 1, 1, 0, 1, 0])
            if data.startswith("0x" + fact.SEL_USER_RESERVE.hex()):
                asset = "0x" + data[10:74][-40:]
                if asset == WETH:
                    return _encode([2 * 10**18, 0, 0, 0, 0, 0, 0, 0, 1])
                return _encode([0, 0, 2000 * 10**6, 0, 0, 0, 0, 0, 0])
            raise AssertionError(data[:20])
        raise AssertionError(method)

    def test_candle_uses_coinbase_when_binance_is_blocked(self):
        def http_get(url: str):
            if "binance.com" in url:
                raise fact.requests.RequestException("451 restricted")
            if "ETH-USD" in url:
                minute = (TS // 60) * 60
                return [[minute, "1", "2", "3", "2428.08", "1"], [minute + 60, "1", "2", "3", "9", "1"]]
            raise AssertionError(url)

        fact.set_http_get(http_get)
        found = fact.candle(fact.asset_label(WETH), TS)
        self.assertEqual(found["venue"], "coinbase")
        self.assertEqual(found["close"], "2428.08")
        self.assertIn("WETH candle is the ETH-USD market", found["note"])
        self.assertTrue(found["prior_errors"])

    def test_selector_matches_erc20_transfer(self):
        self.assertEqual(fact.selector("transfer(address,uint256)").hex(), "a9059cbb")

    def test_v2_pool_is_refused(self):
        def transport(url, method, params):
            if method == "eth_getTransactionReceipt":
                return {"logs": [_log(V2_POOL)]}
            raise AssertionError(method)

        fact.set_transport(transport)
        with self.assertRaises(fact.LiquidationFactError) as caught:
            fact.document_for_tx(TX, created_at="2026-11-05T12:00:00Z")
        self.assertEqual(caught.exception.code, "not_aave_v3_pool")
        self.assertIn(fact.PRIME.pool, str(caught.exception))

    def test_prime_pool_uses_its_own_oracle_and_data_provider(self):
        targets: list[str] = []

        def transport(url, method, params):
            if method == "eth_getTransactionReceipt":
                return {"logs": [_log(fact.PRIME.pool)], "blockNumber": hex(BLOCK)}
            if method == "eth_call":
                targets.append(params[0]["to"].lower())
            return self.transport(url, method, params)

        fact.set_transport(transport)
        document = fact.document_for_tx(TX, created_at="2026-11-05T12:00:00Z")
        record = document["canonical_receipt"]["record"]["liquidations"][0]
        self.assertEqual(record["instance"], "prime")
        self.assertEqual(record["address_book"], "AaveV3EthereumLido")
        self.assertEqual(record["pool"], fact.PRIME.pool)
        self.assertEqual(record["oracle"], fact.PRIME.oracle)
        self.assertEqual(record["data_provider"], fact.PRIME.data_provider)
        self.assertIn(fact.PRIME.pool, targets)
        self.assertIn(fact.PRIME.oracle, targets)
        self.assertIn(fact.PRIME.data_provider, targets)
        self.assertNotIn(fact.CORE.oracle, targets)
        self.assertIsNone(record["commercially_reasonable"])
        self.assertEqual(len(fact.INSTANCES), 4)

    def test_signed_file_verifies_and_states_no_conclusion(self):
        document = fact.document_for_tx(TX, created_at="2026-11-05T12:00:00Z")
        pub = base64.b64decode(os.environ["GATE_RECEIPT_PUBLIC_KEY"])
        verdict = offline_verify.verify_document(document, pub)
        self.assertEqual(verdict["verdict"], "valid", verdict)
        record = document["canonical_receipt"]["record"]["liquidations"][0]
        self.assertIsNone(record["score"])
        self.assertIsNone(record["commercially_reasonable"])
        self.assertEqual(record["pool"], fact.POOL)
        self.assertEqual(record["health_factor_block_before"]["health_factor"], "0.99")
        self.assertEqual(record["health_factor_liquidation_block"]["health_factor"], "0.99")
        self.assertTrue(record["health_factor_read"]["mid_block_trigger_not_traced"])
        self.assertEqual(record["configured_bonus"]["liquidation_bonus_bps"], "10500")
        self.assertEqual(record["configured_bonus"]["aave_percent_factor"], "10500")
        self.assertEqual(record["configured_bonus"]["bonus_above_par_bps"], "500")
        self.assertEqual(record["configured_bonus"]["bonus_percent"], "5")
        self.assertIn("not a 104.5% bonus", record["configured_bonus"]["note"])
        self.assertEqual(record["oracle_price_base"]["collateral_at_liquidation_block"], str(3000 * 10**8))
        self.assertEqual(record["independent_price"]["collateral"]["close"], "3002")
        self.assertEqual(record["independent_price"]["collateral_oracle_minus_candle_close_bps"], "-7")
        self.assertEqual(record["close_factor"]["max_close_factor_bps"], "5000")
        self.assertTrue(record["close_factor"]["applies"])
        self.assertEqual(record["debt_repaid_base"], str(1000 * 10**8))
        self.assertEqual(record["debt_repaid_usd"], "1000")
        self.assertIsNone(fact.health_factor_text(2**256 - 1, 0))
        document["canonical_receipt"]["record"]["liquidations"][0]["debt_to_cover"] = "1"
        document.pop("canonical_receipt_json")
        self.assertEqual(offline_verify.verify_document(document, pub)["verdict"], "invalid")

    def test_page_lists_facts_without_a_score(self):
        gate_app.app.config["TESTING"] = True
        client = gate_app.app.test_client()
        page = client.get("/liquidations")
        self.assertEqual(page.status_code, 200)
        body = page.get_data(as_text=True)
        self.assertIn("No finding on commercial reasonableness.", body)
        self.assertIn("0.99", body)
        self.assertIn("500 bps", body)
        self.assertIn("5%", body)
        self.assertNotIn("reasonableness score", body)
        one = client.get("/liquidations?tx=" + TX)
        self.assertEqual(one.status_code, 200)
        self.assertIn(TX, one.get_data(as_text=True))
        download = client.get("/v1/liquidation-fact/" + TX)
        self.assertEqual(download.status_code, 200)
        payload = download.get_json()
        self.assertEqual(payload["canonical_receipt"]["spec"], "gate-receipt-v1")
        missing = client.get("/v1/liquidation-fact/0x1234")
        self.assertEqual(missing.status_code, 400)
        self.assertEqual(missing.get_json()["error"], "bad_tx_hash")

    def test_week_json_is_the_same_facts(self):
        gate_app.app.config["TESTING"] = True
        client = gate_app.app.test_client()
        response = client.get("/.well-known/aave-v3-liquidations.json")
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertTrue(body["ok"])
        self.assertEqual(body["rows"][0]["tx_hash"], TX)
        self.assertIsNone(body["score"])
        self.assertNotIn("document_price_usd", body)
        self.assertNotIn("price_usd", body["rows"][0])
        self.assertIn("The lookup at /liquidations is free.", body["rpc_cost_note"])
        self.assertEqual(body["rows"][0]["configured_bonus"]["bonus_above_par_bps"], "500")
        self.assertTrue(body.get("snapshot"))

    def test_bonus_factor_10450_is_450_bps_over_par(self):
        def transport(url, method, params):
            if method == "eth_call" and params[0]["data"].startswith("0x" + fact.SEL_CONFIG.hex()):
                return _encode([6, 0, 7800, 10450, 1000, 1, 1, 0, 1, 0])
            return self.transport(url, method, params)

        fact.set_transport(transport)
        cfg = fact._reserve_config(USDC, BLOCK)
        self.assertEqual(cfg["aave_percent_factor"], "10450")
        self.assertEqual(cfg["bonus_above_par_bps"], "450")
        self.assertEqual(cfg["bonus_percent"], "4.5")

    def test_health_factor_above_one_is_previous_block_post_state(self):
        before_wad = 1_005_410_170_254_363_893
        after_wad = 1_184_079_912_633_315_912

        def transport(url, method, params):
            if method == "eth_getTransactionReceipt":
                log = _log()
                log["topics"] = [
                    fact.LIQUIDATION_TOPIC,
                    _topic_addr(USDC),
                    _topic_addr(WETH),
                    _topic_addr(BORROWER),
                ]
                return {"logs": [log], "blockNumber": hex(BLOCK)}
            if method == "eth_call" and params[0]["data"].startswith("0x" + fact.SEL_ACCOUNT.hex()):
                block = int(params[1], 16)
                wad = before_wad if block == BLOCK - 1 else after_wad
                return _encode([5000 * 10**8, 4000 * 10**8, 0, 8000, 7500, wad])
            if method == "eth_call" and params[0]["data"].startswith("0x" + fact.SEL_PRICE.hex()):
                asset = "0x" + params[0]["data"][-40:]
                block = int(params[1], 16)
                if asset == WETH:
                    price = 2367 * 10**8 if block == BLOCK else 2353 * 10**8
                else:
                    price = 10**8
                return _encode([price])
            return self.transport(url, method, params)

        fact.set_transport(transport)
        document = fact.document_for_tx(TX, created_at="2026-11-05T12:00:00Z")
        record = document["canonical_receipt"]["record"]["liquidations"][0]
        self.assertEqual(record["health_factor_block_before"]["block"], str(BLOCK - 1))
        self.assertFalse(record["health_factor_read"]["block_before_below_one"])
        self.assertFalse(record["health_factor_read"]["liquidation_block_post_state_below_one"])
        self.assertTrue(record["health_factor_read"]["debt_oracle_higher_at_liquidation_block"])
        self.assertIn("not an off-by-one", record["health_factor_read"]["note"])
        self.assertTrue(record["health_factor_block_before"]["health_factor"].startswith("1.0054"))
        self.assertTrue(record["health_factor_liquidation_block"]["health_factor"].startswith("1.184"))

    def test_week_page_serves_snapshot_without_a_second_log_scan(self):
        gate_app.app.config["TESTING"] = True
        client = gate_app.app.test_client()
        first = client.get("/.well-known/aave-v3-liquidations.json")
        self.assertEqual(first.status_code, 200)
        calls_after_first = list(self.calls)

        def boom(url, method, params):
            raise fact.LiquidationFactError("rpc_failed", "should use snapshot")

        fact.set_transport(boom)
        second = client.get("/liquidations")
        self.assertEqual(second.status_code, 200)
        html = second.get_data(as_text=True)
        self.assertIn("No finding on commercial reasonableness.", html)
        self.assertIn("500 bps", html)
        self.assertEqual(self.calls, calls_after_first)

    def test_public_lookup_is_free_and_caps_new_hashes(self):
        demo_limit._liquidation_hits.clear()
        gate_app.app.config["TESTING"] = True
        client = gate_app.app.test_client()
        page = client.get("/liquidations?tx=" + TX)
        self.assertEqual(page.status_code, 200)
        body = page.get_data(as_text=True)
        self.assertIn("Free. No account.", body)
        self.assertIn("No finding on commercial reasonableness.", body)
        self.assertIn("health factor 0.99", body)
        self.assertIn('property="og:description"', body)
        self.assertIn("/liquidations?tx=" + TX, body)
        self.assertIn("Etherscan → fact file", body)
        self.assertIn("Copy a line for a forum", body)
        self.assertNotIn("Checkout is not wired", body)

        download = client.get("/v1/liquidation-fact/" + TX)
        self.assertEqual(download.status_code, 200)
        self.assertIn("inline", download.headers["Content-Disposition"])
        payload = download.get_json()
        self.assertTrue(payload["share_line"].endswith(payload["lookup_url"]))
        self.assertIn("/liquidations?tx=" + TX, payload["lookup_url"])
        self.assertNotIn("lookup_url", payload["canonical_receipt_json"])
        self.assertNotIn("price_usd", payload["canonical_receipt"]["record"])
        self.assertNotIn("price_usd", payload["canonical_receipt_json"])
        self.assertIn("The lookup at /liquidations is free.", payload["canonical_receipt"]["record"]["rpc_cost_note"])
        pub = base64.b64decode(os.environ["GATE_RECEIPT_PUBLIC_KEY"])
        self.assertEqual(offline_verify.verify_document(payload, pub)["verdict"], "valid")

        other = "0x" + "cd" * 32
        third = "0x" + "ef" * 32
        junk = client.get(
            "/v1/liquidation-fact/0x1234",
            headers={"X-Forwarded-For": "7.7.7.7"},
        )
        self.assertEqual(junk.status_code, 400)
        with mock.patch.object(demo_limit, "LIQUIDATION_LIMIT", 1):
            first = client.get(
                "/v1/liquidation-fact/" + other,
                headers={"X-Forwarded-For": "7.7.7.7"},
            )
            self.assertEqual(first.status_code, 200, first.get_json())
            again = client.get(
                "/v1/liquidation-fact/" + other,
                headers={"X-Forwarded-For": "7.7.7.7"},
            )
            self.assertEqual(again.status_code, 200)
            blocked = client.get(
                "/v1/liquidation-fact/" + third,
                headers={"X-Forwarded-For": "7.7.7.7"},
            )
            self.assertEqual(blocked.status_code, 429)
            self.assertEqual(blocked.get_json()["error"], "rate_limited")
            self.assertEqual(blocked.headers["Retry-After"], "3600")
            spoofed = client.get(
                "/v1/liquidation-fact/" + third,
                headers={"X-Forwarded-For": "1.2.3.4, 7.7.7.7"},
            )
            self.assertEqual(spoofed.status_code, 429)
            fresh = client.get(
                "/v1/liquidation-fact/" + third,
                headers={"X-Forwarded-For": "8.8.8.8"},
            )
            self.assertEqual(fresh.status_code, 200)
        demo_limit._liquidation_hits.clear()
