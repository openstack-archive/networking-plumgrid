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

from networking_plumgrid.neutron.extensions import \
    physical_attachment_point as ext_pap
from networking_plumgrid.neutron.tests.unit import \
    test_networking_plumgrid as test_pg
from neutron import context
from neutron import manager
from neutron.api import extensions
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


class PhyAttPTestCase(test_pg.PLUMgridPluginV2TestCase):
    def setUp(self, plugin=None, ext_mgr=None):
        super(PhyAttPTestCase, self).setUp()
        ext_mgr = PAPExtensionManager()
        extensions.PluginAwareExtensionManager._instance = None
        self.ext_api = test_ext.setup_extensions_middleware(ext_mgr)


class TestPhysicalAttachmentPoint(PhyAttPTestCase):
    def test_create_pap01(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        pap = {"physical_attachment_point": {
                   "tenant_id": "test_tenant",
                   "name": "test_name",
                   "hash_mode": "L2",
                   "lacp": True,
                   "interfaces": [
                       {"hostname": "test_host", "interface": "ifc"}]}}

        pap_ret = plugin.create_physical_attachment_point(
                      admin_context, pap)
        pap["physical_attachment_point"]["id"] = pap_ret["id"]
        self.assertEqual(pap_ret, pap["physical_attachment_point"])

    def test_create_update_get_pap01(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        pap = {"physical_attachment_point": {
                   "tenant_id": "test_tenant",
                   "name": "test_name",
                   "hash_mode": "L2",
                   "lacp": True,
                   "interfaces": [
                       {"hostname": "test_host", "interface": "ifc"}]}}

        pap_old = plugin.create_physical_attachment_point(
                      admin_context, pap)
        pap_new = {"physical_attachment_point": {
                           "tenant_id": "test_tenant",
                           "name": "new_name",
                           "hash_mode": "L2+L3",
                           "lacp": False,
                           "interfaces": [
                               {"hostname": "test_host", "interface": "ifc"}]}}

        pap_new_ret = plugin.update_physical_attachment_point(
                              admin_context, pap_old["id"], pap_new)
        pap_new_get = plugin.get_physical_attachment_point(
                              admin_context, pap_old["id"])
        self.assertEqual(pap_new_ret, pap_new_get)

    def test_create_update_pap02(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        pap = {"physical_attachment_point": {
                   "tenant_id": "test_tenant",
                   "name": "test_name",
                   "hash_mode": "L2",
                   "lacp": True,
                   "interfaces": [
                       {"hostname": "test_host", "interface": "ifc"}]}}

        pap_old = plugin.create_physical_attachment_point(
                      admin_context, pap)
        pap_new = {"physical_attachment_point": {
                       "tenant_id": "test_tenant",
                       "name": "new_name",
                       "hash_mode": "L2+L3",
                       "lacp": False,
                       "interfaces": []}}

        pap_new_ret = plugin.update_physical_attachment_point(
                          admin_context, pap_old["id"], pap_new)
        pap_new["physical_attachment_point"]["id"] = pap_new_ret["id"]
        self.assertEqual(pap_new_ret, pap_new["physical_attachment_point"])

    def test_create_get_pap01(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        pap = {"physical_attachment_point": {
                   "tenant_id": "test_tenant",
                   "name": "test_name",
                   "hash_mode": "L2",
                   "lacp": True,
                   "interfaces": [
                       {"hostname": "test_host", "interface": "ifc"}]}}
        pap_ret = plugin.create_physical_attachment_point(
                      admin_context, pap)
        pap_get_ret = plugin.get_physical_attachment_point(
                          admin_context, pap_ret["id"])
        self.assertEqual(pap_get_ret, pap_ret)

    def test_create_delete_pap01(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        pap = {"physical_attachment_point": {
                   "tenant_id": "test_tenant",
                   "name": "test_name",
                   "hash_mode": "L2",
                   "lacp": True,
                   "interfaces": [
                       {"hostname": "test_host", "interface": "ifc"},
                       {"hostname": "test_host", "interface": "ifc"}]}}
        pap_ret = plugin.create_physical_attachment_point(
                      admin_context, pap)
        plugin.delete_physical_attachment_point(
                          admin_context, pap_ret["id"])

    def test_create_delete_pap02(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        pap = {"physical_attachment_point": {
                   "tenant_id": "test_tenant",
                   "name": "test_name",
                   "hash_mode": "L2",
                   "lacp": True,
                   "interfaces": []}}
        pap_ret = plugin.create_physical_attachment_point(
                      admin_context, pap)
        plugin.delete_physical_attachment_point(
                          admin_context, pap_ret["id"])

    def test_create_update_get_delete_pap01(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        pap = {"physical_attachment_point": {
                   "tenant_id": "test_tenant",
                   "name": "test_name",
                   "hash_mode": "L2",
                   "lacp": True,
                   "interfaces": [
                       {"hostname": "test_host", "interface": "ifc"}]}}

        pap_old = plugin.create_physical_attachment_point(
                      admin_context, pap)
        pap_new = {"physical_attachment_point": {
                        "tenant_id": "test_tenant",
                        "name": "new_name",
                        "hash_mode": "L2+L3",
                        "lacp": True,
                        "interfaces": [
                            {"hostname": "test_host", "interface": "ifc"},
                            {"hostname": "test_host", "interface": "ifc"}]}}
        pap_new_ret = plugin.update_physical_attachment_point(
                              admin_context, pap_old["id"], pap_new)
        pap_get_ret = plugin.get_physical_attachment_point(
                          admin_context, pap_new_ret["id"])
        self.assertEqual(pap_get_ret, pap_new_ret)
        plugin.delete_physical_attachment_point(
            admin_context, pap_get_ret["id"])

    def test_get_all(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        pap_1 = {"physical_attachment_point": {
                   "tenant_id": "test_tenant",
                   "name": "test_name",
                   "hash_mode": "L2",
                   "lacp": True,
                   "interfaces": [
                       {"hostname": "test_host", "interface": "ifc"}]}}

        pap_1_ret = plugin.create_physical_attachment_point(
                      admin_context, pap_1)
        pap_2 = {"physical_attachment_point": {
                     "tenant_id": "test_tenant",
                     "name": "new_name",
                     "hash_mode": "L2+L3",
                     "lacp": True,
                     "interfaces": [
                         {"hostname": "test_host", "interface": "ifc"},
                         {"hostname": "test_host", "interface": "ifc"}]}}
        pap_2_ret = plugin.create_physical_attachment_point(
                              admin_context, pap_2)
        
        pap_list_get = plugin.get_physical_attachment_points(
                          admin_context)
        self.assertEqual(pap_list_get, [pap_1_ret, pap_2_ret])
