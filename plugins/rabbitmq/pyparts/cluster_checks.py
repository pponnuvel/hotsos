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

from common import (
    issue_types,
    issues_utils,
)
from common.plugins.rabbitmq import RabbitMQEventChecksBase

YAML_PRIORITY = 1


class RabbitMQClusterChecks(RabbitMQEventChecksBase):

    def __init__(self):
        super().__init__(yaml_defs_group='cluster-checks')

    def process_results(self, results):
        """ See defs/events.yaml for definitions. """
        for events in self.event_definitions.values():
            for event in events:
                _results = results.find_by_tag(event)
                if event == "cluster-partitions" and _results:
                    msg = ("cluster either has or has had partitions - check "
                           "cluster_status")
                    issues_utils.add_issue(issue_types.RabbitMQWarning(msg))
