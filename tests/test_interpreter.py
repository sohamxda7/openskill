import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from openskill.interpreter.errors import SkillSyntaxError
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


class EvaluatorTests(unittest.TestCase):
    def test_let_and_arithmetic(self):
        session = SkillSession()
        value = session.eval_text("(let ((x 2) (y 5)) (+ x y))")
        self.assertEqual(value, 7)

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
        self.assertEqual(format_value(session.eval_text("(last '(10 20 30))")), "(30)")
        self.assertEqual(format_value(session.eval_text("(reverse '(1 2 3))")), "(3 2 1)")
        self.assertEqual(format_value(session.eval_text("(append1 '(1 2) 3)")), "(1 2 3)")
        self.assertEqual(session.eval_text("(apply + 1 '(2 3 4))"), 10)

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
        self.assertEqual(session.eval_text("(progn (setq ?x 5) (+ ?x 1))"), 6)
        self.assertEqual(format_value(session.eval_text("(progn (setq ?x 5) (list ?x))")), "(5)")

    def test_string_and_numeric_helpers(self):
        session = SkillSession()
        self.assertEqual(session.eval_text('(sprintf "v=%d" 7)'), "v=7")
        self.assertEqual(session.eval_text('(sprintf nil "v=%d" 7)'), "v=7")
        self.assertEqual(
            session.eval_text('(progn (setq s nil) (sprintf s "v=%d" 7) s)'),
            "v=7",
        )
        self.assertEqual(session.eval_text('(let ((fmt "v=%d")) (sprintf fmt 7))'), "v=7")
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
        self.assertTrue(value[2])
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
