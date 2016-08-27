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
    policy_tag as ptag)
from neutronclient import shell
import sys


class CLITestV20ExtensionPolicyTagJSON(test_cli20.CLITestV20Base):
    def setUp(self):
        # need to mock before super because extensions loaded on instantiation
        self._mock_extension_loading()
        super(CLITestV20ExtensionPolicyTagJSON,
              self).setUp(plurals={'tags': 'tag'})

    def _mock_extension_loading(self):
        ext_pkg = 'neutronclient.common.extension'
        contrib = mock.patch(ext_pkg + '._discover_via_entry_points').start()
        contrib.return_value = [("policy_tag", ptag)]
        return contrib

    def test_ext_cmd_loaded(self):
        """Tests policy tag commands loaded."""
        shell.NeutronShell('2.0')
        ext_cmd = {'policy-tag-list':
                   ptag.PolicyTagList,
                   'policy-tag-create':
                   ptag.PolicyTagCreate,
                   'policy-tag-update':
                   ptag.PolicyTagUpdate,
                   'policy-tag-delete':
                   ptag.PolicyTagDelete,
                   'policy-tag-show':
                   ptag.PolicyTagShow}
        self.assertDictContainsSubset(ext_cmd, shell.COMMANDS['2.0'])

    def test_create_policy_tag_name(self):
        # Create policy tag: ptag1.
        resource = 'policy_tag'
        cmd = ptag.PolicyTagCreate(test_cli20.MyApp(
                                   sys.stdout), None)
        name = 'ptag1'
        args = [name]
        position_names = ['name']
        position_values = [name]
        self.assertRaises(Exception, self._test_create_resource, resource,
                          cmd, name, 'myid', args,
                          position_names, position_values)

    def test_create_policy_tag_desc(self):
        # Create policy tag: ptag1.
        resource = 'policy_tag'
        cmd = ptag.PolicyTagCreate(test_cli20.MyApp(
                                   sys.stdout), None)
        name = 'ptag1'
        description = 'ptag1:desc'
        args = [name, '--description', description]
        position_names = ['name', 'description']
        position_values = [name, description]
        self.assertRaises(Exception, self._test_create_resource, resource,
                          cmd, name, 'myid', args,
                          position_names, position_values)

    def test_create_policy_tag_type_nsh(self):
        # Create policy tag: ptag1.
        resource = 'policy_tag'
        cmd = ptag.PolicyTagCreate(test_cli20.MyApp(
                                   sys.stdout), None)
        name = 'ptag1'
        ptag_type = 'nsh'
        args = [name, '--type', ptag_type]
        position_names = ['name', 'tag_type']
        position_values = [name, ptag_type]
        self.assertRaises(Exception, self._test_create_resource, resource,
                          cmd, name, 'myid', args,
                          position_names, position_values)

    def test_create_policy_tag_type_dot1q(self):
        # Create policy tag: ptag1.
        resource = 'policy_tag'
        cmd = ptag.PolicyTagCreate(test_cli20.MyApp(
                                   sys.stdout), None)
        name = 'ptag1'
        ptag_type = 'dot1q'
        args = [name, '--type', ptag_type]
        position_names = ['name', 'tag_type']
        position_values = [name, ptag_type]
        self.assertRaises(Exception, self._test_create_resource, resource,
                          cmd, name, 'myid', args,
                          position_names, position_values)

    def test_create_policy_tag_type_floatingip(self):
        # Create policy tag: ptag1.
        resource = 'policy_tag'
        cmd = ptag.PolicyTagCreate(test_cli20.MyApp(
                                   sys.stdout), None)
        name = 'ptag1'
        ptag_type = 'fip'
        args = [name, '--type', ptag_type]
        position_names = ['name', 'tag_type']
        position_values = [name, ptag_type]
        self.assertRaises(Exception, self._test_create_resource, resource,
                          cmd, name, 'myid', args,
                          position_names, position_values)

    def test_create_policy_tag(self):
        # Create policy tag: ptag1.
        resource = 'policy_tag'
        cmd = ptag.PolicyTagCreate(test_cli20.MyApp(
                                   sys.stdout), None)
        name = 'ptag1'
        ptag_type = 'nsh'
        tag_id = '20'
        args = [name, '--type', ptag_type, '--tag-id', tag_id]
        position_names = ['name', 'tag_type', 'tag_id']
        position_values = [name, ptag_type, tag_id]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_policy_tag_floatingip(self):
        # Create policy tag: ptag1.
        resource = 'policy_tag'
        cmd = ptag.PolicyTagCreate(test_cli20.MyApp(
                                   sys.stdout), None)
        name = 'ptag1'
        ptag_type = 'fip'
        floatingip = 'fipid'
        args = [name, '--type', ptag_type, '--floating-ip', floatingip]
        position_names = ['name', 'tag_type', 'floatingip_id']
        position_values = [name, ptag_type, floatingip]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_policy_tag_type_fip_tag_id(self):
        # Create policy tag: ptag1.
        resource = 'policy_tag'
        cmd = ptag.PolicyTagCreate(test_cli20.MyApp(
                                   sys.stdout), None)
        name = 'ptag1'
        ptag_type = 'fip'
        floatingip = 'fipid'
        tag_id = '20'
        args = [name, '--type', ptag_type, '--floating-ip', floatingip,
                '--tag-id', tag_id]
        position_names = ['name', 'tag_type', 'floatingip_id', 'tag_id']
        position_values = [name, ptag_type, floatingip, tag_id]
        self.assertRaises(Exception, self._test_create_resource, resource,
                          cmd, name, 'myid', args,
                          position_names, position_values)

    def test_create_policy_tag_type_nsh_fip(self):
        # Create policy tag: ptag1.
        resource = 'policy_tag'
        cmd = ptag.PolicyTagCreate(test_cli20.MyApp(
                                   sys.stdout), None)
        name = 'ptag1'
        ptag_type = 'nsh'
        floatingip = 'fipid'
        tag_id = '20'
        args = [name, '--type', ptag_type, '--floating-ip', floatingip,
                '--tag-id', tag_id]
        position_names = ['name', 'tag_type', 'floatingip_id', 'tag_id']
        position_values = [name, ptag_type, floatingip, tag_id]
        self.assertRaises(Exception, self._test_create_resource, resource,
                          cmd, name, 'myid', args,
                          position_names, position_values)

    def test_create_policy_tag_type_dot1q_fip(self):
        # Create policy tag: ptag1.
        resource = 'policy_tag'
        cmd = ptag.PolicyTagCreate(test_cli20.MyApp(
                                   sys.stdout), None)
        name = 'ptag1'
        ptag_type = 'dot1q'
        floatingip = 'fipid'
        tag_id = '20'
        args = [name, '--type', ptag_type, '--floating-ip', floatingip,
                '--tag-id', tag_id]
        position_names = ['name', 'tag_type', 'floatingip_id', 'tag_id']
        position_values = [name, ptag_type, floatingip, tag_id]
        self.assertRaises(Exception, self._test_create_resource, resource,
                          cmd, name, 'myid', args,
                          position_names, position_values)

    def test_create_policy_tag_router_id(self):
        # Create policy tag: ptag1.
        resource = 'policy_tag'
        cmd = ptag.PolicyTagCreate(test_cli20.MyApp(
                                   sys.stdout), None)
        name = 'ptag1'
        ptag_type = 'fip'
        floatingip = 'fipid'
        routerid = 'routerid'
        args = [name, '--type', ptag_type, '--floating-ip', floatingip,
                '--router-id', routerid]
        position_names = ['name', 'tag_type', 'floatingip_id', 'router_id']
        position_values = [name, ptag_type, floatingip, routerid]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_policy_tag_invalid_tag_type(self):
        # Create policy tag: ptag1.
        resource = 'policy_tag'
        cmd = ptag.PolicyTagCreate(test_cli20.MyApp(
                                   sys.stdout), None)
        name = 'ptag1'
        ptag_type = 'invalid'
        args = [name, '--type', ptag_type]
        position_names = ['name', 'tag_type']
        position_values = [name, ptag_type]
        self.assertRaises(Exception, self._test_create_resource, resource,
                          cmd, name, 'myid', args,
                          position_names, position_values)

    def test_list_policy_tags(self):
        # list policytags: -D.
        resources = "policy_tags"
        cmd = ptag.PolicyTagList(test_cli20.MyApp(
                                 sys.stdout), None)
        self._test_list_resources(resources, cmd, True)

    def test_list_policy_tags_sort(self):
        # list policytags:
        # --sort-key name --sort-key id --sort-key asc --sort-key desc
        resources = "policy_tags"
        cmd = ptag.PolicyTagList(test_cli20.MyApp(
                                 sys.stdout), None)
        self._test_list_resources(resources, cmd,
                                  sort_key=["name", "id"],
                                  sort_dir=["asc", "desc"])

    def test_list_policy_tags_limit(self):
        # list policytags: -P.
        resources = "policy_tags"
        cmd = ptag.PolicyTagList(test_cli20.MyApp(
                                 sys.stdout), None)
        self._test_list_resources(resources, cmd, page_size=1000)

    def test_delete_policy_tag(self):
        # Delete policytag: myid.
        resource = "policy_tag"
        cmd = ptag.PolicyTagDelete(test_cli20.MyApp(
                                   sys.stdout), None)
        my_id = 'myid'
        args = [my_id]
        self._test_delete_resource(resource, cmd, my_id, args)

    def test_show_policy_tag(self):
        # Show policytag: --fields id.
        resource = 'policy_tag'
        cmd = ptag.PolicyTagShow(test_cli20.MyApp(
                                 sys.stdout), None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id, args,
                                 ['id', 'name'])

    def test_update_policy_tag_name(self):
        # Update policytag: myid --name
        resource = 'policy_tag'
        cmd = ptag.PolicyTagUpdate(test_cli20.MyApp(
                                   sys.stdout), None)
        args = ['myid', '--name', 'myptag']
        values = {'name': 'myptag'}
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)
