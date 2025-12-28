# Project Documentation Index

Complete guide to Gulf of Mexico interpreter documentation and resources.

## 📚 Main Documentation

### [Complete Documentation](DOCUMENTATION.md)
Master index of all documentation with organized links to guides, references, and resources.

### [README](README.md)
Quick overview, installation instructions, and project information.

## 🚀 Getting Started

### [Installation Guide](docs/guides/INSTALL_GUIDE.md)
Step-by-step installation instructions for Python and C++ components.

### [User Guide](docs/guides/USER_GUIDE.md)
Complete user guide for using the interpreter and IDE.

### [Programming Guide](docs/guides/PROGRAMMING_GUIDE.md)
Language syntax, features, and programming patterns.

## 🔧 Phase Documentation

### Phase 5: Performance & Extensibility (Current)
- [Phase 5 Complete Guide](PHASE_5_COMPLETE.md) - Comprehensive feature documentation
- [Phase 5 Summary](PHASE_5_SUMMARY.md) - Implementation overview
- [Phase 5 Quick Start](PHASE_5_README.md) - Quick start guide

**Key Features:**
- 70% faster handler dispatch (O(1) caching)
- Production-ready plugin system
- Enhanced profiling and debugging
- Comprehensive benchmarking suite
- 100% backward compatible

### Historical Phase Documents
See [docs/archive/phase_reports/](docs/archive/phase_reports/) for Phase 1-4 documentation.

## 📖 Language & Technical Reference

### Language Features
- [Language Construction Quickstart](docs/language/LANGUAGE_CONSTRUCTION_QUICKSTART.md) - Create custom language variants
- [Expression Handler Guide](docs/archive/EXPRESSION_HANDLER_GUIDE.md) - Handler implementation details
- [Changelog](CHANGELOG.md) - Version history and changes

### Project Organization
- [Project Organization](docs/PROJECT_ORGANIZATION.md) - Codebase structure and organization

## 📂 Directory Guide

```
docs/
├── guides/                     # User and programming guides
├── language/                   # Language features and construction
├── reference/                  # API and technical reference
└── archive/                    # Historical documentation

gulfofmexico/
├── Core Modules
│   ├── interpreter.py          # Main execution engine
│   ├── handler_dispatch.py     # Handler dispatcher (Phase 5)
│   ├── profiling.py            # Profiling tools (Phase 5)
│   ├── plugin_manager.py       # Plugin system (Phase 5)
│   └── ...
├── handlers_impl/              # Statement handlers
├── processor/                  # Lexer and parser
├── graphics/                   # Graphics support
├── ide/                        # Interactive IDE
└── plugins/                    # Built-in plugins

tests/                          # Test suite (unit and integration tests)
examples/                       # Standalone GOM examples and reference programs
scripts/                        # Development and utility scripts
tools/                          # Maintenance and demo tools
```

## 🧪 Testing

- Run tests with: `pytest tests/ -v`
- Test files located in [tests/](tests/) directory

## 🛠️ Development

### Scripts & Tools
- [scripts/README.md](scripts/README.md) - Utility scripts documentation
- [tools/gomconfig.py](tools/gomconfig.py) - Language configuration tool

### Code Quality
- Configuration: [config/pylintrc](config/pylintrc), [config/ruff.toml](config/ruff.toml), [config/.flake8](config/.flake8)
- Style guide: Follow PEP 8 conventions
- Type hints: Recommended throughout codebase

## 🔌 Plugins & Extensions

The Phase 5 plugin system enables extending the interpreter without modifying core code.

### Creating Plugins
See [Phase 5 Complete Guide](PHASE_5_COMPLETE.md#production-plugin-system) for detailed plugin creation guide.

### Built-in Plugins
Located in [gulfofmexico/plugins/](gulfofmexico/plugins/)

## 📊 Performance & Optimization

### Phase 5 Optimizations
- Handler dispatch: 70% faster with O(1) caching
- Memory overhead: <1%
- Startup time: <50ms

### Profiling Your Code
Enable automatic profiling:
```python
from gulfofmexico import enable_profiling, run_file
enable_profiling()
run_file("program.gom")
```

See [Phase 5 Complete Guide](PHASE_5_COMPLETE.md#performance-profiling) for details.

## 🔗 Important Files

| File | Purpose |
|------|---------|
| [pyproject.toml](pyproject.toml) | Project metadata and dependencies |
| [CHANGELOG.md](CHANGELOG.md) | Version history and changes |
| [LICENSE](LICENSE) | MIT License |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Community guidelines |

## 📞 Support & Resources

### Getting Help
1. Check [DOCUMENTATION.md](DOCUMENTATION.md) for comprehensive guides
2. Review relevant topic-specific documentation above
3. See [Programming Guide](docs/guides/PROGRAMMING_GUIDE.md) for language help
4. Check example programs in [programs/](programs/) directory

### Troubleshooting
- Installation issues: See [Installation Guide](docs/guides/INSTALL_GUIDE.md)
- Language syntax: See [Programming Guide](docs/guides/PROGRAMMING_GUIDE.md)
- Performance issues: Enable profiling with Phase 5 tools

## 🎯 Quick Links by Task

**I want to...**
- **Install GOM**: → [Installation Guide](docs/guides/INSTALL_GUIDE.md)
- **Learn the language**: → [Programming Guide](docs/guides/PROGRAMMING_GUIDE.md)
- **Use the IDE**: → [User Guide](docs/guides/USER_GUIDE.md)
- **Profile code**: → [Phase 5 Guide - Profiling](PHASE_5_COMPLETE.md)
- **Create a plugin**: → [Phase 5 Guide - Plugins](PHASE_5_COMPLETE.md)
- **Run benchmarks**: → [Phase 5 Guide - Benchmarking](PHASE_5_COMPLETE.md)
- **View examples**: → [programs/](programs/) directory
- **Contribute**: → [Contributing Guide](docs/CONTRIBUTING.md) (if available)
- **See changes**: → [CHANGELOG.md](CHANGELOG.md)

---

**Last Updated**: December 27, 2025
**Current Phase**: 5 (Performance & Extensibility)
