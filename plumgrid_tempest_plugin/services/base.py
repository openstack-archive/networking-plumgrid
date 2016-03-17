# Copyright 2015 PLUMgrid, Inc. All Rights Reserved.
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

from oslo_serialization import jsonutils as json
from six.moves.urllib import parse as urllib
from tempest.common import service_client


class BasePGClient(service_client.ServiceClient):

    """Base class for Tempest REST clients for Neutron.

    Child classes use v2 of the Neutron API, since the V1 API has been
    removed from the code base.
    """

    version = '2.0'
    uri_prefix = "v2.0"

    def list_resources(self, uri, **filters):
        req_uri = self.uri_prefix + uri
        if filters:
            req_uri += '?' + urllib.urlencode(filters, doseq=1)
        resp, body = self.get(req_uri)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return rest_client.ResponseBody(resp, body)

    def delete_resource(self, uri):
        req_uri = self.uri_prefix + uri
        resp, body = self.delete(req_uri)
        self.expected_success(204, resp.status)
        return rest_client.ResponseBody(resp, body)

    def show_resource(self, uri, **fields):
        # fields is a dict which key is 'fields' and value is a
        # list of field's name. An example:
        # {'fields': ['id', 'name']}
        req_uri = self.uri_prefix + uri
        if fields:
            req_uri += '?' + urllib.urlencode(fields, doseq=1)
        resp, body = self.get(req_uri)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return rest_client.ResponseBody(resp, body)

    def create_resource(self, uri, post_data):
        req_uri = self.uri_prefix + uri
        req_post_data = json.dumps(post_data)
        resp, body = self.raw_request(req_uri, "POST", body=req_post_data)
        body = json.loads(body)
        self.expected_success(201, resp.status)
        return rest_client.ResponseBody(resp, body)

    def update_resource(self, uri, post_data):
        req_uri = self.uri_prefix + uri
        req_post_data = json.dumps(post_data)
        resp, body = self.put(req_uri, req_post_data)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return rest_client.ResponseBody(resp, body)
