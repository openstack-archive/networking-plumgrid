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
from networking_plumgrid.neutron.plugins.common import \
    policy_exceptions as p_excep
from neutron.api.v2 import attributes
from neutron.db import common_db_mixin
from neutron.db import model_base
from neutron.db import models_v2
from oslo_log import log as logging
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm import exc

LOG = logging.getLogger(__name__)


class PolicyService(model_base.BASEV2, models_v2.HasId,
                    models_v2.HasTenant):
    """DB definition for PLUMgrid policy service object"""

    __tablename__ = "pg_policy_services"

    name = sa.Column(sa.String(attributes.NAME_MAX_LEN))
    description = sa.Column(sa.String(255))


class PolicyServicePortBinding(model_base.BASEV2):
    """
    DB definition for ports required by PLUMgrid policy service.
    Represents binding between neutron ports
    and policy services.
    """
    __tablename__ = "pg_policy_service_port_binding"

    port_id = sa.Column(sa.String(36),
                        sa.ForeignKey("ports.id",
                                      ondelete='CASCADE'),
                        primary_key=True)
    policy_service_id = sa.Column(sa.String(36),
                                  sa.ForeignKey("pg_policy_services.id"),
                                  primary_key=True)

    direction = sa.Column(sa.Enum(constants.DIRECTION_INGRESS,
                                  constants.DIRECTION_EGRESS,
                                  constants.BIDIRECTIONAL), primary_key=True)

    # Add a relationship to the Port model in order to instruct SQLAlchemy to
    # eagerly load policy service bindings
    ps_ports = orm.relationship(models_v2.Port,
                             backref=orm.backref("ps_port",
                                                 lazy='joined',
                                                 cascade="delete"))
    policy_service = orm.relationship(PolicyService,
                  backref=orm.backref("psp_binding",
                                  lazy="joined", cascade="all,delete-orphan"),
    primaryjoin="PolicyService.id==PolicyServicePortBinding.policy_service_id")


class PolicyServiceMixin(common_db_mixin.CommonDbMixin):
    def create_policy_service(self, context, policy_service):
        """
        creates a policy with initial set of ports
        Args:
             policy_service:
                   JSON object with policy service attributes
                   name : display name policy service
                   tenant_id : tenant uuid
                   id : policy service uuid
                   description : description of policy service
                   ingress_ports : List of ingress ports to be classified into
                                   policy service
                   egress_ports: List of egress ports to be classified into
                                 policy service
                   bidirectional_ports: List of bidirectional ports to be
                                        classified into policy service
        """
        ps = policy_service["policy_service"]
        #  check availability of ports
        if "ingress_ports" in ps and ps["ingress_ports"]:
            self._check_port_ps_association(context, ps["ingress_ports"])
        if "egress_ports" in ps and ps["egress_ports"]:
            self._check_port_ps_association(context, ps["egress_ports"])
        if "bidirectional_ports" in ps and ps["bidirectional_ports"]:
            self._check_port_ps_association(context,
                                            ps["bidirectional_ports"])
        LOG.info(_LI("Creating policy service %(name)s."),
                 {'name': ps["name"]})
        with context.session.begin(subtransactions=True):
            ps_db = PolicyService(tenant_id=ps["tenant_id"],
                                  name=ps["name"],
                                  description=ps["description"])
            context.session.add(ps_db)
        with context.session.begin(subtransactions=True):
            for ingress_port in ps["ingress_ports"]:
                ps_ingress_port_db = PolicyServicePortBinding(
                                         port_id=ingress_port["id"],
                                         policy_service_id=ps_db.id,
                                         direction=constants.DIRECTION_INGRESS)
                context.session.add(ps_ingress_port_db)
            for egress_port in ps["egress_ports"]:
                ps_egress_port_db = PolicyServicePortBinding(
                                         port_id=egress_port["id"],
                                         policy_service_id=ps_db.id,
                                         direction=constants.DIRECTION_EGRESS)
                context.session.add(ps_egress_port_db)
            for bidirect_port in ps["bidirectional_ports"]:
                ps_bidirect_port_db = PolicyServicePortBinding(
                                         port_id=bidirect_port["id"],
                                         policy_service_id=ps_db.id,
                                         direction=constants.BIDIRECTIONAL)
                context.session.add(ps_bidirect_port_db)
        return self._make_ps_dict(ps_db)

    def get_policy_service(self, context, ps_id, fields=None):
        """
        Gets an existing policy service
        Args:
             ps_id = uuid of the policy service being requested
        """
        try:
            query = self._model_query(context, PolicyService)
            ps_db = query.filter_by(id=ps_id).one()
        except exc.NoResultFound:
            raise p_excep.NoPolicyServiceFound(id=ps_id)
        return self._make_ps_dict(ps_db, fields)

    def get_policy_services(self, context, filters=None, fields=None,
             sorts=None, limit=None, marker=None, page_reverse=None):
        """
        Gets the list of all the existing policy services
        """
        return self._get_collection(context, PolicyService,
                                    self._make_ps_dict, filters=filters,
                                    sorts=sorts, limit=limit,
                                    marker_obj=marker, fields=fields,
                                    page_reverse=page_reverse)

    def delete_policy_service(self, context, ps_id):
        """
        Deletes an existing policy service
        Args:
             ps_id = uuid of the policy service being deleted
        """
        try:
            query = context.session.query(PolicyService)
            ps_db = query.filter_by(id=ps_id).first()
            self._check_ps_in_use(context, ps_db)
        except exc.NoResultFound:
            raise p_excep.NoPolicyServiceFound(id=ps_id)
        with context.session.begin(subtransactions=True):
            context.session.delete(ps_db)

    def update_policy_service(self, context, ps_id, policy_service):
        """
        Updates an existing policy
        Args:
             ps_id:
                   uuid of the policy service being updated
             policy_service:
                   JSON with updated attributes of the policy service
                   name : name of policy service
                   tenant_id : tenant uuid
                   id : uuid of policy service
                   description : description of policy service
                   ingress_ports : List of ingress ports of policy service
                   egress_ports: List of egress ports of policy service
                   add_ingress_ports: List of ingress ports to be added to
                                      policy service
                   remove_ingress_ports: List of ingress ports to be removed
                                         from policy service
                   add_egress_ports: List of egress ports to be added to
                                     policy service
                   remove_egress_ports: List of egress ports to be removed
                                        from policy service
        """
        ps = policy_service["policy_service"]
        if not ps:
            raise p_excep.UpdateParametersRequired()
        with context.session.begin(subtransactions=True):
            try:
                query = self._model_query(context, PolicyService)
                ps_db = query.filter_by(id=ps_id).one()
            except exc.NoResultFound:
                raise p_excep.NoPolicyServiceFound(id=ps_id)
            if 'name' in ps:
                ps_db.update({"name": ps["name"]})

            if 'description' in ps:
                ps_db.update({"description": ps["description"]})

            if 'add_ingress_ports' in ps:
                self._check_port_ps_association(context,
                                                ps["add_ingress_ports"])
                for ingress_port in ps["add_ingress_ports"]:
                    ps_ingress_port_db = PolicyServicePortBinding(
                                         port_id=ingress_port["id"],
                                         policy_service_id=ps_db.id,
                                         direction=constants.DIRECTION_INGRESS)

                    context.session.add(ps_ingress_port_db)
            if 'add_egress_ports' in ps:
                self._check_port_ps_association(context,
                                                ps["add_egress_ports"])
                for egress_port in ps["add_egress_ports"]:
                    ps_egress_port_db = PolicyServicePortBinding(
                                         port_id=egress_port["id"],
                                         policy_service_id=ps_db.id,
                                         direction=constants.DIRECTION_EGRESS)

                    context.session.add(ps_egress_port_db)
            if 'remove_ingress_ports' in ps:
                for ingress_port in ps["remove_ingress_ports"]:
                    query = self._model_query(context,
                                              PolicyServicePortBinding)
                    query.filter_by(port_id=ingress_port["id"],
                                    policy_service_id=ps_db.id).delete()
            if 'remove_egress_ports' in ps:
                for egress_port in ps["remove_egress_ports"]:
                    query = self._model_query(context,
                                              PolicyServicePortBinding)
                    query.filter_by(port_id=egress_port["id"],
                                    policy_service_id=ps_db.id).delete()
            if 'add_bidirectional_ports' in ps:
                self._check_port_ps_association(context,
                                                ps["add_bidirectional_ports"])
                for bidirect_port in ps["add_bidirectional_ports"]:
                    ps_bidirect_port_db = PolicyServicePortBinding(
                                             port_id=bidirect_port["id"],
                                             policy_service_id=ps_db.id,
                                             direction=constants.BIDIRECTIONAL)

                    context.session.add(ps_bidirect_port_db)
            if 'remove_bidirectional_ports' in ps:
                for bidirect_port in ps["remove_bidirectional_ports"]:
                    query = self._model_query(context,
                                              PolicyServicePortBinding)
                    query.filter_by(port_id=bidirect_port["id"],
                                    policy_service_id=ps_db.id).delete()
            query = self._model_query(context, PolicyServicePortBinding)
            ps_db.psp_binding = query.filter_by(policy_service_id=ps_id).all()
        return self._make_ps_dict(ps_db)

    def _check_port_ps_association(self, context, ports):
        for port in ports:
            query = self._model_query(context, PolicyServicePortBinding)
            port_id = port["id"]
            try:
                port_in_use = query.filter_by(port_id=port_id).one()
                if port_in_use:
                    raise p_excep.PortAlreadyInUsePolicyService(port=port_id,
                              ps=port_in_use.policy_service_id)
            except exc.NoResultFound:
                pass

    def _make_ps_dict(self, ps, fields=None):
        ingress_ports = []
        egress_ports = []
        bidirect_ports = []
        for port in ps.psp_binding:
            if port.direction == constants.DIRECTION_INGRESS:
                ingress_ports.append({"id": port.port_id})
            elif port.direction == constants.DIRECTION_EGRESS:
                egress_ports.append({"id": port.port_id})
            elif port.direction == constants.BIDIRECTIONAL:
                bidirect_ports.append({"id": port.port_id})
            else:
                raise p_excep.InvalidPolicyServiceConfiguration()
        ps_dict = {"id": ps.id,
                   "name": ps.name,
                   "ingress_ports": ingress_ports,
                   "egress_ports": egress_ports,
                   "bidirectional_ports": bidirect_ports,
                   "description": ps.description,
                   "tenant_id": ps.tenant_id}
        return self._fields(ps_dict, fields)

    def _check_ps_in_use(self, context, ps_db):
        ports = []
        for port in ps_db.psp_binding:
            port_id = port.port_id
            query = self._model_query(context, PolicyServicePortBinding)
            try:
                port_in_use = query.filter_by(port_id=port_id).one()
                if port_in_use:
                    ports.append(port_id)
            except exc.NoResultFound:
                pass
        if ports:
            raise p_excep.PolicyServiceInUse(id=ps_db.id, port=str(ports))
