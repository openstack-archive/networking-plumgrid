# Copyright 2016 PLUMgrid, Inc. All Rights Reserved.
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

import mock
from networking_plumgrid.neutron.tests.unit.cli import test_cli20
from networking_plumgrid.neutronclient.policy import (
    endpoint as ep)
from neutronclient import shell
import sys


class CLITestV20ExtensionEndpointJSON(test_cli20.CLITestV20Base):
    def setUp(self):
        # need to mock before super because extensions loaded on instantiation
        self._mock_extension_loading()
        super(CLITestV20ExtensionEndpointJSON,
              self).setUp(plurals={'tags': 'tag'})

    def _mock_extension_loading(self):
        ext_pkg = 'neutronclient.common.extension'
        contrib = mock.patch(ext_pkg + '._discover_via_entry_points').start()
        contrib.return_value = [("endpoint", ep)]
        return contrib

    def test_ext_cmd_loaded(self):
        """Tests endpoint commands loaded."""
        shell.NeutronShell('2.0')
        ext_cmd = {'endpoint-list':
                   ep.EndpointList,
                   'endpoint-create':
                   ep.EndpointCreate,
                   'endpoint-update':
                   ep.EndpointUpdate,
                   'endpoint-delete':
                   ep.EndpointDelete,
                   'endpoint-show':
                   ep.EndpointShow}
        self.assertDictContainsSubset(ext_cmd, shell.COMMANDS['2.0'])

    def test_create_endpoint_name(self):
        # Create endpoint: ep1.
        resource = 'endpoint'
        cmd = ep.EndpointCreate(test_cli20.MyApp(
                                sys.stdout), None)
        name = 'ep1'
        args = [name]
        position_names = ['name']
        position_values = [name]
        self.assertRaises(Exception, self._test_create_resource, resource,
                          cmd, name, 'myid', args,
                          position_names, position_values)

    def test_create_endpoint_port(self):
        # Create endpoint: ep1.
        resource = 'endpoint'
        cmd = ep.EndpointCreate(test_cli20.MyApp(
                                sys.stdout), None)
        name = 'ep1'
        port = 'portid'
        args = [name, '--port', port]
        position_names = ['name', 'port_id']
        position_values = [name, port]
        self.assertRaises(Exception, self._test_create_resource, resource,
                          cmd, name, 'myid', args,
                          position_names, position_values)

    def test_create_endpoint_ip_mask(self):
        # Create endpoint: ep1.
        resource = 'endpoint'
        cmd = ep.EndpointCreate(test_cli20.MyApp(
                                sys.stdout), None)
        name = 'ep1'
        ip_mask = '0.0.0.0/0'
        args = [name, '--ip-mask', ip_mask]
        position_names = ['name', 'ip_mask']
        position_values = [name, ip_mask]
        self.assertRaises(Exception, self._test_create_resource, resource,
                          cmd, name, 'myid', args,
                          position_names, position_values)

    def test_create_endpoint_ip_port(self):
        # Create endpoint: ep1.
        resource = 'endpoint'
        cmd = ep.EndpointCreate(test_cli20.MyApp(
                                sys.stdout), None)
        name = 'ep1'
        ip_port = '0.0.0.0_80_8'
        args = [name, '--ip-port', 'ip=0.0.0.0,port=80,mask=8']
        position_names = ['name', 'ip_port']
        position_values = [name, ip_port]
        self.assertRaises(Exception, self._test_create_resource, resource,
                          cmd, name, 'myid', args,
                          position_names, position_values)

    def test_create_endpoint_epg(self):
        # Create endpoint: ep1.
        resource = 'endpoint'
        cmd = ep.EndpointCreate(test_cli20.MyApp(
                                sys.stdout), None)
        name = 'ep1'
        epg = [{'id': 'epgid'}]
        args = [name, '--endpoint-group', 'id=epgid']
        position_names = ['name', 'ep_groups']
        position_values = [name, epg]
        self.assertRaises(Exception, self._test_create_resource, resource,
                          cmd, name, 'myid', args,
                          position_names, position_values)

    def test_create_endpoint_port_epg(self):
        # Create endpoint: ep1.
        resource = 'endpoint'
        cmd = ep.EndpointCreate(test_cli20.MyApp(
                                sys.stdout), None)
        name = 'ep1'
        port = 'portid'
        epg = [{'id': 'epgid'}]
        args = [name, '--port', port, '--endpoint-group', 'id=epgid']
        position_names = ['name', 'port_id', 'ep_groups']
        position_values = [name, port, epg]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_endpoint_port_epg_name(self):
        # Create endpoint: ep1.
        resource = 'endpoint'
        cmd = ep.EndpointCreate(test_cli20.MyApp(
                                sys.stdout), None)
        name = 'ep1'
        port = 'portid'
        epg = [{'id': 'epgid'}]
        args = [name, '--port', port, '--endpoint-group', 'name=epgid']
        position_names = ['name', 'port_id', 'ep_groups']
        position_values = [name, port, epg]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_endpoint_ip_mask_epg(self):
        # Create endpoint: ep1.
        resource = 'endpoint'
        cmd = ep.EndpointCreate(test_cli20.MyApp(
                                sys.stdout), None)
        name = 'ep1'
        ip_mask = '0.0.0.0/0'
        epg = [{'id': 'epgid'}]
        args = [name, '--ip-mask', ip_mask, '--endpoint-group', 'id=epgid']
        position_names = ['name', 'ip_mask', 'ep_groups']
        position_values = [name, ip_mask, epg]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_endpoint_ip_mask_epg_name(self):
        # Create endpoint: ep1.
        resource = 'endpoint'
        cmd = ep.EndpointCreate(test_cli20.MyApp(
                                sys.stdout), None)
        name = 'ep1'
        ip_mask = '0.0.0.0/0'
        epg = [{'id': 'epgid'}]
        args = [name, '--ip-mask', ip_mask, '--endpoint-group', 'name=epgid']
        position_names = ['name', 'ip_mask', 'ep_groups']
        position_values = [name, ip_mask, epg]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_endpoint_ip_port_epg(self):
        # Create endpoint: ep1.
        resource = 'endpoint'
        cmd = ep.EndpointCreate(test_cli20.MyApp(
                                sys.stdout), None)
        name = 'ep1'
        ip_port = '0.0.0.0_80_8'
        epg = [{'id': 'epgid'}]
        args = [name, '--ip-port', 'ip=0.0.0.0,port=80,mask=8',
                '--endpoint-group', 'id=epgid']
        position_names = ['name', 'ip_port', 'ep_groups']
        position_values = [name, ip_port, epg]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_endpoint_ip_port_epg_name(self):
        # Create endpoint: ep1.
        resource = 'endpoint'
        cmd = ep.EndpointCreate(test_cli20.MyApp(
                                sys.stdout), None)
        name = 'ep1'
        ip_port = '0.0.0.0_80_8'
        epg = [{'id': 'epgid'}]
        args = [name, '--ip-port', 'ip=0.0.0.0,port=80,mask=8',
                '--endpoint-group', 'name=epgid']
        position_names = ['name', 'ip_port', 'ep_groups']
        position_values = [name, ip_port, epg]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_endpoint_mul_classfication(self):
        # Create endpoint: ep1.
        resource = 'endpoint'
        cmd = ep.EndpointCreate(test_cli20.MyApp(
                                sys.stdout), None)
        name = 'ep1'
        epg = [{'id': 'epgid'}]
        port = 'portid'
        ip_mask = '0.0.0.0/0'
        args = [name, '--port', port, '--ip-mask', ip_mask,
                '--endpoint-group', 'id=epgid']
        position_names = ['name', 'port_id', 'ip_mask', 'ep_groups']
        position_values = [name, port, ip_mask, epg]
        self.assertRaises(Exception, self._test_create_resource, resource,
                          cmd, name, 'myid', args,
                          position_names, position_values)

    def test_create_endpoint_invalid_ip_port(self):
        # Create endpoint: ep1.
        resource = 'endpoint'
        cmd = ep.EndpointCreate(test_cli20.MyApp(
                                sys.stdout), None)
        name = 'ep1'
        ip_port = '0.0.0.0_80_8'
        epg = [{'id': 'epgid'}]
        args = [name, '--ip-port', 'ip=0.0.0.0,port=80',
                '--endpoint-group', 'name=epgid']
        position_names = ['name', 'ip_port', 'ep_groups']
        position_values = [name, ip_port, epg]
        self.assertRaises(Exception, self._test_create_resource, resource,
                          cmd, name, 'myid', args,
                          position_names, position_values)

    def test_update_endpoint_name(self):
        # Update endpoint: myid --name
        resource = 'endpoint'
        cmd = ep.EndpointUpdate(test_cli20.MyApp(
                                      sys.stdout), None)
        args = ['myid', '--name', 'myep']
        values = {'name': 'myep'}
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_update_endpoint_add_epg(self):
        # Update endpoint: myid --add-endpoint-group
        resource = 'endpoint'
        cmd = ep.EndpointUpdate(test_cli20.MyApp(
                                      sys.stdout), None)
        args = ['myid', '--add-endpoint-group', 'id=epg']
        values = {'add_endpoint_groups': [{'id': 'epg'}]}
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_update_endpoint_remove_epg(self):
        # Update endpoint: myid --remove-endpoint-group
        resource = 'endpoint'
        cmd = ep.EndpointUpdate(test_cli20.MyApp(
                                      sys.stdout), None)
        args = ['myid', '--remove-endpoint-group', 'id=epg']
        values = {'remove_endpoint_groups': [{'id': 'epg'}]}
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_update_endpoint_add_epg_name(self):
        # Update endpoint: myid --add-endpoint-group
        resource = 'endpoint'
        cmd = ep.EndpointUpdate(test_cli20.MyApp(
                                      sys.stdout), None)
        args = ['myid', '--add-endpoint-group', 'name=epg']
        values = {'add_endpoint_groups': [{'id': 'epg'}]}
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_update_endpoint_remove_epg_name(self):
        # Update endpoint: myid --remove-endpoint-group
        resource = 'endpoint'
        cmd = ep.EndpointUpdate(test_cli20.MyApp(
                                      sys.stdout), None)
        args = ['myid', '--remove-endpoint-group', 'name=epg']
        values = {'remove_endpoint_groups': [{'id': 'epg'}]}
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_list_endpoints(self):
        # list endpoints: -D.
        resources = "endpoints"
        cmd = ep.EndpointList(test_cli20.MyApp(
                              sys.stdout), None)
        self._test_list_resources(resources, cmd, True)

    def test_list_endpoints_sort(self):
        # list endpoints:
        # --sort-key name --sort-key id --sort-key asc --sort-key desc
        resources = "endpoints"
        cmd = ep.EndpointList(test_cli20.MyApp(
                              sys.stdout), None)
        self._test_list_resources(resources, cmd,
                                  sort_key=["name", "id"],
                                  sort_dir=["asc", "desc"])

    def test_list_endpoints_limit(self):
        # list endpoints: -P.
        resources = "endpoints"
        cmd = ep.EndpointList(test_cli20.MyApp(
                              sys.stdout), None)
        self._test_list_resources(resources, cmd, page_size=1000)

    def test_delete_endpoint(self):
        # Delete endpoint: myid.
        resource = "endpoint"
        cmd = ep.EndpointDelete(test_cli20.MyApp(
                                sys.stdout), None)
        my_id = 'myid'
        args = [my_id]
        self._test_delete_resource(resource, cmd, my_id, args)

    def test_show_endpoint(self):
        # Show endpoint: --fields id.
        resource = 'endpoint'
        cmd = ep.EndpointShow(test_cli20.MyApp(
                              sys.stdout), None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id, args,
                                 ['id', 'name'])

    def test_create_endpoint_label(self):
        # Create endpoint: ep1.
        resource = 'endpoint'
        cmd = ep.EndpointCreate(test_cli20.MyApp(
                                sys.stdout), None)
        name = 'ep1'
        label = 'mylabel'
        args = [name, '--label', label]
        position_names = ['name', 'label']
        position_values = [name, label]
        self.assertRaises(Exception, self._test_create_resource, resource,
                          cmd, name, 'myid', args,
                          position_names, position_values)

    def test_create_endpoint_label_epg(self):
        # Create endpoint: ep1.
        resource = 'endpoint'
        cmd = ep.EndpointCreate(test_cli20.MyApp(
                                sys.stdout), None)
        name = 'ep1'
        label = 'mylabel'
        epg = [{'id': 'epgid'}]
        args = [name, '--label', label, '--endpoint-group', 'id=epgid']
        position_names = ['name', 'label', 'ep_groups']
        position_values = [name, label, epg]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_endpoint_label_epg_name(self):
        # Create endpoint: ep1.
        resource = 'endpoint'
        cmd = ep.EndpointCreate(test_cli20.MyApp(
                                sys.stdout), None)
        name = 'ep1'
        label = 'mylabel'
        epg = [{'id': 'epgid'}]
        args = [name, '--label', label, '--endpoint-group', 'name=epgid']
        position_names = ['name', 'label', 'ep_groups']
        position_values = [name, label, epg]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)
