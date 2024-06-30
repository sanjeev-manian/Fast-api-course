"""create role on users table

Revision ID: 05f2e06fd2f7
Revises: 
Create Date: 2024-06-19 18:05:41.790979

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "05f2e06fd2f7"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("role", sa.String, nullable=True))
    op.create_table


def downgrade() -> None:
    op.drop_column("users", "role")
