from openskill.interpreter.errors import SkillSyntaxError


class Token(object):
    def __init__(self, kind, text, line, column, filename="<string>"):
        self.kind = kind
        self.text = text
        self.line = line
        self.column = column
        self.filename = filename


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
        start = index
        start_col = column
        while index < length and source[index] not in "();'`,\" \t\r\n":
            index += 1
            column += 1
        text = source[start:index]
        tokens.append(Token("SYMBOL", text, line, start_col, filename))
    tokens.append(Token("EOF", "", line, column, filename))
    return tokens

