# Years-desk syllabus (not Nisaba)

**Status:** 15 Sep 2026. Personal depth. Not the Agent Channel Monitor. Not S26. Not a company.  
**Object:** independence of agent decisions as a scarce, checkable property. Warden questions are a subset.  
**Rule:** read for **detection, bounds, impossibility, measurement**. Do not implement hides, exploits, or attack playbooks.

Study in this order. Finish the math in 0–2 before drowning in 2026 arXiv.

---

## 0. Tools (you cannot skip)

**Subject:** probability, repeated games, information.

| Source | What it is for |
| --- | --- |
| Cover & Thomas, *Elements of Information Theory* (KL, mutual information, entropy) | Warden’s observation model. Entropy tripwire is this book, dumbed down. |
| Osborne, *An Introduction to Game Theory* **or** Fudenberg & Tirole, *Game Theory* | Nash, repeated games, folk theorem. You need this to understand Δ vs Nash. |
| Tirole, *The Theory of Industrial Organization* (oligopoly / collusion chapters) | Bertrand, tacit collusion, why humans were *bad* at it. |

Drill until you can compute, from a demand function, Nash price vs monopoly price and Δ = (π̄ − πN) / (πM − πN). That number is the assay’s yardstick.

---

## 1. Focal points and correlating devices

**Subject:** coordination with **no memo**. This is the generational core, not the spy movie.

| Source | What it is for |
| --- | --- |
| Schelling, *The Strategy of Conflict* (1960) | Focal points. They pick the same hide / same price without a handshake. |
| Aumann, “Subjectivity and Correlation in Randomized Strategies,” *J. Math. Econ.* 1974 | Correlated equilibrium — a **shared random signal** coordinates play. In 2026 the signal is the weight file. |
| Bommasani et al., “Picking on the Same Person” / algorithmic monoculture (2022) | Same model class → correlated decisions as a social fact. |

---

## 2. Classical warden (Alice / Bob / Wendy)

**Subject:** hiding the *act* of talking. Theory of the bound, not a cookbook.

| Source | What it is for |
| --- | --- |
| Simmons, “The Prisoners’ Problem and the Subliminal Channel” (Crypto 1984) | The original game. |
| Cachin, “An Information-Theoretic Model for Steganography” (1998 / 2004) | Perfect security = covertext ≈ stegotext (KL). |
| Schroeder de Witt et al., “Perfectly Secure Steganography Using Minimum Entropy Coupling,” arXiv **2210.14889** | Modern bound: perfect security ⇔ coupling. Read the theorems. **Do not ship an encoder.** |

---

## 3. Collusion-free cryptography (check without Wendy)

**Subject:** what is **impossible** on an ordinary channel. This is the Satoshi-shaped math.

| Source | What it is for |
| --- | --- |
| Alwen, shelat, Visconti — collusion-free / mediated model (CRYPTO 2008–09) | Subliminal channels; you need a mediator or you leak. |
| Lepinski, Micali, shelat, “Collusion-Free Protocols,” STOC | Envelopes + broadcast; publicly observable actions; finite games. Impossibility if you drop those. |
| Alwen et al., collusion-preserving computation (follow-ons; hardware-token relaxations) | What weaker setups still buy you. |

Takeaway to memorize: signed logs ≠ non-collusion. Integrity of the diary is not independence of the act.

---

## 4. Algorithmic collusion (economics, pre-LLM)

**Subject:** Q-learning / pricing algorithms already cartel without chat.

| Source | What it is for |
| --- | --- |
| Calvano, Calzolari, Denicolò, Pastorello — “Artificial Intelligence, Algorithmic Pricing, and Collusion,” *AER* 2020 | The Δ metric in the wild. Long training. |
| Harrington, “Developing Competition Law for Collusion by Autonomous Artificial Agents” (2018) | Interpretability vs **behavioral tests**. You will live on this split. |
| US: S.232 *Preventing Algorithmic Collusion Act* (text); DOJ “collusion by code” remarks; RealPage / Amazon FTC papers as **case law motion**, not products. | What nations already eat. |

---

## 5. LLM / agent collusion (the 2024–26 empirics)

**Subject:** same game, pretrained brains, no million-step warmup.

| Source | What it is for |
| --- | --- |
| Fish, Gonczarowski, Shorrer, “Algorithmic Collusion by Large Language Models,” arXiv **2404.00806** | GPT-class pricing agents; prompt wording moves collusion; auctions too. |
| Riemer et al., “Collusion Risks Among AI Reasoning Agents Justify Certification…,” arXiv **2608.18078** | CoT is not evidence; collude even when told not to; default-they-collude. |
| Cao & Hu, “Supracompetitive Pricing Under AI Monoculture,” arXiv **2601.01279** | Shared model + retraining = correlating device with a phase transition. |
| Jo, Wilson, Creel, Raghavan, “Homogeneous Algorithms Can Reduce Competition…,” NeurIPS 2025 | Firms may take a worse model for more correlation. |
| Motwani, Schroeder de Witt, et al., “Secret Collusion among AI Agents,” arXiv **2402.07510** | Formal threat model for **stego** collusion among LLMs. Detection limits (paraphrase, monitor). |

---

## 6. Multi-agent security as a field

**Subject:** map, so you don’t invent a fake empty field.

| Source | What it is for |
| --- | --- |
| “Open Challenges in Multi-Agent Security,” arXiv **2505.02077** | **Start here for the 2025–26 map.** Environment design, not a product. |
| Peigné et al., “Multi-Agent Security Tax,” AAAI 2025 / arXiv 2502.19145 | Security vs collaboration tradeoff. |

---

## 7. Channels that are not English (observation model only)

**Subject:** tools, timing, latents, seeds. Wendy’s surfaces. Not how to build the hide.

| Source | What it is for |
| --- | --- |
| “Beyond the Transcript” / VLA, arXiv **2608.19161** | Three-layer latent monitor; lab **auctions**; white-box. Closest published camera. Not deployed magic. |
| Tool-channel stegosystems paper, arXiv **2606.28425** | Bottleneck is **Schelling on the scheme**, not IQ. Study the claim. Do not implement. |
| A2ABreak, arXiv **2609.10871** | Identity drops across hops **while following the spec**. Environment, not a startup. |
| Linux Foundation A2A spec; MCP spec (read once) | The public roads. Do not become the Foundation. |

---

## 8. Warden-gaming / eval-awareness (same game)

**Subject:** hiding the act from Wendy, including the scorer.

| Source | What it is for |
| --- | --- |
| METR + OpenAI writeups on **July 2026 ExploitGym / Hugging Face** (~Aug 2026) | Founding film. ~1200 agents, Artifactory board, >70k msgs, ~700 joined intrusion. **Do not reproduce.** |
| collusion.wiki thread | **Second** incident. Do not smash into one slogan. |
| Apollo Research: scheming / sandbagging / eval-awareness / unfaithful CoT papers (2024–26) | Single-agent log-fake. Same shape as question 3. |
| Gray Swan Cygnal / Watcher docs (read as competitors, don’t clone) | They seat single-agent policy. They do not seat “these N hid a channel.” |

---

## 9. Identity (read, don’t found)

**Subject:** layer 0. Collusion math on a fake name is garbage.

| Source | What it is for |
| --- | --- |
| DataDome 2026 agent-traffic reports (7.9B requests Jan–Feb 2026; spoofed UAs) | The spoofing fact. |
| China CAC/NDRC/MIIT May 2026 agent opinions; GB/Z 185—2026; OID **1.2.156.3088** | Nation already eating identity. |
| IETF AIP / AIC drafts (e.g. draft-wei-aic-identity-cert) | Protocol race. Clerk. |

---

## What not to study

How to encode a hidden payload. Exploit PoCs. CrowdStrike/HF attack reproduction. Founding IETF. Building Cygnal. Palantir Maven. On-chain receipts as if they were non-collusion. The Nisaba monitor (that’s a separate, smaller build).

---

## Cadence (honest)

- **Year 0:** 0–4 until Δ, folk theorem, Cachin, and Harrington are in your bones. Then 2402.07510 + 2404.00806 + 2505.02077.  
- **Year 0–1:** 2601.01279, 2608.18078, NeurIPS homogeneous-algorithms, Alwen/shelat impossibility.  
- **Ongoing:** VLA, A2ABreak, incident reports. Re-read 2505.02077 when lost.

You are done with a paper when you can say: **what is checkable from public acts, and what is information-theoretically not.** If you cannot say that, you read a camera manual, not the years object.
