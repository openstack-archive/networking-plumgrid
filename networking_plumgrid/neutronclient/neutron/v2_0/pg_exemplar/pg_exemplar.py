# Copyright (c) 2015 Orange.
# All Rights Reserved.
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


from neutronclient.common import extension
from neutronclient.i18n import _
from neutronclient.neutron import v2_0 as neutronv20


class PGExemplar(extension.NeutronClientExtension):
    resource = 'pg_exemplar'
    path = 'pg-exemplar'
    resource_plural = '%ss' % resource
    object_path = '/pg-exemplar/%s' % path
    resource_path = '/pg-exemplar/%s/%%s' % path
    versions = ['2.0']


class PGExemplarCreate(extension.ClientExtensionCreate,
                             PGExemplar):
    shell_command = 'pg-exemplar-create'

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--name',
            help=_('Name PG Exemplar ext'))

    def args2body(self, parsed_args):
        body = {
            self.resource: {},
        }

        if parsed_args.network_id:
            _network_id = neutronv20.find_resourceid_by_name_or_id(
                self.get_client(), 'network',
                parsed_args.network_id)
            body[self.resource]['network_id'] = _network_id

        return body


class PGExemplarUpdate(extension.ClientExtensionUpdate,
                             PGExemplar):
    shell_command = 'pg-exemplar-update'


class PGExemplarDelete(extension.ClientExtensionDelete,
                             PGExemplar):
    shell_command = 'pg-exemplar-delete'


class PGExemplarList(extension.ClientExtensionList,
                           PGExemplar):
    shell_command = 'pg-exemplar-list'
    pagination_support = True
    sorting_support = True


class PGExemplarShow(extension.ClientExtensionShow,
                           PGExemplar):
    shell_command = 'pg-exemplar-show'
