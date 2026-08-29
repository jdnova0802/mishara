"""First in human history — the depository and recorder of the act.

DTCC immobilized securities. CLS paired money. SWIFT moved messages.
Vienna defined when a treaty is in force. Swiss kept time and recused the vault.
Hague apostilled paper. BIPM kept the second. Civil registries recorded births.

Nobody recorded the *act*. Nobody immobilized *may*. Nobody paired two
throats in one SI second. Nobody apostilled a machine act. Nobody issued
a death certificate for a capability.

That is the headline of the millennium. It reshapes Nisaba:

  Nisaba  = first depository / recorder of the act
  Gate    = the mouth that deposits, pairs, and redeems
  Velaru  = the apostille (stranger verify)
  Mishara = the inhabitant copy
  Conformant = how others speak the grammar (consolation SKU)

Not a sixth sibling. Not a new L2. Not a new money. Not a throne.
Identity designation — frozen as outbound until Gate 1.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

try:
    from gate import inventor as inventor_mod
except ImportError:
    import inventor as inventor_mod

try:
    from gate import exclusion as exclusion_mod
except ImportError:
    import exclusion as exclusion_mod

try:
    from gate import pvp as pvp_mod
except ImportError:
    import pvp as pvp_mod

SPEC = "nisaba-first-in-history-v1"
FAMILY_SIBLINGS_REMAIN = 5
L2_MODULE = False
THEIR_PRODUCTION = False

RESHAPE = {
    "headline": "Humanity recorded the act.",
    "nisaba": (
        "The first depository and recorder of the act in the history of the species. "
        "Not a bank. Not a state. Not a coin. The folio where a write becomes real."
    ),
    "why_empty": (
        "Money has a depository. Messages have a network. Treaties have a convention. "
        "Time has a bureau. Births have a registry. The irreversible digital act — "
        "bind, payout, tool, handoff — had speech, logs, and dashboards. Never a recorder."
    ),
    "dots": (
        "DTCC CSD × CLS PvP × Swiss recusal × Vienna model-law × SI second "
        "× speech-act theory × thermodynamics × vital records × Hague apostille."
    ),
    "not_threatening": (
        "A recorder does not issue money, command force, or sit the throne. "
        "It says whether the act occurred, whether both throats spoke, "
        "whether the capability died unused. Institutions want that. States keep C2."
    ),
    "brands": {
        "nisaba": "depository / recorder of the act",
        "gate": "mouth — deposit, pair, redeem",
        "velaru": "apostille — stranger verify",
        "mishara": "inhabitant copy — the person who lives there",
        "conformant": "grammar others speak — not the depository",
    },
}

SOON: tuple[dict[str, Any], ...] = (
    {
        "id": "pvp_may",
        "name": "PvP may — permission versus permission",
        "horizon": "soon",
        "first": (
            "CLS paired two money legs. Multisig spends one secret. "
            "Nobody consumed two permissions atomically in one SI second."
        ),
        "invention": (
            "Two named throats. One window. Both redeem in the shared UTC now, "
            "or no ticket is consumed. Immobilized until then. Solo radiate is DEAD."
        ),
        "dots": "CLS × dual throat × CGPM 2018 second × license fuse",
        "real": "pvp.py · POST /demo/pas/pvp/open · /demo/pas/pvp/offer",
        "status": "shipped",
        "not_threatening": "Both sides must still want it. Silence voids the window.",
    },
    {
        "id": "machine_act_apostille",
        "name": "Machine-act apostille",
        "horizon": "soon",
        "first": (
            "Hague apostilles paper issued by a state. Nobody apostilles "
            "a machine act — a stranger-verifiable seal that *this write occurred*, "
            "or that it did not, without an account and without a ministry."
        ),
        "invention": (
            "Velaru/Gate receipt as an apostille of the act: country-neutral, "
            "stranger-held, fail-closed. The document is not the product. The act is."
        ),
        "dots": "Hague Apostille × Velaru verify × exclusion folio",
        "real": "apostille() · /.well-known/exclusion.json · receipt URLs",
        "status": "shipped",
        "not_threatening": "A stamp on what happened. Not a passport. Not a court.",
    },
    {
        "id": "capability_vital_record",
        "name": "Capability death certificate",
        "horizon": "soon",
        "first": (
            "Civil registries record that a person died. Software has logs. "
            "Nobody issues a stranger-verifiable death certificate for a *capability* — "
            "this may died, and it was not spent."
        ),
        "invention": (
            "DEAD + no redeemed leaf = vital record of unused permission. "
            "The obituary of a tool, a bind, a payout right."
        ),
        "dots": "vital records × fuse DEAD × proof of exclusion × restraint",
        "real": "death_certificate(job_id) · exclusion.prove",
        "status": "shipped",
        "not_threatening": "An obituary. The opposite of a weapon.",
    },
    {
        "id": "immobilized_may",
        "name": "Immobilized may (act CSD)",
        "horizon": "soon",
        "first": (
            "A CSD immobilizes a security so it cannot walk. "
            "Nobody immobilized *permission* — a ticket that cannot radiate "
            "until delivery versus the other throat."
        ),
        "invention": (
            "Open a PvP window and the tickets cease to be bearer or even named-solo. "
            "They sit in the depository until paired now."
        ),
        "dots": "DTCC immobilization × bind ticket × pvp lock",
        "real": "db.pvp_lock_for_ticket · ticket.redeem → pvp_pair_required",
        "status": "shipped",
        "not_threatening": "Escrow of may. You do not take the asset. You hold the right to act.",
    },
    {
        "id": "silence_line",
        "name": "Silence as a posted ledger line",
        "horizon": "soon",
        "first": (
            "Books post debits and credits. Nobody posts *silence* as a first-class "
            "line — the certified non-answer that held."
        ),
        "invention": (
            "Restraint inventory + exclusion folio as the public silence book. "
            "Double-entry may starts here: a LIVE without a matching silence/ρ is incomplete."
        ),
        "dots": "double-entry × fail-closed × public good",
        "real": "restraint.py · exclusion.py · /.well-known/restraint.json",
        "status": "shipped",
        "not_threatening": "The books of what did not happen. Audit food.",
    },
)

MEDIUM: tuple[dict[str, Any], ...] = (
    {
        "id": "icad",
        "name": "International Central Act Depository",
        "horizon": "medium",
        "first": (
            "There is a DTC for stocks, a SIX SIS for Swiss paper, a Euroclear. "
            "There is no ICAD — a member depository whose positions are *may*."
        ),
        "invention": (
            "Members deposit immobilized tickets. Windows net. Finality hash. "
            "Default waterfall already sketched in settlement.py. The instrument is permission."
        ),
        "dots": "DTCC + settlement.py + pvp + license fuse cascade",
        "real": "settlement.py + pvp.py — designation to join them as one depository",
        "status": "weld",
        "not_threatening": "A CCP for acts. Observers stay. No throne.",
    },
    {
        "id": "correspondent_may",
        "name": "Correspondent may (nostro / vostro of permission)",
        "horizon": "medium",
        "first": (
            "Banks keep nostro/vostro for money they do not issue. "
            "Nobody keeps a correspondent book of *may they do not speak* — "
            "your LIVE is recognized on my rail without bilateral trust."
        ),
        "invention": (
            "Institution A’s redeemed may is a nostro position on Institution B’s mouth. "
            "The depository is the correspondent. Fuse cascade is the nostro kill."
        ),
        "dots": "correspondent banking × license fuse × ICAD",
        "real": "license_fuse.py parent LIVE — designation of the book",
        "status": "weld",
        "not_threatening": "Recognition of a receipt. Not a currency union.",
    },
    {
        "id": "model_law_machine_act",
        "name": "Model Law of the Machine Act",
        "horizon": "medium",
        "first": (
            "UNCITRAL writes model laws states adopt. There is no model law "
            "for *when software has acted*. Courts still treat logs as narrative."
        ),
        "invention": (
            "A text: an irreversible machine act is in force only if a named "
            "may was redeemed in the SI now, stranger-provable, fail-closed on silence. "
            "Gate is the reference implementation. Nisaba does not legislate. It offers the text."
        ),
        "dots": "UNCITRAL × Vienna VCLT ‘in force’ × illocution × Gate redeem",
        "real": "designation — counsel week is the foothill, not this text outbound yet",
        "status": "weld",
        "not_threatening": "A model law. States remain states. Like e-signature laws, not a constitution.",
    },
    {
        "id": "master_irreversible",
        "name": "Master agreement for irreversible commits",
        "horizon": "medium",
        "first": (
            "ISDA mastered derivatives. There is no master that says: "
            "these two mays, this now, this edition pin, this ρ if silence."
        ),
        "invention": (
            "A confirm + schedule whose operative verb is redeem, not promise. "
            "Breach is a voided window, not a lawsuit about intent."
        ),
        "dots": "ISDA × PvP may × edition pin × restraint",
        "real": "pvp window as the confirm — designation of the paper",
        "status": "weld",
        "not_threatening": "Contract furniture. Lawyers already live here.",
    },
    {
        "id": "recused_mouth",
        "name": "Recused mouth",
        "horizon": "medium",
        "first": (
            "Swiss neutrality is a state posture. A clearinghouse that *cannot "
            "take a side in the act it records* — cannot CHARGE from inside, "
            "cannot share the commercial outcome — has not existed for digital acts."
        ),
        "invention": (
            "The mouth prints LIVE/DEAD/SETTLED/VOID. It does not get the payout. "
            "CHARGE stays outside the actor. That is Swiss recusal as code."
        ),
        "dots": "Swiss × CHARGE-outside-the-actor × never sell may",
        "real": "charge_authority · not_admin_charge · inventor.never_sell",
        "status": "law",
        "not_threatening": "The recorder steps out of the deal. That is why both sides will use it.",
    },
)

LONG: tuple[dict[str, Any], ...] = (
    {
        "id": "cima",
        "name": "Convention on Irreversible Machine Acts",
        "horizon": "long",
        "first": (
            "Vienna Convention on the Law of Treaties says when a treaty is in force. "
            "There is no convention that says when a machine act is in force between institutions."
        ),
        "invention": (
            "A text institutions join. Not a state. Not Nisaba-as-sovereign. "
            "Join the convention, speak the grammar, deposit the act. "
            "Leave, and your children cannot outlive the parent."
        ),
        "dots": "VCLT × circle members/observers × license fuse × ICAD",
        "real": "designation — ceiling of the depository, not this year’s outbound",
        "status": "weld",
        "not_threatening": "A club with a text. Observers from states. No throne.",
    },
    {
        "id": "may_as_unit",
        "name": "May as an SI-adjacent unit",
        "horizon": "long",
        "first": (
            "The candela measures luminous intensity. Nobody measures allowed "
            "irreversibility. If may has a unit, civilization can cap, floor, and price it."
        ),
        "invention": (
            "A draft unit: allowed irreversibility per epoch. Gate as reference impl. "
            "BIPM-shaped process, not a coin."
        ),
        "dots": "CGPM × thermodynamics × risk × QIC as the count",
        "real": "shared UTC now is the foothill — designation of the unit",
        "status": "weld",
        "not_threatening": "A lumen for permission. Not money. Not a carbon-credit casino unless others make it one.",
    },
    {
        "id": "entropy_clearing",
        "name": "Entropy clearing",
        "horizon": "long",
        "first": (
            "CCPs net dollars and securities. Nobody nets *one-wayness* — "
            "the thermodynamic fact that this act cannot be undone — as the cleared object."
        ),
        "invention": (
            "Every SETTLED PvP publishes an irreversibility class. "
            "The depository nets the classes. The books show how much world was spent."
        ),
        "dots": "thermo × DTCC netting × QIC × inhabitant (who lives with the entropy)",
        "real": "designation — settlement windows already hash finality",
        "status": "weld",
        "not_threatening": "Accounting for one-wayness. Not a heat weapon.",
    },
    {
        "id": "consent_runtime",
        "name": "Consent runtime",
        "horizon": "long",
        "first": (
            "Consent in law is often a signature at T0. Nobody built a legal object "
            "that is *alive only while both sides still may* — continuous fuse, not a ToS."
        ),
        "invention": (
            "A PvP window that must be re-armed. Silence is DEAD. "
            "Romance-structure × philosophy of action × fuse heartbeat."
        ),
        "dots": "P10 consent runtime × PvP × silence law",
        "real": "pvp ARMED + fuse DEAD — designation of the living object",
        "status": "weld",
        "not_threatening": "Ongoing yes. The opposite of capture.",
    },
    {
        "id": "capability_civil_registry",
        "name": "Civil registry of capability",
        "horizon": "long",
        "first": (
            "States register births. Nobody registers the birth and death of "
            "what a machine was allowed to do, as a public good."
        ),
        "invention": (
            "Vital records of may: issued, immobilized, settled, void, dead-unused. "
            "Population-scale. Mishara is the inhabitant’s copy of the same folio."
        ),
        "dots": "civil registry × vital record × Mishara × ICAD",
        "real": "death_certificate + pvp states — designation of the registry",
        "status": "weld",
        "not_threatening": "A baby book for permission. People keep their rights. Machines get obituaries.",
    },
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _base(public_url: str) -> str:
    return (public_url or "").rstrip("/")


def apostille(job_id: str) -> dict[str, Any]:
    """Hague-shaped seal of a machine act — or of its absence."""
    proof = exclusion_mod.prove(job_id)
    spent = bool(proof.get("spent"))
    return {
        "spec": "gate-machine-act-apostille-v1",
        "first_in_history": True,
        "kind": "machine_act_apostille",
        "job_id": (job_id or "").strip() or None,
        "act_occurred": spent,
        "claim": (
            "redeemed_ticket_leaf_present" if spent else "no_redeemed_ticket_for_job"
        ),
        "apostille_of": "the act" if spent else "the certified non-act",
        "not": ["a state apostille", "a notarized PDF", "a ministry"],
        "tree_head": proof.get("tree_head"),
        "stranger_verify": True,
        "their_production": False,
    }


def death_certificate(job_id: str) -> dict[str, Any]:
    """Vital record: this capability was not spent."""
    proof = exclusion_mod.prove(job_id)
    unused = not bool(proof.get("spent"))
    return {
        "spec": "gate-capability-vital-v1",
        "first_in_history": True,
        "kind": "capability_death_certificate" if unused else "capability_still_or_spent",
        "job_id": (job_id or "").strip() or None,
        "died_unused": unused,
        "spent": not unused,
        "claim": proof.get("claim"),
        "not": ["a person’s death certificate", "a eulogy"],
        "tree_head": proof.get("tree_head"),
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = _base(public_url)
    return {
        "spec": SPEC,
        "name": "First in human history",
        "inventor": inventor_mod.stamp(),
        "evaluated_at": _now(),
        "reshape": dict(RESHAPE),
        "thesis": RESHAPE["headline"] + " " + RESHAPE["nisaba"],
        "soon": [dict(x) for x in SOON],
        "medium": [dict(x) for x in MEDIUM],
        "long": [dict(x) for x in LONG],
        "counts": {"soon": len(SOON), "medium": len(MEDIUM), "long": len(LONG)},
        "pvp": pvp_mod.spec(base),
        "family_siblings_remain": FAMILY_SIBLINGS_REMAIN,
        "l2_module": L2_MODULE,
        "mouth_ceiling": "held — first-in-history designations + PvP/apostille/vital on existing rails",
        "identity_frozen_until_gate1": True,
        "their_production": THEIR_PRODUCTION,
        "cash_usd": 0,
        "never_sell": list(inventor_mod.INVENTOR["never_sell"]),
        "links": {
            "page": f"{base}/first",
            "pvp": f"{base}/.well-known/pvp.json",
            "heavier": f"{base}/.well-known/heavier.json",
            "conformant": f"{base}/.well-known/conformant.json",
            "operator": f"{base}/operator",
        },
        "page": f"{base}/first",
        "gatekeep": "First-in-history depository. Not a buyer chrome plate.",
    }


def page_blocks() -> list[dict[str, Any]]:
    return [
        {"tag": "Headline", "title": "The act", "body": RESHAPE["headline"]},
        {"tag": "Nisaba", "title": "Recorder", "body": RESHAPE["nisaba"]},
        {"tag": "Soon", "title": "PvP may", "body": SOON[0]["invention"]},
        {"tag": "Empty", "title": "The gap", "body": RESHAPE["why_empty"]},
    ]
