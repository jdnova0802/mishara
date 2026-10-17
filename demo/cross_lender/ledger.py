"""Public Tricolor pledge facts, plus synthetic rows that are labeled as synthetic.

The Ford Fusion row is the example in the noteholder complaint (VIN, vehicle,
mileage, balance, due date, and which facilities). The complaint does not
publish the account number. Placeholders stand in for the one-digit account
suffix it describes. Every other vehicle is invented for the demonstrator
and marked provenance="synthetic".
"""

from __future__ import annotations

FUSION_VIN = "3FA6P0H75JR262885"


def _syn(n: int) -> str:
    """17-character synthetic VIN. Not a real vehicle.

    n=11 and n=21 are the planted one-character pair. Every other id is
    mixed so that a one-digit change in n cannot land one character away
    from a different synthetic VIN.
    """
    alphabet = "ABCDEFGHJKLMNPRSTUVWXYZ23456789"
    if n == 21:
        chars = list(_syn(11))
        chars[3] = "Q" if chars[3] != "Q" else "Z"
        vin = "".join(chars)
    else:
        chars = []
        x = (n * 0x45D9F3B) & 0xFFFFFFFF
        for i in range(14):
            x = (x * 1664525 + 1013904223 + i * 97) & 0xFFFFFFFF
            chars.append(alphabet[x % len(alphabet)])
        vin = "SYN" + "".join(chars)
    if len(vin) != 17:
        raise ValueError(vin)
    return vin


# Planted one-character pair. The rest of the book must stay farther apart.
NEAR_VIN = _syn(11)
NEAR_VIN_FLIP = _syn(21)
FICTITIOUS_VIN = _syn(31)
POISONED_VIN = _syn(41)
DEAD_VIN = _syn(51)
COVER_VIN = _syn(61)
OVERLAP_VIN = _syn(71)

# Complaint: three of the four pledges used one account number; the second
# SPV6 pledge added a single digit. The digits themselves are not public.
FUSION_ACCOUNT = "UNPUBLISHED"
FUSION_ACCOUNT_PLUS_DIGIT = "UNPUBLISHED+1"

SOURCES = [
    {
        "id": "indictment",
        "title": "United States v. Chu and Goodgame, SDNY 25 Cr. 579",
        "use": "How borrowing-base files were built, SPV commitment sizes, and the within-file fraud (delinquency edits, fake payments in the dealer system).",
    },
    {
        "id": "sec",
        "title": "SEC v. Chu, Kollar, and Seibold, SDNY 26-cv-7041",
        "use": "VIN falsification, dead loans, and the double-pledged principal table.",
    },
    {
        "id": "noteholder",
        "title": "One William Street and others v. JPMorgan, Barclays, and Fifth Third (SDNY complaint)",
        "use": "The Ford Fusion clone, SPV4 as the JPMorgan facility, SPV6 as the Fifth Third facility, and the trustee's fictitious-loan count.",
    },
    {
        "id": "fitb-8k",
        "title": "Fifth Third 8-K filed 9 September 2025 and 10-Q for the quarter ended 30 September 2025",
        "use": "The only named dollar loss in a bank filing: about $200 million outstanding, $178 million charged off, $20 million specific allowance.",
    },
]


def _row(
    row_id,
    account_id,
    vin,
    year,
    make,
    model,
    mileage,
    principal,
    due,
    delinquency,
    provenance,
    note,
):
    vin = vin.upper()
    if len(vin) != 17:
        raise ValueError(f"{row_id} VIN {vin!r} is {len(vin)} characters, not 17")
    return {
        "row_id": row_id,
        "account_id": account_id,
        "vin": vin,
        "year": year,
        "make": make,
        "model": model,
        "mileage": mileage,
        "principal_reported": principal,
        "due": due,
        "delinquency_reported": delinquency,
        "provenance": provenance,
        "note": note,
    }


def build() -> dict:
    fusion = dict(
        year=2018,
        make="Ford",
        model="Fusion",
        mileage=101570,
        principal=14937.0,
        due="2023-04-15",
    )
    fusion_note = (
        "Pleading example, not a reconstructed full tape. "
        "Noteholder complaint: one 2018 Ford Fusion, this VIN, 101,570 miles, "
        "$14,937 principal, due 15 April 2023, pledged twice inside SPV6 "
        "(second account number adds one digit), again in SPV4, and again in TAST 2024-3."
    )

    # Synthetic clean book. Each VIN is on the dealer export and on one tape.
    clean = {
        "SPV3": _row(
            "spv3-clean-1", "SYN-3001", _syn(301),
            2019, "Nissan", "Sentra", 84000, 6200.0, "2027-03-01", "current",
            "synthetic", "Clean row. Invented so a single-lender tape is not only the fraud example.",
        ),
        "SPV4": _row(
            "spv4-clean-1", "SYN-4001", _syn(401),
            2020, "Hyundai", "Elantra", 61000, 9100.0, "2027-06-01", "current",
            "synthetic", "Clean row on the JPMorgan facility tape.",
        ),
        "SPV5": _row(
            "spv5-clean-1", "SYN-5001", _syn(501),
            2018, "Kia", "Forte", 99000, 4800.0, "2026-11-01", "current",
            "synthetic", "Clean row. Indictment: Seibold described SPV5 as the line they tried to keep relatively clean.",
        ),
        "SPV6": _row(
            "spv6-clean-1", "SYN-6001", _syn(601),
            2021, "Toyota", "Corolla", 45000, 11200.0, "2028-01-15", "current",
            "synthetic", "Clean row on the Fifth Third facility tape.",
        ),
        "TAST-2022-1": _row(
            "tast2022-clean-1", "SYN-T221", _syn(221),
            2017, "Chevrolet", "Malibu", 110000, 3900.0, "2026-08-01", "current",
            "synthetic", "Clean securitization row.",
        ),
        "TAST-2024-3": _row(
            "tast2024-clean-1", "SYN-T243", _syn(243),
            2019, "Honda", "Civic", 72000, 8700.0, "2027-09-01", "current",
            "synthetic", "Clean row in the securitization that also received the Fusion.",
        ),
        "TAST-2025-2": _row(
            "tast2025-clean-1", "SYN-T252", _syn(252),
            2020, "Volkswagen", "Jetta", 54000, 7600.0, "2028-04-01", "current",
            "synthetic", "Clean row. Not one of the 12,486 loans in the real TAST 2025-2 pool.",
        ),
    }

    # Stand-in for the pleaded TAST 2022-1 / TAST 2025-2 overlap.
    # One synthetic VIN, not one of the 3,225 loans the complaint identifies.
    overlap_vin = OVERLAP_VIN
    overlap_note = (
        "Synthetic stand-in. SEC complaint: of 12,486 loans in TAST 2025-2, "
        "at least 6,850 were also pledged elsewhere, including 3,225 loans "
        "still in TAST 2022-1. Double-pledged principal inside TAST 2025-2 "
        "was reported at $49,019,017.92. This row is not one of those loans."
    )

    # Near-duplicate: one digit, same other attributes, two facilities.
    near_real = NEAR_VIN
    near_flip = NEAR_VIN_FLIP
    near_attrs = dict(year=2016, make="Dodge", model="Journey", mileage=128440, principal=4100.0, due="2026-12-01")

    # Fictitious VIN on one tape only. Honest dealer export does not contain it.
    # Stands in for the trustee count (6,960 loans, $135,488,888), and is not one of those VINs.
    fict_vin = FICTITIOUS_VIN

    # Same fictitious pattern, but the originator also inserted the VIN into the
    # dealer export. Absence check misses. Cross-lender match misses.
    poisoned_vin = POISONED_VIN

    # VIN substitution: a charged-off dealer loan is not on any tape.
    # SPV5 instead pledges a different real VIN that is unpledged elsewhere,
    # marked current. No collision, no near-miss, VIN exists in the dealer file.
    dead_vin = DEAD_VIN
    cover_vin = COVER_VIN

    tapes = {
        "SPV3": [
            clean["SPV3"],
            _row(
                "spv3-near", "SYN-NEAR-A", near_real,
                near_attrs["year"], near_attrs["make"], near_attrs["model"],
                near_attrs["mileage"], near_attrs["principal"], near_attrs["due"],
                "current", "synthetic",
                "Synthetic illustration of a VIN later altered by one character on another tape. Not a pleaded VIN.",
            ),
        ],
        "SPV4": [
            clean["SPV4"],
            _row(
                "spv4-fusion", FUSION_ACCOUNT, FUSION_VIN,
                fusion["year"], fusion["make"], fusion["model"], fusion["mileage"],
                fusion["principal"], fusion["due"], "current", "pleading", fusion_note,
            ),
            _row(
                "spv4-fictitious", "SYN-FICT", fict_vin,
                2015, "Ford", "Focus", 140000, 5100.0, "2026-05-01", "current",
                "synthetic",
                "Synthetic fictitious VIN. Trustee analysis recited in the noteholder complaint: "
                "6,960 fictitious loans, $135,488,888, VINs absent from Tricolor's receivable records. "
                "This VIN is not one of those 6,960.",
            ),
        ],
        "SPV5": [
            clean["SPV5"],
            _row(
                "spv5-near", "SYN-NEAR-B", near_flip,
                near_attrs["year"], near_attrs["make"], near_attrs["model"],
                near_attrs["mileage"], near_attrs["principal"], near_attrs["due"],
                "current", "synthetic",
                "Same vehicle attributes as SYN-NEAR-A. The VIN differs by one character. "
                "Synthetic illustration of the SEC allegation that VINs were falsified. Not a pleaded VIN.",
            ),
            _row(
                "spv5-substitution", "SYN-SWAP", cover_vin,
                2014, "Chrysler", "200", 133000, 2750.0, "2026-02-01", "current",
                "synthetic",
                "Miss case. This VIN is a different car on the dealer export and is not pledged anywhere else. "
                "The charged-off loan (SYN-DEAD) never appears on a tape. Cross-lender VIN match does not fire.",
            ),
            _row(
                "spv5-poisoned", "SYN-POISON", poisoned_vin,
                2013, "Nissan", "Versa", 151000, 1900.0, "2025-12-01", "current",
                "synthetic",
                "Miss case. Fictitious loan that was also written into the dealer export, "
                "which is what the indictment describes when fake records were planted in the dealer system. "
                "One tape only, so there is no cross-lender duplicate.",
            ),
        ],
        "SPV6": [
            clean["SPV6"],
            _row(
                "spv6-fusion-a", FUSION_ACCOUNT, FUSION_VIN,
                fusion["year"], fusion["make"], fusion["model"], fusion["mileage"],
                fusion["principal"], fusion["due"], "current", "pleading", fusion_note,
            ),
            _row(
                "spv6-fusion-b", FUSION_ACCOUNT_PLUS_DIGIT, FUSION_VIN,
                fusion["year"], fusion["make"], fusion["model"], fusion["mileage"],
                fusion["principal"], fusion["due"], "current", "pleading",
                fusion_note + " Second SPV6 row: complaint says one digit was added to the account number.",
            ),
        ],
        "TAST-2022-1": [
            clean["TAST-2022-1"],
            _row(
                "tast2022-overlap", "SYN-OV-A", overlap_vin,
                2017, "Ford", "Escape", 102000, 5600.0, "2026-10-01", "current",
                "synthetic", overlap_note,
            ),
        ],
        "TAST-2024-3": [
            clean["TAST-2024-3"],
            _row(
                "tast2024-fusion", FUSION_ACCOUNT, FUSION_VIN,
                fusion["year"], fusion["make"], fusion["model"], fusion["mileage"],
                fusion["principal"], fusion["due"], "current", "pleading", fusion_note,
            ),
        ],
        "TAST-2025-2": [
            clean["TAST-2025-2"],
            _row(
                "tast2025-overlap", "SYN-OV-B", overlap_vin,
                2017, "Ford", "Escape", 102000, 5600.0, "2026-10-01", "current",
                "synthetic", overlap_note,
            ),
        ],
    }

    dealer = [
        _row(
            "dms-fusion", FUSION_ACCOUNT, FUSION_VIN,
            fusion["year"], fusion["make"], fusion["model"], fusion["mileage"],
            fusion["principal"], fusion["due"], "charged_off", "pleading",
            "Dealer export shows the Fusion once. Tapes reported it as current. "
            "The complaint's delinquency status for this specific VIN is not stated; "
            "charged_off here marks the general dead-loan pattern, not a pleaded status for this car.",
        ),
        *[
            _row(
                "dms-" + row["row_id"], row["account_id"], row["vin"],
                row["year"], row["make"], row["model"], row["mileage"],
                row["principal_reported"], row["due"], row["delinquency_reported"],
                "synthetic", "Dealer-system copy of a clean pledged loan.",
            )
            for row in clean.values()
        ],
        _row(
            "dms-near", "SYN-NEAR-A", near_real,
            near_attrs["year"], near_attrs["make"], near_attrs["model"],
            near_attrs["mileage"], near_attrs["principal"], near_attrs["due"],
            "current", "synthetic",
            "Honest dealer export has the original VIN only. The one-digit variant is not in this file.",
        ),
        _row(
            "dms-overlap", "SYN-OV-A", overlap_vin,
            2017, "Ford", "Escape", 102000, 5600.0, "2026-10-01", "current",
            "synthetic", "One car. Two securitization tapes.",
        ),
        _row(
            "dms-dead", "SYN-DEAD", dead_vin,
            2014, "Chrysler", "200", 133000, 2750.0, "2024-01-01", "180_plus_past_due",
            "synthetic",
            "Charged-off style loan. It is on no lender tape. The substitution row pledges a different VIN.",
        ),
        _row(
            "dms-cover", "SYN-COVER", cover_vin,
            2016, "Chrysler", "200", 88000, 6400.0, "2027-05-01", "current",
            "synthetic",
            "A real, separate, unpledged car. SPV5 reports this VIN. Matching it to the dealer file looks fine.",
        ),
        _row(
            "dms-poison", "SYN-POISON", poisoned_vin,
            2013, "Nissan", "Versa", 151000, 1900.0, "2025-12-01", "current",
            "synthetic",
            "Planted dealer-system row. Indictment: fake payments and pledge records were entered in the dealer system so a tie-out would pass.",
        ),
    ]

    facilities = [
        {
            "id": "SPV3",
            "holder": "Lender-3 in the indictment (a California investment manager). Not named there.",
            "commitment": "About $100 million total commitment (indictment).",
        },
        {
            "id": "SPV4",
            "holder": "Noteholder complaint calls this the JPMorgan facility. Indictment: about $770 million shared by Lender-4, Lender-5, and two New York mezzanine lenders.",
            "commitment": "About $770 million (indictment).",
        },
        {
            "id": "SPV5",
            "holder": "Named as a warehouse in the indictment. No public commitment figure in the pages read.",
            "commitment": "Not stated in the sources read.",
        },
        {
            "id": "SPV6",
            "holder": "Noteholder complaint: Fifth Third was administrative agent and warehouse lender on SPV6. Indictment Lender-8, about $250 million, opened August 2022.",
            "commitment": "About $250 million (indictment). Fifth Third's own loan on the borrower was about $200 million (8-K, 9 September 2025).",
        },
        {
            "id": "TAST-2022-1",
            "holder": "Tricolor Auto Securitization Trust 2022-1. Investors, not the warehouse banks.",
            "commitment": "SEC: 3,225 loans in this pool were also listed in TAST 2025-2.",
        },
        {
            "id": "TAST-2024-3",
            "holder": "Tricolor Auto Securitization Trust 2024-3. JPMorgan and Barclays underwrote it (noteholder complaint).",
            "commitment": "SEC double-pledged principal in this pool: $11,415,819.64.",
        },
        {
            "id": "TAST-2025-2",
            "holder": "Tricolor Auto Securitization Trust 2025-2.",
            "commitment": "SEC: 12,486 loans in the pool; about $49 million double-pledged principal on the August 2025 lender analysis.",
        },
    ]

    pleading_totals = [
        {"label": "Trustee forensic: borrowing base inflated by at least", "value": "$675 million", "source": "sec"},
        {"label": "Kollar's August 2025 tally: reported collateral vs internal system", "value": "$2.2 billion reported, about $1.4 billion internal, gap about $800 million", "source": "sec"},
        {"label": "Double-pledged principal inside TAST pools (one lender's August 2025 analysis)", "value": "$365,497,106.65", "source": "sec"},
        {"label": "Fictitious loans absent from Tricolor's own receivable records", "value": "6,960 loans, $135,488,888", "source": "noteholder"},
        {"label": "Fifth Third asset-backed finance loan", "value": "about $200 million outstanding; $178 million charged off; $20 million specific allowance", "source": "fitb-8k"},
        {"label": "Warehouse advance rate", "value": "About 60% to 80% of eligible balance (indictment). SEC complaint describes facilities generally at 70% to 80%.", "source": "indictment"},
    ]

    return {
        "title": "Tricolor cross-lender tape demonstrator",
        "as_of": "Pleadings and bank filings through the documents read on 17 October 2026",
        "fusion_vin": FUSION_VIN,
        "sources": SOURCES,
        "facilities": facilities,
        "pleading_totals": pleading_totals,
        "dealer_system": dealer,
        "tapes": tapes,
        "limits": [
            "Cross-lender VIN match sees a loan only when two tapes the matcher is allowed to read contain the same VIN, or VINs one character apart.",
            "A fictitious loan that sits on only one tape is invisible to that match. It shows up only if an honest dealer-system export is also in the room, and the VIN is missing from it.",
            "The indictment says fake payments and pledge records were typed into the dealer system, and that backup ledgers were fabricated for auditors. A dealer export the originator prepared will not catch a loan they also inserted there.",
            "An altered VIN that is not a one-character neighbor of another pledged VIN, and that belongs to a different real car in the dealer file, is not flagged. The charged-off loan it replaced never appears.",
            "This page does not re-check delinquency against principal decline. That is the check a warehouse analyst actually ran in August 2025, on columns already present in the borrowing base. It is a different control.",
            "SPV6's own tape contains the Fusion twice. A within-tape VIN dedupe, with no other lender involved, would have flagged that pair. SPV4 and TAST 2024-3 each show the Fusion once, so each of those tapes looks unique alone.",
            "Dollar totals in the side panel are pleading figures. They are not the sum of this toy tape. Synthetic rows are not Tricolor loans.",
        ],
    }
