# Gulf of Mexico Language Construction Set

## Overview

The Language Construction Set allows you to customize every aspect of Gulf of Mexico's syntax, keywords, functions, and behavior. Create your own language variants, internationalize keywords, disable features, or create domain-specific dialects.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Configuration File Format](#configuration-file-format)
3. [Customization Options](#customization-options)
4. [Creating Custom Configurations](#creating-custom-configurations)
5. [Using Configurations](#using-configurations)
6. [Presets](#presets)
7. [Advanced Features](#advanced-features)
8. [Examples](#examples)
9. [API Reference](#api-reference)

---

## Quick Start

### Install Dependencies

```bash
pip install pyyaml
```

### Use a Preset

```bash
# Run with Python-like syntax
python -m gulfofmexico --preset python_like myprogram.gom

# Run in serious mode (no satirical features)
python -m gulfofmexico --preset serious myprogram.gom

# Run with Spanish keywords
python -m gulfofmexico --preset spanish myprogram.gom
```

### Create Your Own Configuration

```python
from gulfofmexico.language_config import LanguageConfig

# Start with default Gulf of Mexico
config = LanguageConfig()

# Customize keywords
config.rename_keyword("if", "when_condition")
config.rename_keyword("function", "def")

# Customize functions
config.rename_function("print", "output")
config.add_function("log", arity=-1, description="Logging function")

# Adjust syntax
config.set_array_indexing(0, False)  # 0-based, no fractional
config.disable_satirical_keywords()

# Save configuration
config.save("my_language.yaml")
```

### Use Your Configuration

```bash
# Load from file
python -m gulfofmexico --config my_language.yaml myprogram.gom

# Set as environment variable
export GULFOFMEXICO_CONFIG=my_language.yaml
python -m gulfofmexico myprogram.gom

# Use .gomconfig in current directory
# (automatically loaded)
```

---

## Configuration File Format

Configurations can be in YAML or JSON format. YAML is recommended for readability.

### Basic Structure

```yaml
metadata:
  name: "My Custom Language"
  version: "1.0.0"
  description: "Description of your variant"
  author: "Your Name"

keywords:
  # keyword_name:
  #   original: original_name
  #   custom: custom_name
  #   category: category
  #   description: description

functions:
  # function_name:
  #   name: custom_name
  #   arity: number_of_args  # -1 for variadic
  #   implementation: python_reference
  #   description: description
  #   enabled: true/false

operators:
  # symbol:
  #   symbol: operator_symbol
  #   precedence: number
  #   associativity: left/right/none
  #   enabled: true/false

syntax_options:
  array_start_index: -1  # or 0
  allow_fractional_indexing: true
  flexible_quoting: true
  string_interpolation: true
  interpolation_symbol: "$"
  single_line_comment: "//"
  multi_line_comment_start: null
  multi_line_comment_end: null
  require_semicolons: false
  statement_terminator: "!"
  three_valued_logic: true
  probabilistic_variables: true
  temporal_variables: true
  enable_satirical_keywords: true
  enable_quantum_features: true
  enable_time_travel: true
  enable_gaslighting: true

runtime:
  debug_mode: false
  strict_mode: false
  compatibility_mode: "standard"
```

---

## Customization Options

### Keywords

You can rename, add, or remove keywords:

```python
# Rename keywords
config.rename_keyword("if", "si")
config.rename_keyword("when", "cuando")
config.rename_keyword("function", "función")

# Add custom keywords
config.add_keyword("foreach", category="control", description="For each loop")

# Remove keywords
config.remove_keyword("quantum")  # Remove quantum keyword
config.disable_satirical_keywords()  # Remove all satirical keywords
```

**Keyword Categories:**
- `control`: Flow control (if, when, after)
- `function`: Function-related (function, async, await, return)
- `variable`: Variable declarations (const, var)
- `oop`: Object-oriented (class, className)
- `special`: Special operations (delete, reverse, previous, next)
- `module`: Module system (import, export)
- `error`: Error handling (try, whatever)
- `satirical`: Satirical keywords (all the fun ones)
- `custom`: Your custom keywords

### Built-in Functions

Customize or add built-in functions:

```python
# Rename functions
config.rename_function("print", "output")
config.rename_function("read", "input")

# Add custom functions
config.add_function(
    name="log",
    arity=-1,  # variadic
    implementation="custom.logging.log_function",
    description="Custom logging"
)

# Disable functions
config.disable_function("sleep")  # Disable but keep in config
config.remove_function("quantum")  # Remove completely
```

### Operators

Customize operator precedence and availability:

```python
# Change precedence
config.change_operator_precedence("*", 25)  # Make multiplication higher

# Add custom operators
config.add_operator("**", precedence=35, associativity="right")  # Exponentiation

# Remove operators
config.remove_operator("~=")  # Remove approximate equality
```

**Precedence Levels:**
- 1: Assignment (=)
- 2-3: Logical (|, &)
- 5: Comparison (==, <, >, etc.)
- 10: Addition/Subtraction (+, -)
- 20: Multiplication/Division (*, /)
- 30: Exponentiation (^)
- 40+: Unary (!, ++, --)
- 50: Member access (.)

### Syntax Options

#### Array Indexing

```python
# Traditional 0-based indexing
config.set_array_indexing(start_index=0, allow_fractional=False)

# Gulf of Mexico -1 based indexing (default)
config.set_array_indexing(start_index=-1, allow_fractional=True)

# Custom start index
config.set_array_indexing(start_index=1, allow_fractional=False)  # 1-based like Lua
```

#### Comment Styles

```python
# Python-style comments
config.set_comment_style(single_line="#")

# C-style comments
config.set_comment_style(
    single_line="//",
    multi_start="/*",
    multi_end="*/"
)

# SQL-style comments
config.set_comment_style(single_line="--")
```

#### Language Features

```python
# Enable/disable features
config.enable_feature("satirical", False)  # Disable satirical keywords
config.enable_feature("quantum", False)    # Disable quantum features
config.enable_feature("time_travel", False)  # Disable time travel
config.enable_feature("three_valued_logic", True)  # Keep 3-valued logic

# Shorthand
config.syntax_options.enable_satirical_keywords = False
config.syntax_options.probabilistic_variables = True
```

**Available Features:**
- `satirical`: All satirical keywords (happy, sad, blockchain, etc.)
- `quantum`: Quantum computing features
- `time_travel`: Time travel statements
- `gaslighting`: Gaslighting (definitely_not)
- `three_valued_logic`: true/false/maybe
- `probabilistic`: Probabilistic variables with confidence
- `temporal`: Temporal variables with lifetimes

---

## Creating Custom Configurations

### From Scratch

```python
from gulfofmexico.language_config import LanguageConfig

config = LanguageConfig()
config.name = "My Language"
config.version = "1.0.0"
config.description = "My custom variant"

# Customize as needed...

config.save("my_lang.yaml")
```

### From Preset

```python
# Start with a preset and modify
config = LanguageConfig.from_preset("python_like")

# Add your customizations
config.rename_keyword("class", "blueprint")
config.add_function("debug", arity=-1, description="Debug output")

config.save("my_python_variant.yaml")
```

### Interactive Builder

```python
from gulfofmexico.language_config import create_custom_config_interactive

config = create_custom_config_interactive()
# Follow the prompts...

config.save("my_config.yaml")
```

### Validation

Always validate your configuration:

```python
errors = config.validate()
if errors:
    print("Configuration errors:")
    for error in errors:
        print(f"  - {error}")
else:
    print("Configuration is valid!")
    config.save("my_config.yaml")
```

---

## Using Configurations

### Command Line

```bash
# Load specific config file
python -m gulfofmexico --config my_config.yaml script.gom

# Use preset
python -m gulfofmexico --preset python_like script.gom

# Serious mode shortcut
python -m gulfofmexico --serious-mode script.gom
```

### Environment Variable

```bash
# Set globally
export GULFOFMEXICO_CONFIG=/path/to/my_config.yaml
python -m gulfofmexico script.gom

# Set for one command
GULFOFMEXICO_CONFIG=my_config.yaml python -m gulfofmexico script.gom
```

### Project Config File

Create `.gomconfig` in your project directory (YAML or JSON):

```yaml
# .gomconfig
metadata:
  name: "Project Language Config"

keywords:
  if:
    original: "if"
    custom: "when"

# ... rest of config
```

The interpreter will automatically load `.gomconfig` from:
1. Current directory
2. Home directory (~/.gomconfig)
3. Path in GULFOFMEXICO_CONFIG environment variable

### Programmatic Usage

```python
from gulfofmexico.language_config import LanguageConfig
from gulfofmexico.language_runtime import LanguageRuntime
from gulfofmexico import run_file

# Load configuration
config = LanguageConfig.load("my_config.yaml")

# Apply to runtime
LanguageRuntime.load_config(config)

# Run programs with custom config
run_file("myprogram.gom")
```

---

## Presets

Built-in presets for common use cases:

### `python_like`
- `def` instead of `function`
- 0-based array indexing
- No fractional indexing
- `#` comments
- No semicolons
- Satirical features disabled

### `js_like`
- 0-based array indexing
- Semicolons required
- No satirical features
- Traditional syntax

### `serious`
- All satirical keywords removed
- No quantum/time travel/gaslighting
- Professional mode
- All core features intact

### `minimal`
- Only essential keywords (if, function, return, const, var, class)
- Minimal built-in functions (print, Number, String, Boolean, List)
- No special features
- Strict mode enabled

### `spanish`
- Spanish keyword translations
- `si` (if), `cuando` (when), `función` (function)
- `imprimir` (print), `leer` (read)
- Gulf of Mexico features intact

### `french`
- French keyword translations
- `si` (if), `quand` (when), `fonction` (function)
- `imprimer` (print)
- Gulf of Mexico features intact

---

## Advanced Features

### Custom Function Implementation

```python
# Define custom function
def my_custom_function(arg1, arg2):
    # Your implementation
    from gulfofmexico.builtin import GulfOfMexicoString
    return GulfOfMexicoString(f"{arg1} + {arg2}")

# Add to config
config.add_function(
    name="mycustom",
    arity=2,
    implementation="mymodule.my_custom_function",
    description="My custom function"
)
```

### Exporting Documentation

Generate documentation for your language variant:

```python
# Export mapping table
markdown = config.export_mapping_table("my_language_docs.md")
print(markdown)
```

Output:
```markdown
# Language Configuration Mapping

**Language:** My Language
**Version:** 1.0.0

## Keywords
| Original | Custom | Category | Description |
|----------|--------|----------|-------------|
| `if` | `when_condition` | control | Conditional statement |
...

## Built-in Functions
| Name | Arity | Description | Enabled |
|------|-------|-------------|---------|
| `print` | variadic | Print to stdout | ✓ |
...
```

### Runtime Information

```python
from gulfofmexico.language_runtime import LanguageRuntime

# Get current config info
info = LanguageRuntime.get_info()
print(info)

# Check if features are enabled
if LanguageRuntime.is_feature_enabled("satirical"):
    print("Satirical keywords available!")

# Get current settings
start_idx = LanguageRuntime.get_array_start_index()
print(f"Arrays start at index: {start_idx}")
```

### Hot Reloading

```python
# Load initial config
LanguageRuntime.load_config(config1)

# Later, switch to different config
LanguageRuntime.load_config(config2)

# Reset to default
LanguageRuntime.reset()
```

---

## Examples

### Example 1: Python-Style Gulf of Mexico

```yaml
# python_gom.yaml
metadata:
  name: "Gulf of Mexico (Pythonic)"

keywords:
  function:
    original: "function"
    custom: "def"
  # ... other keywords stay the same

syntax_options:
  array_start_index: 0
  allow_fractional_indexing: false
  single_line_comment: "#"
  enable_satirical_keywords: false
```

Usage:
```python
# program.gom (with python_gom.yaml config)
def greet(name) {
    print("Hello, ${name}!")
}

numbers = List(1, 2, 3, 4, 5)
print(numbers[0])  # Prints 1 (0-indexed)
```

### Example 2: Minimal Teaching Language

```yaml
# teaching.yaml
metadata:
  name: "Gulf of Mexico for Teaching"
  description: "Minimal feature set for beginners"

# Only keep: if, function, return, var
keywords:
  if: {original: "if", custom: "if", category: "control"}
  function: {original: "function", custom: "function", category: "function"}
  return: {original: "return", custom: "return", category: "function"}
  var: {original: "var", custom: "var", category: "variable"}

# Only keep: print, Number, String, List
functions:
  print: {name: "print", arity: -1, enabled: true}
  Number: {name: "Number", arity: 1, enabled: true}
  String: {name: "String", arity: 1, enabled: true}
  List: {name: "List", arity: -1, enabled: true}

syntax_options:
  array_start_index: 0
  allow_fractional_indexing: false
  enable_satirical_keywords: false
  enable_quantum_features: false
  three_valued_logic: false
  probabilistic_variables: false
```

### Example 3: Domain-Specific (Data Science)

```python
from gulfofmexico.language_config import LanguageConfig

config = LanguageConfig.from_preset("python_like")
config.name = "Gulf of Mexico for Data Science"

# Add domain-specific functions
config.add_function("dataframe", arity=1, description="Create DataFrame")
config.add_function("plot", arity=2, description="Plot data")
config.add_function("analyze", arity=1, description="Analyze dataset")

# Rename to match pandas
config.rename_function("List", "Series")
config.add_function("read_csv", arity=1, description="Read CSV file")

config.save("datascience_gom.yaml")
```

---

## API Reference

### LanguageConfig

Main configuration class.

**Methods:**

- `rename_keyword(original: str, new_name: str)` - Rename a keyword
- `add_keyword(name: str, category: str, description: str)` - Add custom keyword
- `remove_keyword(name: str)` - Remove a keyword
- `disable_satirical_keywords()` - Remove all satirical keywords
- `get_keyword_by_category(category: str)` - Get keywords in category
- `add_function(name, arity, implementation, description)` - Add function
- `rename_function(original, new_name)` - Rename function
- `disable_function(name)` - Disable function
- `remove_function(name)` - Remove function
- `add_operator(symbol, precedence, associativity)` - Add operator
- `remove_operator(symbol)` - Remove operator
- `change_operator_precedence(symbol, new_precedence)` - Change precedence
- `set_array_indexing(start_index, allow_fractional)` - Configure arrays
- `set_comment_style(single_line, multi_start, multi_end)` - Configure comments
- `enable_feature(feature, enabled)` - Enable/disable features
- `from_preset(preset_name)` - Load preset (class method)
- `validate()` - Validate configuration
- `to_dict()` - Convert to dictionary
- `from_dict(data)` - Create from dictionary (class method)
- `save(filepath, format)` - Save to file
- `load(filepath)` - Load from file (class method)
- `export_mapping_table(filepath)` - Export documentation

### LanguageRuntime

Runtime system for applying configurations.

**Methods:**

- `load_config(config, config_file)` - Load configuration (class method)
- `get_config()` - Get current config (class method)
- `reset()` - Reset to default (class method)
- `translate_keyword(keyword_text)` - Translate custom to original (class method)
- `is_keyword_enabled(original_keyword)` - Check if enabled (class method)
- `get_array_start_index()` - Get array start index (class method)
- `is_fractional_indexing_enabled()` - Check fractional indexing (class method)
- `is_feature_enabled(feature)` - Check feature status (class method)
- `get_info()` - Get runtime info string (class method)

---

## FAQ

**Q: Can I use multiple configurations?**
A: Yes, you can switch configurations at runtime using `LanguageRuntime.load_config()`.

**Q: Are custom configurations backwards compatible?**
A: Configurations that only rename keywords/functions are backwards compatible. Removing features or changing syntax may break existing code.

**Q: Can I create entirely new keywords?**
A: You can add keywords to the configuration, but you'd need to modify the parser to recognize new syntax. The system currently supports renaming existing keywords.

**Q: How do I share my configuration?**
A: Save your config as a .yaml or .json file and share it. Others can load it with `--config yourfile.yaml`.

**Q: Can I use configurations in the web IDE?**
A: Yes! The web IDE will respect configurations loaded via environment variables or .gomconfig files.

---

## Contributing

Want to add more presets or improve the system?

1. Fork the repository
2. Create your preset or enhancement
3. Add tests and documentation
4. Submit a pull request

---

## License

Same as Gulf of Mexico - see LICENSE file.
