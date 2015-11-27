# Copyright 2015 PLUMgrid, Inc. All Rights Reserved.
# All Rights Reserved
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
#

from neutronclient.common import extension
from neutronclient.i18n import _


class TransitDomain(extension.NeutronClientExtension):
    resource = 'transit_domain'
    resource_plural = 'transit_domains'
    path = 'transit-domains'
    object_path = '/%s' % path
    resource_path = '/%s/%%s' % path
    versions = ['2.0']


def args2body(self, parsed_args):
    try:
        if parsed_args.name:
            tvd_name = parsed_args.name
            body = {'transit_domain': {'name': tvd_name}}
        else:
            body = {'transit_domain': {}}
        return body
    except KeyError as err:
        raise Exception("KeyError: " + str(err))


class TransitDomainCreate(extension.ClientExtensionCreate,
                          TransitDomain):
    """Create a transit domain."""

    shell_command = 'transit-domain-create'

    def add_known_arguments(self, parser):
        parser.add_argument(
            'name', metavar='<TRANSIT-DOMAIN-NAME>',
            help=_('Descriptive name for transit domain.'))

    def args2body(self, parsed_args):
        body = args2body(self, parsed_args)
        if parsed_args.tenant_id:
            (body['transit_domain']
                 ['tenant_id']) = parsed_args.tenant_id
        return body


class TransitDomainList(extension.ClientExtensionList,
                        TransitDomain):
    """List transit domains"""

    shell_command = 'transit-domain-list'
    list_columns = ['id', 'name']
    pagination_support = True
    sorting_support = True


class TransitDomainShow(extension.ClientExtensionShow,
                        TransitDomain):
    """Show information of a given transit domain"""

    shell_command = 'transit-domain-show'


class TransitDomainDelete(extension.ClientExtensionDelete,
                          TransitDomain):
    """Delete a given transit domain"""

    shell_command = 'transit-domain-delete'


class TransitDomainUpdate(extension.ClientExtensionUpdate,
                          TransitDomain):
    """Update a given transit domain"""

    shell_command = 'transit-domain-update'

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--name', metavar='name',
            help=_('Descriptive name for transit domain'))

    def args2body(self, parsed_args):
        body = {'transit_domain': {'name': parsed_args.name}}
        return body
