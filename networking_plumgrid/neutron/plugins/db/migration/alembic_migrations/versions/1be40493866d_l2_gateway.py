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

"""l2_gateway

Revision ID: 1be40493866d
Revises: 2df53910135e
Create Date: 2015-12-08 02:54:29.072922

"""

# revision identifiers, used by Alembic.
revision = '1be40493866d'
down_revision = '2df53910135e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'pgl2gateways',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('tenant_id', sa.String(length=36), nullable=True),
        sa.Column('vtep_ifc', sa.String(length=36), nullable=True),
        sa.Column('vtep_ip', sa.String(length=36), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'pgl2gatewaydevices',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('device_name', sa.String(length=255), nullable=False),
        sa.Column('device_ip', sa.String(length=36), nullable=True),
        sa.Column('l2_gateway_id', sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(
            ['l2_gateway_id'], ['pgl2gateways.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'pgl2gatewayinterfaces',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('interface_name', sa.String(length=255), nullable=False),
        sa.Column('device_id', sa.String(length=36), nullable=False),
        sa.Column('segmentation_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['device_id'], ['pgl2gatewaydevices.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'pgl2gatewayconnections',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=True),
        sa.Column('l2_gateway_id', sa.String(length=36), nullable=True),
        sa.Column('network_id', sa.String(length=36), nullable=True),
        sa.Column('port_id', sa.String(length=36), nullable=True),
        sa.Column('segmentation_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['l2_gateway_id'], ['pgl2gateways.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(
            ['network_id'], ['networks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
