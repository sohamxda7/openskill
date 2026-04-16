import re

from openskill.interpreter.errors import SkillSyntaxError
from openskill.interpreter.forms import ListForm, NumberForm, StringForm, SymbolForm
from openskill.interpreter.lexer import tokenize

INTEGER_RE = re.compile(r"^[+-]?[0-9]+$")
FLOAT_RE = re.compile(r"^[+-]?(?:[0-9]+\.[0-9]*|\.[0-9]+)$")


class Parser(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def peek(self):
        return self.tokens[self.index]

    def consume(self):
        token = self.tokens[self.index]
        self.index += 1
        return token

    def parse_forms(self):
        forms = []
        while self.peek().kind != "EOF":
            forms.append(self.parse_form())
        return forms

    def parse_form(self):
        token = self.peek()
        if token.kind == "LPAREN":
            return self.parse_list()
        if token.kind in ("QUOTE", "BACKQUOTE", "COMMA", "COMMA_AT"):
            return self.parse_prefixed()
        if token.kind == "STRING":
            self.consume()
            return StringForm(token.text, token.line, token.column, token.filename)
        if token.kind == "SYMBOL":
            self.consume()
            return self._atom_form(token)
        if token.kind == "RPAREN":
            raise SkillSyntaxError(
                "unexpected closing parenthesis",
                filename=token.filename,
                line=token.line,
                column=token.column,
            )
        raise SkillSyntaxError(
            "unexpected token %s" % token.kind,
            filename=token.filename,
            line=token.line,
            column=token.column,
        )

    def parse_list(self):
        start = self.consume()
        items = []
        while self.peek().kind != "RPAREN":
            if self.peek().kind == "EOF":
                raise SkillSyntaxError(
                    "unterminated list",
                    filename=start.filename,
                    line=start.line,
                    column=start.column,
                )
            items.append(self.parse_form())
        self.consume()
        return ListForm(items, start.line, start.column, start.filename)

    def parse_prefixed(self):
        token = self.consume()
        symbol_name = {
            "QUOTE": "quote",
            "BACKQUOTE": "quasiquote",
            "COMMA": "unquote",
            "COMMA_AT": "splice",
        }[token.kind]
        symbol = SymbolForm(symbol_name, token.line, token.column, token.filename)
        value = self.parse_form()
        return ListForm([symbol, value], token.line, token.column, token.filename)

    def _atom_form(self, token):
        if INTEGER_RE.match(token.text):
            return NumberForm(int(token.text), token.text, token.line, token.column, token.filename)
        if FLOAT_RE.match(token.text):
            return NumberForm(float(token.text), token.text, token.line, token.column, token.filename)
        return SymbolForm(token.text, token.line, token.column, token.filename)


def parse(source, filename="<string>"):
    tokens = tokenize(source, filename=filename)
    return Parser(tokens).parse_forms()

