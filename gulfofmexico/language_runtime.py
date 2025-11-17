"""
Gulf of Mexico Language Runtime Integration

This module integrates the Language Construction Set with the interpreter,
allowing custom language configurations to be applied at runtime.

Features:
    - Dynamic keyword mapping during parsing
    - Custom function registration
    - Syntax option enforcement
    - Hot-reloading of configurations
    - Backwards compatibility with standard Gulf of Mexico

Integration Points:
    1. Lexer: Apply custom comment syntax
    2. Parser: Remap keywords during syntax tree construction
    3. Interpreter: Use custom function implementations
    4. Runtime: Enforce syntax options (array indexing, etc.)
"""

from __future__ import annotations
from typing import Optional, Dict, Any, Callable
from pathlib import Path
import os

from gulfofmexico.language_config import LanguageConfig
from gulfofmexico.builtin import (
    GulfOfMexicoValue,
    GulfOfMexicoKeyword,
    Name,
    KEYWORDS as DEFAULT_KEYWORDS,
    BUILTIN_FUNCTION_KEYWORDS as DEFAULT_FUNCTIONS,
)


class LanguageRuntime:
    """Runtime system for applying language configurations.

    This class manages the active language configuration and provides
    methods to apply it during interpretation.
    """

    _instance: Optional[LanguageRuntime] = None
    _config: Optional[LanguageConfig] = None
    _keyword_reverse_map: Dict[str, str] = {}  # custom -> original
    _function_map: Dict[str, str] = {}  # custom name -> original name

    def __new__(cls):
        """Singleton pattern to ensure one runtime instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> LanguageRuntime:
        """Get the singleton runtime instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def load_config(
        cls, config: Optional[LanguageConfig] = None, config_file: Optional[str] = None
    ) -> None:
        """Load a language configuration.

        Args:
            config: LanguageConfig instance
            config_file: Path to config file (YAML/JSON)
        """
        runtime = cls.get_instance()

        if config_file:
            runtime._config = LanguageConfig.load(config_file)
        elif config:
            runtime._config = config
        else:
            runtime._config = LanguageConfig()  # Default

        runtime._build_mappings()

        if runtime._config:
            print(f"[Language Runtime] Loaded: {runtime._config.name}")
            if not runtime._config.syntax_options.enable_satirical_keywords:
                print("[Language Runtime] Satirical keywords disabled")

    @classmethod
    def get_config(cls) -> Optional[LanguageConfig]:
        """Get the current language configuration."""
        runtime = cls.get_instance()
        return runtime._config

    @classmethod
    def reset(cls) -> None:
        """Reset to default Gulf of Mexico configuration."""
        runtime = cls.get_instance()
        runtime._config = None
        runtime._keyword_reverse_map = {}
        runtime._function_map = {}
        print("[Language Runtime] Reset to default configuration")

    def _build_mappings(self) -> None:
        """Build reverse mappings for efficient lookup."""
        if not self._config:
            return

        # Build keyword reverse map: custom name -> original name
        self._keyword_reverse_map = {
            mapping.custom: mapping.original
            for mapping in self._config.keyword_mappings.values()
        }

        # Build function map
        self._function_map = {
            func.name: func.implementation or func.name
            for func in self._config.builtin_functions.values()
            if func.enabled
        }

    @classmethod
    def translate_keyword(cls, keyword_text: str) -> str:
        """Translate custom keyword to original.

        Args:
            keyword_text: Custom keyword name

        Returns:
            Original keyword name (or same if no mapping)
        """
        runtime = cls.get_instance()
        if not runtime._config:
            return keyword_text

        return runtime._keyword_reverse_map.get(keyword_text, keyword_text)

    @classmethod
    def is_keyword_enabled(cls, original_keyword: str) -> bool:
        """Check if a keyword is enabled in the current config.

        Args:
            original_keyword: Original keyword name

        Returns:
            True if enabled, False if disabled
        """
        runtime = cls.get_instance()
        if not runtime._config:
            return True

        # Check if keyword exists in current config
        return original_keyword in runtime._config.keyword_mappings

    @classmethod
    def get_custom_keywords_namespace(cls) -> Dict[str, Name]:
        """Get namespace with custom keyword names.

        Returns:
            Dictionary mapping custom keyword names to GulfOfMexicoKeyword values
        """
        runtime = cls.get_instance()
        if not runtime._config:
            return DEFAULT_KEYWORDS.copy()

        # Build custom namespace
        namespace = {}
        for original, mapping in runtime._config.keyword_mappings.items():
            # Use custom name, but store original value
            namespace[mapping.custom] = Name(
                mapping.custom,
                GulfOfMexicoKeyword(original),  # Store original for interpreter
            )

        return namespace

    @classmethod
    def get_custom_functions_namespace(cls) -> Dict[str, Name]:
        """Get namespace with custom function names.

        Returns:
            Dictionary mapping custom function names to built-in functions
        """
        runtime = cls.get_instance()
        if not runtime._config:
            return DEFAULT_FUNCTIONS.copy()

        # For now, return default functions
        # TODO: Implement custom function loading
        return DEFAULT_FUNCTIONS.copy()

    @classmethod
    def get_array_start_index(cls) -> int:
        """Get the configured array start index.

        Returns:
            Start index (-1 for Gulf of Mexico, 0 for traditional)
        """
        runtime = cls.get_instance()
        if not runtime._config:
            return -1  # Default Gulf of Mexico

        return runtime._config.syntax_options.array_start_index

    @classmethod
    def is_fractional_indexing_enabled(cls) -> bool:
        """Check if fractional indexing is enabled.

        Returns:
            True if enabled
        """
        runtime = cls.get_instance()
        if not runtime._config:
            return True  # Default Gulf of Mexico

        return runtime._config.syntax_options.allow_fractional_indexing

    @classmethod
    def is_feature_enabled(cls, feature: str) -> bool:
        """Check if a language feature is enabled.

        Args:
            feature: Feature name (satirical, quantum, time_travel, etc.)

        Returns:
            True if enabled
        """
        runtime = cls.get_instance()
        if not runtime._config:
            return True  # Default: all features enabled

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
            return getattr(runtime._config.syntax_options, feature_map[feature], True)

        return True

    @classmethod
    def get_comment_syntax(cls) -> tuple[str, Optional[str], Optional[str]]:
        """Get comment syntax configuration.

        Returns:
            Tuple of (single_line, multi_start, multi_end)
        """
        runtime = cls.get_instance()
        if not runtime._config:
            return ("//", None, None)

        opts = runtime._config.syntax_options
        return (
            opts.single_line_comment,
            opts.multi_line_comment_start,
            opts.multi_line_comment_end,
        )

    @classmethod
    def should_enforce_semicolons(cls) -> bool:
        """Check if semicolons are required.

        Returns:
            True if semicolons required
        """
        runtime = cls.get_instance()
        if not runtime._config:
            return False

        return runtime._config.syntax_options.require_semicolons

    @classmethod
    def get_info(cls) -> str:
        """Get information about current configuration.

        Returns:
            Human-readable info string
        """
        runtime = cls.get_instance()
        if not runtime._config:
            return "Language: Gulf of Mexico (Default)"

        config = runtime._config
        info = [
            f"Language: {config.name}",
            f"Version: {config.version}",
            f"Description: {config.description}",
            f"Keywords: {len(config.keyword_mappings)}",
            f"Functions: {len([f for f in config.builtin_functions.values() if f.enabled])}",
            f"Operators: {len(config.operators)}",
        ]

        # Feature flags
        opts = config.syntax_options
        features = []
        if opts.enable_satirical_keywords:
            features.append("satirical")
        if opts.three_valued_logic:
            features.append("3-valued-logic")
        if opts.probabilistic_variables:
            features.append("probabilistic")
        if opts.allow_fractional_indexing:
            features.append("fractional-indexing")

        if features:
            info.append(f"Features: {', '.join(features)}")

        info.append(f"Array indexing: starts at {opts.array_start_index}")

        return "\n".join(info)


def apply_config_to_interpreter(
    namespaces: list[Dict[str, Any]], config: Optional[LanguageConfig] = None
) -> None:
    """Apply language configuration to interpreter namespaces.

    This function modifies the interpreter's namespace to use custom
    keyword and function names from the configuration.

    Args:
        namespaces: List of namespace dictionaries
        config: LanguageConfig to apply (uses runtime config if None)
    """
    if config:
        LanguageRuntime.load_config(config)

    if not namespaces:
        return

    # Replace base namespace with custom keywords and functions
    custom_keywords = LanguageRuntime.get_custom_keywords_namespace()
    custom_functions = LanguageRuntime.get_custom_functions_namespace()

    # Update the first namespace (base namespace)
    namespaces[0].update(custom_keywords)
    namespaces[0].update(custom_functions)


def check_config_environment() -> Optional[str]:
    """Check for language config in environment variables.

    Returns:
        Path to config file if found, None otherwise
    """
    # Check for GULFOFMEXICO_CONFIG environment variable
    config_path = os.environ.get("GULFOFMEXICO_CONFIG")
    if config_path and Path(config_path).exists():
        return config_path

    # Check for .gomconfig in current directory
    local_config = Path(".gomconfig")
    if local_config.exists():
        return str(local_config)

    # Check for .gomconfig in home directory
    home_config = Path.home() / ".gomconfig"
    if home_config.exists():
        return str(home_config)

    return None


def auto_load_config() -> Optional[LanguageConfig]:
    """Auto-load configuration from environment.

    Returns:
        Loaded LanguageConfig or None
    """
    config_file = check_config_environment()
    if config_file:
        try:
            config = LanguageConfig.load(config_file)
            print(f"[Auto-loaded config from: {config_file}]")
            return config
        except Exception as e:
            print(f"[Warning: Failed to load config from {config_file}: {e}]")

    return None


# === CLI Integration Helpers ===


def print_language_info() -> None:
    """Print information about the current language configuration."""
    print("\n" + "=" * 60)
    print(LanguageRuntime.get_info())
    print("=" * 60 + "\n")


def create_config_from_args(args: Any) -> Optional[LanguageConfig]:
    """Create configuration from command-line arguments.

    Args:
        args: Parsed argparse namespace

    Returns:
        LanguageConfig if specified, None otherwise
    """
    # Check for --config argument
    if hasattr(args, "config") and args.config:
        return LanguageConfig.load(args.config)

    # Check for --preset argument
    if hasattr(args, "preset") and args.preset:
        return LanguageConfig.from_preset(args.preset)

    # Check for --serious-mode flag
    if hasattr(args, "serious_mode") and args.serious_mode:
        return LanguageConfig.from_preset("serious")

    return None


if __name__ == "__main__":
    # Demo
    print("=== Language Runtime Demo ===\n")

    # Load default
    LanguageRuntime.load_config()
    print_language_info()

    # Load Spanish preset
    spanish = LanguageConfig.from_preset("spanish")
    LanguageRuntime.load_config(spanish)
    print_language_info()

    # Test keyword translation
    print("Translate 'si' ->", LanguageRuntime.translate_keyword("si"))
    print("Translate 'cuando' ->", LanguageRuntime.translate_keyword("cuando"))

    # Check features
    print("\nFeatures:")
    print("  Satirical enabled?", LanguageRuntime.is_feature_enabled("satirical"))
    print("  Quantum enabled?", LanguageRuntime.is_feature_enabled("quantum"))
    print("  Array start index:", LanguageRuntime.get_array_start_index())

    # Reset
    LanguageRuntime.reset()
    print("\n[Reset to default]")
    print_language_info()
