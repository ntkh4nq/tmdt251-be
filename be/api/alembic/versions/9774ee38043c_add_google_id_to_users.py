"""Add google_id to users

Revision ID: 9774ee38043c
Revises: 
Create Date: 2025-12-20 19:07:48.988496

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9774ee38043c'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - only add google_id column."""
    # Add google_id column (ignore if already exists)
    op.execute("""
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS google_id VARCHAR(255) UNIQUE NULL
    """)
    
    # Make password_hashed nullable
    op.alter_column('users', 'password_hashed',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('users', 'password_hashed',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.drop_column('users', 'google_id')