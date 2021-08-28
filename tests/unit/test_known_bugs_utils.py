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

import yaml

import utils

from common import known_bugs_utils


class TestKnownBugsUtils(utils.BaseTestCase):

    def test_get_known_bugs(self):
        known_bugs = {known_bugs_utils.MASTER_YAML_KNOWN_BUGS_KEY:
                      [{'id': 'https://bugs.launchpad.net/bugs/1',
                        'desc': 'no description provided',
                        'origin': 'testplugin.01part'}]}
        with open(os.path.join(self.plugin_tmp_dir,
                               'known_bugs.yaml'), 'w') as fd:
            fd.write(yaml.dump(known_bugs))

        ret = known_bugs_utils._get_known_bugs()
        self.assertEquals(ret, known_bugs)

    def test_get_known_bugs_none(self):
        ret = known_bugs_utils._get_known_bugs()
        self.assertEquals(ret, {})

    def test_add_known_bug_first(self):
        known_bugs_utils.add_known_bug(1)
        ret = known_bugs_utils._get_known_bugs()
        self.assertEquals(ret,
                          {known_bugs_utils.MASTER_YAML_KNOWN_BUGS_KEY:
                           [{'id': 'https://bugs.launchpad.net/bugs/1',
                             'desc': 'no description provided',
                             'origin': 'testplugin.01part'}
                            ]})

    def test_add_known_bug(self):
        known_bugs = {known_bugs_utils.MASTER_YAML_KNOWN_BUGS_KEY:
                      [{'id': 'https://bugs.launchpad.net/bugs/1',
                        'desc': 'no description provided',
                        'origin': 'testplugin.01part'}]}
        with open(os.path.join(self.plugin_tmp_dir,
                               'known_bugs.yaml'), 'w') as fd:
            fd.write(yaml.dump(known_bugs))

        known_bugs_utils.add_known_bug(2)
        ret = known_bugs_utils._get_known_bugs()
        expected = {known_bugs_utils.MASTER_YAML_KNOWN_BUGS_KEY:
                    [{'id': 'https://bugs.launchpad.net/bugs/1',
                      'desc': 'no description provided',
                      'origin': 'testplugin.01part'},
                     {'id': 'https://bugs.launchpad.net/bugs/2',
                      'desc': 'no description provided',
                      'origin': 'testplugin.01part'}]}
        self.assertEquals(ret, expected)
