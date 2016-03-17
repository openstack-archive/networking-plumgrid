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

from plumgrid_tempest_plugin import config
from plumgrid_tempest_plugin.services import rest_client as rs
import random
from tempest.api.network import base
from tempest import test

CONF = config.CONF


class TestTransitDomain(base.BaseNetworkTest):
    """
        This class contains Test Cases for following functionalities:
        - CRUD Transit Domains
    """

    @test.idempotent_id('2def4f70-bff8-4620-9505-876001395785')
    def test_create_transit_domain(self):
        """
            Function: Tests whether the creation of Transit Domain
            is successful or not.
        """

        restC = rs.RESTClient()

        # generate a random number and concatenate with Transit Domain Name
        tempTDName = "my_TD_" + str(random.randint(100, 10000))

        transitDomain = restC.createTransitDomain(tempTDName)

        # Verifying TD Creation with it's name
        self.assertEqual(tempTDName, transitDomain['transit_domain']['name'])

        # CleanUp: Delete the created transit domain
        restC.deleteTransitDomain(transitDomain['transit_domain']['id'])

    @test.idempotent_id('5126aae8-f595-43b9-9b2b-44a650e69138')
    def test_show_transit_domain(self):
        """
            Function: Tests whether details of Transit Domain
            is correctly fetched or not.
        """

        restC = rs.RESTClient()

        tempTd = restC.createTransitDomain("my_TD_" +
                                           str(random.randint(70, 700)))

        transitDomain = restC.showTransitDomain(tempTd['transit_domain']['id'])

        # compare TD IDs to verify correctness
        self.assertEqual(tempTd['transit_domain']['id'],
                         transitDomain['transit_domain']['id'])

        # CleanUp: Delete the created transit domain
        restC.deleteTransitDomain(tempTd['transit_domain']['id'])

    @test.idempotent_id('409ac550-ba8c-4a6d-afe1-4ab642d047ee')
    def test_update_transit_domain(self):
        """
            Function: Tests whether details of Transit Domain
            are correctly updated or not.
        """

        restC = rs.RESTClient()

        transitDomain = restC.createTransitDomain("my_TD_" +
                                                  str(random.randint(70, 700)))

        newTdName = "updated_name_my_TD_" + str(random.randint(100, 10000))

        transitDomain = restC.updateTransitDomain(
                        transitDomain['transit_domain']['id'], newTdName)

        # compare TD Names to verify correctness
        self.assertEqual(newTdName, transitDomain['transit_domain']['name'])

        # CleanUp: Delete the created transit domain
        restC.deleteTransitDomain(transitDomain['transit_domain']['id'])

    @test.idempotent_id('87601bd1-872c-451d-b126-fb1c8a8017b0')
    def test_list_transit_domains(self):
        """
            Function: Tests whether details of all Transit Domains
            are correctly fetched or not.
        """

        restC = rs.RESTClient()
        totalTDs = 5            # total TDs to be created
        totalMatches = 0         # total Matches to be found
        myTransitDomains = {}    # dict to create new TDs

        # Create 10 Transit Domains and save their IDs
        for i in range(0, totalTDs):
            tdName = "my_TD_" + str(random.randint(500, 5000))
            newTd = restC.createTransitDomain(tdName)
            myTransitDomains[tdName] = newTd['transit_domain']['id']

        allTDs = restC.listTransitDomain()

        # compare newly created domains within existing TDs
        for tdName, tdId in myTransitDomains.items():

            for value in allTDs['transit_domains']:
                if(tdId == value['id']):
                    totalMatches += 1

        # check if all created transit domains were found successfully
        self.assertEqual(totalTDs, totalMatches)

        # CleanUp: Delete all newly created TDs
        for tdName, tdId in myTransitDomains.items():
            restC.deleteTransitDomain(tdId)

    @test.idempotent_id('e102a2c5-7d66-4b44-83f3-c046bbe7ee40')
    def test_delete_transit_domain(self):

        restC = rs.RESTClient()

        transitDomain = restC.createTransitDomain("my_TD_" +
                                                  str(random.randint(70, 700)))

        result = restC.deleteTransitDomain(
                 transitDomain['transit_domain']['id'])

        # compare results of deletion
        self.assertEqual(True, result)
