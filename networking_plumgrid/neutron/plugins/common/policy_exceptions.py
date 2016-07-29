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
    message = _("Port %(id)s not associated with a compute resource. Cannot "
                "be part of endpoint.")


class PortNotFound(exceptions.InvalidInput):
    message = _("Port %(id)s not found.")


class PortAlreadyInUseSecurityGroup(exceptions.InUse):
    message = _("Port '%(id)s' already in use by a security group. ")


class InvalidPolicyTagType(exceptions.InvalidInput):
    message = _("Invalid Policy tag type %(type)s. Supported "
                "types are: 'fip', 'dot1q', 'nsh'")


class NoPolicyTagFound(exceptions.NotFound):
    message = _("Policy Tag with id %(id)s does not exist")


class PolicyTagAlreadyInUse(exceptions.InUse):
    message = _("Policy Tag '%(ptag_id)s' already in use by endpoint "
                "group: '%(epg_id)s'.")


class InvalidDataProvidedEndpointGroup(exceptions.InvalidInput):
    message = _("Invalid data provided for Endpoint Group.")


class InvalidDataProvidedEndpoint(exceptions.InvalidInput):
    message = _("Invalid data provided for Endpoint.")


class FloatingIPAlreadyInUse(exceptions.InUse):
    message = _("Floating IP '%(id)s' is in use by a port/policy-tag")


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
    message = _("Policy service only supports ['ingress', 'egress', "
                "'bidirectional'] ports.")


class UpdateParametersRequired(exceptions.InvalidInput):
    message = _("No update parameter specified atleast one needed.")


class PolicyServiceInUse(exceptions.InUse):
    message = _("Policy Service %(id)s %(reason)s with port(s): %(port)s")

    def __init__(self, **kwargs):
        if 'reason' not in kwargs:
            kwargs['reason'] = _("is in use")
        super(PolicyServiceInUse, self).__init__(**kwargs)


class NoPolicyRuleFound(exceptions.NotFound):
    message = _("Policy Rule with id %(id)s does not exist.")


class InvalidPolicyRuleConfig(exceptions.InvalidInput):
    message = _("Endpoint group specified as '%(epg)s' of policy rule does "
                "not exist.")


class InvalidFormatActionTarget(exceptions.InvalidInput):
    message = _("Invalid input format for action-target. Use the following "
                "format 'service-name/uuid' OR '<tenant_id:service-name/uuid'")


class NoActionTargetFound(exceptions.InvalidInput):
    message = _("Action target '%(at)s' specified for policy rule does "
                "not exist.")


class OperationNotAllowed(exceptions.InvalidInput):
    message = _("%(operation)s operation for endpoint group (%(id)s) is "
                "not allowed. Endpoint group (%(id)s) refers to a security "
                "group.")


class NoPolicyTagFoundEndpointGroup(exceptions.InvalidInput):
    message = _("Policy Tag not associated with endpoint group '%(epg)s'."
                "Unable to apply tag to policy rule.")


class DuplicatePortFound(exceptions.InvalidInput):
    message = _("Duplicate ports found in %(match)s of policy service.")


class InvalidDataProvidedPolicyService(exceptions.InvalidInput):
    message = _("Invalid data provided for Policy Service.")


class InvalidPortForPolicyService(exceptions.InvalidInput):
    message = _("Port %(id)s not associated with a compute resource. Cannot "
                "be part of policy service.")


class PortAlreadyInUseEndpoint(exceptions.InUse):
    message = _("Port '%(port)s' already in use by a endpoint "
                "'%(ep)s'.")


class InvalidPortConfigPolicyService(exceptions.InvalidInput):
    message = _("Bidirectional ports cannot be specified along with "
                "ingress or egress ports")


class NotSupportedPortRangeICMP(exceptions.InvalidInput):
    message = _("Port range for ICMP protocol is not supported.")


class UnsupportedProtocol(exceptions.InvalidInput):
    message = _("Protocol (%(protocol)s) not supported for endpoint policy. "
                "Supported protocols are ['any', 'tcp', 'udp', 'icmp'].")


class UnsupportedAction(exceptions.InvalidInput):
    message = _("Action (%(action)s) not supported for endpoint policy. "
                "Supported action(s) are ['copy', 'allow'].")


class MultipleAssociationForEndpoint(exceptions.InvalidInput):
    message = _("Multiple association criterion for endpoint specified."
                " Please specify only one criteria per endpoint.")


class DuplicateEndpointGroup(exceptions.InvalidInput):
    message = _("Duplicate endpoint groups found in endpoint config.")


class InvalidInputActionTarget(exceptions.InvalidInput):
    message = _("Action target is required by the following "
                "policy rule action(s) : ['copy']")
