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

from networking_plumgrid.neutron.plugins.extensions import \
    physical_attachment_point as ext_pap
from neutron.db import common_db_mixin
from neutron.db import model_base
from neutron.db import models_v2
from oslo_log import log as logging
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm import exc

LOG = logging.getLogger(__name__)


class PhysicalAttachmentPoint(model_base.BASEV2, models_v2.HasId,
                              models_v2.HasTenant):
    """DB definition for PLUMgrid physical attachment point object"""

    __tablename__ = "pg_physical_attachment_points"

    name = sa.Column(sa.String(255))
    transit_domain_id = sa.Column(sa.String(255))
    hash_mode = sa.Column(sa.String(255))
    lacp = sa.Column(sa.Boolean)


class Interface(model_base.BASEV2, models_v2.HasId):
    """
    DB definition for interfaces object required by PLUMgrid
    Physical Attachment Points.
    """

    __tablename__ = "pg_physical_attachment_point_interfaces"

    hostname = sa.Column(sa.String(255))
    interface = sa.Column(sa.String(255))
    pap_id = sa.Column(sa.String(36),
                       sa.ForeignKey("pg_physical_attachment_points.id",
                                     ondelete="CASCADE"),
                       nullable=False)
    pap = orm.relationship(PhysicalAttachmentPoint,
              backref=orm.backref("interfaces",
                                  lazy="joined",
                                  cascade="all,delete"),
              primaryjoin="PhysicalAttachmentPoint.id==Interface.pap_id")


class PhysicalAttachmentPointDb(common_db_mixin.CommonDbMixin):
    def create_physical_attachment_point(self, context,
            physical_attachment_point):
        """
        creates a physical attachment point with initial set of interfaces
        Args:
             pap = JSON object with physical attachment point attributes
                   name : display name of physical attachment point
                   tenant_id : tenant uuid
                   id : physical attachment point
                   hash_mode : L2, L3 etc
                   lacp : True/False
                   interfaces : List of interfaces to be attached to physical
                                attachment point
        """

        pap = physical_attachment_point["physical_attachment_point"]
        with context.session.begin(subtransactions=True):
            pap_db = PhysicalAttachmentPoint(
                         tenant_id=pap["tenant_id"],
                         name=pap["name"],
                         hash_mode=pap["hash_mode"],
                         lacp=pap["lacp"],
                         transit_domain_id=pap["transit_domain_id"])

            context.session.add(pap_db)
            for interface in pap["interfaces"]:
                interface_db = Interface(hostname=interface["hostname"],
                                         interface=interface["interface"],
                                         pap=pap_db)

                context.session.add(interface_db)
        return self._make_pap_dict(pap_db)

    def update_physical_attachment_point(self, context, pap_id,
            physical_attachment_point):
        """
        Updates an existing physical attachment point
        Args:
             pap_id = uuid of the physical attachment point being updated
             pap = JSON with updated attributes of the physical
                   attacchment point
                   name : display name of physical attachment point
                   tenant_id : tenant uuid
                   id : physical attachment point
                   hash_mode : L2+L3 etc
                   lacp : True/False
                   interfaces : List of interfaces to be attached to physical
                                attachment point
        """

        pap = physical_attachment_point["physical_attachment_point"]
        if not pap:
            raise ext_pap.UpdateParametersRequired()

        with context.session.begin(subtransactions=True):
            try:
                query = self._model_query(context, PhysicalAttachmentPoint)
                pap_db = query.filter_by(id=pap_id).one()
            except exc.NoResultFound:
                raise ext_pap.NoPhysicalAttachmentPointFound(id=pap_id)

            if 'name' in pap:
                pap_db.update({"name": pap["name"]})

            if 'hash_mode' in pap:
                pap_db.update({"hash_mode": pap["hash_mode"]})

            if 'lacp' in pap:
                pap_db.update({"lacp": pap["lacp"]})

            if 'interfaces' in pap and pap['interfaces']:
                try:
                    query = self._model_query(context, Interface)
                    query.filter_by(pap_id=pap_id).delete()
                except exc.NoResultFound:
                    pass
                for interface in pap["interfaces"]:
                    interface_db = Interface(hostname=interface["hostname"],
                                             interface=interface["interface"],
                                             pap=pap_db)

                    context.session.add(interface_db)
                pap_db.interfaces = query.filter_by(pap_id=pap_id).all()

        return self._make_pap_dict(pap_db)

    def get_physical_attachment_point(self, context, pap_id, fields=None):
        """
        Gets an existing physical attachment point
        Args:
             pap_id = uuid of the physical attachment point being requested
        """

        try:
            query = self._model_query(context, PhysicalAttachmentPoint)
            pap_db = query.filter_by(id=pap_id).one()
        except exc.NoResultFound:
            raise ext_pap.NoPhysicalAttachmentPointFound(id=pap_id)
        return self._make_pap_dict(pap_db, fields)

    def get_physical_attachment_points(self, context, filters=None,
            fields=None, sorts=None, limit=None, marker=None,
            page_reverse=None):
        """
        Gets the list of all the existing physical attachment points
        """

        return self._get_collection(context, PhysicalAttachmentPoint,
                                    self._make_pap_dict, filters=filters,
                                    sorts=sorts, limit=limit,
                                    marker_obj=marker, fields=fields,
                                    page_reverse=page_reverse)

    def delete_physical_attachment_point(self, context, pap_id):
        """
        Deletes an existing physical attachment point
        Args:
             pap_id = uuid of the physical attachment point being deleted
        """

        try:
            query = context.session.query(PhysicalAttachmentPoint)
            pap_db = query.filter_by(id=pap_id).first()
        except exc.NoResultFound:
            raise ext_pap.NoPhysicalAttachmentPointFound(id=pap_id)

        with context.session.begin(subtransactions=True):
            context.session.delete(pap_db)

    def _make_pap_dict(self, pap, fields=None):
        interfaces = []
        for interface in pap.interfaces:
            interfaces.append({"hostname": interface.hostname,
                               "interface": interface.interface})

        pap_dict = {"id": pap.id,
                    "name": pap.name,
                    "interfaces": interfaces,
                    "hash_mode": pap.hash_mode,
                    "lacp": pap.lacp,
                    "tenant_id": pap.tenant_id,
                    "transit_domain_id": pap.transit_domain_id}
        return self._fields(pap_dict, fields)
