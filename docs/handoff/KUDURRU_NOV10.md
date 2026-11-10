# CURSOR HANDOFF — Kudurru layer (Nov 10 2026)

Full overnight paste (verbatim): [`nisaba-cursor-handoff.md`](nisaba-cursor-handoff.md). This file is the live-check overlay only.

Sixth brand: **Kudurru** — consumer-facing proof object. Erra / Velaru / Verra / Gate / Mishara remain backend doctrine. Design law: **the flex object and the proof object are the same artifact.** A Kudurru card’s claim hashes ordered `underlying_receipt_ids`; it is not a vanity checkmark.

Machine-readable schemas: `docs/kudurru/schemas/`.
Compiled TypeScript for items 132/133: `nisaba-132-133/` (`tsc --strict`, `npm test`).

Do **not** rebuild the Claude artifacts (`nisaba-visuals.html`, `kudurru-card.html`, Live Restraint Map). URLs stay with those artifacts.

## Item 100 — PR split

This PR is **synthesis + Kudurru spec only**. It does not weld bugs 1–11, CDPI math, DFIR receipt fields, or marketing frontend.

## Live check of bugs 1–11 (Nov 10, America/New_York)

Probed from this agent. Not a reconstruction of the overnight transcript.

| # | Claim | Live (this repo / public hosts) |
|---|--------|----------------------------------|
| 1 | 502 on `https://velaru.xyz/` | **Not 502.** `302` → `/insurance` then `200`. |
| 2 | 502 on `/docs` | **Not 502.** `https://velaru.xyz/docs` `200`; `https://gate.velaru.xyz/docs` `200`. |
| 3–6 | Six Bind Room verticals + `/demo/bind-room` | **Not in this repo.** `GET /demo/bind-room` on Gate is `404`. `gate/bind_room.py` is the Colorado/SERFF officer pack. No Reinsurance/Clinical/Board/Fleet/Grid/Counsel demo labels in `origin/main`. |
| 7 | Verra retired vs live Bind Room | `https://velaru.xyz/verra` `301`. Gate `/trust/corrections` `404`. Contradiction lives on the Velaru site, not this checkout. |
| 8 | Stale “Last restraint feed” on `/check` | `https://velaru.xyz/check` `200` (heading present). Feed freshness is a Velaru-site job. |
| 9 | Four names for a $49 SKU | Not in `origin/main` commerce files (those live on other branches). Do not invent a new ladder here. |
| 10 | Cmd+K alias `vertical` | No command palette in this repo. |
| 11 | `/compliance/mandate-registry` → `/insurance` | Gate path is `404`. Velaru `/insurance` is the marketing bind-gate page. Registry is not in this checkout. |

Items 1–11 that still reproduce are **on velaru.xyz / a separate frontend**, not Gate’s officer pack. Fix them in the Velaru deploy, not by inventing a six-vertical demo in mishara.

## Items 109–124 — recovery

No prior Cursor agent in this environment logged verbatim 109–124 (cloud-agent list since 2026-11-09: empty). This repo had no Kudurru files. The schemas below are **the overnight session’s own paste**, not a second reconstruction. Item 117 is the batch header for 118–122; there is no separate 117 schema.

## Signing custody (item 142)

Public Gate signing today is `GATE_RECEIPT_PRIVATE_KEY` (Ed25519, Render env, online). That is **single-credential custody**, not HSM M-of-N. This PR does **not** rotate receipt keys. Quorum/HSM is an ops decision, not a code merge.

## Sequencing (do not invert)

- 132 + 133 before 134, 137, 139.
- 136 is standalone (ATLAS field on a receipt).
- 140 consumes 134 + 137.
- 111 `staleness_window_ms`, 118 threshold curve, 133/135 baselines: **tune on live traffic**, never hardcode a demo number.
- Not build-now: 49 (underwriter), 55 (industry standard), 38/45/47/48 (CV models), 51 (ZK).

## Open design calls (do not pick in code)

- 129 streak: hard-reset vs severity-decay vs Chess.com 2-day grace.
- 133 baseline: mean/stddev (simple, outlier-masking) vs median+MAD. The 132/133 demo **keeps mean/stddev** and documents the mask; do not “fix” the demo to hide it.
- 126–128 (rate card, billing dispute, fee-split): named, not schema’d.
