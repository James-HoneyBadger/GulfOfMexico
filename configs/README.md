# Gulf of Mexico Language Configurations

This directory contains preset language configurations for Gulf of Mexico.

## Available Configurations

### `python_like.yaml`
Python-style syntax variant:
- `def` instead of `function`
- 0-based array indexing
- `#` for comments
- No satirical features

**Use when:** You want familiar Python-like syntax

**Example:**
```bash
python -m gulfofmexico --preset python_like myprogram.gom
```

### `spanish_professional.yaml`
Professional mode with Spanish keywords:
- `si` (if), `cuando` (when), `función` (function)
- `imprimir` (print), `leer` (read), `escribir` (write)
- No satirical features
- Gulf of Mexico's unique features intact

**Use when:** You want a serious, professional Spanish variant

**Example:**
```bash
python -m gulfofmexico --config configs/spanish_professional.yaml programa.gom
```

### `minimal.json`
Minimal feature set for teaching:
- Only essential keywords: if, function, return, const, var, class
- Only essential functions: print, Number, String, Boolean, List
- No special features (quantum, time travel, satirical, etc.)
- 0-based indexing
- Strict mode enabled

**Use when:** Teaching programming basics without distractions

**Example:**
```bash
python -m gulfofmexico --config configs/minimal.json lesson1.gom
```

## Creating Your Own Configuration

### Method 1: Start from Preset

```bash
# Copy a preset and modify it
cp configs/python_like.yaml my_config.yaml
# Edit my_config.yaml in your favorite editor
```

### Method 2: Use the CLI Tool

```bash
# Create interactively
python gomconfig.py create --interactive

# Create from preset and modify
python gomconfig.py create --preset python_like --output my_config.yaml
python gomconfig.py edit my_config.yaml
```

### Method 3: Programmatic

```python
from gulfofmexico.language_config import LanguageConfig

config = LanguageConfig.from_preset("python_like")
config.rename_keyword("class", "blueprint")
config.add_function("log", arity=-1, description="Logging")
config.save("configs/my_variant.yaml")
```

## Using Configurations

### Command Line

```bash
# Specific config file
python -m gulfofmexico --config configs/python_like.yaml script.gom

# Use preset name
python -m gulfofmexico --preset python_like script.gom

# Serious mode shortcut
python -m gulfofmexico --serious-mode script.gom
```

### Environment Variable

```bash
export GULFOFMEXICO_CONFIG=configs/spanish_professional.yaml
python -m gulfofmexico programa.gom
```

### Project Config

Create `.gomconfig` in your project directory - it will be automatically loaded:

```yaml
# .gomconfig
metadata:
  name: "My Project Config"

keywords:
  if:
    original: "if"
    custom: "when"
  # ... more customizations
```

## Validating Configurations

```bash
# Validate a config file
python gomconfig.py validate configs/python_like.yaml

# Show detailed info
python gomconfig.py info configs/spanish_professional.yaml
```

## Comparing Configurations

```bash
# See differences between two configs
python gomconfig.py diff configs/python_like.yaml configs/minimal.json
```

## Exporting Documentation

```bash
# Export mapping table as markdown
python gomconfig.py export configs/python_like.yaml --format markdown

# Convert between formats
python gomconfig.py convert configs/python_like.yaml --to json
```

## Configuration File Format

Both YAML and JSON are supported. YAML is recommended for readability.

### Basic Structure

```yaml
metadata:
  name: "My Language Variant"
  version: "1.0.0"
  description: "Description"
  author: "Your Name"

keywords:
  keyword_name:
    original: "original_keyword"
    custom: "custom_keyword"
    category: "category"
    description: "Description"

functions:
  function_name:
    name: "custom_name"
    arity: 1  # or -1 for variadic
    implementation: "python.reference"
    description: "Description"
    enabled: true

operators:
  "+":
    symbol: "+"
    precedence: 10
    associativity: "left"
    enabled: true

syntax_options:
  array_start_index: -1  # or 0
  allow_fractional_indexing: true
  # ... more options

runtime:
  debug_mode: false
  strict_mode: false
  compatibility_mode: "standard"
```

See [docs/language/LANGUAGE_CONSTRUCTION_SET.md](../docs/language/LANGUAGE_CONSTRUCTION_SET.md) for complete documentation.

## Contributing

Want to add a preset configuration?

1. Create your configuration file
2. Test it thoroughly
3. Add documentation here
4. Submit a pull request

### Preset Naming Convention

- `{language}_like.yaml` - Syntax variants (python_like, js_like)
- `{language}_{mode}.yaml` - Internationalization (spanish_professional, french_casual)
- `{purpose}.yaml` - Purpose-specific (teaching, minimal, datascience)

## License

Same as Gulf of Mexico - see LICENSE file.
