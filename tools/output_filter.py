#!/usr/bin/python3
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

import yaml

from common import (
    constants,
    issues_utils,
    known_bugs_utils,
    plugintools,
)

FILTER_SCHEMA = [issues_utils.MASTER_YAML_ISSUES_FOUND_KEY,
                 known_bugs_utils.MASTER_YAML_KNOWN_BUGS_KEY]


def filter_master_yaml():
    with open(constants.MASTER_YAML_OUT) as fd:
        master_yaml = yaml.safe_load(fd)

    # Create a master list of issues and bugs adding info about which plugin
    # added them.

    filtered = {}
    for plugin in master_yaml:
        for key in FILTER_SCHEMA:
            if key in master_yaml[plugin]:
                if key not in filtered:
                    filtered[key] = {}

                if plugin not in filtered[key]:
                    filtered[key][plugin] = []

                items = master_yaml[plugin][key]
                for item in items:
                    filtered[key][plugin].append(item)

    with open(constants.MASTER_YAML_OUT, 'w') as fd:
        if filtered:
            fd.write(plugintools.dump(filtered, stdout=False))
            fd.write("\n")
        else:
            fd.write("")


if __name__ == "__main__":
    filter_master_yaml()
