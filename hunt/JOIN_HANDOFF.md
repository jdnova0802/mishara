# Handoff: what was built (paste this)

Second company is **not Nisaba / not Gate**. Quiet house stays Gate (live yes before irreversible acts). This shop is a **clutch**: a machine **will not GO** until two halves **join**, in a **live time window**, **in the gear**. Face of the object, not Palantir god-view. No people-map, no coded-threat scanner, no coin.

**Mood board (not SKUs):** harbor chain, portcullis, Colossus, Ishtar, Hero’s temple doors, tiger tally (hufu).  
**Modern bodies:** water = boom, earth = wedge/hangar doors, air = pad/chocks. Digital = two halves join. Sound = horn on seal.

**Unpluggable:** software-only ~2, bolt-on in a real go-path ~5, you-are-the-kit ~8. Never 10. Palantir ~3 (wheels still roll).

## Code (bench, laptop)

Repo folder: `join/` (does not import Gate).

- `join/pack.py` — `join-pack-v1`. Public fields: spec, what, not_before, not_after, starter_id, sealer_id. Halves are **files**, not in JSON. `join_sha256` = sha256(starter_half + newline + sealer_half + newline + canonical body). Stranger recomputes. Draft (no hash) is not go. Same id both sides = NO. Same half twice = NO. Now outside window = NO.
- CLI: `python3 -m join.pack seal <starter.half> <sealer.half> <in.json> <out.json>` then `python3 -m join.pack boom …` prints **GO** or **NO**. Toy boom. Not a PLC/ship/car.
- Tests: `python3 -m join.test_pack` (10 tests). CI: `.github/workflows/join.yml`.
- Booth UI: `python3 -m join.web` → http://127.0.0.1:8765/ — same pack. Join with two halves → GO. Blank sealer → NO (“draft is not go”).

`check/` is a **different** fail-closed pack (git/task evidence). Do not weld to this unless asked.

**Do not build:** people-maps, threat OSINT, vehicle/PLC exploits, skippable website approve, Nisaba brand sticker.

**Claude read (16–17 Sep):** mechanism is right: two halves, window, stranger hash, toy boom, not Gate, not Palantir. Agree. **Correction:** the bench is unpluggable ~2, not 8. 8 is only if we become the kit. Old city SKU still says “see people coordinating” — starve that or the distinctive thing dies. Praise is not a filing.
