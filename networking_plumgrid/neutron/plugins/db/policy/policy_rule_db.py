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
from networking_plumgrid.neutron.plugins.db.policy.policy_group_db \
    import PolicyGroup
from networking_plumgrid.neutron.plugins.extensions import \
    policy_rule
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
    tag = sa.Column(sa.String(attributes.NAME_MAX_LEN))
    action_target = sa.Column(sa.String(attributes.NAME_MAX_LEN))
    src_grp_pg = sa.Column(sa.String(36),
                        sa.ForeignKey("pg_policy_groups.id",
                                      ondelete="CASCADE"),
                        nullable=True)
    dst_grp_pg = sa.Column(sa.String(36),
                        sa.ForeignKey("pg_policy_groups.id",
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
                               name='pg_policie_rules_action'))
    source_group = orm.relationship(PolicyGroup,
                              backref=orm.backref('source_ep',
                              cascade='all,delete'),
                    primaryjoin="PolicyGroup.id==PolicyRule.src_grp_pg")
    dest_group = orm.relationship(PolicyGroup,
                              backref=orm.backref('destination_ep',
                              cascade='all,delete'),
                    primaryjoin="PolicyGroup.id==PolicyRule.src_grp_pg")
    send_to = orm.relationship(PolicyGroup,
                              backref=orm.backref('send_to_ep',
                              cascade='all,delete'),
                    primaryjoin="PolicyGroup.id==PolicyRule.src_grp_pg")


class PolicyRuleMixin(common_db_mixin.CommonDbMixin):
    def create_policy_rule(self, context, policy_rule):
        return

    def get_policy_rule(self, context, policy_rule_id, fields=None):
        return

    def get_policy_rules(self, context, filters=None, fields=None,
             sorts=None, limit=None, marker=None, page_reverse=None):
        return

    def delete_policy_rule(self, context, policy_rule_id):
        return
