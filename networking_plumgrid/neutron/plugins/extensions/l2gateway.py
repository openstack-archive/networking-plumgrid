# Copyright 2015 PLUMgrid, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from neutron.api import extensions
from neutron.api.v2 import attributes
from neutron.api.v2 import base
from neutron import manager

from networking_plumgrid.neutron.plugins.common import constants
from networking_plumgrid.neutron.plugins.common import l2gw_validators


RESOURCE_ATTRIBUTE_MAP = {
    constants.L2_GATEWAYS: {
        'id': {'allow_post': False, 'allow_put': False,
               'is_visible': True},
        'vtep_ifc': {'allow_post': True, 'allow_put': True,
                     'validate': {'type:string': None},
                     'is_visible': True, 'default': ''},
        'vtep_ip': {'allow_post': True, 'allow_put': True,
                    'validate': {'type:string': None},
                    'is_visible': True, 'default': ''},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'is_visible': True, 'default': ''},
        'devices': {'allow_post': True, 'allow_put': True,
                    'validate': {'type:l2gwdevice_list': None},
                    'is_visible': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True}
    },
}

validator_func = l2gw_validators.validate_gwdevice_list
attributes.validators['type:l2gwdevice_list'] = validator_func


class L2gateway(extensions.ExtensionDescriptor):

    """API extension for Layer-2 Gateway support."""

    @classmethod
    def get_name(cls):
        return "L2 Gateway"

    @classmethod
    def get_alias(cls):
        return "l2-gateway"

    @classmethod
    def get_description(cls):
        return "Connects Neutron networks with external networks at layer 2."

    @classmethod
    def get_updated(cls):
        return "2015-01-01T00:00:00-00:00"

    @classmethod
    def get_resources(cls):
        # This method registers the URL and the dictionary  of
        # attributes on the neutron-server.

        exts = []
        plugin = manager.NeutronManager.get_plugin()
        resource_name = constants.GATEWAY_RESOURCE_NAME
        collection_name = resource_name.replace('_', '-') + "s"
        params = RESOURCE_ATTRIBUTE_MAP.get(constants.L2_GATEWAYS,
                                            dict())
        controller = base.create_resource(
            collection_name, resource_name, plugin, params)
        ex = extensions.ResourceExtension(collection_name,
                                          controller)
        exts.append(ex)
        return exts
