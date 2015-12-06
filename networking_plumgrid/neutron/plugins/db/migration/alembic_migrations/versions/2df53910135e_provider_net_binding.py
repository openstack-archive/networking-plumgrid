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

"""provider_net_binding

Revision ID: 2df53910135e
Revises: 51b361b5fa76
Create Date: 2015-12-03 21:39:21.991424

"""

# revision identifiers, used by Alembic.
revision = '2df53910135e'
down_revision = '51b361b5fa76'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'pg_provider_net_bindings',
        sa.Column('network_id', sa.String(length=36), nullable=False),
        sa.Column('network_type', sa.String(length=32), nullable=False),
        sa.Column('physical_network', sa.String(length=64), nullable=False),
        sa.Column('vlan_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['network_id'], ['networks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('network_id')
    )
