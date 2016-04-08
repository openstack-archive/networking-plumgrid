# Copyright 2015 OpenStack Foundation.
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


def _format_interfaces(physical_attachment_point):
    try:
        return '\n'.join([jsonutils.dumps(pap) for pap in
                          physical_attachment_point['interfaces']])
    except (TypeError, KeyError):
        return ''


class PhysicalAttachmentPoint(extension.NeutronClientExtension):
    resource = 'physical_attachment_point'
    resource_plural = 'physical_attachment_points'
    path = 'physical-attachment-points'
    object_path = '/%s' % path
    resource_path = '/%s/%%s' % path
    versions = ['2.0']


def add_known_arguments(self, parser):
    parser.add_argument(
        '--interface',
        metavar='hostname=HOSTNAME,interface_name=INTERFACE-NAME',
        action='append', dest='interfaces', type=utils.str2dict,
        help=_('Hostnames and corresponding interfaces for physical'
               ' attachment point. '
               '(--interface option can be repeated)'))
    parser.add_argument('--hash_mode', dest='hash_mode', help=_('Hash mode'
                        ' for the physical attachment point. Default is L2'))
    parser.add_argument('--lacp', dest='lacp', help=_('LACP mode is enabled'
                        ' or disabled. Default is enabled. Options:'
                        ' True/False'))
    parser.add_argument('--transit_domain', dest='transit_domain_id',
                        help=_('Transit domain where'
                        ' physical attachment point should be'))


def args2body(self, parsed_args):
    try:
        if parsed_args.interfaces:
            interfaces = parsed_args.interfaces
        else:
            interfaces = []
        interface_dict = []
        for interface in interfaces:
            if "hostname" in interface and "interface_name" in interface:
                interface = {'hostname': interface['hostname'],
                             'interface': interface['interface_name']}
            else:
                raise KeyError("hostname and interface_name are both needed")
            interface_dict.append(interface)
        if parsed_args.name:
            pap_name = parsed_args.name
            body = {'physical_attachment_point': {'name': pap_name}}
        else:
            body = {'physical_attachment_point': {}}
        if parsed_args.interfaces:
            body['physical_attachment_point']['interfaces'] = interface_dict
        if parsed_args.lacp:
            if (str(parsed_args.lacp).lower() == 'false' or
                str(parsed_args.lacp).lower() == 'true'):
                body['physical_attachment_point']['lacp'] = parsed_args.lacp
            else:
                raise Exception("Please pass True, true, False or false"
                                " for LACP")
        if parsed_args.hash_mode:
            (body['physical_attachment_point']
                 ['hash_mode']) = parsed_args.hash_mode
        if parsed_args.transit_domain_id:
            (body['physical_attachment_point']
                 ['transit_domain_id']) = parsed_args.transit_domain_id
        return body
    except KeyError as err:
        raise Exception("KeyError: " + str(err))


class PhysicalAttachmentPointCreate(extension.ClientExtensionCreate,
                                    PhysicalAttachmentPoint):
    """Create a physical attachment point."""

    shell_command = 'physical-attachment-point-create'

    def add_known_arguments(self, parser):
        parser.add_argument(
            'name', metavar='<PHYSICAL-ATTACHMENT-POINT-NAME>',
            help=_('Descriptive name for logical gateway.'))
        add_known_arguments(self, parser)

    def args2body(self, parsed_args):
        body = args2body(self, parsed_args)
        if parsed_args.tenant_id:
            (body['physical_attachment_point']
                 ['tenant_id']) = parsed_args.tenant_id
        return body


class PhysicalAttachmentPointList(extension.ClientExtensionList,
                                  PhysicalAttachmentPoint):
    """List physical attachment points that belong to a given tenant."""

    shell_command = 'physical-attachment-point-list'
    list_columns = ['id', 'name', 'transit_domain_id', 'interfaces']
    pagination_support = True
    sorting_support = True


class PhysicalAttachmentPointShow(extension.ClientExtensionShow,
                                  PhysicalAttachmentPoint):
    """Show information of a given physical attachment point."""

    shell_command = 'physical-attachment-point-show'


class PhysicalAttachmentPointDelete(extension.ClientExtensionDelete,
                                    PhysicalAttachmentPoint):
    """Delete a given physical attachment point."""

    shell_command = 'physical-attachment-point-delete'


class PhysicalAttachmentPointUpdate(extension.ClientExtensionUpdate,
                                    PhysicalAttachmentPoint):
    """Update a given physical attachment point."""

    shell_command = 'physical-attachment-point-update'

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--name', metavar='name',
            help=_('Descriptive name for logical gateway.'))
        parser.add_argument(
            '--add_interface',
            metavar='hostname=HOSTNAME,interface_name=INTERFACE-NAME',
            action='append', dest='add_interfaces', type=utils.str2dict,
            help=_('Hostnames and corresponding interfaces for physical'
                   ' attachment point. '
                   '(--add_interface option can be repeated)'))
        parser.add_argument(
            '--remove_interface',
            metavar='hostname=HOSTNAME,interface_name=INTERFACE-NAME',
            action='append', dest='remove_interfaces', type=utils.str2dict,
            help=_('Hostnames and corresponding interfaces for physical'
                   ' attachment point. '
                   '(--remove_interface option can be repeated)'))
        parser.add_argument('--hash_mode', dest='hash_mode', help=_('Hash mode'
                            ' for the physical attachment point. Example would'
                            ' L2, L3 etc'))
        parser.add_argument('--lacp', dest='lacp', help=_('LACP mode can be'
                            ' enabled or disabled. Default is disabled.'
                            ' Options: True/False'))

    def args2body(self, parsed_args):
        try:
            if parsed_args.add_interfaces:
                add_interfaces = parsed_args.add_interfaces
            else:
                add_interfaces = []
            add_interface_dict = []
            for interface in add_interfaces:
                if "hostname" in interface and "interface_name" in interface:
                    interface = {'hostname': interface['hostname'],
                                 'interface': interface['interface_name']}
                else:
                    raise KeyError("hostname and interface_name are "
                                   "both needed")
                add_interface_dict.append(interface)
            if parsed_args.remove_interfaces:
                remove_interfaces = parsed_args.remove_interfaces
            else:
                remove_interfaces = []
            remove_interface_dict = []
            for interface in remove_interfaces:
                if "hostname" in interface and "interface_name" in interface:
                    interface = {'hostname': interface['hostname'],
                                 'interface': interface['interface_name']}
                else:
                    raise KeyError("hostname and interface_name "
                                   "are both needed")
                remove_interface_dict.append(interface)
            if parsed_args.name:
                pap_name = parsed_args.name
                body = {'physical_attachment_point': {'name': pap_name}}
            else:
                body = {'physical_attachment_point': {}}
            if parsed_args.add_interfaces:
                (body['physical_attachment_point'][
                 'add_interfaces']) = add_interface_dict
            if parsed_args.remove_interfaces:
                (body['physical_attachment_point']
                 ['remove_interfaces']) = remove_interface_dict
            if parsed_args.lacp:
                if (str(parsed_args.lacp).lower() == 'false' or
                    str(parsed_args.lacp).lower() == 'true'):
                    (body['physical_attachment_point']
                     ['lacp']) = parsed_args.lacp
                else:
                    raise Exception("Please pass True/true, False/false"
                                    " for LACP")
            if parsed_args.hash_mode:
                (body['physical_attachment_point']
                     ['hash_mode']) = parsed_args.hash_mode
            return body
        except KeyError as err:
            raise Exception("KeyError: " + str(err))
