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
from networking_plumgrid.neutron.plugins.common import \
    policy_exceptions as p_excep
from networking_plumgrid.neutron.plugins.extensions import \
    policytag
from neutron.api.v2 import attributes
from neutron.db import common_db_mixin
from neutron.db.l3_db import FloatingIP
from neutron.db import model_base
from neutron.db import models_v2
from oslo_log import log as logging
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm import exc

LOG = logging.getLogger(__name__)


class PolicyTag(model_base.BASEV2, models_v2.HasId,
                models_v2.HasTenant):
    """DB definition for PLUMgrid Policy Tag object"""

    __tablename__ = "pg_policy_tags"

    name = sa.Column(sa.String(attributes.NAME_MAX_LEN))
    tag_type = sa.Column(sa.Enum('fip', 'dot1q', 'nsh',
                                name='policy_tag_type'))
    floatingip_address = sa.Column(sa.String(255))
    tag_id = sa.Column(sa.String(255))
    tenant_id = sa.Column(sa.String(36))
    router_id = sa.Column(sa.String(36))
    floatingip_id = sa.Column(sa.String(36),
                            sa.ForeignKey("floatingips.id",
                            ondelete="CASCADE"),
                            nullable=True)

    fp = orm.relationship(FloatingIP,
              backref=orm.backref("fp_binding",
                                  lazy="joined", cascade="all,delete"),
  primaryjoin="FloatingIP.id==PolicyTag.floatingip_id")


class PolicyTagMixin(common_db_mixin.CommonDbMixin):
    def create_policy_tag(self, context, policy_tag):
        """
        Creates a policy tag with specified tag type
        Args:
             policy_tag:
                   JSON object with policy tag attributes
                   name : display name policy tag
                   tenant_id : tenant uuid
                   id : endpoint group uuid
                   type : type of policy tag (fip|dot1q|nsh)
                   tag_id : tag id in range xx-yy
        """
        ptag = policy_tag["policy_tag"]

        if "floatingip_id" in ptag and ptag["floatingip_id"]:
            self._check_floatingip_in_use(context, ptag["floatingip_id"])

        with context.session.begin(subtransactions=True):
            ptag_db = PolicyTag(tenant_id=ptag["tenant_id"],
                                name=ptag["name"],
                                tag_type=ptag["tag_type"],
                                floatingip_id=ptag["floatingip_id"],
                                floatingip_address=ptag["floating_ip_address"],
                                router_id=ptag["router_id"],
                                tag_id=ptag["tag_id"])
            context.session.add(ptag_db)
        return self._make_ptag_dict(ptag_db)

    def get_policy_tag(self, context, ptag_id, fields=None):
        """
        Gets an existing policy tag
        Args:
             policy_tag_id = uuid of the policy tag being requested
        """
        try:
            query = self._model_query(context, PolicyTag)
            ptag_db = query.filter_by(id=ptag_id).one()
        except exc.NoResultFound:
            raise policytag.NoPolicyTagFound(id=ptag_id)
        return self._make_ptag_dict(ptag_db, fields)

    def get_policy_tags(self, context, filters=None, fields=None,
             sorts=None, limit=None, marker=None, page_reverse=None):
        """
        Gets the list of all the existing policy tags
        """
        return self._get_collection(context, PolicyTag,
                                    self._make_ptag_dict, filters=filters,
                                    sorts=sorts, limit=limit,
                                    marker_obj=marker, fields=fields,
                                    page_reverse=page_reverse)

    def delete_policy_tag(self, context, ptag_id):
        """
        Deletes an existing Policy tag
        Args:
             epg_id = uuid of the policy tag being deleted
        """
        try:
            query = context.session.query(PolicyTag)
            ptag_db = query.filter_by(id=ptag_id).first()
        except exc.NoResultFound:
            raise policytag.NoPolicyTagFound(id=ptag_id)
        with context.session.begin(subtransactions=True):
            context.session.delete(ptag_db)

    def update_policy_tag(self, context, ptag_id, policy_tag):
        """
        Updates an existing policy tag
        Args:
             ptag_id:
                   uuid of the policy tag being updated
             policy_tag:
                   JSON with updated attributes of the policy tag
                   name : name of policy tag
                   tenant_id : tenant uuid
                   id : uuid of policy tag
        """
        ptag = policy_tag["policy_tag"]
        if not ptag:
            raise policytag.UpdateParametersRequired()

        with context.session.begin(subtransactions=True):
            try:
                query = self._model_query(context, PolicyTag)
                ptag_db = query.filter_by(id=ptag_id).one()
            except exc.NoResultFound:
                raise policytag.NoPolicyTagFound(id=ptag_id)
            if 'name' in ptag:
                ptag_db.update({"name": ptag["name"]})
        return self._make_ptag_dict(ptag_db)

    def _make_ptag_dict(self, ptag, fields=None):
        ptag_dict = {"id": ptag.id,
                    "name": ptag.name,
                    "tag_type": ptag.tag_type,
                    "tag_id": ptag.tag_id,
                    "floatingip_id": ptag.floatingip_id,
                    "floating_ip_address": ptag.floatingip_address,
                    "router_id": ptag.router_id,
                    "tenant_id": ptag.tenant_id}
        return self._fields(ptag_dict, fields)

    def _check_floatingip_in_use(self, context, fp_id):
        query = context.session.query(PolicyTag)
        try:
            ptag = query.filter_by(floatingip_id=fp_id).one()
            if ptag:
                raise p_excep.FloatingIPAlreadyInUse(id=fp_id)
        except exc.NoResultFound:
            pass
