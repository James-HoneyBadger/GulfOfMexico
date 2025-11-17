"""
Gulf of Mexico Language Construction Set

This module provides a comprehensive configuration system that allows users to:
    - Rename commands and keywords
    - Add/remove/modify built-in functions
    - Customize syntax options and operators
    - Create language variants and dialects
    - Export/import language configurations

Features:
    - YAML/JSON configuration files for easy editing
    - Hot-reloading of language definitions
    - Validation of configuration consistency
    - Backwards compatibility mode
    - Language preset library (Python-like, JavaScript-like, etc.)

Usage:
    # Create a custom language variant
    config = LanguageConfig()
    config.rename_keyword("if", "si")  # Spanish-like
    config.rename_keyword("when", "cuando")
    config.add_builtin_function("imprimir", lambda x: print(x))
    config.save("spanish_gom.yaml")

    # Use in interpreter
    run_file("myprogram.gom", language_config="spanish_gom.yaml")
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Callable, Optional, Union
from dataclasses import dataclass, field, asdict
from copy import deepcopy

# Optional YAML support
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    yaml = None


@dataclass
class KeywordMapping:
    """Maps original keyword to custom name."""

    original: str
    custom: str
    category: str = "general"  # general, control, function, satirical, etc.
    description: str = ""


@dataclass
class FunctionConfig:
    """Configuration for a built-in function."""

    name: str
    arity: int  # Number of arguments (-1 for variadic)
    implementation: Optional[str] = None  # Python code as string, or reference
    description: str = ""
    enabled: bool = True


@dataclass
class OperatorConfig:
    """Configuration for operators."""

    symbol: str
    precedence: int
    associativity: str = "left"  # left, right, none
    enabled: bool = True


@dataclass
class ParsingConfig:
    """Deep parsing and syntax customization.

    This allows creating entirely new language syntaxes.
    """

    # Delimiters
    block_start: str = "{"
    block_end: str = "}"
    list_start: str = "["
    list_end: str = "]"
    tuple_start: str = "("
    tuple_end: str = ")"
    dict_start: str = "{"
    dict_end: str = "}"

    # Separators
    statement_separator: str = ";"  # or newline
    parameter_separator: str = ","
    key_value_separator: str = ":"

    # String literals
    string_delimiters: list[str] = field(default_factory=lambda: ['"', "'", '"""'])
    escape_character: str = "\\"
    allow_raw_strings: bool = True
    raw_string_prefix: str = "r"

    # Expression syntax
    member_access: str = "."  # e.g., obj.property
    index_access_start: str = "["
    index_access_end: str = "]"
    function_call_start: str = "("
    function_call_end: str = ")"

    # Control flow syntax
    if_then_separator: Optional[str] = (
        None  # None means block-based, "then" for keyword
    )
    else_keyword: str = "else"
    elif_keyword: str = "elif"

    # Function definition syntax
    function_param_start: str = "("
    function_param_end: str = ")"
    function_arrow: Optional[str] = None  # "->" for arrow functions
    return_type_separator: Optional[str] = None  # ":" for type annotations

    # Class definition syntax
    class_inheritance_separator: str = ":"  # class Foo : Bar
    class_body_start: str = "{"
    class_body_end: str = "}"

    # Import/Export syntax
    import_separator: str = "."  # import foo.bar
    from_keyword: str = "from"
    as_keyword: str = "as"

    # Custom parse transforms
    allow_custom_operators: bool = True
    allow_operator_overloading: bool = True


@dataclass
class SyntaxOptions:
    """General syntax configuration options."""

    # Array indexing
    array_start_index: int = -1  # Gulf of Mexico's signature -1 indexing
    allow_fractional_indexing: bool = True

    # String quoting
    flexible_quoting: bool = True  # Gulf of Mexico's unique quote counting
    string_interpolation: bool = True
    interpolation_symbol: str = "$"

    # Comments
    single_line_comment: str = "//"
    multi_line_comment_start: Optional[str] = None
    multi_line_comment_end: Optional[str] = None

    # Statement terminators
    require_semicolons: bool = False
    statement_terminator: str = "!"  # Gulf of Mexico uses ! or newline

    # Type system
    three_valued_logic: bool = True  # true/false/maybe
    probabilistic_variables: bool = True
    temporal_variables: bool = True

    # Special features
    enable_satirical_keywords: bool = True
    enable_quantum_features: bool = True
    enable_time_travel: bool = True
    enable_gaslighting: bool = True


@dataclass
class LanguageConfig:
    """Complete language configuration.

    This class provides a comprehensive way to customize Gulf of Mexico's
    syntax, keywords, functions, and behavior.

    INTERPRETER-ONLY SCOPE:
    This configuration system applies ONLY to the Python-based interpreter.
    The C++ compiler (gomcc) is an experimental system with its own build process.
    """

    # Metadata
    name: str = "Gulf of Mexico"
    version: str = "1.0.0"
    description: str = "A customizable programming language"
    author: str = ""
    target_interpreter: str = (
        "python"  # Only affects Python interpreter, not C++ compiler
    )

    # Configuration sections
    keyword_mappings: dict[str, KeywordMapping] = field(default_factory=dict)
    builtin_functions: dict[str, FunctionConfig] = field(default_factory=dict)
    operators: dict[str, OperatorConfig] = field(default_factory=dict)
    syntax_options: SyntaxOptions = field(default_factory=SyntaxOptions)
    parsing_config: ParsingConfig = field(default_factory=ParsingConfig)

    # Runtime options
    debug_mode: bool = False
    strict_mode: bool = False  # Enforce stricter type checking
    compatibility_mode: str = "standard"  # standard, legacy, experimental

    def __post_init__(self):
        """Initialize with default Gulf of Mexico configuration."""
        if not self.keyword_mappings:
            self._load_default_keywords()
        if not self.builtin_functions:
            self._load_default_functions()
        if not self.operators:
            self._load_default_operators()

    def _load_default_keywords(self):
        """Load default Gulf of Mexico keywords."""
        default_keywords = {
            # Control flow
            "if": KeywordMapping("if", "if", "control", "Conditional statement"),
            "when": KeywordMapping("when", "when", "control", "Reactive programming"),
            "after": KeywordMapping("after", "after", "control", "Temporal execution"),
            # Functions
            "function": KeywordMapping(
                "function", "function", "function", "Function definition"
            ),
            "async": KeywordMapping("async", "async", "function", "Async function"),
            "await": KeywordMapping("await", "await", "function", "Await async result"),
            "return": KeywordMapping("return", "return", "function", "Return value"),
            # Variables
            "const": KeywordMapping(
                "const", "const", "variable", "Constant declaration"
            ),
            "var": KeywordMapping("var", "var", "variable", "Variable declaration"),
            # Classes
            "class": KeywordMapping("class", "class", "oop", "Class definition"),
            "className": KeywordMapping(
                "className", "className", "oop", "Alternative class keyword"
            ),
            # Special
            "delete": KeywordMapping("delete", "delete", "special", "Delete variable"),
            "reverse": KeywordMapping(
                "reverse", "reverse", "special", "Reverse operation"
            ),
            "export": KeywordMapping("export", "export", "module", "Export to file"),
            "import": KeywordMapping("import", "import", "module", "Import from file"),
            "previous": KeywordMapping(
                "previous", "previous", "special", "Previous value"
            ),
            "next": KeywordMapping("next", "next", "special", "Next value"),
            # Error handling
            "try": KeywordMapping("try", "try", "error", "Try block"),
            "whatever": KeywordMapping("whatever", "whatever", "error", "Catch-all"),
            # Satirical - Procrastination
            "later": KeywordMapping(
                "later", "later", "satirical", "Execute later (maybe)"
            ),
            "eventually": KeywordMapping(
                "eventually", "eventually", "satirical", "Execute eventually"
            ),
            "whenever": KeywordMapping(
                "whenever", "whenever", "satirical", "Execute whenever"
            ),
            # Satirical - Corporate
            "synergize": KeywordMapping(
                "synergize", "synergize", "satirical", "Corporate synergy"
            ),
            "leverage": KeywordMapping(
                "leverage", "leverage", "satirical", "Leverage resources"
            ),
            "paradigm_shift": KeywordMapping(
                "paradigm_shift", "paradigm_shift", "satirical", "Shift paradigm"
            ),
            "circle_back": KeywordMapping(
                "circle_back", "circle_back", "satirical", "Circle back later"
            ),
            "touch_base": KeywordMapping(
                "touch_base", "touch_base", "satirical", "Touch base"
            ),
            # Satirical - Emotional
            "happy": KeywordMapping(
                "happy", "happy", "satirical", "Execute when happy"
            ),
            "sad": KeywordMapping("sad", "sad", "satirical", "Execute when sad"),
            "angry": KeywordMapping(
                "angry", "angry", "satirical", "Execute when angry"
            ),
            "excited": KeywordMapping(
                "excited", "excited", "satirical", "Execute when excited"
            ),
            "tired": KeywordMapping(
                "tired", "tired", "satirical", "Execute when tired"
            ),
            # Satirical - Superstitious
            "lucky": KeywordMapping("lucky", "lucky", "satirical", "Lucky execution"),
            "unlucky": KeywordMapping(
                "unlucky", "unlucky", "satirical", "Unlucky execution"
            ),
            "cross_fingers": KeywordMapping(
                "cross_fingers", "cross_fingers", "satirical", "Cross fingers"
            ),
            "knock_on_wood": KeywordMapping(
                "knock_on_wood", "knock_on_wood", "satirical", "Knock on wood"
            ),
            # Satirical - Quantum/Blockchain/AI
            "quantum": KeywordMapping(
                "quantum", "quantum", "satirical", "Quantum computing"
            ),
            "blockchain": KeywordMapping(
                "blockchain", "blockchain", "satirical", "Blockchain technology"
            ),
            "immutable_ledger": KeywordMapping(
                "immutable_ledger", "immutable_ledger", "satirical", "Immutable ledger"
            ),
            "smart_contract": KeywordMapping(
                "smart_contract", "smart_contract", "satirical", "Smart contract"
            ),
            "mine": KeywordMapping("mine", "mine", "satirical", "Mine cryptocurrency"),
            "deep_learning": KeywordMapping(
                "deep_learning", "deep_learning", "satirical", "Deep learning"
            ),
            "neural_network": KeywordMapping(
                "neural_network", "neural_network", "satirical", "Neural network"
            ),
            "ai_powered": KeywordMapping(
                "ai_powered", "ai_powered", "satirical", "AI powered"
            ),
            # Satirical - Agile/DevOps/Startup
            "sprint": KeywordMapping("sprint", "sprint", "satirical", "Agile sprint"),
            "standup": KeywordMapping(
                "standup", "standup", "satirical", "Daily standup"
            ),
            "retro": KeywordMapping("retro", "retro", "satirical", "Retrospective"),
            "burndown": KeywordMapping(
                "burndown", "burndown", "satirical", "Burndown chart"
            ),
            "encrypt": KeywordMapping(
                "encrypt", "encrypt", "satirical", "Encrypt data"
            ),
            "two_factor": KeywordMapping(
                "two_factor", "two_factor", "satirical", "Two-factor auth"
            ),
            "penetration_test": KeywordMapping(
                "penetration_test", "penetration_test", "satirical", "Pen test"
            ),
            "zero_trust": KeywordMapping(
                "zero_trust", "zero_trust", "satirical", "Zero trust"
            ),
            "containerize": KeywordMapping(
                "containerize", "containerize", "satirical", "Containerize app"
            ),
            "orchestrate": KeywordMapping(
                "orchestrate", "orchestrate", "satirical", "Orchestrate services"
            ),
            "microservice": KeywordMapping(
                "microservice", "microservice", "satirical", "Microservice"
            ),
            "kubernetes": KeywordMapping(
                "kubernetes", "kubernetes", "satirical", "Kubernetes"
            ),
            "pivot": KeywordMapping("pivot", "pivot", "satirical", "Business pivot"),
            "disrupt": KeywordMapping(
                "disrupt", "disrupt", "satirical", "Disrupt industry"
            ),
            "unicorn": KeywordMapping(
                "unicorn", "unicorn", "satirical", "Unicorn startup"
            ),
            "hockey_stick": KeywordMapping(
                "hockey_stick", "hockey_stick", "satirical", "Hockey stick growth"
            ),
            # Special features
            "definitely_not": KeywordMapping(
                "definitely_not", "definitely_not", "special", "Gaslighting"
            ),
        }
        self.keyword_mappings = default_keywords

    def _load_default_functions(self):
        """Load default built-in functions."""
        default_functions = {
            # I/O
            "print": FunctionConfig("print", -1, "builtin.db_print", "Print to stdout"),
            "read": FunctionConfig("read", 0, "builtin.db_read", "Read from stdin"),
            "write": FunctionConfig("write", 2, "builtin.db_write", "Write to file"),
            # Type conversions
            "Number": FunctionConfig(
                "Number", 1, "builtin.db_to_number", "Convert to number"
            ),
            "String": FunctionConfig(
                "String", 1, "builtin.db_to_string", "Convert to string"
            ),
            "Boolean": FunctionConfig(
                "Boolean", 1, "builtin.db_to_boolean", "Convert to boolean"
            ),
            # Data structures
            "List": FunctionConfig(
                "List", -1, "builtin.GulfOfMexicoList", "Create list"
            ),
            "Map": FunctionConfig("Map", 0, "builtin.GulfOfMexicoMap", "Create map"),
            # Utilities
            "sleep": FunctionConfig(
                "sleep", 1, "builtin.db_sleep", "Sleep for seconds"
            ),
            "exit": FunctionConfig("exit", 0, "builtin.db_exit", "Exit program"),
            "use": FunctionConfig("use", 1, "builtin.db_use", "Create reactive signal"),
            "new": FunctionConfig("new", -1, "builtin.db_new", "Instantiate class"),
            # Math functions (subset)
            "sin": FunctionConfig("sin", 1, "math.sin", "Sine function"),
            "cos": FunctionConfig("cos", 1, "math.cos", "Cosine function"),
            "tan": FunctionConfig("tan", 1, "math.tan", "Tangent function"),
            "sqrt": FunctionConfig("sqrt", 1, "math.sqrt", "Square root"),
            "abs": FunctionConfig("abs", 1, "builtin.db_abs", "Absolute value"),
            "floor": FunctionConfig("floor", 1, "math.floor", "Floor function"),
            "ceil": FunctionConfig("ceil", 1, "math.ceil", "Ceiling function"),
            "round": FunctionConfig("round", 1, "builtin.db_round", "Round to nearest"),
            "min": FunctionConfig("min", 2, "builtin.db_min", "Minimum of two values"),
            "max": FunctionConfig("max", 2, "builtin.db_max", "Maximum of two values"),
            "random": FunctionConfig(
                "random", 0, "builtin.db_random", "Random number [0,1)"
            ),
            # String functions
            "length": FunctionConfig("length", 1, "builtin.db_len", "Get length"),
            "split": FunctionConfig("split", 2, "builtin.db_split", "Split string"),
            "join": FunctionConfig("join", 2, "builtin.db_join", "Join list"),
            "replace": FunctionConfig(
                "replace", 3, "builtin.db_replace", "Replace substring"
            ),
            # List functions
            "push": FunctionConfig("push", 2, "builtin.db_list_push", "Add to end"),
            "pop": FunctionConfig("pop", 1, "builtin.db_list_pop", "Remove from end"),
            "slice": FunctionConfig("slice", 3, "builtin.db_slice", "Slice sequence"),
            "sort": FunctionConfig("sort", 1, "builtin.db_sort", "Sort list"),
            "reverse_list": FunctionConfig(
                "reverse_list", 1, "builtin.db_reverse_list", "Reverse list"
            ),
            # Regex
            "regex_match": FunctionConfig(
                "regex_match", 2, "builtin.db_regex_match", "Match regex"
            ),
            "regex_findall": FunctionConfig(
                "regex_findall", 2, "builtin.db_regex_findall", "Find all matches"
            ),
            "regex_replace": FunctionConfig(
                "regex_replace", 3, "builtin.db_regex_replace", "Replace with regex"
            ),
        }
        self.builtin_functions = default_functions

    def _load_default_operators(self):
        """Load default operators with precedence."""
        default_operators = {
            # Arithmetic
            "+": OperatorConfig("+", 10, "left"),
            "-": OperatorConfig("-", 10, "left"),
            "*": OperatorConfig("*", 20, "left"),
            "/": OperatorConfig("/", 20, "left"),
            "^": OperatorConfig("^", 30, "right"),
            # Comparison
            "==": OperatorConfig("==", 5, "none"),
            "===": OperatorConfig("===", 5, "none"),
            "====": OperatorConfig("====", 5, "none"),
            "~=": OperatorConfig("~=", 5, "none"),  # Approximate equality
            ";=": OperatorConfig(";=", 5, "none"),  # Not equal
            ">": OperatorConfig(">", 5, "none"),
            "<": OperatorConfig("<", 5, "none"),
            ">=": OperatorConfig(">=", 5, "none"),
            "<=": OperatorConfig("<=", 5, "none"),
            # Logical
            "&": OperatorConfig("&", 3, "left"),
            "|": OperatorConfig("|", 2, "left"),
            "!": OperatorConfig("!", 40, "right"),
            # Assignment
            "=": OperatorConfig("=", 1, "right"),
            # Other
            ".": OperatorConfig(".", 50, "left"),  # Member access
            "++": OperatorConfig("++", 40, "none"),  # Increment
            "--": OperatorConfig("--", 40, "none"),  # Decrement
        }
        self.operators = default_operators

    # === Keyword Management ===

    def rename_keyword(self, original: str, new_name: str) -> None:
        """Rename a keyword.

        Args:
            original: Original keyword name
            new_name: New custom name

        Raises:
            ValueError: If original keyword doesn't exist
        """
        if original not in self.keyword_mappings:
            raise ValueError(f"Keyword '{original}' not found")

        self.keyword_mappings[original].custom = new_name

    def add_keyword(
        self, name: str, category: str = "custom", description: str = ""
    ) -> None:
        """Add a new custom keyword.

        Args:
            name: Keyword name
            category: Category (control, function, satirical, etc.)
            description: Description of the keyword
        """
        self.keyword_mappings[name] = KeywordMapping(name, name, category, description)

    def remove_keyword(self, name: str) -> None:
        """Remove a keyword.

        Args:
            name: Keyword to remove

        Raises:
            ValueError: If keyword doesn't exist
        """
        if name not in self.keyword_mappings:
            raise ValueError(f"Keyword '{name}' not found")

        del self.keyword_mappings[name]

    def disable_satirical_keywords(self) -> None:
        """Disable all satirical keywords (for serious mode)."""
        # Create list of satirical keywords to remove (avoid modifying dict during iteration)
        satirical_keywords = [
            keyword
            for keyword, mapping in self.keyword_mappings.items()
            if mapping.category == "satirical"
        ]
        for keyword in satirical_keywords:
            self.remove_keyword(keyword)
        self.syntax_options.enable_satirical_keywords = False

    def get_keyword_by_category(self, category: str) -> list[str]:
        """Get all keywords in a category.

        Args:
            category: Category name

        Returns:
            List of keyword names in that category
        """
        return [
            kw
            for kw, mapping in self.keyword_mappings.items()
            if mapping.category == category
        ]

    # === Function Management ===

    def add_function(
        self,
        name: str,
        arity: int,
        implementation: Optional[str] = None,
        description: str = "",
    ) -> None:
        """Add a custom built-in function.

        Args:
            name: Function name
            arity: Number of arguments (-1 for variadic)
            implementation: Python code or reference
            description: Function description
        """
        self.builtin_functions[name] = FunctionConfig(
            name, arity, implementation, description, True
        )

    def rename_function(self, original: str, new_name: str) -> None:
        """Rename a built-in function.

        Args:
            original: Original function name
            new_name: New function name

        Raises:
            ValueError: If function doesn't exist
        """
        if original not in self.builtin_functions:
            raise ValueError(f"Function '{original}' not found")

        func_config = self.builtin_functions[original]
        del self.builtin_functions[original]
        func_config.name = new_name
        self.builtin_functions[new_name] = func_config

    def disable_function(self, name: str) -> None:
        """Disable a built-in function.

        Args:
            name: Function name

        Raises:
            ValueError: If function doesn't exist
        """
        if name not in self.builtin_functions:
            raise ValueError(f"Function '{name}' not found")

        self.builtin_functions[name].enabled = False

    def remove_function(self, name: str) -> None:
        """Remove a built-in function.

        Args:
            name: Function name

        Raises:
            ValueError: If function doesn't exist
        """
        if name not in self.builtin_functions:
            raise ValueError(f"Function '{name}' not found")

        del self.builtin_functions[name]

    # === Operator Management ===

    def add_operator(
        self, symbol: str, precedence: int, associativity: str = "left"
    ) -> None:
        """Add a custom operator.

        Args:
            symbol: Operator symbol
            precedence: Precedence level (higher = tighter binding)
            associativity: left, right, or none
        """
        self.operators[symbol] = OperatorConfig(symbol, precedence, associativity, True)

    def remove_operator(self, symbol: str) -> None:
        """Remove an operator.

        Args:
            symbol: Operator symbol

        Raises:
            ValueError: If operator doesn't exist
        """
        if symbol not in self.operators:
            raise ValueError(f"Operator '{symbol}' not found")

        del self.operators[symbol]

    def change_operator_precedence(self, symbol: str, new_precedence: int) -> None:
        """Change operator precedence.

        Args:
            symbol: Operator symbol
            new_precedence: New precedence level

        Raises:
            ValueError: If operator doesn't exist
        """
        if symbol not in self.operators:
            raise ValueError(f"Operator '{symbol}' not found")

        self.operators[symbol].precedence = new_precedence

    # === Syntax Options ===

    def set_array_indexing(
        self, start_index: int, allow_fractional: bool = True
    ) -> None:
        """Configure array indexing behavior.

        Args:
            start_index: Starting index (0 for traditional, -1 for Gulf of Mexico)
            allow_fractional: Allow fractional indices
        """
        self.syntax_options.array_start_index = start_index
        self.syntax_options.allow_fractional_indexing = allow_fractional

    def set_comment_style(
        self,
        single_line: str = "//",
        multi_start: Optional[str] = None,
        multi_end: Optional[str] = None,
    ) -> None:
        """Configure comment syntax.

        Args:
            single_line: Single-line comment prefix
            multi_start: Multi-line comment start
            multi_end: Multi-line comment end
        """
        self.syntax_options.single_line_comment = single_line
        self.syntax_options.multi_line_comment_start = multi_start
        self.syntax_options.multi_line_comment_end = multi_end

    def enable_feature(self, feature: str, enabled: bool = True) -> None:
        """Enable or disable special language features.

        Args:
            feature: Feature name (satirical, quantum, time_travel, etc.)
            enabled: Whether to enable
        """
        feature_map = {
            "satirical": "enable_satirical_keywords",
            "quantum": "enable_quantum_features",
            "time_travel": "enable_time_travel",
            "gaslighting": "enable_gaslighting",
            "three_valued_logic": "three_valued_logic",
            "probabilistic": "probabilistic_variables",
            "temporal": "temporal_variables",
        }

        if feature in feature_map:
            setattr(self.syntax_options, feature_map[feature], enabled)
        else:
            raise ValueError(f"Unknown feature: {feature}")

    # === Presets ===

    @classmethod
    def from_preset(cls, preset_name: str) -> LanguageConfig:
        """Load a preset language configuration.

        Args:
            preset_name: Preset name (python_like, js_like, serious, minimal, etc.)

        Returns:
            Configured LanguageConfig
        """
        config = cls()

        if preset_name == "python_like":
            config.name = "Gulf of Mexico (Python-like)"
            config.rename_keyword("function", "def")
            config.set_array_indexing(0, False)  # 0-based, no fractional
            config.syntax_options.statement_terminator = ""
            config.syntax_options.require_semicolons = False
            config.disable_satirical_keywords()

        elif preset_name == "js_like":
            config.name = "Gulf of Mexico (JavaScript-like)"
            config.set_array_indexing(0, False)
            config.syntax_options.statement_terminator = ";"
            config.syntax_options.require_semicolons = True
            config.disable_satirical_keywords()

        elif preset_name == "serious":
            config.name = "Gulf of Mexico (Serious Mode)"
            config.description = "Professional mode without satirical features"
            config.disable_satirical_keywords()
            config.enable_feature("satirical", False)
            config.enable_feature("quantum", False)
            config.enable_feature("time_travel", False)
            config.enable_feature("gaslighting", False)

        elif preset_name == "minimal":
            config.name = "Gulf of Mexico (Minimal)"
            config.description = "Minimal feature set"
            config.disable_satirical_keywords()
            config.enable_feature("satirical", False)
            config.enable_feature("quantum", False)
            config.enable_feature("time_travel", False)
            config.enable_feature("gaslighting", False)
            config.enable_feature("probabilistic", False)
            config.enable_feature("temporal", False)
            # Remove most built-in functions except essentials
            essential = {"print", "Number", "String", "Boolean", "List"}
            for func_name in list(config.builtin_functions.keys()):
                if func_name not in essential:
                    config.remove_function(func_name)

        elif preset_name == "spanish":
            config.name = "Golfo de México"
            config.description = "Gulf of Mexico en Español"
            config.rename_keyword("if", "si")
            config.rename_keyword("when", "cuando")
            config.rename_keyword("after", "después")
            config.rename_keyword("function", "función")
            config.rename_keyword("return", "retornar")
            config.rename_keyword("class", "clase")
            config.rename_keyword("var", "var")
            config.rename_keyword("const", "const")
            config.rename_function("print", "imprimir")
            config.rename_function("read", "leer")
            config.rename_function("write", "escribir")

        elif preset_name == "french":
            config.name = "Golfe du Mexique"
            config.description = "Gulf of Mexico en Français"
            config.rename_keyword("if", "si")
            config.rename_keyword("when", "quand")
            config.rename_keyword("after", "après")
            config.rename_keyword("function", "fonction")
            config.rename_keyword("return", "retour")
            config.rename_keyword("class", "classe")
            config.rename_function("print", "imprimer")

        else:
            raise ValueError(f"Unknown preset: {preset_name}")

        return config

    # === Validation ===

    def validate(self) -> list[str]:
        """Validate configuration for consistency.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check for duplicate custom names
        custom_names = [m.custom for m in self.keyword_mappings.values()]
        duplicates = [name for name in custom_names if custom_names.count(name) > 1]
        if duplicates:
            errors.append(f"Duplicate keyword names: {set(duplicates)}")

        # Check function arities
        for name, func in self.builtin_functions.items():
            if func.arity < -1:
                errors.append(f"Function '{name}' has invalid arity: {func.arity}")

        # Check operator precedences
        for symbol, op in self.operators.items():
            if op.precedence < 0:
                errors.append(
                    f"Operator '{symbol}' has invalid precedence: {op.precedence}"
                )
            if op.associativity not in ["left", "right", "none"]:
                errors.append(
                    f"Operator '{symbol}' has invalid associativity: {op.associativity}"
                )

        return errors

    # === Serialization ===

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "metadata": {
                "name": self.name,
                "version": self.version,
                "description": self.description,
                "author": self.author,
                "target_interpreter": self.target_interpreter,
            },
            "keywords": {k: asdict(v) for k, v in self.keyword_mappings.items()},
            "functions": {k: asdict(v) for k, v in self.builtin_functions.items()},
            "operators": {k: asdict(v) for k, v in self.operators.items()},
            "syntax_options": asdict(self.syntax_options),
            "parsing_config": asdict(self.parsing_config),
            "runtime": {
                "debug_mode": self.debug_mode,
                "strict_mode": self.strict_mode,
                "compatibility_mode": self.compatibility_mode,
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LanguageConfig:
        """Create configuration from dictionary.

        Args:
            data: Dictionary representation

        Returns:
            LanguageConfig instance
        """
        config = cls()

        if "metadata" in data:
            config.name = data["metadata"].get("name", config.name)
            config.version = data["metadata"].get("version", config.version)
            config.description = data["metadata"].get("description", config.description)
            config.author = data["metadata"].get("author", config.author)

        if "keywords" in data:
            config.keyword_mappings = {
                k: KeywordMapping(**v) for k, v in data["keywords"].items()
            }

        if "functions" in data:
            config.builtin_functions = {
                k: FunctionConfig(**v) for k, v in data["functions"].items()
            }

        if "operators" in data:
            config.operators = {
                k: OperatorConfig(**v) for k, v in data["operators"].items()
            }

        if "syntax_options" in data:
            config.syntax_options = SyntaxOptions(**data["syntax_options"])

        if "parsing_config" in data:
            config.parsing_config = ParsingConfig(**data["parsing_config"])

        if "runtime" in data:
            config.debug_mode = data["runtime"].get("debug_mode", False)
            config.strict_mode = data["runtime"].get("strict_mode", False)
            config.compatibility_mode = data["runtime"].get(
                "compatibility_mode", "standard"
            )

        return config

    def save(self, filepath: Union[str, Path], format: str = "auto") -> None:
        """Save configuration to file.

        Args:
            filepath: Output file path
            format: File format (yaml, json, or auto to detect from extension)
        """
        filepath = Path(filepath)

        if format == "auto":
            format = "yaml" if filepath.suffix in [".yaml", ".yml"] else "json"

        if format == "yaml" and not YAML_AVAILABLE:
            print("Warning: YAML not available, falling back to JSON")
            format = "json"
            filepath = filepath.with_suffix(".json")

        data = self.to_dict()

        with open(filepath, "w") as f:
            if format == "yaml":
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            else:
                json.dump(data, f, indent=2)

        print(f"Configuration saved to {filepath}")

    @classmethod
    def load(cls, filepath: Union[str, Path]) -> LanguageConfig:
        """Load configuration from file.

        Args:
            filepath: Input file path

        Returns:
            LanguageConfig instance
        """
        filepath = Path(filepath)

        is_yaml = filepath.suffix in [".yaml", ".yml"]
        if is_yaml and not YAML_AVAILABLE:
            raise ImportError(
                "YAML support not available. Install with: pip install pyyaml\n"
                "Or use JSON format instead."
            )

        with open(filepath, "r") as f:
            if is_yaml:
                data = yaml.safe_load(f)
            else:
                data = json.load(f)

        return cls.from_dict(data)

    # =====================================================================
    # CRUD OPERATIONS - Complete config management
    # =====================================================================

    def update(self, updates: dict[str, Any], merge: bool = True) -> None:
        """Update configuration with new values.

        Args:
            updates: Dictionary of updates to apply
            merge: If True, merge with existing. If False, replace sections.

        Examples:
            config.update({"metadata": {"author": "Alice"}})
            config.update({"keywords": {"si": {"original": "if", "custom": "si"}}})
        """
        if "metadata" in updates:
            meta = updates["metadata"]
            if "name" in meta:
                self.name = meta["name"]
            if "version" in meta:
                self.version = meta["version"]
            if "description" in meta:
                self.description = meta["description"]
            if "author" in meta:
                self.author = meta["author"]

        if "keywords" in updates:
            if merge:
                # Merge keyword mappings
                for key, value in updates["keywords"].items():
                    if isinstance(value, dict):
                        self.keyword_mappings[key] = KeywordMapping(**value)
                    elif isinstance(value, KeywordMapping):
                        self.keyword_mappings[key] = value
            else:
                # Replace all keywords
                self.keyword_mappings = {
                    k: KeywordMapping(**v) if isinstance(v, dict) else v
                    for k, v in updates["keywords"].items()
                }

        if "functions" in updates:
            if merge:
                for key, value in updates["functions"].items():
                    if isinstance(value, dict):
                        self.builtin_functions[key] = FunctionConfig(**value)
                    elif isinstance(value, FunctionConfig):
                        self.builtin_functions[key] = value
            else:
                self.builtin_functions = {
                    k: FunctionConfig(**v) if isinstance(v, dict) else v
                    for k, v in updates["functions"].items()
                }

        if "operators" in updates:
            if merge:
                for key, value in updates["operators"].items():
                    if isinstance(value, dict):
                        self.operators[key] = OperatorConfig(**value)
                    elif isinstance(value, OperatorConfig):
                        self.operators[key] = value
            else:
                self.operators = {
                    k: OperatorConfig(**v) if isinstance(v, dict) else v
                    for k, v in updates["operators"].items()
                }

        if "syntax_options" in updates:
            if merge:
                # Update individual syntax options
                for key, value in updates["syntax_options"].items():
                    if hasattr(self.syntax_options, key):
                        setattr(self.syntax_options, key, value)
            else:
                self.syntax_options = SyntaxOptions(**updates["syntax_options"])

        if "parsing_config" in updates:
            if merge:
                for key, value in updates["parsing_config"].items():
                    if hasattr(self.parsing_config, key):
                        setattr(self.parsing_config, key, value)
            else:
                self.parsing_config = ParsingConfig(**updates["parsing_config"])

        if "runtime" in updates:
            runtime = updates["runtime"]
            if "debug_mode" in runtime:
                self.debug_mode = runtime["debug_mode"]
            if "strict_mode" in runtime:
                self.strict_mode = runtime["strict_mode"]
            if "compatibility_mode" in runtime:
                self.compatibility_mode = runtime["compatibility_mode"]

    def delete_keyword(self, keyword: str) -> bool:
        """Delete a keyword mapping.

        Args:
            keyword: Original keyword name to delete

        Returns:
            True if deleted, False if not found
        """
        if keyword in self.keyword_mappings:
            del self.keyword_mappings[keyword]
            return True
        return False

    def delete_function(self, function_name: str) -> bool:
        """Delete a function configuration.

        Args:
            function_name: Function name to delete

        Returns:
            True if deleted, False if not found
        """
        if function_name in self.builtin_functions:
            del self.builtin_functions[function_name]
            return True
        return False

    def delete_operator(self, operator: str) -> bool:
        """Delete an operator configuration.

        Args:
            operator: Operator symbol to delete

        Returns:
            True if deleted, False if not found
        """
        if operator in self.operators:
            del self.operators[operator]
            return True
        return False

    def merge(self, other: "LanguageConfig", prefer_other: bool = True) -> None:
        """Merge another configuration into this one.

        Args:
            other: Configuration to merge from
            prefer_other: If True, other's values override. If False, keep existing.
        """
        if prefer_other or not self.name:
            self.name = other.name
        if prefer_other or not self.version:
            self.version = other.version
        if prefer_other or not self.description:
            self.description = other.description
        if prefer_other or not self.author:
            self.author = other.author

        # Merge keywords
        for key, mapping in other.keyword_mappings.items():
            if prefer_other or key not in self.keyword_mappings:
                self.keyword_mappings[key] = deepcopy(mapping)

        # Merge functions
        for key, func in other.builtin_functions.items():
            if prefer_other or key not in self.builtin_functions:
                self.builtin_functions[key] = deepcopy(func)

        # Merge operators
        for key, op in other.operators.items():
            if prefer_other or key not in self.operators:
                self.operators[key] = deepcopy(op)

    def clone(self) -> "LanguageConfig":
        """Create a deep copy of this configuration.

        Returns:
            New LanguageConfig instance with same values
        """
        return deepcopy(self)

    def diff(self, other: "LanguageConfig") -> dict[str, Any]:
        """Compare this config with another and return differences.

        Args:
            other: Configuration to compare with

        Returns:
            Dictionary describing differences
        """
        differences = {
            "metadata": {},
            "keywords": {"added": [], "removed": [], "modified": []},
            "functions": {"added": [], "removed": [], "modified": []},
            "operators": {"added": [], "removed": [], "modified": []},
            "syntax_changes": [],
            "parsing_changes": [],
        }

        # Metadata differences
        if self.name != other.name:
            differences["metadata"]["name"] = {"self": self.name, "other": other.name}
        if self.version != other.version:
            differences["metadata"]["version"] = {
                "self": self.version,
                "other": other.version,
            }

        # Keyword differences
        self_keys = set(self.keyword_mappings.keys())
        other_keys = set(other.keyword_mappings.keys())

        differences["keywords"]["added"] = list(other_keys - self_keys)
        differences["keywords"]["removed"] = list(self_keys - other_keys)

        for key in self_keys & other_keys:
            if self.keyword_mappings[key].custom != other.keyword_mappings[key].custom:
                differences["keywords"]["modified"].append(
                    {
                        "keyword": key,
                        "self": self.keyword_mappings[key].custom,
                        "other": other.keyword_mappings[key].custom,
                    }
                )

        # Function differences
        self_funcs = set(self.builtin_functions.keys())
        other_funcs = set(other.builtin_functions.keys())

        differences["functions"]["added"] = list(other_funcs - self_funcs)
        differences["functions"]["removed"] = list(self_funcs - other_funcs)

        # Syntax option differences
        self_syntax = asdict(self.syntax_options)
        other_syntax = asdict(other.syntax_options)

        for key in self_syntax:
            if self_syntax[key] != other_syntax.get(key):
                differences["syntax_changes"].append(
                    {
                        "option": key,
                        "self": self_syntax[key],
                        "other": other_syntax.get(key),
                    }
                )

        return differences

    @classmethod
    def load_from_url(cls, url: str) -> "LanguageConfig":
        """Load configuration from a URL.

        Args:
            url: HTTP(S) URL to configuration file

        Returns:
            LanguageConfig instance
        """
        import urllib.request

        with urllib.request.urlopen(url) as response:
            content = response.read().decode("utf-8")

        # Detect format from URL
        is_yaml = url.endswith(".yaml") or url.endswith(".yml")

        if is_yaml:
            if not YAML_AVAILABLE:
                raise ImportError("YAML support required for .yaml URLs")
            data = yaml.safe_load(content)
        else:
            data = json.loads(content)

        return cls.from_dict(data)

    def export_mapping_table(self, filepath: Optional[Union[str, Path]] = None) -> str:
        """Export keyword/function mapping table for documentation.

        Args:
            filepath: Optional file to write to

        Returns:
            Markdown table as string
        """
        lines = ["# Language Configuration Mapping\n"]
        lines.append(f"**Language:** {self.name}\n")
        lines.append(f"**Version:** {self.version}\n\n")

        lines.append("## Keywords\n")
        lines.append("| Original | Custom | Category | Description |")
        lines.append("|----------|--------|----------|-------------|")
        for original, mapping in sorted(self.keyword_mappings.items()):
            lines.append(
                f"| `{mapping.original}` | `{mapping.custom}` | "
                f"{mapping.category} | {mapping.description} |"
            )

        lines.append("\n## Built-in Functions\n")
        lines.append("| Name | Arity | Description | Enabled |")
        lines.append("|------|-------|-------------|---------|")
        for name, func in sorted(self.builtin_functions.items()):
            arity_str = "variadic" if func.arity == -1 else str(func.arity)
            enabled_str = "✓" if func.enabled else "✗"
            lines.append(
                f"| `{func.name}` | {arity_str} | "
                f"{func.description} | {enabled_str} |"
            )

        lines.append("\n## Syntax Options\n")
        lines.append("| Option | Value |")
        lines.append("|--------|-------|")
        for key, value in asdict(self.syntax_options).items():
            lines.append(f"| {key} | `{value}` |")

        result = "\n".join(lines)

        if filepath:
            with open(filepath, "w") as f:
                f.write(result)
            print(f"Mapping table exported to {filepath}")

        return result

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"LanguageConfig(name='{self.name}', "
            f"keywords={len(self.keyword_mappings)}, "
            f"functions={len(self.builtin_functions)}, "
            f"operators={len(self.operators)})"
        )


# === Helper Functions ===


def list_presets() -> list[str]:
    """Get list of available presets.

    Returns:
        List of preset names
    """
    return [
        "python_like",
        "js_like",
        "serious",
        "minimal",
        "spanish",
        "french",
    ]


def create_custom_config_interactive() -> LanguageConfig:
    """Interactive configuration builder (CLI).

    Returns:
        Configured LanguageConfig
    """
    print("=== Gulf of Mexico Language Configuration Builder ===\n")

    config = LanguageConfig()

    print("Start from a preset? (y/n): ", end="")
    if input().lower() == "y":
        print(f"Available presets: {', '.join(list_presets())}")
        print("Preset name: ", end="")
        preset = input().strip()
        try:
            config = LanguageConfig.from_preset(preset)
            print(f"Loaded preset: {preset}\n")
        except ValueError:
            print("Invalid preset, starting from default\n")

    print(f"Language name [{config.name}]: ", end="")
    name = input().strip()
    if name:
        config.name = name

    print("Disable satirical keywords? (y/n): ", end="")
    if input().lower() == "y":
        config.disable_satirical_keywords()
        print("Satirical keywords disabled")

    print("\nConfiguration complete!")
    print(config)

    return config


if __name__ == "__main__":
    # Demo usage
    print("=== Language Configuration Demo ===\n")

    # Create default config
    config = LanguageConfig()
    print(f"Default: {config}\n")

    # Try some customizations
    config.rename_keyword("if", "when_condition")
    config.rename_function("print", "output")
    config.set_array_indexing(0, False)

    # Save to file
    config.save("custom_language.yaml")

    # Load preset
    spanish = LanguageConfig.from_preset("spanish")
    print(f"Spanish preset: {spanish}\n")

    # Validate
    errors = config.validate()
    print(f"Validation: {'OK' if not errors else errors}\n")

    # Export mapping table
    table = config.export_mapping_table("language_mapping.md")
    print("Mapping table created!")
