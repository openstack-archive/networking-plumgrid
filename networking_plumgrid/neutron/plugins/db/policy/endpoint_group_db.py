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
from networking_plumgrid.neutron.plugins.db.policy.policy_tag_db \
    import PolicyTag
from networking_plumgrid.neutron.plugins.extensions import \
    endpointgroup as epgroup
from neutron.api.v2 import attributes
from neutron.db import common_db_mixin
from neutron.db import model_base
from neutron.db import models_v2
from oslo_log import log as logging
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm import exc

LOG = logging.getLogger(__name__)


class EndpointGroup(model_base.BASEV2, models_v2.HasId,
                    models_v2.HasTenant):
    """DB definition for PLUMgrid endpoint group object"""

    __tablename__ = "pg_endpoint_groups"

    name = sa.Column(sa.String(attributes.NAME_MAX_LEN))
    description = sa.Column(sa.String(attributes.LONG_DESCRIPTION_MAX_LEN))
    policy_tag_id = sa.Column(sa.String(36),
                              sa.ForeignKey("pg_policy_tags.id",
                                            ondelete="CASCADE"),
                              nullable=True)
    ptags = orm.relationship(PolicyTag,
                              backref=orm.backref('p_tag',
                              cascade='all,delete'),
                    primaryjoin="PolicyTag.id==EndpointGroup.policy_tag_id")


class EndpointGroupMixin(common_db_mixin.CommonDbMixin):
    def create_endpoint_group(self, context, endpoint_group):
        """
        Creates a endpoint group with with optional policy tag
        Args:
             endpoint_group:
                   JSON object with policy group attributes
                   name : display name policy tag
                   tenant_id : tenant uuid
                   id : endpoint group uuid
                   description : description for endpoint group
                   tag : policy tag uuid/name
        """
        ep_group = endpoint_group["endpoint_group"]

        with context.session.begin(subtransactions=True):
            ep_group_db = EndpointGroup(tenant_id=ep_group["tenant_id"],
                                name=ep_group["name"],
                                policy_tag_id=ep_group["tag"],
                                description=ep_group["description"])
            context.session.add(ep_group_db)
        return self._make_ep_grp_dict(ep_group_db)

    def get_endpoint_group(self, context, ep_grp_id, fields=None):
        """
        Gets an existing endpoint group
        Args:
             ep_grp_id = uuid of the policy group being requested
        """
        try:
            query = self._model_query(context, EndpointGroup)
            ep_grp_db = query.filter_by(id=ep_grp_id).one()
        except exc.NoResultFound:
            raise epgroup.NoEndpointGroupFound(id=ep_grp_id)
        return self._make_ep_grp_dict(ep_grp_db, fields)

    def get_endpoint_groups(self, context, filters=None, fields=None,
             sorts=None, limit=None, marker=None, page_reverse=None):
        """
        Gets the list of all the existing endpoint groups
        """
        return self._get_collection(context, EndpointGroup,
                                    self._make_ep_grp_dict, filters=filters,
                                    sorts=sorts, limit=limit,
                                    marker_obj=marker, fields=fields,
                                    page_reverse=page_reverse)

    def delete_endpoint_group(self, context, ep_grp_id):
        """
        Deletes an existing endpoint group
        Args:
             ep_grp_id = uuid of the endpoint group being deleted
        """
        try:
            query = context.session.query(EndpointGroup)
            ep_grp_db = query.filter_by(id=ep_grp_id).first()
        except exc.NoResultFound:
            raise epgroup.NoEndpointGroupFound(id=ep_grp_id)
        with context.session.begin(subtransactions=True):
            context.session.delete(ep_grp_db)

    def _make_ep_grp_dict(self, epg, fields=None):
        ep_grp_dict = {"id": epg.id,
                       "name": epg.name,
                       "tag": epg.policy_tag_id,
                       "description": epg.description,
                       "tenant_id": epg.tenant_id}
        return self._fields(ep_grp_dict, fields)
