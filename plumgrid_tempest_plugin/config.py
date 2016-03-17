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

from __future__ import print_function

import logging as std_logging
import os

from oslo_config import cfg


def register_opt_group(conf, opt_group, options):
    conf.register_group(opt_group)
    for opt in options:
        conf.register_opt(opt, group=opt_group.name)

# Added Plumgrid values Group
plumgrid_group = cfg.OptGroup(name='plumgrid',
                              title="Option required for PLUMgrid Tempest\
                              Tests")

# Added options for Plumgrid Group
PlumgridGroup = [
    cfg.StrOpt('hostname',
               default='home',
               help="Name of Host Machine on which plumgrid tempest tests\
                for PAP will run."),
    cfg.ListOpt('interfaces',
                default=['eth0'],
                help="List of Network Interfaces of Machine on which plumgrid\
                tempest tests for PAP will run."),
]

# Register Plumgrid options with PG group
_opts = [
    (plumgrid_group, PlumgridGroup)
]


def register_opts():
    for g, o in _opts:
        register_opt_group(cfg.CONF, g, o)


def list_opts():
    """Return a list of oslo.config options available.

    The purpose of this is to allow tools like the Oslo sample config file
    generator to discover the options exposed to users.
    """
    return [(g.name, o) for g, o in _opts]


# this should never be called outside of this class
class TempestConfigPrivate(object):
    """Provides OpenStack configuration information."""

    DEFAULT_CONFIG_DIR = os.path.join(
        os.path.abspath(os.path.dirname(os.path.dirname(__file__))),
        "etc")

    DEFAULT_CONFIG_FILE = "tempest.conf"

    def __getattr__(self, attr):
        # Handles config options from the default group
        return getattr(cfg.CONF, attr)

    def __init__(self, parse_conf=True, config_path=None):
        """Initialize a configuration from a conf directory and conf file."""
        super(TempestConfigPrivate, self).__init__()
        config_files = []
        failsafe_path = "/etc/tempest/" + self.DEFAULT_CONFIG_FILE

        if config_path:
            path = config_path
        else:
            # Environment variables override defaults...
            conf_dir = os.environ.get('TEMPEST_CONFIG_DIR',
                                      self.DEFAULT_CONFIG_DIR)
            conf_file = os.environ.get('TEMPEST_CONFIG',
                                       self.DEFAULT_CONFIG_FILE)

            path = os.path.join(conf_dir, conf_file)

        if not os.path.isfile(path):
            path = failsafe_path

        # only parse the config file if we expect one to exist. This is needed
        # to remove an issue with the config file up to date checker.
        if parse_conf:
            config_files.append(path)
        if os.path.isfile(path):
            cfg.CONF([], project='tempest', default_config_files=config_files)
        else:
            cfg.CONF([], project='tempest')
        register_opts()


class TempestConfigProxy(object):
    _config = None
    _path = None

    _extra_log_defaults = [
        ('keystoneclient.session', std_logging.INFO),
        ('paramiko.transport', std_logging.INFO),
        ('requests.packages.urllib3.connectionpool', std_logging.WARN),
    ]

    def _fix_log_levels(self):
        """Tweak the oslo log defaults."""
        for name, level in self._extra_log_defaults:
            std_logging.getLogger(name).setLevel(level)

    def __getattr__(self, attr):
        if not self._config:
            self._fix_log_levels()
            self._config = TempestConfigPrivate(config_path=self._path)

        return getattr(self._config, attr)

    def set_config_path(self, path):
        self._path = path


CONF = TempestConfigProxy()
