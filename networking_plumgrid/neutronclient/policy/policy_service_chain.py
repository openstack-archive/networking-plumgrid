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


def _format_services(policy_service_chain):
    try:
        return '\n'.join([jsonutils.dumps(psc) for psc in
                          policy_service_chain['services']])
    except (TypeError, KeyError):
        return ''


class PolicyServiceChain(extension.NeutronClientExtension):
    resource = 'policy_service_chain'
    resource_plural = 'policy_service_chains'
    path = 'policy-service-chains'
    object_path = '/%s' % path
    resource_path = '/%s/%%s' % path
    versions = ['2.0']


def add_known_arguments(self, parser):
    parser.add_argument(
        '--policy-service',
        metavar='id=ID,name=NAME',
        action='append', dest='policy_services',
        type=utils.str2dict_type(optional_keys=['id', 'name']),
        help=_('Policy service to be added to policy chain.'
               ' id=<policy_service_uuid>,name=<policy_service_name>'
               '(--policy-service option can be repeated)'))
    parser.add_argument('--description', dest='description',
                        help=_('Description of'
                        ' policy service chain.'))


def args2body(self, parsed_args):
    try:
        if parsed_args.policy_services:
            services = parsed_args.policy_services
        else:
            services = []
        services_dict = []
        for service in services:
            if "id" in service:
                service = {'id': service['id']}
            elif "name" in service:
                service = {'id': service['name']}
            else:
                raise KeyError("ID or Name for service is required.")
            services_dict.append(service)
        if parsed_args.name:
            psc_name = parsed_args.name
            body = {'policy_service_chain': {'name': psc_name}}
        else:
            body = {'policy_service_chain': {}}
        if parsed_args.policy_services:
            body['policy_service_chain']['services'] = services_dict
        if parsed_args.description:
            (body['policy_service_chain']
                 ['description']) = parsed_args.description
        else:
            body['policy_service_chain']['description'] = ''
        return body
    except KeyError as err:
        raise Exception("KeyError: " + str(err))


class PolicyServiceChainCreate(extension.ClientExtensionCreate,
                               PolicyServiceChain):
    """Create an Policy Service Chain."""

    shell_command = 'policy-service-chain-create'

    def add_known_arguments(self, parser):
        parser.add_argument(
            'name', metavar='<POLICY-SERVICE-CHAIN-NAME>',
            help=_('Descriptive name for policy service chain.'))
        add_known_arguments(self, parser)

    def args2body(self, parsed_args):
        body = args2body(self, parsed_args)
        if parsed_args.tenant_id:
            (body['policy_service_chain']
                 ['tenant_id']) = parsed_args.tenant_id
        return body


class PolicyServiceChainList(extension.ClientExtensionList,
                             PolicyServiceChain):
    """List policy service chains that belong to a given tenant."""

    shell_command = 'policy-service-chain-list'
    list_columns = ['id', 'name', 'services']
    pagination_support = True
    sorting_support = True


class PolicyServiceChainShow(extension.ClientExtensionShow,
                             PolicyServiceChain):
    """Show information of a given policy service chain."""

    shell_command = 'policy-service-chain-show'


class PolicyServiceChainDelete(extension.ClientExtensionDelete,
                               PolicyServiceChain):
    """Delete a given policy service chain."""

    shell_command = 'policy-service-chain-delete'


class PolicyServiceChainUpdate(extension.ClientExtensionUpdate,
                               PolicyServiceChain):
    """Update a given policy service chain."""

    shell_command = 'policy-service-chain-update'

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--name', metavar='name',
            help=_('Descriptive name for policy service chain.'))
        parser.add_argument(
            '--add-services',
            metavar='id=ID,name=NAME',
            action='append', dest='add_services',
            type=utils.str2dict_type(optional_keys=['id', 'name']),
            help=_('Policy services to be added to service chain. '
                   'id=<policy_service_uuid>,name=<policy_service_name>'
                   '(--add-services option can be repeated.)'))
        parser.add_argument(
            '--remove-services',
            metavar='id=ID,name=NAME',
            action='append', dest='remove_services',
            type=utils.str2dict_type(optional_keys=['id', 'name']),
            help=_('Policy services to be removed from service chain. '
                   'id=<policy_service_uuid>,name=<policy_service_name>'
                   '(--remove-services option can be repeated.)'))
        parser.add_argument('--description', dest='description',
                            help=_('Description of'
                            ' policy service.'))

    def args2body(self, parsed_args):
        try:
            if parsed_args.add_services:
                add_services = parsed_args.add_services
            else:
                add_services = []
            add_services_dict = []
            for service in add_services:
                if "id" in service:
                    service = {'id': service['id']}
                elif "name" in service:
                    service = {'id': service['name']}
                else:
                    raise KeyError("ID or Name for policy service is required.")
                add_services_dict.append(service)
            if parsed_args.remove_services:
                remove_services = parsed_args.remove_services
            else:
                remove_services = []
            remove_services_dict = []
            for service in remove_services:
                if "id" in service:
                    service = {'id': service['id']}
                elif "name" in service:
                    service = {'id': service['name']}
                else:
                    raise KeyError("ID or Name for policy service is required.")
                remove_services_dict.append(service)
            if parsed_args.name:
                psc_name = parsed_args.name
                body = {'policy_service_chain': {'name': psc_name}}
            else:
                body = {'policy_service_chain': {}}
            if parsed_args.add_services:
                (body['policy_service_chain'][
                 'add_services']) = add_services_dict
            if parsed_args.remove_services:
                (body['policy_service_chain']
                 ['remove_services']) = remove_services_dict
            if parsed_args.description:
                body['policy_service_chain']['description'] = parsed_args.description

            return body
        except KeyError as err:
            raise Exception("KeyError: " + str(err))

