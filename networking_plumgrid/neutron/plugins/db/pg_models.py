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


class ProviderNetBinding(model_base.BASEV2):
    """Represents binding of provider network extension."""
    __tablename__ = 'pg_provider_net_bindings'

    network_id = sa.Column(sa.String(36),
                           sa.ForeignKey('networks.id', ondelete="CASCADE"),
                           primary_key=True)
    network_type = sa.Column(sa.String(32))
    physical_network = sa.Column(sa.String(64))
    vlan_id = sa.Column(sa.Integer)

    network = orm.relationship(
        models_v2.Network,
        backref=orm.backref("pgnetbinding", lazy='joined',
                            uselist=False, cascade='delete'))
