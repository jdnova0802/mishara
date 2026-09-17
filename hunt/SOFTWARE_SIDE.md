# Software side (not Palantir glass)

Physical kit: boom, wedge, pad. Software is **not** a map of people. Software is the **tiger tally** — two halves, a live window, draft ≠ go. If they can skip the software and the hull still moves, you are a 2.

---

**What we build (software):**

1. **The join.** Starter half and sealer half. Different places. They must fit. No join, no go-command. Looks like two pieces becoming one, not a CRM.

2. **The window.** Clepsydra. A yes that dies at 6. Stale join does not move the boom. Screenshots don’t count.

3. **Draft vs seal.** Wet clay vs rolled seal. Operators can prepare. Nothing is real until sealed. Stranger can check the impression (the seal), not the faces in the cars.

4. **The horn event.** When it seals, the audible/visible yes fires. That’s the TikTok hook in software: state change, not a feed of suspects.

5. **Adapters, not motors.** Sit on the go-path they already have (boom controller, hangar PLC, pad hold). You don’t invent a new 911. You don’t replace CAD. If CAD drafts, your seal is still required for the steel.

6. **The check.** Fail-closed log. A stranger recomputes that a join happened in-window. Cousin of `check/` — don’t weld to Gate/Nisaba unless you choose.

**What we do not build:** people-maps, threat scanners, coded-speech watch, Palantir Gotham, a skippable approve website, a coin.

**Stations:** two apps or two boxes, not one phone with two toggles. Join is a meeting of halves.

**Benchable now (coding, no harbor):**

- A **join pack**: two halves, live window, draft vs seal, a hash a stranger recomputes. CLI says NO unless both fit and now is inside the window.
- A **toy boom**: a fake door in software that only prints GO if the pack verifies. Not a real boom. Not a car. Proves the mouth.
- Tests. Separate folder from Gate. Don’t import Nisaba.

**Not benchable without a door:** adapters into real PLC / pad / vessel. That’s the 5, later.

`check/` is a cousin (fail-closed pack) for git/tasks. Different object. Don’t glue it on unless you mean to.

If you want the bench, say so. That’s the only code worth writing before a real go-path.
