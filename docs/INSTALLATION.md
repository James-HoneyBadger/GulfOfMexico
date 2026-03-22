# Gulf of Mexico — Installation Guide

Step-by-step instructions for installing and running the Gulf of Mexico interpreter on all supported platforms.

---

## Table of Contents

1. [Requirements](#requirements)
2. [Quick Install (PyPI)](#quick-install-pypi)
3. [Install from Source](#install-from-source)
4. [Optional Extras](#optional-extras)
5. [IDE Setup](#ide-setup)
6. [Platform-Specific Notes](#platform-specific-notes)
7. [Virtual Environments](#virtual-environments)
8. [Verifying the Installation](#verifying-the-installation)
9. [Uninstalling](#uninstalling)
10. [Troubleshooting](#troubleshooting)

---

## Requirements

- **Python 3.10 or later** (tested on 3.10, 3.11, 3.12, 3.13, 3.14)
- **pip** (included with Python)
- **Git** (only needed for source installation)

Check your Python version:

```bash
python --version     # or python3 --version
```

---

## Quick Install (PyPI)

The simplest way to install Gulf of Mexico:

```bash
pip install gulfofmexico
```

This installs the core interpreter and registers the `gom` and `gulfofmexico` command-line tools.

After installation:

```bash
gom                           # Start the REPL
gom examples/01_hello_world.gom   # Run a program (if you have the examples)
```

---

## Install from Source

### 1. Clone the repository

```bash
git clone https://github.com/James-HoneyBadger/GulfOfMexico.git
cd GulfOfMexico
```

### 2. (Recommended) Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows (cmd)
# .venv\Scripts\Activate.ps1     # Windows (PowerShell)
```

### 3. Install in editable mode

```bash
pip install -e .
```

This installs the package in development/editable mode — changes to the source code take effect immediately without reinstalling.

### 4. Verify

```bash
gom examples/01_hello_world.gom
```

Expected output:

```
Hello, World!
Welcome to the Gulf of Mexico programming language.

I am fairly sure this prints.
I am VERY sure this prints.
I am ABSOLUTELY sure this prints.
```

---

## Optional Extras

Gulf of Mexico has several optional dependencies that enable additional features:

```bash
# Install a specific extra
pip install gulfofmexico[ide]

# Install from source with extras
pip install -e ".[ide]"

# Install all extras at once
pip install -e ".[all]"
```

| Extra | Package | Feature |
|-------|---------|---------|
| `ide` | PySide6 (≥6.6) | Graphical IDE with 7 themes, movable panels, settings dialog, and syntax highlighting |
| `input` | pynput (≥1.7.7) | Keyboard input support |
| `graphics` | Pillow (≥11.0) | Image processing |
| `yaml` | PyYAML (≥6.0) | YAML configuration files |
| `globals` | PyGithub (≥2.5) | GitHub-based public variable sharing |

---

## IDE Setup

The Gulf of Mexico IDE is a graphical editor built on PySide6 (Qt 6). To install and run:

```bash
# Install with IDE support
pip install gulfofmexico[ide]

# Launch the IDE
gom-ide

# — or —
python -m gulfofmexico.ide
```

### IDE Features

- **7 built-in themes**: One Dark, Dracula, Nord, Solarized Dark, GitHub Light, Monokai, Catppuccin Mocha
- **Settings dialog** (Ctrl+,) for theme, font size, word wrap, line numbers, and execution options
- **Toolbar** with Run, Stop, New, Open, Save, and panel-toggle buttons; movable to any window edge
- **Closable / floatable panels**: Console and Variables docks can be closed, floated, dragged, nested, and rearranged — layout is saved and restored automatically
- **Panel toggle buttons**: ⬇ Console and ⊞ Variables checkable buttons in the toolbar; View menu items stay in sync
- **Bracket matching** with visual highlights in the editor
- Multi-tab code editor with block-based syntax highlighting
- **Word wrap** and **line-number gutter** toggles
- **Go to Line** (Ctrl+G) dialog
- **Duplicate Line** (Ctrl+D) and **Move Line Up/Down** (Alt+↑/↓)
- **Tab right-click menu**: Close, Close Others, Close All, Duplicate Tab, Copy File Path
- Console output panel with timestamps and optional clear-on-run
- Run (F5) / Stop (Shift+F5)
- File operations: New (Ctrl+N), Open (Ctrl+O), Save (Ctrl+S), Save As (Ctrl+Shift+S)
- Recent files tracking
- Session persistence (window size, position, open tabs, dock layout)

### PyQt5 Fallback

If PySide6 is not available, the IDE will automatically try PyQt5:

```bash
pip install PyQt5
gom-ide
```

---

## Platform-Specific Notes

### Linux

Most Linux distributions include Python 3.10+. Install via your package manager if needed:

```bash
# Debian / Ubuntu
sudo apt update && sudo apt install python3 python3-pip python3-venv

# Fedora
sudo dnf install python3 python3-pip

# Arch
sudo pacman -S python python-pip
```

For the IDE on Linux, you may also need Qt system libraries:

```bash
# Debian / Ubuntu
sudo apt install libgl1-mesa-glx libegl1

# Fedora
sudo dnf install mesa-libGL mesa-libEGL
```

### macOS

Python 3.10+ can be installed via [python.org](https://www.python.org/downloads/) or Homebrew:

```bash
brew install python@3.12
```

### Windows

Download Python from [python.org](https://www.python.org/downloads/). During installation, check **"Add Python to PATH"**.

Then open Command Prompt or PowerShell:

```powershell
pip install gulfofmexico
gom
```

For the IDE on Windows:

```powershell
pip install gulfofmexico[ide]
gom-ide
```

---

## Virtual Environments

Using a virtual environment is recommended to avoid conflicts with system packages.

### With `venv` (built-in)

```bash
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows

pip install -e ".[all]"
```

### With Poetry

The project uses [Poetry](https://python-poetry.org/) for dependency management:

```bash
# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python -

# Install dependencies
cd GulfOfMexico
poetry install

# Install with extras
poetry install --extras "ide"
poetry install --extras "all"

# Run within the Poetry environment
poetry run gom examples/01_hello_world.gom
poetry run gom-ide
```

### With Conda

```bash
conda create -n gom python=3.12
conda activate gom
pip install gulfofmexico
```

---

## Verifying the Installation

### Run the hello world example

```bash
gom examples/01_hello_world.gom
```

### Start the REPL

```bash
gom
```

Type `print "it works!"!` and press Enter. Type `:quit` to exit.

### Run the test suite

```bash
python -m pytest
```

All 170 tests should pass.

### Run the spec compliance test

```bash
gom tests/spec_compliance.gom
```

Should complete with `ALL TESTS COMPLETE` at the end.

### Run inline code

```bash
gom -c "print 42!"
```

Should print `42`.

---

## Uninstalling

```bash
pip uninstall gulfofmexico
```

To also remove persistent `const const const` variables stored on disk:

```bash
rm -rf ~/.gulfofmexico_runtime
```

---

## Troubleshooting

### `gom: command not found`

The console script wasn't added to your PATH. Try:

```bash
python -m gulfofmexico            # Alternative invocation
```

Or ensure your Python scripts directory is on PATH:

```bash
# Linux / macOS
export PATH="$HOME/.local/bin:$PATH"

# Check where pip installs scripts
python -m site --user-base
```

### `ModuleNotFoundError: No module named 'gulfofmexico'`

The package isn't installed in the current Python environment. Verify:

```bash
pip show gulfofmexico
```

If nothing is shown, install it:

```bash
pip install gulfofmexico
```

### `ImportError: PySide6 not found` (when running IDE)

Install the IDE extra:

```bash
pip install gulfofmexico[ide]
```

### Permission errors on Linux

Use `--user` to install without root:

```bash
pip install --user gulfofmexico
```

### Python version too old

Gulf of Mexico requires Python 3.10+. Check your version:

```bash
python --version
```

If you have multiple Python versions, try `python3.12` or `python3.13` explicitly.

---

*For more help, open an issue on [GitHub](https://github.com/James-HoneyBadger/GulfOfMexico/issues).*
