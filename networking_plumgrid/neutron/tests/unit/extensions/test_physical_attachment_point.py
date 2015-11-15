# Copyright (c) 2015 Thales Services SAS
# All Rights Reserved.
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


from networking_plumgrid.neutron import plugin as plumgrid_plugin

from neutron import context
from neutron import manager
from neutron.tests.unit.db import test_db_base_plugin_v2 as test_plugin

import mock
from oslo_utils import importutils

PLUM_DRIVER = ('networking_plumgrid.neutron.drivers.'
               'fake_plumlib.Plumlib')
FAKE_DIRECTOR = '1.1.1.1'
FAKE_PORT = '1234'
FAKE_USERNAME = 'fake_admin'
FAKE_PASSWORD = 'fake_password'
FAKE_TIMEOUT = '0'


class PhysicalAttachmentPointTestCase(test_plugin.NeutronDbPluginV2TestCase):
    _plugin_name = ('networking_plumgrid.neutron.'
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
            super(PhysicalAttachmentPointTestCase,
                  self).setUp(self._plugin_name)

    def tearDown(self):
        super(PhysicalAttachmentPointTestCase, self).tearDown()


class TestPhysicalAttachmentPoint(PhysicalAttachmentPointTestCase):
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
        self.assertEqual(pap_ret, pap["physical_attachment_point"])

    def test_create_update_pap01(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        pap = {"physical_attachment_point": {
                   "tenant_id": "test_tenant",
                   "name": "test_name",
                   "hash_mode": "L2",
                   "lacp": True,
                   "interfaces": [
                       {"hostname": "test_host", "interface": "ifc"}]}}

        with plugin.create_physical_attachment_point(
                 admin_context, pap) as pap_old:
            pap_new = {"physical_attachment_point": {
                           "tenant_id": "test_tenant",
                           "name": "new_name",
                           "hash_mode": "L2+L3",
                           "lacp": True,
                           "interfaces": [
                               {"hostname": "test_host", "interface": "ifc"}]}}

            pap_new_ret = plugin.update_physical_attachment_point(
                              admin_context, pap_old["id"], pap_new)
            self.assertEqual(pap_new_ret, pap_new["physical_attachment_point"])

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

        with plugin.create_physical_attachment_point(
                 admin_context, pap) as pap_old:
            pap_new = {"physical_attachment_point": {
                            "tenant_id": "test_tenant",
                            "name": "new_name",
                            "hash_mode": "L2+L3",
                            "lacp": True,
                            "interfaces": []}}

            pap_new_ret = plugin.update_physical_attachment_point(
                              admin_context, pap_old["id"], pap_new)
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

        with plugin.create_physical_attachment_point(
                 admin_context, pap) as pap_ret:
            pap_get_ret = plugin.get_physical_attachment_point(
                              admin_context, pap_ret["id"])
            self.assertEqual(pap_get_ret, pap_ret["physical_attachment_point"])
