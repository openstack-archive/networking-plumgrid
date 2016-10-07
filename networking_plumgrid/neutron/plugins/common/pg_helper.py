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
# service type constants:

from networking_plumgrid.neutron.plugins.common import constants as \
    net_pg_const
from networking_plumgrid.neutron.plugins.common import exceptions as plum_excep
from networking_plumgrid.neutron.plugins.common import \
    policy_exceptions as policy_exc
from oslo_log import log as logging
from oslo_utils import uuidutils


LOG = logging.getLogger(__name__)


def _retrieve_subnet_dict(self, port_db, context):
    """
    Helper function to retrieve the subnet dictionary
    """
    # Retrieve subnet information
    subnet_db = {}
    if len(port_db["fixed_ips"]) != 0:
        for subnet_index in range(0,
                                  len(port_db["fixed_ips"])):
            subnet_id = (port_db["fixed_ips"][subnet_index]
                         ["subnet_id"])
            subnet_db[subnet_index] = self._get_subnet(context, subnet_id)
    return subnet_db


def _check_floatingip_in_use(self, fp_id, ptag_db):
    """
    Helper function to check if Floating IP already exists and
    is associated with a SecurityGroup/PolicyTag
    """
    for entry in ptag_db:
        if fp_id == entry["floatingip_id"]:
            return True
    return False


def _check_floatingip_network(self, context, ptag_db):
    """
    Helper function to check Floating IP is from the specified
    External Network
    """
    floatingip_db = self.get_floatingip(context,
                                        ptag_db["policy_tag"]["floatingip_id"])
    router_db = self.get_routers(context,
                   filters={"tenant_id": [ptag_db["policy_tag"]["tenant_id"]]})
    floating_net_id = floatingip_db["floating_network_id"]

    if floatingip_db.get('port_id') is not None:
        raise policy_exc.FloatingIPAlreadyInUse(id=str(floatingip_db["id"]))

    external_gateway = []
    if "router_id" in ptag_db["policy_tag"] and \
       ptag_db["policy_tag"]["router_id"] is not None:
        external_gateway.append(ptag_db["policy_tag"]["router_id"])
    else:
        for router in router_db:
            if ("external_gateway_info" in router and
                router["external_gateway_info"] and
                router["external_gateway_info"]
                      ["network_id"] == floating_net_id):
                external_gateway.append(router["id"])
        if len(external_gateway) == 0:
            raise policy_exc.GatewayNotSet(id=str(floatingip_db["id"]))
        if len(external_gateway) > 1:
            raise policy_exc.MultipleExternalGatewaysFound(
                                           gateway_list=external_gateway)
    return (floatingip_db, external_gateway[0])


def _check_duplicate_ports_policy_service_create(self, ps_db):
    """
    Helper function to check if duplicate ingress, egress, bidirectional
    ports exists in create policy service JSON
    """
    port_list = []
    if "ingress_ports" in ps_db and ps_db["ingress_ports"]:
        port_list.append(set([tuple(d.items()) for d
                         in ps_db["ingress_ports"]]))
        if _check_duplicate_ports_config(ps_db["ingress_ports"]):
            return True, "ingress ports"

    if "egress_ports" in ps_db and ps_db["egress_ports"]:
        port_list.append(set([tuple(d.items()) for d
                         in ps_db["egress_ports"]]))
        if _check_duplicate_ports_config(ps_db["egress_ports"]):
            return True, "egress ports"

    if "bidirectional_ports" in ps_db and ps_db["bidirectional_ports"]:
        port_list.append(set([tuple(d.items()) for d
                         in ps_db["bidirectional_ports"]]))
        if _check_duplicate_ports_config(ps_db["bidirectional_ports"]):
            return True, "bidirectional ports"

    if _check_duplicate_ports_across_config(port_list):
        return True, "create parameters"

    return False, None


def _check_duplicate_ports_policy_service_update(self, ps_db):
    """
    Helper function to check if duplicate ingress, egress, bidirectional
    ports exists in update policy service JSON
    """
    port_list = []
    if "add_ingress_ports" in ps_db and ps_db["add_ingress_ports"]:
        port_list.append(set([tuple(d.items()) for d
                         in ps_db["add_ingress_ports"]]))
        if _check_duplicate_ports_config(ps_db["add_ingress_ports"]):
            return True, "add ingress ports"

    if "add_egress_ports" in ps_db and ps_db["add_egress_ports"]:
        port_list.append(set([tuple(d.items()) for d
                          in ps_db["add_egress_ports"]]))
        if _check_duplicate_ports_config(ps_db["add_egress_ports"]):
            return True, "add egress ports"

    if "add_bidirectional_ports" in ps_db and ps_db["add_bidirectional_ports"]:
        port_list.append(set([tuple(d.items()) for d
                          in ps_db["add_bidirectional_ports"]]))
        if _check_duplicate_ports_config(ps_db["add_bidirectional_ports"]):
            return True, "add bidirectional ports"

    if "remove_ingress_ports" in ps_db and ps_db["remove_ingress_ports"]:
        port_list.append(set([tuple(d.items()) for d
                          in ps_db["remove_ingress_ports"]]))
        if _check_duplicate_ports_config(ps_db["remove_ingress_ports"]):
            return True, "remove ingress ports"

    if "remove_egress_ports" in ps_db and ps_db["remove_egress_ports"]:
        port_list.append(set([tuple(d.items()) for d
                          in ps_db["remove_egress_ports"]]))
        if _check_duplicate_ports_config(ps_db["remove_egress_ports"]):
            return True, "remove engress ports"

    if ("remove_bidirectional_ports" in ps_db
        and ps_db["remove_bidirectional_ports"]):
        port_list.append(set([tuple(d.items()) for d
                          in ps_db["remove_bidirectional_ports"]]))
        if _check_duplicate_ports_config(ps_db["remove_bidirectional_ports"]):
            return True, "remove bidirectional ports"

    if _check_duplicate_ports_across_config(port_list):
        return True, "update parameters"

    return False, None


def _check_duplicate_ports_config(port_db):
    if (len(port_db) > len([dict(t) for t in
        set([tuple(d.items()) for d in port_db])])):
        return True


def _check_duplicate_ports_across_config(list_port_db):
    for i in range(0, len(list_port_db)):
        for j in range(i + 1, len(list_port_db)):
            if (len(list_port_db[i].intersection(list_port_db[j])) > 0):
                return True


def _validate_port_owner(port_db):
    """
    Helper function to validate port is owned by a compute resource
    """
    if ("device_owner" in port_db and "binding:vif_type" in port_db and
        "compute" in port_db["device_owner"] and
        port_db["binding:vif_type"] == net_pg_const.BINDING_VIF_TYPE_IOVISOR):
        return True
    return False


def _check_policy_service_leg_mode(ps_obj, updated_ps_obj=None):
    """
    Helper function to check if bidirectional ports are
    specified with ingress or egress ports
    """
    if ("ingress_ports" in ps_obj and "egress_ports"
        in ps_obj and "bidirectional_ports" in ps_obj):
        if updated_ps_obj is None:
            if ((ps_obj["ingress_ports"] or ps_obj["egress_ports"])
                and ps_obj["bidirectional_ports"]):
                return True
        else:
            if ps_obj["ingress_ports"] or ps_obj["egress_ports"]:
                if ("add_bidirectional_ports" in updated_ps_obj or
                    "remove_bidirectional_ports" in updated_ps_obj):
                    return True
            elif ps_obj["bidirectional_ports"]:
                if ("add_ingress_ports" in updated_ps_obj or
                    "add_egress_ports" in updated_ps_obj or
                    "remove_ingress_ports" in updated_ps_obj or
                    "remove_egress_ports" in updated_ps_obj):
                    return True
            else:
                #Update call with any prior ports in policy service
                if ((("add_ingress_ports" in updated_ps_obj or
                      "add_ingress_ports" in updated_ps_obj)
                    or ("remove_ingress_ports" in updated_ps_obj or
                        "remove_egress_ports" in updated_ps_obj))
                    and ("add_bidirectional_ports" in updated_ps_obj or
                         "remove_bidirectional_ports" in updated_ps_obj)):
                    return True
    return False


def _is_security_group(context, ep_obj, ep_db, config):
    if config in ep_db and ep_db[config]:
        for epg in ep_db[config]:
            epg_id_list = ep_obj.get_endpoint_groups(context,
                                     filters={'id': [epg['id']]},
                                     fields=["id"])
            if len(epg_id_list) == 1:
                if ("is_security_group" in epg_id_list[0]
                    and epg_id_list[0]["is_security_group"]):
                    operation = "Endpoint association"
                    raise policy_exc.OperationNotAllowed(operation=operation,
                                                       id=epg_id_list[0]["id"])


def _validate_ep_config(ep_db):
    if ((ep_db["ip_mask"] and ep_db["ip_port"]) or
        (ep_db["ip_mask"]and ep_db["port_id"]) or
        (ep_db["ip_port"] and ep_db["port_id"])):
        raise policy_exc.MultipleAssociationForEndpoint()


def _check_duplicates_endpoint_config(ep_db):
    if "ep_groups" in ep_db and ep_db["ep_groups"]:
        if (len(ep_db["ep_groups"]) > len([dict(t) for t in
            set([tuple(d.items()) for d in ep_db["ep_groups"]])])):
            raise policy_exc.DuplicateEndpointGroup()
    if "add_endpoint_groups" in ep_db and ep_db["add_endpoint_groups"]:
        if (len(ep_db["add_endpoint_groups"]) > len([dict(t) for t in
            set([tuple(d.items()) for d in ep_db["add_endpoint_groups"]])])):
            raise policy_exc.DuplicateEndpointGroup()
    if "remove_endpoint_groups" in ep_db and ep_db["remove_endpoint_groups"]:
        if (len(ep_db["remove_endpoint_groups"]) > len([dict(t) for t in
            set([tuple(d.items()) for d in
            ep_db["remove_endpoint_groups"]])])):
            raise policy_exc.DuplicateEndpointGroup()

    if (("add_endpoint_groups" in ep_db and ep_db["add_endpoint_groups"]) and
        ("remove_endpoint_groups" in ep_db
         and ep_db["remove_endpoint_groups"])):
        if (len(set([tuple(d.items()) for d in ep_db["add_endpoint_groups"]]).
            intersection(set([tuple(d.items()) for d in
            ep_db["remove_endpoint_groups"]]))) > 0):
            raise policy_exc.DuplicateEndpointGroup()


def _process_policy_tag(self, context, epg_db):
    if "policy_tag_id" in epg_db and epg_db["policy_tag_id"]:
        if (not uuidutils.is_uuid_like(epg_db['policy_tag_id']) and
            epg_db['policy_tag_id'] is not None):
            ptag_list = self.get_policy_tags(context,
                                 filters={'name': [epg_db['policy_tag_id']]},
                                 fields=["id"])

            if len(ptag_list) == 1:
                epg_db['policy_tag_id'] = ptag_list[0]["id"]
            elif len(ptag_list) == 0:
                err_message = ("No policy tag"
                               " matches found for tag"
                               " '%s'" % epg_db['policy_tag_id'])
                raise plum_excep.PLUMgridException(err_msg=err_message)
            else:
                err_message = ("Multiple policy tag"
                               " matches found for tag"
                               " '%s', use an ID to be more"
                               " specific." % epg_db['policy_tag_id'])
                raise plum_excep.PLUMgridException(err_msg=err_message)
    return epg_db


def _process_epg_update(self, context, epg_db):
    ptag_db = {}
    if "policy_tag_id" in epg_db and epg_db["policy_tag_id"]:
        config = "policy_tag_id"
    elif "add_tag" in epg_db and epg_db["add_tag"]:
        config = "add_tag"
    elif "remove_tag" in epg_db and epg_db["remove_tag"]:
        config = "remove_tag"
    else:
        config = None
    if config in epg_db and epg_db[config]:
        if (not uuidutils.is_uuid_like(epg_db[config]) and
            epg_db[config] is not None):
            ptag_list = self.get_policy_tags(context,
                                 filters={'name': [epg_db[config]]},
                                 fields=["id"])

            if len(ptag_list) == 1:
                epg_db[config] = ptag_list[0]["id"]
                ptag_db = self.get_policy_tag(context,
                                              ptag_list[0]["id"])
            elif len(ptag_list) == 0:
                err_message = ("No policy tag"
                               " matches found for tag"
                               " '%s'" % epg_db[config])
                raise plum_excep.PLUMgridException(err_msg=err_message)
            else:
                err_message = ("Multiple policy tag"
                               " matches found for tag"
                               " '%s', use an ID to be more"
                               " specific." % epg_db[config])
                raise plum_excep.PLUMgridException(err_msg=err_message)
        elif (uuidutils.is_uuid_like(epg_db[config]) and
              epg_db[config] is not None):
            ptag_id = epg_db[config]
            ptag_db = self.get_policy_tag(context,
                                          ptag_id)
    return (epg_db, ptag_db)


def _check_policy_service_in_use(self, context, id):
    """
    Helper function to check policy service is in use by
    any policy rule
    """
    pr_list = self.get_policy_rules(context,
                              fields=["id", "action_target"])
    action_target_list = []
    for rule in pr_list:
        if _check_remote_action_target(rule):
            action_target_list.append((rule["action_target"].split(":"))[1])
        else:
            action_target_list.append(rule["action_target"])
    in_use_list = filter(lambda x: x == id, action_target_list)
    if len(in_use_list) > 0:
        raise policy_exc.PolicyServiceInUsePolicyRule(id=id)


def _recursive_delete_endpoints(self, context, id):
    """
    Helper function to delete endpoints when endpoint group
    is deleted
    """
    endpoint_list = self.get_endpoints(context,
                                       filters={'ep_groups': [{'id': id}]})
    for endpoint in endpoint_list:
        if ((len(endpoint["ep_groups"]) == 1) and
            endpoint["ep_groups"][0]["id"] == id):
            self.delete_endpoint(context, endpoint["id"])


def _check_remote_action_target(pr_db):
    """
    Helper function to check if action target for policy rule
    is for a tenant id
    """
    if "action_target" in pr_db and pr_db["action_target"]:
        action_target_db = pr_db["action_target"].split(":")
        if len(action_target_db) == 2:
            return True
        else:
            return False


def _update_port_description(port_db, port_data):
    """
    Helper function to update port description
    """
    if "description" in port_data:
        port_db["description"] = port_data["description"]
