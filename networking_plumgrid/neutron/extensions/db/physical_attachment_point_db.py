from networking_plumgrid.neutron.extensions.db import models
from neutron.openstack.common import uuidutils
from oslo_log import log as logging

LOG = logging.getLogger(__name__)

PAP = "physical_attachment_point"
PAPS = "%ss" % PAP

def add_pap(context, pap):
    with context.session.begin(subtransactions=True):
         pap_db = models.PhysicalAttachmentPoint(tenant_id=pap[PAP]["tenant_id"],
                                                 name=pap[PAP]["name"],
                                                 hash_mode=pap[PAP]["hash_mode"],
                                                 lacp=pap[PAP]["lacp"])

         context.session.add(pap_db)

         for interface in pap[PAP]["interfaces"]:
             interface_db = models.Interface(hostname=interface["hostname"],
                                             interface=interface["interface"],
                                             pap=pap_db)

             context.session.add(interface_db)

    return pap["physical_attachment_point"]

def update_pap(context, pap_id, pap):

    qry = context.session.query(models.Interface)
    qry.filter_by(pap_id=pap_id).delete()

    qry = context.session.query(models.PhysicalAttachmentPoint)
    qry.filter_by(id=pap_id).update({"name": pap[PAP]["name"],
                                     "hash_mode": pap[PAP]["hash_mode"],
                                     "lacp": pap[PAP]["lacp"]})

    pap_db=qry.filter_by(id=pap_id).first()
    with context.session.begin(subtransactions=True):
        for interface in pap[PAP]["interfaces"]:
             interface_db = models.Interface(hostname=interface["hostname"],
                                             interface=interface["interface"],
                                             pap=pap_db)

             LOG.error(interface_db)
             context.session.add(interface_db)

    return pap["physical_attachment_point"]

def get_pap(context, pap_id):

    qry = context.session.query(models.PhysicalAttachmentPoint)
    pap_db = qry.filter_by(id=pap_id).first()
    return _make_pap_dict(pap_db)

def get_paps(context):
    LOG.info("Get physical attachment points called")

    qry = context.session.query(models.PhysicalAttachmentPoint)
    paps =  qry.all()

    return _make_pap_collection(context, paps)

def delete_pap(context, pap_id):
    LOG.info("DELETE physical attachment point called")

    qry = context.session.query(models.PhysicalAttachmentPoint)
    pap = qry.filter_by(id=pap_id).first()
    with context.session.begin(subtransactions=True):
        context.session.delete(pap)

def _make_pap_dict(pap):

    interfaces=[]
    for interface in pap.interfaces:
        interfaces.append({"hostname": interface.host_name, 
                           "interface": interface.interface})

    pap_dict = {"id": pap.id,
                "name": pap.name,
                "interfaces": interfaces,
                "hash_mode": pap.hash_mode,
                "lacp": pap.lacp,
                "tenant_id": pap.tenant_id}

    return pap_dict

def _make_pap_collection(context, paps):
    paps_list=[]
    for pap in paps:
        qry = context.session.query(models.Interface)
        interfaces = qry.filter_by(pap_id=pap.id)
        pap.interface=[]
        for interface in interfaces:
            pap.interfaces.append(interface)
        paps_list.append(_make_pap_dict(pap))

    return paps_list
