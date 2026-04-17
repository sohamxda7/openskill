# OpenSKILL - Standalone SKILL Interpreter, REPL, IDE, and Offline API Finder for EDA

OpenSKILL lets you write SKILL code, run it, and look up commands on your own computer without needing Cadence installed.

It is a **standalone SKILL interpreter, REPL, desktop shell, and offline API finder** for EDA engineers, custom IC teams, students, and learners who want a practical Cadence-free SKILL workbench on Linux or Windows.

If you are searching for a **SKILL interpreter**, **SKILL REPL**, **offline SKILL reference**, or a **Cadence-free SKILL learning environment**, this repository is built for that use case.

## Start here

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
3. Start typing SKILL code.

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

## What it supports

- Reader, parser, and evaluator for a growing standalone-safe core SKILL surface
- File execution, one-shot expressions, and a REPL
- Offline API catalog for the commands currently implemented
- Desktop shell with editor, console, REPL, and API Finder
- Core language areas including bindings, procedures, macros, conditionals, loops, lists, strings, tables, arrays, printing, and file/port utilities
- Prefix forms, classic immediate-paren calls such as `println("hello")`, and infix arithmetic with `+ - * /`

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

The shipped help text, signatures, and examples in this repository were written independently for this project. The reference PDFs were used to study language behavior and surface area, but the bundled catalog content is original to this repository.

## License

This project is distributed under **GPL-3.0-or-later**. See `LICENSE` for the full license text and `NOTICE` for project-specific legal notices and disclaimers.

## Legal notice

- This project is an independent educational implementation and is **not affiliated with, endorsed by, or sponsored by Cadence Design Systems, Inc.**
- Names such as **SKILL**, **Cadence**, and **Virtuoso** are used only to describe compatibility goals and remain the property of their respective owners.
- This repository follows a clean-room process for shipped documentation and examples, but it **does not claim immunity from copyright, trademark, contract, DMCA, or other legal challenges**.
- Contributors and users are responsible for ensuring that any source materials or scripts they contribute may be used lawfully.

## Development

```bash
python3 -m unittest discover -s tests
```
