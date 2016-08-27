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
Policy Service extension unit tests
"""
from networking_plumgrid.neutron.plugins.common import \
    policy_exceptions as policy_excep
from networking_plumgrid.neutron.plugins.extensions import \
    policyservice as ext_ps
from networking_plumgrid.neutron.tests.unit import \
    test_networking_plumgrid as test_pg

from neutron.api import extensions
from neutron.api.v2 import attributes
from neutron import context
from neutron import manager
from neutron.tests.unit.api import test_extensions as test_ext
from neutron_lib import exceptions as n_excep
from oslo_log import log as logging
import uuid

LOG = logging.getLogger(__name__)


class PolicyServiceExtensionManager(object):

    def get_resources(self):
        return ext_ps.Policyservice.get_resources()

    def get_actions(self):
        return []

    def get_request_extensions(self):
        return []


class PolicyServiceTestCase(test_pg.PLUMgridPluginV2TestCase):
    def setUp(self, plugin=None, ext_mgr=None):
        super(PolicyServiceTestCase, self).setUp()
        ext_mgr = PolicyServiceExtensionManager()
        extensions.PluginAwareExtensionManager._instance = None
        self.ext_api = test_ext.setup_extensions_middleware(ext_mgr)


class TestPolicyService(PolicyServiceTestCase):

    def test_create_policy_service_name(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        ps = self._make_ps_dict()

        ps_ret = plugin.create_policy_service(admin_context, ps)
        ps["policy_service"]["id"] = ps_ret["id"]
        self.assertEqual(ps_ret, ps["policy_service"])

    def test_create_policy_service_inport(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)
        ps = self._make_ps_dict(inports=[{'id': port_ret['id']}])

        ps_ret = plugin.create_policy_service(admin_context, ps)
        ps["policy_service"]["id"] = ps_ret["id"]
        self.assertEqual(ps_ret, ps["policy_service"])

    def test_create_policy_service_eport(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)
        ps = self._make_ps_dict(eports=[{'id': port_ret['id']}])

        ps_ret = plugin.create_policy_service(admin_context, ps)
        ps["policy_service"]["id"] = ps_ret["id"]
        self.assertEqual(ps_ret, ps["policy_service"])

    def test_create_policy_service_bidirect_port(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)
        ps = self._make_ps_dict(bidirect_ports=[{'id': port_ret['id']}])
        ps_ret = plugin.create_policy_service(admin_context, ps)
        ps["policy_service"]["id"] = ps_ret["id"]
        self.assertEqual(ps_ret, ps["policy_service"])

    def test_create_policy_service_inport_name(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)
        ps = self._make_ps_dict(inports=[{'id': port_ret['name']}])

        ps_ret = plugin.create_policy_service(admin_context, ps)
        ps["policy_service"]["id"] = ps_ret["id"]
        self.assertEqual(ps_ret, ps["policy_service"])

    def test_create_policy_service_eport_name(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)
        ps = self._make_ps_dict(eports=[{'id': port_ret['name']}])

        ps_ret = plugin.create_policy_service(admin_context, ps)
        ps["policy_service"]["id"] = ps_ret["id"]
        self.assertEqual(ps_ret, ps["policy_service"])

    def test_create_policy_service_bidirect_port_name(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)
        ps = self._make_ps_dict(bidirect_ports=[{'id': port_ret['name']}])
        ps_ret = plugin.create_policy_service(admin_context, ps)
        ps["policy_service"]["id"] = ps_ret["id"]
        self.assertEqual(ps_ret, ps["policy_service"])

    def test_create_policy_service_dup_ports_inport(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)
        ps = self._make_ps_dict(inports=[{'id': port_ret['id']},
                                         {'id': port_ret['id']}])
        self.assertRaises(policy_excep.DuplicatePortFound,
                          plugin.create_policy_service, admin_context, ps)

    def test_create_policy_service_dup_ports_eport(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)
        ps = self._make_ps_dict(eports=[{'id': port_ret['id']},
                                {'id': port_ret['id']}])
        self.assertRaises(policy_excep.DuplicatePortFound,
                          plugin.create_policy_service, admin_context, ps)

    def test_create_policy_service_dup_ports_bidirect(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)
        ps = self._make_ps_dict(bidirect_ports=[{'id': port_ret['id']},
                                                {'id': port_ret['id']}])
        self.assertRaises(policy_excep.DuplicatePortFound,
                          plugin.create_policy_service, admin_context, ps)

    def test_create_policy_service_dup_ports_across_config(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)
        ps = self._make_ps_dict(eports=[{'id': port_ret['id']}],
                                inports=[{'id': port_ret['id']}])
        self.assertRaises(policy_excep.DuplicatePortFound,
                          plugin.create_policy_service, admin_context, ps)

    def test_create_policy_service_without_leg_mode(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        ps = self._make_ps_dict()

        ps_ret = plugin.create_policy_service(admin_context, ps)
        ps["policy_service"]["id"] = ps_ret["id"]
        self.assertEqual(ps_ret, ps["policy_service"])

    def test_create_policy_service_inport_owner_not_nova(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"], device_owner="invalid:owner")
        port_ret = plugin.create_port(
                      admin_context, port)
        ps = self._make_ps_dict(inports=[{'id': port_ret['id']}])
        self.assertRaises(policy_excep.InvalidPortForPolicyService,
                          plugin.create_policy_service, admin_context, ps)

    def test_create_policy_service_eport_owner_not_nova(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"], device_owner="invalid:owner")
        port_ret = plugin.create_port(
                      admin_context, port)
        ps = self._make_ps_dict(eports=[{'id': port_ret['id']}])
        self.assertRaises(policy_excep.InvalidPortForPolicyService,
                          plugin.create_policy_service, admin_context, ps)

    def test_create_policy_service_bidirect_port_owner_not_nova(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"], device_owner="invalid:owner")
        port_ret = plugin.create_port(
                      admin_context, port)
        ps = self._make_ps_dict(bidirect_ports=[{'id': port_ret['id']}])
        self.assertRaises(policy_excep.InvalidPortForPolicyService,
                          plugin.create_policy_service, admin_context, ps)

    def test_create_policy_service_inport_port_not_found(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        ps = self._make_ps_dict(inports=[{'id': str(uuid.uuid4())}])
        self.assertRaises(n_excep.PortNotFound,
                          plugin.create_policy_service, admin_context, ps)

    def test_create_policy_service_eport_port_not_found(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        ps = self._make_ps_dict(eports=[{'id': str(uuid.uuid4())}])
        self.assertRaises(n_excep.PortNotFound,
                          plugin.create_policy_service, admin_context, ps)

    def test_create_policy_service_bidirect_port_not_found(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        ps = self._make_ps_dict(bidirect_ports=[{'id': str(uuid.uuid4())}])
        self.assertRaises(n_excep.PortNotFound,
                          plugin.create_policy_service, admin_context, ps)

    def test_create_policy_service_port_already_in_use_ps(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)
        ps1 = self._make_ps_dict(inports=[{'id': port_ret['id']}])

        plugin.create_policy_service(admin_context, ps1)
        ps2 = self._make_ps_dict(name="test_ps2",
                                 inports=[{'id': port_ret['id']}])
        self.assertRaises(policy_excep.PortAlreadyInUsePolicyService,
                          plugin.create_policy_service, admin_context, ps2)

    def test_create_policy_service_inport_bidirect_port(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port1 = self._fake_port(network_ret["id"])
        port_ret1 = plugin.create_port(
                      admin_context, port1)
        port2 = self._fake_port(network_ret["id"])
        port_ret2 = plugin.create_port(
                      admin_context, port2)
        ps = self._make_ps_dict(inports=[{'id': port_ret1['id']}],
                                bidirect_ports=[{'id': port_ret2['id']}])
        self.assertRaises(policy_excep.InvalidPortConfigPolicyService,
                          plugin.create_policy_service, admin_context, ps)

    def test_create_policy_service_eport_bidirect_port(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port1 = self._fake_port(network_ret["id"])
        port_ret1 = plugin.create_port(
                      admin_context, port1)
        port2 = self._fake_port(network_ret["id"])
        port_ret2 = plugin.create_port(
                      admin_context, port2)
        ps = self._make_ps_dict(eports=[{'id': port_ret1['id']}],
                                bidirect_ports=[{'id': port_ret2['id']}])
        self.assertRaises(policy_excep.InvalidPortConfigPolicyService,
                          plugin.create_policy_service, admin_context, ps)

    def test_create_policy_service_inport_eport_bidirect_port(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port1 = self._fake_port(network_ret["id"])
        port_ret1 = plugin.create_port(
                      admin_context, port1)
        port2 = self._fake_port(network_ret["id"])
        port_ret2 = plugin.create_port(
                      admin_context, port2)
        port3 = self._fake_port(network_ret["id"])
        port_ret3 = plugin.create_port(
                      admin_context, port3)
        ps = self._make_ps_dict(eports=[{'id': port_ret1['id']}],
                                inports=[{'id': port_ret2['id']}],
                                bidirect_ports=[{'id': port_ret3['id']}])
        self.assertRaises(policy_excep.InvalidPortConfigPolicyService,
                          plugin.create_policy_service, admin_context, ps)

    def test_delete_policy_service(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        ps = self._make_ps_dict()

        ps_ret = plugin.create_policy_service(admin_context, ps)
        resp = plugin.delete_policy_service(admin_context, ps_ret["id"])
        self.assertEqual(None, resp)

    def test_delete_policy_service_ports_in_use(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)
        ps = self._make_ps_dict(inports=[{'id': port_ret['id']}])

        ps_ret = plugin.create_policy_service(admin_context, ps)
        self.assertRaises(policy_excep.PolicyServiceInUse,
                          plugin.delete_policy_service, admin_context,
                          ps_ret["id"])

    def test_delete_policy_service_does_not_exist(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        self.assertRaises(policy_excep.NoPolicyServiceFound,
                          plugin.delete_policy_service, admin_context,
                          str(uuid.uuid4()))

    def test_update_policy_service_name(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        ps = self._make_ps_dict()
        ps_ret = plugin.create_policy_service(admin_context, ps)
        ps_update_dict = self._make_ps_update_dict()
        ps_update_ret = plugin.update_policy_service(admin_context,
                                                     ps_ret["id"],
                                                     ps_update_dict)
        self.assertEqual(ps_update_dict["policy_service"]["name"],
                         ps_update_ret["name"])

    def test_update_policy_service_inport(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)
        ps = self._make_ps_dict()
        ps_ret = plugin.create_policy_service(admin_context, ps)
        ps_update_dict = self._make_ps_update_dict(add_inports=
                                                   [{"id": port_ret["id"]}])
        ps_update_ret = plugin.update_policy_service(admin_context,
                                                     ps_ret["id"],
                                                     ps_update_dict)
        self.assertEqual(ps_update_dict["policy_service"]["add_ingress_ports"],
                         ps_update_ret["ingress_ports"])

    def test_update_policy_service_eport(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)
        ps = self._make_ps_dict()
        ps_ret = plugin.create_policy_service(admin_context, ps)
        ps_update_dict = self._make_ps_update_dict(add_eports=
                                                   [{"id": port_ret["id"]}])
        ps_update_ret = plugin.update_policy_service(admin_context,
                                                     ps_ret["id"],
                                                     ps_update_dict)
        self.assertEqual(ps_update_dict["policy_service"]["add_egress_ports"],
                         ps_update_ret["egress_ports"])

    def test_update_policy_service_bidirect_port(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)
        ps = self._make_ps_dict()
        ps_ret = plugin.create_policy_service(admin_context, ps)
        ps_update_dict = self._make_ps_update_dict(add_bidirect_ports=
                                                   [{"id": port_ret["id"]}])
        ps_update_ret = plugin.update_policy_service(admin_context,
                                                     ps_ret["id"],
                                                     ps_update_dict)
        self.assertEqual(ps_update_dict["policy_service"]
                         ["add_bidirectional_ports"],
                         ps_update_ret["bidirectional_ports"])

    def test_update_policy_service_add_dup_inports(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)
        ps = self._make_ps_dict()
        ps_ret = plugin.create_policy_service(admin_context, ps)
        ps_update_dict = self._make_ps_update_dict(add_inports=
                                                   [{"id": port_ret["id"]},
                                                    {"id": port_ret["id"]}])
        self.assertRaises(policy_excep.DuplicatePortFound,
                          plugin.update_policy_service, admin_context,
                          ps_ret["id"], ps_update_dict)

    def test_update_policy_service_add_dup_eports(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)
        ps = self._make_ps_dict()
        ps_ret = plugin.create_policy_service(admin_context, ps)
        ps_update_dict = self._make_ps_update_dict(add_eports=
                                                   [{"id": port_ret["id"]},
                                                   {"id": port_ret["id"]}])
        self.assertRaises(policy_excep.DuplicatePortFound,
                          plugin.update_policy_service, admin_context,
                          ps_ret["id"], ps_update_dict)

    def test_update_policy_service_add_dup_bidirect_ports(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)
        ps = self._make_ps_dict()
        ps_ret = plugin.create_policy_service(admin_context, ps)
        ps_update_dict = self._make_ps_update_dict(add_bidirect_ports=
                                                   [{"id": port_ret["id"]},
                                                   {"id": port_ret["id"]}])
        self.assertRaises(policy_excep.DuplicatePortFound,
                          plugin.update_policy_service, admin_context,
                          ps_ret["id"], ps_update_dict)

    def test_update_policy_service_remove_dup_inports(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)
        ps = self._make_ps_dict(inports=[{'id': port_ret['id']}])
        ps_ret = plugin.create_policy_service(admin_context, ps)
        ps_update_dict = self._make_ps_update_dict(remove_inports=
                                                   [{"id": port_ret["id"]},
                                                   {"id": port_ret["id"]}])
        self.assertRaises(policy_excep.DuplicatePortFound,
                          plugin.update_policy_service, admin_context,
                          ps_ret["id"], ps_update_dict)

    def test_update_policy_service_remove_dup_eports(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)
        ps = self._make_ps_dict(eports=[{'id': port_ret['id']}])
        ps_ret = plugin.create_policy_service(admin_context, ps)
        ps_update_dict = self._make_ps_update_dict(remove_eports=
                                                   [{"id": port_ret["id"]},
                                                   {"id": port_ret["id"]}])
        self.assertRaises(policy_excep.DuplicatePortFound,
                          plugin.update_policy_service, admin_context,
                          ps_ret["id"], ps_update_dict)

    def test_update_policy_service_remove_dup_bidirect_ports(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)
        ps = self._make_ps_dict(bidirect_ports=[{'id': port_ret['id']}])
        ps_ret = plugin.create_policy_service(admin_context, ps)
        ps_update_dict = self._make_ps_update_dict(remove_bidirect_ports=
                                                   [{"id": port_ret["id"]},
                                                   {"id": port_ret["id"]}])
        self.assertRaises(policy_excep.DuplicatePortFound,
                          plugin.update_policy_service, admin_context,
                          ps_ret["id"], ps_update_dict)

    def test_update_policy_service_dup_ports(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)
        ps = self._make_ps_dict(inports=[{'id': port_ret['id']}])
        ps_ret = plugin.create_policy_service(admin_context, ps)
        ps_update_dict = self._make_ps_update_dict(remove_inports=
                                                   [{"id": port_ret["id"]}],
                                                   remove_eports=
                                                   [{"id": port_ret["id"]}])
        self.assertRaises(policy_excep.DuplicatePortFound,
                          plugin.update_policy_service, admin_context,
                          ps_ret["id"], ps_update_dict)

    def test_update_policy_service_add_inports_owner_not_nova(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"], device_owner="invalid:owner")
        port_ret = plugin.create_port(
                      admin_context, port)
        ps = self._make_ps_dict()
        ps_ret = plugin.create_policy_service(admin_context, ps)
        ps_update_dict = self._make_ps_update_dict(add_inports=
                                                   [{"id": port_ret["id"]}])
        self.assertRaises(policy_excep.InvalidPortForPolicyService,
                          plugin.update_policy_service, admin_context,
                          ps_ret["id"], ps_update_dict)

    def test_update_policy_service_add_eports_owner_not_nova(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"], device_owner="invalid:owner")
        port_ret = plugin.create_port(
                      admin_context, port)
        ps = self._make_ps_dict()
        ps_ret = plugin.create_policy_service(admin_context, ps)
        ps_update_dict = self._make_ps_update_dict(add_eports=
                                                   [{"id": port_ret["id"]}])
        self.assertRaises(policy_excep.InvalidPortForPolicyService,
                          plugin.update_policy_service, admin_context,
                          ps_ret["id"], ps_update_dict)

    def test_update_policy_service_add_bidirect_ports_owner_not_nova(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"], device_owner="invalid:owner")
        port_ret = plugin.create_port(
                      admin_context, port)
        ps = self._make_ps_dict()
        ps_ret = plugin.create_policy_service(admin_context, ps)
        ps_update_dict = self._make_ps_update_dict(add_bidirect_ports=
                                                   [{"id": port_ret["id"]}])
        self.assertRaises(policy_excep.InvalidPortForPolicyService,
                          plugin.update_policy_service, admin_context,
                          ps_ret["id"], ps_update_dict)

    def test_update_policy_service_add_inport_already_in_use(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)
        ps = self._make_ps_dict(inports=[{'id': port_ret['id']}])

        ps_ret = plugin.create_policy_service(admin_context, ps)
        ps_update_dict = self._make_ps_update_dict(add_inports=
                                                   [{"id": port_ret["id"]}])
        self.assertRaises(policy_excep.PortAlreadyInUsePolicyService,
                          plugin.update_policy_service, admin_context,
                          ps_ret["id"], ps_update_dict)

    def test_update_policy_service_add_eport_already_in_use(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)
        ps = self._make_ps_dict(inports=[{'id': port_ret['id']}])

        ps_ret = plugin.create_policy_service(admin_context, ps)
        ps_update_dict = self._make_ps_update_dict(add_eports=
                                                   [{"id": port_ret["id"]}])
        self.assertRaises(policy_excep.PortAlreadyInUsePolicyService,
                          plugin.update_policy_service, admin_context,
                          ps_ret["id"], ps_update_dict)

    def test_update_policy_service_add_bport_already_in_use(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)
        ps = self._make_ps_dict(bidirect_ports=[{'id': port_ret['id']}])

        ps_ret = plugin.create_policy_service(admin_context, ps)
        ps_update_dict = self._make_ps_update_dict(add_bidirect_ports=
                                                   [{"id": port_ret["id"]}])
        self.assertRaises(policy_excep.PortAlreadyInUsePolicyService,
                          plugin.update_policy_service, admin_context,
                          ps_ret["id"], ps_update_dict)

    def test_create_get_policy_service(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        ps = self._make_ps_dict()
        ps_ret = plugin.create_policy_service(admin_context, ps)
        ps_get_ret = plugin.get_policy_service(admin_context, ps_ret["id"])
        self.assertEqual(ps_ret, ps_get_ret)

    def test_list_policy_services(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        ps1 = self._make_ps_dict(name="list_ps1")
        ps_ret1 = plugin.create_policy_service(admin_context, ps1)
        ps2 = self._make_ps_dict(name="list_ps2")
        ps_ret2 = plugin.create_policy_service(admin_context, ps2)
        ps3 = self._make_ps_dict(name="list_ps3")
        ps_ret3 = plugin.create_policy_service(admin_context, ps3)

        ps_list_ret = plugin.get_policy_services(admin_context)
        self.assertItemsEqual(ps_list_ret, [ps_ret1, ps_ret2, ps_ret3])

    def _make_ps_dict(self, name="test_ps", inports=[], eports=[],
                      bidirect_ports=[]):
        return {"policy_service": {
                    "tenant_id": "test_tenant",
                    "description": "test-ps",
                    "name": name,
                    "ingress_ports": inports,
                    "egress_ports": eports,
                    "bidirectional_ports": bidirect_ports}}

    def _make_ps_update_dict(self, name="updated_ps", add_inports=[],
                             add_eports=[], add_bidirect_ports=[],
                             remove_inports=[], remove_eports=[],
                             remove_bidirect_ports=[]):
        update_dict = {"policy_service": {
                         "tenant_id": "test_tenant",
                         "name": name}}
        if add_inports:
            update_dict["policy_service"]["add_ingress_ports"] = add_inports
        if add_eports:
            update_dict["policy_service"]["add_egress_ports"] = add_eports
        if add_bidirect_ports:
            update_dict["policy_service"]["add_bidirectional_ports"] = \
                add_bidirect_ports
        if remove_inports:
            update_dict["policy_service"]["remove_ingress_ports"] = \
                remove_inports
        if remove_eports:
            update_dict["policy_service"]["remove_egress_ports"] = \
                remove_eports
        if remove_bidirect_ports:
            update_dict["policy_service"]["remove_bidirectional_ports"] = \
                remove_bidirect_ports
        return update_dict

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

    def _fake_port(self, net_id, name="fake_port", security_groups = [],
                   device_owner="compute:nova"):
        return {'port': {'name': name,
                         'network_id': net_id,
                         'mac_address': attributes.ATTR_NOT_SPECIFIED,
                         'fixed_ips': attributes.ATTR_NOT_SPECIFIED,
                         'admin_state_up': True,
                         'device_id': 'fake_device_id',
                         'device_owner': device_owner,
                         'tenant_id': "fake_tenant",
                         'security_group': security_groups}}

    def assertEqualUpdate(self, ps_update_dict, ps_update_ret):
        def make_ps_dict(ps_db):
            if "add_ingress_ports" in ps_db:
                del ps_db["add_ingress_ports"]
            if "add_egress_ports" in ps_db:
                del ps_db["add_egress_ports"]
            if "add_bidirectional_ports" in ps_db:
                del ps_db["add_bidirectional_ports"]
            if "remove_ingress_ports" in ps_db:
                del ps_db["remove_ingress_ports"]
            if "remove_egress_ports" in ps_db:
                del ps_db["remove_egress_ports"]
            if "remove_bidirectional_ports" in ps_db:
                del ps_db["remove_bidirectional_ports"]
            return ps_db
        ps_ref = make_ps_dict(ps_update_dict["policy_service"])
        ps_actual = make_ps_dict(ps_update_ret)
        ps_ref["id"] = ps_actual["id"]
        ps_ref["name"] = ps_actual["name"]
        ps_ref["description"] = ps_actual["description"]
        ps_ref["ingress_ports"] = ps_actual["ingress_ports"]
        ps_ref["egress_ports"] = ps_actual["egress_ports"]
        ps_ref["bidirectional_ports"] = ps_actual["bidirectional_ports"]
        return self.assertEqual(ps_ref, ps_actual)
