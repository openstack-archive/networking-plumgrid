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
PLUMgrid plugin physical attachment point extension unit tests
"""

from networking_plumgrid.neutron.plugins.common import \
    exceptions as plum_excep
from networking_plumgrid.neutron.plugins.extensions import \
    physical_attachment_point as ext_pap
from networking_plumgrid.neutron.tests.unit import \
    test_networking_plumgrid as test_pg
from neutron.api import extensions
from neutron import context
from neutron import manager
from neutron.tests.unit.api import test_extensions as test_ext
from oslo_log import log as logging

LOG = logging.getLogger(__name__)


class PAPExtensionManager(object):

    def get_resources(self):
        return ext_pap.Physical_attachment_point.get_resources()

    def get_actions(self):
        return []

    def get_request_extensions(self):
        return []


class PhysicalAttachmentPointTestCase(test_pg.PLUMgridPluginV2TestCase):
    def setUp(self, plugin=None, ext_mgr=None):
        super(PhysicalAttachmentPointTestCase, self).setUp()
        ext_mgr = PAPExtensionManager()
        extensions.PluginAwareExtensionManager._instance = None
        self.ext_api = test_ext.setup_extensions_middleware(ext_mgr)


class TestPhysicalAttachmentPoint(PhysicalAttachmentPointTestCase):
    def test_create_pap(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        interfaces = [{"hostname": "h1", "interface": "ifc1"}]
        tid = self._create_transit_domain(admin_context, plugin)
        pap = self._make_pap_dict(interfaces=interfaces,
                                  transit_domain_id=tid["id"])
        pap_ret = plugin.create_physical_attachment_point(
                      admin_context, pap)
        pap["physical_attachment_point"]["id"] = pap_ret["id"]
        self.assertEqual(pap_ret, pap["physical_attachment_point"])

    def test_create_pap_without_td(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        interfaces = [{"hostname": "h1", "interface": "ifc1"}]
        pap = self._make_pap_dict(interfaces=interfaces)
        LOG.error(pap)
        pap_ret = plugin.create_physical_attachment_point(
                      admin_context, pap)
        pap["physical_attachment_point"]["id"] = pap_ret["id"]
        self.assertEqual(pap_ret, pap["physical_attachment_point"])

    def test_create_pap_with_td_name(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        interfaces = [{"hostname": "h1", "interface": "ifc1"}]
        tid = self._create_transit_domain(admin_context, plugin)
        pap = self._make_pap_dict(interfaces=interfaces,
                                  transit_domain_id=tid["name"])
        pap_ret = plugin.create_physical_attachment_point(
                      admin_context, pap)
        pap["physical_attachment_point"]["id"] = pap_ret["id"]
        self.assertEqual(pap_ret, pap["physical_attachment_point"])

    def test_create_pap_lacp_true_hash_L2(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        interfaces = [{"hostname": "h1", "interface": "ifc1"}]
        tid = self._create_transit_domain(admin_context, plugin)
        pap = self._make_pap_dict(interfaces=interfaces, lacp=True,
                                  transit_domain_id=tid["id"])
        pap_ret = plugin.create_physical_attachment_point(
                      admin_context, pap)
        pap["physical_attachment_point"]["id"] = pap_ret["id"]
        self.assertEqual(pap_ret, pap["physical_attachment_point"])

    def test_create_pap_lacp_false_hash_not_L2(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        interfaces = [{"hostname": "h1", "interface": "ifc1"}]
        tid = self._create_transit_domain(admin_context, plugin)
        pap = self._make_pap_dict(interfaces=interfaces, lacp='False',
                  hash_mode="L3", transit_domain_id=tid["id"])
        self.assertRaises(plum_excep.PLUMgridException,
            plugin.create_physical_attachment_point,
            admin_context, pap)

    def test_create_pap_no_interfaces(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tid = self._create_transit_domain(admin_context, plugin)
        pap = self._make_pap_dict(transit_domain_id=tid["id"])
        pap_ret = plugin.create_physical_attachment_point(
                      admin_context, pap)
        pap["physical_attachment_point"]["id"] = pap_ret["id"]
        self.assertEqual(pap_ret, pap["physical_attachment_point"])

    def test_create_pap_multi_interfaces(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        interfaces = [{"hostname": "test_host1", "interface": "ifc1"},
                      {"hostname": "test_host1", "interface": "ifc1"}]
        tid = self._create_transit_domain(admin_context, plugin)
        pap = self._make_pap_dict(interfaces=interfaces,
                  transit_domain_id=tid["id"])
        pap_ret = plugin.create_physical_attachment_point(
                      admin_context, pap)
        pap["physical_attachment_point"]["id"] = pap_ret["id"]
        self.assertEqual(pap_ret, pap["physical_attachment_point"])

    def test_create_pap_max_hosts(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        interfaces = [{"hostname": "h%d" % i, "interface": "ifc%d" % j}
                      for i in range(1, 16) for j in range(1, 2)]
        tid = self._create_transit_domain(admin_context, plugin)
        pap = self._make_pap_dict(interfaces=interfaces,
                  transit_domain_id=tid["id"])
        pap_ret = plugin.create_physical_attachment_point(
                      admin_context, pap)
        pap["physical_attachment_point"]["id"] = pap_ret["id"]
        self.assertEqual(pap_ret, pap["physical_attachment_point"])

    def test_create_update_show_pap01(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        tid = self._create_transit_domain(admin_context, plugin)
        pap = self._make_pap_dict(transit_domain_id=tid["id"])
        pap_old = plugin.create_physical_attachment_point(
                      admin_context, pap)
        add_interfaces = [{"hostname": "test_host", "interface": "ifc"}]
        pap_new = self._make_pap_update_dict(add_interfaces=add_interfaces,
                                             transit_domain_id=tid["id"])

        pap_new_ret = plugin.update_physical_attachment_point(
                              admin_context, pap_old["id"], pap_new)
        pap_new_get = plugin.get_physical_attachment_point(
                              admin_context, pap_old["id"])

        pap["physical_attachment_point"]["id"] = pap_old["id"]
        self.assertEqualUpdate(pap_old, pap["physical_attachment_point"])
        self.assertEqualUpdate(pap_new_ret, pap_new_get)

    def test_create_update_show_pap02(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        interfaces = [{"hostname": "h1", "interface": "ifc1"},
                      {"hostname": "h2", "interface": "ifc1"}]
        tid = self._create_transit_domain(admin_context, plugin)
        pap = self._make_pap_dict(interfaces=interfaces,
                                  transit_domain_id=tid["id"])
        pap_old = plugin.create_physical_attachment_point(
                      admin_context, pap)
        pap_new = self._make_pap_update_dict(remove_interfaces=interfaces,
                                             transit_domain_id=tid["id"])
        pap_new_ret = plugin.update_physical_attachment_point(
                              admin_context, pap_old["id"], pap_new)
        pap_new_get = plugin.get_physical_attachment_point(
                              admin_context, pap_old["id"])
        pap["physical_attachment_point"]["id"] = pap_old["id"]
        self.assertEqualUpdate(pap_old, pap["physical_attachment_point"])
        self.assertEqualUpdate(pap_new_ret, pap_new_get)

    def test_create_update_show_pap03(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        interfaces = [{"hostname": "h1", "interface": "ifc1"}]
        tid = self._create_transit_domain(admin_context, plugin)
        pap = self._make_pap_dict(interfaces=interfaces,
                                  transit_domain_id=tid["id"])
        pap_old = plugin.create_physical_attachment_point(
                      admin_context, pap)

        add_interfaces = [{"hostname": "h1", "interface": "ifc2"},
                      {"hostname": "h2", "interface": "ifc1"}]
        pap_new = self._make_pap_update_dict(add_interfaces=add_interfaces,
                                             transit_domain_id=tid["id"])
        pap_new_ret = plugin.update_physical_attachment_point(
                              admin_context, pap_old["id"], pap_new)
        pap_new_get = plugin.get_physical_attachment_point(
                              admin_context, pap_old["id"])
        pap["physical_attachment_point"]["id"] = pap_old["id"]
        self.assertEqual(pap_old, pap["physical_attachment_point"])
        self.assertEqualUpdate(pap_new_ret, pap_new_get)

    def test_create_show_pap_by_uuid(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        interfaces = [{"hostname": "h1", "interface": "ifc1"},
                      {"hostname": "h2", "interface": "ifc2"},
                      {"hostname": "h2", "interface": "ifc2"}]
        tid = self._create_transit_domain(admin_context, plugin)
        pap = self._make_pap_dict(interfaces=interfaces,
                                  transit_domain_id=tid["id"])
        pap_ret = plugin.create_physical_attachment_point(
                      admin_context, pap)
        pap_get_ret = plugin.get_physical_attachment_point(
                          admin_context, pap_ret["id"])
        self.assertEqual(pap_get_ret, pap_ret)

    def test_create_show_pap_by_uuid_no_ifcs(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        tid = self._create_transit_domain(admin_context, plugin)
        pap = self._make_pap_dict(transit_domain_id=tid["id"])
        pap_ret = plugin.create_physical_attachment_point(
                      admin_context, pap)
        pap_get_ret = plugin.get_physical_attachment_point(
                          admin_context, pap_ret["id"])
        self.assertEqual(pap_get_ret, pap_ret)

    def test_create_delete_pap_multi_ifcs(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        interfaces = [{"hostname": "h1", "interface": "ifc1"},
                      {"hostname": "h2", "interface": "ifc2"},
                      {"hostname": "h2", "interface": "ifc2"}]
        tid = self._create_transit_domain(admin_context, plugin)
        pap = self._make_pap_dict(interfaces=interfaces,
                                  transit_domain_id=tid["id"])
        pap_ret = plugin.create_physical_attachment_point(
                      admin_context, pap)
        plugin.delete_physical_attachment_point(
                          admin_context, pap_ret["id"])

    def test_create_delete_pap_no_ifcs(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        tid = self._create_transit_domain(admin_context, plugin)
        pap = self._make_pap_dict(transit_domain_id=tid["id"])
        pap_ret = plugin.create_physical_attachment_point(
                      admin_context, pap)
        plugin.delete_physical_attachment_point(
                          admin_context, pap_ret["id"])

    def test_create_update_get_delete_pap01(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        interfaces = [{"hostname": "h1", "interface": "ifc1"},
                      {"hostname": "h2", "interface": "ifc1"}]
        tid = self._create_transit_domain(admin_context, plugin)
        pap = self._make_pap_dict(interfaces=interfaces,
                                  transit_domain_id=tid["id"])
        pap_old = plugin.create_physical_attachment_point(
                      admin_context, pap)

        add_interfaces = [{"hostname": "h2", "interface": "ifc2"}]
        pap_new = self._make_pap_update_dict(add_interfaces=add_interfaces,
                                             transit_domain_id=tid["id"])
        pap_new_ret = plugin.update_physical_attachment_point(
                              admin_context, pap_old["id"], pap_new)
        pap_get_ret = plugin.get_physical_attachment_point(
                          admin_context, pap_new_ret["id"])
        self.assertEqualUpdate(pap_get_ret, pap_new_ret)
        plugin.delete_physical_attachment_point(
            admin_context, pap_get_ret["id"])

    def test_get_all(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        interfaces = [{"hostname": "h1", "interface": "ifc1"},
                      {"hostname": "h2", "interface": "ifc2"}]
        tid1 = self._create_transit_domain(admin_context, plugin)
        pap_1 = self._make_pap_dict(interfaces=interfaces,
                                    transit_domain_id=tid1["id"])
        pap_1_ret = plugin.create_physical_attachment_point(
                      admin_context, pap_1)

        interfaces = [{"hostname": "h1", "interface": "ifc2"},
                      {"hostname": "h1", "interface": "ifc3"},
                      {"hostname": "h1", "interface": "ifc4"}]
        tid2 = self._create_transit_domain(admin_context, plugin)
        pap_2 = self._make_pap_dict(interfaces=interfaces,
                                    transit_domain_id=tid2["id"])
        pap_2_ret = plugin.create_physical_attachment_point(
                              admin_context, pap_2)
        pap_list_get = plugin.get_physical_attachment_points(
                          admin_context)
        cmp(pap_list_get, [pap_1_ret, pap_2_ret])

    def _make_pap_dict(self, lacp=False, hash_mode="L2",
                       transit_domain_id=None,
                       interfaces=[]):
        return {"physical_attachment_point": {
                   "tenant_id": "test_tenant",
                   "name": "test_name",
                   "hash_mode": hash_mode,
                   "lacp": lacp,
                   "implicit": False,
                   "transit_domain_id": transit_domain_id,
                   "interfaces": interfaces}}

    def _make_pap_update_dict(self, lacp=False, hash_mode="L2",
                              transit_domain_id="test_id",
                              add_interfaces=[], remove_interfaces=[]):
        return {"physical_attachment_point": {
                   "tenant_id": "test_tenant",
                   "name": "test_name",
                   "hash_mode": hash_mode,
                   "lacp": lacp,
                   "implicit": False,
                   "transit_domain_id": transit_domain_id,
                   "add_interfaces": add_interfaces,
                   "remove_interfaces": remove_interfaces}}

    def _create_transit_domain(self, admin_context, plugin):
        td = {"transit_domain": {
                  "tenant_id": "test_tenant",
                  "name": "td",
                  "implicit": False}}
        res = plugin.create_transit_domain(admin_context, td)
        return res

    def _update_interfaces(self, **kwargs):
        interfaces = kwargs.pop("interfaces", [])
        add_interfaces = kwargs.pop("add_interfaces", [])
        remove_interfaces = kwargs.pop("remove_interfaces", [])

        interfaces.extend(add_interfaces)
        for interface in remove_interfaces:
            interfaces = interfaces.remove(interface)

        if not interfaces:
            interfaces = []
        return interfaces

    def assertEqualUpdate(self, pap_ref, pap_actual):
        def make_pap_dict(pap_db):
            if "add_interfaces" in pap_db:
                del pap_db["add_interfaces"]
            if "remove_interfaces" in pap_db:
                del pap_db["remove_interfaces"]
            return pap_db

        pap_ref = make_pap_dict(pap_ref)
        pap_actual = make_pap_dict(pap_actual)
        return self.assertEqual(pap_ref, pap_actual)
