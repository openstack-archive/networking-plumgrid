#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


"""
PGLock object
"""

#from oslo_versionedobjects import fields

from networking_plumgrid.neutron.plugins.db import api as db_api


class PGLock(object):
    #fields = {
    #    'uuid': fields.StringField(),
    #    'created_at': fields.DateTimeField(read_only=True),
    #}

    @classmethod
    def create(cls, uuid):
        return db_api.pg_lock_create(uuid)

    @classmethod
    def get(cls, uuid):
        return db_api.pg_lock_get(uuid)

    @classmethod
    def steal(cls, uuid):
        return db_api.pg_lock_steal(uuid)

    @classmethod
    def release(cls, uuid):
        return db_api.pg_lock_release(uuid)

    @classmethod
    def get_lock_id(cls, uuid):
        return db_api.pg_lock_get_lock_id(uuid)
