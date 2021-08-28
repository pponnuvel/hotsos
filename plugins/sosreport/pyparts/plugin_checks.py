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

from common import (
    constants,
    issue_types,
    issues_utils,
    plugintools,
)
from common.searchtools import (
    SearchDef,
    FileSearcher,
)

YAML_PRIORITY = 0


class SOSReportPluginChecks(plugintools.PluginPartBase):

    def __init__(self):
        super().__init__()
        self.searcher = FileSearcher()

    def check_plugin_timouts(self):
        if not os.path.exists(os.path.join(constants.DATA_ROOT, 'sos_logs')):
            return

        path = os.path.join(constants.DATA_ROOT, 'sos_logs/ui.log')
        self.searcher.add_search_term(SearchDef(r".* Plugin (\S+) timed out.*",
                                                tag="timeouts"), path=path)
        results = self.searcher.search()
        timeouts = []
        for r in results.find_by_tag("timeouts"):
            plugin = r.get(1)
            timeouts.append(plugin)
            msg = ("sosreport plugin '{}' has timed out and may have "
                   "incomplete data".format(plugin))
            issues_utils.add_issue(issue_types.SOSReportWarning(msg))

        if timeouts:
            self._output["plugin-timeouts"] = timeouts

    def __call__(self):
        self.check_plugin_timouts()
