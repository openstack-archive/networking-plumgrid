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


class Endpoint(extension.NeutronClientExtension):
    resource = 'endpoint'
    resource_plural = 'endpoints'
    path = 'endpoints'
    object_path = '/%s' % path
    resource_path = '/%s/%%s' % path
    versions = ['2.0']


def args2body(self, parsed_args):
    try:
        if parsed_args.ep_groups:
            epg_list = parsed_args.ep_groups
        else:
            epg_list = []
        epg_dict = []
        for epg in epg_list:
            if "id" in epg:
                epg = {'id': epg['id']}
            else:
                raise KeyError("ID for Endpoint Group is required.")
            epg_dict.append(epg)
        if parsed_args.name:
            ep_name = parsed_args.name
            body = {'endpoint': {'name': ep_name}}
        else:
            body = {'endpoint': {}}
        if parsed_args.ep_groups:
            body['endpoint']['ep_groups'] = epg_dict
        if parsed_args.ip_port_mask:
            body['endpoint']['ip_port'] = parsed_args.ip_port_mask
        if parsed_args.label:
            body['endpoint']['label'] = parsed_args.label
        if parsed_args.ip_mask:
            body['endpoint']['ip_mask'] = parsed_args.ip_mask
        if parsed_args.port_id:
            body['endpoint']['port_id'] = parsed_args.port_id
        return body
    except KeyError as err:
        raise Exception("KeyError: " + str(err))


class EndpointCreate(extension.ClientExtensionCreate,
                    Endpoint):
    """Create a Endpoint."""

    shell_command = 'endpoint-create'

    def add_known_arguments(self, parser):
        parser.add_argument(
            'name', metavar='<ENDPOINT-NAME>',
            help=_('Descriptive name for endpoint.'))
        parser.add_argument('--description', dest='description',
                        help=_('Description of the Endpoint '
                               'being created.'))
        parser.add_argument('--port', dest='port_id',
                        help=_('Port UUID'))
        parser.add_argument('--label', dest='label',
                        help=_('Label value for non-OS containers'))
        parser.add_argument('--ip_mask', dest='ip_mask',
                        help=_('IP Address/Mask'))
        parser.add_argument('--ip_port', dest='ip_port_mask',
                        help=_('IP address:port/port_mask'))
        parser.add_argument(
                   '--endpoint-group',
                   metavar='id=ENPOINT-GROUP-UUID',
                   action='append', dest='ep_groups', type=utils.str2dict,
                   help=_('Endpoint Groups to be associated with endpoint '
                          'id=<endpoint-group-uuid>,name=<endpoint-name> '
                          '(--endpoint-group option can be repeated)'))

    def args2body(self, parsed_args):
        body = args2body(self, parsed_args)
        if parsed_args.tenant_id:
            (body['endpoint']
                 ['tenant_id']) = parsed_args.tenant_id
        return body


class EndpointList(extension.ClientExtensionList,
                   Endpoint):
    """List endpoints that belong to a given tenant."""

    shell_command = 'endpoint-list'
    list_columns = ['id', 'name', 'label', 'ep_groups', 'port_id', 'ip_mask',
                    'ip_port']
    pagination_support = True
    sorting_support = True


class EndpointShow(extension.ClientExtensionShow,
                   Endpoint):
    """Show information of a given endpoints."""

    shell_command = 'endpoint-show'


class EndpointDelete(extension.ClientExtensionDelete,
                     Endpoint):
    """Delete a given endpoint."""

    shell_command = 'endpoint-delete'


class EndpointUpdate(extension.ClientExtensionUpdate,
                     Endpoint):
    """Update a given endpoint."""

    shell_command = 'endpoint-update'

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--name', metavar='name',
            help=_('Descriptive name for Endpoint'))
        parser.add_argument(
            '--add-endpoint-group',
            metavar='id=ENPOINT-GROUP-UUID',
            action='append', dest='add_endpoint_groups', type=utils.str2dict,
            help=_('Endpoint Group ID to be associated with this Endpoint.'
                   '(--add-endpoint-group option can be repeated)'))
        parser.add_argument(
            '--remove-endpoint-group',
            metavar='id=ENPOINT-GROUP-UUID',
            action='append', dest='remove_endpoint_groups', type=utils.str2dict,
            help=_('Endpoint Group ID to be removed from this Endpoint.'
                   '(--remove-endpoint-group option can be repeated)'))

    def args2body(self, parsed_args):
        try:
            if parsed_args.add_endpoint_groups:
                add_endpoint_groups = parsed_args.add_endpoint_groups
            else:
                add_endpoint_groups = []
            add_endpoint_group_dict = []
            for epg in add_endpoint_groups:
                if "id" in epg:
                    epg = {'id': epg['id']}
                else:
                    raise KeyError("ID for Endpoint Group is required.")
                add_endpoint_group_dict.append(epg)
            if parsed_args.remove_endpoint_groups:
                remove_endpoint_groups = parsed_args.remove_endpoint_groups
            else:
                remove_endpoint_groups = []
            remove_endpoint_group_dict = []
            for epg in remove_endpoint_groups:
                if "id" in epg:
                    epg = {'id': epg['id']}
                else:
                    raise KeyError("ID for Endpoint Group is required.")
                remove_endpoint_group_dict.append(epg)

            if parsed_args.name:
                ep_name = parsed_args.name
                body = {'endpoint': {'name': ep_name}}
            else:
                body = {'endpoint': {}}
            if parsed_args.add_endpoint_groups:
                (body['endpoint'][
                 'add_endpoint_groups']) = add_endpoint_group_dict
            if parsed_args.remove_endpoint_groups:
                (body['endpoint'][
                 'remove_endpoint_groups']) = remove_endpoint_group_dict
            return body
        except KeyError as err:
            raise Exception("KeyError: " + str(err))
