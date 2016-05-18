# Copyright 2015 PLUMgrid, Inc. All Rights Reserved.
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
from networking_plumgrid.neutronclient.endpointgroup import (
    endpoint_group as endpointgrp)
from neutronclient import shell
import sys


class CLITestV20ExtensionEndpointGroupJSON(test_cli20.CLITestV20Base):
    def setUp(self):
        # need to mock before super because extensions loaded on instantiation
        self._mock_extension_loading()
        super(CLITestV20ExtensionEndpointGroupJSON,
              self).setUp(plurals={'tags': 'tag'})

    def _mock_extension_loading(self):
        ext_pkg = 'neutronclient.common.extension'
        contrib = mock.patch(ext_pkg + '._discover_via_entry_points').start()
        contrib.return_value = [("endpoint_group", endpointgrp)]
        return contrib

    def test_ext_cmd_loaded(self):
        """Tests endpoint group commands loaded."""
        shell.NeutronShell('2.0')
        ext_cmd = {'endpoint-group-list':
                   endpointgrp.EndpointGroupList,
                   'endpoint-group-create':
                   endpointgrp.EndpointGroupCreate,
                   'endpoint-group-update':
                   endpointgrp.EndpointGroupUpdate,
                   'endpoint-group-delete':
                   endpointgrp.EndpointGroupDelete,
                   'endpoint-group-show':
                   endpointgrp.EndpointGroupShow}
        self.assertDictContainsSubset(ext_cmd, shell.COMMANDS['2.0'])

    def test_create_endpoint_group_only_name(self):
        # Create endpointgroup: endpointgroup1.
        resource = 'endpoint_group'
        cmd = endpointgrp.EndpointGroupCreate(test_cli20.MyApp(
                                              sys.stdout), None)
        name = 'endpointgroup1'
        description = ''
        epg_type = 'vm_class'
        args = [name]
        position_names = ['name', 'description', 'endpoint_type']
        position_values = [name, description, epg_type]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_endpoint_group_with_description(self):
        # Create endpointgroup: endpointgroup1 with description.
        resource = 'endpoint_group'
        cmd = endpointgrp.EndpointGroupCreate(test_cli20.MyApp(
                                              sys.stdout), None)
        name = 'endpointgroup1'
        description = 'DESC'
        epg_type = 'vm_class'
        args = [name, '--description', description]
        position_names = ['name', 'description', 'endpoint_type']
        position_values = [name, description, epg_type]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_endpoint_group_with_description_and_type(self):
        # Create endpointgroup: endpointgroup1 with description and
        # endpoint type.
        resource = 'endpoint_group'
        cmd = endpointgrp.EndpointGroupCreate(test_cli20.MyApp(
                                              sys.stdout), None)
        name = 'endpointgroup1'
        description = 'DESC'
        epg_type = 'vm_ep'
        args = [name, '--description', description, '--type', epg_type]
        position_names = ['name', 'description', 'endpoint_type']
        position_values = [name, description, epg_type]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_endpoint_group_with_description_type_port_id(self):
        # Create endpointgroup: endpointgroup1 with description, endpoint
        # type and port using id.
        resource = 'endpoint_group'
        cmd = endpointgrp.EndpointGroupCreate(test_cli20.MyApp(
                                              sys.stdout), None)
        name = 'endpointgroup1'
        description = 'DESC'
        epg_type = 'vm_ep'
        ports = [{"id": "mypid"}]
        args = [name, '--description', description, '--type',
                epg_type, '--port', 'id=mypid']
        position_names = ['name', 'description', 'endpoint_type', 'ports']
        position_values = [name, description, epg_type, ports]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_endpoint_group_with_description_type_port_name(self):
        # Create endpointgroup: endpointgroup1 with description,
        # endpoint type and port using name.
        resource = 'endpoint_group'
        cmd = endpointgrp.EndpointGroupCreate(test_cli20.MyApp(
                                              sys.stdout), None)
        name = 'endpointgroup1'
        description = 'DESC'
        epg_type = 'vm_ep'
        ports = [{"id": "myportname"}]
        args = [name, '--description', description, '--type',
                epg_type, '--port', 'name=myportname']
        position_names = ['name', 'description', 'endpoint_type', 'ports']
        position_values = [name, description, epg_type, ports]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_endpoint_group_with_description_type_mul_port_ids(self):
        # Create endpointgroup: endpointgroup1 with description,
        # endpoint type and mulitple ports using ids.
        resource = 'endpoint_group'
        cmd = endpointgrp.EndpointGroupCreate(test_cli20.MyApp(
                                              sys.stdout), None)
        name = 'endpointgroup1'
        description = 'DESC'
        epg_type = 'vm_ep'
        ports = [{"id": "mypid1"}, {"id": "mypid2"}]
        args = [name, '--description', description, '--type',
                epg_type, '--port', 'id=mypid1', '--port', 'id=mypid2']
        position_names = ['name', 'description', 'endpoint_type', 'ports']
        position_values = [name, description, epg_type, ports]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_endpoint_group_with_description_type_mul_port_names(self):
        # Create endpointgroup: endpointgroup1 with description,
        # endpoint type and mulitple ports using names.
        resource = 'endpoint_group'
        cmd = endpointgrp.EndpointGroupCreate(test_cli20.MyApp(
                                              sys.stdout), None)
        name = 'endpointgroup1'
        description = 'DESC'
        epg_type = 'vm_ep'
        ports = [{"id": "myportname1"}, {"id": "myportname2"}]
        args = [name, '--description', description, '--type',
                epg_type, '--port', 'name=myportname1',
                '--port', 'name=myportname2']
        position_names = ['name', 'description', 'endpoint_type', 'ports']
        position_values = [name, description, epg_type, ports]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_endpoint_group_with_description_type_mul_port_hybrid(self):
        # Create endpointgroup: endpointgroup1 with description,
        # endpoint type and mulitple ports using ids/names.
        resource = 'endpoint_group'
        cmd = endpointgrp.EndpointGroupCreate(test_cli20.MyApp(
                                              sys.stdout), None)
        name = 'endpointgroup1'
        description = 'DESC'
        epg_type = 'vm_ep'
        ports = [{"id": "mypid1"}, {"id": "myportname2"}]
        args = [name, '--description', description, '--type',
                epg_type, '--port', 'id=mypid1', '--port', 'name=myportname2']
        position_names = ['name', 'description', 'endpoint_type', 'ports']
        position_values = [name, description, epg_type, ports]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_list_endpoint_groups(self):
        # list endpointgroups: -D.
        resources = "endpoint_groups"
        cmd = endpointgrp.EndpointGroupList(test_cli20.MyApp(
                                           sys.stdout), None)
        self._test_list_resources(resources, cmd, True)

    def test_list_endpoint_groups_sort(self):
        # list endpointgroups:
        # --sort-key name --sort-key id --sort-key asc --sort-key desc
        resources = "endpoint_groups"
        cmd = endpointgrp.EndpointGroupList(test_cli20.MyApp(
                                            sys.stdout), None)
        self._test_list_resources(resources, cmd,
                                  sort_key=["name", "id"],
                                  sort_dir=["asc", "desc"])

    def test_list_endpoint_groups_limit(self):
        # list endpointgroups: -P.
        resources = "endpoint_groups"
        cmd = endpointgrp.EndpointGroupList(test_cli20.MyApp(
                                            sys.stdout), None)
        self._test_list_resources(resources, cmd, page_size=1000)

    def test_delete_endpoint_group(self):
        # Delete endpointgroup: myid.
        resource = "endpoint_group"
        cmd = endpointgrp.EndpointGroupDelete(test_cli20.MyApp(
                                              sys.stdout), None)
        my_id = 'myid'
        args = [my_id]
        self._test_delete_resource(resource, cmd, my_id, args)

    def test_show_endpoint_group(self):
        # Show endpointgroup: --fields id.
        resource = 'endpoint_group'
        cmd = endpointgrp.EndpointGroupShow(test_cli20.MyApp(
                                           sys.stdout), None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id, args,
                                 ['id', 'name'])

    def test_update_endpoint_group_name(self):
        # Update endpointgroup: myid --name
        resource = 'endpoint_group'
        cmd = endpointgrp.EndpointGroupUpdate(test_cli20.MyApp(
                                              sys.stdout), None)
        args = ['myid', '--name', 'myepg']
        values = {'name': 'myepg'}
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_update_endpoint_group_description(self):
        # Update endpointgroup: myid --description
        resource = 'endpoint_group'
        cmd = endpointgrp.EndpointGroupUpdate(test_cli20.MyApp(
                                              sys.stdout), None)
        args = ['myid', '--description', 'myDESC']
        values = {'description': 'myDESC'}
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_update_endpoint_group_add_port_id(self):
        # Update endpointgroup: myid --add-ports id
        resource = 'endpoint_group'
        cmd = endpointgrp.EndpointGroupUpdate(test_cli20.MyApp(
                                              sys.stdout), None)
        args = ['myid', '--add-ports', 'id=mypid']
        values = {'add_ports': [{'id': 'mypid'}]}
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_update_endpoint_group_add_port_name(self):
        # Update endpointgroup: myid --add-ports name
        resource = 'endpoint_group'
        cmd = endpointgrp.EndpointGroupUpdate(test_cli20.MyApp(
                                              sys.stdout), None)
        args = ['myid', '--add-ports', 'name=myportname']
        values = {'add_ports': [{'id': 'myportname'}]}
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_update_endpoint_group_add_mul_port_ids(self):
        # Update endpointgroup: myid --add-ports id --add-ports id
        resource = 'endpoint_group'
        cmd = endpointgrp.EndpointGroupUpdate(test_cli20.MyApp(
                                              sys.stdout), None)
        args = ['myid', '--add-ports', 'id=mypid1', '--add-ports', 'id=mypid2']
        values = {'add_ports': [{'id': 'mypid1'}, {'id': 'mypid2'}]}
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_update_endpoint_group_add_mul_port_names(self):
        # Update endpointgroup: myid --add-ports name --add-ports name
        resource = 'endpoint_group'
        cmd = endpointgrp.EndpointGroupUpdate(test_cli20.MyApp(
                                              sys.stdout), None)
        args = ['myid', '--add-ports', 'name=myportname1',
                '--add-ports', 'name=myportname2']
        values = {'add_ports': [{'id': 'myportname1'}, {'id': 'myportname2'}]}
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_update_endpoint_group_add_mul_ports_hybrid(self):
        # Update endpointgroup: myid --add-ports id --add-ports name
        resource = 'endpoint_group'
        cmd = endpointgrp.EndpointGroupUpdate(test_cli20.MyApp(
                                              sys.stdout), None)
        args = ['myid', '--add-ports', 'id=mypid',
                '--add-ports', 'name=myportname']
        values = {'add_ports': [{'id': 'mypid'}, {'id': 'myportname'}]}
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_update_endpoint_group_remove_port_id(self):
        # Update endpointgroup: myid --remove-ports id
        resource = 'endpoint_group'
        cmd = endpointgrp.EndpointGroupUpdate(test_cli20.MyApp(
                                              sys.stdout), None)
        args = ['myid', '--remove-ports', 'id=mypid']
        values = {'remove_ports': [{'id': 'mypid'}]}
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_update_endpoint_group_remove_port_name(self):
        # Update endpointgroup: myid --remove-ports name
        resource = 'endpoint_group'
        cmd = endpointgrp.EndpointGroupUpdate(test_cli20.MyApp(
                                              sys.stdout), None)
        args = ['myid', '--remove-ports', 'name=myportname']
        values = {'remove_ports': [{'id': 'myportname'}]}
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_update_endpoint_group_remove_mul_port_ids(self):
        # Update endpointgroup: myid --remove-ports id --remove-ports id
        resource = 'endpoint_group'
        cmd = endpointgrp.EndpointGroupUpdate(test_cli20.MyApp(
                                              sys.stdout), None)
        args = ['myid', '--remove-ports', 'id=mypid1',
                '--remove-ports', 'id=mypid2']
        values = {'remove_ports': [{'id': 'mypid1'}, {'id': 'mypid2'}]}
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_update_endpoint_group_remove_mul_port_names(self):
        # Update endpointgroup: myid --remove-ports name --remove-ports name
        resource = 'endpoint_group'
        cmd = endpointgrp.EndpointGroupUpdate(test_cli20.MyApp(
                                              sys.stdout), None)
        args = ['myid', '--remove-ports', 'name=myportname1',
                '--remove-ports', 'name=myportname2']
        values = {'remove_ports': [{'id': 'myportname1'},
                 {'id': 'myportname2'}]}
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_update_endpoint_group_remove_mul_ports_hybrid(self):
        # Update endpointgroup: myid --remove-ports id --remove-ports name
        resource = 'endpoint_group'
        cmd = endpointgrp.EndpointGroupUpdate(test_cli20.MyApp(
                                              sys.stdout), None)
        args = ['myid', '--remove-ports', 'id=mypid',
                '--remove-ports', 'name=myportname']
        values = {'remove_ports': [{'id': 'mypid'}, {'id': 'myportname'}]}
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_update_endpoint_group_add_remove_mul_ports_hybrid(self):
        # Update endpointgroup: myid --add-ports id --remove-ports name
        resource = 'endpoint_group'
        cmd = endpointgrp.EndpointGroupUpdate(test_cli20.MyApp(
                                              sys.stdout), None)
        args = ['myid', '--add-ports', 'id=mypid',
                '--remove-ports', 'name=myportname']
        values = {'add_ports': [{'id': 'mypid'}],
                  'remove_ports': [{'id': 'myportname'}]}
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)
