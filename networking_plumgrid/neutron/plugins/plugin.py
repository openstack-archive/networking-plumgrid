# Copyright 2015 PLUMgrid, Inc. All Rights Reserved.
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
Neutron Plug-in for PLUMgrid Open Networking Suite
"""

import netaddr
from oslo_config import cfg
from oslo_log import log as logging
from oslo_utils import importutils
from oslo_utils import uuidutils
from six import string_types
from sqlalchemy.orm import exc as sa_exc

import networking_plumgrid
from networking_plumgrid._i18n import _
from networking_plumgrid._i18n import _LI, _LW
from networking_plumgrid.neutron.plugins.common import constants as \
    net_pg_const
from networking_plumgrid.neutron.plugins.common.locking import lock as pg_lock
from networking_plumgrid.neutron.plugins.common import pg_helper
from networking_plumgrid.neutron.plugins.db.physical_attachment_point import \
    physical_attachment_point_db as pap_db
from networking_plumgrid.neutron.plugins.db.sqlal import api as db_api
from networking_plumgrid.neutron.plugins.db.transitdomain import \
    transitdomain as tvd_db
from networking_plumgrid.neutron.plugins.extensions import \
    transitdomain as ext_tvd

from functools import wraps
from networking_plumgrid.neutron.plugins.common import exceptions as plum_excep
from networking_plumgrid.neutron.plugins.db.l2gateway import (l2gateway_db
    as l2gw_db)
from networking_plumgrid.neutron.plugins.db import pgdb
from networking_plumgrid.neutron.plugins.extensions import portbindings\
    as p_portbindings
from networking_plumgrid.neutron.plugins import plugin_ver
from neutron.api import extensions as n_ext
from neutron.api.v2 import attributes
from neutron.common import constants
from neutron.common import exceptions as n_exc
from neutron.common import utils
from neutron.db import agents_db
from neutron.db import db_base_plugin_v2
from neutron.db import external_net_db
from neutron.db import extraroute_db
from neutron.db import l3_db
from neutron.db import portbindings_db
from neutron.db import quota_db  # noqa
from neutron.db import securitygroups_db
from neutron.extensions import portbindings
from neutron.extensions import providernet as provider
from neutron.extensions import securitygroup as sec_grp
from neutron.plugins.common import constants as svc_constants
from neutron.plugins.common import utils as svc_utils

LOG = logging.getLogger(__name__)

director_server_opts = [
    cfg.StrOpt('director_server', default='localhost',
               help=_("PLUMgrid Director server to connect to")),
    cfg.IntOpt('director_server_port', default='8080',
               help=_("PLUMgrid Director server port to connect to")),
    cfg.StrOpt('username', default='username',
               help=_("PLUMgrid Director admin username")),
    cfg.StrOpt('password', default='password', secret=True,
               help=_("PLUMgrid Director admin password")),
    cfg.IntOpt('servertimeout', default=5,
               help=_("PLUMgrid Director server timeout")),
    cfg.BoolOpt('distributed_locking', default=True,
               help=_("Distributed locking is enabled or disabled")),
    cfg.StrOpt('driver',
               default="networking_plumgrid.neutron.plugins.drivers.plumlib."
                       "Plumlib",
               help=_("PLUMgrid Driver"))]

l2_gateway_opts = [
    cfg.StrOpt('vendor', default='vendor',
               help=_("L2 Gateway Vendor Type")),
    cfg.StrOpt('sw_username',
               help=_("Username of VTEP device")),
    cfg.StrOpt('sw_password',
               help=_("Password of VTEP device"))]

cfg.CONF.register_opts(director_server_opts, "plumgriddirector")
cfg.CONF.register_opts(l2_gateway_opts, "l2gateway")
ds_lock = cfg.CONF.plumgriddirector.distributed_locking


def pgl(fn):
    """pg_lock decorator"""

    @wraps(fn)
    def locker(*args, **kwargs):
        if ds_lock:
            if args[-1] is not None:
                lock = pg_lock.PGLock(args[1], args[-1], ds_lock)
                with lock.thread_lock(args[-1]):
                    try:
                        return fn(*args, **kwargs)
                    finally:
                        lock.release(args[-1])
        else:
            return fn(*args, **kwargs)
    return locker


class NeutronPluginPLUMgridV2(agents_db.AgentDbMixin,
                              db_base_plugin_v2.NeutronDbPluginV2,
                              external_net_db.External_net_db_mixin,
                              extraroute_db.ExtraRoute_db_mixin,
                              l3_db.L3_NAT_db_mixin,
                              portbindings_db.PortBindingMixin,
                              securitygroups_db.SecurityGroupDbMixin,
                              pap_db.PhysicalAttachmentPointDb,
                              tvd_db.TransitDomainDBMixin,
                              l2gw_db.L2GatewayMixin):

    supported_extension_aliases = ["agent", "binding", "external-net",
                                   "extraroute", "provider", "quotas",
                                   "router", "security-group", "l2-gateway",
                                   "l2-gateway-connection",
                                   "physical-attachment-point",
                                   "subnet_allocation",
                                   "transit-domain"]

    binding_view = "extension:port_binding:view"
    binding_set = "extension:port_binding:set"

    def __init__(self):
        LOG.info(_LI('networking-plumgrid: Starting Plugin'))

        n_ext.append_api_extensions_path(
                      networking_plumgrid.neutron.plugins.extensions.__path__)
        super(NeutronPluginPLUMgridV2, self).__init__()
        self.plumgrid_init()
        db_api.create_table_pg_lock()

        LOG.debug('networking-plumgrid: Neutron server with '
                  'PLUMgrid Plugin has started')

    db_base_plugin_v2.NeutronDbPluginV2.register_dict_extend_funcs(
        attributes.NETWORKS, ['_extend_network_dict_provider_pg'])

    def plumgrid_init(self):
        """PLUMgrid initialization."""
        director_plumgrid = cfg.CONF.plumgriddirector.director_server
        director_port = cfg.CONF.plumgriddirector.director_server_port
        director_admin = cfg.CONF.plumgriddirector.username
        director_password = cfg.CONF.plumgriddirector.password
        timeout = cfg.CONF.plumgriddirector.servertimeout
        plum_driver = cfg.CONF.plumgriddirector.driver

        # PLUMgrid Director(s) info validation
        LOG.info(_LI('networking-plumgrid: %s'), director_plumgrid)
        self._plumlib = importutils.import_object(plum_driver)
        self._plumlib.director_conn(director_plumgrid, director_port, timeout,
                                    director_admin, director_password)

    def create_network(self, context, network):
        """Create Neutron network
        """

        LOG.debug('networking-plumgrid: create_network() called')

        # Process network attributes for consistency
        self._process_network_db(network)
        (network_type, physical_network,
         segmentation_id) = self._process_provider_create(context,
                                                          network['network'])

        # Plugin DB - Network Create and validation
        tenant_id = network["network"]["tenant_id"]
        self._network_admin_state(network)
        self._ensure_default_security_group(context, tenant_id)
        return self._create_network_pg(context, network, network_type,
                                       physical_network, segmentation_id,
                                       tenant_id)

    @pgl
    def _create_network_pg(self, context, network, network_type,
                           physical_network, segmentation_id, tenant_id):
        transit_domain_id = None
        with context.session.begin(subtransactions=True):
            try:
                pap_dict = None
                pdb = None
                net_db = super(NeutronPluginPLUMgridV2,
                               self).create_network(context, network)
                binding = None
                self._process_l3_create(context, net_db, network['network'])

                if network_type and network_type != net_pg_const.LOCAL:
                    pass
                elif ('router:external' in network['network'] and
                      network['network']['router:external']):
                    hostname, ifc = self._plumlib.get_available_interface()
                    # create pap
                    pap_dict = {"physical_attachment_point": {
                                    "name": net_db["name"],
                                    "lacp": False,
                                    "hash_mode": "L2",
                                    "tenant_id": net_db["tenant_id"],
                                    "implicit": True,
                                    "interfaces":
                                    [{"hostname": hostname,
                                      "interface": ifc}]}}
                    pdb = self.create_physical_attachment_point(context,
                                                                pap_dict)
                    network_type = "FLAT"
                    physical_network = pdb["id"]
                if network_type:
                    binding = pgdb.add_network_binding(context.session,
                                                       net_db['id'],
                                                       str(network_type),
                                                       str(physical_network),
                                                       segmentation_id)
                    if network_type.lower() == net_pg_const.L3_GATEWAY_NET:
                        try:
                            super(NeutronPluginPLUMgridV2,
                                  self).get_transit_domain(context,
                                  network["network"]
                                  ["provider:physical_network"],
                                  fields=None)
                        except ext_tvd.NoTransitDomainFound:
                            raise
                    else:
                        papdb = super(NeutronPluginPLUMgridV2,
                                      self).get_physical_attachment_point(
                                      context, physical_network)
                        transit_domain_id = papdb["transit_domain_id"]
                        (network["network"]
                        ["provider:physical_network"]) = str(physical_network)
                        (network["network"]
                        ["provider:network_type"]) = str(network_type)
                self._extend_network_dict_provider_pg(net_db, None, binding)

                LOG.debug('PLUMgrid Library: create_network() called')
                self._plumlib.create_network(tenant_id, net_db, network,
                    transit_domain_id=transit_domain_id)

            except Exception as err_message:
                if ('router:external' in network["network"] and
                    network["network"]['router:external']):
                    if pap_dict and pdb:
                        self.delete_physical_attachment_point(context,
                                                              pdb["id"])
                raise plum_excep.PLUMgridException(err_msg=err_message)

        # Return created network
        return net_db

    def update_network(self, context, net_id, network):
        """Update Neutron network.
        """

        LOG.debug("networking-plumgrid: update_network() called")
        self._network_admin_state(network)
        net_db = super(NeutronPluginPLUMgridV2,
                       self).get_network(context, net_id)
        tenant_id = net_db["tenant_id"]
        return self._update_network_pg(context, net_id, network, net_db,
                                       tenant_id)

    @pgl
    def _update_network_pg(self, context, net_id, network, orig_net_db,
                           tenant_id):
        with context.session.begin(subtransactions=True):
            # Plugin DB - Network Update
            net_db = super(
                NeutronPluginPLUMgridV2, self).update_network(context,
                                                              net_id, network)
            self._process_l3_update(context, net_db, network['network'])

            try:
                LOG.debug("PLUMgrid Library: update_network() called")
                self._plumlib.update_network(tenant_id, net_id, network,
                                             orig_net_db)

            except Exception as err_message:
                raise plum_excep.PLUMgridException(err_msg=err_message)

        # Return updated network
        return net_db

    def delete_network(self, context, net_id):
        """Delete Neutron network.

        Deletes a PLUMgrid-based bridge.
        """

        LOG.debug("networking-plumgrid: delete_network() called")
        net_db = super(NeutronPluginPLUMgridV2,
                       self).get_network(context, net_id)
        tenant_id = net_db["tenant_id"]
        self._delete_network_pg(context, net_id, net_db, tenant_id)
        if net_db.get("provider:physical_network"):
            if (net_db.get("provider:network_type").lower() !=
                net_pg_const.L3_GATEWAY_NET):
                pap_id = net_db["provider:physical_network"]
                pap_db = super(NeutronPluginPLUMgridV2,
                         self).get_physical_attachment_point(context, pap_id,
                                                             fields=None)
                if pap_db.get("implicit"):
                    self.delete_physical_attachment_point(context, pap_id)

    def _delete_network_pg(self, context, net_id, net_db, tenant_id):

        with context.session.begin(subtransactions=True):
            self._process_l3_delete(context, net_id)
            # Plugin DB - Network Delete
            super(NeutronPluginPLUMgridV2, self).delete_network(context,
                                                                net_id)
            lock = pg_lock.PGLock(context, tenant_id, ds_lock)
            with lock.thread_lock(tenant_id):
                try:
                    LOG.debug("PLUMgrid Library: delete_network() called")
                    self._plumlib.delete_network(net_db, net_id)

                except Exception as err_message:
                    raise plum_excep.PLUMgridException(err_msg=err_message)
                finally:
                    lock.release(tenant_id)

    @utils.synchronized('net-pg', external=True)
    def create_port(self, context, port):
        """Create Neutron port.

        Creates a PLUMgrid-based port on the specific Virtual Network
        Function (VNF).
        """
        LOG.debug("networking-plumgrid: create_port() called")

        # Port operations on PLUMgrid are through the
        # VIF driver operations in Nova.
        # It requires admin_state_up to be True

        port["port"]["admin_state_up"] = True
        port_data = port["port"]
        tenant_id = port_data["tenant_id"]
        self._ensure_default_security_group_on_port(context, port)
        return self._create_port_pg(context, port, port_data, tenant_id)

    def _create_port_pg(self, context, port, port_data, tenant_id):
        if ("device_owner" in port_data and
            port_data["device_owner"] == constants.DEVICE_OWNER_ROUTER_GW):
            lo = pg_lock.GL
        else:
            lo = tenant_id
        lock = pg_lock.PGLock(context, lo, ds_lock)
        with lock.thread_lock(lo):
            try:
                with context.session.begin(subtransactions=True):
                    # Plugin DB - Port Create and Return port
                    port_db = super(NeutronPluginPLUMgridV2,
                                    self).create_port(context, port)
                    # Update port security
                    port_data.update(port_db)

                    port_data[sec_grp.SECURITYGROUPS] = (
                        self._get_security_groups_on_port(context, port))

                    self._process_port_create_security_group(
                        context, port_db, port_data[sec_grp.SECURITYGROUPS])

                    self._process_portbindings_create_and_update(context,
                                                                 port_data,
                                                                 port_db)

                    device_id = port_db["device_id"]
                    if (port_db["device_owner"] ==
                        constants.DEVICE_OWNER_ROUTER_GW):
                        router_db = self._get_router(context, device_id)
                    else:
                        router_db = None

                    # Retrieve subnet information
                    subnet_db = pg_helper._retrieve_subnet_dict(self, port_db,
                                                                context)
                    try:
                        LOG.debug("PLUMgrid Library: create_port() called")
                        self._plumlib.create_port(port_db, router_db,
                                                  subnet_db)

                    except Exception as err:
                        raise plum_excep.PLUMgridException(err_msg=err)

                # Plugin DB - Port Create and Return port
                return self._port_viftype_binding(context, port_db)
            finally:
                lock.release(lo)

    @utils.synchronized('net-pg', external=True)
    def update_port(self, context, port_id, port):
        """Update Neutron port.

        Updates a PLUMgrid-based port on the specific Virtual Network
        Function (VNF).
        """
        LOG.debug("networking-plumgrid: update_port() called")
        port_get = super(NeutronPluginPLUMgridV2,
                         self).get_port(context, port_id)
        tenant_id = port_get["tenant_id"]
        return self._update_port_pg(context, port_id, port, port_get,
                                    tenant_id)

    def _update_port_pg(self, context, port_id, port, port_get, tenant_id):
        if ("device_owner" in port_get and
            port_get["device_owner"] == constants.DEVICE_OWNER_ROUTER_GW):
            lo = pg_lock.GL
        else:
            lo = tenant_id
        lock = pg_lock.PGLock(context, lo, ds_lock)
        with lock.thread_lock(lo):
            try:
                with context.session.begin(subtransactions=True):
                    # Plugin DB - Port Create and Return port
                    port_db = super(NeutronPluginPLUMgridV2, self).update_port(
                        context, port_id, port)
                    device_id = port_db["device_id"]
                    if (port_db["device_owner"] ==
                        constants.DEVICE_OWNER_ROUTER_GW):
                        router_db = self._get_router(context, device_id)
                    else:
                        router_db = None

                    if (self._check_update_deletes_security_groups(port) or
                            self._check_update_has_security_groups(port)):
                        self._delete_port_security_group_bindings(
                            context, port_db["id"])
                        sg_ids = self._get_security_groups_on_port(context,
                                                                   port)
                        self._process_port_create_security_group(context,
                                                                 port_db,
                                                                 sg_ids)

                    self._process_portbindings_create_and_update(context,
                                                                 port['port'],
                                                                 port_db)

                    # Retrieve subnet information
                    subnet_db = pg_helper._retrieve_subnet_dict(self, port_db,
                                                                context)
                    try:
                        LOG.debug("PLUMgrid Library: create_port() called")
                        self._plumlib.update_port(port_db, router_db,
                                                  subnet_db)

                    except Exception as err:
                        raise plum_excep.PLUMgridException(err_msg=err)

                # Plugin DB - Port Update
                return self._port_viftype_binding(context, port_db)
            finally:
                lock.release(lo)

    @utils.synchronized('net-pg', external=True)
    def delete_port(self, context, port_id, l3_port_check=True):
        """Delete Neutron port.

        Deletes a PLUMgrid-based port on the specific Virtual Network
        Function (VNF).
        """

        LOG.debug("networking-plumgrid: delete_port() called")

        port_db = super(NeutronPluginPLUMgridV2,
                        self).get_port(context, port_id)
        tenant_id = port_db["tenant_id"]
        self._delete_port_pg(context, port_id, port_db, l3_port_check,
                             tenant_id)

    def _delete_port_pg(self, context, port_id, port_db, l3_port_check,
                        tenant_id):
        if ("device_owner" in port_db and
            port_db["device_owner"] == constants.DEVICE_OWNER_ROUTER_GW):
            lo = pg_lock.GL
        else:
            lo = tenant_id
        lock = pg_lock.PGLock(context, lo, ds_lock)
        with lock.thread_lock(lo):
            try:
                with context.session.begin(subtransactions=True):
                    router_ids = self.disassociate_floatingips(
                        context, port_id, do_notify=False)
                    super(NeutronPluginPLUMgridV2, self).delete_port(context,
                                                                     port_id)

                    if (port_db["device_owner"] ==
                        constants.DEVICE_OWNER_ROUTER_GW):
                        device_id = port_db["device_id"]
                        router_db = self._get_router(context, device_id)
                    else:
                        router_db = None
                    try:
                        LOG.debug("PLUMgrid Library: delete_port() called")
                        self._plumlib.delete_port(port_db, router_db)

                    except Exception as err:
                        raise plum_excep.PLUMgridException(err_msg=err)

                # now that we've left db transaction, we are safe to notify
                self.notify_routers_updated(context, router_ids)
            finally:
                lock.release(lo)

    def get_port(self, context, id, fields=None):
        with context.session.begin(subtransactions=True):
            port_db = super(NeutronPluginPLUMgridV2,
                            self).get_port(context, id, fields)

            self._port_viftype_binding(context, port_db)
        return self._fields(port_db, fields)

    def get_ports(self, context, filters=None, fields=None):
        with context.session.begin(subtransactions=True):
            ports_db = super(NeutronPluginPLUMgridV2,
                             self).get_ports(context, filters, fields)
            for port_db in ports_db:
                self._port_viftype_binding(context, port_db)
        return [self._fields(port, fields) for port in ports_db]

    def create_subnet(self, context, subnet):
        """Create Neutron subnet.

        Creates a PLUMgrid-based DHCP and NAT Virtual Network
        Functions (VNFs).
        """

        LOG.debug("networking-plumgrid: create_subnet() called")
        net_db = super(NeutronPluginPLUMgridV2, self).get_network(
                       context, subnet['subnet']['network_id'], fields=None)
        tenant_id = net_db["tenant_id"]
        return self._create_subnet_pg(context, subnet, net_db, tenant_id)

    @pgl
    def _create_subnet_pg(self, context, subnet, net_db, tenant_id):
        with context.session.begin(subtransactions=True):
            # Plugin DB - Subnet Create
            s = subnet['subnet']
            ipnet = None
            if self._validate_network(s['cidr']):
                ipnet = netaddr.IPNetwork(s['cidr'])
                # PLUMgrid reserves the last IP address for GW
                # when is not defined
                if (s['gateway_ip'] is attributes.ATTR_NOT_SPECIFIED and
                    s['allocation_pools'] is attributes.ATTR_NOT_SPECIFIED):
                    gw_ip = str(netaddr.IPAddress(ipnet.last - 1))
                    ip = netaddr.IPAddress(gw_ip)
                    if (ip.version == 4 or
                       (ip.version == 6 and not ip.is_link_local())):
                        if (ip != ipnet.network and
                            ip != ipnet.broadcast and
                            ipnet.netmask & ip == ipnet.network):
                            subnet['subnet']['gateway_ip'] = gw_ip

                if (s['gateway_ip'] is attributes.ATTR_NOT_SPECIFIED and
                    s['allocation_pools'] != attributes.ATTR_NOT_SPECIFIED):
                    if (subnet['subnet']['allocation_pools'][0]['start'] !=
                        subnet['subnet']['allocation_pools'][0]['end']):
                        gw_ip = str(netaddr.IPAddress(ipnet.last - 1))
                        ip = netaddr.IPAddress(gw_ip)
                        pool_start = s['allocation_pools'][0]['start']
                        pool_end = s['allocation_pools'][0]['end']
                        allocation_range = netaddr.IPRange(pool_start,
                                                           pool_end)
                        if (ip.version == 4 or
                           (ip.version == 6 and not ip.is_link_local())):
                            if (ip != ipnet.network and
                                ip != ipnet.broadcast and
                                ipnet.netmask & ip == ipnet.network):
                                if gw_ip not in allocation_range:
                                    subnet['subnet']['gateway_ip'] = gw_ip

                # PLUMgrid reserves the first IP
                if s['allocation_pools'] == attributes.ATTR_NOT_SPECIFIED:
                    allocation_pool = self._allocate_pools_for_subnet(context,
                                                                      s)
                    subnet['subnet']['allocation_pools'] = allocation_pool

            sub_db = super(NeutronPluginPLUMgridV2, self).create_subnet(
                context, subnet)
            try:
                if not ipnet:
                    ipnet = netaddr.IPNetwork(sub_db['cidr'])
                LOG.debug("PLUMgrid Library: create_subnet() called")
                self._plumlib.create_subnet(sub_db, net_db, ipnet)
            except Exception as err_message:
                raise plum_excep.PLUMgridException(err_msg=err_message)

        return sub_db

    def delete_subnet(self, context, subnet_id):
        """Delete subnet core Neutron API."""

        LOG.debug("networking-plumgrid: delete_subnet() called")
        # Collecting subnet info
        sub_db = self._get_subnet(context, subnet_id)
        net_id = sub_db["network_id"]
        net_db = self.get_network(context, net_id)
        tenant_id = net_db["tenant_id"]
        self._delete_subnet_pg(context, subnet_id, net_db, net_id, sub_db,
                               tenant_id)

    @pgl
    def _delete_subnet_pg(self, context, subnet_id, net_db, net_id, sub_db,
                          tenant_id):

        with context.session.begin(subtransactions=True):
            # Plugin DB - Subnet Delete
            super(NeutronPluginPLUMgridV2, self).delete_subnet(
                context, subnet_id)
            try:
                LOG.debug("PLUMgrid Library: delete_subnet() called")
                self._plumlib.delete_subnet(tenant_id, net_db, net_id, sub_db)
            except Exception as err_message:
                raise plum_excep.PLUMgridException(err_msg=err_message)

    def update_subnet(self, context, subnet_id, subnet):
        """Update subnet core Neutron API."""

        LOG.debug("update_subnet() called")
        # Collecting subnet info
        orig_sub_db = self._get_subnet(context, subnet_id)
        tenant_id = orig_sub_db["tenant_id"]
        net_id = orig_sub_db["network_id"]
        net_db = self.get_network(context, net_id)
        return self._update_subnet_pg(context, subnet_id, subnet, orig_sub_db,
                                      net_db, tenant_id)

    @pgl
    def _update_subnet_pg(self, context, subnet_id, subnet, orig_sub_db,
                          net_db, tenant_id):
        with context.session.begin(subtransactions=True):
            # Plugin DB - Subnet Update
            new_sub_db = super(NeutronPluginPLUMgridV2,
                               self).update_subnet(context, subnet_id, subnet)
            ipnet = netaddr.IPNetwork(new_sub_db['cidr'])

            try:
                LOG.debug("PLUMgrid Library: update_subnet() called")
                self._plumlib.update_subnet(orig_sub_db, new_sub_db, ipnet,
                                            net_db)

            except Exception as err_message:
                raise plum_excep.PLUMgridException(err_msg=err_message)

        return new_sub_db

    def create_router(self, context, router):
        LOG.debug("networking-plumgrid: create_router() called")

        tenant_id = self._get_tenant_id_for_create(context, router["router"])
        return self._create_router_pg(context, router, tenant_id)

    @pgl
    def _create_router_pg(self, context, router, tenant_id):

        with context.session.begin(subtransactions=True):

            # Create router in DB
            router_db = super(NeutronPluginPLUMgridV2,
                              self).create_router(context, router)
            # Create router on the network controller
            try:
                # Add Router to VND
                LOG.debug("PLUMgrid Library: create_router() called")
                self._plumlib.create_router(tenant_id, router_db)
            except Exception as err_message:
                raise plum_excep.PLUMgridException(err_msg=err_message)

        # Return created router
        return router_db

    def update_router(self, context, router_id, router):

        LOG.debug("networking-plumgrid: update_router() called")
        orig_router = self._get_router(context, router_id)
        tenant_id = orig_router["tenant_id"]
        return self._update_router_pg(context, router_id, router, tenant_id)

    @pgl
    def _update_router_pg(self, context, router_id, router, tenant_id):
        with context.session.begin(subtransactions=True):
            router_db = super(NeutronPluginPLUMgridV2,
                              self).update_router(context, router_id, router)
            try:
                LOG.debug("PLUMgrid Library: update_router() called")
                self._plumlib.update_router(router_db, router_id)
            except Exception as err_message:
                raise plum_excep.PLUMgridException(err_msg=err_message)

        # Return updated router
        return router_db

    def delete_router(self, context, router_id):
        LOG.debug("networking-plumgrid: delete_router() called")

        orig_router = self._get_router(context, router_id)
        tenant_id = orig_router["tenant_id"]
        self._delete_router_pg(context, router_id, tenant_id)

    @pgl
    def _delete_router_pg(self, context, router_id, tenant_id):
        with context.session.begin(subtransactions=True):
            router = self._ensure_router_not_in_use(context, router_id)
            router_ports = router.attached_ports.all()
            # Set the router's gw_port to None to avoid a constraint violation.
            router.gw_port = None
            for rp in router_ports:
                self.delete_port(context.elevated(), rp.port.id)
            super(NeutronPluginPLUMgridV2, self).delete_router(context,
                                                               router_id)

            try:
                LOG.debug("PLUMgrid Library: delete_router() called")
                self._plumlib.delete_router(tenant_id, router_id)

            except Exception as err_message:
                raise plum_excep.PLUMgridException(err_msg=err_message)

    def add_router_interface(self, context, router_id, interface_info):

        LOG.debug("networking-plumgrid: "
                  "add_router_interface() called")
        router_db = self._get_router(context, router_id)
        tenant_id = router_db['tenant_id']
        return self._update_router_interface_pg(context, router_id,
                                                interface_info, router_db,
                                                tenant_id)

    def _update_router_interface_pg(self, context, router_id, interface_info,
                                    router_db, tenant_id):
        with context.session.begin(subtransactions=True):
            # Create interface in DB
            int_router = super(NeutronPluginPLUMgridV2,
                               self).add_router_interface(context,
                                                          router_id,
                                                          interface_info)
            lock = pg_lock.PGLock(context, tenant_id, ds_lock)
            with lock.thread_lock(tenant_id):
                try:
                    port_db = self._get_port(context, int_router['port_id'])
                    subnet_id = port_db["fixed_ips"][0]["subnet_id"]
                    subnet_db = super(NeutronPluginPLUMgridV2,
                                      self)._get_subnet(context, subnet_id)
                    ipnet = netaddr.IPNetwork(subnet_db['cidr'])
                    ip_version = subnet_db['ip_version']

                    # Create interface on the network controller
                    LOG.debug("PLUMgrid Library: add_router_interface called")
                    self._plumlib.add_router_interface(tenant_id, router_id,
                                                       port_db, ipnet,
                                                       ip_version)

                except Exception as err_message:
                    raise plum_excep.PLUMgridException(err_msg=err_message)

                finally:
                    lock.release(tenant_id)

        return int_router

    def remove_router_interface(self, context, router_id, int_info):

        LOG.debug("networking-plumgrid: remove_router_interface() called")
        router_db = self._get_router(context, router_id)
        tenant_id = router_db['tenant_id']
        return self._remove_router_interface_pg(context, router_id, int_info,
                                                router_db, tenant_id)

    def _remove_router_interface_pg(self, context, router_id, int_info,
                                    router_db, tenant_id):

        with context.session.begin(subtransactions=True):
            if 'port_id' in int_info:
                port = self._get_port(context, int_info['port_id'])
                net_id = port['network_id']

            elif 'subnet_id' in int_info:
                subnet_id = int_info['subnet_id']
                subnet = self._get_subnet(context, subnet_id)
                net_id = subnet['network_id']

            # Remove router in DB
            del_int_router = super(NeutronPluginPLUMgridV2,
                                   self).remove_router_interface(context,
                                                                 router_id,
                                                                 int_info)
            lock = pg_lock.PGLock(context, tenant_id, ds_lock)
            with lock.thread_lock(tenant_id):
                try:
                    LOG.debug("PLUMgrid Library: "
                              "remove_router_interface() called")
                    self._plumlib.remove_router_interface(tenant_id,
                                                          net_id, router_id)

                except Exception as err_message:
                    raise plum_excep.PLUMgridException(err_msg=err_message)

                finally:
                    lock.release(tenant_id)

        return del_int_router

    def create_floatingip(self, context, floatingip):
        LOG.debug("networking-plumgrid: create_floatingip() called")
        tenant_id = floatingip["floatingip"]["tenant_id"]
        return self._create_floatingip_pg(context, floatingip, tenant_id)

    @pgl
    def _create_floatingip_pg(self, context, floatingip, tenant_id):
        try:
            floating_ip = super(NeutronPluginPLUMgridV2,
                                self).create_floatingip(context, floatingip)
            LOG.debug("PLUMgrid Library: create_floatingip() called")
            self._plumlib.create_floatingip(floating_ip)
            return floating_ip

        except Exception as err_message:
            if floating_ip is not None:
                self.delete_floatingip(context, floating_ip["id"])
            raise plum_excep.PLUMgridException(err_msg=err_message)

    def update_floatingip(self, context, id, floatingip):
        LOG.debug("networking-plumgrid: update_floatingip() called")

        floating_ip_orig = super(NeutronPluginPLUMgridV2,
                                 self).get_floatingip(context, id)
        tenant_id = floating_ip_orig["tenant_id"]
        return self._update_floatingip_pg(context, id, floatingip,
                                          floating_ip_orig, tenant_id)

    @pgl
    def _update_floatingip_pg(self, context, id, floatingip, floating_ip_orig,
                              tenant_id):
        try:
            floating_ip = super(NeutronPluginPLUMgridV2,
                                self).update_floatingip(context, id,
                                                        floatingip)
            # Update status based on association
            if floating_ip.get('port_id') is None:
                floating_ip['status'] = constants.FLOATINGIP_STATUS_DOWN
            else:
                floating_ip['status'] = constants.FLOATINGIP_STATUS_ACTIVE
            self.update_floatingip_status(context, id, floating_ip['status'])
            LOG.debug("PLUMgrid Library: update_floatingip() called")
            self._plumlib.update_floatingip(floating_ip_orig, floating_ip, id)

            return floating_ip

        except Exception as err_message:
            if floatingip['floatingip']['port_id']:
                self.disassociate_floatingips(context,
                                              floatingip['floatingip']
                                              ['port_id'],
                                              do_notify=False)
            raise plum_excep.PLUMgridException(err_msg=err_message)

    def delete_floatingip(self, context, id):
        LOG.debug("networking-plumgrid: delete_floatingip() called")
        floating_ip_orig = super(NeutronPluginPLUMgridV2,
                                 self).get_floatingip(context, id)
        tenant_id = floating_ip_orig["tenant_id"]
        self._delete_floatingip_pg(context, id, floating_ip_orig,
                                   tenant_id)

    @pgl
    def _delete_floatingip_pg(self, context, id, floating_ip_orig, tenant_id):
        try:
            LOG.debug("PLUMgrid Library: delete_floatingip() called")
            self._plumlib.delete_floatingip(floating_ip_orig, id)

        except Exception as err_message:
            raise plum_excep.PLUMgridException(err_msg=err_message)
        super(NeutronPluginPLUMgridV2, self).delete_floatingip(context, id)

    def disassociate_floatingips(self, context, port_id, do_notify=True):
        LOG.debug("networking-plumgrid: disassociate_floatingips() "
                  "called")

        try:
            fip_qry = context.session.query(l3_db.FloatingIP)
            floating_ip = fip_qry.filter_by(fixed_port_id=port_id).one()

            LOG.debug("PLUMgrid Library: disassociate_floatingips()"
                      " called")
            self._plumlib.disassociate_floatingips(floating_ip, port_id)

        except sa_exc.NoResultFound:
            pass

        except Exception as err_message:
            raise plum_excep.PLUMgridException(err_msg=err_message)

        return (super(NeutronPluginPLUMgridV2,
                self).disassociate_floatingips(
                context, port_id, do_notify=do_notify))

    def create_security_group(self, context, security_group, default_sg=False):
        """Create a security group

        Create a new security group, including the default security group
        """
        LOG.debug("networking-plumgrid: create_security_group()"
                  " called")
        sg = security_group.get('security_group')

        tenant_id = self._get_tenant_id_for_create(context, sg)
        if not default_sg:
            self._ensure_default_security_group(context, tenant_id)
        return self._create_security_group_pg(context, security_group, sg,
                                              default_sg, tenant_id)

    @pgl
    def _create_security_group_pg(self, context, security_group, sg,
                                  default_sg, tenant_id):
        with context.session.begin(subtransactions=True):
            sg_db = super(NeutronPluginPLUMgridV2,
                          self).create_security_group(context, security_group,
                                                      default_sg)
            try:
                LOG.debug("PLUMgrid Library: create_security_group()"
                          " called")
                self._plumlib.create_security_group(sg_db)

            except Exception as err_message:
                raise plum_excep.PLUMgridException(err_msg=err_message)

        return sg_db

    def update_security_group(self, context, sg_id, security_group):
        """Update a security group

        Update security group name/description in Neutron and PLUMgrid
        platform
        """
        sg = super(NeutronPluginPLUMgridV2, self).get_security_group(context,
                                                                     sg_id)
        tenant_id = sg["tenant_id"]
        return self._update_security_group_pg(context, sg_id, security_group,
                                              tenant_id)

    @pgl
    def _update_security_group_pg(self, context, sg_id, security_group,
                                  tenant_id):
        with context.session.begin(subtransactions=True):
            sg_db = (super(NeutronPluginPLUMgridV2,
                           self).update_security_group(context,
                                                       sg_id,
                                                       security_group))
            if ('name' in security_group['security_group'] and
                    sg_db['name'] != 'default'):
                try:
                    LOG.debug("PLUMgrid Library: update_security_group()"
                              " called")
                    self._plumlib.update_security_group(sg_db)

                except Exception as err_message:
                    raise plum_excep.PLUMgridException(err_msg=err_message)
            return sg_db

    def delete_security_group(self, context, sg_id):
        """Delete a security group

        Delete security group from Neutron and PLUMgrid Platform

        :param sg_id: security group ID of the rule to be removed
        """
        sg = super(NeutronPluginPLUMgridV2, self).get_security_group(
             context, sg_id)
        if not sg:
            raise sec_grp.SecurityGroupNotFound(id=sg_id)

        if sg['name'] == 'default' and not context.is_admin:
            raise sec_grp.SecurityGroupCannotRemoveDefault()

        tenant_id = sg["tenant_id"]
        self._delete_security_group_pg(context, sg_id, sg, tenant_id)

    @pgl
    def _delete_security_group_pg(self, context, sg_id, sg, tenant_id):
        with context.session.begin(subtransactions=True):

            sec_grp_ip = sg['id']
            filters = {'security_group_id': [sec_grp_ip]}
            if super(NeutronPluginPLUMgridV2,
                     self)._get_port_security_group_bindings(context,
                                                             filters):
                raise sec_grp.SecurityGroupInUse(id=sec_grp_ip)

            sec_db = super(NeutronPluginPLUMgridV2,
                           self).delete_security_group(context, sg_id)
            try:
                LOG.debug("PLUMgrid Library: delete_security_group()"
                          " called")
                self._plumlib.delete_security_group(sg)

            except Exception as err_message:
                raise plum_excep.PLUMgridException(err_msg=err_message)

            return sec_db

    def create_security_group_rule(self, context, security_group_rule):
        """Create a security group rule

        Create a security group rule in Neutron and PLUMgrid Platform
        """
        LOG.debug("networking-plumgrid: create_security_group_rule()"
                  " called")
        bulk_rule = {'security_group_rules': [security_group_rule]}
        return self.create_security_group_rule_bulk(context, bulk_rule)[0]

    def create_security_group_rule_bulk(self, context, security_group_rule):
        """Create security group rules

        Create security group rules in Neutron and PLUMgrid Platform

        :param security_group_rule: list of rules to create
        """
        sg_rules = security_group_rule.get('security_group_rules')
        sg_id = (super(NeutronPluginPLUMgridV2,
                 self)._validate_security_group_rules(
                 context, security_group_rule))

        # Check to make sure security group exists
        security_group = super(NeutronPluginPLUMgridV2,
                               self).get_security_group(context,
                                                        sg_id)

        if not security_group:
            raise sec_grp.SecurityGroupNotFound(id=sg_id)

        # Check for duplicate rules
        self._check_for_duplicate_rules(context, sg_rules)
        tenant_id = security_group["tenant_id"]
        return self._create_security_group_rule_bulk_pg(context,
                                                        security_group_rule,
                                                        sg_rules,
                                                        tenant_id)

    @pgl
    def _create_security_group_rule_bulk_pg(self, context, security_group_rule,
                                            sg_rules, tenant_id):
        with context.session.begin(subtransactions=True):
            sec_db = (super(NeutronPluginPLUMgridV2,
                            self).create_security_group_rule_bulk_native(
                      context, security_group_rule))
            try:
                LOG.debug("PLUMgrid Library: create_security_"
                          "group_rule_bulk() called")
                self._plumlib.create_security_group_rule_bulk(sec_db)

            except Exception as err_message:
                raise plum_excep.PLUMgridException(err_msg=err_message)

            return sec_db

    def delete_security_group_rule(self, context, sgr_id):
        """Delete a security group rule

        Delete a security group rule in Neutron and PLUMgrid Platform
        """

        LOG.debug("networking-plumgrid: delete_security_group_rule()"
                  " called")

        sgr = (super(NeutronPluginPLUMgridV2,
                     self).get_security_group_rule(context, sgr_id))

        if not sgr:
            raise sec_grp.SecurityGroupRuleNotFound(id=sgr_id)
        tenant_id = sgr["tenant_id"]
        self._delete_security_group_rule_pg(context, sgr_id, sgr, tenant_id)

    @pgl
    def _delete_security_group_rule_pg(self, context, sgr_id, sgr, tenant_id):

        super(NeutronPluginPLUMgridV2,
              self).delete_security_group_rule(context, sgr_id)
        try:
            LOG.debug("PLUMgrid Library: delete_security_"
                      "group_rule() called")
            self._plumlib.delete_security_group_rule(sgr)

        except Exception as err_message:
            raise plum_excep.PLUMgridException(err_msg=err_message)

    #
    # Internal PLUMgrid Functions
    #

    def _get_plugin_version(self):
        return plugin_ver.VERSION

    def _port_viftype_binding(self, context, port):
        port[portbindings.VIF_TYPE] = p_portbindings.VIF_TYPE_IOVISOR
        port[portbindings.VIF_DETAILS] = {
            # TODO(rkukura): Replace with new VIF security details
            portbindings.CAP_PORT_FILTER: True}
        return port

    def _network_admin_state(self, network):
        if network["network"].get("admin_state_up") is False:
            LOG.warning(_LW("Networks with admin_state_up=False are not "
                            "supported by PLUMgrid plugin yet."))
        return network

    def _allocate_pools_for_subnet(self, context, subnet):
        """Create IP allocation pools for a given subnet

        Pools are defined by the 'allocation_pools' attribute,
        a list of dict objects with 'start' and 'end' keys for
        defining the pool range.
        Modified from Neutron DB based class

        """

        pools = []
        # Auto allocate the pool around gateway_ip
        net = netaddr.IPNetwork(subnet['cidr'])
        if self._validate_ip(subnet['gateway_ip']):
            boundary = int(netaddr.IPAddress(subnet['gateway_ip']))
        else:
            boundary = net.last
        potential_dhcp_ip = int(net.first + 1)
        if boundary == potential_dhcp_ip:
            first_ip = net.first + 3
            boundary = net.first + 2
        else:
            first_ip = net.first + 2
        last_ip = net.last - 1
        # Use the gw_ip to find a point for splitting allocation pools
        # for this subnet
        split_ip = min(max(boundary, net.first), net.last)
        if split_ip > first_ip:
            pools.append({'start': str(netaddr.IPAddress(first_ip)),
                          'end': str(netaddr.IPAddress(split_ip - 1))})
        if split_ip < last_ip:
            pools.append({'start': str(netaddr.IPAddress(split_ip + 1)),
                          'end': str(netaddr.IPAddress(last_ip))})
            # return auto-generated pools
        # no need to check for their validity
        return pools

    def _validate_ip(self, ip):
        try:
            if netaddr.IPAddress(ip):
                return True
        except Exception:
            return False

    def _validate_network(self, cidr):
        try:
            if netaddr.IPNetwork(cidr):
                return True
        except Exception:
            return False

    def _extend_network_dict_provider_pg(self, network, net_db,
                                         net_binding=None):
        binding = net_db.pgnetbinding if net_db else net_binding
        if binding:
            network[provider.NETWORK_TYPE] = binding.network_type
            network[provider.PHYSICAL_NETWORK] = binding.physical_network
            network[provider.SEGMENTATION_ID] = binding.vlan_id
        return network

    def _process_provider_create(self, context, attrs):
        network_type = attrs.get(provider.NETWORK_TYPE)
        physical_network = attrs.get(provider.PHYSICAL_NETWORK)
        segmentation_id = attrs.get(provider.SEGMENTATION_ID)

        network_type_set = attributes.is_attr_set(network_type)
        physical_network_set = attributes.is_attr_set(physical_network)
        segmentation_id_set = attributes.is_attr_set(segmentation_id)

        if not (network_type_set or physical_network_set or
                segmentation_id_set):
            return (None, None, None)

        if not network_type_set:
            msg = _("provider:network_type required")
            raise n_exc.InvalidInput(error_message=msg)
        elif network_type == svc_constants.TYPE_FLAT:
            if segmentation_id_set:
                msg = _("provider:segmentation_id specified for flat network")
                raise n_exc.InvalidInput(error_message=msg)
            else:
                segmentation_id = None
            if not physical_network_set:
                msg = _("provider:physical_network required")
                raise n_exc.InvalidInput(error_message=msg)
            else:
                if not uuidutils.is_uuid_like(physical_network):
                    physical_network = self._process_phy_net(context,
                                           physical_network)
        elif network_type == svc_constants.TYPE_VLAN:
            if not segmentation_id_set:
                msg = _("provider:segmentation_id required")
                raise n_exc.InvalidInput(error_message=msg)
            if not svc_utils.is_valid_vlan_tag(segmentation_id):
                msg = (_("provider:segmentation_id out of range "
                         "(%(min_id)s through %(max_id)s)") %
                       {'min_id': svc_constants.MIN_VLAN_TAG,
                        'max_id': svc_constants.MAX_VLAN_TAG})
                raise n_exc.InvalidInput(error_message=msg)
            if not physical_network_set:
                msg = _("provider:physical_network required")
                raise n_exc.InvalidInput(error_message=msg)
            else:
                if not uuidutils.is_uuid_like(physical_network):
                    physical_network = self._process_phy_net(context,
                                           physical_network)

        elif network_type == svc_constants.TYPE_LOCAL:
            if physical_network_set:
                msg = _("provider:physical_network specified for local "
                        "network")
                raise n_exc.InvalidInput(error_message=msg)
            else:
                physical_network = None
            if segmentation_id_set:
                msg = _("provider:segmentation_id specified for local "
                        "network")
                raise n_exc.InvalidInput(error_message=msg)
            else:
                segmentation_id = None
        else:
            if not segmentation_id_set:
                segmentation_id = None
            if not physical_network_set:
                physical_network = None

        return network_type, physical_network, segmentation_id

    #
    # PLUMgrid plugin extensions
    #

    def create_l2_gateway(self, context, l2_gateway):
        LOG.debug("networking-plumgrid: create_l2_gateway() called")
        director_plumgrid = cfg.CONF.plumgriddirector.director_server
        director_admin = cfg.CONF.plumgriddirector.username
        director_password = cfg.CONF.plumgriddirector.password
        vendor_type = cfg.CONF.l2gateway.vendor
        sw_username = cfg.CONF.l2gateway.sw_username
        sw_password = cfg.CONF.l2gateway.sw_password

        with context.session.begin(subtransactions=True):
            gateway_info = l2gw_db.L2GatewayMixin.create_l2_gateway(self,
                                                                    context,
                                                                    l2_gateway)
            try:
                LOG.debug('PLUMgrid Library: create_l2_gateway() called')
                self._plumlib.create_l2_gateway(director_plumgrid,
                                                director_admin,
                                                director_password,
                                                gateway_info,
                                                vendor_type,
                                                sw_username,
                                                sw_password)
                return gateway_info
            except Exception as err_message:
                raise plum_excep.PLUMgridException(err_msg=err_message)

    def get_l2_gateway(self, context, id, fields=None):
        LOG.debug("networking-plumgrid: get_l2_gateway() called")
        with context.session.begin(subtransactions=True):
            res = l2gw_db.L2GatewayMixin.get_l2_gateway(self, context, id,
                                                        fields=fields)
            return res

    def delete_l2_gateway(self, context, id):
        LOG.debug("networking-plumgrid: delete_l2_gateway() called")
        with context.session.begin(subtransactions=True):
            gw_info = l2gw_db.L2GatewayMixin.get_l2_gateway(self, context, id)
            l2gw_db.L2GatewayMixin.delete_l2_gateway(self, context, id)
            try:
                LOG.debug('PLUMgrid Library: delete_l2_gateway() called')
                self._plumlib.delete_l2_gateway(gw_info)
            except Exception as err_message:
                raise plum_excep.PLUMgridException(err_msg=err_message)

    def get_l2_gateways(self, context, filters=None, fields=None,
                        sorts=None, limit=None, marker=None,
                        page_reverse=False):
        LOG.debug("networking-plumgrid: get_l2_gateways() called")
        with context.session.begin(subtransactions=True):
            res = l2gw_db.L2GatewayMixin.get_l2_gateways(self, context,
                                              filters=filters, fields=fields,
                                              sorts=sorts, limit=limit,
                                              marker=marker,
                                              page_reverse=page_reverse)
            return res

    def update_l2_gateway(self, context, id, l2_gateway):
        LOG.debug("networking-plumgrid: update_l2_gateway() called")
        with context.session.begin(subtransactions=True):
            res = l2gw_db.L2GatewayMixin.update_l2_gateway(self, context, id,
                                                           l2_gateway)
            return res

    def delete_l2_gateway_connection(self, context, id):
        LOG.debug("networking-plumgrid: delete_l2_gateway_connection() called")
        with context.session.begin(subtransactions=True):
            gw_conn_info = l2gw_db.L2GatewayMixin.get_l2_gateway_connection(
                                                                      self,
                                                                      context,
                                                                      id)
            l2gw_db.L2GatewayMixin.delete_l2_gateway_connection(self,
                                                                context,
                                                                id)
            try:
                LOG.debug("PLUMgrid Library: delete_l2_gateway_connection() "
                          "called")
                self._plumlib.delete_l2_gateway_connection(gw_conn_info)
            except Exception as err_message:
                raise plum_excep.PLUMgridException(err_msg=err_message)

    def create_l2_gateway_connection(self, context, l2_gateway_connection):
        LOG.debug("networking-plumgrid: create_l2_gateway_connection() called")
        with context.session.begin(subtransactions=True):
            gw_conn_info = l2gw_db.L2GatewayMixin.create_l2_gateway_connection(
                                                         self,
                                                         context,
                                                         l2_gateway_connection)
            try:
                LOG.debug("PLUMgrid Library: create_l2_gateway_connection() "
                          "called")
                self._plumlib.add_l2_gateway_connection(gw_conn_info)
                return gw_conn_info
            except Exception as err_message:
                raise plum_excep.PLUMgridException(err_msg=err_message)

    def get_l2_gateway_connections(self, context, filters=None,
                                   fields=None,
                                   sorts=None, limit=None, marker=None,
                                   page_reverse=False):
        LOG.debug("networking-plumgrid: get_l2_gateway_connections() called")
        with context.session.begin(subtransactions=True):
            res = l2gw_db.L2GatewayMixin.get_l2_gateway_connections(self,
                                                                    context)
            return res

    def get_l2_gateway_connection(self, context, id, fields=None):
        LOG.debug("networking-plumgrid: get_l2_gateway_connection() called")
        with context.session.begin(subtransactions=True):
            res = l2gw_db.L2GatewayMixin.get_l2_gateway_connection(self,
                                                                   context,
                                                                   id)
            return res

    def create_physical_attachment_point(self, context,
                                         physical_attachment_point):
        LOG.debug("networking_plumgrid: create_physical_attachment_point() "
                  "called")
        pap_obj = physical_attachment_point["physical_attachment_point"]
        tvd_created = False
        tvd_db = None
        with context.session.begin(subtransactions=True):
            try:
                if pap_obj.get("transit_domain_id") is None:
                    tvd_created = True
                    # create a transit domain
                    transit_domain = {"transit_domain":
                                      {"name": pap_obj["name"],
                                       "implicit": True,
                                       "tenant_id": pap_obj["tenant_id"]}}
                    tvd_db = self.create_transit_domain(context,
                                                        transit_domain)
                    (physical_attachment_point["physical_attachment_point"]
                     ["transit_domain_id"]) = tvd_db["id"]
                else:
                    pap_obj = self._process_pap(context, pap_obj)
                    try:
                        super(NeutronPluginPLUMgridV2,
                              self).get_transit_domain(context,
                              pap_obj["transit_domain_id"], fields=None)
                    except ext_tvd.NoTransitDomainFound:
                        raise

                pdb = super(NeutronPluginPLUMgridV2,
                            self).create_physical_attachment_point(context,
                                        physical_attachment_point)
                self._plumlib.create_physical_attachment_point(pdb)
            except Exception as err_message:
                if tvd_created:
                    if tvd_db:
                        self.delete_transit_domain(context, tvd_db["id"])
                LOG.error(err_message)
                raise plum_excep.PLUMgridException(err_msg=err_message)
        return pdb

    def update_physical_attachment_point(self, context, id,
                                         physical_attachment_point):
        LOG.debug("networking_plumgrid: update_physical_attachment_point() "
                  "called")

        with context.session.begin(subtransactions=True):
            pdb = super(NeutronPluginPLUMgridV2,
                        self).update_physical_attachment_point(context, id,
                                    physical_attachment_point)
            pap_db = pdb
            try:
                pap = physical_attachment_point["physical_attachment_point"]
                pdb['add_interfaces'] = pap.get("add_interfaces", [])
                pdb['remove_interfaces'] = pap.get("remove_interfaces", [])
                self._plumlib.update_physical_attachment_point(pdb)
            except Exception as err_message:
                raise plum_excep.PLUMgridException(err_msg=err_message)
        return pap_db

    def delete_physical_attachment_point(self, context, id):
        LOG.debug("networking_plumgrid: delete_physical_attachment_point() "
                 "called")
        pdb = super(NeutronPluginPLUMgridV2,
                    self).get_physical_attachment_point(context, id)
        with context.session.begin(subtransactions=True):
            super(NeutronPluginPLUMgridV2,
                  self).delete_physical_attachment_point(context, id)
            try:
                self._plumlib.delete_physical_attachment_point(pdb)
            except Exception as err_message:
                raise plum_excep.PLUMgridException(err_msg=err_message)
            if pdb.get("transit_domain_id"):
                transit_domain_id = pdb["transit_domain_id"]
                try:
                    tdb = super(NeutronPluginPLUMgridV2,
                             self).get_transit_domain(context,
                                                      transit_domain_id,
                                                      fields=None)
                    if tdb.get("implicit"):
                        self.delete_transit_domain(context, transit_domain_id)
                except ext_tvd.NoTransitDomainFound:
                    # if transit domain does not exist, no worries!
                    pass

    def get_physical_attachment_point(self, context, id, fields=None):
        LOG.debug("networking_plumgrid: get_physical_attachment_point() "
                  "called")
        return super(NeutronPluginPLUMgridV2,
                     self).get_physical_attachment_point(context, id, fields)

    def get_physical_attachment_points(self, context, filters=None,
                                       fields=None, sorts=None, limit=None,
                                       marker=None, page_reverse=False):
        LOG.debug("networking_plumgrid: list physical attachment"
                  " points called")
        return super(NeutronPluginPLUMgridV2,
                   self).get_physical_attachment_points(context, filters,
                             fields, sorts, limit, marker, page_reverse)

    def create_transit_domain(self, context, transit_domain):
        LOG.debug("networking_plumgrid: create_transit_domain() "
                  "called")

        with context.session.begin(subtransactions=True):
            tdb = super(NeutronPluginPLUMgridV2,
                        self).create_transit_domain(context,
                                  transit_domain)
            try:
                self._plumlib.create_transit_domain(tdb["id"], tdb)
            except Exception as err_message:
                raise plum_excep.PLUMgridException(err_msg=err_message)
        return tdb

    def update_transit_domain(self, context, id, transit_domain):
        LOG.debug("networking_plumgrid: update_transit_domain() "
                  "called")

        with context.session.begin(subtransactions=True):
            tdb = super(NeutronPluginPLUMgridV2,
                        self).update_transit_domain(context, id,
                                transit_domain)
            try:
                self._plumlib.update_transit_domain(id, tdb)
            except Exception as err_message:
                raise plum_excep.PLUMgridException(err_msg=err_message)
        return tdb

    def delete_transit_domain(self, context, id):
        LOG.debug("networking_plumgrid: delete_transit_domain() "
                 "called")
        with context.session.begin(subtransactions=True):
            super(NeutronPluginPLUMgridV2,
                  self).delete_transit_domain(context, id)
            try:
                self._plumlib.delete_transit_domain(id)
            except Exception as err_message:
                raise plum_excep.PLUMgridException(err_msg=err_message)

    def get_transit_domain(self, context, id, fields=None):
        LOG.debug("networking_plumgrid: get_transit_domain()"
                  "called")
        return super(NeutronPluginPLUMgridV2,
                   self).get_transit_domain(context, id, fields)

    def get_transit_domains(self, context, filters=None,
                            fields=None, sorts=None, limit=None,
                            marker=None, page_reverse=False):
        LOG.debug("networking_plumgrid: list_transit_domain() called")
        return super(NeutronPluginPLUMgridV2,
                   self).get_transit_domains(context, filters,
                             fields, sorts, limit, marker, page_reverse)

    def _process_network_db(self, network):
        if ('provider:network_type' in network['network'] and
            isinstance(network['network']['provider:network_type'],
                       string_types)):
            net_type = network['network']['provider:network_type'].lower()
            network['network']['provider:network_type'] = net_type

    def _process_phy_net(self, context, pap_name):
        pap_id_list = self.get_physical_attachment_points(context,
                          filters={'name': [pap_name]}, fields=["id"])
        if len(pap_id_list) == 1:
            return pap_id_list[0]["id"]
        elif len(pap_id_list) == 0:
            err_message = ("No physical_attachment_point matches "
                           "found for name '%s'" % pap_name)
            raise plum_excep.PLUMgridException(err_msg=err_message)
        else:
            err_message = ("Multiple physical_attachment_point"
                           " matches found for name"
                           " '%s', use an ID to be more specific." % pap_name)
            raise plum_excep.PLUMgridException(err_msg=err_message)

    def _process_pap(self, context, pap_db):
        if not uuidutils.is_uuid_like(pap_db['transit_domain_id']):
            td_id_list = self.get_transit_domains(context,
                             filters={'name': [pap_db['transit_domain_id']]},
                             fields=["id"])
            if len(td_id_list) == 1:
                pap_db['transit_domain_id'] = td_id_list[0]["id"]
            elif len(td_id_list) == 0:
                err_message = ("No transit_domain"
                               " matches found for name"
                               " '%s'" % pap_db['transit_domain_id'])
                raise plum_excep.PLUMgridException(err_msg=err_message)
            else:
                err_message = ("Multiple transit_domain"
                               " matches found for name"
                               " '%s', use an ID to be more"
                               " specific." % pap_db['transit_domain_id'])
                raise plum_excep.PLUMgridException(err_msg=err_message)
        return pap_db
