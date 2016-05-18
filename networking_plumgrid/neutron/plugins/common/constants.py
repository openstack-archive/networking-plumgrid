# Copyright 2016 PLUMgrid, Inc. All Rights Reserved.
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
# service type constants:
L2GW = "L2GW"
IFACE_NAME_ATTR = 'interface_name'
NETWORK_ID = 'network_id'
SEG_ID = 'segmentation_id'
L2_SERVICE_RESOURCE_NAME = 'l2_gateway_service'
L2GATEWAY_ID = 'l2_gateway_id'
GATEWAY_RESOURCE_NAME = 'l2_gateway'
L2_GATEWAYS = 'l2-gateways'
DEVICE_ID_ATTR = 'device_name'
DEVICE_IP_ATTR = 'device_ip'
IFACE_NAME_ATTR = 'interfaces'
CONNECTION_RESOURCE_NAME = 'l2_gateway_connection'
EXT_ALIAS = 'l2-gateway-connection'
L2_GATEWAY_SERVICES = "l2-gateway-services"
L2_GATEWAYS_CONNECTION = "%ss" % EXT_ALIAS
L3_GATEWAY_NET = 'l3-gateway'
LOCAL = "local"
SOURCE_EPG = "source_epg"
DESTINATION_EPG = "destination_epg"
SERVICE_EPG = "service_epg"
VM_EP = "vm_ep"
VM_CLASSIFICATION = "vm_class"
BINDING_VIF_TYPE_IOVISOR = "iovisor"
SUPPORTED_ENDPOINT_GROUP_TYPES = ["vm_class", "vm_ep"]
SUPPORTED_ENDPOINT_POLICY_PROTOCOLS = ["any", "tcp", "udp", "icmp"]
SUPPORTED_ENDPOINT_POLICY_ACTIONS = ['copy']
