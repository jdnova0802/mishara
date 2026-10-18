import {
  createPrivateKey,
  createPublicKey,
  generateKeyPairSync,
  sign,
  verify,
  createHash,
} from "node:crypto";
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const KEY_DIR = join(__dirname, ".keys");
const PRIV_PATH = join(KEY_DIR, "receipt_ed25519.pem");
const PUB_PATH = join(KEY_DIR, "receipt_ed25519.pub.pem");

export function ensureKeys() {
  if (!existsSync(KEY_DIR)) mkdirSync(KEY_DIR, { recursive: true });
  if (!existsSync(PRIV_PATH) || !existsSync(PUB_PATH)) {
    const { privateKey, publicKey } = generateKeyPairSync("ed25519");
    writeFileSync(PRIV_PATH, privateKey.export({ type: "pkcs8", format: "pem" }));
    writeFileSync(PUB_PATH, publicKey.export({ type: "spki", format: "pem" }));
  }
  return {
    privateKey: createPrivateKey(readFileSync(PRIV_PATH)),
    publicKeyPem: readFileSync(PUB_PATH, "utf8"),
  };
}

export function mintReceipt(decision, privateKey) {
  const body = {
    spec: "money-rail-receipt-v1",
    decision_id: `dec_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`,
    ts: new Date().toISOString(),
    ...decision,
  };
  const payload = Buffer.from(JSON.stringify(body), "utf8");
  return {
    ...body,
    payload_b64: payload.toString("base64url"),
    signature: sign(null, payload, privateKey).toString("base64url"),
    payload_sha256: createHash("sha256").update(payload).digest("hex"),
  };
}

export function verifyReceipt(receipt, publicKeyPem) {
  const publicKey = createPublicKey(publicKeyPem);
  const payload = Buffer.from(receipt.payload_b64, "base64url");
  return verify(null, payload, publicKey, Buffer.from(receipt.signature, "base64url"));
}
