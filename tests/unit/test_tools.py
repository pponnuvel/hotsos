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

import tempfile
import utils
import yaml

from tools import output_filter


class TestTools(utils.BaseTestCase):

    def test_output_filter_empty(self):
        issues = {}
        with tempfile.NamedTemporaryFile() as ftmp:
            os.environ["MASTER_YAML_OUT"] = ftmp.name
            with open(ftmp.name, 'w') as fd:
                fd.write(yaml.dump(issues))

            output_filter.filter_master_yaml()

            with open(ftmp.name) as fd:
                result = yaml.load(fd, Loader=yaml.SafeLoader)

            self.assertEqual(result, None)

    def test_output_filter(self):
        issue_key = output_filter.issues_utils.MASTER_YAML_ISSUES_FOUND_KEY
        bug_key = output_filter.known_bugs_utils.MASTER_YAML_KNOWN_BUGS_KEY
        issues = {"testplugin":
                  {issue_key: [{"type": "MemoryWarning",
                                "desc": "a msg",
                                "origin": "testplugin.01part"}],
                   bug_key: [{"id": "1234",
                              "desc": "a msg",
                              "origin": "testplugin.01part"}]}}
        expected = {issue_key: {"testplugin": [{"type": "MemoryWarning",
                                                "desc": "a msg",
                                                "origin":
                                                "testplugin.01part"}]},
                    bug_key: {"testplugin": [{"id": "1234",
                                              "desc": "a msg",
                                              "origin": "testplugin.01part"}]}}
        with tempfile.NamedTemporaryFile() as ftmp:
            os.environ["MASTER_YAML_OUT"] = ftmp.name
            with open(ftmp.name, 'w') as fd:
                fd.write(yaml.dump(issues))

            output_filter.filter_master_yaml()

            with open(ftmp.name) as fd:
                result = yaml.load(fd, Loader=yaml.SafeLoader)

            self.assertEqual(result, expected)
