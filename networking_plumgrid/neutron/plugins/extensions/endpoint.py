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
import networking_plumgrid
from networking_plumgrid._i18n import _
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


class UpdateParametersRequired(nexceptions.InvalidInput):
    message = _("No update parameter specified atleast one needed")


class InvalidPortFormat(nexceptions.InvalidInput):
    message = _("Invalid format for port list: ")

    def __init__(self, error):
        super(InvalidPortFormat, self).__init__()
        self.msg = self.message + error


class EndpointInUse(nexceptions.InUse):
    message = _("Endpoint %(id)s %(reason)s with endpoint group(s): %(epg)s")

    def __init__(self, **kwargs):
        if 'reason' not in kwargs:
            kwargs['reason'] = _("is in use")
        super(EndpointInUse, self).__init__(**kwargs)


def _validate_port_list(data, valid_values=None):
    if not isinstance(data, list):
        raise InvalidPortFormat("Must be a List of Ports")

    for port in data:
        if 'id' not in port:
            raise InvalidPortFormat("id field is required")


def _validate_ip_port_list(data, valid_values=None):
    if not isinstance(data, list):
        raise InvalidPortFormat("Must be a List of Ports")

    for port in data:
        if 'ip' not in port:
            msg = _("ip field is required")
            return msg
        ip_addr = port.get('ip')
        if ip_addr and not netaddr.valid_ipv4(ip_addr):
            msg = _("Invalid format for IP address specified.")
            return msg


attr.validators['type:validate_port_list'] = _validate_port_list
attr.validators['type:validate_ip_port_list'] = _validate_ip_port_list


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
        'endpoint_group': {
            'allow_post': True,
            'allow_put': True,
            'is_visible': True,
            'default': ''
        },
        'label': {
            'allow_post': True,
            'allow_put': True,
            'is_visible': True,
            'default': ''
        },
        'port_id': {
            'allow_post': True,
            'allow_put': True,
            'is_visible': True,
            'default': ''
        },
        'ip_mask': {
            'allow_post': True,
            'allow_put': True,
            'is_visible': True,
            'default': ''
        },
        'ep_groups': {
            'allow_post': True,
            'allow_put': True,
            'is_visible': True,
            'default': []
        },
        'ip_port_mask': {
            'allow_post': True,
            'allow_put': True,
            'is_visible': True,
            'default': ''
        },
        'ip_address': {
            'allow_post': True,
            'allow_put': True,
            'is_visible': True,
            'default': ''
        },
        'port_mask': {
            'allow_post': True,
            'allow_put': True,
            'is_visible': True,
            'default': ''
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
