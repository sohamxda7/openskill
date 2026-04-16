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
        self._load_stack = [self.cwd]
        self.symbol_plists = {}
        self.gensym_counter = 0
        self.random_state = random.Random(0)
        self.warnings = []

    def eval_text(self, source, filename="<string>"):
        forms = parse(source, filename=filename)
        result = None
        for form in forms:
            result = evaluate(form, self.global_env, self)
        return result

    def load_file(self, path):
        base_dir = self._load_stack[-1] if self._load_stack else self.cwd
        resolved = path
        if not os.path.isabs(resolved):
            resolved = os.path.join(base_dir, path)
        resolved = os.path.abspath(resolved)
        with open(resolved, "r") as handle:
            source = handle.read()
        self._load_stack.append(os.path.dirname(resolved))
        try:
            return self.eval_text(source, filename=resolved)
        finally:
            self._load_stack.pop()


__all__ = ["SkillSession", "format_value"]
