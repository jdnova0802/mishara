#!/usr/bin/env python3
"""Generate Gate-tied general subject study PDFs (14-17) and refresh 00 index."""

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
    return path


def build_14(pdf: StudyPDF):
    pdf.title_block(
        "Cash & Clearance Arithmetic",
        "Money math that changes Friday decisions. Not textbook finance - the numbers that keep you honest about wage era, deposit, and quit trigger.",
        "Source: General subject pack (Gate-tied) - companion to docs 08, 09",
    )
    pdf.section("One sentence")
    pdf.para(
        "Cash arithmetic is how you refuse fantasy runway: every dollar either ends wage era or it is theater."
    )
    pdf.section("The SKUs that matter")
    pdf.bullets(
        [
            "Diligence deposit: $2,500 due now -> 72h written find on may-gaps. Review band often quoted $5k-$8k after deposit - do not invent higher without a real seat.",
            "Bind Room: $1,750 - examiner pack / stranger-openable halt artifacts. Not a weld.",
            "Quit trigger (locked): paid Clear - $2,500 diligence OR $1,750 Bind. Replies are not Clear.",
            "Operator / register / weld: fortune lane later. Do not budget it as this month's rent.",
        ]
    )
    pdf.section("Gross vs what hits the account")
    pdf.para(
        "Stripe (card) typically takes about 2.9% + $0.30 per successful charge in the US. Always check your Dashboard - numbers drift by country and method."
    )
    pdf.bullets(
        [
            "$2,500 diligence ~= $2,500 - (0.029x2500 + 0.30) ~= $2,427 net before tax/tooling.",
            "$1,750 Bind ~= $1,750 - (0.029x1750 + 0.30) ~= $1,699 net.",
            "Two diligence Clears ~= ~$4,850 net - enough to feel surplus start, not enough to cosplay holdco.",
            "Render / domain / tools (~$30-$50) are not optional if the mouth is dark. Pay the surface before you mourn fee drag.",
        ]
    )
    pdf.section("Wage-era burn (honest)")
    pdf.bullets(
        [
            "Amazon/warehouse take-home ~$470/wk is the floor you are escaping - not a personality.",
            "Weekly burn for Gate while employed should stay tiny: hosting + one tool, not lifestyle.",
            "Do not quit on pipeline vibes. Quit on paid Clear only.",
            "If net after fees cannot cover a month of living without wage, you are still in wage era. Say that out loud.",
        ]
    )
    pdf.section("Unit economics of one send")
    pdf.bullets(
        [
            "Cost of a tight send: minutes + reputation. Spray of 40 sludge emails has negative unit economics.",
            "Quality pack (~20-25) beats volume: each entity should have a specific irreversible write named.",
            "Expected value of one DEPOSIT ask is not reply rate - it is probability of paid Clear x net fee.",
            "One paid Clear beats fifty 'interesting, circle back' threads.",
        ]
    )
    pdf.section("Deposit vs review vs weld")
    pdf.labeled(
        "Deposit",
        "Money now that buys a defined find. Scarcity signal. Your Friday product.",
    )
    pdf.labeled(
        "Review",
        "Follow-on if the find matters. Do not sell it as free after soft chat.",
    )
    pdf.labeled(
        "Weld / exclusive",
        "Fortune path when a real irreversible mouth sits exclusive. Not the first invoice you chase this week.",
    )
    pdf.section("Tax and entity (floor, not CPA advice)")
    pdf.bullets(
        [
            "Nisaba LLC receives the money - keep personal and LLC separate in your head and your bank.",
            "Set aside a rough tax slice of net (often ~25-30% as a crude personal buffer until a real accountant). Better than spending gross like it is free.",
            "This is not tax advice. It is anti-delusion: Clear cash is not 100% spendable lifestyle.",
        ]
    )
    pdf.section("Retrieval drill")
    pdf.bullets(
        [
            "Net of one $2,500 after ~2.9%+$0.30.",
            "Quit trigger amounts - both of them.",
            "Why replies do not count as Clear.",
            "Why fee drag does not excuse skipping Render.",
        ]
    )
    pdf.section("What this is not")
    pdf.bullets(
        [
            "Not MBA valuation theater",
            "Not permission to delay Friday outbound until you finish a finance book",
            "Not claiming revenue you have not collected",
        ]
    )


def build_15(pdf: StudyPDF):
    pdf.title_block(
        "Logic & Irreversible Acts",
        "Civilian Prefinality: how to think in states, denies, and writes that cannot cheaply undo. This is the general subject under Gate's mouth.",
        "Source: General subject pack (Gate-tied) - companion to docs 01, 03, 06, 11",
    )
    pdf.section("One sentence")
    pdf.para(
        "Logic for Gate is not debate club - it is: under uncertainty, the irreversible write must not complete."
    )
    pdf.section("Primitives")
    pdf.labeled(
        "Proposition",
        "A claim that is true or false in a context (fuse is LIVE; ticket is unspent).",
    )
    pdf.labeled(
        "Implication",
        "If A then B. If fuse DEAD -> write must not complete.",
    )
    pdf.labeled(
        "Necessary vs sufficient",
        "LIVE may be necessary for spend and still not sufficient without a matching ticket fingerprint.",
    )
    pdf.labeled(
        "Contradiction",
        "Claiming Clear while reconstruction fails. Soft-yes under unknown is a contradiction with fail-closed.",
    )
    pdf.labeled(
        "Invariant",
        "A law that must hold on every path (write_executed false on Gate clearance; CHARGE-only resurrect).",
    )
    pdf.section("Fail-closed as default")
    pdf.para(
        "Under missing proof, timeout, or broken link to authority: DENY / HOLD. Never invent LIVE because the dashboard felt friendly."
    )
    pdf.bullets(
        [
            "Unknown != allow",
            "Retry on money-leave can duplicate an irreversible act - treat retries as dangerous until proven idempotent",
            "Admin flip is not CHARGE",
        ]
    )
    pdf.section("States, not vibes")
    pdf.bullets(
        [
            "Name the state: LIVE / DEAD / presented / consumed / halted.",
            "Name the transition: what event alone moves DEAD -> LIVE?",
            "Name the side effect: does this step leave money, bind policy, or only return a receipt?",
            "If you cannot name state + transition + side effect, you do not understand the act yet.",
        ]
    )
    pdf.section("Irreversible vs reversible")
    pdf.bullets(
        [
            "Reversible: edit a draft email, regenerate a PDF, restart a demo hop.",
            "Irreversible (or costly to reverse): wire out, peg out, bind coverage, delete with no backup, agent tool that spends.",
            "Gate sits on permission for the irreversible class. Diligence asks where can still completes without may.",
        ]
    )
    pdf.section("Clear <=> reconstruct (logic form)")
    pdf.para(
        "At the effectuation boundary: Clear if and only if the presented proof can be reconstructed AND the authority is LIVE. A GO sticker without reconstructability is not Clear - it is cosplay."
    )
    pdf.section("Practice drills")
    pdf.bullets(
        [
            "Write each of the four laws as IF ... ELSE DENY.",
            "Take one payout path and list: states, who can say may, who executes the write, what stranger can open.",
            "Find one place in your own life where can != may (keys exist, permission missing).",
        ]
    )
    pdf.section("What this is not")
    pdf.bullets(
        [
            "Not symbolic logic homework for its own sake",
            "Not philosophy that never names a write",
            "Not soft ethics that replaces DENY with discussion",
        ]
    )


def build_16(pdf: StudyPDF):
    pdf.title_block(
        "Read the System",
        "Enough systems literacy to deploy, debug honesty, and not brick the mouth - without becoming a full engineer overnight.",
        "Source: General subject pack (Gate-tied) - companion to docs 05, 10, 12",
    )
    pdf.section("One sentence")
    pdf.para(
        "A system is inputs -> state -> outputs -> side effects. Your job is to know which box the irreversible write lives in."
    )
    pdf.section("Request / response")
    pdf.bullets(
        [
            "Client asks (browser, curl, Stripe webhook). Server answers with status + body.",
            "2xx usually means success path. 4xx you/client problem. 5xx server broke - fail-closed territory.",
            "JSON body is structured claims. Read keys that name law: ok, halt, write_executed, their_production.",
        ]
    )
    pdf.section("Where config lives")
    pdf.bullets(
        [
            "Environment variables: secrets and public URL outside the code (Stripe keys, GATE_*, Render env).",
            "Never paste live secrets into a PDF, chat dump, or git commit.",
            "If checkout 404s or deposit fails, check: route deployed, price/payment link set, public URL correct.",
        ]
    )
    pdf.section("Deploy mental model")
    pdf.bullets(
        [
            "Code on a branch != live mouth. Merge + deploy + curl the URLs.",
            "Friday rule: diligence page, one-pager, offer.json, checkout must return success before sends.",
            "Museum demos can be up while their_production stays false. Honesty bit is part of the system.",
        ]
    )
    pdf.section("What broke? (triage order)")
    pdf.bullets(
        [
            "DNS / wrong host - are you hitting gate.velaru.xyz or a stale preview?",
            "Route missing - 404 means deploy or path wrong, not 'philosophy failed'.",
            "Env missing - Stripe/price unset often becomes soft failure or fallback link.",
            "Upstream timeout - Velaru/verify unreachable should DENY, not silent allow.",
            "Logic bug - invariant violated (write_executed true on clearance). Treat as severity max.",
        ]
    )
    pdf.section("Logs without drowning")
    pdf.bullets(
        [
            "Reproduce once with curl. Save status code + one JSON field that matters.",
            "Change one variable. Redeploy or restart. Curl again.",
            "If you cannot state expected vs actual in one sentence, you are not debugging yet.",
        ]
    )
    pdf.section("Minimal map for this week")
    pdf.bullets(
        [
            "GET /diligence - human money face",
            "GET /diligence/one-pager.txt - shareable claim",
            "GET /diligence/offer.json - machine offer",
            "Checkout / payment link - deposit path",
            "POST /v1/act - clearance ask (not the wire)",
            "Velaru verify - stranger-openable proof surface",
        ]
    )
    pdf.section("Retrieval drill")
    pdf.bullets(
        [
            "Define input, state, output, side effect for a payout.",
            "Explain why merge without deploy leaves outbound lying.",
            "List triage order when /diligence 404s.",
        ]
    )
    pdf.section("What this is not")
    pdf.bullets(
        [
            "Not a CS degree",
            "Not permission to rewrite the worker before Friday sends",
            "Not replacing doc 12 - this is systems; 12 is code-map",
        ]
    )


def build_17(pdf: StudyPDF):
    pdf.title_block(
        "Uncertainty Lite",
        "Base rates, false clears, and why one warm reply is not a pattern. Clearance talk without fake stats PhD.",
        "Source: General subject pack (Gate-tied) - companion to docs 06, 09, 13",
    )
    pdf.section("One sentence")
    pdf.para(
        "Uncertainty literacy is how you keep DENY sacred and stop mistaking noise for Clear."
    )
    pdf.section("Confidence vs proof")
    pdf.bullets(
        [
            "Confidence: how sure you feel. Cheap to inflate.",
            "Proof: what a stranger can reconstruct. Expensive and required for Clear.",
            "Soft-yes under panic is a failure mode - it converts uncertainty into fake may.",
        ]
    )
    pdf.section("Base rates (operator honesty)")
    pdf.bullets(
        [
            "Most cold outbound gets ignore. That is the base rate - design for it.",
            "A polite reply raises odds a little; it does not move the quit trigger.",
            "Paid deposit is a different species of event from 'interested'.",
            "Do not update your life plan on n=1 vibe. Update on money and reconstructable halt finds.",
        ]
    )
    pdf.section("False Clear / false DENY")
    pdf.labeled(
        "False Clear",
        "GO without reconstructable LIVE proof - sticker theater.",
    )
    pdf.labeled(
        "False DENY",
        "Halting forever because you refuse to measure. Also a failure - diligence exists to find real may-gaps, not to romanticize freeze.",
    )
    pdf.para(
        "Gate bias under uncertainty: prefer false DENY on the irreversible write over false Clear. Then use paid work to sharpen the real map."
    )
    pdf.section("Signals ranked (Friday)")
    pdf.bullets(
        [
            "Tier 0: ignore / bounce - expected",
            "Tier 1: redirect to right seat - useful routing, not Clear",
            "Tier 2: substantive question on the write - engage async 8-9",
            "Tier 3: deposit paid - Clear for quit math",
            "Never promote Tier 1-2 into Tier 3 in your head",
        ]
    )
    pdf.section("Sample size without cosplay")
    pdf.bullets(
        [
            "20-25 tight sends teach more than 40 sludge.",
            "After a batch: count deposits, not compliments.",
            "If zero deposits, change specificity of the irreversible write named - not your personality narrative.",
        ]
    )
    pdf.section("Risk language with operators")
    pdf.bullets(
        [
            "Say: where can the write complete without may?",
            "Say: stranger-openable receipt / halt artifact.",
            "Do not say: we eliminate all risk. You map and hold denial on a path.",
            "Do not invent percentages you did not measure.",
        ]
    )
    pdf.section("Retrieval drill")
    pdf.bullets(
        [
            "Confidence vs proof in one money example.",
            "Why one reply is not quit fuel.",
            "False Clear vs false DENY - which does Gate prefer on the wire, and why?",
            "Rank Friday signals Tier 0-3 from memory.",
        ]
    )
    pdf.section("What this is not")
    pdf.bullets(
        [
            "Not Bayesian textbook completionism",
            "Not permission to delay sends until you 'feel ready'",
            "Not vibes replacing Prefinality",
        ]
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
        "Read in order. After each document, close it and retrieve from memory. Cash first (Friday send). Depth in parallel (15-20 min/day)."
    )
    pdf.section("The four laws")
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
            "01  SCIENCE - can/may and Tier-S contribution",
            "02  Action OS - company nature",
            "03  Science PRI - formal PRI and first weld",
            "04  Mouth mechanics - fuse, fail-closed, /v1/act",
            "05  Write edge - Cloudflare worker",
            "06  Prefinality - Clear before finality",
            "07  Married write - spend + tickets",
            "08  Bind Room - money face",
            "09  Friday send pack - outbound",
            "10  Production honesty - their_production",
            "11  Mouth literacy (NO CODE) - start here if code-anxious",
            "12  Code reading for Gate - map literacy",
            "13  Foundations trunk - layer-1 heart without textbook cosplay",
            "14  Cash & clearance arithmetic - GENERAL (Gate-tied)",
            "15  Logic & irreversible acts - GENERAL (Gate-tied)",
            "16  Read the system - GENERAL (Gate-tied)",
            "17  Uncertainty lite - GENERAL (Gate-tied)",
        ]
    )
    pdf.section("Suggested path if weak at code")
    pdf.bullets(
        [
            "11 -> 01 -> 02 -> 03 -> 08 -> 09 -> 12 -> 04 -> 05 -> 06 -> 07 -> 10 -> 13",
            "General subjects after mouth basics: 14 -> 15 -> 16 -> 17 (or 14 first if Friday money math is foggy)",
        ]
    )
    pdf.section("Near-term rule")
    pdf.para(
        "Deploy live. Send Friday pack. Quit on clear. Retrieve daily. Clearance rooms after surplus. General docs sharpen judgment - they do not replace DEPOSIT asks."
    )


def main():
    paths = [
        write_pdf("14-cash-clearance-arithmetic.pdf", "14 Cash & clearance arithmetic", build_14),
        write_pdf("15-logic-irreversible-acts.pdf", "15 Logic & irreversible acts", build_15),
        write_pdf("16-read-the-system.pdf", "16 Read the system", build_16),
        write_pdf("17-uncertainty-lite.pdf", "17 Uncertainty lite", build_17),
        write_pdf("00-README-study-order.pdf", "00 Study pack index", build_00),
    ]
    for p in paths:
        print(f"wrote {p} ({p.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
