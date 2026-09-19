#!/usr/bin/env python3
"""Layer-0 mega glossary: elementary plain, every fancy word defined."""

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
    }
    for a, b in repl.items():
        s = s.replace(a, b)
    return s.encode("latin-1", "replace").decode("latin-1")


class StudyPDF(FPDF):
    def __init__(self, short_label: str):
        super().__init__(format="Letter")
        self.short_label = short_label
        self.set_auto_page_break(auto=True, margin=16)
        self.set_margins(16, 14, 16)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", size=8)
        self.set_text_color(80, 80, 80)
        self.cell(0, 8, f"Nisaba LLC  |  study document  |  {self.page_no()}", align="C")

    def header(self):
        if self.page_no() <= 1:
            return
        self.set_font("Helvetica", size=8)
        self.set_text_color(90, 90, 90)
        self.cell(0, 5, self.short_label, align="L")
        self.ln(6)
        self.set_text_color(0, 0, 0)

    def _mc(self, text: str, h: float = 4.5):
        self.multi_cell(0, h, ascii(text), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def title_block(self, title: str, blurb: str, source: str):
        self.add_page()
        self.set_font("Helvetica", "B", 15)
        self._mc(title, 6.5)
        self.ln(1)
        self.set_font("Helvetica", size=9.5)
        self._mc(blurb)
        self.ln(0.5)
        self.set_font("Helvetica", "I", 8.5)
        self.set_text_color(70, 70, 70)
        self._mc(source)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def section(self, text: str):
        self.ln(1)
        self.set_font("Helvetica", "B", 11)
        self._mc(text, 5.5)
        self.ln(0.5)
        self.set_font("Helvetica", size=9.5)

    def para(self, text: str):
        self.set_font("Helvetica", size=9.5)
        self._mc(text)
        self.ln(0.5)

    def bullets(self, items):
        self.set_font("Helvetica", size=9.5)
        for item in items:
            self._mc(f"- {item}")
        self.ln(0.5)

    def atom(self, word: str, kid: str, strict: str = "", example: str = ""):
        self.set_font("Helvetica", "B", 9.5)
        self._mc(word)
        self.set_font("Helvetica", size=9.5)
        self._mc(f"Kid: {kid}")
        if strict:
            self._mc(f"Strict: {strict}")
        if example:
            self.set_font("Helvetica", "I", 8.5)
            self.set_text_color(55, 55, 55)
            self._mc(f"Example: {example}")
            self.set_text_color(0, 0, 0)
        self.ln(0.8)


def write_pdf(filename: str, short: str, build) -> Path:
    pdf = StudyPDF(short)
    build(pdf)
    OUT.mkdir(parents=True, exist_ok=True)
    ART.mkdir(parents=True, exist_ok=True)
    path = OUT / filename
    pdf.output(str(path))
    (ART / filename).write_bytes(path.read_bytes())
    return path


def build_18(pdf: StudyPDF):
    pdf.title_block(
        "Layer 0 Glossary - Every Fancy Word, Kid-Plain",
        "If a word shows up anywhere in the study pack, it must be here. "
        "Kid line first (elementary). Strict line second (clearance-accurate). "
        "No tribal leftovers. Missing word = bug in this doc, not in you.",
        "Source: Master glossary for Action OS / Gate. Read before 01-17. Replaces thin atom sheets.",
    )

    pdf.section("How to use")
    pdf.para(
        "1) Read the kid line out loud. 2) Check the strict line. 3) Give the example from memory. "
        "If you need another Gate word to explain it, that other word is not owned yet - look it up here first."
    )
    pdf.para(
        "Story seed: A computer can press 'send money.' That does not mean it is allowed. "
        "Some sends cannot be undone like taking back a spilled cup of juice. "
        "Gate is the grown-up at the door who says stop or go - and keeps a note a stranger can read."
    )

    # ---- WORLD ----
    pdf.section("A. The world (before company words)")
    pdf.atom(
        "change",
        "Something is different than before.",
        "A state transition in the world or in a system.",
        "Account had $10. Now it has $0.",
    )
    pdf.atom(
        "act / write",
        "A specific thing the computer tries to do that changes the world.",
        "A concrete operation that mutates state - especially money leave, bind, release.",
        "Clicking 'release payout' / POST that sends the wire.",
    )
    pdf.atom(
        "side effect",
        "The real-world leftover of an act - not just words on a screen.",
        "An observable external consequence of executing a write.",
        "Money left the account; a policy became bound.",
    )
    pdf.atom(
        "reversible",
        "You can undo it easily, like erasing pencil.",
        "Change can be cheaply and fully undone.",
        "Editing a draft email you never sent.",
    )
    pdf.atom(
        "irreversible",
        "You cannot undo it easily. The juice already spilled.",
        "Change cannot be cheaply/fully undone; cost of reverse is high or impossible.",
        "Wire already sent. Peg out. Bind issued. Harm done.",
    )
    pdf.atom(
        "irreversibility",
        "The property of being one-way / hard to undo. The whole point of why we need a door.",
        "The constraint class Gate sits on: acts whose completion has lasting, hard-to-reverse effects.",
        "Once money left, 'sorry' does not put it back for free.",
    )
    pdf.atom(
        "finality",
        "The moment the change is basically done-for-real.",
        "The commit point after which the write is treated as completed/settled.",
        "Payment credited; transfer finished.",
    )
    pdf.atom(
        "effectuation",
        "The exact moment the system actually makes the irreversible thing happen.",
        "The boundary where clearance must still be real as the write completes.",
        "Right before the wire fires - not yesterday's green sticker.",
    )
    pdf.atom(
        "permission",
        "Allowed - not just possible.",
        "Normative authorization under live authority, policy, and proof.",
    )
    pdf.atom(
        "authority",
        "Who/what is allowed to say the path is on or off.",
        "The controlling power that can grant or revoke may for a path.",
    )
    pdf.atom(
        "policy",
        "The rules that say what is allowed.",
        "Machine-checkable constraints (caps, counterparties, intents) on a write.",
    )
    pdf.atom(
        "proof",
        "Something another kid can check - not 'because I said so.'",
        "Evidence a third party can verify without trusting your narrative alone.",
    )
    pdf.atom(
        "receipt",
        "A note of what was decided or stopped.",
        "Checkable record of a decision/halt bound to what was asked.",
    )
    pdf.atom(
        "invariant",
        "A rule that must always stay true - like 'never leave the stove on.'",
        "A property that must hold on every path (e.g. write_executed false on Gate clearance).",
    )

    # ---- CAN MAY ----
    pdf.section("B. Can vs may")
    pdf.atom(
        "can",
        "Able to do it. The button works. The keys exist.",
        "Capability: the system is able to perform the write.",
        "Payroll software can wire everyone today.",
    )
    pdf.atom(
        "may",
        "Allowed to do it right now under the rules.",
        "Permission: write may complete under live authority, policy, and proof.",
        "Only this payout, this person, this approval, now.",
    )
    pdf.atom(
        "can != may",
        "Able is not allowed. Biggest law in kid words.",
        "Ability is not permission. Diligence finds where can still completes without may.",
    )
    pdf.atom(
        "justified",
        "There is a good enough reason under the rules - not a vibe.",
        "Epistemic/policy adequacy to allow irreversible commitment.",
    )
    pdf.atom(
        "bypass",
        "A sneaky second door that skips the stop sign.",
        "Any alternate path that completes the write without the mouth's permit.",
        "Admin UI that pays while Gate says DEAD.",
    )

    # ---- STOP GO ----
    pdf.section("C. Stop / go words")
    pdf.atom(
        "DENY",
        "STOP. The dangerous send must not finish. Money stays.",
        "The irreversible write must not complete; the path halts with no quiet success. Not a mood; not a badge with another door open.",
        "Payout refused; receipt shows the halt.",
    )
    pdf.atom(
        "HOLD",
        "Pause. Wait for a grown-up check. Not yes.",
        "Defer completion pending review; write does not complete while HOLD is in force.",
    )
    pdf.atom(
        "ALLOW / GO / ACT (signal yes)",
        "Conditions look okay to proceed - still not the same as money already gone.",
        "Permission signal that path may proceed under current checks; distinct from execution.",
    )
    pdf.atom(
        "NO_GO",
        "Prefinality's hard no - do not sign/send.",
        "Evaluate decision: fail closed; do not commit the transfer.",
    )
    pdf.atom(
        "BLOCK",
        "Velaru-style: proof rail says no / blocked.",
        "Proof/fuse rail refusal (ALLOW/BLOCK language on Velaru).",
    )
    pdf.atom(
        "halt",
        "Stop this path now.",
        "Abort processing of the write path; typically paired with DENY under uncertainty/refusal.",
    )
    pdf.atom(
        "fail-closed",
        "If unsure or broken: STOP. Never guess yes.",
        "Uncertainty/timeout/missing proof => DENY/halt. Unreachable is not LIVE.",
        "Velaru silent -> stop write.",
    )
    pdf.atom(
        "fail-open",
        "If unsure: let it through (dangerous for money).",
        "Uncertainty treated as allow - the failure mode Gate refuses.",
    )
    pdf.atom(
        "soft-yes",
        "Fake yes from panic, manners, or a broken check.",
        "Treating politeness/panic/broken verification as permission.",
    )
    pdf.atom(
        "UNREACHABLE",
        "We could not talk to the checker - so we STOP, we do not invent LIVE.",
        "Upstream/timeout state that must fail closed.",
    )

    # ---- STATES ----
    pdf.section("D. On/off authority")
    pdf.atom(
        "LIVE",
        "The switch is ON for this path.",
        "Fuse/authority currently on; write may be considered under mouth rules.",
    )
    pdf.atom(
        "DEAD",
        "The switch is OFF. Dangerous send must not finish.",
        "Fuse/authority off; irreversible write must not complete.",
    )
    pdf.atom(
        "CHARGE",
        "The only special key that turns OFF back to ON.",
        "Sole allowed regime-change DEAD -> LIVE. Not dashboard flip. Not Slack okay.",
    )
    pdf.atom(
        "fuse",
        "The ON/OFF object you check before acting.",
        "Authority object hopped/looked up for LIVE/DEAD/verdict.",
    )
    pdf.atom(
        "hop",
        "Ask the fuse right now: are we LIVE?",
        "A check/request against the fuse engine for current verdict/state.",
    )
    pdf.atom(
        "verdict",
        "The yes/no answer from the fuse check.",
        "Boolean/result from hop used in clearance decisions.",
    )
    pdf.atom(
        "quorum",
        "More than one required yes - not one buddy alone.",
        "Structured multi-party/policy requirement for LIVE; not charismatic single key.",
    )
    pdf.atom(
        "webhook",
        "A computer calls your computer when something happens (like CHARGE arrives).",
        "HTTP callback delivering an event to your system.",
    )

    # ---- CLEARANCE EXEC ----
    pdf.section("E. Saying yes vs doing the thing")
    pdf.atom(
        "clearance",
        "Permission check: 'Are we allowed right now?'",
        "Decision that the write may proceed; not the write itself.",
    )
    pdf.atom(
        "execution",
        "Actually doing the irreversible thing.",
        "Performing the write (money moves, bind commits, release fires).",
    )
    pdf.atom(
        "clearance != execution",
        "Teacher saying 'you may leave' is not the same as you already left the building.",
        "Gate may permit; exclusive edge executes. write_executed false on Gate clearance.",
    )
    pdf.atom(
        "write_executed",
        "Flag: the irreversible thing really ran.",
        "Boolean that the side effect completed. Must stay false on Gate clearance path.",
    )
    pdf.atom(
        "acted / clearance_allows",
        "Gate's 'you may proceed' signal - still not money gone.",
        "Clearance permit fields; must not be confused with write_executed.",
    )
    pdf.atom(
        "mouth",
        "The door between 'can' and 'may' on the dangerous act.",
        "Permission seat on the irreversible write.",
    )
    pdf.atom(
        "exclusive edge / exclusive door",
        "The only door allowed to do the real send after permit.",
        "Single non-bypassable execution path after valid clearance.",
    )
    pdf.atom(
        "weld",
        "Bolting that exclusive door onto a real path so it cannot be skipped.",
        "Binding the mouth onto a concrete irreversible write path with no side door.",
    )
    pdf.atom(
        "worker (Cloudflare worker)",
        "A tiny program that stands in front of the real website/action and checks Gate first.",
        "Edge compute that asks /v1/act before fetch/origin; may set write-executed after success.",
    )
    pdf.atom(
        "origin",
        "The real place that does the action after the door says okay.",
        "Upstream service/request that performs the side effect after permit.",
    )

    # ---- CLEAR ----
    pdf.section("F. Clear, Prefinality, reconstruct")
    pdf.atom(
        "Clear",
        "At the important moment, permission is real and checkable - not a sticker.",
        "At effectuation: proof reconstructs as presented AND authority is LIVE.",
    )
    pdf.atom(
        "reconstruct",
        "A stranger can rebuild and check the proof.",
        "Independent rebuild/verify of presented evidence; required for Clear.",
    )
    pdf.atom(
        "Clear <=> reconstruct",
        "If you cannot rebuild it, it is not Clear.",
        "Biconditional: Clear iff reconstructable presented proof AND LIVE.",
    )
    pdf.atom(
        "Prefinality",
        "Check GO/NO_GO before the irreversible finish line.",
        "Doctrine/machinery inside Gate: evaluate before finality; not a sister company.",
    )
    pdf.atom(
        "PRI (pre-irreversibility inhibition)",
        "Build the STOP into the machine before the one-way act finishes.",
        "Architectural restraint: execute iff LIVE and justified; else DENY; CHARGE-only reopen.",
    )
    pdf.atom(
        "evaluate",
        "Ask Prefinality for GO/NO_GO/HOLD on this transfer.",
        "API/function that returns decision + receipt bound to transfer fingerprint.",
    )
    pdf.atom(
        "verify",
        "Check that a receipt/proof is real and still valid.",
        "Validation path for receipt/JWT/fuse proof a stranger can use.",
    )
    pdf.atom(
        "fingerprint",
        "A unique stamp of exactly which write was approved.",
        "Hash over canonical fields of the write/transfer so tickets cannot authorize a different act.",
    )
    pdf.atom(
        "JWT / signed receipt",
        "A sealed note the computer signed so others can check it was not forged.",
        "Cryptographically signed token/receipt bound to decision + fingerprint + expiry.",
    )
    pdf.atom(
        "TTL",
        "Time limit - after that, the ticket/note is too old.",
        "Time-to-live; expired grants must not spend.",
    )
    pdf.atom(
        "rail",
        "Which payment/transfer track (like different train lines).",
        "Adapter class for finality (e.g. x402 agent wallet, rtp instant fiat).",
    )
    pdf.atom(
        "x402",
        "A rail where an agent wallet might sign - check before sign.",
        "Prefinality adapter: before_wallet_sign style hook.",
    )
    pdf.atom(
        "RTP / instant fiat rail",
        "Fast bank-like credit path - check before the payment order.",
        "Prefinality adapter before payment_order / FedNow-class credit.",
    )
    pdf.atom(
        "mandate",
        "The rules packet for this transfer (caps, expected payee, etc.).",
        "Policy inputs to evaluate (max_amount, expected counterparty, ceilings).",
    )

    # ---- TICKETS ----
    pdf.section("G. Married write / tickets")
    pdf.atom(
        "married write",
        "Permission glued to one exact action - not a free pass for anything.",
        "Authorization bound to one spend fingerprint (method+path+job+kind).",
    )
    pdf.atom(
        "ticket",
        "A short, one-time permission slip for that exact action.",
        "Short-lived single-use grant redeemable only for the fingerprinted write.",
    )
    pdf.atom(
        "redeem",
        "Use up the ticket while showing the same action.",
        "Atomic consume of ticket presenting matching write; fail closed on mismatch/replay/stale.",
    )
    pdf.atom(
        "single-use",
        "One time only. Replay is cheating.",
        "Ticket cannot be successfully redeemed twice.",
    )
    pdf.atom(
        "stale hop / museum hop",
        "An old 'yes' that can no longer spend - like yesterday's hall pass.",
        "Prior LIVE/hop without fresh ticket cannot authorize spend; demo/old hop is museum.",
    )
    pdf.atom(
        "museum",
        "Looks real, cannot authorize the live dangerous send anymore.",
        "Demo or expired hop/proof without spend power.",
    )
    pdf.atom(
        "TOCTOU (time gap bug) - plain",
        "Checked okay at time A, did something else dangerous at time B.",
        "Time-of-check to time-of-use gap; married tickets exist to close it.",
    )
    pdf.atom(
        "license fuse / parent LIVE",
        "If the parent permission dies, kids cannot outlive it.",
        "Parent authority must be LIVE; children_cannot_outlive_parent.",
    )

    # ---- COMPANY ----
    pdf.section("H. Company / family / honesty")
    pdf.atom(
        "Nisaba / Action OS",
        "The company that sits on permission for irreversible acts.",
        "Firm whose scarcity is DENY that holds + stranger-openable receipt - not narrative.",
    )
    pdf.atom(
        "Gate",
        "The mouth: does the irreversible write complete?",
        "Clearance mouth (/v1/act, CHARGE, weld) - clearance not execution.",
    )
    pdf.atom(
        "Erra",
        "Should we act? Signal ACT/HOLD.",
        "Signal rail in the family map.",
    )
    pdf.atom(
        "Velaru",
        "Did we commit correctly? Proof ALLOW/BLOCK + fuse/verify.",
        "Proof rail; stranger verify surface.",
    )
    pdf.atom(
        "Verra",
        "Did both rails clear before bind?",
        "Action-session rail.",
    )
    pdf.atom(
        "Mishara",
        "Was a person harmed?",
        "Consumer harm path rail.",
    )
    pdf.atom(
        "scarcity (Nisaba)",
        "The valuable thing is a real STOP that holds - not a speech.",
        "Product scarcity = DENY/DEAD that holds, not storytelling.",
    )
    pdf.atom(
        "stranger-openable",
        "Someone outside your team can open the proof.",
        "Verification without logging into your narrative/trust boundary.",
    )
    pdf.atom(
        "their_production",
        "Honesty bit: only true when a real customer's path is exclusively welded.",
        "False until third-party exclusive production weld recorded; demos stay demos.",
    )
    pdf.atom(
        "dogfood",
        "You try your own product on yourself first.",
        "First-party weld/record that lifts readiness but does not flip their_production.",
    )
    pdf.atom(
        "cosplay",
        "Dressing up like production/clearance without the real door.",
        "Claiming force/production/contracts without weld/receipts.",
    )
    pdf.atom(
        "Tier-S / coordinators",
        "Highest serious continuity rooms - we contribute mouth, we do not own their guns.",
        "Contribution altitude under global coordinators; no monopoly ownership claims.",
    )
    pdf.atom(
        "C2",
        "Command-and-control of force systems - state monopoly; we are not that.",
        "Military/state command layer; out of ownership scope.",
    )
    pdf.atom(
        "driver node vs hub",
        "Hold the real lever on the act - not the busy billboard.",
        "Controllability: weld irreversible edges; hub dashboards are not drivers.",
    )

    # ---- MONEY SKUS ----
    pdf.section("I. Money faces / SKUs")
    pdf.atom(
        "SKU",
        "A named thing you sell with a price.",
        "Sellable product unit.",
    )
    pdf.atom(
        "diligence",
        "Paid homework: find where dangerous sends can still happen without may.",
        "$2,500 deposit SKU - written may-gap find; not a weld.",
    )
    pdf.atom(
        "deposit / DEPOSIT ask",
        "Money due now to start the paid find.",
        "Upfront payment that triggers diligence delivery clock.",
    )
    pdf.atom(
        "Bind Room",
        "Paid pack of examiner papers + halt proof links.",
        "$1,750 SKU - officer pack + stranger-openable halt appendix; not a weld.",
    )
    pdf.atom(
        "operator / register",
        "Human doors to commit/weld or register infrastructure fees.",
        "Surfaces for weld checkout and non-SaaS fee registration.",
    )
    pdf.atom(
        "bps",
        "Tiny fee slices (basis points) - pricing for authority dissipation, not SaaS seats.",
        "Basis points on flow; infrastructure fee framing.",
    )
    pdf.atom(
        "Clear (quit trigger sense)",
        "Paid diligence or Bind money that actually cleared - not a polite reply.",
        "External receipt of paid SKU; replies are not Clear.",
    )

    # ---- SYSTEMS LITERACY ----
    pdf.section("J. Computer words used in the pack")
    pdf.atom(
        "API",
        "A menu of things one computer lets another computer ask for.",
        "Application programming interface - machine-callable operations.",
    )
    pdf.atom(
        "HTTP",
        "How browsers/servers send asks and answers.",
        "Request/response protocol on the web.",
    )
    pdf.atom(
        "GET",
        "Please show/read this.",
        "HTTP method for read/retrieve.",
    )
    pdf.atom(
        "POST",
        "Please do/submit this change.",
        "HTTP method often used to submit/act.",
    )
    pdf.atom(
        "URL / endpoint / route",
        "The address of a specific door on the server.",
        "Path that maps to handler code (/v1/act, /diligence).",
    )
    pdf.atom(
        "JSON",
        "Structured text computers exchange - keys and values.",
        "Data format for API bodies.",
    )
    pdf.atom(
        "environment variable",
        "Secret/settings kept outside the code (keys, public URL).",
        "Process config/secrets injection; never commit live secrets.",
    )
    pdf.atom(
        "DNS",
        "Phone book from name to computer address.",
        "Domain name resolution.",
    )
    pdf.atom(
        "timeout",
        "Waited too long - treat as broken, fail closed.",
        "Exceeded wait bound; must not become soft LIVE.",
    )
    pdf.atom(
        "5xx / 4xx / 2xx",
        "Server broken / you asked wrong / mostly okay.",
        "HTTP status classes.",
    )
    pdf.atom(
        "PII",
        "Personal private person info - Gate should refuse holding it on PAS paths.",
        "Personally identifiable information.",
    )
    pdf.atom(
        "PAS",
        "Gate's bind/authority paths (policy action side) - still fail closed; no PII dump.",
        "Product/action surface namespace for bind-ticket style controls.",
    )
    pdf.atom(
        "SPF / DKIM / DMARC",
        "Email authenticity locks so others cannot easily forge your From address.",
        "DNS email authentication suite for outbound trust.",
    )

    # ---- BIND ROOM DIALECT ----
    pdf.section("K. Bind Room buyer dialect (SKU words - not Layer-0 physics)")
    pdf.para(
        "These appear in doc 08. They are insurance/compliance shop words. "
        "Learn them as buyer language after atoms - they are not the physics of DENY."
    )
    pdf.atom(
        "SERFF",
        "A filing system insurers use to submit docs to regulators.",
        "System for Electronic Rates & Forms Filing - shapes officer pack length/format talk.",
    )
    pdf.atom(
        "NYDFS",
        "New York financial regulator letters/rules buyers cite.",
        "NY Department of Financial Services circulars (e.g. board oversight expectations).",
    )
    pdf.atom(
        "ECDIS",
        "Their phrase for algorithms/tools that can discriminate if badly governed.",
        "Buyer vocabulary in Section 5 governing principles text.",
    )
    pdf.atom(
        "PolicyCenter",
        "A common insurance system where bind/issue writes happen.",
        "Guidewire-class policy admin; hop-before-bind story lives here.",
    )
    pdf.atom(
        "CUO",
        "Chief Underwriting Officer - senior insurance buyer/exam audience.",
        "Title often receiving Bind Room packaging.",
    )
    pdf.atom(
        "officer pack / appendix B",
        "Short official booklet + on-request list of verify links per bind event.",
        "Bind Room artifact pair examiners take.",
    )

    # ---- DRILLS ----
    pdf.section("L. Elementary teach-back (pass/fail)")
    pdf.bullets(
        [
            "What is irreversibility? (one-way / hard to undo)",
            "What is DENY? (dangerous send must not finish)",
            "What is can vs may?",
            "What is clearance vs execution?",
            "What is Clear? (rebuildable proof + still LIVE at the moment)",
            "What is a ticket vs a hop?",
            "What is their_production?",
            "Pick any fancy word from another PDF and find it here. If missing, that is a bug - tell the agent.",
        ]
    )
    pdf.section("M. Missing-word rule")
    pdf.para(
        "This glossary is supposed to be complete for the study pack. "
        "If you meet a technical/fancy word not defined here, stop. Do not guess from vibes. "
        "Add it here before continuing. Layer 0 means no mishaps."
    )


def build_00(pdf: StudyPDF):
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf._mc("Nisaba Action OS - Study Pack", 6.5)
    pdf.ln(1)
    pdf.set_font("Helvetica", size=9.5)
    pdf._mc("Teaching docs first. Code dumps quarantined. Glossary is law.")
    pdf.ln(0.5)
    pdf.set_font("Helvetica", "I", 8.5)
    pdf.set_text_color(70, 70, 70)
    pdf._mc("Source: gate/study-pdfs/  |  reference dumps: gate/study-pdfs/reference/")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(240, 240, 240)
    pdf.multi_cell(
        0,
        4.5,
        ascii(
            "HARD RULE: Start at 18 (full kid-plain glossary). "
            "Every fancy word must be defined there - including irreversibility. "
            "04-07/10 code dumps are REFERENCE ONLY. Cash first (Friday send)."
        ),
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
        fill=True,
    )
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 11)
    pdf._mc("Suggested path", 5.5)
    pdf.set_font("Helvetica", size=9.5)
    for item in [
        "18 (glossary) -> 11 -> 01 -> 02 -> 03 -> 14 -> 08 -> 09 -> 04 -> 05 -> 06 -> 07 -> 10 -> 15-17 -> 12",
        "If a word is missing from 18, that is a pack bug - expand 18 before guessing",
    ]:
        pdf._mc(f"- {item}")
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 11)
    pdf._mc("Document list", 5.5)
    pdf.set_font("Helvetica", size=9.5)
    for item in [
        "18  Layer 0 glossary - START HERE (elementary + strict)",
        "11  Mouth literacy",
        "01-03  Doctrine teaching",
        "04-07  Mouth teaching (code in reference/)",
        "08  Bind Room SKU/ops",
        "09  Friday send pack",
        "10  Production honesty teaching",
        "12-17  Map literacy + foundations + general",
    ]:
        pdf._mc(f"- {item}")


def main():
    p = write_pdf("18-layer-0-atoms.pdf", "18 Layer 0 glossary", build_18)
    p0 = write_pdf("00-README-study-order.pdf", "00 Study pack index", build_00)
    print(f"wrote {p} pages~ size={p.stat().st_size}")
    print(f"wrote {p0} size={p0.stat().st_size}")
    from pypdf import PdfReader

    r = PdfReader(str(p))
    text = "\n".join((pg.extract_text() or "") for pg in r.pages)
    for needle in [
        "irreversibility",
        "DENY",
        "Prefinality",
        "married write",
        "their_production",
        "SERFF",
        "fail-closed",
        "fingerprint",
        "TOCTOU",
    ]:
        print(needle, "OK" if needle in text else "MISSING")
    print("pages", len(r.pages), "chars", len(text))


if __name__ == "__main__":
    main()
