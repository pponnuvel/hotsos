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

import tempfile

from common import constants


def sorted_dict(d, key=None, reverse=False):
    """
    Return dictionary sorted using key. If no key provided sorted by dict keys.
    """
    if key is None:
        return dict(sorted(d.items(), key=lambda e: e[0], reverse=reverse))

    return dict(sorted(d.items(), key=key, reverse=reverse))


def mktemp_dump(data):
    """Create a temporary file under the current plugin tmp directory and write
    data to the file.
    """
    ftmp = tempfile.mktemp(dir=constants.PLUGIN_TMP_DIR)
    with open(ftmp, 'w') as fd:
        fd.write(data)

    return ftmp
