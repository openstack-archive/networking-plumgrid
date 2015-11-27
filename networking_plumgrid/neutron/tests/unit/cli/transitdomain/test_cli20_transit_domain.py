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
from networking_plumgrid.neutronclient.transitdomain import (
    transitdomain as transitdom)
from neutronclient import shell
import sys


class CLITestV20ExtensionTransitDomainJSON(test_cli20.CLITestV20Base):
    def setUp(self):
        # need to mock before super because extensions loaded on instantiation
        self._mock_extension_loading()
        super(CLITestV20ExtensionTransitDomainJSON,
              self).setUp(plurals={'tags': 'tag'})

    def _create_patch(self, name, func=None):
        patcher = mock.patch(name)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing

    def _mock_extension_loading(self):
        ext_pkg = 'neutronclient.common.extension'
        contrib = self._create_patch(ext_pkg + '._discover_via_entry_points')
        contrib.return_value = [("transit_domain", transitdom)]
        return contrib

    def test_ext_cmd_loaded(self):
        """Tests transit domain commands loaded."""
        shell.NeutronShell('2.0')
        ext_cmd = {'transit-domain-list':
                   transitdom.TransitDomainList,
                   'transit-domain-create':
                   transitdom.TransitDomainCreate,
                   'transit-domain-update':
                   transitdom.TransitDomainUpdate,
                   'transit-domain-delete':
                   transitdom.TransitDomainDelete,
                   'transit-domain-show':
                   transitdom.TransitDomainShow}
        self.assertDictContainsSubset(ext_cmd, shell.COMMANDS['2.0'])

    def _create_transit_domain(self, args, name):
        resource = 'transit_domain'
        cmd = transitdom.TransitDomainCreate(test_cli20.MyApp(
                                             sys.stdout), None)
        position_names = ['name']
        position_values = [name]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def _update_transit_domain(self, args, values):
        resource = 'transit_domain'
        cmd = transitdom.TransitDomainUpdate(test_cli20.MyApp(
                                             sys.stdout), None)
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_create_transit_domain(self):
        """Test create transit domain"""

        name = 'transitdomain1'
        args = [name]
        self._create_transit_domain(args, name)

    def test_list_transit_domains(self):
        """Test List transit domains."""

        resources = "transit_domains"
        cmd = transitdom.TransitDomainList(test_cli20.MyApp(
                                           sys.stdout), None)
        self._test_list_resources(resources, cmd, True)

    def test_list_transit_domains_sort(self):
        """list transit domains: --sort-key name
           --sort-key id --sort-key asc --sort-key desc
        """
        resources = "transit_domains"
        cmd = transitdom.TransitDomainList(test_cli20.MyApp(
                                           sys.stdout), None)
        self._test_list_resources(resources, cmd,
                                  sort_key=["name", "id"],
                                  sort_dir=["asc", "desc"])

    def test_list_transit_domains_limit(self):
        """list transit domains: -P."""
        resources = "transit_domains"
        cmd = transitdom.TransitDomainList(test_cli20.MyApp(
                                           sys.stdout), None)
        self._test_list_resources(resources, cmd, page_size=1000)

    def test_delete_transit_domain_point(self):
        """Test delete transit domain"""
        resource = "transit_domain"
        cmd = transitdom.TransitDomainDelete(test_cli20.MyApp(
                                             sys.stdout), None)

        my_id = 'my-id'
        args = [my_id]
        self._test_delete_resource(resource, cmd, my_id, args)

    def test_show_transit_domain_point(self):
        """
        Test show transit domain: --fields id
        --fields name myid.
        """

        resource = 'transit_domain'
        cmd = transitdom.TransitDomainShow(test_cli20.MyApp(
                                           sys.stdout), None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id, args,
                                 ['id', 'name'])
