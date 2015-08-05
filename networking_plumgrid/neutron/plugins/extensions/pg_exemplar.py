# Copyright (c) 2012 OpenStack Foundation.
# All rights reserved.
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

from neutron.api import extensions
from neutron import manager
 
# You have to specify the attributes neutron-server should expect when
# someone invokes this plugin. Let's say you want
# 'name', 'priority', 'credential' for your extension /foxinsocks
# then following dictionary must be declared.
# I am following the naming convention used by other extensions.
# Feel free to ask me or read my other blogs on
# http://control-that-vm.blogspot.com if this goes above your head :)
 
RESOURCE_ATTRIBUTE_MAP = {
    'pg_exemplar': {
    'name': {'allow_post': True, 'allow_put': True,
                 'is_visible': True},
    'priority': {'allow_post': True, 'allow_put': True,
                 'is_visible': True},
    'credential': {'allow_post': True, 'allow_put': True,
                 'is_visible': True},
    # tenant_id is the user id used by keystone for authorisation
    # It's good to use the following as it is and it is necessary
    # for every extension 
    'tenant_id': {'allow_post': True, 'allow_put': False,
                  'required_by_policy': True,
                  'validate': {'type:string': None},
                  'is_visible': True}
    }
}
 
# Great! Now you have the defined the attributes that you need for your
# extensions. You need to store this dictionary in the neutron-server
# by the following class
 
class PGExemplar(extensions.ExtensionDescriptor):
    # The name of this class should be the same as the file name
    # There are a couple of methods and their properties defined in the
    # parent class of this class, ExtensionDescriptor you can check them
 
    @classmethod
    def get_name(cls):
        # You can coin a name for this extension
        return "Fox in socks"
 
    @classmethod
    def get_alias(cls):
        # This alias will be used by your core_plugin class to load
        # the extension
        return "foxinsock"
 
    @classmethod
    def get_description(cls):
        # A small description about this extension
        return "A quick brown fox jumped over a lazy dog"
 
    @classmethod
    def get_namespace(cls):
        # The XML namespace for this extension
        # but as we move on to use JSON over XML based request
        # this is not that important, correct me if I am wrong.
        return "http://whatdoesthesocksay.com"
 
    @classmethod
    def get_updated(cls):
        # Specify when was this extension last updated,
        # good for management when there are changes in the design
        return "2014-05-06T10:00:00-00:00"
 
    def get_extended_resources(self, version):
        if version == "2.0":
            return EXTENDED_ATTRIBUTES_2_0
        else:
            return {}
