"""insured_adress_column_aggregation

Revision ID: 7a989b6d8e00
Revises: ebdb14ea7e02
Create Date: 2023-09-22 09:23:37.741030

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a989b6d8e00'
down_revision = 'ebdb14ea7e02'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(table_name='cases', column=sa.Column('insured_address', sa.String(255), nullable=False))


def downgrade() -> None:
    pass
