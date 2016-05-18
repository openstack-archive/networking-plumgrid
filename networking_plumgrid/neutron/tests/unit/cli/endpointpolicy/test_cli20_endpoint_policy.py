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
from networking_plumgrid.neutronclient.endpointpolicy import (
    endpoint_policy as endpointplcy)
from neutronclient import shell
import sys


class CLITestV20ExtensionEndpointPolicyJSON(test_cli20.CLITestV20Base):
    def setUp(self):
        # need to mock before super because extensions loaded on instantiation
        self._mock_extension_loading()
        super(CLITestV20ExtensionEndpointPolicyJSON,
              self).setUp(plurals={'tags': 'tag'})

    def _mock_extension_loading(self):
        ext_pkg = 'neutronclient.common.extension'
        contrib = mock.patch(ext_pkg + '._discover_via_entry_points').start()
        contrib.return_value = [("endpoint_policy", endpointplcy)]
        return contrib

    def test_ext_cmd_loaded(self):
        """Tests endpoint policy commands loaded."""
        shell.NeutronShell('2.0')
        ext_cmd = {'endpoint-policy-list':
                   endpointplcy.EndpointPolicyList,
                   'endpoint-policy-create':
                   endpointplcy.EndpointPolicyCreate,
                   'endpoint-policy-delete':
                   endpointplcy.EndpointPolicyDelete,
                   'endpoint-policy-show':
                   endpointplcy.EndpointPolicyShow}
        self.assertDictContainsSubset(ext_cmd, shell.COMMANDS['2.0'])

    def test_list_endpoint_policies(self):
        # list endpointpolicies: -D.
        resources = "endpoint_policies"
        cmd = endpointplcy.EndpointPolicyList(test_cli20.MyApp(
                                              sys.stdout), None)
        self._test_list_resources(resources, cmd, True)

    def test_list_endpoint_policies_sort(self):
        # list endpointpolicies:
        # --sort-key name --sort-key id --sort-key asc --sort-key desc
        resources = "endpoint_policies"
        cmd = endpointplcy.EndpointPolicyList(test_cli20.MyApp(
                                              sys.stdout), None)
        self._test_list_resources(resources, cmd,
                                  sort_key=["name", "id"],
                                  sort_dir=["asc", "desc"])

    def test_list_endpoint_policies_limit(self):
        # list endpointpolicies: -P.
        resources = "endpoint_policies"
        cmd = endpointplcy.EndpointPolicyList(test_cli20.MyApp(
                                              sys.stdout), None)
        self._test_list_resources(resources, cmd, page_size=1000)

    def test_delete_endpoint_policy(self):
        # Delete endpointpolicy: myid.
        resource = "endpoint_policy"
        cmd = endpointplcy.EndpointPolicyDelete(test_cli20.MyApp(
                                                sys.stdout), None)
        my_id = 'myid'
        args = [my_id]
        self._test_delete_resource(resource, cmd, my_id, args)

    def test_show_endpoint_policy(self):
        # Show endpointpolicy: --fields id.
        resource = 'endpoint_policy'
        cmd = endpointplcy.EndpointPolicyShow(test_cli20.MyApp(
                                             sys.stdout), None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id, args,
                                 ['id', 'name'])

    def test_create_endpoint_policy(self):
        # Create endpointpolicy: endpointpolicy1.
        resource = 'endpoint_policy'
        cmd = endpointplcy.EndpointPolicyCreate(test_cli20.MyApp(
                                                sys.stdout), None)
        name = 'endpointpolicy1'
        service_epg = 'myserviceepg'
        args = [name, '--service-endpoint-group', service_epg]
        position_names = ['name', 'service_endpoint_group']
        position_values = [name, service_epg]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_endpoint_policy_only_name(self):
        # Create endpointpolicy: endpointpolicy1.
        resource = 'endpoint_policy'
        cmd = endpointplcy.EndpointPolicyCreate(test_cli20.MyApp(
                                                sys.stdout), None)
        name = 'endpointpolicy1'
        args = [name]
        position_names = ['name']
        position_values = [name]
        self.assertRaises(Exception, self._test_create_resource, resource,
                          cmd, name, 'myid', args,
                          position_names, position_values)

    def test_create_endpoint_policy_with_src_grp(self):
        # Create endpointpolicy: endpointpolicy1 --source-group.
        resource = 'endpoint_policy'
        cmd = endpointplcy.EndpointPolicyCreate(test_cli20.MyApp(
                                                sys.stdout), None)
        name = 'endpointpolicy1'
        service_epg = 'myserviceepg'
        src_grp = 'mysrcgrp'
        args = [name, '--service-endpoint-group', service_epg,
                '--source-group', src_grp]
        position_names = ['name', 'service_endpoint_group', 'src_grp']
        position_values = [name, service_epg, src_grp]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_endpoint_policy_with_dst_grp(self):
        # Create endpointpolicy: endpointpolicy1 --destination-group.
        resource = 'endpoint_policy'
        cmd = endpointplcy.EndpointPolicyCreate(test_cli20.MyApp(
                                                sys.stdout), None)
        name = 'endpointpolicy1'
        service_epg = 'myserviceepg'
        dst_grp = 'mydstgrp'
        args = [name, '--service-endpoint-group', service_epg,
                '--destination-group', dst_grp]
        position_names = ['name', 'service_endpoint_group', 'dst_grp']
        position_values = [name, service_epg, dst_grp]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_endpoint_policy_with_protocol(self):
        # Create endpointpolicy: endpointpolicy1 --protocol.
        resource = 'endpoint_policy'
        cmd = endpointplcy.EndpointPolicyCreate(test_cli20.MyApp(
                                                sys.stdout), None)
        name = 'endpointpolicy1'
        service_epg = 'myserviceepg'
        protocol = 'icmp'
        args = [name, '--service-endpoint-group', service_epg,
                '--protocol', protocol]
        position_names = ['name', 'service_endpoint_group', 'protocol']
        position_values = [name, service_epg, protocol]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_endpoint_policy_with_invalid_protocol(self):
        # Create endpointpolicy: endpointpolicy1 --protocol.
        resource = 'endpoint_policy'
        cmd = endpointplcy.EndpointPolicyCreate(test_cli20.MyApp(
                                                sys.stdout), None)
        name = 'endpointpolicy1'
        service_epg = 'myserviceepg'
        protocol = 'fake-protocol'
        args = [name, '--service-endpoint-group', service_epg,
                '--protocol', protocol]
        position_names = ['name', 'service_endpoint_group', 'protocol']
        position_values = [name, service_epg, protocol]
        self.assertRaises(Exception, self._test_create_resource, resource,
                          cmd, name, 'myid', args,
                          position_names, position_values)

    def test_create_endpoint_policy_with_source_port_range(self):
        # Create endpointpolicy: endpointpolicy1 --source-port-range.
        resource = 'endpoint_policy'
        cmd = endpointplcy.EndpointPolicyCreate(test_cli20.MyApp(
                                                sys.stdout), None)
        name = 'endpointpolicy1'
        service_epg = 'myserviceepg'
        src_port_range = '1-65535'
        args = [name, '--service-endpoint-group', service_epg,
                '--source-port-range', src_port_range]
        position_names = ['name', 'service_endpoint_group', 'src_port_range']
        position_values = [name, service_epg, src_port_range]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_endpoint_policy_with_dest_port_range(self):
        # Create endpointpolicy: endpointpolicy1 --destination-port-range.
        resource = 'endpoint_policy'
        cmd = endpointplcy.EndpointPolicyCreate(test_cli20.MyApp(
                                                sys.stdout), None)
        name = 'endpointpolicy1'
        service_epg = 'myserviceepg'
        dst_port_range = '1-65535'
        args = [name, '--service-endpoint-group', service_epg,
                '--destination-port-range', dst_port_range]
        position_names = ['name', 'service_endpoint_group', 'dst_port_range']
        position_values = [name, service_epg, dst_port_range]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_endpoint_policy_with_action(self):
        # Create endpointpolicy: endpointpolicy1 --action.
        resource = 'endpoint_policy'
        cmd = endpointplcy.EndpointPolicyCreate(test_cli20.MyApp(
                                                sys.stdout), None)
        name = 'endpointpolicy1'
        service_epg = 'myserviceepg'
        action = 'copy'
        args = [name, '--service-endpoint-group', service_epg,
                '--action', action]
        position_names = ['name', 'service_endpoint_group', 'action']
        position_values = [name, service_epg, action]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_endpoint_policy_with_invalid_action(self):
        # Create endpointpolicy: endpointpolicy1 --action.
        resource = 'endpoint_policy'
        cmd = endpointplcy.EndpointPolicyCreate(test_cli20.MyApp(
                                                sys.stdout), None)
        name = 'endpointpolicy1'
        service_epg = 'myserviceepg'
        action = 'invalid-action'
        args = [name, '--service-endpoint-group', service_epg,
                '--action', action]
        position_names = ['name', 'service_endpoint_group', 'action']
        position_values = [name, service_epg, action]
        self.assertRaises(Exception, self._test_create_resource, resource,
                          cmd, name, 'myid', args,
                          position_names, position_values)
