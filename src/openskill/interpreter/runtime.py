# Author: Soham Sen <sensoham135@gmail.com> <sohamsen2000@outlook.com>

import errno
import os
import random

from openskill.interpreter.errors import SkillError
from openskill.interpreter.evaluator import create_global_env, evaluate, format_value
from openskill.interpreter.parser import parse


class SkillSession(object):
    def __init__(self, cwd=None):
        self.cwd = os.path.abspath(cwd or os.getcwd())
        self.global_env = create_global_env()
        self.output = []
        self.current_env = self.global_env
        self._load_stack = []
        self.symbol_plists = {}
        self.class_registry = {}
        self.gensym_counter = 0
        self.random_state = random.Random()
        self.warnings = []
        self.skill_path = [self.cwd]
        self.max_loop_iterations = 100000
        self.loop_iterations = 0
        self._open_ports = []

    def eval_text(self, source, filename="<string>"):
        self.loop_iterations = 0
        known_heads = {
            name
            for name, value in self.global_env.values.items()
            if callable(value) or hasattr(value, "invoke") or hasattr(value, "expand")
        }
        try:
            forms = parse(source, filename=filename, known_heads=known_heads)
            result = None
            for form in forms:
                result = evaluate(form, self.global_env, self)
            return result
        except RecursionError:
            raise SkillError("Expression is too deeply nested to evaluate safely")

    def resolve_path(self, path, base_dir=None):
        raw = str(path)
        if os.path.isabs(raw):
            return os.path.abspath(raw)
        return os.path.abspath(os.path.join(base_dir or self.cwd, raw))

    def resolve_existing_path(self, path, search_skill_path=False):
        raw = str(path)
        if os.path.isabs(raw):
            resolved = os.path.abspath(raw)
            if os.path.exists(resolved):
                return resolved
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), resolved)

        candidates = []
        if self._load_stack:
            candidates.append(self._load_stack[-1])
        candidates.append(self.cwd)
        if search_skill_path:
            candidates.extend(self.skill_path)

        seen = set()
        for base_dir in candidates:
            resolved = self.resolve_path(raw, base_dir=base_dir)
            if resolved in seen:
                continue
            seen.add(resolved)
            if os.path.exists(resolved):
                return resolved
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.resolve_path(raw))

    def load_file(self, path):
        resolved = self.resolve_existing_path(path, search_skill_path=True)
        try:
            with open(resolved, "r", encoding="utf-8-sig") as handle:
                source = handle.read()
        except UnicodeDecodeError:
            raise SkillError("Could not decode SKILL source file as UTF-8: %s" % resolved)
        self._load_stack.append(os.path.dirname(resolved))
        try:
            return self.eval_text(source, filename=resolved)
        finally:
            self._load_stack.pop()

    def register_port(self, port):
        self._open_ports.append(port)
        return port

    def unregister_port(self, port):
        self._open_ports = [item for item in self._open_ports if item is not port]

    def cleanup(self):
        for port in list(self._open_ports):
            try:
                port.close()
            except Exception:
                pass
            self.unregister_port(port)


__all__ = ["SkillSession", "format_value"]
