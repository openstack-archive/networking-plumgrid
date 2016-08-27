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
    policy_service as ps)
from neutronclient import shell
import sys


class CLITestV20ExtensionPolicyServiceJSON(test_cli20.CLITestV20Base):
    def setUp(self):
        # need to mock before super because extensions loaded on instantiation
        self._mock_extension_loading()
        super(CLITestV20ExtensionPolicyServiceJSON,
              self).setUp(plurals={'tags': 'tag'})

    def _mock_extension_loading(self):
        ext_pkg = 'neutronclient.common.extension'
        contrib = mock.patch(ext_pkg + '._discover_via_entry_points').start()
        contrib.return_value = [("policy_service", ps)]
        return contrib

    def test_ext_cmd_loaded(self):
        """Tests policy service commands loaded."""
        shell.NeutronShell('2.0')
        ext_cmd = {'policy-service-list':
                   ps.PolicyServiceList,
                   'policy-service-create':
                   ps.PolicyServiceCreate,
                   'policy-service-update':
                   ps.PolicyServiceUpdate,
                   'policy-service-delete':
                   ps.PolicyServiceDelete,
                   'policy-service-show':
                   ps.PolicyServiceShow}
        self.assertDictContainsSubset(ext_cmd, shell.COMMANDS['2.0'])

    def test_create_policy_service_name(self):
        # Create policy service: ps1.
        resource = 'policy_service'
        cmd = ps.PolicyServiceCreate(test_cli20.MyApp(
                                      sys.stdout), None)
        name = 'ps1'
        args = [name]
        position_names = ['name']
        position_values = [name]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_policy_service_desc(self):
        # Create policy service: ps1.
        resource = 'policy_service'
        cmd = ps.PolicyServiceCreate(test_cli20.MyApp(
                                      sys.stdout), None)
        name = 'ps1'
        desc = 'policy service'
        args = [name, '--description', desc]
        position_names = ['name', 'description']
        position_values = [name, desc]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_policy_service_inport(self):
        # Create policy service: ps1.
        resource = 'policy_service'
        cmd = ps.PolicyServiceCreate(test_cli20.MyApp(
                                      sys.stdout), None)
        name = 'ps1'
        inport = [{'id': 'portid'}]
        args = [name, '--ingress-port', 'id=portid']
        position_names = ['name', 'ingress_ports']
        position_values = [name, inport]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_policy_service_eport(self):
        # Create policy service: ps1.
        resource = 'policy_service'
        cmd = ps.PolicyServiceCreate(test_cli20.MyApp(
                                      sys.stdout), None)
        name = 'ps1'
        eport = [{'id': 'portid'}]
        args = [name, '--egress-port', 'id=portid']
        position_names = ['name', 'egress_ports']
        position_values = [name, eport]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_policy_service_bidirect_port(self):
        # Create policy service: ps1.
        resource = 'policy_service'
        cmd = ps.PolicyServiceCreate(test_cli20.MyApp(
                                      sys.stdout), None)
        name = 'ps1'
        bidirect_port = [{'id': 'portid'}]
        args = [name, '--bidirectional-port', 'id=portid']
        position_names = ['name', 'bidirectional_ports']
        position_values = [name, bidirect_port]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_policy_service_inport_name(self):
        # Create policy service: ps1.
        resource = 'policy_service'
        cmd = ps.PolicyServiceCreate(test_cli20.MyApp(
                                      sys.stdout), None)
        name = 'ps1'
        inport = [{'id': 'portid'}]
        args = [name, '--ingress-port', 'name=portid']
        position_names = ['name', 'ingress_ports']
        position_values = [name, inport]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_policy_service_eport_name(self):
        # Create policy service: ps1.
        resource = 'policy_service'
        cmd = ps.PolicyServiceCreate(test_cli20.MyApp(
                                      sys.stdout), None)
        name = 'ps1'
        eport = [{'id': 'portid'}]
        args = [name, '--egress-port', 'name=portid']
        position_names = ['name', 'egress_ports']
        position_values = [name, eport]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_policy_service_bidirect_port_name(self):
        # Create policy service: ps1.
        resource = 'policy_service'
        cmd = ps.PolicyServiceCreate(test_cli20.MyApp(
                                      sys.stdout), None)
        name = 'ps1'
        bidirect_port = [{'id': 'portid'}]
        args = [name, '--bidirectional-port', 'name=portid']
        position_names = ['name', 'bidirectional_ports']
        position_values = [name, bidirect_port]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_create_policy_service_inport_eport(self):
        # Create policy service: ps1.
        resource = 'policy_service'
        cmd = ps.PolicyServiceCreate(test_cli20.MyApp(
                                      sys.stdout), None)
        name = 'ps1'
        inport = [{'id': 'portid'}]
        eport = [{'id': 'portid'}]
        args = [name, '--ingress-port', 'id=portid',
                '--egress-port', 'id=portid']
        position_names = ['name', 'ingress_ports', 'egress_ports']
        position_values = [name, inport, eport]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def test_update_policy_service_name(self):
        # Update policy service: myid --name
        resource = 'policy_service'
        cmd = ps.PolicyServiceUpdate(test_cli20.MyApp(
                                     sys.stdout), None)
        args = ['myid', '--name', 'myps']
        values = {'name': 'myps'}
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_update_policy_service_desc(self):
        # Update policy service: myid --description
        resource = 'policy_service'
        cmd = ps.PolicyServiceUpdate(test_cli20.MyApp(
                                     sys.stdout), None)
        args = ['myid', '--description', 'myps desc']
        values = {'description': 'myps desc'}
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_update_policy_service_add_inport(self):
        # Update policy service: myid --add-ingress-port
        resource = 'policy_service'
        cmd = ps.PolicyServiceUpdate(test_cli20.MyApp(
                                     sys.stdout), None)
        args = ['myid', '--add-ingress-port', 'id=portid']
        values = {'add_ingress_ports': [{'id': 'portid'}]}
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_update_policy_service_add_eport(self):
        # Update policy service: myid --add-egress-port
        resource = 'policy_service'
        cmd = ps.PolicyServiceUpdate(test_cli20.MyApp(
                                     sys.stdout), None)
        args = ['myid', '--add-egress-port', 'id=portid']
        values = {'add_egress_ports': [{'id': 'portid'}]}
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_update_policy_service_remove_inport(self):
        # Update policy service: myid --remove-ingress-port
        resource = 'policy_service'
        cmd = ps.PolicyServiceUpdate(test_cli20.MyApp(
                                     sys.stdout), None)
        args = ['myid', '--remove-ingress-port', 'id=portid']
        values = {'remove_ingress_ports': [{'id': 'portid'}]}
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_update_policy_service_remove_eport(self):
        # Update policy service: myid --remove-egress-port
        resource = 'policy_service'
        cmd = ps.PolicyServiceUpdate(test_cli20.MyApp(
                                     sys.stdout), None)
        args = ['myid', '--remove-egress-port', 'id=portid']
        values = {'remove_egress_ports': [{'id': 'portid'}]}
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_update_policy_service_add_bidirect_port(self):
        # Update policy service: myid --add-bidirectional-port
        resource = 'policy_service'
        cmd = ps.PolicyServiceUpdate(test_cli20.MyApp(
                                     sys.stdout), None)
        args = ['myid', '--add-bidirectional-port', 'id=portid']
        values = {'add_bidirectional_ports': [{'id': 'portid'}]}
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_update_policy_service_remove_bidirect_port(self):
        # Update policy service: myid --remove-bidirectional-port
        resource = 'policy_service'
        cmd = ps.PolicyServiceUpdate(test_cli20.MyApp(
                                     sys.stdout), None)
        args = ['myid', '--remove-bidirectional-port', 'id=portid']
        values = {'remove_bidirectional_ports': [{'id': 'portid'}]}
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_list_policy_services(self):
        # list policy services: -D.
        resources = "policy_services"
        cmd = ps.PolicyServiceList(test_cli20.MyApp(
                                   sys.stdout), None)
        self._test_list_resources(resources, cmd, True)

    def test_list_policy_services_sort(self):
        # list policy services:
        # --sort-key name --sort-key id --sort-key asc --sort-key desc
        resources = "policy_services"
        cmd = ps.PolicyServiceList(test_cli20.MyApp(
                                   sys.stdout), None)
        self._test_list_resources(resources, cmd,
                                  sort_key=["name", "id"],
                                  sort_dir=["asc", "desc"])

    def test_list_policy_services_limit(self):
        # list policy services: -P.
        resources = "policy_services"
        cmd = ps.PolicyServiceList(test_cli20.MyApp(
                                   sys.stdout), None)
        self._test_list_resources(resources, cmd, page_size=1000)

    def test_delete_policy_service(self):
        # Delete policy service: myid.
        resource = "policy_service"
        cmd = ps.PolicyServiceDelete(test_cli20.MyApp(
                                sys.stdout), None)
        my_id = 'myid'
        args = [my_id]
        self._test_delete_resource(resource, cmd, my_id, args)

    def test_show_policy_service(self):
        # Show policy service: --fields id.
        resource = 'policy_service'
        cmd = ps.PolicyServiceShow(test_cli20.MyApp(
                              sys.stdout), None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id, args,
                                 ['id', 'name'])
