#!/usr/bin/env python3
"""
Advanced Demo: Creating Entirely New Programming Languages
===========================================================

This demo shows how to use the Language Construction Set to create
completely different programming languages from Gulf of Mexico.

Features demonstrated:
1. Creating a Lisp-like language
2. Creating a Logo/Turtle-like language
3. Creating a SQL-like language
4. Using CRUD operations (update, delete, merge)
5. Loading from URLs
6. Deep parsing customization
"""

from gulfofmexico.language_config import (
    FunctionConfig,
    KeywordMapping,
    LanguageConfig,
    ParsingConfig,
    SyntaxOptions,
)


def demo_lisp_like_language():
    """Create a Lisp-style language using Gulf of Mexico."""
    print("=" * 70)
    print("DEMO 1: Creating a Lisp-Like Language")
    print("=" * 70)

    config = LanguageConfig(
        name="GulfLisp",
        version="1.0.0",
        description="A Lisp-inspired variant of Gulf of Mexico",
        author="Language Construction Set Demo",
    )

    # Lisp-style syntax
    config.parsing_config = ParsingConfig(
        # Use parentheses for everything
        block_start="(",
        block_end=")",
        list_start="(",
        list_end=")",
        function_call_start="(",
        function_call_end=")",
        # Space-separated, no commas
        parameter_separator=" ",
        statement_separator=" ",
    )

    # Rename keywords to Lisp-style
    config.rename_keyword("function", "defun")
    config.rename_keyword("if", "if")
    config.rename_keyword("var", "let")
    config.rename_keyword("const", "defvar")
    config.rename_keyword("return", "return")

    # Lisp-style function names
    config.rename_function("print", "print")
    # Note: Only rename functions that exist in default Gulf of Mexico
    # Could add more with config.add_function() if needed
    # Lisp-style comments and other syntax options
    config.update(
        {
            "syntax_options": {
                "single_line_comment": ";",
            }
        },
        merge=True,
    )

    # Disable satirical features for serious Lisp
    config.disable_satirical_keywords()

    config.syntax_options.array_start_index = 0  # 0-based like most Lisps

    # Save configuration
    config.save("demo_gulplisp.json")
    print("\n✓ Created GulfLisp configuration")
    print("  - Saved to: demo_gulplisp.json")
    print(f"  - Keywords: {len(config.keyword_mappings)}")
    print(f"  - Block syntax: () instead of {'{}'}")
    print("  - Comment style: ; (Lisp)")

    # Example code snippet
    example = """
    ; GulfLisp Example
    (defun factorial (n)
      (if (< n 2)
        1
        (* n (factorial (- n 1)))))

    (print (factorial 5))
    """
    print("\n  Example GulfLisp code:")
    print("  " + "\n  ".join(example.strip().split("\n")))

    return config


def demo_logo_like_language():
    """Create a Logo/Turtle graphics inspired language."""
    print("\n" + "=" * 70)
    print("DEMO 2: Creating a Logo/Turtle-Like Language")
    print("=" * 70)

    config = LanguageConfig(
        name="GulfTurtle",
        version="1.0.0",
        description="A Logo/Turtle graphics inspired language",
        author="Language Construction Set Demo",
    )

    # Logo-style commands (imperative, simple)
    config.rename_keyword("function", "to")  # to square :size
    config.rename_keyword("return", "output")
    config.rename_keyword("if", "if")
    config.rename_keyword("when", "when")

    # Add turtle graphics functions
    config.add_function(
        "forward",
        FunctionConfig(
            name="forward",
            arity=1,
            description="Move turtle forward by distance",
            enabled=True,
        ),
    )

    config.add_function(
        "back",
        FunctionConfig(
            name="back",
            arity=1,
            description="Move turtle backward by distance",
            enabled=True,
        ),
    )

    config.add_function(
        "left",
        FunctionConfig(
            name="left",
            arity=1,
            description="Turn turtle left by degrees",
            enabled=True,
        ),
    )

    config.add_function(
        "right",
        FunctionConfig(
            name="right",
            arity=1,
            description="Turn turtle right by degrees",
            enabled=True,
        ),
    )

    config.add_function(
        "penup",
        FunctionConfig(
            name="penup",
            arity=0,
            description="Lift pen (stop drawing)",
            enabled=True,
        ),
    )

    config.add_function(
        "pendown",
        FunctionConfig(
            name="pendown",
            arity=0,
            description="Lower pen (start drawing)",
            enabled=True,
        ),
    )

    # Simple syntax
    config.syntax_options.require_semicolons = False
    config.syntax_options.enable_satirical_keywords = False
    config.syntax_options.single_line_comment = "#"

    # Save configuration
    config.save("demo_gulfturtle.json")
    print("\n✓ Created GulfTurtle configuration")
    print("  - Saved to: demo_gulfturtle.json")
    print("  - Added 6 turtle graphics functions")
    print("  - Simple, imperative syntax")

    # Example code
    example = """
    # Draw a square
    to square :size {
      forward :size
      right 90
      forward :size
      right 90
      forward :size
      right 90
      forward :size
    }

    square 100
    """
    print("\n  Example GulfTurtle code:")
    print("  " + "\n  ".join(example.strip().split("\n")))

    return config


def demo_sql_like_language():
    """Create a SQL-inspired data query language."""
    print("\n" + "=" * 70)
    print("DEMO 3: Creating a SQL-Like Query Language")
    print("=" * 70)

    config = LanguageConfig(
        name="GulfQL",
        version="1.0.0",
        description="A SQL-inspired query language built on Gulf of Mexico",
        author="Language Construction Set Demo",
    )

    # SQL-style keywords (uppercase by convention)
    config.rename_keyword("function", "PROCEDURE")
    config.rename_keyword("if", "CASE")
    config.rename_keyword("when", "WHEN")
    config.rename_keyword("var", "DECLARE")
    config.rename_keyword("return", "RETURN")

    # Add SQL-style functions
    config.add_function(
        "SELECT",
        FunctionConfig(
            name="SELECT",
            arity=-1,  # Variadic
            description="Select data from dataset",
            enabled=True,
        ),
    )

    config.add_function(
        "FROM",
        FunctionConfig(
            name="FROM",
            arity=1,
            description="Specify data source",
            enabled=True,
        ),
    )

    config.add_function(
        "WHERE",
        FunctionConfig(
            name="WHERE",
            arity=1,
            description="Filter condition",
            enabled=True,
        ),
    )

    config.add_function(
        "JOIN",
        FunctionConfig(
            name="JOIN",
            arity=2,
            description="Join two datasets",
            enabled=True,
        ),
    )

    config.add_function(
        "GROUP_BY",
        FunctionConfig(
            name="GROUP_BY",
            arity=1,
            description="Group results by field",
            enabled=True,
        ),
    )

    config.add_function(
        "ORDER_BY",
        FunctionConfig(
            name="ORDER_BY",
            arity=1,
            description="Sort results by field",
            enabled=True,
        ),
    )

    # SQL uses semicolons
    config.syntax_options.require_semicolons = True
    config.syntax_options.statement_terminator = ";"
    config.syntax_options.enable_satirical_keywords = False

    # Save configuration
    config.save("demo_gulfql.json")
    print("\n✓ Created GulfQL configuration")
    print("  - Saved to: demo_gulfql.json")
    print("  - Added 6 SQL-like functions")
    print("  - Semicolon-terminated statements")

    # Example code
    example = """
    -- GulfQL Example
    DECLARE users;

    PROCEDURE getActiveUsers() {
      SELECT name, email, status
      FROM users
      WHERE status == "active"
      ORDER_BY name;
    }

    DECLARE results;
    results = getActiveUsers();
    """
    print("\n  Example GulfQL code:")
    print("  " + "\n  ".join(example.strip().split("\n")))

    return config


def demo_crud_operations():
    """Demonstrate CRUD operations on configurations."""
    print("\n" + "=" * 70)
    print("DEMO 4: CRUD Operations - Update, Delete, Merge")
    print("=" * 70)

    # Load an existing config
    config = LanguageConfig.load("demo_gulfql.json")
    print(f"Loaded: {config.name}")

    # UPDATE: Change metadata
    print("\n1. UPDATE: Changing metadata...")
    config.update(
        {
            "metadata": {
                "version": "2.0.0",
                "author": "CRUD Demo",
            }
        },
        merge=True,
    )
    print(f"   ✓ Updated version to {config.version}")
    print(f"   ✓ Updated author to {config.author}")

    # UPDATE: Add new function
    print("\n2. UPDATE: Adding new function...")
    config.update(
        {
            "functions": {
                "COUNT": {
                    "name": "COUNT",
                    "arity": 1,
                    "description": "Count rows",
                    "enabled": True,
                }
            }
        },
        merge=True,
    )
    print("   ✓ Added COUNT function")

    # DELETE: Remove a function
    print("\n3. DELETE: Removing a function...")
    if config.delete_function("GROUP_BY"):
        print("   ✓ Deleted GROUP_BY function")

    # DELETE: Remove a keyword
    print("\n4. DELETE: Removing a keyword...")
    if config.delete_keyword("when"):
        print("   ✓ Deleted 'when' keyword")

    # MERGE: Merge with another config
    print("\n5. MERGE: Merging with Turtle config...")
    turtle_config = LanguageConfig.load("demo_gulfturtle.json")
    original_func_count = len(config.builtin_functions)
    config.merge(turtle_config, prefer_other=False)
    new_func_count = len(config.builtin_functions)
    print("   ✓ Merged configurations")
    print(f"   ✓ Functions: {original_func_count} → {new_func_count}")

    # CLONE: Create a copy
    print("\n6. CLONE: Creating a deep copy...")
    cloned = config.clone()
    cloned.name = "GulfQL Extended"
    print("   ✓ Cloned configuration")
    print(f"   ✓ Original: {config.name}")
    print(f"   ✓ Clone: {cloned.name}")

    # DIFF: Compare configurations
    print("\n7. DIFF: Comparing original vs modified...")
    diff = config.diff(LanguageConfig.load("demo_gulfql.json"))
    print(f"   ✓ Functions added: {len(diff['functions']['added'])}")
    print(f"   ✓ Functions removed: {len(diff['functions']['removed'])}")
    print(f"   ✓ Keywords removed: {len(diff['keywords']['removed'])}")

    # Save result
    config.save("demo_gulfql_modified.json")
    print("\n   ✓ Saved modified config to: demo_gulfql_modified.json")


def demo_extreme_customization():
    """Create an extremely customized language - almost unrecognizable."""
    print("\n" + "=" * 70)
    print("DEMO 5: Extreme Customization - Minimal Assembly-Like Language")
    print("=" * 70)

    config = LanguageConfig(
        name="GulfASM",
        version="1.0.0",
        description="Assembly-like minimalist language",
        author="Extreme Demo",
    )

    # Remove ALL default keywords
    keywords_to_delete = list(config.keyword_mappings.keys())
    for kw in keywords_to_delete:
        config.delete_keyword(kw)

    print(f"✓ Deleted all {len(keywords_to_delete)} default keywords")

    # Add only minimal assembly-like keywords
    config.keyword_mappings = {
        "mov": KeywordMapping("mov", "mov", "instruction", "Move value to register"),
        "add": KeywordMapping("add", "add", "instruction", "Add values"),
        "sub": KeywordMapping("sub", "sub", "instruction", "Subtract values"),
        "jmp": KeywordMapping("jmp", "jmp", "control", "Jump to label"),
        "cmp": KeywordMapping("cmp", "cmp", "instruction", "Compare values"),
        "label": KeywordMapping("label", "label", "control", "Define label"),
        "call": KeywordMapping("call", "call", "control", "Call procedure"),
        "ret": KeywordMapping("ret", "ret", "control", "Return from procedure"),
    }

    print(f"✓ Added {len(config.keyword_mappings)} assembly-like keywords")

    # Remove all built-in functions except essentials
    functions_to_delete = list(config.builtin_functions.keys())
    for func in functions_to_delete:
        config.delete_function(func)

    # Add minimal functions
    config.add_function(
        "syscall",
        FunctionConfig(
            name="syscall",
            arity=-1,
            description="System call",
            enabled=True,
        ),
    )

    # Minimal syntax
    config.syntax_options = SyntaxOptions(
        array_start_index=0,
        allow_fractional_indexing=False,
        flexible_quoting=False,
        string_interpolation=False,
        single_line_comment=";",
        multi_line_comment_start=None,
        multi_line_comment_end=None,
        require_semicolons=False,
        statement_terminator="",
        three_valued_logic=False,
        probabilistic_variables=False,
        temporal_variables=False,
        enable_satirical_keywords=False,
        enable_quantum_features=False,
        enable_time_travel=False,
        enable_gaslighting=False,
    )

    config.save("demo_gulfasm.json")
    print("\n✓ Created GulfASM configuration")
    print("  - Saved to: demo_gulfasm.json")
    print(f"  - {len(config.keyword_mappings)} keywords (vs 61 default)")
    print(f"  - {len(config.builtin_functions)} functions (vs 35 default)")
    print("  - All satirical features disabled")

    # Example code
    example = """
    ; GulfASM Example - Minimal assembly-like syntax
    label start
      mov r1 0
      mov r2 10

    label loop
      add r1 1
      cmp r1 r2
      jmp loop

      call print_result
      ret

    label print_result
      syscall write r1
      ret
    """
    print("\n  Example GulfASM code:")
    print("  " + "\n  ".join(example.strip().split("\n")))

    return config


def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("ADVANCED LANGUAGE CONSTRUCTION SET DEMO")
    print("Creating Entirely New Programming Languages")
    print("=" * 70)

    demos = [
        ("Lisp-Like Language", demo_lisp_like_language),
        ("Logo/Turtle Language", demo_logo_like_language),
        ("SQL-Like Language", demo_sql_like_language),
        ("Extreme Customization", demo_extreme_customization),
        ("CRUD Operations", demo_crud_operations),  # Run after files are created
    ]

    results = []
    for name, demo_func in demos:
        try:
            result = demo_func()
            results.append((name, "✓ SUCCESS", result))
        except Exception as e:
            results.append((name, f"✗ ERROR: {e}", None))
            import traceback

            traceback.print_exc()

    # Summary
    print("\n" + "=" * 70)
    print("DEMO SUMMARY")
    print("=" * 70)

    for name, status, config in results:
        print(f"{status} - {name}")

    print("\nGenerated Files:")
    print("  ✓ examples/configs/demo_gulplisp.json - Lisp-like language")
    print("  ✓ examples/configs/demo_gulfturtle.json - Turtle graphics language")
    print("  ✓ examples/configs/demo_gulfql.json - SQL-like query language")
    print("  ✓ examples/configs/demo_gulfql_modified.json - Modified via CRUD ops")
    print("  ✓ examples/configs/demo_gulfasm.json - Minimal assembly-like language")

    print("\n" + "=" * 70)
    print("Try loading these configs:")
    print("  python gomconfig.py info examples/configs/demo_gulplisp.json")
    print("  python gomconfig.py validate examples/configs/demo_gulfturtle.json")
    print("  python gomconfig.py diff examples/configs/demo_gulfql.json examples/configs/demo_gulfql_modified.json")
    print("=" * 70)


if __name__ == "__main__":
    main()
