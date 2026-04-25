import httpx
import pytest

from arb_finder.api.app import app
from arb_finder.engine import arb_math


@pytest.mark.asyncio
async def test_healthz() -> None:
    transport = httpx.ASGITransport(app=app)  # type: ignore[arg-type]
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_metrics_endpoint() -> None:
    transport = httpx.ASGITransport(app=app)  # type: ignore[arg-type]
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/metrics")
    assert resp.status_code == 200
    assert b"python_info" in resp.content


def test_arb_math_implied_sum() -> None:
    # Odds sourced from two books — genuine arb: implied sum < 1.0
    # 1/2.10 + 1/3.80 + 1/4.20 ≈ 0.477 + 0.263 + 0.238 = 0.978
    arb_odds = [2.10, 3.80, 4.20]
    s = arb_math.implied_sum(arb_odds)
    assert s == pytest.approx(1 / 2.10 + 1 / 3.80 + 1 / 4.20, rel=1e-9)
    assert s < 1.0
    assert arb_math.arb_exists(arb_odds, threshold=0.99)

    # Single-book odds with margin do NOT form an arb
    no_arb_odds = [2.10, 3.60, 3.80]
    assert not arb_math.arb_exists(no_arb_odds, threshold=1.0)

    # Stakes must sum to the requested total
    total = 100.0
    leg_stakes = arb_math.stakes(arb_odds, total)
    assert abs(sum(leg_stakes) - total) < 1e-9
