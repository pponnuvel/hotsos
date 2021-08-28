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

from common.checks import APTPackageChecksBase
from common.plugins.storage import (
    CephChecksBase,
    CEPH_PKGS_CORE,
)

YAML_PRIORITY = 0


class CephPackageChecks(CephChecksBase, APTPackageChecksBase):

    def __init__(self, *args, **kwargs):
        super().__init__(core_pkgs=CEPH_PKGS_CORE)

    @property
    def output(self):
        if self._output:
            return {"ceph": self._output}

    def __call__(self):
        # require at least one core package to be installed to include
        # this in the report.
        if self.core:
            self._output["dpkg"] = self.all


class CephServiceChecks(CephChecksBase):

    def get_running_services_info(self):
        """Get string info for running services."""
        if self.services:
            self._output["services"] = self.get_service_info_str()

    def __call__(self):
        self.get_running_services_info()
