# Copyright 2016 PLUMgrid, Inc. All Rights Reserved.
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

"""endpoint group

Revision ID: 202cb6b05811
Revises: 351c4f5710e7
Create Date: 2016-04-24 00:50:34.678718

"""

# revision identifiers, used by Alembic.
revision = '202cb6b05811'
down_revision = '351c4f5710e7'

from alembic import op
import sqlalchemy as sa


policy_protocol_enum = sa.Enum('any', 'tcp', 'udp', 'icmp',
                              name='pg_endpoint_policies_protocol')
policy_action_enum = sa.Enum('copy',
                             name='pg_endpoint_policies_action')
endpoint_type_enum = sa.Enum('vm_ep', 'vm_class',
                             name='pg_endpoint_groups_endpoint_type')


def upgrade():
    op.create_table(
        'pg_endpoint_groups',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('description', sa.String(length=1024), nullable=True),
        sa.Column('endpoint_type', endpoint_type_enum, nullable=True),
        sa.Column('tenant_id', sa.String(length=36), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'pg_endpoint_policies',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('src_grp', sa.String(length=36), nullable=True),
        sa.Column('dst_grp', sa.String(length=36), nullable=True),
        sa.Column('protocol', policy_protocol_enum, nullable=False),
        sa.Column('src_port_range', sa.String(length=255), nullable=True),
        sa.Column('dst_port_range', sa.String(length=255), nullable=True),
        sa.Column('action', policy_action_enum, nullable=False),
        sa.Column('service_epg', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(['service_epg'], ['pg_endpoint_groups.id'],
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['src_grp'], ['pg_endpoint_groups.id'],
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['dst_grp'], ['pg_endpoint_groups.id'],
                                ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'pg_endpoint_group_port_binding',
        sa.Column('port_id', sa.String(length=36), nullable=False),
        sa.Column('endpoint_group_id', sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(['port_id'], ['ports.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['endpoint_group_id'],
                                ['pg_endpoint_groups.id'])
    )
