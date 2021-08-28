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

import utils
import yaml

from common import (
    issue_types,
    issues_utils,
)


class TestIssuesUtils(utils.BaseTestCase):

    def test_get_issues(self):
        issues = {}
        with open(os.path.join(self.plugin_tmp_dir, 'issues.yaml'), 'w') as fd:
            fd.write(yaml.dump(issues))

        ret = issues_utils._get_issues()
        self.assertEquals(ret, issues)

    def test_add_issue(self):
        issues_utils.add_issue(issue_types.MemoryWarning("test"))
        ret = issues_utils._get_issues()
        self.assertEquals(ret,
                          {issues_utils.MASTER_YAML_ISSUES_FOUND_KEY:
                           [{'type': 'MemoryWarning',
                             'desc': 'test',
                             'origin': 'testplugin.01part'}]})
