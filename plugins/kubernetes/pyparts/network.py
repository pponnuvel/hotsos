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

from common.plugins.kubernetes import KubernetesChecksBase

YAML_PRIORITY = 1


class KubernetesNetworkChecks(KubernetesChecksBase):

    def get_network_info(self):
        for port in self.flannel_ports:
            if 'flannel' not in self._output:
                self._output['flannel'] = {}

            self._output['flannel'][port.name] = port.encap_info
            if port.addresses:
                self._output['flannel'][port.name]['addr'] = port.addresses[0]

    def __call__(self):
        self.get_network_info()
