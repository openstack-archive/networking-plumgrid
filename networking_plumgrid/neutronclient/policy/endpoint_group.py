# Copyright 2016 OpenStack Foundation.
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

from networking_plumgrid._i18n import _
from neutronclient.common import extension
from neutronclient.common import utils
from oslo_serialization import jsonutils


class EndpointGroup(extension.NeutronClientExtension):
    resource = 'endpoint_group'
    resource_plural = 'endpoint_groups'
    path = 'endpoint-groups'
    object_path = '/%s' % path
    resource_path = '/%s/%%s' % path
    versions = ['2.0']


def args2body(self, parsed_args):
    try:
        if parsed_args.name:
            ep_grp_name = parsed_args.name
            body = {'endpoint_group': {'name': ep_grp_name}}
        else:
            body = {'endpoint_group': {}}
        if parsed_args.tag:
            body['endpoint_group']['policy_tag_id'] = parsed_args.tag
        else:
            body['endpoint_group']['policy_tag_id'] = None
        if parsed_args.description:
            body['endpoint_group']['description'] = parsed_args.description
        else:
            body['endpoint_group']['description'] = ''
        return body
    except KeyError as err:
        raise Exception("KeyError: " + str(err))


class EndpointGroupCreate(extension.ClientExtensionCreate,
                          EndpointGroup):
    """Create a Endpoint Group."""

    shell_command = 'endpoint-group-create'

    def add_known_arguments(self, parser):
        parser.add_argument(
            'name', metavar='<ENDPOINT-GROUP-NAME>',
            help=_('Descriptive name for endpoint group.'))
        parser.add_argument('--description', dest='description',
                        help=_('Description of the Endpoint Group '
                               'being created.'))
        parser.add_argument('--tag', dest='tag',
                        help=_('policy-tag name/uuid '))
        #add_known_arguments(self, parser)

    def args2body(self, parsed_args):
        body = args2body(self, parsed_args)
        if parsed_args.tenant_id:
            (body['endpoint_group']
                 ['tenant_id']) = parsed_args.tenant_id
        return body


class EndpointGroupList(extension.ClientExtensionList,
                      EndpointGroup):
    """List endpoint groups that belong to a given tenant."""

    shell_command = 'endpoint-group-list'
    list_columns = ['id', 'name', 'policy_tag_id', 'description',
                    'is_security_group']
    pagination_support = True
    sorting_support = True


class EndpointGroupShow(extension.ClientExtensionShow,
                        EndpointGroup):
    """Show information of a given endpoint group."""

    shell_command = 'endpoint-group-show'


class EndpointGroupDelete(extension.ClientExtensionDelete,
                          EndpointGroup):
    """Delete a given endpoint group."""

    shell_command = 'endpoint-group-delete'


class EndpointGroupUpdate(extension.ClientExtensionUpdate,
                          EndpointGroup):
    """Update a given endpoint-group."""

    shell_command = 'endpoint-group-update'
