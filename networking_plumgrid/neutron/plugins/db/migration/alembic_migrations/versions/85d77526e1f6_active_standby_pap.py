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

"""active_standby_pap

Revision ID: 85d77526e1f6
Revises: 351c4f5710e7
Create Date: 2016-08-14 11:07:32.564472

"""

# revision identifiers, used by Alembic.
revision = '85d77526e1f6'
down_revision = '351c4f5710e7'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        'pg_physical_attachment_points',
        sa.Column('active_standby', sa.Boolean(), nullable=False),
    )
