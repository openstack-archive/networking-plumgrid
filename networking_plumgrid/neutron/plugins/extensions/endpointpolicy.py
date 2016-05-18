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
from random import randint

PG_EPG = 'endpoint_policy'
PG_EPGS = 'endpoint-policies'

extensions.append_api_extensions_path(
    networking_plumgrid.neutron.plugins.extensions.__path__)


class EndpointPolicyInvalidPortRange(nexceptions.InvalidInput):
    message = _("Invalid port range specified '%(port)s'. Following format "
                "is supported e.g. '%(min)s-%(max)s'")


class NoEndpointPolicyFound(nexceptions.NotFound):
    message = _("Endpoint Policy with id '%(id)s' does not exist.")


class NoEndpointGroupFound(nexceptions.NotFound):
    message = _("Endpoint Group with id '(%(id)s)' specified as "
                "%(policy_config)s does not exist.")


class InvalidEndpointGroupForPolicy(nexceptions.InvalidInput):
    message = _("Endpoint Group with id '%(id)s' and type '%(type)s' "
                "cannot be specified as '%(policy_config)s' for policy.")


class InvalidEndpointPolicyConfig(nexceptions.InvalidInput):
    message = _("Endpoint Policy only supports source_epg, "
                "destination_epg and service_epg.")


class InvalidConfigForServiceEndpointGroup(nexceptions.InvalidInput):
    message = _("Service Endpoint is required for endpoint policy.")


def _validate_port_range(self, port_range):
    if port_range is None:
        return port_range
    try:
        lower_bound, upper_bound = port_range.split('-')
        lower_bound_val = int(lower_bound)
        upper_bound_val = int(upper_bound)
    except (ValueError, TypeError):
        port_range_min = randint(1, 65535)
        port_range_max = randint(port_range_min, 65535)
        raise EndpointPolicyInvalidPortRange(port=port_range,
                                             min=str(port_range_min),
                                             max=str(port_range_max))

    if ((lower_bound_val >= 0 and lower_bound_val <= 65535 and
        upper_bound_val >= 0 and upper_bound_val <= 65535) and
        lower_bound_val <= upper_bound_val):
        return port_range
    else:
        port_range_min = randint(1, 65535)
        port_range_max = randint(port_range_min, 65535)
        raise EndpointPolicyInvalidPortRange(port=port_range,
                                             min=str(port_range_min),
                                             max=str(port_range_max))

attr.validators['type:validate_port_range'] = _validate_port_range
ep_supported_protocols = ['any', 'tcp', 'udp', 'icmp']
ep_supported_actions = ['copy']

RESOURCE_ATTRIBUTE_MAP = {
    'endpoint_policy': {
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
            'allow_put': False,
            'is_visible': True,
            'default': ''
        },
        'src_grp': {
            'allow_post': True,
            'allow_put': False,
            'is_visible': True,
            'default': None
        },
        'dst_grp': {
            'allow_post': True,
            'allow_put': False,
            'is_visible': True,
            'default': None
        },
        'protocol': {
            'allow_post': True,
            'allow_put': False,
            'is_visible': True,
            'default': 'any',
            'validate': {
                'type:values': ep_supported_protocols
            }
        },
        'src_port_range': {
            'allow_post': True,
            'allow_put': False,
            'is_visible': True,
            'default': None,
            'validate': {
                'type:validate_port_range': None
            }
        },
        'dst_port_range': {
            'allow_post': True,
            'allow_put': False,
            'is_visible': True,
            'default': None,
            'validate': {
                'type:validate_port_range': None
            }
        },
        'action': {
            'allow_post': True,
            'allow_put': False,
            'is_visible': True,
            'default': 'copy',
            'validate': {'type:values': ep_supported_actions}
        },
        'service_endpoint_group': {
            'allow_post': True,
            'allow_put': False,
            'is_visible': True,
            'required_by_policy': True
        },
        'tenant_id': {
            'allow_post': True,
            'allow_put': False,
            'required_by_policy': True,
            'validate': {'type:string': attr.TENANT_ID_MAX_LEN},
            'is_visible': True
        }
    }
}


class Endpointpolicy(extensions.ExtensionDescriptor):

    @classmethod
    def get_name(cls):
        return "Endpoint Policy"

    @classmethod
    def get_alias(cls):
        return "endpoint-policy"

    @classmethod
    def get_description(cls):
        return "This API will be used to configure endpoint policies inside" \
               " endpoint groups from Neutron and map it to policy based" \
               " TAP/SFC in PLUMgrid"

    @classmethod
    def get_namespace(cls):
        return "http://docs.openstack.org/ext/endpoint_policy" \
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
