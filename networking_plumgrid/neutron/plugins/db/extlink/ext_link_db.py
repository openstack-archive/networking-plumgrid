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

from neutron.db import common_db_mixin
from oslo_log import log as logging

LOG = logging.getLogger(__name__)


class ExtLinkMixin(common_db_mixin.CommonDbMixin):
    def get_ext_links(self, context, ext_list, filters=None, fields=None,
             sorts=None, limit=None, marker=None, page_reverse=None):
        """
        Gets the list of all the existing links/connectors for a tenant
        """
        return self._make_ext_link_dict(ext_list)

    def _make_ext_link_dict(self, ext_list):
        return ext_list
