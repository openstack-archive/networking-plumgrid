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
