# Copyright 2015 OpenStack Foundation.
# All Rights Reserved
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
#

import sys

import mock

from networking_plumgrid.neutron.tests.unit.cli import test_cli20
from networking_plumgrid.neutronclient.l2gw_client_ext import (
    _l2_gateway as l2_gateway)

from neutronclient import shell


class CLITestV20ExtensionL2GWJSON(test_cli20.CLITestV20Base):
    def setUp(self):
        # need to mock before super because extensions loaded on instantiation
        self._mock_extension_loading()
        super(CLITestV20ExtensionL2GWJSON, self).setUp(plurals={'tags': 'tag'})

    def _mock_extension_loading(self):
        ext_pkg = 'neutronclient.common.extension'
        contrib = mock.patch(ext_pkg + '._discover_via_entry_points').start()
        contrib.return_value = [("_l2_gateway", l2_gateway)]
        return contrib

    def test_ext_cmd_loaded(self):
        """Tests l2gw  commands loaded."""
        shell.NeutronShell('2.0')
        ext_cmd = {'l2-gateway-list': l2_gateway.L2GatewayList,
                   'l2-gateway-create': l2_gateway.L2GatewayCreate,
                   'l2-gateway-update': l2_gateway.L2GatewayUpdate,
                   'l2-gateway-delete': l2_gateway.L2GatewayDelete,
                   'l2-gateway-show': l2_gateway.L2GatewayShow}
        self.assertDictContainsSubset(ext_cmd, shell.COMMANDS['2.0'])

    def _create_l2_gateway(self, args, name, vtep_ifc, vtep_ip, device):
        resource = 'l2_gateway'
        cmd = l2_gateway.L2GatewayCreate(test_cli20.MyApp(sys.stdout), None)
        position_names = ['name', 'vtep_ifc', 'vtep_ip', 'devices']
        position_values = [name, vtep_ifc, vtep_ip, device]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def _update_l2gateway(self, args, values):
        resource = 'l2_gateway'
        cmd = l2_gateway.L2GatewayUpdate(test_cli20.MyApp(sys.stdout), None)
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_create_l2gateway(self):
        """Test Create l2gateway."""

        name = 'l2gateway1'
        vtep_ifc = '1'
        vtep_ip = '3.3.3.3/32'
        args = [name, '--vtep_ifc=1', '--vtep_ip=3.3.3.3/32', '--device',
                'name=d1,device_ip=192.168.10.100,interface_names=i1']
        device = [{'device_name': 'd1', 'device_ip': '192.168.10.100',
                   'interfaces': [{'name': 'i1'}]}]
        self._create_l2_gateway(args, name, vtep_ifc, vtep_ip, device)

    def test_create_l2gateway_with_multiple_devices(self):
        """Test Create l2gateway for multiple devices."""

        name = 'l2gateway1'
        vtep_ifc = '1'
        vtep_ip = '3.3.3.3/32'
        args = [name, '--vtep_ifc=1', '--vtep_ip=3.3.3.3/32', '--device',
                'name=dev1,device_ip=192.168.10.100,interface_names=int1',
                '--device',
                'name=dev2,device_ip=192.168.10.200,interface_names=int2']
        devices = [{'device_ip': '192.168.10.100', 'device_name': 'dev1',
                    'interfaces': [{'name': 'int1'}]},
                   {'device_ip': '192.168.10.200', 'device_name': 'dev2',
                    'interfaces': [{'name': 'int2'}]}]
        self._create_l2_gateway(args, name, vtep_ifc, vtep_ip, devices)

    def test_create_l2gateway_with_multiple_interfaces(self):
        """Test Create l2gateway with multiple interfaces."""

        name = 'l2gw-mul-interface'
        vtep_ifc = '1'
        vtep_ip = '3.3.3.3/32'
        args = [name, '--vtep_ifc=1', '--vtep_ip=3.3.3.3/32', '--device',
                'name=d1,device_ip=192.168.10.100,interface_names=int1;int2']
        interfaces = [{'name': 'int1'}, {'name': 'int2'}]
        device = [{'device_ip': '192.168.10.100', 'device_name': 'd1',
                   'interfaces': interfaces}]
        self._create_l2_gateway(args, name, vtep_ifc, vtep_ip, device)

    def test_create_l2gateway_with_segmenation_id(self):
        """Test Create l2gateway with segmentation-id."""

        name = 'l2gw-seg-id'
        vtep_ifc = '1'
        vtep_ip = '3.3.3.3/32'
        args = [name, '--vtep_ifc=1', '--vtep_ip=3.3.3.3/32', '--device',
                'name=d1,device_ip=192.168.10.100,interface_names=int1|100']
        interfaces = [{'name': 'int1', "segmentation_id": ["100"]}]
        device = [{'device_ip': '192.168.10.100', 'device_name': 'd1',
                   'interfaces': interfaces}]
        self._create_l2_gateway(args, name, vtep_ifc, vtep_ip, device)

    def test_create_l2gateway_with_mul_segmenation_id(self):
        """Test Create l2gateway with multiple segmentation-ids."""

        name = 'l2gw-mul-seg-id'
        vtep_ifc = '1'
        vtep_ip = '3.3.3.3/32'
        args = [name, '--vtep_ifc=1', '--vtep_ip=3.3.3.3/32', '--device',
               'name=d1,device_ip=192.168.10.100,interface_names=int1|100#200']
        interfaces = [{'name': 'int1', "segmentation_id": ["100", "200"]}]
        device = [{'device_ip': '192.168.10.100', 'device_name': 'd1',
                   'interfaces': interfaces}]
        self._create_l2_gateway(args, name, vtep_ifc, vtep_ip, device)

    def test_list_l2gateway(self):
        """Test List l2gateways."""

        resources = "l2_gateways"
        cmd = l2_gateway.L2GatewayList(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, True)

    def test_delete_l2gateway(self):
        """Test Delete l2gateway."""

        resource = 'l2_gateway'
        cmd = l2_gateway.L2GatewayDelete(test_cli20.MyApp(sys.stdout), None)
        my_id = 'my-id'
        args = [my_id]
        self._test_delete_resource(resource, cmd, my_id, args)

    def test_show_l2gateway(self):
        """Test Show l2gateway: --fields id --fields name myid."""

        resource = 'l2_gateway'
        cmd = l2_gateway.L2GatewayShow(test_cli20.MyApp(sys.stdout), None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id, args,
                                 ['id', 'name'])

    def test_update_l2gateway(self):
        """Test Update l2gateway."""

        args = ['myid', '--name', 'myname', '--vtep_ifc', '1', '--vtep_ip',
                '3.3.3.3/32', '--device',
                'name=d1,device_ip=192.168.10.100,interface_names=i1']
        values = {'name': 'myname',
                  'vtep_ifc': '1',
                  'vtep_ip': '3.3.3.3/32',
                  'devices': [{'device_name': 'd1',
                               'device_ip': '192.168.10.100',
                               'interfaces': [{'name': 'i1'}]}]}
        self._update_l2gateway(args, values)

    def test_update_l2gateway_name(self):
        """Test Update l2gatewayi name."""

        args = ['myid', '--name', 'myname']
        values = {'name': 'myname'}
        self._update_l2gateway(args, values)

    def test_update_l2gateway_with_multiple_interfaces(self):
        """Test Update l2gateway with multiple interfaces."""

        args = ['myid', '--name', 'myname', '--vtep_ifc', '1', '--vtep_ip',
                '3.3.3.3/32', '--device',
                'name=d1,device_ip=192.168.10.100,interface_names=i1;i2']
        values = {'name': 'myname',
                  'vtep_ifc': '1',
                  'vtep_ip': '3.3.3.3/32',
                  'devices': [{'device_name': 'd1',
                               'device_ip': '192.168.10.100',
                               'interfaces': [{'name': 'i1'},
                                              {'name': 'i2'}]}]}
        self._update_l2gateway(args, values)

    def test_update_l2gateway_with_segmentation_id(self):
        """Test Update l2gateway with segmentation-id."""

        args = ['myid', '--name', 'myname', '--vtep_ifc', '1', '--vtep_ip',
                '3.3.3.3/32', '--device',
                'name=d1,device_ip=192.168.10.100,interface_names=int1|100']
        interfaces = [{'name': 'int1', "segmentation_id": ["100"]}]
        values = {'name': 'myname',
                  'vtep_ifc': '1',
                  'vtep_ip': '3.3.3.3/32',
                  'devices': [{'device_name': 'd1',
                               'device_ip': '192.168.10.100',
                               'interfaces': interfaces}]}
        self._update_l2gateway(args, values)
