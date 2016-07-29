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
    message = _("Floating IP '%(id)s' is already in use by a port/policy-tag")


class FloatingIPMismatch(exceptions.InvalidInput):
    message = _("Floating IP '%(id)s' does not match with External Network.")


class GatewayNotSet(exceptions.InvalidInput):
    message = _("Failed to associate Floating IP '%(id)s'. Gateway not "
                "set for Router.")


class MultipleExternalGatewaysFound(exceptions.InvalidInput):
    message = _("Multiple External Gateways found '%(gateway_list)s'. Please "
                "provide specific Router ID.")


class NoPolicyServiceFound(exceptions.NotFound):
    message = _("Policy Service with id %(id)s does not exist.")


class PortAlreadyInUsePolicyService(exceptions.InUse):
    message = _("Port '%(port)s' already in use by a policy service "
                "'%(ps)s'.")


class InvalidPolicyServiceConfiguration(exceptions.InvalidInput):
    message = _("Policy service only supports ['ingress', 'egress'] ports.")


class UpdateParametersRequired(exceptions.InvalidInput):
    message = _("No update parameter specified atleast one needed.")


class NoPolicyServiceChainFound(exceptions.NotFound):
    message = _("Policy Service Chain with id %(id)s does not exist.")


class PolicyServiceInUse(exceptions.InUse):
    message = _("Policy Service %(id)s %(reason)s with port(s): %(port)s")

    def __init__(self, **kwargs):
        if 'reason' not in kwargs:
            kwargs['reason'] = _("is in use")
        super(PolicyServiceInUse, self).__init__(**kwargs)


class PolicyServiceChainInUse(exceptions.InUse):
    message = _("Policy Service Chain %(id)s %(reason)s with policy service(s): %(ps)s")

    def __init__(self, **kwargs):
        if 'reason' not in kwargs:
            kwargs['reason'] = _("is in use")
        super(PolicyServiceChainInUse, self).__init__(**kwargs)

class PolicyServiceAlreadyInUse(exceptions.InUse):
    message = _("Policy Service '%(ps)s' already in use by a policy service chain. "
                "Cannot be associated with policy service chain '%(psc)s'.")

class NoPolicyRuleFound(exceptions.NotFound):
    message = _("Policy Rule with id %(id)s does not exist.")

class InvalidPolicyRuleConfig(exceptions.InvalidInput):
    message = _("Endpoint group specified as '%(epg)s' of policy rule does not exist.")

class InvalidFormatActionTarget(exceptions.InvalidInput):
    message = _("Invalid input format for action-target. Use the following format "
                "'<tenant_id:service-name/uuid OR tenant_id:service-chain-id/name>'")

class NoActionTargetFound(exceptions.InvalidInput):
    message = _("Action target '%(at)s' specified for policy rule does not exist.")

