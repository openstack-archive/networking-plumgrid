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


class PolicyTag(extension.NeutronClientExtension):
    resource = 'policy_tag'
    resource_plural = 'policy_tags'
    path = 'policy-tags'
    object_path = '/%s' % path
    resource_path = '/%s/%%s' % path
    versions = ['2.0']


def args2body(self, parsed_args):
    try:
        if parsed_args.name:
            ptag_name = parsed_args.name
            body = {'policy_tag': {'name': ptag_name}}
        else:
            body = {'policy_tag': {}}
        if parsed_args.tag_type:
            if (str(parsed_args.tag_type).lower() == 'fip' or
                str(parsed_args.tag_type).lower() == 'dot1q' or
                str(parsed_args.tag_type).lower() == 'nsh'):
                body['policy_tag']['tag_type'] \
                    = parsed_args.tag_type
            else:
                raise Exception("Supported values for policy tag type are:"
                                " 'fip', 'dot1q', 'nsh'")
        else:
            raise Exception("Policy tag type is required to be specified. "
                            "Supported values for policy tag type are:"
                            " 'fip', 'dot1q', 'nsh'")
        if parsed_args.tag_id:
            body['policy_tag']['tag_id'] = parsed_args.tag_id
        else:
            body['policy_tag']['tag_id'] = ''
        if parsed_args.router_id:
            body['policy_tag']['router_id'] = parsed_args.router_id
        else:
            body['policy_tag']['router_id'] = None
        if parsed_args.floating_ip:
            body['policy_tag']['floating_ip'] = parsed_args.floating_ip
        else:
            body['policy_tag']['floating_ip'] = None
        if (parsed_args.tag_type and parsed_args.tag_type.lower() == 'fip' \
            and not parsed_args.floating_ip):
            raise Exception("Floating IP UUID must be specified when "
                            "using tag type=fip")
        if (parsed_args.tag_type and (parsed_args.tag_type.lower() == 'dot1q' \
            or parsed_args.tag_type.lower() == 'nsh') \
            and not parsed_args.tag_id):
            raise Exception("ID in range (xx-yy) must be specified when "
                            "using tag type=dot1q or type=nsh")
        if (parsed_args.router_id and parsed_args.tag_type.lower() != 'fip'):
            raise Exception("Tag type='fip' must be specified when using "
                            "Router ID")
        return body
    except KeyError as err:
        raise Exception("KeyError: " + str(err))


class PolicyTagCreate(extension.ClientExtensionCreate,
                      PolicyTag):
    """Create a Policy Tag."""

    shell_command = 'policy-tag-create'

    def add_known_arguments(self, parser):
        parser.add_argument(
            'name', metavar='<POLICY-TAG-NAME>',
            help=_('Descriptive name for policy tag.'))
        parser.add_argument('--type', dest='tag_type',
                            help=_('Type'
                            ' of policy tag. Options:'
                            ' fip, dot1q, nsh'))
        parser.add_argument('--floating-ip', dest='floating_ip',
                        help=_('UUID of Floating IP to associate '
                               ' with the Policy Tag.'))
        parser.add_argument('--tag-id', dest='tag_id',
                        help=_('ID in range xx-yy '))
        parser.add_argument('--router-id', dest='router_id',
                        help=_('Router ID to be specified in case '
                               'of multiple External Gateways, when '
                               'associating a Floating IP.'))

    def args2body(self, parsed_args):
        body = args2body(self, parsed_args)
        if parsed_args.tenant_id:
            (body['policy_tag']
                 ['tenant_id']) = parsed_args.tenant_id
        return body


class PolicyTagList(extension.ClientExtensionList,
                    PolicyTag):
    """List policy tags that belong to a given tenant."""

    shell_command = 'policy-tag-list'
    list_columns = ['id', 'name', 'tag_type', 'tag_id', 'floating_ip_address']
    pagination_support = True
    sorting_support = True


class PolicyTagShow(extension.ClientExtensionShow,
                    PolicyTag):
    """Show information of a given policy tag."""

    shell_command = 'policy-tag-show'


class PolicyTagDelete(extension.ClientExtensionDelete,
                      PolicyTag):
    """Delete a given policy tag."""

    shell_command = 'policy-tag-delete'


class PolicyTagUpdate(extension.ClientExtensionUpdate,
                      PolicyTag):
    """Update a given policy-tag."""

    shell_command = 'policy-tag-update'
