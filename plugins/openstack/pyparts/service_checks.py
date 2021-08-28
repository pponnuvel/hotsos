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

import re

from common import (
    issue_types,
    issues_utils,
)
from common.cli_helpers import CLIHelper


class NeutronServiceChecks(object):

    def check_ovs_cleanup(self):
        """
        Allow one run on node boot/reboot but not after.
        """
        raise_issue = False
        start_count = 0
        cli = CLIHelper()
        for line in cli.journalctl(unit="neutron-ovs-cleanup"):
            expr = r"Started OpenStack Neutron OVS cleanup."
            if re.compile("-- Reboot --").match(line):
                # reset after reboot
                start_count = 0
            elif re.compile(expr).search(line):
                if start_count:
                    raise_issue = True
                    break

                start_count += 1

        if raise_issue:
            msg = ("neutron-ovs-cleanup has been manually run on this "
                   "host. This is not recommended and can have unintended "
                   "side-effects.")
            issues_utils.add_issue(issue_types.OpenstackWarning(msg))

    def __call__(self):
        self.check_ovs_cleanup()
