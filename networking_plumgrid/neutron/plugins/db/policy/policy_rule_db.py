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

from networking_plumgrid.neutron.plugins.common import constants
from networking_plumgrid.neutron.plugins.db.policy.endpoint_group_db \
    import EndpointGroup
from networking_plumgrid.neutron.plugins.db.policy.policy_tag_db \
    import PolicyTag
from networking_plumgrid.neutron.plugins.extensions import \
    policyrule
from neutron.api.v2 import attributes
from neutron.db import common_db_mixin
from neutron.db import model_base
from neutron.db import models_v2
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
                                 name='pg_policy_rule_protocol'))
    src_port_range = sa.Column(sa.String(attributes.NAME_MAX_LEN))
    dst_port_range = sa.Column(sa.String(attributes.NAME_MAX_LEN))
    action = sa.Column(sa.Enum('copy', 'allow', 'redirect',
                               name='pg_policy_action'))
    action_target_service = sa.Column(sa.String(36),
                            sa.ForeignKey("pg_policy_services.id",
                                          ondelete="CASCADE"),
                            nullable=True)
    action_target_service_chain = sa.Column(sa.String(36),
                                  sa.ForeignKey("pg_policy_service_chains.id",
                                                ondelete="CASCADE"),
                                  nullable=True)
    action_target_tenant_id = tag = sa.Column(sa.String(36))
    tag = sa.Column(sa.String(36),
                    sa.ForeignKey("pg_policy_tags.id",
                                  ondelete="CASCADE"),
                    nullable=True)

    policy_tags = orm.relationship(PolicyTag,
                              backref=orm.backref('prule_tag',
                              cascade='all,delete'),
                    primaryjoin="PolicyTag.id==PolicyRule.tag")

    source_group = orm.relationship(EndpointGroup,
                              backref=orm.backref('source_ep',
                              cascade='all,delete'),
                    primaryjoin="EndpointGroup.id==PolicyRule.src_grp_epg")
    dest_group = orm.relationship(EndpointGroup,
                              backref=orm.backref('destination_ep',
                              cascade='all,delete'),
                    primaryjoin="EndpointGroup.id==PolicyRule.src_grp_epg")
    send_to = orm.relationship(EndpointGroup,
                              backref=orm.backref('send_to_ep',
                              cascade='all,delete'),
                    primaryjoin="EndpointGroup.id==PolicyRule.src_grp_epg")


class PolicyRuleMixin(common_db_mixin.CommonDbMixin):
    def create_policy_rule(self, context, policy_rule):
        pass

    def get_policy_rule(self, context, policy_rule_id, fields=None):
        pass

    def get_policy_rules(self, context, filters=None, fields=None,
             sorts=None, limit=None, marker=None, page_reverse=None):
        pass

    def delete_policy_rule(self, context, policy_rule_id):
        pass
