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
from neutron import manager
from neutron_lib.api import validators
from neutron_lib import exceptions as nexceptions
from random import randint

PG_POLICY_RULE = 'policy_rule'
PG_POLICY_RULES = 'policy-rules'

extensions.append_api_extensions_path(
    networking_plumgrid.neutron.plugins.extensions.__path__)


class PolicyRuleInvalidPortRange(nexceptions.InvalidInput):
    message = _("Invalid port range specified '%(port)s'. Following format "
                "is supported e.g. '%(min)s-%(max)s'")


class NoPolicyRuleFound(nexceptions.NotFound):
    message = _("Policy Rule with id '%(id)s' does not exist.")


class NoPolicyGroupFound(nexceptions.NotFound):
    message = _("Policy Group with id '(%(id)s)' specified as "
                "%(policy_config)s does not exist.")


class InvalidPolicyGroupForPolicy(nexceptions.InvalidInput):
    message = _("Policy Group with id '%(id)s' and type '%(type)s' "
                "cannot be specified as '%(policy_config)s' for policy.")


class InvalidPolicyRuleConfig(nexceptions.InvalidInput):
    message = _("Policy Rule only supports source_epg, "
                "destination_epg and service_epg.")


def _validate_port_range(data, valid_values=None):
    if not data:
        return
    try:
        lower_bound, upper_bound = data.split('-')
        lower_bound_val = int(lower_bound)
        upper_bound_val = int(upper_bound)
    except (ValueError, TypeError):
        port_range_min = randint(1, 65535)
        port_range_max = randint(port_range_min, 65535)
        raise PolicyRuleInvalidPortRange(port=data,
                                         min=str(port_range_min),
                                         max=str(port_range_max))

    if (not (lower_bound_val >= 0 and lower_bound_val <= 65535 and
        upper_bound_val >= 0 and upper_bound_val <= 65535) and
        lower_bound_val <= upper_bound_val):
        port_range_min = randint(1, 65535)
        port_range_max = randint(port_range_min, 65535)
        raise PolicyRuleInvalidPortRange(port=data,
                                         min=str(port_range_min),
                                         max=str(port_range_max))


def _validate_action_target(self, action_target):
    #TODO(muawiakhan):FIXME
    return action_target

validators.validators['type:validate_port_range'] = _validate_port_range
validators.validators['type:validate_action_target'] = _validate_action_target
ep_supported_protocols = ['any', 'tcp', 'udp', 'icmp']
ep_supported_actions = ['copy', 'allow']


RESOURCE_ATTRIBUTE_MAP = {
    'policy_rule': {
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
        'tag': {
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
            'default': None,
            'validate': {'type:values': ep_supported_actions}
        },
        'action_target': {
            'allow_post': True,
            'allow_put': False,
            'is_visible': True,
            'default': None,
            'validate': {
                'type:validate_action_target': None
            },
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


class Policyrule(extensions.ExtensionDescriptor):

    @classmethod
    def get_name(cls):
        return "Policy Rule"

    @classmethod
    def get_alias(cls):
        return "policy-rule"

    @classmethod
    def get_description(cls):
        return "This API will be used to configure policy rules inside" \
               " policy groups from Neutron and map it in PLUMgrid."

    @classmethod
    def get_namespace(cls):
        return "http://docs.openstack.org/ext/policy_rule" \
               "/api/v2.0"

    @classmethod
    def get_updated(cls):
        return "2016-01-01T00:00:00-00:00"

    @classmethod
    def get_resources(cls):
        exts = []
        plugin = manager.NeutronManager.get_plugin()

        resource_name = PG_POLICY_RULE
        collection_name = PG_POLICY_RULES
        params = RESOURCE_ATTRIBUTE_MAP.get(resource_name, dict())
        controller = base.create_resource(
            collection_name, resource_name, plugin, params)
        ex = extensions.ResourceExtension(collection_name,
                                          controller)
        exts.append(ex)
        return exts
