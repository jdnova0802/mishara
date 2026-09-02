# Paste this into desktop Cursor

Copy everything between PASTE START and PASTE END. One paste. Do not add commentary.

Cloud cannot deploy Render from this environment. Live `gate.velaru.xyz` is still the old door.

---

PASTE START

Deploy stranger-two to live gate.velaru.xyz. Commit any local work on this branch. Push. Verify live. Stop.

Do not invent. Do not email. Do not merge to main. Do not run python gate/deploy_render.py — that script can rotate GATE_RECEIPT_* keys if they are missing from .env.

Repo: https://github.com/jdnova0802/mishara
Branch (source of truth): cursor/nisaba-cosmic-unison-719d
PR: https://github.com/jdnova0802/mishara/pull/34 (draft → main)
Who: Demond Davis / Nisaba LLC. Patent 64/124,027. hello@velaru.xyz.

Locks: may · sheath · prove. Gate 1 = stranger paid + proved. Bind $1,750 = Gate 1. Internal architecture = external architecture. Do not email the freeze list.

WHY
Live https://gate.velaru.xyz/ and https://gate.velaru.xyz/bind-room still show the old door:
- hero-sub still says "Full assessment $3,500"
- /bind-room still says "Full assessment is $3,500 · this deposit starts the officer pack"
That copy is not on this branch. This branch already has stranger-two (gate/bind_room.py STRANGER_TWO_PARAS, templates/index.html, templates/bind_room.html). Render is serving an older commit (likely main). Emails in gate/TUESDAY.md point at this live door. Do not let the 11:00 AM ET send fire until live matches.

DONE LOOKS LIKE
curl both pages. They must contain both paragraphs and must not contain "Full assessment":

Your CGL will not cover the agent. Specialist E&O will ask what stops the irreversible write.

Bind Room is the officer pack plus a stranger-openable receipt — $1,750. Not another governance PDF.

Ask button: Book Bind Room
Halt: We will not sell may. We will not implement the rail on this SKU. If the hop is not on your write path, it is still a question.

Price on the door: $1,750 only. Estate $3,500 may still exist on /estate. That is a different SKU. Kill assessment-ladder copy on / and /bind-room only.

DO THIS IN ORDER

1. git fetch origin cursor/nisaba-cosmic-unison-719d
   git checkout cursor/nisaba-cosmic-unison-719d
   git pull origin cursor/nisaba-cosmic-unison-719d

2. If desktop has uncommitted changes that belong on this branch: commit with a clear message and git push -u origin cursor/nisaba-cosmic-unison-719d. If clean, do not invent a dummy commit.

3. Deploy THIS BRANCH to Render service gate-api.
   Service id: srv-d9romc2jnfac7385gn80
   Custom domain: gate.velaru.xyz
   Set the Git branch to cursor/nisaba-cosmic-unison-719d (not main). Then Manual Deploy → Clear build cache & deploy.

   If RENDER_API_KEY is already in ~/DocumentsVelaru/.env or gate/.env, you may API-deploy without touching env-vars:

   source the env file so RENDER_API_KEY is set.
   curl -sS -X PATCH "https://api.render.com/v1/services/srv-d9romc2jnfac7385gn80" \
     -H "Authorization: Bearer $RENDER_API_KEY" -H "Content-Type: application/json" \
     -d '{"branch":"cursor/nisaba-cosmic-unison-719d"}'
   curl -sS -X POST "https://api.render.com/v1/services/srv-d9romc2jnfac7385gn80/deploys" \
     -H "Authorization: Bearer $RENDER_API_KEY" -H "Content-Type: application/json" \
     -d '{"clearCache":"clear"}'

   Wait until the deploy is live (usually a few minutes). Do not declare done from the Render spinner.

4. Verify (must pass all):
   curl -sL https://gate.velaru.xyz/ | grep -F "Specialist E&O will ask what stops the irreversible write."
   curl -sL https://gate.velaru.xyz/ | grep -F "Bind Room is the officer pack plus a stranger-openable receipt"
   curl -sL https://gate.velaru.xyz/ | grep -F "We will not sell may."
   ! curl -sL https://gate.velaru.xyz/ | grep -F "Full assessment"
   curl -sL https://gate.velaru.xyz/bind-room | grep -F "Specialist E&O will ask what stops the irreversible write."
   curl -sL https://gate.velaru.xyz/bind-room | grep -F "Bind Room is the officer pack plus a stranger-openable receipt"
   ! curl -sL https://gate.velaru.xyz/bind-room | grep -F "Full assessment"
   Also open both URLs in a browser and click Book Bind Room once (do not need to pay).

5. Reply with: commit SHA on the branch, Render deploy id, and the grep proof. Then halt. Do not send the Tuesday emails from desktop. Do not invent the next remaining.

If Render refuses a non-main branch: say so and stop. Do not merge PR 34 to main unless Demond says merge.

PASTE END
