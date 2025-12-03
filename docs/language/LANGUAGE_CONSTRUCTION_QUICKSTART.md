# Language Construction Set - Quick Start Guide

## What Is This?

The Language Construction Set lets you **create entirely new programming languages** by customizing Gulf of Mexico. You can:

- Rename ANY keyword (if→si, function→defun, etc.)
- Add/remove/modify built-in functions
- Change syntax (array indexing, comments, delimiters)
- Customize parsing (parentheses vs braces, etc.)
- Create language variants (Lisp-like, SQL-like, Logo-like, etc.)

**Scope**: Works with **Python interpreter only** (not the experimental C++ compiler).

## Installation

Already installed with Gulf of Mexico:
```bash
pip install -e .
```

## 5-Minute Quick Start

### 1. List Available Presets

```bash
python gomconfig.py list-presets
```

Output:
```
Available Presets:
  python_like    - Python-style syntax
  js_like        - JavaScript-style syntax
  serious        - No satirical features
  minimal        - Teaching mode (6 keywords, 5 functions)
  spanish        - Spanish keywords
  french         - French keywords
```

### 2. Create From Preset

```bash
python gomconfig.py create --preset python_like --output my_language.json
```

### 3. View Configuration

```bash
python gomconfig.py info my_language.json
```

### 4. Run Demo

```bash
python demo_create_new_languages.py
```

This creates 5 complete language variants:
- `demo_gulplisp.json` - Lisp-like
- `demo_gulfturtle.json` - Logo/Turtle graphics
- `demo_gulfql.json` - SQL-like
- `demo_gulfasm.json` - Assembly-like
- Plus CRUD operations demo

## Common Tasks

### Rename Keywords

```python
from gulfofmexico.language_config import LanguageConfig

config = LanguageConfig()
config.rename_keyword("if", "si")        # Spanish
config.rename_keyword("function", "defun")  # Lisp
config.save("my_lang.json")
```

### Add Custom Functions

```python
from gulfofmexico.language_config import LanguageConfig, FunctionConfig

config = LanguageConfig()
config.add_function("turtle_forward", FunctionConfig(
    name="turtle_forward",
    arity=1,
    description="Move turtle forward",
    enabled=True,
))
config.save("turtle_lang.json")
```

### Disable Satirical Features

```python
config = LanguageConfig()
config.disable_satirical_keywords()
config.save("serious_mode.json")
```

### Update Configuration

```bash
# Update via CLI
python gomconfig.py update my_lang.json \
    --set metadata.author "Your Name" \
    --set metadata.version "2.0" \
    --output my_lang_v2.json

# Merge two configurations
python gomconfig.py update my_lang.json \
    --merge other_lang.json \
    --output merged.json
```

### Delete Elements

```bash
# Delete keywords, functions, operators
python gomconfig.py delete my_lang.json \
    --keyword synergize \
    --function blockchain \
    --output cleaned.json
```

### Compare Configurations

```bash
python gomconfig.py diff config1.json config2.json
```

## Programmatic Usage

### Load Configuration

```python
from gulfofmexico.language_config import LanguageConfig

# From file
config = LanguageConfig.load("my_lang.json")

# From URL
config = LanguageConfig.load_from_url("https://example.com/lang.json")

# From preset
config = LanguageConfig.from_preset("python_like")
```

### Update Configuration

```python
# Update metadata
config.update({
    "metadata": {
        "author": "Alice",
        "version": "2.0",
    }
}, merge=True)

# Update syntax options
config.update({
    "syntax_options": {
        "array_start_index": 0,  # 0-based like Python
        "single_line_comment": "#",
    }
}, merge=True)
```

### CRUD Operations

```python
# Delete
config.delete_keyword("synergize")
config.delete_function("blockchain")

# Merge
other_config = LanguageConfig.load("other.json")
config.merge(other_config, prefer_other=True)

# Clone
backup = config.clone()

# Diff
differences = config.diff(other_config)
print(differences["keywords"]["added"])
```

### Deep Customization

```python
from gulfofmexico.language_config import ParsingConfig

config = LanguageConfig()

# Lisp-style parentheses everywhere
config.parsing_config = ParsingConfig(
    block_start="(",
    block_end=")",
    list_start="(",
    list_end=")",
    parameter_separator=" ",
)

# Python-style comments
config.update({
    "syntax_options": {
        "single_line_comment": "#",
    }
}, merge=True)

config.save("my_lisp.json")
```

## Real-World Examples

### Example 1: Spanish Gulf of Mexico

```python
config = LanguageConfig(
    name="GOM en Español",
    description="Gulf of Mexico en idioma español"
)

# Rename keywords
config.rename_keyword("if", "si")
config.rename_keyword("when", "cuando")
config.rename_keyword("function", "función")
config.rename_keyword("return", "retornar")
config.rename_keyword("var", "variable")

# Rename functions
config.rename_function("print", "imprimir")

config.save("gom_spanish.json")
```

### Example 2: Teaching Mode (Minimal)

```python
config = LanguageConfig(
    name="GOM for Teaching",
    description="Simplified version for beginners"
)

# Keep only essential keywords
essential = ["if", "function", "var", "return", "print", "input"]
all_keywords = list(config.keyword_mappings.keys())
for kw in all_keywords:
    if kw not in essential:
        config.delete_keyword(kw)

# Disable all special features
config.update({
    "syntax_options": {
        "enable_satirical_keywords": False,
        "enable_quantum_features": False,
        "enable_time_travel": False,
        "array_start_index": 0,  # 0-based for beginners
    }
}, merge=True)

config.save("teaching_mode.json")
```

### Example 3: Domain-Specific Language (Data Analysis)

```python
from gulfofmexico.language_config import FunctionConfig

config = LanguageConfig(
    name="DataGOM",
    description="Data analysis DSL"
)

# Add domain-specific functions
data_functions = [
    FunctionConfig("SELECT", -1, description="Select columns"),
    FunctionConfig("FILTER", 2, description="Filter rows"),
    FunctionConfig("GROUP_BY", 2, description="Group data"),
    FunctionConfig("AGGREGATE", -1, description="Aggregate data"),
    FunctionConfig("JOIN", 3, description="Join datasets"),
]

for func in data_functions:
    config.add_function(func.name, func)

# Use SQL-style syntax
config.update({
    "syntax_options": {
        "require_semicolons": True,
        "statement_terminator": ";",
    }
}, merge=True)

config.save("data_gom.json")
```

## CLI Reference

```bash
# Create
gomconfig create --preset PRESET --output FILE
gomconfig create --interactive

# View
gomconfig info FILE
gomconfig validate FILE
gomconfig list-presets

# Modify
gomconfig update FILE --set KEY VALUE [--output FILE]
gomconfig update FILE --merge OTHER_FILE [--output FILE]
gomconfig delete FILE --keyword KW --function FN [--output FILE]

# Compare
gomconfig diff FILE1 FILE2

# Export
gomconfig export FILE --format markdown|json|yaml [--output FILE]
gomconfig convert FILE --to json|yaml [--output FILE]
```

## Tips & Best Practices

### Start with a Preset
```bash
python gomconfig.py create --preset python_like --output my_lang.json
```
Then customize from there.

### Use JSON for No Dependencies
YAML requires `pyyaml`, but JSON works out of the box.

### Validate Early and Often
```bash
python gomconfig.py validate my_lang.json
```

### Clone Before Major Changes
```python
backup = config.clone()
# Make risky changes
if something_wrong:
    config = backup
```

### Use Diff to Review Changes
```bash
python gomconfig.py diff original.json modified.json
```

## Troubleshooting

### "Module not found: yaml"
Either install pyyaml (`pip install pyyaml`) or use JSON format instead.

### "Configuration file not found"
Use absolute paths or run from the project root.

### "Invalid configuration"
Run `python gomconfig.py validate FILE` to see specific errors.

### Changes don't apply
Make sure you're using the **Python interpreter**, not the C++ compiler:
```bash
python -m gulfofmexico script.gom --config my_lang.json
```

## Next Steps

1. **Try the demos**: `python demo_create_new_languages.py`
2. **Read full docs**: `LANGUAGE_CONSTRUCTION_SET.md`
3. **See enhanced features**: `LANGUAGE_CONSTRUCTION_ENHANCED.md`
4. **Experiment**: Create your own language variant!

## Examples to Try

```bash
# Create Spanish version
python gomconfig.py create --preset spanish --output spanish.json

# Create minimal teaching version
python gomconfig.py create --preset minimal --output teaching.json

# Customize existing preset
python gomconfig.py update spanish.json --set metadata.author "Your Name"

# Compare two variants
python gomconfig.py diff spanish.json french.json

# View what's in a config
python gomconfig.py info teaching.json
```

## Need Help?

- Full documentation: `LANGUAGE_CONSTRUCTION_SET.md`
- Enhanced features: `LANGUAGE_CONSTRUCTION_ENHANCED.md`
- Quick reference: `LANGUAGE_CONSTRUCTION_QUICKREF.md`
- Examples: `demo_create_new_languages.py`
- Compiler status: `compiler/EXPERIMENTAL_STATUS.md`

## Remember

✅ Works with **Python interpreter** (full customization)
❌ Does NOT work with C++ compiler (experimental, fixed syntax)

For language customization, always use:
```bash
python -m gulfofmexico script.gom --config your_config.json
```
