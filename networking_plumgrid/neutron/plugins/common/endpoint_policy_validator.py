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

from networking_plumgrid.neutron.plugins.common import constants as \
    const
from networking_plumgrid.neutron.plugins.common import \
    endpoint_policy_exceptions as epp_exc
from networking_plumgrid.neutron.plugins.extensions import \
    endpointpolicy as epp_ext
from random import randint


def _validate_endpoint_policy_config(epp_db):
    """
    Helper function to validate endpoing policy config
    """
    if "protocol" in epp_db:
        if not _validate_endpoint_policy_protocol(epp_db):
            raise epp_exc.UnsupportedProtocol(protocol=epp_db["protocol"])
    if "action" in epp_db:
        if not _validate_endpoint_policy_action(epp_db):
            raise epp_exc.UnsupportedAction(action=epp_db["action"])
    if "src_port_range" in epp_db:
        _validate_port_range(epp_db["src_port_range"])
    if "dst_port_range" in epp_db:
        _validate_port_range(epp_db["dst_port_range"])
    if _validate_port_range_for_icmp(epp_db):
        return True
    return True


def _validate_endpoint_policy_protocol(epp_db):
    """
    Helper function to validate protocol for endpoint policy
    """
    if epp_db["protocol"] in const.SUPPORTED_ENDPOINT_POLICY_PROTOCOLS:
        return True
    return False


def _validate_endpoint_policy_action(epp_db):
    """
    Helper function to validate action for endpoint policy
    """
    if epp_db["action"] in const.SUPPORTED_ENDPOINT_POLICY_ACTIONS:
        return True
    return False


def _validate_port_range(port_range):
    if port_range is None:
        return port_range
    try:
        lower_bound, upper_bound = port_range.split('-')
        lower_bound_val = int(lower_bound)
        upper_bound_val = int(upper_bound)
    except (ValueError, TypeError):
        port_range_min = randint(1, 65535)
        port_range_max = randint(port_range_min, 65535)
        raise epp_ext.EndpointPolicyInvalidPortRange(port=port_range,
                                             min=str(port_range_min),
                                             max=str(port_range_max))

    if ((lower_bound_val >= 0 and lower_bound_val <= 65535 and
        upper_bound_val >= 0 and upper_bound_val <= 65535) and
        lower_bound_val <= upper_bound_val):
        return port_range
    else:
        port_range_min = randint(1, 65535)
        port_range_max = randint(port_range_min, 65535)
        raise epp_ext.EndpointPolicyInvalidPortRange(port=port_range,
                                             min=str(port_range_min),
                                             max=str(port_range_max))


def _validate_port_range_for_icmp(epp_db):
    if ("protocol" in epp_db and
        epp_db["protocol"] == const.SUPPORTED_ENDPOINT_POLICY_PROTOCOLS[3]):
        if ("src_port_range" in epp_db and
            epp_db["src_port_range"] is not None):
            raise epp_exc.NotSupportedPortRangeICMP()
        elif ("dst_port_range" in epp_db and
              epp_db["dst_port_range"] is not None):
            raise epp_exc.NotSupportedPortRangeICMP()
    return True
