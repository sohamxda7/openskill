import re

from openskill.interpreter.evaluator import create_global_env
from openskill.interpreter.errors import SkillSyntaxError
from openskill.interpreter.forms import ListForm, NumberForm, StringForm, SymbolForm
from openskill.interpreter.lexer import tokenize

INTEGER_RE = re.compile(r"^[+-]?[0-9]+$")
FLOAT_RE = re.compile(r"^[+-]?(?:[0-9]+\.[0-9]*|\.[0-9]+)$")
KNOWN_CALL_HEADS = set(create_global_env().values.keys()) | {
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
}


class Parser(object):
    INFIX_PRECEDENCE = {
        "=": 10,
        "||": 15,
        "&&": 20,
        "==": 30,
        "!=": 30,
        "<": 30,
        "<=": 30,
        ">": 30,
        ">=": 30,
        "+": 40,
        "-": 40,
        "*": 50,
        "/": 50,
    }
    PREFIX_PRECEDENCE = 60

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
            forms.append(self.parse_expression())
        return forms

    def parse_form(self):
        return self.parse_expression()

    def parse_expression(self, minimum_precedence=0):
        left = self._parse_postfix(self.parse_prefix())
        return self._parse_expression_tail(left, minimum_precedence)

    def _parse_expression_tail(self, left, minimum_precedence=0):
        while True:
            operator = self._peek_infix_operator()
            if operator is None:
                return left
            if operator.line != left.line:
                return left
            precedence = self.INFIX_PRECEDENCE[operator.text]
            if precedence < minimum_precedence:
                return left
            self.consume()
            right = self.parse_expression(precedence if operator.text == "=" else precedence + 1)
            left = self._rewrite_infix(operator, left, right)

    def parse_prefix(self):
        token = self.peek()
        if token.kind in ("SYMBOL", "OPERATOR") and token.text in ("!", "-"):
            operator = self.consume()
            value = self.parse_expression(self.PREFIX_PRECEDENCE)
            return self._rewrite_prefix(operator, value)
        return self.parse_primary()

    def parse_primary(self):
        token = self.peek()
        if token.kind == "LPAREN":
            return self.parse_list()
        if token.kind in ("QUOTE", "BACKQUOTE", "COMMA", "COMMA_AT"):
            return self.parse_prefixed()
        if token.kind == "STRING":
            self.consume()
            return StringForm(token.text, token.line, token.column, token.filename)
        if token.kind in ("SYMBOL", "OPERATOR"):
            self.consume()
            atom = self._atom_form(token)
            if isinstance(atom, SymbolForm) and self._has_immediate_lparen(token):
                return self._parse_immediate_call(atom, token)
            return atom
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
        if self.peek().kind == "RPAREN":
            self.consume()
            return ListForm([], start.line, start.column, start.filename)

        first = self._parse_postfix(self.parse_primary())
        if self._peek_infix_operator() is not None and not self._is_known_call_head(first):
            grouped = self._parse_expression_tail(first)
            if self.peek().kind == "RPAREN":
                self.consume()
                return grouped
            items = [grouped]
            while self.peek().kind != "RPAREN":
                if self.peek().kind == "EOF":
                    raise SkillSyntaxError(
                        "unterminated list",
                        filename=start.filename,
                        line=start.line,
                        column=start.column,
                    )
                items.append(self.parse_expression())
            self.consume()
            return ListForm(items, start.line, start.column, start.filename)

        items = [first]
        while self.peek().kind != "RPAREN":
            if self.peek().kind == "EOF":
                raise SkillSyntaxError(
                    "unterminated list",
                    filename=start.filename,
                    line=start.line,
                    column=start.column,
                )
            items.append(self.parse_expression())
        self.consume()
        return ListForm(items, start.line, start.column, start.filename)

    def _parse_list_items(self, start, parse_head=False):
        items = []
        if self.peek().kind == "EOF":
            raise SkillSyntaxError(
                "unterminated list",
                filename=start.filename,
                line=start.line,
                column=start.column,
            )
        if self.peek().kind != "RPAREN":
            items.append(self.parse_primary() if parse_head else self.parse_expression())
        while self.peek().kind != "RPAREN":
            if self.peek().kind == "EOF":
                raise SkillSyntaxError(
                    "unterminated list",
                    filename=start.filename,
                    line=start.line,
                    column=start.column,
                )
            items.append(self.parse_expression())
        self.consume()
        return items

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

    def _has_immediate_lparen(self, token):
        next_token = self.peek()
        return (
            next_token.kind == "LPAREN"
            and next_token.line == token.line
            and next_token.column == token.column + len(token.text)
        )

    def _parse_immediate_call(self, operator, token):
        start = self.consume()
        items = [operator]
        items.extend(self._parse_list_items(start))
        return ListForm(items, token.line, token.column, token.filename)

    def _parse_postfix(self, left):
        while True:
            token = self.peek()
            if token.kind != "ARROW" or token.line != left.line:
                return left
            operator = self.consume()
            slot = self.peek()
            if slot.kind != "SYMBOL" or slot.line != operator.line:
                raise SkillSyntaxError(
                    "slot access expects a slot name",
                    filename=operator.filename,
                    line=operator.line,
                    column=operator.column,
                )
            slot_form = self._atom_form(self.consume())
            head = SymbolForm("->", operator.line, operator.column, operator.filename)
            left = ListForm([head, left, slot_form], operator.line, operator.column, operator.filename)

    def _peek_infix_operator(self):
        token = self.peek()
        if token.kind not in ("SYMBOL", "OPERATOR"):
            return None
        if token.text not in self.INFIX_PRECEDENCE:
            return None
        next_token = self.tokens[self.index + 1]
        if next_token.kind in ("RPAREN", "EOF"):
            return None
        return token

    def _rewrite_prefix(self, operator, value):
        symbol_name = {
            "!": "not",
            "-": "difference",
        }[operator.text]
        symbol = SymbolForm(symbol_name, operator.line, operator.column, operator.filename)
        return ListForm([symbol, value], operator.line, operator.column, operator.filename)

    def _rewrite_infix(self, operator, left, right):
        if operator.text == "=":
            if isinstance(left, SymbolForm):
                symbol_name = "setq"
                args = [left, right]
            elif self._is_slot_access(left):
                symbol_name = "->="
                args = [left.items[1], left.items[2], right]
            else:
                raise SkillSyntaxError(
                    "assignment target must be a symbol or slot access",
                    filename=operator.filename,
                    line=operator.line,
                    column=operator.column,
                )
        else:
            symbol_name = {
                "||": "or",
                "==": "equal",
                "!=": "nequal",
                "<": "<",
                "<=": "<=",
                ">": ">",
                ">=": ">=",
                "&&": "and",
                "+": "plus",
                "-": "difference",
                "*": "times",
                "/": "quotient",
            }[operator.text]
            args = [left, right]
        symbol = SymbolForm(symbol_name, operator.line, operator.column, operator.filename)
        if symbol_name == "and" and isinstance(left, ListForm) and left.items and isinstance(left.items[0], SymbolForm):
            if left.items[0].name == "and":
                return ListForm(left.items + [right], left.line, left.column, left.filename)
        if symbol_name == "or" and isinstance(left, ListForm) and left.items and isinstance(left.items[0], SymbolForm):
            if left.items[0].name == "or":
                return ListForm(left.items + [right], left.line, left.column, left.filename)
        return ListForm([symbol] + args, operator.line, operator.column, operator.filename)

    def _is_slot_access(self, form):
        return (
            isinstance(form, ListForm)
            and len(form.items) == 3
            and isinstance(form.items[0], SymbolForm)
            and form.items[0].name == "->"
        )

    def _is_known_call_head(self, form):
        return isinstance(form, SymbolForm) and form.name in KNOWN_CALL_HEADS


def parse(source, filename="<string>"):
    tokens = tokenize(source, filename=filename)
    return Parser(tokens).parse_forms()
