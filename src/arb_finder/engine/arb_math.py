"""Core arbitrage math — no I/O, no side-effects."""


def implied_sum(odds: list[float]) -> float:
    """Return Σ(1/oᵢ); < 1.0 means an arb exists."""
    return sum(1.0 / o for o in odds)


def arb_exists(odds: list[float], threshold: float = 0.99) -> bool:
    """True when the implied sum is below the operational threshold."""
    return implied_sum(odds) < threshold


def stakes(odds: list[float], total: float = 100.0) -> list[float]:
    """Return per-leg stake amounts that guarantee equal payout across all outcomes."""
    s = implied_sum(odds)
    payout = total / s
    return [payout / o for o in odds]


def margin_pct(odds: list[float]) -> float:
    """Return the bookmaker margin as a percentage (positive = no arb)."""
    return (implied_sum(odds) - 1.0) * 100.0
