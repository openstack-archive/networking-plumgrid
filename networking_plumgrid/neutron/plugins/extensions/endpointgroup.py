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
from networking_plumgrid._i18n import _
from neutron.api import extensions
from neutron.api.v2 import attributes as attr
from neutron.api.v2 import base
from neutron.common import exceptions as nexceptions
from neutron import manager

PG_EPG = 'endpoint_group'
PG_EPGS = 'endpoint-groups'

extensions.append_api_extensions_path(
    networking_plumgrid.neutron.plugins.extensions.__path__)


class NoEndpointGroupFound(nexceptions.NotFound):
    message = _("Endpoint Group with id %(id)s does not exist")


class UpdateParametersRequired(nexceptions.InvalidInput):
    message = _("No update parameter specified atleast one needed")


class SGUpdateDisallowed(nexceptions.InvalidInput):
    message = _("Update for Security Group parameters is not allowed.")

RESOURCE_ATTRIBUTE_MAP = {
    'endpoint_group': {
        'id': {
            'allow_post': False,
            'allow_put': False,
            'validate': {
                'type:uuid': None
            },
            'is_visible': True,
            'primary_key': True
        },
        'name': {
            'allow_post': True,
            'allow_put': True,
            'is_visible': True,
            'default': ''
        },
        'description': {
            'allow_post': True,
            'allow_put': True,
            'is_visible': True,
            'default': ''
        },
        'policy_tag_id': {
            'allow_post': True,
            'allow_put': True,
            'is_visible': True,
            'default': None,
        },
        'is_security_group': {
            'allow_post': False,
            'allow_put': False,
            'is_visible': True,
            'default': False,
            'validate': {'type:boolean': None}

        },
        'add_tag': {
            'allow_post': True,
            'allow_put': True,
            'is_visible': True,
            'default': None,
        },
        'remove_tag': {
            'allow_post': True,
            'allow_put': True,
            'is_visible': True,
            'default': None,
        },
        'tenant_id': {'allow_post': True,
                      'allow_put': False,
                      'required_by_policy': True,
                      'validate': {'type:string': attr.TENANT_ID_MAX_LEN},
                      'is_visible': True},
    }
}


class Endpointgroup(extensions.ExtensionDescriptor):

    @classmethod
    def get_name(cls):
        return "Endpoint Group"

    @classmethod
    def get_alias(cls):
        return "endpoint-group"

    @classmethod
    def get_description(cls):
        return "This API will be used to create endpoint groups" \
               " from Neutron and map it in PLUMgrid."

    @classmethod
    def get_namespace(cls):
        return "http://docs.openstack.org/ext/endpoint_group" \
               "/api/v2.0"

    @classmethod
    def get_updated(cls):
        return "2016-01-01T00:00:00-00:00"

    @classmethod
    def get_resources(cls):
        exts = []
        plugin = manager.NeutronManager.get_plugin()

        resource_name = PG_EPG
        collection_name = PG_EPGS
        params = RESOURCE_ATTRIBUTE_MAP.get(resource_name, dict())
        controller = base.create_resource(
            collection_name, resource_name, plugin, params)
        ex = extensions.ResourceExtension(collection_name,
                                          controller)
        exts.append(ex)
        return exts
