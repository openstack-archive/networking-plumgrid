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

from neutron.api import extensions
from neutron.api.v2 import attributes as attr
from neutron.api.v2 import base
from neutron.common import exceptions as nexceptions
from neutron import manager


PG_PAP = 'physical_attachment_point'
PG_PAPS = '%ss' % PG_PAP


class InvalidInterfaceFormat(nexceptions.InvalidInput):
    message = _("Invalid format for interfaces: ")

    def __init__(self, error):
        super(InvalidInterfaceFormat, self).__init__()
        self.msg = self.message + error


def _validate_interfaces_list(data, valid_values=None):
    if not isinstance(data, list):
        raise InvalidInterfaceFormat("Must be a List of Interfaces")

    for interface in data:
        if 'hostname' not in interface:
            raise InvalidInterfaceFormat("hostname field is required")

        if 'interface' not in interface:
            raise InvalidInterfaceFormat("interface field is required")


attr.validators['type:validate_interfaces_list'] = _validate_interfaces_list


RESOURCE_ATTRIBUTE_MAP = {
    'physical_attachment_point': {
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
        'interfaces': {
            'allow_post': True,
            'allow_put': True,
            'is_visible': True,
            'validate': {
                'type:validate_interfaces_list': None
            }
        },
        'hash_mode': {
            'allow_post': True,
            'allow_put': True,
            'is_visible': True,
            'default': 'L2',
            'validate': {
                'type:values': ['L2', 'L3', 'L4'
                                'L2+L3', 'L3+L4']
            }
        },
        'lacp': {
            'allow_post': True,
            'allow_put': True,
            'is_visible': True,
            'default': True,
            'validate': {
                 'type:boolean': None
            }
        },
        'tenant_id': {
            'allow_post': True,
            'allow_put': False,
            'is_visible': True
        },
    }
}


class Physical_attachment_point(extensions.ExtensionDescriptor):

    @classmethod
    def get_name(cls):
        return "L2 Software Gateway with Port Bundle"

    @classmethod
    def get_alias(cls):
        return "physical-attachment-point"

    @classmethod
    def get_description(cls):
        return """"
               This API will be used to configure physical attachment
               points from Neutron and map it to Neutron external and
               provider networks
               """

    @classmethod
    def get_namespace(cls):
        return "http://docs.openstack.org/ext/physical_attachment_points" \
               "/api/v2.0"

    @classmethod
    def get_updated(cls):
        return "2012-10-05T10:00:00-00:00"

    @classmethod
    def get_resources(cls):
        exts = []
        plugin = manager.NeutronManager.get_plugin()

        resource_name = PG_PAP
        collection_name = PG_PAPS
        params = RESOURCE_ATTRIBUTE_MAP.get(resource_name, dict())
        controller = base.create_resource(
            collection_name, resource_name, plugin, params)
        ex = extensions.ResourceExtension(collection_name,
                                          controller)
        exts.append(ex)
        return exts
