# Copyright 2016 PLUMgrid, Inc. All Rights Reserved.
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

"""
Policy Service extension unit tests
"""
#from networking_plumgrid.neutron.plugins.common import \
#    exceptions as p_excep
#from networking_plumgrid.neutron.plugins.common import \
#    policy_exceptions as policy_excep
from networking_plumgrid.neutron.plugins.extensions import \
    policyservice as ext_ps
from networking_plumgrid.neutron.tests.unit import \
    test_networking_plumgrid as test_pg

from neutron.api import extensions
from neutron.api.v2 import attributes
#from neutron import context
#from neutron import manager
from neutron.tests.unit.api import test_extensions as test_ext
from oslo_log import log as logging
#import uuid

LOG = logging.getLogger(__name__)


class PolicyServiceExtensionManager(object):

    def get_resources(self):
        return ext_ps.Policyservice.get_resources()

    def get_actions(self):
        return []

    def get_request_extensions(self):
        return []


class PolicyServiceTestCase(test_pg.PLUMgridPluginV2TestCase):
    def setUp(self, plugin=None, ext_mgr=None):
        super(PolicyServiceTestCase, self).setUp()
        ext_mgr = PolicyServiceExtensionManager()
        extensions.PluginAwareExtensionManager._instance = None
        self.ext_api = test_ext.setup_extensions_middleware(ext_mgr)


class TestPolicyService(PolicyServiceTestCase):

    def test_create_policy_service_inport(self):
        pass

    def test_create_policy_service_eport(self):
        pass

    def test_create_policy_service_bidirect_port(self):
        pass

    def test_create_policy_service_inport_name(self):
        pass

    def test_create_policy_service_eport_name(self):
        pass

    def test_create_policy_service_bidirect_port_name(self):
        pass

    def test_create_policy_service_dup_ports_inport(self):
        pass

    def test_create_policy_service_dup_ports_eport(self):
        pass

    def test_create_policy_service_dup_ports_bidirect(self):
        pass

    def test_create_policy_service_dup_ports_across_config(self):
        pass

    def test_create_policy_service_without_leg_mode(self):
        pass

    def test_create_policy_service_inport_owner_not_nova(self):
        pass

    def test_create_policy_service_eport_owner_not_nova(self):
        pass

    def test_create_policy_service_bidirect_port_owner_not_nova(self):
        pass

    def test_create_policy_service_inport_port_not_found(self):
        pass

    def test_create_policy_service_eport_port_not_found(self):
        pass

    def test_create_policy_service_bidirect_port_not_found(self):
        pass

    def test_create_policy_service_port_already_in_use_ps(self):
        pass

    def test_delete_policy_service(self):
        pass

    def test_delete_policy_service_ports_in_use(self):
        pass

    def test_delete_policy_service_does_not_exist(self):
        pass

    def test_update_policy_service_name(self):
        pass

    def test_update_policy_service_inport(self):
        pass

    def test_update_policy_service_eport(self):
        pass

    def test_update_policy_service_bidirect_port(self):
        pass

    def test_update_policy_service_add_dup_inports(self):
        pass

    def test_update_policy_service_add_dup_eports(self):
        pass

    def test_update_policy_service_add_dup_bidirect_ports(self):
        pass

    def test_update_policy_service_remove_dup_inports(self):
        pass

    def test_update_policy_service_remove_dup_eports(self):
        pass

    def test_update_policy_service_remove_dup_bidirect_ports(self):
        pass

    def test_update_policy_service_dup_ports(self):
        pass

    def test_update_policy_service_without_leg_mode(self):
        pass

    def test_update_policy_service_add_inports_owner_not_nova(self):
        pass

    def test_update_policy_service_add_eports_owner_not_nova(self):
        pass

    def test_update_policy_service_add_bidirect_ports_owner_not_nova(self):
        pass

    def test_update_policy_service_remove_inports_owner_not_nova(self):
        pass

    def test_update_policy_service_remove_eports_owner_not_nova(self):
        pass

    def test_update_policy_service_remove_bidirect_ports_owner_not_nova(self):
        pass

    def test_update_policy_service_add_inport_already_in_use(self):
        pass

    def test_update_policy_service_add_eport_already_in_use(self):
        pass

    def test_update_policy_service_add_bport_already_in_use(self):
        pass

    def test_create_get_policy_service(self):
        pass

    def test_create_update_get_policy_service_add_ports(self):
        pass

    def test_create_update_get_policy_service_remove_ports(self):
        pass

    def test_list_policy_services(self):
        pass

    def _make_ps_dict(self, name="test_ps", inports=[], eports=[],
                      bidirect_ports=[]):
        return {"policy_service": {
                    "tenant_id": "test_tenant",
                    "description": "test-ps",
                    "name": name,
                    "ingress_ports": inports,
                    "egress_ports": eports,
                    "bidirectional_ports": bidirect_ports}}

    def _make_ps_update_dict(self, name="updated_ps", add_inports=[],
                             add_eports=[], add_bidirect_ports=[],
                             remove_inports=[], remove_eports=[],
                             remove_bidirect_ports=[]):
        return {"policy_service": {
                     "tenant_id": "test_tenant",
                     "name": name,
                     "add_ingress_ports": add_inports,
                     "add_egress_ports": add_eports,
                     "add_bidirectional_ports": add_bidirect_ports,
                     "remove_ingress_ports": remove_inports,
                     "remove_egress_ports": remove_eports,
                     "remove_bidirectional_ports": remove_bidirect_ports}}

    def _fake_network(self):
        data = {'network': {'name': "fake_network",
                            'admin_state_up': False,
                            'shared': False,
                            'router:external': [],
                            'provider:network_type': None,
                            'provider:segmentation_id': None,
                            'provider:physical_network': None}}
        return data

    def _fake_subnet(self, net_id):
        allocation_pools = [{'start': '10.0.0.2',
                             'end': '10.0.0.254'}]
        return {'subnet': {'name': "fake_subnet",
                           'network_id': net_id,
                           'gateway_ip': '10.0.0.1',
                           'dns_nameservers': ['10.0.0.2'],
                           'host_routes': [],
                           'cidr': '10.0.0.0/24',
                           'allocation_pools': allocation_pools,
                           'enable_dhcp': True,
                           'ip_version': 4}}

    def _fake_port(self, net_id, name="fake_port", security_groups = [],
                   device_owner="compute:nova"):
        return {'port': {'name': name,
                         'network_id': net_id,
                         'mac_address': attributes.ATTR_NOT_SPECIFIED,
                         'fixed_ips': attributes.ATTR_NOT_SPECIFIED,
                         'admin_state_up': True,
                         'device_id': 'fake_device_id',
                         'device_owner': device_owner,
                         'tenant_id': "fake_tenant",
                         'security_group': security_groups}}
