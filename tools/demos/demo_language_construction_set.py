#!/usr/bin/env python3
"""
Gulf of Mexico Language Construction Set Demo

This script demonstrates the capabilities of the Language Construction Set
by creating and using custom language configurations.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from gulfofmexico.language_config import LanguageConfig, list_presets
from gulfofmexico.language_runtime import LanguageRuntime


def demo_1_basic_customization():
    """Demo 1: Basic keyword and function renaming."""
    print("\n" + "=" * 70)
    print("DEMO 1: Basic Customization")
    print("=" * 70)

    config = LanguageConfig()

    print("\n1. Renaming keywords:")
    config.rename_keyword("if", "when_condition")
    config.rename_keyword("function", "def")
    print("   ✓ 'if' → 'when_condition'")
    print("   ✓ 'function' → 'def'")

    print("\n2. Renaming functions:")
    config.rename_function("print", "output")
    print("   ✓ 'print' → 'output'")

    print("\n3. Adjusting array indexing:")
    config.set_array_indexing(0, False)
    print("   ✓ Arrays now start at index 0 (traditional)")
    print("   ✓ Fractional indexing disabled")

    print("\n4. Saving configuration:")
    config.save("demo_basic.json")
    print("   ✓ Saved to demo_basic.json")

    return config


def demo_2_presets():
    """Demo 2: Using presets."""
    print("\n" + "=" * 70)
    print("DEMO 2: Working with Presets")
    print("=" * 70)

    print("\nAvailable presets:")
    for preset in list_presets():
        print(f"  • {preset}")

    print("\nLoading 'python_like' preset:")
    config = LanguageConfig.from_preset("python_like")
    print(f"   Name: {config.name}")
    print(f"   Description: {config.description}")
    print(f"   Array indexing: starts at {config.syntax_options.array_start_index}")
    print(f"   Satirical features: {'enabled' if config.syntax_options.enable_satirical_keywords else 'disabled'}")

    return config


def demo_3_serious_mode():
    """Demo 3: Creating a serious/professional variant."""
    print("\n" + "=" * 70)
    print("DEMO 3: Serious/Professional Mode")
    print("=" * 70)

    config = LanguageConfig()
    config.name = "Gulf of Mexico Professional Edition"
    config.description = "Professional mode without satirical features"

    print("\n1. Disabling satirical keywords:")
    satirical_before = len(config.get_keyword_by_category("satirical"))
    config.disable_satirical_keywords()
    print(f"   Removed {satirical_before} satirical keywords")

    print("\n2. Disabling special features:")
    config.enable_feature("satirical", False)
    config.enable_feature("quantum", False)
    config.enable_feature("time_travel", False)
    config.enable_feature("gaslighting", False)
    print("   ✓ All satirical features disabled")

    print("\n3. Enabling strict mode:")
    config.strict_mode = True
    print("   ✓ Strict type checking enabled")

    print("\n4. Saving professional configuration:")
    config.save("demo_professional.json")
    print("   ✓ Saved to demo_professional.json")

    return config


def demo_4_internationalization():
    """Demo 4: Creating an internationalized variant."""
    print("\n" + "=" * 70)
    print("DEMO 4: Internationalization (French)")
    print("=" * 70)

    config = LanguageConfig()
    config.name = "Golfe du Mexique"
    config.description = "Gulf of Mexico en Français"

    print("\n1. Translating control keywords:")
    translations = {
        "if": "si",
        "when": "quand",
        "after": "après",
        "function": "fonction",
        "return": "retour",
        "class": "classe",
        "var": "var",
        "const": "const",
    }

    for original, french in translations.items():
        config.rename_keyword(original, french)
        print(f"   {original:12} → {french}")

    print("\n2. Translating built-in functions:")
    func_translations = {
        "print": "imprimer",
        "read": "lire",
        "write": "écrire",
        "Number": "Nombre",
        "String": "Texte",
        "Boolean": "Booléen",
        "List": "Liste",
    }

    for original, french in func_translations.items():
        try:
            config.rename_function(original, french)
            print(f"   {original:12} → {french}")
        except ValueError:
            pass  # Function might not exist in config

    print("\n3. Saving French configuration:")
    config.save("demo_french.json")
    print("   ✓ Saved to demo_french.json")

    return config


def demo_5_minimal():
    """Demo 5: Creating a minimal teaching variant."""
    print("\n" + "=" * 70)
    print("DEMO 5: Minimal Teaching Variant")
    print("=" * 70)

    config = LanguageConfig()
    config.name = "Gulf of Mexico for Teaching"
    config.description = "Minimal feature set for beginners"

    print("\n1. Keeping only essential keywords:")
    essential_keywords = {"if", "function", "return", "var", "const", "class"}

    # Remove all non-essential keywords
    all_keywords = set(config.keyword_mappings.keys())
    to_remove = all_keywords - essential_keywords

    for keyword in to_remove:
        config.remove_keyword(keyword)

    print(f"   Kept {len(essential_keywords)} essential keywords")
    print(f"   Removed {len(to_remove)} non-essential keywords")

    print("\n2. Keeping only essential functions:")
    essential_functions = {"print", "Number", "String", "Boolean", "List"}

    all_functions = set(config.builtin_functions.keys())
    to_remove = all_functions - essential_functions

    for func in to_remove:
        config.remove_function(func)

    print(f"   Kept {len(essential_functions)} essential functions")
    print(f"   Removed {len(to_remove)} non-essential functions")

    print("\n3. Simplifying syntax:")
    config.set_array_indexing(0, False)
    config.enable_feature("three_valued_logic", False)
    config.enable_feature("probabilistic", False)
    config.enable_feature("temporal", False)
    print("   ✓ 0-based indexing")
    print("   ✓ Standard boolean logic")
    print("   ✓ Simple variables")

    print("\n4. Saving minimal configuration:")
    config.save("demo_minimal.json")
    print("   ✓ Saved to demo_minimal.json")

    validation = config.validate()
    if validation:
        print(f"\n⚠️  Validation warnings: {validation}")
    else:
        print("\n✓ Configuration validated successfully")

    return config


def demo_6_runtime():
    """Demo 6: Using configurations at runtime."""
    print("\n" + "=" * 70)
    print("DEMO 6: Runtime Integration")
    print("=" * 70)

    print("\n1. Loading configuration into runtime:")
    config = LanguageConfig.from_preset("python_like")
    LanguageRuntime.load_config(config)

    print("\n2. Querying runtime information:")
    info = LanguageRuntime.get_info()
    print(info)

    print("\n3. Testing keyword translation:")
    # In Python-like mode, 'def' maps to 'function'
    original = LanguageRuntime.translate_keyword("def")
    print(f"   'def' translates to: '{original}'")

    print("\n4. Checking feature status:")
    features = ["satirical", "quantum", "three_valued_logic"]
    for feature in features:
        status = "enabled" if LanguageRuntime.is_feature_enabled(feature) else "disabled"
        print(f"   {feature:20} {status}")

    print("\n5. Getting array configuration:")
    start_idx = LanguageRuntime.get_array_start_index()
    fractional = LanguageRuntime.is_fractional_indexing_enabled()
    print(f"   Array start index: {start_idx}")
    print(f"   Fractional indexing: {'enabled' if fractional else 'disabled'}")

    print("\n6. Resetting to default:")
    LanguageRuntime.reset()
    print("   ✓ Reset to default Gulf of Mexico configuration")


def demo_7_validation():
    """Demo 7: Configuration validation."""
    print("\n" + "=" * 70)
    print("DEMO 7: Configuration Validation")
    print("=" * 70)

    print("\n1. Creating a valid configuration:")
    config = LanguageConfig()
    errors = config.validate()
    print(f"   Validation result: {'✓ Valid' if not errors else f'✗ {len(errors)} errors'}")

    print("\n2. Creating an invalid configuration:")
    bad_config = LanguageConfig()

    # Create duplicate custom names (invalid)
    bad_config.rename_keyword("if", "test")
    bad_config.rename_keyword("when", "test")  # Duplicate!

    errors = bad_config.validate()
    if errors:
        print(f"   Found {len(errors)} validation errors:")
        for error in errors:
            print(f"     • {error}")

    print("\n3. Creating a config with invalid arity:")
    bad_config2 = LanguageConfig()
    bad_config2.add_function("bad_func", arity=-5)  # Invalid arity

    errors = bad_config2.validate()
    if errors:
        print(f"   Found {len(errors)} validation errors:")
        for error in errors:
            print(f"     • {error}")


def demo_8_documentation():
    """Demo 8: Generating documentation."""
    print("\n" + "=" * 70)
    print("DEMO 8: Documentation Generation")
    print("=" * 70)

    config = LanguageConfig.from_preset("spanish")

    print("\n1. Generating mapping table:")
    table = config.export_mapping_table("demo_spanish_docs.md")

    print("   ✓ Generated documentation")
    print("   ✓ Saved to: demo_spanish_docs.md")

    print("\n2. Table preview (first 20 lines):")
    lines = table.split("\n")[:20]
    for line in lines:
        print(f"   {line}")

    if len(lines) < len(table.split("\n")):
        print(f"   ... ({len(table.split('\n')) - 20} more lines)")


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 10 + "Gulf of Mexico Language Construction Set Demo" + " " * 12 + "║")
    print("╚" + "=" * 68 + "╝")

    demos = [
        demo_1_basic_customization,
        demo_2_presets,
        demo_3_serious_mode,
        demo_4_internationalization,
        demo_5_minimal,
        demo_6_runtime,
        demo_7_validation,
        demo_8_documentation,
    ]

    for i, demo in enumerate(demos, 1):
        try:
            demo()
        except Exception as e:
            print(f"\n❌ Error in demo {i}: {e}")
            import traceback

            traceback.print_exc()

    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print("\nGenerated files:")
    demo_files = [
        "demo_basic.json",
        "demo_professional.json",
        "demo_french.json",
        "demo_minimal.json",
        "demo_spanish_docs.md",
    ]
    for file in demo_files:
        if Path(file).exists():
            print(f"  ✓ {file}")

    print("\nNext steps:")
    print("  1. Examine the generated configuration files")
    print("  2. Try: python gomconfig.py info demo_basic.json")
    print("  3. Try: python gomconfig.py validate demo_minimal.json")
    print("  4. Read: LANGUAGE_CONSTRUCTION_SET.md for full documentation")
    print("  5. Create your own: python gomconfig.py create --interactive")
    print()


if __name__ == "__main__":
    main()
