# Author: Soham Sen <sensoham135@gmail.com> <sohamsen2000@outlook.com>

import json
import os
import pkgutil

_ROOT = os.path.dirname(os.path.dirname(__file__))
_DATA_PATHS = [
    os.path.join(_ROOT, "api", "catalog.json"),
]


def load_index(path=None):
    if path:
        with open(path, "r") as handle:
            return json.load(handle)
    try:
        bundled = pkgutil.get_data("openskill", "api/catalog.json")
    except (IOError, OSError):
        bundled = None
    if bundled is not None:
        return json.loads(bundled.decode("utf-8"))
    for candidate in _DATA_PATHS:
        if os.path.exists(candidate):
            with open(candidate, "r") as handle:
                return json.load(handle)
    return []


def search(query, path=None):
    query = query.strip().lower()
    if not query:
        return []

    results = []
    for item in load_index(path=path):
        haystack = "{0} {1} {2} {3} {4}".format(
            item.get("symbol", ""),
            item.get("kind", ""),
            item.get("summary", ""),
            item.get("signature", ""),
            " ".join(item.get("tags", [])),
        ).lower()
        if query in haystack:
            results.append(item)
    return results
