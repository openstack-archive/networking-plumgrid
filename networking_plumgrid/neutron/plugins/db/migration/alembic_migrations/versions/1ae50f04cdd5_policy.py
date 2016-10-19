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

"""policy

Revision ID: 1ae50f04cdd5
Revises: 351c4f5710e7
Create Date: 2016-07-29 15:35:12.194948

"""

# revision identifiers, used by Alembic.
revision = '1ae50f04cdd5'
down_revision = '351c4f5710e7'

from alembic import op
import sqlalchemy as sa

tag_enum = sa.Enum('dot1q', 'fip', 'nsh',
                   name='pg_policy_tags_type')
direction_enum = sa.Enum('ingress', 'egress', 'bidirectional',
                         name='pg_port_group_direction')
policy_rule_protocol_enum = sa.Enum('any', 'tcp', 'udp', 'icmp',
                                    name='pg_policy_rule_protocol')
policy_action_enum = sa.Enum('allow', 'copy',
                             name='pg_policy_rule_action')


def upgrade():
    op.create_table(
        'pg_policy_tags',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('tag_id', sa.String(length=1024), nullable=True),
        sa.Column('tag_type', tag_enum, nullable=True),
        sa.Column('floatingip_address', sa.String(length=255), nullable=True),
        sa.Column('floatingip_id', sa.String(length=36), nullable=True),
        sa.Column('router_id', sa.String(length=36), nullable=True),
        sa.Column('tenant_id', sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(['floatingip_id'], ['floatingips.id'],
                                ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'pg_endpoint_groups',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('description', sa.String(length=1024), nullable=True),
        sa.Column('policy_tag_id', sa.String(length=36), nullable=True),
        sa.Column('tenant_id', sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(['policy_tag_id'], ['pg_policy_tags.id'],
                                ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'pg_security_policy_tag_binding',
        sa.Column('security_group_id', sa.String(length=36), nullable=False),
        sa.Column('policy_tag_id', sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(['security_group_id'], ['securitygroups.id'],
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['policy_tag_id'],
                                ['pg_policy_tags.id'])
    )

    op.create_table(
        'pg_endpoints',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('ip_mask', sa.String(length=36), nullable=True),
        sa.Column('port_id', sa.String(length=36), nullable=True),
        sa.Column('ip_port', sa.String(length=255), nullable=True),
        sa.Column('label', sa.String(length=255), nullable=True),
        sa.Column('tenant_id', sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(['port_id'], ['ports.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'pg_endpoint_group_member_binding',
        sa.Column('endpoint_id', sa.String(length=36), nullable=False),
        sa.Column('endpoint_group_id', sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(['endpoint_id'], ['pg_endpoints.id'],
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['endpoint_group_id'],
                                ['pg_endpoint_groups.id'], ondelete='CASCADE')
    )

    op.create_table(
        'pg_security_group_endpoint_binding',
        sa.Column('security_group_id', sa.String(length=36), nullable=False),
        sa.Column('endpoint_id', sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(['security_group_id'], ['securitygroups.id'],
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['endpoint_id'],
                                ['pg_endpoints.id'])
    )

    op.create_table(
        'pg_policy_services',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('description', sa.String(length=1024), nullable=True),
        sa.Column('tenant_id', sa.String(length=36), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'pg_policy_service_port_binding',
        sa.Column('policy_service_id', sa.String(length=36), nullable=False),
        sa.Column('port_id', sa.String(length=36), nullable=False),
        sa.Column('direction', direction_enum, nullable=False),
        sa.ForeignKeyConstraint(['policy_service_id'],
                                ['pg_policy_services.id'],
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['port_id'],
                                ['ports.id'], ondelete='CASCADE')
    )

    op.create_table(
        'pg_policy_rules',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('src_grp_epg', sa.String(length=36), nullable=True),
        sa.Column('src_grp_sg', sa.String(length=36), nullable=True),
        sa.Column('dst_grp_epg', sa.String(length=36), nullable=True),
        sa.Column('dst_grp_sg', sa.String(length=36), nullable=True),
        sa.Column('protocol', policy_rule_protocol_enum, nullable=False),
        sa.Column('src_port_range', sa.String(length=255), nullable=True),
        sa.Column('dst_port_range', sa.String(length=255), nullable=True),
        sa.Column('action', policy_action_enum, nullable=False),
        sa.Column('action_target_service', sa.String(length=36),
                  nullable=True),
        sa.Column('action_target_tenant_id', sa.String(length=36),
                  nullable=True),
        sa.Column('tag', sa.String(length=36), nullable=True),
        sa.Column('tenant_id', sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(['src_grp_epg'], ['pg_endpoint_groups.id'],
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['src_grp_sg'], ['securitygroups.id'],
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['dst_grp_epg'], ['pg_endpoint_groups.id'],
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['dst_grp_sg'], ['securitygroups.id'],
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['action_target_service'],
                                ['pg_policy_services.id'],
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag'], ['pg_policy_tags.id'],
                                ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
