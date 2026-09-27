# PASTE — Claude reply: ARD path critical check + Neuronto verify

**27 Sep 2026.** Citation-backed. Dual-path fix shipped in companion PR.

---

## Message (copy below the line)

---

CRITICAL CHECK — answered against primary sources (fetched live, not memory)

### 1) Manifest path: `ard.json` vs `ai-catalog.json`

**Both names are real. Current normative path is `ard.json`. Predecessor / Google announcement still says `ai-catalog.json`.**

| Source (fetched) | Path it names | Role |
|---|---|---|
| [ards-project ard.md v0.91](https://github.com/ards-project/ard-spec/blob/main/spec/ard.md) (Status: Proposal, Date: **August 26, 2026**) | `/.well-known/ard.json` **MUST** for consumers; `ai-catalog.json` **MAY** (predecessor) | Current ARD proposal |
| [agenticresourcediscovery.org/spec/](https://agenticresourcediscovery.org/spec/) | Same: normative `ard.json`; predecessor `ai-catalog.json` optional | Spec site |
| [Google Developers Blog announcement](https://developers.googleblog.com/announcing-the-agentic-resource-discovery-specification/) | `ai-catalog.json` only (0 hits for `ard.json` on page) | Launch announcement naming |
| [specification.website ARD page](https://specification.website/spec/agent-readiness/agentic-resource-discovery/) | Still documents `ai-catalog.json` | Third-party writeup lagging v0.91 |

**ards-project §5.1 (normative consumer resolution), fetched from raw GitHub:**
> A consumer resolving a domain's entries MUST fetch `/.well-known/ard.json`… ARD's predecessor specified `/.well-known/ai-catalog.json`… a consumer MAY additionally consult these… A resource that remains only at `ai-catalog.json` may not be found.

**Pre-fix live check on Gate:**
- `https://gate.velaru.xyz/.well-known/ard.json` → **200** (`ard-v0.91`, 3 entries)
- `https://gate.velaru.xyz/.well-known/ai-catalog.json` → **404** ← Claude’s risk was real for Google-announcement crawlers

**Fix (this PR):** serve the **same body** at both paths. No rename (that would drop v0.91). Alias, not replace.

### 2) Neuronto — real service + checkable listing

**Real.** Independent checks (not memory):

| Check | Result |
|---|---|
| `https://neuronto.com/` | HTTP **200** |
| GitHub org | https://github.com/neuronto/agentic-resource-discovery |
| Submit status | https://neuronto.com/submit/status/bd114e1f13e2 → `{"status":"indexed","target":"gate.velaru.xyz","verified_tools":3}` |
| **Publisher page (checkable)** | https://neuronto.com/ard-publishers/gate.velaru.xyz → HTTP **200**, title includes `gate.velaru.xyz`, lists 3 resources from live `ard.json`, first seen **27 Sep 2026** |

Neuronto’s own docs state they request **both** well-known paths (`ard.json` and `ai-catalog.json`). Indexing on Neuronto via `ard.json` was valid. Dual-path still matters for Google-announcement / specification.website crawlers that only look for `ai-catalog.json`.

**“#1 on Neuronto”** = Neuronto analytics preview for Gate’s own `representativeQueries` on Neuronto’s index — not a global web ranking. Open web was **0 of 5** on that same check. Do not overclaim.

### Honesty correction to prior “done”

Prior claim “ARD discovery path complete” was **true for v0.91 + Neuronto**, **incomplete for Google-announcement path** (404 on `ai-catalog.json`). That gap is what this PR closes. Do not re-mark fully done until `ai-catalog.json` returns 200 with the same body on prod.

### Deploy after merge

1. Merge this PR → Render auto-deploy
2. Verify:
```bash
curl -sS https://gate.velaru.xyz/.well-known/ai-catalog.json | python3 -c "import sys,json; m=json.load(sys.stdin); print(m['spec'], len(m['entries']))"
curl -sS https://gate.velaru.xyz/.well-known/ard.json | python3 -c "import sys,json; m=json.load(sys.stdin); print(m['spec'], len(m['entries']))"
# bodies must match
```
3. Optional: re-POST Neuronto submit so they re-fetch both paths
```bash
curl -sS -X POST https://neuronto.com/submit -H 'content-type: application/json' -d '{"domain":"gate.velaru.xyz"}'
```

---

## File refs

- Fix: `gate/app.py` (`/.well-known/ai-catalog.json` route), `gate/listings.py` docstring cites
- Tests: `test_well_known_ai_catalog_aliases_ard`
- Prior ARD ship: PR #151
