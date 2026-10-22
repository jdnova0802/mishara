"""Minimal Base log for a seal root.

The contract stores nothing. commit() copies three words into a LOG and stops.
Broadcast stays in this module so the web process never signs or sends.

Gas model (EIP-1559, target address pre-warmed by the transaction):
  21000 intrinsic
  + 16 per non-zero calldata byte, 4 per zero byte
  + execution of the dispatcher, CALLDATACOPY, and LOG1
A commit of three 32-byte words is about 25,000 gas. Callers refuse to
broadcast a commit whose estimate is above COMMIT_GAS_CEILING.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
_GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
_GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

_KECCAK_ROT = (
    (0, 36, 3, 41, 18),
    (1, 44, 10, 45, 2),
    (62, 6, 43, 15, 61),
    (28, 55, 25, 21, 56),
    (27, 20, 39, 8, 14),
)
_KECCAK_RC = (
    0x0000000000000001, 0x0000000000008082, 0x800000000000808A, 0x8000000080008000,
    0x000000000000808B, 0x0000000080000001, 0x8000000080008081, 0x8000000000008009,
    0x000000000000008A, 0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
    0x000000008000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
    0x8000000000008002, 0x8000000000000080, 0x000000000000800A, 0x800000008000000A,
    0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008,
)

COMMIT_GAS_CEILING = 30_000
DEPLOY_GAS_CEILING = 150_000
MEMO_COMMIT_GAS = 25_000
# Base Sepolia eth_estimateGas, state-override of this runtime, 22 Oct 2026: 24408.
# The static model for that same calldata is 23838. Both sit on the memo's 25000.
DEFAULT_MAX_FEE_WEI = 200_000_000  # 0.2 gwei; about one cent at the memo's ETH price for 25k gas
DEFAULT_PRIORITY_WEI = 1_000_000  # 0.001 gwei

BASE_CHAIN_ID = 8453
BASE_SEPOLIA_CHAIN_ID = 84532
BASE_RPC = "https://mainnet.base.org"
BASE_SEPOLIA_RPC = "https://sepolia.base.org"

EVENT_SIG = "SealRoot(uint256,bytes32,bytes32)"
COMMIT_SIG = "commit(uint256,bytes32,bytes32)"


def keccak256(data: bytes) -> bytes:
    """Keccak-256 (pad 0x01), not NIST SHA3-256."""
    rate = 136
    state = [0] * 25
    padlen = rate - (len(data) % rate)
    if padlen == 1:
        padded = data + b"\x81"
    else:
        padded = data + b"\x01" + (b"\x00" * (padlen - 2)) + b"\x80"
    for offset in range(0, len(padded), rate):
        block = padded[offset : offset + rate]
        for i in range(rate // 8):
            state[i] ^= int.from_bytes(block[i * 8 : (i + 1) * 8], "little")
        _keccak_f(state)
    out = bytearray()
    for i in range(4):
        out += state[i].to_bytes(8, "little")
    return bytes(out)


def _rotl(x: int, n: int) -> int:
    n %= 64
    return ((x << n) | (x >> (64 - n))) & 0xFFFFFFFFFFFFFFFF


def _keccak_f(st: list[int]) -> None:
    for rc in _KECCAK_RC:
        c = [st[x] ^ st[x + 5] ^ st[x + 10] ^ st[x + 15] ^ st[x + 20] for x in range(5)]
        d = [c[(x - 1) % 5] ^ _rotl(c[(x + 1) % 5], 1) for x in range(5)]
        for x in range(5):
            for y in range(5):
                st[x + 5 * y] ^= d[x]
        b = [0] * 25
        for x in range(5):
            for y in range(5):
                b[y + 5 * ((2 * x + 3 * y) % 5)] = _rotl(st[x + 5 * y], _KECCAK_ROT[x][y])
        for x in range(5):
            for y in range(5):
                st[x + 5 * y] = b[x + 5 * y] ^ ((~b[((x + 1) % 5) + 5 * y]) & b[((x + 2) % 5) + 5 * y])
        st[0] ^= rc


def _point_add(p: tuple[int, int] | None, q: tuple[int, int] | None) -> tuple[int, int] | None:
    if p is None:
        return q
    if q is None:
        return p
    x1, y1 = p
    x2, y2 = q
    if x1 == x2 and (y1 + y2) % _P == 0:
        return None
    if p == q:
        m = (3 * x1 * x1 * pow(2 * y1, -1, _P)) % _P
    else:
        m = ((y2 - y1) * pow((x2 - x1) % _P, -1, _P)) % _P
    x3 = (m * m - x1 - x2) % _P
    y3 = (m * (x1 - x3) - y1) % _P
    return x3, y3


def _point_mul(k: int, point: tuple[int, int] | None) -> tuple[int, int] | None:
    result = None
    addend = point
    while k:
        if k & 1:
            result = _point_add(result, addend)
        addend = _point_add(addend, addend)
        k >>= 1
    return result


def public_key(private_key: int) -> tuple[int, int]:
    point = _point_mul(private_key, (_GX, _GY))
    if point is None:
        raise ValueError("invalid private key")
    return point


def _recover(digest: bytes, r: int, s: int, y_parity: int) -> tuple[int, int] | None:
    if not (1 <= r < _N and 1 <= s < _N):
        return None
    x = r
    y2 = (pow(x, 3, _P) + 7) % _P
    y = pow(y2, (_P + 1) // 4, _P)
    if pow(y, 2, _P) != y2:
        return None
    if (y & 1) != (y_parity & 1):
        y = (_P - y) % _P
    z = int.from_bytes(digest, "big")
    s_r = _point_mul(s, (x, y))
    z_g = _point_mul(z, (_GX, _GY))
    if s_r is None or z_g is None:
        return None
    diff = _point_add(s_r, (z_g[0], (-z_g[1]) % _P))
    return _point_mul(pow(r, -1, _N), diff)


def rlp_bytes(data: bytes) -> bytes:
    if len(data) == 1 and data[0] < 0x80:
        return data
    return _rlp_len(0x80, data) + data


def rlp_int(n: int) -> bytes:
    if n < 0:
        raise ValueError("rlp int")
    if n == 0:
        return b"\x80"
    raw = n.to_bytes((n.bit_length() + 7) // 8, "big")
    return rlp_bytes(raw)


def rlp_list(items: list[bytes]) -> bytes:
    payload = b"".join(items)
    return _rlp_len(0xC0, payload) + payload


def _rlp_len(offset: int, payload: bytes) -> bytes:
    n = len(payload)
    if n <= 55:
        return bytes([offset + n])
    len_bytes = n.to_bytes((n.bit_length() + 7) // 8, "big")
    return bytes([offset + 55 + len(len_bytes)]) + len_bytes


def _sign_digest(digest: bytes, private_key: int) -> tuple[int, int, int]:
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.asymmetric.utils import Prehashed, decode_dss_signature
    from cryptography.hazmat.primitives import hashes

    key = ec.derive_private_key(private_key, ec.SECP256K1())
    der = key.sign(digest, ec.ECDSA(Prehashed(hashes.SHA256())))
    r, s = decode_dss_signature(der)
    pub = public_key(private_key)
    y_parity = None
    if s > _N // 2:
        s = _N - s
    for parity in (0, 1):
        rec = _recover(digest, r, s, parity)
        if rec == pub:
            y_parity = parity
            break
    if y_parity is None:
        raise RuntimeError("could not recover signing key")
    return y_parity, r, s


def sign_eip1559(
    *,
    private_key: int,
    chain_id: int,
    nonce: int,
    max_priority_fee: int,
    max_fee: int,
    gas_limit: int,
    to: bytes | None,
    data: bytes,
    value: int = 0,
) -> bytes:
    """Return the raw typed transaction (0x02 || rlp)."""
    to_bytes = to or b""
    if to_bytes and len(to_bytes) != 20:
        raise ValueError("to must be 20 bytes")
    unsigned = [
        rlp_int(chain_id),
        rlp_int(nonce),
        rlp_int(max_priority_fee),
        rlp_int(max_fee),
        rlp_int(gas_limit),
        rlp_bytes(to_bytes),
        rlp_int(value),
        rlp_bytes(data),
        rlp_list([]),
    ]
    payload = rlp_list(unsigned)
    digest = keccak256(b"\x02" + payload)
    y_parity, r, s = _sign_digest(digest, private_key)
    signed = rlp_list(unsigned + [rlp_int(y_parity), rlp_int(r), rlp_int(s)])
    return b"\x02" + signed


def tx_hash(raw: bytes) -> str:
    return "0x" + keccak256(raw).hex()


class _Asm:
    def __init__(self) -> None:
        self.ops: list[tuple] = []

    def op(self, name: str, arg: Any = None) -> None:
        self.ops.append((name, arg))

    def label(self, name: str) -> None:
        self.ops.append(("LABEL", name))

    def bytecode(self) -> bytes:
        sizes = {"PUSH1": 2, "PUSH2": 3, "PUSH4": 5, "PUSH32": 33}
        singles = {
            "CALLDATALOAD": 0x35,
            "CALLDATASIZE": 0x36,
            "CALLDATACOPY": 0x37,
            "CODECOPY": 0x39,
            "SHR": 0x1C,
            "EQ": 0x14,
            "LT": 0x10,
            "JUMPI": 0x57,
            "JUMP": 0x56,
            "JUMPDEST": 0x5B,
            "DUP1": 0x80,
            "REVERT": 0xFD,
            "LOG1": 0xA1,
            "STOP": 0x00,
            "RETURN": 0xF3,
        }
        pos = 0
        labels: dict[str, int] = {}
        for name, arg in self.ops:
            if name == "LABEL":
                labels[arg] = pos
                continue
            pos += sizes.get(name, 1)
        out = bytearray()
        for name, arg in self.ops:
            if name == "LABEL":
                continue
            if name == "PUSH1":
                out += bytes([0x60, arg & 0xFF])
            elif name == "PUSH2":
                value = labels[arg] if isinstance(arg, str) else arg
                out += bytes([0x61]) + int(value).to_bytes(2, "big")
            elif name == "PUSH4":
                raw = arg if isinstance(arg, bytes) else int(arg).to_bytes(4, "big")
                out += bytes([0x63]) + raw
            elif name == "PUSH32":
                raw = arg if isinstance(arg, bytes) else int(arg).to_bytes(32, "big")
                out += bytes([0x7F]) + raw
            else:
                out.append(singles[name])
        return bytes(out)


def event_topic() -> bytes:
    return keccak256(EVENT_SIG.encode())


def commit_selector() -> bytes:
    return keccak256(COMMIT_SIG.encode())[:4]


def build_runtime() -> bytes:
    """Dispatcher plus LOG1 of the three calldata words. No SSTORE."""
    a = _Asm()
    a.op("PUSH4", commit_selector())
    a.op("PUSH1", 0)
    a.op("CALLDATALOAD")
    a.op("PUSH1", 0xE0)
    a.op("SHR")
    a.op("EQ")
    a.op("PUSH2", "body")
    a.op("JUMPI")
    a.op("PUSH2", "bad")
    a.op("JUMP")
    a.label("body")
    a.op("JUMPDEST")
    a.op("CALLDATASIZE")
    a.op("PUSH1", 100)
    a.op("LT")
    a.op("PUSH2", "bad")
    a.op("JUMPI")
    a.op("PUSH1", 96)
    a.op("PUSH1", 4)
    a.op("PUSH1", 0)
    a.op("CALLDATACOPY")
    a.op("PUSH32", event_topic())
    a.op("PUSH1", 96)
    a.op("PUSH1", 0)
    a.op("LOG1")
    a.op("STOP")
    a.label("bad")
    a.op("JUMPDEST")
    a.op("PUSH1", 0)
    a.op("PUSH1", 0)
    a.op("REVERT")
    return a.bytecode()


def build_deploy(runtime: bytes | None = None) -> bytes:
    runtime = build_runtime() if runtime is None else runtime
    if not runtime or len(runtime) > 255:
        raise ValueError("runtime must fit a PUSH1 length")
    # 12-byte init: CODECOPY runtime from offset 12, RETURN it.
    init = bytes(
        [
            0x60,
            len(runtime),
            0x60,
            0x0C,
            0x60,
            0x00,
            0x39,
            0x60,
            len(runtime),
            0x60,
            0x00,
            0xF3,
        ]
    )
    return init + runtime


RUNTIME_CODE = build_runtime()
DEPLOY_CODE = build_deploy(RUNTIME_CODE)


def encode_commit(tree_size: int, root_hash: bytes, prev_root_hash: bytes) -> bytes:
    if len(root_hash) != 32 or len(prev_root_hash) != 32:
        raise ValueError("roots must be 32 bytes")
    if tree_size < 0 or tree_size >= 2**256:
        raise ValueError("tree_size")
    return commit_selector() + tree_size.to_bytes(32, "big") + root_hash + prev_root_hash


def _mem_cost(size: int) -> int:
    if size <= 0:
        return 0
    words = (size + 31) // 32
    return words * 3 + (words * words) // 512


def execution_gas(calldata: bytes) -> int:
    """Yellow-paper gas for the commit runtime, including a successful LOG1."""
    return _execute(RUNTIME_CODE, calldata, gas_only=True)


def commit_gas(tree_size: int, root_hash: bytes, prev_root_hash: bytes) -> int:
    data = encode_commit(tree_size, root_hash, prev_root_hash)
    calldata_cost = sum(4 if b == 0 else 16 for b in data)
    return 21_000 + calldata_cost + execution_gas(data)


def _execute(code: bytes, calldata: bytes, *, gas_only: bool = False) -> int:
    stack: list[int] = []
    memory = bytearray()
    pc = 0
    gas = 0
    last_mem = 0

    def push(n: int) -> None:
        stack.append(n)

    def pop() -> int:
        if not stack:
            raise RuntimeError("stack underflow")
        return stack.pop()

    def grow(size: int) -> None:
        nonlocal gas, last_mem
        if size > len(memory):
            memory.extend(b"\x00" * (size - len(memory)))
        new = _mem_cost(size)
        gas += new - last_mem
        last_mem = new

    while pc < len(code):
        op = code[pc]
        pc += 1
        if op == 0x00:  # STOP
            gas += 0
            break
        if op == 0x5B:  # JUMPDEST
            gas += 1
            continue
        if 0x60 <= op <= 0x7F:
            n = op - 0x5F
            gas += 3
            push(int.from_bytes(code[pc : pc + n], "big"))
            pc += n
            continue
        if op == 0x80:  # DUP1
            gas += 3
            push(stack[-1])
            continue
        if op == 0x35:  # CALLDATALOAD
            gas += 3
            off = pop()
            word = calldata[off : off + 32]
            word = word + b"\x00" * (32 - len(word))
            push(int.from_bytes(word, "big"))
            continue
        if op == 0x36:  # CALLDATASIZE
            gas += 2
            push(len(calldata))
            continue
        if op == 0x1C:  # SHR
            gas += 3
            shift = pop()
            value = pop()
            push(0 if shift >= 256 else value >> shift)
            continue
        if op == 0x14:  # EQ
            gas += 3
            a = pop()
            b = pop()
            push(1 if a == b else 0)
            continue
        if op == 0x10:  # LT
            gas += 3
            a = pop()
            b = pop()
            push(1 if b < a else 0)
            continue
        if op == 0x57:  # JUMPI
            gas += 10
            dest = pop()
            cond = pop()
            if cond:
                pc = dest
            continue
        if op == 0x56:  # JUMP
            gas += 8
            pc = pop()
            continue
        if op == 0x37:  # CALLDATACOPY
            dest = pop()
            offset = pop()
            length = pop()
            words = (length + 31) // 32
            gas += 3 + 3 * words
            grow(dest + length)
            chunk = calldata[offset : offset + length]
            chunk = chunk + b"\x00" * (length - len(chunk))
            memory[dest : dest + length] = chunk
            continue
        if op == 0xA1:  # LOG1
            offset = pop()
            length = pop()
            pop()  # topic
            gas += 375 + 375 + 8 * length
            grow(offset + length)
            if not gas_only:
                logged = bytes(memory[offset : offset + length])
                if logged != calldata[4:100]:
                    raise RuntimeError("log data is not the three commit words")
            break
        if op == 0xFD:  # REVERT
            pop()
            pop()
            raise RuntimeError("commit reverted")
        raise RuntimeError(f"unexpected opcode {op:#x}")
    else:
        raise RuntimeError("execution fell off the end")
    return gas


def _rpc(url: str, method: str, params: list) -> Any:
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "User-Agent": "gate-seal-anchor/1"},
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            payload = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        raise RuntimeError(f"{method} HTTP {exc.code}: {detail}") from None
    except urllib.error.URLError as exc:
        raise RuntimeError(f"{method} unreachable: {exc.reason}") from None
    if payload.get("error"):
        raise RuntimeError(f"{method}: {payload['error']}")
    return payload.get("result")


def estimate_commit_remote(rpc_url: str | None = None) -> dict[str, Any]:
    """eth_estimateGas against overridden bytecode. Does not sign or spend.

    The state override installs the log contract and a funded sender for the
    duration of the call. Nothing is broadcast.
    """
    url = rpc_url or BASE_SEPOLIA_RPC
    root = b"\x11" * 32
    prev = b"\x22" * 32
    data = encode_commit(3, root, prev)
    sender = "0x" + "22" * 20
    contract = "0x" + "11" * 20
    override = {
        sender: {"balance": "0x3635c9adc5dea00000"},
        contract: {"code": "0x" + RUNTIME_CODE.hex()},
    }
    tx = {"from": sender, "to": contract, "data": "0x" + data.hex()}
    result = _rpc(url, "eth_estimateGas", [tx, "latest", override])
    remote = int(result, 16)
    static = commit_gas(3, root, prev)
    return {
        "rpc": url,
        "remote_gas": remote,
        "static_gas": static,
        "memo_gas": MEMO_COMMIT_GAS,
        "ceiling": COMMIT_GAS_CEILING,
        "within_memo": remote <= COMMIT_GAS_CEILING and abs(remote - MEMO_COMMIT_GAS) <= 8_000,
    }


class BaseAnchor:
    """JSON-RPC publisher. Constructed only when a spend mode is explicitly on."""

    def __init__(self, *, chain_id: int, rpc_url: str, private_key: int, contract: str | None):
        self.chain_id = chain_id
        self.rpc_url = rpc_url
        self.private_key = private_key
        self.contract = (contract or "").strip() or None
        self._sender = "0x" + keccak256(_xy(public_key(private_key)))[-20:].hex()

    def base_fee_wei(self) -> int:
        block = _rpc(self.rpc_url, "eth_getBlockByNumber", ["latest", False])
        return int(block["baseFeePerGas"], 16)

    def estimate_commit(self, data: bytes) -> int:
        self.ensure_contract()
        tx = {
            "from": self._sender,
            "to": self.contract,
            "data": "0x" + data.hex(),
        }
        return int(_rpc(self.rpc_url, "eth_estimateGas", [tx, "latest"]), 16)

    def broadcast_commit(self, data: bytes, gas_limit: int, max_fee: int, priority: int) -> str:
        self.ensure_contract()
        raw = self._sign(to=_hex_addr(self.contract), data=data, gas_limit=gas_limit, max_fee=max_fee, priority=priority)
        sent = _rpc(self.rpc_url, "eth_sendRawTransaction", ["0x" + raw.hex()])
        return sent

    def receipt_status(self, tx_hash_hex: str) -> int | None:
        receipt = self.receipt(tx_hash_hex)
        if not receipt:
            return None
        return int(receipt["status"], 16)

    def receipt_contract(self, tx_hash_hex: str) -> str | None:
        receipt = self.receipt(tx_hash_hex)
        if not receipt:
            return None
        return receipt.get("contractAddress")

    def receipt(self, tx_hash_hex: str) -> dict | None:
        return _rpc(self.rpc_url, "eth_getTransactionReceipt", [tx_hash_hex])

    def ensure_contract(self) -> str:
        if self.contract:
            return self.contract
        raise RuntimeError("contract missing — call deploy() before commit")

    def deploy(self, gas_limit: int, max_fee: int, priority: int) -> str:
        raw = self._sign(to=None, data=DEPLOY_CODE, gas_limit=gas_limit, max_fee=max_fee, priority=priority)
        return _rpc(self.rpc_url, "eth_sendRawTransaction", ["0x" + raw.hex()])

    def estimate_deploy(self) -> int:
        tx = {"from": self._sender, "data": "0x" + DEPLOY_CODE.hex()}
        return int(_rpc(self.rpc_url, "eth_estimateGas", [tx, "latest"]), 16)

    def nonce(self) -> int:
        n = _rpc(self.rpc_url, "eth_getTransactionCount", [self._sender, "pending"])
        return int(n, 16)

    def _sign(self, *, to: bytes | None, data: bytes, gas_limit: int, max_fee: int, priority: int) -> bytes:
        return sign_eip1559(
            private_key=self.private_key,
            chain_id=self.chain_id,
            nonce=self.nonce(),
            max_priority_fee=priority,
            max_fee=max_fee,
            gas_limit=gas_limit,
            to=to,
            data=data,
        )


def _xy(point: tuple[int, int]) -> bytes:
    return point[0].to_bytes(32, "big") + point[1].to_bytes(32, "big")


def _hex_addr(text: str) -> bytes:
    raw = text[2:] if text.startswith("0x") else text
    out = bytes.fromhex(raw)
    if len(out) != 20:
        raise ValueError("contract address")
    return out


def parse_private_key(text: str) -> int:
    raw = (text or "").strip()
    if raw.startswith("0x"):
        raw = raw[2:]
    if len(raw) != 64:
        raise ValueError("private key must be 32 bytes hex")
    value = int(raw, 16)
    if not (1 <= value < _N):
        raise ValueError("private key out of range")
    return value
