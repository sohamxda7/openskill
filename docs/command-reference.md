# OpenSKILL Command Reference
This reference is a browsable snapshot of the offline catalog used by the CLI, REPL, and GUI API finder. It is generated from `src/openskill/api/catalog.json`.
Use `openskill api find QUERY` or `:api QUERY` in the REPL when you want to search by name.
## Arithmetic
| Symbol | Signature | Summary |
| --- | --- | --- |
| `*` | `(* number ...)` | Multiply numbers together. |
| `+` | `(+ number ...)` | Add numbers together. |
| `-` | `(- number ...)` | Subtract numbers or negate one value. |
| `/` | `(/ number ...)` | Divide numbers from left to right. |
| `abs` | `(abs number)` | Return the absolute value of a number. |
| `acos` | `(acos number)` | Return the inverse cosine of a value in range. |
| `add1` | `(add1 number)` | Increment a number by one. |
| `asin` | `(asin number)` | Return the inverse sine of a value in range. |
| `atan` | `(atan number)` | Return the inverse tangent of a value. |
| `cos` | `(cos number)` | Return the cosine of an angle in radians. |
| `difference` | `(difference number ...)` | Subtract numbers from left to right. |
| `exp` | `(exp number)` | Raise e to the given power. |
| `expt` | `(expt base power)` | Raise a number to a power. |
| `fix` | `(fix number)` | Convert a number to an integer by truncation. |
| `float` | `(float number)` | Convert a number to floating-point. |
| `leftshift` | `(leftshift value count)` | Shift an integer left by a bit count. |
| `log` | `(log number)` | Return the natural logarithm of a positive number. |
| `max` | `(max number ...)` | Return the largest numeric argument. |
| `min` | `(min number ...)` | Return the smallest numeric argument. |
| `mod` | `(mod left right)` | Compute the remainder from integer-style division. |
| `plus` | `(plus number ...)` | Add numbers together. |
| `quotient` | `(quotient number ...)` | Divide numbers from left to right. |
| `random` | `(random [limit])` | Return a pseudo-random float or an integer below a supplied limit. |
| `remainder` | `(remainder left right)` | Return the truncated-division remainder, preserving the dividend sign. |
| `rightshift` | `(rightshift value count)` | Shift an integer right by a bit count. |
| `round` | `(round number)` | Round a number to the nearest integer. |
| `sin` | `(sin number)` | Return the sine of an angle in radians. |
| `sqrt` | `(sqrt number)` | Return the square root of a non-negative number. |
| `srandom` | `(srandom seed)` | Reset the pseudo-random generator to a known seed. |
| `sub1` | `(sub1 number)` | Decrement a number by one. |
| `tan` | `(tan number)` | Return the tangent of an angle in radians. |
| `times` | `(times number ...)` | Multiply numbers together. |

## Array
| Symbol | Signature | Summary |
| --- | --- | --- |
| `array` | `(array size [init])` | Allocate a fixed-size array value initialized with one element value. |
| `arrayref` | `(arrayref array index)` | Read one element from an array. |
| `setarray` | `(setarray array index value)` | Update one element in an array. |

## Binding
| Symbol | Signature | Summary |
| --- | --- | --- |
| `let` | `(let ((sym value) ...) body...)` | Create temporary local bindings for a body of expressions. |
| `set` | `(set 'symbol value)` | Assign a value through a quoted symbol reference. |
| `setq` | `(setq sym value ...)` | Assign one or more symbols in the active dynamic environment. |

## Comparison
| Symbol | Signature | Summary |
| --- | --- | --- |
| `<` | `(< left right ...)` | Check for strictly increasing numeric order. |
| `<=` | `(<= left right ...)` | Check for nondecreasing numeric order. |
| `=` | `(= left right ...)` | Check whether all numeric values are equal. |
| `>` | `(> left right ...)` | Check for strictly decreasing numeric order. |
| `>=` | `(>= left right ...)` | Check for nonincreasing numeric order. |

## Conditional
| Symbol | Signature | Summary |
| --- | --- | --- |
| `and` | `(and form...)` | Evaluate forms left to right and stop on the first falsey result. |
| `case` | `(case key (label body...) ...)` | Dispatch to the first matching clause for a computed key. |
| `caseq` | `(caseq key (label body...) ...)` | Dispatch across clauses using eq-style matching for each label. |
| `cond` | `(cond (test body...) ...)` | Evaluate clauses in order and run the first clause whose test is truthy. |
| `if` | `(if test then [else])` | Choose between two branches based on the truthiness of a test. |
| `or` | `(or form...)` | Evaluate forms left to right and stop on the first truthy result. |
| `unless` | `(unless test body...)` | Run the body only when the test expression is falsey. |
| `when` | `(when test body...)` | Run the body only when the test expression is truthy. |

## Control
| Symbol | Signature | Summary |
| --- | --- | --- |
| `catch` | `(catch tag body...)` | Evaluate a body and intercept throws for a matching tag. |
| `return` | `(return [value])` | Exit the nearest prog block immediately. |
| `throw` | `(throw tag value)` | Abort to the nearest matching catch and return a tagged value. |

## Definition
| Symbol | Signature | Summary |
| --- | --- | --- |
| `defmacro` | `(defmacro name (arg1 arg2 ... \| @rest args) body...)` | Define a macro that receives unevaluated forms and returns expansion data. |
| `defun` | `(defun name (arg1 arg2 ...) body...)` | Define a named procedure using a function-style declaration. |
| `lambda` | `(lambda (arg1 arg2 ...) body...)` | Create an anonymous callable for passing behavior around. |
| `mprocedure` | `(mprocedure (name form) body...)` | Define a named macro that receives the entire call form in one formal argument. |
| `nprocedure` | `(nprocedure (name arg1 arg2 ...) body...)` | Define a named callable using the same runtime procedure object as procedure. |
| `procedure` | `(procedure (name arg1 arg2 ...) body...)` | Define a named callable using dynamic runtime bindings. |

## Error
| Symbol | Signature | Summary |
| --- | --- | --- |
| `error` | `(error message ...)` | Raise an interpreter error with the given message. |
| `errset` | `(errset form...)` | Evaluate forms and suppress interpreter errors, returning nil on failure. |
| `errsetstring` | `(errsetstring source)` | Evaluate a source string and suppress interpreter errors. |
| `getWarn` | `(getWarn)` | Return and consume the oldest queued warning message. |
| `warn` | `(warn message ...)` | Emit a warning message to the session output buffer. |

## File
| Symbol | Signature | Summary |
| --- | --- | --- |
| `close` | `(close port)` | Close an open file or string port. |
| `drain` | `(drain port)` | Flush an output port. |
| `eof` | `(eof port)` | Test whether an input port is at end-of-file. |
| `evalstring` | `(evalstring source)` | Evaluate a source string and return its result. |
| `fileLength` | `(fileLength port)` | Return the length of an open file or string stream. |
| `fileSeek` | `(fileSeek port position)` | Move a port to an absolute position. |
| `fileTell` | `(fileTell port)` | Return the current seek position of a port. |
| `fprintf` | `(fprintf port format arg ...)` | Format text and write it to an output port. |
| `fscanf` | `(fscanf port format ...)` | Read whitespace-delimited fields from a port. |
| `getc` | `(getc port)` | Read one character from an input port. |
| `getOutstring` | `(getOutstring port)` | Read the accumulated contents of an in-memory string output port. |
| `gets` | `(gets port)` | Read one line from an input port and preserve the trailing newline when present. |
| `infile` | `(infile path)` | Open a file for line and character input. |
| `instring` | `(instring string)` | Create an input port that reads from a string buffer. |
| `lineread` | `(lineread port)` | Read one line from an input port, without the newline terminator. |
| `load` | `(load path)` | Read and execute another SKILL source file. |
| `loadi` | `(loadi path)` | Load a file through the interpreter's standard file loader. |
| `loadstring` | `(loadstring source)` | Evaluate a source string as if it had been loaded from a file. |
| `outfile` | `(outfile path)` | Open a file for text output. |
| `outstring` | `(outstring)` | Create an output port backed by an in-memory string buffer. |

## Filesystem
| Symbol | Signature | Summary |
| --- | --- | --- |
| `changeWorkingDir` | `(changeWorkingDir path)` | Change the interpreter's current working directory. |
| `createDir` | `(createDir path)` | Create a directory path if it does not already exist. |
| `deleteFile` | `(deleteFile path)` | Delete a file path. |
| `getDirFiles` | `(getDirFiles path)` | Return the sorted file names inside a directory. |
| `getSkillPath` | `(getSkillPath)` | Return the current SKILL load path list used by the session. |
| `getWorkingDir` | `(getWorkingDir)` | Return the interpreter's current working directory. |
| `isDir` | `(isDir path)` | Test whether a path names a directory. |
| `isFile` | `(isFile path)` | Test whether a path names a regular file. |
| `isFileName` | `(isFileName path)` | Test whether a value looks like a non-empty file name string. |
| `setSkillPath` | `(setSkillPath path-list)` | Replace the current SKILL load path list used by the session. |

## Function
| Symbol | Signature | Summary |
| --- | --- | --- |
| `apply` | `(apply func arg... list)` | Call a function using explicit arguments plus a final list of trailing arguments. |
| `eval` | `(eval form)` | Evaluate data as code in the current runtime environment. |
| `funcall` | `(funcall func arg ...)` | Invoke a callable with explicit arguments. |

## List
| Symbol | Signature | Summary |
| --- | --- | --- |
| `append` | `(append list1 list2 ...)` | Join multiple lists into one sequence. |
| `append1` | `(append1 list value)` | Append one item to the end of a list. |
| `assoc` | `(assoc key alist)` | Search an association list for a pair whose first item matches the key. |
| `assq` | `(assq key alist)` | Search an association list using eq-style key matching. |
| `caadr` | `(caadr list)` | Return the first element of the second nested list. |
| `caar` | `(caar list)` | Return the first element of the first nested list. |
| `caddr` | `(caddr list)` | Return the third element of a list. |
| `cadr` | `(cadr list)` | Return the second element of a list. |
| `car` | `(car list)` | Return the first element of a list. |
| `cdar` | `(cdar list)` | Return the tail of the first nested list. |
| `cddr` | `(cddr list)` | Return the list after dropping the first two elements. |
| `cdr` | `(cdr list)` | Return the remainder of a list after the first element. |
| `cons` | `(cons head tail)` | Add a new element to the front of an existing list. |
| `copy` | `(copy value)` | Copy a list value before further mutation. |
| `copylist` | `(copylist list)` | Create a shallow copy of a list. |
| `exists` | `(exists var list test)` | Return the first matching tail whose bound element satisfies the test. |
| `forall` | `(forall var list test)` | Return t when every element satisfies the test expression. |
| `last` | `(last list)` | Return the final tail of a list. |
| `length` | `(length value)` | Measure the size of a list or string-like container. |
| `lindex` | `(lindex item list)` | Return the zero-based index of the first matching item. |
| `list` | `(list value ...)` | Build a new list from evaluated values. |
| `map` | `(map func list)` | Apply a callable to each list element and collect the results. |
| `mapc` | `(mapc func list)` | Apply a function to each element for side effects and return the original list. |
| `mapcan` | `(mapcan func list)` | Map over a list and concatenate each list result. |
| `mapcar` | `(mapcar func list)` | Apply a callable to each list element and collect the results. |
| `mapcon` | `(mapcon func list)` | Map over successive list tails and concatenate each list result. |
| `mapinto` | `(mapinto func list)` | Map a callable over a list and write the results back into the same list. |
| `maplist` | `(maplist func list)` | Apply a callable to each successive tail of a list and collect the results. |
| `member` | `(member item list)` | Find the first matching item and return the matching tail. |
| `memq` | `(memq item list)` | Find the first eq-matching item and return the matching tail. |
| `nconc` | `(nconc list1 list2 ...)` | Destructively join lists by extending the first live list. |
| `ncons` | `(ncons value)` | Build a one-element list. |
| `nth` | `(nth index list)` | Read a list element by zero-based index. |
| `nthcdr` | `(nthcdr index list)` | Return the list tail that starts at a zero-based index. |
| `nthelem` | `(nthelem index list)` | Return a list element by one-based index. |
| `remd` | `(remd item list)` | Destructively remove equal-matching elements from a list. |
| `remdq` | `(remdq item list)` | Destructively remove eq-matching elements from a list. |
| `remove` | `(remove item list)` | Return a list with matching elements removed using structural comparison. |
| `remq` | `(remq item list)` | Return a list with matching elements removed using eq-style comparison. |
| `reverse` | `(reverse list)` | Return a new list with the item order reversed. |
| `rplaca` | `(rplaca list value)` | Replace the first element of a non-empty list. |
| `rplacd` | `(rplacd list tail)` | Replace the tail of a non-empty list. |
| `setof` | `(setof func list)` | Return the list of input elements whose predicate result is truthy. |
| `sort` | `(sort list predicate)` | Sort a list in place using a comparison predicate or nil for default ordering. |
| `sortcar` | `(sortcar list predicate)` | Sort a list of lists in place using each element's first item as the sort key. |
| `subst` | `(subst new old tree)` | Recursively replace matching values in a nested list tree. |
| `xcons` | `(xcons tail head)` | Build a list by consing the second argument onto the first list tail. |

## Loop
| Symbol | Signature | Summary |
| --- | --- | --- |
| `for` | `(for sym start end body...)` | Iterate from start to end, including the end value. |
| `foreach` | `(foreach sym list body...)` | Walk each item in a list and bind it to a loop symbol. |
| `while` | `(while test body...)` | Repeat a body while the test expression stays truthy. |

## Meta
| Symbol | Signature | Summary |
| --- | --- | --- |
| `gensym` | `(gensym [prefix])` | Generate a fresh unbound symbol name with an optional string or symbol prefix. |
| `getd` | `(getd 'symbol)` | Read the current callable bound to a quoted symbol. |
| `intern` | `(intern string)` | Convert a string into a symbol value. |
| `macroexpand` | `(macroexpand form)` | Expand one macro call without evaluating the resulting form. |
| `makunbound` | `(makunbound 'symbol)` | Remove a value binding from the current runtime environment. |
| `putd` | `(putd 'symbol callable)` | Store a callable under a quoted symbol name. |
| `symbolName` | `(symbolName 'symbol)` | Return the printable name of a symbol. |
| `symeval` | `(symeval 'symbol)` | Read the current value stored under a quoted symbol. |

## Output
| Symbol | Signature | Summary |
| --- | --- | --- |
| `print` | `(print value ...)` | Render values into the session output stream. |
| `printf` | `(printf format arg ...)` | Format text and send it to the session output buffer. |
| `println` | `(println value ...)` | Render values for console-style output. |

## Predicate
| Symbol | Signature | Summary |
| --- | --- | --- |
| `arrayp` | `(arrayp value)` | Test whether a value is an array. |
| `atom` | `(atom value)` | Test whether a value is not a list. |
| `boundp` | `(boundp 'symbol)` | Check whether a quoted symbol currently has a bound value. |
| `dtpr` | `(dtpr value)` | Test whether a value is a non-empty list pair. |
| `eq` | `(eq left right)` | Check whether two values compare as the same simple value. |
| `equal` | `(equal left right)` | Compare values structurally, including list contents. |
| `evenp` | `(evenp value)` | Test whether an integer is even. |
| `fixp` | `(fixp value)` | Test whether a value is an integer. |
| `floatp` | `(floatp value)` | Test whether a value is a floating-point number. |
| `integerp` | `(integerp value)` | Test whether a value is an integer. |
| `listp` | `(listp value)` | Test whether a value is a list or nil. |
| `minusp` | `(minusp value)` | Test whether a numeric value is less than zero. |
| `neq` | `(neq left right)` | Check whether two values are not eq-equal. |
| `nequal` | `(nequal left right)` | Check whether two values differ structurally. |
| `not` | `(not value)` | Invert SKILL truthiness, treating only nil as false. |
| `null` | `(null value)` | Test whether a value is nil. |
| `numberp` | `(numberp value)` | Test whether a value is numeric. |
| `oddp` | `(oddp value)` | Test whether an integer is odd. |
| `onep` | `(onep value)` | Test whether a numeric value is exactly one. |
| `pairp` | `(pairp value)` | Test whether a value is a non-empty list. |
| `plusp` | `(plusp value)` | Test whether a numeric value is greater than zero. |
| `portp` | `(portp value)` | Test whether a value is an open port. |
| `stringp` | `(stringp value)` | Test whether a value is a string. |
| `symbolp` | `(symbolp value)` | Test whether a value is a symbol. |
| `tablep` | `(tablep value)` | Test whether a value is a table. |
| `tailp` | `(tailp tail list)` | Test whether one list appears as a tail of another. |
| `type` | `(type value)` | Return a simple symbolic description of a runtime value. |
| `typep` | `(typep value type-symbol)` | Test whether a value reports the given type symbol. |
| `zerop` | `(zerop value)` | Test whether a numeric value is zero. |

## Property
| Symbol | Signature | Summary |
| --- | --- | --- |
| `defprop` | `(defprop 'symbol value key)` | Define a property value on a symbol. |
| `get` | `(get target key)` | Read a property from a symbol plist or a value from a table. |
| `getq` | `(getq target key)` | Read a property using the same runtime behavior as get. |
| `getqq` | `(getqq target key)` | Read a property using the same runtime behavior as get. |
| `plist` | `(plist 'symbol)` | Return the current property list for a symbol. |
| `putprop` | `(putprop 'symbol value key)` | Store one property value on a symbol. |
| `putpropq` | `(putpropq 'symbol value key)` | Store one property value on a symbol. |
| `putpropqq` | `(putpropqq 'symbol value key)` | Store one property value on a symbol. |
| `remprop` | `(remprop 'symbol key)` | Remove one property from a symbol plist. |
| `setplist` | `(setplist 'symbol plist)` | Replace the entire property list for a symbol. |

## Reader
| Symbol | Signature | Summary |
| --- | --- | --- |
| `quasiquote` | `(quasiquote form) or `form` | Build literal-looking data while allowing selected parts to evaluate. |
| `quote` | `(quote form) or 'form` | Return literal data instead of evaluating it as code. |

## Regex
| Symbol | Signature | Summary |
| --- | --- | --- |
| `rexCompile` | `(rexCompile pattern)` | Compile a regular-expression pattern for reuse. |
| `rexExecute` | `(rexExecute regex string)` | Check whether a compiled regex or pattern matches a string. |
| `rexMatchp` | `(rexMatchp regex string)` | Check whether a regex or pattern matches a string. |
| `rexReplace` | `(rexReplace regex replacement string)` | Replace regex matches in a string. |
| `rexSubstitute` | `(rexSubstitute regex replacement string)` | Replace regex matches in a string. |

## Sequencing
| Symbol | Signature | Summary |
| --- | --- | --- |
| `prog` | `(prog ((sym value) ...) body...)` | Create local variables for a block that can exit early with return. |
| `prog1` | `(prog1 form1 form2 ...)` | Evaluate all forms and keep the first result. |
| `prog2` | `(prog2 form1 form2 form3 ...)` | Evaluate all forms and keep the second result. |
| `progn` | `(progn form1 form2 ...)` | Group expressions and return the final result. |

## String
| Symbol | Signature | Summary |
| --- | --- | --- |
| `alphalessp` | `(alphalessp left right)` | Test whether one string sorts before another lexicographically. |
| `atof` | `(atof string)` | Convert a numeric string to a floating-point value. |
| `atoi` | `(atoi string)` | Convert a numeric string to an integer. |
| `buildString` | `(buildString piece ...)` | Assemble a string from several values. |
| `concat` | `(concat piece ...)` | Create a symbol by concatenating several pieces into one print name. |
| `getchar` | `(getchar string index)` | Return one character from a string using one-based indexing. |
| `index` | `(index needle string)` | Return the one-based position of the first matching substring. |
| `lowerCase` | `(lowerCase string)` | Convert a string to lowercase. |
| `nindex` | `(nindex needle string start)` | Return the one-based position of the first match at or after a one-based starting index. |
| `parseString` | `(parseString string [delimiters])` | Split a string into tokens using whitespace or an explicit delimiter set. |
| `rindex` | `(rindex needle string)` | Return the one-based position of the last matching substring. |
| `sprintf` | `(sprintf dest-or-nil format arg ...)` | Format text, optionally store it in a destination variable, and return the resulting string. |
| `strcat` | `(strcat piece ...)` | Concatenate multiple values into one string. |
| `strcmp` | `(strcmp left right)` | Compare two strings lexicographically. |
| `strlen` | `(strlen string)` | Return the length of a string. |
| `substr` | `(substr string start [length])` | Return a slice of a string using the current interpreter's zero-based offsets. |
| `substring` | `(substring string start [length])` | Return a slice of a string using one-based starting positions. |
| `upperCase` | `(upperCase string)` | Convert a string to uppercase. |

## Table
| Symbol | Signature | Summary |
| --- | --- | --- |
| `makeTable` | `(makeTable name [default])` | Allocate a table with an optional default value for missing keys. |
| `put` | `(put table key value)` | Store a value under a table key. |

