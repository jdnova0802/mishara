#!/usr/bin/env bash
# Prove Gate is public. Refuses localhost. Run after Render deploy:
#   ./verify-public.sh https://YOUR_GATE.onrender.com
set -euo pipefail
URL="${1:-}"
URL="${URL%/}"

if [[ -z "$URL" ]]; then
  echo "usage: $0 https://YOUR_GATE.onrender.com"
  exit 2
fi
if [[ "$URL" != https://* ]]; then
  echo "FAIL: URL must be https (got $URL)"
  exit 1
fi
if echo "$URL" | grep -Eiq 'localhost|127\.0\.0\.1|0\.0\.0\.0'; then
  echo "FAIL: localhost is not a listing. Deploy first, then pass the live URL."
  exit 1
fi

fail=0
check() {
  local name="$1" code="$2" expect="$3"
  shift 3
  local body
  body="$(mktemp)"
  local got
  got="$(curl -sS -o "$body" -w "%{http_code}" "$@" || echo err)"
  if [[ "$got" != "$expect" ]]; then
    echo "FAIL $name — HTTP $got (want $expect)"
    head -c 400 "$body"; echo
    fail=1
  else
    echo "OK   $name — HTTP $got"
  fi
  rm -f "$body"
}

check health GET 200 "$URL/health"
if curl -sS "$URL/health" | grep -Eq '"local"[[:space:]]*:[[:space:]]*true'; then
  echo "FAIL health advertises local=true"
  fail=1
else
  echo "OK   health local=false"
fi

check listings GET 200 "$URL/.well-known/listings.json"
check mcp_disc GET 200 "$URL/.well-known/mcp.json"
check x402 GET 200 "$URL/.well-known/x402.json"
check gate_wk GET 200 "$URL/.well-known/gate.json"
check llms GET 200 "$URL/llms.txt"
check openapi GET 200 "$URL/openapi.json"
check kong GET 200 "$URL/listings/kong-mcp.yaml"
check gw GET 200 "$URL/listings/guidewire-partnerconnect.json"
check dc GET 200 "$URL/listings/duckcreek-partner.json"
check control GET 200 "$URL/listings/control-not-model.json"
check bind_js GET 200 "$URL/listings/cloudflare-worker-bind.js"
check bind_room GET 200 "$URL/bind-room"
check officer GET 200 "$URL/bind-room/officer-pack.json"
check bound GET 200 "$URL/bound"
check bound_wk GET 200 "$URL/.well-known/bound-answer.json"
check only GET 200 "$URL/only"
check exclusive_wk GET 200 "$URL/.well-known/exclusive-timing.json"
check floor GET 200 "$URL/floor"
check floor_wk GET 200 "$URL/.well-known/floor.json"
check this GET 200 "$URL/this"
check particular_wk GET 200 "$URL/.well-known/particular.json"
check capture GET 200 "$URL/capture"
check capture_wk GET 200 "$URL/.well-known/capture.json"
check scanner GET 200 "$URL/scanner"
check spend_wk GET 200 "$URL/.well-known/spend-protocol.json"
check uplink GET 200 "$URL/uplink"
check radiation_wk GET 200 "$URL/.well-known/command-radiation.json"
check mass GET 200 "$URL/mass"
check mass_wk GET 200 "$URL/.well-known/mass.json"
check relics GET 200 "$URL/.well-known/relics.json"
check refusal GET 200 "$URL/refusal"
check tattoo GET 200 "$URL/tattoo"
check tattoo_wk GET 200 "$URL/.well-known/tattoo.json"
check gosu GET 200 "$URL/listings/guidewire-gosu-prebind.gs"
check renewal GET 200 "$URL/listings/guidewire-renewal-prebind.gs"

check demo_hop POST 200 \
  -X POST "$URL/demo/hop" \
  -H "Content-Type: application/json" \
  -d '{"fuse_id":"fuse_velaru_drill"}'

check demo_act POST 200 \
  -X POST "$URL/demo/act" \
  -H "Content-Type: application/json" \
  -d '{"fuse_id":"fuse_velaru_drill","action":"public-check"}'

check demo_pas POST 200 \
  -X POST "$URL/demo/pas/bind-check" \
  -H "Content-Type: application/json" \
  -d '{}'

check demo_pc POST 200 \
  -X POST "$URL/demo/pas/policycenter/pre-bind" \
  -H "Content-Type: application/json" \
  -d '{"fuse_id":"fuse_velaru_drill","job_id":"pc:DEMO"}'

check receipt_key GET 200 "$URL/.well-known/receipt-key.json"
if ! curl -sS "$URL/.well-known/receipt-key.json" | grep -Eq '"spec"[[:space:]]*:[[:space:]]*"gate-receipt-key-v1"'; then
  echo "FAIL receipt-key staple missing gate-receipt-key-v1"
  fail=1
else
  echo "OK   receipt-key staple spec"
fi
if curl -sS "$URL/.well-known/receipt-key.json" | grep -Eq '"key_present"[[:space:]]*:[[:space:]]*false'; then
  echo "FAIL receipt-key key_present=false — set GATE_RECEIPT_PRIVATE_KEY / PUBLIC_KEY"
  fail=1
else
  echo "OK   receipt-key key_present"
fi

# Mint a demo event, then stranger-audit must all_pass when keys are live.
pc_body="$(mktemp)"
pc_code="$(curl -sS -o "$pc_body" -w "%{http_code}" \
  -X POST "$URL/demo/pas/policycenter/pre-bind" \
  -H "Content-Type: application/json" \
  -d '{"fuse_id":"fuse_velaru_drill","job_id":"pc:VERIFY-PUBLIC-RECEIPT"}' || echo err)"
if [[ "$pc_code" != "200" ]]; then
  echo "FAIL demo_pc_receipt — HTTP $pc_code"
  head -c 400 "$pc_body"; echo
  fail=1
  latest_id=""
else
  echo "OK   demo_pc_receipt — HTTP $pc_code"
  latest_id="$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d.get("event_id") or "")' "$pc_body" 2>/dev/null || true)"
fi
rm -f "$pc_body"
if [[ -z "$latest_id" ]]; then
  latest_id="$(curl -sS "$URL/.well-known/live.json" \
    | python3 -c 'import sys,json; d=json.load(sys.stdin); p=d.get("pulse") or {}; print(p.get("id") or "")' 2>/dev/null || true)"
fi
if [[ -n "$latest_id" ]]; then
  check receipt_verify GET 200 "$URL/.well-known/receipt/${latest_id}/verify.json"
  check receipt_page GET 200 "$URL/receipt/${latest_id}"
  if ! curl -sS "$URL/.well-known/receipt/${latest_id}/verify.json" | grep -Eq '"all_pass"[[:space:]]*:[[:space:]]*true'; then
    echo "FAIL stranger receipt audit all_pass!=true for $latest_id"
    curl -sS "$URL/.well-known/receipt/${latest_id}/verify.json" | head -c 600; echo
    fail=1
  else
    echo "OK   stranger receipt audit all_pass"
  fi
else
  echo "FAIL could not resolve bind event id for stranger receipt audit"
  fail=1
fi

check demo_mga POST 200 \
  -X POST "$URL/demo/pas/mga-authority" \
  -H "Content-Type: application/json" \
  -d '{"fuse_id":"fuse_velaru_drill","premium":60000,"authority_limit":50000}'

check prefinality_wk GET 200 "$URL/.well-known/prefinality.json"
check prefinality_jwks GET 200 "$URL/.well-known/prefinality-jwks.json"
check x402_fanout GET 200 "$URL/.well-known/x402"
check prefinality_sdk GET 200 "$URL/sdk/prefinality/wrap.mjs"

check demo_prefinality POST 200 \
  -X POST "$URL/demo/prefinality/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"rail":"x402","transfer":{"amount":"0.002","currency":"USDC","counterparty":"0x0000000000000000000000000000000000000001"},"mandate":{"agent_id":"verify-public","max_amount":"1.00"}}'

check no_pii POST 400 \
  -X POST "$URL/demo/pas/policycenter/pre-bind" \
  -H "Content-Type: application/json" \
  -d '{"fuse_id":"fuse_velaru_drill","ssn":"000-00-0000"}'

init="$(mktemp)"
got="$(curl -sS -o "$init" -w "%{http_code}" \
  -X POST "$URL/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"verify-public","version":"1"}}}')"
if [[ "$got" != "200" ]] || ! grep -q '"protocolVersion"' "$init"; then
  echo "FAIL mcp initialize — HTTP $got"
  head -c 400 "$init"; echo
  fail=1
else
  echo "OK   mcp initialize — HTTP $got"
fi
rm -f "$init"

if [[ "$fail" -ne 0 ]]; then
  echo ""
  echo "Public check failed. Fix env (GATE_PUBLIC_URL, disk, Velaru) and rerun."
  exit 1
fi
echo ""
echo "Public. Paste $URL/for/carriers or $URL/bind-room to one human."
echo "Paperwork: $URL/listings/guidewire-partnerconnect.json"
echo "           $URL/listings/duckcreek-partner.json"
echo "Contract:  $URL/listings/control-not-model.json"
