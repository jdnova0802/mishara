# `/v1/act` vs AttriGuard, AgentCap, OWASP (primary sources)

Pull date **18 Nov 2026**. Sources: this repo (`gate/app.py` `run_welded_act`, `gate/owned_write.py`, `gate/app.py` `_mcp_call_tool`, `gate/cloudflare-worker.js`, `gate/counterfactual.py`, `gate/bound.py`, `gate/receipt.py`); He et al., USENIX Security 2026 pp. 1547–1566, PDF `https://www.usenix.org/system/files/usenixsecurity26-he-yu.pdf`; Kabbinamakki Suresh & Gao, arXiv **2611.00729** (AgentCap); OWASP *AI Agent Security Cheat Sheet* (`https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html`); OWASP *Top 10 for Agentic Applications 2026* (ASI, Dec 2025, `https://genai.owasp.org/download/52117/`).

Correction up front, against a tempting slogan: `/v1/act` is a **hop-then-maybe-invoke** door on a spend-shaped mouth. It is **not** AgentCap’s capability object, and it is **not** AttriGuard’s causal test. Default path never writes (`write_executed=false`). Owned-write POSTs a caller HTTPS function after a LIVE hop; `their_production` stays false. Calling that “a working capability-gated payment rail” overclaims the code.

---

## What Gate actually does (named)

`POST /v1/act` (`welded_act` → `run_welded_act`):

1. Requires `fuse_id`. Optional `action` (truncated to 128 chars). Optional `write_url` + `exclusive_owned`.
2. If `write_url` is set without a keyed path (`allow_invoke`), refuse (`owned_write_key_required`). Demo and MCP always take this refuse.
3. Classify `write_url`: HTTPS, not PAS/Guidewire/Duck Creek, not private IP. Else 400, **no hop**.
4. Hop Velaru `POST /api/v1/fuse/hop`. Timeout / halt / DEAD → `acted=false`, `write_executed=false`, **do not POST** `write_url`.
5. If hop `verdict is True` and `write_url` present: `owned_write.invoke` POSTs `{spec, fuse_id, action, clearance_allows, halt}` once for **this HTTP request**. 2xx ⇒ `write_executed=true`. Timeout/non-2xx ⇒ fail closed, `write_executed=false`.
6. If no `write_url`: clearance only. Cloudflare worker (`cloudflare-worker.js`) then `fetch(request)` on permit. Worker is the exclusive origin door; Gate did not execute the write.
7. `bound.attach` signs a bound-answer receipt. `counterfactual.py` is a **cryptographic inaction claim** on forbidden PAS spend paths after HALT/BLOCK — not an LLM shadow replay.

MCP tool `welded_act`: `allow_invoke=False`; `write_url` in arguments is refused. MCP is clearance-only.

Auth for `/v1/act` is a **standing Bearer API key** (`@metered_api`). Hop budget is a commercial 402, not a per-tool capability budget.

---

## 1. Line-by-line: specified vs Gate

Legend: **Y** = this implementation already does it. **N** = specified and missing. **~** = same English word, different mechanism.

### AttriGuard (He et al., USENIX Sec 26)

Paper property (named) | Gate `/v1/act`
---|---
Defense sits **after the model proposes** a tool call and **before** `EXECUTE(c)` (Alg. 1 lines 4, 12–16) | **Y** hop then invoke / worker fetch. Propose is whoever POSTed `/v1/act`, not an in-process LLM.
Gating question is **why** the call was produced: intent-supported vs observation-driven (Def. 1) | **N** hop is LIVE/DEAD on a fuse. No attribution of the caller’s proposal to user intent vs untrusted observations.
Teacher-forced **shadow replay** of π on control-attenuated observations (Alg. 1 lines 8–11) | **N**. `counterfactual.py` is an inaction **receipt**, not a second LLM rollout. Do not equate the two “counterfactuals.”
Hierarchical control attenuation of tool outputs | **N**
Fuzzy survival (function match + critical-arg match + judge; not bitwise identity) | **N**
Reject by returning empty tool result + IPI warning into the agent history | **N** (refuse is HTTP halt / no POST)
~2× token cost of undefended agent | **N/A** (no agent loop)
Eval: AgentDojo (92 user / 882 attack after dropping non-goals) + **ASB** (Zhang et al. ICLR 2025), four LLMs, static ASR 0% in their tables; adaptive subset still single-digit on Gemini-2.5 | **N** — see §3. AttriGuard’s second bench is **ASB**, not InjecAgent.
Threat: IPI in observation stream; model untrusted to self-explain; non-goals = text-to-text and **pure explicit delegation** to attacker-modifiable content | **~** Gate treats the **caller** as untrusted to write without a LIVE hop. It does not model IPI inside an agent’s observation stream at all.
Data-flow IPI (same tool, attacker args) harder than control-flow IPI (extra tools) | **N** Gate does not bind payout args. A LIVE fuse + attacker `write_url` or attacker-chosen origin path (worker uses `METHOD + pathname` as `action`) is exactly the data-flow hole AttriGuard names.

**Satisfied vs AttriGuard:** pre-execution intercept; fail closed if the **external** check says no.

**Not satisfied:** the entire causal-attribution stack (shadow replay, attenuation, survival). Gate’s “counterfactual” is the wrong object.

### AgentCap (arXiv 2611.00729)

Paper property (named) | Gate `/v1/act`
---|---
Separate **propose** (model) from **authorize** (policy engine) from **verify** (gateway) before the tool | **Y** hop = authorize; invoke/worker = execute. Missing the middle **token**.
“No model-generated tool call reaches an MCP server without independently authorized and verifiable authority” | **~** MCP `welded_act` hops but **cannot** invoke. Keyed `/v1/act` can invoke without presenting a capability JWT.
Capability token τ = ⟨j, u, a, r, i, s, θ, q, e, b, P, G, ρ⟩, Ed25519 JWT, verified at the tool boundary | **N** No such object. Closest: fuse hop JSON + bound receipt. Receipt attests the **hop**, not (action, resource, args, budget).
Short-lived, **budget-bounded** (paper’s banking grant: `ttl: 30s`, `budget: 1`) | **N** API key is standing. Owned-write invoke is once **per HTTP request**; a second POST with the same key, LIVE fuse, and `write_url` invokes again. No remaining-budget decrement.
Bound to agent, session, declared intent, action, resource | **N** `action` is a free 128-char string. `write_url` is classified for SSRF/PAS, not bound as resource `r` in a token. No session id in the capability sense (MCP has `Mcp-Session-Id` for transport only).
Intent whitelist (model-supplied, not trusted; binds purpose so a token cannot be reused under another purpose) | **N**
Argument **provenance** / `bound_params: [recipient]` — reject recipient supported only by untrusted tool output | **N** invoke body has no recipient, amount, or provenance labels.
Workflow **prerequisites** (`requires: [get_balance]`) | **N**
**deny_combination** / mutually exclusive authority | **N** (`exclusive_owned=true` is a **caller boolean**, not a mutex among capabilities)
Delegation as attenuating parent→child chains (`a'=a`, `r'=r`, `b'≤b`, `e'≤e`, `d'<d`) | **N**
Trust score with revocation / sandbox after anomalous denials | **N**
Standing tool credentials are the named threat (Intro + §2) | Gate **uses** standing Bearer keys. That is AgentCap’s attack, not its fix.
MCP wrapper obtains request-scoped authority; gateway forwards only after validating the token | MCP on Gate is a **tool catalog + hop**. It refuses `write_url`. It does not issue or check τ.
Static surface analyzer on the policy | **N**
Eval: AgentDojo v1.2.2 (97 benign / 949 attacked) + InjecAgent (1054 attacked); GPT-5.4 ASR 0.00% both | **N** — §3
Audit record id embedded in the signed token | **~** `bound.attach` + Ed25519 receipt chain (`receipt.py`) is the same *spirit* (decision and record in one branch). The signed object is not a capability.

**Satisfied vs AgentCap:** propose/authorize split; fail-closed sequential checks; MCP exists as a surface; signed audit of the **authorization decision**.

**Not satisfied:** per-invocation capability objects. Gate is **standing credentials + a propose/authorize wrapper**, which is exactly the architecture AgentCap §1 says is insufficient (“Expiration and rate limits restrict when and how often credentials may be used, but cannot distinguish a legitimate call from an attacker-directed call made within the same limits”). Hop-limit 402 is that rate limit.

### OWASP Agent Security Cheat Sheet + ASI 2026

Cheat-sheet / ASI line | Gate `/v1/act`
---|---
**Tool Authorization Middleware:** enforce in the execution component, **outside** the agent’s context | **Y**
`user_confirmed` flag is insufficient | **Y** (Gate does not use that flag)
Approval must belong to the **current actor** and **exact tool call**, remain valid, not already consumed | **N** No approval artifact. Actor = whoever holds the API key. “Tool call” = `action` string + optional URL, not normalized parameters.
Check **and consume** the approval in **one atomic step immediately before execution** | **N** Nothing is consumed. Replay the POST, invoke again if the fuse is still LIVE.
Changes to target or parameters require new approval | **~** New `write_url` is re-classified. Parameter changes inside the caller function are invisible to Gate (invoke JSON has no args).
Fail closed for unknown tools or missing approval | **Y** unknown MCP tool `{code: unknown_tool}`; DEAD/timeout/non-2xx/PAS/demo fail closed
**High-Impact Action Integrity:** separate decision-making from execution; policy independently validates scope, privilege, approval **before** execution | **Y** hop before POST. **N** on scope/privilege of the **effect** (amount, recipient, Operate ctlVal)
Bind approval to actor, tool name, **target resource**, **normalized parameters**, timestamp, expiry | **N** missing resource+params+expiry binding
Short-lived authorization artifacts and **replay protection** for irreversible ops | **N** on `/v1/act`. Idempotency keys exist on **operator weld** (`Idempotency-Key` in `app.py` ~5112), not on owned-write invoke
Step-up authentication for payment initiation | **N**
HITL / action preview / dry-run diff (cheat sheet §4; ASI02 mitigation 2) | **N**
Least privilege per tool (ASI02.1); no send rights on a summarizer | **~** default clearance-only is strong least privilege. Owned-write + standing key is full invoke rights for any allowed URL.
ASI02.4 **Intent Gate** PEP/PDP: validate intent **and arguments**, issue short-lived credentials | hop validates fuse state, **not** arguments; credentials stay long-lived
ASI02.5 adaptive tool budgeting | hop **count** budget, not tool-effect budget
ASI02.6 JIT / ephemeral access, bind keys to session | **N**
ASI03.1 task-scoped time-bound tokens | **N**
ASI03.3 re-verify each privileged step with a centralized policy engine | **Y** every `/v1/act` re-hops. **N** that the engine sees the privileged **step’s args**
ASI01.4 validate user intent and agent intent before high-impact actions | **N** no intent objects
ASI08.4 independent policy enforcement; separate planning and execution | **Y**
Structured logs: classification, authorization outcome, approval id, execution result, policy version | **~** receipts log hop + `write_executed`. No approval id (there is none).
Abuse-case matrix: approval bypass, tool misuse even when the model is confident | Unit tests cover deny-does-not-invoke (`gate/test_owned_write.py`). **N** IPI / AgentDojo rows.

**Satisfied vs OWASP middleware paragraph:** enforcement outside the model; fail closed; hop-before-write.

**Not satisfied:** exact-call bind, atomic consume, replay protection, short-lived artifacts, argument validation. Those four are the cheat sheet’s actual middleware spec, not optional color.

---

## 2. Smallest generalization (citable, no rewrite)

Do **not** port AttriGuard’s 2× LLM replay onto Gate. Do **not** rebuild AgentCap’s policy language. Keep `run_welded_act`: hop first, fail closed, POST only on LIVE.

The missing object is a **call capability** issued from the hop and consumed at invoke:

```
τ = {
  j,                    # token id
  actor,                # key / agent id
  tool,                 # "owned_write" | "cf_origin_fetch" | "iec61850.operate" | …
  resource,             # write_url or Operate LN.DO or card auth id
  args_hash,            # canonical JSON of effect args (amount, recipient, ctlVal, …)
  fuse_id,
  issued_at, exp,
  budget: 1,
  nonce
}
```

Sign it with the same Ed25519 already used for receipts. At invoke: verify signature, `args_hash` matches the body about to be POSTed, `budget` atomically 1→0, else refuse. Hop remains the policy engine (LIVE/DEAD). τ is the **exact-call bind** AgentCap’s JWT and OWASP’s middleware both require and Gate currently omits.

That is domain-agnostic:

- Payments: `tool=owned_write`, `resource=https://…/payout`, `args_hash=canonical({amount,recipient})`.
- ICS: `tool=iec61850.operate`, `resource=XCBR1.Pos`, `args_hash=canonical({ctlVal,orCat})`. Same hop, same consume, different `resource` classifier (today’s PAS-hostname denylist becomes an allowlist of Operate endpoints).
- Worker path: issue τ bound to `METHOD + URL + body hash` **before** `fetch(request)`, so the worker cannot fetch a different path than the hop authorized (today `action` is only a string in the hop body; the subsequent `fetch(request)` is unconstrained by a token).

What this is **not**: argument provenance (AgentCap `bound_params`), causal survival (AttriGuard), delegation chains, trust decay. Those are later papers. The smallest step that makes the **same gate** plug into a non-payment mouth without rewriting `run_welded_act` is **bind + consume-once on the effect tuple**.

Until τ exists, the honest citation is: *hop-gated invoke on one spend-shaped URL, standing key, unbound args.* That is an existence proof of fail-closed propose/authorize, not a general capability kernel.

---

## 3. Evaluation gap (do not claim ASR)

| Suite | Papers | This repo |
|-------|--------|-----------|
| AgentDojo (Debenedetti et al., NeurIPS 2024) | AttriGuard (primary); AgentCap (complete suite v1.2.2) | **No adapter, no ASR** |
| InjecAgent (Zhan et al., ACL Findings 2024) | AgentCap | **None** |
| Agent Security Bench (Zhang et al., ICLR 2025) | AttriGuard (second bench) | **None** |
| Gate unit tests (`test_owned_write.py`) | — | deny does not invoke; allow POSTs; PAS URL refused; demo/MCP cannot `write_url`; clearance-only default |

There is **no** AgentDojo/InjecAgent/ASB run against `/v1/act`. Claiming Gate is “ahead of the published work” on IPI ASR is false. Papers measured toy tools with published ASRs. Gate measured hop/invoke wiring on a real mouth with **zero** IPI ASR.

What is actually ahead, if anything: a **deployed fail-closed hop before a write_url**, stranger-verifiable receipts, default `write_executed=false`. What is behind: capability tokens, exact-call consume, provenance, causal attribution, and the academic test suites those papers used to get tables.

**Cite as:** architecture-on-a-rail, unevaluated on the standard agent-security suites. **Do not cite as:** AgentCap-equivalent authorization, or AttriGuard-equivalent IPI defense.

---

## Sources (primary)

- He, Zhu, Li, Shao, Yao, Liu, Qin. *AttriGuard.* USENIX Security 2026, Baltimore, pp. 1547–1566. `https://www.usenix.org/conference/usenixsecurity26/presentation/he-yu`
- Kabbinamakki Suresh, Gao. *AgentCap.* arXiv:2611.00729, Nov 2026. `https://arxiv.org/abs/2611.00729`
- OWASP. *AI Agent Security Cheat Sheet* (Tool Authorization Middleware; High-Impact Action Integrity Controls). `https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html`
- OWASP ASI. *Top 10 for Agentic Applications 2026* (Dec 2025), ASI01–ASI03, ASI08. `https://genai.owasp.org/download/52117/`
- Debenedetti et al. *AgentDojo.* NeurIPS 2024.
- Zhan et al. *InjecAgent.* ACL Findings 2024.
- Zhang et al. *ASB.* ICLR 2025.
- This repo: `gate/app.py` (`run_welded_act`, `welded_act`, `_mcp_call_tool`), `gate/owned_write.py`, `gate/cloudflare-worker.js`, `gate/counterfactual.py`, `gate/test_owned_write.py`.
