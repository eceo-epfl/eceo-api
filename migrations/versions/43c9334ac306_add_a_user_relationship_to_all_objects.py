"""Add a user relationship to all objects

Revision ID: 43c9334ac306
Revises: 395a34832513
Create Date: 2024-05-23 16:19:12.723057

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '43c9334ac306'
down_revision: Union[str, None] = '395a34832513'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('inputobject', sa.Column('owner', sqlmodel.sql.sqltypes.GUID(), nullable=True))
    op.add_column('submission', sa.Column('owner', sqlmodel.sql.sqltypes.GUID(), nullable=True))
    op.add_column('transect', sa.Column('owner', sqlmodel.sql.sqltypes.GUID(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('transect', 'owner')
    op.drop_column('submission', 'owner')
    op.drop_column('inputobject', 'owner')
    # ### end Alembic commands ###
