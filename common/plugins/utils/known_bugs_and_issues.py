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

"""
This is typically added as the last part of any plugin to be executed. It
serves to collect any bug information created during the course of the plugin
execution (i.e. each preceding part) and output as yaml for inclusion in the
master yaml section for this plugin.
"""
from common.known_bugs_utils import (
    add_known_bugs_to_master_plugin,
)
from common.issues_utils import (
    add_issues_to_master_plugin,
)
from common import plugintools


class KnownBugsAndIssuesCollector(object):
    def __call__(self):
        add_known_bugs_to_master_plugin()
        add_issues_to_master_plugin()
        plugintools.dump_all_parts()
