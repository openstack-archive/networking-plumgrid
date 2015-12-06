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

from networking_plumgrid.neutron.plugins.db import pg_models


def add_network_binding(session, network_id, network_type, physical_network,
                        vlan_id):
    binding = pg_models.ProviderNetBinding(network_id=network_id,
                                           network_type=network_type,
                                           physical_network=physical_network,
                                           vlan_id=vlan_id)
    session.add(binding)
    return binding


def get_network_binding(session, network_id):
    qry = session.query(pg_models.ProviderNetBinding)
    nets = qry.filter_by(network_id=network_id).first()
    return nets
