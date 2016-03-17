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
from tempest import test

from plumgrid_tempest_plugin.tests import base

LOG = logging.getLogger(__name__)


class TestTransitDomains(base.BaseTest):
    credentials = ['primary', 'admin']

    @classmethod
    def setup_clients(cls):
        super(TestTransitDomains, cls).setup_clients()

        cls.client = cls.os.pap_client
        cls.admin_client = cls.os_adm.td_client

    @test.attr(type='smoke')
    @test.idempotent_id('29a30571-2f4c-4bc6-87c4-6f8052e04f93')
    def test_create_td(self):
        resp, td = self.admin_client.create_td()
        self.addCleanup(self.admin_client.delete_td,
                        td["transit_domain"]["id"])
        self.assertEqual(resp.status, httplib.CREATED)

    @test.attr(type='smoke')
    @test.idempotent_id('9ff01991-a7df-4a1e-b2e9-5bc0f5dc21fb')
    def test_show_td(self):
        _, td = self.admin_client.create_td()
        self.addCleanup(self.admin_client.delete_td,
                        td["transit_domain"]["id"])
        _, body = self.admin_client.show_td(
                       td["transit_domain"]["id"])

        self.assertEqual(td['transit_domain'],
                         body['transit_domain'])

    @test.attr(type='smoke')
    @test.idempotent_id('89b2e4be-1cae-4a88-b6e3-8c100ceebba5')
    def test_update_td(self):
        resp, td = self.admin_client.create_td()
        self.addCleanup(self.admin_client.delete_td,
                        td["transit_domain"]["id"])
        resp, updated_td = self.admin_client.update_td(
                               td['transit_domain']['id'],
                               name='test_td_new')
        self.assertEqual(resp.status, httplib.OK)

    @test.attr(type='smoke')
    @test.idempotent_id('61390bee-9d9a-4728-bcfc-439c112c061e')
    def test_delete_td(self):
        _, td = self.admin_client.create_td()
        resp, td = self.admin_client.delete_td(
                     td['transit_domain']['id'])
        self.assertEqual(resp.status, httplib.NO_CONTENT)

    @test.attr(type='smoke')
    @test.idempotent_id('0f2cc7dc-049b-43fa-a7b0-41c044bcc09f')
    def test_list_tds(self):
        _, td1 = self.admin_client.create_td()
        _, td2 = self.admin_client.create_td()
        self.addCleanup(self.admin_client.delete_td,
                        td1["transit_domain"]["id"])
        self.addCleanup(self.admin_client.delete_td,
                        td2["transit_domain"]["id"])
        resp, tds_list = self.admin_client.list_tds()
        self.assertEqual(resp.status, httplib.OK)
        self.assertEqual(len(tds_list['transit_domains']), 3)
