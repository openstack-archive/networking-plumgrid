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
from networking_plumgrid.neutron.plugins.db.policy.endpoint_group_db \
    import EndpointGroup
from networking_plumgrid.neutron.plugins.extensions import \
    endpoint
from neutron.api.v2 import attributes
from neutron.db import common_db_mixin
from neutron.db import model_base
from neutron.db import models_v2
from oslo_log import log as logging
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm import exc

LOG = logging.getLogger(__name__)

class Endpoint(model_base.BASEV2, models_v2.HasId,
               models_v2.HasTenant):
    """DB definition for PLUMgrid endpoint object"""

    __tablename__ = "pg_endpoints"

    name = sa.Column(sa.String(attributes.NAME_MAX_LEN))
    label = sa.Column(sa.String(attributes.LONG_DESCRIPTION_MAX_LEN))
    ip_mask = sa.Column(sa.String(attributes.LONG_DESCRIPTION_MAX_LEN))
    port_mask = sa.Column(sa.String(255))

    port_id = sa.Column(sa.String(36),
                        sa.ForeignKey("ports.id",
                                      ondelete='CASCADE'),
                        nullable=False)

    ep_ports = orm.relationship(models_v2.Port,
                             backref=orm.backref("ep_port",
                                                 lazy='joined',
                                                 cascade="delete"))


class EndpointGroupMemberBinding(model_base.BASEV2):
    """
    DB definition for ports object required by PLUMgrid
    Represents binding between endpoints
    and endpoint groups.
    """

    __tablename__ = "pg_endpoint_group_member_binding"

    endpoint_id = sa.Column(sa.String(36),
                      sa.ForeignKey("pg_endpoints.id",
                                    ondelete='CASCADE'),
                      primary_key=True)

    endpoint_group_id = sa.Column(sa.String(36),
                                sa.ForeignKey("pg_endpoint_groups.id",
                                              ondelete='CASCADE'),
                                primary_key=True)

    ep = orm.relationship(Endpoint,
              backref=orm.backref("ep_binding",
                                  lazy="joined",
                                  cascade="all,delete"),
    primaryjoin="Endpoint.id==EndpointGroupMemberBinding.endpoint_id")

    epg = orm.relationship(EndpointGroup,
              backref=orm.backref("epg_binding",
                                  lazy="joined",
                                  cascade="all,delete"),
    primaryjoin="EndpointGroup.id==EndpointGroupMemberBinding.endpoint_group_id")


class EndpointMixin(common_db_mixin.CommonDbMixin):
    def create_endpoint(self, context, endpoint):
        """
        Creates an endpoint with initial set of ports
        Args:
             endpoint:
                   JSON object with endpoint group attributes
                   name : display name endpoint
        """
        ep = endpoint["endpoint"]

        if ep["port_id"]:
            # check availability of port
            self._check_port_ep_association(context, ep["port_id"])
        
        with context.session.begin(subtransactions=True):
            ep_db = Endpoint(name=ep["name"],
                             label=ep["label"],
                             port_id=ep["port_id"],
                             ip_mask=ep["ip_mask"],
                             port_mask=ep["ip_port_mask"])
            context.session.add(ep_db)

            for epg in ep["ep_groups"]:
                ep_grp_db = EndpointGroupMemberBinding(endpoint_id=ep_db.id,
                                            endpoint_group_id=epg["id"],
                                            ep=ep_db)
                context.session.add(ep_grp_db)
        return self._make_ep_dict(ep_db)

    def get_endpoint(self, context, ep_id, fields=None):
        """
        Gets an existing endpoint
        Args:
             ep_id = uuid of the endpoint being requested
        """
        try:
            query = self._model_query(context, Endpoint)
            ep_db = query.filter_by(id=ep_id).one()
        except exc.NoResultFound:
            raise endpoint.NoEndpointFound(id=ep_id)
        return self._make_ep_dict(ep_db, fields)

    def get_endpoints(self, context, filters=None, fields=None,
             sorts=None, limit=None, marker=None, page_reverse=None):
        """
        Gets the list of all the existing endpoints
        """
        return self._get_collection(context, Endpoint,
                                    self._make_ep_dict, filters=filters,
                                    sorts=sorts, limit=limit,
                                    marker_obj=marker, fields=fields,
                                    page_reverse=page_reverse)

    def delete_endpoint(self, context, ep_id):
        """
        Deletes an existing Endpoint
        Args:
             ep_id = uuid of the endpoint being deleted
        """
        try:
            query = context.session.query(Endpoint)
            ep_db = query.filter_by(id=ep_id).first()
            self._check_ep_in_use(context, ep_db)
        except exc.NoResultFound:
            raise endpoint.NoEndpointFound(id=ep_id)
        with context.session.begin(subtransactions=True):
            context.session.delete(ep_db)

    def _check_port_ep_association(self, context, port_id):
        query = self._model_query(context, Endpoint)
        try:
            port_in_use = query.filter_by(port_id=port_id).one()
            if port_in_use:
                raise endpoint.PortInUse(port=port_id,
                          id=port_in_use.port_id)
        except exc.NoResultFound:
            pass

    def _check_ep_in_use(self, context, ep_db):
        epg_list = []
        for epg in ep_db.ep_binding:
            epg_id = epg.endpoint_group_id
            query = self._model_query(context, EndpointGroupMemberBinding)
            try:
                epg_in_use = query.filter_by(endpoint_group_id=epg_id).one()
                if epg_in_use:
                    epg_list.append(epg_id)
            except exc.NoResultFound:
                pass
        if epg_list:
            raise endpoint.EndpointInUse(id=ep_db.id, epg=str(epg_list))

    def _make_ep_dict(self, ep, fields=None):
        epg_list = []
        for epg in ep.ep_binding:
            epg_list.append({"id": epg.endpoint_group_id})
        ep_dict = {"id": ep.id,
                   "name": ep.name,
                   "ep_groups": epg_list,
                   "label": ep.label,
                   "ip_mask": ep.ip_mask,
                   "port_id": ep.port_id,
                   "port_mask": ep.port_mask}
        return self._fields(ep_dict, fields)
