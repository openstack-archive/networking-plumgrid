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


class InvalidPortForEndpointGroup(exceptions.InvalidInput):
    message = _("Port %(id)s not associated with a VM. Cannot "
                "be part of endpoint group.")


class PortNotFound(exceptions.InvalidInput):
    message = _("Port %(id)s not found.")


class PortAlreadyInUse(exceptions.InUse):
    message = _("Port '%(id)s' already in use by a security group. "
                "Cannot be associated with endpoint group of type 'vm_ep'.")


class InvalidPolicyTagType(exceptions.InvalidInput):
    message = _("Invalid Policy tag type %(type)s. Supported "
                "types are: 'fip', 'dot1q', 'nsh'")


class InvalidDataProvided(exceptions.InvalidInput):
    message = _("Invalid data provided for Endpoint Group.")


class FloatingIPAlreadyInUse(exceptions.InUse):
    message = _("Floating IP '%(id)s' is already in use by a port/endpoint"
                " group.")

class FloatingIPMismatch(exceptions.InvalidInput):
    message = _("Floating IP '%(id)s' does not match with External Network.")


class GatewayNotSet(exceptions.InvalidInput):
    message = _("Failed to associate Floating IP '%(id)s'. Gateway not "
                "set for Router.")
