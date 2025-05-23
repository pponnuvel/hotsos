from functools import cached_property

from hotsos.core.config import HotSOSConfig
from hotsos.core.issues import IssuesManager, HotSOSScenariosWarning
from hotsos.core.log import log
from hotsos.core.ycheck.engine import (
    YDefsLoader,
    YDefsSection,
    YHandlerBase,
)
from hotsos.core.ycheck.engine.properties.common import YDefsContext
from hotsos.core.ycheck.common import GlobalSearcherPreloaderBase
from hotsos.core.exceptions import AlreadyLoadedError


class ScenariosSearchPreloader(YHandlerBase, GlobalSearcherPreloaderBase):
    """
    Find all scenario checks that have a search property and load their search
    into the global searcher.

    @param global_searcher: GlobalSearcher object
    """

    @property
    def filter(self):
        return HotSOSConfig.scenario_filter

    @cached_property
    def root(self):
        """ Return the root of all scenarios. """
        plugin_defs = YDefsLoader('scenarios').plugin_defs
        return YDefsSection(HotSOSConfig.plugin_name, plugin_defs or {})

    @property
    def scenarios(self):
        """
        Generator for all scenarios.

        Searches are expected to exist within checks so we extract them from
        each scenario and discover their searches.

        @return: scenario
        """
        for scenario in self.root.leaf_sections:
            # NOTE: scenario is not an override object, it is a PTreeSection
            # that contains the objects i.e. we go looking for the checks etc
            # within this scenario (sub)section.
            if self.skip_filtered(self.filter, scenario.resolve_path):
                log.info("skipping scenario %s from pre-search "
                         "(filter=%s)", scenario.resolve_path, self.filter)
                continue

            yield scenario

    def _preload_searches(self):
        """
        Find all scenario checks that have a search property and load their
        search into the global searcher.
        """
        if self.global_searcher.is_loaded(self.__class__.__name__):
            raise AlreadyLoadedError(
                "scenario searches have already been loaded into "
                "the global searcher. This operation can only be "
                "performed once.")

        log.debug("started loading scenario searches into searcher "
                  "(%s)", self.global_searcher.searcher)
        added = 0
        for scenario in self.scenarios:
            checks = scenario.checks
            log.debug("looking for searches in %s", checks.override_path)
            # this is needed to resolve search expression references
            checks.initialise(scenario.vars)
            for check in checks:
                if check.search is None:
                    continue

                # Checks can use input outside their scope so we
                # take that into account here.
                _input = check.input
                if _input is None:
                    _input = scenario.input

                log.debug("loading search for check '%s'", check.name)
                added += 1
                self._load_item_search(self.global_searcher, check.search,
                                       _input)

        self.global_searcher.set_loaded(self.__class__.__name__)
        log.debug("identified a total of %s scenario check searches", added)
        log.debug("finished loading scenario searches into searcher "
                  "(registry now has %s items)", len(self.global_searcher))

    def run(self):
        # Pre-load all scenario check searches into a global searcher
        self._preload_searches()


class Scenario():
    """
    Representation of a scenario containing all checks and conclusions.
    """
    def __init__(self, name, _checks, conclusions):
        log.debug("scenario: %s", name)
        self.name = name
        self._checks = _checks
        self._conclusions = conclusions

    @property
    def checks(self):
        return {c.name: c for c in self._checks}

    @property
    def conclusions(self):
        return {c.name: c for c in self._conclusions}


class YScenarioChecker(YHandlerBase):
    """
    This class handles the loading, execution and processing of all scenarios
    for the current plugin.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._scenarios = []
        hours = 24
        if HotSOSConfig.use_all_logs:
            hours *= HotSOSConfig.max_logrotate_depth

        # It is assumed that the global searcher already exists, is loaded with
        # searches and they have been executed. Unit tests however, should be
        # resetting the registry prior to each run and we will therefore need
        # to load searches each time which is why we do this here. This is
        # therefore not intended to be used outside of a test scenario.
        label = ScenariosSearchPreloader.__name__
        if not self.global_searcher.is_loaded(label):
            log.info("global searcher catalog is empty so launching "
                     "pre-load of scenario searches")
            # NOTE: this is not re-entrant safe and is only ever expected
            #       to be done from a unit test.
            ScenariosSearchPreloader(self.global_searcher).run()

    @property
    def filter(self):
        return HotSOSConfig.scenario_filter

    def load(self):
        plugin_content = YDefsLoader('scenarios').plugin_defs
        if not plugin_content:
            return

        yscenarios = YDefsSection(HotSOSConfig.plugin_name, plugin_content,
                                  context=YDefsContext({'global_searcher':
                                                        self.global_searcher}))
        if (not HotSOSConfig.force_mode and yscenarios.requires and not
                yscenarios.requires.result):
            log.debug("plugin '%s' scenarios pre-requisites not met - "
                      "skipping", HotSOSConfig.plugin_name)
            return

        log.debug("sections=%s, scenarios=%s",
                  len(list(yscenarios.branch_sections)),
                  len(list(yscenarios.leaf_sections)))

        to_skip = set()
        for scenario in yscenarios.leaf_sections:
            if ScenariosSearchPreloader.skip_filtered(self.filter,
                                                      scenario.resolve_path):
                log.info("skipping scenario %s (filter=%s)",
                         scenario.resolve_path,
                         HotSOSConfig.scenario_filter)
                continue

            # Only register scenarios if requirements are satisfied.
            group_name = scenario.parent.name
            if (not HotSOSConfig.force_mode and
                    (group_name in to_skip or
                        (scenario.requires and not scenario.requires.result))):
                log.debug("%s requirements not met - skipping scenario %s",
                          group_name, scenario.name)
                to_skip.add(group_name)
                continue

            scenario.checks.initialise(scenario.vars)
            scenario.checks.check_context.global_searcher = \
                self.global_searcher
            _scenario = Scenario(scenario.name, scenario.checks,
                                 scenario.conclusions)
            scenario.conclusions.initialise(scenario.vars, _scenario.checks)
            self._scenarios.append(_scenario)

    @property
    def scenarios(self):
        return self._scenarios

    @staticmethod
    def _run_scenario_conclusion(scenario, issue_mgr):
        """ Determine the conclusion of this scenario. """
        results = {}
        # Run conclusions in order of priority. One or more conclusion may
        # share the same priority. If one or more conclusion of the same
        # priority is reached the rest (of lower priority) are ignored.
        last_priority = None
        for conc in sorted(scenario.conclusions.values(), key=lambda _conc:
                           int(_conc.priority or 1), reverse=True):
            priority = int(conc.priority or 1)
            if last_priority is not None:
                if priority < last_priority and last_priority in results:
                    break

            last_priority = priority
            if conc.reached(scenario.checks):
                if priority in results:
                    results[priority].append(conc)
                else:
                    results[priority] = [conc]

                log.debug("conclusion reached: %s (priority=%s)", conc.name,
                          priority)

        if results:
            highest = max(results.keys())
            log.debug("selecting highest priority=%s conclusions (%s)",
                      highest, len(results[highest]))
            for conc in results[highest]:
                issue_mgr.add(conc.issue, context=conc.issue_context)
        else:
            log.debug("no conclusions reached")

    def run(self, load=True):
        if load:
            self.load()

        failed_scenarios = []
        issue_mgr = IssuesManager()
        for scenario in self.scenarios:
            log.debug("running scenario: %s", scenario.name)
            # catch failed scenarios and allow others to run
            try:
                self._run_scenario_conclusion(scenario, issue_mgr)
            # We really do want to catch all here since we don't care why
            # it failed but don't want to fail hard if it does.
            except Exception:  # pylint: disable=W0718
                log.exception("caught exception when running scenario %s:",
                              scenario.name)
                failed_scenarios.append(scenario.name)

        if failed_scenarios:
            msg = ("One or more scenarios failed to run "
                   f"({', '.join(failed_scenarios)}) - run hotsos in "
                   "debug mode (--debug) to get more detail")
            issue_mgr.add(HotSOSScenariosWarning(msg))
