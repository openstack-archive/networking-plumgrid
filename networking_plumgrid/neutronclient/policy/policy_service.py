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


def _format_ingress_ports(policy_service):
    try:
        return '\n'.join([jsonutils.dumps(ps) for ps in
                          policy_service['ingress_ports']])
    except(TypeError, KeyError):
        return ''


def _format_egress_ports(policy_service):
    try:
        return '\n'.join([jsonutils.dumps(ps) for ps in
                          policy_service['egress_ports']])
    except(TypeError, KeyError):
        return ''


class PolicyService(extension.NeutronClientExtension):
    resource = 'policy_service'
    resource_plural = 'policy_services'
    path = 'policy-services'
    object_path = '/%s' % path
    resource_path = '/%s/%%s' % path
    versions = ['2.0']


def add_known_arguments(self, parser):
    parser.add_argument(
        '--ingress-port',
        metavar='id=ID,name=NAME',
        action='append', dest='ingress_ports',
        type=utils.str2dict_type(optional_keys=['id', 'name']),
        help=_('Ingress port to be classified into policy service.'
               ' id=<ingress_port_uuid>,name=<ingress_port_name>'
               '(--ingress-port option can be repeated)'))
    parser.add_argument(
        '--egress-port',
        metavar='id=ID,name=NAME',
        action='append', dest='egress_ports',
        type=utils.str2dict_type(optional_keys=['id', 'name']),
        help=_('Egress port to be classified into policy service.'
               ' id=<egress_port_uuid>,name=<egress_port_name>'
               '(--egress-port option can be repeated)'))
    parser.add_argument(
        '--bidirectional-port',
        metavar='id=ID,name=NAME',
        action='append', dest='bidirect_ports',
        type=utils.str2dict_type(optional_keys=['id', 'name']),
        help=_('Bidirectional port to be classified into policy service.'
               ' id=<bidirectional_port_uuid>,name=<bidirectional_port_name>'
               '(--bidirectional-port option can be repeated)'))
    parser.add_argument('--description', dest='description',
                        help=_('Description of'
                        ' policy service.'))


def args2body(self, parsed_args):
    try:
        if parsed_args.ingress_ports:
            ingress_ports = parsed_args.ingress_ports
        else:
            ingress_ports = []
        ingress_port_dict = []
        for port in ingress_ports:
            if "id" in port:
                port = {'id': port['id']}
            elif "name" in port:
                port = {'id': port['name']}
            else:
                raise KeyError("ID or Name for ingress port is required.")
            ingress_port_dict.append(port)
        if parsed_args.egress_ports:
            egress_ports = parsed_args.egress_ports
        else:
            egress_ports = []
        egress_port_dict = []
        for port in egress_ports:
            if "id" in port:
                port = {'id': port['id']}
            elif "name" in port:
                port = {'id': port['name']}
            else:
                raise KeyError("ID or Name for egress port is required.")
            egress_port_dict.append(port)
        if parsed_args.bidirect_ports:
            bidirect_ports = parsed_args.bidirect_ports
        else:
            bidirect_ports = []
        bidirect_port_dict = []
        for port in bidirect_ports:
            if "id" in port:
                port = {'id': port['id']}
            elif "name" in port:
                port = {'id': port['name']}
            else:
                raise KeyError("ID or Name for ingress port is required.")
            bidirect_port_dict.append(port)
        if parsed_args.name:
            ps_name = parsed_args.name
            body = {'policy_service': {'name': ps_name}}
        else:
            body = {'policy_service': {}}
        if parsed_args.ingress_ports:
            body['policy_service']['ingress_ports'] = ingress_port_dict
        if parsed_args.egress_ports:
            body['policy_service']['egress_ports'] = egress_port_dict
        if parsed_args.bidirect_ports:
            body['policy_service']['bidirectional_ports'] = bidirect_port_dict
        if parsed_args.description:
            (body['policy_service']
                 ['description']) = parsed_args.description
        return body
    except KeyError as err:
        raise Exception("KeyError: " + str(err))


class PolicyServiceCreate(extension.ClientExtensionCreate,
                          PolicyService):
    """Create a Policy Service."""

    shell_command = 'policy-service-create'

    def add_known_arguments(self, parser):
        parser.add_argument(
            'name', metavar='<POLICY-SERVICE-NAME>',
            help=_('Descriptive name for policy service.'))
        add_known_arguments(self, parser)

    def args2body(self, parsed_args):
        body = args2body(self, parsed_args)
        if parsed_args.tenant_id:
            (body['policy_service']
                 ['tenant_id']) = parsed_args.tenant_id
        return body


class PolicyServiceList(extension.ClientExtensionList,
                        PolicyService):
    """List policy services that belong to a given tenant."""

    shell_command = 'policy-service-list'
    list_columns = ['id', 'name', 'ingress_ports', 'egress_ports',
                    'bidirectional_ports']
    pagination_support = True
    sorting_support = True


class PolicyServiceShow(extension.ClientExtensionShow,
                        PolicyService):
    """Show information of a given policy service."""

    shell_command = 'policy-service-show'


class PolicyServiceDelete(extension.ClientExtensionDelete,
                          PolicyService):
    """Delete a given policy service."""

    shell_command = 'policy-service-delete'


class PolicyServiceUpdate(extension.ClientExtensionUpdate,
                          PolicyService):
    """Update a given policy service."""

    shell_command = 'policy-service-update'

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--name', metavar='name',
            help=_('Descriptive name for policy service.'))
        parser.add_argument(
            '--add-ingress-port',
            metavar='id=ID,name=NAME',
            action='append', dest='add_ingress_ports',
            type=utils.str2dict_type(optional_keys=['id', 'name']),
            help=_('Ingress port to be added to policy service. '
                   'id=<ingress_port_uuid>,name=<ingress_port_name>'
                   '(--add-ingress-port option can be repeated)'))
        parser.add_argument(
            '--add-egress-port',
            metavar='id=ID,name=NAME',
            action='append', dest='add_egress_ports',
            type=utils.str2dict_type(optional_keys=['id', 'name']),
            help=_('Egress port to be added to policy service. '
                   'id=<egress_port_uuid>,name=<egress_port_name>'
                   '(--add-egress-port option can be repeated)'))
        parser.add_argument(
            '--remove-ingress-port',
            metavar='id=ID,name=NAME',
            action='append', dest='remove_ingress_ports',
            type=utils.str2dict_type(optional_keys=['id', 'name']),
            help=_('Ingress port to be removed from policy service. '
                   'id=<ingress_port_uuid>,name=<ingress_port_name>'
                   '(--remove-ingress_port option can be repeated)'))
        parser.add_argument(
            '--remove-egress-port',
            metavar='id=ID,name=NAME',
            action='append', dest='remove_egress_ports',
            type=utils.str2dict_type(optional_keys=['id', 'name']),
            help=_('Egress port to be removed from policy service. '
                   'id=<egress_port_uuid>,name=<egress_port_name>'
                   '(--remove-egress_port option can be repeated)'))
        parser.add_argument(
            '--add-bidirectional-port',
            metavar='id=ID,name=NAME',
            action='append', dest='add_bidirect_ports',
            type=utils.str2dict_type(optional_keys=['id', 'name']),
            help=_('Bidirectional port to be added to policy service. '
                  'id=<bidirectional_port_uuid>,name=<bidirectional_port_name>'
                  '(--add-bidirectional-port option can be repeated)'))
        parser.add_argument(
            '--remove-bidirectional-port',
            metavar='id=ID,name=NAME',
            action='append', dest='remove_bidirect_ports',
            type=utils.str2dict_type(optional_keys=['id', 'name']),
            help=_('Bidirectional port to be removed from policy service. '
                  'id=<bidirectional_port_uuid>,name=<bidirectional_port_name>'
                  '(--remove-bidirectional-port option can be repeated)'))
        parser.add_argument('--description', dest='description',
                            help=_('Description of'
                            ' policy service.'))

    def args2body(self, parsed_args):
        try:
            if parsed_args.add_ingress_ports:
                add_ingress_ports = parsed_args.add_ingress_ports
            else:
                add_ingress_ports = []
            add_ingress_port_dict = []
            for port in add_ingress_ports:
                if "id" in port:
                    port = {'id': port['id']}
                elif "name" in port:
                    port = {'id': port['name']}
                else:
                    raise KeyError("ID or Name for port is required.")
                add_ingress_port_dict.append(port)
            if parsed_args.add_egress_ports:
                add_egress_ports = parsed_args.add_egress_ports
            else:
                add_egress_ports = []
            add_egress_port_dict = []
            for port in add_egress_ports:
                if "id" in port:
                    port = {'id': port['id']}
                elif "name" in port:
                    port = {'id': port['name']}
                else:
                    raise KeyError("ID or Name for port is required.")
                add_egress_port_dict.append(port)
            if parsed_args.add_bidirect_ports:
                add_bidirect_ports = parsed_args.add_bidirect_ports
            else:
                add_bidirect_ports = []
            add_bidirect_port_dict = []
            for port in add_bidirect_ports:
                if "id" in port:
                    port = {'id': port['id']}
                elif "name" in port:
                    port = {'id': port['name']}
                else:
                    raise KeyError("ID or Name for port is required.")
                add_bidirect_port_dict.append(port)
            if parsed_args.remove_ingress_ports:
                remove_ingress_ports = parsed_args.remove_ingress_ports
            else:
                remove_ingress_ports = []
            remove_ingress_port_dict = []
            for port in remove_ingress_ports:
                if "id" in port:
                    port = {'id': port['id']}
                elif "name" in port:
                    port = {'id': port['name']}
                else:
                    raise KeyError("ID or Name for port is required.")
                remove_ingress_port_dict.append(port)
            if parsed_args.remove_egress_ports:
                remove_egress_ports = parsed_args.remove_egress_ports
            else:
                remove_egress_ports = []
            remove_egress_port_dict = []
            for port in remove_egress_ports:
                if "id" in port:
                    port = {'id': port['id']}
                elif "name" in port:
                    port = {'id': port['name']}
                else:
                    raise KeyError("ID or Name for port is required.")
                remove_egress_port_dict.append(port)
            if parsed_args.remove_bidirect_ports:
                remove_bidirect_ports = parsed_args.remove_bidirect_ports
            else:
                remove_bidirect_ports = []
            remove_bidirect_port_dict = []
            for port in remove_bidirect_ports:
                if "id" in port:
                    port = {'id': port['id']}
                elif "name" in port:
                    port = {'id': port['name']}
                else:
                    raise KeyError("ID or Name for port is required.")
                remove_bidirect_port_dict.append(port)
            if parsed_args.name:
                ps_name = parsed_args.name
                body = {'policy_service': {'name': ps_name}}
            else:
                body = {'policy_service': {}}
            if parsed_args.add_ingress_ports:
                (body['policy_service'][
                 'add_ingress_ports']) = add_ingress_port_dict
            if parsed_args.add_egress_ports:
                (body['policy_service'][
                 'add_egress_ports']) = add_egress_port_dict
            if parsed_args.remove_ingress_ports:
                (body['policy_service']
                 ['remove_ingress_ports']) = remove_ingress_port_dict
            if parsed_args.remove_egress_ports:
                (body['policy_service']
                 ['remove_egress_ports']) = remove_egress_port_dict
            if parsed_args.add_bidirect_ports:
                (body['policy_service']
                 ['add_bidirectional_ports']) = add_bidirect_port_dict
            if parsed_args.remove_bidirect_ports:
                (body['policy_service']
                 ['remove_bidirectional_ports']) = remove_bidirect_port_dict
            if parsed_args.description:
                (body['policy_service']
                 ['description']) = parsed_args.description

            return body
        except KeyError as err:
            raise Exception("KeyError: " + str(err))
