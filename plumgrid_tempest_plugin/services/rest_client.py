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

from tempest import config
from oslo_serialization import jsonutils
import requests

CONF = config.CONF

class RESTClient(object):
    """
        This class implements a REST client for PLUMgrid Neutron API extensions
    """

    # Constructor
    def __init__(self, tenant_name, username, password):
        self.tenant = tenant_name
        self.username = username
        self.password = password
        self.base_url = "http://localhost:"
        self.port_neutron = "9696"
        self.transit_domain_url = "/v2.0/transit-domains"
        self.pap_url = "/v2.0/physical-attachment-points"
        headers = {'accept': 'application/json', 'content-type':
                   'application/json'}

    def _get_access_token(self):
        """
            Function that returns Access Token from Keystone that
            is required to make REST calls to Neutron
            ARGUMENTS: none
            RETURN TYPE: String
        """

        # Set up auth URL
        url = CONF.identity.uri + "/tokens"

        # Set up Custom Headers for Request
        headers = {'accept': 'application/json', 'content-type':
                   'application/json'}

        # Set up parameters to send Authorization Details
        data = {"auth": {"passwordCredentials": {"username": self.username,
                         "password": self.password},
                         "tenantName": self.tenant}}

        body = jsonutils.dumps(data)
        response = requests.post(url, headers=headers, data=body)
        resp_body = response.json()

        return resp_body['access']['token']['id']

    def _authenticate(self):
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
        sefl._authenticate()

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
                td_id = UUID of Transit Domain
            RETURN TYPE: JSON
        """
        # Get authentication
        sefl._authenticate()

        url = self.base_url + self.port_neutron \
            + self.transit_domain_url + "/" + tdId
        response = requests.get(url, headers=self.headers)

        resp_body = response.json()

        # Return JSON of response
        return resp_body

    def list_transit_domain(self):
        """
            REST Function to list all (existing) Transit Domain
            ARGUMENTS: NONE
            RETURN TYPE: JSON
        """
        # Get authentication
        sefl._authenticate()

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
        sefl._authenticate()

        url = self.base_url + self.port_neutron \
            + self.transit_domain_url + "/" + td_id
        data = {"transit_domain": {"name": td_name}}
        body = jsonutils.dumps(data)
        response = requests.put(url, headers=self.headers, data=body)
        resp_body = jsonutils.loads(response.text)

        return resp_body

    def delete_transit_domain(self, **kwargs):
        """
            Function to delete Transit Domain with given ID of Transit Domain
            ARGUMENTS which kwargs MAY have:
                td_id = ID of Transit Domain (not tenant_id) to find TD by ID
                tdName = Name of Transit Domain
            RETURN TYPE: boolean [True, False]
        """
        # Get authentication
        sefl._authenticate()

        td_id = None
        if 'td_name' in kwargs:
            td_id = self._get_transit_domain_by_name(kwargs['td_name'])

            # if UUID of Transit Domain is not found
            if(tdId is None):
                return False
        else:
            td_id = kwargs['td_id']

        # Set up URL to specific access Transit Domain
        url = self.base_url + self.port_neutron \
            + self.transit_domain_url + "/" + td_id
        response = requests.delete(url, headers=self.headers)

        # if server deleted transit domain successfully then return true
        if(response.status_code == 204):
            return True
        else:
            return False

    def _get_transit_domain_by_name(self, td_name):
        """
            Function that resolves Transit Domain's Name to
            respective UUID. It returns None if UUID isn't resovled
        """
        all_tds = self.list_transit_domain()
        found_td = None

        for value in all_tds['transit_domains']:
            if(value['name'] == td_name):
                found_td = value['id']

        return found_td

    def createPap(self, **kwargs):
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

        # Set up URL to be accessed
        url = self.base_url + self.port_neutron + self.pap_url

        # Set up Custom Headers for Request
        headers = {'X-Auth-Token': self.accessToken,
                   'accept': 'application/json',
                   'content-type': 'application/json'}

        data = {"physical_attachment_point": kwargs}

        # Convert it into JSON
        dataInJson = jsonutils.dumps(data)

        # Send POST request to create PAP and get RESPONSE
        response = requests.post(url, headers=headers, data=dataInJson)

        # Convert response in JSON
        jsonResp = response.json()

        # Return JSON of response
        return jsonResp

    def showPap(self, papId):
        """
            Function to return a specific PAP
            ARGUMENTS:
                papId = ID of Physical Attachment Point
            RETURN TYPE: JSON
        """

        # Set up URL for a specific Transit Domain to be accessed
        url = self.base_url + self.port_neutron \
            + self.pap_url + "/" + papId

        # Set up Custom Headers for Request
        headers = {'X-Auth-Token': self.accessToken,
                   'accept': 'application/json',
                   'content-type': 'application/json'}

        # Send GET request and get RESPONSE
        response = requests.get(url, headers=headers)

        # Convert response in JSON
        jsonResp = response.json()

        # Return JSON of response
        return jsonResp

    def listPap(self):
        """
            REST Function to list all (existing) PAPs
            ARGUMENTS: NONE
            RETURN TYPE: JSON
        """

        # Set up URL to be accessed
        url = self.base_url + self.port_neutron + self.pap_url

        # Set up Custom Headers for Request
        headers = {'X-Auth-Token': self.accessToken,
                   'accept': 'application/json',
                   'content-type': 'application/json'}

        # Send GET request to List all TDs and get response in JSON
        response = requests.get(url, headers=headers)

        # Convert response in JSON
        jsonResp = response.json()

        # Return JSON of response
        return jsonResp

    def updatePap(self, papId, **kwargs):
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

        # Set up URL to specific access to PAP
        url = self.base_url + self.port_neutron \
            + self.pap_url + "/" + papId

        # Set up Custom Headers for Request
        headers = {'X-Auth-Token': self.accessToken,
                   'accept': 'application/json',
                   'content-type': 'application/json'}

        # Set up parameters to send PAP request according to variables
        data = {"physical_attachment_point": kwargs}

        # Convert it into JSON
        dataInJson = jsonutils.dumps(data)

        # Send PUT request to update Transit Domain Details
        response = requests.put(url, headers=headers, data=dataInJson)

        # NOTE: response returns 200 in normal cases
        # so get body.text which is String; converts it to JSON
        jsonResp = jsonutils.loads(response.text)

        # return JSON Response
        return jsonResp

    def deletePap(self, papId):
        """
            Function to delete PAP with given UUID
            ARGUMENTS:
                papId = ID of Physical Attachment Point to find it
            RETURN TYPE: boolean [True, False]
        """

        # Set up URL to specific access Transit Domain
        url = self.base_url + self.port_neutron \
            + self.pap_url + "/" + papId

        # Set up Custom Headers for Request
        headers = {'X-Auth-Token': self.accessToken,
                   'accept': 'application/json',
                   'content-type': 'application/json'}

        # Send PUT request to delete Transit Domain Details
        response = requests.delete(url, headers=headers)

        # if server deleted transit domain successfully then return true
        if(response.status_code == 204):
            return True
        else:
            return False
