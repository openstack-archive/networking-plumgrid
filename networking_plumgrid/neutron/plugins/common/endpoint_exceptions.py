# Copyright 2016 PLUMgrid, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from networking_plumgrid._i18n import _
from neutron.common import exceptions


class InvalidPortForEndpoint(exceptions.InvalidInput):
    message = _("Port %(id)s not associated with a VM. Cannot "
                "be part of endpoint.")


class PortNotFound(exceptions.InvalidInput):
    message = _("Port %(id)s not found.")


class PortAlreadyInUse(exceptions.InUse):
    message = _("Port '%(id)s' already in use by a security group. "
                "Cannot be associated with endpoint.")


class InvalidEndpointType(exceptions.InvalidInput):
    message = _("Invalid Endpoint type %(type)s. Supported "
                "types are: 'vm_ep', 'vm_class'")


class InvalidDataProvided(exceptions.InvalidInput):
    message = _("Invalid data provided for Endpoint.")
