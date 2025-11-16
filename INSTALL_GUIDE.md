# Gulf of Mexico Installation Guide

Getting the *perfect* programming language onto your imperfect computer.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Detailed Installation](#detailed-installation)
3. [Optional Dependencies](#optional-dependencies)
4. [IDE Setup](#ide-setup)
5. [Troubleshooting](#troubleshooting)
6. [Uninstallation](#uninstallation)

## Quick Start

For the impatient among us (we get it):

```bash
git clone https://github.com/James-HoneyBadger/GOM.git
cd GOM
pip install -e .
python -m gulfofmexico programs/examples/01_hello_world.gom
```

If that worked, congratulations! You're done. If not, keep reading.

## Detailed Installation

### Requirements

- **Python 3.10 or higher** - Because we live in the future
- **pip** - For installing things
- **Git** - For cloning things

Check your Python version:

```bash
python --version
# or
python3 --version
```

If you see something like `Python 3.10.x` or higher, you're golden.

### Step 1: Clone the Repository

```bash
git clone https://github.com/James-HoneyBadger/GOM.git
cd GOM
```

This downloads the entire Gulf of Mexico experience to your local machine. Exciting!

### Step 2: Install the Package

We recommend installing in **editable mode** so you can tinker with the internals (you know you want to):

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

You should see a prompt. Type `print("It works!")!` and press Enter.

## Optional Dependencies

Gulf of Mexico has some optional features that require extra packages. They're like DLC, but free.

### Input Handling (pynput)

For fancy keyboard input in programs:

```bash
pip install pynput
```

Already included if you did `pip install -e .` (we gotchu).

### GitHub Globals (pygithub)

For mysterious GitHub integration features:

```bash
pip install pygithub
```

Also already included. We're thorough like that.

### Qt IDE (PySide6 or PyQt5)

For the graphical IDE with actual windows and buttons:

```bash
pip install PySide6
```

Or if you prefer PyQt5:

```bash
pip install PyQt5
```

**Note:** The Qt IDE doesn't work on all systems (looking at you, CPU instruction limitations). If it fails, the IDE automatically falls back to a web-based interface. Crisis averted!

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

Should work out of the box. You're probably fine.

If you get permission errors:

```bash
pip install --user -e .
```

### macOS

Same as Linux, but more expensive.

If you're using Homebrew Python:

```bash
brew install python@3.10
pip3 install -e .
```

### Windows

Python on Windows can be... *special*.

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

If you're fancy and like isolation:

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

We've included a bunch:

```bash
# Hello World
python -m gulfofmexico programs/examples/01_hello_world.gom

# Feature showcase
python -m gulfofmexico programs/demos/feature_showcase.gom

# Calculator
python -m gulfofmexico programs/demos/calculator.gom
```

Browse the `programs/` directory for more.

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

Or it should automatically fall back. If it doesn't, well, you tried.

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

Or keep it around. You might come back. They always come back.

## Getting Help

- **User Guide**: [USER_GUIDE.md](USER_GUIDE.md)
- **Technical Reference**: [TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md)
- **Programming Guide**: [PROGRAMMING_GUIDE.md](PROGRAMMING_GUIDE.md)
- **Example Programs**: `programs/` directory
- **GitHub Issues**: [Report problems](https://github.com/James-HoneyBadger/GOM/issues)

## Success!

If you've made it this far, you should have a working Gulf of Mexico installation. Fire up a program and experience the *perfection*.

```bash
python -m gulfofmexico programs/examples/01_hello_world.gom
```

Welcome to the Gulf! 🌊
