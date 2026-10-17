"""The Ford Fusion must light up. The two planted miss-cases must stay dark."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ledger import (
    COVER_VIN,
    DEAD_VIN,
    FICTITIOUS_VIN,
    FUSION_ACCOUNT,
    FUSION_ACCOUNT_PLUS_DIGIT,
    FUSION_VIN,
    NEAR_VIN,
    NEAR_VIN_FLIP,
    OVERLAP_VIN,
    POISONED_VIN,
    _syn,
    build,
)
from match import analyze, hamming, solo_exceptions


def test_fusion_is_four_pledges_and_spv6_can_see_two_of_them_alone():
    report = analyze(build())
    fusion = next(hit for hit in report["exact"] if hit["vin"] == FUSION_VIN)
    assert fusion["pledge_count"] == 4
    assert fusion["across_facilities"] is True
    assert fusion["facilities"] == ["SPV4", "SPV6", "TAST-2024-3"]
    assert fusion["account_ids"].count(FUSION_ACCOUNT) == 3
    assert FUSION_ACCOUNT_PLUS_DIGIT in fusion["account_ids"]
    assert fusion["distinct_vehicles_if_vin_is_truthful"] == 1

    solo = solo_exceptions(build())
    assert solo["SPV6"][0]["vin"] == FUSION_VIN
    assert solo["SPV6"][0]["pledge_count"] == 2
    assert solo["SPV4"] == []
    assert solo["TAST-2024-3"] == []


def test_one_digit_vin_is_a_near_match_and_missing_from_the_dealer_file():
    report = analyze(build())
    near = report["near"]
    assert len(near) == 1
    pair = {near[0]["vin_a"], near[0]["vin_b"]}
    assert pair == {NEAR_VIN, NEAR_VIN_FLIP}
    assert near[0]["distance"] == 1
    assert hamming(NEAR_VIN, NEAR_VIN_FLIP) == 1
    absent = {hit["vin"] for hit in report["absent_from_dealer"]}
    assert NEAR_VIN_FLIP in absent
    assert NEAR_VIN not in absent


def test_single_tape_fictitious_vin_needs_the_dealer_export():
    report = analyze(build())
    exact_vins = {hit["vin"] for hit in report["exact"]}
    assert FICTITIOUS_VIN not in exact_vins
    absent = next(hit for hit in report["absent_from_dealer"] if hit["vin"] == FICTITIOUS_VIN)
    assert absent["facilities"] == ["SPV4"]
    assert absent["pledge_count"] == 1


def test_poisoned_dealer_row_and_vin_substitution_are_not_flagged():
    report = analyze(build())
    flagged = {hit["vin"] for hit in report["exact"]}
    flagged.update(hit["vin"] for hit in report["absent_from_dealer"])
    for hit in report["near"]:
        flagged.add(hit["vin_a"])
        flagged.add(hit["vin_b"])
    assert POISONED_VIN not in flagged
    assert COVER_VIN not in flagged
    assert DEAD_VIN not in flagged
    unflagged = {hit["vin"] for hit in report["unflagged"]}
    assert POISONED_VIN in unflagged
    assert COVER_VIN in unflagged


def test_overlap_stand_in_is_caught_and_clean_rows_are_not_exact_hits():
    report = analyze(build())
    overlap = next(hit for hit in report["exact"] if hit["vin"] == OVERLAP_VIN)
    assert overlap["facilities"] == ["TAST-2022-1", "TAST-2025-2"]
    exact_vins = {hit["vin"] for hit in report["exact"]}
    assert _syn(301) not in exact_vins
    assert FUSION_VIN not in {hit["vin"] for hit in report["absent_from_dealer"]}


def test_every_vin_is_seventeen_characters():
    ledger = build()
    vins = []
    for tape in ledger["tapes"].values():
        for row in tape:
            assert len(row["vin"]) == 17
            vins.append(row["vin"])
    for row in ledger["dealer_system"]:
        assert len(row["vin"]) == 17
        vins.append(row["vin"])
    close = []
    for i, left in enumerate(sorted(set(vins))):
        for right in sorted(set(vins))[i + 1 :]:
            if hamming(left, right) == 1:
                close.append((left, right))
    assert close == [tuple(sorted((NEAR_VIN, NEAR_VIN_FLIP)))]


def test_page_embeds_the_engine_report():
    import json
    from html.parser import HTMLParser

    import build_page

    build_page.main()
    html = build_page.OUT.read_text()
    assert "__PAYLOAD__" not in html

    class Grab(HTMLParser):
        def __init__(self):
            super().__init__()
            self.capture = False
            self.chunks = []

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            self.capture = tag == "script" and attrs.get("id") == "payload"

        def handle_endtag(self, tag):
            if tag == "script":
                self.capture = False

        def handle_data(self, data):
            if self.capture:
                self.chunks.append(data)

    grab = Grab()
    grab.feed(html)
    payload = json.loads("".join(grab.chunks))
    ledger = build()
    assert payload["report"] == analyze(ledger)
    assert payload["solo"] == solo_exceptions(ledger)
    assert payload["ledger"]["fusion_vin"] == FUSION_VIN
