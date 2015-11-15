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

import sqlalchemy as sa
from sqlalchemy import orm

from neutron.db import model_base
from neutron.db import models_v2


class PhysicalAttachmentPoint(model_base.BASEV2, models_v2.HasId,
                              models_v2.HasTenant):
    __tablename__ = "physical_attachment_points"

    name = sa.Column(sa.String(255))
    hash_mode = sa.Column(sa.String(255))
    lacp = sa.Column(sa.Boolean)


class Interface(model_base.BASEV2, models_v2.HasId):
    hostname = sa.Column(sa.String(255))
    interface = sa.Column(sa.String(255))
    pap_id = sa.Column(sa.String(36),
             sa.ForeignKey("physical_attachment_points.id",
                           ondelete="CASCADE"),
             nullable=False)
    pap = orm.relationship(PhysicalAttachmentPoint,
                    backref=orm.backref("interfaces", lazy="joined",
                    cascade="all,delete"),
                    primaryjoin="PhysicalAttachmentPoint.id==Interface.pap_id")
