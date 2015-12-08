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
from neutron.api.v2 import base
from neutron import manager

from networking_plumgrid.neutron.plugins.common import constants

RESOURCE_ATTRIBUTE_MAP = {
    constants.L2_GATEWAYS_CONNECTION: {
        'id': {'allow_post': False, 'allow_put': False,
               'is_visible': True},
        'l2_gateway_id': {'allow_post': True, 'allow_put': False,
                          'validate': {'type:string': None},
                          'is_visible': True, 'default': ''},
        'network_id': {'allow_post': True, 'allow_put': False,
                       'validate': {'type:string': None},
                       'is_visible': True},
        'segmentation_id': {'allow_post': True, 'allow_put': False,
                            'validate': {'type:string': None},
                            'is_visible': True, 'default': ''},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True}
    },
}


class L2gatewayconnection(extensions.ExtensionDescriptor):

    """API extension for Layer-2 Gateway  connection support."""

    @classmethod
    def get_name(cls):
        return "L2 Gateway connection"

    @classmethod
    def get_alias(cls):
        return "l2-gateway-connection"

    @classmethod
    def get_description(cls):
        return "Connects Neutron networks with external networks at layer 2."

    @classmethod
    def get_updated(cls):
        return "2014-01-01T00:00:00-00:00"

    @classmethod
    def get_resources(cls):
        # This method registers the URL and the dictionary  of
        # attributes on the neutron-server.
        exts = []
        plugin = manager.NeutronManager.get_plugin()
        resource_name = constants.CONNECTION_RESOURCE_NAME
        collection_name = resource_name.replace('_', '-') + "s"
        params = RESOURCE_ATTRIBUTE_MAP.get(constants.L2_GATEWAYS_CONNECTION,
                                            dict())
        controller = base.create_resource(
            collection_name, resource_name, plugin, params)
        ex = extensions.ResourceExtension(collection_name,
                                          controller)
        exts.append(ex)
        return exts
