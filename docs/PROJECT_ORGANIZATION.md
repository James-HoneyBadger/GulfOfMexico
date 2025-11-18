# Gulf of Mexico - Project Organization Summary

**Last Updated:** November 17, 2025

## 📋 Project Overview

Gulf of Mexico is a feature-rich, customizable programming language with:
- **Python interpreter** (production-ready, full features)
- **C++ compiler** (experimental, research project)
- **Language Construction Set** (create custom language variants)
- **50+ example programs**
- **Comprehensive documentation**

## 📁 File Structure

### Root Directory

```
GulfOfMexico/
├── README.md                          # Main project overview (comprehensive)
├── DOCUMENTATION.md                   # Complete documentation index
├── CODE_OF_CONDUCT.md                # Community guidelines
├── LICENSE                           # MIT License
├── pyproject.toml                    # Python package configuration
├── .gitignore                        # Git ignore patterns
│
├── gomconfig.py                      # CLI tool for language configuration
├── demo_create_new_languages.py     # Advanced language creation demos
├── demo_language_construction_set.py # Basic customization demos
│
└── README_OLD.md                     # Previous README (archived)
```

### Core Implementation (`gulfofmexico/`)

```
gulfofmexico/                         # Python interpreter package
├── __init__.py                       # Package initialization
├── __main__.py                       # Entry point (python -m gulfofmexico)
│
├── language_config.py                # Language Construction Set core
├── language_runtime.py               # Runtime integration
│
├── interpreter.py                    # Main interpreter
├── builtin.py                        # Built-in functions and keywords
├── context.py                        # Execution context
├── handlers.py                       # Statement/expression handlers
│
├── processor/                        # Lexer and parser
│   ├── lexer.py                     # Tokenization
│   ├── syntax_tree.py               # AST nodes
│   └── expression_tree.py           # Expression parsing
│
├── engine/                           # Core engine
│   ├── core.py                      # Execution engine
│   ├── evaluator.py                 # Expression evaluator
│   ├── namespace.py                 # Variable scoping
│   └── handlers/                    # Handler modules
│
├── ide/                              # Graphical IDE
│   ├── app.py                       # Main IDE application
│   ├── editor.py                    # Code editor
│   ├── highlighter.py               # Syntax highlighting
│   └── web_ide.py                   # Web-based IDE
│
├── plugins/                          # Plugin system
│   ├── example_math_utils.py        # Math utilities plugin
│   └── example_custom_statement.py  # Custom statement plugin
│
├── async_scheduler.py                # Async/await implementation
├── serialize.py                      # Serialization utilities
├── repl.py                           # REPL implementation
├── plugin_system.py                  # Plugin loader
├── utils.py                          # Utility functions
└── constants.py                      # Constants
```

### C++ Compiler (`compiler/`) - ⚠️ Experimental

```
compiler/
├── README.md                         # Compiler overview
├── EXPERIMENTAL_STATUS.md            # ⚠️ Important: limitations and scope
├── CMakeLists.txt                    # CMake build configuration
│
├── include/                          # Header files
│   ├── ast.h                        # Abstract syntax tree
│   ├── lexer.h                      # Lexer
│   ├── parser.h                     # Parser
│   ├── codegen.h                    # Code generation
│   └── runtime.h                    # Runtime support
│
├── src/                              # Source files
│   ├── main.cpp                     # Compiler entry point
│   ├── lexer.cpp                    # Lexer implementation
│   ├── parser.cpp                   # Parser implementation
│   ├── ast.cpp                      # AST implementation
│   ├── codegen.cpp                  # Code generator
│   └── runtime.cpp                  # Runtime functions
│
├── examples/                         # Compiler test examples
│   ├── simple.gom
│   ├── arrays.gom
│   ├── functions.gom
│   └── comprehensive.gom
│
└── build/                            # Build directory (generated)
    ├── gomcc                        # Compiler executable
    ├── Makefile                     # Generated makefile
    └── ...                          # Build artifacts
```

### Documentation (`docs/`)

```
docs/
├── guides/                           # User guides
│   ├── INSTALL_GUIDE.md             # Installation instructions
│   ├── USER_GUIDE.md                # Complete user documentation
│   └── PROGRAMMING_GUIDE.md         # Language features guide
│
├── language/                         # Language Construction Set
│   ├── LANGUAGE_CONSTRUCTION_QUICKSTART.md    # 5-minute intro
│   ├── LANGUAGE_CONSTRUCTION_SET.md           # Complete guide
│   ├── LANGUAGE_CONSTRUCTION_ENHANCED.md      # Advanced features
│   ├── LANGUAGE_CONSTRUCTION_QUICKREF.md      # Cheat sheet
│   └── LANGUAGE_CONSTRUCTION_SET_SUMMARY.md   # Overview
│
├── reference/                        # Technical reference
│   ├── TECHNICAL_REFERENCE.md       # Architecture & internals
│   ├── BUILTIN_FUNCTIONS.md         # Function reference
│   ├── BENCHMARKS.md                # Performance comparisons
│   ├── FEATURE_PARITY.md            # Interpreter vs compiler
│   ├── SPEC_PARITY_STATUS.md        # Specification compliance
│   ├── ASYNC_SCHEDULER_STATUS.md    # Async system details
│   ├── GRAPHICS_IMPLEMENTATION.md   # Graphics system
│   └── MANDELBROT_DOCUMENTATION.md  # Fractal example
│
├── compiler/                         # Compiler documentation
│   ├── CONSOLIDATION_COMPLETE.md    # Full compiler docs
│   ├── CONSOLIDATION_SUMMARY.md     # Quick overview
│   └── CONSOLIDATION_PROGRESS.md    # Development history
│
└── archive/                          # Historical/obsolete docs
    ├── DOCUMENTATION_UPDATE.md
    ├── IMPLEMENTATION_GUIDE.md
    ├── PHASE_5_6_COMPLETE.md
    ├── VALIDATION_REPORT.md
    └── examples_configs.md
```

### Programs (`programs/`)

```
programs/
├── README.md                         # Program catalog
│
├── examples/                         # Learning examples
│   ├── 01_hello_world.gom
│   ├── 02_variables.gom
│   ├── 03_arrays.gom
│   ├── 04_functions.gom
│   ├── 05_classes.gom
│   ├── 06_async.gom
│   └── ... (50+ examples)
│
├── demos/                            # Feature demonstrations
│   ├── feature_showcase.gom
│   ├── async_pipeline.gom
│   ├── banking_system.gom
│   ├── calculator.gom
│   ├── multi_file.gom
│   ├── reactive_counter.gom
│   ├── rpg_character.gom
│   └── task_manager.gom
│
└── tests/                            # Test programs
    └── ... (test files)
```

### Examples (`examples/`)

```
examples/
├── cosine_pattern.gom                # Graphics example
├── cosine_pattern_100.gom           # Graphics example
├── showcase.gom                      # Feature showcase
│
└── configs/                          # Demo language configurations
    ├── demo_gulplisp.json           # Lisp-like language
    ├── demo_gulfturtle.json         # Turtle graphics language
    ├── demo_gulfql.json             # SQL-like query language
    ├── demo_gulfql_modified.json    # Modified via CRUD operations
    ├── demo_gulfql_v2.json          # Updated version
    ├── demo_gulfql_minimal.json     # Minimal version
    ├── demo_gulfasm.json            # Assembly-like language
    ├── demo_basic.json              # Basic customization
    ├── demo_french.json             # French language variant
    ├── demo_minimal.json            # Minimal teaching mode
    ├── demo_professional.json       # Professional mode
    └── demo_spanish_docs.md         # Spanish documentation
```

### Configuration Presets (`configs/`)

```
configs/
├── README.md                         # Preset documentation
├── python_like.yaml                 # Python-style syntax
├── spanish_professional.yaml        # Spanish variant
└── minimal.json                     # Teaching mode
```

### Tests (`tests/`)

```
tests/
├── test_integration.py              # Integration tests
├── test_control_flow_handlers.py    # Control flow tests
├── test_function_handlers.py        # Function tests
├── test_special_handlers.py         # Special feature tests
└── test_variable_handlers.py        # Variable tests
```

### Scripts (`scripts/`)

```
scripts/
├── README.md                        # Script documentation
├── run_all_programs.py              # Run all example programs
├── run_programs_via_repl.py         # Run programs via REPL
├── benchmarks.py                    # Performance benchmarks
├── fix_function_calls.py            # Code formatting
└── fix_indentation.py               # Code formatting
```

### Executables (`executables/`)

```
executables/
├── cosine_pattern                   # Compiled executable
├── cosine_pattern_100              # Compiled executable
└── showcase                         # Compiled executable
```

## 🎯 Key Files by Purpose

### For Users

**Getting Started:**
- `README.md` - Start here!
- `docs/guides/INSTALL_GUIDE.md` - Installation
- `docs/guides/USER_GUIDE.md` - Complete usage guide

**Learning the Language:**
- `docs/guides/PROGRAMMING_GUIDE.md` - All language features
- `programs/examples/` - 50+ learning examples
- `docs/reference/BUILTIN_FUNCTIONS.md` - Function reference

**Language Customization:**
- `docs/language/LANGUAGE_CONSTRUCTION_QUICKSTART.md` - Quick start
- `docs/language/LANGUAGE_CONSTRUCTION_SET.md` - Complete guide
- `gomconfig.py` - CLI configuration tool
- `examples/configs/` - Example configurations

### For Developers

**Core Implementation:**
- `gulfofmexico/interpreter.py` - Main interpreter
- `gulfofmexico/language_config.py` - Configuration system
- `gulfofmexico/builtin.py` - Built-in functions

**Architecture:**
- `docs/reference/TECHNICAL_REFERENCE.md` - System architecture
- `docs/reference/FEATURE_PARITY.md` - Feature comparison

**Testing:**
- `tests/` - Test suite
- `scripts/run_all_programs.py` - Test runner

### For Contributors

**Documentation:**
- `DOCUMENTATION.md` - Complete doc index
- `CODE_OF_CONDUCT.md` - Community guidelines
- `docs/reference/TECHNICAL_REFERENCE.md` - Architecture

**Building:**
- `pyproject.toml` - Python package config
- `compiler/CMakeLists.txt` - C++ build config

## 📊 File Count Summary

| Category | Count | Location |
|----------|-------|----------|
| **Documentation** | 25+ | `docs/`, `*.md` |
| **Python Source** | 30+ | `gulfofmexico/` |
| **C++ Source** | 10+ | `compiler/src/`, `compiler/include/` |
| **Example Programs** | 50+ | `programs/examples/` |
| **Demo Programs** | 10+ | `programs/demos/` |
| **Test Files** | 5+ | `tests/` |
| **Config Examples** | 11+ | `examples/configs/` |
| **Presets** | 3+ | `configs/` |

## 🔄 Update History

### November 17, 2025 - Major Organization
- Created organized `docs/` directory structure
- Moved all documentation to appropriate subdirectories
- Created comprehensive `README.md`
- Created `DOCUMENTATION.md` master index
- Organized demo configs to `examples/configs/`
- Updated all documentation references
- Created this organization summary

### Previous Updates
- Language Construction Set implementation
- CRUD operations for configurations
- CLI configuration tool
- Advanced language creation demos
- Compiler marked as experimental

## 🎓 Documentation Guidelines

### Adding New Documentation

1. **User Guides** → `docs/guides/`
2. **Language Features** → `docs/language/`
3. **Technical Reference** → `docs/reference/`
4. **Compiler Docs** → `docs/compiler/`
5. **Historical/Obsolete** → `docs/archive/`

### Naming Conventions

- Use UPPER_CASE for major documents (README.md, INSTALL_GUIDE.md)
- Use descriptive names (LANGUAGE_CONSTRUCTION_SET.md)
- Include topic prefix for series (LANGUAGE_CONSTRUCTION_*)

### Cross-References

Always use relative paths from root:
- `[User Guide](docs/guides/USER_GUIDE.md)`
- `[Language Construction](docs/language/LANGUAGE_CONSTRUCTION_SET.md)`

## ✅ Organization Checklist

- [x] Created organized `docs/` structure
- [x] Moved all documentation files
- [x] Created `DOCUMENTATION.md` index
- [x] Updated `README.md`
- [x] Organized demo configs
- [x] Updated all internal references
- [x] Created this summary
- [x] Validated all links

## 🚀 Quick Access

### Most Important Files

1. **README.md** - Start here
2. **DOCUMENTATION.md** - Find any documentation
3. **docs/guides/USER_GUIDE.md** - Learn to use Gulf of Mexico
4. **docs/language/LANGUAGE_CONSTRUCTION_QUICKSTART.md** - Customize the language
5. **compiler/EXPERIMENTAL_STATUS.md** - Understand compiler limitations

### Most Used Commands

```bash
# Run program
python -m gulfofmexico script.gom

# Start REPL
python -m gulfofmexico

# Create language config
python gomconfig.py create --preset python_like

# Run demos
python demo_create_new_languages.py

# View documentation
cat DOCUMENTATION.md
```

---

**Everything is organized and documented!** 

**Start exploring**: [README.md](README.md) or [DOCUMENTATION.md](DOCUMENTATION.md)
