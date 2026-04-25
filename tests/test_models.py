"""Smoke tests for the SQLAlchemy models — no DB connection required."""

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from arb_finder.shared.models import (
    ArbLeg,
    ArbOpportunity,
    Base,
    MarketFamily,
    NotificationDelivery,
    OddsSnapshot,
    OpportunityState,
    Period,
    SelectionCode,
    SourceKind,
)


def test_all_tables_registered() -> None:
    tables = set(Base.metadata.tables.keys())
    assert tables == {"odds_snapshot", "arb_opportunity", "arb_leg", "notification_delivery"}


def test_source_kind_values() -> None:
    assert SourceKind.HTML_PUBLIC == "html_public"
    assert SourceKind.BROWSER_DOM == "browser_dom"
    assert SourceKind.BROWSER_XHR == "browser_xhr"
    assert SourceKind.BROWSER_WS == "browser_ws"


def test_market_family_values() -> None:
    assert MarketFamily.FT_1X2 == "FT_1X2"
    assert MarketFamily.FT_OU == "FT_OU"
    assert MarketFamily.FT_BTTS == "FT_BTTS"


def test_period_first_half_db_value() -> None:
    # DB stores the string "1H" — not the Python identifier name
    assert Period.FIRST_HALF == "1H"
    assert Period.FT == "FT"


def test_selection_code_values() -> None:
    expected = {"HOME", "DRAW", "AWAY", "OVER", "UNDER"}
    assert {s.value for s in SelectionCode} == expected


def test_opportunity_state_transition_order() -> None:
    states = [s.value for s in OpportunityState]
    assert states == ["new", "improved", "stale", "expired"]


def test_odds_snapshot_instantiation() -> None:
    now = datetime.now(tz=UTC)
    snap = OddsSnapshot(
        snapshot_id=uuid.uuid4(),
        operator_brand="bplay",
        jurisdiction="caba",
        hostname="www.bplay.bet.ar",
        source_kind=SourceKind.HTML_PUBLIC,
        requires_session=False,
        fetched_at_utc=now,
        sport="football",
        competition="arg_primera_division",
        home_team="river_plate",
        away_team="boca_juniors",
        kickoff_utc=now,
        is_live=False,
        market_family=MarketFamily.FT_1X2,
        period=Period.FT,
        selection_code=SelectionCode.HOME,
        odds_decimal=Decimal("2.10"),
        source_url="https://www.bplay.bet.ar/deportes/futbol",
        raw_hash="a" * 64,
    )
    assert snap.operator_brand == "bplay"
    assert snap.odds_decimal == Decimal("2.10")
    assert snap.canonical_fixture_id is None  # nullable until normalizer runs


def test_arb_opportunity_default_state() -> None:
    opp = ArbOpportunity(
        opportunity_id=uuid.uuid4(),
        canonical_fixture_id=uuid.uuid4(),
        competition="arg_primera_division",
        home_team="river_plate",
        away_team="boca_juniors",
        kickoff_utc=datetime.now(tz=UTC),
        market_family=MarketFamily.FT_1X2,
        period=Period.FT,
        implied_sum=Decimal("0.978"),
        theoretical_margin_pct=Decimal("-2.25"),
        realizable_margin_pct=Decimal("-2.10"),
        total_stake=Decimal("100.00"),
        state=OpportunityState.NEW,
    )
    assert opp.state == OpportunityState.NEW
    assert opp.confirmed_at_utc is None


def test_arb_leg_no_fk_to_hypertable() -> None:
    # snapshot_id exists as a plain UUID column (no FK) — this is intentional
    cols = {c.name for c in ArbLeg.__table__.columns}
    assert "snapshot_id" in cols
    fk_targets = {fk.target_fullname for fk in ArbLeg.__table__.foreign_keys}
    assert not any("odds_snapshot" in t for t in fk_targets)


def test_notification_delivery_instantiation() -> None:
    opp_id = uuid.uuid4()
    delivery = NotificationDelivery(
        delivery_id=uuid.uuid4(),
        opportunity_id=opp_id,
        telegram_chat_id="-100123456789",
        state=OpportunityState.NEW,
        dedupe_hash="b" * 64,
        sent_at_utc=datetime.now(tz=UTC),
    )
    assert delivery.telegram_message_id is None
    assert delivery.opportunity_id == opp_id
