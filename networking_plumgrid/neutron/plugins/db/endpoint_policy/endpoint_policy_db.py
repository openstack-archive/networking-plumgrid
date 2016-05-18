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
from networking_plumgrid.neutron.plugins.db.endpoint_group.endpoint_group_db \
    import EndpointGroup
from networking_plumgrid.neutron.plugins.extensions import \
    endpointpolicy as ep_policy
from neutron.api.v2 import attributes
from neutron.db import common_db_mixin
from neutron.db import model_base
from neutron.db import models_v2
from oslo_log import log as logging
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm import exc

LOG = logging.getLogger(__name__)


class EndpointPolicy(model_base.BASEV2, models_v2.HasId,
                    models_v2.HasTenant):
    """DB definition for PLUMgrid endpoint policy object"""

    __tablename__ = "pg_endpoint_policies"

    name = sa.Column(sa.String(attributes.NAME_MAX_LEN))
    src_grp = sa.Column(sa.String(36),
                        sa.ForeignKey("pg_endpoint_groups.id",
                                      ondelete="CASCADE"),
                        nullable=True)
    dst_grp = sa.Column(sa.String(36),
                        sa.ForeignKey("pg_endpoint_groups.id",
                                      ondelete="CASCADE"),
                        nullable=True)
    protocol = sa.Column(sa.Enum('any', 'icmp', 'tcp', 'udp',
                                 name='pg_endpoint_policies_protocol'))
    src_port_range = sa.Column(sa.String(attributes.NAME_MAX_LEN))
    dst_port_range = sa.Column(sa.String(attributes.NAME_MAX_LEN))
    action = sa.Column(sa.Enum('copy',
                               name='pg_endpoint_policies_action'))
    service_epg = sa.Column(sa.String(36),
                            sa.ForeignKey("pg_endpoint_groups.id",
                                          ondelete="CASCADE"),
                            nullable=True)
    source_group = orm.relationship(EndpointGroup,
                              backref=orm.backref('source_ep',
                              cascade='all,delete'),
                    primaryjoin="EndpointGroup.id==EndpointPolicy.src_grp")
    dest_group = orm.relationship(EndpointGroup,
                              backref=orm.backref('destination_ep',
                              cascade='all,delete'),
                    primaryjoin="EndpointGroup.id==EndpointPolicy.src_grp")
    send_to = orm.relationship(EndpointGroup,
                              backref=orm.backref('send_to_ep',
                              cascade='all,delete'),
                    primaryjoin="EndpointGroup.id==EndpointPolicy.src_grp")


class EndpointPolicyMixin(common_db_mixin.CommonDbMixin):
    def create_endpoint_policy(self, context, endpoint_policy):
        """
        creates a endpoint policy
        Args:
             endpoint_group:
                   JSON object with endpoint policy attributes
                   name : display name endpoint policy
                   tenant_id : tenant uuid
                   id : endpoint policy uuid
                   src_grp : source endpoint group for policy
                   dst_grp: destination endpoint group for policy
                   protocol: protocol for policy
                   action: action to be perfromed my policy
                   src_port_range: source port range of policy
                   dst_port_range: destination port range of policy
                   service_endpoint_group: uuid of service endpoint group
        """
        epp = endpoint_policy["endpoint_policy"]
        self._validate_endpoint_policy_config(context, epp)
        with context.session.begin(subtransactions=True):
            epp_db = EndpointPolicy(tenant_id=epp["tenant_id"],
                                   name=epp["name"],
                                   src_grp=epp['src_grp'],
                                   dst_grp=epp['dst_grp'],
                                   protocol=epp['protocol'],
                                   src_port_range=epp['src_port_range'],
                                   dst_port_range=epp['dst_port_range'],
                                   action=epp['action'],
                                   service_epg=epp["service_endpoint_group"])
            context.session.add(epp_db)
        return self._make_epp_dict(epp_db)

    def _make_epp_dict(self, epp, fields=None):
        epp_dict = {"id": epp.id,
                    "name": epp.name,
                    "src_grp": epp.src_grp,
                    "dst_grp": epp.dst_grp,
                    "protocol": epp.protocol,
                    "src_port_range": epp.src_port_range,
                    "dst_port_range": epp.dst_port_range,
                    "action": epp.action,
                    "service_endpoint_group": epp.service_epg,
                    "tenant_id": epp.tenant_id}
        return self._fields(epp_dict, fields)

    def get_endpoint_policy(self, context, epp_id, fields=None):
        """
        Gets an existing endpoint policy
        """
        try:
            query = self._model_query(context, EndpointPolicy)
            epp_db = query.filter_by(id=epp_id).one()
        except exc.NoResultFound:
            raise ep_policy.NoEndpointPolicyFound(id=epp_id)

        return self._make_epp_dict(epp_db, fields)

    def get_endpoint_policies(self, context, filters=None, fields=None,
             sorts=None, limit=None, marker=None, page_reverse=None):
        """
        Gets the list of all the existing endpoint policies
        """
        return self._get_collection(context, EndpointPolicy,
                                    self._make_epp_dict, filters=filters,
                                    sorts=sorts, limit=limit,
                                    marker_obj=marker, fields=fields,
                                    page_reverse=page_reverse)

    def delete_endpoint_policy(self, context, epp_id):
        """
        Deletes an existing endpoint policy
        """
        try:
            query = context.session.query(EndpointPolicy)
            epp_db = query.filter_by(id=epp_id).first()
        except exc.NoResultFound:
            raise ep_policy.NoEndpointPolicyFound(id=epp_id)
        context.session.delete(epp_db)

    def _validate_endpoint_policy_config(self, context, epp):
        """
            Validate endpoint policy configurations
        """
        self._check_endpoint_group_for_policy(context, epp["src_grp"],
                                              constants.SOURCE_EPG)
        self._check_endpoint_group_for_policy(context, epp["dst_grp"],
                                              constants.DESTINATION_EPG)
        self._check_endpoint_group_for_policy(context,
                                              epp["service_endpoint_group"],
                                              constants.SERVICE_EPG)

    def _check_endpoint_group_for_policy(self, context, epg_id, policy_config):
        """
            Check validity of endpoint groups for endpoint policy
        """
        if policy_config == constants.SOURCE_EPG:
            self._validate_classification_endpoint(context, epg_id,
                                                   policy_config)
        elif policy_config == constants.DESTINATION_EPG:
            self._validate_classification_endpoint(context, epg_id,
                                                   policy_config)
        elif policy_config == constants.SERVICE_EPG:
            self._validate_vm_endpoint(context, epg_id, policy_config)
        else:
            raise ep_policy.InvalidEnpointPolicyConfig()

    def _validate_classification_endpoint(self, context, epg_id,
                                          policy_config):
        if epg_id is None:
            return epg_id
        else:
            try:
                query = context.session.query(EndpointGroup)
                epg_db = query.filter_by(id=epg_id).one()
                if epg_db["endpoint_type"] == constants.VM_EP:
                    raise ep_policy.InvalidEndpointGroupForPolicy(id=epg_id,
                                                  type=constants.VM_EP,
                                                  policy_config=policy_config)
                return epg_id
            except exc.NoResultFound:
                raise ep_policy.NoEndpointGroupFound(id=epg_id,
                                                 policy_config=policy_config)

    def _validate_vm_endpoint(self, context, epg_id, policy_config):
            if epg_id is None:
                raise ep_policy.InvalidConfigForServiceEndpointGroup()
            else:
                try:
                    query = context.session.query(EndpointGroup)
                    epg_db = query.filter_by(id=epg_id).one()
                    if epg_db["endpoint_type"] == constants.VM_CLASSIFICATION:
                        raise ep_policy.InvalidEndpointGroupForPolicy(
                                              id=epg_id,
                                              type=constants.VM_CLASSIFICATION,
                                              policy_config=policy_config)
                    return epg_id
                except exc.NoResultFound:
                    raise ep_policy.NoEndpointGroupFound(id=epg_id,
                                                 policy_config=policy_config)
