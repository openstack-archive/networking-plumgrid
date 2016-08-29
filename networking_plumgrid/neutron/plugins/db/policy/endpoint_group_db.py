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
from networking_plumgrid.neutron.plugins.db.policy.policy_tag_db \
    import PolicyTag
from networking_plumgrid.neutron.plugins.extensions import \
    endpointgroup as epgroup
from neutron.api.v2 import attributes
from neutron.db import common_db_mixin
from neutron.db import model_base
from neutron.db import models_v2
from neutron.db import securitygroups_db
from neutron.db.securitygroups_db import SecurityGroup
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
                                            ondelete="RESTRICT"),
                              nullable=True)
    ptags = orm.relationship(PolicyTag,
                             backref=orm.backref('p_tag'),
                    primaryjoin="PolicyTag.id==EndpointGroup.policy_tag_id")


class SecurityPolicyTagBinding(model_base.BASEV2):
    """
    DB definition for storing Security Groups and
    Policy Tag mapping
    """
    __tablename__ = "pg_security_policy_tag_binding"

    security_group_id = sa.Column(sa.String(length=36),
                                  sa.ForeignKey("securitygroups.id",
                                                ondelete='CASCADE'),
                                  primary_key=True)
    policy_tag_id = sa.Column(sa.String(length=36),
                              sa.ForeignKey("pg_policy_tags.id",
                                            ondelete='RESTRICT'),
                              nullable=False)

    ep = orm.relationship(SecurityGroup,
              backref=orm.backref("sg_binding",
                                  lazy="joined",
                                  cascade="all,delete"),
  primaryjoin="SecurityGroup.id==SecurityPolicyTagBinding.security_group_id")


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
                query = self._model_query(context,
                                          securitygroups_db.SecurityGroup)
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
        is_security_group = False
        if not epg:
            raise epgroup.UpdateParametersRequired()

        with context.session.begin(subtransactions=True):
            try:
                query = self._model_query(context, EndpointGroup)
                epg_db = query.filter_by(id=epg_id).one()
            except exc.NoResultFound:
                is_security_group = self._is_security_group(context, epg_id)
                if is_security_group is True:
                    query = self._model_query(context,
                                              securitygroups_db.SecurityGroup)
                    ep_grp_db = query.filter_by(id=epg_id).one()
                else:
                    raise epgroup.NoEndpointGroupFound(id=epg_id)
            if is_security_group is True:
                if 'name' in epg or 'description' in epg:
                    raise epgroup.SGUpdateDisallowed()
                if 'add_tag' in epg:
                    sg_grp_db = SecurityPolicyTagBinding(
                                            security_group_id=epg_id,
                                            policy_tag_id=epg["add_tag"])
                    context.session.add(sg_grp_db)
                if 'remove_tag' in epg:
                    try:
                        query = self._model_query(context,
                                                  SecurityPolicyTagBinding)
                        query.filter_by(policy_tag_id=epg["remove_tag"]).one()
                    except exc.NoResultFound:
                        raise p_excep.NoPolicyTagAssociation(
                                                         id=epg['remove_tag'],
                                                         epg_id=epg_id)
                    query = self._model_query(context,
                                              SecurityPolicyTagBinding)
                    query.filter_by(security_group_id=epg_id,
                                    policy_tag_id=epg["remove_tag"]).delete()
            else:
                if 'name' in epg:
                    epg_db.update({"name": epg["name"]})
                if 'description' in epg:
                    epg_db.update({"description": epg["description"]})
                if 'add_tag' in epg:
                    epg_db.update({"policy_tag_id": epg["add_tag"]})
                if 'remove_tag' in epg:
                    if epg_db["policy_tag_id"]:
                        epg_db["policy_tag_id"] = None
                    else:
                        raise p_excep.NoPolicyTagAssociation(
                                                         id=epg['remove_tag'],
                                                         epg_id=epg_id)
        if is_security_group is True:
            return self._make_ep_grp_dict_from_sec_grp_obj(context, ep_grp_db)
        else:
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
        sg_map = self._get_security_policy_tag_binding(context,
                                                       sec_grp_obj["id"])
        epg_dict = {"id": sec_grp_obj["id"],
                    "name": sec_grp_obj["name"],
                    "description": sec_grp_obj["description"],
                    "policy_tag_id": None,
                    "tenant_id": sec_grp_obj["tenant_id"],
                    "is_security_group": True}
        if sg_map and sg_map["security_group_id"] == sec_grp_obj["id"]:
            epg_dict["policy_tag_id"] = sg_map["policy_tag_id"]
        return epg_dict

    def _make_security_group_to_epg_dict(self, context, secgrp_collection,
                                         epg_collection):
        """
        Make a dict to show security groups as part of
        endpoint group list
        Args:
            secgrp_collection: List of security groups
        """
        for sec_grp in secgrp_collection:
            if "name" not in sec_grp:
                sec_grp = self._make_security_group_dict(
                              self._get_security_group(context, sec_grp['id']))
            sg_map = self._get_security_policy_tag_binding(context,
                                                           sec_grp["id"])
            epg_dict = {"id": sec_grp["id"],
                        "name": sec_grp["name"],
                        "description": sec_grp["description"],
                        "policy_tag_id": None,
                        "tenant_id": sec_grp["tenant_id"],
                        "is_security_group": True}
            if sg_map and sg_map["security_group_id"] == sec_grp["id"]:
                epg_dict["policy_tag_id"] = sg_map["policy_tag_id"]
            epg_collection.append(epg_dict)
        return epg_collection

    def _check_policy_tag(self, context, ptag_id):
        query = context.session.query(PolicyTag)
        try:
            query.filter_by(id=ptag_id).one()
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
            try:
                query = self._model_query(context,
                                          SecurityPolicyTagBinding)
                sg_map = query.filter_by(policy_tag_id=ptag_id).one()
                if sg_map:
                    raise p_excep.PolicyTagAlreadyInUseSG(ptag_id=ptag_id,
                                              sg_id=sg_map.security_group_id)
            except exc.NoResultFound:
                pass

    def _is_security_group(self, context, epg_id):
        epg_id_list = self.get_endpoint_groups(context,
                                               filters={'id': [epg_id]},
                                               fields=["id"])
        if len(epg_id_list) == 1:
            if ("is_security_group" in epg_id_list[0]
                and epg_id_list[0]["is_security_group"]):
                return True

    def _get_security_policy_tag_binding(self, context, sg_id):
        query = self._model_query(context,
                                  SecurityPolicyTagBinding)
        sg_map = {}
        try:
            sg_map = query.filter_by(security_group_id=sg_id).one()
            return sg_map
        except exc.NoResultFound:
            return sg_map
