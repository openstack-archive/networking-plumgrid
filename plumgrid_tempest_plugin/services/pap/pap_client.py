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


PG_PAP = 'physical-attachment-points'


class PAPClient(base.ClientBase):
    """API Tempest REST client for Physical Attachment Point API"""

    # Set appropriate API version
    uri_prefix = 'v2.0'

    def create_pap(self, name=None, lacp=False, hash_mode='L2',
                   interfaces=[], params=None):
        """Create a PAP with the specified parameters.

        :param name: The name of the Physical Attachment Point.
            Default: Random Value
        :param lacp: enable/disable LACP on Physical Attachment Point.
            Default: False
        :param hash_mode: hash_mode config for Physical Attachment Point.
            Default: L2
        :param interfaces: List of gateway interfaces.
            Default: None
        :param params: A Python dict that represents the query paramaters to
                       include in the request URI.
        :return: A tuple with the server response and the created pap.
        """
        pap = {"physical_attachment_point": {
                  "name": name or self._rand_pap_name(),
                  "lacp": lacp,
                  "hash_mode": hash_mode,
                  "interfaces": interfaces}}

        resp, body = self._create_request(PG_PAP, pap, params=params)
        return resp, body

    def show_pap(self, uuid, params=None):
        """Gets a specific physical attachment points.
        :param uuid: Unique identifier of the physical attachment point
                     in UUID format.
        :param params: A Python dict that represents the query paramaters to
                       include in the request URI.
        :return: Serialized physical attachment point as a dictionary.
        """
        return self._show_request(PG_PAP, uuid, params=params)

    def list_paps(self, params=None):
        """Gets a list of all existing physical attachment points.
        :param params: A Python dict that represents the query paramaters to
                       include in the request URI.
        :return: Serialized physical attachment points as a list.
        """
        return self._list_request(PG_PAP, params=params)

    def delete_pap(self, uuid, params=None):
        """Deletes a physical attachment point having the specified UUID.
        :param uuid: The unique identifier of the physical attachment point.
        :param params: A Python dict that represents the query paramaters to
                       include in the request URI.
        :return: A tuple with the server response and the response body.
        """
        resp, body = self._delete_request(PG_PAP, uuid, params=params)
        return resp, body

    def update_pap(self, uuid, name=None, lacp=False, hash_mode='L2',
                   add_interfaces=[], remove_interfaces=[], params=None):
        """Create a PAP with the specified parameters.

        :param uuid: The unique identifier of the Physical Attachment Point.
        :param name: The name of the Physical Attachment Point.
            Default: Random Value
        :param lacp: enable/disable LACP on Physical Attachment Point.
            Default: False
        :param hash_mode: hash_mode config for Physical Attachment Point.
            Default: L2
        :param interfaces: List of gateway interfaces.
            Default: None
        :param params: A Python dict that represents the query paramaters to
                       include in the request URI.
        :return: A tuple with the server response and the created pap.
        """
        pap = {"physical_attachment_point": {
                  "name": name or self._rand_pap_name(),
                  "lacp": lacp,
                  "hash_mode": hash_mode,
                  "add_interfaces": add_interfaces,
                  "remove_interfaces": remove_interfaces}}

        resp, body = self._update_request(PG_PAP, uuid, pap, params=params)
        return resp, body

    def _rand_pap_name(self, name='', prefix='test_pap'):
        return data_utils.rand_name(name=name, prefix=prefix)
