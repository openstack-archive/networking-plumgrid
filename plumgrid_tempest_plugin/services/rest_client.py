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

from oslo_serialization import jsonutils
import requests
from tempest import config

CONF = config.CONF


class RESTClient(object):
    """
        This class implements a REST client for PLUMgrid Neutron
        API extensions
    """

    def __init__(self, tenant_name, username, password):
        self.tenant = tenant_name
        self.username = username
        self.password = password
        self.base_url = "http://localhost:"
        self.port_neutron = "9696"
        self.transit_domain_url = "/v2.0/transit-domains"
        self.pap_url = "/v2.0/physical-attachment-points"
        self.headers = {'accept': 'application/json',
                        'content-type': 'application/json'}

    def _get_access_token(self):
        """
            Function that returns Access Token from Keystone that
            is required to make REST calls to Neutron
            ARGUMENTS: none
            RETURN TYPE: String
        """

        # Set up auth URL
        url = CONF.identity.uri + "/tokens"

        # Set up parameters to send Authorization Details
        data = {"auth": {"passwordCredentials": {"username": self.username,
                         "password": self.password},
                         "tenantName": self.tenant}}

        body = jsonutils.dumps(data)
        response = requests.post(url, headers=self.headers, data=body)
        resp_body = response.json()

        return resp_body['access']['token']['id']

    def _authenticate(self):
        """
            This function returns Access Token
            from Neutron API after Authentication
        """
        token = self._get_access_token()
        self.headers.update({'X-Auth-Token': token})

    def create_transit_domain(self, td_name):
        """
            REST Function to create a Transit Domain
            and return the created Transit Domain
            ARGUMENTS:
                td_name = name of transit domain
            RETURN TYPE: JSON
        """

        # Get authentication
        self._authenticate()

        # Create Resource
        url = self.base_url + self.port_neutron + self.transit_domain_url
        data = {"transit_domain": {"name": td_name}}
        body = jsonutils.dumps(data)
        response = requests.post(url, headers=self.headers, data=body)
        resp_body = response.json()

        return resp_body

    def show_transit_domain(self, td_id):
        """
            Function to return a specific Transit Domain
            ARGUMENTS:
                td_id = ID of Transit Domain (tenant_id of TD)
            RETURN TYPE: JSON
        """

        # Get authentication
        self._authenticate()

        url = self.base_url + self.port_neutron \
            + self.transit_domain_url + "/" + td_id

        response = requests.get(url, headers=self.headers)
        resp_body = response.json()
        return resp_body

    def list_transit_domain(self):
        """
            REST Function to list all (existing) Transit Domain
            ARGUMENTS: NONE
            RETURN TYPE: JSON
        """

        # Get authentication
        self._authenticate()

        url = self.base_url + self.port_neutron + self.transit_domain_url

        response = requests.get(url, headers=self.headers)
        resp_body = response.json()
        return resp_body

    def update_transit_domain(self, td_id, td_name):
        """
            Function to update Transit Domain with given new parameters
            ARGUMENTS:
                td_id = ID of Transit Domain (tenant_id of TD) to find TD by ID
                td_name = New name of Transit Domain which is to be updated
            RETURN TYPE: JSON
        """

        # Get authentication
        self._authenticate()

        # Set up URL to specific access Transit Domain
        url = self.base_url + self.port_neutron \
            + self.transit_domain_url + "/" + td_id

        data = {"transit_domain": {"name": td_name}}
        body = jsonutils.dumps(data)
        response = requests.put(url, headers=self.headers, data=body)
        resp_body = jsonutils.loads(response.text)

        return resp_body

    def delete_transit_domain(self, **kwargs):
        """
            Function to delete Transit Domain with given ID or Name of
            Transit Domain.
            Note: Function will return False if there exists a Transit Domain
            with duplicate names.
            ARGUMENTS which kwargs MAY have:
                td_id = ID of Transit Domain (not tenant_id) to find TD by ID
                td_name = Name of Transit Domain
            RETURN TYPE: boolean [True, False]
        """

        # Get authentication
        self._authenticate()

        # if UUID is provided, then delete by ID
        if 'td_id' in kwargs:
            td_id = kwargs["td_id"]
            return self._delete_transit_domain_by_uuid(td_id)

        # if Name of TD is given, then process respectively
        elif 'td_name' in kwargs:
            td_name = kwargs["td_name"]

            # Set up GET request with TD name
            url = self.base_url + self.port_neutron + self.transit_domain_url\
                + "?fields=id&name=" + td_name
            response = requests.get(url, headers=self.headers)
            resp_body = response.json()
            transit_domains = resp_body['transit_domains']

            # get number of transit domains with given name,
            # returned from response
            no_of_domains = len(transit_domains)

            # if duplication exist
            if no_of_domains > 1:
                return False

            # if Transit Domain not found
            elif no_of_domains == 0:
                return False

            # if correct Transit Domain found
            elif no_of_domains == 1:
                # Delete it by UUID
                return self._delete_transit_domain_by_uuid(
                                            transit_domains[0]['id'])

        # if no argument inside kwargs
        else:
            return False

    def _delete_transit_domain_by_uuid(self, td_id):
        """
            Private Function
            This function deletes a Transit Domain
            by its UUID
        """
        url = self.base_url + self.port_neutron \
            + self.transit_domain_url + "/" + td_id

        response = requests.delete(url, headers=self.headers)

        # if server deleted transit domain successfully
        if response.status_code == 204:
            return True
        else:
            return False

    def create_pap(self, **kwargs):
        """
            REST Function to create return (created) PAP
            ARGUMENTS **kwargs will have:
                name = name of Physical Attachment Point
                interfaces = LIST of interfaces that includes
                hostnames and respective interface_names
                transit_domain_id = UUID of Transit Domain
                hash_mode = String: L2 / L3 / L2+L3 / L3+L4
                lacp = String: True / False
            RETURN TYPE: JSON
        """

        # Get authentication
        self._authenticate()

        url = self.base_url + self.port_neutron + self.pap_url

        data = {"physical_attachment_point": kwargs}
        body = jsonutils.dumps(data)
        response = requests.post(url, headers=self.headers, data=body)
        resp_body = response.json()

        return resp_body

    def show_pap(self, pap_id):
        """
            Function to return a specific PAP
            ARGUMENTS:
                pap_id = ID of Physical Attachment Point
            RETURN TYPE: JSON
        """

        # Get authentication
        self._authenticate()

        # Set up URL for a specific Transit Domain to be accessed
        url = self.base_url + self.port_neutron \
            + self.pap_url + "/" + pap_id

        response = requests.get(url, headers=self.headers)
        resp_body = response.json()

        return resp_body

    def list_pap(self):
        """
            REST Function to list all (existing) PAPs
            ARGUMENTS: NONE
            RETURN TYPE: JSON
        """

        # Get authentication
        self._authenticate()

        # Set up URL to be accessed
        url = self.base_url + self.port_neutron + self.pap_url
        response = requests.get(url, headers=self.headers)
        json_resp = response.json()

        # Return JSON of response
        return json_resp

    def update_pap(self, pap_id, **kwargs):
        """
            Function to update PAP with given new parameters
            ARGUMENTS
                id = UUID of Physical Attachment Point
                **kwargs will have:
                name = name of Physical Attachment Point
                add_interfaces = LIST of new interfaces to Add
                remove_interfaces = LIST of interfaces to Remove
                hash_mode = String: L2 / L3 / L2+L3 / L3+L4
                lacp = String: True / False

            RETURN TYPE: JSON
        """

        # Get authentication
        self._authenticate()

        # Set up URL to specific access to PAP
        url = self.base_url + self.port_neutron \
            + self.pap_url + "/" + pap_id

        # Create Resource
        data = {"physical_attachment_point": kwargs}
        body = jsonutils.dumps(data)
        response = requests.put(url, headers=self.headers, data=body)
        resp_body = jsonutils.loads(response.text)

        return resp_body

    def delete_pap(self, pap_id):
        """
            Function to delete PAP with given UUID
            ARGUMENTS:
                pap_id = ID of Physical Attachment Point to find it
            RETURN TYPE: boolean [True, False]
        """

        # Get authentication
        self._authenticate()

        # Set up URL to specific access Transit Domain
        url = self.base_url + self.port_neutron \
            + self.pap_url + "/" + pap_id

        response = requests.delete(url, headers=self.headers)

        # if server deleted transit domain successfully then return true
        if response.status_code == 204:
            return True
        else:
            return False
