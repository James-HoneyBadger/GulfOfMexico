#!/usr/bin/env python3
"""
Gulf of Mexico Language Configuration CLI Tool

Command-line utility for creating, editing, and managing language configurations.

Usage:
    gomconfig create [--preset PRESET] [--output FILE]
    gomconfig edit FILE
    gomconfig validate FILE
    gomconfig info [FILE]
    gomconfig export FILE [--format markdown|json|yaml]
    gomconfig list-presets
    gomconfig convert FILE --from FORMAT --to FORMAT
"""

import argparse
import sys
from pathlib import Path

from gulfofmexico.language_config import (
    LanguageConfig,
    create_custom_config_interactive,
    list_presets,
)
from gulfofmexico.language_runtime import LanguageRuntime


def cmd_create(args):
    """Create a new language configuration."""
    if args.preset:
        try:
            config = LanguageConfig.from_preset(args.preset)
            print(f"Created configuration from preset: {args.preset}")
        except ValueError as e:
            print(f"Error: {e}")
            print(f"Available presets: {', '.join(list_presets())}")
            return 1
    elif args.interactive:
        config = create_custom_config_interactive()
    else:
        config = LanguageConfig()
        print("Created default configuration")

    # Save to file
    output = args.output or "language_config.yaml"
    config.save(output)
    print(f"Saved to: {output}")
    return 0


def cmd_edit(args):
    """Edit an existing configuration (opens in text editor)."""
    import os
    import subprocess

    filepath = Path(args.file)
    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        return 1

    # Determine editor
    editor = os.environ.get("EDITOR", "nano")

    # Open in editor
    try:
        subprocess.run([editor, str(filepath)])
        print(f"Edited: {filepath}")

        # Validate after editing
        try:
            config = LanguageConfig.load(filepath)
            errors = config.validate()
            if errors:
                print("\nValidation errors:")
                for error in errors:
                    print(f"  ❌ {error}")
                return 1
            else:
                print("\n✓ Configuration is valid")
        except Exception as e:
            print(f"\n❌ Error loading config: {e}")
            return 1
    except FileNotFoundError:
        print(f"Error: Editor '{editor}' not found")
        print("Set EDITOR environment variable to your preferred editor")
        return 1

    return 0


def cmd_validate(args):
    """Validate a configuration file."""
    filepath = Path(args.file)
    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        return 1

    try:
        config = LanguageConfig.load(filepath)
        errors = config.validate()

        if errors:
            print(f"❌ Validation failed for: {filepath}")
            print("\nErrors:")
            for error in errors:
                print(f"  • {error}")
            return 1
        else:
            print(f"✓ Configuration is valid: {filepath}")
            print("\nSummary:")
            print(f"  Name: {config.name}")
            print(f"  Version: {config.version}")
            print(f"  Keywords: {len(config.keyword_mappings)}")
            print(f"  Functions: {len(config.builtin_functions)}")
            print(f"  Operators: {len(config.operators)}")
            return 0
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return 1


def cmd_info(args):
    """Show information about a configuration."""
    if args.file:
        filepath = Path(args.file)
        if not filepath.exists():
            print(f"Error: File not found: {filepath}")
            return 1

        try:
            config = LanguageConfig.load(filepath)
        except Exception as e:
            print(f"Error loading config: {e}")
            return 1
    else:
        # Show current runtime config
        LanguageRuntime.load_config()
        config = LanguageRuntime.get_config()
        if not config:
            print("No configuration loaded")
            return 1

    # Display detailed info
    print("=" * 70)
    print(f"Language Configuration: {config.name}")
    print("=" * 70)
    print("\nMetadata:")
    print(f"  Version: {config.version}")
    print(f"  Description: {config.description}")
    if config.author:
        print(f"  Author: {config.author}")

    print("\nComponents:")
    print(f"  Keywords: {len(config.keyword_mappings)}")
    print(f"  Functions: {len(config.builtin_functions)}")
    print(f"  Operators: {len(config.operators)}")

    # Show keyword categories
    categories = {}
    for mapping in config.keyword_mappings.values():
        categories[mapping.category] = categories.get(mapping.category, 0) + 1

    print("\nKeyword Categories:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")

    # Show enabled/disabled functions
    enabled = sum(1 for f in config.builtin_functions.values() if f.enabled)
    disabled = len(config.builtin_functions) - enabled
    print("\nFunctions:")
    print(f"  Enabled: {enabled}")
    if disabled > 0:
        print(f"  Disabled: {disabled}")

    # Show syntax options
    opts = config.syntax_options
    print("\nSyntax Options:")
    print(f"  Array indexing: starts at {opts.array_start_index}")
    print(f"  Fractional indexing: {'enabled' if opts.allow_fractional_indexing else 'disabled'}")
    print(f"  Comment style: {opts.single_line_comment}")
    print(f"  Statement terminator: '{opts.statement_terminator}'")

    # Show enabled features
    features = []
    if opts.enable_satirical_keywords:
        features.append("satirical")
    if opts.three_valued_logic:
        features.append("3-valued-logic")
    if opts.probabilistic_variables:
        features.append("probabilistic")
    if opts.temporal_variables:
        features.append("temporal")
    if opts.enable_quantum_features:
        features.append("quantum")

    if features:
        print(f"  Features: {', '.join(features)}")

    print("\nRuntime:")
    print(f"  Debug mode: {'enabled' if config.debug_mode else 'disabled'}")
    print(f"  Strict mode: {'enabled' if config.strict_mode else 'disabled'}")
    print(f"  Compatibility: {config.compatibility_mode}")

    print("=" * 70)

    return 0


def cmd_export(args):
    """Export configuration in different formats."""
    filepath = Path(args.file)
    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        return 1

    try:
        config = LanguageConfig.load(filepath)
    except Exception as e:
        print(f"Error loading config: {e}")
        return 1

    format_type = args.format or "markdown"
    output = args.output or f"{filepath.stem}_export"

    if format_type == "markdown":
        output_file = f"{output}.md"
        config.export_mapping_table(output_file)
        print(f"Exported mapping table to: {output_file}")

    elif format_type == "json":
        output_file = f"{output}.json"
        config.save(output_file, format="json")
        print(f"Exported to JSON: {output_file}")

    elif format_type == "yaml":
        output_file = f"{output}.yaml"
        config.save(output_file, format="yaml")
        print(f"Exported to YAML: {output_file}")

    else:
        print(f"Error: Unknown format: {format_type}")
        print("Supported formats: markdown, json, yaml")
        return 1

    return 0


def cmd_list_presets(args):
    """List available presets."""
    presets = list_presets()

    print("Available Presets:")
    print("=" * 70)

    for preset in presets:
        try:
            config = LanguageConfig.from_preset(preset)
            print(f"\n{preset}:")
            print(f"  {config.description}")
        except Exception as e:
            print(f"\n{preset}: (error loading: {e})")

    print("\nUsage:")
    print("  gomconfig create --preset PRESET_NAME")
    print("  python -m gulfofmexico --preset PRESET_NAME script.gom")

    return 0


def cmd_convert(args):
    """Convert configuration between formats."""
    filepath = Path(args.file)
    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        return 1

    try:
        config = LanguageConfig.load(filepath)
    except Exception as e:
        print(f"Error loading config: {e}")
        return 1

    from_format = args.from_format or ("yaml" if filepath.suffix in [".yaml", ".yml"] else "json")
    to_format = args.to_format

    output = args.output or f"{filepath.stem}.{to_format}"

    config.save(output, format=to_format)
    print(f"Converted {filepath} ({from_format}) to {output} ({to_format})")

    return 0


def cmd_diff(args):
    """Show differences between two configurations."""
    file1 = Path(args.file1)
    file2 = Path(args.file2)

    if not file1.exists():
        print(f"Error: File not found: {file1}")
        return 1
    if not file2.exists():
        print(f"Error: File not found: {file2}")
        return 1

    try:
        config1 = LanguageConfig.load(file1)
        config2 = LanguageConfig.load(file2)
    except Exception as e:
        print(f"Error loading configs: {e}")
        return 1

    print(f"Comparing: {file1} vs {file2}")
    print("=" * 70)

    # Compare keywords
    keys1 = set(config1.keyword_mappings.keys())
    keys2 = set(config2.keyword_mappings.keys())

    if keys1 != keys2:
        print("\nKeyword Differences:")
        only_in_1 = keys1 - keys2
        only_in_2 = keys2 - keys1

        if only_in_1:
            print(f"  Only in {file1.name}: {', '.join(sorted(only_in_1))}")
        if only_in_2:
            print(f"  Only in {file2.name}: {', '.join(sorted(only_in_2))}")

        # Check renamed keywords
        common = keys1 & keys2
        renamed = []
        for key in common:
            if config1.keyword_mappings[key].custom != config2.keyword_mappings[key].custom:
                renamed.append(
                    f"{key}: '{config1.keyword_mappings[key].custom}' -> '{config2.keyword_mappings[key].custom}'"
                )

        if renamed:
            print("  Renamed:")
            for r in renamed:
                print(f"    {r}")
    else:
        print("\n✓ Keywords are identical")

    # Compare functions
    funcs1 = set(config1.builtin_functions.keys())
    funcs2 = set(config2.builtin_functions.keys())

    if funcs1 != funcs2:
        print("\nFunction Differences:")
        only_in_1 = funcs1 - funcs2
        only_in_2 = funcs2 - funcs1

        if only_in_1:
            print(f"  Only in {file1.name}: {', '.join(sorted(only_in_1))}")
        if only_in_2:
            print(f"  Only in {file2.name}: {', '.join(sorted(only_in_2))}")
    else:
        print("\n✓ Functions are identical")

    # Compare syntax options
    opts1 = config1.syntax_options
    opts2 = config2.syntax_options

    differences = []
    if opts1.array_start_index != opts2.array_start_index:
        differences.append(f"array_start_index: {opts1.array_start_index} -> {opts2.array_start_index}")
    if opts1.allow_fractional_indexing != opts2.allow_fractional_indexing:
        differences.append(
            f"fractional_indexing: {opts1.allow_fractional_indexing} -> {opts2.allow_fractional_indexing}"
        )
    if opts1.enable_satirical_keywords != opts2.enable_satirical_keywords:
        differences.append(
            f"satirical_keywords: {opts1.enable_satirical_keywords} -> {opts2.enable_satirical_keywords}"
        )

    if differences:
        print("\nSyntax Option Differences:")
        for diff in differences:
            print(f"  {diff}")
    else:
        print("\n✓ Syntax options are identical")

    return 0


def cmd_update(args):
    """Update a configuration file."""
    from pathlib import Path

    filepath = Path(args.file)
    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        return 1

    try:
        config = LanguageConfig.load(filepath)
        print(f"Loaded: {filepath}")

        # Apply updates from --set flags
        if args.set:
            updates = {}
            for key, value in args.set:
                # Parse nested keys like "metadata.author"
                parts = key.split(".")
                current = updates
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]

                # Try to parse value as JSON for complex types
                try:
                    import json

                    parsed_value = json.loads(value)
                    current[parts[-1]] = parsed_value
                except:
                    # Keep as string if not valid JSON
                    current[parts[-1]] = value

            config.update(updates, merge=True)
            print(f"Applied {len(args.set)} update(s)")

        # Merge with another config
        if args.merge:
            merge_path = Path(args.merge)
            if not merge_path.exists():
                print(f"Error: Merge file not found: {merge_path}")
                return 1

            merge_config = LanguageConfig.load(merge_path)
            config.merge(merge_config, prefer_other=True)
            print(f"Merged with: {merge_path}")

        # Save result
        output = args.output or args.file
        config.save(output)
        print(f"✓ Updated configuration saved to: {output}")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


def cmd_delete(args):
    """Delete elements from configuration."""
    from pathlib import Path

    filepath = Path(args.file)
    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        return 1

    try:
        config = LanguageConfig.load(filepath)
        print(f"Loaded: {filepath}")

        deleted_count = 0

        # Delete keywords
        if args.keyword:
            for kw in args.keyword:
                if config.delete_keyword(kw):
                    print(f"  ✓ Deleted keyword: {kw}")
                    deleted_count += 1
                else:
                    print(f"  ✗ Keyword not found: {kw}")

        # Delete functions
        if args.function:
            for func in args.function:
                if config.delete_function(func):
                    print(f"  ✓ Deleted function: {func}")
                    deleted_count += 1
                else:
                    print(f"  ✗ Function not found: {func}")

        # Delete operators
        if args.operator:
            for op in args.operator:
                if config.delete_operator(op):
                    print(f"  ✓ Deleted operator: {op}")
                    deleted_count += 1
                else:
                    print(f"  ✗ Operator not found: {op}")

        if deleted_count == 0:
            print("No elements deleted")
            return 0

        # Save result
        output = args.output or args.file
        config.save(output)
        print(f"\n✓ Configuration with {deleted_count} deletion(s) saved to: {output}")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Gulf of Mexico Language Configuration Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create from preset
  gomconfig create --preset python_like --output my_lang.yaml

  # Create interactively
  gomconfig create --interactive

  # Validate configuration
  gomconfig validate my_lang.yaml

  # Show info
  gomconfig info my_lang.yaml

  # Export documentation
  gomconfig export my_lang.yaml --format markdown

  # List available presets
  gomconfig list-presets

  # Convert between formats
  gomconfig convert my_lang.yaml --to json

  # Compare configurations
  gomconfig diff config1.yaml config2.yaml
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create new configuration")
    create_parser.add_argument("--preset", help="Start from preset")
    create_parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    create_parser.add_argument("--output", "-o", help="Output file (default: language_config.yaml)")

    # Edit command
    edit_parser = subparsers.add_parser("edit", help="Edit configuration in text editor")
    edit_parser.add_argument("file", help="Configuration file to edit")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate configuration")
    validate_parser.add_argument("file", help="Configuration file to validate")

    # Info command
    info_parser = subparsers.add_parser("info", help="Show configuration information")
    info_parser.add_argument("file", nargs="?", help="Configuration file (default: current runtime)")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export configuration")
    export_parser.add_argument("file", help="Configuration file to export")
    export_parser.add_argument("--format", "-f", choices=["markdown", "json", "yaml"], help="Export format")
    export_parser.add_argument("--output", "-o", help="Output file")

    # List presets command
    list_parser = subparsers.add_parser("list-presets", help="List available presets")

    # Convert command
    convert_parser = subparsers.add_parser("convert", help="Convert between formats")
    convert_parser.add_argument("file", help="Configuration file to convert")
    convert_parser.add_argument("--from", dest="from_format", help="Source format")
    convert_parser.add_argument(
        "--to",
        dest="to_format",
        required=True,
        choices=["json", "yaml"],
        help="Target format",
    )
    convert_parser.add_argument("--output", "-o", help="Output file")

    # Diff command
    diff_parser = subparsers.add_parser("diff", help="Compare two configurations")
    diff_parser.add_argument("file1", help="First configuration file")
    diff_parser.add_argument("file2", help="Second configuration file")

    # Update command
    update_parser = subparsers.add_parser("update", help="Update configuration")
    update_parser.add_argument("file", help="Configuration file to update")
    update_parser.add_argument(
        "--set", action="append", nargs=2, metavar=("KEY", "VALUE"), help="Set key=value (can be used multiple times)"
    )
    update_parser.add_argument("--merge", help="Merge with another config file")
    update_parser.add_argument("--output", "-o", help="Output file (default: update in place)")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete config elements")
    delete_parser.add_argument("file", help="Configuration file")
    delete_parser.add_argument("--keyword", action="append", help="Delete keyword (can be repeated)")
    delete_parser.add_argument("--function", action="append", help="Delete function (can be repeated)")
    delete_parser.add_argument("--operator", action="append", help="Delete operator (can be repeated)")
    delete_parser.add_argument("--output", "-o", help="Output file (default: update in place)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Dispatch to command handler
    commands = {
        "create": cmd_create,
        "edit": cmd_edit,
        "validate": cmd_validate,
        "info": cmd_info,
        "export": cmd_export,
        "list-presets": cmd_list_presets,
        "convert": cmd_convert,
        "diff": cmd_diff,
        "update": cmd_update,
        "delete": cmd_delete,
    }

    handler = commands.get(args.command)
    if handler:
        return handler(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
