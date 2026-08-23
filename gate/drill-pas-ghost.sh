#!/usr/bin/env bash
# PAS Ghost Bind + Throat public drill — stranger verify, no API key, no PII.
# Usage:
#   ./gate/drill-pas-ghost.sh
#   ./gate/drill-pas-ghost.sh https://gate.velaru.xyz
set -euo pipefail

GATE="${1:-https://gate.velaru.xyz}"
GATE="${GATE%/}"

if [[ "$GATE" != https://* ]]; then
  echo "FAIL: GATE must be https (got $GATE)"
  exit 2
fi
if echo "$GATE" | grep -Eiq 'localhost|127\.0\.0\.1'; then
  echo "FAIL: use the live Gate URL, not localhost"
  exit 2
fi

pass=0
fail=0
say() { echo ""; echo "== $*"; }
ok() { echo "OK   $*"; pass=$((pass + 1)); }
bad() { echo "FAIL $*"; fail=$((fail + 1)); }

check_get() {
  local name="$1" path="$2"
  local body code
  body="$(mktemp)"
  code="$(curl -sS -o "$body" -w "%{http_code}" "$GATE$path" || echo err)"
  if [[ "$code" == "200" ]]; then
    ok "$name HTTP $code"
  else
    bad "$name HTTP $code"
    head -c 300 "$body"; echo
  fi
  rm -f "$body"
}

json_field_eq() {
  local body="$1" field="$2" want="$3"
  python3 - "$body" "$field" "$want" <<'PY'
import json, sys
path, field, want = sys.argv[1], sys.argv[2], sys.argv[3]
d = json.load(open(path, encoding="utf-8"))
got = d.get(field)
if str(got) == want:
    sys.exit(0)
print(f"field {field}={got!r} want {want!r}", file=sys.stderr)
sys.exit(1)
PY
}

check_post_json() {
  local name="$1" path="$2" data="$3" want_field="$4" want_val="$5"
  local body raw
  body="$(mktemp)"
  raw="$(curl -sS -o "$body" -w "%{http_code}" \
    -X POST "$GATE$path" \
    -H "Content-Type: application/json" \
    -d "$data" || echo err)"
  if [[ "$raw" != "200" ]]; then
    bad "$name HTTP $raw"
    head -c 300 "$body"; echo
    rm -f "$body"
    return
  fi
  if json_field_eq "$body" "$want_field" "$want_val"; then
    ok "$name → $want_field=$want_val"
  else
    bad "$name → expected $want_field=$want_val"
    head -c 400 "$body"; echo
  fi
  rm -f "$body"
}

check_get_json() {
  local name="$1" path="$2" want_field="$3" want_val="$4"
  local body raw
  body="$(mktemp)"
  raw="$(curl -sS -o "$body" -w "%{http_code}" "$GATE$path" || echo err)"
  if [[ "$raw" != "200" ]]; then
    bad "$name HTTP $raw"
    head -c 300 "$body"; echo
    rm -f "$body"
    return
  fi
  if json_field_eq "$body" "$want_field" "$want_val"; then
    ok "$name → $want_field=$want_val"
  else
    bad "$name → expected $want_field=$want_val"
    head -c 400 "$body"; echo
  fi
  rm -f "$body"
}

say "Manifests (posture + spec)"
check_get "throat.json" "/.well-known/throat.json"
check_get "ghost-bind.json" "/.well-known/ghost-bind.json"
check_get "officer-pack" "/bind-room/officer-pack.json"

say "Act I — Soft PAS would stick (Throat CHOKE + Ghost HAUNT)"
check_post_json \
  "soft-yes / soft_pas" \
  "/demo/pas/soft-yes-snare" \
  '{"scenario":{"soft_pas":true,"decision":"ALLOW","allow_bind":true,"would_bind":true}}' \
  "throat_state" "CHOKE"
check_post_json \
  "soft-yes / soft_pas ghost" \
  "/demo/pas/soft-yes-snare" \
  '{"scenario":{"soft_pas":true,"decision":"ALLOW","allow_bind":true,"would_bind":true}}' \
  "ghost_verdict" "HAUNTED_CRITICAL"

say "Act II — Timeout treated as LIVE (classic silent fail-open)"
check_post_json \
  "soft-yes / timeout" \
  "/demo/pas/soft-yes-snare" \
  '{"scenario":{"timeout":true,"decision":"ALLOW","allow_bind":true,"would_bind":true}}' \
  "throat_state" "CHOKE"

say "Act III — Boss said yes without quorum (charisma path)"
check_post_json \
  "soft-yes / boss" \
  "/demo/pas/soft-yes-snare" \
  '{"scenario":{"boss_said_yes":true,"decision":"ALLOW","allow_bind":true,"would_bind":true}}' \
  "throat_state" "CHOKE"

say "Act IV — UW approve on DEAD fuse (Charge Bride FORGED)"
check_post_json \
  "charge-bride / uw not charge" \
  "/demo/pas/charge-bride" \
  '{"fuse_state":"DEAD","uw_approved":true,"would_proceed":true}' \
  "verdict" "FORGED"

say "Act V — Full red-team pack (6/6 must pass)"
check_get_json \
  "soft-yes-snare drills" \
  "/demo/pas/soft-yes-snare/drills" \
  "all_ok" "True"

say "Summary"
echo "Gate: $GATE"
echo "Bind Room: $GATE/bind-room"
echo "Paste DM link: $GATE/bind-room"
echo "Officer pack: $GATE/bind-room/officer-pack.json"
if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "ALL OK ($pass checks). PAS would have stuck — Throat CHOKED. Stranger can verify."
  exit 0
fi
echo ""
echo "$fail check(s) failed. Fix deploy/branch before outbound."
exit 1
