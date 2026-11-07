"""Create the RaceOps foundation baseline.

Revision ID: 20261024_0001
Revises: None
Create Date: 2026-10-24
"""

from collections.abc import Sequence

revision: str = "20261024_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Establish the baseline without inventing domain tables."""
    pass


def downgrade() -> None:
    """Remove the baseline marker without dropping domain data."""
    pass
