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

"""
Test cases for  Neutron PLUMgrid Plug-in
"""

import mock
from oslo_utils import importutils

from networking_plumgrid.neutron.plugins.extensions import portbindings
from networking_plumgrid.neutron.plugins import plugin as plumgrid_plugin
from neutron import context
from neutron.extensions import providernet as provider
from neutron import manager
from neutron.tests.unit import _test_extension_portbindings as test_bindings
from neutron.tests.unit.db import test_db_base_plugin_v2 as test_plugin

PLUM_DRIVER = ('networking_plumgrid.neutron.plugins.drivers.'
               'fake_plumlib.Plumlib')
FAKE_DIRECTOR = '1.1.1.1'
FAKE_PORT = '1234'
FAKE_USERNAME = 'fake_admin'
FAKE_PASSWORD = 'fake_password'
FAKE_TIMEOUT = '0'


class PLUMgridPluginV2TestCase(test_plugin.NeutronDbPluginV2TestCase):
    _plugin_name = ('networking_plumgrid.neutron.plugins.'
                    'plugin.NeutronPluginPLUMgridV2')

    def setUp(self):
        def mocked_plumlib_init(self):
            director_plumgrid = FAKE_DIRECTOR
            director_port = FAKE_PORT
            director_username = FAKE_USERNAME
            director_password = FAKE_PASSWORD
            timeout = FAKE_TIMEOUT
            self._plumlib = importutils.import_object(PLUM_DRIVER)
            self._plumlib.director_conn(director_plumgrid,
                                        director_port, timeout,
                                        director_username,
                                        director_password)

        with mock.patch.object(plumgrid_plugin.NeutronPluginPLUMgridV2,
                               'plumgrid_init', new=mocked_plumlib_init):
            super(PLUMgridPluginV2TestCase, self).setUp(self._plugin_name)

    def tearDown(self):
        super(PLUMgridPluginV2TestCase, self).tearDown()


class TestPlumgridPluginNetworksV2(test_plugin.TestNetworksV2,
                                   PLUMgridPluginV2TestCase):
    pass


class TestPlumgridV2HTTPResponse(test_plugin.TestV2HTTPResponse,
                                 PLUMgridPluginV2TestCase):
    pass


class TestPlumgridPluginPortsV2(test_plugin.TestPortsV2,
                                PLUMgridPluginV2TestCase):

    def test_range_allocation(self):
        self.skipTest("Plugin does not support Neutron allocation process")

    def test_create_port_with_ipv6_dhcp_stateful_subnet_in_fixed_ips(self):
        self.skipTest("Plugin does not support IPv6")


class TestPlumgridPluginSubnetsV2(test_plugin.TestSubnetsV2,
                                  PLUMgridPluginV2TestCase):
    _unsupported = (
        'test_create_subnet_default_gw_conflict_allocation_pool_returns_409',
        'test_create_subnet_defaults', 'test_create_subnet_gw_values',
        'test_create_subnet_ipv6_gw_values',
        'test_update_subnet_gateway_in_allocation_pool_returns_409',
        'test_update_subnet_allocation_pools',
        'test_update_subnet_allocation_pools_invalid_pool_for_cidr')

    def setUp(self):
        if self._testMethodName in self._unsupported:
            self.skipTest("Plugin does not support Neutron allocation process")
        super(TestPlumgridPluginSubnetsV2, self).setUp()

    def test_create_subnets_bulk_emulated_plugin_failure(self):
        self.skipTest("Temporarily skipped; will be removed")

    def test_delete_network(self):
        self.skipTest("Temporarily skipped; will be removed")

    def test_subnet_admin_delete(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network1 = self._fake_network('network1')
        network1_ret = plugin.create_network(tenant_context, network1)

        subnet1 = self._fake_subnet(network1_ret['id'])
        plugin.create_subnet(tenant_context, subnet1)
        net_db = plugin.get_network(admin_context, network1_ret['id'])

        self.assertEqual(network1_ret['tenant_id'], net_db["tenant_id"])

    def _fake_network(self, name):
        data = {'network': {'name': name,
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
        return {'subnet': {'name': net_id,
                           'network_id': net_id,
                           'gateway_ip': '10.0.0.1',
                           'dns_nameservers': ['10.0.0.2'],
                           'host_routes': [],
                           'cidr': '10.0.0.0/24',
                           'allocation_pools': allocation_pools,
                           'enable_dhcp': True,
                           'ip_version': 4}}

    def test_subnet_update_enable_dhcp_no_ip_available_returns_409_ipv6(self):
        self.skipTest("Plugin does not support IPv6")

    def test_create_subnet_ipv6_pd_gw_values(self):
        self.skipTest("Plugin does not support IPv6")


class TestPlumgridPluginPortBinding(PLUMgridPluginV2TestCase,
                                    test_bindings.PortBindingsTestCase):
    VIF_TYPE = portbindings.VIF_TYPE_IOVISOR
    HAS_PORT_FILTER = True

    def setUp(self):
        super(TestPlumgridPluginPortBinding, self).setUp()


class TestPlumgridNetworkAdminState(PLUMgridPluginV2TestCase):
    def test_network_admin_state(self):
        name = 'network_test'
        admin_status_up = False
        tenant_id = 'tenant_test'
        network = {'network': {'name': name,
                               'admin_state_up': admin_status_up,
                               'tenant_id': tenant_id}}
        plugin = manager.NeutronManager.get_plugin()
        self.assertEqual(plugin._network_admin_state(network), network)


class TestPlumgridAllocationPool(PLUMgridPluginV2TestCase):
    def test_allocate_pools_for_subnet(self):
        cidr = '10.0.0.0/24'
        gateway_ip = '10.0.0.254'
        subnet = {'gateway_ip': gateway_ip,
                  'cidr': cidr,
                  'ip_version': 4}
        allocation_pool = [{"start": '10.0.0.2',
                            "end": '10.0.0.253'}]
        context = None
        plugin = manager.NeutronManager.get_plugin()
        pool = plugin._allocate_pools_for_subnet(context, subnet)
        self.assertEqual(allocation_pool, pool)

    def test_conflict_dhcp_gw_ip(self):
        cidr = '10.0.0.0/24'
        gateway_ip = '10.0.0.1'
        subnet = {'gateway_ip': gateway_ip,
                  'cidr': cidr,
                  'ip_version': 4}
        allocation_pool = [{"start": '10.0.0.3',
                            "end": '10.0.0.254'}]
        context = None
        plugin = manager.NeutronManager.get_plugin()
        pool = plugin._allocate_pools_for_subnet(context, subnet)
        self.assertEqual(allocation_pool, pool)


class TestPlumgridProvidernet(PLUMgridPluginV2TestCase):

    def test_create_provider_network(self):
        tenant_id = 'admin'
        data = {'network': {'name': 'net1',
                            'admin_state_up': True,
                            'tenant_id': tenant_id,
                            provider.NETWORK_TYPE: 'vlan',
                            provider.SEGMENTATION_ID: 3333,
                            provider.PHYSICAL_NETWORK: 'phy3333'}}

        network_req = self.new_create_request('networks', data, self.fmt)
        net = self.deserialize(self.fmt, network_req.get_response(self.api))
        plumlib = importutils.import_object(PLUM_DRIVER)
        plumlib.create_network(tenant_id, net, data)
        self.assertEqual(net['network'][provider.NETWORK_TYPE], 'vlan')
        self.assertEqual(net['network'][provider.SEGMENTATION_ID], 3333)
        self.assertEqual(net['network'][provider.PHYSICAL_NETWORK], 'phy3333')

    def test_create_provider_non_external_non_shared_network(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        pap = {"physical_attachment_point": {
                   "tenant_id": "test_tenant",
                   "name": "test_name",
                   "hash_mode": "L2+L3",
                   "transit_domain_id": self._create_transit_domain(
                                        admin_context, plugin),
                   "lacp": True,
                   "interfaces": []}}

        pap_ret = plugin.create_physical_attachment_point(
                      admin_context, pap)
        data = {'network': {'name': 'net1',
                            'admin_state_up': True,
                            'tenant_id': 'test_tenant',
                            provider.NETWORK_TYPE: 'vlan',
                            provider.SEGMENTATION_ID: 3333,
                            provider.PHYSICAL_NETWORK: pap_ret['id'],
                            'shared': False,
                            'router:external': False}}

        net_db = plugin.create_network(admin_context, data)
        self.assertEqual(net_db['network'][provider.NETWORK_TYPE], 'vlan')
        self.assertEqual(net_db['network'][provider.SEGMENTATION_ID], 3333)
        self.assertEqual(
            net_db['network'][provider.PHYSICAL_NETWORK], pap_ret['id'])

    def _create_transit_domain(self, admin_context, plugin):
        td = {"transit_domain": {
                  "tenant_id": "test_tenant",
                  "name": "td",
                  "implicit": False}}
        res = plugin.create_transit_domain(admin_context, td)
        return res["id"]


class TestDisassociateFloatingIP(PLUMgridPluginV2TestCase):

    def test_disassociate_floating_ip(self):
        port_id = "abcdefgh"
        tenant_id = "94eb42de4e331"
        fip_net_id = "b843d18245678"
        fip_addr = "10.0.3.44"
        fip_id = "e623679734051"
        fip = {"router_id": "94eb42de4e331",
               "tenant_id": tenant_id,
               "floating_network_id": fip_net_id,
               "fixed_ip_address": "192.168.8.2",
               "floating_ip_address": fip_addr,
               "port_id": port_id,
               "id": fip_id}
        plumlib = importutils.import_object(PLUM_DRIVER)
        fip_res = plumlib.disassociate_floatingips(fip, port_id)
        self.assertEqual(fip_res["id"], fip_id)
        self.assertEqual(fip_res["floating_ip_address"], fip_addr)
        self.assertEqual(fip_res["floating_network_id"], fip_net_id)
