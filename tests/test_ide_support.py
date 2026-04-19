# Author: Soham Sen <sensoham135@gmail.com> <sohamsen2000@outlook.com>

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from openskill.ide.editor_support import (
    analyze_brackets,
    completion_candidates,
    editor_symbols,
    extract_user_symbols,
    line_number_text,
    matching_bracket_pair,
    should_show_completion_popup,
    symbol_fragment_bounds,
    syntax_highlight_ranges,
)


class EditorSupportTests(unittest.TestCase):
    def test_extract_user_symbols_finds_procedures_macros_and_classes(self):
        source = """
        (procedure (hello name) (println name))
        (defun add2 (x) (+ x 2))
        (defmacro unlessNil (value form) `(when ,value ,form))
        (defclass point () ((x @initarg ?x)))
        """
        self.assertEqual(
            extract_user_symbols(source),
            ["add2", "hello", "point", "unlessNil"],
        )

    def test_symbol_fragment_bounds_tracks_symbol_under_cursor(self):
        text = "(println helloWorld)"
        start, end, fragment = symbol_fragment_bounds(text, len("(println hello"))
        self.assertEqual((start, end, fragment), (9, 19, "helloWorld"))

    def test_completion_candidates_merge_catalog_and_user_symbols(self):
        source = "(procedure (helloWorld name) name)\n(defun helperFn (x) x)"
        matches = completion_candidates("he", ["help", "when", "hello"], source, limit=10)
        self.assertEqual(matches[:4], ["hello", "helloWorld", "help", "helperFn"])

    def test_editor_symbols_include_syntax_markers(self):
        source = "(procedure (helloWorld name) name)"
        symbols = editor_symbols(["println"], source)
        self.assertIn("println", symbols)
        self.assertIn("helloWorld", symbols)
        self.assertIn("else", symbols)
        self.assertIn("then", symbols)
        self.assertIn("->=", symbols)

    def test_syntax_highlight_ranges_cover_catalog_syntax_and_user_symbols(self):
        source = 'if(a < 1 then println("skip") else helperFn(a))\n(procedure (helperFn value) value)'
        ranges = syntax_highlight_ranges(source, ["if", "<", "println"], source)
        highlighted = [token for _, _, token in ranges]
        self.assertIn("if", highlighted)
        self.assertIn("<", highlighted)
        self.assertIn("then", highlighted)
        self.assertIn("else", highlighted)
        self.assertIn("println", highlighted)
        self.assertIn("helperFn", highlighted)
        self.assertNotIn("skip", highlighted)

    def test_syntax_highlight_ranges_ignore_partial_invalid_input(self):
        self.assertEqual(syntax_highlight_ranges('"', ["println"], '"'), [])

    def test_should_show_completion_popup_hides_exact_match_only(self):
        self.assertTrue(should_show_completion_popup("pr", ["println"]))
        self.assertTrue(should_show_completion_popup("println", ["println", "printf"]))
        self.assertFalse(should_show_completion_popup("println", ["println"]))
        self.assertFalse(should_show_completion_popup("", ["println"]))

    def test_analyze_brackets_tracks_depth_and_unmatched_tokens(self):
        depth_by_offset, match_by_offset, unmatched = analyze_brackets("(a [b {c}]")
        self.assertEqual(depth_by_offset[0], 0)
        self.assertEqual(depth_by_offset[3], 1)
        self.assertEqual(match_by_offset[3], 9)
        self.assertEqual(match_by_offset[9], 3)
        self.assertIn(0, unmatched)

    def test_analyze_brackets_ignores_brackets_inside_strings(self):
        text = '(setq x ")")'
        open_offset = text.index("(")
        close_offset = len(text) - 1
        string_close_offset = text.index(")")
        depth_by_offset, match_by_offset, unmatched = analyze_brackets(text)
        self.assertEqual(depth_by_offset[open_offset], 0)
        self.assertEqual(match_by_offset[open_offset], close_offset)
        self.assertNotIn(string_close_offset, match_by_offset)
        self.assertNotIn(string_close_offset, unmatched)
        self.assertNotIn(close_offset, unmatched)

    def test_analyze_brackets_ignores_brackets_inside_comments(self):
        text = '; TODO: fix this (\n(println 1)'
        open_offsets = [index for index, char in enumerate(text) if char == "("]
        comment_offset, real_offset = open_offsets
        close_offset = text.rindex(")")
        depth_by_offset, match_by_offset, unmatched = analyze_brackets(text)
        self.assertNotIn(comment_offset, depth_by_offset)
        self.assertNotIn(comment_offset, unmatched)
        self.assertEqual(depth_by_offset[real_offset], 0)
        self.assertEqual(match_by_offset[real_offset], close_offset)
        self.assertNotIn(close_offset, unmatched)

    def test_matching_bracket_pair_checks_current_and_previous_position(self):
        text = "(list (1 2 3))"
        self.assertEqual(matching_bracket_pair(text, 0), (0, len(text) - 1))
        self.assertEqual(matching_bracket_pair(text, len(text)), (len(text) - 1, 0))

    def test_line_number_text_covers_each_line(self):
        self.assertEqual(line_number_text("a\nb\nc"), "1\n2\n3")


if __name__ == "__main__":
    unittest.main()
