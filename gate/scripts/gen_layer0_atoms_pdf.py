#!/usr/bin/env python3
"""Generate Layer-0 atoms study PDF + refresh index entry."""

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
        self.ln(3)

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

    def atom(self, word: str, definition: str, example: str = ""):
        self.set_font("Helvetica", "B", 10)
        self._mc(word)
        self.set_font("Helvetica", size=10)
        self._mc(definition)
        if example:
            self.set_font("Helvetica", "I", 9)
            self.set_text_color(50, 50, 50)
            self._mc(f"Example: {example}")
            self.set_text_color(0, 0, 0)
            self.set_font("Helvetica", size=10)
        self.ln(1)


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
        "Layer 0 Atoms - Every Word From Scratch",
        "Surgery on atoms. If a later doc uses a word, this page owns its definition. No tribal vocabulary. Middle-school plain, clearance-strict.",
        "Source: Layer-0 glossary for the Action OS mouth. Read this before 01-17 when jargon feels hollow.",
    )

    pdf.section("What Layer 0 means")
    pdf.para(
        "Layer 0 = the smallest real thing a word points at. Not 'sounds smart in a room.' Not Jensen-layer (using tools). Atom-layer: you can define it, give one money example, and say what must happen in the world."
    )
    pdf.para(
        "Rule: if you cannot define it without using another undefined Gate word, you do not own it yet. Come back here."
    )

    pdf.section("The world (before Gate words)")
    pdf.atom(
        "Change",
        "Something becomes different than it was.",
        "A balance goes from $1000 to $0.",
    )
    pdf.atom(
        "Act / write",
        "A specific change a system tries to make. In Gate talk, 'write' means the change that gets recorded or sent - especially money leaving, a policy binding, a release.",
        "POST that releases a payout. Button that wires funds.",
    )
    pdf.atom(
        "Reversible",
        "You can undo the change cheaply and fully (draft email, unsaved form).",
    )
    pdf.atom(
        "Irreversible",
        "You cannot undo it cheaply or fully. The world has moved. Money left. Policy bound. Harm done.",
        "Wire sent. Peg out. Bind issued. Agent tool spent.",
    )
    pdf.atom(
        "Permission",
        "It is allowed to complete - not merely possible.",
    )
    pdf.atom(
        "Proof",
        "Evidence another person can check without trusting your story alone.",
    )

    pdf.section("Can vs may (two atoms people mix up)")
    pdf.atom(
        "can",
        "The system is able to do the write. Keys exist. API works. Agent has the tool. Ability.",
        "Payroll software can send every employee a wire today.",
    )
    pdf.atom(
        "may",
        "The write is allowed to complete under live authority, policy, and proof. Permission.",
        "Only this payout, for this person, under this approval, right now, may leave.",
    )
    pdf.para(
        "Law in plain words: being able to do it is not the same as being allowed to do it. can != may."
    )

    pdf.section("Stop / go words (this is where DENY lives)")
    pdf.atom(
        "DENY",
        "DEFINITION: The irreversible write must not complete. The system stops that path. It does not quietly succeed. DENY is a real halt on the write - not a mood, not a meeting, not a red UI badge with a side door still open.",
        "Payout release is refused. Money stays. A receipt says the halt happened.",
    )
    pdf.atom(
        "What DENY is not",
        "Not 'we talked about risk.' Not 'dashboard shows red while another API still pays.' Not 'soft no' that becomes yes under pressure. If the write can still finish, you did not DENY.",
    )
    pdf.atom(
        "HOLD",
        "Pause for more check or human review. Not a full Clear. Not a silent yes. The write does not complete while HOLD is in force.",
    )
    pdf.atom(
        "ALLOW / GO / LIVE permit",
        "Signals that permission conditions are currently met for this path - still not the same as the money already leaving (see clearance vs execution).",
    )
    pdf.atom(
        "halt",
        "Stop processing this write path now. Closely tied to DENY under uncertainty or refusal.",
    )
    pdf.atom(
        "fail-closed",
        "If we are unsure, broken, timed out, or missing proof: DENY / halt. Never treat 'we couldn't check' as yes.",
        "Velaru does not answer -> stop the write. Do not guess LIVE.",
    )
    pdf.atom(
        "soft-yes",
        "A fake allow: panic, politeness, or broken check treated as permission. This is the failure mode fail-closed exists to kill.",
    )

    pdf.section("Authority states")
    pdf.atom(
        "LIVE",
        "The fuse / authority for this path is currently on - the write is allowed to be considered for completion under the mouth's rules.",
    )
    pdf.atom(
        "DEAD",
        "The fuse / authority is off. The irreversible write must not complete.",
    )
    pdf.atom(
        "CHARGE",
        "The only allowed way to turn DEAD back into LIVE. Not a dashboard flip. Not 'admin said okay in Slack.' A real regime-change packet the system accepts.",
    )
    pdf.atom(
        "fuse",
        "The live/dead switch object for a path - the thing you hop/check before acting.",
    )

    pdf.section("Clearance vs execution (two different jobs)")
    pdf.atom(
        "clearance",
        "A decision that the write may proceed (permission check). Clearance answers: is this allowed right now?",
    )
    pdf.atom(
        "execution",
        "Actually doing the irreversible write (money moves, bind commits, release fires).",
    )
    pdf.atom(
        "write_executed",
        "A flag meaning the irreversible write really ran. On Gate's clearance path this stays false - Gate is the mouth that permits or denies, not the wire itself.",
    )
    pdf.atom(
        "exclusive edge / weld / worker",
        "The one door that is allowed to run the write after a valid permit. If another door can still write, the mouth is fake.",
    )
    pdf.para(
        "Law in plain words: saying yes is not the same as money leaving. clearance != execution."
    )

    pdf.section("Clear and reconstruct")
    pdf.atom(
        "Clear (as a noun/event)",
        "At the moment that matters (before finality), permission is real: the proof matches what was presented AND authority is LIVE. Clear is not a vibe.",
    )
    pdf.atom(
        "reconstruct",
        "A stranger can rebuild and check the proof - not take your word. If it cannot be rebuilt, it is not Clear.",
    )
    pdf.atom(
        "receipt",
        "A checkable record of what was decided or what was halted.",
    )
    pdf.atom(
        "stranger-openable",
        "Someone outside your team can open the proof without logging into your story.",
    )
    pdf.para(
        "Law in plain words: Clear means you can rebuild the proof and it is still LIVE. Clear <=> reconstruct."
    )

    pdf.section("Money / honesty atoms")
    pdf.atom(
        "mouth",
        "The place permission sits on the irreversible write - the door between can and may.",
    )
    pdf.atom(
        "scarcity (for Nisaba)",
        "The valuable thing is a DENY that holds - not a speech about safety.",
    )
    pdf.atom(
        "museum",
        "A demo or old hop that looks real but cannot spend / cannot authorize the live write anymore.",
    )
    pdf.atom(
        "their_production",
        "Honesty flag: true only when a real third party's irreversible path is exclusively welded. False means demos are demos.",
    )
    pdf.atom(
        "diligence (SKU)",
        "Paid find: where can the irreversible write still complete without may. Deposit money for a written map - not a weld.",
    )
    pdf.atom(
        "Bind Room (SKU)",
        "Paid examiner artifacts / stranger-openable halt evidence pack - not a weld.",
    )

    pdf.section("Family questions (only after atoms above)")
    pdf.bullets(
        [
            "Erra: Should we act? (signal)",
            "Velaru: Did we commit correctly? (proof / fuse)",
            "Gate: Does the irreversible write complete? (mouth)",
            "Verra: Did both rails clear before bind?",
            "Mishara: Was a person harmed?",
        ]
    )

    pdf.section("Retrieval drill (blank page)")
    pdf.bullets(
        [
            "Define DENY without saying 'deny.'",
            "Give one money example of can without may.",
            "Why is fail-closed not the same as being mean?",
            "What alone turns DEAD into LIVE?",
            "Why can Gate say yes and money still not leave?",
            "What makes Clear different from a green sticker?",
        ]
    )

    pdf.section("How to use this with the other PDFs")
    pdf.para(
        "When 01-10 throw jargon at you, stop. Find the atom here. If the atom is missing, the other doc failed teaching - not you. Layer 0 first. Code dumps (04-07) are reference after you own the atoms."
    )


def build_00(pdf: StudyPDF):
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf._mc("Nisaba Action OS - Study Pack", 7)
    pdf.ln(2)
    pdf.set_font("Helvetica", size=10)
    pdf._mc("Readable study documents for the irreversible-write mouth.")
    pdf.ln(1)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(70, 70, 70)
    pdf._mc("Source: gate/study-pdfs/")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)
    pdf.section("How to use")
    pdf.para(
        "If words feel hollow, start at 18 (Layer 0 atoms). Then retrieve. Cash first (Friday send). Depth in parallel (15-20 min/day)."
    )
    pdf.section("The four laws (only after you can define each word)")
    pdf.bullets(
        [
            "can != may",
            "clearance != execution (write_executed false on Gate clearance)",
            "CHARGE-only resurrect (DEAD -> LIVE)",
            "Clear <=> reconstruct (presented AND LIVE)",
        ]
    )
    pdf.section("Document list")
    pdf.bullets(
        [
            "18  Layer 0 atoms - START HERE if jargon is undefined (DENY, LIVE, Clear, ...)",
            "01  SCIENCE - can/may and Tier-S contribution",
            "02  Action OS - company nature",
            "03  Science PRI - formal PRI and first weld",
            "04  Mouth mechanics - fuse, fail-closed, /v1/act (REFERENCE/code)",
            "05  Write edge - Cloudflare worker (REFERENCE/code)",
            "06  Prefinality - Clear before finality (REFERENCE-heavy)",
            "07  Married write - spend + tickets (REFERENCE/code)",
            "08  Bind Room - money face",
            "09  Friday send pack - outbound",
            "10  Production honesty - their_production",
            "11  Mouth literacy (NO CODE) - plain teaching after atoms",
            "12  Code reading for Gate - map literacy",
            "13  Foundations trunk - layer-1 heart without textbook cosplay",
            "14  Cash & clearance arithmetic - GENERAL (Gate-tied)",
            "15  Logic & irreversible acts - GENERAL (Gate-tied)",
            "16  Read the system - GENERAL (Gate-tied)",
            "17  Uncertainty lite - GENERAL (Gate-tied)",
        ]
    )
    pdf.section("Suggested path")
    pdf.bullets(
        [
            "Layer-0 path: 18 -> 11 -> 01 -> 02 -> 14 -> 08 -> 09 -> 15 -> 16 -> 17 -> 12 -> then code refs 04-07",
            "If weak at code: same as above; do not drown in 06/07 until atoms + 11 are blank-page solid",
        ]
    )
    pdf.section("Near-term rule")
    pdf.para(
        "Deploy live. Send Friday pack. Quit on clear. Own atoms before jargon. General docs sharpen judgment - they do not replace DEPOSIT asks."
    )


def main():
    p18 = write_pdf("18-layer-0-atoms.pdf", "18 Layer 0 atoms", build_18)
    p00 = write_pdf("00-README-study-order.pdf", "00 Study pack index", build_00)
    print(f"wrote {p18} ({p18.stat().st_size})")
    print(f"wrote {p00} ({p00.stat().st_size})")


if __name__ == "__main__":
    main()
