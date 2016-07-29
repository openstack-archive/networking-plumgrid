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
Policy Tag extension unit tests
"""
from networking_plumgrid.neutron.plugins.common import \
    policy_exceptions as policy_excep
from networking_plumgrid.neutron.plugins.extensions import \
    policytag
from networking_plumgrid.neutron.tests.unit import \
    test_networking_plumgrid as test_pg

from neutron.api import extensions
from neutron import context
from neutron.extensions import l3
from neutron import manager
from neutron.tests.unit.api import test_extensions as test_ext
from oslo_log import log as logging

LOG = logging.getLogger(__name__)


class PolicyTagExtensionManager(object):

    def get_resources(self):
        return policytag.Policytag.get_resources()

    def get_actions(self):
        return []

    def get_request_extensions(self):
        return []


class PolicyTagTestCase(test_pg.PLUMgridPluginV2TestCase):
    def setUp(self, plugin=None, ext_mgr=None):
        super(PolicyTagTestCase, self).setUp()
        ext_mgr = PolicyTagExtensionManager()
        extensions.PluginAwareExtensionManager._instance = None
        self.ext_api = test_ext.setup_extensions_middleware(ext_mgr)


class TestPolicyTag(PolicyTagTestCase):
    def test_create_policy_tag_with_fip(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        subnet = self._fake_subnet(network_ret["id"])
        subnet["subnet"]["tenant_id"] = tenant_context.tenant_id
        plugin.create_subnet(tenant_context, subnet)

        floatingip = self._make_floatingip_dict(network_ret)
        floatingip_ret = plugin.create_floatingip(admin_context, floatingip)
        ptag = self._make_ptag_dict(tag_type="fip",
                    floatingip_id=floatingip_ret["id"],
                    floating_ip_address=floatingip_ret["floating_ip_address"],
                    router_id="testrouter")

        ptag_ret = plugin.create_policy_tag(
                      admin_context, ptag)
        ptag["policy_tag"]["id"] = ptag_ret["id"]
        self.assertEqual(ptag_ret, ptag["policy_tag"])

    def test_create_policy_tag_with_dot1q(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        ptag = self._make_ptag_dict(tag_type="dot1q",
                                    tag_id="100-200")

        ptag_ret = plugin.create_policy_tag(
                      admin_context, ptag)
        ptag["policy_tag"]["id"] = ptag_ret["id"]
        self.assertEqual(ptag_ret, ptag["policy_tag"])

    def test_create_policy_tag_with_nsh(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        ptag = self._make_ptag_dict(tag_type="nsh",
                                    tag_id="10")

        ptag_ret = plugin.create_policy_tag(
                      admin_context, ptag)
        ptag["policy_tag"]["id"] = ptag_ret["id"]
        self.assertEqual(ptag_ret, ptag["policy_tag"])

    def test_create_policy_tag_with_no_type(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        ptag = self._make_ptag_dict(tag_type=None)

        self.assertRaises(policy_excep.InvalidPolicyTagType,
                          plugin.create_policy_tag, admin_context, ptag)

    def test_create_policy_tag_with_non_existing_fip(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        ptag = self._make_ptag_dict(tag_type="fip",
                                    floatingip_id="testid",
                                    floating_ip_address="10.0.0.1",
                                    router_id="test-router")

        self.assertRaises(l3.FloatingIPNotFound,
                          plugin.create_policy_tag, admin_context, ptag)

    def test_create_policy_tag_in_use_fip(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        subnet = self._fake_subnet(network_ret["id"])
        subnet["subnet"]["tenant_id"] = tenant_context.tenant_id
        plugin.create_subnet(tenant_context, subnet)

        floatingip = self._make_floatingip_dict(network_ret)
        floatingip_ret = plugin.create_floatingip(admin_context, floatingip)
        ptag = self._make_ptag_dict(tag_type="fip",
                    floatingip_id=floatingip_ret["id"],
                    floating_ip_address=floatingip_ret["floating_ip_address"],
                    router_id="testrouter")

        # Create first policy tag with Floating IP
        plugin.create_policy_tag(
                      admin_context, ptag)

        # Create second policy tag with same Floating IP
        self.assertRaises(policy_excep.FloatingIPAlreadyInUse,
                          plugin.create_policy_tag, admin_context, ptag)

    def test_create_delete_policy_tag(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        subnet = self._fake_subnet(network_ret["id"])
        subnet["subnet"]["tenant_id"] = tenant_context.tenant_id
        plugin.create_subnet(tenant_context, subnet)

        floatingip = self._make_floatingip_dict(network_ret)
        floatingip_ret = plugin.create_floatingip(admin_context, floatingip)
        ptag = self._make_ptag_dict(tag_type="fip",
                    floatingip_id=floatingip_ret["id"],
                    floating_ip_address=floatingip_ret["floating_ip_address"],
                    router_id="testrouter")

        ptag_ret = plugin.create_policy_tag(
                      admin_context, ptag)

        resp = plugin.delete_policy_tag(admin_context, ptag_ret["id"])
        self.assertEqual(None, resp)

    def test_create_update_policy_tag(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        ptag = self._make_ptag_dict(tag_type="dot1q",
                                    tag_id="100-200")

        ptag_ret = plugin.create_policy_tag(
                      admin_context, ptag)

        ptag_update_dict = self._make_ptag_update_dict(
                                                   name="updated-policy-tag")
        ptag_update_ret = plugin.update_policy_tag(admin_context,
                                                   ptag_ret["id"],
                                                   ptag_update_dict)
        ptag_update_dict["policy_tag"]["id"] = ptag_update_ret["id"]
        ptag_update_dict["policy_tag"]["tag_id"] = ptag_update_ret["tag_id"]
        (ptag_update_dict["policy_tag"]
         ["tag_type"]) = ptag_update_ret["tag_type"]
        (ptag_update_dict["policy_tag"]
         ["router_id"]) = ptag_update_ret["router_id"]
        (ptag_update_dict["policy_tag"]
         ["floatingip_id"]) = ptag_update_ret["floatingip_id"]
        (ptag_update_dict["policy_tag"]
         ["floating_ip_address"]) = ptag_update_ret["floating_ip_address"]
        self.assertEqual(ptag_update_dict["policy_tag"], ptag_update_ret)

    def test_list_policy_tags(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        tenant_context = context.Context('', 'not_admin')

        # Create policy Tag with Floating IP
        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        subnet = self._fake_subnet(network_ret["id"])
        subnet["subnet"]["tenant_id"] = tenant_context.tenant_id
        plugin.create_subnet(tenant_context, subnet)

        floatingip = self._make_floatingip_dict(network_ret)
        floatingip_ret = plugin.create_floatingip(admin_context, floatingip)
        ptag1 = self._make_ptag_dict(tag_type="fip",
                    floatingip_id=floatingip_ret["id"],
                    floating_ip_address=floatingip_ret["floating_ip_address"],
                    router_id="testrouter")

        ptag_ret1 = plugin.create_policy_tag(
                      admin_context, ptag1)

        # Create Policy Tag with dot1q
        ptag2 = self._make_ptag_dict(tag_type="dot1q",
                                    tag_id="100-200")

        ptag_ret2 = plugin.create_policy_tag(
                      admin_context, ptag2)

        # Create Policy Tag with nsh
        ptag3 = self._make_ptag_dict(tag_type="nsh",
                                    tag_id="10")

        ptag_ret3 = plugin.create_policy_tag(
                      admin_context, ptag3)

        ptag_list_ret = plugin.get_policy_tags(admin_context)
        self.assertItemsEqual(ptag_list_ret, [ptag_ret1, ptag_ret2, ptag_ret3])

    def _make_ptag_dict(self, tag_type, tag_id=None,
                        floatingip_id=None, floating_ip_address=None,
                        router_id=None):
        return {"policy_tag": {
                               "tenant_id": "test_tenant",
                               "name": "test_name",
                               "tag_type": tag_type,
                               "tag_id": tag_id,
                               "floatingip_id": floatingip_id,
                               "floating_ip_address": floating_ip_address,
                               "router_id": router_id}}

    def _fake_network(self):
        data = {'network': {'name': "fake_network",
                            'admin_state_up': True,
                            'shared': False,
                            'router:external': True,
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
                           'enable_dhcp': False,
                           'ip_version': 4}}

    def _make_floatingip_dict(self, network):
        return {"floatingip": {"floating_network_id": network["id"],
                               "tenant_id": network["tenant_id"],
                               "router_id": "testrouter"}}

    def _make_ptag_update_dict(self, name="test_tenant"):
        return {"policy_tag": {
                               "tenant_id": "test_tenant",
                               "name": name}}
