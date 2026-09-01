"""Bigger than the act — the remaining.

The act is a journal line. Civilizations that lasted invented the other half:

  Egypt weighed the heart against Ma'at — not the deed, the order that remained.
  Torah kept covenant — the remaining of a promise, not the moment it was spoken.
  Rome kept title — the remaining of occupation.
  Pacioli (1494) invented modern capital as double-entry: journal is nothing
  without the balance. The remaining *is* the invention.
  Carbon accounting tried this for atoms. The emission is the act.
  The remaining atmosphere is the object.
  Banks hold reserves (stock). Satoshi built flow. DTCC journals securities.
  Nobody held the remaining of a machine write.

Nisaba was never only the scribe of the act. She was the accountant of
the remaining. We seated half the goddess. This seats the other half.

Stack (not a cleverer layer — the floor still holds):

  given      = opening — the world was already there
  may        = unspent one-wayness (potency)
  act        = journal line (spending)
  remaining  = the world after (stock / balance sheet)
  inhabitant = who the remaining is for
  prove      = a stranger can open the remaining
  floor      = the remaining cannot be climbed under

The act is the difference between the given and the remaining.
What's bigger than the act is the remaining.

Not a sixth sibling. Not a new L2. Not Being-as-a-SKU.
Identity designation — frozen as outbound until Gate 1.
cleverer_layer stays null. We do not productize God.
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
    from gate import db as db_mod
except ImportError:
    import db as db_mod

try:
    from gate import inhabitant as inhabitant_mod
except ImportError:
    import inhabitant as inhabitant_mod

SPEC = "nisaba-remaining-v1"
FAMILY_SIBLINGS_REMAIN = 5
L2_MODULE = False
THEIR_PRODUCTION = False
CLEVERER_LAYER = None

IDENTITY = "given = spent + remaining + immobilized + W + dead-unused + void"
LEGACY_IDENTITY = "remaining = given − spent one-wayness"

RESHAPE = {
    "headline": "Bigger than the act is the remaining.",
    "nisaba": (
        "The first depository of the remaining — the world after a machine write. "
        "The act is a journal line. The remaining is the balance sheet. "
        "Nisaba was the accountant, not only the scribe."
    ),
    "why_empty": (
        "Every civilization that survived invented a technology of the remaining: "
        "Ma'at, covenant, title, double-entry, reserves, the carbon budget. "
        "Money has a stock. Emissions have an atmosphere. Births have a people. "
        "The irreversible digital write had a log of the event and no folio of "
        "the world after. We recorded the act. We did not hold what remained."
    ),
    "dots": (
        "Pacioli double-entry × DTCC journal-vs-CSD × carbon remaining-budget "
        "× Ma'at × covenant × title × CGPM shared now × inhabitant afterward "
        "× κ conservation × floor (one-way time) × the given as opening balance."
    ),
    "not_threatening": (
        "A balance sheet does not issue money, command force, or sit the throne. "
        "It says what the world is after the write, who has to live there, "
        "and that some changes cannot be undone. Institutions want the stock. "
        "States keep C2. Being is not a SKU."
    ),
    "civilization": (
        "Before law, naming. Before naming, a world that was already there. "
        "Before the act, one-way time — without which act and remaining are "
        "the same word. Far future: when most writes can be reversed, the only "
        "acts that still mean act are the ones that spend true one-wayness. "
        "The scarce object becomes the remaining irreversible, not the event log."
    ),
    "brands": {
        "nisaba": "depository of the remaining — stock of the world after",
        "first": "journal / recorder of the act — the flow, not the object",
        "gate": "mouth that spends one-wayness",
        "velaru": "prove the remaining — stranger opens the stock",
        "mishara": "inhabitant of the remaining — they did not have to ask",
        "afterward": "letter to whoever lives in the remaining later — already seated",
        "floor": "the remaining cannot be climbed under. cleverer_layer is null",
        "conformant": "grammar of the spend — consolation SKU, not the stock",
    },
}

SOON: tuple[dict[str, Any], ...] = (
    {
        "id": "remaining_folio",
        "name": "Remaining folio",
        "horizon": "soon",
        "first": (
            "Logs record the event. Apostilles seal the act. Nobody publishes "
            "the stock after — given, spent, remaining — as a stranger-held folio."
        ),
        "invention": (
            "For one job: the given (tickets issued, world already there), "
            "the act (whether one-wayness was spent), the remaining (what is "
            "left). The act is a field. The folio is the remaining."
        ),
        "dots": "double-entry × exclusion prove × inhabitant copy",
        "real": "remaining.folio · POST /demo/pas/remaining",
        "status": "shipped",
        "not_threatening": "A trial balance for one write. Not a central bank.",
    },
    {
        "id": "hold_book",
        "name": "Hold (Ν) — candidate becoming non-effective",
        "horizon": "soon",
        "first": (
            "The folio booked the after. Prefinality evaluated pay. Bind Room "
            "sold a pack about a stop. Nobody conserved becoming that has not "
            "been allowed to take effect — overflow queued, effect was default."
        ),
        "invention": (
            "A candidate may be proposed for free. Ν does not grow with the "
            "candidate count. If Ν is zero the candidate dies — it is not "
            "queued. Effectuation is undefined until a seal consumes Ν and "
            "writes spend, cut (Ω), and burden (Ρ) in the same remaining. "
            "The hold is the book. Not pending. Not a Bind sentence."
        ),
        "dots": "Ν × DAS pipe-not-stock × rehearsal≠spend × overflow-die",
        "real": (
            "remaining.hold · POST /demo/pas/remaining/hold · "
            "POST /demo/pas/remaining/seal · folio.hold"
        ),
        "status": "shipped",
        "not_threatening": "A hold-book on one job. Not C2. Not a new page.",
    },
    {
        "id": "accounting_identity",
        "name": "Accounting identity of may",
        "horizon": "soon",
        "first": (
            "Permission systems count spends. They do not publish the identity "
            "remaining = given − spent as a civil object that can fail closed."
        ),
        "invention": (
            "The folio states the close and whether it holds. Unused-as-product "
            "is W, not leftover remaining. If given does not equal spent + "
            "remaining + immobilized + W + dead-unused + void, the remaining "
            "is a lie. Unattested W cannot become remaining."
        ),
        "dots": "Pacioli × κ mouth-invariant × spend map",
        "real": "remaining.folio identity_holds",
        "status": "shipped",
        "not_threatening": "Bookkeeping. Auditors already speak this language.",
    },
    {
        "id": "one_way_class",
        "name": "One-way class",
        "horizon": "soon",
        "first": (
            "APIs treat every write as reversible with a compensating call. "
            "Nobody tags a digital write as potency, spent one-wayness, or "
            "no-given — the classes that make an act an act."
        ),
        "invention": (
            "Unspent tickets are potency. A consumed redeem is spent "
            "one-wayness. No ticket and no event is no-given — you cannot "
            "act except upon what was already there. Rehearsal is not a class "
            "this mouth prints."
        ),
        "dots": "thermodynamics × PRI × floor (time is one-way)",
        "real": "remaining.folio one_way_class",
        "status": "shipped",
        "not_threatening": "A label on irreversibility. Physics already won.",
    },
    {
        "id": "remaining_party",
        "name": "Remaining party is not the actor",
        "horizon": "soon",
        "first": (
            "Every receipt is addressed to the institution that acted. "
            "The remaining is for the inhabitant. The holder is a field on "
            "the ticket, not the party the world is for."
        ),
        "invention": (
            "folio.for = inhabitant. folio.not_for = the actor. "
            "Named may still names who may redeem. The remaining names who "
            "has to live there. Two names. The second is bigger."
        ),
        "dots": "inhabitant afterward × named may × CHARGE outside the actor",
        "real": "remaining.folio for / not_for",
        "status": "shipped",
        "not_threatening": "The copy they already have. Now it is the heading of the stock.",
    },
    {
        "id": "the_given",
        "name": "The given as opening",
        "horizon": "soon",
        "first": (
            "Actor-systems invent the world at t=0. Nothing was already there. "
            "That is how a write pretends to be creation. The given is the "
            "opening balance — tickets, a live fuse, a shared now, a floor."
        ),
        "invention": (
            "The folio opens with given.kind = opening. If there is no ticket "
            "and no event, given.absent is true: there was no world this mouth "
            "can spend. We will not invent an opening. That is the same weld "
            "as the missing inhabitant letter."
        ),
        "dots": "the given (Marion / Heidegger) × floor × missing letter",
        "real": "remaining.folio given",
        "status": "shipped",
        "not_threatening": "Opening balance. We do not sell Being.",
    },
    {
        "id": "wilderness_column",
        "name": "Wilderness column",
        "horizon": "soon",
        "first": (
            "The books treated unused as leftover remaining a CFO can cut, "
            "or as void that never happened. Unused-as-product had no column."
        ),
        "invention": (
            "W is attested unused whose correct next state is still unused. "
            "Ordinary redeem of W HALTs. Steward paid for unusedness cannot "
            "spend it. The Third opens, never spends, unless CHARGE-outside "
            "for a W-draw or a reclassify. ω = W / given."
        ),
        "dots": "unused-as-product × The Third × CHARGE-outside × Roman second mirror",
        "real": "POST /demo/pas/remaining/wilderness · folio.close",
        "status": "shipped",
        "not_threatening": "A column. Not a telescope. Not a journal. Not Being.",
    },
)

MEDIUM: tuple[dict[str, Any], ...] = (
    {
        "id": "world_budget",
        "name": "World-budget of one-wayness",
        "horizon": "medium",
        "first": (
            "Carbon has a remaining budget. Machine writes have unlimited "
            "atmosphere. Nobody meters remaining permitted one-wayness for a "
            "jurisdiction or a weld."
        ),
        "invention": (
            "A remaining budget per married write-class: how much one-wayness "
            "is left this period. QIC meters the flow. The budget is the stock. "
            "Rent the remaining, do not sell the atmosphere."
        ),
        "dots": "carbon remaining-budget × QIC × register 10 bps",
        "real": "designation — QIC is the flow meter; budget is the stock weld",
        "status": "weld",
        "not_threatening": "A speed limit on irreversible writes. Not a money supply.",
    },
    {
        "id": "irreversibility_taxonomy",
        "name": "Irreversibility taxonomy",
        "horizon": "medium",
        "first": (
            "Law knows felony vs misdemeanor. Physics knows reversible vs not. "
            "Digital writes are all 'API calls.' Nobody classifies which "
            "machine acts spend true one-wayness."
        ),
        "invention": (
            "A published ladder: rehearsal / compensating / one-way civic / "
            "unuttered. Only one-way civic enters the remaining folio as spend. "
            "The Unuttered never gets a throat. Conformant speaks the grammar; "
            "the taxonomy says which grammar may exist."
        ),
        "dots": "Unuttered × mouth-license × PRI × Model Law of the Machine Act",
        "real": "designation on unison unmouthed + remaining class",
        "status": "law",
        "not_threatening": "A dictionary of what cannot be undone. States keep the top rung.",
    },
    {
        "id": "trial_balance_may",
        "name": "Trial balance of may",
        "horizon": "medium",
        "first": (
            "κ conserves permission-mass across hops. No stranger-held trial "
            "balance of issued / spent / remaining / immobilized / dead-unused "
            "across a mouth."
        ),
        "invention": (
            "Period close: given = spent + remaining + immobilized + W + "
            "dead-unused + void. If it does not close, the mouth does not "
            "speak. κ is the mouth. W is the warehouse. ω = W / given."
        ),
        "dots": "κ × Pacioli × ICAD × restraint inventory × unused-as-product",
        "real": "remaining.folio close + wilderness attest / open / draw",
        "status": "shipped",
        "not_threatening": "Month-end for permission. Controllers already buy this.",
    },
    {
        "id": "licensed_forgetfulness",
        "name": "Licensed forgetfulness",
        "horizon": "medium",
        "first": (
            "When every act is recorded, the scarce right is for the remaining "
            "to become un-addressable. Nobody licenses forgetting as a rare "
            "write — they either hoard forever or delete in the dark."
        ),
        "invention": (
            "A CHARGE-class write that retires addressability of a remaining "
            "folio. Not deletion of the act. Not a right to rewrite. The "
            "stock may heal. The journal line still existed. Recused mouth. "
            "Inhabitant-facing. Actor cannot self-forgive."
        ),
        "dots": "right to be forgotten × CHARGE outside × recused mouth × healing",
        "real": "discharge.py · /discharge · $1,500 Discharge of Record · standing lapses; the chain does not",
        "status": "shipped",
        "not_threatening": "GDPR-shaped mercy with a stranger receipt. Not a memory hole.",
    },
    {
        "id": "estate_of_remaining",
        "name": "Estate of remaining",
        "horizon": "medium",
        "first": (
            "When the bearer dies, dissolves, or goes insolvent, remaining that "
            "stays LIVE is an orphan well. Human death has probate. Digital may did not."
        ),
        "invention": (
            "Probate one remaining: wound down, inherited, or washed. "
            "No successor → leftover writes HALT. CHARGE-outside. "
            "Actor cannot self-probate. Estate is not admin resurrect."
        ),
        "dots": "orphan wells × probate × U7 × CHARGE outside",
        "real": "estate.py · /estate · $3,500 Estate of Remaining",
        "status": "shipped",
        "not_threatening": "Wind-down for a dead vendor. Not a court. Not deletion.",
    },
    {
        "id": "correspondent_remaining",
        "name": "Correspondent remaining",
        "horizon": "medium",
        "first": (
            "Correspondent banking shares stock across vaults. Correspondent "
            "may (first) pairs two throats. Nobody shares the remaining of a "
            "write across two recused mouths."
        ),
        "invention": (
            "Two depositories hold the same remaining folio. Neither forges "
            "alone. PvP spends one-wayness; correspondent remaining proves "
            "the stock after both have spoken."
        ),
        "dots": "correspondent banking × PvP may × Swiss recusal × Velaru",
        "real": "general.correspondent_books · POST /demo/pas/correspondent · /general",
        "status": "shipped",
        "not_threatening": "Two books, one remaining. How clearing already works.",
    },
)

LONG: tuple[dict[str, Any], ...] = (
    {
        "id": "atmosphere_of_writes",
        "name": "Atmosphere of writes",
        "horizon": "long",
        "first": (
            "The atmosphere is the remaining of every fire. Machine writes "
            "have no atmosphere — infinite room, no weather, no budget that "
            "civilization can point at."
        ),
        "invention": (
            "Planetary remaining of one-way civic writes. Not a coin. Not C2. "
            "A published stock institutions can cite the way they cite CO₂. "
            "Nisaba holds the folio. States hold the ceiling."
        ),
        "dots": "Keeling curve × carbon budget × CHC × never-sell planetary capacity",
        "real": "ceiling designation — contribute, do not own the weather",
        "status": "weld",
        "not_threatening": "A public remaining, like parts-per-million. Not a throne.",
    },
    {
        "id": "si_of_remaining",
        "name": "SI-adjacent unit of remaining",
        "horizon": "long",
        "first": (
            "The candela measures light that remains at the eye. May-candela "
            "(first) measures permission. Nobody measures remaining "
            "one-wayness as a unit a bureau could keep."
        ),
        "invention": (
            "A unit of unspent / spent / remaining one-wayness, SI-adjacent, "
            "recused. The act is an instance. The unit is prior. BIPM keeps "
            "the second; this would keep the remaining."
        ),
        "dots": "CGPM 2018 × may-candela × candela as remaining light",
        "real": "designation — we do not found a bureau",
        "status": "weld",
        "not_threatening": "A unit others can adopt. We rent the padlock, not the meter bar.",
    },
    {
        "id": "healing_convention",
        "name": "Convention on the remaining",
        "horizon": "long",
        "first": (
            "Vienna says when a treaty is in force. CIMA (first) would say "
            "when a machine act occurred. Nobody says when a remaining may "
            "heal — when the world after is allowed to become less addressable."
        ),
        "invention": (
            "A model instrument: remaining folios, world-budgets, licensed "
            "forgetfulness, inhabitant standing. Recorder, not sovereign. "
            "The act convention is the journal. This is the stock convention."
        ),
        "dots": "Vienna × Hague × CIMA × GDPR × inhabitant civil receipt",
        "real": "counsel-shaped designation after Gate 1",
        "status": "weld",
        "not_threatening": "Model law for the world after. States stay states.",
    },
    {
        "id": "given_not_invented",
        "name": "The given cannot be invented",
        "horizon": "long",
        "first": (
            "Creation myths start at t=0. Platforms do too. The deepest prior "
            "to the act is that a world was already there, and someone already "
            "lived in it. You cannot act except upon the given."
        ),
        "invention": (
            "Law: a mouth that invents its opening is not Conformant. "
            "The given is prior. The floor is the given under another name. "
            "We do not sell the given. We refuse to forge it."
        ),
        "dots": "floor × missing letter × the Unuttered × cleverer_layer null",
        "real": "floor.py — designation that the given is the opening, not a SKU",
        "status": "law",
        "not_threatening": "We will not productize Being. That is the point.",
    },
    {
        "id": "true_one_wayness",
        "name": "When reversal is cheap",
        "horizon": "long",
        "first": (
            "Far future: most writes can be undone. Then 'act' dies as a word "
            "unless some spends still cannot be reversed — death, emission, "
            "spoken vow, spent unique may, extinction, the last copy gone."
        ),
        "invention": (
            "The registry of true one-wayness. Not every act. Only the spends "
            "that still mean act after reversal is cheap. The remaining of "
            "those is the last civil object. Entropy clearing (first) is the "
            "flow. This is the stock that survives heat-death of the reversible."
        ),
        "dots": "entropy × death certificate × never-sell planetary capacity × floor",
        "real": "designation — far future, not a pitch",
        "status": "weld",
        "not_threatening": "A cemetery for the irreversible. People keep their rights.",
    },
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _base(public_url: str) -> str:
    return (public_url or "").rstrip("/")


def _tickets_for_job(job_id: str) -> list[dict[str, Any]]:
    jid = (job_id or "").strip()
    if not jid:
        return []
    getter = getattr(db_mod, "tickets_for_job", None)
    if callable(getter):
        rows = getter(jid) or []
        return [dict(r) for r in rows]
    return []


def _one_way_class(*, issued: int, consumed: int, has_event: bool, spent: bool) -> str:
    if spent or consumed > 0:
        return "spent_one_wayness"
    if issued > 0:
        return "potency"
    if has_event:
        return "event_without_ticket"
    return "no_given"


def _stock_class(ticket: dict[str, Any]) -> str:
    return (ticket.get("stock_class") or "remaining").strip() or "remaining"


def _halt(reason: str, **extra: Any) -> dict[str, Any]:
    out = {
        "ok": False,
        "halt": True,
        "reason": reason,
        "identity": IDENTITY,
        "unattested_w_cannot_become_remaining": True,
        "steward_cannot_spend_w": True,
        "w_draw_is_not_ordinary_spend": True,
        "third_opens_never_spends": True,
        "effectuate_undefined_without_n": True,
        "cleverer_layer": CLEVERER_LAYER,
    }
    out.update(extra)
    return out


def _hold_book(job_id: str) -> dict[str, Any]:
    n = db_mod.n_stock_for_job(job_id) if job_id else 0
    rows = db_mod.holds_for_job(job_id) if job_id else []
    held = [r for r in rows if r.get("state") == "held"]
    died = [r for r in rows if r.get("state") == "died"]
    sealed = [r for r in rows if r.get("state") == "sealed"]
    return {
        "kind": "prefinality_remaining",
        "book": "Ν",
        "N": n,
        "candidates": len(rows),
        "held": len(held),
        "died": len(died),
        "sealed": len(sealed),
        "overflow_dies": True,
        "proposals_are_free": True,
        "N_does_not_grow_with_C": True,
        "effectuate_undefined_without_seal": True,
        "not_pending": True,
        "not_the_bind_sentence": True,
        "open": [
            {
                "id": r.get("id"),
                "candidate": r.get("candidate"),
                "state": r.get("state"),
                "effective": r.get("state") == "sealed",
                "cut": r.get("cut"),
                "burden": r.get("burden"),
                "died_reason": r.get("died_reason"),
            }
            for r in rows
        ],
    }


def _columns(tickets: list[dict[str, Any]], job_id: str, now: str) -> dict[str, Any]:
    immobilized_ids = db_mod.pvp_active_ticket_ids_for_job(job_id) if job_id else set()
    spent = remaining = immobilized = wilderness = dead_unused = void = 0
    for t in tickets:
        consumed = bool(t.get("consumed_at"))
        klass = _stock_class(t)
        if consumed:
            spent += 1
            continue
        if klass == "wilderness":
            wilderness += 1
            continue
        if klass == "void":
            void += 1
            continue
        tid = t.get("id") or ""
        if tid in immobilized_ids:
            immobilized += 1
            continue
        expired = bool(t.get("not_after") and t["not_after"] < now)
        if expired:
            dead_unused += 1
            continue
        remaining += 1
    given = len(tickets)
    close = spent + remaining + immobilized + wilderness + dead_unused + void
    omega = (wilderness / given) if given else 0.0
    return {
        "given": given,
        "spent": spent,
        "remaining": remaining,
        "immobilized": immobilized,
        "W": wilderness,
        "dead_unused": dead_unused,
        "void": void,
        "close": close,
        "omega": omega,
        "holds": given == close,
    }


def folio(job_id: str) -> dict[str, Any]:
    """The remaining of one job — stock, not the apostille of the act."""
    jid = (job_id or "").strip()
    proof = exclusion_mod.prove(jid)
    spent_act = bool(proof.get("spent"))
    event = db_mod.latest_bind_event_for_job(jid) if jid else None
    tickets = _tickets_for_job(jid)
    cols = _columns(tickets, jid, _now())
    issued = cols["given"]
    consumed = cols["spent"]
    unconsumed = cols["remaining"]
    identity_holds = cols["holds"]
    has_event = bool(event)
    given_absent = (not jid) or (issued == 0 and not has_event and not spent_act)
    one_way = _one_way_class(
        issued=issued, consumed=consumed, has_event=has_event, spent=spent_act
    )
    if cols["W"] and cols["remaining"] == 0 and not spent_act and consumed == 0:
        one_way = "wilderness"
    letter = None
    if event:
        letter = inhabitant_mod.for_event(event, "")
    return {
        "spec": SPEC,
        "kind": "remaining_folio",
        "job_id": jid or None,
        "identity": IDENTITY,
        "legacy_identity": LEGACY_IDENTITY,
        "identity_holds": identity_holds,
        "the_act_is_not_the_object": True,
        "given": {
            "kind": "opening",
            "claim": "the world was already there",
            "tickets_issued": issued,
            "event_existed": has_event,
            "absent": given_absent,
            "we_will_not_invent_an_opening": True,
        },
        "act": {
            "occurred": spent_act,
            "tickets_consumed": consumed,
            "claim": proof.get("claim"),
            "not_the_object": True,
        },
        "remaining": {
            "kind": "stock_after",
            "tickets_unconsumed": unconsumed,
            "one_way_spent": spent_act or consumed > 0,
            "one_way_class": one_way,
            "for": "inhabitant",
            "not_for": "the actor",
        },
        "hold": _hold_book(jid),
        "close": {
            "spent": cols["spent"],
            "remaining": cols["remaining"],
            "immobilized": cols["immobilized"],
            "W": cols["W"],
            "dead_unused": cols["dead_unused"],
            "void": cols["void"],
            "omega": cols["omega"],
            "holds": cols["holds"],
            "law": {
                "unattested_w_cannot_become_remaining": True,
                "w_draw_is_not_ordinary_spend": True,
                "steward_cannot_spend_w": True,
                "third_opens_never_spends": True,
                "effectuate_undefined_without_n": True,
                "overflow_dies": True,
            },
        },
        "inhabitant": {
            "audience": inhabitant_mod.AUDIENCE,
            "letter_kind": (
                "spared"
                if letter and inhabitant_mod.is_spared(event)
                else "spent"
                if letter and inhabitant_mod.is_spent(event)
                else "none"
            ),
        },
        "tree_head": proof.get("tree_head"),
        "cleverer_layer": CLEVERER_LAYER,
        "l2_module": L2_MODULE,
        "their_production": THEIR_PRODUCTION,
        "not": [
            "an apostille of the act",
            "a new money",
            "a cleverer layer",
            "Being as a SKU",
            "a sixth sibling",
            "a new homepage",
            "pending",
            "the Bind sentence",
        ],
    }


def hold(job_id: str, candidate: str) -> dict[str, Any]:
    """Propose a candidate becoming. Ν does not grow. Overflow dies."""
    jid = (job_id or "").strip()
    n = db_mod.n_stock_for_job(jid) if jid else 0
    result = db_mod.hold_propose(job_id=jid, candidate=candidate, n_stock=n)
    if not result.get("ok"):
        return _halt(result.get("halt") or "hold_failed", **result)
    pack = folio(jid)
    return {
        "ok": True,
        "kind": "hold",
        "book": "Ν",
        "identity": IDENTITY,
        "effective": False,
        "overflow_die": result.get("state") == "died",
        "hold": result,
        "folio": pack,
        "N": (pack.get("hold") or {}).get("N"),
        "not_the_bind_sentence": True,
        "cleverer_layer": CLEVERER_LAYER,
    }


def seal(
    job_id: str,
    hold_id: str,
    ticket_id: str,
    cut: str,
    burden: str,
) -> dict[str, Any]:
    """Consume Ν. Write spend · cut · burden. Other held candidates die if Ν hits zero."""
    jid = (job_id or "").strip()
    result = db_mod.hold_seal(
        hold_id=hold_id,
        job_id=jid,
        ticket_id=ticket_id,
        cut=cut,
        burden=burden,
    )
    if not result.get("ok"):
        return _halt(result.get("halt") or "seal_failed", **result)
    pack = folio(jid)
    return {
        "ok": True,
        "kind": "seal",
        "book": "Ν",
        "identity": IDENTITY,
        "effective": True,
        "seal": result,
        "folio": pack,
        "N": (pack.get("hold") or {}).get("N"),
        "tetrad": {
            "spend": (pack.get("act") or {}).get("occurred"),
            "cut": result.get("cut"),
            "burden": result.get("burden"),
            "hold_consumed": True,
        },
        "not_the_bind_sentence": True,
        "cleverer_layer": CLEVERER_LAYER,
    }


def attest_wilderness(job_id: str, ticket_id: str, steward_id: str) -> dict[str, Any]:
    result = db_mod.wilderness_attest(
        job_id=(job_id or "").strip(),
        ticket_id=(ticket_id or "").strip(),
        steward_id=(steward_id or "").strip(),
    )
    if not result.get("ok"):
        return _halt(result.get("halt") or "wilderness_attest_failed", **result)
    pack = folio((job_id or "").strip())
    return {
        "ok": True,
        "kind": "wilderness_attested",
        "identity": IDENTITY,
        "attestation": result,
        "folio": pack,
        "omega": (pack.get("close") or {}).get("omega"),
    }


def open_wilderness(job_id: str, ticket_id: str, third_id: str) -> dict[str, Any]:
    result = db_mod.wilderness_open(
        ticket_id=(ticket_id or "").strip(),
        third_id=(third_id or "").strip(),
    )
    if not result.get("ok"):
        return _halt(result.get("halt") or "wilderness_open_failed", **result)
    return {
        "ok": True,
        "kind": "wilderness_opened",
        "identity": IDENTITY,
        "third_opens_never_spends": True,
        "attestation": result,
        "folio": folio((job_id or "").strip()),
    }


def reclassify_wilderness(
    job_id: str, ticket_id: str, actor_id: str, charge_id: str
) -> dict[str, Any]:
    result = db_mod.wilderness_reclassify(
        ticket_id=(ticket_id or "").strip(),
        actor_id=(actor_id or "").strip(),
        charge_id=(charge_id or "").strip(),
    )
    if not result.get("ok"):
        return _halt(result.get("halt") or "unattested_w_cannot_become_remaining", **result)
    return {
        "ok": True,
        "kind": "wilderness_reclassified",
        "identity": IDENTITY,
        "attestation": result,
        "folio": folio((job_id or "").strip()),
    }


def draw_wilderness(
    job_id: str, ticket_id: str, actor_id: str, charge_id: str
) -> dict[str, Any]:
    result = db_mod.wilderness_draw(
        ticket_id=(ticket_id or "").strip(),
        actor_id=(actor_id or "").strip(),
        charge_id=(charge_id or "").strip(),
    )
    if not result.get("ok"):
        return _halt(result.get("halt") or "w_draw_failed", **result)
    return {
        "ok": True,
        "kind": "w_draw",
        "identity": IDENTITY,
        "w_draw_is_not_ordinary_spend": True,
        "attestation": result,
        "folio": folio((job_id or "").strip()),
    }


def null_result(job_id: str, tried: str = "") -> dict[str, Any]:
    """Failure has a remaining. The try that did not succeed is the stock."""
    pack = folio((job_id or "").strip())
    what = (tried or "").strip()[:200]
    return {
        "spec": SPEC,
        "kind": "null_result",
        "inventor": inventor_mod.stamp(),
        "identity": IDENTITY,
        "job_id": pack.get("job_id"),
        "tried": what or None,
        "succeeded": False,
        "act_occurred": (pack.get("act") or {}).get("occurred"),
        "folio": pack,
        "custodian": "failure has a remaining",
        "not_publication": True,
        "not_a_win": True,
        "generation_does_not_rerun_blind": True,
        "cleverer_layer": CLEVERER_LAYER,
        "until_gate1_usd": 0,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = _base(public_url)
    return {
        "spec": SPEC,
        "name": "The remaining",
        "inventor": inventor_mod.stamp(),
        "evaluated_at": _now(),
        "reshape": dict(RESHAPE),
        "thesis": RESHAPE["headline"] + " " + RESHAPE["nisaba"],
        "identity": IDENTITY,
        "soon": [dict(x) for x in SOON],
        "medium": [dict(x) for x in MEDIUM],
        "long": [dict(x) for x in LONG],
        "counts": {"soon": len(SOON), "medium": len(MEDIUM), "long": len(LONG)},
        "family_siblings_remain": FAMILY_SIBLINGS_REMAIN,
        "l2_module": L2_MODULE,
        "cleverer_layer": CLEVERER_LAYER,
        "mouth_ceiling": "held — remaining designations + folio on existing rails",
        "identity_frozen_until_gate1": True,
        "their_production": THEIR_PRODUCTION,
        "cash_usd": 0,
        "never_sell": list(inventor_mod.INVENTOR["never_sell"]),
        "not_god": True,
        "links": {
            "page": f"{base}/remaining",
            "first": f"{base}/.well-known/first.json",
            "afterward": f"{base}/.well-known/afterward.json",
            "floor": f"{base}/.well-known/floor.json",
            "inhabitant": f"{base}/.well-known/inhabitant.json",
            "kappa": f"{base}/.well-known/kappa.json",
            "heavier": f"{base}/.well-known/heavier.json",
            "finished": f"{base}/finished",
            "standing": f"{base}/standing",
            "general": f"{base}/general",
            "operator": f"{base}/operator",
            "hold": f"POST {base}/demo/pas/remaining/hold",
            "seal": f"POST {base}/demo/pas/remaining/seal",
        },
        "page": f"{base}/remaining",
        "gatekeep": "The remaining. Not a buyer chrome plate. Operated cash is /finished. Remaining lease is /standing. Weld is /operator.",
    }


def page_blocks() -> list[dict[str, Any]]:
    return [
        {"tag": "Headline", "title": "The remaining", "body": RESHAPE["headline"]},
        {"tag": "Nisaba", "title": "Accountant", "body": RESHAPE["nisaba"]},
        {"tag": "Identity", "title": "Books", "body": IDENTITY},
        {
            "tag": "Wilderness",
            "title": "W",
            "body": (
                "Unused-as-product is a column. Unattested W cannot become "
                "remaining. The steward cannot spend it. The Third opens."
            ),
        },
        {
            "tag": "Hold",
            "title": "Ν",
            "body": (
                "Candidate becoming is held non-effective. Proposals are free. "
                "Ν does not grow with them. Overflow dies. Effectuation is "
                "undefined until seal consumes remaining and writes spend, "
                "cut, and burden. Not pending. Not the Bind sentence."
            ),
        },
        {"tag": "Civilization", "title": "Prior", "body": RESHAPE["civilization"]},
    ]
