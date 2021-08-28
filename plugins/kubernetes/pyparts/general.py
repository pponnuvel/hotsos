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
    checks,
    constants,
    plugintools,
)
from common.plugins.kubernetes import (
    KubernetesChecksBase,
    SNAPS_DEPS,
    SNAPS_K8S,
)

YAML_PRIORITY = 0


class KubernetesPackageChecks(plugintools.PluginPartBase,
                              checks.SnapPackageChecksBase):

    def __init__(self):
        super().__init__(core_snaps=SNAPS_K8S, other_snaps=SNAPS_DEPS)

    def __call__(self):
        # require at least one core package to be installed to include
        # this in the report.
        if self.core:
            self._output["snaps"] = self.all


class KubernetesServiceChecks(KubernetesChecksBase):

    def get_running_services_info(self):
        """Get string info for running services."""
        if self.services:
            self._output["services"] = self.get_service_info_str()

    def __call__(self):
        self.get_running_services_info()


class KubernetesResourceChecks(KubernetesChecksBase):

    def get_pod_info(self):
        pod_info = []
        pods_path = os.path.join(constants.DATA_ROOT,
                                 "var/log/pods")
        if os.path.exists(pods_path):
            for pod in os.listdir(pods_path):
                pod_info.append(pod)

        if pod_info:
            self._output["pods"] = pod_info

    def get_container_info(self):
        container_info = []
        containers_path = os.path.join(constants.DATA_ROOT,
                                       "var/log/containers")
        if os.path.exists(containers_path):
            for container in os.listdir(containers_path):
                container_info.append(container)

        if container_info:
            self._output["containers"] = container_info

    def __call__(self):
        self.get_pod_info()
        self.get_container_info()
