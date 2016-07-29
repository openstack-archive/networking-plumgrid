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
    policy_exceptions as p_excep
from networking_plumgrid.neutron.plugins.extensions import \
    policyrule as ext_pr
from random import randint


def _validate_policy_rule_config(pr_db):
    """
    Helper function to validate policy rule config
    """
    if "protocol" in pr_db:
        if not _validate_policy_rule_protocol(pr_db):
            raise p_excep.UnsupportedProtocol(protocol=pr_db["protocol"])
    if "action" in pr_db:
        if not _validate_policy_rule_action(pr_db):
            raise p_excep.UnsupportedAction(action=pr_db["action"])
    if "src_port_range" in pr_db:
        _validate_port_range(pr_db["src_port_range"])
    if "dst_port_range" in pr_db:
        _validate_port_range(pr_db["dst_port_range"])
    if _validate_port_range_for_icmp(pr_db):
        return True
    return True


def _validate_policy_rule_protocol(pr_db):
    """
    Helper function to validate protocol for policy rule
    """
    if pr_db["protocol"] in const.SUPPORTED_POLICY_RULE_PROTOCOLS:
        return True
    return False


def _validate_policy_rule_action(pr_db):
    """
    Helper function to validate action for policy rule
    """
    if pr_db["action"] in const.SUPPORTED_POLICY_RULE_ACTIONS:
        if (("action_target" not in pr_db or not pr_db["action_target"])
            and pr_db["action"] == 'copy'):
            raise p_excep.InvalidInputActionTarget()
        if (pr_db["action"] == 'allow' and ("action_target" in pr_db
            and pr_db["action_target"])):
            raise p_excep.InvalidInputActionTarget()
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
        raise ext_pr.PolicyRuleInvalidPortRange(port=port_range,
                                             min=str(port_range_min),
                                             max=str(port_range_max))

    if ((lower_bound_val >= 0 and lower_bound_val <= 65535 and
        upper_bound_val >= 0 and upper_bound_val <= 65535) and
        lower_bound_val <= upper_bound_val):
        return port_range
    else:
        port_range_min = randint(1, 65535)
        port_range_max = randint(port_range_min, 65535)
        raise ext_pr.PolicyRuleInvalidPortRange(port=port_range,
                                             min=str(port_range_min),
                                             max=str(port_range_max))


def _validate_port_range_for_icmp(pr_db):
    if ("protocol" in pr_db and
        pr_db["protocol"] == const.SUPPORTED_POLICY_RULE_PROTOCOLS[3]):
        if ("src_port_range" in pr_db and
            pr_db["src_port_range"] is not None):
            raise p_excep.NotSupportedPortRangeICMP()
        elif ("dst_port_range" in pr_db and
              pr_db["dst_port_range"] is not None):
            raise p_excep.NotSupportedPortRangeICMP()
    return True
