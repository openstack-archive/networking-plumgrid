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
    ip_mask = sa.Column(sa.String(255))
    ip_port = sa.Column(sa.String(255))

    port_id = sa.Column(sa.String(36),
                        sa.ForeignKey("ports.id",
                                      ondelete='CASCADE'),
                        nullable=True)

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
            ep_db = Endpoint(tenant_id=ep["tenant_id"],
                             name=ep["name"],
                             port_id=ep["port_id"],
                             ip_mask=ep["ip_mask"],
                             ip_port=ep["ip_port"])
            context.session.add(ep_db)

            for epg in ep["ep_groups"]:
                self._check_ep_exists(context, epg["id"])
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
            ep_db = query.filter_by(id=ep_id).one()
        except exc.NoResultFound:
            raise endpoint.NoEndpointFound(id=ep_id)
        with context.session.begin(subtransactions=True):
            context.session.delete(ep_db)

    def update_endpoint(self, context, ep_id, endpoint):
        """
        Updates an existing endpoint
        Args:
             ep_id:
                   uuid of the endpoint being updated
             endpoint_group:
                   JSON with updated attributes of the endpoint
                   name : name of endpoint
                   tenant_id : tenant uuid
                   id : uuid of endpoint
        """
        ep = endpoint["endpoint"]
        if not ep:
            raise endpoint.UpdateParametersRequired()
        with context.session.begin(subtransactions=True):
            try:
                query = self._model_query(context, Endpoint)
                ep_db = query.filter_by(id=ep_id).one()
            except exc.NoResultFound:
                raise endpoint.NoEndpointFound(id=ep_id)

            if 'name' in ep:
                ep_db.update({"name": ep["name"]})
            if 'add_endpoint_groups' in ep:
                self._check_existing_epg_association(context,
                                                     ep["add_endpoint_groups"])
                for epg in ep["add_endpoint_groups"]:
                    ep_grp_db = EndpointGroupMemberBinding(
                                            endpoint_id=ep_db.id,
                                            endpoint_group_id=epg["id"],
                                            ep=ep_db)
                    context.session.add(ep_grp_db)
            if 'remove_endpoint_groups' in ep:
                self._check_epg(context, ep_id, ep["remove_endpoint_groups"])
                for epg in ep["remove_endpoint_groups"]:
                    query = self._model_query(context,
                                              EndpointGroupMemberBinding)
                    query.filter_by(endpoint_id=ep_db.id,
                          endpoint_group_id=epg["id"]).delete()
        return self._make_ep_dict(ep_db)

    def _check_epg(self, context, ep_id, endpoint_groups):
        for epg in endpoint_groups:
            query = self._model_query(context, EndpointGroupMemberBinding)
            epg_id = epg["id"]
            try:
                ep = query.filter_by(endpoint_id=ep_id,
                                     endpoint_group_id=epg_id).one()
                if not ep:
                    raise endpoint.NoEndpointGroupFound(id=epg_id)
            except exc.NoResultFound:
                pass

    def _check_port_ep_association(self, context, port_id):
        query = self._model_query(context, Endpoint)
        try:
            port_in_use = query.filter_by(port_id=port_id).one()
            if port_in_use:
                raise endpoint.PortInUse(port=port_id,
                          id=port_in_use.port_id)
        except exc.NoResultFound:
            pass

    def _check_ep_exists(self, context, epg_id):
        query = context.session.query(EndpointGroup)
        try:
            query.filter_by(id=epg_id).one()
        except exc.NoResultFound:
            raise endpoint.NoEndpointGroupFound(id=epg_id)

    def _make_ep_dict(self, ep, fields=None):
        epg_list = []
        for epg in ep.ep_binding:
            epg_list.append({"id": epg.endpoint_group_id})
        ep_dict = {"id": ep.id,
                   "name": ep.name,
                   "ep_groups": epg_list,
                   "ip_mask": ep.ip_mask,
                   "port_id": ep.port_id,
                   "ip_port": ep.ip_port,
                   "tenant_id": ep.tenant_id}
        return self._fields(ep_dict, fields)

    def _check_existing_epg_association(self, context, endpoint_groups):
        for epg in endpoint_groups:
            query = self._model_query(context, EndpointGroupMemberBinding)
            epg_id = epg["id"]
            try:
                epg_in_use = query.filter_by(endpoint_group_id=epg_id).one()
                if epg_in_use:
                    raise p_excep.EndpointGroupAlreadyInUse(epg=epg_id,
                              ep=epg_in_use.endpoint_id)
            except exc.NoResultFound:
                pass
