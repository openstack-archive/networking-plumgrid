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

from networking_plumgrid.neutron.plugins.common import constants as \
    net_pg_const


def _validate_endpoint_group_port(port_db):
    """
    Helper function to validate port is owner by VM
    """
    if ("device_owner" in port_db and "binding:vif_type" in port_db and
        "compute" in port_db["device_owner"] and
        port_db["binding:vif_type"] == net_pg_const.BINDING_VIF_TYPE_IOVISOR):
        return True
    return False


def _validate_vm_ep_association(port_db, ep_type):
    """
    Helper function to validate if port being added to
    endpoint group type 'vm_ep' is not associated with a
    security group
    """
    if ep_type == net_pg_const.VM_CLASSIFICATION:
        return True
    elif ep_type == net_pg_const.VM_EP:
        if "security_groups" in port_db and not port_db["security_groups"]:
            return True
    return False
