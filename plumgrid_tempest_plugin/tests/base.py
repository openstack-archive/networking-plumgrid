# Copyright 2016 PLUMgrid, Inc. All Rights Reserved.
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
from tempest import clients
from tempest import config
from tempest import test

from plumgrid_tempest_plugin.services.pap import pap_client
from plumgrid_tempest_plugin.services.pap import td_client

CONF = config.CONF


class Manager(clients.Manager):
    def __init__(self, credentials=None, service=None):
        super(Manager, self).__init__(credentials, service)
        params = {
            'service': 'network',
            'region': CONF.identity.region,
            'endpoint_type': CONF.network.endpoint_type,
            'build_interval': CONF.network.build_interval,
            'build_timeout': CONF.network.build_timeout
        }
        params.update(self.default_params)
        self.td_client = td_client.TDClient(self.auth_provider, **params)
        self.pap_client = pap_client.PAPClient(self.auth_provider, **params)


class BaseTest(test.BaseTestCase):
    """Base class for PLUMgrid tests."""

    # Use the PLUMgrid Client Manager
    client_manager = Manager

    # NOTE: credentials holds a list of the credentials to be allocated
    # at class setup time. Credential types can be 'primary', 'alt', 'admin' or
    # a list of roles - the first element of the list being a label, and the
    # rest the actual roles.
    # NOTE: primary will result in a manager @ cls.os, alt will have
    # cls.os_alt, and admin will have cls.os_adm.
    credentials = ['primary']
