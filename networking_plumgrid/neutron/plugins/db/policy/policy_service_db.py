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
import json
from networking_plumgrid._i18n import _LI
from networking_plumgrid.neutron.plugins.common import \
    constants
from networking_plumgrid.neutron.plugins.extensions import \
    policyservice
from neutron.api.v2 import attributes
from neutron.db import common_db_mixin
from neutron.db import model_base
from neutron.db import models_v2
from oslo_log import log as logging
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm import exc

LOG = logging.getLogger(__name__)


class PolicyService(model_base.BASEV2, models_v2.HasId,
                    models_v2.HasTenant):
    """DB definition for PLUMgrid policy service object"""

    __tablename__ = "pg_policy_services"

    name = sa.Column(sa.String(attributes.NAME_MAX_LEN))
    description = sa.Column(sa.String(attributes.LONG_DESCRIPTION_MAX_LEN))

    ingress_grp = sa.Column(sa.String(36),
                        sa.ForeignKey("pg_service_port_group.id",
                                      ondelete="CASCADE"),
                        nullable=True)
    egress_grp = sa.Column(sa.String(36),
                        sa.ForeignKey("pg_service_port_group.id",
                                      ondelete="CASCADE"),
                        nullable=True)


class PolicyServiceMixin(common_db_mixin.CommonDbMixin):
    def create_policy_service(self, context, policy_service):
        return

    def get_policy_service(self, context, policy_service_id, fields=None):
        return

    def get_policy_services(self, context, filters=None, fields=None,
             sorts=None, limit=None, marker=None, page_reverse=None):
        return

    def delete_policy_service(self, context, policy_service_id):
        return
