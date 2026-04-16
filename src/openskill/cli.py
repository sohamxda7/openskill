import argparse
import os
import sys

from openskill.apifinder.index import load_index, search
from openskill import __version__
from openskill.interpreter.runtime import SkillSession, format_value
from openskill.runtime.repl import start_repl


def _emit_result(session, result):
    emitted = False
    if session.output:
        print("\n".join(session.output))
        session.output[:] = []
        emitted = True
    if result is not None and not (emitted and result is True):
        print(format_value(result))


def _run_repl(session):
    return start_repl(session=session)


def _launch_gui():
    try:
        from openskill.ui.app import launch
    except ImportError as exc:
        raise SystemExit(
            "The desktop shell needs a Python build with tkinter support."
        ) from exc
    return launch()


def _doctor():
    entries = len(load_index())
    gui_ready = "yes"
    try:
        __import__("tkinter")
    except ImportError:
        gui_ready = "no"
    print("OpenSKILL doctor")
    print("version: %s" % __version__)
    print("cwd: %s" % os.getcwd())
    print("api_entries: %s" % entries)
    print("gui_available: %s" % gui_ready)
    return 0


def _api_find(argv):
    if len(argv) < 3 or argv[1] != "find":
        print("Usage: openskill api find QUERY")
        return 2
    query = " ".join(argv[2:])
    for item in search(query):
        print("{symbol} [{kind}] - {summary}".format(**item))
    return 0


def main(argv=None):
    argv = argv or sys.argv[1:]
    if argv:
        if argv[0] == "doctor":
            return _doctor()
        if argv[0] == "api":
            return _api_find(argv)
        if argv[0] == "repl":
            return _run_repl(SkillSession(cwd=os.getcwd()))

    parser = argparse.ArgumentParser(prog="openskill")
    parser.add_argument("script", nargs="?", help="Path to a SKILL source file")
    parser.add_argument(
        "--expr",
        help="Evaluate one expression and print the result",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the desktop shell",
    )
    args = parser.parse_args(argv)

    if args.gui:
        return _launch_gui()

    session = SkillSession(cwd=os.getcwd())
    if args.expr:
        value = session.eval_text(args.expr, filename="<expr>")
        _emit_result(session, value)
        return 0
    if args.script:
        value = session.load_file(args.script)
        _emit_result(session, value)
        return 0
    return _run_repl(session)
    
