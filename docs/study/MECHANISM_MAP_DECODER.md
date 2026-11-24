# MECHANISM MAP DECODER — PLAIN ENGLISH

A **do-list**. You pick one map. You run six checks. You write pass or fail on each. If a check fails, you fix that map (or stop treating it as studied) before you move on.

This is **not** How to Learn (that’s for a cycle: who did what to whom). This is **not** a Deep. **Do not** spend Thursday–Saturday hours “studying the decoder.” Run it when you finish a map, edit a map, or a live case hits a map.

**Use this on:** AI / Technical Map, Political Economy Map, Perception / Control Map, and any other Maps/Branches note written like those (what it is, what it is not, how it runs, how it fails). In the repo, the example is `docs/study/PERCEPTION_CONTROL_MAP.md`.

**Do not use this on:**

- 11-box grids (Religion as Institution, Socionomics, peoples atlases, class / trade / war lookup)
- Cycle notes (use How to Learn)
- The homework lists (`HOME_LEARNABLE_CURRICULUM.md`, `PHASE3_PERCEPTION_CONTROL.md`)
- The Morning, X lineup, standing priority list

If the heading names don’t match, that’s fine. Same job, different title:

- “How a Case Runs” = “How it actually works” (and “How it actually fails” is part of the run)
- “What This Is NOT” = “What this is not”
- “Best Free Starters” = any real URLs the map tells you to open
- “Open problems” = “OPEN”

No heading and no paragraph that does that job = empty. Empty = fail.

---

## How to run it (one sitting)

1. Open **one** map. Write its title and pull date here: _______________
2. Do checks 1 → 6 in order. Don’t skip.
3. For each check: do the action, then circle **PASS** or **FAIL**. If FAIL, do the “fix” line before you call the map studied.
4. If check 1 fails, stop. You haven’t studied it yet. The other checks are about the **paper**, not about you.

Don’t schedule this as a course. Twenty minutes per map is the point.

---

## The six checks

### 1. Can you say how a case runs with the map closed?

**Do**

- Close the file.
- Out loud, walk one full case in order: step 1, step 2, step 3.
- Then name **one failure that still looks like it worked** (the math ran, the quote existed, the model answered — and the real thing was still wrong).

**PASS if:** you can do that without peeking.  
**FAIL if:** you remember product names, companion tables, or “it’s about Kalman” but not the steps.

**Fix if FAIL:** you haven’t studied it. Open the “how it works” section, say it again tomorrow with the file closed. Don’t tick the map as done.

**Worked example (Perception / Control):** “Predict with a motion model and process noise Q. A measurement comes in with noise R. The gain is how much you trust the sensor vs the model. Then name EKF vs UKF vs SLAM as different machines. Failure that looks like success: the filter prints a small P while you’re lost because Q/R were a lie, or SITL hovered and you called it a flight test.”

---

### 2. Does “what this is not” actually stop a mix-up?

**Do**

- Pick **one real nearby thing** (a news story, a vendor demo, the next Deep, a live weld). Write it: _______________
- Read “What this is not.”
- In one sentence, say why that nearby thing is **not** this map.

**PASS if:** the sentence uses a named line from the boundary, and the nearby thing stays out.  
**FAIL if:** the boundary is vague (“not hype,” “not everything”) **or** the nearby thing sneaks back in under a new name (simulator hover called a flight test; Palantir called a Kalman filter; a quote called a bind).

**Fix if FAIL:** rewrite the “not” list with the nearby thing named, or you don’t have a map — you have a mood.

**Worked example:** Nearby thing = a Palantir fusion screenshot. Boundary line = onboard estimate is not a Gotham graph. One sentence: “That screenshot is link analysis. This map is where the vehicle thinks it is.” If you can’t say that, the boundary failed.

---

### 3. Are the starter links still good?

**Do**

- List every URL under Best Free Starters (or any URL the map tells you to open). If there are none, that’s a FAIL — a mechanism map owes at least one thing a person can actually open this week.
- Click each one. You want HTTP 200, or a redirect you can **name** (old host → new host).
- Ask: is this still the right first page, or did the field replace it with something better?
- Write today’s date on the map if the list still holds.

**PASS if:** links open, they’re starters (not a 400-page dump to look serious), and the pull date is real.  
**FAIL if:** 404/403 with no named redirect, “just Wikipedia,” a dead 2019 tutorial, or you pasted the curriculum homework list into the map and called it starters.

**Fix if FAIL:** hit the links, drop the dead ones, put the live starter in, date it. Don’t study from a dead list.

---

### 4. Is the OPEN section still true?

**Do**

- Read OPEN / open problems.
- For each bullet: still unsolved in public, **or** someone shipped a real answer since the pull date?
- Add one line if the field opened a **new** problem a practitioner would actually hit — or write “refused, not this map.”

**PASS if:** leftover opens are still open; solved ones are gone or marked closed with a date.  
**FAIL if:** a solved thing is still listed as open, or OPEN is a junk drawer (“more research needed”).

**Fix if FAIL:** edit OPEN. The map is a picture of *now*, not of the week you wrote it.

---

### 5. Is this the machine, or the product wrapped around the machine?

**Do**

- Fill three blanks out loud:
  - The **machine** (the actual mechanism) is: _______________
  - The **product/wrapper** people sell on top of it is: _______________
  - The wrapper **claims** _______________ which the machine **does not guarantee**.

**PASS if:** those three are different.  
**FAIL if:** the map treats a brand, a screenshot, a model name, or a policy PDF as the machine.

**Fix if FAIL:** split the three in the map. Until then you studied marketing.

**Worked examples**

- AI / Technical: machine = the model. Wrapper = the agent with tools. Claim that isn’t guaranteed = “safe by default.”
- Perception / Control: machine = Kalman predict/update. Wrapper = PX4. Claim that isn’t guaranteed = “the drone knows where it is.”
- Insurance-style map: machine = quote vs bind. Wrapper = the portal. Claim that isn’t guaranteed = “you’re covered because you have a PDF.”

---

### 6. Could someone who has to *use* this actually act from it?

**Do**

- Read one failure section.
- Ask: if I were the person running this (filter, bind, handshake), would this tell me what to **do** when it goes wrong — or only give me words to say at dinner?

**PASS if:** two machines that look alike are kept apart (EKF is not UKF; quote is not bind), and the failure is something that happens on a desk or in a log.  
**FAIL if:** it’s a TED talk (“AI is just math”) **or** it’s a pile of terms used once and never run.

**Fix if FAIL:** cut the speech. Put back one failure you could hit this month. If you can’t, the map is a poster.

---

## Scorecard (copy this into the note or say it)

Map: _______________  Date run: _______________

| # | Check | Pass / Fail |
|---|--------|-------------|
| 1 | Said the run with the file closed | |
| 2 | Nearby case bounced off “what this is not” | |
| 3 | Starter links open and still the right first page | |
| 4 | OPEN is still true | |
| 5 | Machine / wrapper / fake claim are three different things | |
| 6 | A user could act from a failure, not just talk | |

**If 1 is fail:** you only read it. Stop.  
**If 1 is pass and 2 is fail:** you can recite it and still mix it with the neighbor. Worse.  
**If 1–2 pass and 3 or 4 fail:** you studied an old copy. Update links and OPEN.  
**If 1–4 pass and 5 is fail:** you studied a product page.  
**If 1–5 pass and 6 is fail:** you studied a poster.

A map in this house style also still needs, or it isn’t done:

- One line that would **prove the map wrong** (which part dies).
- What this map is **vs** the homework list **vs** the neighbor note. Don’t paste milestones into the map.
- A pull date (America/New_York).

Done means: you said the run from memory, one nearby case stayed out, one live starter, one still-open problem, machine ≠ product. Headings that look finished don’t count.
