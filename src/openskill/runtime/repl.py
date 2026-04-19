# Author: Soham Sen <sensoham135@gmail.com> <sohamsen2000@outlook.com>

from __future__ import print_function

from openskill.apifinder.index import search
from openskill.interpreter.errors import SkillSyntaxError
from openskill.interpreter.lexer import tokenize
from openskill.interpreter.runtime import SkillSession, format_value


HELP_TEXT = """Commands:
  :help              Show this message
  :quit              Exit the REPL
  :api QUERY         Search the offline API index
  :reset             Reset the session

The REPL supports core expression evaluation plus local API search.
"""


def start_repl(input_stream=None, output_stream=None, session=None):
    input_stream = input_stream or __import__("sys").stdin
    output_stream = output_stream or __import__("sys").stdout
    session = session or SkillSession()
    buffer_lines = []
    paren_balance = 0

    output_stream.write("OpenSKILL bootstrap REPL\n")
    output_stream.write("Type :help for commands.\n")
    output_stream.flush()

    while True:
        output_stream.write("openskill> ")
        output_stream.flush()
        line = input_stream.readline()
        if not line:
            output_stream.write("\n")
            return 0

        line = line.strip()
        if not line:
            continue
        if line == ":quit":
            return 0
        if line == ":help":
            output_stream.write(HELP_TEXT)
            output_stream.flush()
            continue
        if line == ":reset":
            session = SkillSession()
            buffer_lines = []
            paren_balance = 0
            output_stream.write("Session reset.\n")
            output_stream.flush()
            continue
        if line.startswith(":api "):
            query = line[5:].strip()
            results = search(query)
            if results:
                for item in results:
                    output_stream.write(
                        "{symbol} [{kind}] - {summary}\n".format(**item)
                    )
            else:
                output_stream.write("No API entries matched '{0}'.\n".format(query))
            output_stream.flush()
            continue

        buffer_lines.append(line)
        paren_balance = _paren_balance("\n".join(buffer_lines))
        if paren_balance > 0:
            continue
        source = "\n".join(buffer_lines)
        buffer_lines = []
        paren_balance = 0
        try:
            result = session.eval_text(source, filename="<repl>")
            emitted = False
            last_output = None
            if session.output:
                last_output = session.output[-1]
                output_stream.write("\n".join(session.output) + "\n")
                session.output[:] = []
                emitted = True
            rendered = format_value(result) if result is not None else None
            if rendered is not None and not (emitted and (result is True or rendered == last_output)):
                output_stream.write(rendered + "\n")
        except Exception as exc:
            output_stream.write(str(exc) + "\n")
        output_stream.flush()


def _paren_balance(source):
    balance = 0
    try:
        for token in tokenize(source, filename="<repl-balance>"):
            if token.kind == "LPAREN":
                balance += 1
            elif token.kind == "RPAREN":
                balance -= 1
    except SkillSyntaxError:
        return 0
    return balance
