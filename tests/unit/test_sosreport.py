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

from plugins.sosreport.pyparts import plugin_checks


class TestSOSReportPluginPartPluginChecks(utils.BaseTestCase):

    def test_check_plugin_timouts_none(self):
        inst = plugin_checks.SOSReportPluginChecks()
        inst()
        self.assertIsNone(inst.output)

    def test_check_plugin_timouts_some(self):
        with tempfile.TemporaryDirectory() as dtmp:
            os.environ["DATA_ROOT"] = dtmp
            os.makedirs(os.path.join(dtmp, "sos_logs"))
            with open(os.path.join(dtmp, "sos_logs", 'ui.log'), 'w') as fd:
                fd.write(" Plugin networking timed out\n")

            inst = plugin_checks.SOSReportPluginChecks()
            inst()
            self.assertEquals(inst.output, {"plugin-timeouts": ["networking"]})
