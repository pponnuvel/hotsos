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

from common import checks
from common.plugins.openvswitch import (
    OpenvSwitchChecksBase,
    OPENVSWITCH_SERVICES_EXPRS,
    OVS_PKGS_CORE,
    OVS_PKGS_DEPS,
)

YAML_PRIORITY = 0


class OpenvSwitchServiceChecks(OpenvSwitchChecksBase,
                               checks.ServiceChecksBase):

    def __init__(self):
        super().__init__(service_exprs=OPENVSWITCH_SERVICES_EXPRS)

    def get_running_services_info(self):
        """Get string info for running daemons."""
        if self.services:
            self._output["services"] = self.get_service_info_str()

    def __call__(self):
        self.get_running_services_info()


class OpenvSwitchPackageChecks(OpenvSwitchChecksBase,
                               checks.APTPackageChecksBase):

    def __init__(self):
        super().__init__(core_pkgs=OVS_PKGS_CORE, other_pkgs=OVS_PKGS_DEPS)

    def __call__(self):
        # require at least one core package to be installed to include
        # this in the report.
        if self.core:
            self._output["dpkg"] = self.all
