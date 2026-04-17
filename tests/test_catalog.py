import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from openskill.apifinder.index import load_index, search
from openskill.interpreter.evaluator import create_global_env
from openskill.interpreter.parser import parse


SPECIAL_FORMS = {
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
    "exists",
    "forall",
    "->",
}


class CatalogTests(unittest.TestCase):
    def test_catalog_covers_supported_core_surface(self):
        entries = load_index()
        symbols = {entry["symbol"] for entry in entries}
        self.assertGreaterEqual(len(entries), 225)
        for required in {
            "quote",
            "quasiquote",
            "if",
            "cond",
            "caseq",
            "and",
            "or",
            "prog",
            "prog1",
            "prog2",
            "return",
            "catch",
            "throw",
            "procedure",
            "defclass",
            "lambda",
            "defun",
            "defmacro",
            "nprocedure",
            "mprocedure",
            "for",
            "foreach",
            "while",
            "apply",
            "funcall",
            "eval",
            "symeval",
            "getd",
            "putd",
            "makunbound",
            "remd",
            "gensym",
            "intern",
            "symbolName",
            "mapcar",
            "map",
            "mapc",
            "maplist",
            "mapcan",
            "mapcon",
            "mapinto",
            "setof",
            "exists",
            "forall",
            "sort",
            "sortcar",
            "type",
            "reverse",
            "append1",
            "caar",
            "cdar",
            "cddr",
            "caadr",
            "copy",
            "copylist",
            "ncons",
            "xcons",
            "memq",
            "assq",
            "lindex",
            "nthcdr",
            "nthelem",
            "remove",
            "remq",
            "remd",
            "remdq",
            "nconc",
            "rplaca",
            "rplacd",
            "tailp",
            "subst",
            "plist",
            "setplist",
            "get",
            "putprop",
            "remprop",
            "makeInstance",
            "->",
            "integerp",
            "fixp",
            "typep",
            "floatp",
            "zerop",
            "plusp",
            "minusp",
            "evenp",
            "oddp",
            "onep",
            "pairp",
            "dtpr",
            "sprintf",
            "concat",
            "strlen",
            "strcmp",
            "alphalessp",
            "substr",
            "substring",
            "getchar",
            "index",
            "rindex",
            "nindex",
            "upperCase",
            "lowerCase",
            "buildString",
            "parseString",
            "rexCompile",
            "rexExecute",
            "rexMatchp",
            "rexReplace",
            "rexSubstitute",
            "fix",
            "float",
            "add1",
            "sub1",
            "round",
            "expt",
            "remainder",
            "leftshift",
            "rightshift",
            "exp",
            "log",
            "sqrt",
            "sin",
            "cos",
            "tan",
            "asin",
            "acos",
            "atan",
            "random",
            "srandom",
            "array",
            "arrayref",
            "setarray",
            "arrayp",
            "portp",
            "makeTable",
            "put",
            "tablep",
            "tableToList",
            "getTableKeys",
            "removeTableEntry",
            "infile",
            "outfile",
            "instring",
            "outstring",
            "getOutstring",
            "close",
            "lineread",
            "gets",
            "getc",
            "fprintf",
            "fscanf",
            "eof",
            "drain",
            "fileLength",
            "fileTell",
            "fileSeek",
            "isFile",
            "isDir",
            "isFileName",
            "createDir",
            "getDirFiles",
            "deleteFile",
            "getWorkingDir",
            "changeWorkingDir",
            "getSkillPath",
            "setSkillPath",
            "loadi",
            "loadstring",
            "evalstring",
            "macroexpand",
            "getWarn",
            "errsetstring",
            "plus",
            "difference",
            "times",
            "quotient",
            "warn",
            "error",
            "errset",
            "+",
            ">=",
            "printf",
        }:
            self.assertIn(required, symbols)

    def test_catalog_has_only_list_remd(self):
        entries = [entry for entry in load_index() if entry["symbol"] == "remd"]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["signature"], "(remd item list)")

    def test_search_uses_catalog_as_single_source_of_truth(self):
        results = search("quasiquote")
        self.assertTrue(results)
        self.assertEqual(results[0]["symbol"], "quasiquote")

    def test_catalog_entries_have_required_fields_and_parseable_examples(self):
        required_fields = {"symbol", "kind", "signature", "summary", "returns", "example", "tags"}
        for entry in load_index():
            self.assertTrue(required_fields.issubset(entry))
            self.assertTrue(entry["symbol"])
            self.assertTrue(entry["summary"])
            self.assertTrue(entry["signature"])
            self.assertIsInstance(entry["tags"], list)
            parse(entry["example"], filename="<catalog-example>")

    def test_catalog_symbols_resolve_to_special_forms_or_runtime_bindings(self):
        runtime_symbols = set(create_global_env().values.keys())
        documented = {entry["symbol"] for entry in load_index()}
        for symbol in documented:
            self.assertTrue(
                symbol in SPECIAL_FORMS or symbol in runtime_symbols,
                msg="catalog symbol is not implemented: %s" % symbol,
            )


if __name__ == "__main__":
    unittest.main()
