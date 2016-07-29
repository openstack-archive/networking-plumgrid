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
from networking_plumgrid.neutron.plugins.extensions import \
    policyservicechain as ext_ps
from networking_plumgrid.neutron.plugins.db.policy.policy_service_db import \
    PolicyService
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


class PolicyServiceChain(model_base.BASEV2, models_v2.HasId,
                    models_v2.HasTenant):
    """DB definition for PLUMgrid policy service chain object"""

    __tablename__ = "pg_policy_service_chains"

    name = sa.Column(sa.String(attributes.NAME_MAX_LEN))
    description = sa.Column(sa.String(255))


class PolicyServiceChainBinding(model_base.BASEV2):
    """
    DB definition for policy services required to form a chain.
    Represents binding between policy services and policy service chains.
    """

    __tablename__ = "pg_policy_service_chain_binding"

    policy_service_chain_id = sa.Column(sa.String(36),
                                sa.ForeignKey("pg_policy_service_chains.id",
                                      ondelete='CASCADE'),
                            primary_key=True)
    policy_service_id = sa.Column(sa.String(36),
                                  sa.ForeignKey("pg_policy_services.id"),
                                  primary_key=True)

    index = sa.Column(sa.BigInteger(),
                      primary_key=True, autoincrement=True)
    # Add a relationship to the Policy Service Model in order to instruct
    # SQLAlchemy to eagerly load policy service chain bindings
    policy_services = orm.relationship(PolicyService,
                                       backref=orm.backref("ps",
                                       lazy='joined',
                                       cascade="delete"))
    psc = orm.relationship(PolicyServiceChain,
                                  backref=orm.backref("psc_binding",
                                  lazy="joined", cascade="all,delete-orphan"),
      primaryjoin="PolicyServiceChain.id==PolicyServiceChainBinding.policy_service_chain_id")


class PolicyServiceChainMixin(common_db_mixin.CommonDbMixin):
    def create_policy_service_chain(self, context, policy_service_chain):
        """
        Creates a policy service chain with intial set of policy services
        Args:
             policy_service_chain:
                   JSON object with policy service chain attributes
                   name : display name policy service chain
                   tenant_id : tenant uuid
                   id : policy service chain uuid
                   description : description of policy service chain
                   services : List of policy services part of the chain
        """
        psc = policy_service_chain["policy_service_chain"]
        # TODO(muawiakhan): FIXME Can a service be classified into multiple chains?
        self._check_ps_chain_association(context, psc["services"])
        LOG.info(_LI("Creating policy service chain %(name)s."), {'name': psc["name"]})
        with context.session.begin(subtransactions=True):
            psc_db = PolicyServiceChain(tenant_id=psc["tenant_id"],
                                  name=psc["name"],
                                  description=psc["description"])
            context.session.add(psc_db)
        with context.session.begin(subtransactions=True):
            for service in psc["services"]:
                psc_service_db = PolicyServiceChainBinding(policy_service_id=service["id"],
                                         policy_service_chain_id=psc_db.id)
                context.session.add(psc_service_db)
        return self._make_psc_dict(psc_db)

    def get_policy_service_chain(self, context, psc_id, fields=None):
        """
        Gets an existing policy service chain
        Args:
             psc_id = uuid of the policy service chain being requested
        """
        try:
            query = self._model_query(context, PolicyServiceChain)
            psc_db = query.filter_by(id=psc_id).one()
        except exc.NoResultFound:
            raise p_excep.NoPolicyServiceChainFound(id=psc_id)
        return self._make_psc_dict(psc_db, fields)

    def get_policy_service_chains(self, context, filters=None, fields=None,
             sorts=None, limit=None, marker=None, page_reverse=None):
        """
        Gets the list of all the existing policy service chains
        """
        return self._get_collection(context, PolicyServiceChain,
                                    self._make_psc_dict, filters=filters,
                                    sorts=sorts, limit=limit,
                                    marker_obj=marker, fields=fields,
                                    page_reverse=page_reverse)

    def delete_policy_service_chain(self, context, psc_id):
        """
        Deletes an existing policy service chain
        Args:
             psc_id = uuid of the policy service chain being deleted
        """
        try:
            query = context.session.query(PolicyServiceChain)
            psc_db = query.filter_by(id=psc_id).first()
            self._check_psc_in_use(context, psc_db)
        except exc.NoResultFound:
            raise p_excep.NoPolicyServiceChainFound(id=psc_id)
        with context.session.begin(subtransactions=True):
            context.session.delete(psc_db)

    def update_policy_service_chain(self, context, psc_id, policy_service_chain):
        """
        Updates an existing policy service chain
        Args:
             psc_id:
                   uuid of the policy service chain being updated
             policy_service_chain:
                   JSON with updated attributes of the policy service chain
                   name : name of policy service chain
                   tenant_id : tenant uuid
                   id : uuid of policy service chain
                   description : description of policy service chain
                   services : List of policy services part of the chain
                   add_services : List of policy services to be added to chain
                   remove_services : List of policy services to be removed from chain
        """
        psc = policy_service_chain["policy_service_chain"]
        if not psc:
            raise p_excep.UpdateParametersRequired()
        with context.session.begin(subtransactions=True):
            try:
                query = self._model_query(context, PolicyServiceChain)
                psc_db = query.filter_by(id=psc_id).one()
            except exc.NoResultFound:
                raise p_excep.NoPolicyServiceChainFound(id=psc_id)
            if 'name' in psc:
                psc_db.update({"name": psc["name"]})

            if 'description' in psc:
                psc_db.update({"description": psc["description"]})

            if 'add_services' in psc:
                self._check_ps_chain_association(context, psc["add_services"])
                for service in psc["add_services"]:
                    psc_service_db = PolicyServiceChainBinding(policy_service_id=service["id"],
                                             policy_service_chain_id=psc_db.id)

                    context.session.add(psc_service_db)
            if 'remove_services' in psc:
                for service in psc["remove_services"]:
                    query = self._model_query(context,
                                              PolicyServiceChainBinding)
                    query.filter_by(policy_service_id=service["id"],
                                    policy_service_chain_id=psc_db.id).delete()
            query = self._model_query(context, PolicyServiceChainBinding)
            psc_db.psc_binding = query.filter_by(policy_service_chain_id=psc_id).all()
        return self._make_psc_dict(psc_db)

    def _check_psc_in_use(self, context, psc_db):
        services = []
        for service in psc_db.psc_binding:
            service_id = service.policy_service_id
            query = self._model_query(context, PolicyServiceChainBinding)
            try:
                chain_in_use = query.filter_by(policy_service_id=service_id).one()
                if chain_in_use:
                    services.append(service_id)
            except exc.NoResultFound:
                pass
        if services:
            raise p_excep.PolicyServiceChainInUse(id=psc_db.id, ps=str(services))

    def _check_ps_chain_association(self, context, services):
        for service in services:
            query = self._model_query(context, PolicyServiceChainBinding)
            service_id = service["id"]
            try:
                service_in_use = query.filter_by(policy_service_id=service_id).one()
                if service_in_use:
                    raise p_excep.PolicyServiceAlreadyInUse(ps=service_id,
                              psc=service_in_use.policy_service_chain_id)
            except exc.NoResultFound:
                pass

    def _make_psc_dict(self, psc, fields=None):
        services = []
        for service in psc.psc_binding:
            services.append({"id": service.policy_service_id})
        psc_dict = {"id": psc.id,
                    "name": psc.name,
                    "services": services,
                    "description": psc.description,
                    "tenant_id": psc.tenant_id}
        return self._fields(psc_dict, fields)
