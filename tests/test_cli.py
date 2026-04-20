# Author: Soham Sen <sensoham135@gmail.com> <sohamsen2000@outlook.com>

import contextlib
import io
import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from openskill.apifinder.index import load_index, search
from openskill.cli import main
from openskill.runtime.repl import start_repl


class ApiFinderTests(unittest.TestCase):
    def test_search_finds_symbol(self):
        results = search("procedure")
        self.assertTrue(results)
        self.assertEqual(results[0]["symbol"], "procedure")

    def test_load_index_rejects_invalid_shapes(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            handle.write('{"symbol": "procedure"}')
            path = handle.name
        try:
            with self.assertRaises(ValueError):
                load_index(path)
        finally:
            os.unlink(path)


class CliTests(unittest.TestCase):
    def test_doctor_command(self):
        code = main(["doctor"])
        self.assertEqual(code, 0)

    def test_api_find_command(self):
        code = main(["api", "find", "when"])
        self.assertEqual(code, 0)

    def test_expr_errors_return_nonzero_without_traceback(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = main(["--expr", '(load "missing.il")'])
        self.assertEqual(code, 1)
        rendered = stderr.getvalue()
        self.assertIn("missing.il", rendered)
        self.assertNotIn("Traceback", rendered)

    def test_expr_regex_errors_return_nonzero_without_traceback(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = main(["--expr", '(rexCompile "[a-")'])
        self.assertEqual(code, 1)
        rendered = stderr.getvalue()
        self.assertIn("rexCompile failed", rendered)
        self.assertNotIn("Traceback", rendered)

    def test_expr_deep_nesting_returns_nonzero_without_traceback(self):
        stderr = io.StringIO()
        expression = "(" * 2000 + "1" + ")" * 2000
        with contextlib.redirect_stderr(stderr):
            code = main(["--expr", expression])
        self.assertEqual(code, 1)
        rendered = stderr.getvalue()
        self.assertIn("too deeply nested", rendered)
        self.assertNotIn("Traceback", rendered)

    def test_script_decode_errors_return_nonzero_without_traceback(self):
        stderr = io.StringIO()
        with tempfile.NamedTemporaryFile(delete=False) as handle:
            handle.write(b"\xff")
            path = handle.name
        try:
            with contextlib.redirect_stderr(stderr):
                code = main([path])
        finally:
            os.unlink(path)
        self.assertEqual(code, 1)
        rendered = stderr.getvalue()
        self.assertIn("Could not decode SKILL source file", rendered)
        self.assertNotIn("Traceback", rendered)


class ReplTests(unittest.TestCase):
    def test_repl_handles_quit(self):
        input_stream = io.StringIO(":quit\n")
        output_stream = io.StringIO()
        code = start_repl(input_stream=input_stream, output_stream=output_stream)
        self.assertEqual(code, 0)
        self.assertIn("OpenSKILL bootstrap REPL", output_stream.getvalue())

    def test_repl_does_not_double_echo_println(self):
        input_stream = io.StringIO('(println "hello")\n:quit\n')
        output_stream = io.StringIO()
        code = start_repl(input_stream=input_stream, output_stream=output_stream)
        self.assertEqual(code, 0)
        rendered = output_stream.getvalue()
        self.assertEqual(rendered.count('"hello"'), 1)

    def test_repl_counts_parens_outside_strings(self):
        input_stream = io.StringIO('(println "text ((")\n:quit\n')
        output_stream = io.StringIO()
        code = start_repl(input_stream=input_stream, output_stream=output_stream)
        self.assertEqual(code, 0)
        rendered = output_stream.getvalue()
        self.assertIn('"text (("', rendered)
        self.assertNotIn("Interpreter placeholder", rendered)

    def test_repl_reports_unterminated_string_without_crashing(self):
        input_stream = io.StringIO('"unterminated\n:quit\n')
        output_stream = io.StringIO()
        code = start_repl(input_stream=input_stream, output_stream=output_stream)
        self.assertEqual(code, 0)
        rendered = output_stream.getvalue()
        self.assertIn("unterminated string literal", rendered)

    def test_repl_supports_multiline_strings(self):
        input_stream = io.StringIO('"hello\nworld"\n:quit\n')
        output_stream = io.StringIO()
        code = start_repl(input_stream=input_stream, output_stream=output_stream)
        self.assertEqual(code, 0)
        rendered = output_stream.getvalue()
        self.assertIn('"hello', rendered)
        self.assertIn('world"', rendered)
        self.assertNotIn("unterminated string literal", rendered)


if __name__ == "__main__":
    unittest.main()
