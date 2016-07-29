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
from neutron_lib.api import validators
from neutron.api import extensions
from neutron.api.v2 import attributes as attr
from neutron.api.v2 import base
from neutron.common import exceptions as nexceptions
from neutron import manager

PG_POLICY_TAG = 'policy_tag'
PG_POLICY_TAGS = 'policy-tags'

extensions.append_api_extensions_path(
    networking_plumgrid.neutron.plugins.extensions.__path__)


class NoPolicyTagFound(nexceptions.NotFound):
    message = _("Policy Tag with id %(id)s does not exist")

def _validate_tag_id(self, tag_id):
    #TODO(muawiakhan): Fixme
    if tag_id is None:
        return tag_id
    try:
        lower_bound, upper_bound = tag_id.split('-')
    except (ValueError, TypeError):
        return tag_id

validators.validators['type:validate_tag_id'] = _validate_tag_id
pt_supported_types = ['fip', 'dot1q', 'nsh']

RESOURCE_ATTRIBUTE_MAP = {
    'policy_tag': {
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
        'tag_type': {
            'allow_post': True,
            'allow_put': True,
            'is_visible': True,
            'default': '',
            'validate': {'type:values': pt_supported_types}
        },
        'tag_id': {
            'allow_post': True,
            'allow_put': True,
            'is_visible': True,
            'default': None,
            'validate': {
                'type:validate_tag_id': None
            }
        },
        'floatingip_id': {
            'allow_post': True,
            'allow_put': True,
            'is_visible': True,
            'default': None,
            'validate': {
                'type:uuid_or_none': None
            },
        },
        'floating_ip_address': {
            'allow_post': True,
            'allow_put': True,
            'is_visible': True,
            'default': ''
        },
        'router_id': {
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


class Policytag(extensions.ExtensionDescriptor):

    @classmethod
    def get_name(cls):
        return "Policy Tag"

    @classmethod
    def get_alias(cls):
        return "policy-tag"

    @classmethod
    def get_description(cls):
        return "This API will be used to create policy tags" \
               " from Neutron and map it in PLUMgrid."

    @classmethod
    def get_namespace(cls):
        return "http://docs.openstack.org/ext/policy_tag" \
               "/api/v2.0"

    @classmethod
    def get_updated(cls):
        return "2016-01-01T00:00:00-00:00"

    @classmethod
    def get_resources(cls):
        exts = []
        plugin = manager.NeutronManager.get_plugin()

        resource_name = PG_POLICY_TAG
        collection_name = PG_POLICY_TAGS
        params = RESOURCE_ATTRIBUTE_MAP.get(resource_name, dict())
        controller = base.create_resource(
            collection_name, resource_name, plugin, params)
        ex = extensions.ResourceExtension(collection_name,
                                          controller)
        exts.append(ex)
        return exts
