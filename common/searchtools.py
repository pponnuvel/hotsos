#!/usr/bin/python3
import os

import glob
import gzip
import multiprocessing
import re


class SearchResultPart(object):

    def __init__(self, index, value):
        self.index = index
        self.value = value


class SearchResult(object):

    def __init__(self, linenumber, search_term_tag=None):
        self.tag = search_term_tag
        self.linenumber = linenumber
        self._parts = {}

    def add(self, index, value):
        self._parts[index] = SearchResultPart(index, value)

    def get(self, index):
        """Retrieve a result part by its index."""
        if index not in self._parts:
            return None

        return self._parts[index].value


class SearchResultsCollection(object):

    def __init__(self):
        self._iter_idx = 0
        self._results = {}

    @property
    def files(self):
        return list(self._results.keys())

    def add(self, path, results):
        self._results[path] = results

    def find_by_path(self, path):
        if path not in self._results:
            return []

        return self._results[path]

    def find_by_tag(self, path, tag):
        results = []
        for result in self._results.get(path, []):
            if result.tag == tag:
                results.append(result)

        return results

    def __iter__(self):
        return iter(self._results)


class FileSearcher(object):

    def __init__(self):
        self.paths = {}

    def add_search_term(self, key, indices, path, tag=None):
        """Add a term to search for.

        A search term is registered against a path which can be a file,
        directory or glob. Any number of search terms can be registered.
        Searches are executed concurrently by file.

        @param key: regex pattern to search for
        @param indices: list of indexes within a successful match that we want
                        to extract.
        @param path: path that we will be searching for this key
        @param tag: optional user-friendly identifier for this search term
        """
        entry = {"key": re.compile(key), "indices": indices, "tag": tag}
        if path in self.paths:
            self.paths[path].append(entry)
        else:
            self.paths[path] = [entry]

    def _job_wrapper(self, pool, path, entry):
        term_key = path
        return pool.apply_async(self._search_task_wrapper,
                                (entry, term_key))

    def _search_task_wrapper(self, path, term_key):
        with gzip.open(path, 'r') as fd:
            try:
                # test if file is gzip
                fd.read(1)
                fd.seek(0)
                return self._search_task(term_key, fd, decode=True)
            except OSError:
                pass

        with open(path) as fd:
            return self._search_task(term_key, fd)

    def _search_task(self, term_key, fd, decode=False):
        results = []
        for ln, line in enumerate(fd):
            # line numbers are not zero-indexed
            ln += 1
            for s_term in self.paths[term_key]:
                if type(line) == bytes:
                    line = line.decode("utf-8")

                ret = s_term["key"].match(line)
                if ret:
                    r = SearchResult(ln, s_term.get("tag"))
                    for i in s_term["indices"]:
                        r.add(i, ret[i])

                    results.append(r)

        return results

    def search(self):
        results = SearchResultsCollection()
        """Execute all the search queries.

        @return: search results
        """
        with multiprocessing.Pool(processes=os.cpu_count()) as pool:
            jobs = {}
            for path in self.paths:
                jobs[path] = {}
                if os.path.isfile(path):
                    jobs[path][path] = self._job_wrapper(pool, path, path)
                elif os.path.isdir(path):
                    for e in os.listdir(path):
                        d_entry = os.path.join(path, e)
                        jobs[path][d_entry] = self._job_wrapper(pool, path,
                                                                d_entry)
                else:
                    for e in glob.glob(path):
                        jobs[path][e] = self._job_wrapper(pool, path, e)

            for path in jobs:
                for file in jobs[path]:
                    results.add(file, jobs[path][file].get())

        return results
