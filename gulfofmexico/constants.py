"""
Constants for Gulf of Mexico Interpreter

Defines global constants used throughout the interpreter.

Variable System:
    - MAX_CONFIDENCE: Maximum confidence level for variables
    - DEFAULT_CONFIDENCE: Default when no ! modifiers specified
    - INFINITE_LIFETIME: Effectively infinite line count

File Storage:
    - DB_RUNTIME_PATH: Directory for runtime data (~/.gulfofmexico_runtime)
    - DB_IMMUTABLE_CONSTANTS_PATH: File listing immutable globals
    - DB_IMMUTABLE_CONSTANTS_VALUES_PATH: Directory storing global values
    - DB_VAR_TO_VALUE_SEP: Separator for serialized data (";;;")

GitHub Integration:
    - GITHUB_GLOBAL_VARS_REPO: Repository for public globals (unused)
    - GITHUB_GLOBAL_VARS_LABEL: Label for global variable issues (unused)

Note: GitHub integration for public globals exists but the actual
implementation uses a patched repository URL in interpreter.py.

Precision:
    - FLOAT_COMPARISON_EPSILON: Tolerance for float equality (1e-10)

Experimental Cache Settings (unused in production):
    - EXPRESSION_CACHE_SIZE: Max cached expressions
    - NAMESPACE_CACHE_SIZE: Max cached namespaces
"""

# Variable confidence and lifetime values
MAX_CONFIDENCE = 100000000000
DEFAULT_CONFIDENCE = 0
INFINITE_LIFETIME = 100000000000

# File storage paths for persistent variables
DB_RUNTIME_PATH = ".gulfofmexico_runtime"
DB_IMMUTABLE_CONSTANTS_PATH = ".immutable_constants"
DB_IMMUTABLE_CONSTANTS_VALUES_PATH = ".immutable_constants_values"
DB_VAR_TO_VALUE_SEP = ";;;"

# GitHub integration (experimental, not actively used)
GITHUB_GLOBAL_VARS_REPO = "GulfOfMexico/GulfOfMexico-Public-Variables"
GITHUB_GLOBAL_VARS_LABEL = "global variable"

# Precision settings
FLOAT_COMPARISON_EPSILON = 1e-10

# Cache settings (experimental, not used in production interpreter)
EXPRESSION_CACHE_SIZE = 1000
NAMESPACE_CACHE_SIZE = 500
