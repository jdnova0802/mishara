#!/usr/bin/env python3
"""Study-pack clarity pass: plain teaching for 01-08, 10-11 + loud 00 index.

Code dumps live in gate/study-pdfs/reference/*.code-dump.pdf
Undefined words -> doc 18 Layer 0 atoms.
"""

from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos

OUT = Path(__file__).resolve().parents[1] / "study-pdfs"
ART = Path("/opt/cursor/artifacts/study-pdfs")


def ascii(s: str) -> str:
    repl = {
        "\u2014": "-",
        "\u2013": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2022": "-",
        "\u2192": "->",
        "\u21d4": "<=>",
        "\u2260": "!=",
        "\u2248": "~=",
        "\u00a0": " ",
        "\u2026": "...",
        "\u2227": "AND",
        "\u21d2": "=>",
    }
    for a, b in repl.items():
        s = s.replace(a, b)
    return s.encode("latin-1", "replace").decode("latin-1")


class StudyPDF(FPDF):
    def __init__(self, short_label: str):
        super().__init__(format="Letter")
        self.short_label = short_label
        self.set_auto_page_break(auto=True, margin=18)
        self.set_margins(18, 16, 18)

    def footer(self):
        self.set_y(-14)
        self.set_font("Helvetica", size=8)
        self.set_text_color(80, 80, 80)
        self.cell(0, 8, f"Nisaba LLC  |  study document  |  {self.page_no()}", align="C")

    def header(self):
        if self.page_no() <= 1:
            return
        self.set_font("Helvetica", size=8)
        self.set_text_color(90, 90, 90)
        self.cell(0, 6, self.short_label, align="L")
        self.ln(8)
        self.set_text_color(0, 0, 0)

    def _mc(self, text: str, h: float = 5):
        self.multi_cell(0, h, ascii(text), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def title_block(self, title: str, blurb: str, source: str):
        self.add_page()
        self.set_font("Helvetica", "B", 16)
        self._mc(title, 7)
        self.ln(2)
        self.set_font("Helvetica", size=10)
        self._mc(blurb)
        self.ln(1)
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(70, 70, 70)
        self._mc(source)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def banner(self, text: str):
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(240, 240, 240)
        self.set_text_color(40, 40, 40)
        self.multi_cell(
            0,
            5,
            ascii(text),
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            fill=True,
        )
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def section(self, text: str):
        self.ln(1)
        self.set_font("Helvetica", "B", 11)
        self._mc(text, 6)
        self.ln(1)
        self.set_font("Helvetica", size=10)

    def para(self, text: str):
        self.set_font("Helvetica", size=10)
        self._mc(text)
        self.ln(1)

    def bullets(self, items):
        self.set_font("Helvetica", size=10)
        for item in items:
            self._mc(f"- {item}")
        self.ln(1)

    def labeled(self, label: str, body: str):
        self.set_font("Helvetica", size=10)
        self._mc(f"{label}: {body}")
        self.ln(1)


def write_pdf(filename: str, short: str, build) -> Path:
    pdf = StudyPDF(short)
    build(pdf)
    OUT.mkdir(parents=True, exist_ok=True)
    ART.mkdir(parents=True, exist_ok=True)
    path = OUT / filename
    pdf.output(str(path))
    (ART / filename).write_bytes(path.read_bytes())
    print(f"wrote {filename} ({path.stat().st_size})")
    return path


ATOMS = "Undefined word? Open doc 18 (Layer 0 atoms) and define it before continuing."


def build_00(pdf: StudyPDF):
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf._mc("Nisaba Action OS - Study Pack", 7)
    pdf.ln(2)
    pdf.set_font("Helvetica", size=10)
    pdf._mc("Teaching docs first. Code dumps are quarantined. Own atoms before jargon.")
    pdf.ln(1)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(70, 70, 70)
    pdf._mc("Source: gate/study-pdfs/  |  Code dumps: gate/study-pdfs/reference/")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)
    pdf.banner(
        "HARD RULE: 04-07 and old 10 code dumps are REFERENCE ONLY "
        "(see reference/*.code-dump.pdf). Teaching versions replaced them in this folder. "
        "Start at 18 if any word is undefined. Cash first (Friday send)."
    )
    pdf.section("How to use")
    pdf.para(
        "Read teaching docs. After each, close it and retrieve from memory. "
        "If a word feels hollow, stop and open 18. Do not 'study' by scrolling Python."
    )
    pdf.section("The four laws (only after each word is defined)")
    pdf.bullets(
        [
            "can != may",
            "clearance != execution (Gate clearance does not move the money)",
            "CHARGE-only resurrect (DEAD -> LIVE)",
            "Clear <=> reconstruct (presented AND LIVE)",
        ]
    )
    pdf.section("Document list")
    pdf.bullets(
        [
            "18  Layer 0 atoms - START HERE when jargon is hollow",
            "11  Mouth literacy - plain teaching of the firm",
            "01  SCIENCE - why Gate sits between can and may",
            "02  Action OS - what the company is",
            "03  Science PRI - laws in plain + first weld",
            "04  Mouth mechanics - TEACHING (code dump in reference/)",
            "05  Write edge - TEACHING (code dump in reference/)",
            "06  Prefinality - TEACHING (code dump in reference/)",
            "07  Married write - TEACHING (code dump in reference/)",
            "08  Bind Room - SKU/ops (not first literacy)",
            "09  Friday send pack - outbound checklist",
            "10  Production honesty - TEACHING (code dump in reference/)",
            "12  Code reading for Gate - map literacy",
            "13  Foundations trunk",
            "14-17  General Gate-tied subjects",
        ]
    )
    pdf.section("Suggested path")
    pdf.bullets(
        [
            "18 -> 11 -> 01 -> 02 -> 03 -> 14 -> 08 -> 09 -> 04 -> 05 -> 06 -> 07 -> 10 -> 15 -> 16 -> 17 -> 12",
            "Only open reference/*.code-dump.pdf after you can teach the law blank-page",
        ]
    )
    pdf.section("Near-term rule")
    pdf.para(
        "Deploy diligence live. Send Friday pack. Quit on paid Clear. "
        "Atoms before jargon. Teaching before code. External receipts before identity."
    )


def build_01(pdf: StudyPDF):
    pdf.title_block(
        "SCIENCE - Can, May, and the First Weld",
        "Why Gate exists, in plain language first. Then the science labels.",
        "Source: gate/SCIENCE.md  |  " + ATOMS,
    )
    pdf.banner(ATOMS)
    pdf.section("Plain opener (middle-school test)")
    pdf.para(
        "Computers can do more dangerous things every year - send money, bind coverage, "
        "let an agent click a tool. Being able to do it is not the same as being allowed. "
        "Gate is a mouth on that gap: before an irreversible change finishes, check permission. "
        "If unsure, stop (DENY). Keep a receipt someone else can open."
    )
    pdf.para(
        "First real job we prove: payout / withdraw - clear before the wire. "
        "Prove a real DENY on one money-leave path before talking grid or force."
    )
    pdf.section("What we are not")
    pdf.bullets(
        [
            "We do not own nukes, military command, the power grid, or link monopolies.",
            "We contribute as a clearance mouth under people who already own those stacks.",
            "We do not sell a pretty dashboard that never sits on the write.",
        ]
    )
    pdf.section("Words you must own (from 18)")
    pdf.bullets(
        [
            "can / may",
            "irreversible write",
            "DENY / fail-closed",
            "LIVE / DEAD / CHARGE",
            "clearance vs execution",
        ]
    )
    pdf.section("Science labels -> plain Gate law")
    pdf.labeled(
        "PRI (pre-irreversibility inhibition)",
        "Do not complete an unjustified irreversible act. Execute only if LIVE and justified; else DENY. No bypass. Only CHARGE re-opens.",
    )
    pdf.labeled(
        "Fail-closed",
        "Uncertainty means DENY. Soft-yes under panic is the failure mode.",
    )
    pdf.labeled(
        "Measure -> control -> receipt",
        "You cannot magically 'just intervene' with zero cost. Check, decide LIVE/DENY, leave stranger-checkable evidence. Silent free yes is illegal.",
    )
    pdf.labeled(
        "Driver node (not hub dashboard)",
        "Sit on the actual irreversible edge (the write). Owning a busy overview screen is not the same as holding the door.",
    )
    pdf.labeled(
        "Quorum / unfireable mouth",
        "LIVE needs more than one friendly operator vibe - policy quorum + CHARGE + Gate. Proof sits where the actor alone cannot forge it (Velaru verify).",
    )
    pdf.section("First weld (named)")
    pdf.bullets(
        [
            "Name: Withdraw / payout - clear before wire",
            "Prove DENY on one irreversible money-leave path",
            "Example path shape: POST /v1/payouts/{id}/release",
            "Human checkout door: /operator -> withdraw",
            "Next after prove: grid shed/reconnect. Nuclear C2 stays state-only.",
        ]
    )
    pdf.section("Contribution ladder (altitude, not ownership fantasies)")
    pdf.bullets(
        [
            "1. Commercial driver weld (payout clear) - prove DENY",
            "2. Critical infra mouth (grid) after prove",
            "3. Named in coordinator plans + cleared custodians",
            "4. Defense/comms release mouth under programs - unclaimed until real",
        ]
    )
    pdf.section("Retrieval drill")
    pdf.bullets(
        [
            "Explain can vs may with one money example.",
            "What is the first weld and why not grid first?",
            "What does fail-closed mean without using the phrase fail-closed?",
            "What do we refuse to own?",
        ]
    )


def build_02(pdf: StudyPDF):
    pdf.title_block(
        "Action OS - What the Company Is",
        "Nisaba in one breath, then the family map.",
        "Source: gate/action_os.py  |  " + ATOMS,
    )
    pdf.banner(ATOMS)
    pdf.section("Plain opener")
    pdf.para(
        "Nisaba is the Action OS. We sit on permission for irreversible acts - "
        "money leaving, coverage binding, force-class releases in category. "
        "Our scarce product is a DENY that actually holds, with a receipt a stranger can open. "
        "A speech about safety with no halt is just software marketing."
    )
    pdf.para(
        "Palantir made knowing cheaper. We sit on acting: should this irreversible write complete?"
    )
    pdf.section("Formula")
    pdf.para(
        "Own permission on irreversible acts for any power that needs it - "
        "and make your scarcity the DENY, not the narrative."
    )
    pdf.section("Who we serve")
    pdf.bullets(
        [
            "Anyone whose write is irreversible: treasuries, payment rails, companies, carriers, states.",
            "Serving conflicting powers is structural when you sit on the act - neutrality theater is fake.",
            "We refuse soft-yes resurrection and forged LIVE. We do not refuse the category.",
        ]
    )
    pdf.section("Family map (one question each)")
    pdf.bullets(
        [
            "Erra: Should we act? (signal ACT/HOLD)",
            "Velaru: Did we commit correctly? (proof ALLOW/BLOCK + fuse)",
            "Gate: Does the irreversible write complete? (mouth /v1/act, CHARGE, weld)",
            "Verra: Did both rails clear before bind?",
            "Mishara: Was a person harmed?",
        ]
    )
    pdf.section("Integrity rules")
    pdf.bullets(
        [
            "CHARGE is the only DEAD -> LIVE path - buyer cannot purchase a dashboard flip",
            "Stranger verify without login",
            "One exclusive door per weld - no bypass UI",
            "Fail closed on DEAD / timeout / 5xx - never treat unreachable as LIVE",
            "their_production stays false until a real exclusive third-party weld",
            "Force/battlefield doors stay unclaimed until welded - category != costume",
        ]
    )
    pdf.section("Money faces vs the firm")
    pdf.bullets(
        [
            "Diligence ($2,500): paid find of may-gaps - not a weld",
            "Bind Room ($1,750): examiner halt artifacts - not a weld",
            "Operator / register / weld: fortune lane when a real path is exclusive",
            "Prefinality is law inside Nisaba - not a sister company",
        ]
    )
    pdf.section("Not this")
    pdf.bullets(
        [
            "Claimed contracts or production we do not have",
            "AI governance slideshows that never sit on the write",
            "Scarcity as storytelling while DENY does not hold",
        ]
    )
    pdf.section("Retrieval drill")
    pdf.bullets(
        [
            "One sentence: what is Nisaba?",
            "What is the scarce product?",
            "Name Gate's question.",
            "Why is controversy structural?",
        ]
    )


def build_03(pdf: StudyPDF):
    pdf.title_block(
        "Science PRI - Laws and First Weld",
        "PRI as architecture, not a vibe. Plain first, then formal labels.",
        "Source: gate/science_pri.py  |  " + ATOMS,
    )
    pdf.banner(ATOMS)
    pdf.section("Plain opener")
    pdf.para(
        "Bad outcomes often happen when a system finishes a one-way action without enough "
        "justification. PRI means: build the stop into the architecture. "
        "If it is not LIVE and justified, DENY. If something breaks while checking, DENY. "
        "Turning the path back on takes CHARGE - not a friendly admin click."
    )
    pdf.section("First commercial driver")
    pdf.labeled("ID", "withdraw_payout_clear")
    pdf.labeled("Write", "withdraw / payout - clear before wire")
    pdf.labeled(
        "Why first",
        "Money leaving is irreversible enough to prove the mouth, commercial enough to sell, before grid or program cosplay.",
    )
    pdf.labeled("Example path", "POST /v1/payouts/{id}/release")
    pdf.labeled("Checkout", "/operator?write=withdraw")
    pdf.labeled("Next after prove", "grid_shed_reconnect - not first")
    pdf.section("Formal laws (after atoms)")
    pdf.labeled(
        "PRI",
        "execute(a) only if LIVE(a) AND justified(a); else DENY. bypass empty. CHARGE-only re-open.",
    )
    pdf.labeled(
        "Fail-closed",
        "uncertainty => DENY. Life-safety overrides are explicit coordinator lanes, not soft-yes.",
    )
    pdf.labeled(
        "Intervention cost",
        "Real control is measure -> LIVE|DENY -> receipt. Silent free yes is illegal. Price the dissipation (weld + bps).",
    )
    pdf.labeled(
        "Driver on the act graph",
        "Weld one irreversible edge at a time. Hub dashboards are not drivers.",
    )
    pdf.labeled(
        "Quorum mouth",
        "LIVE needs quorum(policy) AND CHARGE AND Gate mouth. Stranger-verify outside the actor's forge zone.",
    )
    pdf.section("Not first")
    pdf.bullets(
        [
            "Grid blackstart (step 2)",
            "Milcomms release mouth (ladder later)",
            "Nuclear C2 (state only)",
        ]
    )
    pdf.section("Retrieval drill")
    pdf.bullets(
        [
            "State PRI as IF/ELSE DENY.",
            "Why payout before grid?",
            "What alone re-opens DEAD?",
        ]
    )


def build_04(pdf: StudyPDF):
    pdf.title_block(
        "Mouth Mechanics - How Gate Clearance Works",
        "Teaching version. Full code dump quarantined in reference/.",
        "Source: gate/app.py (law)  |  reference/04-app-mouth-excerpts.code-dump.pdf  |  " + ATOMS,
    )
    pdf.banner(
        "TEACHING DOC. Code dump moved to study-pdfs/reference/. "
        "Do not confuse scrolling Python with owning the law. " + ATOMS
    )
    pdf.section("Plain opener")
    pdf.para(
        "Gate asks Velaru: is this path allowed right now? "
        "If the answer is no, broken, timed out, or unreadable - stop. "
        "If the answer is yes, Gate returns a permit. Gate still does not move the money. "
        "Another exclusive door (worker/weld) is the only place the write may run after permit."
    )
    pdf.section("Three jobs in the mouth")
    pdf.labeled(
        "fail_closed",
        "Timeouts and bad upstream answers become DENY/halt. Unreachable is never treated as LIVE.",
    )
    pdf.labeled(
        "velaru_fuse",
        "All fuse questions go through that fail-closed client. Non-JSON / 5xx / timeout => halt.",
    )
    pdf.labeled(
        "run_welded_act (/v1/act)",
        "Returns whether the act may proceed. write_executed stays false from Gate. acted/clearance_allows means permit - not execution.",
    )
    pdf.section("Law")
    pdf.para(
        "Clearance is not execution. The exclusive edge is the only place the irreversible write may run after a valid permit."
    )
    pdf.section("What to hunt when you later open the code dump")
    pdf.bullets(
        [
            "write_executed must stay false on Gate clearance paths",
            "halt / fail_closed / UNREACHABLE paths",
            "CHARGE mentioned as only DEAD -> LIVE path",
            "Demo routes vs welded closed-world routes",
        ]
    )
    pdf.section("Retrieval drill")
    pdf.bullets(
        [
            "Why can Gate say yes and money still not leave?",
            "What happens if Velaru times out?",
            "Name the three jobs above from memory.",
        ]
    )


def build_05(pdf: StudyPDF):
    pdf.title_block(
        "Write Edge - The Exclusive Door",
        "Teaching version. Worker source dump is in reference/.",
        "Source: gate/cloudflare-worker.js (law)  |  reference/05-...code-dump.pdf  |  " + ATOMS,
    )
    pdf.banner(
        "TEACHING DOC. Code dump in study-pdfs/reference/. " + ATOMS
    )
    pdf.section("Plain opener")
    pdf.para(
        "Imagine a locked door in front of the real action. "
        "First the door asks Gate: may this proceed? If Gate says halt/DEAD/no - the door refuses. "
        "Only after a valid permit does the door fetch/run the real request and mark that the write executed. "
        "If someone can skip this door, you do not have a mouth - you have theater."
    )
    pdf.section("Order of operations")
    pdf.bullets(
        [
            "1. Configure Gate URL + key (no localhost in production)",
            "2. Ask Gate /v1/act for clearance",
            "3. If not ok / halt / acted false -> return halt (DENY path)",
            "4. Only then fetch the origin request (the irreversible side effect)",
            "5. Mark write-executed headers only after that success path",
        ]
    )
    pdf.section("Law")
    pdf.para(
        "Gate issues clearance. The worker/weld is the exclusive edge that may execute. Museum hops are not production."
    )
    pdf.section("Honesty checks")
    pdf.bullets(
        [
            "Is there only one door?",
            "Does unreachable Gate fail closed?",
            "Is write-executed set only after the real fetch?",
            "Can a stranger open verify proof of a halt?",
        ]
    )
    pdf.section("Retrieval drill")
    pdf.bullets(
        [
            "Explain exclusive edge without saying exclusive.",
            "When is write-executed allowed to become true?",
            "What if Gate is misconfigured?",
        ]
    )


def build_06(pdf: StudyPDF):
    pdf.title_block(
        "Prefinality - Clear Before Finality",
        "Teaching version. Full prefinality.py dump is in reference/.",
        "Source: gate/prefinality.py (law)  |  reference/06-...code-dump.pdf  |  " + ATOMS,
    )
    pdf.banner(
        "TEACHING DOC. 10-page code dump quarantined in reference/. " + ATOMS
    )
    pdf.section("Plain opener")
    pdf.para(
        "Before money (or a similar final transfer) actually finishes, ask GO / NO_GO / HOLD. "
        "A green sticker is not enough. At the moment of effectuation, Clear means: "
        "the proof can be rebuilt as presented AND authority is still LIVE. "
        "If fields are missing, policy fails, fuse is DEAD, or receipt cannot be verified - NO_GO."
    )
    pdf.section("What Prefinality is")
    pdf.bullets(
        [
            "Doctrine + machinery inside Gate/Nisaba - not a sister company",
            "Evaluates whether a transfer/finality step may proceed",
            "Binds a signed receipt to a fingerprint of the transfer",
            "Clearance remains distinct from execution (write_executed false here)",
        ]
    )
    pdf.section("Decisions")
    pdf.bullets(
        [
            "GO - may proceed only if receipt still verifies and is unexpired at commit",
            "HOLD - human review before commit",
            "NO_GO - do not sign or send; fail closed",
        ]
    )
    pdf.section("Rails (adapters, same mouth idea)")
    pdf.bullets(
        [
            "x402 - before an agent wallet signs",
            "rtp - before instant fiat credit / payment order",
        ]
    )
    pdf.section("Fail-closed triggers (examples)")
    pdf.bullets(
        [
            "Bad/missing amount or counterparty",
            "Amount over mandate cap",
            "Routing anomaly / injection into destination",
            "Fuse DEAD",
            "Signing required but unsigned in prod",
        ]
    )
    pdf.section("What to hunt later in the code dump")
    pdf.bullets(
        [
            "evaluate vs verify",
            "transfer_fingerprint",
            "mint/verify receipt JWT",
            "write_executed false / clearance_only true in responses",
        ]
    )
    pdf.section("Retrieval drill")
    pdf.bullets(
        [
            "Define Clear without saying Clear.",
            "Why is GO alone not enough at effectuation?",
            "Name three NO_GO reasons.",
        ]
    )


def build_07(pdf: StudyPDF):
    pdf.title_block(
        "Married Write - Tickets and Spend",
        "Teaching version. Full spend/ticket dumps are in reference/.",
        "Source: gate/spend_protocol.py + ticket.py  |  reference/07-...code-dump.pdf  |  " + ATOMS,
    )
    pdf.banner(
        "TEACHING DOC. 11-page code dump quarantined in reference/. " + ATOMS
    )
    pdf.section("Plain opener")
    pdf.para(
        "A LIVE hop is ink - proof something was checked - not a blank check to spend later. "
        "To actually spend (e.g. bind), you need a short-lived, single-use ticket "
        "married to one exact write (method + path + job + kind). "
        "If you try a different write, or the ticket is stale, or you replay it - halt."
    )
    pdf.section("Why this exists")
    pdf.para(
        "Time gap problem: permission at time A, different dangerous action at time B. "
        "Marrying the ticket to one fingerprint closes that gap. Stale hop = museum."
    )
    pdf.section("Atoms in this doc")
    pdf.labeled(
        "fingerprint",
        "A hash of the exact write being authorized - so 'bind-only' cannot authorize 'bind-and-issue'.",
    )
    pdf.labeled(
        "ticket",
        "Short-lived, single-use grant bound to that fingerprint. Default TTL is short (seconds).",
    )
    pdf.labeled(
        "redeem",
        "Consume the ticket while presenting the same write. Fail closed on skew, mismatch, replay, dead parent.",
    )
    pdf.section("Law")
    pdf.para(
        "LIVE hop != spend grant. Ticket bound to write fingerprint. Redeem must present the same write."
    )
    pdf.section("What to hunt later in the code dump")
    pdf.bullets(
        [
            "How fingerprint is computed",
            "TTL + single_use + stale_hop_cannot_spend",
            "redeem halt reasons",
            "children_cannot_outlive_parent (license fuse)",
        ]
    )
    pdf.section("Retrieval drill")
    pdf.bullets(
        [
            "Why is a LIVE hop not enough to spend?",
            "What is married about a married write?",
            "What is a museum hop?",
        ]
    )


def build_08(pdf: StudyPDF):
    pdf.title_block(
        "Bind Room - Money Face SKU",
        "Examiner artifacts for insurance/compliance buyers. Not the first literacy doc.",
        "Source: gate/bind_room.py  |  " + ATOMS,
    )
    pdf.banner(
        "WARNING: This is a SKU / ops / examiner pack - not Layer-0 teaching. "
        "Regulator words (SERFF, NYDFS, ECDIS, PolicyCenter) are buyer dialect. "
        "Own atoms in 18 and mouth literacy in 11 before living here. Price: $1,750."
    )
    pdf.section("Plain opener")
    pdf.para(
        "Bind Room sells two things examiners actually take: "
        "(A) a short officer pack shaped like a filing, and "
        "(B) an on-request appendix of halt/verify links per bind event. "
        "It is not the production weld. It is evidence and packaging around halt-on-bind."
    )
    pdf.section("What you are selling")
    pdf.bullets(
        [
            "A: Officer pack (<=10 pages) - titles on each Section 5 duty",
            "B: Appendix of verify_url + hop per bind event (not the SERFF body)",
            "Price / CTA: $1,750",
        ]
    )
    pdf.section("Plain meaning of the pack")
    pdf.bullets(
        [
            "Who can stop bind when authority is DEAD?",
            "Can you show a DEAD drill with a stranger-openable verify link?",
            "Is hop required before the irreversible bind write?",
            "Timeout = HALT, never silent LIVE",
            "CHARGE-only resurrect - approve-in-meeting is not enough",
            "Gate is control plane, not a rating model - carrier duty remains",
        ]
    )
    pdf.section("Refuse")
    pdf.bullets(
        [
            "Do not lead with courtroom evidence cosplay to a CUO",
            "Do not sell model inventory piles",
            "Do not put PII on Gate",
        ]
    )
    pdf.section("Retrieval drill")
    pdf.bullets(
        [
            "Is Bind Room a weld? (No.)",
            "What two artifacts do examiners take?",
            "Name one plain control the pack must show.",
        ]
    )


def build_10(pdf: StudyPDF):
    pdf.title_block(
        "Production Honesty - their_production",
        "Teaching version. Code dump quarantined in reference/.",
        "Source: gate/production_skin.py (law)  |  reference/10-...code-dump.pdf  |  " + ATOMS,
    )
    pdf.banner(
        "TEACHING DOC. Code dump in study-pdfs/reference/. " + ATOMS
    )
    pdf.section("Plain opener")
    pdf.para(
        "Demo hops are museum until a real third party runs their irreversible write "
        "through your exclusive door. their_production is the honesty bit: "
        "false means do not talk like you are in production on their path. "
        "Dogfood (you welding yourself) can lift readiness - it still does not flip their_production."
    )
    pdf.section("Two different welds")
    pdf.labeled(
        "dogfood_weld",
        "First-party recorded weld. Helps proof/deploy maturity. Does NOT claim their_production.",
    )
    pdf.labeled(
        "production weld (their_production)",
        "Third-party exclusive path attested. Requires real confirm + exclusivity. This is the honesty flip.",
    )
    pdf.section("Readiness vs production")
    pdf.bullets(
        [
            "Proof suite / checklist can say deploy-ready",
            "Only recorded exclusive third-party weld flips their_production",
            "Force/battlefield remains category-only until welded",
        ]
    )
    pdf.section("Checklist ideas (plain)")
    pdf.bullets(
        [
            "Closed-world /v1/act door exists",
            "Public demo hop fails closed with verify link",
            "CHARGE-only DEAD -> LIVE",
            "PII rejected on PAS paths",
            "Register + operator checkout live",
            "Action OS formula published",
            "Proof suite passes",
            "Stranger verify via Velaru",
        ]
    )
    pdf.section("Retrieval drill")
    pdf.bullets(
        [
            "Define their_production without the flag name.",
            "Why doesn't dogfood count as their_production?",
            "What stays false until a real exclusive third-party weld?",
        ]
    )


def build_11(pdf: StudyPDF):
    pdf.title_block(
        "Mouth Literacy - No Code Required",
        "Founder-deep plain language. If any word is undefined, leave and open doc 18 first.",
        "Source: doctrine synthesis  |  Prerequisite: 18 Layer 0 atoms",
    )
    pdf.banner(
        "PREREQUISITE: Doc 18 (Layer 0 atoms). "
        "If you cannot define DENY, can, may, LIVE, Clear - stop and do 18 before this page."
    )
    pdf.section("One sentence")
    pdf.para(
        "Nisaba is the Action OS: we sit on permission for irreversible acts. "
        "Scarcity is a DENY that holds, with a receipt a stranger can open."
    )
    pdf.section("The problem we sit on")
    pdf.para(
        "Modern systems multiply what they can do - pay out, peg out, bind, agent side effects. "
        "Catastrophe and liability often come from completing an irreversible write when may is missing. "
        "Can is cheap. May is scarce."
    )
    pdf.labeled("can", "Able to perform the write (API works, keys exist, agent has a tool).")
    pdf.labeled("may", "Allowed to complete under live authority, policy, and proof.")
    pdf.section("The four laws (memorize - with definitions)")
    pdf.bullets(
        [
            "1. can != may - Ability is not permission. Diligence asks: where can the write still complete without may?",
            "2. clearance != execution - Gate may permit; Gate does not move the money. Exclusive edge executes after permit.",
            "3. CHARGE-only resurrect - DEAD means stop. Only CHARGE returns LIVE - not dashboard politeness.",
            "4. Clear <=> reconstruct - Clear means proof rebuilds as presented AND LIVE. A GO sticker alone is not Clear.",
        ]
    )
    pdf.section("Family map")
    pdf.bullets(
        [
            "Erra: Should we act?",
            "Velaru: Did we commit correctly?",
            "Gate: Does the irreversible write complete?",
            "Verra: Did both rails clear before bind?",
            "Mishara: Was a person harmed?",
        ]
    )
    pdf.section("Money faces vs the firm")
    pdf.bullets(
        [
            "Diligence ($2,500 deposit) - paid find of may-gaps. Not a weld.",
            "Bind Room ($1,750) - examiner halt artifacts. Not a weld.",
            "Operator / register / weld - fortune lane when exclusive path is real.",
            "Prefinality is law inside Nisaba - not a sister company.",
        ]
    )
    pdf.section("Honesty bit")
    pdf.para(
        "their_production: false until a recorded third-party exclusive production weld. Demo hops are museum."
    )
    pdf.section("First commercial driver")
    pdf.para(
        "Withdraw / payout - clear before wire. Prove DENY on one money-leave path before grid or force cosplay."
    )
    pdf.section("Retrieval drill (blank page)")
    pdf.bullets(
        [
            "Write the one sentence.",
            "Define can vs may with one money example.",
            "Define DENY without saying deny.",
            "Explain why Gate saying yes is not money leaving.",
            "Explain DEAD and what alone can resurrect.",
            "Explain Clear in one sentence.",
            "Name Erra, Velaru, Gate questions in order.",
        ]
    )
    pdf.section("What this is not")
    pdf.bullets(
        [
            "Not AI governance slideshows that never sit on the write",
            "Not claiming production you do not have",
            "Not a substitute for Layer 0 atoms (18)",
        ]
    )


def main():
    write_pdf("00-README-study-order.pdf", "00 Study pack index", build_00)
    write_pdf("01-SCIENCE.pdf", "01 SCIENCE", build_01)
    write_pdf("02-action_os.pdf", "02 Action OS", build_02)
    write_pdf("03-science_pri.pdf", "03 Science PRI", build_03)
    write_pdf("04-app-mouth-excerpts.pdf", "04 Mouth mechanics", build_04)
    write_pdf("05-cloudflare-worker.pdf", "05 Write edge", build_05)
    write_pdf("06-prefinality.pdf", "06 Prefinality", build_06)
    write_pdf("07-spend-and-ticket.pdf", "07 Married write", build_07)
    write_pdf("08-bind_room.pdf", "08 Bind Room", build_08)
    write_pdf("10-production_skin.pdf", "10 Production honesty", build_10)
    write_pdf("11-mouth-literacy-no-code.pdf", "11 Mouth literacy", build_11)
    # copy reference dumps to artifacts
    ref = OUT / "reference"
    art_ref = ART / "reference"
    art_ref.mkdir(parents=True, exist_ok=True)
    for p in ref.glob("*.pdf"):
        (art_ref / p.name).write_bytes(p.read_bytes())
    print("clarity pass complete")


if __name__ == "__main__":
    main()
