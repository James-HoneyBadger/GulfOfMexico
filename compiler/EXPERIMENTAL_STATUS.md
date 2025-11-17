# Gulf of Mexico C++ Compiler - Experimental Status

⚠️ **EXPERIMENTAL - NOT FOR PRODUCTION USE** ⚠️

## Overview

The Gulf of Mexico C++ compiler (`gomcc`) is an **experimental** code translation system that converts Gulf of Mexico source code to C++ executables. It is **separate and independent** from the main Python-based interpreter.

## Important Distinctions

### Python Interpreter (Main/Stable)
- **Location**: `gulfofmexico/` Python package
- **Status**: **STABLE** - Primary implementation
- **Configuration**: Uses Language Construction Set (fully customizable)
- **Features**: Complete language support, all satirical features, plugins
- **Usage**: `python -m gulfofmexico script.gom`
- **Customization**: Full language customization via `language_config.py`

### C++ Compiler (Experimental)
- **Location**: `compiler/` directory
- **Status**: **EXPERIMENTAL** - Research project
- **Configuration**: **NONE** - Does NOT use Language Construction Set
- **Features**: Subset of language features, basic compilation only
- **Usage**: `compiler/build/gomcc script.gom` (requires CMake build)
- **Customization**: **NOT SUPPORTED** - No language configuration

## Scope Separation

```
┌─────────────────────────────────────────────────────────┐
│              Python Interpreter (STABLE)                 │
│  ┌───────────────────────────────────────────────┐     │
│  │    Language Construction Set                   │     │
│  │    - Keyword customization                     │     │
│  │    - Function customization                    │     │
│  │    - Syntax customization                      │     │
│  │    - Parsing customization                     │     │
│  │    - Create new language variants              │     │
│  └───────────────────────────────────────────────┘     │
│                                                          │
│  Full GOM features + Plugins + Customization            │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│           C++ Compiler (EXPERIMENTAL)                    │
│                                                          │
│  - Fixed GOM syntax (no customization)                  │
│  - Subset of features                                   │
│  - Separate build system (CMake)                        │
│  - No plugin support                                    │
│  - No Language Construction Set integration             │
└─────────────────────────────────────────────────────────┘
```

## Why Separate?

1. **Different Goals**:
   - **Interpreter**: Flexibility, experimentation, full feature support
   - **Compiler**: Performance, static compilation, minimal dependencies

2. **Different Implementations**:
   - **Interpreter**: Python-based, dynamic, easily configurable
   - **Compiler**: C++-based, static, requires compilation

3. **Different Maturity**:
   - **Interpreter**: Production-ready, stable, well-tested
   - **Compiler**: Research prototype, incomplete, may have bugs

## Language Construction Set Does NOT Apply to Compiler

The Language Construction Set (LCS) and all configuration files (`language_config.py`, `.gomconfig`, etc.) **ONLY** affect the Python interpreter.

### What LCS Affects:
✅ `python -m gulfofmexico script.gom` - **YES**, fully customizable
✅ `python run_gom.py script.gom` - **YES**, uses interpreter
✅ `gulfofmexico.ide` Web IDE - **YES**, uses interpreter
✅ Plugin system - **YES**, interpreter-based

### What LCS Does NOT Affect:
❌ `gomcc script.gom` - **NO**, compiler has fixed syntax
❌ Compiled executables - **NO**, already compiled
❌ C++ compiler build process - **NO**, separate CMake system

## When to Use Each

### Use Python Interpreter When:
- You want to customize the language
- You need full GOM feature support
- You're using plugins or extensions
- You need dynamic behavior
- You're experimenting or learning

### Use C++ Compiler When:
- You need maximum performance
- You're willing to accept limited features
- You don't need language customization
- You want standalone executables
- You're doing research on compilation

## Current Compiler Limitations

The experimental compiler currently supports:
- ✅ Basic variables and assignments
- ✅ Simple functions
- ✅ Basic control flow (if/when)
- ✅ Arrays and loops
- ✅ Limited built-in functions

The compiler does NOT support:
- ❌ Language customization (LCS)
- ❌ Satirical keywords
- ❌ Quantum/temporal features
- ❌ Plugin system
- ❌ Full standard library
- ❌ Classes and OOP
- ❌ Async/await
- ❌ Many advanced features

## Future Plans

The compiler is a long-term research project. Potential future work:
- [ ] Expand feature support
- [ ] Optimize performance
- [ ] Better error messages
- [ ] Possible LCS integration (distant future)

For now, **use the Python interpreter** for all serious work and language customization.

## Building the Compiler

If you want to experiment with the compiler:

```bash
cd compiler/build
cmake ..
make

# Compile a GOM file
./gomcc ../examples/simple.gom

# Run the output
./simple
```

## Documentation

- Python Interpreter: See main README.md, USER_GUIDE.md
- Language Customization: See LANGUAGE_CONSTRUCTION_SET.md
- Compiler Details: See compiler/README.md, compiler/COMPILER_COMPLETE.md

## Questions?

**Q: Can I use my custom language config with the compiler?**
A: No, the compiler has a fixed parser and does not support LCS.

**Q: Why did you build a compiler if it's experimental?**
A: Research and learning. Also, it may become production-ready in the future.

**Q: Which should I use?**
A: **Use the Python interpreter** unless you specifically need the compiler.

**Q: Will the compiler ever support LCS?**
A: Maybe in the distant future, but it's not a current priority.

---

**Bottom Line**: The Python interpreter is the main, stable, customizable implementation. The C++ compiler is an experimental research project with a fixed syntax and limited features.
