# OpenSKILL

OpenSKILL is an independent SKILL learning workbench with a local interpreter, REPL, desktop shell, and offline API Finder. It is aimed at **core language learning and scripting**, not Cadence database or layout automation.

## License

This project is distributed under **GPL-3.0-or-later**. See `LICENSE` for the full license text and `NOTICE` for project-specific legal notices and disclaimers.

## What it supports

- Reader, parser, and evaluator for a partial core SKILL-style subset
- File execution with `load("script.il")`
- REPL and command-line runner
- Offline API catalog for the commands currently implemented
- Desktop shell with editor, console, REPL, and API Finder

## What it does not support

- Virtuoso, OpenAccess, CDB, and layout/database APIs
- Cadence UI automation and live-session integration
- Any network dependency for help lookup

OpenSKILL is **not** a full core-SKILL-complete environment yet.

## Documentation provenance

The shipped help text, signatures, and examples in this repository were written independently for this project. The reference PDFs were used to study language behavior and surface area, but the bundled catalog content is original to this repository.

## Legal notice

- This project is an independent educational implementation and is **not affiliated with, endorsed by, or sponsored by Cadence Design Systems, Inc.**
- Names such as **SKILL**, **Cadence**, and **Virtuoso** are used only to describe compatibility goals and remain the property of their respective owners.
- This repository follows a clean-room process for shipped documentation and examples, but it **does not claim immunity from copyright, trademark, contract, DMCA, or other legal challenges**.
- Contributors and users are responsible for ensuring that any source materials or scripts they contribute may be used lawfully.

## Repository layout

```text
src/openskill/
  interpreter/   Core reader, parser, evaluator, runtime
  api/           Offline API catalog and search helpers
  apifinder/     Offline API search helpers
  ide/           Tk-based desktop shell
  runtime/       REPL utilities
tests/           Unit coverage for interpreter/runtime behavior
scripts/         Packaging helpers
```

## Getting started

### 1. Create a virtual environment

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -U pip
```

### 2. Install the project

```bash
python -m pip install -e .
```

With packaging tools:

```bash
python -m pip install -e .[build]
```

### 3. Run it

Start the REPL:

```bash
openskill
```

Run a script:

```bash
openskill examples/hello.il
```

Try the desktop shell:

```bash
python -m openskill.ui.app
```

The desktop shell uses the Python standard library `tkinter`, so it works best on Python builds that include Tk support.

## CLI and GUI usage

```bash
openskill [path/to/script.il]
openskill --expr '(println "hello")'
openskill --gui
```

## Current support level

The current implementation focuses on:
- literals: numbers, strings, symbols, lists
- quoting: quote / quasiquote / unquote / splice
- flow control: `if`, `when`, `unless`, `case`, `while`, `for`, `foreach`
- scoping and definition: `let`, `setq`, `lambda`, `procedure`, `progn`
- core utilities: arithmetic, comparison, list operations, predicates, printing, `load`, `assoc`, `mapcar`, `boundp`
- runtime model: classic-style dynamic bindings, with `nil` treated as false and as the empty list

Current implementation is **partial** and does not yet cover the full core command surface described in the SKILL references.

## Packaging

Single-file packaging is intended to run on native Linux and Windows builders.

```bash
python -m pip install -e .[build]
python -m PyInstaller --noconfirm --clean --onefile --windowed \
  --name openskill \
  --paths src \
  --add-data "src/openskill/api/catalog.json:openskill/api" \
  src/openskill/ui/app.py
```

Tagged releases are built automatically in GitHub Actions and published as GitHub Release assets for Linux and Windows.

## Development

Run tests:

```bash
python -m unittest discover -s tests
```
