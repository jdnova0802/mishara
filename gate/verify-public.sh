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

check demo_mga POST 200 \
  -X POST "$URL/demo/pas/mga-authority" \
  -H "Content-Type: application/json" \
  -d '{"fuse_id":"fuse_velaru_drill","premium":60000,"authority_limit":50000}'

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
