# Copyright 2015 PLUMgrid, Inc. All Rights Reserved.
#
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

from neutron.db import model_base
from neutron.db import models_v2
from oslo_log import log as logging
import sqlalchemy as sa
from sqlalchemy import orm

LOG = logging.getLogger(__name__)

PAP = "physical_attachment_point"
PAPS = "%ss" % PAP


class PhysicalAttachmentPoint(model_base.BASEV2, models_v2.HasId,
                              models_v2.HasTenant):
    """DB definition for PLUMgrid physical attachment point object"""

    __tablename__ = "pg_physical_attachment_points"

    name = sa.Column(sa.String(255))
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


def add_pap(context, pap):
    """
    creates a physical attachment point with initial set of interfaces
    Args:
         pap = JSON object with physical attachment point attributes
               name : display name of physical attachment point
               tenant_id : tenant uuid
               id : physical attachment point
               hash_mode : L2+L3 etc
               lacp : True/False
               interfaces : List of interfaces to be attached to physical
                            attachment point
    """
    with context.session.begin(subtransactions=True):
        pap_db = PhysicalAttachmentPoint(
                     tenant_id=pap[PAP]["tenant_id"],
                     name=pap[PAP]["name"],
                     hash_mode=pap[PAP]["hash_mode"],
                     lacp=pap[PAP]["lacp"])

        context.session.add(pap_db)

        for interface in pap[PAP]["interfaces"]:
            interface_db = Interface(hostname=interface["hostname"],
                                     interface=interface["interface"],
                                     pap=pap_db)

            context.session.add(interface_db)
    return get_pap(context, pap_db.id)


def update_pap(context, pap_id, pap):
    """
    Updates an existing physical attachment point
    Args:
         pap_id = uuid of the physical attachment point being updated
         pap = JSON with updated attributes of the physical attacchment point
               name : display name of physical attachment point
               tenant_id : tenant uuid
               id : physical attachment point
               hash_mode : L2+L3 etc
               lacp : True/False
               interfaces : List of interfaces to be attached to physical
                            attachment point
    """

    with context.session.begin(subtransactions=True):
        qry = context.session.query(Interface)
        qry.filter_by(pap_id=pap_id).delete()

        qry = context.session.query(PhysicalAttachmentPoint)
        qry.filter_by(id=pap_id).update({"name": pap[PAP]["name"],
                                         "hash_mode": pap[PAP]["hash_mode"],
                                         "lacp": pap[PAP]["lacp"]})
        pap_db = qry.filter_by(id=pap_id).first()

        for interface in pap[PAP]["interfaces"]:
            interface_db = Interface(hostname=interface["hostname"],
                                     interface=interface["interface"],
                                     pap=pap_db)

            context.session.add(interface_db)

    return get_pap(context, pap_id)


def get_pap(context, pap_id):
    """
    Gets an existing physical attachment point
    Args:
         pap_id = uuid of the physical attachment point being requested
    """

    qry = context.session.query(PhysicalAttachmentPoint)
    pap_db = qry.filter_by(id=pap_id).first()
    return _make_pap_dict(pap_db)


def get_paps(context):
    """
    Gets the list of all the existing physical attachment point
    """

    qry = context.session.query(PhysicalAttachmentPoint)
    paps = qry.all()
    return _make_pap_collection(context, paps)


def delete_pap(context, pap_id):
    """
    Deletes an existing physical attachment point
    Args:
         pap_id = uuid of the physical attachment point being deleted
    """

    qry = context.session.query(PhysicalAttachmentPoint)
    pap = qry.filter_by(id=pap_id).first()
    with context.session.begin(subtransactions=True):
        context.session.delete(pap)


def _make_pap_dict(pap):
    interfaces = []
    for interface in pap.interfaces:
        interfaces.append({"hostname": interface.hostname,
                           "interface": interface.interface})

    pap_dict = {"id": pap.id,
                "name": pap.name,
                "interfaces": interfaces,
                "hash_mode": pap.hash_mode,
                "lacp": pap.lacp,
                "tenant_id": pap.tenant_id}
    return pap_dict


def _make_pap_collection(context, paps):
    paps_list = []
    for pap in paps:
        paps_list.append(_make_pap_dict(pap))
    return paps_list


def _get_interfaces_by_pap(context, pap_id):
    ifc_qry = context.session.query(Interface)
    return ifc_qry.filter_by(pap_id=pap_id).all()
