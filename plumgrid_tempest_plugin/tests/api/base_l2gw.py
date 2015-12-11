# Copyright 2015 PLUMgrid, Inc. All Rights Reserved.
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

from oslo_log import log as logging

LOG = logging.getLogger(__name__)


SEGMENTATION_ID_DELIMITER = "#"
INTERFACE_SEG_ID_DELIMITER = "|"
DEVICE_INTERFACE_DELIMITER = "::"
DEVICE_DELIMITER = ","
INTERFACE_DELIMITER = ";"
"""
  Sample for providing input for gateway creation in config is noted below
  Options provide flexibility to user to create l2gateway
  For single device ,single interface with single vlan
    l2gw_switch = device_name1::int_name1|vlan1
  For single device multiple interfaces with single or multiple vlans
    l2gw_switch = device_name1::int_name1|vlan1#vlan2;int_name2|vlan3
  For multiple devices with mutiple interfaces having single or mutiple vlan
    l2gw_switch = device_name1::int_name1|vlan1,device_name2::int_name2|vlan2
"""


def get_interface(interfaces):
    interface_dict = []
    for interface in interfaces:
        if INTERFACE_SEG_ID_DELIMITER in interface:
            (int_name, segid) = interface.split(INTERFACE_SEG_ID_DELIMITER)
            if SEGMENTATION_ID_DELIMITER in segid:
                segid = segid.split(SEGMENTATION_ID_DELIMITER)
            else:
                segid = [segid]
            interface_detail = {'name': int_name, 'segmentation_id': segid}
        else:
            interface_detail = {'name': interface}
        interface_dict.append(interface_detail)
    return interface_dict


def get_l2gw_body(l2gw_conf):
    device_dict = []
    devices = l2gw_conf.split(DEVICE_DELIMITER)
    for device in devices:
        if DEVICE_INTERFACE_DELIMITER in device:
            (device_name, device_ip, interface) = device.split(
                                                   DEVICE_INTERFACE_DELIMITER)
            if INTERFACE_DELIMITER in interface:
                interface_dict = interface.split(INTERFACE_DELIMITER)
                interfaces = get_interface(interface_dict)
            else:
                interfaces = get_interface([interface])
        device = {'device_name': device_name,
                  'device_ip': device_ip,
                  'interfaces': interfaces}
        device_dict.append(device)
    body = {'devices': device_dict}
    return body


def form_dict_devices(devices):
    seg_ids = []
    device_dict = dict()
    int_seg = []
    for device in devices:
        device_name = device['device_name']
        interfaces = device['interfaces']
        for interface in interfaces:
            interface_name = interface['name']
            int_seg.append(interface_name)
            seg_id = interface['segmentation_id']
            if type(seg_id) is list:
                for segid in seg_id:
                    seg_ids.append(segid)
            else:
                seg_ids.append(seg_id)
            int_seg.append(seg_id)
            device_dict.setdefault(device_name, []).append(int_seg)
            int_seg = []
    return device_dict
