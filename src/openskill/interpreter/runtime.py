import errno
import os
import random

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
        self.random_state = random.Random(0)
        self.warnings = []
        self.skill_path = [self.cwd]
        self.max_loop_iterations = 100000
        self.loop_iterations = 0

    def eval_text(self, source, filename="<string>"):
        self.loop_iterations = 0
        forms = parse(source, filename=filename)
        result = None
        for form in forms:
            result = evaluate(form, self.global_env, self)
        return result

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
        with open(resolved, "r") as handle:
            source = handle.read()
        self._load_stack.append(os.path.dirname(resolved))
        try:
            return self.eval_text(source, filename=resolved)
        finally:
            self._load_stack.pop()


__all__ = ["SkillSession", "format_value"]
