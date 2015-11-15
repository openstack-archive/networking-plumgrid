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
Transit domain extension unit tests
"""

from networking_plumgrid.neutron.plugins.extensions import \
    transitdomain as ext_tvd
from networking_plumgrid.neutron.tests.unit import \
    test_networking_plumgrid as test_pg

from neutron.api import extensions
from neutron import context
from neutron import manager
from neutron.tests.unit.api import test_extensions as test_ext
from oslo_log import log as logging

LOG = logging.getLogger(__name__)


class TransitDomainExtensionManager(object):

    def get_resources(self):
        return ext_tvd.Transitdomain.get_resources()

    def get_actions(self):
        return []

    def get_request_extensions(self):
        return []


class TransitDomainTestCase(test_pg.PLUMgridPluginV2TestCase):
    def setUp(self, plugin=None, ext_mgr=None):
        super(TransitDomainTestCase, self).setUp()
        ext_mgr = TransitDomainExtensionManager()
        extensions.PluginAwareExtensionManager._instance = None
        self.ext_api = test_ext.setup_extensions_middleware(ext_mgr)


class TestTransitDomain(TransitDomainTestCase):
    def test_create_transit_domain(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        tvd = {"transit_domain": {
                   "tenant_id": "admin",
                   "name": "test_name"}}

        tvd_ret = plugin.create_transit_domain(
                      admin_context, tvd)
        tvd["transit_domain"]["id"] = tvd_ret["id"]
        self.assertEqual(tvd_ret, tvd["transit_domain"])

    def test_update_transit_domain(self):
        #TODO(shahbazn) To be implemented
        pass

    def test_get_transit_domain(self):
        #TODO(shahbazn) To be implemented
        pass

    def test_delete_transit_domain(self):
        #TODO(shahbazn) To be implemented
        pass

    def test_create_update_get_delete_pap01(self):
        #TODO(shahbazn) To be implemented
        pass

    def test_list_transit_domain(self):
        #TODO(shahbazn) To be implemented
        pass
