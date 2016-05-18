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


class EndpointPolicy(extension.NeutronClientExtension):
    resource = 'endpoint_policy'
    resource_plural = 'endpoint_policies'
    path = 'endpoint-policies'
    object_path = '/%s' % path
    resource_path = '/%s/%%s' % path
    versions = ['2.0']


def add_known_arguments(self, parser):
        parser.add_argument(
            '--source-group', dest='src_grp',
            help=_('Source endpoint group name or ID to apply policy.'))
        parser.add_argument(
            '--destination-group', dest='dst_grp',
            help=_('Destination endpoint group name or ID to apply policy.'))
        parser.add_argument(
            '--protocol', dest='protocol',
            help=_('Protocol of packet. Allowed values are: '
                   '[any, icmp, tcp, udp]'))
        parser.add_argument(
            '--source-port-range', metavar='e.g. 1-65535',
            dest='src_port_range',
            help=_('Source port range for policy. Not supported for ICMP'))
        parser.add_argument(
            '--destination-port-range', metavar='e.g. 1-65535',
            dest='dst_port_range',
            help=_('Destination port range. Not supported for ICMP.'))
        parser.add_argument(
            '--action', dest='action',
            help=_('Action to be performed by the policy. Allowed'
                   ' values are: [copy]'))
        parser.add_argument(
            '--service-endpoint-group', metavar='SERVICE_ENDPOINT_GROUP',
            dest='service_epg',
            help=_('Service endpoint group name i.e. endpoint group with'
                   ' type "vm_ep" or ID to apply policy.'))


def args2body(self, parsed_args):
    try:
        if parsed_args.name:
            epg_name = parsed_args.name
            body = {'endpoint_policy': {'name': epg_name}}
        else:
            body = {'endpoint_policy': {}}
        if parsed_args.action:
            if (str(parsed_args.action).lower() == 'copy'):
                body['endpoint_policy']['action'] = parsed_args.action
            else:
                raise Exception("Supported values for action are:"
                                " [copy]")
        if parsed_args.src_grp:
            body['endpoint_policy']['src_grp'] = parsed_args.src_grp
        if parsed_args.dst_grp:
            body['endpoint_policy']['dst_grp'] = parsed_args.dst_grp
        if parsed_args.src_port_range:
            body['endpoint_policy']['src_port_range'] \
                = parsed_args.src_port_range
        if parsed_args.dst_port_range:
            body['endpoint_policy']['dst_port_range'] \
                = parsed_args.dst_port_range
        if parsed_args.protocol:
            supported_protocol = ['any', 'tcp', 'udp', 'icmp']
            if (str(parsed_args.protocol).lower() in supported_protocol):
                body['endpoint_policy']['protocol'] = parsed_args.protocol
            else:
                raise Exception("Supported values for protocol are:"
                                " [any, icmp, tcp, udp]")
        if not parsed_args.service_epg:
            raise Exception("Service endpoint group is mandatory"
                            " for endpoint policy.")
        else:
            body['endpoint_policy']['service_endpoint_group'] \
                = parsed_args.service_epg
        return body
    except KeyError as err:
        raise Exception("KeyError: " + str(err))


class EndpointPolicyCreate(extension.ClientExtensionCreate,
                          EndpointPolicy):
    """Create an Endpoint policy."""

    shell_command = 'endpoint-policy-create'

    def add_known_arguments(self, parser):
        parser.add_argument(
            'name', metavar='<ENDPOINT-POLICY-NAME>',
            help=_('Descriptive name for endpoint policy.'))
        add_known_arguments(self, parser)

    def args2body(self, parsed_args):
        body = args2body(self, parsed_args)
        if parsed_args.tenant_id:
            (body['endpoint_policy']
                 ['tenant_id']) = parsed_args.tenant_id
        return body


class EndpointPolicyList(extension.ClientExtensionList,
                        EndpointPolicy):
    """List endpoint policies that belong to a given tenant."""

    shell_command = 'endpoint-policy-list'
    list_columns = (['id', 'name', 'protocol', 'service_endpoint_group'])
    pagination_support = True
    sorting_support = True


class EndpointPolicyShow(extension.ClientExtensionShow,
                        EndpointPolicy):
    """Show information of a given endpoint policy."""

    shell_command = 'endpoint-policy-show'


class EndpointPolicyDelete(extension.ClientExtensionDelete,
                          EndpointPolicy):
    """Delete a given endpoint policy."""

    shell_command = 'endpoint-policy-delete'
