# Gulf of Mexico — Installation Guide

Install the interpreter, verify it runs, and get to your first program quickly.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Detailed Installation](#detailed-installation)
3. [Optional Dependencies](#optional-dependencies)
4. [IDE Setup](#ide-setup)
5. [Troubleshooting](#troubleshooting)
6. [Uninstallation](#uninstallation)

## Quick Start

Quick path to a working setup:

```bash
git clone https://github.com/James-HoneyBadger/GulfOfMexico.git
cd GulfOfMexico
pip install -e .
python -m gulfofmexico programs/examples/01_hello_world.gom
```

If that worked, congratulations! You're done. If not, keep reading.

## Detailed Installation

### Requirements

- Python 3.10 or higher
- pip
- Git

Check your Python version:

```bash
python --version
# or
python3 --version
```

If you see `Python 3.10.x` or higher, you're good to proceed.

### Step 1: Clone the Repository

```bash
git clone https://github.com/James-HoneyBadger/GulfOfMexico.git
cd GulfOfMexico
```

This downloads the repository to your local machine.

### Step 2: Install the Package

We recommend installing in editable mode so changes update immediately:

```bash
pip install -e .
```

Or, if you're using `pip3`:

```bash
pip3 install -e .
```

This installs Gulf of Mexico and its required dependencies.

### Step 3: Verify Installation

Try running the interpreter:

```bash
python -m gulfofmexico --version
```

Or jump straight into the REPL:

```bash
python -m gulfofmexico
```

You should see a prompt. Try: `print("It works!")!` and press Enter.

## Optional Dependencies

Gulf of Mexico has optional features that require extra packages.

### Input Handling (pynput)

For fancy keyboard input in programs:

```bash
pip install pynput
```

Included if you installed extras via Poetry or requirements; otherwise install manually.

### GitHub Globals (pygithub)

For GitHub integration features:

```bash
pip install pygithub
```

Included if installed with the appropriate extras.

### Qt IDE (PySide6 or PyQt5)

For the graphical IDE with actual windows and buttons:

```bash
pip install PySide6
```

Or if you prefer PyQt5:

```bash
pip install PyQt5
```

Note: If Qt isn't available on your system, the IDE can fall back to a web-based interface.

## IDE Setup

### Launching the IDE

The Gulf of Mexico IDE comes in two delicious flavors:

**Auto-detect mode** (tries Qt, falls back to web):

```bash
python -m gulfofmexico.ide
```

**Force web mode** (when you know Qt won't work):

```bash
python -m gulfofmexico.ide --web
```

The web IDE runs at `http://localhost:8080/ide` and opens automatically in your browser.

### IDE Features

- Syntax highlighting (sort of)
- Run button (definitely)
- Output panel (absolutely)
- File management (maybe)

## Platform-Specific Notes

### Linux

Should work out of the box.

If you get permission errors:

```bash
pip install --user -e .
```

### macOS

Similar to Linux; if using Homebrew Python, ensure the correct version is installed.

If you're using Homebrew Python:

```bash
brew install python@3.10
pip3 install -e .
```

### Windows

Make sure Python is in your PATH:

```bash
python --version
```

If that doesn't work, try:

```bash
py --version
```

Then install using:

```bash
py -m pip install -e .
```

Run Gulf of Mexico with:

```bash
py -m gulfofmexico
```

### Virtual Environments (Recommended)

Recommended for isolation:

```bash
python -m venv gom-env
source gom-env/bin/activate  # On Windows: gom-env\Scripts\activate
pip install -e .
```

Now Gulf of Mexico lives in its own little world, separate from your other Python chaos.

## Running Programs

### Single File

```bash
python -m gulfofmexico myprogram.gom
```

### Inline Code

```bash
python -m gulfofmexico -c "print(42)!"
```

### Interactive REPL

```bash
python -m gulfofmexico
```

Type away! Exit with `Ctrl+D` (Linux/Mac) or `Ctrl+Z` then Enter (Windows).

### Example Programs

Explore the organized examples:

```bash
# Hello World
python -m gulfofmexico programs/examples/01_hello_world.gom

# Feature showcase
python -m gulfofmexico programs/demos/feature_showcase.gom

# Ultimate demo (all features)
python -m gulfofmexico programs/demos/grand_deluxe_demo.gom

# Calculator
python -m gulfofmexico programs/demos/calculator.gom

# Graphics
python -m gulfofmexico programs/03_graphics/19_mandelbrot.gom
```

Browse the `programs/` directory for more. See [programs/README.md](../../programs/README.md) for the complete catalog.

## Troubleshooting

### "Command not found: python"

Try `python3` instead:

```bash
python3 -m gulfofmexico
```

### "No module named 'gulfofmexico'"

You probably forgot to install it:

```bash
cd /path/to/GOM
pip install -e .
```

### Qt IDE Crashes

This happens. Use the web IDE:

```bash
python -m gulfofmexico.ide --web
```

It should automatically fall back when Qt is unavailable.

### "SyntaxError" When Running Programs

Check your `.gom` file:

- Every statement needs an `!` at the end
- Use 3-space indentation (it's quirky, we know)
- Make sure strings are properly quoted

### Programs Don't Output Anything

Are you using `print()`? Did you remember the `!`?

```gom
print("Hello")!  // ✓ Works
print("Hello")   // ✗ Silent failure
```

### Import Errors

If you see errors about missing Python packages:

```bash
pip install requests pynput pygithub
```

## Updating

Pull the latest changes and reinstall:

```bash
cd GOM
git pull
pip install -e .
```

## Uninstallation

We're sad to see you go, but we understand:

```bash
pip uninstall gulfofmexico
```

Then delete the directory:

```bash
cd ..
rm -rf GOM
```

Or keep it around for later.

## Getting Help

- **User Guide**: [USER_GUIDE.md](./USER_GUIDE.md)
- **Technical Reference**: [TECHNICAL_REFERENCE.md](../reference/TECHNICAL_REFERENCE.md)
- **Programming Guide**: [PROGRAMMING_GUIDE.md](./PROGRAMMING_GUIDE.md)
- **Example Programs**: [programs/README.md](../../programs/README.md) - Complete catalog
- **Validation Report**: [VALIDATION_REPORT.md](../reference/VALIDATION_REPORT.md) - Test results and status
- **GitHub Issues**: [Report problems](https://github.com/James-HoneyBadger/GulfOfMexico/issues)

## Success!

You should now have a working Gulf of Mexico installation. Fire up a program and get started.

```bash
python -m gulfofmexico programs/01_basics/01_hello_world.gom
```

Welcome to the Gulf! 🌊
