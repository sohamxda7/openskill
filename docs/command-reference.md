<!-- Author: Soham Sen <sensoham135@gmail.com> <sohamsen2000@outlook.com> -->

# OpenSKILL Command Reference
This reference is a browsable snapshot of the offline catalog used by the CLI, REPL, and GUI API finder. It is generated from `src/openskill/api/catalog.json`.
The examples are written as runnable snippets; the test suite parses and executes every documented catalog entry.
Use `openskill api find QUERY` or `:api QUERY` in the REPL when you want to search by name.

## Arithmetic
| Symbol | Signature | Example | Summary |
| --- | --- | --- | --- |
| `%` | `left % right (compatibility; prefer mod(left right))` | `10 % 3` | Compute the remainder from integer-style division using compatibility operator syntax; prefer mod(left right) in Cadence-style examples. |
| `&` | `left & right` | `6 & 3` | Compute bitwise AND across integer values. |
| `*` | `left * right` | `2 * 3 * 4` | Multiply numbers together. |
| `**` | `base ** power` | `2 ** 5` | Raise a number to a power using Cadence SKILL exponentiation syntax. |
| `+` | `left + right` | `1 + 2 + 3` | Add numbers together. |
| `-` | `left - right or -value` | `10 - 3 - 2` | Subtract numbers or negate one value. |
| `/` | `left / right` | `20 / 5` | Divide numbers from left to right. |
| `<<` | `value << count` | `3 << 2` | Logically shift an integer left by a bit count, zero-filling vacated bits. |
| `>>` | `value >> count` | `12 >> 2` | Logically shift a 32-bit integer word right by a bit count, zero-filling vacated bits. |
| `^` | `left ^ right` | `6 ^ 3` | Compute bitwise exclusive OR across integer values. |
| `abs` | `abs(number)` | `abs(-7)` | Return the absolute value of a number. |
| `acos` | `acos(number)` | `acos(1)` | Return the inverse cosine of a value in range. |
| `add1` | `add1(number)` | `add1(4)` | Increment a number by one. |
| `asin` | `asin(number)` | `asin(0)` | Return the inverse sine of a value in range. |
| `atan` | `atan(number)` | `atan(0)` | Return the inverse tangent of a value. |
| `band` | `band(value ...)` | `band(6 3)` | Compute bitwise AND across integer values. |
| `bnand` | `bnand(left right)` | `bnand(6 3)` | Compute bitwise NAND for two integer values. |
| `bnor` | `bnor(left right)` | `bnor(6 3)` | Compute bitwise NOR for two integer values. |
| `bnot` | `bnot(value)` | `bnot(0)` | Compute bitwise NOT for one integer value. |
| `bor` | `bor(value ...)` | `bor(6 3)` | Compute bitwise OR across integer values. |
| `bxnor` | `bxnor(left right)` | `bxnor(6 3)` | Compute bitwise XNOR for two integer values. |
| `bxor` | `bxor(value ...)` | `bxor(6 3)` | Compute bitwise exclusive OR across integer values. |
| `cos` | `cos(number)` | `cos(0)` | Return the cosine of an angle in radians. |
| `difference` | `difference(number ...)` | `9 - 4` | Subtract numbers from left to right. |
| `exp` | `exp(number)` | `exp(1)` | Raise e to the given power. |
| `expt` | `expt(base power)` | `2 ** 5` | Raise a number to a power; the infix operator form is base ** power. |
| `fix` | `fix(number)` | `fix(3.7)` | Convert a number to an integer by truncation. |
| `float` | `float(number)` | `float(3)` | Convert a number to floating-point. |
| `leftshift` | `leftshift(value count)` | `3 << 2` | Logically shift an integer left by a bit count, zero-filling vacated bits. |
| `log` | `log(number)` | `log(1)` | Return the natural logarithm of a positive number. |
| `max` | `max(number ...)` | `max(7 2 5)` | Return the largest numeric argument. |
| `min` | `min(number ...)` | `min(7 2 5)` | Return the smallest numeric argument. |
| `minus` | `minus(number ...)` | `minus(10 3 2)` | Subtract numbers or negate one value. |
| `mod` | `mod(left right)` | `mod(10 3)` | Compute the remainder from integer-style division. |
| `plus` | `plus(number ...)` | `1 + 2 + 3` | Add numbers together. |
| `quotient` | `quotient(number ...)` | `8 / 2` | Divide numbers from left to right. |
| `random` | `random([limit])` | `random(10)` | Return a pseudo-random float or an integer below a supplied limit. |
| `remainder` | `remainder(left right)` | `remainder(-7 3)` | Return the truncated-division remainder, preserving the dividend sign. |
| `rightshift` | `rightshift(value count)` | `12 >> 2` | Logically shift a 32-bit integer word right by a bit count, zero-filling vacated bits. |
| `round` | `round(number)` | `round(2.6)` | Round a number to the nearest integer. |
| `sin` | `sin(number)` | `sin(0)` | Return the sine of an angle in radians. |
| `sqrt` | `sqrt(number)` | `sqrt(9)` | Return the square root of a non-negative number. |
| `srandom` | `srandom(seed)` | `srandom(11)` | Reset the pseudo-random generator to a known seed. |
| `sub1` | `sub1(number)` | `sub1(4)` | Decrement a number by one. |
| `tan` | `tan(number)` | `tan(0)` | Return the tangent of an angle in radians. |
| `times` | `times(number ...)` | `2 * 3 * 4` | Multiply numbers together. |
| `\|` | `left \| right` | `6 \| 3` | Compute bitwise OR across integer values. |
| `~` | `~value` | `~0` | Compute bitwise NOT for one integer value. |
| `~&` | `left ~& right` | `6 ~& 3` | Compute bitwise NAND for two integer values. |
| `~^` | `left ~^ right` | `6 ~^ 3` | Compute bitwise XNOR for two integer values. |
| `~\|` | `left ~\| right` | `6 ~\| 3` | Compute bitwise NOR for two integer values. |

## Array
| Symbol | Signature | Example | Summary |
| --- | --- | --- | --- |
| `array` | `array(size [init])` | `array(3 0)` | Allocate a fixed-size array value initialized with one element value. |
| `arrayref` | `arrayref(array index)` | `arrayref(array(3 0) 1)` | Read one element from an array. |
| `setarray` | `setarray(array index value)` | `let(((a array(3 0))) setarray(a 1 9))` | Update one element in an array. |

## Binding
| Symbol | Signature | Example | Summary |
| --- | --- | --- | --- |
| `let` | `let(((sym value) ...) body...)` | `let(((x 2) (y 5)) x + y)` | Create temporary local bindings for a body of expressions. |
| `set` | `set('symbol value)` | `set('count 5)` | Assign a value through a quoted symbol reference. |
| `setq` | `setq(sym value ...) or sym = value` | `setq(count 3 message "ready")` | Assign one or more symbols in the active dynamic environment. |

## Comparison
| Symbol | Signature | Example | Summary |
| --- | --- | --- | --- |
| `!=` | `left != right` | `3 != 4` | Compare two values structurally and return true when they differ. |
| `<` | `left < right` | `1 < 2 < 3` | Check for strictly increasing numeric order. |
| `<=` | `left <= right` | `1 <= 1 <= 2` | Check for nondecreasing numeric order. |
| `=` | `=(left right ...)` | `=(3 3 3)` | Check whether all numeric values are equal. |
| `==` | `left == right` | `3 == 3` | Compare two values structurally using infix equality syntax. |
| `>` | `left > right` | `3 > 2 > 1` | Check for strictly decreasing numeric order. |
| `>=` | `left >= right` | `3 >= 3 >= 1` | Check for nonincreasing numeric order. |
| `geqp` | `geqp(left right ...)` | `geqp(3 3 1)` | Check for nonincreasing numeric order. |
| `greaterp` | `greaterp(left right ...)` | `greaterp(3 2 1)` | Check for strictly decreasing numeric order. |
| `leqp` | `leqp(left right ...)` | `leqp(1 1 2)` | Check for nondecreasing numeric order. |
| `lessp` | `lessp(left right ...)` | `lessp(1 2 3)` | Check for strictly increasing numeric order. |

## Conditional
| Symbol | Signature | Example | Summary |
| --- | --- | --- | --- |
| `&&` | `left && right` | `t && 3` | Evaluate logical AND using infix syntax and SKILL truthiness. |
| `and` | `left && right` | `t && (3 > 0) && 3` | Evaluate forms left to right and stop on the first falsey result. |
| `case` | `case(key (label body...) ...)` | `case('run ((edit) 1) ((run) 2) (t 0))` | Dispatch to the first matching clause for a computed key. |
| `caseq` | `caseq(key (label body...) ...)` | `caseq('b ((a) 1) ((b c) 2))` | Dispatch across clauses using eq-style matching for each label. |
| `cond` | `cond((test body...) ...)` | `let(((x 1)) cond(((x > 0) 'pos) (t 'other)))` | Evaluate clauses in order and run the first clause whose test is truthy. |
| `if` | `if(test then trueExpr [else falseExpr])` | `if(3 > 0 then "positive" else "not-positive")` | Choose between two branches based on the truthiness of a test. |
| `or` | `left \|\| right` | `nil \|\| 7` | Evaluate forms left to right and stop on the first truthy result. |
| `unless` | `unless(test body...)` | `unless(nil "load-me-later")` | Run the body only when the test expression is falsey. |
| `when` | `when(test body...)` | `when(t println("go"))` | Run the body only when the test expression is truthy. |
| `\|\|` | `left \|\| right` | `nil \|\| 7` | Evaluate logical OR using infix syntax and SKILL truthiness. |

## Control
| Symbol | Signature | Example | Summary |
| --- | --- | --- | --- |
| `catch` | `catch(tag body...)` | `catch('tag throw('tag 9))` | Evaluate a body and intercept throws for a matching tag. |
| `return` | `return([value])` | `prog(() return(7) 9)` | Exit the nearest prog block immediately. |
| `throw` | `throw(tag value)` | `catch('tag throw('tag 9))` | Abort to the nearest matching catch and return a tagged value. |

## Definition
| Symbol | Signature | Example | Summary |
| --- | --- | --- | --- |
| `defclass` | `defclass(name (superclass) ((slot @initarg ?key @initform value) ...))` | `defclass(point () ((x @initarg ?x @initform 0) (y @initarg ?y @initform 0)))` | Define a minimal SKILL++ class with single inheritance and slot defaults. |
| `defmacro` | `defmacro(name (arg1 arg2 ... \| @rest args) body...)` | ``defmacro(unlessNil (value form) `(when ,value ,form))`` | Define a macro that receives unevaluated forms and returns expansion data. |
| `defun` | `defun(name (arg1 arg2 ...) body...)` | `defun(add2 (a b) a + b)` | Define a named procedure using a function-style declaration. |
| `lambda` | `lambda((arg1 arg2 ...) body...)` | `funcall(lambda((x) x + 1) 4)` | Create an anonymous callable for passing behavior around. |
| `mprocedure` | `mprocedure(name(form) body...)` | ``mprocedure(twice(form) `progn(,cadr(form) ,cadr(form)))`` | Define a named macro that receives the entire call form in one formal argument. |
| `nprocedure` | `nprocedure(name(arg1 arg2 ...) body...)` | `nprocedure(double(x) x * 2)` | Define a named callable using the same runtime procedure object as procedure. |
| `procedure` | `procedure(name(arg1 arg2 ...) body...)` | `procedure(greet(who) println(strcat("Hello, " who)))` | Define a named callable using dynamic runtime bindings. |

## Error
| Symbol | Signature | Example | Summary |
| --- | --- | --- | --- |
| `error` | `error(message ...)` | `errset(error("boom"))` | Raise an interpreter error with the given message. |
| `errset` | `errset(form...)` | `errset(error("boom"))` | Evaluate forms and suppress interpreter errors, returning nil on failure. |
| `errsetstring` | `errsetstring(source)` | `errsetstring("1 + 2 + 3")` | Evaluate a source string and suppress interpreter errors. |
| `getWarn` | `getWarn()` | `getWarn()` | Return and consume the oldest queued warning message. |
| `warn` | `warn(message ...)` | `warn("careful")` | Emit a warning message to the session output buffer. |

## File
| Symbol | Signature | Example | Summary |
| --- | --- | --- | --- |
| `close` | `close(port)` | `let(((port outstring())) close(port))` | Close an open file or string port. |
| `drain` | `drain(port)` | `let(((p outstring())) fprintf(p "x") drain(p))` | Flush an output port. |
| `eof` | `eof(port)` | `let(((p instring(""))) eof(p))` | Test whether an input port is at end-of-file. |
| `evalstring` | `evalstring(source)` | `evalstring("1 + 2")` | Evaluate a source string and return its result. |
| `fileLength` | `fileLength(port)` | `let(((p instring("abc"))) fileLength(p))` | Return the length of an open file or string stream. |
| `fileSeek` | `fileSeek(port position)` | `let(((p instring("abc"))) fileSeek(p 0))` | Move a port to an absolute position. |
| `fileTell` | `fileTell(port)` | `let(((p instring("abc"))) fileTell(p))` | Return the current seek position of a port. |
| `fprintf` | `fprintf(port format arg ...)` | `let(((p outstring())) fprintf(p "a=%d" 5) getOutstring(p))` | Format text and write it to an output port. |
| `fscanf` | `fscanf(port format ...)` | `let(((p instring("10 20"))) fscanf(p "%d" "%d"))` | Read whitespace-delimited fields from a port. |
| `getc` | `getc(port)` | `let(((p instring("xy"))) getc(p))` | Read one character from an input port. |
| `getOutstring` | `getOutstring(port)` | `let(((p outstring())) fprintf(p "x") getOutstring(p))` | Read the accumulated contents of an in-memory string output port. |
| `gets` | `gets(port)` | `let(((p instring("row1\nrow2"))) gets(p))` | Read one line from an input port and preserve the trailing newline when present. |
| `infile` | `infile(path)` | `let(((p outfile("notes.txt"))) fprintf(p "row1\nrow2") close(p) close(infile("notes.txt")))` | Open a file for line and character input. |
| `instring` | `instring(string)` | `instring("row1\nrow2")` | Create an input port that reads from a string buffer. |
| `lineread` | `lineread(port)` | `let(((p instring("row1\nrow2"))) lineread(p))` | Read one line from an input port, without the newline terminator. |
| `load` | `load(path)` | `let(((p outfile("startup.il"))) fprintf(p "1 + 2") close(p) load("startup.il"))` | Read and execute another SKILL source file. |
| `loadi` | `loadi(path)` | `let(((p outfile("startup.il"))) fprintf(p "3 + 4") close(p) loadi("startup.il"))` | Load a file through the interpreter's standard file loader. |
| `loadstring` | `loadstring(source)` | `loadstring("1 + 2")` | Evaluate a source string as if it had been loaded from a file. |
| `outfile` | `outfile(path)` | `let(((p outfile("notes.txt"))) fprintf(p "note") close(p))` | Open a file for text output. |
| `outstring` | `outstring()` | `outstring()` | Create an output port backed by an in-memory string buffer. |

## Filesystem
| Symbol | Signature | Example | Summary |
| --- | --- | --- | --- |
| `changeWorkingDir` | `changeWorkingDir(path)` | `changeWorkingDir(".")` | Change the interpreter's current working directory. |
| `createDir` | `createDir(path)` | `createDir("build")` | Create a directory path if it does not already exist. |
| `deleteFile` | `deleteFile(path)` | `let(((p outfile("old.log"))) fprintf(p "done") close(p) deleteFile("old.log"))` | Delete a file path. |
| `getDirFiles` | `getDirFiles(path)` | `getDirFiles(".")` | Return the sorted file names inside a directory. |
| `getSkillPath` | `getSkillPath()` | `getSkillPath()` | Return the current SKILL load path list used by the session. |
| `getWorkingDir` | `getWorkingDir()` | `getWorkingDir()` | Return the interpreter's current working directory. |
| `isDir` | `isDir(path)` | `isDir(".")` | Test whether a path names a directory. |
| `isFile` | `isFile(path)` | `isFile("notes.txt")` | Test whether a path names a regular file. |
| `isFileName` | `isFileName(path)` | `isFileName("notes.txt")` | Test whether a value looks like a non-empty file name string. |
| `setSkillPath` | `setSkillPath(path-list)` | `setSkillPath(list("."))` | Replace the current SKILL load path list used by the session. |

## Function
| Symbol | Signature | Example | Summary |
| --- | --- | --- | --- |
| `apply` | `apply(func arg... list)` | `apply(lambda((a b c d) a + b + c + d) 1 '(2 3 4))` | Call a function using explicit arguments plus a final list of trailing arguments. |
| `eval` | `eval(form)` | `eval(quote(plus(1 2 3)))` | Evaluate data as code in the current runtime environment. |
| `funcall` | `funcall(func arg ...)` | `funcall(lambda((a b c) a + b + c) 1 2 3)` | Invoke a callable with explicit arguments. |

## List
| Symbol | Signature | Example | Summary |
| --- | --- | --- | --- |
| `append` | `append(list1 list2 ...)` | `append('(1 2) '(3 4))` | Join multiple lists into one sequence. |
| `append1` | `append1(list value)` | `append1('(1 2) 3)` | Append one item to the end of a list. |
| `assoc` | `assoc(key alist)` | `assoc('mode '((mode run) (count 2)))` | Search an association list for a pair whose first item matches the key. |
| `assq` | `assq(key alist)` | `assq('mode '((mode run) (count 2)))` | Search an association list using eq-style key matching. |
| `caadr` | `caadr(list)` | `caadr('((1 2) (3 4)))` | Return the first element of the second nested list. |
| `caar` | `caar(list)` | `caar('((10 20) (30 40)))` | Return the first element of the first nested list. |
| `caddr` | `caddr(list)` | `caddr('(10 20 30))` | Return the third element of a list. |
| `cadr` | `cadr(list)` | `cadr('(10 20 30))` | Return the second element of a list. |
| `car` | `car(list)` | `car('(10 20 30))` | Return the first element of a list. |
| `cdar` | `cdar(list)` | `cdar('((10 20) (30 40)))` | Return the tail of the first nested list. |
| `cddr` | `cddr(list)` | `cddr('(10 20 30 40))` | Return the list after dropping the first two elements. |
| `cdr` | `cdr(list)` | `cdr('(10 20 30))` | Return the remainder of a list after the first element. |
| `cons` | `cons(head tail)` | `cons(0 list(1 2 3))` | Add a new element to the front of an existing list. |
| `copy` | `copy(value)` | `copy('(1 2 3))` | Copy a list value before further mutation. |
| `copylist` | `copylist(list)` | `copylist('(1 2 3))` | Create a shallow copy of a list. |
| `exists` | `exists(var list test)` | `exists(x '(1 2 3) (x > 1))` | Return the first matching tail whose bound element satisfies the test. |
| `forall` | `forall(var list test)` | `forall(x '(1 2 3) (x > 0))` | Return t when every element satisfies the test expression. |
| `last` | `last(list)` | `last('(10 20 30))` | Return the final tail of a list. |
| `length` | `length(value)` | `length('(a b c))` | Measure the size of a list or string-like container. |
| `lindex` | `lindex(item list)` | `lindex('c '(a b c d))` | Return the zero-based index of the first matching item. |
| `list` | `list(value ...)` | `list(1 2 3)` | Build a new list from evaluated values. |
| `map` | `map(func list)` | `map(lambda((x) x * 2) '(1 2 3))` | Apply a callable to each list element and collect the results. |
| `mapc` | `mapc(func list)` | `mapc(println '(1 2 3))` | Apply a function to each element for side effects and return the original list. |
| `mapcan` | `mapcan(func list)` | `mapcan(lambda((x) list(x x)) '(1 2))` | Map over a list and concatenate each list result. |
| `mapcar` | `mapcar(func list)` | `mapcar(lambda((x) x * 2) '(1 2 3))` | Apply a callable to each list element and collect the results. |
| `mapcon` | `mapcon(func list)` | `mapcon(lambda((x) list(car(x))) '(1 2 3))` | Map over successive list tails and concatenate each list result. |
| `mapinto` | `mapinto(func list)` | `let(((x '(1 2 3))) mapinto(lambda((y) y + 1) x))` | Map a callable over a list and write the results back into the same list. |
| `maplist` | `maplist(func list)` | `maplist(lambda((x) x) '(1 2 3))` | Apply a callable to each successive tail of a list and collect the results. |
| `member` | `member(item list)` | `member('b '(a b c))` | Find the first matching item and return the matching tail. |
| `memq` | `memq(item list)` | `memq('b '(a b c))` | Find the first eq-matching item and return the matching tail. |
| `nconc` | `nconc(list1 list2 ...)` | `let(((x '(1 2))) nconc(x '(3 4)))` | Destructively join lists by extending the first live list. |
| `ncons` | `ncons(value)` | `ncons(5)` | Build a one-element list. |
| `nth` | `nth(index list)` | `nth(1 '(10 20 30))` | Read a list element by zero-based index. |
| `nthcdr` | `nthcdr(index list)` | `nthcdr(2 '(1 2 3 4))` | Return the list tail that starts at a zero-based index. |
| `nthelem` | `nthelem(index list)` | `nthelem(1 '(4 5 6))` | Return a list element by one-based index. |
| `remd` | `remd(item list)` | `let(((x '(a b a c))) remd('a x))` | Destructively remove equal-matching elements from a list. |
| `remdq` | `remdq(item list)` | `let(((x '(a b a c))) remdq('a x))` | Destructively remove eq-matching elements from a list. |
| `remove` | `remove(item list)` | `remove(2 '(1 2 3 2))` | Return a list with matching elements removed using structural comparison. |
| `remq` | `remq(item list)` | `remq('a '(a b a c))` | Return a list with matching elements removed using eq-style comparison. |
| `reverse` | `reverse(list)` | `reverse('(1 2 3))` | Return a new list with the item order reversed. |
| `rplaca` | `rplaca(list value)` | `let(((x '(1 2 3))) rplaca(x 9))` | Replace the first element of a non-empty list. |
| `rplacd` | `rplacd(list tail)` | `let(((x '(1 2 3))) rplacd(x '(8 7)))` | Replace the tail of a non-empty list. |
| `setof` | `setof(func list)` | `setof(lambda((x) x > 1) '(1 2 3))` | Return the list of input elements whose predicate result is truthy. |
| `sort` | `sort(list predicate)` | `sort('(3 1 2) <)` | Sort a list in place using a comparison predicate or nil for default ordering. |
| `sortcar` | `sortcar(list predicate)` | `sortcar('((3 c) (1 a) (2 b)) <)` | Sort a list of lists in place using each element's first item as the sort key. |
| `subst` | `subst(new old tree)` | `subst('x 'b '(a (b c) b))` | Recursively replace matching values in a nested list tree. |
| `xcons` | `xcons(tail head)` | `xcons('(2 3) 1)` | Build a list by consing the second argument onto the first list tail. |

## Loop
| Symbol | Signature | Example | Summary |
| --- | --- | --- | --- |
| `for` | `for(sym start end body...)` | `for(i 1 3 println(i))` | Iterate from start to end, including the end value. |
| `foreach` | `foreach(sym sequence body...)` | `foreach(item list(1 2 3) println(item))` | Walk each item in a list, or each key in a table, and bind it to a loop symbol. |
| `while` | `while(test body...)` | `let(((i 0)) while((i < 3) setq(i (i + 1))))` | Repeat a body while the test expression stays truthy. |

## Meta
| Symbol | Signature | Example | Summary |
| --- | --- | --- | --- |
| `gensym` | `gensym([prefix])` | `gensym('net)` | Generate a fresh unbound symbol name with an optional string or symbol prefix. |
| `getd` | `getd('symbol)` | `getd('printf)` | Read the current callable bound to a quoted symbol. |
| `intern` | `intern(string)` | `intern("chip")` | Convert a string into a symbol value. |
| `macroexpand` | `macroexpand(form)` | ``progn(defmacro(inc (name) `setq(,name plus(,name 1))) macroexpand('(inc count)))`` | Expand one macro call without evaluating the resulting form. |
| `makunbound` | `makunbound('symbol)` | `makunbound('count)` | Remove a value binding from the current runtime environment. |
| `putd` | `putd('symbol callable)` | `putd('twice lambda((x) x * 2))` | Store a callable under a quoted symbol name. |
| `symbolName` | `symbolName('symbol)` | `symbolName('chip)` | Return the printable name of a symbol. |
| `symeval` | `symeval('symbol)` | `progn(setq(count 3) symeval('count))` | Read the current value stored under a quoted symbol. |

## Object
| Symbol | Signature | Example | Summary |
| --- | --- | --- | --- |
| `->` | `obj->slot or obj->slot = value` | `progn(chip->width = 10 chip->width)` | Read or write a symbol plist entry or class instance slot using arrow surface syntax. |
| `makeInstance` | `makeInstance('className ?initarg value ...)` | `progn(defclass(point () ((x @initarg ?x @initform 0))) makeInstance('point ?x 3))` | Instantiate a defclass-defined class using supported initargs and initforms. |

## Output
| Symbol | Signature | Example | Summary |
| --- | --- | --- | --- |
| `print` | `print(value ...)` | `print("ready")` | Render values into the session output stream. |
| `printf` | `printf(format arg ...)` | `printf("count=%d" 3)` | Format text and send it to the session output buffer. |
| `println` | `println(value ...)` | `println("ready")` | Render values for console-style output. |

## Predicate
| Symbol | Signature | Example | Summary |
| --- | --- | --- | --- |
| `!` | `!expr` | `!nil` | Invert SKILL truthiness using unary null-operator syntax. |
| `arrayp` | `arrayp(value)` | `arrayp(array(3 0))` | Test whether a value is an array. |
| `atom` | `atom(value)` | `atom('a)` | Test whether a value is not a list. |
| `boundp` | `boundp('symbol)` | `boundp('ready)` | Check whether a quoted symbol currently has a bound value. |
| `dtpr` | `dtpr(value)` | `dtpr('(1 2))` | Test whether a value is a non-empty list pair. |
| `eq` | `eq(left right)` | `eq('a 'a)` | Check whether two values compare as the same simple value. |
| `equal` | `equal(left right)` | `'(1 2) == '(1 2)` | Compare values structurally, including list contents. |
| `evenp` | `evenp(value)` | `evenp(8)` | Test whether an integer is even. |
| `fixp` | `fixp(value)` | `fixp(7)` | Test whether a value is an integer. |
| `floatp` | `floatp(value)` | `floatp(4.5)` | Test whether a value is a floating-point number. |
| `integerp` | `integerp(value)` | `integerp(4)` | Test whether a value is an integer. |
| `listp` | `listp(value)` | `listp('(1 2))` | Test whether a value is a list or nil. |
| `minusp` | `minusp(value)` | `minusp(-1)` | Test whether a numeric value is less than zero. |
| `neq` | `neq(left right)` | `neq('a 'b)` | Check whether two values are not eq-equal. |
| `nequal` | `nequal(left right)` | `'(1 2) != '(2 3)` | Check whether two values differ structurally. |
| `not` | `not(value)` | `!nil` | Invert SKILL truthiness, treating only nil as false. |
| `null` | `null(value)` | `null(nil)` | Test whether a value is nil. |
| `numberp` | `numberp(value)` | `numberp(42)` | Test whether a value is numeric. |
| `oddp` | `oddp(value)` | `oddp(9)` | Test whether an integer is odd. |
| `onep` | `onep(value)` | `onep(1)` | Test whether a numeric value is exactly one. |
| `pairp` | `pairp(value)` | `pairp('(1 2))` | Test whether a value is a non-empty list. |
| `plusp` | `plusp(value)` | `plusp(4)` | Test whether a numeric value is greater than zero. |
| `portp` | `portp(value)` | `let(((p instring("x"))) portp(p))` | Test whether a value is an open port. |
| `stringp` | `stringp(value)` | `stringp("hello")` | Test whether a value is a string. |
| `symbolp` | `symbolp(value)` | `symbolp('mode)` | Test whether a value is a symbol. |
| `tablep` | `tablep(value)` | `tablep(makeTable("pins" 0))` | Test whether a value is a table. |
| `tailp` | `tailp(tail list)` | `tailp('(3 4) '(1 2 3 4))` | Test whether one list appears as a tail of another. |
| `type` | `type(value)` | `type('(1 2 3))` | Return a simple symbolic description of a runtime value. |
| `typep` | `typep(value type-symbol)` | `typep(4 'integer)` | Test whether a value reports the given type symbol. |
| `zerop` | `zerop(value)` | `zerop(0)` | Test whether a numeric value is zero. |

## Property
| Symbol | Signature | Example | Summary |
| --- | --- | --- | --- |
| `defprop` | `defprop('symbol value key)` | `defprop('chip 10 'width)` | Define a property value on a symbol. |
| `get` | `get(target key)` | `get('chip 'width)` | Read a property from a symbol plist or a value from a table. |
| `getq` | `getq(target key)` | `getq('chip 'width)` | Read a property using the same runtime behavior as get. |
| `getqq` | `getqq(target key)` | `getqq('chip 'width)` | Read a property using the same runtime behavior as get. |
| `plist` | `plist('symbol)` | `plist('chip)` | Return the current property list for a symbol. |
| `putprop` | `putprop('symbol value key)` | `putprop('chip 10 'width)` | Store one property value on a symbol. |
| `putpropq` | `putpropq('symbol value key)` | `putpropq('chip 10 'width)` | Store one property value on a symbol. |
| `putpropqq` | `putpropqq('symbol value key)` | `putpropqq('chip 10 'width)` | Store one property value on a symbol. |
| `remprop` | `remprop('symbol key)` | `remprop('chip 'width)` | Remove one property from a symbol plist. |
| `setplist` | `setplist('symbol plist)` | `setplist('chip '(width 10 height 20))` | Replace the entire property list for a symbol. |

## Range
| Symbol | Signature | Example | Summary |
| --- | --- | --- | --- |
| `:` | `left : right` | `1:3` | Build a two-element range list from two evaluated values. |
| `range` | `range(left right)` | `range(1 3)` | Build a two-element range list from two evaluated values. |

## Reader
| Symbol | Signature | Example | Summary |
| --- | --- | --- | --- |
| `quasiquote` | ``quasiquote(form) or `form`` | ```(a ,(1 + 2) ,@list(4 5))`` | Build literal-looking data while allowing selected parts to evaluate. |
| `quote` | `quote(form) or 'form` | `'(a b c)` | Return literal data instead of evaluating it as code. |

## Regex
| Symbol | Signature | Example | Summary |
| --- | --- | --- | --- |
| `rexCompile` | `rexCompile(pattern)` | `rexCompile("a+")` | Compile a regular-expression pattern for reuse. |
| `rexExecute` | `rexExecute(regex string)` | `rexExecute(rexCompile("a+") "caaat")` | Check whether a compiled regex or pattern matches a string. |
| `rexMatchp` | `rexMatchp(regex string)` | `rexMatchp("a+" "caaat")` | Check whether a regex or pattern matches a string. |
| `rexReplace` | `rexReplace(regex replacement string)` | `rexReplace("a+" "x" "caaat")` | Replace regex matches in a string. |
| `rexSubstitute` | `rexSubstitute(regex replacement string)` | `rexSubstitute("a+" "x" "caaat")` | Replace regex matches in a string. |

## Sequencing
| Symbol | Signature | Example | Summary |
| --- | --- | --- | --- |
| `prog` | `prog(((sym value) ...) body...)` | `prog(((x 1)) return((x + 4)))` | Create local variables for a block that can exit early with return. |
| `prog1` | `prog1(form1 form2 ...)` | `prog1(setq(x 1) setq(x 2))` | Evaluate all forms and keep the first result. |
| `prog2` | `prog2(form1 form2 form3 ...)` | `prog2(1 (1 + 1) 3)` | Evaluate all forms and keep the second result. |
| `progn` | `progn(form1 form2 ...)` | `progn(a = 1 b = 2 a + b)` | Group expressions and return the final result. |

## String
| Symbol | Signature | Example | Summary |
| --- | --- | --- | --- |
| `alphalessp` | `alphalessp(left right)` | `alphalessp("abc" "abd")` | Test whether one string sorts before another lexicographically. |
| `atof` | `atof(string)` | `atof("3.5")` | Convert a numeric string to a floating-point value. |
| `atoi` | `atoi(string)` | `atoi("42")` | Convert a numeric string to an integer. |
| `buildString` | `buildString(piece ...)` | `buildString("a" 1 "b")` | Assemble a string from several values. |
| `concat` | `concat(piece ...)` | `concat("a" 1 "b")` | Create a symbol by concatenating several pieces into one print name. |
| `getchar` | `getchar(string index)` | `getchar("abcdef" 2)` | Return one character from a string using one-based indexing. |
| `index` | `index(needle string)` | `index("bc" "abcdef")` | Return the one-based position of the first matching substring. |
| `lowerCase` | `lowerCase(string)` | `lowerCase("AbC")` | Convert a string to lowercase. |
| `nindex` | `nindex(needle string start)` | `nindex("bc" "zbcxbc" 3)` | Return the one-based position of the first match at or after a one-based starting index. |
| `parseString` | `parseString(string [delimiters])` | `parseString("a,b;c" ",;")` | Split a string into tokens using whitespace or an explicit delimiter set. |
| `rindex` | `rindex(needle string)` | `rindex("bc" "zbcxbc")` | Return the one-based position of the last matching substring. |
| `sprintf` | `sprintf(dest-or-nil format arg ...)` | `sprintf(nil "v=%d" 7)` | Format text, optionally store it in a destination variable, and return the resulting string. |
| `strcat` | `strcat(piece ...)` | `strcat("net_" 7)` | Concatenate multiple values into one string. |
| `strcmp` | `strcmp(left right)` | `strcmp("abc" "abd")` | Compare two strings lexicographically. |
| `strlen` | `strlen(string)` | `strlen("hello")` | Return the length of a string. |
| `substr` | `substr(string start [length])` | `substr("abcdef" 2 3)` | Return a slice of a string using the current interpreter's zero-based offsets. |
| `substring` | `substring(string start [length])` | `substring("abcdef" 2 3)` | Return a slice of a string using one-based starting positions. |
| `upperCase` | `upperCase(string)` | `upperCase("Abc")` | Convert a string to uppercase. |

## Table
| Symbol | Signature | Example | Summary |
| --- | --- | --- | --- |
| `getTableKeys` | `getTableKeys(table)` | `let(((tbl makeTable("pins" 0))) put(tbl 'a 11) getTableKeys(tbl))` | Return the keys currently stored in a table in insertion order. |
| `makeTable` | `makeTable(name [default])` | `makeTable("pins" 0)` | Allocate a table with an optional default value for missing keys. |
| `put` | `put(table key value)` | `let(((tbl makeTable("pins" 0))) put(tbl 'a 11))` | Store a value under a table key. |
| `removeTableEntry` | `removeTableEntry(table key)` | `let(((tbl makeTable("pins" 0))) put(tbl 'a 11) removeTableEntry(tbl 'a))` | Delete one key from a table if it exists. |
| `tableToList` | `tableToList(table)` | `let(((tbl makeTable("pins" 0))) put(tbl 'a 11) tableToList(tbl))` | Flatten table contents into a plist-style key/value list in insertion order. |
