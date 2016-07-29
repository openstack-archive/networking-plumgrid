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

import netaddr
import re
import socket
import networking_plumgrid
from networking_plumgrid._i18n import _
from neutron_lib.api import validators
from neutron.api import extensions
from neutron.api.v2 import attributes as attr
from neutron.api.v2 import base
from neutron.common import exceptions as nexceptions
from neutron import manager

PG_EP = 'endpoint'
PG_EPS = 'endpoints'

extensions.append_api_extensions_path(
    networking_plumgrid.neutron.plugins.extensions.__path__)


class PortInUse(nexceptions.InvalidInput):
    message = _("Port %(port)s is already in use by endpoint"
                " with id %(id)s")


class IPPortInUse(nexceptions.InvalidInput):
    message = _("IP-PortRange %(ip)s:%(port)s is already in use by endpoint"
                " with id %(id)s")


class NoEndpointFound(nexceptions.NotFound):
    message = _("Endpoint with id %(id)s does not exist")

class NoEndpointGroupFound(nexceptions.NotFound):
    message = _("Endpoint Group with id %(id)s does not exist")

class UpdateParametersRequired(nexceptions.InvalidInput):
    message = _("No update parameter specified atleast one needed")


class InvalidEndpointGroupFormat(nexceptions.InvalidInput):
    message = _("Invalid format for endpoint group list: ")

    def __init__(self, error):
        super(InvalidEndpointGroupFormat, self).__init__()
        self.msg = self.message + error

class InvalidIPMaskFormat(nexceptions.InvalidInput):
    message = _("Invalid format for ip_mask. Please specify "
                "correct CIDR: Format ('X.X.X.X/Y')")

class InvalidIPPortFormat(nexceptions.InvalidInput):
    message = _("Invalid entry for ip_port. Please specify "
                "correct ip_port. ")
    def __init__(self, error):
        super(InvalidIPPortFormat, self).__init__()
        self.msg = self.message + error


class EndpointInUse(nexceptions.InUse):
    message = _("Endpoint %(id)s %(reason)s with endpoint group(s): %(epg)s")

    def __init__(self, **kwargs):
        if 'reason' not in kwargs:
            kwargs['reason'] = _("is in use")
        super(EndpointInUse, self).__init__(**kwargs)


def _validate_ip_mask(data, valid_values=None):
    if data is not None:
        valid_ip_mask = re.findall("(?:\d{1,3}\.){3}\d{1,3}(?:/\d\d?)?", data)
        if valid_ip_mask:
            try:
                netaddr.IPNetwork(data)
            except netaddr.core.AddrFormatError:
                raise InvalidIPMaskFormat()
        else:
            raise InvalidIPMaskFormat()

def _validate_ip_port(data, valid_values=None):
    if data is not None:
        valid_ip_port = data.split('_')
        if len(valid_ip_port) != 3:
            raise InvalidIPPortFormat("")
        else:
            try:
                socket.inet_pton(socket.AF_INET, valid_ip_port[0])
                if (int(valid_ip_port[1]) >=0 and int(valid_ip_port[1]) <=65535):
                    if not(int(valid_ip_port[2]) >= 0 and int(valid_ip_port[2]) <=16):
                        raise InvalidIPPortFormat("Error: Invalid mask. Please use "
                                "mask in range (0-16)")
                else:
                    raise InvalidIPPortFormat("Error: Invalid port. Please "
                                "use port in range (1-65535)")
            except (socket.error, ValueError):
                raise InvalidIPPortFormat("")

def _validate_epg_list(data, valid_values=None):
    if not isinstance(data, list):
        raise InvalidEndpointGroupFormat("Must be a list of endpoint groups")

    for epg in data:
        if 'id' not in epg:
            raise InvalidEndpointGroupFormat("id field is required")


validators.validators['type:validate_ip_mask'] = _validate_ip_mask
validators.validators['type:validate_ip_port'] = _validate_ip_port
validators.validators['type:validate_epg_list'] = _validate_epg_list


RESOURCE_ATTRIBUTE_MAP = {
    'endpoint': {
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
        'port_id': {
            'allow_post': True,
            'allow_put': False,
            'is_visible': True,
            'default': None
        },
        'ip_mask': {
            'allow_post': True,
            'allow_put': False,
            'is_visible': True,
            'default': None,
            'validate': {
                'type:validate_ip_mask': None
            }
        },
        'ep_groups': {
            'allow_post': True,
            'allow_put': True,
            'is_visible': True,
            'default': []
        },
        'ip_port': {
            'allow_post': True,
            'allow_put': False,
            'is_visible': True,
            'default': None,
            'validate': {
                'type:validate_ip_port': None
            }
        },
        'add_endpoint_groups': {
            'allow_post': False,
            'allow_put': True,
            'is_visible': True,
            'default': None,
            'validate': {
                'type:validate_epg_list': None
            }
        },
        'remove_endpoint_groups': {
            'allow_post': False,
            'allow_put': True,
            'is_visible': True,
            'default': None,
            'validate': {
                'type:validate_epg_list': None
            }
        },
        'tenant_id': {'allow_post': True,
                      'allow_put': False,
                      'required_by_policy': True,
                      'validate': {'type:string': attr.TENANT_ID_MAX_LEN},
                      'is_visible': True},
    }
}


class Endpoint(extensions.ExtensionDescriptor):

    @classmethod
    def get_name(cls):
        return "Endpoint"

    @classmethod
    def get_alias(cls):
        return "endpoint"

    @classmethod
    def get_description(cls):
        return "This API will be used to create endpoints" \
               " for endpoint groups from Neutron and map it " \
               "in PLUMgrid."

    @classmethod
    def get_namespace(cls):
        return "http://docs.openstack.org/ext/endpoint" \
               "/api/v2.0"

    @classmethod
    def get_updated(cls):
        return "2016-01-01T00:00:00-00:00"

    @classmethod
    def get_resources(cls):
        exts = []
        plugin = manager.NeutronManager.get_plugin()

        resource_name = PG_EP
        collection_name = PG_EPS
        params = RESOURCE_ATTRIBUTE_MAP.get(resource_name, dict())
        controller = base.create_resource(
            collection_name, resource_name, plugin, params)
        ex = extensions.ResourceExtension(collection_name,
                                          controller)
        exts.append(ex)
        return exts
