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

from networking_plumgrid.neutron.plugins.common import \
    policy_exceptions as policy_exc
from neutron.common import constants


def _retrieve_subnet_dict(self, port_db, context):
    """
    Helper function to retrieve the subnet dictionary
    """
    # Retrieve subnet information
    subnet_db = {}
    if len(port_db["fixed_ips"]) != 0:
        for subnet_index in range(0,
                                  len(port_db["fixed_ips"])):
            subnet_id = (port_db["fixed_ips"][subnet_index]
                         ["subnet_id"])
            subnet_db[subnet_index] = self._get_subnet(context, subnet_id)
    return subnet_db


def _check_floatingip_in_use(self, fp_id, ptag_db):
    """
    Helper function to check if Floating IP already exists and
    is associated with a SecurityGroup/PolicyTag
    """
    for entry in ptag_db:
        if fp_id == entry["floatingip_id"]:
            return True
    return False


def _retrieve_floatingip_info(self, floating_ip_addr, floating_ip_db):
    """
    Helper function to retrieve the Floating IP ID for the
    specified Floating IP Address
    """
    for entry in floating_ip_db:
        if floating_ip_addr == entry["floating_ip_address"]:
            return entry
    return None


def _check_floatingip_network(self, context, ptag_db):
    """
    Helper function to check Floating IP is from the specified
    External Network
    """
    floatingip_db = self.get_floatingip(context,
                                        ptag_db["policy_tag"]["floatingip_id"])
    router_db = self.get_routers(context)
    floating_net_id = floatingip_db["floating_network_id"]

    if floatingip_db.get('port_id') is not None:
        raise policy_exc.FloatingIPAlreadyInUse(id=str(floatingip_db["id"]))

    external_gateway = []
    if "router_id" in ptag_db["policy_tag"] and \
                      ptag_db["policy_tag"]["router_id"] is not None:
        external_gateway.append(ptag_db["policy_tag"]["router_id"])
    else:
        for router in router_db:
            if "external_gateway_info" in router and \
             router["external_gateway_info"] and \
             router["external_gateway_info"]["network_id"] == floating_net_id:
                external_gateway.append(router["id"])
        if len(external_gateway) == 0:
            raise policy_exc.GatewayNotSet(id=str(floatingip_db["id"]))
        if len(external_gateway) > 1:
            raise policy_exc.MultipleExternalGatewaysFound(
                                           gateway_list=external_gateway)
    return (floatingip_db, external_gateway[0])
