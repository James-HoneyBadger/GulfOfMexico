# Gulf of Mexico — Complete Documentation Index

Your hub for all Gulf of Mexico docs: quick starts, language customization, technical reference, and compiler notes.

## Contents

- [Docs style guide](#️-docs-style-guide)
- [Quick Navigation](#-quick-navigation)
- [Documentation by Use Case](#-documentation-by-use-case)
- [File Structure](#-file-structure)
- [Learning Paths](#-learning-paths)
- [Tools & Utilities](#-tools--utilities)
- [Key Documentation by Topic](#-key-documentation-by-topic)
- [Important Notes](#️-important-notes)
- [Getting Help](#-getting-help)
- [Community & Policies](#-community--policies)
- [Contributing](#-contributing)
- [Quick Stats](#-quick-stats)
- [Roadmap](#-roadmap)
- [Changelog](#-changelog)

## ✍️ Docs style guide

Keep docs scannable and consistent:

- Headings: Use H1 for the page title, H2 for major sections, H3 for subsections.
- Intros: Start each page with a one‑line summary of what the page covers.
- Lists: Prefer short bullet lists over long paragraphs when enumerating items.
- Code: Use fenced code blocks with a language hint (bash, python, gom, text).
- Callouts: Use short emoji callouts (e.g., ⚠️, ✅, 📦) sparingly for emphasis.
- Links: Prefer relative links within the repo; use descriptive link text.
- Tone: Direct, friendly, and concise. Avoid jokes in policy/reference docs.
- Sections to include when relevant: Overview, Prerequisites, Steps/Examples,
  Next steps/Related links.

## 📚 Quick Navigation

### Getting Started
- **[README.md](README.md)** - Project overview and quick start
- **[Installation Guide](docs/guides/INSTALL_GUIDE.md)** - Setup instructions
- **[User Guide](docs/guides/USER_GUIDE.md)** - Complete user documentation
- **[Programming Guide](docs/guides/PROGRAMMING_GUIDE.md)** - Language features and syntax

### Language Construction Set ✨
- **[Quick Start](docs/language/LANGUAGE_CONSTRUCTION_QUICKSTART.md)** - 5-minute introduction
- **[Complete Guide](docs/language/LANGUAGE_CONSTRUCTION_SET.md)** - Full documentation
- **[Enhanced Features](docs/language/LANGUAGE_CONSTRUCTION_ENHANCED.md)** - Advanced capabilities
- **[Quick Reference](docs/language/LANGUAGE_CONSTRUCTION_QUICKREF.md)** - Cheat sheet
- **[Summary](docs/language/LANGUAGE_CONSTRUCTION_SET_SUMMARY.md)** - System overview

### Technical Reference
- **[Technical Reference](docs/reference/TECHNICAL_REFERENCE.md)** - Architecture and internals
- **[Built-in Functions](docs/reference/BUILTIN_FUNCTIONS.md)** - Complete function reference
- **[Benchmarks](docs/reference/BENCHMARKS.md)** - Performance comparisons
- **[Feature Parity](docs/reference/FEATURE_PARITY.md)** - Interpreter vs compiler features
- **[Spec Parity Status](docs/reference/SPEC_PARITY_STATUS.md)** - Specification compliance
- **[Async Scheduler](docs/reference/ASYNC_SCHEDULER_STATUS.md)** - Async/await implementation
- **[Graphics Implementation](docs/reference/GRAPHICS_IMPLEMENTATION.md)** - Graphics system
- **[Mandelbrot](docs/reference/MANDELBROT_DOCUMENTATION.md)** - Fractal rendering example

### Compiler Documentation
- **[Compiler README](compiler/README.md)** - C++ compiler overview
- **[Experimental Status](compiler/EXPERIMENTAL_STATUS.md)** ⚠️ - Important limitations
- **[Compiler Complete](docs/compiler/CONSOLIDATION_COMPLETE.md)** - Full implementation details
- **[Compiler Summary](docs/compiler/CONSOLIDATION_SUMMARY.md)** - Quick overview
- **[Compiler Progress](docs/compiler/CONSOLIDATION_PROGRESS.md)** - Development history

## 🎯 Documentation by Use Case

### I want to...

#### Learn Gulf of Mexico
1. Start with [README.md](README.md)
2. Read [User Guide](docs/guides/USER_GUIDE.md)
3. Follow [Programming Guide](docs/guides/PROGRAMMING_GUIDE.md)
4. Try examples in `programs/examples/`

#### Customize the Language
1. Read [Language Construction Quickstart](docs/language/LANGUAGE_CONSTRUCTION_QUICKSTART.md)
2. Try `python demo_create_new_languages.py`
3. Explore [Complete Guide](docs/language/LANGUAGE_CONSTRUCTION_SET.md)
4. Check [Enhanced Features](docs/language/LANGUAGE_CONSTRUCTION_ENHANCED.md)

#### Use the Compiler
⚠️ **Read [Experimental Status](compiler/EXPERIMENTAL_STATUS.md) first!**
1. See [Compiler README](compiler/README.md)
2. Understand limitations vs interpreter
3. Build and test examples

#### Develop/Contribute
1. Read [Technical Reference](docs/reference/TECHNICAL_REFERENCE.md)
2. Check [Feature Parity](docs/reference/FEATURE_PARITY.md)
3. Review [Benchmarks](docs/reference/BENCHMARKS.md)
4. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

#### Create a DSL or Language Variant
1. Read [Language Construction Quickstart](docs/language/LANGUAGE_CONSTRUCTION_QUICKSTART.md)
2. Run `python demo_create_new_languages.py` to see examples
3. Use `gomconfig.py` CLI tool
4. Reference [Enhanced Features](docs/language/LANGUAGE_CONSTRUCTION_ENHANCED.md)

## 📂 File Structure

```
GulfOfMexico/
├── README.md                          # Main project README
├── DOCUMENTATION.md                   # This file
├── CODE_OF_CONDUCT.md                # Community guidelines
├── LICENSE                           # MIT License
│
├── docs/                             # All documentation
│   ├── guides/                       # User guides
│   │   ├── INSTALL_GUIDE.md         # Installation instructions
│   │   ├── USER_GUIDE.md            # Complete user documentation
│   │   └── PROGRAMMING_GUIDE.md     # Language features guide
│   │
│   ├── language/                     # Language Construction Set docs
│   │   ├── LANGUAGE_CONSTRUCTION_QUICKSTART.md   # Quick start
│   │   ├── LANGUAGE_CONSTRUCTION_SET.md          # Complete guide
│   │   ├── LANGUAGE_CONSTRUCTION_ENHANCED.md     # Advanced features
│   │   ├── LANGUAGE_CONSTRUCTION_QUICKREF.md     # Cheat sheet
│   │   └── LANGUAGE_CONSTRUCTION_SET_SUMMARY.md  # Overview
│   │
│   ├── reference/                    # Technical reference
│   │   ├── TECHNICAL_REFERENCE.md   # Architecture & internals
│   │   ├── BUILTIN_FUNCTIONS.md     # Function reference
│   │   ├── BENCHMARKS.md            # Performance data
│   │   ├── FEATURE_PARITY.md        # Feature comparison
│   │   ├── SPEC_PARITY_STATUS.md    # Spec compliance
│   │   ├── ASYNC_SCHEDULER_STATUS.md # Async system
│   │   ├── GRAPHICS_IMPLEMENTATION.md # Graphics
│   │   └── MANDELBROT_DOCUMENTATION.md # Example
│   │
│   ├── compiler/                     # Compiler documentation
│   │   ├── CONSOLIDATION_COMPLETE.md # Full compiler docs
│   │   ├── CONSOLIDATION_SUMMARY.md  # Quick overview
│   │   └── CONSOLIDATION_PROGRESS.md # Dev history
│   │
│   └── archive/                      # Historical documentation
│
├── compiler/                         # C++ compiler (experimental)
│   ├── README.md                    # Compiler overview
│   ├── EXPERIMENTAL_STATUS.md       # ⚠️ Important limitations
│   └── ...                          # Compiler source code
│
├── gulfofmexico/                    # Python interpreter
│   ├── language_config.py           # Language Construction Set
│   ├── language_runtime.py          # Runtime integration
│   ├── interpreter.py               # Main interpreter
│   └── ...                          # Other modules
│
├── examples/                         # Example programs
│   └── configs/                     # Demo language configurations
│       ├── demo_gulplisp.json      # Lisp-like language
│       ├── demo_gulfturtle.json    # Turtle graphics language
│       ├── demo_gulfql.json        # SQL-like language
│       └── demo_gulfasm.json       # Assembly-like language
│
├── programs/                        # Example GOM programs (user-facing)
│   ├── examples/                   # Learning examples
│   └── demos/                      # Feature demonstrations
│
├── configs/                         # Preset language configs
│   ├── python_like.yaml            # Python-style preset
│   ├── minimal.json                # Minimal teaching mode
│   └── README.md                   # Preset documentation
│
├── gomconfig.py                    # CLI configuration tool
├── demo_create_new_languages.py   # Language creation demos
└── demo_language_construction_set.py # Basic demos
```

## 🎓 Learning Paths

### Path 1: Complete Beginner
1. [README.md](README.md) - Overview
2. [Installation Guide](docs/guides/INSTALL_GUIDE.md) - Setup
3. [User Guide](docs/guides/USER_GUIDE.md) - Learn the language
4. Try examples in `programs/examples/01_hello_world.gom`
5. Experiment with REPL: `python -m gulfofmexico`

### Path 2: Experienced Programmer
1. [README.md](README.md) - Quick overview
2. [Programming Guide](docs/guides/PROGRAMMING_GUIDE.md) - Language features
3. [Built-in Functions](docs/reference/BUILTIN_FUNCTIONS.md) - Function reference
4. Try demos in `programs/demos/`

### Path 3: Language Designer
1. [Language Construction Quickstart](docs/language/LANGUAGE_CONSTRUCTION_QUICKSTART.md)
2. Run `python demo_create_new_languages.py`
3. [Complete Guide](docs/language/LANGUAGE_CONSTRUCTION_SET.md)
4. [Enhanced Features](docs/language/LANGUAGE_CONSTRUCTION_ENHANCED.md)
5. Create your own language variant!

### Path 4: Contributor/Developer
1. [Technical Reference](docs/reference/TECHNICAL_REFERENCE.md)
2. [Feature Parity](docs/reference/FEATURE_PARITY.md)
3. [Compiler Experimental Status](compiler/EXPERIMENTAL_STATUS.md)
4. Review codebase in `gulfofmexico/`

## 🔧 Tools & Utilities

### Language Configuration
- **gomconfig.py** - CLI tool for managing language configurations
  ```bash
  python gomconfig.py create --preset python_like
  python gomconfig.py validate my_config.json
  python gomconfig.py info my_config.json
  ```

### Demos & Examples
- **demo_create_new_languages.py** - Create new programming languages
- **demo_language_construction_set.py** - Basic language customization
- **programs/** - Extensive example programs

### Compiler (Experimental)
- **compiler/build/gomcc** - C++ compiler executable
- See [Experimental Status](compiler/EXPERIMENTAL_STATUS.md) for limitations

## 📖 Key Documentation by Topic

### Installation & Setup
- [Installation Guide](docs/guides/INSTALL_GUIDE.md)
- [README.md](README.md#installation)

### Language Features
- [User Guide](docs/guides/USER_GUIDE.md)
- [Programming Guide](docs/guides/PROGRAMMING_GUIDE.md)
- [Built-in Functions](docs/reference/BUILTIN_FUNCTIONS.md)

### Language Customization
- [Quick Start](docs/language/LANGUAGE_CONSTRUCTION_QUICKSTART.md) ⭐ Start here!
- [Complete Guide](docs/language/LANGUAGE_CONSTRUCTION_SET.md)
- [Quick Reference](docs/language/LANGUAGE_CONSTRUCTION_QUICKREF.md)

### Advanced Topics
- [Technical Reference](docs/reference/TECHNICAL_REFERENCE.md)
- [Async Scheduler](docs/reference/ASYNC_SCHEDULER_STATUS.md)
- [Graphics System](docs/reference/GRAPHICS_IMPLEMENTATION.md)

### Performance
- [Benchmarks](docs/reference/BENCHMARKS.md)
- [Feature Parity](docs/reference/FEATURE_PARITY.md)

### Compiler
- ⚠️ [Experimental Status](compiler/EXPERIMENTAL_STATUS.md) - **Read first!**
- [Compiler README](compiler/README.md)
- [Complete Documentation](docs/compiler/CONSOLIDATION_COMPLETE.md)

## ⚠️ Important Notes

### Interpreter vs Compiler

**Python Interpreter** (Recommended):
- ✅ Full language support
- ✅ Complete Language Construction Set
- ✅ All features working
- ✅ Production-ready

**C++ Compiler** (Experimental):
- ⚠️ Research project only
- ❌ No Language Construction Set support
- ❌ Subset of features
- ❌ Not production-ready

See [Experimental Status](compiler/EXPERIMENTAL_STATUS.md) for details.

### Language Construction Set Scope

The Language Construction Set customizes the **Python interpreter only**.
It does NOT affect the C++ compiler.

## 🆘 Getting Help

1. Check [User Guide](docs/guides/USER_GUIDE.md)
2. Review [Programming Guide](docs/guides/PROGRAMMING_GUIDE.md)
3. Search this documentation index
4. Check example programs in `programs/`
5. Review [Technical Reference](docs/reference/TECHNICAL_REFERENCE.md)

## 🤝 Community & Policies

- Code of Conduct: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- License: [LICENSE](LICENSE) (MIT)
- Security/abuse reports: email <james@honey-badger.org>

## 🤝 Contributing

1. Read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
2. Review [Technical Reference](docs/reference/TECHNICAL_REFERENCE.md)
3. Check [Feature Parity](docs/reference/FEATURE_PARITY.md)
4. Submit pull requests with tests

## 📊 Quick Stats

- **Programming Language**: Gulf of Mexico
- **Implementations**: Python interpreter (stable) + C++ compiler (experimental)
- **Language Construction Set**: 5 comprehensive docs, CLI tool, demos
- **Example Programs**: 50+ in `programs/`
- **Demo Configurations**: 11 language variants in `examples/configs/`
- **Documentation Files**: 25+ organized docs
- **Built-in Functions**: 35+ (interpreter), subset in compiler

## 🗺️ Roadmap

Upcoming documentation:
- [ ] API Reference (auto-generated)
- [ ] Video tutorials
- [ ] Interactive playground documentation
- [ ] Community-contributed language variants
- [ ] LSP documentation (when implemented)

---

## 📝 Changelog

- 2025-11-17: Cleanup of internal GOM test programs. Active docs and scripts updated to reference only user-facing examples in `programs/examples/` and `programs/demos/`; compiler samples in `compiler/examples/`; Python unit tests in `tests/`. See [CHANGELOG.md](CHANGELOG.md) for details.

---

**Last Updated**: November 18, 2025

**Need help?** Start with the [README.md](README.md) or jump to the [User Guide](docs/guides/USER_GUIDE.md)!
