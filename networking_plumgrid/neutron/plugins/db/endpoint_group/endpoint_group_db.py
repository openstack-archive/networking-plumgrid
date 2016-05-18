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

from networking_plumgrid._i18n import _LI
from networking_plumgrid.neutron.plugins.common import \
    constants
from networking_plumgrid.neutron.plugins.extensions import \
    endpointgroup as ep_group
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
    endpoint_type = sa.Column(sa.Enum('vm_class', 'vm_ep',
                                  name='pg_endpoint_groups_endpoint_type'))


class EndpointGroupPortBinding(model_base.BASEV2):
    """
    DB definition for interfaces object required by PLUMgrid
    Physical Attachment Points. Represents binding between neutron ports
    and endpoint groups.
    """

    __tablename__ = "pg_endpoint_group_port_binding"

    port_id = sa.Column(sa.String(36),
                        sa.ForeignKey("ports.id",
                                      ondelete='CASCADE'),
                        primary_key=True)
    endpoint_group_id = sa.Column(sa.String(36),
                                  sa.ForeignKey("pg_endpoint_groups.id"),
                                  primary_key=True)

    # Add a relationship to the Port model in order to instruct SQLAlchemy to
    # eagerly load endpoint group bindings
    epg_ports = orm.relationship(models_v2.Port,
                             backref=orm.backref("epg_port",
                                                 lazy='joined',
                                                 cascade="delete"))
    epg = orm.relationship(EndpointGroup,
              backref=orm.backref("epg_binding",
                                  lazy="joined", cascade="all,delete-orphan"),
  primaryjoin="EndpointGroup.id==EndpointGroupPortBinding.endpoint_group_id")


class EndpointGroupMixin(common_db_mixin.CommonDbMixin):
    def create_endpoint_group(self, context, endpoint_group):
        """
        creates a endpoint group with initial set of ports
        Args:
             endpoint_group:
                   JSON object with endpoint group attributes
                   name : display name endpoint group
                   tenant_id : tenant uuid
                   id : endpoint group uuid
                   description : description of endpoint group
                   ports : List of ports to be classified into endpoint group
        """
        epg = endpoint_group["endpoint_group"]
        #  check availability of ports
        self._check_port_epg_association(context, epg["ports"])
        if epg["endpoint_type"] == constants.VM_EP:
            if self._check_service_epg_limit(context, epg["tenant_id"]):
                LOG.info(_LI("Creating service endpoint group"))
        with context.session.begin(subtransactions=True):
            epg_db = EndpointGroup(tenant_id=epg["tenant_id"],
                                   name=epg["name"],
                                   description=epg["description"],
                                   endpoint_type=epg["endpoint_type"])
            context.session.add(epg_db)
        with context.session.begin(subtransactions=True):
            for port in epg["ports"]:
                epg_port_db = EndpointGroupPortBinding(port_id=port["id"],
                                         endpoint_group_id=epg_db.id)
                context.session.add(epg_port_db)
        return self._make_epg_dict(epg_db)

    def get_endpoint_group(self, context, epg_id, fields=None):
        """
        Gets an existing endpoint group
        Args:
             epg_id = uuid of the endpoint group being requested
        """
        try:
            query = self._model_query(context, EndpointGroup)
            epg_db = query.filter_by(id=epg_id).one()
        except exc.NoResultFound:
            raise ep_group.NoEndpointGroupFound(id=epg_id)
        return self._make_epg_dict(epg_db, fields)

    def get_endpoint_groups(self, context, filters=None,
             fields=None, sorts=None, limit=None, marker=None,
             page_reverse=None):
        """
        Gets the list of all the existing endpoint groups
        """
        return self._get_collection(context, EndpointGroup,
                                    self._make_epg_dict, filters=filters,
                                    sorts=sorts, limit=limit,
                                    marker_obj=marker, fields=fields,
                                    page_reverse=page_reverse)

    def delete_endpoint_group(self, context, epg_id):
        """
        Deletes an existing Endpoint group
        Args:
             epg_id = uuid of the endpoint group being deleted
        """
        try:
            query = context.session.query(EndpointGroup)
            epg_db = query.filter_by(id=epg_id).first()
            self._check_epg_in_use(context, epg_db)
        except exc.NoResultFound:
            raise ep_group.NoEndpointGroupFound(id=epg_id)
        with context.session.begin(subtransactions=True):
            context.session.delete(epg_db)

    def _check_epg_in_use(self, context, epg_db):
        ports = []
        for port in epg_db.epg_binding:
            port_id = port.port_id
            query = self._model_query(context, EndpointGroupPortBinding)
            try:
                port_in_use = query.filter_by(port_id=port_id).one()
                if port_in_use:
                    ports.append(port_id)
            except exc.NoResultFound:
                pass
        if ports:
            raise ep_group.EndpointGroupInUse(id=epg_db.id, port=str(ports))

    def _check_port_epg_association(self, context, ports):
        for port in ports:
            query = self._model_query(context, EndpointGroupPortBinding)
            port_id = port["id"]
            try:
                port_in_use = query.filter_by(port_id=port_id).one()
                if port_in_use:
                    raise ep_group.PortInUse(port=port_id,
                              id=port_in_use.endpoint_group_id)
            except exc.NoResultFound:
                pass

    def _make_epg_dict(self, epg, fields=None):
        ports = []
        for port in epg.epg_binding:
            ports.append({"id": port.port_id})
        epg_dict = {"id": epg.id,
                    "name": epg.name,
                    "ports": ports,
                    "description": epg.description,
                    "endpoint_type": epg.endpoint_type,
                    "tenant_id": epg.tenant_id}
        return self._fields(epg_dict, fields)

    def _get_port_endpoint_group_bindings(self, context,
                                          filters=None, fields=None):
        return self._get_collection(context,
                                    EndpointGroupPortBinding,
                                    self._make_security_group_binding_dict,
                                    filters=filters, fields=fields)

    def _make_endpoint_group_binding_dict(self, endpoint_group, fields=None):
        res = {'port_id': endpoint_group['port_id'],
               'security_group_id': endpoint_group['epg_id']}
        return self._fields(res, fields)

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
                   description : description of endpoint group
                   ports : List of ports to be attached to endpoint group
        """
        epg = endpoint_group["endpoint_group"]
        if not epg:
            raise ep_group.UpdateParametersRequired()
        with context.session.begin(subtransactions=True):
            try:
                query = self._model_query(context, EndpointGroup)
                epg_db = query.filter_by(id=epg_id).one()
            except exc.NoResultFound:
                raise ep_group.NoEndpointGroupFound(id=epg_id)
            if 'name' in epg:
                epg_db.update({"name": epg["name"]})

            if 'description' in epg:
                epg_db.update({"description": epg["description"]})

            if 'add_ports' in epg:
                self._check_port_epg_association(context, epg["add_ports"])
                for port in epg["add_ports"]:
                    epg_port_db = EndpointGroupPortBinding(port_id=port["id"],
                                             endpoint_group_id=epg_db.id)

                    context.session.add(epg_port_db)
            if 'remove_ports' in epg:
                for port in epg["remove_ports"]:
                    query = self._model_query(context,
                                              EndpointGroupPortBinding)
                    query.filter_by(port_id=port["id"],
                                    endpoint_group_id=epg_db.id).delete()
            query = self._model_query(context, EndpointGroupPortBinding)
            epg_db.epg_binding = query.filter_by(endpoint_group_id=
                                                 epg_id).all()
        return self._make_epg_dict(epg_db)

    def _check_service_epg_limit(self, context, tenant_id):
        try:
            query = self._model_query(context, EndpointGroup)
            pap_db = query.filter_by(endpoint_type=constants.VM_EP,
                                     tenant_id=tenant_id).one()
            if pap_db:
                raise ep_group.ServiceEndpointGroupLimit
        except exc.NoResultFound:
            return True
