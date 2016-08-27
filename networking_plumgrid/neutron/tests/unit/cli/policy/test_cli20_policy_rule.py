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
    policy_rule as pr)
from neutronclient import shell
import sys


class CLITestV20ExtensionPolicyRuleJSON(test_cli20.CLITestV20Base):
    def setUp(self):
        # need to mock before super because extensions loaded on instantiation
        self._mock_extension_loading()
        super(CLITestV20ExtensionPolicyRuleJSON,
              self).setUp(plurals={'tags': 'tag'})

    def _mock_extension_loading(self):
        ext_pkg = 'neutronclient.common.extension'
        contrib = mock.patch(ext_pkg + '._discover_via_entry_points').start()
        contrib.return_value = [("policy_rule", pr)]
        return contrib

    def test_ext_cmd_loaded(self):
        """Tests policy rule commands loaded."""
        shell.NeutronShell('2.0')
        ext_cmd = {'policy-rule-list':
                   pr.PolicyRuleList,
                   'policy-rule-create':
                   pr.PolicyRuleCreate,
                   'policy-rule-delete':
                   pr.PolicyRuleDelete,
                   'policy-rule-show':
                   pr.PolicyRuleShow}
        self.assertDictContainsSubset(ext_cmd, shell.COMMANDS['2.0'])

    def test_create_policy_rule_name(self):
        # Create policy rule: pr1.
        resource = 'policy_rule'
        cmd = pr.PolicyRuleCreate(test_cli20.MyApp(
                                  sys.stdout), None)
        name = 'pr1'
        args = [name]
        position_names = ['name']
        position_values = [name]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_policy_rule_src_grp(self):
        # Create policy rule: pr1.
        resource = 'policy_rule'
        cmd = pr.PolicyRuleCreate(test_cli20.MyApp(
                                  sys.stdout), None)
        name = 'pr1'
        src_grp = 'epg1'
        args = [name, '--src-grp', src_grp]
        position_names = ['name', 'src_grp']
        position_values = [name, src_grp]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_policy_rule_dst_grp(self):
        # Create policy rule: pr1.
        resource = 'policy_rule'
        cmd = pr.PolicyRuleCreate(test_cli20.MyApp(
                                  sys.stdout), None)
        name = 'pr1'
        dst_grp = 'epg1'
        args = [name, '--dst-grp', dst_grp]
        position_names = ['name', 'dst_grp']
        position_values = [name, dst_grp]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_policy_rule_proto_any(self):
        # Create policy rule: pr1.
        resource = 'policy_rule'
        cmd = pr.PolicyRuleCreate(test_cli20.MyApp(
                                  sys.stdout), None)
        name = 'pr1'
        proto = 'any'
        args = [name, '--protocol', proto]
        position_names = ['name', 'protocol']
        position_values = [name, proto]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_policy_rule_proto_tcp(self):
        # Create policy rule: pr1.
        resource = 'policy_rule'
        cmd = pr.PolicyRuleCreate(test_cli20.MyApp(
                                  sys.stdout), None)
        name = 'pr1'
        proto = 'tcp'
        args = [name, '--protocol', proto]
        position_names = ['name', 'protocol']
        position_values = [name, proto]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_policy_rule_proto_udp(self):
        # Create policy rule: pr1.
        resource = 'policy_rule'
        cmd = pr.PolicyRuleCreate(test_cli20.MyApp(
                                  sys.stdout), None)
        name = 'pr1'
        proto = 'udp'
        args = [name, '--protocol', proto]
        position_names = ['name', 'protocol']
        position_values = [name, proto]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_policy_rule_proto_invalid(self):
        # Create policy rule: pr1.
        resource = 'policy_rule'
        cmd = pr.PolicyRuleCreate(test_cli20.MyApp(
                                  sys.stdout), None)
        name = 'pr1'
        proto = 'invalid'
        args = [name, '--protocol', proto]
        position_names = ['name', 'protocol']
        position_values = [name, proto]
        self.assertRaises(Exception, self._test_create_resource, resource,
                          cmd, name, 'myid', args,
                          position_names, position_values)

    def test_create_policy_rule_action_allow(self):
        # Create policy rule: pr1.
        resource = 'policy_rule'
        cmd = pr.PolicyRuleCreate(test_cli20.MyApp(
                                  sys.stdout), None)
        name = 'pr1'
        action = 'allow'
        args = [name, '--action', action]
        position_names = ['name', 'action']
        position_values = [name, action]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_policy_rule_action_copy(self):
        # Create policy rule: pr1.
        resource = 'policy_rule'
        cmd = pr.PolicyRuleCreate(test_cli20.MyApp(
                                  sys.stdout), None)
        name = 'pr1'
        action = 'copy'
        args = [name, '--action', action]
        position_names = ['name', 'action']
        position_values = [name, action]
        self.assertRaises(Exception, self._test_create_resource, resource,
                          cmd, name, 'myid', args,
                          position_names, position_values)

    def test_create_policy_rule_action_invalid(self):
        # Create policy rule: pr1.
        resource = 'policy_rule'
        cmd = pr.PolicyRuleCreate(test_cli20.MyApp(
                                  sys.stdout), None)
        name = 'pr1'
        action = 'invalid'
        args = [name, '--action', action]
        position_names = ['name', 'action']
        position_values = [name, action]
        self.assertRaises(Exception, self._test_create_resource, resource,
                          cmd, name, 'myid', args,
                          position_names, position_values)

    def test_create_policy_rule_action_target(self):
        # Create policy rule: pr1.
        resource = 'policy_rule'
        cmd = pr.PolicyRuleCreate(test_cli20.MyApp(
                                  sys.stdout), None)
        name = 'pr1'
        action_target = 'ps1'
        args = [name, '--action-target', action_target]
        position_names = ['name', 'action_target']
        position_values = [name, action_target]
        self.assertRaises(Exception, self._test_create_resource, resource,
                          cmd, name, 'myid', args,
                          position_names, position_values)

    def test_create_policy_rule_remote_action_target(self):
        # Create policy rule: pr1.
        resource = 'policy_rule'
        cmd = pr.PolicyRuleCreate(test_cli20.MyApp(
                                  sys.stdout), None)
        name = 'pr1'
        action_target = 'tenant:ps1'
        args = [name, '--action-target', action_target]
        position_names = ['name', 'action_target']
        position_values = [name, action_target]
        self.assertRaises(Exception, self._test_create_resource, resource,
                          cmd, name, 'myid', args,
                          position_names, position_values)

    def test_create_policy_rule_copy_action_target(self):
        resource = 'policy_rule'
        cmd = pr.PolicyRuleCreate(test_cli20.MyApp(
                                  sys.stdout), None)
        name = 'pr1'
        action_target = 'ps1'
        action = 'copy'
        args = [name, '--action-target', action_target, '--action', action]
        position_names = ['name', 'action_target', 'action']
        position_values = [name, action_target, action]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_policy_rule_copy_remote_action_target(self):
        resource = 'policy_rule'
        cmd = pr.PolicyRuleCreate(test_cli20.MyApp(
                                  sys.stdout), None)
        name = 'pr1'
        action_target = 'tenant:ps1'
        action = 'copy'
        args = [name, '--action-target', action_target, '--action', action]
        position_names = ['name', 'action_target', 'action']
        position_values = [name, action_target, action]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_policy_rule_copy_invalid_remote_action_target(self):
        resource = 'policy_rule'
        cmd = pr.PolicyRuleCreate(test_cli20.MyApp(
                                  sys.stdout), None)
        name = 'pr1'
        action_target = 'tenant:ps1:invalid'
        action = 'copy'
        args = [name, '--action-target', action_target, '--action', action]
        position_names = ['name', 'action_target', 'action']
        position_values = [name, action_target, action]
        self.assertRaises(Exception, self._test_create_resource, resource,
                          cmd, name, 'myid', args,
                          position_names, position_values)

    def test_create_policy_rule_allow_action_target(self):
        resource = 'policy_rule'
        cmd = pr.PolicyRuleCreate(test_cli20.MyApp(
                                  sys.stdout), None)
        name = 'pr1'
        action_target = 'ps1'
        action = 'allow'
        args = [name, '--action-target', action_target, '--action', action]
        position_names = ['name', 'action_target', 'action']
        position_values = [name, action_target, action]
        self.assertRaises(Exception, self._test_create_resource, resource,
                          cmd, name, 'myid', args,
                          position_names, position_values)

    def test_create_policy_rule_sgt(self):
        # Create policy rule: pr1.
        resource = 'policy_rule'
        cmd = pr.PolicyRuleCreate(test_cli20.MyApp(
                                  sys.stdout), None)
        name = 'pr1'
        args = [name, '--sgt']
        position_names = ['name']
        position_values = [name]
        self.assertRaises(Exception, self._test_create_resource, resource,
                          cmd, name, 'myid', args,
                          position_names, position_values)

    def test_create_policy_rule_dgt(self):
        # Create policy rule: pr1.
        resource = 'policy_rule'
        cmd = pr.PolicyRuleCreate(test_cli20.MyApp(
                                  sys.stdout), None)
        name = 'pr1'
        args = [name, '--dgt']
        position_names = ['name']
        position_values = [name]
        self.assertRaises(Exception, self._test_create_resource, resource,
                          cmd, name, 'myid', args,
                          position_names, position_values)

    def test_create_policy_rule_tag(self):
        resource = 'policy_rule'
        cmd = pr.PolicyRuleCreate(test_cli20.MyApp(
                                  sys.stdout), None)
        name = 'pr1'
        tag = 'ptag1'
        args = [name, '--tag', tag]
        position_names = ['name', 'tag']
        position_values = [name, tag]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_policy_rule_src_port_range(self):
        resource = 'policy_rule'
        cmd = pr.PolicyRuleCreate(test_cli20.MyApp(
                                  sys.stdout), None)
        name = 'pr1'
        src_port_range = '1-65535'
        args = [name, '--src-port-range', src_port_range]
        position_names = ['name', 'src_port_range']
        position_values = [name, src_port_range]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_policy_rule_dst_port_range(self):
        resource = 'policy_rule'
        cmd = pr.PolicyRuleCreate(test_cli20.MyApp(
                                  sys.stdout), None)
        name = 'pr1'
        dst_port_range = '1-65535'
        args = [name, '--dst-port-range', dst_port_range]
        position_names = ['name', 'dst_port_range']
        position_values = [name, dst_port_range]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_list_policy_rules(self):
        # list policy rules: -D.
        resources = "policy_rules"
        cmd = pr.PolicyRuleList(test_cli20.MyApp(
                                sys.stdout), None)
        self._test_list_resources(resources, cmd, True)

    def test_list_policy_rules_sort(self):
        # list policy rules:
        # --sort-key name --sort-key id --sort-key asc --sort-key desc
        resources = "policy_rules"
        cmd = pr.PolicyRuleList(test_cli20.MyApp(
                                sys.stdout), None)
        self._test_list_resources(resources, cmd,
                                  sort_key=["name", "id"],
                                  sort_dir=["asc", "desc"])

    def test_list_policy_rules_limit(self):
        # list policy rules: -P.
        resources = "policy_rules"
        cmd = pr.PolicyRuleList(test_cli20.MyApp(
                                sys.stdout), None)
        self._test_list_resources(resources, cmd, page_size=1000)

    def test_delete_policy_rule(self):
        # Delete policy rule: myid.
        resource = "policy_rule"
        cmd = pr.PolicyRuleDelete(test_cli20.MyApp(
                                  sys.stdout), None)
        my_id = 'myid'
        args = [my_id]
        self._test_delete_resource(resource, cmd, my_id, args)

    def test_show_policy_rule(self):
        # Show policy rule: --fields id.
        resource = 'policy_rule'
        cmd = pr.PolicyRuleShow(test_cli20.MyApp(
                                sys.stdout), None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id, args,
                                 ['id', 'name'])
