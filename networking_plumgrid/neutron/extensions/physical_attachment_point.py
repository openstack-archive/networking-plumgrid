from neutron.api import extensions
from neutron.api.v2 import attributes as attr
from neutron.api.v2 import base
from neutron.common import exceptions as nexceptions
from neutron import manager

PG_PAP='physical_attachment_point'
PG_PAPS='%ss' % PG_PAP



class InvalidInterfaceFormat(nexceptions.InvalidInput):
    message = _("Invalid format for interfaces: ")

    def __init__(self, error):
        super(InvalidInterfaceFormat, self).__init__()
        self.msg = self.message + error

def _validate_interfaces_list(data, valid_values=None):
    if not isinstance(data, list):
        raise InvalidInterfaceFormat("Must be a List of Interfaces")

    for interface in data:
        if 'hostname' not in interface:
            raise InvalidInterfaceFormat("hostname field is required")
        
        if 'interface' not in interface:
            raise InvalidInterfaceFormat("interface field is required")
        
attr.validators['type:validate_interfaces_list'] = _validate_interfaces_list

RESOURCE_ATTRIBUTE_MAP = {
    'physical_attachment_point': {
        'id': {
            'allow_post': False,
            'allow_put': False,
            'validate': {
                'type:uuid': None
            },
            'is_visible': True,
            'primary_key': True
        },
        'name': {
            'allow_post': True,
            'allow_put': True,
            'is_visible': True,
            'default': ''
        },
        'interfaces': {
            'allow_post': True,
            'allow_put': True,
            'is_visible': True,
            'validate': {
                'type:validate_interfaces_list': None
            }
        },
        'hash_mode': {
            'allow_post': True,
            'allow_put': True,
            'is_visible': True,
            'default': 'L2',
            'validate': {
                'type:values': ['L2', 'L3', 'L4'
                                'L2+L3', 'L3+L4']
            }
        },
        'lacp': {
            'allow_post': True,
            'allow_put': True,
            'is_visible': True,
            'default': True,
            'validate': {
                 'type:boolean': None
             }
        },
        'tenant_id': {
            'allow_post': True,
            'allow_put': False,
            'is_visible': True
        },
        
    }
}


class Physical_attachment_point(extensions.ExtensionDescriptor):

    @classmethod
    def get_name(cls):
        return "L2 Software Gateway with Port Bundle"

    @classmethod
    def get_alias(cls):
        # This alias will be used by the core plugin class to load
        # the extension. We will talk about that later how to register this extension
        # so plugin can load it.
        return "physical-attachment-point"

    @classmethod
    def get_description(cls):
        return "This API extensions exposes PLUMgrid Port Bundle concept in Openstack"

    @classmethod
    def get_namespace(cls):
        # Doc information
        return "http://docs.openstack.org/ext/physical_attachment_points/api/v2.0"

    @classmethod
    def get_updated(cls):
        # Specify when was this extension last updated,
        # good for management when there are changes in the design
        return "2012-10-05T10:00:00-00:00"

    @classmethod
    def get_resources(cls):
        # This method registers the URL and the dictionary  of
        # attributes on the neutron-server.

        exts = []
        plugin = manager.NeutronManager.get_plugin()

        resource_name = PG_PAP
        collection_name = PG_PAPS
        params = RESOURCE_ATTRIBUTE_MAP.get(resource_name, dict())
        controller = base.create_resource(
            collection_name, resource_name, plugin, params)
        ex = extensions.ResourceExtension(collection_name,
                                          controller)
        exts.append(ex)
        return exts
