"""Tests for crucial_roles module."""

from gate.crucial_roles import (
    DREAM_SEAT_ID,
    INSEPARABLE_TWIN_ID,
    MOST_VITAL_S_TIER_ID,
    RoleTier,
    crucial_roles_manifest,
    get_role,
    roles_by_tier,
)


def test_manifest_structure():
    m = crucial_roles_manifest()
    assert m["doctrine"] == "crucial_roles"
    assert m["version"] == "1.0.0"
    assert m["total_roles"] == 35
    assert m["dream_seat"]["id"] == DREAM_SEAT_ID
    assert m["most_vital_s_tier"]["id"] == MOST_VITAL_S_TIER_ID
    assert m["inseparable_twin"]["prove_id"] == INSEPARABLE_TWIN_ID
    assert m["spec"] == "gate/CRUCIAL_ROLES.md"


def test_tier_counts():
    m = crucial_roles_manifest()
    assert m["tiers"]["S"]["count"] == 10
    assert m["tiers"]["A"]["count"] == 8
    assert m["tiers"]["B"]["count"] == 6
    assert m["tiers"]["C"]["count"] == 5
    assert m["tiers"]["NOT"]["count"] == 6


def test_cic_is_s_tier_and_load_bearing_wall():
    cic = get_role("cic")
    assert cic is not None
    assert cic.tier == RoleTier.S
    assert cic.title.startswith("Chief of Irreversibility Clearance")
    assert not cic.load_bearing_for_cic  # CIC is the throne, not a wall

    load_bearing = crucial_roles_manifest()["load_bearing_for_cic"]
    assert "stranger_prove_custodian" in load_bearing
    assert "bone_law_engineer" in load_bearing
    assert "cic" not in load_bearing


def test_enterable_path():
    m = crucial_roles_manifest()
    assert m["enterable_path"]["tiers"] == ["C", "B", "A", "S"]
    assert m["enterable_path"]["microscopic_version_now"] == "Bind Room"


def test_roles_by_tier():
    s_roles = roles_by_tier(RoleTier.S)
    assert len(s_roles) == 10
    assert s_roles[0].id == "cic"
