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
            elif "name" in epg:
                epg = {'id': epg['name']}
            else:
                raise KeyError("ID for Endpoint Group is required.")
            epg_dict.append(epg)
        if parsed_args.ip_port_mask:
            ip_port_list = parsed_args.ip_port_mask
        else:
            ip_port_list = []
        ip_port_mask = None
        if len(ip_port_list) > 1:
            raise Exception("Cannot use multiple ip-port classifcation "
                            "criteria. Please specify only one.")
        for ip_port in ip_port_list:
            if "ip" not in ip_port or \
               "port" not in ip_port or \
               "mask" not in ip_port:
                raise Exception("IP Address, Port and Port Mask need to be "
                                "specifed when using --ip-port classification")
            else:
                ip_port_mask = ip_port["ip"] + "_" + ip_port["port"] \
                               + "_" + ip_port["mask"]

        if ((parsed_args.port_id or parsed_args.ip_mask or
             parsed_args.ip_port_mask) and not
            parsed_args.ep_groups):
            raise Exception("Atleast one endpoint group(--endpoint-group)"
                            " is required for association.")
        if (parsed_args.ep_groups and (not parsed_args.port_id and not
            parsed_args.ip_mask and not parsed_args.ip_port_mask)):
            raise Exception("Please specify an association criteria. "
                            "Supported criterion are: ['--port', "
                            "'--ip-mask', '--ip-port']")
        if ((parsed_args.ip_port_mask and parsed_args.ip_mask) or
            (parsed_args.ip_port_mask and parsed_args.port_id) or
            (parsed_args.ip_mask and parsed_args.port_id)):
            raise Exception("Multiple association criterion for endpoint "
                            "specified. Please specify only one criteria "
                            "per endpoint.")
        if (not parsed_args.port_id and not parsed_args.ip_mask and
            not parsed_args.ip_port_mask):
            raise Exception("Please specify an association criteria. "
                            "Supported criterion are: ['--port', "
                            "'--ip-mask', '--ip-port']")
        if parsed_args.name:
            ep_name = parsed_args.name
            body = {'endpoint': {'name': ep_name}}
        else:
            body = {'endpoint': {}}
        if parsed_args.ep_groups:
            body['endpoint']['ep_groups'] = epg_dict
        if parsed_args.ip_port_mask:
            body['endpoint']['ip_port'] = ip_port_mask
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
        parser.add_argument('--port', dest='port_id',
                        metavar='PORT UUID/NAME',
                        help=_('Port UUID/NAME'))
        parser.add_argument('--ip-mask', dest='ip_mask',
                        help=_('IP Address/Mask'))
        parser.add_argument(
                   '--ip-port',
                   metavar='ip=IP-ADDRESS, port=PORT-NUMBER, mask=PORT-MASK',
                   action='append', dest='ip_port_mask', type=utils.str2dict,
                   help=_('IP Address and Port Mask to specify port range'))
        parser.add_argument(
                   '--endpoint-group',
                   metavar='id=ENPOINT-GROUP-UUID, name=ENDPOINT-GROUP-NAME',
                   action='append', dest='ep_groups', type=utils.str2dict,
                   help=_('Endpoint Groups to be associated with endpoint '
                          'id=<endpoint-group-uuid>,name=<endpoint-group-name>'
                          ' (--endpoint-group option can be repeated)'))

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
    list_columns = ['id', 'name', 'ep_groups', 'port_id', 'ip_mask',
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
            metavar='id=ENPOINT-GROUP-UUID, name=ENDPOINT-GROUP-NAME',
            action='append', dest='add_endpoint_groups', type=utils.str2dict,
            help=_('Endpoint Group ID to be associated with this Endpoint.'
                   '(--add-endpoint-group option can be repeated)'))
        parser.add_argument(
            '--remove-endpoint-group',
            metavar='id=ENPOINT-GROUP-UUID, name=ENDPOINT-GROUP-NAME',
            action='append', dest='remove_endpoint_groups',
            type=utils.str2dict,
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
                elif "name" in epg:
                    epg = {'id': epg["name"]}
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
                elif "name" in epg:
                    epg = {'id': epg['name']}
                else:
                    raise KeyError("ID for Endpoint Group is required.")
                remove_endpoint_group_dict.append(epg)

            if (parsed_args.add_endpoint_groups and
                parsed_args.remove_endpoint_groups):
                if len(set([tuple(d.items()) for d in
                       add_endpoint_group_dict]).
                       intersection(set([tuple(d.items()) for d
                       in remove_endpoint_group_dict]))) > 0:
                    raise Exception("Duplicate endpoint groups found.")
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
