#!/usr/bin/python3
import re
import os

from common import (
    constants,
    cli_helpers,
)
from openstack_common import OpenstackChecksBase

CONFIG_FILES = {"neutron": {"neutron": "etc/neutron/neutron.conf",
                            "openvswitch-agent":
                            "etc/neutron/plugins/ml2/openvswitch_agent.ini",
                            "l3-agent": "etc/neutron/l3_agent.ini",
                            "dhcp-agent": "etc/neutron/dhcp_agent.ini"},
                "nova": {"nova": "etc/nova/nova.conf"}}

FEATURES = {"neutron": {"neutron": ["availability_zone"],
                        "openvswitch-agent": ["l2_population"],
                        "l3-agent": ["agent_mode", "ovs_use_veth"],
                        "dhcp-agent": ["enable_metadata_network",
                                       "enable_isolated_metadata",
                                       "ovs_use_veth"]},
            "nova": {"nova": ["vcpu_pin_set", "cpu_shared_set",
                              "cpu_dedicated_set"]}}

# checked against neutron
DEFAULTS = {"neutron": {"dhcp-agent": {"enable_metadata_network": False,
                                       "enable_isolated_metadata": False}}}
YAML_PRIORITY = 5


class ServiceFeatureChecks(OpenstackChecksBase):

    @property
    def output(self):
        if self._output:
            return {"features": self._output}

    def get_service_features(self):
        for service in FEATURES:
            for module in FEATURES[service]:
                module_features = {}
                cfg = os.path.join(constants.DATA_ROOT,
                                   CONFIG_FILES[service][module])
                if not os.path.exists(cfg):
                    continue

                for key in FEATURES[service][module]:
                    for line in open(cfg).readlines():
                        ret = re.compile(r"^{}\s*=\s*(.+)\s*".format(key)
                                         ).match(line)
                        if ret:
                            module_features[key] = cli_helpers.bool_str(ret[1])
                            break

                    if key not in module_features:
                        if key in DEFAULTS.get(service, {}).get(module, {}):
                            default = DEFAULTS[service][module][key]
                            module_features[key] = default

                # TODO: only include modules for which there is an actual agent
                #       installed since otherwise their config is irrelevant.
                if module_features:
                    if service not in self._output:
                        self._output[service] = {}

                    self._output[service][module] = module_features

    def __call__(self):
        self.get_service_features()