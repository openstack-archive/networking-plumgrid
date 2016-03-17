# Copyright 2016 PLUMgrid, Inc. All Rights Reserved.
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

from plumgrid_tempest_plugin.services import base

class PAPClient(base.BasePGClient):

	def create_pap(self, **kwargs):
		uri = '/physical-attachment-points'
		post_data = {'physical_attachment_points': kwargs}
		return self.create_resource(uri, post_data)
		#my_pgClient = base.BasePGClient() # Created object of BasePGClient class
		#return my_pgClient.create_resource(uri, post_data)

	def update_pap(self, pap_id, **kwargs):
		uri = '/physical-attachment-points%s' % pap_id
		put_data = {'physical_attachment_points': kwargs}
		return self.update_resource(uri, put_data)

	def show_pap(self, pap_id, **fields):
		uri = "/physical-attachment-points%s" % pap_id
		return self.show_resource(uri, **fields)

	def list_paps(self, **filters):
		uri = "/physical-attachment-points"
		return self.list_resources(uri, **filters)

	def delete_pap(self, pap_id):
		uri = '/physical-attachment-points%s' % pap_id
		return self.delete_resource(uri)

	def doSomething(self):
		print "Don't Mind! This is just a useless function."
