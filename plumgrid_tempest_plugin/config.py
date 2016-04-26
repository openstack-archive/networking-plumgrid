# Copyright 2015 PLUMgrid, Inc. All Rights Reserved.
# All Rights Reserved.
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
from oslo_config import cfg
from tempest import config

plumgrid_group = cfg.OptGroup(name='plumgrid',
                         title='PLUMgrid tempest configuration options')

PLUMgridGroup = [
    cfg.StrOpt('interfaces',
               default='',
               help="List of gateway interfaces"),
]

_opts = [(plumgrid_group, PLUMgridGroup)]


def register_opts(conf):
    for g, o in _opts:
        config.register_opt_group(conf, g, o)


def list_opts():
    """Return a list of oslo.config options available.

    The purpose of this is to allow tools like the Oslo sample config file
    generator to discover the options exposed to users.
    """
    return [(g.name, o) for g, o in _opts]
