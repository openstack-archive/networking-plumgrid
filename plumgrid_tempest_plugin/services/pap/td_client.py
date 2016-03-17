# Copyright 2016 PLUMgrid, Inc. All Rights Reserved.
# All Rights Reserved.
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
from tempest.lib.common.utils import data_utils

from plumgrid_tempest_plugin.services import base


PG_TD = 'transit-domains'


class TDClient(base.ClientBase):
    """API Tempest REST client for Transit Domains API"""

    # Set appropriate API version
    uri_prefix = 'v2.0'

    def create_td(self, name=None, params=None):
        """Create a Transit Domain with the specified parameters.

        :param name: The name of the Transit Domain.
            Default: Random Value
        :param params: A Python dict that represents the query paramaters to
                       include in the request URI.
        :return: A tuple with the server response and the created pap.
        """
        td = {"transit_domain": {
                  "name": name or self._rand_td_name()}}

        resp, body = self._create_request(PG_TD, td, params=params)
        return resp, body

    def show_td(self, uuid, params=None):
        """Gets a specific physical attachment points.
        :param uuid: Unique identifier of the transit domain
                     in UUID format.
        :param params: A Python dict that represents the query paramaters to
                       include in the request URI.
        :return: Serialized physical attachment point as a dictionary.
        """
        return self._show_request(PG_TD, uuid, params=params)

    def list_tds(self, params=None):
        """Gets a list of all existing physical attachment points.
        :param params: A Python dict that represents the query paramaters to
                       include in the request URI.
        :return: Serialized physical attachment points as a list.
        """
        return self._list_request(PG_TD, params=params)

    def delete_td(self, uuid, params=None):
        """Deletes a physical attachment point having the specified UUID.
        :param uuid: The unique identifier of the physical attachment point.
        :param params: A Python dict that represents the query paramaters to
                       include in the request URI.
        :return: A tuple with the server response and the response body.
        """
        resp, body = self._delete_request(PG_TD, uuid, params=params)
        return resp, body

    def update_td(self, uuid, name=None, params=None):
        """Create a Transit Domain with the specified parameters.

        :param uuid: The unique identifier of the Transit Domain.
        :param name: The name of the Transit Domain.
            Default: Random Value
        :param params: A Python dict that represents the query paramaters to
                       include in the request URI.
        :return: A tuple with the server response and the created pap.
        """
        td = {"transit_domain": {
                  "name": name or self._rand_td_name()}}

        resp, body = self._update_request(PG_TD, uuid, td, params=params)
        return resp, body

    def _rand_td_name(self, name='', prefix='test_td'):
        return data_utils.rand_name(name=name, prefix=prefix)
