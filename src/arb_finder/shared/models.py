from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Enumerations (values must match the Postgres enum types in the migration)
# ---------------------------------------------------------------------------


class SourceKind(StrEnum):
    HTML_PUBLIC = "html_public"
    BROWSER_DOM = "browser_dom"
    BROWSER_XHR = "browser_xhr"
    BROWSER_WS = "browser_ws"


class MarketFamily(StrEnum):
    FT_1X2 = "FT_1X2"
    FT_OU = "FT_OU"
    FT_BTTS = "FT_BTTS"


class Period(StrEnum):
    FT = "FT"
    FIRST_HALF = "1H"  # DB value is the string "1H"


class SelectionCode(StrEnum):
    HOME = "HOME"
    DRAW = "DRAW"
    AWAY = "AWAY"
    OVER = "OVER"
    UNDER = "UNDER"


class OpportunityState(StrEnum):
    NEW = "new"
    IMPROVED = "improved"
    STALE = "stale"
    EXPIRED = "expired"


# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------


class OddsSnapshot(Base):
    """Immutable, append-only row per (operator, market, selection) observation.

    Declared as a TimescaleDB hypertable partitioned on fetched_at_utc.
    Foreign keys TO this table are not supported by TimescaleDB; callers
    must store snapshot_id and join at query time.
    """

    __tablename__ = "odds_snapshot"
    __table_args__ = (
        sa.Index(
            "ix_odds_snapshot_operator_fetched",
            "operator_brand",
            "jurisdiction",
            "fetched_at_utc",
        ),
        sa.Index(
            "ix_odds_snapshot_fixture_market",
            "canonical_fixture_id",
            "market_family",
            "fetched_at_utc",
        ),
        sa.Index("ix_odds_snapshot_raw_hash", "raw_hash"),
    )

    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    operator_brand: Mapped[str] = mapped_column(sa.String(64))
    jurisdiction: Mapped[str] = mapped_column(sa.String(32))
    hostname: Mapped[str] = mapped_column(sa.String(255))
    source_kind: Mapped[SourceKind] = mapped_column(
        sa.Enum(SourceKind, name="source_kind_enum")
    )
    requires_session: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    fetched_at_utc: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), server_default=sa.func.now()
    )
    canonical_fixture_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    sport: Mapped[str] = mapped_column(sa.String(32), default="football")
    competition: Mapped[str] = mapped_column(sa.String(128))
    home_team: Mapped[str] = mapped_column(sa.String(128))
    away_team: Mapped[str] = mapped_column(sa.String(128))
    kickoff_utc: Mapped[datetime] = mapped_column(sa.TIMESTAMP(timezone=True))
    is_live: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    market_family: Mapped[MarketFamily] = mapped_column(
        sa.Enum(MarketFamily, name="market_family_enum")
    )
    period: Mapped[Period] = mapped_column(sa.Enum(Period, name="period_enum"))
    line_value: Mapped[Decimal | None] = mapped_column(sa.Numeric(10, 4), nullable=True)
    selection_code: Mapped[SelectionCode] = mapped_column(
        sa.Enum(SelectionCode, name="selection_code_enum")
    )
    odds_decimal: Mapped[Decimal] = mapped_column(sa.Numeric(10, 4))
    source_url: Mapped[str] = mapped_column(sa.Text)
    raw_hash: Mapped[str] = mapped_column(sa.String(64))
    raw_payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)


class ArbOpportunity(Base):
    """A detected arbitrage opportunity, from candidate through confirmation."""

    __tablename__ = "arb_opportunity"
    __table_args__ = (
        sa.Index("ix_arb_opportunity_state", "state"),
        sa.Index("ix_arb_opportunity_fixture", "canonical_fixture_id"),
    )

    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    detected_at_utc: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), server_default=sa.func.now()
    )
    canonical_fixture_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    sport: Mapped[str] = mapped_column(sa.String(32), default="football")
    competition: Mapped[str] = mapped_column(sa.String(128))
    home_team: Mapped[str] = mapped_column(sa.String(128))
    away_team: Mapped[str] = mapped_column(sa.String(128))
    kickoff_utc: Mapped[datetime] = mapped_column(sa.TIMESTAMP(timezone=True))
    market_family: Mapped[MarketFamily] = mapped_column(
        sa.Enum(MarketFamily, name="market_family_enum")
    )
    period: Mapped[Period] = mapped_column(sa.Enum(Period, name="period_enum"))
    line_value: Mapped[Decimal | None] = mapped_column(sa.Numeric(10, 4), nullable=True)
    implied_sum: Mapped[Decimal] = mapped_column(sa.Numeric(10, 6))
    theoretical_margin_pct: Mapped[Decimal] = mapped_column(sa.Numeric(8, 4))
    realizable_margin_pct: Mapped[Decimal] = mapped_column(sa.Numeric(8, 4))
    total_stake: Mapped[Decimal] = mapped_column(sa.Numeric(12, 2))
    state: Mapped[OpportunityState] = mapped_column(
        sa.Enum(OpportunityState, name="opportunity_state_enum"),
        default=OpportunityState.NEW,
    )
    confirmed_at_utc: Mapped[datetime | None] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=True
    )
    requoted_at_utc: Mapped[datetime | None] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=True
    )
    expires_at_utc: Mapped[datetime | None] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=True
    )

    legs: Mapped[list[ArbLeg]] = relationship(
        "ArbLeg", back_populates="opportunity", cascade="all, delete-orphan"
    )
    deliveries: Mapped[list[NotificationDelivery]] = relationship(
        "NotificationDelivery", back_populates="opportunity", cascade="all, delete-orphan"
    )


class ArbLeg(Base):
    """One side of an arbitrage opportunity (one operator + one selection)."""

    __tablename__ = "arb_leg"
    __table_args__ = (sa.Index("ix_arb_leg_opportunity", "opportunity_id"),)

    leg_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("arb_opportunity.opportunity_id", ondelete="CASCADE"),
    )
    # No FK to odds_snapshot — TimescaleDB does not support FK references to a hypertable.
    snapshot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    operator_brand: Mapped[str] = mapped_column(sa.String(64))
    jurisdiction: Mapped[str] = mapped_column(sa.String(32))
    selection_code: Mapped[SelectionCode] = mapped_column(
        sa.Enum(SelectionCode, name="selection_code_enum")
    )
    odds_decimal: Mapped[Decimal] = mapped_column(sa.Numeric(10, 4))
    stake: Mapped[Decimal] = mapped_column(sa.Numeric(12, 2))
    stake_rounded: Mapped[Decimal | None] = mapped_column(sa.Numeric(12, 2), nullable=True)

    opportunity: Mapped[ArbOpportunity] = relationship("ArbOpportunity", back_populates="legs")


class NotificationDelivery(Base):
    """Tracks the Telegram message lifecycle for one arb opportunity."""

    __tablename__ = "notification_delivery"
    __table_args__ = (
        sa.Index("ix_notification_delivery_opportunity", "opportunity_id"),
        sa.Index("ix_notification_delivery_dedupe", "dedupe_hash"),
    )

    delivery_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("arb_opportunity.opportunity_id", ondelete="CASCADE"),
    )
    telegram_chat_id: Mapped[str] = mapped_column(sa.String(64))
    telegram_message_id: Mapped[int | None] = mapped_column(sa.BigInteger, nullable=True)
    state: Mapped[OpportunityState] = mapped_column(
        sa.Enum(OpportunityState, name="opportunity_state_enum")
    )
    dedupe_hash: Mapped[str] = mapped_column(sa.String(64))
    sent_at_utc: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), server_default=sa.func.now()
    )
    last_edited_at_utc: Mapped[datetime | None] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=True
    )

    opportunity: Mapped[ArbOpportunity] = relationship(
        "ArbOpportunity", back_populates="deliveries"
    )
