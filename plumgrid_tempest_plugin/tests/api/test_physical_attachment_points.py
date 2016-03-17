# Copyright 2016 PLUMgrid Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#    http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import httplib
from oslo_log import log as logging
from tempest import config
from tempest import test

from plumgrid_tempest_plugin.tests import base

CONF = config.CONF
LOG = logging.getLogger(__name__)


def _process_phys_ifcs():
    ifc_list = []
    ifcs_str = CONF.plumgrid.interfaces
    for ifc in ifcs_str.split(','):
        hostname = ifc.split('+')[0]
        for interface in ifc.split('+')[1:]:
            ifc_list.append({'hostname': hostname,
                             'interface': interface})
    return ifc_list


class TestPhysicalAttachmentPoint(base.BaseTest):
    credentials = ['primary', 'admin']
    interfaces = _process_phys_ifcs()

    @classmethod
    def setup_clients(cls):
        super(TestPhysicalAttachmentPoint, cls).setup_clients()

        cls.client = cls.os.pap_client
        cls.admin_client = cls.os_adm.pap_client

    @test.attr(type='smoke')
    @test.idempotent_id('2fb95a42-482d-45cd-93fd-9e161a709874')
    def test_create_pap(self):
        resp, pap = self.admin_client.create_pap()
        self.addCleanup(self.admin_client.delete_pap,
                        pap["physical_attachment_point"]["id"])
        self.assertEqual(resp.status, httplib.CREATED)

    @test.attr(type='smoke')
    @test.idempotent_id('5d4b2eb6-5ce6-44c3-afb3-b0fb75a15c7c')
    def test_show_pap(self):
        _, pap = self.admin_client.create_pap()
        self.addCleanup(self.admin_client.delete_pap,
                        pap["physical_attachment_point"]["id"])
        _, body = self.admin_client.show_pap(
                       pap['physical_attachment_point']['id'])

        self.assertEqual(pap['physical_attachment_point'],
                         body['physical_attachment_point'])

    @test.attr(type='smoke')
    @test.idempotent_id('3ba5892a-5fb1-49fc-b113-1e3b47712a37')
    def test_update_pap(self):
        resp, pap = self.admin_client.create_pap()
        self.addCleanup(self.admin_client.delete_pap,
                        pap["physical_attachment_point"]["id"])
        resp, updated_pap = self.admin_client.update_pap(
                          pap['physical_attachment_point']['id'],
                          add_interfaces=self.interfaces)
        self.assertEqual(resp.status, httplib.OK)

    @test.attr(type='smoke')
    @test.idempotent_id('3f817924-7ca0-41a3-bf30-ce00079a90d6')
    def test_delete_pap(self):
        _, pap = self.admin_client.create_pap(interfaces=self.interfaces)
        resp, pap = self.admin_client.delete_pap(
                     pap['physical_attachment_point']['id'])
        self.assertEqual(resp.status, httplib.NO_CONTENT)

    @test.attr(type='smoke')
    @test.idempotent_id('fb1e3803-2872-439a-bb4a-e3de50d3ed91')
    def test_list_paps(self):
        _, pap1 = self.admin_client.create_pap(interfaces=self.interfaces)
        _, pap2 = self.admin_client.create_pap()
        self.addCleanup(self.admin_client.delete_pap,
                        pap1["physical_attachment_point"]["id"])
        self.addCleanup(self.admin_client.delete_pap,
                        pap2["physical_attachment_point"]["id"])
        resp, paps_list = self.admin_client.list_paps()
        self.assertEqual(resp.status, httplib.OK)
        self.assertEqual(len(paps_list['physical_attachment_points']), 3)

    @test.attr(type='smoke')
    @test.idempotent_id('2fb95a42-482d-45cd-93fd-9e161a709874')
    def test_show_pap_by_name(self):
        _, pap1 = self.admin_client.create_pap()
        _, pap2 = self.admin_client.create_pap()
        self.addCleanup(self.admin_client.delete_pap,
                        pap1["physical_attachment_point"]["id"])
        self.addCleanup(self.admin_client.delete_pap,
                        pap2["physical_attachment_point"]["id"])
        resp, pap_ret = self.admin_client.list_paps({
                            'name': pap1["physical_attachment_point"]["name"]})
        self.assertEqual(pap_ret["physical_attachment_points"][0],
                         pap1["physical_attachment_point"])
