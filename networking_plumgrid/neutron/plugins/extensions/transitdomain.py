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
from neutron.api.v2 import base
from neutron.common import exceptions as nexceptions
from neutron import manager


TVD = 'transit_domain'
TVDS = 'transit-domains'


class NoTransitDomainFound(nexceptions.NotFound):
    message = _("Transit domain with id %(id)s does not exist")


class TransitDomainInUse(nexceptions.InUse):
    message = _("Transit domain with id %(id)s is in use.")


RESOURCE_ATTRIBUTE_MAP = {
    TVD: {
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
        'implicit': {
            'allow_post': False,
            'allow_put': False,
            'is_visible': False,
            'default': False,
            'validate': {
                 'type:boolean': None
            }
        },
        'tenant_id': {
            'allow_post': True,
            'allow_put': False,
            'is_visible': True
        }
    }
}


class Transitdomain(extensions.ExtensionDescriptor):

    @classmethod
    def get_name(cls):
        return "Transit Domain"

    @classmethod
    def get_alias(cls):
        return "transit-domain"

    @classmethod
    def get_description(cls):
        return "Transit domain API"

    @classmethod
    def get_namespace(cls):
        return "http://docs.openstack.org/ext/transit_domains" \
               "/api/v2.0"

    @classmethod
    def get_updated(cls):
        return "2012-10-05T10:00:00-00:00"

    @classmethod
    def get_resources(cls):
        exts = []
        plugin = manager.NeutronManager.get_plugin()

        resource_name = TVD
        collection_name = TVDS
        params = RESOURCE_ATTRIBUTE_MAP.get(resource_name, dict())
        controller = base.create_resource(
            collection_name, resource_name, plugin, params)
        ex = extensions.ResourceExtension(collection_name,
                                          controller)
        exts.append(ex)
        return exts
