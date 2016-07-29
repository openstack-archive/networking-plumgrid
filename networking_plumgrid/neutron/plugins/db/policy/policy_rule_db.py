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
from networking_plumgrid.neutron.plugins.db.policy.endpoint_group_db \
    import EndpointGroup
from networking_plumgrid.neutron.plugins.db.policy.policy_service_db \
    import PolicyService
from networking_plumgrid.neutron.plugins.db.policy.policy_tag_db \
    import PolicyTag
from neutron.api.v2 import attributes
from neutron.db import common_db_mixin
from neutron.db import model_base
from neutron.db import models_v2
from neutron.db.securitygroups_db import SecurityGroup
from oslo_log import log as logging
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm import exc

LOG = logging.getLogger(__name__)


class PolicyRule(model_base.BASEV2, models_v2.HasId,
                 models_v2.HasTenant):
    """DB definition for PLUMgrid policy rule object"""

    __tablename__ = "pg_policy_rules"

    name = sa.Column(sa.String(attributes.NAME_MAX_LEN))
    src_grp_epg = sa.Column(sa.String(36),
                        sa.ForeignKey("pg_endpoint_groups.id",
                                      ondelete="CASCADE"),
                        nullable=True)
    dst_grp_epg = sa.Column(sa.String(36),
                        sa.ForeignKey("pg_endpoint_groups.id",
                                      ondelete="CASCADE"),
                        nullable=True)

    src_grp_sg = sa.Column(sa.String(36),
                        sa.ForeignKey("securitygroups.id",
                                      ondelete="CASCADE"),
                        nullable=True)
    dst_grp_sg = sa.Column(sa.String(36),
                        sa.ForeignKey("securitygroups.id",
                                      ondelete="CASCADE"),
                        nullable=True)

    protocol = sa.Column(sa.Enum('any', 'icmp', 'tcp', 'udp',
                                 name='pg_policy_rules_protocol'))
    src_port_range = sa.Column(sa.String(attributes.NAME_MAX_LEN))
    dst_port_range = sa.Column(sa.String(attributes.NAME_MAX_LEN))
    action = sa.Column(sa.Enum('copy', 'allow',
                               name='pg_policies_rules_action'))
    action_target_service = sa.Column(sa.String(36),
                            sa.ForeignKey("pg_policy_services.id",
                                          ondelete="CASCADE"),
                            nullable=True)
    action_target_tenant_id = sa.Column(sa.String(36), nullable=True)
    tag = sa.Column(sa.String(36),
                    sa.ForeignKey("pg_policy_tags.id",
                                  ondelete="CASCADE"),
                    nullable=True)
    source_epg = orm.relationship(EndpointGroup,
                              backref=orm.backref('src_epg',
                              cascade='all,delete'),
                    primaryjoin="EndpointGroup.id==PolicyRule.src_grp_epg")
    destination_epg = orm.relationship(EndpointGroup,
                              backref=orm.backref('dst_epg',
                              cascade='all,delete'),
                    primaryjoin="EndpointGroup.id==PolicyRule.dst_grp_epg")
    source_sg = orm.relationship(SecurityGroup,
                              backref=orm.backref('src_sg',
                              cascade='all,delete'),
                    primaryjoin="SecurityGroup.id==PolicyRule.src_grp_sg")
    destination_sg = orm.relationship(SecurityGroup,
                              backref=orm.backref('dst_sg',
                              cascade='all,delete'),
                    primaryjoin="SecurityGroup.id==PolicyRule.dst_grp_sg")
    send_to_service = orm.relationship(PolicyService,
                              backref=orm.backref('service_binding',
                              cascade='all,delete'),
              primaryjoin="PolicyService.id==PolicyRule.action_target_service")
    policy_tag = orm.relationship(PolicyTag,
                              backref=orm.backref('tag_binding',
                              cascade='all,delete'),
                    primaryjoin="PolicyTag.id==PolicyRule.tag")


class PolicyRuleMixin(common_db_mixin.CommonDbMixin):
    def create_policy_rule(self, context, policy_rule):
        """
        creates a policy rule
        Args:
             policy_ryke:
                   JSON object with policy rule attributes
                   name : display name policy rule
                   tenant_id : tenant uuid
                   id : policy rule uuid
                   src_grp : source endpoint group for policy rule
                   dst_grp: destination endpoint group for policy rule
                   protocol: protocol for policy rule
                   action: action to be perfromed my policy rule
                   src_port_range: source port range of policy rule
                   dst_port_range: destination port range of policy rule
                   action_target: uuid of target policy service
                   tag: uuid of policy tag for policy rule
        """
        pr = policy_rule["policy_rule"]
        self._validate_src_grp_policy_rule_config(context, pr)
        self._validate_dst_grp_policy_rule_config(context, pr)
        self._configure_policy_rule_endpoint_groups(pr)
        self._validate_action_target(context, pr)
        if "tag" in pr:
            self._configure_policy_tag(context, pr)
        with context.session.begin(subtransactions=True):
            pr_db = PolicyRule(tenant_id=pr["tenant_id"],
                         name=pr["name"],
                         src_grp_epg=pr['src_grp_epg'],
                         dst_grp_epg=pr['dst_grp_epg'],
                         src_grp_sg=pr['src_grp_sg'],
                         dst_grp_sg= pr['dst_grp_sg'],
                         protocol=pr['protocol'],
                         src_port_range=pr['src_port_range'],
                         dst_port_range=pr['dst_port_range'],
                         action=pr['action'],
                         action_target_service=pr["action_target_service"],
                         action_target_tenant_id=pr["action_target_tenant_id"],
                         tag=pr['tag'])
            context.session.add(pr_db)
        return self._make_pr_dict(pr_db)

    def get_policy_rule(self, context, pr_id, fields=None):
        """
        Gets an existing policy rule
        """
        try:
            query = self._model_query(context, PolicyRule)
            pr_db = query.filter_by(id=pr_id).one()
        except exc.NoResultFound:
            raise p_excep.NoPolicyRuleFound(id=pr_id)
        return self._make_pr_dict(pr_db, fields)

    def get_policy_rules(self, context, filters=None, fields=None,
             sorts=None, limit=None, marker=None, page_reverse=None):
        """
        Gets the list of all the existing policy rules
        """
        return self._get_collection(context, PolicyRule,
                                    self._make_pr_dict, filters=filters,
                                    sorts=sorts, limit=limit,
                                    marker_obj=marker, fields=fields,
                                    page_reverse=page_reverse)

    def delete_policy_rule(self, context, pr_id):
        """
        Deletes an existing policy rule
        """
        try:
            query = context.session.query(PolicyRule)
            pr_db = query.filter_by(id=pr_id).first()
        except exc.NoResultFound:
            raise p_excep.NoPolicyRuleFound(id=pr_id)
        context.session.delete(pr_db)

    def _validate_src_grp_policy_rule_config(self, context, pr):
        """
            Validate source group config for policy rule
        """
        if pr["src_grp"] is not None:
            is_security_group = False
            if self._check_endpoint_group_for_policy_rule(context,
                                                          pr["src_grp"]):
                pr["src_security_group"] = is_security_group
                return
            if self._check_security_group_for_policy_rule(context,
                                                          pr["src_grp"]):
                is_security_group = True
                pr["src_security_group"] = is_security_group
                return
            raise p_excep.InvalidPolicyRuleConfig(epg='source-group')
        else:
            pr["src_security_group"] = None

    def _validate_dst_grp_policy_rule_config(self, context, pr):
        """
            Validate destination group config for policy rule
        """
        if pr["dst_grp"] is not None:
            is_security_group = False
            if self._check_endpoint_group_for_policy_rule(context,
                                                          pr["dst_grp"]):
                pr["dst_security_group"] = is_security_group
                return
            if self._check_security_group_for_policy_rule(context,
                                                          pr["dst_grp"]):
                is_security_group = True
                pr["dst_security_group"] = is_security_group
                return
            raise p_excep.InvalidPolicyRuleConfig(epg='destination-group')
        else:
            pr["dst_security_group"] = None

    def _check_endpoint_group_for_policy_rule(self, context, epg_id):
        try:
            query = context.session.query(EndpointGroup)
            epg_db = query.filter_by(id=epg_id).one()
            if epg_db["id"] == epg_id:
                return True
        except exc.NoResultFound:
            return False

    def _check_security_group_for_policy_rule(self, context, sg_id):
        try:
            query = context.session.query(SecurityGroup)
            sg_db = query.filter_by(id=sg_id).one()
            if sg_db["id"] == sg_id:
                return True
        except exc.NoResultFound:
            return False

    def _configure_policy_rule_endpoint_groups(self, pr):
        if pr['src_security_group'] is None:
            pr['src_grp_epg'] = None
            pr['src_grp_sg'] = None
        elif pr['src_security_group']:
            pr['src_grp_epg'] = None
            pr['src_grp_sg'] = pr['src_grp']
        else:
            pr['src_grp_epg'] = pr['src_grp']
            pr['src_grp_sg'] = None
        if pr['dst_security_group'] is None:
            pr['dst_grp_epg'] = None
            pr['dst_grp_sg'] = None
        elif pr['dst_security_group']:
            pr['dst_grp_epg'] = None
            pr['dst_grp_sg'] = pr['dst_grp']
        else:
            pr['dst_grp_epg'] = pr['dst_grp']
            pr['dst_grp_sg'] = None

    def _make_pr_dict(self, pr, fields=None):
        if pr.src_grp_epg is None and pr.src_grp_sg is None:
            src_grp = None
        elif pr.src_grp_epg is None:
            src_grp = pr.src_grp_sg
        else:
            src_grp = pr.src_grp_epg
        if pr.dst_grp_epg is None and pr.dst_grp_sg is None:
            dst_grp = None
        elif pr.dst_grp_epg is None:
            dst_grp = pr.dst_grp_sg
        else:
            dst_grp = pr.dst_grp_epg

        action_target = ((str(pr.action_target_tenant_id) + ":" if
                         pr.action_target_tenant_id else "") +
                         (pr.action_target_service if
                         pr.action_target_service else ""))
        if not action_target:
            action_target = None

        pr_dict = {"id": pr.id,
                   "name": pr.name,
                   "src_grp": src_grp,
                   "dst_grp": dst_grp,
                   "protocol": pr.protocol,
                   "src_port_range": pr.src_port_range,
                   "dst_port_range": pr.dst_port_range,
                   "action": pr.action,
                   "action_target": action_target,
                   "tag": pr.tag,
                   "tenant_id": pr.tenant_id}
        return self._fields(pr_dict, fields)

    def _validate_action_target(self, context, pr):
        tenant_id = None
        action_target_id = None
        if pr["action_target"] is None:
            pr["action_target_service"] = None
            pr["action_target_tenant_id"] = None
        else:
            action_target = pr["action_target"].split(":")
            if len(action_target) == 1:
                action_target_id = action_target[0]
            elif len(action_target) == 2:
                tenant_id = action_target[0]
                action_target_id = action_target[1]
            else:
                raise p_excep.InvalidFormatActionTarget()
            if tenant_id is None:
                try:
                    query = context.session.query(PolicyService)
                    ps_db = query.filter_by(id=action_target_id).one()
                    if ps_db["id"] == action_target_id:
                        pr["action_target_service"] = pr["action_target"]
                        pr["action_target_tenant_id"] = None
                except exc.NoResultFound:
                    raise p_excep.NoActionTargetFound(at=action_target_id)
            else:
                try:
                    query = context.session.query(PolicyService)
                    ps_db = query.filter_by(id=action_target_id,
                                            tenant_id=tenant_id).one()
                    if ps_db["id"] == action_target_id:
                        pr["action_target_service"] = action_target_id
                        pr["action_target_tenant_id"] = tenant_id
                except exc.NoResultFound:
                    raise p_excep.NoActionTargetFound(at=action_target_id)

    def _configure_policy_tag(self, context, pr):
        ep_grp = pr["tag"]
        if ep_grp is None:
            return None
        else:
            try:
                query = context.session.query(PolicyTag)
                pt_db = query.filter_by(id=ep_grp).one()
                pr["tag"] = pt_db["id"]
            except exc.NoResultFound:
                try:
                    query = context.session.query(EndpointGroup)
                    epg_db = query.filter_by(id=ep_grp).one()
                    if ("policy_tag_id" not in epg_db or
                        epg_db["policy_tag_id"] is None):
                        raise p_excep.NoPolicyTagFoundEndpointGroup(epg=ep_grp)
                    pr["tag"] = epg_db["policy_tag_id"]
                except exc.NoResultFound:
                    raise p_excep.NoPolicyTagFoundEndpointGroup(epg=ep_grp)
