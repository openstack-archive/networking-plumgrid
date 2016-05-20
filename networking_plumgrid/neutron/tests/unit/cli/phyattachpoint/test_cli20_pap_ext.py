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

import mock
from networking_plumgrid.neutron.tests.unit.cli import test_cli20
from networking_plumgrid.neutronclient.phyattachmentpoint import (
    physical_attachment_point as phyattp)
from neutronclient import shell
import sys


class CLITestV20ExtensionPhyAttPJSON(test_cli20.CLITestV20Base):
    def setUp(self):
        # need to mock before super because extensions loaded on instantiation
        self._mock_extension_loading()
        super(CLITestV20ExtensionPhyAttPJSON, self).setUp(plurals={'tags':
                                                                   'tag'})

    def _mock_extension_loading(self):
        ext_pkg = 'neutronclient.common.extension'
        contrib = mock.patch(ext_pkg + '._discover_via_entry_points').start()
        contrib.return_value = [("physical_attachment_point", phyattp)]
        return contrib

    def test_ext_cmd_loaded(self):
        """Tests physical attachment point  commands loaded."""
        shell.NeutronShell('2.0')
        ext_cmd = {'physical-attachment-point-list':
                   phyattp.PhysicalAttachmentPointList,
                   'physical-attachment-point-create':
                   phyattp.PhysicalAttachmentPointCreate,
                   'physical-attachment-point-update':
                   phyattp.PhysicalAttachmentPointUpdate,
                   'physical-attachment-point-delete':
                   phyattp.PhysicalAttachmentPointDelete,
                   'physical-attachment-point-show':
                   phyattp.PhysicalAttachmentPointShow}
        self.assertDictContainsSubset(ext_cmd, shell.COMMANDS['2.0'])

    def _create_physical_attachment_point(self, args, name, lacp, hash_mode,
                                          interface):
        resource = 'physical_attachment_point'
        cmd = phyattp.PhysicalAttachmentPointCreate(test_cli20.MyApp(
                                                    sys.stdout), None)
        position_names = ['name', 'lacp', 'hash_mode', 'interfaces']
        position_values = [name, lacp, hash_mode, interface]
        self._test_create_resource(resource, cmd, name, 'myid', args,
                                   position_names, position_values)

    def _update_physical_attachment_point(self, args, values):
        resource = 'physical_attachment_point'
        cmd = phyattp.PhysicalAttachmentPointUpdate(test_cli20.MyApp(
                                                    sys.stdout), None)
        self._test_update_resource(resource, cmd, 'myid',
                                   args, values)

    def test_create_physical_attachment_point(self):
        """Test Create physical attachment point."""

        name = 'phyattpoint1'
        lacp = 'True'
        hash_mode = 'L3'
        args = [name, '--lacp', lacp, '--hash_mode', hash_mode,
                '--interface', 'hostname=u1,interface_name=i1']
        interface = [{"hostname": "u1", "interface": "i1"}]
        self._create_physical_attachment_point(args, name, lacp,
                                               hash_mode, interface)

    def test_create_physical_attachment_point_with_multiple_interfaces(self):
        """Test Create physical attachment point for multiple interfaces."""

        name = 'phyattpoint1'
        lacp = 'True'
        hash_mode = 'L3'
        args = [name, '--lacp', lacp, '--hash_mode', hash_mode, '--interface',
                'hostname=u1,interface_name=i1', '--interface',
                'hostname=u2,interface_name=i2']
        interface = [{"hostname": "u1", "interface": "i1"},
                     {"hostname": "u2", "interface": "i2"}]
        self._create_physical_attachment_point(args, name, lacp,
                                               hash_mode, interface)

    def test_create_physical_attachment_point_lacp_off(self):
        """Test Create physical attachment point."""

        name = 'phyattpoint1'
        lacp = 'False'
        hash_mode = 'L2'
        args = [name, '--lacp', lacp, '--hash_mode', hash_mode,
                '--interface', 'hostname=u1,interface_name=i1']
        interface = [{"hostname": "u1", "interface": "i1"}]
        self._create_physical_attachment_point(args, name, lacp,
                                               hash_mode, interface)

    def test_list_physical_attachment_points(self):
        """Test List physical attachment points."""

        resources = "physical_attachment_points"
        cmd = phyattp.PhysicalAttachmentPointList(test_cli20.MyApp(
                                                  sys.stdout), None)
        self._test_list_resources(resources, cmd, True)

    def test_list_physical_attachment_points_pagination(self):
        #FIXME(fawadkhaliq)
        self.skipTest("Pagination does not work right now")
        #resources = 'physical_attachment_points'
        #cmd = phyattp.PhysicalAttachmentPointList(test_cli20.MyApp(
        #                                           sys.stdout), None)
        #self._test_list_resources_with_pagination(resources, cmd)

    def test_list_physical_attachment_points_sort(self):
        """list physical attachment points: --sort-key name
           --sort-key id --sort-key asc --sort-key desc
        """
        resources = 'physical_attachment_points'
        cmd = phyattp.PhysicalAttachmentPointList(test_cli20.MyApp(
                                                  sys.stdout), None)
        self._test_list_resources(resources, cmd,
                                  sort_key=["name", "id"],
                                  sort_dir=["asc", "desc"])

    def test_list_physical_attachment_points_limit(self):
        """list physical attachment points: -P."""
        resources = 'physical_attachment_points'
        cmd = phyattp.PhysicalAttachmentPointList(test_cli20.MyApp(
                                                  sys.stdout), None)
        self._test_list_resources(resources, cmd, page_size=1000)

    def test_delete_physical_attachment_point(self):
        """Test Delete physical attachment points."""

        resource = 'physical_attachment_point'
        cmd = phyattp.PhysicalAttachmentPointDelete(test_cli20.MyApp(
                                                    sys.stdout), None)
        my_id = 'my-id'
        args = [my_id]
        self._test_delete_resource(resource, cmd, my_id, args)

    def test_show_physical_attachment_point(self):
        """
        Test Show physical attachment point: --fields id
        --fields name myid.
        """

        resource = 'physical_attachment_point'
        cmd = phyattp.PhysicalAttachmentPointShow(test_cli20.MyApp(
                                                  sys.stdout), None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id, args,
                                 ['id', 'name'])

    def test_update_physical_attachment_point(self):
        """Test Update physical attachment point hash mode."""

        args = ['myid', '--lacp', 'False']
        values = {'lacp': 'False'}
        self._update_physical_attachment_point(args, values)

    def test_update_physical_attachment_point_name(self):
        """Test Update physical attachment point name."""

        args = ['myid', '--name', 'myname']
        values = {'name': 'myname'}
        self._update_physical_attachment_point(args, values)

    def test_update_physical_attachment_point_hash_mode(self):
        """Test Update physical attachment point hash mode."""

        args = ['myid', '--name', 'myname', '--hash_mode', 'L2']
        values = {'name': 'myname', 'hash_mode': 'L2'}
        self._update_physical_attachment_point(args, values)
