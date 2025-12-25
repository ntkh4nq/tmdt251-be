"""fix_discount_type_enum

Revision ID: 81eff8f37fc2
Revises: 9774ee38043c
Create Date: 2025-12-25 12:52:18.851672

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '81eff8f37fc2'
down_revision: Union[str, Sequence[str], None] = '9774ee38043c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Bỏ các dòng tạo constraint đã tồn tại
    # Chỉ giữ lại phần fix discount_type enum
    
    # Drop old enum type và tạo lại
    op.execute("ALTER TABLE discounts ALTER COLUMN discount_type TYPE VARCHAR(50)")
    op.execute("DROP TYPE IF EXISTS discount_type")
    op.execute("CREATE TYPE discount_type AS ENUM ('percent', 'fixed')")
    op.execute("ALTER TABLE discounts ALTER COLUMN discount_type TYPE discount_type USING discount_type::discount_type")


def downgrade() -> None:
    """Downgrade schema."""
    pass