# Author: Soham Sen <sensoham135@gmail.com> <sohamsen2000@outlook.com>

import json
import os
import pkgutil

_ROOT = os.path.dirname(os.path.dirname(__file__))
_DATA_PATHS = [
    os.path.join(_ROOT, "api", "catalog.json"),
]


def _validate_index(data):
    if not isinstance(data, list):
        raise ValueError("API index must be a list of entries")
    normalized = []
    for item in data:
        if not isinstance(item, dict):
            raise ValueError("API index entries must be objects")
        normalized.append(item)
    return normalized


def load_index(path=None):
    if path:
        with open(path, "r", encoding="utf-8") as handle:
            return _validate_index(json.load(handle))
    try:
        bundled = pkgutil.get_data("openskill", "api/catalog.json")
    except (IOError, OSError, ValueError):
        bundled = None
    if bundled is not None:
        try:
            return _validate_index(json.loads(bundled.decode("utf-8")))
        except (UnicodeDecodeError, ValueError):
            return []
    for candidate in _DATA_PATHS:
        if os.path.exists(candidate):
            try:
                with open(candidate, "r", encoding="utf-8") as handle:
                    return _validate_index(json.load(handle))
            except (OSError, ValueError):
                return []
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
