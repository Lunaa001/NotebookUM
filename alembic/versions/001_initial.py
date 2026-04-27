"""Initial migration: add Usuario and Document models

Revision ID: 001_initial
Revises: 
Create Date: 2026-04-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create usuarios table
    op.create_table(
        'usuarios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('fecha_registro', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_usuarios_email'), 'usuarios', ['email'], unique=True)
    op.create_index(op.f('ix_usuarios_id'), 'usuarios', ['id'], unique=False)
    
    # Create documentos table
    op.create_table(
        'documentos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=False),
        sa.Column('nombre_archivo', sa.String(length=255), nullable=False),
        sa.Column('ruta_archivo', sa.String(length=500), nullable=False),
        sa.Column('texto_extraido', sa.Text(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documentos_id'), 'documentos', ['id'], unique=False)
    op.create_index(op.f('ix_documentos_usuario_id'), 'documentos', ['usuario_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_documentos_usuario_id'), table_name='documentos')
    op.drop_index(op.f('ix_documentos_id'), table_name='documentos')
    op.drop_table('documentos')
    
    op.drop_index(op.f('ix_usuarios_id'), table_name='usuarios')
    op.drop_index(op.f('ix_usuarios_email'), table_name='usuarios')
    op.drop_table('usuarios')
