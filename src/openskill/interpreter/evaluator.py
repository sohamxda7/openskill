from __future__ import division

import functools
import io
import math
import os
import random
import re
from itertools import product

from openskill.interpreter.errors import SkillError, SkillEvalError
from openskill.interpreter.forms import ListForm, NumberForm, StringForm, SymbolForm


class SkillSymbolValue(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "SkillSymbolValue(%r)" % (self.name,)

    def __str__(self):
        return self.name


class BuiltinFunction(object):
    def __init__(self, name, func):
        self.name = name
        self.func = func

    def __call__(self, session, *args):
        return self.func(session, *args)


class SkillProcedure(object):
    def __init__(self, name, params, body, env):
        self.name = name
        self.params = params
        self.body = body
        self.env = env

    def invoke(self, session, caller_env, *args):
        call_env = Environment(parent=caller_env)
        _bind_arguments(self.name, self.params, args, call_env, session)
        result = None
        for form in self.body:
            result = evaluate(form, call_env, session)
        return result


class SkillMacro(object):
    def __init__(self, name, params, body, env, whole_form=False):
        self.name = name
        self.params = params
        self.body = body
        self.env = env
        self.whole_form = whole_form

    def expand(self, session, caller_env, arg_forms, full_form=None):
        macro_env = Environment(parent=caller_env)
        if self.whole_form:
            _bind_arguments(self.name, self.params, [datum_from_form(full_form)], macro_env, session)
        else:
            _bind_arguments(self.name, self.params, [datum_from_form(form) for form in arg_forms], macro_env, session)
        result = None
        for form in self.body:
            result = evaluate(form, macro_env, session)
        return result


class SkillTable(object):
    def __init__(self, name=None, default=None):
        self.name = name or "<table>"
        self.default = default
        self.data = {}


class SkillArray(object):
    def __init__(self, values):
        self.values = list(values)


class SkillRegex(object):
    def __init__(self, pattern):
        self.pattern = pattern
        self.compiled = re.compile(pattern)


class SkillPort(object):
    def __init__(self, handle, mode, string_backed=False):
        self.handle = handle
        self.mode = mode
        self.string_backed = string_backed

    def close(self):
        if self.handle is not None:
            self.handle.close()
            self.handle = None


class SkillClass(object):
    def __init__(self, name, base_class, slots):
        self.name = name
        self.base_class = base_class
        self.slots = slots


class SkillInstance(object):
    def __init__(self, skill_class, slot_values):
        self.skill_class = skill_class
        self.slot_values = slot_values


class ReturnFromProg(Exception):
    def __init__(self, value):
        self.value = value


class SkillThrow(Exception):
    def __init__(self, tag, value):
        self.tag = tag
        self.value = value


class Environment(object):
    def __init__(self, parent=None):
        self.parent = parent
        self.values = {}

    def define(self, name, value):
        self.values[name] = value
        return value

    def set(self, name, value):
        if name in self.values:
            self.values[name] = value
            return value
        if self.parent is not None:
            return self.parent.set(name, value)
        self.values[name] = value
        return value

    def get(self, name, form=None):
        if name in self.values:
            return self.values[name]
        if self.parent is not None:
            return self.parent.get(name, form=form)
        raise SkillEvalError("undefined symbol `%s`" % name, form=form)


def is_truthy(value):
    return value is not None and value is not False


def skill_equal(left, right):
    if left in (None, []) and right in (None, []):
        return True
    if isinstance(left, SkillSymbolValue) and isinstance(right, SkillSymbolValue):
        return left.name == right.name
    if isinstance(left, list) and isinstance(right, list):
        if len(left) != len(right):
            return False
        return all(skill_equal(a, b) for a, b in zip(left, right))
    return left == right


def skill_eq(left, right):
    if left in (None, []) and right in (None, []):
        return True
    if isinstance(left, SkillSymbolValue) and isinstance(right, SkillSymbolValue):
        return left.name == right.name
    if isinstance(left, list) or isinstance(right, list):
        return left is right
    return left == right


def format_value(value):
    if value is None or value is False or value == []:
        return "nil"
    if value is True:
        return "t"
    if isinstance(value, SkillSymbolValue):
        return value.name
    if isinstance(value, str):
        return '"%s"' % value.replace("\\", "\\\\").replace('"', '\\"')
    if isinstance(value, list):
        return "(" + " ".join(format_value(item) for item in value) + ")"
    if isinstance(value, BuiltinFunction):
        return "<builtin %s>" % value.name
    if isinstance(value, SkillProcedure):
        return "<procedure %s>" % value.name
    if isinstance(value, SkillMacro):
        return "<macro %s>" % value.name
    if isinstance(value, SkillTable):
        return "<table %s>" % value.name
    if isinstance(value, SkillArray):
        return "#(" + " ".join(format_value(item) for item in value.values) + ")"
    if isinstance(value, SkillRegex):
        return "<regex %s>" % value.pattern
    if isinstance(value, SkillPort):
        return "<port %s>" % value.mode
    if isinstance(value, SkillClass):
        return "<class %s>" % value.name
    if isinstance(value, SkillInstance):
        return "<instance %s>" % value.skill_class.name
    return str(value)


def datum_from_form(form):
    if isinstance(form, NumberForm):
        return form.value
    if isinstance(form, StringForm):
        return form.value
    if isinstance(form, SymbolForm):
        if form.name == "nil":
            return None
        if form.name == "t":
            return True
        return SkillSymbolValue(form.name)
    if isinstance(form, ListForm):
        if not form.items:
            return None
        return [datum_from_form(item) for item in form.items]
    raise SkillEvalError("unsupported datum", form=form)


def form_from_datum(value, filename="<eval>", line=1, column=1):
    if value is None:
        return SymbolForm("nil", line, column, filename)
    if value is True:
        return SymbolForm("t", line, column, filename)
    if isinstance(value, SkillSymbolValue):
        return SymbolForm(value.name, line, column, filename)
    if isinstance(value, int) or isinstance(value, float):
        return NumberForm(value, str(value), line, column, filename)
    if isinstance(value, str):
        return StringForm(value, line, column, filename)
    if isinstance(value, list):
        return ListForm(
            [form_from_datum(item, filename=filename, line=line, column=column) for item in value],
            line,
            column,
            filename,
        )
    raise SkillEvalError("cannot convert runtime datum to form")


def eval_quasiquote(form, env, session):
    if isinstance(form, ListForm):
        result = []
        for item in form.items:
            if isinstance(item, ListForm) and item.items:
                head = item.items[0]
                if isinstance(head, SymbolForm) and head.name == "unquote":
                    if len(item.items) != 2:
                        raise SkillEvalError("unquote expects one value", form=item)
                    result.append(evaluate(item.items[1], env, session))
                    continue
                if isinstance(head, SymbolForm) and head.name == "splice":
                    if len(item.items) != 2:
                        raise SkillEvalError("splice expects one value", form=item)
                    spliced = evaluate(item.items[1], env, session)
                    if not isinstance(spliced, list):
                        raise SkillEvalError("splice requires a list result", form=item)
                    result.extend(spliced)
                    continue
            result.append(eval_quasiquote(item, env, session))
        return result
    return datum_from_form(form)


def _ensure_symbol(form):
    if not isinstance(form, SymbolForm):
        raise SkillEvalError("expected symbol", form=form)
    return form.name


def _parse_param_entry(form):
    if isinstance(form, SymbolForm):
        return form.name, None
    if isinstance(form, ListForm) and form.items:
        name = _ensure_symbol(form.items[0])
        default = form.items[1] if len(form.items) > 1 else None
        return name, default
    raise SkillEvalError("invalid parameter specification", form=form)


def _compile_params(params_form):
    spec = {
        "required": [],
        "optional": [],
        "key": [],
        "rest": None,
        "aux": [],
    }
    mode = "required"
    for item in params_form.items:
        if isinstance(item, SymbolForm) and item.name in ("@rest", "@optional", "@key", "@aux"):
            mode = item.name[1:]
            continue
        if mode == "required":
            spec["required"].append(_ensure_symbol(item))
            continue
        if mode == "rest":
            spec["rest"] = _ensure_symbol(item)
            mode = "post_rest"
            continue
        if mode == "post_rest":
            raise SkillEvalError("only @aux may follow @rest", form=item)
        if mode in ("optional", "key", "aux"):
            spec[mode].append(_parse_param_entry(item))
            continue
        raise SkillEvalError("unsupported parameter mode", form=item)
    return spec


def _evaluate_default(default_form, env, session):
    if default_form is None:
        return None
    return evaluate(default_form, env, session)


def _bind_arguments(name, spec, args, env, session):
    required = spec["required"]
    optional = spec["optional"]
    key_entries = dict(spec["key"])
    rest_name = spec["rest"]
    aux_entries = spec["aux"]

    if len(args) < len(required):
        raise SkillEvalError("%s expected at least %s arguments, got %s" % (name, len(required), len(args)))

    position = 0
    for required_name in required:
        env.define(required_name, args[position])
        position += 1

    if spec["key"] and spec["optional"]:
        raise SkillEvalError("%s cannot combine @key and @optional" % name)

    for optional_name, default in optional:
        if position < len(args):
            env.define(optional_name, args[position])
            position += 1
        else:
            env.define(optional_name, _evaluate_default(default, env, session))

    seen_keys = {}
    provided_keys = {}
    rest_values = []
    if spec["key"]:
        while position < len(args):
            current = args[position]
            if (
                isinstance(current, SkillSymbolValue)
                and current.name.startswith("?")
                and position + 1 < len(args)
                and current.name[1:] in key_entries
                and current.name[1:] not in seen_keys
            ):
                matched_name = current.name[1:]
                provided_keys[matched_name] = args[position + 1]
                seen_keys[matched_name] = True
                position += 2
                continue
            rest_values.append(current)
            position += 1
        for key_name, default in spec["key"]:
            if key_name in provided_keys:
                env.define(key_name, provided_keys[key_name])
            else:
                env.define(key_name, _evaluate_default(default, env, session))
    else:
        rest_values.extend(args[position:])

    if rest_name is not None:
        env.define(rest_name, rest_values if rest_values else None)
    elif rest_values:
        raise SkillEvalError("%s got unexpected extra arguments" % name)

    for aux_name, default in aux_entries:
        env.define(aux_name, _evaluate_default(default, env, session))


def _eval_sequence(forms, env, session):
    result = None
    for form in forms:
        result = evaluate(form, env, session)
    return result


_SYMBOL_KEY_TAG = object()


def _plist_key(value):
    if isinstance(value, SkillSymbolValue):
        return (_SYMBOL_KEY_TAG, value.name)
    if isinstance(value, list):
        return tuple(_plist_key(item) for item in value)
    return value


def _plist_key_to_value(value):
    if isinstance(value, tuple):
        if len(value) == 2 and value[0] is _SYMBOL_KEY_TAG:
            return SkillSymbolValue(value[1])
        return [_plist_key_to_value(item) for item in value]
    return value


def _require_symbol_value(value, name):
    if not isinstance(value, SkillSymbolValue):
        raise SkillEvalError("%s expects a quoted symbol" % name)
    return value.name


def _ensure_list_value(value, name):
    if value is None:
        return []
    if not isinstance(value, list):
        raise SkillEvalError("%s expects a list" % name)
    return value


def _ensure_array_value(value, name):
    if not isinstance(value, SkillArray):
        raise SkillEvalError("%s expects an array" % name)
    return value.values


def _plist_for_symbol(session, symbol_name):
    return list(session.symbol_plists.get(symbol_name, []))


def _set_plist_for_symbol(session, symbol_name, values):
    session.symbol_plists[symbol_name] = list(values)
    return session.symbol_plists[symbol_name]


def _plist_lookup(session, symbol_name, indicator):
    items = session.symbol_plists.get(symbol_name, [])
    target = _plist_key(indicator)
    index = 0
    while index + 1 < len(items):
        if _plist_key(items[index]) == target:
            return items[index + 1]
        index += 2
    return None


def _plist_put(session, symbol_name, indicator, value):
    items = list(session.symbol_plists.get(symbol_name, []))
    target = _plist_key(indicator)
    index = 0
    while index + 1 < len(items):
        if _plist_key(items[index]) == target:
            items[index + 1] = value
            session.symbol_plists[symbol_name] = items
            return value
        index += 2
    items.extend([indicator, value])
    session.symbol_plists[symbol_name] = items
    return value


def _plist_remove(session, symbol_name, indicator):
    items = list(session.symbol_plists.get(symbol_name, []))
    target = _plist_key(indicator)
    index = 0
    while index + 1 < len(items):
        if _plist_key(items[index]) == target:
            del items[index : index + 2]
            session.symbol_plists[symbol_name] = items
            return True
        index += 2
    session.symbol_plists[symbol_name] = items
    return None


def _resolve_class_reference(session, value, name, form=None):
    if isinstance(value, SkillClass):
        return value
    if not isinstance(value, SkillSymbolValue):
        raise SkillEvalError("%s expects a class or quoted class name" % name, form=form)
    skill_class = session.class_registry.get(value.name)
    if skill_class is None:
        raise SkillEvalError("unknown class `%s`" % value.name, form=form)
    return skill_class


def _compile_class_slots(slots_form):
    if not isinstance(slots_form, ListForm):
        raise SkillEvalError("defclass slot list must be a list", form=slots_form)
    compiled = []
    seen = set()
    for slot_form in slots_form.items:
        if isinstance(slot_form, SymbolForm):
            slot_name = slot_form.name
            spec = {"name": slot_name, "initarg": None, "initform": None}
        elif isinstance(slot_form, ListForm) and slot_form.items:
            slot_name = _ensure_symbol(slot_form.items[0])
            spec = {"name": slot_name, "initarg": None, "initform": None}
            index = 1
            while index < len(slot_form.items):
                option_form = slot_form.items[index]
                option_name = _ensure_symbol(option_form)
                if option_name in ("@reader", "@writer"):
                    raise SkillEvalError("%s is not supported in defclass MVP" % option_name, form=option_form)
                if option_name not in ("@initarg", "@initform"):
                    raise SkillEvalError("unsupported slot option `%s`" % option_name, form=option_form)
                if index + 1 >= len(slot_form.items):
                    raise SkillEvalError("slot option `%s` requires a value" % option_name, form=option_form)
                value_form = slot_form.items[index + 1]
                if option_name == "@initarg":
                    if not isinstance(value_form, SymbolForm) or not value_form.name.startswith("?"):
                        raise SkillEvalError("@initarg expects a ?keyword symbol", form=value_form)
                    spec["initarg"] = value_form.name
                else:
                    spec["initform"] = value_form
                index += 2
        else:
            raise SkillEvalError("invalid slot specification", form=slot_form)
        if slot_name in seen:
            raise SkillEvalError("duplicate slot `%s`" % slot_name, form=slot_form)
        seen.add(slot_name)
        compiled.append(spec)
    return compiled


def _evaluate_slot_target(form, env, session):
    if isinstance(form, SymbolForm):
        try:
            return env.get(form.name, form=form)
        except SkillEvalError:
            return SkillSymbolValue(form.name)
    return evaluate(form, env, session)


def _get_slot_value(session, target, slot_name, form):
    if isinstance(target, SkillInstance):
        if slot_name not in target.skill_class.slots:
            raise SkillEvalError("unknown slot `%s` on class `%s`" % (slot_name, target.skill_class.name), form=form)
        return target.slot_values.get(slot_name)
    if isinstance(target, SkillSymbolValue):
        return _plist_lookup(session, target.name, SkillSymbolValue(slot_name))
    raise SkillEvalError("slot access requires a symbol plist or class instance", form=form)


def _set_slot_value(session, target, slot_name, value, form):
    if isinstance(target, SkillInstance):
        if slot_name not in target.skill_class.slots:
            raise SkillEvalError("unknown slot `%s` on class `%s`" % (slot_name, target.skill_class.name), form=form)
        target.slot_values[slot_name] = value
        return value
    if isinstance(target, SkillSymbolValue):
        return _plist_put(session, target.name, SkillSymbolValue(slot_name), value)
    raise SkillEvalError("slot assignment requires a symbol plist or class instance", form=form)


def _eval_let(form, env, session):
    if len(form.items) < 2:
        raise SkillEvalError("let requires bindings and body", form=form)
    bindings_form = form.items[1]
    if not isinstance(bindings_form, ListForm):
        raise SkillEvalError("let bindings must be a list", form=bindings_form)
    let_env = Environment(parent=env)
    for binding in bindings_form.items:
        if isinstance(binding, SymbolForm):
            let_env.define(binding.name, None)
            continue
        if not isinstance(binding, ListForm) or not binding.items:
            raise SkillEvalError("invalid let binding", form=binding)
        name = _ensure_symbol(binding.items[0])
        value = None
        if len(binding.items) > 1:
            value = evaluate(binding.items[1], env, session)
        let_env.define(name, value)
    return _eval_sequence(form.items[2:], let_env, session)


def _eval_lambda(form, env):
    if len(form.items) < 3:
        raise SkillEvalError("lambda requires parameters and body", form=form)
    params_form = form.items[1]
    if not isinstance(params_form, ListForm):
        raise SkillEvalError("lambda parameters must be a list", form=params_form)
    return SkillProcedure("<lambda>", _compile_params(params_form), form.items[2:], env)


def _eval_procedure(form, env):
    if len(form.items) < 3:
        raise SkillEvalError("procedure requires signature and body", form=form)
    signature = form.items[1]
    if not isinstance(signature, ListForm) or not signature.items:
        raise SkillEvalError("procedure signature must be a list", form=signature)
    name = _ensure_symbol(signature.items[0])
    params_form = ListForm(signature.items[1:], signature.line, signature.column, signature.filename)
    proc = SkillProcedure(name, _compile_params(params_form), form.items[2:], env)
    env.set(name, proc)
    return proc


def _eval_setq(form, env, session):
    if len(form.items) < 3 or len(form.items[1:]) % 2 != 0:
        raise SkillEvalError("setq requires symbol/value pairs", form=form)
    result = None
    items = form.items[1:]
    index = 0
    while index < len(items):
        name_form = items[index]
        name = _ensure_symbol(name_form)
        value = evaluate(items[index + 1], env, session)
        env.set(name, value)
        result = value
        index += 2
    return result


def _eval_case(form, env, session):
    if len(form.items) < 3:
        raise SkillEvalError("case requires a key and clauses", form=form)
    key = evaluate(form.items[1], env, session)
    for clause in form.items[2:]:
        if not isinstance(clause, ListForm) or not clause.items:
            raise SkillEvalError("invalid case clause", form=clause)
        label_form = clause.items[0]
        labels = label_form.items if isinstance(label_form, ListForm) else [label_form]
        for label in labels:
            if isinstance(label, SymbolForm) and label.name == "t":
                return _eval_sequence(clause.items[1:], env, session)
            if skill_equal(key, datum_from_form(label)):
                return _eval_sequence(clause.items[1:], env, session)
    return None


def _eval_caseq(form, env, session):
    if len(form.items) < 3:
        raise SkillEvalError("caseq requires a key and clauses", form=form)
    key = evaluate(form.items[1], env, session)
    for clause in form.items[2:]:
        if not isinstance(clause, ListForm) or not clause.items:
            raise SkillEvalError("invalid caseq clause", form=clause)
        label_form = clause.items[0]
        labels = label_form.items if isinstance(label_form, ListForm) else [label_form]
        for label in labels:
            if isinstance(label, SymbolForm) and label.name == "t":
                return _eval_sequence(clause.items[1:], env, session)
            if skill_eq(key, datum_from_form(label)):
                return _eval_sequence(clause.items[1:], env, session)
    return None


def _eval_cond(form, env, session):
    for clause in form.items[1:]:
        if not isinstance(clause, ListForm) or not clause.items:
            raise SkillEvalError("invalid cond clause", form=clause)
        test_value = evaluate(clause.items[0], env, session)
        if is_truthy(test_value):
            if len(clause.items) == 1:
                return test_value
            return _eval_sequence(clause.items[1:], env, session)
    return None


def _eval_foreach(form, env, session):
    if len(form.items) < 4:
        raise SkillEvalError("foreach requires a variable, list, and body", form=form)
    name = _ensure_symbol(form.items[1])
    values = evaluate(form.items[2], env, session)
    if values is None:
        return None
    if isinstance(values, SkillTable):
        loop_env = Environment(parent=env)
        loop_env.define(name, None)
        for key in list(values.data.keys()):
            loop_env.set(name, _plist_key_to_value(key))
            _eval_sequence(form.items[3:], loop_env, session)
        return values
    if not isinstance(values, list):
        raise SkillEvalError("foreach expects a list or table", form=form.items[2])
    loop_env = Environment(parent=env)
    loop_env.define(name, None)
    for value in values:
        loop_env.set(name, value)
        _eval_sequence(form.items[3:], loop_env, session)
    return values


def _eval_for(form, env, session):
    if len(form.items) < 5:
        raise SkillEvalError("for requires a variable, start, end, and body", form=form)
    name = _ensure_symbol(form.items[1])
    start = evaluate(form.items[2], env, session)
    end = evaluate(form.items[3], env, session)
    step = 1 if start <= end else -1
    loop_env = Environment(parent=env)
    loop_env.define(name, None)
    current = start
    while (step > 0 and current <= end) or (step < 0 and current >= end):
        loop_env.set(name, current)
        _eval_sequence(form.items[4:], loop_env, session)
        current += step
    return True


def _eval_defun(form, env):
    if len(form.items) < 4:
        raise SkillEvalError("defun requires a name, parameters, and body", form=form)
    name = _ensure_symbol(form.items[1])
    params_form = form.items[2]
    if not isinstance(params_form, ListForm):
        raise SkillEvalError("defun parameters must be a list", form=params_form)
    proc = SkillProcedure(name, _compile_params(params_form), form.items[3:], env)
    env.set(name, proc)
    return proc


def _eval_defclass(form, env, session):
    if len(form.items) != 4:
        raise SkillEvalError("defclass requires a name, superclass list, and slot list", form=form)
    name = _ensure_symbol(form.items[1])
    bases_form = form.items[2]
    if not isinstance(bases_form, ListForm):
        raise SkillEvalError("defclass superclasses must be a list", form=bases_form)
    if len(bases_form.items) > 1:
        raise SkillEvalError("multiple inheritance is not supported", form=bases_form)
    base_class = None
    if bases_form.items:
        base_name = _ensure_symbol(bases_form.items[0])
        base_class = session.class_registry.get(base_name)
        if base_class is None:
            try:
                base_class = env.get(base_name, form=bases_form.items[0])
            except SkillEvalError:
                base_class = None
        if not isinstance(base_class, SkillClass):
            raise SkillEvalError("unknown superclass `%s`" % base_name, form=bases_form.items[0])
    slots = dict(base_class.slots) if base_class is not None else {}
    for slot in _compile_class_slots(form.items[3]):
        slots[slot["name"]] = slot
    skill_class = SkillClass(name, base_class, slots)
    session.class_registry[name] = skill_class
    env.set(name, skill_class)
    return skill_class


def _eval_defmacro(form, env):
    if len(form.items) < 4:
        raise SkillEvalError("defmacro requires a name, parameters, and body", form=form)
    name = _ensure_symbol(form.items[1])
    params_form = form.items[2]
    if not isinstance(params_form, ListForm):
        raise SkillEvalError("defmacro parameters must be a list", form=params_form)
    macro = SkillMacro(name, _compile_params(params_form), form.items[3:], env)
    env.set(name, macro)
    return macro


def _eval_mprocedure(form, env):
    if len(form.items) < 3:
        raise SkillEvalError("mprocedure requires signature and body", form=form)
    signature = form.items[1]
    if not isinstance(signature, ListForm) or not signature.items:
        raise SkillEvalError("mprocedure signature must be a list", form=signature)
    name = _ensure_symbol(signature.items[0])
    params_form = ListForm(signature.items[1:], signature.line, signature.column, signature.filename)
    compiled = _compile_params(params_form)
    if len(compiled["required"]) != 1 or compiled["optional"] or compiled["key"] or compiled["rest"]:
        raise SkillEvalError("mprocedure requires a single formal argument", form=signature)
    macro = SkillMacro(name, compiled, form.items[2:], env, whole_form=True)
    env.set(name, macro)
    return macro


def _eval_errset(form, env, session):
    try:
        result = _eval_sequence(form.items[1:], env, session)
    except SkillError:
        return None
    return [result]


def _evaluate_call_arg(form, env, session):
    return evaluate(form, env, session)


def _evaluate_procedure_call_args(operator, arg_forms, env, session):
    if isinstance(operator, BuiltinFunction) and operator.name == "makeInstance":
        args = []
        for index, form in enumerate(arg_forms):
            if index > 0 and index % 2 == 1 and isinstance(form, SymbolForm) and form.name.startswith("?"):
                args.append(SkillSymbolValue(form.name))
            else:
                args.append(_evaluate_call_arg(form, env, session))
        return args
    if not isinstance(operator, SkillProcedure) or not operator.params["key"]:
        return [_evaluate_call_arg(arg, env, session) for arg in arg_forms]
    args = []
    position = 0
    positional_limit = len(operator.params["required"]) + len(operator.params["optional"])
    key_names = {name for name, _ in operator.params["key"]}
    while position < len(arg_forms):
        form = arg_forms[position]
        if position >= positional_limit and isinstance(form, SymbolForm) and form.name.startswith("?") and form.name[1:] in key_names:
            args.append(SkillSymbolValue(form.name))
            position += 1
            continue
        args.append(_evaluate_call_arg(form, env, session))
        position += 1
    return args


def _eval_exists_form(form, env, session):
    if len(form.items) != 4:
        raise SkillEvalError("exists requires variable, list, and test", form=form)
    name = _ensure_symbol(form.items[1])
    values = evaluate(form.items[2], env, session)
    if values is None:
        return None
    values = _ensure_list_value(values, "exists")
    loop_env = Environment(parent=env)
    loop_env.define(name, None)
    for index, value in enumerate(values):
        loop_env.set(name, value)
        if is_truthy(evaluate(form.items[3], loop_env, session)):
            return values[index:]
    return None


def _eval_forall_form(form, env, session):
    if len(form.items) != 4:
        raise SkillEvalError("forall requires variable, list, and test", form=form)
    name = _ensure_symbol(form.items[1])
    values = evaluate(form.items[2], env, session)
    if values is None:
        return True
    values = _ensure_list_value(values, "forall")
    loop_env = Environment(parent=env)
    loop_env.define(name, None)
    for value in values:
        loop_env.set(name, value)
        if not is_truthy(evaluate(form.items[3], loop_env, session)):
            return None
    return True


def _eval_catch(form, env, session):
    if len(form.items) < 3:
        raise SkillEvalError("catch requires tag and body", form=form)
    tag = evaluate(form.items[1], env, session)
    try:
        return _eval_sequence(form.items[2:], env, session)
    except SkillThrow as exc:
        if skill_equal(exc.tag, tag):
            return exc.value
        raise


def _eval_prog(form, env, session):
    if len(form.items) < 2:
        raise SkillEvalError("prog requires a binding list", form=form)
    bindings_form = form.items[1]
    if not isinstance(bindings_form, ListForm):
        raise SkillEvalError("prog bindings must be a list", form=bindings_form)
    prog_env = Environment(parent=env)
    for binding in bindings_form.items:
        if isinstance(binding, SymbolForm):
            prog_env.define(binding.name, None)
            continue
        if not isinstance(binding, ListForm) or not binding.items:
            raise SkillEvalError("invalid prog binding", form=binding)
        name = _ensure_symbol(binding.items[0])
        value = None
        if len(binding.items) > 1:
            value = evaluate(binding.items[1], env, session)
        prog_env.define(name, value)
    try:
        return _eval_sequence(form.items[2:], prog_env, session)
    except ReturnFromProg as exc:
        return exc.value


def evaluate(form, env, session):
    if isinstance(form, NumberForm):
        return form.value
    if isinstance(form, StringForm):
        return form.value
    if isinstance(form, SymbolForm):
        if form.name == "nil":
            return None
        if form.name == "t":
            return True
        return env.get(form.name, form=form)
    if not isinstance(form, ListForm):
        raise SkillEvalError("unknown form", form=form)
    if not form.items:
        return None
    head = form.items[0]
    if isinstance(head, SymbolForm):
        if head.name == "quote":
            if len(form.items) != 2:
                raise SkillEvalError("quote expects one value", form=form)
            return datum_from_form(form.items[1])
        if head.name == "quasiquote":
            if len(form.items) != 2:
                raise SkillEvalError("quasiquote expects one value", form=form)
            return eval_quasiquote(form.items[1], env, session)
        if head.name == "if":
            if len(form.items) not in (3, 4):
                raise SkillEvalError("if expects condition, then, optional else", form=form)
            branch = form.items[2] if is_truthy(evaluate(form.items[1], env, session)) else (
                form.items[3] if len(form.items) == 4 else None
            )
            return None if branch is None else evaluate(branch, env, session)
        if head.name == "when":
            if len(form.items) < 3:
                raise SkillEvalError("when requires condition and body", form=form)
            if is_truthy(evaluate(form.items[1], env, session)):
                return _eval_sequence(form.items[2:], env, session)
            return None
        if head.name == "unless":
            if len(form.items) < 3:
                raise SkillEvalError("unless requires condition and body", form=form)
            if not is_truthy(evaluate(form.items[1], env, session)):
                return _eval_sequence(form.items[2:], env, session)
            return None
        if head.name == "progn":
            return _eval_sequence(form.items[1:], env, session)
        if head.name == "let":
            return _eval_let(form, env, session)
        if head.name == "setq":
            return _eval_setq(form, env, session)
        if head.name == "lambda":
            return _eval_lambda(form, env)
        if head.name == "procedure":
            return _eval_procedure(form, env)
        if head.name == "case":
            return _eval_case(form, env, session)
        if head.name == "caseq":
            return _eval_caseq(form, env, session)
        if head.name == "cond":
            return _eval_cond(form, env, session)
        if head.name == "catch":
            return _eval_catch(form, env, session)
        if head.name == "throw":
            if len(form.items) != 3:
                raise SkillEvalError("throw requires tag and value", form=form)
            raise SkillThrow(evaluate(form.items[1], env, session), evaluate(form.items[2], env, session))
        if head.name == "foreach":
            return _eval_foreach(form, env, session)
        if head.name == "for":
            return _eval_for(form, env, session)
        if head.name == "exists" and len(form.items) == 4 and isinstance(form.items[1], SymbolForm):
            return _eval_exists_form(form, env, session)
        if head.name == "forall" and len(form.items) == 4 and isinstance(form.items[1], SymbolForm):
            return _eval_forall_form(form, env, session)
        if head.name == "prog":
            return _eval_prog(form, env, session)
        if head.name == "prog1":
            if len(form.items) < 2:
                raise SkillEvalError("prog1 requires at least one form", form=form)
            first = evaluate(form.items[1], env, session)
            _eval_sequence(form.items[2:], env, session)
            return first
        if head.name == "prog2":
            if len(form.items) < 3:
                raise SkillEvalError("prog2 requires at least two forms", form=form)
            evaluate(form.items[1], env, session)
            second = evaluate(form.items[2], env, session)
            _eval_sequence(form.items[3:], env, session)
            return second
        if head.name == "return":
            if len(form.items) > 2:
                raise SkillEvalError("return expects zero or one value", form=form)
            value = evaluate(form.items[1], env, session) if len(form.items) == 2 else None
            raise ReturnFromProg(value)
        if head.name == "defun":
            return _eval_defun(form, env)
        if head.name == "defclass":
            return _eval_defclass(form, env, session)
        if head.name == "defmacro":
            return _eval_defmacro(form, env)
        if head.name == "nprocedure":
            return _eval_procedure(form, env)
        if head.name == "mprocedure":
            return _eval_mprocedure(form, env)
        if head.name == "errset":
            return _eval_errset(form, env, session)
        if head.name == "while":
            result = None
            while is_truthy(evaluate(form.items[1], env, session)):
                result = _eval_sequence(form.items[2:], env, session)
            return result
        if head.name == "and":
            result = True
            for item in form.items[1:]:
                result = evaluate(item, env, session)
                if not is_truthy(result):
                    return None
            return result
        if head.name == "or":
            for item in form.items[1:]:
                value = evaluate(item, env, session)
                if is_truthy(value):
                    return value
            return None
        if head.name == "sprintf":
            if len(form.items) < 2:
                raise SkillEvalError("sprintf expects at least a format string", form=form)
            target_name = None
            start_index = 1
            if isinstance(form.items[1], SymbolForm):
                if form.items[1].name == "nil":
                    start_index = 2
                else:
                    is_bound = True
                    try:
                        current_value = env.get(form.items[1].name)
                    except SkillEvalError:
                        is_bound = False
                        current_value = None
                    if (not is_bound) or current_value is None or (len(form.items) > 2 and isinstance(form.items[2], StringForm)):
                        target_name = form.items[1].name
                        start_index = 2
            if len(form.items) <= start_index:
                raise SkillEvalError("sprintf requires a format string", form=form)
            fmt = evaluate(form.items[start_index], env, session)
            values = tuple(_evaluate_call_arg(arg, env, session) for arg in form.items[start_index + 1 :])
            text = fmt % values if values else fmt
            if target_name is not None:
                env.set(target_name, text)
            return text
        if head.name == "->":
            if len(form.items) != 3:
                raise SkillEvalError("-> expects a target and slot name", form=form)
            return _get_slot_value(session, _evaluate_slot_target(form.items[1], env, session), _ensure_symbol(form.items[2]), form)
        if head.name == "->=":
            if len(form.items) != 4:
                raise SkillEvalError("->= expects a target, slot name, and value", form=form)
            value = evaluate(form.items[3], env, session)
            return _set_slot_value(
                session,
                _evaluate_slot_target(form.items[1], env, session),
                _ensure_symbol(form.items[2]),
                value,
                form,
            )
    operator = evaluate(head, env, session)
    if isinstance(operator, SkillMacro):
        expansion = operator.expand(session, env, form.items[1:], full_form=form)
        return evaluate(form_from_datum(expansion, filename=form.filename, line=form.line, column=form.column), env, session)
    args = _evaluate_procedure_call_args(operator, form.items[1:], env, session)
    previous_env = getattr(session, "current_env", None)
    session.current_env = env
    try:
        if isinstance(operator, SkillProcedure):
            return operator.invoke(session, env, *args)
        if isinstance(operator, SkillMacro):
            return operator.expand(session, env, form.items[1:], full_form=form)
        if callable(operator):
            return operator(session, *args)
    finally:
        session.current_env = previous_env
    raise SkillEvalError("first element is not callable", form=head)


def _require_args(name, args, minimum=None, exact=None):
    if exact is not None and len(args) != exact:
        raise SkillEvalError("%s expects %s arguments, got %s" % (name, exact, len(args)))
    if minimum is not None and len(args) < minimum:
        raise SkillEvalError("%s expects at least %s arguments, got %s" % (name, minimum, len(args)))


def _builtin_plus(session, *args):
    return sum(args) if args else 0


def _builtin_minus(session, *args):
    _require_args("-", args, minimum=1)
    if len(args) == 1:
        return -args[0]
    result = args[0]
    for value in args[1:]:
        result -= value
    return result


def _builtin_multiply(session, *args):
    result = 1
    for value in args:
        result *= value
    return result


def _builtin_divide(session, *args):
    _require_args("/", args, minimum=1)
    integer_mode = all(isinstance(value, int) and not isinstance(value, bool) for value in args)
    if len(args) == 1:
        result = 1 / args[0]
        return int(result) if integer_mode else result
    result = args[0]
    for value in args[1:]:
        result = int(result / value) if integer_mode else (result / value)
    return result


def _builtin_mod(session, *args):
    _require_args("mod", args, exact=2)
    return args[0] % args[1]


def _builtin_list(session, *args):
    return list(args)


def _builtin_cons(session, *args):
    _require_args("cons", args, exact=2)
    tail = args[1]
    if tail is None:
        tail = []
    if not isinstance(tail, list):
        raise SkillEvalError("cons expects a list tail")
    return [args[0]] + tail


def _builtin_ncons(session, *args):
    _require_args("ncons", args, exact=1)
    return [args[0]]


def _builtin_xcons(session, *args):
    _require_args("xcons", args, exact=2)
    return _builtin_cons(session, args[1], args[0])


def _builtin_car(session, *args):
    _require_args("car", args, exact=1)
    value = args[0]
    if not value:
        return None
    if not isinstance(value, list):
        raise SkillEvalError("car expects a list")
    return value[0]


def _builtin_cdr(session, *args):
    _require_args("cdr", args, exact=1)
    value = args[0]
    if not value:
        return []
    if not isinstance(value, list):
        raise SkillEvalError("cdr expects a list")
    return value[1:]


def _builtin_append(session, *args):
    result = []
    for value in args:
        if value is None:
            continue
        if not isinstance(value, list):
            raise SkillEvalError("append expects lists")
        result.extend(value)
    return result


def _builtin_length(session, *args):
    _require_args("length", args, exact=1)
    value = args[0]
    if value is None:
        return 0
    if isinstance(value, SkillArray):
        return len(value.values)
    return len(value)


def _builtin_nth(session, *args):
    _require_args("nth", args, exact=2)
    index, values = args
    if not isinstance(values, list):
        raise SkillEvalError("nth expects a list")
    return values[index]


def _builtin_last(session, *args):
    _require_args("last", args, exact=1)
    values = args[0]
    if not values:
        return None
    if not isinstance(values, list):
        raise SkillEvalError("last expects a list")
    return values[-1:]


def _builtin_member(session, *args):
    _require_args("member", args, exact=2)
    needle, values = args
    if not isinstance(values, list):
        raise SkillEvalError("member expects a list")
    for index, value in enumerate(values):
        if skill_equal(needle, value):
            return values[index:]
    return None


def _builtin_memq(session, *args):
    _require_args("memq", args, exact=2)
    needle, values = args
    values = _ensure_list_value(values, "memq")
    for index, value in enumerate(values):
        if skill_eq(needle, value):
            return values[index:]
    return None


def _builtin_assoc(session, *args):
    _require_args("assoc", args, exact=2)
    needle, values = args
    if not isinstance(values, list):
        raise SkillEvalError("assoc expects a list")
    for item in values:
        if isinstance(item, list) and item and skill_equal(item[0], needle):
            return item
    return None


def _builtin_assq(session, *args):
    _require_args("assq", args, exact=2)
    needle, values = args
    values = _ensure_list_value(values, "assq")
    for item in values:
        if isinstance(item, list) and item and skill_eq(item[0], needle):
            return item
    return None


def _builtin_boundp(session, *args):
    _require_args("boundp", args, exact=1)
    value = args[0]
    if not isinstance(value, SkillSymbolValue):
        return None
    try:
        session.global_env.get(value.name)
    except SkillEvalError:
        return None
    return True


def _builtin_mapcar(session, *args):
    _require_args("mapcar", args, exact=2)
    proc, values = args
    if values is None:
        return None
    if not isinstance(values, list):
        raise SkillEvalError("mapcar expects a list")
    result = []
    for item in values:
        result.append(_invoke_callable(session, proc, item))
    return result


def _builtin_map(session, *args):
    return _builtin_mapcar(session, *args)


def _invoke_callable(session, proc, *args):
    env = getattr(session, "current_env", None) or session.global_env
    if isinstance(proc, SkillProcedure):
        return proc.invoke(session, env, *args)
    if callable(proc):
        return proc(session, *args)
    raise SkillEvalError("expected a callable value")


def _builtin_apply(session, *args):
    _require_args("apply", args, minimum=2)
    proc = args[0]
    prefix = list(args[1:-1])
    final_args = args[-1]
    if final_args is None:
        final_args = []
    if not isinstance(final_args, list):
        raise SkillEvalError("apply expects the last argument to be a list")
    return _invoke_callable(session, proc, *(prefix + final_args))


def _builtin_funcall(session, *args):
    _require_args("funcall", args, minimum=1)
    return _invoke_callable(session, args[0], *args[1:])


def _builtin_reverse(session, *args):
    _require_args("reverse", args, exact=1)
    value = args[0]
    if value is None:
        return None
    if not isinstance(value, list):
        raise SkillEvalError("reverse expects a list")
    return list(reversed(value))


def _builtin_append1(session, *args):
    _require_args("append1", args, exact=2)
    values, item = args
    if values is None:
        values = []
    if not isinstance(values, list):
        raise SkillEvalError("append1 expects a list")
    return values + [item]


def _builtin_copylist(session, *args):
    _require_args("copylist", args, exact=1)
    return list(_ensure_list_value(args[0], "copylist"))


def _builtin_lindex(session, *args):
    _require_args("lindex", args, exact=2)
    needle, values = args
    values = _ensure_list_value(values, "lindex")
    for index, value in enumerate(values):
        if skill_equal(needle, value):
            return index
    return None


def _builtin_set(session, *args):
    _require_args("set", args, exact=2)
    symbol, value = args
    if not isinstance(symbol, SkillSymbolValue):
        raise SkillEvalError("set expects a quoted symbol")
    env = getattr(session, "current_env", None) or session.global_env
    env.set(symbol.name, value)
    return value


def _builtin_copy(session, *args):
    _require_args("copy", args, exact=1)
    value = args[0]
    if isinstance(value, list):
        return list(value)
    return value


def _builtin_nthcdr(session, *args):
    _require_args("nthcdr", args, exact=2)
    index, values = args
    values = _ensure_list_value(values, "nthcdr")
    return values[index:]


def _builtin_nthelem(session, *args):
    _require_args("nthelem", args, exact=2)
    index, values = args
    values = _ensure_list_value(values, "nthelem")
    return values[index - 1]


def _builtin_remove_common(args, name, use_eq=False):
    _require_args(name, args, exact=2)
    needle, values = args
    values = _ensure_list_value(values, name)
    matcher = skill_eq if use_eq else skill_equal
    return [value for value in values if not matcher(needle, value)]


def _builtin_remove(session, *args):
    return _builtin_remove_common(args, "remove", use_eq=False)


def _builtin_remq(session, *args):
    return _builtin_remove_common(args, "remq", use_eq=True)


def _builtin_remd_common(args, name, use_eq=False):
    _require_args(name, args, exact=2)
    needle, values = args
    values = _ensure_list_value(values, name)
    matcher = skill_eq if use_eq else skill_equal
    values[:] = [value for value in values if not matcher(needle, value)]
    return values if values else None


def _builtin_remd(session, *args):
    return _builtin_remd_common(args, "remd", use_eq=False)


def _builtin_remdq(session, *args):
    return _builtin_remd_common(args, "remdq", use_eq=True)


def _builtin_nconc(session, *args):
    if not args:
        return None
    result = None
    current = None
    for value in args:
        if value is None:
            continue
        if not isinstance(value, list):
            raise SkillEvalError("nconc expects lists")
        if result is None:
            result = value
            current = result
            continue
        current.extend(value)
    return result


def _builtin_rplaca(session, *args):
    _require_args("rplaca", args, exact=2)
    values = _ensure_list_value(args[0], "rplaca")
    if not values:
        raise SkillEvalError("rplaca expects a non-empty list")
    values[0] = args[1]
    return values


def _builtin_rplacd(session, *args):
    _require_args("rplacd", args, exact=2)
    values = _ensure_list_value(args[0], "rplacd")
    tail = args[1]
    tail = [] if tail is None else _ensure_list_value(tail, "rplacd")
    if not values:
        raise SkillEvalError("rplacd expects a non-empty list")
    values[1:] = tail
    return values


def _builtin_tailp(session, *args):
    _require_args("tailp", args, exact=2)
    tail, values = args
    values = _ensure_list_value(values, "tailp")
    if tail is None:
        return True
    if not isinstance(tail, list):
        return None
    for index in range(len(values) + 1):
        if skill_equal(values[index:], tail):
            return True
    return None


def _subst_value(new_value, old_value, tree):
    if skill_equal(tree, old_value):
        return new_value
    if isinstance(tree, list):
        return [_subst_value(new_value, old_value, item) for item in tree]
    return tree


def _builtin_subst(session, *args):
    _require_args("subst", args, exact=3)
    return _subst_value(args[0], args[1], args[2])


def _builtin_type(session, *args):
    _require_args("type", args, exact=1)
    value = args[0]
    if value is None or value == []:
        return SkillSymbolValue("nil")
    if value is True or value is False:
        return SkillSymbolValue("boolean")
    if isinstance(value, int):
        return SkillSymbolValue("integer")
    if isinstance(value, float):
        return SkillSymbolValue("float")
    if isinstance(value, str):
        return SkillSymbolValue("string")
    if isinstance(value, list):
        return SkillSymbolValue("list")
    if isinstance(value, SkillArray):
        return SkillSymbolValue("array")
    if isinstance(value, SkillSymbolValue):
        return SkillSymbolValue("symbol")
    if isinstance(value, SkillClass):
        return SkillSymbolValue("class")
    if isinstance(value, SkillInstance):
        return SkillSymbolValue(value.skill_class.name)
    if isinstance(value, (BuiltinFunction, SkillProcedure, SkillMacro)):
        return SkillSymbolValue("function")
    return SkillSymbolValue(type(value).__name__)


def _builtin_typep(session, *args):
    _require_args("typep", args, exact=2)
    value, type_name = args
    if isinstance(type_name, SkillSymbolValue):
        type_name = type_name.name
    return True if format_value(_builtin_type(session, value)) == str(type_name) else None


def _builtin_eval(session, *args):
    _require_args("eval", args, exact=1)
    env = getattr(session, "current_env", None) or session.global_env
    return evaluate(form_from_datum(args[0]), env, session)


def _builtin_symeval(session, *args):
    _require_args("symeval", args, exact=1)
    env = getattr(session, "current_env", None) or session.global_env
    return env.get(_require_symbol_value(args[0], "symeval"))


def _builtin_getd(session, *args):
    _require_args("getd", args, exact=1)
    env = getattr(session, "current_env", None) or session.global_env
    return env.get(_require_symbol_value(args[0], "getd"))


def _builtin_putd(session, *args):
    _require_args("putd", args, exact=2)
    env = getattr(session, "current_env", None) or session.global_env
    symbol_name = _require_symbol_value(args[0], "putd")
    env.set(symbol_name, args[1])
    return args[1]


def _builtin_makunbound(session, *args):
    _require_args("makunbound", args, exact=1)
    env = getattr(session, "current_env", None) or session.global_env
    symbol_name = _require_symbol_value(args[0], "makunbound")
    if symbol_name in env.values:
        del env.values[symbol_name]
        return True
    return None

def _builtin_gensym(session, *args):
    prefix = args[0] if args else "G"
    if isinstance(prefix, SkillSymbolValue):
        prefix = prefix.name
    session.gensym_counter += 1
    return SkillSymbolValue("%s%s" % (prefix, session.gensym_counter))


def _builtin_plist(session, *args):
    _require_args("plist", args, exact=1)
    symbol_name = _require_symbol_value(args[0], "plist")
    values = _plist_for_symbol(session, symbol_name)
    return values if values else None


def _builtin_intern(session, *args):
    _require_args("intern", args, exact=1)
    return SkillSymbolValue(args[0])


def _builtin_symbol_name(session, *args):
    _require_args("symbolName", args, exact=1)
    return _require_symbol_value(args[0], "symbolName")


def _builtin_setplist(session, *args):
    _require_args("setplist", args, exact=2)
    symbol_name = _require_symbol_value(args[0], "setplist")
    values = _ensure_list_value(args[1], "setplist")
    stored = _set_plist_for_symbol(session, symbol_name, values)
    return stored if stored else None


def _builtin_make_instance(session, *args):
    if not args:
        raise SkillEvalError("makeInstance expects a class and optional initargs")
    skill_class = _resolve_class_reference(session, args[0], "makeInstance")
    if (len(args) - 1) % 2 != 0:
        raise SkillEvalError("makeInstance expects ?initarg/value pairs")
    provided = {}
    index = 1
    while index < len(args):
        initarg = args[index]
        if not isinstance(initarg, SkillSymbolValue) or not initarg.name.startswith("?"):
            raise SkillEvalError("makeInstance expects ?initarg/value pairs")
        if initarg.name in provided:
            raise SkillEvalError("duplicate initarg `%s`" % initarg.name)
        provided[initarg.name] = args[index + 1]
        index += 2
    env = getattr(session, "current_env", None) or session.global_env
    slot_values = {}
    used = set()
    for slot_name, spec in skill_class.slots.items():
        if spec["initarg"] is not None and spec["initarg"] in provided:
            slot_values[slot_name] = provided[spec["initarg"]]
            used.add(spec["initarg"])
        elif spec["initform"] is not None:
            slot_values[slot_name] = evaluate(spec["initform"], env, session)
        else:
            slot_values[slot_name] = None
    unknown = [name for name in provided if name not in used]
    if unknown:
        raise SkillEvalError("unknown initarg `%s`" % unknown[0])
    return SkillInstance(skill_class, slot_values)


def _builtin_get(session, *args):
    _require_args("get", args, exact=2)
    target, indicator = args
    if isinstance(target, SkillTable):
        return target.data.get(_plist_key(indicator), target.default)
    symbol_name = _require_symbol_value(target, "get")
    return _plist_lookup(session, symbol_name, indicator)


def _builtin_getq(session, *args):
    return _builtin_get(session, *args)


def _builtin_getqq(session, *args):
    return _builtin_get(session, *args)


def _builtin_putprop(session, *args):
    _require_args("putprop", args, exact=3)
    symbol_name = _require_symbol_value(args[0], "putprop")
    return _plist_put(session, symbol_name, args[2], args[1])


def _builtin_putpropq(session, *args):
    return _builtin_putprop(session, *args)


def _builtin_putpropqq(session, *args):
    return _builtin_putprop(session, *args)


def _builtin_defprop(session, *args):
    return _builtin_putprop(session, *args)


def _builtin_remprop(session, *args):
    _require_args("remprop", args, exact=2)
    symbol_name = _require_symbol_value(args[0], "remprop")
    return _plist_remove(session, symbol_name, args[1])


def _builtin_eq(session, *args):
    _require_args("eq", args, exact=2)
    return True if skill_eq(args[0], args[1]) else None


def _builtin_equal(session, *args):
    _require_args("equal", args, exact=2)
    return True if skill_equal(args[0], args[1]) else None


def _builtin_neq(session, *args):
    _require_args("neq", args, exact=2)
    return None if skill_eq(args[0], args[1]) else True


def _builtin_nequal(session, *args):
    _require_args("nequal", args, exact=2)
    return None if skill_equal(args[0], args[1]) else True


def _builtin_null(session, *args):
    _require_args("null", args, exact=1)
    value = args[0]
    return True if value is None or value is False or value == [] else None


def _builtin_atom(session, *args):
    _require_args("atom", args, exact=1)
    return None if isinstance(args[0], list) else True


def _builtin_listp(session, *args):
    _require_args("listp", args, exact=1)
    return True if isinstance(args[0], list) or args[0] is None else None


def _builtin_pairp(session, *args):
    _require_args("pairp", args, exact=1)
    return True if isinstance(args[0], list) and len(args[0]) >= 1 else None


def _builtin_dtpr(session, *args):
    return _builtin_pairp(session, *args)


def _builtin_symbolp(session, *args):
    _require_args("symbolp", args, exact=1)
    return True if isinstance(args[0], SkillSymbolValue) else None


def _builtin_stringp(session, *args):
    _require_args("stringp", args, exact=1)
    return True if isinstance(args[0], str) else None


def _builtin_numberp(session, *args):
    _require_args("numberp", args, exact=1)
    return True if isinstance(args[0], (int, float)) else None


def _builtin_integerp(session, *args):
    _require_args("integerp", args, exact=1)
    return True if isinstance(args[0], int) and not isinstance(args[0], bool) else None


def _builtin_floatp(session, *args):
    _require_args("floatp", args, exact=1)
    return True if isinstance(args[0], float) else None


def _builtin_zerop(session, *args):
    _require_args("zerop", args, exact=1)
    return True if args[0] == 0 else None


def _builtin_plusp(session, *args):
    _require_args("plusp", args, exact=1)
    return True if args[0] > 0 else None


def _builtin_onep(session, *args):
    _require_args("onep", args, exact=1)
    return True if args[0] == 1 else None


def _builtin_minusp(session, *args):
    _require_args("minusp", args, exact=1)
    return True if args[0] < 0 else None


def _builtin_evenp(session, *args):
    _require_args("evenp", args, exact=1)
    return True if args[0] % 2 == 0 else None


def _builtin_oddp(session, *args):
    _require_args("oddp", args, exact=1)
    return True if args[0] % 2 != 0 else None


def _builtin_fixp(session, *args):
    return _builtin_integerp(session, *args)


def _builtin_compare(op):
    def inner(session, *args):
        _require_args(op, args, minimum=2)
        for left, right in zip(args, args[1:]):
            if op == "=" and not left == right:
                return None
            if op == "<" and not left < right:
                return None
            if op == "<=" and not left <= right:
                return None
            if op == ">" and not left > right:
                return None
            if op == ">=" and not left >= right:
                return None
        return True

    return inner


def _builtin_not(session, *args):
    _require_args("not", args, exact=1)
    return True if not is_truthy(args[0]) else None


def _builtin_print(session, *args):
    text = " ".join(format_value(arg) for arg in args)
    session.output.append(text)
    return True


def _builtin_println(session, *args):
    return _builtin_print(session, *args)


def _builtin_printf(session, *args):
    _require_args("printf", args, minimum=1)
    fmt = args[0]
    values = tuple(args[1:])
    text = fmt % values if values else fmt
    session.output.append(text)
    return True


def _builtin_sprintf(session, *args):
    _require_args("sprintf", args, minimum=1)
    fmt = args[0]
    values = tuple(args[1:])
    return fmt % values if values else fmt


def _builtin_strcat(session, *args):
    return "".join(str(arg) for arg in args)


def _builtin_concat(session, *args):
    return SkillSymbolValue("".join(str(arg) for arg in args))


def _builtin_strlen(session, *args):
    _require_args("strlen", args, exact=1)
    return len(args[0])


def _builtin_strcmp(session, *args):
    _require_args("strcmp", args, exact=2)
    left, right = args
    if left == right:
        return 0
    return -1 if left < right else 1


def _builtin_alpha_lessp(session, *args):
    _require_args("alphalessp", args, exact=2)
    return True if args[0] < args[1] else None


def _builtin_substr(session, *args):
    _require_args("substr", args, minimum=2)
    text = args[0]
    start = args[1]
    length = args[2] if len(args) > 2 else None
    if length is None:
        return text[start:]
    return text[start : start + length]


def _builtin_substring(session, *args):
    _require_args("substring", args, minimum=2)
    text = args[0]
    start = args[1] - 1
    length = args[2] if len(args) > 2 else None
    if length is None:
        return text[start:]
    return text[start : start + length]


def _builtin_getchar(session, *args):
    _require_args("getchar", args, exact=2)
    text, index = args
    if isinstance(text, SkillSymbolValue):
        text = text.name
    if index < 1 or index > len(text):
        return None
    return SkillSymbolValue(text[index - 1])


def _builtin_index_common(args, name, reverse=False, start=None):
    _require_args(name, args, exact=2)
    needle, text = args
    if reverse:
        position = text.rfind(needle)
    else:
        position = text.find(needle, start or 0)
    return (position + 1) if position >= 0 else None


def _builtin_index(session, *args):
    return _builtin_index_common(args, "index")


def _builtin_rindex(session, *args):
    return _builtin_index_common(args, "rindex", reverse=True)


def _builtin_nindex(session, *args):
    _require_args("nindex", args, exact=3)
    needle, text, start = args
    position = text.find(needle, start - 1)
    return (position + 1) if position >= 0 else None


def _builtin_upper_case(session, *args):
    _require_args("upperCase", args, exact=1)
    return args[0].upper()


def _builtin_lower_case(session, *args):
    _require_args("lowerCase", args, exact=1)
    return args[0].lower()


def _builtin_build_string(session, *args):
    return "".join(str(arg) for arg in args)


def _builtin_parse_string(session, *args):
    _require_args("parseString", args, minimum=1)
    text = args[0]
    if len(args) == 1:
        pieces = text.strip().split()
        return pieces if pieces else None
    delimiters = args[1]
    parts = []
    current = []
    for char in text:
        if char in delimiters:
            if current:
                parts.append("".join(current))
                current = []
        else:
            current.append(char)
    if current:
        parts.append("".join(current))
    return parts if parts else None


def _ensure_regex(value, name):
    if isinstance(value, SkillRegex):
        return value
    if isinstance(value, str):
        return SkillRegex(value)
    raise SkillEvalError("%s expects a pattern string or compiled regex" % name)


def _builtin_rex_compile(session, *args):
    _require_args("rexCompile", args, exact=1)
    return _ensure_regex(args[0], "rexCompile")


def _builtin_rex_execute(session, *args):
    _require_args("rexExecute", args, exact=2)
    regex = _ensure_regex(args[0], "rexExecute")
    match = regex.compiled.search(args[1])
    return True if match else None


def _builtin_rex_matchp(session, *args):
    _require_args("rexMatchp", args, exact=2)
    return _builtin_rex_execute(session, *args)


def _builtin_rex_replace(session, *args):
    _require_args("rexReplace", args, exact=3)
    regex = _ensure_regex(args[0], "rexReplace")
    return regex.compiled.sub(args[1], args[2])


def _builtin_rex_substitute(session, *args):
    return _builtin_rex_replace(session, *args)


def _builtin_atoi(session, *args):
    _require_args("atoi", args, exact=1)
    return int(args[0])


def _builtin_atof(session, *args):
    _require_args("atof", args, exact=1)
    return float(args[0])


def _builtin_fix(session, *args):
    _require_args("fix", args, exact=1)
    return int(args[0])


def _builtin_float(session, *args):
    _require_args("float", args, exact=1)
    return float(args[0])


def _builtin_abs(session, *args):
    _require_args("abs", args, exact=1)
    return abs(args[0])


def _builtin_min(session, *args):
    _require_args("min", args, minimum=1)
    return min(args)


def _builtin_max(session, *args):
    _require_args("max", args, minimum=1)
    return max(args)


def _builtin_add1(session, *args):
    _require_args("add1", args, exact=1)
    return args[0] + 1


def _builtin_sub1(session, *args):
    _require_args("sub1", args, exact=1)
    return args[0] - 1


def _builtin_round(session, *args):
    _require_args("round", args, exact=1)
    value = args[0]
    if value >= 0:
        return int(math.floor(value + 0.5))
    return int(math.ceil(value - 0.5))


def _builtin_expt(session, *args):
    _require_args("expt", args, exact=2)
    return args[0] ** args[1]


def _builtin_remainder(session, *args):
    _require_args("remainder", args, exact=2)
    left, right = args
    value = math.fmod(left, right)
    if isinstance(left, int) and isinstance(right, int):
        return int(value)
    return value


def _builtin_leftshift(session, *args):
    _require_args("leftshift", args, exact=2)
    return args[0] << args[1]


def _builtin_rightshift(session, *args):
    _require_args("rightshift", args, exact=2)
    return args[0] >> args[1]


def _builtin_exp(session, *args):
    _require_args("exp", args, exact=1)
    return math.exp(args[0])


def _builtin_log(session, *args):
    _require_args("log", args, exact=1)
    return math.log(args[0])


def _builtin_sqrt(session, *args):
    _require_args("sqrt", args, exact=1)
    return math.sqrt(args[0])


def _builtin_sin(session, *args):
    _require_args("sin", args, exact=1)
    return math.sin(args[0])


def _builtin_cos(session, *args):
    _require_args("cos", args, exact=1)
    return math.cos(args[0])


def _builtin_tan(session, *args):
    _require_args("tan", args, exact=1)
    return math.tan(args[0])


def _builtin_asin(session, *args):
    _require_args("asin", args, exact=1)
    return math.asin(args[0])


def _builtin_acos(session, *args):
    _require_args("acos", args, exact=1)
    return math.acos(args[0])


def _builtin_atan(session, *args):
    _require_args("atan", args, exact=1)
    return math.atan(args[0])


def _builtin_random(session, *args):
    limit = args[0] if args else None
    if limit is None:
        return session.random_state.random()
    return session.random_state.randrange(limit)


def _builtin_srandom(session, *args):
    _require_args("srandom", args, exact=1)
    session.random_state.seed(args[0])
    return True


def _builtin_array(session, *args):
    _require_args("array", args, minimum=1)
    size = args[0]
    init = args[1] if len(args) > 1 else None
    return SkillArray([init for _ in range(size)])


def _builtin_arrayref(session, *args):
    _require_args("arrayref", args, exact=2)
    values, index = args
    return _ensure_array_value(values, "arrayref")[index]


def _builtin_setarray(session, *args):
    _require_args("setarray", args, exact=3)
    values, index, value = args
    _ensure_array_value(values, "setarray")[index] = value
    return value


def _builtin_arrayp(session, *args):
    _require_args("arrayp", args, exact=1)
    return True if isinstance(args[0], SkillArray) else None


def _builtin_portp(session, *args):
    _require_args("portp", args, exact=1)
    return True if isinstance(args[0], SkillPort) and args[0].handle is not None else None


def _builtin_make_table(session, *args):
    _require_args("makeTable", args, minimum=1)
    name = args[0]
    default = args[1] if len(args) > 1 else None
    return SkillTable(name=name if isinstance(name, str) else format_value(name), default=default)


def _builtin_put(session, *args):
    _require_args("put", args, exact=3)
    table, key, value = args
    if not isinstance(table, SkillTable):
        raise SkillEvalError("put expects a table")
    table.data[_plist_key(key)] = value
    return value


def _builtin_tablep(session, *args):
    _require_args("tablep", args, exact=1)
    return True if isinstance(args[0], SkillTable) else None


def _builtin_table_to_list(session, *args):
    _require_args("tableToList", args, exact=1)
    table = args[0]
    if not isinstance(table, SkillTable):
        raise SkillEvalError("tableToList expects a table")
    values = []
    for key, value in table.data.items():
        values.extend([_plist_key_to_value(key), value])
    return values


def _builtin_get_table_keys(session, *args):
    _require_args("getTableKeys", args, exact=1)
    table = args[0]
    if not isinstance(table, SkillTable):
        raise SkillEvalError("getTableKeys expects a table")
    return [_plist_key_to_value(key) for key in table.data.keys()]


def _builtin_remove_table_entry(session, *args):
    _require_args("removeTableEntry", args, exact=2)
    table, key = args
    if not isinstance(table, SkillTable):
        raise SkillEvalError("removeTableEntry expects a table")
    normalized = _plist_key(key)
    if normalized not in table.data:
        return None
    del table.data[normalized]
    return True


def _builtin_infile(session, *args):
    _require_args("infile", args, exact=1)
    return SkillPort(open(args[0], "r"), "input")


def _builtin_outfile(session, *args):
    _require_args("outfile", args, exact=1)
    return SkillPort(open(args[0], "w"), "output")


def _builtin_instring(session, *args):
    _require_args("instring", args, exact=1)
    return SkillPort(io.StringIO(args[0]), "input", string_backed=True)


def _builtin_outstring(session, *args):
    _require_args("outstring", args, exact=0)
    return SkillPort(io.StringIO(), "output", string_backed=True)


def _require_open_port(port, name):
    if not isinstance(port, SkillPort) or port.handle is None:
        raise SkillEvalError("%s expects an open port" % name)
    return port


def _builtin_get_outstring(session, *args):
    _require_args("getOutstring", args, exact=1)
    port = _require_open_port(args[0], "getOutstring")
    if not port.string_backed:
        raise SkillEvalError("getOutstring expects a string output port")
    return port.handle.getvalue()


def _builtin_close(session, *args):
    _require_args("close", args, exact=1)
    port = _require_open_port(args[0], "close")
    port.close()
    return True


def _builtin_lineread(session, *args):
    _require_args("lineread", args, exact=1)
    port = _require_open_port(args[0], "lineread")
    line = port.handle.readline()
    if line == "":
        return None
    return line.rstrip("\n")


def _builtin_gets(session, *args):
    _require_args("gets", args, exact=1)
    port = _require_open_port(args[0], "gets")
    line = port.handle.readline()
    return line if line != "" else None


def _builtin_getc(session, *args):
    _require_args("getc", args, exact=1)
    port = _require_open_port(args[0], "getc")
    value = port.handle.read(1)
    return SkillSymbolValue(value) if value != "" else None


def _builtin_fprintf(session, *args):
    _require_args("fprintf", args, minimum=2)
    port = _require_open_port(args[0], "fprintf")
    fmt = args[1]
    values = tuple(args[2:])
    text = fmt % values if values else fmt
    port.handle.write(text)
    return True


def _builtin_fscanf(session, *args):
    _require_args("fscanf", args, minimum=2)
    port = _require_open_port(args[0], "fscanf")
    count = len(args) - 1
    data = port.handle.read().split()
    if len(data) < count:
        return None
    result = data[:count]
    return result if len(result) > 1 else result[0]


def _builtin_eof(session, *args):
    _require_args("eof", args, exact=1)
    port = _require_open_port(args[0], "eof")
    position = port.handle.tell()
    chunk = port.handle.read(1)
    port.handle.seek(position)
    return True if chunk == "" else None


def _builtin_drain(session, *args):
    _require_args("drain", args, exact=1)
    port = _require_open_port(args[0], "drain")
    if hasattr(port.handle, "flush"):
        port.handle.flush()
    return True


def _builtin_file_length(session, *args):
    _require_args("fileLength", args, exact=1)
    port = _require_open_port(args[0], "fileLength")
    position = port.handle.tell()
    port.handle.seek(0, os.SEEK_END)
    length = port.handle.tell()
    port.handle.seek(position)
    return length


def _builtin_file_tell(session, *args):
    _require_args("fileTell", args, exact=1)
    port = _require_open_port(args[0], "fileTell")
    return port.handle.tell()


def _builtin_file_seek(session, *args):
    _require_args("fileSeek", args, exact=2)
    port = _require_open_port(args[0], "fileSeek")
    port.handle.seek(args[1])
    return args[1]


def _builtin_is_file(session, *args):
    _require_args("isFile", args, exact=1)
    return True if os.path.isfile(args[0]) else None


def _builtin_is_dir(session, *args):
    _require_args("isDir", args, exact=1)
    return True if os.path.isdir(args[0]) else None


def _builtin_is_file_name(session, *args):
    _require_args("isFileName", args, exact=1)
    return True if isinstance(args[0], str) and len(args[0]) > 0 else None


def _builtin_create_dir(session, *args):
    _require_args("createDir", args, exact=1)
    os.makedirs(args[0], exist_ok=True)
    return True


def _builtin_get_dir_files(session, *args):
    _require_args("getDirFiles", args, exact=1)
    return sorted(os.listdir(args[0]))


def _builtin_delete_file(session, *args):
    _require_args("deleteFile", args, exact=1)
    os.remove(args[0])
    return True


def _builtin_get_working_dir(session, *args):
    _require_args("getWorkingDir", args, exact=0)
    return session.cwd


def _builtin_change_working_dir(session, *args):
    _require_args("changeWorkingDir", args, exact=1)
    session.cwd = os.path.abspath(args[0])
    return session.cwd


def _builtin_get_skill_path(session, *args):
    _require_args("getSkillPath", args, exact=0)
    return list(session.skill_path)


def _builtin_set_skill_path(session, *args):
    _require_args("setSkillPath", args, exact=1)
    values = _ensure_list_value(args[0], "setSkillPath")
    session.skill_path = [str(value) for value in values]
    return list(session.skill_path)


def _builtin_errsetstring(session, *args):
    _require_args("errsetstring", args, exact=1)
    try:
        return [session.eval_text(args[0], filename="<errsetstring>")]
    except SkillError:
        return None


def _builtin_load(session, *args):
    _require_args("load", args, exact=1)
    return session.load_file(args[0])


def _builtin_warn(session, *args):
    _require_args("warn", args, minimum=1)
    message = " ".join(str(arg) for arg in args)
    session.warnings.append(message)
    session.output.append("Warning: " + message)
    return True


def _builtin_error(session, *args):
    _require_args("error", args, minimum=1)
    raise SkillEvalError(" ".join(str(arg) for arg in args))


def _builtin_get_warn(session, *args):
    _require_args("getWarn", args, exact=0)
    if not session.warnings:
        return None
    return session.warnings.pop(0)


def _builtin_mapc(session, *args):
    _require_args("mapc", args, exact=2)
    proc, values = args
    if values is None:
        return None
    if not isinstance(values, list):
        raise SkillEvalError("mapc expects a list")
    for item in values:
        _invoke_callable(session, proc, item)
    return values


def _builtin_maplist(session, *args):
    _require_args("maplist", args, exact=2)
    proc, values = args
    values = _ensure_list_value(values, "maplist")
    result = []
    for index in range(len(values)):
        result.append(_invoke_callable(session, proc, values[index:]))
    return result


def _builtin_mapcan(session, *args):
    _require_args("mapcan", args, exact=2)
    proc, values = args
    values = _ensure_list_value(values, "mapcan")
    result = []
    for item in values:
        mapped = _invoke_callable(session, proc, item)
        if mapped is None:
            continue
        if not isinstance(mapped, list):
            raise SkillEvalError("mapcan expects mapped values to be lists or nil")
        result.extend(mapped)
    return result if result else None


def _builtin_mapcon(session, *args):
    _require_args("mapcon", args, exact=2)
    proc, values = args
    values = _ensure_list_value(values, "mapcon")
    result = []
    for index in range(len(values)):
        mapped = _invoke_callable(session, proc, values[index:])
        if mapped is None:
            continue
        if not isinstance(mapped, list):
            raise SkillEvalError("mapcon expects mapped values to be lists or nil")
        result.extend(mapped)
    return result if result else None


def _builtin_mapinto(session, *args):
    _require_args("mapinto", args, exact=2)
    proc, values = args
    values = _ensure_list_value(values, "mapinto")
    for index, item in enumerate(list(values)):
        values[index] = _invoke_callable(session, proc, item)
    return values if values else None


def _builtin_setof(session, *args):
    _require_args("setof", args, exact=2)
    proc, values = args
    values = _ensure_list_value(values, "setof")
    result = []
    for item in values:
        if is_truthy(_invoke_callable(session, proc, item)):
            result.append(item)
    return result if result else None


def _builtin_exists(session, *args):
    _require_args("exists", args, exact=2)
    proc, values = args
    if values is None:
        return None
    if not isinstance(values, list):
        raise SkillEvalError("exists expects a list")
    for item in values:
        if is_truthy(_invoke_callable(session, proc, item)):
            return True
    return None


def _builtin_forall(session, *args):
    _require_args("forall", args, exact=2)
    proc, values = args
    if values is None:
        return True
    if not isinstance(values, list):
        raise SkillEvalError("forall expects a list")
    for item in values:
        if not is_truthy(_invoke_callable(session, proc, item)):
            return None
    return True


def _sort_with_predicate(session, values, predicate, key=None):
    def default_sort_value(value):
        if isinstance(value, SkillSymbolValue):
            return value.name
        return value

    def compare(left, right):
        lhs = key(left) if key is not None else left
        rhs = key(right) if key is not None else right
        if predicate is None:
            lhs = default_sort_value(lhs)
            rhs = default_sort_value(rhs)
            if lhs < rhs:
                return -1
            if lhs > rhs:
                return 1
            return 0
        if is_truthy(_invoke_callable(session, predicate, lhs, rhs)):
            return -1
        if is_truthy(_invoke_callable(session, predicate, rhs, lhs)):
            return 1
        return 0

    return sorted(values, key=functools.cmp_to_key(compare))


def _builtin_sort(session, *args):
    _require_args("sort", args, exact=2)
    values, predicate = args
    values = _ensure_list_value(values, "sort")
    values[:] = _sort_with_predicate(session, list(values), predicate)
    return values


def _builtin_sortcar(session, *args):
    _require_args("sortcar", args, exact=2)
    values, predicate = args
    values = _ensure_list_value(values, "sortcar")
    for item in values:
        if not isinstance(item, list) or not item:
            raise SkillEvalError("sortcar expects a list of non-empty lists")
    values[:] = _sort_with_predicate(session, list(values), predicate, key=lambda item: item[0])
    return values


def _builtin_evalstring(session, *args):
    _require_args("evalstring", args, exact=1)
    return session.eval_text(args[0], filename="<evalstring>")


def _builtin_loadstring(session, *args):
    _require_args("loadstring", args, exact=1)
    return session.eval_text(args[0], filename="<loadstring>")


def _builtin_loadi(session, *args):
    _require_args("loadi", args, exact=1)
    return session.load_file(args[0])


def _builtin_macroexpand(session, *args):
    _require_args("macroexpand", args, exact=1)
    env = getattr(session, "current_env", None) or session.global_env
    form = form_from_datum(args[0], filename="<macroexpand>")
    if not isinstance(form, ListForm) or not form.items:
        return args[0]
    operator = evaluate(form.items[0], env, session)
    if not isinstance(operator, SkillMacro):
        return args[0]
    return operator.expand(session, env, form.items[1:], full_form=form)


def _make_cxr(name):
    pattern = name[1:-1]

    def inner(session, value):
        current = value
        for op in reversed(pattern):
            if op == "a":
                current = _builtin_car(session, current)
            else:
                current = _builtin_cdr(session, current)
        return current

    return inner


def create_global_env():
    env = Environment()
    builtins = {
        "+": _builtin_plus,
        "plus": _builtin_plus,
        "-": _builtin_minus,
        "difference": _builtin_minus,
        "*": _builtin_multiply,
        "times": _builtin_multiply,
        "/": _builtin_divide,
        "quotient": _builtin_divide,
        "mod": _builtin_mod,
        "list": _builtin_list,
        "cons": _builtin_cons,
        "ncons": _builtin_ncons,
        "xcons": _builtin_xcons,
        "car": _builtin_car,
        "cdr": _builtin_cdr,
        "cadr": lambda session, value: _builtin_car(session, _builtin_cdr(session, value)),
        "caddr": lambda session, value: _builtin_car(session, _builtin_cdr(session, _builtin_cdr(session, value))),
        "append": _builtin_append,
        "set": _builtin_set,
        "length": _builtin_length,
        "nth": _builtin_nth,
        "last": _builtin_last,
        "member": _builtin_member,
        "memq": _builtin_memq,
        "assoc": _builtin_assoc,
        "assq": _builtin_assq,
        "append1": _builtin_append1,
        "copy": _builtin_copy,
        "copylist": _builtin_copylist,
        "lindex": _builtin_lindex,
        "nthcdr": _builtin_nthcdr,
        "nthelem": _builtin_nthelem,
        "remove": _builtin_remove,
        "remq": _builtin_remq,
        "remdq": _builtin_remdq,
        "nconc": _builtin_nconc,
        "rplaca": _builtin_rplaca,
        "rplacd": _builtin_rplacd,
        "tailp": _builtin_tailp,
        "subst": _builtin_subst,
        "apply": _builtin_apply,
        "funcall": _builtin_funcall,
        "eval": _builtin_eval,
        "symeval": _builtin_symeval,
        "getd": _builtin_getd,
        "putd": _builtin_putd,
        "makunbound": _builtin_makunbound,
        "remd": _builtin_remd,
        "gensym": _builtin_gensym,
        "intern": _builtin_intern,
        "symbolName": _builtin_symbol_name,
        "plist": _builtin_plist,
        "setplist": _builtin_setplist,
        "makeInstance": _builtin_make_instance,
        "get": _builtin_get,
        "getq": _builtin_getq,
        "getqq": _builtin_getqq,
        "putprop": _builtin_putprop,
        "putpropq": _builtin_putpropq,
        "putpropqq": _builtin_putpropqq,
        "defprop": _builtin_defprop,
        "remprop": _builtin_remprop,
        "reverse": _builtin_reverse,
        "type": _builtin_type,
        "typep": _builtin_typep,
        "eq": _builtin_eq,
        "neq": _builtin_neq,
        "equal": _builtin_equal,
        "nequal": _builtin_nequal,
        "boundp": _builtin_boundp,
        "null": _builtin_null,
        "atom": _builtin_atom,
        "listp": _builtin_listp,
        "pairp": _builtin_pairp,
        "dtpr": _builtin_dtpr,
        "symbolp": _builtin_symbolp,
        "stringp": _builtin_stringp,
        "numberp": _builtin_numberp,
        "integerp": _builtin_integerp,
        "fixp": _builtin_fixp,
        "floatp": _builtin_floatp,
        "zerop": _builtin_zerop,
        "plusp": _builtin_plusp,
        "onep": _builtin_onep,
        "minusp": _builtin_minusp,
        "evenp": _builtin_evenp,
        "oddp": _builtin_oddp,
        "mapcar": _builtin_mapcar,
        "map": _builtin_map,
        "mapc": _builtin_mapc,
        "maplist": _builtin_maplist,
        "mapcan": _builtin_mapcan,
        "mapcon": _builtin_mapcon,
        "mapinto": _builtin_mapinto,
        "setof": _builtin_setof,
        "exists": _builtin_exists,
        "forall": _builtin_forall,
        "sort": _builtin_sort,
        "sortcar": _builtin_sortcar,
        "=": _builtin_compare("="),
        "<": _builtin_compare("<"),
        "<=": _builtin_compare("<="),
        ">": _builtin_compare(">"),
        ">=": _builtin_compare(">="),
        "not": _builtin_not,
        "print": _builtin_print,
        "println": _builtin_println,
        "printf": _builtin_printf,
        "sprintf": _builtin_sprintf,
        "strcat": _builtin_strcat,
        "concat": _builtin_concat,
        "strlen": _builtin_strlen,
        "strcmp": _builtin_strcmp,
        "alphalessp": _builtin_alpha_lessp,
        "substr": _builtin_substr,
        "substring": _builtin_substring,
        "getchar": _builtin_getchar,
        "index": _builtin_index,
        "rindex": _builtin_rindex,
        "nindex": _builtin_nindex,
        "upperCase": _builtin_upper_case,
        "lowerCase": _builtin_lower_case,
        "buildString": _builtin_build_string,
        "parseString": _builtin_parse_string,
        "rexCompile": _builtin_rex_compile,
        "rexExecute": _builtin_rex_execute,
        "rexMatchp": _builtin_rex_matchp,
        "rexReplace": _builtin_rex_replace,
        "rexSubstitute": _builtin_rex_substitute,
        "atoi": _builtin_atoi,
        "atof": _builtin_atof,
        "fix": _builtin_fix,
        "float": _builtin_float,
        "abs": _builtin_abs,
        "add1": _builtin_add1,
        "sub1": _builtin_sub1,
        "round": _builtin_round,
        "expt": _builtin_expt,
        "remainder": _builtin_remainder,
        "leftshift": _builtin_leftshift,
        "rightshift": _builtin_rightshift,
        "exp": _builtin_exp,
        "log": _builtin_log,
        "sqrt": _builtin_sqrt,
        "sin": _builtin_sin,
        "cos": _builtin_cos,
        "tan": _builtin_tan,
        "asin": _builtin_asin,
        "acos": _builtin_acos,
        "atan": _builtin_atan,
        "random": _builtin_random,
        "srandom": _builtin_srandom,
        "min": _builtin_min,
        "max": _builtin_max,
        "warn": _builtin_warn,
        "getWarn": _builtin_get_warn,
        "error": _builtin_error,
        "load": _builtin_load,
        "loadi": _builtin_loadi,
        "loadstring": _builtin_loadstring,
        "evalstring": _builtin_evalstring,
        "macroexpand": _builtin_macroexpand,
        "array": _builtin_array,
        "arrayref": _builtin_arrayref,
        "setarray": _builtin_setarray,
        "arrayp": _builtin_arrayp,
        "portp": _builtin_portp,
        "makeTable": _builtin_make_table,
        "put": _builtin_put,
        "tablep": _builtin_tablep,
        "tableToList": _builtin_table_to_list,
        "getTableKeys": _builtin_get_table_keys,
        "removeTableEntry": _builtin_remove_table_entry,
        "infile": _builtin_infile,
        "outfile": _builtin_outfile,
        "instring": _builtin_instring,
        "outstring": _builtin_outstring,
        "getOutstring": _builtin_get_outstring,
        "close": _builtin_close,
        "lineread": _builtin_lineread,
        "gets": _builtin_gets,
        "getc": _builtin_getc,
        "fprintf": _builtin_fprintf,
        "fscanf": _builtin_fscanf,
        "eof": _builtin_eof,
        "drain": _builtin_drain,
        "fileLength": _builtin_file_length,
        "fileTell": _builtin_file_tell,
        "fileSeek": _builtin_file_seek,
        "isFile": _builtin_is_file,
        "isDir": _builtin_is_dir,
        "isFileName": _builtin_is_file_name,
        "createDir": _builtin_create_dir,
        "getDirFiles": _builtin_get_dir_files,
        "deleteFile": _builtin_delete_file,
        "getWorkingDir": _builtin_get_working_dir,
        "changeWorkingDir": _builtin_change_working_dir,
        "getSkillPath": _builtin_get_skill_path,
        "setSkillPath": _builtin_set_skill_path,
        "errsetstring": _builtin_errsetstring,
    }
    for width in range(2, 5):
        for ops in product("ad", repeat=width):
            name = "c%sr" % ("".join(ops),)
            if name not in builtins:
                builtins[name] = _make_cxr(name)
    for name, func in builtins.items():
        env.define(name, BuiltinFunction(name, func))
    env.define("nil", None)
    env.define("t", True)
    return env
