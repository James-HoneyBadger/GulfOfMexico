# Gulf of Mexico Interpreter - Project Overview

Welcome to the **Gulf of Mexico** programming language interpreter! This is an esoteric programming language based on Lu Wilson (TodePond)'s conceptual design, featuring unique characteristics like probabilistic variables, negative indexing, and temporal lifetimes.

## 📚 Quick Navigation

### Getting Started
- **[Installation Guide](docs/guides/INSTALL_GUIDE.md)** - Set up the interpreter
- **[User Guide](docs/guides/USER_GUIDE.md)** - Learn how to use GOM
- **[Programming Guide](docs/guides/PROGRAMMING_GUIDE.md)** - Language features and syntax

### Running Programs
```bash
# Run a GOM program
python -m gulfofmexico program.gom

# Start interactive REPL
python -m gulfofmexico

# Launch graphical IDE
python -m gulfofmexico.ide
```

### Documentation
- **[Complete Documentation Index](DOCUMENTATION.md)** - All docs and guides
- **[Latest Changes](CHANGELOG.md)** - What's new
- **[Language Features](docs/language/LANGUAGE_CONSTRUCTION_QUICKSTART.md)** - Create custom language variants

## 🎯 Current Status

### Production Ready
- ✅ **Python Interpreter** - Full-featured with REPL and IDE
- ✅ **Handler Architecture** - Modular statement processing (Phase 4)
- ✅ **Performance Optimized** - 70% faster dispatch (Phase 5)
- ✅ **Plugin System** - Production-ready extensibility (Phase 5)
- ✅ **Profiling Tools** - Complete observability (Phase 5)

### Experimental
- ⚠️ **C++ Compiler** - Research project, not production-ready

## 🚀 Phase 5: Performance & Extensibility

Latest major release with comprehensive optimizations:

### Key Improvements
- **70% Faster Handler Dispatch** - O(1) caching, 0.15ms per statement
- **Production Plugin System** - Full extensibility with dependencies
- **Enhanced Profiling** - Frame-based tracing with detailed metrics
- **Benchmarking Suite** - Automated performance analysis
- **100% Backward Compatible** - All existing code works unchanged

### Documentation
- [Phase 5 Complete Guide](PHASE_5_COMPLETE.md)
- [Phase 5 Summary](PHASE_5_SUMMARY.md)
- [Phase 5 Quick Start](PHASE_5_README.md)

## 📁 Project Structure

```
gulfofmexico/                  # Main interpreter package
├── interpreter.py            # Core execution engine
├── handler_dispatch.py        # Optimized handler dispatcher (Phase 5)
├── profiling.py              # Performance profiling tools (Phase 5)
├── plugin_manager.py         # Plugin system (Phase 5)
├── interpreter_phase5.py     # Integration layer (Phase 5)
├── benchmarking.py           # Benchmarking suite (Phase 5)
├── handlers.py               # Handler base classes
├── handler_registry.py       # Handler registration
├── handlers_impl/            # Handler implementations
├── processor/                # Lexer and parser
├── engine/                   # Experimental handler engine
├── graphics/                 # Graphics support
├── ide/                      # Interactive IDE
├── plugins/                  # Built-in plugins
└── ...

docs/                          # Documentation
├── guides/                   # User guides
├── language/                 # Language documentation
├── reference/                # API reference
└── archive/                  # Historical phase documents

tests/                         # Test suite
programs/                      # Example programs
examples/                      # GOM code examples
scripts/                       # Utility scripts
compiler/                      # C++ compiler (experimental)
```

## 🔧 Installation

### Quick Install
```bash
# Clone repository
git clone https://github.com/James-HoneyBadger/GulfOfMexico.git
cd GulfOfMexico

# Install Python interpreter
pip install -e .

# Verify installation
python -m gulfofmexico --version
```

See [Installation Guide](docs/guides/INSTALL_GUIDE.md) for detailed instructions.

## 💡 Quick Examples

### Hello World
```gom
"Hello, Gulf of Mexico!"
```

### Variables
```gom
x is 42
y is "text"
z is [1, 2, 3]
```

### Functions
```gom
double is function(x) [
    x times 2
]
```

### Conditionals
```gom
if x > 10 [
    print("Big number")
]
```

See [Programming Guide](docs/guides/PROGRAMMING_GUIDE.md) for more examples.

## 🧪 Testing

Run the test suite:
```bash
pytest tests/ -v
```

Test categories:
- **Unit Tests** - Individual module tests
- **Integration Tests** - Multi-module interaction
- **Program Tests** - Complete program execution
- **Performance Tests** - Benchmarking

## 🔌 Plugin System (Phase 5)

Extend the interpreter with custom functionality:

```python
from gulfofmexico.plugin_manager import ProductionPlugin, PluginMetadata

class MyPlugin(ProductionPlugin):
    @property
    def metadata(self):
        return PluginMetadata(
            name="my_plugin",
            version="1.0.0"
        )
    
    def get_statement_handlers(self):
        return [MyCustomHandler()]
```

## 📊 Performance (Phase 5)

| Metric | Value |
|--------|-------|
| Handler dispatch | 0.15ms/statement (70% faster) |
| Cache hit rate | 95%+ |
| Memory overhead | <1% |
| Startup time | <50ms |

## 🤝 Contributing

Contributions are welcome! Areas for contribution:
- Bug fixes and performance improvements
- Plugin development
- Documentation and examples
- Tool development

## 📝 License

MIT License - See [LICENSE](LICENSE) for details.

## 🙏 Credits

- **Original Design**: Lu Wilson (TodePond)
- **Python Implementation**: James Temple
- **Contributors**: See GitHub for full list

## 📞 Support

For issues, questions, or suggestions:
1. Check [DOCUMENTATION.md](DOCUMENTATION.md) for comprehensive guides
2. Review [Installation Guide](docs/guides/INSTALL_GUIDE.md)
3. Check existing issues on GitHub
4. Create a new issue with details

---

**The Gulf of Mexico: Where programming meets creativity!** 🌊
