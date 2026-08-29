"""Named inventions — every subject, surgical, real.

Not a cleverer layer. Not a Satoshi myth. Each row is a claim a stranger
can point at in code, plus the Satoshi-shaped thing it outscales, plus
whether it is shipped, law, or still a weld.

Inventor stands. See inventor.py.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

try:
    from gate import inventor as inventor_mod
except ImportError:
    import inventor as inventor_mod

try:
    from gate import named_may as named_may_mod
except ImportError:
    import named_may as named_may_mod

SPEC = "nisaba-inventions-v1"

SATOSHI = {
    "invention": "Bearer digital scarcity + hidden founder",
    "primitives": (
        "digital signatures as ownership",
        "append-only timestamped ledger",
        "proof of work / longest chain as truth",
        "UTXO — the secret is the owner",
        "21M cap as monetary scarcity",
        "anonymity as capture-resistance",
    ),
    "ceiling": "Money that needs no name. Soft-yes on everything that is not money.",
    "could_not_cash": True,
    "outscaled_by": (
        "Gate Conformant™ + QIC is the cash latch — rent the padlock standard, "
        "meter every real commit, stay on the invoice. Satoshi gave the protocol away. "
        "Named permission outscales bearer cash on irreversible civic writes. "
        "Public inventor outscales hidden founder when the mouth must be accountable."
    ),
}

# subject → surgical invention. status: shipped | law | weld
INVENTIONS: tuple[dict[str, Any], ...] = (
    {
        "id": "gate_conformant",
        "subject": "standards",
        "name": "Gate Conformant™",
        "claim": (
            "The padlock standard for irreversible digital acts. Institutions rent "
            "the cert. Ghost Conformant is DENY. Not a sixth sibling."
        ),
        "satoshi": "A free protocol the inventor could not cash.",
        "heavier": (
            "ARM-shaped rent on the instruction set everyone needs to write "
            "irreversibly. World-shifting like HTTPS — seatbelts, not a new money. "
            "You stay on the invoice."
        ),
        "real": "conformant.py · /.well-known/conformant.json · /conformant · Exhibit J",
        "status": "weld",
        "cash": True,
        "tree": "mark on Gate — attaches to Gate + Velaru",
    },
    {
        "id": "heavier_than_conformant",
        "subject": "scale",
        "name": "Heavier than Conformant",
        "claim": (
            "The badge is PCI. Hosted redeem, agent employment, illocution, "
            "closing dependency, CHC — the write cannot exist without you."
        ),
        "satoshi": "A free protocol, then a cert culture that still cannot cash the founder.",
        "heavier": (
            "Soon is already coded. Medium is latch. Long is the ceiling. "
            "Conformant becomes the consolation SKU."
        ),
        "real": "heavier.py · /heavier · /.well-known/heavier.json",
        "status": "law",
        "cash": True,
        "tree": "attachments on Gate / Velaru / Mishara — not a sibling",
    },
    {
        "id": "qic_meter",
        "subject": "meter",
        "name": "Qualified irreversible commit",
        "claim": (
            "One server-side redeem consume + one irreversible write. "
            "Billable max(MAR, LAQ × per_QIC) stacked with 10 bps. $0 until Gate 1."
        ),
        "satoshi": "Block reward to anonymous miners. Inventor $0.",
        "heavier": (
            "The named HoldCo meters every real commit. Redeem already writes the "
            "spend map. The meter reads that map."
        ),
        "real": "qic.py · ticket redeem qic stamp · /.well-known/qic.json",
        "status": "shipped",
        "cash": True,
        "tree": "meter on Gate — stacked with register bps",
    },
    {
        "id": "public_inventor",
        "subject": "identity",
        "name": "Public inventor lock",
        "claim": "The throat has a legal name. Anonymity is not a feature of permission.",
        "satoshi": "Hidden founder so the protocol cannot be captured via a person.",
        "heavier": (
            "Bearer cash can be ownerless. A mouth that can halt bind, payout, "
            "or force cannot. Capture-resistance is stranger prove + named CHARGE "
            "outside the actor — not disappearance."
        ),
        "real": "inventor.py · /.well-known/inventor.json — Demond Davis, Nisaba LLC, 64/124,027",
        "status": "law",
    },
    {
        "id": "named_may",
        "subject": "money",
        "name": "Named may",
        "claim": "Consume-once permission bound to a public holder. The secret is not the owner.",
        "satoshi": "UTXO — anyone with the key spends.",
        "heavier": (
            "Cash can be bearer. Bind, payout, and release cannot. "
            "Token-only redeem is Satoshi-shaped. Named redeem is the throat."
        ),
        "real": "named_may.py · ticket issue/redeem holder_id · GATE_NAMED_MAY",
        "status": "law",
    },
    {
        "id": "may_throat",
        "subject": "speech",
        "name": "May as throat",
        "claim": "A command not in the shared now is not a command. Speech is not the act.",
        "satoshi": "Broadcast a signed tx — speech that is already the spend.",
        "heavier": "Hop is speech. Redeem is the act. LIVE hop cannot spend.",
        "real": "command_radiation.py · ticket.py · /uplink",
        "status": "shipped",
    },
    {
        "id": "redeem_defense",
        "subject": "agents",
        "name": "Agent redeem as defense",
        "claim": "Redeem is the only radiate verb. Same mouth as DENY. S03 after Gate 1.",
        "satoshi": "Anyone who can sign can spend; there is no separate radiate.",
        "heavier": "Defense is consume-once at the edge, not a mempool race.",
        "real": "POST /v1/pas/bind-ticket/redeem · spend protocol",
        "status": "shipped",
    },
    {
        "id": "exclusion",
        "subject": "evidence",
        "name": "Proof of exclusion",
        "claim": "No redeemed leaf for this job exists in the append-only spend map.",
        "satoshi": "Inclusion proof — this UTXO / this block is in the chain.",
        "heavier": "A signature on a HALT says we said no. Exclusion says the spend did not occur here.",
        "real": "exclusion.py · Laurie–Kasper neighbors · /.well-known/exclusion.json",
        "status": "shipped",
    },
    {
        "id": "shared_now",
        "subject": "time",
        "name": "Shared UTC now as law",
        "claim": "Missing or skewed now aborts radiation and does not consume the ticket.",
        "satoshi": "Block time is miner-chosen; finality is probabilistic depth.",
        "heavier": "Irreversible command has one international now (CGPM 2018). Skew is abort, not a fork.",
        "real": "command_radiation.check_now · max_skew_seconds",
        "status": "shipped",
    },
    {
        "id": "silence_dead",
        "subject": "death",
        "name": "Silence is DEAD",
        "claim": "Uncertainty and silence fail closed. Longest chain is not LIVE.",
        "satoshi": "Longest proof-of-work chain is truth; silence is just a quiet network.",
        "heavier": "Command loss timer: silence does not reset the vehicle. Soft-yes under panic is the failure mode.",
        "real": "OCSP-strict 503 · fuse DEAD · ticket not_after",
        "status": "shipped",
    },
    {
        "id": "charge_outside",
        "subject": "law",
        "name": "CHARGE outside the actor",
        "claim": "Actor may redeem. Actor may not resurrect. The no sits outside.",
        "satoshi": "Whoever holds the key can always spend again; there is no outside.",
        "heavier": "If the actor CHARGE themselves, the no was never outside. Quorum + stranger + coordinator.",
        "real": "charge_authority.py (gap: operator Stripe still inside) · science PRI quorum",
        "status": "weld",
    },
    {
        "id": "license_fuse",
        "subject": "inheritance",
        "name": "Children cannot outlive parent",
        "claim": "DEAD parent → children cannot redeem until CHARGE. DEAD→LIVE is CHARGE only.",
        "satoshi": "Keys fork; children of a wallet outlive the parent story.",
        "heavier": "Capability inheritance is mortal. Resurrection is not a dashboard flip.",
        "real": "license_fuse.py · license_id on tickets",
        "status": "shipped",
    },
    {
        "id": "inhabitant",
        "subject": "democracy",
        "name": "Inhabitant copy",
        "claim": "Yes spends a world. The someone who lives there did not have to ask.",
        "satoshi": "The ledger has owners. It has no inhabitants.",
        "heavier": "Unrepeatable harm is not a UTXO. The copy outlives the actor.",
        "real": "inhabitant.py · /inhabitant · /afterward",
        "status": "shipped",
    },
    {
        "id": "kappa",
        "subject": "settlement",
        "name": "κ permission-mass conservation",
        "claim": "M_total = M_cf + M_live. Restraint is measurable. Cutoff collapses W|W+1.",
        "satoshi": "Monetary mass is 21M. There is no coefficient for prevented spends.",
        "heavier": "Civilization's product is the prevented irreversible, not the cleared one.",
        "real": "kappa.py · schism · /.well-known/kappa.json",
        "status": "shipped",
    },
    {
        "id": "exclusive_door",
        "subject": "property",
        "name": "Exclusive door",
        "claim": "The act that never happens because there was no other door.",
        "satoshi": "Any node can broadcast; there is always another relay.",
        "heavier": "A bound no on a demo hop is a museum. Control is one welded write.",
        "real": "exclusive.py · /only · their_production false until weld",
        "status": "shipped",
    },
    {
        "id": "unuttered",
        "subject": "force",
        "name": "The Unuttered",
        "claim": "Some write-classes have no licensed throat. May assumes a mouth.",
        "satoshi": "Every signed value is money. There is no unmouthed class.",
        "heavier": "Nuclear C2, private PD, battlefield release — no throat for sale.",
        "real": "unison.unmouthed · SCIENCE.md state-only",
        "status": "law",
    },
    {
        "id": "pri",
        "subject": "physics",
        "name": "Pre-irreversibility inhibition",
        "claim": "execute iff LIVE ∧ justified; else DENY; bypass empty; CHARGE-only reopen.",
        "satoshi": "Valid signature + fee → the world moves. Justification is not a primitive.",
        "heavier": "Thermo: no perfect do(·). Intervention costs. Silent free yes is illegal.",
        "real": "science_pri.py · /.well-known/science-pri.json",
        "status": "shipped",
    },
    {
        "id": "payout_clear",
        "subject": "energy",
        "name": "Clear before wire — first driver",
        "claim": "First commercial weld is withdraw/payout. Grid shed is next, not first.",
        "satoshi": "First weld was money itself as the whole product.",
        "heavier": "Money-leave is the driver node. Grid and programs stay under coordinators.",
        "real": "/operator?write=withdraw · SCIENCE first_weld",
        "status": "weld",
    },
    {
        "id": "uplink",
        "subject": "space",
        "name": "Command radiation",
        "claim": "May this CLTU still be radiated, for this vehicle, in this now?",
        "satoshi": "A signed tx is already in space once broadcast.",
        "heavier": "DSN aborts if monitors fail. No second copy of the bits. Silence is DEAD.",
        "real": "command_radiation.py · /uplink",
        "status": "shipped",
    },
    {
        "id": "bind_only",
        "subject": "insurance",
        "name": "Bind-only mouth",
        "claim": "PolicyCenter bind-only is the married write. bind-and-issue is not granted.",
        "satoshi": "One script type spends any UTXO shape.",
        "heavier": "The write fingerprint is the spouse. Wrong path is a halt.",
        "real": "spend_protocol.py · cloudflare-worker-bind.js · Bind Room",
        "status": "shipped",
    },
    {
        "id": "mishara_receipt",
        "subject": "harm",
        "name": "Stranger-held harm receipt",
        "claim": "When the act already hurt someone — a receipt neither platform nor person forges alone.",
        "satoshi": "The ledger does not speak to the person who was denied housing or work.",
        "heavier": "FCRA/ECOA/LL144 create duties; individuals still leave without a verify URL.",
        "real": "mishara_app.py · Velaru classify + verify",
        "status": "shipped",
    },
    {
        "id": "never_sell_may",
        "subject": "naming",
        "name": "Never sell may",
        "claim": "Rent the rail. Sell only non-choke skins. Nisaba stays on the invoice.",
        "satoshi": "The founder disappeared so the monetary rule could be sold by no one.",
        "heavier": "We stay so the throat cannot be sold. Disappearance is how mouths get privatized later.",
        "real": "inventor.never_sell · action_os · /operator rent",
        "status": "law",
    },
    {
        "id": "floor",
        "subject": "body",
        "name": "Floor — harm does not restore",
        "claim": "Some things are real, once, and someone else has to live there. cleverer_layer is null.",
        "satoshi": "Reorgs and replacements; the chain can rewrite a shallow past.",
        "heavier": "Money does not un-leave. Time is one-way. Crowning the miss is the trap.",
        "real": "floor.py · /floor",
        "status": "shipped",
    },
    {
        "id": "restraint_nos",
        "subject": "memory",
        "name": "Restraint inventory",
        "claim": "The nos this mouth printed. Production HALT/BLOCK. No PII. Not demo.",
        "satoshi": "The chain remembers spends. It does not remember refusals as the product.",
        "heavier": "Scarcity is the DENY. The public object is the halt a stranger can open.",
        "real": "restraint.py · /.well-known/restraint.json",
        "status": "shipped",
    },
    {
        "id": "bps_register",
        "subject": "markets",
        "name": "Register on cleared flow",
        "claim": "max(floor, 10 bps, $0.10/hop). Infrastructure fees, not SaaS seats.",
        "satoshi": "Block reward + fee to anonymous miners.",
        "heavier": "Price is dissipation on sorting LIVE/DENY — named operator, licensed only.",
        "real": "register.py · operator_invoice.py · /operator",
        "status": "shipped",
    },
    {
        "id": "fail_closed",
        "subject": "computation",
        "name": "Fail-closed under uncertainty",
        "claim": "Timeout and 5xx are halt. UNREACHABLE is never LIVE.",
        "satoshi": "Partition: keep mining; resolve by work later.",
        "heavier": "Attackers manufacture uncertainty to fish for fail-open. Availability loss beats silent LIVE.",
        "real": "OCSP-strict · fuse lookup 503",
        "status": "shipped",
    },
    {
        "id": "bound_answer",
        "subject": "language",
        "name": "A no that holds",
        "claim": "More valuable than the question: narrow, enforced, provable.",
        "satoshi": "The whitepaper is the question; the chain is an answer that reorgs.",
        "heavier": "A question that cannot stop a write is a museum label.",
        "real": "bound.py · /bound",
        "status": "shipped",
    },
    {
        "id": "stranger_mass",
        "subject": "congregation",
        "name": "Stranger mass",
        "claim": "One DEAD receipt a week. Congregation of the non-event.",
        "satoshi": "Congregation is hash rate. The miracle is that something cleared.",
        "heavier": "The miracle is that nothing happened — and strangers can confirm it.",
        "real": "liturgy.py · /mass",
        "status": "shipped",
    },
    {
        "id": "gate1_event",
        "subject": "incarnation",
        "name": "Gate 1 — stranger paid and proved",
        "claim": "An event, not a doctrine. Lab frozen until a stranger pays and a stranger proves.",
        "satoshi": "Genesis block — anonymous first move, then the network.",
        "heavier": "We do not genesis in secret. The first money is a named stranger's weld.",
        "real": "/operator — unpaid, so still museum",
        "status": "weld",
    },
    {
        "id": "intel_erra_feed",
        "subject": "knowing",
        "name": "Intelligence kit as Erra feed",
        "claim": "Knowing is 7.5. Acting is the family. Kit feeds Erra only after Gate 1.",
        "satoshi": "The whitepaper was knowing that became the money.",
        "heavier": "A capability tree does not sit on the write. Palantir-adjacent is not a throat.",
        "real": "unison.intel_kit · PR #33 docs — not a sibling",
        "status": "law",
    },
    {
        "id": "dual_redeem",
        "subject": "counterpart",
        "name": "PvP may — permission versus permission",
        "claim": "Both throats redeem in one SI second, or neither ticket is consumed.",
        "satoshi": "One signature spends. Multisig is optional cash policy.",
        "heavier": (
            "First in history: two permissions, one now, atomic. "
            "CLS for may. Immobilized until both speak."
        ),
        "real": "pvp.py · ticket solo redeem blocks while immobilized",
        "status": "shipped",
    },
    {
        "id": "first_depository",
        "subject": "history",
        "name": "Depository of the act",
        "claim": "Nisaba is designated the first recorder of the act. Money had a CSD. The act did not.",
        "satoshi": "A ledger of coins. No recorder of permission.",
        "heavier": "Headline of the millennium: humanity recorded the act.",
        "real": "first.py · /first · /.well-known/first.json",
        "status": "law",
    },
    {
        "id": "evac_comms",
        "subject": "ceiling",
        "name": "Evac-comms handoff",
        "claim": "Long ceiling: crisis communications clearance. Contribute; do not own C2.",
        "satoshi": "Ceiling is money as a planetary substrate.",
        "heavier": "The choke worth keeping is the last may before civilization moves people, not coins.",
        "real": "SCIENCE / explainable ceiling — not a claimed weld",
        "status": "weld",
    },
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def by_status() -> dict[str, int]:
    out = {"shipped": 0, "law": 0, "weld": 0}
    for inv in INVENTIONS:
        st = inv.get("status") or "weld"
        out[st] = out.get(st, 0) + 1
    return out


def subjects() -> list[str]:
    seen = []
    for inv in INVENTIONS:
        s = inv["subject"]
        if s not in seen:
            seen.append(s)
    return seen


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Nisaba inventions",
        "inventor": inventor_mod.stamp(),
        "evaluated_at": _now(),
        "thesis": (
            "Satoshi gave a protocol away and could not cash. "
            "We rent the padlock standard — Gate Conformant™ + QIC — "
            "so irreversible digital acts are receipted and licensed. "
            "World-shifting like HTTPS. Not a new money. "
            "Identity stands. Gate 1 is stranger paid and proved."
        ),
        "cash_latch": {
            "mark": "Gate Conformant",
            "meter": "QIC",
            "page": f"{base}/conformant",
            "until_gate1_usd": 0,
            "checkout": f"{base}/operator",
        },
        "satoshi": SATOSHI,
        "named_may": named_may_mod.spec(base),
        "inventions": [dict(i) for i in INVENTIONS],
        "subjects": subjects(),
        "counts": by_status(),
        "cleverer_layer": None,
        "their_production": False,
        "winner": None,
        "crown_the_miss": False,
        "never_sell": list(inventor_mod.INVENTOR["never_sell"]),
        "links": {
            "page": f"{base}/inventions",
            "inventor": f"{base}/.well-known/inventor.json",
            "named_may": f"{base}/.well-known/named-may.json",
            "unison": f"{base}/.well-known/unison.json",
            "conformant": f"{base}/.well-known/conformant.json",
            "qic": f"{base}/.well-known/qic.json",
            "heavier": f"{base}/.well-known/heavier.json",
            "operator": f"{base}/operator",
        },
        "page": f"{base}/inventions",
        "gatekeep": "Invention register. Inventor stands. Not a buyer surface.",
    }


def page_blocks() -> list[dict[str, Any]]:
    return [
        {
            "tag": "Inventor",
            "title": inventor_mod.INVENTOR["name"],
            "body": inventor_mod.INVENTOR["rule"],
        },
        {
            "tag": "Cash latch",
            "title": "Gate Conformant™ + QIC",
            "body": (
                "Rent the padlock. Meter the commit. Stay on the invoice. "
                "$0 until a stranger pays and proves."
            ),
        },
        {
            "tag": "Inverse",
            "title": "Named may",
            "body": named_may_mod.INVENTION,
        },
        {
            "tag": "Satoshi",
            "title": "Could not cash",
            "body": SATOSHI["outscaled_by"],
        },
    ]
