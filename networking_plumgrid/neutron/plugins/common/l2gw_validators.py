# Copyright 2015 PLUMgrid, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import netaddr
from neutron.api.v2 import attributes
from neutron.common import exceptions

from networking_plumgrid._i18n import _
from networking_plumgrid.neutron.plugins.common import constants

ALLOWED_CONNECTION_ATTRIBUTES = set((constants.NETWORK_ID,
                                     constants.SEG_ID,
                                     constants.L2GATEWAY_ID
                                     ))


def validate_gwdevice_list(data, valid_values=None):
    """Validate the list of devices."""
    if not data:
        # Devices must be provided
        msg = _("Cannot create a gateway with an empty device list")
        return msg
    try:
        for device in data:
            interface_data = device.get(constants.IFACE_NAME_ATTR)
            device_name = device.get(constants.DEVICE_ID_ATTR)
            device_ip = device.get(constants.DEVICE_IP_ATTR)
            if device_ip and not netaddr.valid_ipv4(device_ip):
                msg = _("Cannot create a gateway with an invalid device IP")
                return msg
            if not device_ip:
                msg = _("Cannot create a gateway with an empty device IP")
                return msg
            if not device_name:
                msg = _("Cannot create a gateway with an empty device_name")
                return msg
            if not interface_data:
                msg = _("Cannot create a gateway with an empty interface")
                return msg
            for int_dict in interface_data:
                err_msg = attributes._validate_dict(int_dict, None)
                if not int_dict.get('name'):
                    msg = _("Cannot create a gateway with an empty"
                            "interface name")
                    return msg
                if not constants.SEG_ID in int_dict:
                    msg = _("Cannot create a gateway with an empty "
                            "segmentation ID")
                    return msg
                else:
                    seg_id_list = int_dict.get(constants.SEG_ID)
                    if seg_id_list and type(seg_id_list) is not list:
                        msg = _("segmentation_id type should be of list type")
                        return msg
                    if len(seg_id_list) > 1:
                        msg = _("Only one segmentation_id per interface is "
                                "allowed")
                        return msg
                    if not seg_id_list:
                        msg = _("segmentation_id_list should not be empty")
                        return msg
                    for seg_id in seg_id_list:
                        is_valid_vlan_id(seg_id)
                    if err_msg:
                        return err_msg
    except TypeError:
        return (_("%s: provided data are not iterable") %
                validate_gwdevice_list.__name__)


def validate_network_mapping_list(network_mapping, check_vlan):
    """Validate network mapping list in connection."""
    if network_mapping.get('segmentation_id'):
        seg_id = network_mapping.get(constants.SEG_ID)
        is_valid_vlan_id(seg_id)

    if not network_mapping.get('segmentation_id'):
        raise exceptions.InvalidInput(
            error_message=_("Segmentation id must be specified in create"
                            "l2gateway connections"))
    network_id = network_mapping.get(constants.NETWORK_ID)
    if not network_id:
        raise exceptions.InvalidInput(
            error_message=_("A valid network identifier must be specified "
                            "when connecting a network to a network "
                            "gateway. Unable to complete operation"))
    connection_attrs = set(network_mapping.keys())
    if not connection_attrs.issubset(ALLOWED_CONNECTION_ATTRIBUTES):
        raise exceptions.InvalidInput(
            error_message=(_("Invalid keys found among the ones provided "
                             "in request : %(connection_attrs)s."),
                           connection_attrs))
    return network_id


def is_valid_vlan_id(seg_id):
    try:
        int_seg_id = int(seg_id)
    except ValueError:
        msg = _("Segmentation id must be a valid integer")
        raise exceptions.InvalidInput(error_message=msg)
    if int_seg_id < 0 or int_seg_id >= 4095:
        msg = _("Segmentation id is out of range")
        raise exceptions.InvalidInput(error_message=msg)


def is_valid_cidr(vtep_ip):
    if "/" not in vtep_ip:
        msg = _("Invalid CIDR format specified")
        raise exceptions.InvalidInput(error_message=msg)
    else:
        try:
            netaddr.IPNetwork(vtep_ip)
        except Exception as err_message:
            raise exceptions.InvalidInput(error_message=err_message)
