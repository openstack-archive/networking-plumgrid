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

import networking_plumgrid
from neutron.api import extensions
from neutron.api.v2 import attributes as attr
from neutron.api.v2 import base
from neutron.common import exceptions as nexceptions
from neutron import manager


PG_PAP = 'physical_attachment_point'
PG_PAPS = 'physical-attachment-points'

extensions.append_api_extensions_path(
    networking_plumgrid.neutron.plugins.extensions.__path__)


class InvalidInterfaceFormat(nexceptions.InvalidInput):
    message = _("Invalid format for interfaces: ")

    def __init__(self, error):
        super(InvalidInterfaceFormat, self).__init__()
        self.msg = self.message + error


class UpdateParametersRequired(nexceptions.InvalidInput):
    message = _("No update parameter specified atleast one needed")


class InvalidLacpValue(nexceptions.InvalidInput):
    message = _("LACP value must be set to True for hash_mode %(hash_mode)s")


class NoPhysicalAttachmentPointFound(nexceptions.NotFound):
    message = _("Physical Attachment Point with id %(id)s does not exist")


class TransitDomainLimit(nexceptions.InvalidInput):
    message = _("Only one physical attachment point"
                " allowed per transit domain.")


class InterfaceInUse(nexceptions.InvalidInput):
    message = _("Interface %(ifc)s is already in use by physical"
                " attachment point with id %(id)s")


def _validate_interfaces_list(data, valid_values=None):
    if not isinstance(data, list):
        raise InvalidInterfaceFormat("Must be a List of Interfaces")

    for interface in data:
        if 'hostname' not in interface:
            raise InvalidInterfaceFormat("hostname field is required")

        if 'interface' not in interface:
            raise InvalidInterfaceFormat("interface_name field is required")


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
            'allow_put': False,
            'is_visible': True,
            'default': [],
            'validate': {
                'type:validate_interfaces_list': None
            }
        },
        'add_interfaces': {
            'allow_post': False,
            'allow_put': True,
            'is_visible': True,
            'default': [],
            'validate': {
                'type:validate_interfaces_list': None
            }
        },
        'remove_interfaces': {
            'allow_post': False,
            'allow_put': True,
            'is_visible': True,
            'default': [],
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
                'type:values': ['L2', 'L2+L3', 'L3', 'L3+L4']
            }
        },
        'lacp': {
            'allow_post': True,
            'allow_put': True,
            'is_visible': True,
            'default': False,
            'validate': {
                 'type:boolean': None
            }
        },
        'implicit': {
            'allow_post': False,
            'allow_put': False,
            'is_visible': False,
            'default': False,
            'validate': {
                 'type:boolean': None
            }
        },
        'transit_domain_id': {
            'allow_post': True,
            'allow_put': False,
            'is_visible': True,
            'default': None,
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
        return "Physical Attachment Point"

    @classmethod
    def get_alias(cls):
        return "physical-attachment-point"

    @classmethod
    def get_description(cls):
        return "This API will be used to configure physical attachment" \
               "points from Neutron and map it to Neutron external and" \
               "provider networks"

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
