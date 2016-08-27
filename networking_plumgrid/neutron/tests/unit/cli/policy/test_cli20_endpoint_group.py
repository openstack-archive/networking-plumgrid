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
    endpoint_group as epg)
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
        contrib.return_value = [("endpoint_group", epg)]
        return contrib

    def test_ext_cmd_loaded(self):
        """Tests endpoint group commands loaded."""
        shell.NeutronShell('2.0')
        ext_cmd = {'endpoint-group-list':
                   epg.EndpointGroupList,
                   'endpoint-group-create':
                   epg.EndpointGroupCreate,
                   'endpoint-group-update':
                   epg.EndpointGroupUpdate,
                   'endpoint-group-delete':
                   epg.EndpointGroupDelete,
                   'endpoint-group-show':
                   epg.EndpointGroupShow}
        self.assertDictContainsSubset(ext_cmd, shell.COMMANDS['2.0'])

    def test_create_endpoint_group_name(self):
        # Create endpoint group: epg1.
        resource = 'endpoint_group'
        cmd = epg.EndpointGroupCreate(test_cli20.MyApp(
                                      sys.stdout), None)
        name = 'epg1'
        args = [name]
        position_names = ['name']
        position_values = [name]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_endpoint_group_description(self):
        # Create endpoint group: epg1.
        resource = 'endpoint_group'
        cmd = epg.EndpointGroupCreate(test_cli20.MyApp(
                                      sys.stdout), None)
        name = 'epg1'
        description = 'epg desc'
        args = [name, '--description', description]
        position_names = ['name', 'description']
        position_values = [name, description]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_endpoint_group_tag(self):
        # Create endpoint group: epg1.
        resource = 'endpoint_group'
        cmd = epg.EndpointGroupCreate(test_cli20.MyApp(
                                      sys.stdout), None)
        name = 'epg1'
        tag = 'tagid'
        args = [name, '--tag', tag]
        position_names = ['name', 'policy_tag_id']
        position_values = [name, tag]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_update_endpoint_group_name(self):
        # Update endpointgroup: myid --name
        resource = 'endpoint_group'
        cmd = epg.EndpointGroupUpdate(test_cli20.MyApp(
                                      sys.stdout), None)
        args = ['myid', '--name', 'myepg']
        values = {'name': 'myepg'}
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_update_endpoint_group_desc(self):
        # Update endpointgroup: myid --description
        resource = 'endpoint_group'
        cmd = epg.EndpointGroupUpdate(test_cli20.MyApp(
                                      sys.stdout), None)
        args = ['myid', '--description', 'myepg desc']
        values = {'description': 'myepg desc'}
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_update_endpoint_group_add_tag(self):
        # Update endpointgroup: myid --add-tag
        resource = 'endpoint_group'
        cmd = epg.EndpointGroupUpdate(test_cli20.MyApp(
                                      sys.stdout), None)
        args = ['myid', '--add-tag', 'tagid']
        values = {'add_tag': 'tagid'}
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_update_endpoint_group_remove_tag(self):
        # Update endpointgroup: myid --remove-tag
        resource = 'endpoint_group'
        cmd = epg.EndpointGroupUpdate(test_cli20.MyApp(
                                      sys.stdout), None)
        args = ['myid', '--remove-tag', 'tagid']
        values = {'remove_tag': 'tagid'}
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_list_endpoint_groups(self):
        # list endpointgroups: -D.
        resources = "endpoint_groups"
        cmd = epg.EndpointGroupList(test_cli20.MyApp(
                                    sys.stdout), None)
        self._test_list_resources(resources, cmd, True)

    def test_list_endpoint_groups_sort(self):
        # list endpointgroups:
        # --sort-key name --sort-key id --sort-key asc --sort-key desc
        resources = "endpoint_groups"
        cmd = epg.EndpointGroupList(test_cli20.MyApp(
                                    sys.stdout), None)
        self._test_list_resources(resources, cmd,
                                  sort_key=["name", "id"],
                                  sort_dir=["asc", "desc"])

    def test_list_endpoint_groups_limit(self):
        # list endpointgroups: -P.
        resources = "endpoint_groups"
        cmd = epg.EndpointGroupList(test_cli20.MyApp(
                                    sys.stdout), None)
        self._test_list_resources(resources, cmd, page_size=1000)

    def test_delete_endpoint_group(self):
        # Delete endpointgroup: myid.
        resource = "endpoint_group"
        cmd = epg.EndpointGroupDelete(test_cli20.MyApp(
                                      sys.stdout), None)
        my_id = 'myid'
        args = [my_id]
        self._test_delete_resource(resource, cmd, my_id, args)

    def test_show_endpoint_group(self):
        # Show endpointgroup: --fields id.
        resource = 'endpoint_group'
        cmd = epg.EndpointGroupShow(test_cli20.MyApp(
                                    sys.stdout), None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id, args,
                                 ['id', 'name'])
