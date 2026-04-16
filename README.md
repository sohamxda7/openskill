# OpenSKILL - Standalone SKILL Interpreter, REPL, IDE, and Offline API Finder for EDA

OpenSKILL lets you write SKILL code, run it, and look up commands on your own computer without needing Cadence installed.

It is a **standalone SKILL interpreter, REPL, desktop IDE, and offline API Finder** for EDA engineers, custom IC teams, students, and learners who want a simple Cadence-free SKILL workbench on Linux or Windows.

If you are searching for a **SKILL interpreter**, **SKILL REPL**, **offline SKILL reference**, or a **Cadence-free SKILL learning environment**, this repository is built for that use case.

## Quick start

### Fastest way

1. Download the latest build from **GitHub Releases**: <https://github.com/sohamxda7/openskill/releases>
2. Run the binary for your platform:
   - **Linux CLI:** `./openskill-<version>-linux`
   - **Windows CLI:** `openskill-<version>-windows.exe`
   - **Linux IDE:** `./openskill-ide-<version>-linux`
   - **Windows IDE:** `openskill-ide-<version>-windows.exe`
3. Start typing SKILL code.

### From source

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
openskill
```

Run a script:

```bash
openskill examples/hello.il
```

## Why EDA users care

- Run core SKILL scripts locally without a Cadence license checkout
- Learn SKILL syntax, control flow, list processing, macros, and file I/O in one place
- Search an offline API catalog while you code
- Download single-file CLI and IDE binaries from GitHub Releases
- Use it as a teaching, experimentation, and scripting workbench for custom IC and EDA workflows

## Releases

Prebuilt binaries are published on **GitHub Releases** for **Linux** and **Windows**:

- **CLI:** `openskill-<version>-linux` / `openskill-<version>-windows.exe`
- **Desktop IDE:** `openskill-ide-<version>-linux` / `openskill-ide-<version>-windows.exe`
- **Integrity file:** `SHA256SUMS.txt`

Download the latest release here:

<https://github.com/sohamxda7/openskill/releases>

Each push to `main` creates a new prerelease snapshot with commit-based versioning, and version tags create stable releases.

## License

This project is distributed under **GPL-3.0-or-later**. See `LICENSE` for the full license text and `NOTICE` for project-specific legal notices and disclaimers.

## What it supports

- Reader, parser, and evaluator for a growing standalone-safe core SKILL surface
- File execution with `load("script.il")`
- REPL and command-line runner
- Offline API catalog for the commands currently implemented
- Desktop shell with editor, console, REPL, and API Finder

## What it does not support

- Virtuoso, OpenAccess, CDB, and layout/database APIs
- Cadence UI automation and live-session integration
- Any network dependency for help lookup

OpenSKILL is **not** a full core-SKILL-complete environment yet, but it already covers a broad standalone-safe subset with **200+ documented commands/forms** in the offline catalog.

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

Need the build tools too?

```bash
python -m pip install -e .[build]
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
- flow control: `if`, `when`, `unless`, `case`, `caseq`, `cond`, `catch`, `throw`, `while`, `for`, `foreach`, `prog`
- scoping and definition: `let`, `setq`, `lambda`, `procedure`, `defun`, `defmacro`, `progn`
- core utilities: arithmetic, comparison, list operations, predicates, property lists, macros, string search helpers, regex helpers, printing, file/port I/O, arrays, tables, `load`, mapping helpers, and symbol/meta helpers
- runtime model: classic-style dynamic bindings, with `nil` treated as false and as the empty list

Current implementation is still **partial** relative to the full reference surface, but it is already useful for SKILL language learning, offline experimentation, and standalone scripting.

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
