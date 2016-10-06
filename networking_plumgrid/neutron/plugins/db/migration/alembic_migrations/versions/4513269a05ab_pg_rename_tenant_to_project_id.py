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

"""pg rename tenant to project id

Revision ID: 4513269a05ab
Revises: 1b5eb4d4f7d3
Create Date: 2016-09-08 01:38:55.828075

"""

# revision identifiers, used by Alembic.
revision = '4513269a05ab'
down_revision = '1b5eb4d4f7d3'

from alembic import op
import sqlalchemy as sa


_INSPECTOR = None


def get_inspector():
    """Reuse inspector"""

    global _INSPECTOR

    if _INSPECTOR:
        return _INSPECTOR

    else:
        bind = op.get_bind()
        _INSPECTOR = sa.engine.reflection.Inspector.from_engine(bind)

    return _INSPECTOR


def get_tables():
    """
    Returns hardcoded list of tables which have ``tenant_id`` column.

    DB head can be changed. To prevent possible problems, when models will be
    updated, return hardcoded list of tables, up-to-date for this day.

    Output retrieved by using:

    >>> metadata = head.get_metadata()
    >>> all_tables = metadata.sorted_tables
    >>> tenant_tables = []
    >>> for table in all_tables:
    ...     for column in table.columns:
    ...         if column.name == 'tenant_id':
    ...             tenant_tables.append((table, column))

    """

    tables = [
        'pg_endpoint_group_member_binding',
        'pg_endpoint_groups',
        'pg_endpoints',
        'pg_physical_attachment_point_interfaces',
        'pg_physical_attachment_points',
        'pg_policy_rules',
        'pg_policy_service_port_binding',
        'pg_policy_services',
        'pg_policy_tags',
        'pg_provider_net_bindings',
        'pg_security_policy_tag_binding',
        'pg_transit_domains',
        'pgl2gatewayconnections',
        'pgl2gatewaydevices',
        'pgl2gatewayinterfaces',
        'pgl2gateways',
    ]

    return tables


def get_columns(table):
    """Returns list of columns for given table."""
    inspector = get_inspector()
    return inspector.get_columns(table)


def get_data():
    """Returns combined list of tuples: [(table, column)].

    List is built, based on retrieved tables, where column with name
    ``tenant_id`` exists.
    """

    output = []
    tables = get_tables()
    for table in tables:
        columns = get_columns(table)

        for column in columns:
            if column['name'] == 'tenant_id':
                output.append((table, column))

    return output


def alter_column(table, column):
    old_name = 'tenant_id'
    new_name = 'project_id'

    op.alter_column(
        table_name=table,
        column_name=old_name,
        new_column_name=new_name,
        existing_type=column['type'],
        existing_nullable=column['nullable']
    )


def recreate_index(index, table_name):
    old_name = index['name']
    new_name = old_name.replace('tenant', 'project')

    op.drop_index(op.f(old_name), table_name)
    op.create_index(new_name, table_name, ['project_id'])


def upgrade():
    inspector = get_inspector()

    data = get_data()
    for table, column in data:
        alter_column(table, column)

        indexes = inspector.get_indexes(table)
        for index in indexes:
            if 'tenant_id' in index['name']:
                recreate_index(index, table)


def contract_creation_exceptions():
    """Special migration for the blueprint to support Keystone V3.
    We drop all tenant_id columns and create project_id columns instead.
    """
    return {
        sa.Column: ['.'.join([table, 'project_id']) for table in get_tables()],
        sa.Index: get_tables()
    }
