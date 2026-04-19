# Author: Soham Sen <sensoham135@gmail.com> <sohamsen2000@outlook.com>

from openskill.interpreter.errors import SkillSyntaxError


class Token(object):
    def __init__(self, kind, text, line, column, filename="<string>"):
        self.kind = kind
        self.text = text
        self.line = line
        self.column = column
        self.filename = filename


def _is_token_boundary(char):
    return char == "" or char in "();'`,\" \t\r\n"


def _is_identifier_letter(char):
    return char.isalpha() or char in "_?"


def _is_arithmetic_operator(source, index):
    char = source[index]
    if char in "+*/":
        return True
    if char != "-":
        return False
    prev_char = source[index - 1] if index > 0 else ""
    next_char = source[index + 1] if index + 1 < len(source) else ""
    if _is_token_boundary(prev_char) or _is_token_boundary(next_char):
        return True
    if _is_identifier_letter(prev_char) and _is_identifier_letter(next_char):
        return False
    return True


def _starts_multi_char_operator(source, index):
    return any(source.startswith(operator, index) for operator in ("&&", "||", "==", "!=", "<=", ">=", "->"))


def tokenize(source, filename="<string>"):
    tokens = []
    index = 0
    line = 1
    column = 1
    length = len(source)
    while index < length:
        char = source[index]
        if char in " \t\r":
            index += 1
            column += 1
            continue
        if char == "\n":
            index += 1
            line += 1
            column = 1
            continue
        if char == ";":
            while index < length and source[index] != "\n":
                index += 1
                column += 1
            continue
        if char == "(":
            tokens.append(Token("LPAREN", char, line, column, filename))
            index += 1
            column += 1
            continue
        if char == ")":
            tokens.append(Token("RPAREN", char, line, column, filename))
            index += 1
            column += 1
            continue
        if char == "'":
            tokens.append(Token("QUOTE", char, line, column, filename))
            index += 1
            column += 1
            continue
        if char == "`":
            tokens.append(Token("BACKQUOTE", char, line, column, filename))
            index += 1
            column += 1
            continue
        if char == ",":
            next_char = source[index + 1] if index + 1 < length else ""
            if next_char == "@":
                tokens.append(Token("COMMA_AT", ",@", line, column, filename))
                index += 2
                column += 2
            else:
                tokens.append(Token("COMMA", char, line, column, filename))
                index += 1
                column += 1
            continue
        if char == "\"":
            start_line = line
            start_col = column
            index += 1
            column += 1
            chars = []
            while index < length:
                char = source[index]
                if char == "\"":
                    index += 1
                    column += 1
                    break
                if char == "\\":
                    if index + 1 >= length:
                        raise SkillSyntaxError(
                            "unterminated string escape",
                            filename=filename,
                            line=line,
                            column=column,
                        )
                    escaped = source[index + 1]
                    mapping = {
                        "n": "\n",
                        "r": "\r",
                        "t": "\t",
                        "\"": "\"",
                        "\\": "\\",
                    }
                    chars.append(mapping.get(escaped, escaped))
                    index += 2
                    column += 2
                    continue
                chars.append(char)
                index += 1
                if char == "\n":
                    line += 1
                    column = 1
                else:
                    column += 1
            else:
                raise SkillSyntaxError(
                    "unterminated string literal",
                    filename=filename,
                    line=start_line,
                    column=start_col,
                )
            tokens.append(Token("STRING", "".join(chars), start_line, start_col, filename))
            continue
        for operator, kind in (
            ("&&", "SYMBOL"),
            ("||", "SYMBOL"),
            ("==", "SYMBOL"),
            ("!=", "SYMBOL"),
            ("<=", "SYMBOL"),
            (">=", "SYMBOL"),
            ("->", "ARROW"),
        ):
            if source.startswith(operator, index):
                tokens.append(Token(kind, operator, line, column, filename))
                index += len(operator)
                column += len(operator)
                break
        else:
            operator = None
        if operator is not None:
            continue
        if _is_arithmetic_operator(source, index):
            tokens.append(Token("OPERATOR", char, line, column, filename))
            index += 1
            column += 1
            continue
        if char in "<>":
            tokens.append(Token("SYMBOL", char, line, column, filename))
            index += 1
            column += 1
            continue
        if char == "=":
            tokens.append(Token("SYMBOL", "=", line, column, filename))
            index += 1
            column += 1
            continue
        if char == "!":
            tokens.append(Token("SYMBOL", "!", line, column, filename))
            index += 1
            column += 1
            continue
        start = index
        start_col = column
        while index < length and source[index] not in "();'`,\" \t\r\n":
            if _starts_multi_char_operator(source, index):
                break
            if _is_arithmetic_operator(source, index):
                break
            if source[index] in "!<>":
                break
            if source[index] == "=" and source[index - 1] not in "<>":
                break
            index += 1
            column += 1
        text = source[start:index]
        tokens.append(Token("SYMBOL", text, line, start_col, filename))
    tokens.append(Token("EOF", "", line, column, filename))
    return tokens
