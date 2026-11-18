# Four-pillar mastery — reference roadmap

Locked sequence. Software engineering is not a fifth pillar: C/CMake (and later Rust/Spicy) is how every checkpoint is proven. Horizon **8–12 years**. Checkpoints are binary: you can show the artifact or you cannot. No journal required.

| Phase | Years on the 8–12 clock | Bottleneck |
|-------|-------------------------|------------|
| 1 ML-KEM in a real tree | 0–3 | Merged non-docs work |
| 2 Attack / harden that binary | 2–6 | Lab access (paid or COSIC) |
| 3 One grid protocol | 3–8 | Spec + a live stack, not a blog |
| 4 Hand-written detections | 5–12 | Rules that fire on captures you did not author |

Overlap is expected. Do not start phase 3 until phase 1 has a merged artifact. Do not call phase 2 done because you watched a talk.

---

## 1 — Implement ML-KEM in a real codebase

**Pick one tree and stay in it.** Default: **mlkem-native** (C90, already the default ML-KEM in libOQS ≥ 0.13.0 and AWS-LC ≥ v1.50.0). Use **libcrux-ml-kem** only if the work is Rust + formal/secret-independence. Use **liboqs** only as the integration surface after the native tree.

| Item | Specific |
|------|----------|
| Spec | NIST **FIPS 203** (final 13 Aug 2024), PDF `https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf`. Errata spreadsheet on `https://csrc.nist.gov/pubs/fips/203/final`. Work **ML-KEM-768** first (FIPS 203 §8, parameter set in Table 2). |
| Code | `https://github.com/pq-code-package/mlkem-native` — build, KATs, and a first issue labeled for newcomers or a failing backend. README names the consumers (libOQS, AWS-LC, rustls via AWS-LC). |
| Alternate tree | `https://github.com/cryspen/libcrux` crate `libcrux-ml-kem` (docs: `https://docs.rs/libcrux-ml-kem`). Feature `check-secret-independence`. |
| Integration tree | `https://github.com/open-quantum-safe/liboqs` — only after a native change needs an OQS wrapper/test. |
| Do not start here | A from-scratch Kyber in a gist. pqm4 (`https://github.com/mupq/pqm4`) is the **attack** target in phase 2, not the production tree. |

**Done when all of these are true:**

1. You can derive, from FIPS 203 only, the byte sizes of `ek`, `dk`, `c`, `K` for ML-KEM-768 and where the Fujisaki–Okamoto re-encryption sits in `ML-KEM.Decaps`.
2. `mlkem-native` (or libcrux) builds on your machine; official KATs pass.
3. A **non-documentation** change is merged upstream (constant-time, backend, KAT, UB, or API). PR URL is the checkpoint.
4. You can point at the NTT / `mlk_rej_uniform` / FO transform in that tree and say what a timing leak there would mean for decaps.

**Time:** 18–36 months of engineering inside years 0–3. If nothing is merged by month 24, you are still reading.

---

## 2 — Attack and harden *that* implementation

The target is the binary from phase 1 (or pqm4’s ML-KEM on Cortex-M4 if the native tree is not yet on a probe). Labs named in the lock: **COSIC, eShard, Keysight**. They are not interchangeable.

| Item | Specific |
|------|----------|
| Paper (start before paying) | Ravi, Roy, Bhasin, et al., **“Generic Side-channel attacks on CCA-secure lattice-based PKE and KEMs,”** TCHES 2021(3). `https://tches.iacr.org/index.php/TCHES/article/view/8592`. Chosen-ciphertext + EM → plaintext-checking oracle on pqm4 Kyber. This is eShard exercise 1’s ancestor. |
| COSIC paper with Leuven on the byline | Rajendran, Ravi, **D’Anvers (COSIC)**, Bhasin, Chattopadhyay, **“Pushing the Limits of Generic Side-Channel Attacks on LWE-based KEMs,”** TCHES 2023. `https://tches.iacr.org/index.php/TCHES/article/view/10289`. Parallel PC-oracle on Kyber. |
| COSIC teaching | KU Leuven **B-KUL-H0E85A Hardware Security**, Ingrid Verbauwhede / Benedikt Gierlichs. Syllabus: `https://onderwijsaanbod.kuleuven.be/syllabi/e/H0E85A`. Practica H0E86a. This is the course; the **Security Evaluations Lab** (`https://www.esat.kuleuven.be/cosic/cosic-research/embedded-security-team/`) is PhD or industrial, not a MOOC. |
| COSIC short course | **COSIC Course on Cryptography and Cybersecurity**, Leuven, 18th edition **22–25 June 2026**. `https://www.esat.kuleuven.be/cosic/events/cosic-course/`. Embedded-security day is the relevant slice, not the whole brochure. |
| eShard (ML-KEM on the syllabus) | **PQC Physical Security Training**, 2 days, SCA + fault on **ML-KEM and ML-DSA**. Exercise 1: SCA chosen-ciphertext on Kyber decrypt/decompress. Exercise 2: FI on Kyber keygen. Page: `https://www.eshard.com/pqc-physical-security-training`. Platform: esDynamic / Insight; they publish **CPA on NTT multiplication, ML-KEM on STM32** at `https://www.eshard.com/side-channel`. |
| Keysight | **Inspector Essential Side Channel Analysis**, 3 days / 3 courses (acquisition, DPA/CPA on DES/AES, EM + countermeasures). `https://www.keysight.com/us/en/products/services/device-vulnerability-analysis-services/security-training/inspector-side-channel-analysis-training.html`. PQC: Keysight Inspector **pre-release ML-KEM** support, NXP ML-DSA eval write-up 22 Jul 2025: `https://www.keysight.com/us/en/about/newsroom/featured/2025/0722-keysight-supports-post-quantum-cryptography-evaluation.html`. |
| Device for homework between paid weeks | pqm4 on STM32F4; same class of target as TCHES 8592. |

**Done when all of these are true:**

1. You can explain, without notes, why IND-CCA does **not** stop a PC-oracle built from FO-transform leakage (TCHES 8592).
2. You have sat **one** of: eShard PQC 2-day, Keysight Inspector Essential 3-day, or COSIC H0E85A / Evaluations Lab time. Certificate or lab notebook with traces is the artifact.
3. You recover a key (or a documented failure with traces) from **ML-KEM decaps** — pqm4 or your phase-1 binary — via CPA or a PC-oracle, not from a tutorial AES.
4. You land a hardening change (masking, shuffling, FO blinding, or a rejected-ciphertext path) and re-run the same attack. “Done” is the **delta**, including what still works.

**Time:** 2–4 years inside years 2–6. The paid weeks are days; the years are traces, masking, and a second attack after the patch. If you cannot get Inspector or eShard, COSIC course + H0E85A is the academic path; do not substitute a YouTube CPA on AES.

---

## 3 — One grid protocol

**Lock one.** Default for detections in phase 4: **IEC 61850** (MMS + GOOSE). Swap to **IEEE 1815 DNP3** only if the plant you can actually touch is US/NERC. Modbus is too thin as the *only* protocol for a decade. ICCP/TASE.2 is the control-center overlay; learn it after 61850 or DNP3, not instead.

### Default fork — IEC 61850

| Item | Specific |
|------|----------|
| Overview (free-ish) | IEC **TR 61850-1** (introduction). Buy or library. Do not use vendor marketing as the model. |
| Object model | **IEC 61850-7-2** (ACSI) + **61850-7-4** (compatible logical-node classes). You must be able to name `XCBR`, `CSWI`, `GGIO`, and a report-control block. |
| Wire | **IEC 61850-8-1** (MMS + GOOSE mapping) and **61850-9-2** (SV) if the yard uses sample values. |
| Security | **IEC 62351-3** (TLS) and **62351-6** (GOOSE/SV). Unauthenticated GOOSE is the detection gold in phase 4. |
| Code | `https://github.com/mz-automation/libiec61850` — C99 client/server, GOOSE, SV, examples, TLS. Run `server_example_basic_io` against `client_example1` on loopback, then GOOSE publisher/subscriber on a tap. |

### Alternate fork — DNP3 (only if the yard is DNP3)

| Item | Specific |
|------|----------|
| Spec | **IEEE Std 1815-2012** (DNP3). |
| Code | `https://github.com/dnp3/opendnp3` (or step-up `https://github.com/automatak/dnp3`). Outstation + master on loopback; unsolicited analog + binary. |
| Security | DNP3 SA (IEEE 1815-2012 Vol. 2 / IEC 62351-5 family). |

### Named but not the decade

| Protocol | Start only if 61850/DNP3 is already closed |
|----------|---------------------------------------------|
| Modbus | Modbus Application Protocol **V1.1b3**, `https://www.modbus.org/docs/Modbus_Application_Protocol_V1_1b3.pdf`. Too little semantics for “mastery.” |
| ICCP/TASE.2 | **IEC 60870-6-503 / -802**. Parser later: `https://github.com/DINA-community/icsnpp-iccp`. |

**Done when all of these are true (61850 fork):**

1. You can sketch, from 7-2/8-1, a trip: `CSWI` operate → `XCBR` position → GOOSE `stNum` increment, without looking it up.
2. libiec61850 examples run; you have a pcap of **your** GOOSE and **your** MMS associate/identify/read.
3. You can say what 62351-6 adds to a GOOSE PDU and what a replay of `stNum`/`sqNum` looks like on the wire.
4. You have stood the same stack against one second IED or a second open implementation (not only the example binary).

**Time:** 2–4 years inside years 3–8. Spec literacy is months; a second device and 62351 are the years.

---

## 4 — Hand-write detections against that protocol

Do not start from a Sigma pack. Start from the pcaps in phase 3 and the parsers below. The skill is **writing the predicate**, not enabling a plugin.

| Item | Specific |
|------|----------|
| GOOSE parser | DINA **icsnpp-iec61850-goose** (Spicy/Zeek). `https://github.com/DINA-community/icsnpp-iec61850-goose`. Ethertype `0x88b8`. Log: `goose.log`. |
| MMS stack | Current: **icsnpp-mms** + TPKT/COTP/SESS/PRES/ACSE. Index: `https://github.com/DINA-community/ot-parsers`. Do **not** use archived `icsnpp-iec61850-mms`. |
| DNP3 fork | Zeek built-in DNP3 analyzer + ICSNPP extras if you locked IEEE 1815. |
| ATT&CK | MITRE **ATT&CK for ICS**, technique **T0801 / T0836 / T0831** family (block command, modify parameter, spoof reporting). Map each rule to one technique ID. `https://attack.mitre.org/matrices/ics/` |
| Field reports | CISA ICS advisories tagged 61850/GOOSE/MMS — use as *false-positive teachers*, not as the rule source. |

**Rules you write yourself (61850 fork). Each needs a pcap that fires and a pcap that must not:**

1. GOOSE with **no** 62351-6 HMAC on a LAN that claims 62351.
2. `stNum` jump backward or `sqNum` reset without `stNum` bump (replay / inject).
3. MMS `Write` to `XCBR` / `CSWI` from an IP not in the SCL-allowed clients.
4. MMS initiate without TLS (62351-3) on a subnet that requires it.
5. GOOSE APPID / `goID` not in the SCD (unknown publisher).

**Done when all of these are true:**

1. Zeek with the DINA GOOSE (and MMS if you claim MMS) plugin logs your phase-3 pcaps.
2. Five detections exist as **your** Zeek scripts or Suricata rules, each mapped to an ATT&CK-ICS ID, each with a hit pcap and a miss pcap.
3. At least one rule is revised after a false positive on a capture you did not generate (public 4SICS / lab pcap, or a second IED).
4. You can disable the DINA parser and still explain the GOOSE header bytes the rule keys on.

**Time:** 3–6 years inside years 5–12. The first rule is a weekend. Surviving a foreign pcap is the career.

---

## How the four lock

```
FIPS 203 ──► mlkem-native PR ──► that binary on a probe
                                      │
                                      ▼
                         TCHES 8592 / eShard / Inspector / H0E85A
                                      │
                                      ▼
                         harden, re-attack, keep the delta
                                      │
                         (SE still: C, build, CI, patches)
                                      │
                                      ▼
              IEC 61850-8-1 + libiec61850  (or IEEE 1815 + opendnp3)
                                      │
                                      ▼
              icsnpp-iec61850-goose + five hand-written predicates
```

If a checkpoint is skipped, the next phase is sightseeing. Re-run this file against the artifacts, not against hours logged.

Named Field / Code / Media gaps (what is still open vs already settled) live in `docs/study/FOUR_PILLAR_GAP_ANALYSIS.md`. Use that file to pick work; use this file to sequence it.
