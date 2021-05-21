import os
import re

from common.cli_helpers import CLIHelper
from common.known_bugs_utils import add_known_bug
from common.issues_utils import add_issue
from common.issue_types import BcacheWarning
from common.plugins.storage import BcacheChecksBase

YAML_PRIORITY = 3
# The real limit is 30 but we go just above in case bcache is flapping
# just above and below the limit.
CACHE_AVAILABLE_PERCENT_LIMIT_LP1900438 = 33
CSET_CONFIGS = {"congested_read_threshold_us": 0,
                "congested_write_threshold_us": 0}
BDEV_CONFIGS = {"sequential_cutoff": 0,
                "cache_mode": "writeback",
                "writeback_percent": 10}
CONFIGS_ASSERTIONS = {"sequential_cutoff": "eq",
                      "cache_mode": "selected",
                      "writeback_percent": "gte",
                      "congested_read_threshold_us": "eq",
                      "congested_write_threshold_us": "eq"}


class ConfigBase(BcacheChecksBase):

    def __init__(self):
        self.config = {}
        self._load()

    def get(self, cset, bdev, key):
        cset = self.config.get(cset)
        if cset:
            if bdev:
                return cset.get(bdev, {}).get(key)
            else:
                return cset.get(key)


class CachesetsConfig(ConfigBase):

    def _load(self):
        for cset in self.get_cachesets():
            for key in CSET_CONFIGS:
                cfg = os.path.join(cset, key)
                if os.path.exists(cfg):
                    _cset = os.path.basename(cset)
                    if _cset not in self.config:
                        self.config[_cset] = {}

                    with open(cfg) as fd:
                        self.config[_cset][key] = fd.read().strip()


class BdevsConfig(ConfigBase):

    def _load(self):
        for cset in self.get_cachesets():
            for bdev in self.get_cacheset_bdevs(cset):
                _bdev = os.path.basename(bdev)
                _cset = os.path.basename(cset)
                for key in BDEV_CONFIGS:
                    cfg = os.path.join(bdev, key)
                    if os.path.exists(cfg):
                        if _cset not in self.config:
                            self.config[_cset] = {_bdev: {}}
                        elif _bdev not in self.config[_cset]:
                            self.config[_cset][_bdev] = {}

                        with open(cfg) as fd:
                            self.config[_cset][_bdev][key] = fd.read().strip()


class BcacheConfigChecks(BcacheChecksBase):

    def __init__(self):
        super().__init__()

    def check_configs(self, cset, bdev=None):
        report = {}
        if bdev:
            config_refs = BDEV_CONFIGS
            configs = BdevsConfig()
        else:
            config_refs = CSET_CONFIGS
            configs = CachesetsConfig()

        for key in config_refs:
            expected = config_refs[key]
            assertion = CONFIGS_ASSERTIONS[key]
            if assertion == "eq":
                actual = str(configs.get(cset, bdev, key))
                if actual != str(config_refs[key]):
                    report[key] = {"expected": expected,
                                   "actual": actual}
            elif assertion == "gte":
                actual = int(configs.get(cset, bdev, key))
                if actual != config_refs[key]:
                    report[key] = {"expected": expected,
                                   "actual": actual}
            elif assertion == "selected":
                actual = configs.get(cset, bdev, key)
                expr = r"\[{}\]".format(config_refs[key])
                if re.compile(expr).match(actual):
                    report[key] = {"expected": expected,
                                   "actual": actual}

        return report

    def check_config(self):
        reports = {}
        for cset in self.get_cachesets():
            _cset = os.path.basename(cset)
            report = self.check_configs(_cset)
            if report:
                if "csets" not in reports:
                    reports["csets"] = {}

                if _cset not in reports["csets"]:
                    reports["csets"][_cset] = report
                else:
                    reports["csets"][_cset].update(report)

            for bdev in self.get_cacheset_bdevs(cset):
                _bdev = os.path.basename(bdev)
                report = self.check_configs(_cset, _bdev)
                if report:
                    if "csets" not in reports:
                        reports["csets"] = {}

                    if _cset not in reports["csets"]:
                        reports["csets"][_cset] = {"bdevs": {}}
                    else:
                        reports["csets"][_cset]["bdevs"] = {}

                    reports["csets"][_cset]["bdevs"][_bdev] = report

        if reports:
            self._output["unexpected-config"] = reports

    def __call__(self):
        self.check_config()


class BcacheDeviceChecks(BcacheChecksBase):

    def get_device_info(self):
        devs = {}
        for dev_type in ["bcache", "nvme"]:
            for line in CLIHelper().ls_lanR_sys_block():
                expr = r".+[0-9:]+\s+({}[0-9a-z]+)\s+.+".format(dev_type)
                ret = re.compile(expr).match(line)
                if ret:
                    if dev_type not in devs:
                        devs[dev_type] = {}

                    devname = ret[1]
                    devs[dev_type][devname] = {}
                    for line in CLIHelper().udevadm_info_dev(device=devname):
                        expr = r".+\s+disk/by-dname/(.+)"
                        ret = re.compile(expr).match(line)
                        if ret:
                            devs[dev_type][devname]["dname"] = ret[1]
                        elif "dname" not in devs[dev_type][devname]:
                            devs[dev_type][devname]["dname"] = \
                                "<notfound>"

        if devs:
            self._output["devices"] = devs

    def __call__(self):
        self.get_device_info()


class BcacheStatsChecks(BcacheChecksBase):

    def get_info(self):
        csets = self.get_sysfs_cachesets()
        if csets:
            self._output["cachesets"] = csets

    def check_stats(self):
        if not self.get_sysfs_cachesets():
            return

        for cset in self.get_sysfs_cachesets():
            limit = CACHE_AVAILABLE_PERCENT_LIMIT_LP1900438
            key = 'cache_available_percent'
            if cset[key] <= limit:
                msg = ("bcache {} ({}) is <= {} - "
                       "this node could be suffering from bug 1900438".
                       format(key, cset[key], limit))
                add_issue(BcacheWarning(msg))
                add_known_bug(1900438, "see BcacheWarning for info")

    def __call__(self):
        self.get_info()
        self.check_stats()
