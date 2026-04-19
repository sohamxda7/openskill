# Author: Soham Sen <sensoham135@gmail.com> <sohamsen2000@outlook.com>

import re

from openskill.interpreter.lexer import tokenize


BRACKET_PALETTE = (
    "#d19a66",
    "#61afef",
    "#98c379",
    "#c678dd",
    "#e06c75",
    "#56b6c2",
)

_DEFINITION_PATTERNS = (
    re.compile(r"\((?:procedure|nprocedure|mprocedure)\s*\(\s*([^\s()]+)"),
    re.compile(r"\((?:defun|defmacro|defclass)\s+([^\s()]+)"),
)
_SYMBOL_DELIMITERS = set("()[]{}'\"`;,\t\r\n ")
_EDITOR_MARKERS = frozenset(
    {
        "quote",
        "quasiquote",
        "if",
        "when",
        "unless",
        "progn",
        "let",
        "setq",
        "lambda",
        "procedure",
        "case",
        "caseq",
        "cond",
        "catch",
        "throw",
        "foreach",
        "for",
        "exists",
        "forall",
        "prog",
        "prog1",
        "prog2",
        "return",
        "defun",
        "defclass",
        "defmacro",
        "nprocedure",
        "mprocedure",
        "errset",
        "while",
        "and",
        "or",
        "sprintf",
        "->",
        "->=",
        "unquote",
        "splice",
        "then",
        "else",
        "t",
        "nil",
        "@optional",
        "@key",
        "@rest",
        "@aux",
        "@whole",
    }
)


def extract_user_symbols(source):
    symbols = set()
    for pattern in _DEFINITION_PATTERNS:
        symbols.update(match.group(1) for match in pattern.finditer(source))
    return sorted(symbols)


def editor_symbols(catalog_symbols, source):
    return sorted(set(catalog_symbols).union(_EDITOR_MARKERS).union(extract_user_symbols(source)), key=lambda item: item.lower())


def symbol_fragment_bounds(text, cursor_offset):
    if cursor_offset < 0:
        cursor_offset = 0
    if cursor_offset > len(text):
        cursor_offset = len(text)
    start = cursor_offset
    while start > 0 and text[start - 1] not in _SYMBOL_DELIMITERS:
        start -= 1
    end = cursor_offset
    while end < len(text) and text[end] not in _SYMBOL_DELIMITERS:
        end += 1
    return start, end, text[start:end]


def completion_candidates(prefix, catalog_symbols, source, limit=12):
    prefix = prefix or ""
    combined = editor_symbols(catalog_symbols, source)
    if not prefix:
        return combined[:limit]
    lowered = prefix.lower()
    starts = [item for item in combined if item.lower().startswith(lowered)]
    contains = [item for item in combined if lowered in item.lower() and item not in starts]
    return (starts + contains)[:limit]


def syntax_highlight_ranges(text, catalog_symbols, source):
    highlightable = set(editor_symbols(catalog_symbols, source))
    ranges = []
    for token in tokenize(text):
        if token.kind == "EOF":
            continue
        if token.kind not in ("SYMBOL", "OPERATOR", "ARROW"):
            continue
        if token.text not in highlightable:
            continue
        start = "%d.%d" % (token.line, token.column - 1)
        end = "%d.%d" % (token.line, token.column - 1 + len(token.text))
        ranges.append((start, end, token.text))
    return ranges


def should_show_completion_popup(fragment, matches):
    if not fragment or not matches:
        return False
    return len(matches) > 1 or matches[0] != fragment


def analyze_brackets(text):
    opening = {"(": ")", "[": "]", "{": "}"}
    closing = {value: key for key, value in opening.items()}
    depth_by_offset = {}
    match_by_offset = {}
    unmatched_offsets = set()
    stack = []
    in_string = False
    in_comment = False
    escaping = False

    for offset, char in enumerate(text):
        if in_comment:
            if char == "\n":
                in_comment = False
            continue
        if in_string:
            if escaping:
                escaping = False
                continue
            if char == "\\":
                escaping = True
                continue
            if char == '"':
                in_string = False
            continue
        if char == ";":
            in_comment = True
            continue
        if char == '"':
            in_string = True
            continue
        if char in opening:
            depth = len(stack)
            stack.append((char, offset, depth))
            depth_by_offset[offset] = depth
            continue
        if char in closing:
            if stack and stack[-1][0] == closing[char]:
                _, opener_offset, depth = stack.pop()
                depth_by_offset[offset] = depth
                match_by_offset[opener_offset] = offset
                match_by_offset[offset] = opener_offset
            else:
                unmatched_offsets.add(offset)

    for _, offset, _ in stack:
        unmatched_offsets.add(offset)
    return depth_by_offset, match_by_offset, unmatched_offsets


def matching_bracket_pair(text, cursor_offset):
    _, match_by_offset, _ = analyze_brackets(text)
    probe_offsets = []
    if 0 <= cursor_offset < len(text):
        probe_offsets.append(cursor_offset)
    if 0 < cursor_offset <= len(text):
        probe_offsets.append(cursor_offset - 1)
    for offset in probe_offsets:
        if offset in match_by_offset:
            return offset, match_by_offset[offset]
    return None


def line_number_text(text):
    line_count = text.count("\n") + 1
    return "\n".join(str(index) for index in range(1, line_count + 1))
