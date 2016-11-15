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


class PolicyRule(extension.NeutronClientExtension):
    resource = 'policy_rule'
    resource_plural = 'policy_rules'
    path = 'policy-rules'
    object_path = '/%s' % path
    resource_path = '/%s/%%s' % path
    versions = ['2.0']


def add_known_arguments(self, parser):
        parser.add_argument(
            '--src-grp', dest='src_grp',
            help=_('Source endpoint group or security group '
                   'name or ID to apply policy.'))
        parser.add_argument(
            '--dest-grp', dest='dst_grp',
            help=_('Destination endpoint group OR security group '
                   'name or ID to apply policy.'))
        parser.add_argument(
            '--protocol', dest='protocol',
            help=_('Protocol of packet. Allowed values are: '
                   '[any, icmp, tcp, udp]'))
        parser.add_argument(
            '--src-port-range', metavar='e.g. 1-65535',
            dest='src_port_range',
            help=_('Source port range for policy. Not supported for ICMP'))
        parser.add_argument(
            '--dest-port-range', metavar='e.g. 1-65535',
            dest='dst_port_range',
            help=_('Destination port range. Not supported for ICMP.'))
        parser.add_argument(
            '--action', dest='action',
            help=_('Action to be performed by the policy. Allowed'
                   ' values are: [copy, allow]'))
        parser.add_argument(
            '--action-target', metavar='<service_name/id or '
            'or tenant_id:service_name/uuid',
            dest='action_target',
            help=_('Action target for policy rule  i.e. policy service'
                   ' or tenant_id:policy service'))
        parser.add_argument(
            '--sgt', action='store_true',
            help=_('Apply source endpoint group tag to policy rule'))
        parser.add_argument(
            '--dgt', action='store_true',
            help=_('Apply destination endpoint group tag to policy rule'))
        parser.add_argument(
            '--tag', metavar='POLICY_TAG',
            dest='tag',
            help=_('Global policy tag to be applied to policy rule'))


def args2body(self, parsed_args):
    try:
        if parsed_args.name:
            pr_name = parsed_args.name
            body = {'policy_rule': {'name': pr_name}}
        else:
            body = {'policy_rule': {}}
        if parsed_args.action:
            if (str(parsed_args.action).lower() == 'copy' or
                str(parsed_args.action).lower() == 'allow'):
                body['policy_rule']['action'] = parsed_args.action
            else:
                raise Exception("Supported values for action are:"
                                " [allow, copy]")
        if parsed_args.src_grp:
            body['policy_rule']['src_grp'] = parsed_args.src_grp
        if parsed_args.dst_grp:
            body['policy_rule']['dst_grp'] = parsed_args.dst_grp
        if parsed_args.src_port_range:
            body['policy_rule']['src_port_range'] \
                = parsed_args.src_port_range
        if parsed_args.dst_port_range:
            body['policy_rule']['dst_port_range'] \
                = parsed_args.dst_port_range
        if parsed_args.protocol:
            supported_protocol = ['any', 'tcp', 'udp', 'icmp']
            if (str(parsed_args.protocol).lower() in supported_protocol):
                body['policy_rule']['protocol'] = parsed_args.protocol
            else:
                raise Exception("Supported values for protocol are:"
                                " [any, icmp, tcp, udp]")
        if (str(parsed_args.action).lower() == 'allow' and
            parsed_args.action_target):
            raise Exception("Target can only be specified with the"
                            " following action(s): ['copy']")
        if (str(parsed_args.action).lower() == 'copy'
            and not parsed_args.action_target):
            raise Exception("Action Target should be specified with "
                            "the following action(s): ['copy']")
        if (parsed_args.action_target and
            str(parsed_args.action).lower() != 'copy'):
            raise Exception("Action Target should be specified with "
                            "the following action(s): ['copy']")
        if parsed_args.action_target:
            if(len(parsed_args.action_target.split(":")) > 2):
                raise Exception("Invalid format for action target. "
                                "Help: <service_name/id or "
                                "or tenant_id:service_name/uuid>")
            body['policy_rule']['action_target'] \
                = parsed_args.action_target
        if parsed_args.sgt and parsed_args.dgt:
            raise Exception("You cannot enable source and destination "
                            "policy tag for a policy_rule.")
        if (parsed_args.tag and (parsed_args.sgt or parsed_args.dgt)):
            raise Exception("You cannot enable global policy tag with sgt or "
                            "dgt for a policy_rule.")

        if ((parsed_args.src_port_range or parsed_args.dst_port_range) and
            not parsed_args.protocol):
            raise Exception("Must also specify protocol if port range"
                            " is given")
        if parsed_args.sgt:
            if not parsed_args.src_grp:
                raise Exception("Please specify source group with "
                                "--sgt(source group tag) option.")
            body['policy_rule']['tag'] = parsed_args.src_grp
        if parsed_args.dgt:
            if not parsed_args.dst_grp:
                raise Exception("Please specify source group with "
                                "--dgt(destination group tag) option.")
            body['policy_rule']['tag'] = parsed_args.dst_grp
        if parsed_args.tag:
            body['policy_rule']['tag'] = parsed_args.tag
        return body
    except KeyError as err:
        raise Exception("KeyError: " + str(err))


class PolicyRuleCreate(extension.ClientExtensionCreate,
                       PolicyRule):
    """Create an Policy Rule."""

    shell_command = 'policy-rule-create'

    def add_known_arguments(self, parser):
        parser.add_argument(
            'name', metavar='<POLICY-RULE-NAME>',
            help=_('Descriptive name for policy rule.'))
        add_known_arguments(self, parser)

    def args2body(self, parsed_args):
        body = args2body(self, parsed_args)
        if parsed_args.tenant_id:
            (body['policy_rule']
                 ['tenant_id']) = parsed_args.tenant_id
        return body


class PolicyRuleList(extension.ClientExtensionList,
                     PolicyRule):
    """List policy rules that belong to a given tenant."""

    shell_command = 'policy-rule-list'
    list_columns = (['id', 'name', 'src_grp', 'dst_grp', 'protocol',
                     'action', 'action_target'])
    pagination_support = True
    sorting_support = True


class PolicyRuleShow(extension.ClientExtensionShow,
                     PolicyRule):
    """Show information of a given policy rule."""

    shell_command = 'policy-rule-show'


class PolicyRuleDelete(extension.ClientExtensionDelete,
                       PolicyRule):
    """Delete a given policy rule."""

    shell_command = 'policy-rule-delete'
