# OpenSKILL

OpenSKILL is a standalone SKILL interpreter, REPL, desktop shell, and offline API finder for learning and running a Cadence-free subset of SKILL on your own machine.

## Start here

- Manual: [`docs/user-manual.md`](docs/user-manual.md)
- Command reference: [`docs/command-reference.md`](docs/command-reference.md)
- Runnable starter files: [`examples/`](examples/)

## Quick start

### Run a release binary

Download the latest CLI or IDE build from GitHub Releases:

<https://github.com/sohamxda7/openskill/releases>

Examples:

- Linux CLI: `./openskill-<version>-linux`
- Windows CLI: `openskill-<version>-windows.exe`
- Linux IDE: `./openskill-ide-<version>-linux`
- Windows IDE: `openskill-ide-<version>-windows.exe`

### Run from source

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

## What OpenSKILL covers today

OpenSKILL focuses on a standalone-safe SKILL subset for language learning, scripting, and offline experimentation. It includes:

- script execution, one-shot expressions, and a REPL
- a Tk-based desktop shell with editor, console, REPL, and API finder
- an offline catalog of the currently documented commands and forms
- core language features such as bindings, procedures, macros, conditionals, loops, lists, strings, tables, arrays, printing, and file/port utilities

It does **not** provide Virtuoso, OpenAccess, CDB, database automation, or live Cadence session integration.

## Development

```bash
python3 -m unittest discover -s tests
```
