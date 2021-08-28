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
import re

from common.cli_helpers import CLIHelper
from common.issue_types import JujuWarning
from common.issues_utils import add_issue
from common.plugins.juju import (
    JUJU_LOG_PATH,
    JujuChecksBase,
)

YAML_PRIORITY = 0


class JujuMachineChecks(JujuChecksBase):

    def get_machine_info(self):
        machine_info = {"machines": {}}
        ps_machines = set()
        machines_running = set()
        machines_stopped = set()

        if not os.path.exists(JUJU_LOG_PATH):
            return

        machine = self.machine.agent_service_name
        machine_unit = machine.partition("jujud-machine-")[2]
        for line in CLIHelper().ps():
            if "jujud-machine-" in line:
                expr = r".+jujud-machine-(\d+(?:-lxd-\d+)?).*"
                ret = re.compile(expr).match(line)
                if ret:
                    ps_machines.add("jujud-machine-{}".format(ret[1]))

        if machine in ps_machines:
            machines_running.add("{} (version={})".
                                 format(machine_unit, self.machine.version))
        else:
            machines_stopped.add(machine_unit)

        if machines_running:
            machine_info["machines"]["running"] = list(machines_running)

        if machines_stopped:
            machine_info["machines"]["stopped"] = list(machines_stopped)

        if not machines_running and (machines_stopped or
                                     self._get_local_running_units):
            msg = ("there is no Juju machined running on this host but it "
                   "seems there should be")
            add_issue(JujuWarning(msg))

        if machine_info["machines"]:
            self._output.update(machine_info)

    def __call__(self):
        self.get_machine_info()
