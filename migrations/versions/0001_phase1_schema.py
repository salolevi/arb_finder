"""Phase 1 schema: odds_snapshot (hypertable), arb_opportunity, arb_leg, notification_delivery.

Revision ID: 0001
Revises:
Create Date: 2026-04-25
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── Prerequisites ────────────────────────────────────────────────────────
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE")

    # ── Postgres enum types ──────────────────────────────────────────────────
    op.execute(
        "CREATE TYPE source_kind_enum AS ENUM "
        "('html_public', 'browser_dom', 'browser_xhr', 'browser_ws')"
    )
    op.execute(
        "CREATE TYPE market_family_enum AS ENUM ('FT_1X2', 'FT_OU', 'FT_BTTS')"
    )
    op.execute("CREATE TYPE period_enum AS ENUM ('FT', '1H')")
    op.execute(
        "CREATE TYPE selection_code_enum AS ENUM "
        "('HOME', 'DRAW', 'AWAY', 'OVER', 'UNDER')"
    )
    op.execute(
        "CREATE TYPE opportunity_state_enum AS ENUM "
        "('new', 'improved', 'stale', 'expired')"
    )

    # ── odds_snapshot ────────────────────────────────────────────────────────
    # Created before the hypertable call; must not have any FK constraints
    # pointing at it (TimescaleDB limitation).
    op.create_table(
        "odds_snapshot",
        sa.Column("snapshot_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("operator_brand", sa.String(64), nullable=False),
        sa.Column("jurisdiction", sa.String(32), nullable=False),
        sa.Column("hostname", sa.String(255), nullable=False),
        sa.Column(
            "source_kind",
            sa.Enum(name="source_kind_enum", create_type=False),
            nullable=False,
        ),
        sa.Column(
            "requires_session",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "fetched_at_utc",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("canonical_fixture_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "sport", sa.String(32), nullable=False, server_default=sa.text("'football'")
        ),
        sa.Column("competition", sa.String(128), nullable=False),
        sa.Column("home_team", sa.String(128), nullable=False),
        sa.Column("away_team", sa.String(128), nullable=False),
        sa.Column("kickoff_utc", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column(
            "is_live", sa.Boolean, nullable=False, server_default=sa.text("false")
        ),
        sa.Column(
            "market_family",
            sa.Enum(name="market_family_enum", create_type=False),
            nullable=False,
        ),
        sa.Column(
            "period", sa.Enum(name="period_enum", create_type=False), nullable=False
        ),
        sa.Column("line_value", sa.Numeric(10, 4), nullable=True),
        sa.Column(
            "selection_code",
            sa.Enum(name="selection_code_enum", create_type=False),
            nullable=False,
        ),
        sa.Column("odds_decimal", sa.Numeric(10, 4), nullable=False),
        sa.Column("source_url", sa.Text, nullable=False),
        sa.Column("raw_hash", sa.String(64), nullable=False),
        sa.Column("raw_payload", postgresql.JSONB, nullable=True),
    )

    # Promote to TimescaleDB hypertable (partitioned by time)
    op.execute("SELECT create_hypertable('odds_snapshot', 'fetched_at_utc')")

    op.create_index(
        "ix_odds_snapshot_operator_fetched",
        "odds_snapshot",
        ["operator_brand", "jurisdiction", "fetched_at_utc"],
    )
    op.create_index(
        "ix_odds_snapshot_fixture_market",
        "odds_snapshot",
        ["canonical_fixture_id", "market_family", "fetched_at_utc"],
    )
    op.create_index("ix_odds_snapshot_raw_hash", "odds_snapshot", ["raw_hash"])

    # ── arb_opportunity ──────────────────────────────────────────────────────
    op.create_table(
        "arb_opportunity",
        sa.Column("opportunity_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "detected_at_utc",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("canonical_fixture_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "sport", sa.String(32), nullable=False, server_default=sa.text("'football'")
        ),
        sa.Column("competition", sa.String(128), nullable=False),
        sa.Column("home_team", sa.String(128), nullable=False),
        sa.Column("away_team", sa.String(128), nullable=False),
        sa.Column("kickoff_utc", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column(
            "market_family",
            sa.Enum(name="market_family_enum", create_type=False),
            nullable=False,
        ),
        sa.Column(
            "period", sa.Enum(name="period_enum", create_type=False), nullable=False
        ),
        sa.Column("line_value", sa.Numeric(10, 4), nullable=True),
        sa.Column("implied_sum", sa.Numeric(10, 6), nullable=False),
        sa.Column("theoretical_margin_pct", sa.Numeric(8, 4), nullable=False),
        sa.Column("realizable_margin_pct", sa.Numeric(8, 4), nullable=False),
        sa.Column("total_stake", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "state",
            sa.Enum(name="opportunity_state_enum", create_type=False),
            nullable=False,
            server_default=sa.text("'new'"),
        ),
        sa.Column("confirmed_at_utc", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("requoted_at_utc", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("expires_at_utc", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index("ix_arb_opportunity_state", "arb_opportunity", ["state"])
    op.create_index(
        "ix_arb_opportunity_fixture", "arb_opportunity", ["canonical_fixture_id"]
    )

    # ── arb_leg ───────────────────────────────────────────────────────────────
    op.create_table(
        "arb_leg",
        sa.Column("leg_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "opportunity_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("arb_opportunity.opportunity_id", ondelete="CASCADE"),
            nullable=False,
        ),
        # snapshot_id intentionally has no FK — TimescaleDB hypertables do not
        # support being the target of a foreign key from a regular table.
        sa.Column("snapshot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("operator_brand", sa.String(64), nullable=False),
        sa.Column("jurisdiction", sa.String(32), nullable=False),
        sa.Column(
            "selection_code",
            sa.Enum(name="selection_code_enum", create_type=False),
            nullable=False,
        ),
        sa.Column("odds_decimal", sa.Numeric(10, 4), nullable=False),
        sa.Column("stake", sa.Numeric(12, 2), nullable=False),
        sa.Column("stake_rounded", sa.Numeric(12, 2), nullable=True),
    )
    op.create_index("ix_arb_leg_opportunity", "arb_leg", ["opportunity_id"])

    # ── notification_delivery ─────────────────────────────────────────────────
    op.create_table(
        "notification_delivery",
        sa.Column("delivery_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "opportunity_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("arb_opportunity.opportunity_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("telegram_chat_id", sa.String(64), nullable=False),
        sa.Column("telegram_message_id", sa.BigInteger, nullable=True),
        sa.Column(
            "state",
            sa.Enum(name="opportunity_state_enum", create_type=False),
            nullable=False,
        ),
        sa.Column("dedupe_hash", sa.String(64), nullable=False),
        sa.Column(
            "sent_at_utc",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("last_edited_at_utc", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_notification_delivery_opportunity",
        "notification_delivery",
        ["opportunity_id"],
    )
    op.create_index(
        "ix_notification_delivery_dedupe", "notification_delivery", ["dedupe_hash"]
    )


def downgrade() -> None:
    op.drop_table("notification_delivery")
    op.drop_table("arb_leg")
    op.drop_table("arb_opportunity")
    op.drop_table("odds_snapshot")  # also drops the hypertable metadata

    op.execute("DROP TYPE IF EXISTS opportunity_state_enum")
    op.execute("DROP TYPE IF EXISTS selection_code_enum")
    op.execute("DROP TYPE IF EXISTS period_enum")
    op.execute("DROP TYPE IF EXISTS market_family_enum")
    op.execute("DROP TYPE IF EXISTS source_kind_enum")
