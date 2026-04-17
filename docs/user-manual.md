# OpenSKILL User Manual

This is the main user guide for OpenSKILL. Use it for the big picture, setup, day-to-day command usage, language basics, and beginner examples. For the full symbol catalog, see [`docs/command-reference.md`](command-reference.md).

## 1. What OpenSKILL is

OpenSKILL is a standalone workbench for writing and running a practical subset of SKILL without needing a live Cadence installation. In the current repository it provides four main pieces:

- a file runner for `.il` scripts
- a command-line REPL
- a desktop shell with editor, console, REPL, and API search
- an offline API catalog backed by `src/openskill/api/catalog.json`

It is useful for learning SKILL syntax, prototyping standalone scripts, and looking up supported commands locally.

## 2. What OpenSKILL is not

OpenSKILL is not a full replacement for Cadence tools. This repository does **not** currently provide:

- Virtuoso or layout/database APIs
- OpenAccess or CDB integration
- Cadence UI automation
- online help lookup or cloud services

Document only what is present today: the standalone interpreter, REPL, desktop shell, and offline API catalog.

## 3. Installing and starting it

### Release binaries

If you want the shortest path, download a release from:

<https://github.com/sohamxda7/openskill/releases>

Common binaries:

- CLI: `openskill-<version>-linux` or `openskill-<version>-windows.exe`
- IDE: `openskill-ide-<version>-linux` or `openskill-ide-<version>-windows.exe`

### From source

Install the package in editable mode:

```bash
python3 -m pip install -e .
```

Then start the CLI:

```bash
openskill
```

If you are running straight from the repository checkout and do not want to install it first, use:

```bash
PYTHONPATH=src python3 -m openskill.cli
```

### First successful run

Open the REPL:

```bash
openskill
```

Evaluate one expression:

```bash
openskill --expr '(+ 1 2 3)'
```

Run a script file:

```bash
openskill examples/hello.il
```

Check the local environment:

```bash
openskill doctor
```

## 4. Ways to use OpenSKILL

### Script runner

Run a file and print any generated output and final return value:

```bash
openskill path/to/script.il
```

### One-shot expression mode

Use `--expr` for quick checks:

```bash
openskill --expr '(let ((x 2) (y 5)) (+ x y))'
```

### REPL

Start with either of these:

```bash
openskill
openskill repl
```

Useful REPL commands:

- `:help` - show built-in help
- `:quit` - leave the REPL
- `:api QUERY` - search the offline catalog from inside the REPL
- `:reset` - create a fresh session and clear current REPL state

The REPL keeps reading until parentheses balance, so you can enter multi-line expressions naturally.

### CLI API finder

Search the offline command catalog from the shell:

```bash
openskill api find procedure
openskill api find file
```

### Desktop shell / GUI

After installation:

```bash
openskill --gui
```

From a source checkout:

```bash
PYTHONPATH=src python3 -m openskill.ui.app
```

The desktop shell includes:

- an editor tab with a Run button
- a console pane for output and errors
- a REPL tab for line-by-line evaluation
- an API Finder panel for local command lookup

## 5. Runnable starter examples

The repository now includes real starter scripts in [`examples/`](../examples/):

- [`examples/arithmetic.il`](../examples/arithmetic.il) - infix arithmetic with `+ - * /` and list output
- [`examples/procedure.il`](../examples/procedure.il) - `defun`, `procedure`, and computed return data
- [`examples/hello.il`](../examples/hello.il) - simplest greeting and `procedure`
- [`examples/control-flow.il`](../examples/control-flow.il) - `setq`, `for`, and `cond`
- [`examples/lists.il`](../examples/lists.il) - quoting, list operations, and printing
- [`examples/ports.il`](../examples/ports.il) - string ports, formatted output, and input reading

Run any of them with:

```bash
openskill examples/arithmetic.il
```

If you are using the repository checkout directly:

```bash
PYTHONPATH=src python3 -m openskill.cli examples/arithmetic.il
```

## 6. Language model: how SKILL code is read here

OpenSKILL reads code as expressions. Most code is written as parenthesized prefix forms:

```skill
(+ 1 2 3)
(setq width 10)
(if (> width 5) "wide" "narrow")
```

Arithmetic can also be written with infix `+ - * /`:

```skill
width * height
sum + 1
total / 4
```

That infix support is intentionally narrow: use it for arithmetic only. Other operator-style compatibility remains limited to the already-supported subset such as `=`, `==`, `!=`, `&&`, and prefix `!`.

Classic SKILL immediate-paren calls are also accepted when the `(` touches the symbol with no whitespace:

```skill
println("hello world")
plus(1 2)
let(((x 1) (y 2)) plus(x y))
```

A file may contain many top-level forms. They are evaluated in order.

### Comments

A semicolon starts a comment that continues to the end of the line:

```skill
; this is a comment
(setq x 10) ; so is this
```

### Basic data types you will use first

- numbers: `1`, `-3`, `4.5`
- strings: `"hello"`
- symbols: `width`, `sum`, `myProc`
- lists: `'(a b c)` or `(list 1 2 3)`

### Truth values

OpenSKILL follows the classic Lisp-style rule used by SKILL:

- `nil` means false
- `t` means true
- `nil` is also the empty list
- `0` is still truthy

So this returns `1`, not `2`:

```skill
(if 0 1 2)
```

## 7. Syntax primer

### Quote

Use quote when you want literal data instead of evaluation:

```skill
'a
'(1 2 3)
```

Without quote, a symbol is treated as a variable or function name.

### Quasiquote, unquote, and splice

Use backquote to build list-shaped data while evaluating selected parts:

```skill
`(a ,(+ 1 2) ,@(list 4 5))
```

That produces:

```skill
(a 3 4 5)
```

### Strings and escapes

Strings use double quotes. Common escapes such as `\n`, `\r`, `\t`, `\"`, and `\\` are supported.

### Bindings and definitions

Use `let` for temporary local bindings:

```skill
(let ((x 2) (y 5))
  (+ x y))
```

Use `setq` for assignment in the active session:

```skill
(setq total 0)
```

Define callable code with `procedure`, `defun`, or `lambda`:

```skill
(procedure (greet who)
  (println (strcat "Hello, " who)))
```

### Question-mark names and parameter keywords

Names like `?x` are accepted as normal symbols, so code such as this works today:

```skill
(progn
  (setq ?x 5)
  (+ ?x 1))
```

At the moment, OpenSKILL does **not** document a separate keyword-argument calling convention beyond ordinary symbol names and positional arguments. If you use `?name`-style identifiers, treat them as normal symbols in the current implementation.

## 8. Core programming patterns

### Conditionals

```skill
(if test then else)
(when test body1 body2)
(unless test body1 body2)
(cond
  (test1 body1)
  (test2 body2)
  (t fallback))
```

### Loops

```skill
(for i 1 3
  (println i))

(foreach item '(a b c)
  (println item))

(while (< count 3)
  (setq count (+ count 1)))
```

### Lists

```skill
(list 1 2 3)
(reverse '(1 2 3))
(append1 '(1 2) 3)
(nth 1 '(10 20 30))
```

### Strings and formatting

```skill
(sprintf "v=%d" 7)
(strcat "pin_" 'A)
(strlen "hello")
```

### Loading code from another file

```skill
(load "other-file.il")
```

Use this when you split larger programs across files.

## 9. A tiny macro guide

OpenSKILL includes `defmacro`, `quote`, `quasiquote`, `unquote`, and `splice`, so you can build simple source-to-source helpers.

Example:

```skill
(defmacro unlessNil (value form)
  `(when ,value ,form))

(unlessNil "ok"
  (println "ran"))
```

Practical advice:

- start with functions first
- add a macro only when you want new surface syntax
- use backquote and comma rather than manual list assembly when possible
- use `macroexpand` if you want to inspect a macro result

## 10. Practical command-discovery workflow

There are three built-in ways to discover what is supported.

### 1. Search from the CLI

```bash
openskill api find foreach
```

### 2. Search from the REPL

```text
:api foreach
```

### 3. Browse the generated reference page

See [`docs/command-reference.md`](command-reference.md), which is organized from the repository's command catalog.

If you want the raw source of truth used by the finder, inspect `src/openskill/api/catalog.json`.

## 11. Desktop shell quick walkthrough

When you open the GUI:

1. Type or open a `.il` file in the editor tab.
2. Click **Run** to evaluate the full editor buffer.
3. Use the lower console pane to read results or errors.
4. Switch to the **REPL** tab for quick single-line experiments.
5. Use **API Finder** on the right to search symbols, signatures, summaries, return shapes, and examples.

The GUI is best for learning and experimentation. The CLI is usually faster for automation and script runs.

## 12. Common beginner workflow

1. Start with `examples/arithmetic.il`.
2. Move to `examples/procedure.il`, then `examples/control-flow.il` and `examples/lists.il`.
3. Use `openskill --expr '...'` for quick one-liners.
4. Keep a REPL open and use `:api name` when you forget a command.
5. Move repeated code into procedures or separate `.il` files loaded with `load`.

## 13. Current boundaries and expectations

OpenSKILL already covers a useful standalone subset, but the command surface is still partial compared with a full production SKILL environment. Before depending on a symbol, check one of these:

- `openskill api find <name>`
- `:api <name>` in the REPL
- [`docs/command-reference.md`](command-reference.md)

That keeps your scripts aligned with what this repository actually implements today.
