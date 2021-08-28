# Copyright 2021 Edward Hope-Morley
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os

import shutil
import tempfile
import unittest


# Must be set prior to other imports
TESTS_DIR = os.environ["TESTS_DIR"]
os.environ["DATA_ROOT"] = os.path.join(TESTS_DIR, "fake_data_root")


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        # Always reset env globals
        os.environ["DATA_ROOT"] = os.path.join(TESTS_DIR, "fake_data_root")
        # If a test relies on loading info from defs yaml this needs to be set
        # to actual plugin name.
        os.environ["PLUGIN_NAME"] = "testplugin"
        os.environ["USE_ALL_LOGS"] = "True"
        os.environ["PART_NAME"] = "01part"
        os.environ["PLUGIN_YAML_DEFS"] = os.path.join(TESTS_DIR, "defs")
        self.plugin_tmp_dir = tempfile.mkdtemp()
        os.environ["PLUGIN_TMP_DIR"] = self.plugin_tmp_dir

    def tearDown(self):
        if os.path.isdir(self.plugin_tmp_dir):
            shutil.rmtree(self.plugin_tmp_dir)
