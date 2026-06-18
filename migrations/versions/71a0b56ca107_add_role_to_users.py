"""Add role to users

Revision ID: 71a0b56ca107
Revises: 936f24dd2639
Create Date: 2026-06-18 23:16:43.697707

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '71a0b56ca107'
down_revision: Union[str, Sequence[str], None] = '936f24dd2639'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    userrole = sa.Enum('ADMIN', 'USER', name='userrole')
    userrole.create(op.get_bind())

    op.add_column('users', sa.Column('role', userrole, nullable=False, server_default='USER'))



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'role')
    # TODO: удалить enum-тип после удаления колонки
    sa.Enum(name='userrole').drop(op.get_bind())
