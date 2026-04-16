import io
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from openskill.apifinder.index import search
from openskill.cli import main
from openskill.runtime.repl import start_repl


class ApiFinderTests(unittest.TestCase):
    def test_search_finds_symbol(self):
        results = search("procedure")
        self.assertTrue(results)
        self.assertEqual(results[0]["symbol"], "procedure")


class CliTests(unittest.TestCase):
    def test_doctor_command(self):
        code = main(["doctor"])
        self.assertEqual(code, 0)

    def test_api_find_command(self):
        code = main(["api", "find", "when"])
        self.assertEqual(code, 0)


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


if __name__ == "__main__":
    unittest.main()
