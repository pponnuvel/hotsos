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
    checks,
    host_helpers,
    plugintools,
)

SERVICES = ["etcdctl",
            "calicoctl",
            "flanneld",
            "kubectl2",
            "kubelet",
            "containerd-shim",
            "containerd",
            "dockerd",
            "kubelet",
            "kube-proxy",
            "calico-node",
            ]

# Snaps that only exist in a K8s deployment
SNAPS_K8S = [r'charm[\S]+',
             r'conjure-up',
             r'cdk-addons',
             r'helm',
             r'kubernetes-[\S]+',
             r'kube-[\S]+',
             r'kubectl',
             r'kubelet',
             r'kubeadm',
             r'kubefed',
             ]
# Snaps that are used in a K8s deployment
SNAPS_DEPS = [r'core[0-9]*',
              r'docker',
              r'go',
              r'vault',
              r'etcd',
              ]


class KubernetesBase(object):

    def __init__(self):
        super().__init__(SERVICES, hint_range=(0, 3))
        self.nethelp = host_helpers.HostNetworkingHelper()

    @property
    def flannel_ports(self):
        ports = []
        for port in self.nethelp.host_interfaces:
            if "flannel" in port.name:
                ports.append(port)

        return ports

    @property
    def bind_interfaces(self):
        """
        Fetch interfaces used by Kubernetes.
        """
        return {'flannel': self.flannel_ports}


class KubernetesChecksBase(KubernetesBase, plugintools.PluginPartBase,
                           checks.ServiceChecksBase):
    pass
