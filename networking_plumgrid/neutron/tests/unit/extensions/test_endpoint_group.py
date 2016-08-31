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
Endpoint Group extension unit tests
"""
from networking_plumgrid.neutron.plugins.common import \
    exceptions as p_excep
from networking_plumgrid.neutron.plugins.extensions import \
    endpointgroup
from networking_plumgrid.neutron.tests.unit import \
    test_networking_plumgrid as test_pg

from neutron.api import extensions
from neutron import context
from neutron import manager
from neutron.tests.unit.api import test_extensions as test_ext
from oslo_log import log as logging

LOG = logging.getLogger(__name__)


class EndpointGroupExtensionManager(object):

    def get_resources(self):
        return endpointgroup.Endpointgroup.get_resources()

    def get_actions(self):
        return []

    def get_request_extensions(self):
        return []


class EndpointGroupTestCase(test_pg.PLUMgridPluginV2TestCase):
    def setUp(self, plugin=None, ext_mgr=None):
        super(EndpointGroupTestCase, self).setUp()
        ext_mgr = EndpointGroupExtensionManager()
        extensions.PluginAwareExtensionManager._instance = None
        self.ext_api = test_ext.setup_extensions_middleware(ext_mgr)


class TestEndpointGroup(EndpointGroupTestCase):
    def test_create_endpoint_group(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epg["endpoint_group"]["id"] = epg_ret["id"]
        self.assertEqual(epg_ret, epg["endpoint_group"])

    def test_create_endpoint_group_with_policy_tag(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        ptag = self._fake_policy_tag_dict()
        ptag_ret = plugin.create_policy_tag(admin_context, ptag)
        ptag["policy_tag"]["id"] = ptag_ret["id"]

        epg = self._make_epg_dict(ptag_id=ptag_ret["id"])

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epg["endpoint_group"]["id"] = epg_ret["id"]
        self.assertEqual(epg_ret, epg["endpoint_group"])

    def test_create_endpoint_group_with_invalid_policy_tag(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        ptag = self._fake_policy_tag_dict()
        ptag_ret = plugin.create_policy_tag(admin_context, ptag)
        ptag["policy_tag"]["id"] = ptag_ret["id"]

        epg = self._make_epg_dict(ptag_id="abcdef123")

        self.assertRaises(p_excep.PLUMgridException,
                          plugin.create_endpoint_group, admin_context, epg)

    def test_create_endpoint_group_with_in_use_policy_tag(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        ptag = self._fake_policy_tag_dict()
        ptag_ret = plugin.create_policy_tag(admin_context, ptag)
        ptag["policy_tag"]["id"] = ptag_ret["id"]

        # Create first endpoint group with policy tag
        epg1 = self._make_epg_dict(ptag_id=ptag_ret["id"])
        epg_ret1 = plugin.create_endpoint_group(
                      admin_context, epg1)
        epg1["endpoint_group"]["id"] = epg_ret1["id"]

        # Create a second endpoint group with same policy tag
        epg2 = self._make_epg_dict(ptag_id=ptag_ret["id"])
        epg_ret2 = plugin.create_endpoint_group(
                      admin_context, epg2)
        epg2["endpoint_group"]["id"] = epg_ret2["id"]
        self.assertEqual(epg_ret1, epg1["endpoint_group"])
        self.assertEqual(epg_ret2, epg2["endpoint_group"])

    def test_create_delete_endpoint_group(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        ptag = self._fake_policy_tag_dict()
        ptag_ret = plugin.create_policy_tag(admin_context, ptag)
        ptag["policy_tag"]["id"] = ptag_ret["id"]

        epg = self._make_epg_dict(ptag_id=ptag_ret["id"])

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epg["endpoint_group"]["id"] = epg_ret["id"]

        resp = plugin.delete_endpoint_group(admin_context, epg_ret["id"])
        self.assertEqual(None, resp)

    def test_create_update_endpoint_group(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        ptag = self._fake_policy_tag_dict()
        ptag_ret = plugin.create_policy_tag(admin_context, ptag)
        ptag["policy_tag"]["id"] = ptag_ret["id"]

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epg["endpoint_group"]["id"] = epg_ret["id"]

        epg_update_dict = self._make_epg_update_dict(name="updated-epg-name",
                                            add_tag=ptag["policy_tag"]["id"])
        epg_update_ret = plugin.update_endpoint_group(admin_context,
                                                      epg_ret["id"],
                                                      epg_update_dict)
        epg_update_dict["endpoint_group"]["id"] = epg_update_ret["id"]
        self.assertEqual(epg_update_dict["endpoint_group"], epg_update_ret)

    def test_create_update_security_group_with_policy_tag(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        ptag = self._fake_policy_tag_dict()
        ptag_ret = plugin.create_policy_tag(admin_context, ptag)
        ptag["policy_tag"]["id"] = ptag_ret["id"]

        # Create security group
        sg = self._fake_sg()
        sg_ret = plugin.create_security_group(admin_context, sg)

        sg_update_dict = self._make_sg_update_dict(
                                             add_tag=ptag["policy_tag"]["id"])

        sg_update_ret = plugin.update_endpoint_group(admin_context,
                                                     sg_ret["id"],
                                                     sg_update_dict)

        sg_update_dict["endpoint_group"]["id"] = sg_update_ret["id"]
        (sg_update_dict["endpoint_group"]
         ["description"]) = sg_update_ret["description"]
        sg_update_dict["endpoint_group"]["name"] = sg_update_ret["name"]
        (sg_update_dict["endpoint_group"]
         ["is_security_group"]) = sg_update_ret["is_security_group"]
        (sg_update_dict["endpoint_group"]
         ["policy_tag_id"]) = sg_update_ret["policy_tag_id"]
        (sg_update_dict["endpoint_group"]
         ["remove_tag"]) = sg_update_ret["remove_tag"]
        self.assertEqual(sg_update_dict["endpoint_group"], sg_update_ret)

    def test_list_all_endpoint_groups(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        # Create first endpoint group
        epg1 = self._make_epg_dict()
        epg_ret1 = plugin.create_endpoint_group(
                      admin_context, epg1)
        epg1["endpoint_group"]["id"] = epg_ret1["id"]

        # Create second endpoint group
        ptag = self._fake_policy_tag_dict()
        ptag_ret = plugin.create_policy_tag(admin_context, ptag)
        ptag["policy_tag"]["id"] = ptag_ret["id"]

        epg2 = self._make_epg_dict(ptag_id=ptag_ret["id"])

        epg_ret2 = plugin.create_endpoint_group(
                      admin_context, epg2)
        epg2["endpoint_group"]["id"] = epg_ret2["id"]

        # List both endpoint groups
        epg_list_ret = plugin.get_endpoint_groups(admin_context)
        self.assertItemsEqual(epg_list_ret, [epg_ret1, epg_ret2])

    def _make_epg_dict(self, ptag_id=None,
                       name="test_sg_name"):

        epg_dict = {"endpoint_group": {
                   "tenant_id": "test_tenant",
                   "name": name,
                   "description": "test_description",
                   "is_security_group": False}}
        if ptag_id is not None:
            epg_dict["endpoint_group"]["policy_tag_id"] = ptag_id
        return epg_dict

    def _make_epg_update_dict(self, name="test_tenant",
                              description="test_description",
                              add_tag=[],
                              remove_tag=[]):
        return {"endpoint_group": {
                   "tenant_id": "test_tenant",
                   "name": name,
                   "description": description,
                   "add_tag": add_tag,
                   "remove_tag": remove_tag,
                   "is_security_group": False,
                   "policy_tag_id": None}}

    def _make_sg_update_dict(self, add_tag=[],
                             remove_tag=[]):
        sg_dict = {"endpoint_group": {
                   "tenant_id": "test_tenant"}}
        if len(add_tag) != 0:
            sg_dict["endpoint_group"]["add_tag"] = add_tag
        if len(remove_tag) != 0:
            sg_dict["endpoint_group"]["remove_tag"] = remove_tag
        return sg_dict

    def _fake_policy_tag_dict(self):
        return {"policy_tag": {
                               "tenant_id": "test_tenant",
                               "name": "test_name",
                               "tag_type": "dot1q",
                               "tag_id": "10-20",
                               "floatingip_id": None,
                               "floating_ip_address": None,
                               "router_id": None}}

    def _fake_sg(self):
        return {"security_group": {"name": "fake-sg",
                                   "description": "test_description",
                                   "tenant_id": "test_tenant"}}
