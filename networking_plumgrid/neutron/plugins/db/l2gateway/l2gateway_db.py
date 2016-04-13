# Copyright 2015 PLUMgrid, Inc. All Rights Reserved.
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

from neutron.common import exceptions

from networking_plumgrid._i18n import _
from networking_plumgrid.neutron.plugins.common import (l2_exceptions
     as l2gw_exc)
from networking_plumgrid.neutron.plugins.common import constants
from networking_plumgrid.neutron.plugins.common import l2gw_validators
from networking_plumgrid.neutron.plugins.db.l2gateway import (l2gateway_models
     as models)
from networking_plumgrid.neutron.plugins.db.l2gateway import db_query
from oslo_log import log as logging
from oslo_utils import uuidutils
import six
from sqlalchemy.orm import exc as sa_orm_exc

LOG = logging.getLogger(__name__)


class L2GatewayMixin(db_query.L2GatewayCommonDbMixin):
    """Class L2GatewayMixin for handling l2_gateway resource."""
    gateway_resource = constants.GATEWAY_RESOURCE_NAME
    connection_resource = constants.CONNECTION_RESOURCE_NAME

    def _get_l2_gateway(self, context, gw_id):
        try:
            gw = context.session.query(models.PGL2Gateway).get(gw_id)
        except sa_orm_exc.NoResultFound:
            raise l2gw_exc.L2GatewayNotFound(gateway_id=gw_id)
        return gw

    def _get_l2_gateways(self, context):
        return context.session.query(models.PGL2Gateway).all()

    def _get_l2_gw_interfaces(self, context, id):
        return context.session.query(models.PGL2GatewayInterface).filter_by(
            device_id=id).all()

    def _is_vlan_configured_on_any_interface_for_l2gw(self,
                                                      context,
                                                      l2gw_id, vlan_id):
        result = {}
        match = False
        devices_db = self._get_l2_gateway_devices(context, l2gw_id)
        for device_model in devices_db:
            interfaces_db = self._get_l2_gw_interfaces(context,
                                                       device_model.id)
            for int_model in interfaces_db:
                query = context.session.query(models.PGL2GatewayInterface)
                int_db = query.filter_by(id=int_model.id).first()
                seg_id = int_db[constants.SEG_ID]
                if str(seg_id) == str(vlan_id):
                    result[device_model.id] = True
                    break
                else:
                    result[device_model.id] = False
        if match in result.values():
            return False
        else:
            return True

    def _get_l2_gateway_devices(self, context, l2gw_id):
        return context.session.query(models.PGL2GatewayDevice).filter_by(
            l2_gateway_id=l2gw_id).all()

    def _get_l2gw_devices_by_name_andl2gwid(self, context, device_name,
                                            l2gw_id):
        return context.session.query(models.PGL2GatewayDevice).filter_by(
            device_name=device_name, l2_gateway_id=l2gw_id).all()

    def _get_l2_gateway_connection(self, context, cn_id):
        try:
            con = context.session.query(
                  models.PGL2GatewayConnection).get(cn_id)
        except sa_orm_exc.NoResultFound:
            raise l2gw_exc.L2GatewayConnectionNotFound(id=cn_id)
        return con

    def _make_l2gw_connections_dict(self, gw_conn, fields=None):
        if gw_conn is None:
            raise l2gw_exc.L2GatewayConnectionNotFound(id="")
        segmentation_id = gw_conn['segmentation_id']
        if segmentation_id == 0:
            segmentation_id = ""
        res = {'id': gw_conn['id'],
               'network_id': gw_conn['network_id'],
               'l2_gateway_id': gw_conn['l2_gateway_id'],
               'tenant_id': gw_conn['tenant_id'],
               'segmentation_id': segmentation_id
               }
        return self._fields(res, fields)

    def _make_l2_gateway_dict(self, l2_gateway, fields=None):
        device_list = []
        for d in l2_gateway.devices:
            interface_list = []
            for interfaces_db in d.interfaces:
                seg_id = interfaces_db[constants.SEG_ID]
                if seg_id == 0:
                    seg_id = ""
                interface_list.append({'name':
                                       interfaces_db['interface_name'],
                                       constants.SEG_ID:
                                       seg_id})
            aligned_int__list = self._align_interfaces_list(interface_list)
            device_list.append({'device_name': d['device_name'],
                                'device_ip': d['device_ip'],
                                'id': d['id'],
                                'interfaces': aligned_int__list})
        res = {'id': l2_gateway['id'],
               'name': l2_gateway['name'],
               'vtep_ifc': l2_gateway['vtep_ifc'],
               'vtep_ip': l2_gateway['vtep_ip'],
               'devices': device_list,
               'tenant_id': l2_gateway['tenant_id']}
        return self._fields(res, fields)

    def _set_mapping_info_defaults(self, mapping_info):
        if not mapping_info.get(constants.SEG_ID):
            mapping_info[constants.SEG_ID] = 0

    def _retrieve_gateway_connections(self, context, gateway_id,
                                      mapping_info={}, only_one=False):
        filters = {'l2_gateway_id': [gateway_id]}
        for k, v in six.iteritems(mapping_info):
            if v and k != constants.SEG_ID:
                filters[k] = [v]
        query = self._get_collection_query(context,
                                           models.PGL2GatewayConnection,
                                           filters)
        return query.one() if only_one else query.all()

    def create_l2_gateway(self, context, l2_gateway):
        """Create a logical gateway."""
        self._admin_check(context, 'CREATE')
        gw = l2_gateway[self.gateway_resource]
        vtep_ip = gw.get('vtep_ip')
        l2gw_validators.is_valid_cidr(vtep_ip)
        tenant_id = self._get_tenant_id_for_create(context, gw)
        devices = gw['devices']
        self._validate_any_seg_id_empty_in_interface_dict(devices)
        gw_db = models.PGL2Gateway(
                    id=gw.get('id', uuidutils.generate_uuid()),
                    tenant_id=tenant_id,
                    name=gw.get('name'),
                    vtep_ifc=gw.get('vtep_ifc'),
                    vtep_ip=vtep_ip)
        context.session.add(gw_db)
        l2gw_device_dict = {}
        for device in devices:
            l2gw_device_dict['l2_gateway_id'] = id
            device_name = device['device_name']
            device_ip = device['device_ip']
            l2gw_device_dict['device_name'] = device_name
            l2gw_device_dict['device_ip'] = device_ip
            l2gw_device_dict['id'] = uuidutils.generate_uuid()
            uuid = self._generate_uuid()
            dev_db = models.PGL2GatewayDevice(id=uuid,
                                              l2_gateway_id=gw_db.id,
                                              device_name=device_name,
                                              device_ip=device_ip)
            context.session.add(dev_db)
            for interface_list in device['interfaces']:
                int_name = interface_list.get('name')
                if constants.SEG_ID in interface_list:
                    seg_id_list = interface_list.get(constants.SEG_ID)
                    for seg_ids in seg_id_list:
                        uuid = self._generate_uuid()
                        interface_db = self._get_int_model(uuid,
                                                           int_name,
                                                           dev_db.id,
                                                           seg_ids)
                        context.session.add(interface_db)
                else:
                    raise l2gw_exc.L2GatewaySegmentationRequired()
                context.session.query(models.PGL2GatewayDevice).all()
        return self._make_l2_gateway_dict(gw_db)

    def update_l2_gateway(self, context, id, l2_gateway):
        """Update l2 gateway."""
        self._admin_check(context, 'UPDATE')
        gw = l2_gateway[self.gateway_resource]
        if 'devices' in gw:
            devices = gw['devices']
        l2gw_db = self._get_l2_gateway(context, id)
        if l2gw_db.network_connections:
            raise l2gw_exc.L2GatewayInUse(gateway_id=id)
        dev_db = self._get_l2_gateway_devices(context, id)
        if not gw.get('devices'):
            raise l2gw_exc.L2GatewayDeviceRequired()
        for device in devices:
            dev_name = device['device_name']
            dev_db = self._get_l2gw_devices_by_name_andl2gwid(context,
                                                              dev_name,
                                                              id)
            if not dev_db:
                raise l2gw_exc.L2GatewayDeviceNotFound(device_id="")
            interface_db = self._get_l2_gw_interfaces(context,
                                                      dev_db[0].id)
            self._delete_l2_gateway_interfaces(context, interface_db)
            interface_dict_list = []
            self.validate_device_name(context, dev_name, id)
            for interfaces in device['interfaces']:
                interface_dict_list.append(interfaces)
            self._update_interfaces_db(context, interface_dict_list,
                                       dev_db)
        if gw.get('name'):
            l2gw_db.name = gw.get('name')
        return self._make_l2_gateway_dict(l2gw_db)

    def _update_interfaces_db(self, context, interface_dict_list, device_db):
        for interfaces in interface_dict_list:
            int_name = interfaces.get('name')
            if constants.SEG_ID in interfaces:
                seg_id_list = interfaces.get(constants.SEG_ID)
                for seg_ids in seg_id_list:
                    uuid = self._generate_uuid()
                    int_db = self._get_int_model(uuid,
                                                 int_name,
                                                 device_db[0].id,
                                                 seg_ids)
                    context.session.add(int_db)
            else:
                uuid = self._generate_uuid()
                interface_db = self._get_int_model(uuid,
                                                   int_name,
                                                   device_db[0].id,
                                                   0)
                context.session.add(interface_db)

    def get_l2_gateway(self, context, id, fields=None):
        """get the l2 gateway by id."""
        self._admin_check(context, 'GET')
        gw_db = self._get_l2_gateway(context, id)
        if gw_db:
            return self._make_l2_gateway_dict(gw_db, fields)
        else:
            return []

    def delete_l2_gateway(self, context, id):
        """delete the l2 gateway  by id."""
        self._admin_check(context, 'DELETE')
        gw_db = self._get_l2_gateway(context, id)
        if gw_db is None:
            raise l2gw_exc.L2GatewayNotFound(gateway_id=id)
        if gw_db.network_connections:
            raise l2gw_exc.L2GatewayInUse(gateway_id=id)
        context.session.delete(gw_db)
        LOG.debug("l2 gateway '%s' was deleted.", id)

    def get_l2_gateways(self, context, filters=None, fields=None,
                        sorts=None,
                        limit=None,
                        marker=None,
                        page_reverse=False):
        """list the l2 gateways available in the neutron DB."""
        self._admin_check(context, 'GET')
        marker_obj = self._get_marker_obj(
            context, 'l2_gateway', limit, marker)
        return self._get_collection(context, models.PGL2Gateway,
                                    self._make_l2_gateway_dict,
                                    filters=filters, fields=fields,
                                    sorts=sorts, limit=limit,
                                    marker_obj=marker_obj,
                                    page_reverse=page_reverse)

    def _update_segmentation_id(self, context, l2gw_id, segmentation_id):
        """Update segmentation id for interfaces."""
        device_db = self._get_l2_gateway_devices(context, l2gw_id)
        for device_model in device_db:
            interface_db = self._get_l2_gw_interfaces(context,
                                                      device_model.id)
            for interface_model in interface_db:
                interface_model.segmentation_id = segmentation_id

    def _delete_l2_gateway_interfaces(self, context, int_db_list):
        """delete the l2 interfaces  by id."""
        for interfaces in int_db_list:
            context.session.delete(interfaces)
        LOG.debug("l2 gateway interfaces was deleted.")

    def create_l2_gateway_connection(self, context, l2_gateway_connection):
        """Create l2 gateway connection."""
        self._admin_check(context, 'CREATE')
        gw_connection = l2_gateway_connection[self.connection_resource]
        l2_gw_id = gw_connection.get('l2_gateway_id')
        network_id = gw_connection.get('network_id')
        nw_map = {}
        nw_map['network_id'] = network_id
        nw_map['l2_gateway_id'] = l2_gw_id
        segmentation_id = ""
        if constants.SEG_ID in gw_connection:
            segmentation_id = gw_connection.get(constants.SEG_ID)
            nw_map[constants.SEG_ID] = segmentation_id
        is_vlan = self._is_vlan_configured_on_any_interface_for_l2gw(context,
                                                              l2_gw_id,
                                                              segmentation_id)
        network_id = l2gw_validators.validate_network_mapping_list(nw_map,
                                                                   is_vlan)
        if not is_vlan:
            raise l2gw_exc.L2GatewaySegmentationRequired()
        gw_db = self._get_l2_gateway(context, l2_gw_id)
        tenant_id = self._get_tenant_id_for_create(context, gw_db)
        if self._retrieve_gateway_connections(context,
                                              l2_gw_id,
                                              nw_map):
            raise l2gw_exc.L2GatewayConnectionExists(mapping=nw_map,
                                                     gateway_id=l2_gw_id)
        nw_map['tenant_id'] = tenant_id
        connection_id = uuidutils.generate_uuid()
        nw_map['id'] = connection_id
        if not segmentation_id:
            raise l2gw_exc.L2GatewaySegmentationRequired()
        gw_db.network_connections.append(
                models.PGL2GatewayConnection(**nw_map))
        gw_db = models.PGL2GatewayConnection(id=connection_id,
                                             tenant_id=tenant_id,
                                             network_id=network_id,
                                             l2_gateway_id=l2_gw_id,
                                             segmentation_id=segmentation_id)
        return self._make_l2gw_connections_dict(gw_db)

    def get_l2_gateway_connections(self, context, filters=None,
                                   fields=None,
                                   sorts=None, limit=None, marker=None,
                                   page_reverse=False):
        """List l2 gateway connections."""
        self._admin_check(context, 'GET')
        marker_obj = self._get_marker_obj(
            context, 'l2_gateway_connection', limit, marker)
        return self._get_collection(context, models.PGL2GatewayConnection,
                                    self._make_l2gw_connections_dict,
                                    filters=filters, fields=fields,
                                    sorts=sorts, limit=limit,
                                    marker_obj=marker_obj,
                                    page_reverse=page_reverse)

    def get_l2_gateway_connection(self, context, id, fields=None):
        """Get l2 gateway connection."""
        self._admin_check(context, 'GET')
        """Get the l2 gateway  connection  by id."""
        gw_db = self._get_l2_gateway_connection(context, id)
        return self._make_l2gw_connections_dict(gw_db, fields)

    def delete_l2_gateway_connection(self, context, id):
        """Delete the l2 gateway connection by id."""
        self._admin_check(context, 'DELETE')
        gw_db = self._get_l2_gateway_connection(context, id)
        context.session.delete(gw_db)
        LOG.debug("l2 gateway '%s' was destroyed.", id)

    def _admin_check(self, context, action):
        """Admin role check helper."""
        if not context.is_admin:
            reason = _('Cannot %s resource for non admin tenant') % action
            raise exceptions.AdminRequired(reason=reason)

    def _generate_uuid(self):
        """Generate uuid helper."""
        uuid = uuidutils.generate_uuid()
        return uuid

    def _get_int_model(self, uuid, interface_name, dev_id, seg_id):
        return models.PGL2GatewayInterface(id=uuid,
                                         interface_name=interface_name,
                                         device_id=dev_id,
                                         segmentation_id=seg_id)

    def get_l2gateway_devices_by_gateway_id(self, context, l2_gateway_id):
        """Get l2gateway_devices_by id."""
        session = context.session
        with session.begin():
            return session.query(models.PGL2GatewayDevice).filter_by(
                l2_gateway_id=l2_gateway_id).all()

    def get_l2gateway_interfaces_by_device_id(self, context, device_id):
        """Get all l2gateway_interfaces_by device_id."""
        session = context.session
        with session.begin():
            return session.query(models.PGL2GatewayInterface).filter_by(
                device_id=device_id).all()

    def validate_device_name(self, context, device_name, l2gw_id):
        if device_name:
            devices_db = self._get_l2gw_devices_by_name_andl2gwid(context,
                                                                  device_name,
                                                                  l2gw_id)
        if not devices_db:
            raise l2gw_exc.L2GatewayDeviceNameNotFound(device_name=device_name)

    def _validate_any_seg_id_empty_in_interface_dict(self, devices):
        """Validate segmentation_id for consistency."""
        for device in devices:
            interface_list = device['interfaces']
            if not interface_list:
                raise l2gw_exc.L2GatewayInterfaceRequired()
            if constants.SEG_ID in interface_list[0]:
                for interfaces in interface_list[1:len(interface_list)]:
                    if constants.SEG_ID not in interfaces:
                        raise l2gw_exc.L2GatewaySegmentationRequired()
            if constants.SEG_ID not in interface_list[0]:
                for interfaces in interface_list[1:len(interface_list)]:
                    if constants.SEG_ID in interfaces:
                        raise l2gw_exc.L2GatewaySegmentationRequired()

    def _align_interfaces_list(self, interface_list):
        """Align interfaces list based on input dict for multiple seg ids."""
        interface_dict = {}
        aligned_interface_list = []
        for interfaces in interface_list:
            actual__name = interfaces.get('name')
            if actual__name in interface_dict:
                interface_name = interface_dict.get(actual__name)
                seg_id_list = interfaces.get(constants.SEG_ID)
                interface_name.append(str(seg_id_list))
                interface_dict.update({actual__name: interface_name})
            else:
                seg_id = str(interfaces.get(constants.SEG_ID)).split()
                interface_dict.update({actual__name: seg_id})
        for name in interface_dict:
            aligned_interface_list.append({'segmentation_id':
                                           interface_dict[name],
                                           'name': name})
        return aligned_interface_list

    def _get_l2_gateway_connections(self, context):
        """Get l2 gateway connections."""
        try:
            con = context.session.query(models.PGL2GatewayConnection).all()
        except sa_orm_exc.NoResultFound:
            raise l2gw_exc.L2GatewayConnectionNotFound(
                id="")
        return con

    def _get_l2gw_ids_by_interface_switch(self, context, interface_name,
                                          switch_name):
        """Get l2 gateway ids by interface and switch."""
        connections = self._get_l2_gateway_connections(context)
        l2gw_id_list = []
        if connections:
            for connection in connections:
                l2gw_id = connection.l2_gateway_id
                devices = self._get_l2_gateway_device_by_name_id(context,
                                                                 switch_name,
                                                                 l2gw_id)
                if devices:
                    for device in devices:
                        interfaces = self._get_l2_gw_interfaces(context,
                                                                device.id)
                        for interface in interfaces:
                            if interface_name == interface.interface_name:
                                l2gw_id_list.append(l2gw_id)
                else:
                    LOG.debug("l2 gateway devices are empty")
        else:
            LOG.debug("l2 gateway connections are empty")
        return l2gw_id_list

    def _delete_connection_by_l2gw_id(self, context, l2gw_id):
        """Delete the l2 gateway connection by l2gw id."""
        con_db = self._get_l2_gateway_connection_by_l2gw_id(context,
                                                            l2gw_id)
        if con_db:
            context.session.delete(con_db[0])
            LOG.debug("l2 gateway connection was destroyed.")

    def _get_l2_gateway_connection_by_l2gw_id(self, context, l2gw_id):
        """Get the l2 gateway connection by l2gw id."""
        try:
            con = context.session.query(
                  models.PGL2GatewayConnection).filter_by(
                  l2_gateway_id=l2gw_id).all()
        except sa_orm_exc.NoResultFound:
            raise l2gw_exc.L2GatewayConnectionNotFound(
                id=l2gw_id)
        return con

    def _get_l2_gateway_device_by_name_id(self, context, device_name, l2gw_id):
        """Get the l2 gateway device by name and id."""
        try:
            gw = context.session.query(models.PGL2GatewayDevice).filter_by(
                device_name=device_name, l2_gateway_id=l2gw_id).all()
        except sa_orm_exc.NoResultFound:
            raise l2gw_exc.L2GatewayDeviceNotFound(
                device_id=device_name)
        return gw
