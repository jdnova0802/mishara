# Four-pillar gap analysis

Pull date **18 Nov 2026**. Layers are separate. A gap is named (paper, issue, spec note) or it is not listed. Textbook-settled items are labeled **settled** so they are not mistaken for work.

---

## 1 — ML-KEM in a real codebase

### Field

**Settled.** FIPS 203 (13 Aug 2024) is the algorithm: ML-KEM-512/768/1024, Module-LWE, FO transform, implicit rejection. Re-implementing Kyber from the round-3 spec is re-deriving something NIST already froze. KyberSlash (secret-dependent `div` by `q=3329` in `poly_tomsg` / `poly_compress`) is **settled as a bug class**: Bernstein, Bhargavan, Bhasin, Chattopadhyay, Chia, Kannwischer, Kiefer, Paiva, Ravi, Tamvada, TCHES 2025(2):209–234, CHES 2025 Best Paper. Reference C and liboqs were patched (liboqs 0.10.1, 7 Jun 2024, pulls pq-crystals commits `0264efac` / `9b8d3069`).

**Frontier (named).**

- NIST CSRC FIPS 203 page, planning note **17 Nov 2025**: an issue will be corrected in a future update; details in the “Errata (potential updates)” spreadsheet on `https://csrc.nist.gov/pubs/fips/203/final`. Implementations that claim FIPS 203 without tracking that spreadsheet are behind the spec, not ahead of it.
- Groups still publishing **implementation** (not algorithm) work: Cryspen / INRIA (libcrux, hax/F*), PQ Code Package (mlkem-native, HOL Light), AWS-LC, Open Quantum Safe. RWC 2025 talk: Bhargavan, Erbsen, Franceschino, Kiefer, van der Merwe, “Using Formally Verified Post-Quantum Algorithms at Scale” (slides: `https://cryspen.com/post/rwc-2025/RWC_2025_Slides.pdf`) — remaining work they name is **ML-DSA**, C extraction size, API/alignment for NSS/BoringSSL/OpenSSH, not a new KEM.
- Unsolved in the **software production** sense: connecting HOL Light / F* proofs to **physical** leakage. mlkem-native `SOUNDNESS.md` B4 states transient faults and fault injection are **outside the formal model**; no redundant computation is implemented. That is an explicit scope hole, not a missing textbook chapter.

**Ahead vs re-derive.** Writing another portable ML-KEM-768 that matches KATs is re-derivation. Tracking the Nov 2025 FIPS 203 errata into mlkem-native KATs/ACVP, or extending proofs past ISA-faithful hardware (`SOUNDNESS.md` B4), is not.

### Code

| Tree | Role | Named, dated weakness |
|------|------|------------------------|
| `pq-code-package/mlkem-native` | Default ML-KEM in libOQS ≥ 0.13.0, AWS-LC ≥ v1.50.0 | README (post PR **#1685**, merged 9 May 2026): **power/EM, microarchitectural (speculative), fault injection out of scope**. `SOUNDNESS.md`: no fault-detection checks. Issue **#1921** (open 25 Sep 2026): portable C **assumes constant-time 32×32 multiply**; cores with early-terminating MUL are not covered. Issue **#1939** (open 13 Oct 2026): `rej_uniform_avx2_asm` needs **BMI2 and POPCNT** but only AVX2 is checked. Issue **#1842** (open 3 Aug 2026): ACVP **keyless `decapsulationKeyCheck` workaround** until past ACVP v1.1.0.43. Issue **#1820** (open 1 Aug 2026): RISC-V **VLEN=128 native NTT missing**. Issue **#1932** (soundness, 5 Oct 2026): CBMC does not yet check **relative alignment of pointers passed to assembly**. |
| `cryspen/libcrux` (`libcrux-ml-kem`) | Verified Rust, SIMD backends | Issue **#1200** (open 6 Oct 2025): `generate_key_pair` takes randomness **by value**, blocking `Zeroize`; decaps is infallible (FO implicit reject) and that is under-documented. Issue **#1483** (`libcrux-secrets`, later): `Secret<T>` `Add`/`Sub` not sealed — a user-defined `T` can be variable-time. Issue **#1299** is **ML-DSA**, not ML-KEM — do not treat it as an ML-KEM gap. PR **#1480** (open Jun 2026): hacspec/F*/Lean spec for ML-KEM **not merged**; comments note docs still citing **FIPS 203 draft** in places. |
| `open-quantum-safe/liboqs` | Integration / OQS-provider | KyberSlash portable C: **fixed in 0.10.1 (7 Jun 2024)**. Remaining work is **wrapping** mlkem-native, not a second KEM. |
| `mupq/pqm4` | Cortex-M4 attack target | The TCHES 8592 / 10289 target. Not a production tree. |

**Ahead vs re-derive.** A first KAT-green build of mlkem-native is settled homework. Closing **#1939** (feature-bit vs ISA), **#1921** (MUL latency), **#1842** (ACVP workaround), or adding **fault detection** the README currently refuses, is engineering the trees have left open.

### Media

**Covered.** CHES 2025 Best Paper (KyberSlash). RWC 2025 Cryspen/PQCA verification talk. RWC 2026 (Taipei, 9–11 Mar 2026) is the live venue, not a new algorithm. PQCP GitHub issue tracker is the working conversation.

**Quiet.** Production C (mlkem-native / AWS-LC) **masking**. Hardware papers exist (HOPE-MLKEM, TCHES `https://tches.iacr.org/index.php/TCHES/article/view/12889`, 23 Apr 2026; Buschkowski et al. ePrint **2026/1265**, RUB, 16 Jun 2026 / rev 16 Oct 2026). Those do **not** show up as mlkem-native issues. The gap is **software-tree masking**, not another KyberSlash write-up.

---

## 2 — Implementation-security attack / harden

### Field

**Settled.** Chosen-ciphertext + EM/power → plaintext-checking oracle on FO KEMs: Ravi, Roy, Bhasin et al., TCHES 2021, `https://tches.iacr.org/index.php/TCHES/article/view/8592` (pqm4, Cortex-M4). Parallel PC-oracle: Rajendran, Ravi, **D’Anvers (COSIC)**, Bhasin, Chattopadhyay, TCHES 2023, `https://tches.iacr.org/index.php/TCHES/article/view/10289`. CPA on unprotected NTT is textbook for eShard’s STM32 demo.

**Frontier (named).**

- **Fine-shuffling is broken.** Ait Manssour, Ben El Haj Soulami, Duquesne, Fumaroli, ePrint **2026/934** (Valeo / Rennes): template attack on Ravi et al. 2020 bitwise-fine-shuffling (aggregate 16 ANDs of the swap mask), STM32F303; they propose **first-order masked fine-shuffling**, proven in the probing model, **25%** overhead on ML-KEM-768 decaps vs **51%** for the defeated bitwise variant.
- **NTT refresh vs mask+shuffle.** Bronchain et al. (style): TCHES “Keep it Simple: Refreshing the NTT of Kyber’s Decapsulation…”, `https://tches.iacr.org/index.php/TCHES/article/view/12690` — shuffling alone theoretically weak vs PC-oracles; masking alone starved of noise on cheap MCUs; they refresh NTT layers with linear-overhead gadgets and show BP does not propagate. Evaluation gap they name: **lazy reduction** makes profiling of asm NTT unlike the leaky reference C NTT.
- **Hardware high-order masking.** HOPE-MLKEM (TCHES 12889). HADES mixed-domain masking, ePrint **2026/1265** (RUB: Buschkowski, Hoeher, Sasdrich, Güneysu), TVLA 10M traces first- and second-order on FPGA.
- **Blinding.** Duparc (EPFL) + Taha (Nagra), ePrint **2025/181**, NTT + CRT/RNR blinding vs SASCA and faults.
- Groups: COSIC (Gierlichs, Verbauwhede, D’Anvers), NTU/Temasek (Ravi, Bhasin), RUB CASA (Güneysu), Valeo (Fumaroli), NXP+Keysight (ML-DSA Inspector eval, 22 Jul 2025 Keysight newsroom).

**Ahead vs re-derive.** Replaying TCHES 8592 on pqm4 is a lab exercise. Reproducing **2026/934** against a **masked** NTT in a tree that currently has **zero** masking (mlkem-native README), or showing NTT-refresh (TCHES 12690) on **lazy-reduction asm**, is not.

### Code

| Artifact | Specific hole |
|----------|----------------|
| mlkem-native | No SCA/FI countermeasures by charter (README after **#1685**, 9 May 2026). Hardening that tree *is* the gap. |
| pqm4 | Still the paper target; not a hardened product. |
| eShard platform | Published **CPA on NTT multiply, ML-KEM on STM32** (`https://www.eshard.com/side-channel`). Training: PQC 2-day, exercises 1–2 = CCA SCA on Kyber decrypt + FI on keygen (`https://www.eshard.com/pqc-physical-security-training`). |
| Keysight Inspector | Pre-release **ML-KEM** eval (Keysight–NXP note 22 Jul 2025 is **ML-DSA**; ML-KEM is listed as pre-release). Gap: public ML-KEM Inspector recipes vs AES/DES courses. |
| HOPE-MLKEM | Open hardware masked ML-KEM (TCHES 12889). Not wired to mlkem-native C. |

### Media

**Covered.** CHES 2025 posters: Chinbat, Wu, Zhang, “Coefficient Classification Template Attack on the NTT Accelerator for ML-KEM” (`https://ches.iacr.org/2025/acceptedposters.php`). eShard and Keysight **sell** the AES-then-PQC training path. COSIC Course 22–25 Jun 2026 (`https://www.esat.kuleuven.be/cosic/events/cosic-course/`).

**Quiet.** Transfer of **2026/934** (masked fine-shuffle) and **TCHES 12690** (NTT refresh) into **mlkem-native / AWS-LC**. Vendor blogs stop at “we support PQC eval.” No public CTF currently owns ML-KEM FI the way CHES CTF owns AES — KyberSlash has a **browser lab** (`https://systemslibrarian.github.io/crypto-lab-kyberslash/`) which is pedagogy of a **patched** bug, not a live contest.

---

## 3 — One grid protocol + hand-written detections

Default protocol in the locked roadmap: **IEC 61850** (MMS + GOOSE). DNP3/Modbus/ICCP are named only where they have a distinct, cited hole.

### Field

**Settled.** GOOSE is multicast Ethernet, ethertype `0x88b8`, `stNum`/`sqNum` sequencing, 3 ms trip budget (IEC 61850-5). Integrity/authenticity for GOOSE is **IEC 62351-6:2020** (HMAC-SHA-256 or AES-GMAC). Unauthenticated GOOSE spoofing is a twenty-year demo, not a 2026 discovery.

**Frontier (named).**

- **62351-6 vs 3 ms on real IEDs.** International Journal of Critical Infrastructure Protection, **26 Sep 2026**, DOI `10.1016/j.ijcip.2026.100907`: TEE + 62351-6; claim AES-128-GMAC authenticated frame generation stays inside the 3 ms budget. Unsolved in the field: **deployment on shipped IEDs**, not the paper’s lab TEE.
- **Process-aware detection, not just `stNum`.** IEEE CSR 2025 (4–6 Aug 2025), IEEE Xplore `11130060`: GOOSE **masquerade** detection using **relay-local RMS and phase angle** vs protocol payload. Network-only `stNum` rules miss consistent physical forgeries.
- **MMS process disruption.** arXiv **2601.03690** (2026): MMS field–value pairs on the **EPIC** testbed; attacks via **libiec61850** and IEC61850Bean; maps to NERC CIP-005-7 R1 Part 1.5. Named CVE in that paper: **CVE-2025-0814** (Schneider MMS DoS).
- **GOOSE AEAD / nonce.** Polepaka et al. 2025, Zenodo `10.5281/zenodo.21556976`, “Complete Security Design for IEC 61850 GOOSE: ASCON-AEAD128, Nonce Construction, and Replay Protection” — filed as libiec61850 **#604–#607** (25 Jul 2026). This is the current design argument against the library’s counter-based replay check.
- SANS ICS paper 26 Jan 2026, “Defensible IEC 61850 Substation Network Security Monitoring with Zeek” (`https://www.sans.edu/cyber-research/defensible-iec-substation-network-security-monitoring-zeek`): L2 invariants (MAC/VLAN/multicast/rate). Useful, but it is a **master’s/SANS** packaging of invariants, not a new protocol result.

**Ahead vs re-derive.** A Suricata rule `stNum` goes backward is settled. Combining **IEEE CSR 2025** physical RMS/angle with **icsnpp-iec61850-goose** logs, or closing the **Polepaka replay semantics** in a stack that still delivers replayed APDUs to listeners, is not.

### Code

| Tree | Named issue (date) |
|------|---------------------|
| `mz-automation/libiec61850` | **#607** (25 Jul 2026, open): `parseGoosePayload` **fires the subscriber listener even when replay sets `isValid=false`**. Examples do not check `GooseSubscriber_isValid()`. **#606** (same day): replay is `if (stNum==) sqNum>=`; **cross-`stNum` replay skips `sqNum`**. **#605**: `stNum`/`sqNum` BER encoding → **nonce collision**. **#626** (12 Nov 2026): R-Session **HMAC-SHA256-80 defined but not encoded or verified**; `createHMAC` ignores `hmacMaxSize` (writes 32 bytes, overflow on HMAC-128); **MAC compare is `memcmp`**. **#629** (12 Nov 2026): R-Session **no replay protection** for received SPDUs. **#624**: APDU length two octets too long; stack **refuses its own SPDUs**. **#611/#610** (3 Aug 2026): MMS client parsers **read past declared length** / missing `bufPos < maxBufPos`. **#620** (20 Oct 2026): NULL deref in `enqueueReport` when RCB dataset deleted. README: **PRs not accepted** on GitHub (CLA/email) — #626’s author had to publish a fork patch. |
| DINA `icsnpp-iec61850-goose` | GOOSE → `goose.log`. |
| DINA `icsnpp-mms` + TPKT/COTP/SESS/PRES/ACSE | Current MMS path. Archived `icsnpp-iec61850-mms` is **wrong**. Zeek discussion **#4752**: MMS plugin **still missing message types**; “current state has not yet been pushed to the main branch.” |
| `opendnp3` / IEEE 1815 | Only if the yard is DNP3; not the 61850 hole. |
| Modbus V1.1b3 | Spec is frozen; not a research surface for this track. |
| ICCP | Parser: `DINA-community/icsnpp-iccp`. Secondary to 61850. |

### Media

**Covered.** IEEE CSR, SANS ICS, CISA ICS advisories, vendor 62351 slideware, Black Hat ICS talks on unauthenticated GOOSE (legacy).

**Quiet.** libiec61850 **#607/#606/#626/#629** — filed, open, not a conference talk. R-GOOSE/R-SV (IEC 61850-8-1 R-Session) security is being patched in issues from **12 Nov 2026**, not in SANS PDFs. icsnpp-mms **incomplete main-branch** is a Zeek discussion, not a product blog.

---

## 4 — Defense-only autonomous AI security

Offense (jailbreak leaderboards, GCG, AgentDojo attack papers as an end in themselves) is out of scope. Defense at the **tool/spend boundary** is in.

### Field

**Settled.** Prompt-injection as an input-classification problem; OWASP LLM Top 10; “add a system prompt.” That is textbook 2023–24.

**Frontier (named).**

- **Action-level causal attribution, not input filters.** He, Zhu, Li, Shao, Yao, Liu, Qin, **AttriGuard**, USENIX Security 2026, Baltimore, pp. 1547–1566, `https://www.usenix.org/conference/usenixsecurity26/presentation/he-yu`. Parallel counterfactual re-execution; 0% ASR on static IPI in their setting. Open problem they leave: **cost of shadow replay** on production agents, and adaptive attacks on the survival criterion.
- **Authorization outside the model.** AgentCap, arXiv **2611.00729** (Nov 2026): MCP wrapper, short-lived budget-bounded capability tokens, policy over trust / workflow / mutually exclusive authority / argument provenance. Claim: action selection stays in the model; authority does not. Gap they attack: **standing tool credentials**.
- **SoK.** Kim et al., USENIX Security 2026, “SoK: Attack and Defense Landscape of Agentic AI Systems,” `https://www.usenix.org/system/files/usenixsecurity26-kim-juhee-agentic.pdf`. Open challenges they name in §5: privilege separation evaluated only on **simplified IPI**, not web/FS/DB; **formal methods vs stochastic policies** (“security properties of agents that interact with web/FS/mobile remain underspecified”).
- OWASP **Top 10 for Agentic Applications 2026** (ASI, Dec 2025 PDF on genai.owasp.org) and **AI Agent Security Cheat Sheet** (`https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html`): “Tool Authorization Middleware” — approval must be bound to **exact tool call**, consumed atomically, fail-closed. This is a **requirement list**, not an implementation.

**Ahead vs re-derive.** Another classifier for “is this prompt injection?” is crowded and SoK-covered. A **deterministic gate** on tool/spend (AgentCap’s split: propose vs authorize) with **replay-protected, single-use** tokens is the paper-level gap that production MCP servers have not absorbed.

### Code

| Artifact | Specific hole |
|----------|----------------|
| MCP servers in the wild | Standing API keys; no per-invocation capability object as in AgentCap. |
| OWASP cheat sheet | Specifies atomic consume-before-execute; **no reference implementation** in the sheet. |
| AgentCap (paper) | Evaluation on AgentDojo / InjecAgent — **not** a production payments or ICS tool bridge. |
| AttriGuard | Research prototype; **2× agent execution** cost class. |
| Gate `/v1/act` (this repo, owned-write) | Clearance vs invoke is the same **propose/authorize** split. It is **not** wired as a general agent-tool capability kernel, and default `write_executed=false`. Treat as an existence proof of the *shape*, not a completed agent-security product. Line-by-line vs AttriGuard / AgentCap / OWASP: `docs/study/ACT_VS_AGENTCAP_ATTRIGUARD.md`. |

### Media

**Covered.** USENIX Security 2026 (AttriGuard, agent SoK). OWASP ASI 2026 Top 10. Vendor “agent guardrails” blog posts (input filters, DLP).

**Quiet.** Binding **capability tokens to card-authorization / x402 / MCP tools** with stranger-verifiable receipts. Papers stop at AgentDojo. Payments and IEC 61850 operate/GOOSE are not in those benchmarks. That join — **defense-only, pre-execution, exact-call bind** — is named in OWASP’s middleware paragraph and unimplemented in the public agent stacks those papers measure.

---

## What not to spend years re-deriving

| Looks like depth | Already settled |
|------------------|-----------------|
| Portable ML-KEM-768 from FIPS 203 | FIPS 203 + mlkem-native KATs |
| KyberSlash write-up | TCHES 2025 Best Paper; patched in liboqs 0.10.1 |
| Unprotected pqm4 PC-oracle | TCHES 8592 (2021) |
| `stNum` decreased ⇒ alert | IEC 61850-8-1 sequencing, every ICS 101 |
| Prompt-injection classifier | OWASP LLM Top 10 / SoK 2026 |

## Where this track is still open (one line each)

1. **mlkem-native #1939 / #1921 / SOUNDNESS.md B4** — ISA flags, MUL latency, no FI.  
2. **ePrint 2026/934 + TCHES 12690 into a production C/Rust tree that has no masking.**  
3. **libiec61850 #607 / #606 / #626 / #629** — listener-on-replay, cross-`stNum` replay, R-Session HMAC-80 and no SPDU replay.  
4. **IEEE CSR 2025 physical GOOSE check + icsnpp-goose**, not another `stNum` rule.  
5. **AgentCap/AttriGuard-class authorize-at-tool-boundary on a real mouth (spend or `Operate`), not AgentDojo.** Smallest Gate step: exact-call bind + consume-once (`ACT_VS_AGENTCAP_ATTRIGUARD.md` §2). No AgentDojo ASR on `/v1/act` yet (§3).
