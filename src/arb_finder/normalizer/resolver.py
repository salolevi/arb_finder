"""Canonical fixture and market resolution using alias dictionaries.

Phase 1 stub: resolves names to canonical slugs via alias lookups with
fallbacks. The full fixture-matching logic (kick-off time windowing,
cross-operator dedup, canonical_fixture_id assignment) is Phase 3.
"""

from __future__ import annotations

import re

from arb_finder.normalizer.aliases import COMPETITION_ALIASES, TEAM_ALIASES


def resolve_team(operator_brand: str, raw_name: str) -> str:
    """Return the canonical team slug for a raw operator team name."""
    name = raw_name.strip()
    direct = TEAM_ALIASES.get((operator_brand, name))
    if direct:
        return direct
    lower = name.lower()
    for (_, alias), canonical in TEAM_ALIASES.items():
        if alias.lower() == lower:
            return canonical
    return _slugify(name)


def resolve_competition(operator_brand: str, raw_name: str) -> str:
    """Return the canonical competition slug for a raw operator competition name."""
    name = raw_name.strip()
    direct = COMPETITION_ALIASES.get((operator_brand, name))
    if direct:
        return direct
    lower = name.lower()
    for (_, alias), canonical in COMPETITION_ALIASES.items():
        if alias.lower() == lower:
            return canonical
    return _slugify(name)


def _slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")
