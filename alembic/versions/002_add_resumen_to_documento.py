"""Add resumen field to documentos table

Revision ID: 002_add_resumen
Revises: 001_initial
Create Date: 2026-04-27 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_resumen'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('documentos', sa.Column('resumen', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('documentos', 'resumen')
