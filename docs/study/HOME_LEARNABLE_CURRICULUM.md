# AI SECURITY THEN ML-KEM THEN PERCEPTION/CONTROL — PLAIN ENGLISH

Checkpoint curriculum. Phase 1 = prompt injection / agent abuse (SDT as the scoreboard). Phase 2 = hybrid ML-KEM + TLS. Phase 3 = perception/control (Kalman / SLAM / MPC, simulation only). 10/10 means a stranger can reproduce the artifact.

Cadence: ~30 hrs/week deep work (Thu–Sat). Sun–Wed = warehouse overnight shifts (no study assumed).
Mechanism: spoken-recall checkpoints + bookmarked references only. No notebook / tracker / written logging system.
Constraint: zero capital, home-executable, no clearance, no paid cert required to start.

Phase 1–2 URLs checked 2026-11-22 (HTTP 200, or a named redirect). Do not search those again.
Phase 3 URLs checked 2026-11-24, America/New_York (HTTP 200, or a named redirect). Dead hosts were dropped, not invented.

────────────────────────────────
ORDER DECISION (settled before the roadmap)
────────────────────────────────

Hiring-priority-first wins. Phase 1 = AI/adversarial-ML security (SDT folded in). Phase 2 = cryptography. Phase 3 = perception/control for the later physical-autonomy company.

Why not build-order-first (crypto → measure → attack):
• That sequence describes complementary *career skills across lanes*, not a dependency chain inside one curriculum. You do not need a working ML-KEM or TLS stack to red-team prompt injection, score attack success rates, or tune a detector threshold.
• SDT inside Phase 1 is applied to *attack/detection outcomes* (ASR, FPR/FNR of a guardrail, cost of missing vs false-alerting). That math does not wait on crypto.
• Opportunity cost: AI Security Engineer postings +268.3% (CyberSN Jan–Sep 2026) while most cyber roles fell. Spending 3+ months on crypto first delays the near-term hireable artifact.
• Crypto still goes second — as the harder, slower “implement” depth — once the hiring-facing portfolio piece is live.

Why Phase 3 is third, not parallel, even though it is a different domain:
• You do not need ML-KEM to run a Kalman filter. The dependency is *hours*, not math. Thirty Thursday–Saturday hours cannot carry two Deeps. Parallelizing is how both stay unfinished.
• Phase 3 does not buy the 2026 software-security hire. It is the long-term autonomy stack (reachable at home because it is math/code/simulation — unlike aero shop loops you do not have).
• Start Phase 3 only after Phase 2’s *home* 10/10 gate. Do not wait on an upstream merge or a lab. Do not “just peek” at PX4 during Phase 1 or 2.

Do not silently flip Phase 1/2 later unless the hiring signal collapses.
Do not silently pull Phase 3 forward unless Phase 2’s home gate is done.

════════════════════════════════
PHASE 1 — AI / ADVERSARIAL-ML SECURITY
(OWASP LLM01:2026 Prompt Injection + agent tool-abuse; SDT as the scoring language)
════════════════════════════════

Calendar estimate: 11–13 weeks @ 30 hrs/week ≈ 330–390 hours.
Exit gate: the 10/10 artifact below exists and you can explain it aloud cold.

Bookmark set (open once, pin in browser; do not maintain a notes file):
• OWASP Top 10 for LLM Applications 2026 (HTML)
  https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/
• OWASP Top 10 for LLM Applications 2026 (PDF download; filename OWASP-GenAI-LLM-Top-10-2026-v1.0.pdf)
  https://genai.owasp.org/download/56857/
• OWASP Top 10 2026 canonical markdown
  https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/tree/main/2026/final
• OWASP LLM Prompt Injection Prevention Cheat Sheet
  https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html
• OWASP AI Agent Security Cheat Sheet
  https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html
• MITRE ATLAS (homepage is the matrix; /matrices/ATLAS and /techniques/AML.T0051 are 404 — search Prompt Injection on the homepage)
  https://atlas.mitre.org/
  search: https://atlas.mitre.org/?search=prompt%20injection
• Google ML Crash Course — Thresholds and the confusion matrix
  https://developers.google.com/machine-learning/crash-course/classification/thresholding
• Google ML Crash Course — Accuracy, precision, recall
  https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall
• Google ML Crash Course — ROC and AUC
  https://developers.google.com/machine-learning/crash-course/classification/roc-and-auc
• 3Blue1Brown — The medical test paradox (M4 only; ~20 min; not a Bayes course)
  https://www.3blue1brown.com/lessons/better-bayes/
• Simon Willison — prompt injection tag
  https://simonwillison.net/tags/prompt-injection/
• NVIDIA/garak
  https://github.com/NVIDIA/garak
• microsoft/PyRIT (repo)  https://github.com/microsoft/PyRIT
  docs  https://microsoft.github.io/PyRIT/
• promptfoo/promptfoo
  https://github.com/promptfoo/promptfoo
• ReversecLabs/damn-vulnerable-llm-agent
  https://github.com/ReversecLabs/damn-vulnerable-llm-agent
• PortSwigger Web Security Academy — Web LLM attacks (topic)
  https://portswigger.net/web-security/llm-attacks
• PortSwigger — Web LLM attacks (learning path)
  https://portswigger.net/web-security/learning-paths/llm-attacks
• Lakera Gandalf (old host 301s to Agent Breaker)
  https://gandalf.lakera.ai/  →  https://play.lakera.ai/agent-breaker
• Wiz Prompt Airlines
  https://www.promptairlines.com/
• HackAPrompt dataset (Hugging Face)
  https://huggingface.co/datasets/hackaprompt/hackaprompt-dataset
• protectai/llm-guard (repo ARCHIVED; docs still up)
  https://github.com/protectai/llm-guard
  https://protectai.github.io/llm-guard/

Local free stack (install once):
• Ollama  https://ollama.com/  + one local instruct model (e.g. mistral-nemo or llama3.x — pick what fits your RAM)
• Python 3.11+ venv
• pip/npm: garak (https://github.com/NVIDIA/garak), promptfoo (https://github.com/promptfoo/promptfoo), pyrit per https://github.com/microsoft/PyRIT
• Optional free cloud model credits later; not required — local Ollama is the default target

────────────────────────────────
P1 · MILESTONE SEQUENCE (do in order; finish each before the next)
────────────────────────────────

M1 — Taxonomy cold (1 weekend / ~20–25 hrs)
Do:
1. Read OWASP LLM01:2026 end-to-end (delivery surface × propagation × encoding axes).
   Start: https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/
   PDF:   https://genai.owasp.org/download/56857/
2. Read LLM03:2026 Excessive Agency enough to separate “injection at the input boundary” from “too much tool power.”
3. Open ATLAS (https://atlas.mitre.org/), find Prompt Injection / LLM abuse techniques; say the ATLAS IDs aloud once.
   Search: https://atlas.mitre.org/?search=prompt%20injection
Spoken-recall checkpoint (record voice memo or talk to empty room — then delete; do not keep a log):
  “In one breath: what is LLM01 vs LLM03 vs LLM10, and why injection stays #1 even when incident counts look low.”
Pass: you can do that without looking. Fail: re-read LLM01 only, retry next morning.

M2 — Direct injection intuition (1 weekend / ~25–30 hrs)
Do:
1. Clear Lakera Gandalf through as many levels as you can in one sitting; then retry cold next day.
   Pin: https://play.lakera.ai/agent-breaker
2. Clear Wiz Prompt Airlines (https://www.promptairlines.com/) once.
3. Bookmark HackAPrompt (https://huggingface.co/datasets/hackaprompt/hackaprompt-dataset); skim 20 winning payloads — do not copy into a notebook; leave the tab.
Spoken-recall:
  “Name three direct-injection patterns that worked and why a keyword filter would miss each.”

M3 — Structured labs with a real agent surface (1.5 weekends / ~40–45 hrs)
Do:
1. Complete PortSwigger Web Security Academy — Web LLM attacks (all free labs in that path).
   Path: https://portswigger.net/web-security/learning-paths/llm-attacks
   Topic: https://portswigger.net/web-security/llm-attacks
2. Clone ReversecLabs/damn-vulnerable-llm-agent (https://github.com/ReversecLabs/damn-vulnerable-llm-agent);
   run the Ollama path (.env.ollama.template → edit llm-config.yaml → `python -m streamlit run main.py`).
3. Model fallback if ReAct JSON/tool-calls flake (in this order — do not invent other named tools):
   a. Primary: `ollama pull mistral-nemo` (DVLA’s own documented local default).
   b. If structured Thought/Action JSON is unreliable: step up to a ≥13–14B local instruct
      model via Ollama, e.g. `ollama pull qwen2.5:14b` or `ollama pull qwen3:14b`
      (needs ~14–16 GB RAM/VRAM class machine; Q4 quant). Point llm-config.yaml at it.
   c. If local hardware can’t hold 14B: use DVLA’s OpenAI path with a free-tier / low-spend
      key (OpenAI or another OpenAI-compatible free tier you already have), spending-capped.
      Still zero-capital to *start*; free tier is the backup, not a required paid product.
4. Solve both intended DVLA flags: (a) classic system-overwrite injection for userId=2,
   (b) Thought/Action/Observation injection hijacking the ReAct loop.
   Use upstream README solutions only after one honest failed attempt each.
   README’s other intended flag is UNION SQL on GetUserTransactions — honest attempt first, then README.
Spoken-recall:
  “Walk through the ReAct loop. Where does Observation injection sit, and what tool call did you force?”
DO NOT USE: any “CyberCTF/vulnerable-llm-agent Isoloom” path — drop it from the plan.

M4 — SDT enters as the scoreboard (1 weekend / ~25–30 hrs)
Do:
1. Read Google ML Crash Course: Thresholding, Accuracy/precision/recall, and ROC/AUC (free). No separate “SDT course.” No extra Bayesian module.
   https://developers.google.com/machine-learning/crash-course/classification/thresholding
   https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall
   https://developers.google.com/machine-learning/crash-course/classification/roc-and-auc
   Crash Course already covers: accuracy lies under class imbalance, 0.5 is not a default when costs differ, AUC is ranking quality across all thresholds so it does not pick an operating point.
2. One sitting (~45 min, stolen from re-watching ROC — do not add hours): 3Blue1Brown “The medical test paradox”
   https://www.3blue1brown.com/lessons/better-bayes/
   Map: disease → attack, test → detector, P(disease | +) → PPV of an alert. That is the base-rate logic under the FP/FN cost story (expected cost = prior × c_miss × miss + (1−prior) × c_fa × fa). Stop there. Do not assign Seeing Theory, Beta priors, or any other Bayes chapter.
3. Write a tiny local Python script (throwaway is fine; Git will hold the final version later) that, given a CSV of {attack_id, score, label_success}, plots ROC and picks a threshold under two cost regimes: (FP costly = false alarm blocks legit user) vs (FN costly = missed injection). Also print expected cost at two attack base rates (rare vs common) so the PPV story has numbers, not slogans.
4. Apply it to a hand-scored set of ≥30 Gandalf/DVLA attempts (success/fail + a numeric confidence you assign or a guardrail score).
Spoken-recall:
  “Why AUC alone does not pick your threshold. Give the FP vs FN cost story for a production agent with email+shell tools — including what a 1% FPR still does to PPV when attacks are rare.”

M5 — Breadth scanner: garak (1 weekend / ~25–30 hrs)
Do:
1. Point garak (https://github.com/NVIDIA/garak) at your local Ollama endpoint.
2. Run probe sets covering promptinject / jailbreak / leakage families (exact probe names per current garak --list_probes; use what exists in your install).
3. Save raw report artifacts in the repo (reports are evidence, not a diary).
Spoken-recall:
  “What did garak catch that your manual Gandalf practice did not, and what did it miss that DVLA taught you?”

M6 — Multi-turn: PyRIT (1.5 weekends / ~40–45 hrs)
Do:
1. Stand up PyRIT (https://github.com/microsoft/PyRIT · docs https://microsoft.github.io/PyRIT/) against the same local target (and/or DVLA).
2. Run at least one multi-turn strategy (e.g. Crescendo-style / multi-turn jailbreak per current PyRIT docs).
3. Score outcomes with the M4 SDT script: success rate by turn depth; plot how ASR rises with turns.
Spoken-recall:
  “Why single-shot scanners understate agent risk. Quote your turn-depth ASR numbers from memory.”

M7 — App-specific regression: Promptfoo (1 weekend / ~25–30 hrs)
Do:
1. Define a tiny intentional agent app of your own (local): tools = {read_file, http_get, send_email_stub} with an allowlist. This is your product-under-test.
2. Write Promptfoo cases (https://github.com/promptfoo/promptfoo) for: direct injection, indirect injection via retrieved markdown, tool-arg injection, exfil via tool args.
3. Wire `promptfoo eval` so one command re-runs the suite.
Spoken-recall:
  “What is the difference between a generic garak pass and a Promptfoo case that encodes *your* tool policy?”

M8 — Indirect injection + RAG/memory (1.5 weekends / ~40–45 hrs)
Do:
1. Add a trivial RAG folder to your agent (3–5 local .md files). Plant an indirect injection in one file (hidden instruction in retrieved content, not in the user chat).
2. Demonstrate: user asks an innocent question → retriever pulls poisoned doc → agent executes attacker goal (unauthorized tool call or secret leak).
3. Map the run to OWASP LLM01:2026 axes:
   • delivery = retrieved content
   • propagation = single-shot (or cross-session if you also write agent memory)
   • encoding = plain text (optionally one obfuscated variant: base64 / invisible unicode)
4. Add one Promptfoo case that fails until you fix a retrieval trust boundary
   (e.g. wrap retrieved text as untrusted data; strip instruction-like lines —
   imperfect is fine; measure before/after with the M4 SDT script).
Spoken-recall:
  “Indirect injection kill chain in order. Where would you put the trust boundary if you could only pick one place?”

M9 — Guardrail + measure the tradeoff (1 weekend / ~25–30 hrs)
Do:
1. Add a simple detector layer in front of / around the agent.
   Start with protectai/llm-guard (https://github.com/protectai/llm-guard — ARCHIVED; pip still, or https://protectai.github.io/llm-guard/)
   *or* a small heuristic/regex+LLM judge — measurement is the point, not shipping a commercial guardrail.
2. Re-run your Promptfoo suite + a garak subset before and after the detector.
3. Feed {attack_id, detector_score, label_success} into the M4 SDT script.
   Produce ROC (or precision-recall if heavily imbalanced).
4. Pick two operating points and defend both aloud:
   • “security-first” (FN costly: missed injection → tool abuse)
   • “UX-first” (FP costly: false alarm blocks legit user)
   Invent and defend FP/FN costs in dollars-or-hours; do not default to Youden’s index.
Spoken-recall:
  “At your chosen threshold: ASR, FPR, and why that point — not the Youden index default.”

M10 — Portfolio lock (1–1.5 weekends / ~30–40 hrs)
Do:
1. Public GitHub repo containing: vulnerable agent (or DVLA fork notes), Promptfoo suite, before/after metrics, one HTML or Markdown findings report.
2. Findings report sections (fixed template — write it once as the artifact, not as ongoing notes): executive summary · methodology · findings mapped to LLM01/LLM03 + ATLAS IDs · SDT threshold rationale · mitigations · reproduce commands.
3. 3–5 minute screen recording walking the indirect-injection demo and the ROC threshold choice (raw demo, not a polished video essay).
Spoken-recall (final Phase 1 gate):
  Cold, no screen: “Explain the demo, the worst finding, the threshold you shipped, and what still breaks.” If you stumble, do not start Phase 2.

────────────────────────────────
P1 · WHAT “10/10” MEANS
────────────────────────────────
Not: “I understand prompt injection.”
Yes — all of the following exist and are reproducible by a stranger:
1. Public repo with one-command local reproduce (README: Ollama model name + `promptfoo eval` + garak command).
2. At least one working indirect prompt-injection → unauthorized tool call demo against your own agent.
3. Findings report mapping to OWASP LLM01:2026 (+ LLM03 where agency is the blast radius) and ATLAS IDs.
4. Quantified before/after with ROC/threshold analysis under unequal FP/FN costs (SDT applied, not theorized).
5. Spoken: you can teach the kill chain and the threshold choice in 5 minutes with no notes.

════════════════════════════════
PHASE 2 — CRYPTOGRAPHY
(hybrid ML-KEM + classical PKI/TLS + crypto-agility)
Start only after Phase 1 spoken final gate passes.
════════════════════════════════

Calendar estimate: 12–14 weeks @ 30 hrs/week ≈ 360–420 hours.
Exit gate: the 10/10 artifact below.

Bookmark set (open once, pin in browser):
• NIST FIPS 203 landing + errata
  https://csrc.nist.gov/pubs/fips/203/final
• NIST FIPS 203 PDF
  https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf
• RFC 8446 (TLS 1.3)
  https://www.rfc-editor.org/rfc/rfc8446.html
• RFC 10024 (PQ/T hybrid key agreement for TLS 1.3: X25519MLKEM768, SecP256r1MLKEM768, SecP384r1MLKEM1024)
  https://www.rfc-editor.org/rfc/rfc10024.html
• pq-code-package/mlkem-native
  https://github.com/pq-code-package/mlkem-native
• cryspen/libcrux (redirects to celabshq/libcrux)
  https://github.com/cryspen/libcrux  →  https://github.com/celabshq/libcrux
  crate docs: https://docs.rs/libcrux-ml-kem
• open-quantum-safe/liboqs
  https://github.com/open-quantum-safe/liboqs
• OpenSSL 3.5+ native ML-KEM
  https://docs.openssl.org/master/man7/EVP_PKEY-ML-KEM/
• OpenSSL hybrid ML-KEM groups (X25519MLKEM768 etc.)
  https://docs.openssl.org/master/man7/EVP_PKEY-MLX-KEM/
• OpenSSL s_client (handshake demo)
  https://docs.openssl.org/master/man1/openssl-s_client/
• open-quantum-safe/oqs-provider (only if OpenSSL < 3.5 or non-standardized hybrids)
  https://github.com/open-quantum-safe/oqs-provider
• Cloudflare hybrid KEM in TLS (intuition only; FIPS + RFCs remain primary)
  https://developers.cloudflare.com/ssl/post-quantum-cryptography/
  https://blog.cloudflare.com/post-quantum-for-all/
  https://blog.cloudflare.com/post-quantum-cryptography-ga/
• Cloudflare lattice primer (M2 read-only; do not re-implement)
  https://blog.cloudflare.com/lattice-crypto-primer/

Local free stack:
• C toolchain + CMake/Ninja (or Rust toolchain if you choose libcrux path)
• OpenSSL ≥ 3.5 if available on your distro; else liboqs + oqs-provider on OpenSSL 3.x
• Wireshark (free) for handshake inspection
• git

Reference implementation choice (pick one primary; use the others as oracles):
• Primary recommend: mlkem-native (C, FIPS 203, used as default ML-KEM backend in liboqs ≥ 0.13) OR libcrux-ml-kem (Rust) if you are stronger in Rust.
• Oracle/cross-check: liboqs test_kem + ACVP vectors.

────────────────────────────────
P2 · MILESTONE SEQUENCE
────────────────────────────────

M1 — Classical baseline you can explain (1 weekend / ~25–30 hrs)
Do:
1. Read TLS 1.3 handshake outline (client hello → server hello → keys) from RFC 8446
   (https://www.rfc-editor.org/rfc/rfc8446.html) § key schedule skim + Cloudflare PQC page
   (https://developers.cloudflare.com/ssl/post-quantum-cryptography/).
2. Use stock OpenSSL `s_client`/`s_server` with classical X25519; capture in Wireshark; identify key_share.
   https://docs.openssl.org/master/man1/openssl-s_client/
Spoken-recall:
  “What is authenticated encryption’s job vs key exchange’s job in TLS 1.3? Where does a KEM fit?”

M2 — FIPS 203 as an API, not a vibe (1 weekend / ~25–30 hrs)
Do:
1. Read FIPS 203 sections on KeyGen / Encaps / Decaps and the sizes for ML-KEM-512/768/1024.
   Also read §3.2 (the MLWE assumption) in the same PDF — do not skip it for the API pages.
   PDF: https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf
   errata: https://csrc.nist.gov/pubs/fips/203/final
2. One sitting (1–2 hrs, stolen from a second full-spec read — do not add hours, do not add a milestone):
   Cloudflare “Prepping for post-quantum: a beginner’s guide to lattice cryptography”
   https://blog.cloudflare.com/lattice-crypto-primer/
   Read only. Do not re-implement their tutorial (that duplicates M3).
   Spoken bar you are aiming at: Shor kills hidden-period problems on abelian groups (RSA, ECDH). LWE is recover s from As+e; noise is why Gaussian elimination fails; no known quantum poly-time analogue of Shor for that. Module-LWE is the same equation with polynomial entries so keys fit on the wire.
   Stop there. No Regev reduction, no Module-SIVP, no FO/QROM, no “why not McEliece” research comparison. M5 (hybrid combiner) is the wrong place for this — combiner ≠ hardness.
3. Run liboqs `test_kem` for ML-KEM-768 (https://github.com/open-quantum-safe/liboqs); run ACVP-related tests if enabled in your build (`ninja run_tests` / project’s ACVP test path).
Spoken-recall:
  “Name ciphertext and shared-secret sizes for ML-KEM-768. What does Decaps return on a forged ciphertext (rejection)? In one breath: why RSA/ECDH die under Shor and why ML-KEM is believed not to.”

M3 — Build against a reference (2 weekends / ~55–65 hrs)
Do:
1. Clone mlkem-native (https://github.com/pq-code-package/mlkem-native) *or* use libcrux-ml-kem (https://github.com/celabshq/libcrux · https://docs.rs/libcrux-ml-kem).
2. Produce a minimal CLI: `keygen | encaps | decaps` that prints hex shared secrets and exits non-zero on mismatch.
3. Cross-check at least 10 known-answer / ACVP vectors (via liboqs vectors or NIST ACVP JSON) against your CLI — bit-exact.
Spoken-recall:
  “How did you prove bit-exactness? What failed first, and what was the bug class?”

M4 — Constant-time / misuse awareness (1 weekend / ~25–30 hrs)
Do:
1. Read mlkem-native / libcrux docs on constant-time claims; do not invent your own side-channel lab gear.
2. Add negative tests: corrupted ciphertext → rejection path; truncated key → fail closed.
3. Deliberately misuse once in a branch (e.g. compare secrets with early-exit memcmp in a *test that you then fix*) so you can explain the footgun.
Spoken-recall:
  “What is a timing side channel in Decaps comparison terms, in plain English?”

M5 — Hybrid KEM combiner (1.5 weekends / ~40–45 hrs)
Do:
1. Implement a teaching hybrid: shared_secret = KDF(ss_X25519 || ss_MLKEM) using a real KDF (HKDF-SHA256) — label it *non-production teaching code* unless you follow RFC 10024 transcript rules exactly.
   RFC 10024: https://www.rfc-editor.org/rfc/rfc10024.html
2. Separately, prefer *real* TLS hybrids via OpenSSL 3.5+ groups: X25519MLKEM768 (and optionally SecP256r1MLKEM768).
   https://docs.openssl.org/master/man7/EVP_PKEY-MLX-KEM/
3. Document in README which path is “toy combiner for learning” vs “RFC 10024 / OpenSSL native.”
Spoken-recall:
  “Why is a naked ss1||ss2 without the TLS transcript binder not ‘the TLS hybrid’?”

M6 — TLS 1.3 hybrid handshake that you can capture (2 weekends / ~55–65 hrs)
Do:
1. Bring up OpenSSL `s_server`/`s_client` (or rustls with AWS-LC if you took the Rust path) negotiating X25519MLKEM768 (`-groups X25519MLKEM768` once OpenSSL ≥ 3.5 is on the box).
2. Wireshark: show key_share group id / sizes consistent with ML-KEM-768 hybrid.
3. Script a one-command demo: start server → client connect → print negotiated group → curl/fetch a page over it.
Spoken-recall:
  “Walk the hybrid ClientHello/ServerHello. What grows vs classical X25519, and by roughly how much?”

M7 — X.509 / PKI layer (1.5 weekends / ~40–45 hrs)
Do:
1. Build a local PKI: root CA → intermediate → leaf (classical signatures are fine for this milestone; optional ML-DSA later if time).
2. Serve TLS with that leaf; trust the root in your client explicitly.
3. Break it on purpose once (wrong SAN / expired leaf) and show the client failure mode.
Spoken-recall:
  “Chain of trust in one breath. What does the KEM replace, and what does it *not* replace, in this setup?”

M8 — Crypto-agility pattern (1.5 weekends / ~40–45 hrs)
Do:
1. Design a tiny library API: `NegotiatedKEM` enum { X25519, MLKEM768, X25519MLKEM768 } with versioned wire format + feature flag.
2. Demonstrate algorithm swap without rewriting callers (config flip or both peers advertising preferences).
3. Write an interoperability test matrix: your CLI ↔ liboqs ↔ OpenSSL for encaps/decaps or TLS group negotiation where applicable.
Spoken-recall:
  “What is crypto-agility in one sentence, and what breaks if you hard-code ML-KEM-768 only?”

M9 — Portfolio lock (1–1.5 weekends / ~30–40 hrs)
Do:
1. Public repo: `mlkem-cli` (bit-exact tests) + `hybrid-tls-demo` (one-command OpenSSL/rustls demo) + short writeup “Hybrid ML-KEM in TLS 1.3 — what I implemented, what I only wrapped, what is not FIPS-validated.”
2. Include reproduce script and Wireshark screenshot(s) in `/artifacts`.
3. 3–5 minute recording: keygen/encaps/decaps bit-exact run, then TLS hybrid connect.
Spoken-recall (final Phase 2 gate):
  Cold: “FIPS 203 role of KeyGen/Encaps/Decaps; which hybrid group you demo; what crypto-agility buys you; what you did *not* claim (no ‘FIPS certified module’ language).”

────────────────────────────────
P2 · WHAT “10/10” MEANS
────────────────────────────────
Not: “I read about post-quantum crypto.”
Yes:
1. Bit-exact ML-KEM-768 encaps/decaps against public ACVP/KAT vectors in a CLI you own.
2. Working TLS 1.3 hybrid demo using a standardized group (prefer X25519MLKEM768 via OpenSSL ≥ 3.5).
3. Local PKI-issued cert used in that demo; you can explain chain validation failures.
4. Explicit crypto-agility seam (algorithm negotiable without rewriting callers).
5. Honest writeup separating: your code / upstream reference / standardized TLS hybrid / anything not validated.
6. Spoken cold explanation without notes.

════════════════════════════════
PHASE 3 — PERCEPTION / CONTROL
(Kalman / EKF / UKF, SLAM/VIO, MPC — math/code/simulation)
Start only after Phase 2 spoken final gate passes.
════════════════════════════════

Calendar estimate: 6–8 weeks @ 30 hrs/week ≈ 160–200 hours (install overruns real; 16 weeks of robotics Twitter is not a finish).
Exit gate: the 10/10 artifact below. Everything is software-in-the-loop or offline datasets. A hover in jMAVSim is not a hardware flight. Say that at the gate.

Why this is the Deep physical subject: mechanical/aerospace genuine specialist depth needs a shop (wind tunnel, stands, coupons) you do not have. Estimation and control are reachable at home.

SDT from Phase 1 is *detection* (is this H1?). Kalman is *estimation* (where is x?). Same probability objects; different question. One spoken line in P3-M4. Do not restudy ROC under a robotics sticker.

Bookmark set (open once, pin in browser):
• Kalmanfilter.net — 1-D / EKF / UKF
  https://kalmanfilter.net/kalman1d.html
  https://kalmanfilter.net/ekf.html
  https://kalmanfilter.net/ukf.html
• Rlabbe — Kalman and Bayesian Filters in Python (check, not copy-paste)
  https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python
• FilterPy
  https://github.com/rlabbe/filterpy
  https://filterpy.readthedocs.io/en/latest/kalman/KalmanFilter.html
  https://filterpy.readthedocs.io/en/latest/kalman/ExtendedKalmanFilter.html
  https://filterpy.readthedocs.io/en/latest/kalman/UnscentedKalmanFilter.html
• NumPy / SciPy / Matplotlib
  https://numpy.org/doc/stable/
  https://docs.scipy.org/doc/scipy/
  https://matplotlib.org/stable/
• Solà — Quaternion kinematics for the error-state Kalman filter (read; do not re-derive the whole report)
  https://arxiv.org/abs/1502.01030
• ROS 2 Humble install + tutorials + tf2
  https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html
  https://docs.ros.org/en/humble/Tutorials.html
  https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools.html
  https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html
  https://docs.ros.org/en/humble/Concepts/Basic/About-TF2.html
  https://docs.ros.org/en/humble/p/tf2/
• PX4 SITL (default jMAVSim; Gazebo only if jMAVSim is blocked)
  https://docs.px4.io/main/en/
  https://docs.px4.io/main/en/dev_setup/dev_env_linux_ubuntu.html
  https://docs.px4.io/main/en/simulation/
  https://docs.px4.io/main/en/sim_jmavsim/
  https://docs.px4.io/main/en/sim_sih/
  https://docs.px4.io/main/en/sim_gazebo_gz/
  https://github.com/PX4/PX4-Autopilot
  https://docs.px4.io/main/en/ros2/user_guide.html
  https://docs.px4.io/main/en/ros2/offboard_control.html
  https://docs.px4.io/main/en/flight_modes/offboard.html
• MAVLink / MAVSDK
  https://mavlink.io/en/
  https://mavsdk.mavlink.io/main/en/python/quickstart.html
• EuRoC MAV dataset (Research Collection is the file host; old wiki 200s but says moved)
  paper: https://arxiv.org/abs/1605.05732
  DOI: https://doi.org/10.3929/ethz-b-000690084
  MH_01_easy zip: https://www.research-collection.ethz.ch/bitstream/handle/20.500.11850/263889/1/MH_01_easy.zip
  ASL index: https://ethz-asl.github.io/datasets/
• OpenVINS
  https://github.com/rpng/open_vins
  https://docs.openvins.com/gs-installing.html
  https://docs.openvins.com/gs-tutorial.html
• evo (trajectory error)
  https://github.com/MichaelGrupp/evo
• KITTI odometry
  https://www.cvlibs.net/datasets/kitti/
  https://www.cvlibs.net/datasets/kitti/eval_odometry.php
  paper: https://www.cvlibs.net/publications/Geiger2012CVPR.pdf
• GTSAM + iSAM2 paper
  https://gtsam.org/
  https://gtsam.org/get_started/
  https://gtsam.org/tutorials/intro.html
  https://github.com/borglab/gtsam
  https://arxiv.org/abs/1207.4759
• CasADi + do-mpc + Underactuated trajopt
  https://web.casadi.org/
  https://web.casadi.org/get/
  https://web.casadi.org/docs/
  https://web.casadi.org/blog/opti/
  https://www.do-mpc.com/en/latest/getting_started.html
  https://www.do-mpc.com/en/latest/example_gallery/oscillating_masses_discrete.html
  https://github.com/do-mpc/do-mpc
  https://underactuated.csail.mit.edu/trajopt.html
• Optional later (not first VIO): ORB-SLAM3
  https://github.com/UZ-SLAMLab/ORB_SLAM3
  https://arxiv.org/abs/2007.11898

Local free stack:
• Ubuntu 22.04 (or WSL2 with Ubuntu 22.04). Humble’s documented path is Debian packages on Ubuntu.
• Python 3.11+ venv: numpy scipy matplotlib filterpy evo
• ROS 2 Humble
• PX4 Autopilot + jMAVSim (Java). SIH if Java is blocked.
• CMake/C++ as needed for OpenVINS / GTSAM / PX4
• git. No drone, no lidar, no Jetson, no motion-capture hall.

────────────────────────────────
P3 · MILESTONE SEQUENCE
────────────────────────────────

M1 — State, Gaussian, covariance (1 weekend / ~10 hrs)
Do:
1. Read https://kalmanfilter.net/kalman1d.html
2. Write a 1-D constant-velocity simulator: true x, noisy z, plot both. No filter yet.
3. Draw 100 samples from a 2-D Gaussian; sample covariance should be close to the matrix you wrote.
Spoken-recall:
  “What is a state, what is a measurement, and why is covariance a matrix instead of one number?”

M2 — Linear Kalman from scratch (1 weekend / ~14 hrs)
Do:
1. Implement predict (x, P through F, Q) and update (K, x, P through H, R) in NumPy. No FilterPy inside the function.
2. Overlay FilterPy on the same noise seed. Match to numerical noise.
   https://filterpy.readthedocs.io/en/latest/kalman/KalmanFilter.html
   Rlabbe book as a check, not a paste: https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python
Spoken-recall:
  “Write the predict equations, then the update equations, in words: what does K do to P?”

M3 — EKF and UKF from scratch (1 weekend / ~16 hrs)
Do:
1. https://kalmanfilter.net/ekf.html and https://kalmanfilter.net/ukf.html
2. Nonlinear plant (unicycle or range-bearing). Your EKF *and* UKF vs FilterPy.
3. Large angle step on purpose: see EKF lie. Honesty > a pretty plot.
4. Solà arXiv 1502.01030 — read for attitude/error-state literacy; do not re-derive the report.
Spoken-recall:
  “When is the EKF’s Jacobian a lie, and what does the UKF do instead of that Jacobian?”

M4 — Noise, observability, consistency (1 sitting / ~10 hrs)
Do:
1. Sweep Q and R. Too-small R: overfit measurements. Too-small Q: trust a dead model.
2. NIS on innovations; NEES on error vs truth. Say consistent / optimistic / pessimistic.
3. One spoken sentence: SDT decides a hypothesis; this filter estimates a vector. Gating an innovation is the cousin. Stop. No ROC restudy.
Spoken-recall:
  “If NEES is always huge, is P too small or too big, and what would you touch first, Q or R?”

M5 — ROS 2 Humble, topics, tf2 (1 weekend / ~12 hrs)
Do:
1. Install: https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html
2. CLI + Python pub/sub + tf2 static broadcaster (bookmark set).
3. Publish a fake PoseStamped from your M2 filter at 50 Hz. tf2_echo map → base_link.
Spoken-recall:
  “What is a topic versus a TF frame, and why does a filter that does not timestamp its pose poison the tree?”

M6 — EuRoC + OpenVINS (1.5 weekends / ~18 hrs)
Do:
1. Download MH_01_easy from the Research Collection zip in the bookmark set. Read Burri et al. arXiv 1605.05732.
2. Run OpenVINS on MH_01_easy. evo ATE and RPE in the README. If ATE is garbage, fix frames/time — do not “tune until RViz looks straight.”
3. ORB-SLAM3 is optional *after* this ATE exists. Not the first VIO.
Spoken-recall:
  “What sensors are on EuRoC, what is ground truth, and what would a good ATE on MH_01 mean that a pretty video does not?”

M7 — KITTI odometry (1 weekend / ~12 hrs)
Do:
1. One sequence with ground truth (00 or 07). Not the whole raw corpus.
2. A path you can explain (OpenVINS or a minimal stereo/VO). evo vs KITTI poses.
Spoken-recall:
  “KITTI is a car, EuRoC is a MAV. What breaks in your estimator when scale, IMU, and loop-closures change between those two?”

M8 — Factor graphs / GTSAM (1 weekend / ~14 hrs)
Do:
1. 2-D pose-graph: odometry edges + one loop-closure. Optimize. Show the loop pull the tail in.
2. iSAM2 paper arXiv 1207.4759 — read what incremental means. Do not build a research system.
Spoken-recall:
  “What is a factor, what is a variable, and how is a batch pose-graph different from a causal Kalman filter?”

M9 — PX4 SITL, jMAVSim (1 weekend / ~14 hrs)
Do:
1. Build PX4 SITL; start jMAVSim; arm, takeoff, hover, land via MAVSDK or commander. Screen video.
2. Gazebo only if jMAVSim will not run. Still SITL. Still not hardware.
Spoken-recall:
  “What is SITL versus a real IMU, and which loops (estimation, rate, position) are you actually closing in jMAVSim?”

M10 — MPC on a planar plant (1 weekend / ~16 hrs)
Do:
1. CasADi Opti or do-mpc oscillating-masses example, then *your* discrete MPC on a 2-D double integrator or unicycle: horizon N, input limits, hit a waypoint.
2. Underactuated trajopt chapter for the words. Liniger RSS 2011 PDF is formulation-only — do not build a race car.
Spoken-recall:
  “What is predicted over the horizon, what is applied to the plant, and what happens if the model in the MPC is not the model you simulate?”

M11 — Close a loop in SITL (1 weekend / ~14 hrs)
Do:
1. Required path A: offboard position setpoints, fly a square in jMAVSim. PX4’s own controller may stay in the loop.
2. Path B (the spine): EKF state → your M10 MPC on the *toy* plant, or on PX4 only if you can still name every block. If offboard rates will not stabilize, keep path A + toy MPC and say PX4 kept the inner loop. Do not fake a custom rate controller you did not stabilize.
Spoken-recall:
  “Name the blocks: sensors → estimator → planner/MPC → mixer. Which of those did you write, and which did PX4 keep?”

M12 — Portfolio lock (1 weekend / ~12 hrs)
Do:
1. Public repo: reproduce commands (Humble, PX4 tag, EuRoC sequence, Python pins).
2. Demos: (1) NumPy KF/EKF/UKF vs FilterPy + NEES plot; (2) OpenVINS MH_01 + evo numbers; (3) jMAVSim hover or offboard square, caption SITL only; (4) CasADi/do-mpc waypoint.
3. One-page README findings: what broke, what is simulated-only, what you would not claim to a flight test engineer.
4. 3–5 minute recording: M2 equations → M6 ATE → M10 horizon → M11 block diagram. No notes. That recording *is* the Phase 3 spoken gate.
Spoken-recall (final Phase 3 gate):
  The walkthrough. If you need the README, the lock is not closed.

────────────────────────────────
P3 · WHAT “10/10” MEANS
────────────────────────────────
Not: “I watched a PX4 video.”
Yes:
1. Linear KF predict/update spoken, including what K does to P.
2. EKF vs UKF in one minute, including a case where linearization is the failure.
3. NEES/NIS: you can say whether a filter is lying about its uncertainty.
4. OpenVINS (or a VIO you can defend) on EuRoC MH_01 with a published ATE, not an RViz screenshot.
5. One KITTI sequence with a number, and a spoken difference vs EuRoC.
6. A GTSAM (or equivalent) pose-graph that actually uses a loop-closure.
7. PX4 SITL hover or offboard square *and* the sentence “this is not hardware.”
8. MPC on a constrained planar plant you can derive.
9. Block diagram of M11: your code vs PX4’s.
10. Public repo a stranger can clone; video; README; spoken walkthrough without notes.

════════════════════════════════
CALENDAR AT A GLANCE (~30 hrs/week)
════════════════════════════════
Weeks 1–12ish ………… Phase 1 (AI/adv-ML + SDT-as-tool) → hiring-facing artifact live
Week 13 ……………… buffer / Phase 1 spoken gate retry if needed
Weeks 14–27ish ……… Phase 2 (hybrid ML-KEM + PKI/TLS + agility)
Week 28 ……………… Phase 2 gate + both artifacts linked from one portfolio README
Weeks 29–36ish ……… Phase 3 (KF/EKF/UKF → EuRoC/OpenVINS → PX4 SITL → MPC)
Week 37 ……………… Phase 3 gate. Three public artifacts. Stop adding phases.

If a phase slips: finish the phase’s 10/10 gate before starting the next. Do not parallelize. Do not “just peek” at OpenSSL hybrids during Phase 1. Do not “just peek” at PX4 during Phase 2. That splits the 30-hour block.

════════════════════════════════
ANTI-PATTERNS (explicit)
════════════════════════════════
• No Anki/Notion/obsidian study-log as the system. Bookmarks + spoken gates only.
• No paid cert wall (OSCP, etc.) as a Phase dependency.
• No clearance labs, no commercial AI red-team SaaS required.
• No claiming FIPS validation because you passed KATs.
• No skipping SDT measurement in Phase 1 — without ROC/threshold cost talk, the phase is a CTF hobby, not AI Security Engineer evidence.
• No swapping Phase 1/2 order without a new hiring-signal reason stronger than +268% AI Security growth.
• No pulling Phase 3 in parallel because “it is a different domain.” Hours, not domain, are the constraint.
• No Isoloom / CyberCTF/vulnerable-llm-agent fallback.
• No extra Bayes/stats course in P1-M4. The medical-test video + expected-cost-at-two-base-rates is the whole insert; Seeing Theory / Beta updating is out.
• No lattice-math unit in Phase 2. §3.2 + the Cloudflare primer, read-only, inside M2’s existing hours. No new milestone. No Regev/SIVP/QROM. Do not park “why LWE” in M5.
• No drone / lidar / Jetson / wind-tunnel shopping. That was the point of picking perception/control over aero shop work.
• No mechanical/aerospace scope creep (FEA, airfoils, engine maps, CAD as a second Deep).
• No library-only Kalman (FilterPy is the check after your NumPy matches).
• No 40 ROS packages. Humble CLI + one publisher + tf2 until P3-M9.
• No ORB-SLAM3 as the first VIO. OpenVINS first.
• No Gazebo unless jMAVSim is blocked.
• No calling SITL a flight test.
• No Palantir fusion, entity resolution, DISARM, CAN, TSN, Link-16, or H∞ as the spine.
• No training a huge vision model to “do SLAM.” Run a published VIO on a public log.
• No fourth home Deep after Phase 3’s 10/10. Hardware flight is a company resource, not the next PDF.
