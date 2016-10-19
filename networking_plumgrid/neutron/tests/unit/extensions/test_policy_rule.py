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
from networking_plumgrid.neutron.plugins.common import \
    exceptions as p_excep
from networking_plumgrid.neutron.plugins.common import \
    policy_exceptions as policy_excep
from networking_plumgrid.neutron.plugins.extensions import \
    policyrule as ext_pr
from networking_plumgrid.neutron.tests.unit import \
    test_networking_plumgrid as test_pg

from neutron.api import extensions
from neutron import context
from neutron import manager
from neutron.tests.unit.api import test_extensions as test_ext
from oslo_log import log as logging
import uuid

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
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        pr = self._make_pr_dict()

        pr_ret = plugin.create_policy_rule(admin_context, pr)
        pr_get_ret = plugin.get_policy_rule(admin_context, pr_ret["id"])
        self.assertEqual(pr_ret, pr_get_ret)

    def test_create_policy_rule_src_grp_epg(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        pr = self._make_pr_dict(src_grp=epg_ret["id"])
        pr_ret = plugin.create_policy_rule(admin_context, pr)
        pr_get_ret = plugin.get_policy_rule(admin_context, pr_ret["id"])
        self.assertEqual(pr_ret, pr_get_ret)

    def test_create_policy_rule_dst_grp_epg(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        pr = self._make_pr_dict(dst_grp=epg_ret["id"])
        pr_ret = plugin.create_policy_rule(admin_context, pr)
        pr_get_ret = plugin.get_policy_rule(admin_context, pr_ret["id"])
        self.assertEqual(pr_ret, pr_get_ret)

    def test_create_policy_rule_src_grp_epg_invalid(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        pr = self._make_pr_dict(src_grp=str(uuid.uuid4()))
        self.assertRaises(policy_excep.InvalidPolicyRuleConfig,
                          plugin.create_policy_rule, admin_context, pr)

    def test_create_policy_rule_dst_grp_epg_invalid(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        pr = self._make_pr_dict(dst_grp=str(uuid.uuid4()))
        self.assertRaises(policy_excep.InvalidPolicyRuleConfig,
                          plugin.create_policy_rule, admin_context, pr)

    def test_create_policy_rule_src_dst_grp_epg(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        pr = self._make_pr_dict(src_grp=epg_ret["id"], dst_grp=epg_ret["id"])
        pr_ret = plugin.create_policy_rule(admin_context, pr)
        pr_get_ret = plugin.get_policy_rule(admin_context, pr_ret["id"])
        self.assertEqual(pr_ret, pr_get_ret)

    def test_create_policy_rule_src_grp_sg(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        sg = self._fake_sg()

        sg_ret = plugin.create_security_group(
                          admin_context, sg)
        pr = self._make_pr_dict(src_grp=sg_ret["id"])
        pr_ret = plugin.create_policy_rule(admin_context, pr)
        pr_get_ret = plugin.get_policy_rule(admin_context, pr_ret["id"])
        self.assertEqual(pr_ret, pr_get_ret)

    def test_create_policy_rule_dst_grp_sg(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        sg = self._fake_sg()

        sg_ret = plugin.create_security_group(
                          admin_context, sg)
        pr = self._make_pr_dict(dst_grp=sg_ret["id"])
        pr_ret = plugin.create_policy_rule(admin_context, pr)
        pr_get_ret = plugin.get_policy_rule(admin_context, pr_ret["id"])
        self.assertEqual(pr_ret, pr_get_ret)

    def test_create_policy_rule_src_dst_grp_sg(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        sg = self._fake_sg()

        sg_ret = plugin.create_security_group(
                          admin_context, sg)
        pr = self._make_pr_dict(src_grp=sg_ret["id"], dst_grp=sg_ret["id"])
        pr_ret = plugin.create_policy_rule(admin_context, pr)
        pr_get_ret = plugin.get_policy_rule(admin_context, pr_ret["id"])
        self.assertEqual(pr_ret, pr_get_ret)

    def test_create_policy_rule_src_epg_dst_sg(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        sg = self._fake_sg()

        sg_ret = plugin.create_security_group(
                          admin_context, sg)
        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        pr = self._make_pr_dict(src_grp=epg_ret["id"], dst_grp=sg_ret["id"])
        pr_ret = plugin.create_policy_rule(admin_context, pr)
        pr_get_ret = plugin.get_policy_rule(admin_context, pr_ret["id"])
        self.assertEqual(pr_ret, pr_get_ret)

    def test_create_policy_rule_src_sg_dst_epg(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        sg = self._fake_sg()

        sg_ret = plugin.create_security_group(
                          admin_context, sg)
        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        pr = self._make_pr_dict(src_grp=sg_ret["id"], dst_grp=epg_ret["id"])
        pr_ret = plugin.create_policy_rule(admin_context, pr)
        pr_get_ret = plugin.get_policy_rule(admin_context, pr_ret["id"])
        self.assertEqual(pr_ret, pr_get_ret)

    def test_create_policy_rule_action_allow(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        pr = self._make_pr_dict()

        pr_ret = plugin.create_policy_rule(admin_context, pr)
        pr_get_ret = plugin.get_policy_rule(admin_context, pr_ret["id"])
        self.assertEqual(pr_ret, pr_get_ret)

    def test_create_policy_rule_action_copy(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        ps = self._make_ps_dict()

        ps_ret = plugin.create_policy_service(admin_context, ps)
        pr = self._make_pr_dict(action="copy", action_target=ps_ret["id"])

        pr_ret = plugin.create_policy_rule(admin_context, pr)
        pr_get_ret = plugin.get_policy_rule(admin_context, pr_ret["id"])
        self.assertEqual(pr_ret, pr_get_ret)

    def test_create_policy_rule_action_invalid(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        pr = self._make_pr_dict(action="invalid")
        self.assertRaises(policy_excep.UnsupportedAction,
                          plugin.create_policy_rule, admin_context, pr)

    def test_create_policy_rule_protocol_any(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        pr = self._make_pr_dict(protocol="any")

        pr_ret = plugin.create_policy_rule(admin_context, pr)
        pr_get_ret = plugin.get_policy_rule(admin_context, pr_ret["id"])
        self.assertEqual(pr_ret, pr_get_ret)

    def test_create_policy_rule_protocol_tcp(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        pr = self._make_pr_dict(protocol="tcp")

        pr_ret = plugin.create_policy_rule(admin_context, pr)
        pr_get_ret = plugin.get_policy_rule(admin_context, pr_ret["id"])
        self.assertEqual(pr_ret, pr_get_ret)

    def test_create_policy_rule_protocol_udp(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        pr = self._make_pr_dict(protocol="udp")

        pr_ret = plugin.create_policy_rule(admin_context, pr)
        pr_get_ret = plugin.get_policy_rule(admin_context, pr_ret["id"])
        self.assertEqual(pr_ret, pr_get_ret)

    def test_create_policy_rule_protocol_invalid(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        pr = self._make_pr_dict(protocol="invalid")
        self.assertRaises(policy_excep.UnsupportedProtocol,
                          plugin.create_policy_rule, admin_context, pr)

    def test_create_policy_rule_icmp_with_range(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        pr = self._make_pr_dict(protocol="icmp", src_port_range="10-10")
        self.assertRaises(policy_excep.NotSupportedPortRangeICMP,
                          plugin.create_policy_rule, admin_context, pr)

    def test_create_policy_rule_src_port_range(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        pr = self._make_pr_dict(src_port_range="10-10", protocol="tcp")

        pr_ret = plugin.create_policy_rule(admin_context, pr)
        pr_get_ret = plugin.get_policy_rule(admin_context, pr_ret["id"])
        self.assertEqual(pr_ret, pr_get_ret)

    def test_create_policy_rule_dst_port_range(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        pr = self._make_pr_dict(dst_port_range="10-10", protocol="tcp")

        pr_ret = plugin.create_policy_rule(admin_context, pr)
        pr_get_ret = plugin.get_policy_rule(admin_context, pr_ret["id"])
        self.assertEqual(pr_ret, pr_get_ret)

    def test_create_policy_rule_invalid_src_port_range(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        pr = self._make_pr_dict(src_port_range="x-y", protocol="tcp")
        self.assertRaises(ext_pr.PolicyRuleInvalidPortRange,
                          plugin.create_policy_rule, admin_context, pr)

    def test_create_policy_rule_invalid_dst_port_range(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        pr = self._make_pr_dict(dst_port_range="x-y", protocol="tcp")
        self.assertRaises(ext_pr.PolicyRuleInvalidPortRange,
                          plugin.create_policy_rule, admin_context, pr)

    def test_create_policy_rule_src_port_range_no_protocol(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        pr = self._make_pr_dict(dst_port_range="10-10")
        self.assertRaises(policy_excep.ProtocolNotSpecified,
                          plugin.create_policy_rule, admin_context, pr)

    def test_create_policy_rule_dst_port_range_no_protocol(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        pr = self._make_pr_dict(dst_port_range="10-10")
        self.assertRaises(policy_excep.ProtocolNotSpecified,
                          plugin.create_policy_rule, admin_context, pr)

    def test_create_policy_rule_action_target(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        ps = self._make_ps_dict()

        ps_ret = plugin.create_policy_service(admin_context, ps)
        pr = self._make_pr_dict(action="copy", action_target=ps_ret["id"])

        pr_ret = plugin.create_policy_rule(admin_context, pr)
        pr_get_ret = plugin.get_policy_rule(admin_context, pr_ret["id"])
        self.assertEqual(pr_ret, pr_get_ret)

    def test_create_policy_rule_remote_action_target(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        ps = self._make_ps_dict()

        ps_ret = plugin.create_policy_service(admin_context, ps)
        pr = self._make_pr_dict(action="copy",
                                action_target=ps_ret["tenant_id"] + ":"
                                + ps_ret["name"])
        self.assertRaises(p_excep.PLUMgridException,
                          plugin.create_policy_rule, admin_context, pr)

    def test_create_policy_rule_src_grp_tag(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        ptag = self._make_ptag_dict(tag_type="dot1q",
                                    tag_id="100-200")

        ptag_ret = plugin.create_policy_tag(
                      admin_context, ptag)
        epg = self._make_epg_dict(ptag_id=ptag_ret["id"])

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        pr = self._make_pr_dict(src_grp=epg_ret["id"], tag=ptag_ret["id"])
        pr_ret = plugin.create_policy_rule(admin_context, pr)
        pr_get_ret = plugin.get_policy_rule(admin_context, pr_ret["id"])
        self.assertEqual(pr_ret, pr_get_ret)

    def test_create_policy_rule_dst_grp_tag(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        ptag = self._make_ptag_dict(tag_type="dot1q",
                                    tag_id="100-200")

        ptag_ret = plugin.create_policy_tag(
                      admin_context, ptag)
        epg = self._make_epg_dict(ptag_id=ptag_ret["id"])

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        pr = self._make_pr_dict(dst_grp=epg_ret["id"], tag=ptag_ret["id"])
        pr_ret = plugin.create_policy_rule(admin_context, pr)
        pr_get_ret = plugin.get_policy_rule(admin_context, pr_ret["id"])
        self.assertEqual(pr_ret, pr_get_ret)

    def test_create_policy_rule_global_tag(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        ptag = self._make_ptag_dict(tag_type="dot1q",
                                    tag_id="100-200")

        ptag_ret = plugin.create_policy_tag(
                      admin_context, ptag)
        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        pr = self._make_pr_dict(dst_grp=epg_ret["id"], tag=ptag_ret["id"])
        pr_ret = plugin.create_policy_rule(admin_context, pr)
        pr_get_ret = plugin.get_policy_rule(admin_context, pr_ret["id"])
        self.assertEqual(pr_ret, pr_get_ret)

    def test_create_policy_rule_global_tag_does_not_exist(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        epg = self._make_epg_dict()

        epg_ret = plugin.create_endpoint_group(
                      admin_context, epg)
        pr = self._make_pr_dict(src_grp=epg_ret["id"], tag=str(uuid.uuid4()))
        self.assertRaises(policy_excep.NoPolicyTagFoundEndpointGroup,
                          plugin.create_policy_rule, admin_context, pr)

    def test_create_policy_rule_action_target_does_not_exist(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        pr = self._make_pr_dict(action="copy", action_target=str(uuid.uuid4()))
        self.assertRaises(policy_excep.NoActionTargetFound,
                          plugin.create_policy_rule, admin_context, pr)

    def test_create_policy_rule_remote_action_target_does_not_exist(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        pr = self._make_pr_dict(action="copy",
                                action_target=str(uuid.uuid4()) + ":" +
                                str(uuid.uuid4()))
        self.assertRaises(p_excep.PLUMgridException,
                          plugin.create_policy_rule, admin_context, pr)

    def test_delete_policy_rule(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        pr = self._make_pr_dict()

        pr_ret = plugin.create_policy_rule(admin_context, pr)
        resp = plugin.delete_policy_rule(admin_context, pr_ret["id"])
        self.assertEqual(None, resp)

    def test_delete_policy_rule_does_not_exist(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()
        self.assertRaises(policy_excep.NoPolicyRuleFound,
                          plugin.delete_policy_rule, admin_context,
                          str(uuid.uuid4()))

    def test_list_policy_rules(self):
        plugin = manager.NeutronManager.get_plugin()
        admin_context = context.get_admin_context()

        pr1 = self._make_pr_dict(name="list_pr1")
        pr_ret1 = plugin.create_policy_rule(admin_context, pr1)
        pr2 = self._make_pr_dict(name="list_pr2")
        pr_ret2 = plugin.create_policy_rule(admin_context, pr2)
        pr3 = self._make_pr_dict(name="list_pr3")
        pr_ret3 = plugin.create_policy_rule(admin_context, pr3)

        pr_list_ret = plugin.get_policy_rules(admin_context)
        self.assertItemsEqual(pr_list_ret, [pr_ret1, pr_ret2, pr_ret3])

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
                      src_grp=None, dst_grp=None, action="allow",
                      protocol="any", src_port_range=None,
                      dst_port_range=None, tag=None):
        return {"policy_rule": {
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
