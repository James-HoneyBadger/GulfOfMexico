# Language Construction Set - Quick Reference

## One-Line Usage

```bash
# Presets
python -m gulfofmexico --preset python_like script.gom
python -m gulfofmexico --preset serious script.gom
python -m gulfofmexico --preset spanish script.gom

# Custom config
python -m gulfofmexico --config my_config.yaml script.gom

# Environment variable
export GULFOFMEXICO_CONFIG=my_config.yaml
python -m gulfofmexico script.gom
```

## Configuration Management

```bash
# Create
python gomconfig.py create --preset python_like
python gomconfig.py create --interactive

# Validate
python gomconfig.py validate config.yaml

# Info
python gomconfig.py info config.yaml

# Export
python gomconfig.py export config.yaml --format markdown

# Compare
python gomconfig.py diff config1.yaml config2.yaml
```

## Programmatic API

### Basic Customization

```python
from gulfofmexico.language_config import LanguageConfig

config = LanguageConfig()

# Rename keywords
config.rename_keyword("if", "si")
config.rename_keyword("function", "def")

# Rename functions
config.rename_function("print", "imprimir")

# Array indexing
config.set_array_indexing(0, False)  # 0-based, no fractional

# Comment style
config.set_comment_style("#")

# Features
config.enable_feature("satirical", False)
config.disable_satirical_keywords()

# Save
config.save("my_config.yaml")
```

### Using Presets

```python
# Load preset
config = LanguageConfig.from_preset("python_like")

# Modify and save
config.rename_keyword("class", "blueprint")
config.save("my_variant.yaml")
```

### Runtime Integration

```python
from gulfofmexico.language_runtime import LanguageRuntime

# Load config
LanguageRuntime.load_config(config)

# Query
is_enabled = LanguageRuntime.is_feature_enabled("satirical")
start_idx = LanguageRuntime.get_array_start_index()
info = LanguageRuntime.get_info()

# Reset
LanguageRuntime.reset()
```

## Common Customizations

### Serious Mode (No Satire)

```python
config = LanguageConfig()
config.disable_satirical_keywords()
config.enable_feature("satirical", False)
config.enable_feature("quantum", False)
config.enable_feature("time_travel", False)
config.save("serious.yaml")
```

### Teaching Mode (Minimal)

```python
config = LanguageConfig()

# Keep only: if, function, return, var, const, class
essential = {"if", "function", "return", "var", "const", "class"}
for kw in list(config.keyword_mappings.keys()):
    if kw not in essential:
        config.remove_keyword(kw)

# Keep only: print, Number, String, Boolean, List
essential_funcs = {"print", "Number", "String", "Boolean", "List"}
for fn in list(config.builtin_functions.keys()):
    if fn not in essential_funcs:
        config.remove_function(fn)

config.set_array_indexing(0, False)
config.enable_feature("three_valued_logic", False)
config.save("teaching.yaml")
```

### Internationalization (Spanish)

```python
config = LanguageConfig()

# Keywords
translations = {
    "if": "si",
    "when": "cuando",
    "function": "función",
    "return": "retornar",
    "class": "clase"
}
for orig, trans in translations.items():
    config.rename_keyword(orig, trans)

# Functions
config.rename_function("print", "imprimir")
config.rename_function("read", "leer")

config.save("spanish.yaml")
```

## Configuration File Format

### Minimal YAML Example

```yaml
metadata:
  name: "My Language"
  version: "1.0.0"

keywords:
  if:
    original: "if"
    custom: "when"
    category: "control"
    description: "Conditional"

syntax_options:
  array_start_index: 0
  enable_satirical_keywords: false
```

### Minimal JSON Example

```json
{
  "metadata": {
    "name": "My Language",
    "version": "1.0.0"
  },
  "keywords": {
    "if": {
      "original": "if",
      "custom": "when",
      "category": "control",
      "description": "Conditional"
    }
  },
  "syntax_options": {
    "array_start_index": 0,
    "enable_satirical_keywords": false
  }
}
```

## Preset Comparison

| Feature | Default | python_like | serious | minimal |
|---------|---------|-------------|---------|---------|
| function keyword | `function` | `def` | `function` | `function` |
| Array start | `-1` | `0` | `-1` | `0` |
| Fractional indexing | ✓ | ✗ | ✓ | ✗ |
| Satirical keywords | ✓ | ✗ | ✗ | ✗ |
| Quantum features | ✓ | ✗ | ✗ | ✗ |
| 3-valued logic | ✓ | ✓ | ✓ | ✗ |
| Probabilistic vars | ✓ | ✓ | ✓ | ✗ |
| Comment style | `//` | `#` | `//` | `//` |
| Semicolons | ✗ | ✗ | ✗ | ✗ |

## Validation Checklist

✓ No duplicate custom keyword names  
✓ Function arities >= -1  
✓ Operator precedences >= 0  
✓ Valid associativity (left/right/none)  
✓ Required metadata fields present  

## Troubleshooting

**Problem:** Config not loading  
**Solution:** Check file format (YAML requires pyyaml: `pip install pyyaml`)

**Problem:** Validation errors  
**Solution:** Run `python gomconfig.py validate config.yaml` for details

**Problem:** Features not working  
**Solution:** Check runtime is loaded: `LanguageRuntime.get_info()`

**Problem:** YAML not available  
**Solution:** Install pyyaml OR use JSON format instead

## Links

- [Full Documentation](LANGUAGE_CONSTRUCTION_SET.md)
- [Example Configs](configs/)
- [Interactive Demo](demo_language_construction_set.py)
