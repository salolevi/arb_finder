"""Tests for canonical alias lookups and the resolver functions."""

import pytest

from arb_finder.normalizer.aliases import COMPETITION_ALIASES, TEAM_ALIASES
from arb_finder.normalizer.resolver import resolve_competition, resolve_team

# ── alias dictionary structure ───────────────────────────────────────────────


def test_all_alias_keys_are_two_tuples() -> None:
    for key in TEAM_ALIASES:
        assert isinstance(key, tuple)
        assert len(key) == 2
    for key in COMPETITION_ALIASES:
        assert isinstance(key, tuple)
        assert len(key) == 2


def test_all_alias_values_are_slugs() -> None:
    import re

    slug_re = re.compile(r"^[a-z0-9_]+$")
    for canonical in TEAM_ALIASES.values():
        assert slug_re.match(canonical), f"Bad slug: {canonical!r}"
    for canonical in COMPETITION_ALIASES.values():
        assert slug_re.match(canonical), f"Bad slug: {canonical!r}"


# ── team resolution ───────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("operator", "raw", "expected"),
    [
        ("bplay", "River Plate", "river_plate"),
        ("bplay", "River", "river_plate"),
        ("betsson", "Boca Juniors", "boca_juniors"),
        ("betano", "Vélez Sársfield", "velez_sarsfield"),
        ("bplay", "Newell's Old Boys", "newells_old_boys"),
        ("bplay", "Huracán", "huracan"),
        ("bplay", "Huracan", "huracan"),  # accent-free variant
    ],
)
def test_resolve_team_known_aliases(operator: str, raw: str, expected: str) -> None:
    assert resolve_team(operator, raw) == expected


def test_resolve_team_strips_whitespace() -> None:
    assert resolve_team("bplay", "  River Plate  ") == "river_plate"


def test_resolve_team_cross_operator_fallback() -> None:
    # "betano" has "River Plate" mapped; an unknown operator should still resolve
    # via the cross-operator scan
    result = resolve_team("unknown_operator", "River Plate")
    assert result == "river_plate"


def test_resolve_team_slugify_fallback() -> None:
    result = resolve_team("bplay", "Club Desconocido FC")
    assert result == "club_desconocido_fc"


# ── competition resolution ────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("operator", "raw", "expected"),
    [
        ("bplay", "Liga Profesional", "arg_primera_division"),
        ("bplay", "Copa Argentina", "arg_copa_argentina"),
        ("betano", "Argentina - Liga Profesional", "arg_primera_division"),
        ("betsson", "Copa de la Liga Profesional", "arg_copa_de_la_liga"),
    ],
)
def test_resolve_competition_known_aliases(
    operator: str, raw: str, expected: str
) -> None:
    assert resolve_competition(operator, raw) == expected


def test_resolve_competition_slugify_fallback() -> None:
    result = resolve_competition("bplay", "Liga Desconocida 2025")
    assert result == "liga_desconocida_2025"
