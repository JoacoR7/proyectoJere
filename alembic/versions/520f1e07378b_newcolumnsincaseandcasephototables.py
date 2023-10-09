"""newColumnsInCaseAndCasePhotoTables

Revision ID: 520f1e07378b
Revises: 7a989b6d8e00
Create Date: 2023-10-09 17:13:33.142880

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '520f1e07378b'
down_revision = '7a989b6d8e00'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(table_name='cases', column=sa.Column('car_use', sa.String(50), nullable=False))
    op.add_column(table_name='cases', column=sa.Column('driver_name', sa.String(255), nullable=False))
    op.add_column(table_name='cases', column=sa.Column('driver_occupation', sa.String(255), nullable=False))
    op.add_column(table_name='case_photo', column=sa.Column('detail', sa.String(255), nullable=False))

def downgrade() -> None:
    pass
