"""Add column type to vehicles table

Revision ID: 11775aebe91e
Revises: 6d9de603778f
Create Date: 2023-08-03 09:51:46.795201

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '11775aebe91e'
down_revision = '6d9de603778f'
branch_labels = None
depends_on = None


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('vehicles')
    op.drop_table('case_photo')
    op.drop_table('users')
    op.drop_table('case_access_token')
    op.drop_table('business')
    op.drop_table('cases')
    # ### end Alembic commands ###


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(table_name='vehicles', column=sa.Column('type', sa.Enum("car", "pickup"), nullable=False))
    """op.create_table('cases',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('business_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('vehicle_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('accident_number', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('created_at', mysql.DATETIME(), nullable=False),
    sa.Column('finished_at', mysql.DATETIME(), nullable=True),
    sa.Column('dropped', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('policy', mysql.VARCHAR(length=150), nullable=True),
    sa.Column('insured_name', mysql.VARCHAR(length=150), nullable=True),
    sa.Column('insured_dni', mysql.VARCHAR(length=150), nullable=True),
    sa.Column('insured_phone', mysql.VARCHAR(length=150), nullable=False),
    sa.Column('accident_date', mysql.DATETIME(), nullable=True),
    sa.Column('accident_place', mysql.VARCHAR(length=150), nullable=True),
    sa.Column('thef_type', mysql.ENUM('partial', 'inner', 'outside'), nullable=True),
    sa.ForeignKeyConstraint(['business_id'], ['business.id'], name='cases_ibfk_2', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='cases_ibfk_1', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], name='cases_ibfk_3', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('business',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', mysql.VARCHAR(length=150), nullable=False),
    sa.Column('case_dropped_letter', mysql.TEXT(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('case_access_token',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('access_token', mysql.VARCHAR(length=150), nullable=False),
    sa.Column('due_date', mysql.DATETIME(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('users',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', mysql.VARCHAR(length=150), nullable=False),
    sa.Column('username', mysql.VARCHAR(length=150), nullable=False),
    sa.Column('password', mysql.VARCHAR(length=150), nullable=False),
    sa.Column('disabled_at', mysql.DATETIME(), nullable=True),
    sa.Column('role', mysql.ENUM('operator', 'admin'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('case_photo',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('photo', sa.BLOB(), nullable=False),
    sa.Column('case_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('validated', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False),
    sa.Column('validation_attemps', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('metadata', mysql.VARCHAR(length=150), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('vehicles',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('brand', mysql.VARCHAR(length=150), nullable=False),
    sa.Column('model', mysql.VARCHAR(length=150), nullable=False),
    sa.Column('type', mysql.ENUM("car", "pickup"), nullable=False),
    sa.Column('licence_plate', mysql.VARCHAR(length=150), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )"""
    # ### end Alembic commands ###
