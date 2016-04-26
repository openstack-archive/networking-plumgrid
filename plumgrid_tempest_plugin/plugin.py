# Copyright 2015 PLUMgrid, Inc. All Rights Reserved.
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

import os

from plumgrid_tempest_plugin import config as project_config
from tempest.test_discover import plugins


class PLUMgridTempestPlugin(plugins.TempestPlugin):
    """
    A PLUMgridTempestPlugin class provides the basic hooks for an external
    plugin to provide tempest the necessary information to run the plugin.
    """
    def load_tests(self):
        """
        Method to return the information necessary to load the tests in the
        plugin.

        :return: a tuple with the first value being the test_dir and the second
                 being the top_level
        :return type: tuple
        """
        base_path = os.path.split(os.path.dirname(
            os.path.abspath(__file__)))[0]
        test_dir = "plumgrid_tempest_plugin/tests"
        full_test_dir = os.path.join(base_path, test_dir)
        return full_test_dir, base_path

    def register_opts(self, conf):
        """
        Add additional configuration options to tempest.

        This method will be run for the plugin during the register_opts()
        function in tempest.config

        Parameters:
        conf (ConfigOpts): The conf object that can be used to register
        additional options on.
        """
        project_config.register_opts(conf)

    def get_opt_lists(self):
        """
        Get a list of options for sample config generation

        Return option_list: A list of tuples with the group name
                            and options in that group.
        Return type: list
        """
        return project_config.list_opts()
