# Copyright 2016 PLUMgrid, Inc. All Rights Reserved.
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

"""
Policy Rule extension unit tests
"""
#from networking_plumgrid.neutron.plugins.common import \
#    exceptions as p_excep
#from networking_plumgrid.neutron.plugins.common import \
#    policy_exceptions as policy_excep
from networking_plumgrid.neutron.plugins.extensions import \
    policyrule as ext_pr
from networking_plumgrid.neutron.tests.unit import \
    test_networking_plumgrid as test_pg

from neutron.api import extensions
#from neutron import context
#from neutron import manager
from neutron.tests.unit.api import test_extensions as test_ext
from oslo_log import log as logging
#import uuid

LOG = logging.getLogger(__name__)


class PolicyRuleExtensionManager(object):

    def get_resources(self):
        return ext_pr.Policyrule.get_resources()

    def get_actions(self):
        return []

    def get_request_extensions(self):
        return []


class PolicyRuleTestCase(test_pg.PLUMgridPluginV2TestCase):
    def setUp(self, plugin=None, ext_mgr=None):
        super(PolicyRuleTestCase, self).setUp()
        ext_mgr = PolicyRuleExtensionManager()
        extensions.PluginAwareExtensionManager._instance = None
        self.ext_api = test_ext.setup_extensions_middleware(ext_mgr)


class TestPolicyRule(PolicyRuleTestCase):

    def test_create_policy_rule(self):
        pass

    def test_create_policy_rule_src_grp_epg(self):
        pass

    def test_create_policy_rule_dst_grp_epg(self):
        pass

    def test_create_policy_rule_src_grp_epg_invalid(self):
        pass

    def test_create_policy_rule_dst_grp_epg_invalid(self):
        pass

    def test_create_policy_rule_src_dst_grp_epg(self):
        pass

    def test_create_policy_rule_src_grp_sg(self):
        pass

    def test_create_policy_rule_dst_grp_sg(self):
        pass

    def test_create_policy_rule_src_grp_sg_invalid(self):
        pass

    def test_create_policy_rule_dst_grp_sg_invalid(self):
        pass

    def test_create_policy_rule_src_dst_grp_sg(self):
        pass

    def test_create_policy_rule_src_epg_dst_sg(self):
        pass

    def test_create_policy_rule_src_sg_dst_epg(self):
        pass

    def test_create_policy_rule_action_allow(self):
        pass

    def test_create_policy_rule_action_copy(self):
        pass

    def test_create_policy_rule_action_invalid(self):
        pass

    def test_create_policy_rule_protocol_any(self):
        pass

    def test_create_policy_rule_protocol_tcp(self):
        pass

    def test_create_policy_rule_protocol_udp(self):
        pass

    def test_create_policy_rule_protocol_invalid(self):
        pass

    def test_create_policy_rule_icmp_with_range(self):
        pass

    def test_create_policy_rule_src_port_range(self):
        pass

    def test_create_policy_rule_dst_port_range(self):
        pass

    def test_create_policy_rule_invalid_src_port_range(self):
        pass

    def test_create_policy_rule_invalid_dst_port_range(self):
        pass

    def test_create_policy_rule_action_target(self):
        pass

    def test_create_policy_rule_remote_action_target(self):
        pass

    def test_create_policy_rule_src_grp_tag(self):
        pass

    def test_create_policy_rule_dst_grp_tag(self):
        pass

    def test_create_policy_rule_global_tag(self):
        pass

    def test_create_policy_rule_src_grp_tag_not_associated_with_src_grp(self):
        pass

    def test_create_policy_rule_dst_grp_tag_not_associated_with_dst_grp(self):
        pass

    def test_create_policy_rule_global_tag_does_not_exist(self):
        pass

    def test_create_policy_rule_action_target_doest_not_exist(self):
        pass

    def test_create_policy_rule_remote_action_target_does_not_exist(self):
        pass

    def test_delete_policy_rule(self):
        pass

    def test_delete_policy_rule_does_not_exist(self):
        pass

    def test_list_policy_rules(self):
        pass

    def test_create_get_policy_rule(self):
        pass

    def _make_epg_dict(self, ptag_id=None,
                       name="test_sg_name"):
        epg_dict = {"endpoint_group": {
                   "tenant_id": "test_tenant",
                   "name": name,
                   "description": "test_description",
                   "is_security_group": False}}
        if ptag_id is not None:
            epg_dict["endpoint_group"]["policy_tag_id"] = ptag_id
        return epg_dict

    def _make_epg_update_dict(self, name="test_tenant",
                              description="test_description",
                              add_tag=[],
                              remove_tag=[]):
        return {"endpoint_group": {
                   "tenant_id": "test_tenant",
                   "name": name,
                   "description": description,
                   "add_tag": add_tag,
                   "remove_tag": remove_tag,
                   "is_security_group": False,
                   "policy_tag_id": None}}

    def _make_ps_dict(self, name="test_ps", inports=[], eports=[],
                      bidirect_ports=[]):
        return {"policy_service": {
                    "tenant_id": "test_tenant",
                    "description": "test-ps",
                    "name": name,
                    "ingress_ports": inports,
                    "egress_ports": eports,
                    "bidirectional_ports": bidirect_ports}}

    def _make_pr_dict(self, action_target=None, name="test_policy",
                      src_grp=None, dst_grp=None, action="copy",
                      protocol="any", src_port_range=None,
                      dst_port_range=None, tag=None):
        return {"endpoint_policy": {
                   "tenant_id": "test_tenant",
                   "name": name,
                   "src_grp": src_grp,
                   "dst_grp": dst_grp,
                   "action": action,
                   "src_port_range": src_port_range,
                   "dst_port_range": dst_port_range,
                   "protocol": protocol,
                   "action_target": action_target,
                   "tag": tag}}

    def _make_ptag_dict(self, tag_type, tag_id=None,
                        floatingip_id=None, floating_ip_address=None,
                        router_id=None):
        return {"policy_tag": {
                               "tenant_id": "test_tenant",
                               "name": "test_name",
                               "tag_type": tag_type,
                               "tag_id": tag_id,
                               "floatingip_id": floatingip_id,
                               "floating_ip_address": floating_ip_address,
                               "router_id": router_id}}

    def _fake_sg(self):
        return {"security_group": {"name": "fake-sg",
                                   "description": "sample-description",
                                   "tenant_id": "test-tenant"}}
