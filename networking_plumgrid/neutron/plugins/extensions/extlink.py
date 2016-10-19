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

import networking_plumgrid
from neutron.api import extensions
from neutron.api.v2 import attributes as attr
from neutron.api.v2 import base
from neutron import manager

PG_LINK = 'ext_link'
PG_LINKS = 'ext-links'

extensions.append_api_extensions_path(
    networking_plumgrid.neutron.plugins.extensions.__path__)


RESOURCE_ATTRIBUTE_MAP = {
    'ext_link': {
        'id': {
            'allow_post': False,
            'allow_put': False,
            'is_visible': True,
            'default': ''
        },
        'name': {
            'allow_post': False,
            'allow_put': False,
            'is_visible': True,
            'default': ''
        },
        'local_tenant': {
            'allow_post': False,
            'allow_put': False,
            'is_visible': True,
            'default': ''
        },
        'remote_tenant': {
            'allow_post': False,
            'allow_put': False,
            'is_visible': True,
            'default': '',
        },
        'local_ne_type': {
            'allow_post': False,
            'allow_put': False,
            'is_visible': True,
            'default': '',
        },
        'local_ne_id': {
            'allow_post': False,
            'allow_put': False,
            'is_visible': True,
            'default': '',
        },
        'remote_ne_type': {
            'allow_post': False,
            'allow_put': False,
            'is_visible': True,
            'default': '',
        },
        'remote_ne_id': {
            'allow_post': False,
            'allow_put': False,
            'is_visible': True,
            'default': '',
        },
        'tenant_id': {'allow_post': False,
                      'allow_put': False,
                      'required_by_policy': True,
                      'validate': {'type:string': attr.TENANT_ID_MAX_LEN},
                      'is_visible': True},
    }
}


class Extlink(extensions.ExtensionDescriptor):

    @classmethod
    def get_name(cls):
        return "External Links"

    @classmethod
    def get_alias(cls):
        return "ext-link"

    @classmethod
    def get_description(cls):
        return "This API will be used to get link/conenctors" \
               " from PLUMgrid."

    @classmethod
    def get_namespace(cls):
        return "http://docs.openstack.org/ext/ext_link" \
               "/api/v2.0"

    @classmethod
    def get_updated(cls):
        return "2016-01-01T00:00:00-00:00"

    @classmethod
    def get_resources(cls):
        exts = []
        plugin = manager.NeutronManager.get_plugin()

        resource_name = PG_LINK
        collection_name = PG_LINKS
        params = RESOURCE_ATTRIBUTE_MAP.get(resource_name, dict())
        controller = base.create_resource(
            collection_name, resource_name, plugin, params)
        ex = extensions.ResourceExtension(collection_name,
                                          controller)
        exts.append(ex)
        return exts
