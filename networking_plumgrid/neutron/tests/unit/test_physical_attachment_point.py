"""
PLUMgrid plugin physical attachment point extension unit tests
"""

import mock
from oslo_utils import importutils

from networking_plumgrid.neutron import plugin as plumgrid_plugin
from networking_plumgrid.neutron.extensions import physical_attachment_point as pg_pap

from neutron import manager
from neutron import context
from neutron.tests.unit import testlib_api
from neutron.tests.unit.db import test_db_base_plugin_v2 as test_plugin

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
            super(PhysicalAttachmentPointTestCase, self).setUp(self._plugin_name)

    def tearDown(self):
        super(PhysicalAttachmentPointTestCase, self).tearDown()


class TestPhysicalAttachmentPoint(PhysicalAttachmentPointTestCase):
    def test_create_pap01(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        pap = { "physical_attachment_point": {
                    "tenant_id": "test_tenant",
                    "name": "test_name",
                    "hash_mode": "L2",
                    "lacp": True,
                    "interfaces": [{"hostname": "test_host", "interface": "ifc"}]
                }
              }
        ret = plugin.create_physical_attachment_point(admin_context, pap)
        self.assertEqual(ret, pap["physical_attachment_point"])

    def test_create_update_pap01(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        pap_id = "93687ac5-74cc-45f6-85e1-984a17629d49"
        pap = { "physical_attachment_point": {
                    "tenant_id": "test_tenant",
                    "name": "test_name",
                    "hash_mode": "L2",
                    "lacp": True,
                    "interfaces": [{"hostname": "test_host", "interface": "ifc"}]
                }
              }

        with plugin.create_physical_attachment_point(admin_context, pap) as pap_old:
            pap_new = { "physical_attachment_point": {
                            "tenant_id": "test_tenant",
                            "name": "new_name",
                            "hash_mode": "L2+L3",
                            "lacp": True,
                            "interfaces": [{"hostname": "test_host", "interface": "ifc"}]
                            }
                      } 
            self.assertEqual(plugin.update_physical_attachment_point(admin_context, pap_old["id"], pap_new), pap_new["physical_attachment_point"])

    def test_create_update_pap01(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        pap = { "physical_attachment_point": {
                    "tenant_id": "test_tenant",
                    "name": "test_name",
                    "hash_mode": "L2",
                    "lacp": True,
                    "interfaces": [{"hostname": "test_host", "interface": "ifc"}]
                }
              }

        with plugin.create_physical_attachment_point(admin_context, pap) as pap_old:
            pap_new = { "physical_attachment_point": {
                            "tenant_id": "test_tenant",
                            "name": "new_name",
                            "hash_mode": "L2+L3",
                            "lacp": True,
                            "interfaces": [{"hostname": "test_host", "interface": "ifc"}]
                            }
                      } 
            self.assertEqual(plugin.get_physical_attachment_point(admin_context, pap_old["id"], pap_new), pap_new["physical_attachment_point"])

    def test_create_get_pap01(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        pap = { "physical_attachment_point": {
                    "tenant_id": "test_tenant",
                    "name": "test_name",
                    "hash_mode": "L2",
                    "lacp": True,
                    "interfaces": [{"hostname": "test_host", "interface": "ifc"}]
                }
              }

        with plugin.create_physical_attachment_point(admin_context, pap) as pap_ret:
            self.assertEqual(plugin.get_physical_attachment_point(admin_context, pap_ret["id"]), pap_ret["physical_attachment_point"])
