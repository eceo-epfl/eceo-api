"""Add geom to transect

Revision ID: 2383bd7f9d7a
Revises: 73c7306d0019
Create Date: 2024-05-21 13:29:45.744411

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision: str = '2383bd7f9d7a'
down_revision: Union[str, None] = '73c7306d0019'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_geospatial_column('transect', sa.Column('geom', Geometry(geometry_type='LINESTRING', srid=4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry'), nullable=True))
    op.create_geospatial_index('idx_transect_geom', 'transect', ['geom'], unique=False, postgresql_using='gist', postgresql_ops={})
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_geospatial_index('idx_transect_geom', table_name='transect', postgresql_using='gist', column_name='geom')
    op.drop_geospatial_column('transect', 'geom')
    # ### end Alembic commands ###
