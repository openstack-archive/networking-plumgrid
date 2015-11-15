# Copyright 2015 PLUMgrid, Inc. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""phy_att_point

Revision ID: 351c4f5710e7
Revises: 1be40493866d
Create Date: 2015-12-14 07:01:48.954910

"""

# revision identifiers, used by Alembic.
revision = '351c4f5710e7'
down_revision = '1be40493866d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'pg_transit_domains',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('tenant_id', sa.String(length=36), nullable=True),
        sa.Column('implicit', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'pg_physical_attachment_points',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('tenant_id', sa.String(length=36), nullable=True),
        sa.Column('implicit', sa.Boolean(), nullable=True),
        sa.Column('lacp', sa.Boolean(), nullable=False),
        sa.Column('hash_mode', sa.String(length=255), nullable=True),
        sa.Column('transit_domain_id', sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(
            ['transit_domain_id'], ['pg_transit_domains.id'],
            ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'pg_physical_attachment_point_interfaces',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('hostname', sa.String(length=255), nullable=False),
        sa.Column('interface', sa.String(length=255), nullable=True),
        sa.Column('pap_id', sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(
            ['pap_id'], ['pg_physical_attachment_points.id'],
            ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
