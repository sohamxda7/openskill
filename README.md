<!-- Author: Soham Sen <sensoham135@gmail.com> <sohamsen2000@outlook.com> -->

# OpenSKILL - Run, Learn, and Explore SKILL Without Cadence Installed

OpenSKILL lets you run SKILL locally, learn the language, and search an offline reference on your own computer without Cadence installed.

It gives EDA engineers, custom IC teams, chip design learners, and student-friendly lab environments a practical **Cadence-free** setup for **EDA scripting**: a standalone SKILL interpreter, REPL, desktop shell, and **SKILL IDE** for Linux or Windows. The interpreter logic and bundled reference content are original work created for this project.

If you are searching for a **SKILL interpreter**, **SKILL REPL**, **offline SKILL reference**, or a **Cadence-free** way to **learn SKILL** for **custom IC** and broader EDA workflows, this repository is built for that use case.

OpenSKILL runs local file I/O with your current user permissions, so treat SKILL files like normal local scripts and run only code you trust.

## New users start here

- **User manual:** [`docs/user-manual.md`](docs/user-manual.md)
- **Command reference:** [`docs/command-reference.md`](docs/command-reference.md)
- **Runnable starter files:** [`examples/`](examples/)

## Quick start

### Fastest way

1. Download the latest build from **GitHub Releases**: <https://github.com/sohamxda7/openskill/releases>
2. Run the binary for your platform:
   - **Linux CLI:** `./openskill-<version>-linux`
   - **Windows CLI:** `openskill-<version>-windows.exe`
   - **Linux IDE:** `./openskill-ide-<version>-linux`
   - **Windows IDE:** `openskill-ide-<version>-windows.exe`
3. Start typing SKILL code and exploring the offline reference.

### From source

```bash
python3 -m pip install -e .
openskill
```

From a checkout without installing:

```bash
PYTHONPATH=src python3 -m openskill.cli
```

Run a starter script:

```bash
openskill examples/hello.il
```

Launch the desktop shell from source:

```bash
openskill --gui
# or, from a checkout without installing
PYTHONPATH=src python3 -m openskill.ui.app
```

## Why EDA users care

- Run core SKILL scripts locally without a Cadence license checkout
- Learn SKILL syntax, control flow, lists, strings, tables, and file I/O in one place
- Search an offline SKILL reference while you code
- Try beginner-friendly runnable examples before moving to your own scripts
- Download single-file CLI and IDE binaries from GitHub Releases
- Use it as a teaching, experimentation, and scripting workbench for custom IC, chip design, and EDA workflows

## Releases

Prebuilt binaries are published on **GitHub Releases** for **Linux** and **Windows**:

- **CLI:** `openskill-<version>-linux` / `openskill-<version>-windows.exe`
- **Desktop IDE:** `openskill-ide-<version>-linux` / `openskill-ide-<version>-windows.exe`
- **Integrity file:** `SHA256SUMS.txt`

Download the latest release here:

<https://github.com/sohamxda7/openskill/releases>

Each push to `main` creates a new prerelease snapshot with commit-based versioning, and version tags create stable releases.

## What it supports

- Reader, parser, and evaluator for a growing standalone-safe core SKILL surface
- File execution, one-shot expressions, and a REPL
- Offline API catalog for the commands currently implemented
- Desktop shell with editor, console, REPL, API Finder, line numbers, bracket matching, rainbow brackets, and autocomplete
- Runnable examples for arithmetic, procedures, lists, strings, Fibonacci, and a simple state machine
- Core language areas including bindings, procedures, macros, conditionals, loops, lists, strings, tables, arrays, printing, file/port utilities, and a minimal SKILL++ object layer
- Prefix forms, classic immediate-paren calls such as `println("hello")`, infix arithmetic with `+ - * /`, table helpers such as `tableToList`, and object syntax such as `defclass`, `makeInstance`, and `obj->slot`
- Self-contained catalog examples that are exercised by the test suite against every documented symbol

OpenSKILL is **not** a full core-SKILL-complete environment yet, but it already covers a broad standalone-safe subset with **200+ documented commands/forms** in the offline catalog.

## What it does not support

- Virtuoso, OpenAccess, CDB, and layout/database APIs
- Cadence UI automation and live-session integration
- Any network dependency for help lookup

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

## CLI and GUI usage

```bash
openskill [path/to/script.il]
openskill --expr '(println "hello")'
openskill --gui
```

Use the manual for setup, workflow, language basics, and beginner examples, and use the command reference when you want the browsable catalog of currently documented symbols.

## Documentation provenance

The shipped help text, signatures, and examples in this repository were written independently for this project. Publicly available reference material was used to study externally visible behavior and language surface area, but the bundled catalog content is original to this repository.

## License

This project is distributed under **GPL-3.0-or-later**. See `LICENSE` for the full license text and `NOTICE` for project-specific legal notices and disclaimers.

## Legal notice

- This project is an independent educational implementation and is **not affiliated with, endorsed by, or sponsored by Cadence Design Systems, Inc.**
- This repository does **not** contain, bundle, or redistribute proprietary Cadence source code, binaries, documentation, or data files.
- Names such as **SKILL**, **Cadence**, and **Virtuoso** are used only to describe compatibility goals and remain the property of their respective owners; such use does **not** imply certification, approval, or endorsement.
- This repository uses independently written documentation and examples, but it **does not claim immunity from copyright, trademark, contract, DMCA, or other legal challenges**.
- Contributors and users are responsible for ensuring that any source materials or scripts they contribute may be used lawfully.

## Development

```bash
python3 -m unittest discover -s tests
```

That suite now checks the interpreter/runtime behavior, starter examples, and every catalog example entry.
