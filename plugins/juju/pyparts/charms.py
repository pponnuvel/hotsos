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

import glob
import re
import os

from common.plugins.juju import (
    CHARM_MANIFEST_GLOB,
    JujuChecksBase,
    JUJU_LIB_PATH,
)

YAML_PRIORITY = 1


class JujuCharmChecks(JujuChecksBase):

    def get_charm_versions(self):
        if not os.path.exists(JUJU_LIB_PATH):
            return

        versions = []
        for entry in glob.glob(os.path.join(JUJU_LIB_PATH,
                                            CHARM_MANIFEST_GLOB)):
            for manifest in os.listdir(entry):
                base = os.path.basename(manifest)
                ret = re.compile(r".+_(\S+)-([0-9]+)$").match(base)
                if ret:
                    versions.append("{}-{}".format(ret[1], ret[2]))

        if versions:
            self._output["charms"] = sorted(versions)

    def __call__(self):
        self.get_charm_versions()
