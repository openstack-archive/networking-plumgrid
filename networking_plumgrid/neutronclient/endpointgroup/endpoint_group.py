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


def _format_ports(endpoint_group):
    try:
        return '\n'.join([jsonutils.dumps(epg) for epg in
                          endpoint_group['ports']])
    except (TypeError, KeyError):
        return ''


class EndpointGroup(extension.NeutronClientExtension):
    resource = 'endpoint_group'
    resource_plural = 'endpoint_groups'
    path = 'endpoint-groups'
    object_path = '/%s' % path
    resource_path = '/%s/%%s' % path
    versions = ['2.0']


def add_known_arguments(self, parser):
    parser.add_argument(
        '--port',
        metavar='id=ID,name=NAME',
        action='append', dest='ports',
        type=utils.str2dict_type(optional_keys=['id', 'name']),
        help=_('Ports to be classified in endpoint'
               ' group. id=<port_uuid>,name=<port_name>'
               '(--port option can be repeated)'))
    parser.add_argument('--description', dest='description',
                        help=_('Description of'
                        ' endpoint group'))


def args2body(self, parsed_args):
    try:
        if parsed_args.ports:
            ports = parsed_args.ports
        else:
            ports = []
        port_dict = []
        for port in ports:
            if "id" in port:
                port = {'id': port['id']}
            elif "name" in port:
                port = {'id': port['name']}
            else:
                raise KeyError("ID or Name for port is required.")
            port_dict.append(port)
        if parsed_args.name:
            epg_name = parsed_args.name
            body = {'endpoint_group': {'name': epg_name}}
        else:
            body = {'endpoint_group': {}}
        if parsed_args.endpoint_type:
            if (str(parsed_args.endpoint_type).lower() == 'vm_ep' or
                str(parsed_args.endpoint_type).lower() == 'vm_class'):
                body['endpoint_group']['endpoint_type'] \
                    = parsed_args.endpoint_type
            else:
                raise Exception("Supported values for endpoint type are:"
                                " vm_ep, vm_class")
        else:
            body['endpoint_group']['endpoint_type'] = 'vm_class'
        if parsed_args.ports:
            body['endpoint_group']['ports'] = port_dict
        if parsed_args.description:
            (body['endpoint_group']
                 ['description']) = parsed_args.description
        else:
            body['endpoint_group']['description'] = ''
        return body
    except KeyError as err:
        raise Exception("KeyError: " + str(err))


class EndpointGroupCreate(extension.ClientExtensionCreate,
                          EndpointGroup):
    """Create an Endpoint group."""

    shell_command = 'endpoint-group-create'

    def add_known_arguments(self, parser):
        parser.add_argument(
            'name', metavar='<ENDPOINT-GROUP-NAME>',
            help=_('Descriptive name for endpoint group.'))
        parser.add_argument('--type', dest='endpoint_type',
                            help=_('Type'
                            ' of endpoint group. Default is vm_class. Options:'
                            ' vm_class, vm_ep'))
        add_known_arguments(self, parser)

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
    list_columns = ['id', 'name', 'endpoint_type', 'ports']
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
    """Update a given endpoint group."""

    shell_command = 'endpoint-group-update'

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--name', metavar='name',
            help=_('Descriptive name for endpoint.'))
        parser.add_argument(
            '--add-ports',
            metavar='id=ID,name=NAME',
            action='append', dest='add_ports',
            type=utils.str2dict_type(optional_keys=['id', 'name']),
            help=_('Ports/Servers to be added to endpoint group. '
                   'id=<port_uuid>,name=<port_name>'
                   '(--add-ports option can be repeated)'))
        parser.add_argument(
            '--remove-ports',
            metavar='id=ID,name=NAME',
            action='append', dest='remove_ports',
            type=utils.str2dict_type(optional_keys=['id', 'name']),
            help=_('Ports/Servers to be removed from endpoint group. '
                   'id=<port_uuid>,name=<port_name>'
                   '(--remove-ports option can be repeated)'))
        parser.add_argument('--description', dest='description',
                            help=_('Description of'
                            ' endpoint group'))

    def args2body(self, parsed_args):
        try:
            if parsed_args.add_ports:
                add_ports = parsed_args.add_ports
            else:
                add_ports = []
            add_port_dict = []
            for port in add_ports:
                if "id" in port:
                    port = {'id': port['id']}
                elif "name" in port:
                    port = {'id': port['name']}
                else:
                    raise KeyError("ID or Name for port is required.")
                add_port_dict.append(port)
            if parsed_args.remove_ports:
                remove_ports = parsed_args.remove_ports
            else:
                remove_ports = []
            remove_port_dict = []
            for port in remove_ports:
                if "id" in port:
                    port = {'id': port['id']}
                elif "name" in port:
                    port = {'id': port['name']}
                else:
                    raise KeyError("ID or Name for port is required.")
                remove_port_dict.append(port)
            if parsed_args.name:
                epg_name = parsed_args.name
                body = {'endpoint_group': {'name': epg_name}}
            else:
                body = {'endpoint_group': {}}
            if parsed_args.add_ports:
                (body['endpoint_group'][
                 'add_ports']) = add_port_dict
            if parsed_args.remove_ports:
                (body['endpoint_group']
                 ['remove_ports']) = remove_port_dict
            if parsed_args.description:
                body['endpoint_group']['description'] = parsed_args.description

            return body
        except KeyError as err:
            raise Exception("KeyError: " + str(err))
