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

from networking_plumgrid.neutron.plugins.db.physical_attachment_point import \
    physical_attachment_point_db as pap_models
from networking_plumgrid.neutron.plugins.extensions import \
    transitdomain as ext_tvd
from neutron.db import common_db_mixin
from neutron.db import model_base
from neutron.db import models_v2
from oslo_log import log as logging
import sqlalchemy as sa
from sqlalchemy.orm import exc

LOG = logging.getLogger(__name__)


class TransitDomain(model_base.BASEV2, models_v2.HasId,
                    models_v2.HasTenant):
    """DB definition for Transit Domain"""

    __tablename__ = "pg_transit_domains"

    name = sa.Column(sa.String(255))
    implicit = sa.Column(sa.Boolean)


class TransitDomainDBMixin(common_db_mixin.CommonDbMixin):
    def create_transit_domain(self, context, transit_domain):
        """
        creates a transit domain
        """

        tvd = transit_domain["transit_domain"]
        if tvd.get("implicit") is None:
            tvd["implicit"] = False
        with context.session.begin(subtransactions=True):
            tvd_db = TransitDomain(
                         tenant_id=tvd["tenant_id"],
                         name=tvd["name"],
                         implicit=tvd["implicit"])
            context.session.add(tvd_db)
        return self._make_tvd_dict(tvd_db)

    def update_transit_domain(self, context, tvd_id, transit_domain):
        """Updates an existing transit domain"""

        tvd = transit_domain["transit_domain"]
        if not tvd:
            raise ext_tvd.UpdateParametersRequired()

        with context.session.begin(subtransactions=True):
            try:
                query = self._model_query(context, TransitDomain)
                tvd_db = query.filter_by(id=tvd_id).one()
            except exc.NoResultFound:
                raise ext_tvd.NoTransitDomainFound(id=tvd_id)
            if 'name' in tvd:
                tvd_db.update({"name": tvd["name"]})
            context.session.add(tvd_db)
        return self._make_tvd_dict(tvd_db)

    def get_transit_domain(self, context, tvd_id, fields=None):
        """
        Gets an existing transit domain
        """

        try:
            query = self._model_query(context, TransitDomain)
            tvd_db = query.filter_by(id=tvd_id).one()
        except exc.NoResultFound:
                raise ext_tvd.NoTransitDomainFound(id=tvd_id)

        return self._make_tvd_dict(tvd_db, fields)

    def get_transit_domains(self, context, filters=None, fields=None,
             sorts=None, limit=None, marker=None, page_reverse=None):
        """
        Gets the list of all the existing transit domains
        """

        return self._get_collection(context, TransitDomain,
                                    self._make_tvd_dict, filters=filters,
                                    sorts=sorts, limit=limit,
                                    marker_obj=marker, fields=fields,
                                    page_reverse=page_reverse)

    def delete_transit_domain(self, context, tvd_id):
        """
        Deletes an existing transit domain
        """

        try:
            if self._transit_domain_check_phy_att_points(context, tvd_id):
                raise ext_tvd.TransitDomainInUse(id=tvd_id)
            query = context.session.query(TransitDomain)
            tvd_db = query.filter_by(id=tvd_id).first()
        except exc.NoResultFound:
                raise ext_tvd.NoTransitDomainFound(id=tvd_id)
        context.session.delete(tvd_db)

    def _make_tvd_dict(self, tvd, fields=None):
        tvd_dict = {"id": tvd.id,
                    "name": tvd.name,
                    "implicit": tvd.implicit,
                    "tenant_id": tvd.tenant_id}
        return self._fields(tvd_dict, fields)

    def _transit_domain_check_phy_att_points(self, context, transit_domain_id):
        return (context.session.query(pap_models.PhysicalAttachmentPoint).
                filter_by(transit_domain_id=transit_domain_id).first())
