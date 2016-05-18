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
from networking_plumgrid.neutron.plugins.extensions import \
    endpointgroup as ext_epg
from networking_plumgrid.neutron.plugins.common import \
    endpoint_group_exceptions as epg_excep
from networking_plumgrid.neutron.plugins.common import \
    exceptions as p_excep
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


class EndpointGroupExtensionManager(object):

    def get_resources(self):
        return ext_epg.Endpointgroup.get_resources()

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

    def test_create_endpoint_group_with_port(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)

        epg = self._make_epg_dict(ports=[{"id": port_ret["id"]}])

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epg["endpoint_group"]["id"] = epg_ret["id"]
        self.assertEqual(epg_ret, epg["endpoint_group"])

    def test_create_service_endpoint_group(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict(epg_type="vm_ep")

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epg["endpoint_group"]["id"] = epg_ret["id"]
        self.assertEqual(epg_ret, epg["endpoint_group"])

    def test_create_endpoint_group_no_name(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()
        epg["endpoint_group"]["name"] = None
        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epg["endpoint_group"]["id"] = epg_ret["id"]
        self.assertEqual(epg_ret, epg["endpoint_group"])

    def test_create_endpoint_group_no_name_description(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()
        epg["endpoint_group"]["name"] = None
        epg["endpoint_group"]["description"] = None
        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epg["endpoint_group"]["id"] = epg_ret["id"]
        self.assertEqual(epg_ret, epg["endpoint_group"])

    def test_create_endpoint_group_with_no_type(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()
        epg["endpoint_group"]["endpoint_type"] = None
        self.assertRaises(epg_excep.InvalidEndpointGroupType,
                          plugin.create_endpoint_group, admin_context, epg)

    def test_create_endpoint_group_with_invalid_type(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict(epg_type="fake_type")

        self.assertRaises(epg_excep.InvalidEndpointGroupType,
                          plugin.create_endpoint_group, admin_context, epg)

    def test_create_endpoint_group_with_non_existing_port(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        port_id = str(uuid.uuid4())
        epg = self._make_epg_dict(ports=[{"id": port_id}])

        self.assertRaises(n_excep.PortNotFound,
                          plugin.create_endpoint_group, admin_context, epg)

    def test_create_endpoint_group_with_port_invalid_device_owner(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"], device_owner="fake:owner")
        port_ret = plugin.create_port(
                      admin_context, port)
        epg = self._make_epg_dict(ports=[{"id": port_ret["id"]}])
        self.assertRaises(epg_excep.InvalidPortForEndpointGroup,
                          plugin.create_endpoint_group, admin_context, epg)

    def test_create_endpoint_group_with_port_name(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)

        epg = self._make_epg_dict(ports=[{"id": port_ret["name"]}])
        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epg["endpoint_group"]["id"] = epg_ret["id"]
        self.assertEqual(epg_ret, epg["endpoint_group"])

    def test_create_endpoint_group_with_invalid_port_name(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict(ports=[{"id": "invalid_fake_port"}])
        self.assertRaises(p_excep.PLUMgridException,
                          plugin.create_endpoint_group, admin_context, epg)

    def test_create_associated_service_endpoint_group(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"],
                               security_groups=[str(uuid.uuid4())])
        port_ret = plugin.create_port(
                      admin_context, port)

        epg = self._make_epg_dict(epg_type="vm_ep",
                                  ports=[{"id": port_ret["id"]}])
        self.assertRaises(epg_excep.PortAlreadyInUse,
                          plugin.create_endpoint_group, admin_context, epg)

    def test_create_endpoint_group_with_invalid_port_dict(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)

        epg = self._make_epg_dict(ports=[{"name": port_ret["name"]}])
        self.assertRaises(epg_excep.InvalidDataProvided,
                          plugin.create_endpoint_group, admin_context, epg)

    def test_create_delete_endpoint_group(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        resp = plugin.delete_endpoint_group(admin_context, epg_ret["id"])
        self.assertEqual(None, resp)

    def test_create_delete_service_endpoint_group(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict(epg_type="vm_ep")

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        resp = plugin.delete_endpoint_group(admin_context, epg_ret["id"])
        self.assertEqual(None, resp)

    def test_delete_endpoint_group_does_not_exist(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        self.assertRaises(ext_epg.NoEndpointGroupFound,
                          plugin.delete_endpoint_group, admin_context,
                          str(uuid.uuid4()))

    def test_create_delete_endpoint_group_with_ports(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        tenant_context = context.Context('', 'not_admin')

        network = self._fake_network()
        network["network"]["tenant_id"] = tenant_context.tenant_id
        network_ret = plugin.create_network(tenant_context, network)

        port = self._fake_port(network_ret["id"])
        port_ret = plugin.create_port(
                      admin_context, port)

        epg = self._make_epg_dict(ports=[{"id": port_ret["id"]}])

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        self.assertRaises(ext_epg.EndpointGroupInUse,
                          plugin.delete_endpoint_group, admin_context,
                          epg_ret["id"])

    def test_create_update_endpoint_group(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        epg["endpoint_group"]["id"] = epg_ret["id"]
        epg_update_dict = self._make_epg_update_dict(name="updated_epg")
        epg_update_ret = plugin.update_endpoint_group(admin_context,
                                                      epg_ret["id"],
                                                      epg_update_dict)
        epg_update_dict["endpoint_group"]["id"] = epg_update_ret["id"]
        epg_update_dict["endpoint_group"]["ports"] = epg_update_ret["ports"]
        (epg_update_dict["endpoint_group"]["endpoint_type"] =
            (epg_update_ret["endpoint_type"])
        self.assertEqual(epg_update_dict["endpoint_group"], epg_update_ret)

    def _make_epg_dict(self, epg_type="vm_class",
                       ports=[]):
        return {"endpoint_group": {
                   "tenant_id": "test_tenant",
                   "name": "test_name",
                   "description": "test_description",
                   "endpoint_type": epg_type,
                   "ports": ports}}

    def _make_epg_update_dict(self, name="test_tenant",
                              description="test_description",
                              add_ports=[], remove_ports=[]):
        return {"endpoint_group": {
                   "tenant_id": "test_tenant",
                   "name": name,
                   "description": description,
                   "add_ports": add_ports,
                   "remove_ports": remove_ports}}

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
