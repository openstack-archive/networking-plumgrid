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
    endpoint as ext_ep
from networking_plumgrid.neutron.tests.unit import \
    test_networking_plumgrid as test_pg

from neutron.api import extensions
from neutron.api.v2 import attributes
from neutron import context
from neutron import manager
from neutron.tests.unit.api import test_extensions as test_ext
from oslo_log import log as logging
import uuid

LOG = logging.getLogger(__name__)


class EndpointExtensionManager(object):

    def get_resources(self):
        return ext_ep.Endpoint.get_resources()

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
    def test_create_endpoint_with_ip_mask(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        ep = self._make_ep_dict(ip_mask='0.0.0.0/0',
                                ep_groups=[{'id': epg_ret['id']}])
        ep_ret = plugin.create_endpoint(admin_context, ep)
        ep["endpoint"]["id"] = ep_ret["id"]
        self.assertEqual(ep_ret, ep["endpoint"])

    def test_create_endpoint_with_ip_port_mask(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        ep = self._make_ep_dict(ip_port='1.1.1.1_100_8',
                                ep_groups=[{'id': epg_ret['id']}])
        ep_ret = plugin.create_endpoint(admin_context, ep)
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

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        ep = self._make_ep_dict(port=port_ret["id"],
                                ep_groups=[{'id': epg_ret['id']}])
        ep_ret = plugin.create_endpoint(admin_context, ep)
        ep["endpoint"]["id"] = ep_ret["id"]
        self.assertEqual(ep_ret, ep["endpoint"])

    def test_create_endpoint_with_ip_mask_epg_name(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        ep = self._make_ep_dict(ip_mask='0.0.0.0/0',
                                ep_groups=[{'id': epg_ret['name']}])
        ep_ret = plugin.create_endpoint(admin_context, ep)
        ep["endpoint"]["id"] = ep_ret["id"]
        self.assertEqual(ep_ret, ep["endpoint"])

    def test_create_endpoint_with_ip_port_mask_epg_name(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        ep = self._make_ep_dict(ip_port='1.1.1.1_100_8',
                                ep_groups=[{'id': epg_ret['name']}])
        ep_ret = plugin.create_endpoint(admin_context, ep)
        ep["endpoint"]["id"] = ep_ret["id"]
        self.assertEqual(ep_ret, ep["endpoint"])

    def test_create_endpoint_with_port_epg_name(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        ep = self._make_ep_dict(port=port_ret["id"],
                                ep_groups=[{'id': epg_ret['name']}])
        ep_ret = plugin.create_endpoint(admin_context, ep)
        ep["endpoint"]["id"] = ep_ret["id"]
        self.assertEqual(ep_ret, ep["endpoint"])

    def test_create_endpoint_with_port_and_epg_name(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        ep = self._make_ep_dict(port=port_ret["name"],
                                ep_groups=[{'id': epg_ret['name']}])
        ep_ret = plugin.create_endpoint(admin_context, ep)
        ep["endpoint"]["id"] = ep_ret["id"]
        self.assertEqual(ep_ret, ep["endpoint"])

    def test_create_endpoint_with_ip_mask_and_ip_port(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        ep = self._make_ep_dict(ip_mask='0.0.0.0/0',
                                ip_port="1.1.1.1_100_8",
                                ep_groups=[{'id': epg_ret['id']}])
        self.assertRaises(policy_excep.MultipleAssociationForEndpoint,
                          plugin.create_endpoint, admin_context, ep)

    def test_create_endpoint_with_port_and_ip_mask(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        ep = self._make_ep_dict(port=port_ret["id"],
                                ip_mask='0.0.0.0/0',
                                ep_groups=[{'id': epg_ret['id']}])
        self.assertRaises(policy_excep.MultipleAssociationForEndpoint,
                          plugin.create_endpoint, admin_context, ep)

    def test_create_endpoint_with_port_and_ip_port(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        ep = self._make_ep_dict(port=port_ret["id"],
                                ip_port='1.1.1.1_100_8',
                                ep_groups=[{'id': epg_ret['id']}])
        self.assertRaises(policy_excep.MultipleAssociationForEndpoint,
                          plugin.create_endpoint, admin_context, ep)

    def test_create_endpoint_with_duplicate_epg(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        ep = self._make_ep_dict(port=port_ret["id"],
                                ep_groups=[{'id': epg_ret['id']},
                                {'id': epg_ret['id']}])
        self.assertRaises(policy_excep.DuplicateEndpointGroup,
                          plugin.create_endpoint, admin_context, ep)

    def test_create_endpoint_with_security_group(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        sg = self._fake_sg()

        sg_ret = plugin.create_security_group(admin_context, sg)
        ep = self._make_ep_dict(ip_mask='0.0.0.0/0',
                                ep_groups=[{'id': sg_ret['id']}])
        ep_ret = plugin.create_endpoint(admin_context, ep)
        ep["endpoint"]["id"] = ep_ret["id"]
        self.assertEqual(ep_ret, ep["endpoint"])

    def test_create_endpoint_non_existent_port(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(admin_context, epg)
        ep = self._make_ep_dict(port='fake-port',
                                ep_groups=[{'id': epg_ret['id']}])
        self.assertRaises(p_excep.PLUMgridException,
                          plugin.create_endpoint, admin_context, ep)

    def test_create_endpoint_port_owner_not_nova(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"], device_owner="not:nova")
        port_ret = plugin.create_port(
                      admin_context, port)

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        ep = self._make_ep_dict(port=port_ret["id"],
                                ep_groups=[{'id': epg_ret['id']}])
        self.assertRaises(policy_excep.InvalidPortForEndpoint,
                          plugin.create_endpoint, admin_context, ep)

    def test_create_endpoint_port_in_use(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        ep1 = self._make_ep_dict(port=port_ret["id"],
                                 ep_groups=[{'id': epg_ret['id']}])
        plugin.create_endpoint(admin_context, ep1)
        ep2 = self._make_ep_dict(name="test_ep2",
                                 port=port_ret["id"],
                                 ep_groups=[{'id': epg_ret['id']}])
        self.assertRaises(ext_ep.PortInUse,
                          plugin.create_endpoint, admin_context, ep2)

    def test_create_endpoint_invalid_epg(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)

        ep = self._make_ep_dict(port=port_ret["id"],
                                ep_groups=[{'id': str(uuid.uuid4())}])
        self.assertRaises(ext_ep.NoEndpointGroupFound,
                          plugin.create_endpoint, admin_context, ep)

    def test_delete_endpoint_ip_mask(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        ep = self._make_ep_dict(ip_mask='0.0.0.0/0',
                                ep_groups=[{'id': epg_ret['id']}])
        ep_ret = plugin.create_endpoint(admin_context, ep)
        resp = plugin.delete_endpoint(admin_context, ep_ret["id"])
        self.assertEqual(None, resp)

    def test_delete_endpoint_ip_port(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        ep = self._make_ep_dict(ip_port='1.1.1.1_100_8',
                                ep_groups=[{'id': epg_ret['id']}])
        ep_ret = plugin.create_endpoint(admin_context, ep)
        resp = plugin.delete_endpoint(admin_context, ep_ret["id"])
        self.assertEqual(None, resp)

    def test_delete_endpoint_port(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        ep = self._make_ep_dict(port=port_ret["id"],
                                ep_groups=[{'id': epg_ret['id']}])
        ep_ret = plugin.create_endpoint(admin_context, ep)
        resp = plugin.delete_endpoint(admin_context, ep_ret["id"])
        self.assertEqual(None, resp)

    def test_delete_endpoint_does_not_exist(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        self.assertRaises(ext_ep.NoEndpointFound,
                          plugin.delete_endpoint, admin_context,
                          str(uuid.uuid4()))

    def test_list_endpoints(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        ep1 = self._make_ep_dict(ip_mask='0.0.0.0/0',
                                 ep_groups=[{'id': epg_ret['id']}])
        ep_ret1 = plugin.create_endpoint(admin_context, ep1)
        ep2 = self._make_ep_dict(ip_mask='1.0.0.0/0',
                                 ep_groups=[{'id': epg_ret['id']}])
        ep_ret2 = plugin.create_endpoint(admin_context, ep2)
        ep3 = self._make_ep_dict(ip_mask='2.0.0.0/0',
                                 ep_groups=[{'id': epg_ret['id']}])
        ep_ret3 = plugin.create_endpoint(admin_context, ep3)

        ep_list_ret = plugin.get_endpoints(admin_context)
        self.assertItemsEqual(ep_list_ret, [ep_ret1, ep_ret2, ep_ret3])

    def test_create_update_endpoint_name(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        ep = self._make_ep_dict(ip_mask='0.0.0.0/0',
                                ep_groups=[{'id': epg_ret['id']}])
        ep_ret = plugin.create_endpoint(admin_context, ep)
        ep_update = self._make_ep_update_dict(name="update_ep_name")
        ep_update_ret = plugin.update_endpoint(admin_context,
                                               ep_ret["id"], ep_update)
        self._consolidate_update_config(ep_update, ep_update_ret)
        self.assertEqual(ep_update["endpoint"], ep_update_ret)

    def test_create_update_endpoint_add_epg(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg1 = self._make_epg_dict()

        epg_ret1 = plugin.create_endpoint_group(
                      admin_context, epg1)
        ep = self._make_ep_dict(ip_mask='0.0.0.0/0',
                                ep_groups=[{'id': epg_ret1['id']}])
        epg2 = self._make_epg_dict(name="test_epg2")

        epg_ret2 = plugin.create_endpoint_group(
                      admin_context, epg2)
        ep_ret = plugin.create_endpoint(admin_context, ep)
        ep_update = self._make_ep_update_dict(add_ep_groups=
                                              [{"id": epg_ret2['id']}])
        ep_update_ret = plugin.update_endpoint(admin_context,
                                               ep_ret["id"], ep_update)
        self._consolidate_update_config(ep_update, ep_update_ret)
        self.assertEqual(ep_update["endpoint"], ep_update_ret)

    def test_create_update_endpoint_remove_epg(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg1 = self._make_epg_dict()

        epg_ret1 = plugin.create_endpoint_group(
                      admin_context, epg1)
        ep = self._make_ep_dict(ip_mask='0.0.0.0/0',
                                ep_groups=[{'id': epg_ret1['id']}])
        ep_ret = plugin.create_endpoint(admin_context, ep)
        ep_update = self._make_ep_update_dict(remove_ep_groups=
                                              [{"id": epg_ret1['id']}])
        ep_update_ret = plugin.update_endpoint(admin_context,
                                               ep_ret["id"], ep_update)
        self._consolidate_update_config(ep_update, ep_update_ret)
        self.assertEqual(ep_update["endpoint"], ep_update_ret)

    def test_create_update_endpoint_add_epg_name(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg1 = self._make_epg_dict()

        epg_ret1 = plugin.create_endpoint_group(
                      admin_context, epg1)
        ep = self._make_ep_dict(ip_mask='0.0.0.0/0',
                                ep_groups=[{'id': epg_ret1['id']}])
        epg2 = self._make_epg_dict(name="test_epg2")

        epg_ret2 = plugin.create_endpoint_group(
                      admin_context, epg2)
        ep_ret = plugin.create_endpoint(admin_context, ep)
        ep_update = self._make_ep_update_dict(add_ep_groups=
                                              [{"id": epg_ret2['name']}])
        ep_update_ret = plugin.update_endpoint(admin_context,
                                               ep_ret["id"], ep_update)
        self._consolidate_update_config(ep_update, ep_update_ret)
        self.assertEqual(ep_update["endpoint"], ep_update_ret)

    def test_create_update_endpoint_remove_epg_name(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg1 = self._make_epg_dict()

        epg_ret1 = plugin.create_endpoint_group(
                      admin_context, epg1)
        ep = self._make_ep_dict(ip_mask='0.0.0.0/0',
                                ep_groups=[{'id': epg_ret1['id']}])
        ep_ret = plugin.create_endpoint(admin_context, ep)
        ep_update = self._make_ep_update_dict(remove_ep_groups=
                                              [{"id": epg_ret1['name']}])
        ep_update_ret = plugin.update_endpoint(admin_context,
                                               ep_ret["id"], ep_update)
        self._consolidate_update_config(ep_update, ep_update_ret)
        self.assertEqual(ep_update["endpoint"], ep_update_ret)

    def test_create_update_endpoint_add_duplicate_epg(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg1 = self._make_epg_dict()

        epg_ret1 = plugin.create_endpoint_group(
                      admin_context, epg1)
        ep = self._make_ep_dict(ip_mask='0.0.0.0/0',
                                ep_groups=[{'id': epg_ret1['id']}])
        epg2 = self._make_epg_dict(name="test_epg2")

        epg_ret2 = plugin.create_endpoint_group(
                      admin_context, epg2)
        ep_ret = plugin.create_endpoint(admin_context, ep)
        ep_update = self._make_ep_update_dict(add_ep_groups=
                                              [{"id": epg_ret2['id']},
                                              {"id": epg_ret2['id']}])
        self.assertRaises(policy_excep.DuplicateEndpointGroup,
                          plugin.update_endpoint, admin_context,
                          ep_ret["id"], ep_update)

    def test_create_update_endpoint_remove_duplicate_epg(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg1 = self._make_epg_dict()

        epg_ret1 = plugin.create_endpoint_group(
                      admin_context, epg1)
        ep = self._make_ep_dict(ip_mask='0.0.0.0/0',
                                ep_groups=[{'id': epg_ret1['id']}])
        ep_ret = plugin.create_endpoint(admin_context, ep)
        ep_update = self._make_ep_update_dict(remove_ep_groups=
                                              [{"id": epg_ret1['id']},
                                              {"id": epg_ret1['id']}])
        self.assertRaises(policy_excep.DuplicateEndpointGroup,
                          plugin.update_endpoint, admin_context,
                          ep_ret["id"], ep_update)

    def test_create_update_endpoint_add_remove_dup_epg(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg1 = self._make_epg_dict()

        epg_ret1 = plugin.create_endpoint_group(
                      admin_context, epg1)
        ep = self._make_ep_dict(ip_mask='0.0.0.0/0',
                                ep_groups=[{'id': epg_ret1['id']}])
        epg2 = self._make_epg_dict(name="test_epg2")

        epg_ret2 = plugin.create_endpoint_group(
                      admin_context, epg2)
        ep_ret = plugin.create_endpoint(admin_context, ep)
        ep_update = self._make_ep_update_dict(add_ep_groups=
                                              [{"id": epg_ret2['id']}],
                                              remove_ep_groups=
                                              [{"id": epg_ret2["id"]}])
        self.assertRaises(policy_excep.DuplicateEndpointGroup,
                          plugin.update_endpoint, admin_context,
                          ep_ret["id"], ep_update)

    def test_create_update_endpoint_add_sg(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg1 = self._make_epg_dict()

        epg_ret1 = plugin.create_endpoint_group(
                      admin_context, epg1)
        ep = self._make_ep_dict(ip_mask='0.0.0.0/0',
                                ep_groups=[{'id': epg_ret1['id']}])
        ep_ret = plugin.create_endpoint(admin_context, ep)
        sg = self._fake_sg()

        sg_ret = plugin.create_security_group(admin_context, sg)
        ep_update = self._make_ep_update_dict(add_ep_groups=
                                              [{"id": sg_ret['id']}])
        ep_update_ret = plugin.update_endpoint(admin_context, ep_ret["id"],
                                               ep_update)
        self._consolidate_update_config(ep_update, ep_update_ret)
        self.assertEqual(ep_update["endpoint"], ep_update_ret)

    def test_create_update_endpoint_remove_sg(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg1 = self._make_epg_dict()

        epg_ret1 = plugin.create_endpoint_group(
                      admin_context, epg1)
        ep = self._make_ep_dict(ip_mask='0.0.0.0/0',
                                ep_groups=[{'id': epg_ret1['id']}])
        ep_ret = plugin.create_endpoint(admin_context, ep)
        sg = self._fake_sg()

        sg_ret = plugin.create_security_group(admin_context, sg)
        ep_update = self._make_ep_update_dict(remove_ep_groups=
                                              [{"id": sg_ret['id']}])
        ep_update_ret = plugin.update_endpoint(admin_context, ep_ret["id"],
                                               ep_update)
        self._consolidate_update_config(ep_update, ep_update_ret)
        self.assertEqual(ep_update["endpoint"], ep_update_ret)

    def test_create_update_endpoint_delete_port_bw(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        ep = self._make_ep_dict(port=port_ret["id"],
                                ep_groups=[{'id': epg_ret['id']}])
        ep_ret = plugin.create_endpoint(admin_context, ep)
        plugin.delete_port(admin_context, port_ret["id"])
        ep_update = self._make_ep_update_dict(name="update_ep_name")
        self.assertRaises(ext_ep.NoEndpointFound,
                          plugin.update_endpoint, admin_context,
                          ep_ret["id"], ep_update)

    def test_create_update_get_endpoint_name(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        ep = self._make_ep_dict(ip_mask='0.0.0.0/0',
                                ep_groups=[{'id': epg_ret['id']}])
        ep_ret = plugin.create_endpoint(admin_context, ep)
        ep_update = self._make_ep_update_dict(name="update_ep_name")
        ep_update_ret = plugin.update_endpoint(admin_context,
                                               ep_ret["id"], ep_update)
        ep_get_ret = plugin.get_endpoint(admin_context, ep_ret["id"])
        self.assertEqualUpdate(ep_get_ret, ep_update_ret)

    def test_create_update_get_endpoint_add_epg(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg1 = self._make_epg_dict()

        epg_ret1 = plugin.create_endpoint_group(
                      admin_context, epg1)
        ep = self._make_ep_dict(ip_mask='0.0.0.0/0',
                                ep_groups=[{'id': epg_ret1['id']}])
        epg2 = self._make_epg_dict(name="test_epg2")

        epg_ret2 = plugin.create_endpoint_group(
                      admin_context, epg2)
        ep_ret = plugin.create_endpoint(admin_context, ep)
        ep_update = self._make_ep_update_dict(add_ep_groups=
                                              [{"id": epg_ret2['id']}])
        ep_update_ret = plugin.update_endpoint(admin_context,
                                               ep_ret["id"], ep_update)
        ep_get_ret = plugin.get_endpoint(admin_context, ep_ret["id"])
        self.assertEqualUpdate(ep_get_ret, ep_update_ret)

    def _make_epg_dict(self, name="test_name"):
        return {"endpoint_group": {
                   "tenant_id": "test_tenant",
                   "name": name,
                   "description": "test_description"}}

    def _make_ep_dict(self, name="test_endpoint", port=None,
                      ip_mask=None, ip_port=None, ep_groups=[]):
        return {"endpoint": {
                    "name": name,
                    "tenant_id": "test_tenant",
                    "port_id": port,
                    "ip_mask": ip_mask,
                    "ip_port": ip_port,
                    "ep_groups": ep_groups}}

    def _make_ep_update_dict(self, name="test_endpoint",
                             add_ep_groups=[], remove_ep_groups=[]):
        return {"endpoint": {
                   "tenant_id": "test_tenant",
                   "name": name,
                   "add_endpoint_groups": add_ep_groups,
                   "remove_endpoint_groups": remove_ep_groups}}

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

    def _fake_sg(self):
        return {"security_group": {"name": "fake-sg",
                                   "description": "sample-description",
                                   "tenant_id": "test-tenant"}}

    def assertEqualUpdate(self, ep_ref, ep_actual):
        def make_ep_dict(ep_db):
            if "add_endpoint_groups" in ep_db:
                del ep_db["add_endpoint_groups"]
            if "remove_endpoint_groups" in ep_db:
                del ep_db["remove_endpoint_groups"]
            return ep_db

        ep_ref = make_ep_dict(ep_ref)
        ep_actual = make_ep_dict(ep_actual)
        return self.assertItemsEqual(ep_ref, ep_actual)

    def _consolidate_update_config(self, ep_update, ep_update_ret):
        ep_update["endpoint"]["id"] = ep_update_ret["id"]
        ep_update["endpoint"]["ep_groups"] = ep_update_ret["ep_groups"]
        ep_update["endpoint"]["ip_port"] = ep_update_ret["ip_port"]
        ep_update["endpoint"]["ip_mask"] = ep_update_ret["ip_mask"]
        ep_update["endpoint"]["port_id"] = ep_update_ret["port_id"]
