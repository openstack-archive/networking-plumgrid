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


class UnsupportedProtocol(exceptions.InvalidInput):
    message = _("Protocol (%(protocol)s) not supported for endpoint policy. "
                "Supported protocols are ['any', 'tcp', 'udp', 'icmp'].")


class UnsupportedAction(exceptions.InvalidInput):
    message = _("Action (%(action)s) not supported for endpoint policy. "
                "Supported action(s) are ['copy'].")


class NotSupportedPortRangeICMP(exceptions.InvalidInput):
    message = _("Port range for ICMP protocol is not supported.")
