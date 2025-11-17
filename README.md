# GOM - Gulf of Mexico Programming Language

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![What's New](https://img.shields.io/badge/What’s%20New-CHANGELOG-brightgreen)](CHANGELOG.md)

> *The perfect programming language* - Based on the conceptual design by **Lu Wilson (TodePond)** ([original repo](https://github.com/TodePond/GulfOfMexico))

## 📖 Quick Links

- **[Complete Documentation](DOCUMENTATION.md)** - Full documentation index
- **[What’s New](CHANGELOG.md)** - Latest changes
- **[Installation Guide](docs/guides/INSTALL_GUIDE.md)** - Setup instructions
- **[User Guide](docs/guides/USER_GUIDE.md)** - Complete user documentation
- **[Programming Guide](docs/guides/PROGRAMMING_GUIDE.md)** - Language features
- **[Language Construction Set](docs/language/LANGUAGE_CONSTRUCTION_QUICKSTART.md)** - Create custom language variants

> Note (Nov 2025): Internal GOM test programs used for designing/debugging the language were removed. Use user-facing examples in `programs/examples/`, demos in `programs/demos/`, compiler examples in `compiler/examples/`, and Python unit tests in `tests/`.

## 🚀 Two Implementations

### Python Interpreter ⭐ (Recommended)
- **Full-featured** REPL with graphical IDE
- **Complete** language support with all features
- **Language Construction Set** - Create custom language variants
- **Plugin system** for extensibility
- **Rich debugging** and interactive development
- **Production-ready** and fully tested

### C++ Compiler ⚠️ (Experimental)
- **Research project** - not production-ready
- Compiles to C++ and native executables
- **Subset** of features (no satirical keywords, limited functions)
- **Does NOT support** Language Construction Set customization
- **Use Python interpreter** for full features
- See [`compiler/EXPERIMENTAL_STATUS.md`](compiler/EXPERIMENTAL_STATUS.md) for details

## 🎯 Installation

```bash
# Clone repository
git clone https://github.com/James-HoneyBadger/GulfOfMexico.git
cd GulfOfMexico

# Install Python interpreter
pip install -e .

# Optional: Build C++ compiler (experimental)
cd compiler/build
cmake ..
make -j4
```

For detailed installation instructions, see [`docs/guides/INSTALL_GUIDE.md`](docs/guides/INSTALL_GUIDE.md).

## ⚡ Quick Start

### Run Your First Program

```bash
# Create a file: hello.gom
echo 'print("Hello, Gulf of Mexico!")!' > hello.gom

# Run it
python -m gulfofmexico hello.gom
```

### Interactive REPL

```bash
# Start REPL
python -m gulfofmexico

# Or use the graphical IDE
python -m gulfofmexico.ide
```

### Try Examples

```bash
# Run example programs
python -m gulfofmexico programs/examples/01_hello_world.gom
python -m gulfofmexico programs/examples/02_variables.gom

# Run feature demonstrations
python -m gulfofmexico programs/demos/feature_showcase.gom
```

## 🎨 Language Construction Set ✨ **NEW!**

**Create your own programming language** by customizing Gulf of Mexico!

### What Can You Customize?

- ✅ **Keywords** - Rename any keyword (`if`→`si`, `function`→`defun`)
- ✅ **Functions** - Add, remove, or rename built-in functions
- ✅ **Syntax** - Array indexing, comments, delimiters
- ✅ **Parsing** - Block syntax, separators, operators
- ✅ **Features** - Enable/disable satirical keywords, quantum features

### Quick Examples

```bash
# Use Python-like syntax
python -m gulfofmexico --preset python_like myprogram.gom

# Spanish keywords
python -m gulfofmexico --preset spanish programa.gom

# Minimal teaching mode
python -m gulfofmexico --preset minimal script.gom

# Load custom configuration
python -m gulfofmexico --config my_language.json script.gom
```

### Create Language Variants

```bash
# See what's possible
python demo_create_new_languages.py

# This creates:
# - GulfLisp (Lisp-like)
# - GulfTurtle (Logo/Turtle graphics)
# - GulfQL (SQL-like)
# - GulfASM (Assembly-like)
# Plus demonstrates CRUD operations!
```

### CLI Configuration Tool

```bash
# Create from preset
python gomconfig.py create --preset python_like --output my_lang.json

# Interactive creation
python gomconfig.py create --interactive

# Update configuration
python gomconfig.py update my_lang.json --set metadata.author "Your Name"

# Delete elements
python gomconfig.py delete my_lang.json --keyword synergize --function blockchain

# Merge configurations
python gomconfig.py update config1.json --merge config2.json

# Compare configurations
python gomconfig.py diff config1.json config2.json

# Validate
python gomconfig.py validate my_lang.json

# Show info
python gomconfig.py info my_lang.json
```

### Available Presets

- **python_like** - Python-style (`def`, 0-based arrays, `#` comments)
- **js_like** - JavaScript-style (semicolons, 0-based)
- **serious** - No satirical features
- **minimal** - Teaching mode (6 keywords, 5 functions)
- **spanish** - Spanish keywords
- **french** - French keywords

### Documentation

- **[Quick Start](docs/language/LANGUAGE_CONSTRUCTION_QUICKSTART.md)** - 5-minute introduction
- **[Complete Guide](docs/language/LANGUAGE_CONSTRUCTION_SET.md)** - Full documentation
- **[Enhanced Features](docs/language/LANGUAGE_CONSTRUCTION_ENHANCED.md)** - Advanced capabilities
- **[Quick Reference](docs/language/LANGUAGE_CONSTRUCTION_QUICKREF.md)** - Cheat sheet

See examples in [`examples/configs/`](examples/configs/) - includes Lisp, SQL, Logo, and Assembly variants!

## 🌟 Core Language Features

### Arrays Start at -1
```gom
var items = ["first", "second", "third"]
print(items[-1])!  // Prints "first"
print(items[0])!   // Prints "second"
print(items[1])!   // Prints "third"
```

### Flexible String Syntax
```gom
var message = "Hello World"!          // Double quotes
var name = 'Alice'!                   // Single quotes
var multiline = """
  This is a
  multi-line string
"""!                                  // Triple quotes
```

### Three-Valued Logic
```gom
var answer = maybe!  // true, false, or maybe
```

### Functions
```gom
function greet(name) {
  print("Hello, " + name)!
  return "Greetings sent"!
}

var result = greet("World")!
```

### Satirical Keywords
```gom
// Procrastination scheduling
later {
  print("I'll do this eventually")!
}

// Corporate synergy
synergize data with analytics!

// Quantum computing
quantum_compute {
  // Exists in multiple states simultaneously
}
```

### More Features

- **Classes and Objects** - OOP support
- **Async/Await** - Asynchronous programming
- **Pattern Matching** - Advanced control flow
- **Time Travel** - Temporal variable lifetimes
- **Graphics** - Built-in turtle graphics and image manipulation
- **Plugin System** - Extend the language

See [`docs/guides/PROGRAMMING_GUIDE.md`](docs/guides/PROGRAMMING_GUIDE.md) for complete language documentation.

## 📚 Documentation

### Essential Reading
- **[DOCUMENTATION.md](DOCUMENTATION.md)** - Complete documentation index
- **[User Guide](docs/guides/USER_GUIDE.md)** - How to use Gulf of Mexico
- **[Programming Guide](docs/guides/PROGRAMMING_GUIDE.md)** - Language features

### Language Customization
- **[Quick Start](docs/language/LANGUAGE_CONSTRUCTION_QUICKSTART.md)** - Get started in 5 minutes
- **[Complete Guide](docs/language/LANGUAGE_CONSTRUCTION_SET.md)** - Everything about customization

### Reference
- **[Built-in Functions](docs/reference/BUILTIN_FUNCTIONS.md)** - Complete function reference
- **[Technical Reference](docs/reference/TECHNICAL_REFERENCE.md)** - Architecture and internals
- **[Benchmarks](docs/reference/BENCHMARKS.md)** - Performance comparisons

### Compiler
- **⚠️ [Experimental Status](compiler/EXPERIMENTAL_STATUS.md)** - Important limitations
- **[Compiler README](compiler/README.md)** - C++ compiler overview

## 🔧 Advanced Usage

### Debugging

```bash
# Show internal debug messages
python -m gulfofmexico --debug script.gom

# Show completion messages
python -m gulfofmexico --verbose script.gom

# Launch IDE with debug output
python -m gulfofmexico.ide --debug

# Or use environment variables
GULFOFMEXICO_DEBUG=1 python -m gulfofmexico script.gom
```

### REPL Commands

```text
:load programs/examples/01_hello_world.gom   # Load and run a file
:vars                                         # Show all variables
:history 10                                   # Show last 10 commands
:run 5                                        # Re-run command #5
:reset                                        # Clear all state
:quit                                         # Exit REPL
```

### Custom Configuration

```python
from gulfofmexico.language_config import LanguageConfig

# Create custom language
config = LanguageConfig(name="MyLanguage")

# Customize keywords
config.rename_keyword("if", "cuando")
config.rename_keyword("function", "función")

# Customize functions  
config.rename_function("print", "imprimir")

# Disable satirical features
config.disable_satirical_keywords()

# Save
config.save("my_language.json")

# Use it
# python -m gulfofmexico --config my_language.json script.gom
```

## 📁 Project Structure

```
GulfOfMexico/
├── gulfofmexico/              # Python interpreter (main implementation)
│   ├── language_config.py     # Language Construction Set
│   ├── language_runtime.py    # Runtime integration
│   ├── interpreter.py          # Main interpreter
│   ├── builtin.py             # Built-in functions
│   └── ...
│
├── compiler/                   # C++ compiler (experimental)
│   ├── EXPERIMENTAL_STATUS.md # ⚠️ Read this first!
│   └── ...
│
├── docs/                       # All documentation
│   ├── guides/                # User guides
│   ├── language/              # Language Construction Set docs
│   ├── reference/             # Technical reference
│   └── compiler/              # Compiler documentation
│
├── programs/                   # Example programs (user-facing)
│   ├── examples/              # Learning examples
│   └── demos/                 # Feature demonstrations
│
├── examples/configs/           # Demo language configurations
│   ├── demo_gulplisp.json     # Lisp-like language
│   ├── demo_gulfturtle.json   # Turtle graphics
│   ├── demo_gulfql.json       # SQL-like language
│   └── demo_gulfasm.json      # Assembly-like
│
├── configs/                    # Language presets
│   ├── python_like.yaml       # Python-style
│   ├── minimal.json           # Teaching mode
│   └── README.md
│
├── gomconfig.py               # CLI configuration tool
├── demo_create_new_languages.py  # Advanced demos
└── README.md                  # This file
```

## 🎓 Examples

### Hello World
```gom
print("Hello, World")!
```

### Variables and Arrays
```gom
var name = "Alice"!
var numbers = [10, 20, 30]!
var first = numbers[-1]!  // -1 indexing!
```

### Functions
```gom
function factorial(n) {
  if n < 2 {
    return 1!
  }
  return n * factorial(n - 1)!
}

print(factorial(5))!  // 120
```

### Classes
```gom
class Person {
  function __init__(name, age) {
    this.name = name!
    this.age = age!
  }
  
  function greet() {
    print("Hello, I'm " + this.name)!
  }
}

var alice = Person("Alice", 30)!
alice.greet()!
```

### Async/Await
```gom
async function fetchData(url) {
  var result = await http.get(url)!
  return result!
}

var data = await fetchData("https://api.example.com/data")!
```

See [`programs/examples/`](programs/examples/) for 50+ example programs!

## 🚦 Language Construction Set Examples

### Create a Lisp-Like Language

```python
from gulfofmexico.language_config import LanguageConfig, ParsingConfig

config = LanguageConfig(name="GulfLisp")

# Lisp-style syntax
config.parsing_config = ParsingConfig(
    block_start="(",
    block_end=")",
    list_start="(",
    list_end=")",
)

# Lisp keywords
config.rename_keyword("function", "defun")
config.rename_keyword("var", "let")

config.save("gulplisp.json")
```

### Create a Teaching Language

```python
config = LanguageConfig(name="TeachingGOM")

# Keep only essentials
config.disable_satirical_keywords()
config.update({"syntax_options": {"array_start_index": 0}}, merge=True)

# Remove advanced features
config.delete_keyword("quantum_compute")
config.delete_keyword("time_travel")

config.save("teaching.json")
```

Run the comprehensive demo:
```bash
python demo_create_new_languages.py
```

This creates 5 complete language variants:
- **GulfLisp** - Lisp-like with parentheses
- **GulfTurtle** - Logo/Turtle graphics  
- **GulfQL** - SQL-like query language
- **GulfASM** - Minimal assembly-like
- Plus CRUD operations demonstration!

## ⚠️ Important: Interpreter vs Compiler

| Feature | Python Interpreter | C++ Compiler |
|---------|-------------------|--------------|
| **Status** | ✅ Production-ready | ⚠️ Experimental |
| **Language Construction Set** | ✅ Full support | ❌ Not supported |
| **All Features** | ✅ Complete | ❌ Subset only |
| **Satirical Keywords** | ✅ Yes | ❌ No |
| **Plugin System** | ✅ Yes | ❌ No |
| **Customization** | ✅ Full | ❌ None |
| **Use For** | Development, production | Research, experiments |

**Recommendation**: Use the **Python interpreter** for all development and production use.

See [`compiler/EXPERIMENTAL_STATUS.md`](compiler/EXPERIMENTAL_STATUS.md) for detailed comparison.

## 🤝 Contributing

Contributions are welcome! Please:

1. Read [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)
2. Check [`docs/reference/TECHNICAL_REFERENCE.md`](docs/reference/TECHNICAL_REFERENCE.md)
3. Submit pull requests with tests
4. Follow the existing code style

## 📊 Statistics

- **Programming Language**: Gulf of Mexico
- **Implementations**: Python interpreter (stable) + C++ compiler (experimental)
- **Language Construction Set**: 5 comprehensive docs, CLI tool, working demos
- **Example Programs**: 50+ programs in [`programs/`](programs/)
- **Demo Configurations**: 11+ language variants in [`examples/configs/`](examples/configs/)
- **Documentation**: 25+ organized documents in [`docs/`](docs/)
- **Built-in Functions**: 35+ functions (interpreter)
- **Presets**: 6 language presets ready to use

## 🎯 Use Cases

- **Learning**: Great for teaching programming concepts
- **Prototyping**: Quick experimentation with satirical features
- **Language Design**: Create custom language variants
- **DSL Creation**: Build domain-specific languages
- **Research**: Experiment with novel language features

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

## 🙏 Credits

- **Original Concept**: Lu Wilson (TodePond) - https://github.com/TodePond/GulfOfMexico
- **Implementation**: James-HoneyBadger
- **Language Construction Set**: Advanced customization system

## 📞 Links

- **GitHub**: https://github.com/James-HoneyBadger/GulfOfMexico
- **Documentation**: [DOCUMENTATION.md](DOCUMENTATION.md)
- **Original Concept**: https://github.com/TodePond/GulfOfMexico

---

**Get Started**: [`python -m gulfofmexico`](docs/guides/USER_GUIDE.md)

**Customize**: [`python demo_create_new_languages.py`](docs/language/LANGUAGE_CONSTRUCTION_QUICKSTART.md)

**Learn More**: [DOCUMENTATION.md](DOCUMENTATION.md)
