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
from networking_plumgrid.neutron.plugins.common import \
    policy_exceptions as p_excep
from networking_plumgrid.neutron.plugins.db.policy.policy_tag_db \
    import PolicyTag
from networking_plumgrid.neutron.plugins.extensions import \
    endpointgroup as epgroup
from networking_plumgrid.neutron.plugins.extensions import \
    policytag
from neutron.api.v2 import attributes
from neutron.db import common_db_mixin
from neutron.db import model_base
from neutron.db import models_v2
from neutron.db import securitygroups_db
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
    description = sa.Column(sa.String(255))
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

        if "policy_tag_id" in ep_group and ep_group["policy_tag_id"]:
            # Check policy tag exists
            self._check_policy_tag(context, ep_group["policy_tag_id"])

            # Check policy tag is not already in use
            self._check_ptag_in_use(context, ep_group["policy_tag_id"])
        else:
            ep_group["policy_tag_id"] = None

        with context.session.begin(subtransactions=True):
            ep_group_db = EndpointGroup(tenant_id=ep_group["tenant_id"],
                                name=ep_group["name"],
                                policy_tag_id=ep_group["policy_tag_id"],
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
            try:
                query = self._model_query(context, securitygroups_db.SecurityGroup)
                ep_grp_db = query.filter_by(id=ep_grp_id).one()
            except exc.NoResultFound:
                raise epgroup.NoEndpointGroupFound(id=ep_grp_id)
            return self._make_ep_grp_dict_from_sec_grp_obj(context, ep_grp_db)

        return self._make_ep_grp_dict(ep_grp_db, fields)

    def get_endpoint_groups(self, context, filters=None, fields=None,
             sorts=None, limit=None, marker=None, page_reverse=None):
        """
        Gets the list of all the existing endpoint groups
        """
        endpoint_groups = self._get_collection(context, EndpointGroup,
                                    self._make_ep_grp_dict, filters=filters,
                                    sorts=sorts, limit=limit,
                                    marker_obj=marker, fields=fields,
                                    page_reverse=page_reverse)
        security_groups = self.get_security_groups(context, filters=filters,
                                                   fields=fields)
        return self._make_security_group_to_epg_dict(context, security_groups,
                                                     endpoint_groups)

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

    def update_endpoint_group(self, context, epg_id, endpoint_group):
        """
        Updates an existing endpoint group
        Args:
             epg_id:
                   uuid of the endpoint group being updated
             endpoint_group:
                   JSON with updated attributes of the endpoint group
                   name : name of endpoint group
                   tenant_id : tenant uuid
                   id : uuid of endpoint group
        """
        epg = endpoint_group["endpoint_group"]
        if not epg:
            raise epgroup.UpdateParametersRequired()

        with context.session.begin(subtransactions=True):
            try:
                query = self._model_query(context, EndpointGroup)
                epg_db = query.filter_by(id=epg_id).one()
            except exc.NoResultFound:
                raise epgroup.NoEndpointGroupFound(id=epg_id)
            if 'name' in epg:
                epg_db.update({"name": epg["name"]})
            if 'description' in epg:
                epg_db.update({"description": epg["description"]})
        return self._make_ep_grp_dict(epg_db)

    def _make_ep_grp_dict(self, epg, fields=None):
        ep_grp_dict = {"id": epg.id,
                       "name": epg.name,
                       "policy_tag_id": epg.policy_tag_id,
                       "description": epg.description,
                       "tenant_id": epg.tenant_id,
                       "is_security_group": False}
        return self._fields(ep_grp_dict, fields)

    def _make_ep_grp_dict_from_sec_grp_obj(self, context, sec_grp_obj):
        sec_grp_port_binding = self._get_port_security_group_bindings(context)
        epg_ports = []
        for port in sec_grp_port_binding:
            epg_ports.append(port["port_id"])
        epg_dict = {"id": sec_grp_obj["id"],
                    "name": sec_grp_obj["name"],
                    "description": sec_grp_obj["description"],
                    "policy_tag_id": None,
                    "tenant_id": sec_grp_obj["tenant_id"],
                    "is_security_group": True}
        return epg_dict

    def _make_security_group_to_epg_dict(self, context, secgrp_collection, epg_collection):
        """
        Make a dict to show security groups as part of
        endpoint group list
        Args:
            secgrp_collection: List of security groups
        """
        for sec_grp in secgrp_collection:
            if "name" not in sec_grp:
                sec_grp = self._make_security_group_dict(self._get_security_group(context, sec_grp['id']))
            epg_dict = {"id": sec_grp["id"],
                        "name": sec_grp["name"],
                        "description": sec_grp["description"],
                        "policy_tag_id": None,
                        "tenant_id": sec_grp["tenant_id"],
                        "is_security_group": True}
            epg_collection.append(epg_dict)
        return epg_collection

    def _check_policy_tag(self, context, ptag_id):
        query = context.session.query(PolicyTag)
        try:
            ptag = query.filter_by(id=ptag_id).one()
        except exc.NoResultFound:
            raise p_excep.NoPolicyTagFound(id=ptag_id)

    def _check_ptag_in_use(self, context, ptag_id):
        query = context.session.query(EndpointGroup)
        try:
            ptag = query.filter_by(policy_tag_id=ptag_id).one()
            if ptag:
                raise p_excep.PolicyTagAlreadyInUse(ptag_id=ptag_id,
                                                    epg_id=ptag.id)
        except exc.NoResultFound:
            pass
