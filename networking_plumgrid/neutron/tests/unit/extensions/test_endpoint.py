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
Endpoint extension unit tests
"""
from networking_plumgrid.neutron.plugins.common import \
    exceptions as p_excep
from networking_plumgrid.neutron.plugins.common import \
    policy_exceptions as policy_excep
from networking_plumgrid.neutron.plugins.extensions import \
    endpoint
from networking_plumgrid.neutron.tests.unit import \
    test_networking_plumgrid as test_pg

from neutron.api import extensions
from neutron.api.v2 import attributes
from neutron.common import exceptions as n_excep
from neutron import context
from neutron import manager
from neutron.tests.unit.api import test_extensions as test_ext
from oslo_log import log as logging
import uuid

LOG = logging.getLogger(__name__)


class EndpointExtensionManager(object):

    def get_resources(self):
        return endpoint.Endpoint.get_resources()

    def get_actions(self):
        return []

    def get_request_extensions(self):
        return []


class EndpointTestCase(test_pg.PLUMgridPluginV2TestCase):
    def setUp(self, plugin=None, ext_mgr=None):
        super(EndpointTestCase, self).setUp()
        ext_mgr = EndpointExtensionManager()
        extensions.PluginAwareExtensionManager._instance = None
        self.ext_api = test_ext.setup_extensions_middleware(ext_mgr)


class TestEndpoint(EndpointTestCase):
    def test_create_endpoint(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        ep = self._make_ep_dict()

        ep_ret = plugin.create_endpoint(
                      admin_context, ep)
        ep["endpoint"]["id"] = ep_ret["id"]
        self.assertEqual(ep_ret, ep["endpoint"])

    def test_create_endpoint_with_port(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)

        ep = self._make_ep_dict(port_id=port_ret["id"])

        ep_ret = plugin.create_endpoint(
                      admin_context, ep)
        ep["endpoint"]["id"] = ep_ret["id"]
        self.assertEqual(ep_ret, ep["endpoint"])

    def test_create_endpoint_with_epg(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id

        epg = self._make_epg_dict()
        epg_ret = plugin.create_endpoint_group(admin_context, epg)

        ep = self._make_ep_dict(ep_groups=[{"id": epg_ret["id"]}])

        ep_ret = plugin.create_endpoint(
                      admin_context, ep)
        ep["endpoint"]["id"] = ep_ret["id"]
        self.assertEqual(ep_ret, ep["endpoint"])

    def test_create_endpoint_with_multiple_epg(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id

        epg1 = self._make_epg_dict()
        epg_ret1 = plugin.create_endpoint_group(admin_context, epg1)

        epg2 = self._make_epg_dict(name="test_epg_name2")
        epg_ret2 = plugin.create_endpoint_group(admin_context, epg2)

        ep = self._make_ep_dict(ep_groups=[{"id": epg_ret1["id"]},
                                           {"id": epg_ret2["id"]}])

        ep_ret = plugin.create_endpoint(
                      admin_context, ep)
        ep["endpoint"]["id"] = ep_ret["id"]
        # TO-DO: FIXME(Muneeb)
        #self.assertEqual(ep_ret, ep["endpoint"])

    def test_create_endpoint_with_ip_port(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id

        ep = self._make_ep_dict(ip_port="10.10.1.0:128/7")

        ep_ret = plugin.create_endpoint(
                      admin_context, ep)
        ep["endpoint"]["id"] = ep_ret["id"]
        self.assertEqual(ep_ret, ep["endpoint"])

    def test_create_endpoint_with_ip_mask(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id

        ep = self._make_ep_dict(ip_mask="10.10.1.0/24")

        ep_ret = plugin.create_endpoint(
                      admin_context, ep)
        ep["endpoint"]["id"] = ep_ret["id"]
        self.assertEqual(ep_ret, ep["endpoint"])

    def test_create_endpoint_no_name(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        ep = self._make_ep_dict()
        ep["endpoint"]["name"] = None
        ep_ret = plugin.create_endpoint(
                      admin_context, ep)
        ep["endpoint"]["id"] = ep_ret["id"]
        self.assertEqual(ep_ret, ep["endpoint"])

    def test_create_endpoint_with_non_existing_port(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        port_id = str(uuid.uuid4())
        ep = self._make_ep_dict(port_id=port_id)

        self.assertRaises(n_excep.PortNotFound,
                          plugin.create_endpoint, admin_context, ep)

    def test_create_endpoint_with_non_existing_epg(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id

        ep = self._make_ep_dict(ep_groups=[{"id": "test-epg-1"}])

        self.assertRaises(p_excep.PLUMgridException,
                          plugin.create_endpoint, admin_context, ep)

    def test_create_endpoint_with_port_invalid_device_owner(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"], device_owner="fake:owner")
        port_ret = plugin.create_port(
                      admin_context, port)
        ep = self._make_ep_dict(port_id=port_ret["id"])
        self.assertRaises(policy_excep.InvalidPortForEndpoint,
                          plugin.create_endpoint, admin_context, ep)

    def test_create_endpoint_with_invalid_port_name(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        ep = self._make_ep_dict(port_id="invalid_fake_port")
        self.assertRaises(p_excep.PLUMgridException,
                          plugin.create_endpoint, admin_context, ep)

    def test_create_delete_endpoint(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        ep = self._make_ep_dict()

        ep_ret = plugin.create_endpoint(
                      admin_context, ep)
        resp = plugin.delete_endpoint(admin_context, ep_ret["id"])
        self.assertEqual(None, resp)

    def test_delete_endpoint_does_not_exist(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        self.assertRaises(endpoint.NoEndpointFound,
                          plugin.delete_endpoint, admin_context,
                          str(uuid.uuid4()))

    def test_create_update_endpoint_name(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        ep = self._make_ep_dict()

        ep_ret = plugin.create_endpoint(
                      admin_context, ep)
        ep_update_dict = self._make_ep_update_dict(name=
                                                   "updated_ep_name")
        ep_update_ret = plugin.update_endpoint(admin_context,
                                               ep_ret["id"],
                                               ep_update_dict)
        ep_update_dict["endpoint"]["id"] = ep_update_ret["id"]
        ep_update_dict["endpoint"]["ip_port"] = ep_update_ret["ip_port"]
        ep_update_dict["endpoint"]["ip_mask"] = ep_update_ret["ip_mask"]
        ep_update_dict["endpoint"]["port_id"] = ep_update_ret["port_id"]
        ep_update_dict["endpoint"]["ep_groups"] = ep_update_ret["ep_groups"]
        self.assertEqual(ep_update_dict["endpoint"], ep_update_ret)

    def test_create_update_endpoint_add_epg(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id

        # Create endpoint group
        epg = self._make_epg_dict()
        epg_ret = plugin.create_endpoint_group(admin_context, epg)

        ep = self._make_ep_dict()
        ep_ret = plugin.create_endpoint(
                      admin_context, ep)

        ep_update_dict = self._make_ep_update_dict(
                                              add_epg=[{"id": epg_ret["id"]}])

        ep_update_ret = plugin.update_endpoint(admin_context,
                                               ep_ret["id"],
                                               ep_update_dict)

        ep_get_ret = plugin.get_endpoint(admin_context, ep_ret["id"])

        self.assertEqualUpdate(ep_get_ret, ep_update_ret)

    #def test_create_update_endpoint_remove_epg(self):
        # TO-DO: FIXME(Muneeb)
        #plugin = manager.NeutronManager.get_plugin()
        #admin_context = context.get_admin_context()
        #tenant_context = context.Context('', 'not_admin')

        #network = self._fake_network()
        #network["network"]["tenant_id"] = tenant_context.tenant_id

        # Create endpoint group
        #epg = self._make_epg_dict()
        #epg_ret = plugin.create_endpoint_group(admin_context, epg)

        #ep = self._make_ep_dict(ep_groups=[{"id": epg_ret["id"]}])

        #ep_ret = plugin.create_endpoint(
        #              admin_context, ep)

        #ep_update_dict = self._make_ep_update_dict(
        #                                   remove_epg=[{"id": epg_ret["id"]}])

        #ep_update_ret = plugin.update_endpoint(admin_context,
        #                                       ep_ret["id"],
        #                                       ep_update_dict)

        #ep_get_ret = plugin.get_endpoint(admin_context, ep_ret["id"])

        #self.assertEqualUpdate(ep_update_ret, ep_get_ret)

    def test_list_all_endpoints(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        ep1 = self._make_ep_dict()
        ep_ret1 = plugin.create_endpoint(
                      admin_context, ep1)

        ep2 = self._make_ep_dict()
        ep_ret2 = plugin.create_endpoint(
                      admin_context, ep2)

        ep3 = self._make_ep_dict()
        ep_ret3 = plugin.create_endpoint(
                      admin_context, ep3)

        ep_list_ret = plugin.get_endpoints(admin_context)
        self.assertItemsEqual(ep_list_ret, [ep_ret1, ep_ret2, ep_ret3])

    def _make_ep_dict(self,
                      name="test_ep_name",
                      ip_mask=None,
                      ip_port=None,
                      port_id=None,
                      ep_groups=[]):
        ep_dict = {"endpoint": {
                   "tenant_id": "test_tenant",
                   "name": name,
                   "ip_mask": ip_mask,
                   "ip_port": ip_port,
                   "port_id": port_id,
                   "ep_groups": ep_groups}}

        if port_id is not None:
            ep_dict["endpoint"]["port_id"] = port_id
        return ep_dict

    def _make_ep_update_dict(self, name="test_tenant",
                             description="test_description",
                             add_epg=[],
                             remove_epg=[]):
        return {"endpoint": {
                   "tenant_id": "test_tenant",
                   "name": name,
                   "add_endpoint_groups": add_epg,
                   "remove_endpoint_groups": remove_epg}}

    def _make_epg_dict(self, ptag_id=None,
                       name="test_epg_name"):

        epg_dict = {"endpoint_group": {
                   "tenant_id": "test_tenant",
                   "name": name,
                   "description": "test_description",
                   "is_security_group": False}}
        if ptag_id is not None:
            epg_dict["endpoint_group"]["policy_tag_id"] = ptag_id
        return epg_dict

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

    def _fake_port(self, net_id, security_groups = [],
                   device_owner="compute:nova"):
        return {'port': {'name': 'fake_port',
                         'network_id': net_id,
                         'mac_address': attributes.ATTR_NOT_SPECIFIED,
                         'fixed_ips': attributes.ATTR_NOT_SPECIFIED,
                         'admin_state_up': True,
                         'device_id': 'fake_device_id',
                         'device_owner': device_owner,
                         'tenant_id': "fake_tenant",
                         'security_group': security_groups}}

    def assertEqualUpdate(self, ep_ref, ep_actual):
        def make_ep_dict(ep_db):
            if "add_endpoint_groups" in ep_db:
                del ep_db["add_endpoint_groups"]
            if "remove_endpoint_groups" in ep_db:
                del ep_db["remove_endpoint_groups"]
            return ep_db

        ep_ref = make_ep_dict(ep_ref)
        ep_actual = make_ep_dict(ep_actual)
        return self.assertEqual(ep_ref, ep_actual)
