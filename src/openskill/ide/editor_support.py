import re


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


def extract_user_symbols(source):
    symbols = set()
    for pattern in _DEFINITION_PATTERNS:
        symbols.update(match.group(1) for match in pattern.finditer(source))
    return sorted(symbols)


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
    user_symbols = extract_user_symbols(source)
    combined = sorted(set(catalog_symbols).union(user_symbols), key=lambda item: item.lower())
    if not prefix:
        return combined[:limit]
    lowered = prefix.lower()
    starts = [item for item in combined if item.lower().startswith(lowered)]
    contains = [item for item in combined if lowered in item.lower() and item not in starts]
    return (starts + contains)[:limit]


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
