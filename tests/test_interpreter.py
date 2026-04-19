# Author: Soham Sen <sensoham135@gmail.com> <sohamsen2000@outlook.com>

import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from openskill.interpreter.errors import SkillEvalError, SkillSyntaxError
from openskill.interpreter.lexer import tokenize
from openskill.interpreter.parser import parse
from openskill.interpreter.runtime import SkillSession, format_value


class ParserTests(unittest.TestCase):
    def test_parses_quote(self):
        forms = parse("'(a 1 \"x\")", filename="sample.il")
        self.assertEqual(forms[0].items[0].name, "quote")
        self.assertEqual(forms[0].line, 1)
        self.assertEqual(forms[0].column, 1)

    def test_parses_immediate_paren_calls(self):
        forms = parse('println("hello") plus(1 2) g()', filename="sample.il")
        self.assertEqual(forms[0].items[0].name, "println")
        self.assertEqual(forms[0].items[1].value, "hello")
        self.assertEqual(forms[1].items[0].name, "plus")
        self.assertEqual([item.value for item in forms[1].items[1:]], [1, 2])
        self.assertEqual(forms[2].items[0].name, "g")
        self.assertEqual(len(forms[2].items), 1)

    def test_immediate_paren_calls_require_adjacency(self):
        forms = parse('println ("hello")', filename="sample.il")
        self.assertEqual(forms[0].name, "println")
        self.assertEqual(forms[1].items[0].value, "hello")

    def test_parses_nested_immediate_paren_special_forms(self):
        forms = parse("procedure(foo(a @optional (b 2)) let(((x 1)) plus(a b x)))", filename="sample.il")
        self.assertEqual(forms[0].items[0].name, "procedure")
        signature = forms[0].items[1]
        self.assertEqual(signature.items[0].name, "foo")
        self.assertEqual(signature.items[1].name, "a")
        self.assertEqual(signature.items[2].name, "@optional")
        self.assertEqual(signature.items[3].items[0].name, "b")
        body = forms[0].items[2]
        self.assertEqual(body.items[0].name, "let")
        self.assertEqual(body.items[1].items[0].items[0].name, "x")
        self.assertEqual(body.items[2].items[0].name, "plus")

    def test_reports_unterminated_list(self):
        with self.assertRaises(SkillSyntaxError) as ctx:
            parse("(list 1 2", filename="broken.il")
        self.assertIn("broken.il:1:1", str(ctx.exception))

    def test_lexes_bang_as_operator_before_symbols(self):
        tokens = tokenize("!variable !=", filename="sample.il")
        self.assertEqual([token.text for token in tokens[:-1]], ["!", "variable", "!="])

    def test_lexes_arithmetic_operators_as_separate_tokens(self):
        tokens = tokenize("a + b * c / -d", filename="sample.il")
        self.assertEqual(
            [(token.kind, token.text) for token in tokens[:-1]],
            [
                ("SYMBOL", "a"),
                ("OPERATOR", "+"),
                ("SYMBOL", "b"),
                ("OPERATOR", "*"),
                ("SYMBOL", "c"),
                ("OPERATOR", "/"),
                ("OPERATOR", "-"),
                ("SYMBOL", "d"),
            ],
        )

    def test_lexes_tight_operator_syntax(self):
        tokens = tokenize("fib(n-1) x<y+z A*x1+B*y1+C != 0.0", filename="sample.il")
        self.assertEqual(
            [token.text for token in tokens[:-1]],
            ["fib", "(", "n", "-", "1", ")", "x", "<", "y", "+", "z", "A", "*", "x1", "+", "B", "*", "y1", "+", "C", "!=", "0.0"],
        )

    def test_lexes_arrow_slot_access(self):
        tokens = tokenize("obj->slot = 1", filename="sample.il")
        self.assertEqual(
            [(token.kind, token.text) for token in tokens[:-1]],
            [("SYMBOL", "obj"), ("ARROW", "->"), ("SYMBOL", "slot"), ("SYMBOL", "="), ("SYMBOL", "1")],
        )

    def test_lexes_relational_and_logical_operators(self):
        tokens = tokenize("a<1 b <= 2 c>=3 d > 4 left || right", filename="sample.il")
        self.assertEqual(
            [token.text for token in tokens[:-1]],
            ["a", "<", "1", "b", "<=", "2", "c", ">=", "3", "d", ">", "4", "left", "||", "right"],
        )

    def test_rewrites_operator_compat_expressions(self):
        forms = parse("tot = plus(a b) when(!flag && a == b || total >= limit ok)", filename="sample.il")
        assignment = forms[0]
        self.assertEqual(assignment.items[0].name, "setq")
        self.assertEqual(assignment.items[1].name, "tot")
        self.assertEqual(assignment.items[2].items[0].name, "plus")

        when_form = forms[1]
        self.assertEqual(when_form.items[0].name, "when")
        condition = when_form.items[1]
        self.assertEqual(condition.items[0].name, "or")
        and_form = condition.items[1]
        self.assertEqual(and_form.items[0].name, "and")
        self.assertEqual(and_form.items[1].items[0].name, "not")
        self.assertEqual(and_form.items[2].items[0].name, "equal")
        self.assertEqual(condition.items[2].items[0].name, ">=")

    def test_preserves_prefix_equals_calls(self):
        forms = parse("(= 3 3)", filename="sample.il")
        self.assertEqual(forms[0].items[0].name, "=")
        self.assertEqual([item.value for item in forms[0].items[1:]], [3, 3])

    def test_rewrites_infix_arithmetic_with_precedence(self):
        forms = parse("a + b * c", filename="sample.il")
        self.assertEqual(forms[0].items[0].name, "plus")
        self.assertEqual(forms[0].items[1].name, "a")
        multiply = forms[0].items[2]
        self.assertEqual(multiply.items[0].name, "times")
        self.assertEqual([item.name for item in multiply.items[1:]], ["b", "c"])

    def test_rewrites_infix_comparisons_inside_if(self):
        forms = parse('if(a < b + c then println("x") else println("y"))', filename="sample.il")
        condition = forms[0].items[1]
        self.assertEqual(condition.items[0].name, "<")
        self.assertEqual(condition.items[1].name, "a")
        self.assertEqual(condition.items[2].items[0].name, "plus")

    def test_groups_unary_prefix_expressions(self):
        forms = parse("(!done) (-a + b)", filename="sample.il")
        self.assertEqual(forms[0].items[0].name, "not")
        self.assertEqual(forms[0].items[1].name, "done")
        self.assertEqual(forms[1].items[0].name, "plus")
        self.assertEqual(forms[1].items[1].items[0].name, "difference")
        self.assertEqual(forms[1].items[1].items[1].name, "a")
        self.assertEqual(forms[1].items[2].name, "b")

    def test_rewrites_unary_minus(self):
        forms = parse("-a a + -b a - b - c", filename="sample.il")
        self.assertEqual(forms[0].items[0].name, "difference")
        self.assertEqual(forms[0].items[1].name, "a")

        plus_form = forms[1]
        self.assertEqual(plus_form.items[0].name, "plus")
        self.assertEqual(plus_form.items[1].name, "a")
        self.assertEqual(plus_form.items[2].items[0].name, "difference")
        self.assertEqual(plus_form.items[2].items[1].name, "b")

        chained = forms[2]
        self.assertEqual(chained.items[0].name, "difference")
        self.assertEqual(chained.items[1].items[0].name, "difference")
        self.assertEqual([item.name for item in chained.items[1].items[1:]], ["a", "b"])
        self.assertEqual(chained.items[2].name, "c")

    def test_preserves_prefix_arithmetic_calls(self):
        forms = parse("(+ 1 2) (- 5 3)", filename="sample.il")
        self.assertEqual(forms[0].items[0].name, "+")
        self.assertEqual([item.value for item in forms[0].items[1:]], [1, 2])
        self.assertEqual(forms[1].items[0].name, "-")
        self.assertEqual([item.value for item in forms[1].items[1:]], [5, 3])

    def test_preserves_operator_symbols_as_call_arguments(self):
        forms = parse(
            "(procedure (dispatch op x y) (funcall op x y)) (dispatch + 1 2) (dispatch < 1 2) (funcall - 5 3)",
            filename="sample.il",
        )
        self.assertEqual(forms[1].items[0].name, "dispatch")
        self.assertEqual(forms[1].items[1].name, "+")
        self.assertEqual(forms[2].items[0].name, "dispatch")
        self.assertEqual(forms[2].items[1].name, "<")
        self.assertEqual(forms[3].items[0].name, "funcall")
        self.assertEqual(forms[3].items[1].name, "-")

    def test_rewrites_slot_access_and_assignment(self):
        forms = parse("inst->x inst->x = 3", filename="sample.il")
        self.assertEqual(forms[0].items[0].name, "->")
        self.assertEqual(forms[0].items[1].name, "inst")
        self.assertEqual(forms[0].items[2].name, "x")
        self.assertEqual(forms[1].items[0].name, "->=")
        self.assertEqual(forms[1].items[1].name, "inst")
        self.assertEqual(forms[1].items[2].name, "x")
        self.assertEqual(forms[1].items[3].value, 3)

    def test_rejects_invalid_slot_rewrite(self):
        with self.assertRaises(SkillSyntaxError):
            parse("inst->(x)", filename="sample.il")


class EvaluatorTests(unittest.TestCase):
    def test_examples_load_from_repo_root(self):
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        example_names = [
            "hello.il",
            "arithmetic.il",
            "control-flow.il",
            "lists.il",
            "ports.il",
            "procedure.il",
            "fibonacci.il",
            "list-manipulation.il",
            "string-processing.il",
            "state-machine.il",
        ]
        for example_name in example_names:
            with self.subTest(example=example_name):
                session = SkillSession(cwd=repo_root)
                session.load_file(os.path.join("examples", example_name))
                self.assertTrue(session.output)

    def test_let_and_arithmetic(self):
        session = SkillSession()
        value = session.eval_text("(let ((x 2) (y 5)) (+ x y))")
        self.assertEqual(value, 7)
        self.assertIsNone(session.eval_text("(errset (/ 1 0))"))
        self.assertIsNone(session.eval_text('(errset (+ "a" 1))'))

    def test_procedure_definition(self):
        session = SkillSession()
        session.eval_text("(procedure (add2 a b) (+ a b))")
        value = session.eval_text("(add2 4 6)")
        self.assertEqual(value, 10)

    def test_loops_and_case(self):
        session = SkillSession()
        program = """
        (setq sum 0)
        (for i 1 3
          (setq sum (+ sum i)))
        (case sum
          ((1 2 3) 0)
          (6 "ok"))
        """
        self.assertEqual(session.eval_text(program), "ok")

    def test_load_relative_file(self):
        session = SkillSession()
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "child.il")
            with open(path, "w") as handle:
                handle.write("(setq loaded 41)\n(+ loaded 1)\n")
            value = session.load_file(path)
        self.assertEqual(value, 42)

    def test_zero_is_truthy(self):
        session = SkillSession()
        self.assertEqual(session.eval_text("(if 0 1 2)"), 1)
        self.assertIsNone(session.eval_text("(null 0)"))
        self.assertEqual(session.eval_text("(- 5 5)"), 0)

    def test_quasiquote_and_predicates(self):
        session = SkillSession()
        value = session.eval_text("`(a ,(+ 1 2) ,@(list 4 5))")
        self.assertEqual(format_value(value), "(a 3 4 5)")
        self.assertEqual(format_value(session.eval_text("(type '(1 2 3))")), "list")
        self.assertEqual(format_value(session.eval_text("(type 3)")), "integer")

    def test_short_circuit_and_collection_helpers(self):
        session = SkillSession()
        session.eval_text("(setq x 0)")
        self.assertIsNone(session.eval_text("(and nil (setq x 99))"))
        self.assertEqual(session.eval_text("x"), 0)
        self.assertEqual(session.eval_text("(or nil 7)"), 7)
        self.assertEqual(session.eval_text("(nth 1 '(10 20 30))"), 20)
        self.assertIsNone(session.eval_text("(nth 99 '(10 20 30))"))
        self.assertEqual(format_value(session.eval_text("(last '(10 20 30))")), "(30)")
        self.assertEqual(format_value(session.eval_text("(reverse '(1 2 3))")), "(3 2 1)")
        self.assertEqual(format_value(session.eval_text("(append1 '(1 2) 3)")), "(1 2 3)")
        self.assertEqual(session.eval_text("(apply + 1 '(2 3 4))"), 10)
        self.assertEqual(session.eval_text("(apply - '(5 3))"), 2)

    def test_print_family_writes_output_buffer(self):
        session = SkillSession()
        result = session.eval_text('(progn (println "hello") (printf "n=%d" 3))')
        self.assertTrue(result)
        self.assertEqual(session.output, ['"hello"', 'n=3'])

    def test_classic_immediate_paren_calls(self):
        session = SkillSession()
        value = session.eval_text(
            """
            procedure(sumPair(a b @optional (c 10) @rest rest)
              list(plus(a b c) rest))
            list(
              plus(1 2)
              sumPair(3 4)
              sumPair(3 4 5 6 7)
              let(((x 1) (y 2)) plus(x y)))
            """
        )
        self.assertEqual(format_value(value), "(3 (17 nil) (12 (6 7)) 3)")
        self.assertEqual(session.output, [])

    def test_classic_immediate_paren_print_and_nested_calls(self):
        session = SkillSession()
        value = session.eval_text(
            """
            procedure(ping() 42)
            println("hello world")
            plus(ping() plus(1 2))
            """
        )
        self.assertEqual(value, 45)
        self.assertEqual(session.output, ['"hello world"'])

    def test_classic_if_then_else_operator_syntax(self):
        session = SkillSession()
        value = session.eval_text(
            """
            a = 1
            hit1 = if((a < 1) then println("wrong"))
            hit2 = if((a < 2) then println("right"))
            hit3 = if(a < 2 then println("then branch") else println("else branch"))
            hit4 = if(a < 1 then println("wrong") else println("fallback"))
            list(hit1 hit2 hit3 hit4)
            """
        )
        self.assertEqual(value, [None, "right", "then branch", "fallback"])
        self.assertEqual(session.output, ['"right"', '"then branch"', '"fallback"'])

    def test_if_without_then_still_supports_infix_conditions(self):
        session = SkillSession()
        value = session.eval_text(
            """
            a = 1
            list(
              if(a < 2 11 22)
              if(a > 2 11 22)
              when(a <= 1 println("when branch"))
              unless(a >= 2 println("unless branch")))
            """
        )
        self.assertEqual(value, [11, 22, "when branch", "unless branch"])
        self.assertEqual(session.output, ['"when branch"', '"unless branch"'])

    def test_println_returns_printed_value_for_recursive_list_code(self):
        session = SkillSession()
        value = session.eval_text(
            """
            procedure(MyFlattenList(data)
              let((result)
                foreach(item data
                  if(listp(item) then
                    result = append(result MyFlattenList(item))
                  else
                    result = append(result list(item))
                  )
                )
                println(result)
              )
            )
            MyFlattenList('(1 (2 3) ((4)) 5))
            """
        )
        self.assertEqual(value, [1, 2, 3, 4, 5])
        self.assertEqual(session.output[-1], "(1 2 3 4 5)")

    def test_logical_or_and_comparisons_in_classic_syntax(self):
        session = SkillSession()
        value = session.eval_text(
            """
            a = 1
            b = 3
            if(a > 2 || b >= 3 then
              println("matched")
              99
            else
              0)
            """
        )
        self.assertEqual(value, 99)
        self.assertEqual(session.output, ['"matched"'])

    def test_grouped_unary_operator_syntax(self):
        session = SkillSession()
        value = session.eval_text(
            """
            done = nil
            a = 3
            b = 5
            list(
              if((!done) then 'go else 'stop)
              (-a + b))
            """
        )
        self.assertEqual(format_value(value), "(go 2)")

    def test_tight_operator_syntax_matches_skill_examples(self):
        session = SkillSession()
        value = session.eval_text(
            """
            procedure(fib(n)
              if((n == 1 || n == 2) then
                1
              else
                fib(n-1) + fib(n-2)))
            a = 2
            b = 3
            c = 5
            x = 2
            y = 3
            z = 4
            A = 1
            x1 = 2
            B = 1
            y1 = 3
            C = 1
            list(
              fib(4)
              if(x<y+z && y<z+x && z<x+y then 'triangle else 'bad)
              if(A*x1+B*y1+C != 0.0 then 'nonzero else 'zero))
            """
        )
        self.assertEqual(format_value(value), "(3 triangle nonzero)")

    def test_cond_and_defun(self):
        session = SkillSession()
        value = session.eval_text(
            """
            (defun add3 (a b c) (+ a b c))
            (cond
              ((> 1 2) 0)
              ((< 1 2) (add3 1 2 3))
              (t 99))
            """
        )
        self.assertEqual(value, 6)

    def test_eval_set_and_funcall(self):
        session = SkillSession()
        session.eval_text("(set 'count 5)")
        self.assertEqual(session.eval_text("count"), 5)
        self.assertEqual(session.eval_text("(eval '(+ 1 2 3))"), 6)
        self.assertEqual(session.eval_text("(funcall + 1 2 3 4)"), 10)
        self.assertEqual(session.eval_text("(funcall - 5 3)"), 2)
        self.assertEqual(session.eval_text("(progn (setq ?x 5) (+ ?x 1))"), 6)

    def test_user_defined_dispatch_accepts_operator_values(self):
        session = SkillSession()
        value = session.eval_text(
            """
            (procedure (dispatch op x y)
              (funcall op x y))
            (list
              (dispatch + 1 2)
              (dispatch - 5 3)
              (dispatch < 1 2))
            """
        )
        self.assertEqual(format_value(value), "(3 2 t)")
        self.assertEqual(format_value(session.eval_text("(progn (setq ?x 5) (list ?x))")), "(5)")

    def test_operator_compatibility(self):
        session = SkillSession()
        value = session.eval_text(
            """
            tot = plus(1 2)
            flag = nil
            same = tot == 3
            diff = tot != 4
            both = same && diff
            when(flag println("skip"))
            when(!flag tot = plus(tot 4))
            list(tot same diff both !flag (= 3 3))
            """
        )
        self.assertEqual(format_value(value), "(7 t t t t t)")

    def test_infix_arithmetic_evaluation(self):
        session = SkillSession()
        value = session.eval_text(
            """
            a = 12
            b = a + a
            b
            """
        )
        self.assertEqual(value, 24)

    def test_infix_arithmetic_operators(self):
        session = SkillSession()
        value = session.eval_text(
            """
            a = 10
            b = 4
            c = 2
            list(
              a + b
              a + b * c
              a - b
              -a
              a + -b
              a - b - c
              (+ a b)
              (- a b))
            """
        )
        self.assertEqual(format_value(value), "(14 18 6 -10 6 4 14 6)")

    def test_string_and_numeric_helpers(self):
        session = SkillSession()
        self.assertEqual(session.eval_text('(sprintf "v=%d" 7)'), "v=7")
        self.assertEqual(session.eval_text('(sprintf nil "v=%d" 7)'), "v=7")
        self.assertEqual(
            session.eval_text('(progn (setq s nil) (sprintf s "v=%d" 7) s)'),
            "v=7",
        )
        self.assertEqual(session.eval_text('(let ((fmt "v=%d")) (sprintf fmt 7))'), "v=7")
        self.assertEqual(session.eval_text('(sprintf "100%%")'), "100%")
        with self.assertRaises(SkillEvalError):
            session.eval_text('(sprintf "%d %d" 1)')
        self.assertEqual(session.eval_text('(strlen "hello")'), 5)
        self.assertEqual(session.eval_text('(strcmp "abc" "abd")'), -1)
        self.assertEqual(session.eval_text('(substr "abcdef" 2 3)'), "cde")
        self.assertEqual(session.eval_text('(atoi "42")'), 42)
        self.assertEqual(session.eval_text('(atof "3.5")'), 3.5)
        self.assertTrue(session.eval_text("(integerp 4)"))
        self.assertTrue(session.eval_text("(onep 1)"))
        self.assertTrue(session.eval_text("(floatp 4.5)"))
        self.assertTrue(session.eval_text("(zerop 0)"))
        self.assertTrue(session.eval_text("(plusp 4)"))
        self.assertTrue(session.eval_text("(neq 1 2)"))
        self.assertTrue(session.eval_text("(nequal '(1 2) '(2 3))"))
        self.assertEqual(format_value(session.eval_text('(concat "a" 1 "b")')), "a1b")
        self.assertEqual(format_value(session.eval_text("(concat 'net (intern \"_1\"))")), "net_1")
        self.assertEqual(session.eval_text('(strcat "pin_" \'A)'), "pin_A")
        self.assertTrue(session.eval_text('(alphalessp "abc" "abd")'))

    def test_errset_warn_and_higher_order_helpers(self):
        session = SkillSession()
        self.assertIsNone(session.eval_text('(errset (error "boom"))'))
        self.assertIsNone(session.eval_text("(errset (arrayref (array 1) 9))"))
        self.assertIsNone(session.eval_text('(errset (load "missing.il"))'))
        self.assertEqual(session.eval_text('(errset (deleteFile "missing.txt"))'), [None])
        self.assertTrue(session.eval_text('(warn "careful")'))
        self.assertIn("Warning: careful", session.output[-1])
        self.assertEqual(session.eval_text("(getWarn)"), "careful")
        self.assertEqual(format_value(session.eval_text("(mapc (lambda (x) x) '(1 2 3))")), "(1 2 3)")
        self.assertTrue(session.eval_text("(exists (lambda (x) (> x 2)) '(1 2 3))"))
        self.assertTrue(session.eval_text("(forall (lambda (x) (> x 0)) '(1 2 3))"))

    def test_prog_variants_and_caseq(self):
        session = SkillSession()
        self.assertEqual(session.eval_text("(prog ((x 1)) (setq x (+ x 4)) (return x) 99)"), 5)
        self.assertEqual(session.eval_text("(prog1 1 2 3)"), 1)
        self.assertEqual(session.eval_text("(prog2 1 2 3)"), 2)
        self.assertEqual(session.eval_text("(caseq '(1 2) (((1 2)) 7) (t 0))"), 0)
        self.assertEqual(session.eval_text("(case '(1 2) (((1 2)) 7) (t 0))"), 7)
        self.assertEqual(session.eval_text("(caseq 'b ((a) 1) ((b c) 2))"), 2)
        self.assertEqual(session.eval_text("(progn (setq i 99) (for i 1 2 nil) i)"), 99)

    def test_symbol_and_property_helpers(self):
        session = SkillSession()
        self.assertEqual(session.eval_text("(set 'alpha 9)"), 9)
        self.assertEqual(session.eval_text("(symeval 'alpha)"), 9)
        self.assertTrue(str(format_value(session.eval_text("(gensym \"tmp\")"))).startswith("tmp"))
        self.assertTrue(str(format_value(session.eval_text("(gensym 'net)"))).startswith("net"))
        session.eval_text("(putprop 'chip 10 'width)")
        self.assertEqual(session.eval_text("(get 'chip 'width)"), 10)
        self.assertEqual(format_value(session.eval_text("(plist 'chip)")), "(width 10)")
        self.assertEqual(format_value(session.eval_text("(setplist 'chip '(height 20 width 30))")), "(height 20 width 30)")
        self.assertEqual(session.eval_text("(getq 'chip 'height)"), 20)
        self.assertEqual(session.eval_text("(getqq 'chip 'width)"), 30)
        self.assertEqual(session.eval_text("(putpropq 'chip 99 'width)"), 99)
        self.assertEqual(session.eval_text("(putpropqq 'chip 77 'depth)"), 77)
        self.assertEqual(session.eval_text("(defprop 'chip 55 'area)"), 55)
        self.assertTrue(session.eval_text("(remprop 'chip 'depth)"))

    def test_function_cell_helpers(self):
        session = SkillSession()
        session.eval_text("(putd 'twice (lambda (x) (* x 2)))")
        self.assertEqual(session.eval_text("(funcall (getd 'twice) 9)"), 18)

    def test_list_mutation_and_substitution_helpers(self):
        session = SkillSession()
        self.assertEqual(format_value(session.eval_text("(copy '(1 2 3))")), "(1 2 3)")
        self.assertEqual(format_value(session.eval_text("(nthcdr 2 '(1 2 3 4))")), "(3 4)")
        self.assertEqual(session.eval_text("(nthelem 1 '(4 5 6))"), 4)
        self.assertEqual(format_value(session.eval_text("(memq 'b '(a b c))")), "(b c)")
        self.assertEqual(format_value(session.eval_text("(assq 'mode '((mode run) (count 2)))")), "(mode run)")
        self.assertEqual(session.eval_text("(lindex 'c '(a b c d))"), 2)
        self.assertEqual(format_value(session.eval_text("(remove 2 '(1 2 3 2))")), "(1 3)")
        self.assertEqual(format_value(session.eval_text("(remq 'a '(a b a c))")), "(b c)")
        self.assertEqual(format_value(session.eval_text("(let ((x '(a b a c))) (remd 'a x))")), "(b c)")
        self.assertEqual(format_value(session.eval_text("(let ((x '(a b a c))) (remdq 'a x))")), "(b c)")
        self.assertEqual(format_value(session.eval_text("(subst 'x 'b '(a (b c) b))")), "(a (x c) x)")
        self.assertTrue(session.eval_text("(tailp '(3 4) '(1 2 3 4))"))
        self.assertEqual(
            format_value(session.eval_text("(let ((x '(1 2)) (y '(3 4))) (nconc x y))")),
            "(1 2 3 4)",
        )
        self.assertEqual(
            format_value(session.eval_text("(let ((x '(1 2 3))) (rplaca x 9) (rplacd x '(8 7)) x)")),
            "(9 8 7)",
        )

    def test_string_math_array_and_table_helpers(self):
        session = SkillSession()
        self.assertEqual(session.eval_text('(upperCase "Abc")'), "ABC")
        self.assertEqual(session.eval_text('(lowerCase "AbC")'), "abc")
        self.assertEqual(session.eval_text('(buildString "a" 1 "b")'), "a1b")
        self.assertEqual(session.eval_text("(buildString 'a 1 'b)"), "a1b")
        self.assertEqual(format_value(session.eval_text('(parseString "a  b c")')), '("a" "b" "c")')
        self.assertEqual(format_value(session.eval_text('(parseString "a,b;c" ",;")')), '("a" "b" "c")')
        self.assertEqual(session.eval_text("(add1 4)"), 5)
        self.assertEqual(session.eval_text("(sub1 4)"), 3)
        self.assertEqual(session.eval_text("(plus 1 2 3)"), 6)
        self.assertEqual(session.eval_text("(difference 9 4)"), 5)
        self.assertEqual(session.eval_text("(times 2 3 4)"), 24)
        self.assertEqual(session.eval_text("(quotient 8 2)"), 4)
        self.assertEqual(session.eval_text("(round 2.6)"), 3)
        self.assertEqual(session.eval_text("(round 2.5)"), 3)
        self.assertEqual(session.eval_text("(round -2.5)"), -3)
        self.assertAlmostEqual(session.eval_text("(sqrt 9)"), 3.0)
        self.assertAlmostEqual(session.eval_text("(exp 1)"), 2.7182818, places=5)
        self.assertAlmostEqual(session.eval_text("(log 1)"), 0.0, places=5)
        self.assertAlmostEqual(session.eval_text("(sin 0)"), 0.0, places=5)
        self.assertAlmostEqual(session.eval_text("(cos 0)"), 1.0, places=5)
        self.assertAlmostEqual(session.eval_text("(tan 0)"), 0.0, places=5)
        self.assertAlmostEqual(session.eval_text("(asin 0)"), 0.0, places=5)
        self.assertAlmostEqual(session.eval_text("(acos 1)"), 0.0, places=5)
        self.assertAlmostEqual(session.eval_text("(atan 0)"), 0.0, places=5)
        self.assertTrue(session.eval_text("(progn (srandom 11) (< (random 10) 10))"))
        self.assertEqual(
            format_value(
                session.eval_text("(let ((a (array 3 0))) (setarray a 1 9) (list (arrayp a) (arrayref a 1)))")
            ),
            "(t 9)",
        )
        with self.assertRaises(SkillEvalError):
            session.eval_text("(let ((a (array 3 0))) (arrayref a 10))")
        self.assertIsNone(session.eval_text("(arrayp '(1 2 3))"))
        self.assertIsNone(session.eval_text("(listp (array 2 0))"))
        self.assertEqual(
            format_value(
                session.eval_text(
                    "(let ((tbl (makeTable \"pins\" 0))) (put tbl 'a 11) (list (tablep tbl) (get tbl 'a) (get tbl 'b)))"
                )
            ),
            "(t 11 0)",
        )
        self.assertEqual(
            format_value(
                session.eval_text(
                    """
                    (let ((tbl (makeTable "pins" 0)))
                      (put tbl 'a 11)
                      (put tbl "b" 12)
                      (put tbl '(c d) 13)
                      (list
                        (tableToList tbl)
                        (getTableKeys tbl)
                        (removeTableEntry tbl "b")
                        (removeTableEntry tbl "missing")
                        (tableToList tbl)
                        (getTableKeys tbl)
                        (get tbl "b")))
                    """
                )
            ),
            "((a 11 \"b\" 12 (c d) 13) (a \"b\" (c d)) t nil (a 11 (c d) 13) (a (c d)) 0)",
        )
        self.assertEqual(
            format_value(session.eval_text("(let ((tbl (makeTable \"pins\"))) (list (tableToList tbl) (getTableKeys tbl)))")),
            "(nil nil)",
        )
        self.assertEqual(
            format_value(
                session.eval_text(
                    """
                    (let ((tbl (makeTable "pins" 0))
                          (seen nil))
                      (put tbl 'a 11)
                      (put tbl "b" 12)
                      (put tbl '(c d) 13)
                      (list
                        (eq (foreach key tbl
                              (setq seen (append1 seen key)))
                            tbl)
                        seen
                        (let ((empty (makeTable "empty")))
                          (eq (foreach key empty
                                (error "should not run"))
                              empty))))
                    """
                )
            ),
            "(t (a \"b\" (c d)) t)",
        )
        self.assertEqual(
            format_value(
                session.eval_text(
                    """
                    (let ((tbl (makeTable "pins" 0)))
                      (put tbl (list "symbol" "foo") 99)
                      (list (getTableKeys tbl) (tableToList tbl)))
                    """
                )
            ),
            '((("symbol" "foo")) (("symbol" "foo") 99))',
        )
        self.assertEqual(
            format_value(
                session.eval_text(
                    """
                    (list
                      (let ((tbl (makeTable "pins" 0))
                            (seen nil))
                        (put tbl 'a 1)
                        (put tbl 'b 2)
                        (foreach key tbl
                          (setq seen (append1 seen key))
                          (removeTableEntry tbl key))
                        (list seen (getTableKeys tbl)))
                      (let ((tbl (makeTable "pins" 0))
                            (seen nil))
                        (put tbl 'a 1)
                        (foreach key tbl
                          (setq seen (append1 seen key))
                          (put tbl 'b 2))
                        (list seen (getTableKeys tbl))))
                    """
                )
            ),
            "(((a b) nil) ((a) (a b)))",
        )

    def test_port_and_file_helpers(self):
        session = SkillSession()
        self.assertEqual(
            format_value(
                session.eval_text(
                    "(let ((p (outstring))) (fprintf p \"a=%d\" 5) (list (getOutstring p) (close p)))"
                )
            ),
            '("a=5" t)',
        )
        value = session.eval_text(
            "(let ((p (instring \"row1\\nrow2\\n\"))) (list (lineread p) (gets p) (getc p) (close p)))"
        )
        self.assertEqual(value[0], "row1")
        self.assertEqual(value[1], "row2\n")
        self.assertIsNone(value[2])
        self.assertTrue(value[3])
        self.assertEqual(
            format_value(session.eval_text('(let ((p (instring "10 20 30"))) (list (fscanf p "%d") (fscanf p "%d") (fscanf p "%d")) )')),
            '("10" "20" "30")',
        )
        self.assertEqual(
            format_value(session.eval_text('(let ((p (instring "10 20 30"))) (fscanf p "%d %d"))')),
            '("10" "20")',
        )
        self.assertEqual(
            format_value(session.eval_text('(let ((p (instring "10 20 30"))) (list (fscanf p "%d" "%d") (getc p) (eof p)))')),
            '(("10" "20") 3 nil)',
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "sample.txt")
            program = """
            (let ((p (outfile "%s")))
              (fprintf p "hello\\nworld")
              (close p))
            (let ((p (infile "%s")))
              (list (lineread p) (lineread p) (close p)))
            """ % (
                path.replace("\\", "\\\\"),
                path.replace("\\", "\\\\"),
            )
            self.assertEqual(format_value(session.eval_text(program)), '("hello" "world" t)')

    def test_additional_numeric_predicate_and_filesystem_helpers(self):
        session = SkillSession()
        self.assertEqual(session.eval_text("(fix 3.7)"), 3)
        self.assertEqual(session.eval_text("(float 3)"), 3.0)
        self.assertEqual(session.eval_text("(expt 2 5)"), 32)
        self.assertEqual(session.eval_text("(remainder -7 3)"), -1)
        self.assertEqual(session.eval_text("(leftshift 3 2)"), 12)
        self.assertEqual(session.eval_text("(rightshift 12 2)"), 3)
        self.assertEqual(format_value(session.eval_text("(ncons 5)")), "(5)")
        self.assertEqual(format_value(session.eval_text("(xcons '(2 3) 1)")), "(1 2 3)")
        self.assertTrue(session.eval_text("(pairp '(1 2))"))
        self.assertTrue(session.eval_text("(dtpr '(1 2))"))
        self.assertTrue(session.eval_text("(typep 4 'integer)"))
        self.assertTrue(session.eval_text("(errsetstring \"(+ 1 2 3)\")"))
        self.assertIsNone(session.eval_text('(errsetstring "(load \\"missing.il\\")")'))
        with tempfile.TemporaryDirectory() as temp_dir:
            subdir = os.path.join(temp_dir, "child")
            filepath = os.path.join(subdir, "a.txt")
            program = """
            (createDir "%s")
            (isDir "%s")
            (let ((p (outfile "%s")))
              (fprintf p "1 2 3")
              (drain p)
              (close p))
            (list
              (isFile "%s")
              (isFileName "%s")
              (getDirFiles "%s")
              (progn (changeWorkingDir "%s") (getWorkingDir))
              (setSkillPath (list "%s"))
              (getSkillPath))
            """ % (
                subdir.replace("\\", "\\\\"),
                subdir.replace("\\", "\\\\"),
                filepath.replace("\\", "\\\\"),
                filepath.replace("\\", "\\\\"),
                filepath.replace("\\", "\\\\"),
                subdir.replace("\\", "\\\\"),
                temp_dir.replace("\\", "\\\\"),
                temp_dir.replace("\\", "\\\\"),
            )
            value = session.eval_text(program)
            self.assertTrue(value[0])
            self.assertTrue(value[1])
            self.assertEqual(value[2], ["a.txt"])
            self.assertEqual(value[3], temp_dir)
            self.assertEqual(value[4], [temp_dir])
            self.assertEqual(value[5], [temp_dir])
            self.assertTrue(session.eval_text('(deleteFile "%s")' % filepath.replace("\\", "\\\\")))
            self.assertIsNone(session.eval_text('(isFile "%s")' % filepath.replace("\\", "\\\\")))
            self.assertIsNone(session.eval_text('(deleteFile "%s")' % filepath.replace("\\", "\\\\")))
        with tempfile.TemporaryDirectory() as temp_dir:
            examples_dir = os.path.join(temp_dir, "examples")
            os.makedirs(examples_dir)
            hello_path = os.path.join(examples_dir, "hello.il")
            nested_path = os.path.join(examples_dir, "nested.il")
            with open(hello_path, "w") as handle:
                handle.write('(procedure (hello name) (println (strcat "Hello, " name "!")))\n(hello "OpenSKILL")\n')
            with open(nested_path, "w") as handle:
                handle.write('(load "hello.il")\n')
            session = SkillSession(cwd=temp_dir)
            self.assertEqual(
                session.eval_text('(progn (changeWorkingDir "examples") (list (getWorkingDir) (isFile "hello.il")) )'),
                [examples_dir, True],
            )
            value = session.eval_text('(load "hello.il")')
            self.assertTrue(value)
            self.assertIn('Hello, OpenSKILL!', session.output[-1])
            session = SkillSession(cwd=temp_dir)
            session.eval_text('(setSkillPath (list "examples"))')
            value = session.eval_text('(load "hello.il")')
            self.assertTrue(value)
            self.assertIn('Hello, OpenSKILL!', session.output[-1])
            session = SkillSession(cwd=temp_dir)
            value = session.eval_text('(load "examples/nested.il")')
            self.assertTrue(value)
            self.assertIn('Hello, OpenSKILL!', session.output[-1])
            with self.assertRaises(SkillEvalError) as ctx:
                session.eval_text('(changeWorkingDir "missing-dir")')
            self.assertIn("existing directory", str(ctx.exception))

    def test_skillpp_class_definition_and_defaults(self):
        session = SkillSession()
        value = session.eval_text(
            """
            (defclass point () ((x @initarg ?x @initform 0) (y @initarg ?y @initform 2)))
            (let ((p (makeInstance 'point ?x 7)))
              (list (type p) p->x p->y))
            """
        )
        self.assertEqual(format_value(value), "(point 7 2)")

    def test_skillpp_inheritance_and_slot_writes(self):
        session = SkillSession()
        value = session.eval_text(
            """
            (defclass point () ((x @initarg ?x @initform 0) (y @initarg ?y @initform 0)))
            (defclass colorPoint (point) ((color @initarg ?color @initform "red")))
            (let ((p (makeInstance 'colorPoint ?x 3)))
              (progn
                p->y = 9
                p->color = "blue"
                (list p->x p->y p->color)))
            """
        )
        self.assertEqual(format_value(value), '(3 9 "blue")')

    def test_skillpp_symbol_plist_slot_surface(self):
        session = SkillSession()
        value = session.eval_text(
            """
            chip->width = 10
            (let ((alias 'chip))
              (list chip->width alias->width (get 'chip 'width)))
            """
        )
        self.assertEqual(format_value(value), "(10 10 10)")

    def test_skillpp_rejects_unsupported_and_invalid_forms(self):
        session = SkillSession()
        with self.assertRaises(SkillEvalError) as multiple:
            session.eval_text("(defclass bad (a b) ())")
        self.assertIn("multiple inheritance", str(multiple.exception))

        with self.assertRaises(SkillEvalError) as reader:
            session.eval_text("(defclass bad () ((x @reader readX)))")
        self.assertIn("@reader", str(reader.exception))

        session.eval_text("(defclass point () ((x @initarg ?x)))")
        with self.assertRaises(SkillEvalError) as initarg:
            session.eval_text("(makeInstance 'point ?y 1)")
        self.assertIn("unknown initarg", str(initarg.exception))

        with self.assertRaises(SkillEvalError) as target:
            session.eval_text("(progn (setq count 3) count->x)")
        self.assertIn("slot access requires", str(target.exception))

    def test_additional_port_helpers(self):
        session = SkillSession()
        value = session.eval_text(
            """
            (let ((p (instring "10 20 30")))
              (list (fscanf p "%d" "%d")
                    (fileTell p)
                    (eof p)
                    (fileSeek p 0)
                    (portp p)
                    (close p)))
            """
        )
        self.assertEqual(value[0], ["10", "20"])
        self.assertTrue(isinstance(value[1], int))
        self.assertIsNone(value[2])
        self.assertEqual(value[3], 0)
        self.assertTrue(value[4])
        self.assertTrue(value[5])

    def test_additional_core_helpers(self):
        session = SkillSession()
        self.assertEqual(session.eval_text("(caadr '((1 2) (3 4)))"), 3)
        self.assertEqual(format_value(session.eval_text("(maplist (lambda (x) x) '(1 2 3))")), "((1 2 3) (2 3) (3))")
        self.assertEqual(format_value(session.eval_text("(mapcan (lambda (x) (list x x)) '(1 2))")), "(1 1 2 2)")
        self.assertEqual(
            format_value(session.eval_text("(mapcon (lambda (x) (list (car x))) '(1 2 3))")),
            "(1 2 3)",
        )
        self.assertEqual(format_value(session.eval_text("(sort '(3 1 2) <)")), "(1 2 3)")
        self.assertEqual(format_value(session.eval_text("(sort '(c a b) nil)")), "(a b c)")
        self.assertEqual(
            format_value(session.eval_text("(sortcar '((3 c) (1 a) (2 b)) <)")),
            "((1 a) (2 b) (3 c))",
        )
        self.assertEqual(session.eval_text('(evalstring "(+ 1 2 3)")'), 6)
        self.assertEqual(session.eval_text('(loadstring "(setq tmp 9) (+ tmp 1)")'), 10)
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "loadi.il")
            with open(path, "w") as handle:
                handle.write("(+ 4 5)\n")
            expr = '(loadi "%s")' % path.replace("\\", "\\\\")
            self.assertEqual(session.eval_text(expr), 9)

    def test_macro_helpers(self):
        session = SkillSession()
        value = session.eval_text(
            """
            (defmacro inc (name)
              `(setq ,name (+ ,name 1)))
            (setq count 3)
            (inc count)
            count
            """
        )
        self.assertEqual(value, 4)
        self.assertEqual(format_value(session.eval_text("(macroexpand '(inc count))")), "(setq count (+ count 1))")
        self.assertTrue(
            session.eval_text(
                """
                (mprocedure (twice form)
                  (let ((value (cadr form)))
                    `(list ,value ,value)))
                (equal (twice 9) '(9 9))
                """
            )
        )
        self.assertEqual(
            session.eval_text(
                """
                (defmacro sum (@rest nums) `(plus ,@nums))
                (sum 1 2 3 4)
                """
            ),
            10,
        )

    def test_regex_and_symbol_conversion_helpers(self):
        session = SkillSession()
        self.assertTrue(session.eval_text('(rexMatchp "a+" "caaat")'))
        self.assertTrue(session.eval_text('(rexExecute (rexCompile "a+") "caaat")'))
        self.assertEqual(session.eval_text('(rexReplace "a+" "x" "caaat")'), "cxt")
        self.assertEqual(session.eval_text('(rexSubstitute "a+" "x" "caaat")'), "cxt")
        self.assertEqual(format_value(session.eval_text('(intern "chip")')), "chip")
        self.assertEqual(session.eval_text("(symbolName 'chip)"), "chip")
        self.assertTrue(session.eval_text("(fixp 7)"))
        self.assertTrue(session.eval_text("(minusp -1)"))
        self.assertTrue(session.eval_text("(evenp 8)"))
        self.assertTrue(session.eval_text("(oddp 9)"))
        self.assertEqual(session.eval_text('(substring "abcdef" 2 3)'), "bcd")
        self.assertEqual(format_value(session.eval_text('(getchar "abcdef" 2)')), "b")
        self.assertIsNone(session.eval_text('(getchar "abcdef" 9)'))
        self.assertEqual(session.eval_text('(index "bc" "abcdef")'), 2)
        self.assertEqual(session.eval_text('(rindex "bc" "zbcxbc")'), 5)
        self.assertEqual(session.eval_text('(nindex "bc" "zbcxbc" 3)'), 5)

    def test_lambda_closures_capture_lexical_state(self):
        session = SkillSession()
        result = session.eval_text(
            """
            (setq makeCounter
              (lambda ()
                (let ((count 0))
                  (lambda ()
                    (setq count (+ count 1))
                    count))))
            (setq c (makeCounter))
            (list (c) (c))
            """
        )
        self.assertEqual(result, [1, 2])

    def test_while_loop_has_iteration_guard(self):
        session = SkillSession()
        with self.assertRaises(SkillEvalError) as ctx:
            session.eval_text("(while t nil)")
        self.assertIn("maximum iteration limit", str(ctx.exception))

    def test_binding_removal_helpers(self):
        session = SkillSession()
        session.eval_text("(set 'alpha 9)")
        self.assertTrue(session.eval_text("(makunbound 'alpha)"))
        self.assertIsNone(session.eval_text("(boundp 'alpha)"))

    def test_catch_setof_and_mapping_helpers(self):
        session = SkillSession()
        self.assertEqual(session.eval_text("(catch 'tag (throw 'tag 9))"), 9)
        self.assertEqual(format_value(session.eval_text("(setof (lambda (x) (> x 1)) '(1 2 3))")), "(2 3)")
        self.assertEqual(format_value(session.eval_text("(exists x '(1 2 3) (> x 1))")), "(2 3)")
        self.assertTrue(session.eval_text("(forall x '(1 2 3) (> x 0))"))
        self.assertEqual(session.eval_text("(progn (setq x 77) (exists x '(1 2 3) (> x 1)) x)"), 77)
        self.assertEqual(format_value(session.eval_text("(map (lambda (x) (* x 2)) '(1 2 3))")), "(2 4 6)")
        self.assertEqual(
            format_value(session.eval_text("(let ((x '(1 2 3))) (mapinto (lambda (y) (+ y 1)) x))")),
            "(2 3 4)",
        )

    def test_flexible_parameter_lists(self):
        session = SkillSession()
        self.assertEqual(
            format_value(
                session.eval_text(
                    """
                    (procedure (trace fun @rest args)
                      args)
                    (trace 'plus 1 2 3)
                    """
                )
            ),
            "(1 2 3)",
        )
        self.assertEqual(
            format_value(
                session.eval_text(
                    """
                    (procedure (bbox height width @optional (xCoord 0) (yCoord 0))
                      (list xCoord yCoord))
                    (bbox 1 2 4)
                    """
                )
            ),
            "(4 0)",
        )
        self.assertEqual(
            format_value(
                session.eval_text(
                    """
                    (defun test (a @key x y @rest z)
                      (list a x y z))
                    (test 0 ?x 1 ?x 2)
                    """
                )
            ),
            "(0 1 nil (?x 2))",
        )
        self.assertEqual(
            session.eval_text(
                """
                (defun optional-default (x @optional (y (+ x 1)))
                  y)
                (optional-default 2)
                """
            ),
            3,
        )
        self.assertEqual(
            session.eval_text(
                """
                (defun key-default (@key (x 1) (y (+ x 2)))
                  y)
                (key-default ?x 5)
                """
            ),
            7,
        )
        self.assertEqual(
            session.eval_text(
                """
                (defun aux-default (x @aux (y (+ x 3)))
                  y)
                (aux-default 4)
                """
            ),
            7,
        )


if __name__ == "__main__":
    unittest.main()
