# Copyright 2015 PLUMgrid, Inc. All Rights Reserved.
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

from neutron.tests.api import base
from neutron.tests.tempest import test
from plumgrid_tempest_plugin import config
from plumgrid_tempest_plugin.tests.api import base_l2gw
from random import randint
from tempest_lib.common.utils import data_utils
from tempest_lib import exceptions as lib_exc

CONF = config.CONF


class L2GatewaysNegativeTestJSON(base.BaseNetworkTest):
    _interface = 'json'

    @classmethod
    def resource_setup(cls):
        super(L2GatewaysNegativeTestJSON, cls).resource_setup()
        # Atleast one switch detail should be provided to run the tests
        if (len(CONF.network.l2gw_switch) < 0):
            msg = ('Atleast one switch detail must be defined.')
            raise cls.skipException(msg)
        if not test.is_extension_enabled('l2gateway', 'network'):
            msg = "L2Gateway Extension not enabled."
            raise cls.skipException(msg)

    @test.attr(type=['negative', 'smoke'])
    @test.idempotent_id('b301d83d-3af3-4712-86dc-a6824e9b14e5')
    def test_create_l2gateway_non_admin_user(self):
        gw_name = data_utils.rand_name('l2gw')
        devices = base_l2gw.get_l2gw_body(CONF.network.l2gw_switch)["devices"]
        self.assertRaises(lib_exc.Forbidden,
                          self.client.create_l2_gateway,
                          name=gw_name, devices=devices)

    @test.attr(type=['negative', 'smoke'])
    @test.idempotent_id('68451dfe-b3b5-4eb1-b03f-9935d4a2dbe7')
    def test_list_l2gateway_non_admin_user(self):
        self.assertRaises(lib_exc.Forbidden,
                          self.client.list_l2_gateways)

    @test.attr(type=['negative', 'smoke'])
    @test.idempotent_id('f8589452-7aff-4992-b865-5bb5c41fa755')
    def test_update_l2gateway_non_admin_user(self):
        non_exist_id = data_utils.rand_name('l2gw')
        self.assertRaises(lib_exc.Forbidden,
                          self.client.update_l2_gateway,
                          non_exist_id, name="updated_name")

    @test.attr(type=['negative', 'smoke'])
    @test.idempotent_id('d9f57800-6cae-4770-a2d7-ab60cf7417bf')
    def test_delete_l2gateway_non_admin_user(self):
        non_exist_id = data_utils.rand_name('l2gw')
        self.assertRaises(lib_exc.Forbidden,
                          self.client.delete_l2_gateway,
                          non_exist_id)

    @test.attr(type=['negative', 'smoke'])
    @test.idempotent_id('c6b61a8d-8c82-497d-9fad-9929c9acf035')
    def test_create_l2gateway_connection_non_admin_user(self):
        non_exist_id = data_utils.rand_name('network')
        self.assertRaises(lib_exc.Forbidden,
                          self.client.create_l2_gateway_connection,
                          network_id=non_exist_id, l2_gateway_id=non_exist_id)

    @test.attr(type=['negative', 'smoke'])
    @test.idempotent_id('a56a0180-7d98-414c-9a44-fe47a30fe436')
    def test_list_l2gateway_connection_non_admin_user(self):
        self.assertRaises(lib_exc.Forbidden,
                          self.client.list_l2_gateway_connections)

    @test.attr(type=['negative', 'smoke'])
    @test.idempotent_id('ce42c68d-5c41-4988-8912-233e3fe5c8fd')
    def test_delete_l2gateway_connection_non_admin_user(self):
        non_exist_id = data_utils.rand_name('l2gwconnection')
        self.assertRaises(lib_exc.Forbidden,
                          self.client.delete_l2_gateway_connection,
                          non_exist_id)


class L2GatewaysNegativeAdminTestJSON(base.BaseAdminNetworkTest):
    _interface = 'json'

    @classmethod
    def resource_setup(cls):
        super(L2GatewaysNegativeAdminTestJSON, cls).resource_setup()
        if not test.is_extension_enabled('l2gateway', 'network'):
            msg = "L2Gateway Extension not enabled."
            raise cls.skipException(msg)

    @test.attr(type=['negative', 'smoke'])
    @test.idempotent_id('42067b44-3aff-4428-8305-d0496bd38179')
    def test_delete_l2gw_associated_l2gw_connection(self):
        # Create a network
        name = data_utils.rand_name('network')
        net_body = self.admin_client.create_network(name=name)
        net_id = net_body['network']['id']
        self.addCleanup(self.admin_client.delete_network, net_id)
        # Create an L2Gateway
        gw_name = data_utils.rand_name('l2gw')
        vtep_ifc = "1"
        vtep_ip = "3.3.3.3/32"
        devices = base_l2gw.get_l2gw_body(CONF.network.l2gw_switch)["devices"]
        seg_id = devices[0]['interfaces'][0]['segmentation_id'][0]
        body = self.admin_client.create_l2_gateway(
            name=gw_name, vtep_ifc=vtep_ifc, vtep_ip=vtep_ip, devices=devices)
        l2_gateway = body['l2_gateway']
        self.addCleanup(self.admin_client.delete_l2_gateway, l2_gateway['id'])
        # Create an L2Gateway Connection
        l2_gw_conn_body = self.admin_client.create_l2_gateway_connection(
            l2_gateway_id=l2_gateway['id'], network_id=net_id,
            segmentation_id=seg_id)
        l2_gw_conn_id = l2_gw_conn_body['l2_gateway_connection']['id']
        self.addCleanup(self.admin_client.delete_l2_gateway_connection,
                        l2_gw_conn_id)
        self.assertRaises(lib_exc.Conflict,
                          self.admin_client.delete_l2_gateway,
                          l2_gateway['id'])

    @test.attr(type=['negative', 'smoke'])
    def test_create_l2gw_with_empty_device_name(self):
        # Create an L2Gateway
        seg_id = randint(2, 4094)
        seg_id_str = [str(seg_id)]
        gw_name = data_utils.rand_name('l2gw')
        dev_name = ""
        interface_name = data_utils.rand_name('interface')
        device = [{"device_name": dev_name, "interfaces":
                  [{"name": interface_name, "segmentation_id": seg_id_str}]}]
        self.assertRaises(lib_exc.BadRequest,
                          self.admin_client.create_l2_gateway,
                          name=gw_name, devices=device
                          )

    @test.attr(type=['negative', 'smoke'])
    def test_create_l2gw_with_invalid_vtep_ip(self):
        # Create an L2Gateway
        seg_id = randint(2, 4094)
        seg_id_str = [str(seg_id)]
        gw_name = data_utils.rand_name('l2gw')
        vtep_ifc = "1"
        vtep_ip = "vtep-ip"
        dev_name = "d1"
        interface_name = data_utils.rand_name('interface')
        device = [{"device_name": dev_name, "interfaces":
                  [{"name": interface_name, "segmentation_id": seg_id_str}]}]
        self.assertRaises(lib_exc.BadRequest,
                          self.admin_client.create_l2_gateway,
                          name=gw_name, vtep_ifc=vtep_ifc, vtep_ip=vtep_ip,
                          devices=device
                          )

    @test.attr(type=['negative', 'smoke'])
    def test_create_l2gw_connection_with_invalid_segmentation_id(self):
        # Create an L2Gateway
        gw_name = data_utils.rand_name('l2gw')
        vtep_ifc = "1"
        vtep_ip = "3.3.3.3/32"
        dev_name = data_utils.rand_name('device_name')
        interface_name = data_utils.rand_name('interface')
        devices = [{"device_name": dev_name, "device_ip": "192.168.10.100",
                    "interfaces":
                   [{"segmentation_id": [111], "name": interface_name}]}]
        body = self.admin_client.create_l2_gateway(
            name=gw_name, vtep_ifc=vtep_ifc, vtep_ip=vtep_ip, devices=devices)
        l2_gateway = body['l2_gateway']
        l2_gw_id = l2_gateway['id']
        self.addCleanup(self.admin_client.delete_l2_gateway, l2_gw_id)

        # Create a network
        name = data_utils.rand_name('network')
        net_body = self.admin_client.create_network(name=name)
        net_id = net_body['network']['id']
        self.addCleanup(self.admin_client.delete_network, net_id)
        for i in ['-1', '4095', '4096']:
            seg_id = [i]
            self.assertRaises(lib_exc.BadRequest,
                              self.admin_client.create_l2_gateway_connection,
                              l2_gateway_id=l2_gw_id, network_id=net_id,
                              segmentation_id=seg_id)

    @test.attr(type=['negative', 'smoke'])
    def test_create_l2gw_with_invalid_segmentation_id(self):
        # Create an L2Gateway
        gw_name = data_utils.rand_name('l2gw')
        dev_name = data_utils.rand_name('device_name')
        interface_name = data_utils.rand_name('interface')
        for i in ['-1', '4095', '4096']:
            seg_id = [i]
            device = [{"device_name": dev_name, "device_ip": "192.168.10.100",
                       "interfaces":
                      [{"name": interface_name, "segmentation_id": seg_id}]}]
            self.assertRaises(lib_exc.BadRequest,
                              self.admin_client.create_l2_gateway,
                              name=gw_name, devices=device
                              )

    @test.attr(type=['negative', 'smoke'])
    def test_create_l2gw_with_empty_interface_name(self):
        # Create an L2Gateway
        seg_id = randint(2, 4094)
        seg_id_str = [str(seg_id)]
        gw_name = data_utils.rand_name('l2gw')
        dev_name = data_utils.rand_name('device')
        interface_name = ""
        device = [{"device_name": dev_name, "device_ip": "192.168.10.100",
                   "interfaces":
                  [{"name": interface_name, "segmentation_id": seg_id_str}]}]
        self.assertRaises(lib_exc.BadRequest,
                          self.admin_client.create_l2_gateway,
                          name=gw_name, devices=device
                          )

    @test.attr(type=['negative', 'smoke'])
    def test_delete_non_existent_l2gateway(self):
        non_exist_id = data_utils.rand_name('l2gw')
        self.assertRaises(lib_exc.NotFound,
                          self.admin_client.delete_l2_gateway,
                          non_exist_id)

    @test.attr(type=['negative', 'smoke'])
    def test_delete_non_existent_l2gateway_connection(self):
        non_exist_id = data_utils.rand_name('l2gwConnection')
        self.assertRaises(lib_exc.NotFound,
                          self.admin_client.delete_l2_gateway_connection,
                          non_exist_id)

    @test.attr(type=['negative', 'smoke'])
    def test_create_l2gw_connection_with_invalid_network_name(self):
        # Create an L2Gateway
        gw_name = data_utils.rand_name('l2gw')
        vtep_ifc = "1"
        vtep_ip = "3.3.3.3/32"
        devices = base_l2gw.get_l2gw_body(CONF.network.l2gw_switch)["devices"]
        seg_id = devices[0]['interfaces'][0]['segmentation_id'][0]
        body = self.admin_client.create_l2_gateway(
            name=gw_name, vtep_ifc=vtep_ifc, vtep_ip=vtep_ip, devices=devices)
        l2_gateway = body['l2_gateway']
        l2_gw_id = l2_gateway['id']
        self.addCleanup(self.admin_client.delete_l2_gateway, l2_gw_id)

        # Create a network
        net_id = "network"
        self.assertRaises(lib_exc.ServerFault,
                          self.admin_client.create_l2_gateway_connection,
                          l2_gateway_id=l2_gw_id, network_id=net_id,
                          segmentation_id=seg_id
                          )

    @test.attr(type=['negative', 'smoke'])
    def test_update_gateway_with_invalid_device_name(self):
        # Create an L2Gateway
        gw_name = data_utils.rand_name('l2gw')
        vtep_ifc = "1"
        vtep_ip = "3.3.3.3/32"
        devices = base_l2gw.get_l2gw_body(CONF.network.l2gw_switch)["devices"]
        body = self.admin_client.create_l2_gateway(
            name=gw_name, vtep_ifc=vtep_ifc, vtep_ip=vtep_ip, devices=devices)
        l2_gateway = body['l2_gateway']
        self.addCleanup(self.admin_client.delete_l2_gateway, l2_gateway['id'])
        device_1 = [{"device_name": ""}]

        # Create a connection again for same L2Gateway and Network
        self.assertRaises(lib_exc.BadRequest,
                          self.admin_client.update_l2_gateway,
                          gw_name, devices=device_1
                          )

    @test.attr(type=['negative', 'smoke'])
    def test_create_l2gw_and_l2gw_connection_both_without_seg_id(self):
        # Create an L2Gateway
        gw_name = data_utils.rand_name('l2gw')
        vtep_ifc = "1"
        vtep_ip = "3.3.3.3/32"
        devices = base_l2gw.get_l2gw_body(CONF.network.l2gw_switch)["devices"]
        body = self.admin_client.create_l2_gateway(
            name=gw_name, vtep_ifc=vtep_ifc, vtep_ip=vtep_ip, devices=devices)
        l2_gateway = body['l2_gateway']
        l2_gw_id = l2_gateway['id']
        self.addCleanup(self.admin_client.delete_l2_gateway, l2_gw_id)

        # Create a network
        name = data_utils.rand_name('network')
        net_body = self.admin_client.create_network(name=name)
        net_id = net_body['network']['id']
        self.addCleanup(self.admin_client.delete_network, net_id)
        self.assertRaises(lib_exc.Conflict,
                          self.admin_client.create_l2_gateway_connection,
                          l2_gateway_id=l2_gw_id, network_id=net_id
                          )
