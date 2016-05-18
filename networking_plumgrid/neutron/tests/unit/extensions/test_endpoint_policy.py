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
Endpoint Policy extension unit tests
"""
from networking_plumgrid.neutron.plugins.common import \
    endpoint_policy_exceptions as epp_excep
from networking_plumgrid.neutron.plugins.common import \
    exceptions as p_excep
from networking_plumgrid.neutron.plugins.extensions import \
    endpointpolicy as ext_epp
from networking_plumgrid.neutron.tests.unit import \
    test_networking_plumgrid as test_pg

from neutron.api import extensions
from neutron import context
from neutron import manager
from neutron.tests.unit.api import test_extensions as test_ext
from oslo_log import log as logging
import uuid

LOG = logging.getLogger(__name__)


class EndpointPolicyExtensionManager(object):

    def get_resources(self):
        return ext_epp.Endpointpolicy.get_resources()

    def get_actions(self):
        return []

    def get_request_extensions(self):
        return []


class EndpointPolicyTestCase(test_pg.PLUMgridPluginV2TestCase):
    def setUp(self, plugin=None, ext_mgr=None):
        super(EndpointPolicyTestCase, self).setUp()
        ext_mgr = EndpointPolicyExtensionManager()
        extensions.PluginAwareExtensionManager._instance = None
        self.ext_api = test_ext.setup_extensions_middleware(ext_mgr)


class TestEndpointPolicy(EndpointPolicyTestCase):
    def test_create_endpoint_policy(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epp = self._make_epp_dict(epg_ret["id"])
        epp_ret = plugin.create_endpoint_policy(admin_context,
                                                epp)
        epp["endpoint_policy"]["id"] = epp_ret["id"]
        self.assertEqual(epp_ret, epp["endpoint_policy"])

    def test_create_endpoint_policy_service_epg_name(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epp = self._make_epp_dict(epg_ret["name"])
        epp_ret = plugin.create_endpoint_policy(admin_context,
                                                epp)
        epp["endpoint_policy"]["id"] = epp_ret["id"]
        self.assertEqual(epp_ret, epp["endpoint_policy"])

    def test_create_endpoint_policy_with_name(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epp = self._make_epp_dict(epg_ret["id"], name="fake_policy")
        epp_ret = plugin.create_endpoint_policy(admin_context,
                                                epp)
        epp["endpoint_policy"]["id"] = epp_ret["id"]
        self.assertEqual(epp_ret, epp["endpoint_policy"])

    def test_create_endpoint_policy_with_src_grp(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        src_epg = self._make_epg_dict(epg_type="vm_class")

        src_epg_ret = plugin.create_endpoint_group(
                      admin_context, src_epg)
        epp = self._make_epp_dict(epg_ret["id"], src_grp=src_epg_ret["id"])
        epp_ret = plugin.create_endpoint_policy(admin_context,
                                                epp)
        epp["endpoint_policy"]["id"] = epp_ret["id"]
        self.assertEqual(epp_ret, epp["endpoint_policy"])

    def test_create_endpoint_policy_with_src_grp_name(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        src_epg = self._make_epg_dict(epg_type="vm_class", name="src_grp")

        src_epg_ret = plugin.create_endpoint_group(
                      admin_context, src_epg)
        epp = self._make_epp_dict(epg_ret["id"], src_grp=src_epg_ret["name"])
        epp_ret = plugin.create_endpoint_policy(admin_context,
                                                epp)
        epp["endpoint_policy"]["id"] = epp_ret["id"]
        self.assertEqual(epp_ret, epp["endpoint_policy"])

    def test_create_endpoint_policy_with_dst_grp(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        dst_epg = self._make_epg_dict(epg_type="vm_class")

        dst_epg_ret = plugin.create_endpoint_group(
                      admin_context, dst_epg)
        epp = self._make_epp_dict(epg_ret["id"], dst_grp=dst_epg_ret["id"])
        epp_ret = plugin.create_endpoint_policy(admin_context,
                                                epp)
        epp["endpoint_policy"]["id"] = epp_ret["id"]
        self.assertEqual(epp_ret, epp["endpoint_policy"])

    def test_create_endpoint_policy_with_dst_grp_name(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        dst_epg = self._make_epg_dict(epg_type="vm_class", name="dst_grp")

        dst_epg_ret = plugin.create_endpoint_group(
                      admin_context, dst_epg)
        epp = self._make_epp_dict(epg_ret["id"], dst_grp=dst_epg_ret["name"])
        epp_ret = plugin.create_endpoint_policy(admin_context,
                                                epp)
        epp["endpoint_policy"]["id"] = epp_ret["id"]
        self.assertEqual(epp_ret, epp["endpoint_policy"])

    def test_create_endpoint_policy_with_protocol_tcp(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epp = self._make_epp_dict(epg_ret["id"], protocol="tcp")
        epp_ret = plugin.create_endpoint_policy(admin_context,
                                                epp)
        epp["endpoint_policy"]["id"] = epp_ret["id"]
        self.assertEqual(epp_ret, epp["endpoint_policy"])

    def test_create_endpoint_policy_with_protocol_udp(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epp = self._make_epp_dict(epg_ret["id"], protocol="udp")
        epp_ret = plugin.create_endpoint_policy(admin_context,
                                                epp)
        epp["endpoint_policy"]["id"] = epp_ret["id"]
        self.assertEqual(epp_ret, epp["endpoint_policy"])

    def test_create_endpoint_policy_with_protocol_icmp(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epp = self._make_epp_dict(epg_ret["id"], protocol="icmp")
        epp_ret = plugin.create_endpoint_policy(admin_context,
                                                epp)
        epp["endpoint_policy"]["id"] = epp_ret["id"]
        self.assertEqual(epp_ret, epp["endpoint_policy"])

    def test_create_endpoint_policy_with_src_port_range(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epp = self._make_epp_dict(epg_ret["id"], src_port_range="1-65535")
        epp_ret = plugin.create_endpoint_policy(admin_context,
                                                epp)
        epp["endpoint_policy"]["id"] = epp_ret["id"]
        self.assertEqual(epp_ret, epp["endpoint_policy"])

    def test_create_endpoint_policy_with_dst_port_range(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epp = self._make_epp_dict(epg_ret["id"], dst_port_range="1-65535")
        epp_ret = plugin.create_endpoint_policy(admin_context,
                                                epp)
        epp["endpoint_policy"]["id"] = epp_ret["id"]
        self.assertEqual(epp_ret, epp["endpoint_policy"])

    def test_create_endpoint_policy_with_all_config(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        class_epg = self._make_epg_dict(epg_type="vm_class")

        class_epg_ret = plugin.create_endpoint_group(
                      admin_context, class_epg)
        epp = self._make_epp_dict(epg_ret["id"], dst_grp=class_epg_ret["id"],
                                  src_grp=class_epg_ret["id"],
                                  name="fake_policy",
                                  protocol="tcp", src_port_range="1-65535",
                                  dst_port_range="1-65535")
        epp_ret = plugin.create_endpoint_policy(admin_context,
                                                epp)
        epp["endpoint_policy"]["id"] = epp_ret["id"]
        self.assertEqual(epp_ret, epp["endpoint_policy"])

    def test_create_endpoint_policy_with_service_src_grp(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epp = self._make_epp_dict(epg_ret["id"], src_grp=epg_ret["id"])
        self.assertRaises(ext_epp.InvalidEndpointGroupForPolicy,
                          plugin.create_endpoint_policy, admin_context, epp)

    def test_create_endpoint_policy_with_service_dst_grp(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epp = self._make_epp_dict(epg_ret["id"], dst_grp=epg_ret["id"])
        self.assertRaises(ext_epp.InvalidEndpointGroupForPolicy,
                          plugin.create_endpoint_policy, admin_context, epp)

    def test_create_endpoint_policy_with_invalid_service_epg_id(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epp = self._make_epp_dict(str(uuid.uuid4()))
        self.assertRaises(ext_epp.NoEndpointGroupFound,
                          plugin.create_endpoint_policy, admin_context, epp)

    def test_create_endpoint_policy_with_invalid_src_grp_id(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epp = self._make_epp_dict(epg_ret["id"], src_grp=str(uuid.uuid4()))
        self.assertRaises(ext_epp.NoEndpointGroupFound,
                          plugin.create_endpoint_policy, admin_context, epp)

    def test_create_endpoint_policy_with_invalid_dst_grp_id(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epp = self._make_epp_dict(epg_ret["id"], dst_grp=str(uuid.uuid4()))
        self.assertRaises(ext_epp.NoEndpointGroupFound,
                          plugin.create_endpoint_policy, admin_context, epp)

    def test_create_endpoint_policy_with_invalid_service_epg_name(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epp = self._make_epp_dict("fake_service_epg")
        self.assertRaises(p_excep.PLUMgridException,
                          plugin.create_endpoint_policy, admin_context, epp)

    def test_create_endpoint_policy_with_invalid_src_grp_name(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epp = self._make_epp_dict(epg_ret["id"], src_grp="fake_src_grp")
        self.assertRaises(p_excep.PLUMgridException,
                          plugin.create_endpoint_policy, admin_context, epp)

    def test_create_endpoint_policy_with_invalid_dst_grp_name(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epp = self._make_epp_dict(epg_ret["id"], dst_grp="fake_dst_grp")
        self.assertRaises(p_excep.PLUMgridException,
                          plugin.create_endpoint_policy, admin_context, epp)

    def test_create_endpoint_policy_with_invalid_protocol(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epp = self._make_epp_dict(epg_ret["id"], protocol="fake-protocol")
        self.assertRaises(epp_excep.UnsupportedProtocol,
                          plugin.create_endpoint_policy, admin_context, epp)

    def test_create_endpoint_policy_with_invalid_action(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epp = self._make_epp_dict(epg_ret["id"], action="fake-action")
        self.assertRaises(epp_excep.UnsupportedAction,
                          plugin.create_endpoint_policy, admin_context, epp)

    def test_create_endpoint_policy_with_invalid_service_epg_type(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict(epg_type="vm_class")

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epp = self._make_epp_dict(epg_ret["id"])
        self.assertRaises(ext_epp.InvalidEndpointGroupForPolicy,
                          plugin.create_endpoint_policy, admin_context, epp)

    def test_create_endpoint_policy_with_invalid_src_port_range_syntax(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epp = self._make_epp_dict(epg_ret["id"],
                                  src_port_range="invalid_range")
        self.assertRaises(ext_epp.EndpointPolicyInvalidPortRange,
                          plugin.create_endpoint_policy, admin_context, epp)

    def test_create_endpoint_policy_with_invalid_dst_port_range_syntax(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epp = self._make_epp_dict(epg_ret["id"],
                                  dst_port_range="invalid_range")
        self.assertRaises(ext_epp.EndpointPolicyInvalidPortRange,
                          plugin.create_endpoint_policy, admin_context, epp)

    def test_create_endpoint_policy_with_invalid_src_port_range(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epp = self._make_epp_dict(epg_ret["id"], src_port_range="100-1")
        self.assertRaises(ext_epp.EndpointPolicyInvalidPortRange,
                          plugin.create_endpoint_policy, admin_context, epp)

    def test_create_endpoint_policy_with_invalid_dst_port_range(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epp = self._make_epp_dict(epg_ret["id"], dst_port_range="100-1")
        self.assertRaises(ext_epp.EndpointPolicyInvalidPortRange,
                          plugin.create_endpoint_policy, admin_context, epp)

    def test_create_endpoint_policy_with_src_port_range_icmp(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epp = self._make_epp_dict(epg_ret["id"], protocol="icmp",
                                  src_port_range="1-100")
        self.assertRaises(epp_excep.NotSupportedPortRangeICMP,
                          plugin.create_endpoint_policy, admin_context, epp)

    def test_create_endpoint_policy_with_src_grp_duplicate_name(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        src_epg1 = self._make_epg_dict(epg_type="vm_class", name="src_grp")

        src_epg_ret1 = plugin.create_endpoint_group(
                      admin_context, src_epg1)
        src_epg2 = self._make_epg_dict(epg_type="vm_class", name="src_grp")

        plugin.create_endpoint_group(admin_context, src_epg2)
        epp = self._make_epp_dict(epg_ret["id"], src_grp=src_epg_ret1["name"])
        self.assertRaises(p_excep.PLUMgridException,
                          plugin.create_endpoint_policy, admin_context, epp)

    def test_create_endpoint_policy_with_dst_grp_duplicate_name(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        dst_epg1 = self._make_epg_dict(epg_type="vm_class", name="dst_grp")

        dst_epg_ret1 = plugin.create_endpoint_group(
                      admin_context, dst_epg1)
        dst_epg2 = self._make_epg_dict(epg_type="vm_class", name="dst_grp")

        plugin.create_endpoint_group(admin_context, dst_epg2)
        epp = self._make_epp_dict(epg_ret["id"], src_grp=dst_epg_ret1["name"])
        self.assertRaises(p_excep.PLUMgridException,
                          plugin.create_endpoint_policy, admin_context, epp)

    def test_create_delete_endpoint_policy(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epp = self._make_epp_dict(epg_ret["id"])
        epp_ret = plugin.create_endpoint_policy(admin_context,
                                                epp)
        resp = plugin.delete_endpoint_policy(admin_context, epp_ret["id"])
        self.assertEqual(None, resp)

    def test_create_delete_endpoint_policy_does_not_exist(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        self.assertRaises(ext_epp.NoEndpointPolicyFound,
                          plugin.delete_endpoint_policy,
                          admin_context, "fake-epp")

    def test_create_get_endpoint_policy(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epp = self._make_epp_dict(epg_ret["id"])
        epp_ret = plugin.create_endpoint_policy(admin_context,
                                                epp)
        epp_get_ret = plugin.get_endpoint_policy(admin_context,
                                                 epp_ret["id"])
        self.assertEqual(epp_ret, epp_get_ret)

    def test_create_list_endpoint_policies(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epp1 = self._make_epp_dict(epg_ret["id"], protocol="tcp")
        epp_ret1 = plugin.create_endpoint_policy(admin_context,
                                                 epp1)
        epp2 = self._make_epp_dict(epg_ret["id"], protocol="udp")
        epp_ret2 = plugin.create_endpoint_policy(admin_context,
                                                 epp2)
        epp3 = self._make_epp_dict(epg_ret["id"], protocol="icmp")
        epp_ret3 = plugin.create_endpoint_policy(admin_context,
                                                 epp3)
        epp_list_ret = plugin.get_endpoint_policies(admin_context)
        self.assertItemsEqual(epp_list_ret, [epp_ret1, epp_ret2, epp_ret3])

    def _make_epg_dict(self, name="test_name", epg_type="vm_ep",
                       ports=[]):
        return {"endpoint_group": {
                   "tenant_id": "test_tenant",
                   "name": name,
                   "description": "test_description",
                   "endpoint_type": epg_type,
                   "ports": ports}}

    def _make_epp_dict(self, service_epg, name="test_policy", src_grp=None,
                       dst_grp=None, action="copy", protocol="any",
                       src_port_range=None, dst_port_range=None):
        return {"endpoint_policy": {
                   "tenant_id": "test_tenant",
                   "name": name,
                   "src_grp": src_grp,
                   "dst_grp": dst_grp,
                   "action": action,
                   "src_port_range": src_port_range,
                   "dst_port_range": dst_port_range,
                   "protocol": protocol,
                   "service_endpoint_group": service_epg}}
