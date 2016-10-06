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

"""add label sec grp to endpoint

Revision ID: 1b5eb4d4f7d3
Revises: 1ae50f04cdd5, 85d77526e1f6
Create Date: 2016-10-27 01:59:31.893201

"""

# revision identifiers, used by Alembic.
revision = '1b5eb4d4f7d3'
down_revision = ('1ae50f04cdd5', '85d77526e1f6')

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        'pg_endpoints',
        sa.Column('label', sa.String(length=255), nullable=True)
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
