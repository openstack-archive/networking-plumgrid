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

'''
Interface for database access.

Usage:

The underlying driver is loaded . SQLAlchemy is currently the only
supported backend.
'''

from oslo_config import cfg
from oslo_db import api

CONF = cfg.CONF


_BACKEND_MAPPING = {'sqlalchemy':
                    'networking_plumgrid.neutron.plugins.db.sqlal.api'}

IMPL = api.DBAPI.from_config(CONF, backend_mapping=_BACKEND_MAPPING)


def get_engine():
    return IMPL.get_engine()


def get_session():
    return IMPL.get_session()


def pg_lock_create(uuid):
    return IMPL.pg_lock_create(uuid)


def pg_lock_get(uuid):
    return IMPL.pg_lock_get(uuid)


def pg_lock_get_id(uuid):
    return IMPL.pg_lock_get_id(uuid)


def pg_lock_steal(uuid):
    return IMPL.pg_lock_steal(uuid)


def pg_lock_release(uuid):
    return IMPL.pg_lock_release(uuid)
