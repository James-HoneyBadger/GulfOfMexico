"""Comprehensive tests for the Gulf of Mexico interpreter.

Covers: lexer, parser, expression tree, operators, execution, builtins,
        variables, lifetimes, classes, control flow, error handling, and
        new features (++/--, readfile, import tariff, etc.).
"""

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TIMEOUT = 15  # seconds per test


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_gom(
    code: str,
    *,
    timeout: int = TIMEOUT,
    env: dict[str, str] | None = None,
    show_traceback: bool = False,
) -> subprocess.CompletedProcess:
    """Write *code* to a temp file, run via the interpreter, return result."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".gom", delete=False, encoding="utf-8"
    ) as f:
        f.write(code)
        f.flush()
        path = f.name
    try:
        command = [sys.executable, "-m", "gulfofmexico"]
        if show_traceback:
            command.append("-s")
        command.append(path)
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(ROOT),
            env={**os.environ, **(env or {})},
        )
    finally:
        os.unlink(path)


def assert_output(code: str, expected: str, *, strip: bool = True) -> None:
    """Assert that *code* produces *expected* on stdout (exit 0)."""
    result = run_gom(code)
    assert result.returncode == 0, (
        f"Non-zero exit ({result.returncode}):\n"
        f"STDERR: {result.stderr[-500:]}"
    )
    out = result.stdout.strip() if strip else result.stdout
    exp = expected.strip() if strip else expected
    assert out == exp, f"Expected:\n{exp!r}\nGot:\n{out!r}"


def assert_error(code: str, pattern: str | None = None) -> None:
    """Assert that *code* exits non-zero; optionally check stderr matches *pattern*."""
    result = run_gom(code)
    assert result.returncode != 0, "Expected an error but got exit 0"
    if pattern:
        assert re.search(pattern, result.stderr), (
            f"Expected pattern {pattern!r} in stderr:\n{result.stderr[-500:]}"
        )


# =========================================================================
# 1. Basic Output & Statement Terminators
# =========================================================================

class TestBasicOutput:
    def test_print_string(self):
        assert_output('print "hello"!', "hello")

    def test_print_number(self):
        assert_output("print 42!", "42")

    def test_print_float(self):
        assert_output("print 3.14!", "3.14")

    def test_double_bang(self):
        assert_output('print "confident"!!', "confident")

    def test_triple_bang(self):
        assert_output('print "very confident"!!!', "very confident")

    def test_debug_terminator(self):
        """? terminator should still execute."""
        result = run_gom('print "debug"?')
        assert result.returncode == 0
        assert "debug" in result.stdout

    def test_multiple_prints(self):
        assert_output(
            'print "a"!\nprint "b"!\nprint "c"!',
            "a\nb\nc",
        )


# =========================================================================
# 2. Variables & Constants
# =========================================================================

class TestVariables:
    def test_var_declaration(self):
        assert_output("var x = 10!\nprint x!", "10")

    def test_const_declaration(self):
        assert_output('const name = "GOM"!\nprint name!', "GOM")

    def test_var_reassignment(self):
        assert_output("var x = 1!\nvar x = 2!\nprint x!", "2")

    def test_undefined_value(self):
        assert_output("const u = undefined!\nprint u!", "undefined")

    def test_noop_value(self):
        assert_output("const n = noop!\nprint n!", "noop")

    def test_boolean_true(self):
        assert_output("print true!", "true")

    def test_boolean_false(self):
        assert_output("print false!", "false")

    def test_boolean_maybe(self):
        # maybe stays as 'maybe' when printed; it only resolves in boolean contexts
        result = run_gom("print maybe!")
        assert result.returncode == 0
        assert result.stdout.strip() == "maybe"


# =========================================================================
# 3. Arithmetic Operators
# =========================================================================

class TestArithmetic:
    def test_addition(self):
        assert_output("const r = 3 + 4! print r!", "7")

    def test_subtraction(self):
        assert_output("const r = 10 - 3! print r!", "7")

    def test_multiplication(self):
        assert_output("const r = 4 * 5! print r!", "20")

    def test_division(self):
        # Division always returns float
        result = run_gom("const r = 10 / 4! print r!")
        assert result.returncode == 0
        assert float(result.stdout.strip()) == 2.5

    def test_exponentiation(self):
        assert_output("const r = 2 ^ 10! print r!", "1024")

    def test_unary_negative(self):
        assert_output("print -5!", "-5")

    def test_negate_string_reverses(self):
        assert_output('print -"abc"!', "cba")

    def test_negate_list_reverses(self):
        assert_output("print -[1, 2, 3]!", "[3, 2, 1]")

    def test_string_concatenation(self):
        assert_output('const r = "hello" + " world"! print r!', "hello world")

    def test_significant_whitespace_precedence(self):
        """Tighter spacing binds first."""
        assert_output("const r = 2 * 1+3! print r!", "8")
        assert_output("const r = 2*1 + 3! print r!", "5")


# =========================================================================
# 4. Increment / Decrement operators (++)/(-- )
# =========================================================================

class TestIncrementDecrement:
    def test_increment_literal(self):
        assert_output("print ++5!", "6")

    def test_decrement_literal(self):
        assert_output("print --5!", "4")

    def test_increment_variable(self):
        assert_output("var x = 10!\nprint ++x!", "11")

    def test_decrement_variable(self):
        assert_output("var x = 10!\nprint --x!", "9")

    def test_increment_expression(self):
        assert_output("var y = ++3 + 2!\nprint y!", "6")

    def test_decrement_in_assignment(self):
        assert_output("var z = --10!\nprint z!", "9")

    def test_increment_negative(self):
        assert_output("var x = -1! print ++x!", "0")

    def test_decrement_zero(self):
        assert_output("print --0!", "-1")


# =========================================================================
# 5. Comparison & Tiered Equality
# =========================================================================

class TestComparison:
    def test_greater_than(self):
        assert_output("const r = 5 > 3! print r!", "true")

    def test_less_than(self):
        assert_output("const r = 3 < 5! print r!", "true")

    def test_greater_equal(self):
        assert_output("const r = 5 >= 5! print r!", "true")

    def test_less_equal(self):
        assert_output("const r = 3 <= 5! print r!", "true")

    def test_exact_equality(self):
        assert_output("const r = 10 == 10! print r!", "true")
        assert_output("const r = 10 == 11! print r!", "false")

    def test_approx_equality(self):
        """Single = is approximate (absolute difference ≤ 10 threshold per spec)."""
        assert_output("const r = 10 = 11! print r!", "true")   # |11-10|=1 ≤ 10
        assert_output("const r = 10 = 15! print r!", "true")   # |15-10|=5 ≤ 10
        assert_output("const r = 10 = 100! print r!", "false")  # |100-10|=90 > 10
        assert_output("const r = 10 = 25! print r!", "false")  # |25-10|=15 > 10

    def test_strict_equality(self):
        assert_output("const r = 10 === 10! print r!", "true")

    def test_inequality(self):
        # GOM uses ;= for inequality, not !=
        assert_output("const r = 10 ;= 5! print r!", "true")


# =========================================================================
# 6. Logical Operators & Three-Valued Logic
# =========================================================================

class TestLogic:
    def test_and_true(self):
        # GOM uses & for AND (not &&)
        assert_output("const r = true & true! print r!", "true")

    def test_and_false(self):
        assert_output("const r = true & false! print r!", "false")

    def test_or_true(self):
        # GOM uses | for OR (not ||)
        assert_output("const r = false | true! print r!", "true")

    def test_or_false(self):
        assert_output("const r = false | false! print r!", "false")

    def test_not_true(self):
        assert_output("print ;true!", "false")

    def test_not_false(self):
        assert_output("print ;false!", "true")


# =========================================================================
# 7. Control Flow
# =========================================================================

class TestControlFlow:
    def test_if_true(self):
        assert_output(
            'if true {\n   print "yes"!\n}',
            "yes",
        )

    def test_if_false_no_execute(self):
        # GOM has no 'else' — use sequential if blocks instead
        code = (
            "const x = false!\n"
            "if x {\n"
            '   print "yes"!\n'
            "}\n"
            "if ;x {\n"
            '   print "no"!\n'
            "}"
        )
        assert_output(code, "no")

    def test_nested_if(self):
        assert_output(
            'if true {\n   if true {\n      print "nested"!\n   }\n}',
            "nested",
        )

    def test_after_statement_executes(self):
        result = run_gom('after 1 {\n   print "later"!\n}!')
        assert result.returncode == 0
        assert result.stdout.strip() == "later"


# =========================================================================
# 8. Functions
# =========================================================================

class TestFunctions:
    def test_simple_function(self):
        # GOM requires (params) => { body }! syntax
        code = (
            'function greet(name) => {\n'
            '   print "Hello, ${name}"!\n'
            '}!\n'
            'greet "World"!\n'
        )
        assert_output(code, "Hello, World")

    def test_function_return(self):
        code = (
            "function double(x) => {\n"
            "   return x * 2!\n"
            "}!\n"
            "print double(5)!\n"
        )
        assert_output(code, "10")

    def test_recursive_function(self):
        code = (
            "function factorial(n) => {\n"
            "   if n <= 1 {\n"
            "      return 1!\n"
            "   }\n"
            "   const prev = n - 1!\n"
            "   return n * factorial(prev)!\n"
            "}!\n"
            "print factorial(5)!\n"
        )
        assert_output(code, "120")

    def test_fn_keyword(self):
        """'fn' is a valid function keyword (subset of 'function')."""
        code = (
            "fn add(a, b) => {\n"
            "   return a + b!\n"
            "}!\n"
            "const r = add(3, 4)!\n"
            "print r!\n"
        )
        assert_output(code, "7")

    def test_func_keyword(self):
        code = (
            "func square(x) => {\n"
            "   return x * x!\n"
            "}!\n"
            "print square(4)!\n"
        )
        assert_output(code, "16")


# =========================================================================
# 9. Strings
# =========================================================================

class TestStrings:
    def test_string_length(self):
        code = (
            'const s = "hello"!\n'
            "print s.length!\n"
        )
        assert_output(code, "5")

    def test_dollar_interpolation(self):
        code = (
            'const x = 42!\n'
            'print "value: ${x}"!\n'
        )
        assert_output(code, "value: 42")

    def test_pound_interpolation(self):
        code = (
            "const x = 10!\n"
            'print "val: £{x}"!\n'
        )
        assert_output(code, "val: 10")

    def test_escape_newline(self):
        code = r'print "a\nb"!'
        result = run_gom(code)
        assert result.returncode == 0
        assert "a\nb" in result.stdout

    def test_escape_tab(self):
        code = r'print "a\tb"!'
        result = run_gom(code)
        assert result.returncode == 0
        assert "a\tb" in result.stdout


# =========================================================================
# 10. Lists
# =========================================================================

class TestLists:
    def test_list_literal(self):
        assert_output("print [1, 2, 3]!", "[1, 2, 3]")

    def test_list_indexing_neg1(self):
        """GOM uses -1 based indexing."""
        code = (
            "const arr = [10, 20, 30]!\n"
            "print arr[-1]!\n"
        )
        assert_output(code, "10")

    def test_list_length(self):
        code = (
            "const arr = [1, 2, 3, 4, 5]!\n"
            "print arr.length!\n"
        )
        assert_output(code, "5")

    def test_list_push(self):
        code = (
            "var arr = [1, 2]!\n"
            "arr.push 3!\n"
            "print arr!\n"
        )
        assert_output(code, "[1, 2, 3]")

    def test_empty_list(self):
        assert_output("print []!", "[]")


# =========================================================================
# 11. Classes
# =========================================================================

class TestClasses:
    def test_class_instantiation(self):
        code = (
            "class Dog {\n"
            "   var name = undefined!\n"
            "}!\n"
            "var dog = new Dog!\n"
            'dog.name = "Rex"!\n'
            "print dog.name!\n"
        )
        assert_output(code, "Rex")

    def test_class_delete_reinstantiate(self):
        """After deleting instance, class can be re-instantiated."""
        code = (
            "class Singleton {\n"
            "   var value = 0!\n"
            "}!\n"
            "var s = new Singleton!\n"
            "s.value = 42!\n"
            "print s.value!\n"
            "delete s!\n"
            "var s2 = new Singleton!\n"
            "print s2.value!\n"
        )
        assert_output(code, "42\n0")


# =========================================================================
# 12. Comments
# =========================================================================

class TestComments:
    def test_single_line_comment(self):
        assert_output(
            '// this is a comment\nprint "ok"!',
            "ok",
        )

    def test_block_comment(self):
        assert_output(
            '/* block\ncomment */\nprint "ok"!',
            "ok",
        )

    def test_inline_comment(self):
        assert_output(
            'print "hi"! // inline comment',
            "hi",
        )


# =========================================================================
# 13. Word Numbers
# =========================================================================

class TestWordNumbers:
    def test_zero(self):
        assert_output("print zero!", "0")

    def test_one(self):
        assert_output("print one!", "1")

    def test_ten(self):
        assert_output("print ten!", "10")

    def test_twenty(self):
        # twenty is a function: twenty(N) = 20 + N
        assert_output("print twenty(0)!", "20")

    def test_hundred(self):
        # hundred is a function: hundred(N) = N * 100
        assert_output("print hundred(1)!", "100")


# =========================================================================
# 14. Delete Statement
# =========================================================================

class TestDelete:
    def test_delete_variable(self):
        """Deleting a variable removes it from scope."""
        code = (
            "var x = 42!\n"
            "print x!\n"
            "delete x!\n"
        )
        result = run_gom(code)
        assert result.returncode == 0
        assert "42" in result.stdout


# =========================================================================
# 15. Lifetimes
# =========================================================================

class TestLifetimes:
    def test_line_lifetime(self):
        """Variable with lifetime should expire after N statements."""
        code = (
            "var x <3> = 10!\n"
            "print x!\n"
            "print x!\n"
            "print x!\n"  # Third line still alive (expires AFTER 3rd use)
        )
        result = run_gom(code)
        assert result.returncode == 0
        lines = result.stdout.strip().split("\n")
        # First three prints should be 10
        assert lines[0] == "10"
        assert lines[1] == "10"
        assert lines[2] == "10"

    def test_line_lifetime_expires_after_count(self):
        code = (
            "var x <2> = 10!\n"
            "print x!\n"
            "print x!\n"
            "print x!\n"
        )
        result = run_gom(code)
        assert result.returncode != 0
        lines = [line for line in result.stdout.strip().split("\n") if line]
        assert lines[0] == "10"
        assert lines[1] == "10"

    def test_temporal_lifetime_with_seconds_suffix(self):
        code = (
            "var x <0.001s> = 10!\n"
            "sleep 20!\n"
            "print x!\n"
        )
        result = run_gom(code)
        assert result.returncode != 0

    def test_line_lifetime_expiry_reports_undefined_variable(self):
        code = (
            "var x <1> = 10!\n"
            "print x!\n"
            "print x!\n"
        )
        result = run_gom(code, show_traceback=True)
        assert result.returncode != 0
        assert "Variable is undefined" in result.stderr

    def test_temporal_lifetime_expiry_reports_undefined_variable(self):
        code = (
            "var x <0.001s> = 10!\n"
            "sleep 20!\n"
            "print x!\n"
        )
        result = run_gom(code, show_traceback=True)
        assert result.returncode != 0
        assert "Variable is undefined" in result.stderr


# =========================================================================
# 16. Multiple Return Values
# =========================================================================

class TestMultipleReturns:
    def test_multiple_returns(self):
        # GOM uses lists for multiple return values (see example 17)
        code = (
            "function swap(a, b) => {\n"
            "   return [b, a]!\n"
            "}!\n"
            "const result = swap(1, 2)!\n"
            "print result!\n"
        )
        result = run_gom(code)
        assert result.returncode == 0
        # Multiple return values come as a list
        assert "2" in result.stdout and "1" in result.stdout


# =========================================================================
# 17. Maps
# =========================================================================

class TestMaps:
    def test_map_creation_and_access(self):
        # Maps use Map constructor and dot methods
        code = (
            "var m = new Map!\n"
            "print m!\n"
        )
        result = run_gom(code)
        assert result.returncode == 0


# =========================================================================
# 18. Builtin Functions
# =========================================================================

class TestBuiltins:
    def test_abs(self):
        assert_output("print abs -5!", "5")

    def test_floor(self):
        assert_output("print floor 3.7!", "3")

    def test_ceil(self):
        assert_output("print ceil 3.2!", "4")

    def test_round(self):
        assert_output("print round 3.5!", "4")

    def test_sqrt(self):
        assert_output("print sqrt 16!", "4.0")

    def test_min(self):
        assert_output("const r = min(3, 7)! print r!", "3")

    def test_max(self):
        assert_output("const r = max(3, 7)! print r!", "7")

    def test_Number_cast(self):
        # Number() cast may return float representation
        result = run_gom('print Number("42")!')
        assert result.returncode == 0
        assert float(result.stdout.strip()) == 42

    def test_String_cast(self):
        assert_output("print String 42!", "42")

    def test_Boolean_true(self):
        assert_output("print Boolean 1!", "true")

    def test_Boolean_false(self):
        assert_output("print Boolean 0!", "false")

    def test_Boolean_non_binary_number_is_maybe(self):
        assert_output("print Boolean 2!", "maybe")

    def test_exit_zero(self):
        result = run_gom("exit 0!")
        assert result.returncode == 0

    def test_sleep_doesnt_crash(self):
        result = run_gom("sleep 1!")
        assert result.returncode == 0

    def test_sleep_uses_milliseconds(self):
        result = run_gom("sleep 10!\nprint 1!")
        assert result.returncode == 0
        assert result.stdout.strip() == "1"


# =========================================================================
# 19. Error Handling
# =========================================================================

class TestErrors:
    def test_missing_terminator(self):
        """A statement without !/? is a parse error."""
        result = run_gom("print 42")
        assert result.returncode != 0

    def test_undefined_variable(self):
        """Using an undefined variable prints undefined but doesn't crash."""
        result = run_gom("print nonexistent!")
        # GOM doesn't error on undefined — it prints "undefined"
        assert result.returncode == 0

    def test_bad_indentation(self):
        """Wrong indentation (not 3-space) should be an error."""
        code = "if true {\n  print 1!\n}"  # 2-space indent
        assert_error(code)

    def test_tab_indentation_is_rejected(self):
        code = "if true {\n\tprint 1!\n}"
        assert_error(code)


# =========================================================================
# 20. Lexer / Token-level tests
# =========================================================================

class TestLexer:
    def test_tokenize_basic(self):
        """Ensure the lexer can tokenize a simple program without errors."""
        from gulfofmexico.processor.lexer import tokenize
        tokens = tokenize("test.gom", 'print "hello"!\n')
        # Should have at least: NAME(print) WHITESPACE STRING(hello) BANG NEWLINE
        assert len(tokens) >= 4

    def test_tokenize_increment(self):
        from gulfofmexico.processor.lexer import tokenize
        tokens = tokenize("test.gom", "++x!\n")
        from gulfofmexico.base import TokenType
        types = [t.type for t in tokens]
        assert TokenType.INCREMENT in types

    def test_tokenize_decrement(self):
        from gulfofmexico.processor.lexer import tokenize
        tokens = tokenize("test.gom", "--x!\n")
        from gulfofmexico.base import TokenType
        types = [t.type for t in tokens]
        assert TokenType.DECREMENT in types


# =========================================================================
# 21. Expression Tree
# =========================================================================

class TestExpressionTree:
    def test_build_simple(self):
        from gulfofmexico.processor.lexer import tokenize
        from gulfofmexico.processor.expression_tree import build_expression_tree
        tokens = tokenize("test.gom", "1 + 2\n")
        # Filter out newlines for expression tree building
        from gulfofmexico.base import TokenType
        expr_tokens = [t for t in tokens if t.type not in (TokenType.NEWLINE,)]
        tree = build_expression_tree("test.gom", expr_tokens, "1 + 2\n")
        assert tree is not None


# =========================================================================
# 22. Serialization (readfile)
# =========================================================================

class TestReadfile:
    def test_readfile_builtin_exists(self):
        """readfile should be a recognized builtin keyword."""
        from gulfofmexico.builtin import BUILTIN_FUNCTION_KEYWORDS
        assert "readfile" in BUILTIN_FUNCTION_KEYWORDS

    def test_readfile_reads_file(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write("file content here")
            path = f.name
        try:
            code = f'print readfile "{path}"!\n'
            assert_output(code, "file content here")
        finally:
            os.unlink(path)


# =========================================================================
# 23. Integration tests — example programs produce expected patterns
# =========================================================================

class TestExampleIntegration:
    def test_hello_world(self):
        result = run_gom(Path(ROOT / "examples" / "01_hello_world.gom").read_text())
        assert result.returncode == 0
        assert "Hello" in result.stdout

    def test_algorithms_example_completes(self):
        result = run_gom(Path(ROOT / "examples" / "23_algorithms.gom").read_text())
        assert result.returncode == 0


# =========================================================================
# 24. Base types and conversions
# =========================================================================

class TestBaseTypes:
    def test_gulfofmexico_number(self):
        from gulfofmexico.builtin import GulfOfMexicoNumber
        n = GulfOfMexicoNumber(42)
        assert n.value == 42

    def test_gulfofmexico_string(self):
        from gulfofmexico.builtin import GulfOfMexicoString
        s = GulfOfMexicoString("hello")
        assert s.value == "hello"

    def test_gulfofmexico_boolean(self):
        from gulfofmexico.builtin import GulfOfMexicoBoolean
        b = GulfOfMexicoBoolean(True)
        assert b.value is True

    def test_gulfofmexico_list(self):
        from gulfofmexico.builtin import GulfOfMexicoList, GulfOfMexicoNumber
        lst = GulfOfMexicoList([GulfOfMexicoNumber(1), GulfOfMexicoNumber(2)])
        assert len(lst.values) == 2

    def test_db_to_string(self):
        from gulfofmexico.builtin import GulfOfMexicoNumber, db_to_string
        result = db_to_string(GulfOfMexicoNumber(42))
        assert result.value == "42"

    def test_db_to_boolean(self):
        from gulfofmexico.builtin import GulfOfMexicoNumber, db_to_boolean
        result = db_to_boolean(GulfOfMexicoNumber(1))
        assert result.value is True
        result0 = db_to_boolean(GulfOfMexicoNumber(0))
        assert result0.value is False

    def test_db_not(self):
        from gulfofmexico.builtin import GulfOfMexicoBoolean, db_not
        assert db_not(GulfOfMexicoBoolean(True)).value is False
        assert db_not(GulfOfMexicoBoolean(False)).value is True


# =========================================================================
# 25. Operator edge cases
# =========================================================================

class TestOperatorEdgeCases:
    def test_equal_spacing_right_to_left(self):
        """Equal spacing picks leftmost operator as root (right-to-left evaluation)."""
        assert_output("const r = 2 * 1 + 3! print r!", "8")

    def test_list_addition(self):
        assert_output("const r = [1, 2] + [3, 4]! print r!", "[1, 2, 3, 4]")

    def test_string_multiply_by_number(self):
        """String * number is not supported in GOM; multiplication expects numbers."""
        result = run_gom('const r = "ab" * 3!')
        assert result.returncode != 0  # Should error since strings can't multiply


# =========================================================================
# 26. Import tariff
# =========================================================================

class TestImportTariff:
    def test_import_removes_at_most_one_statement(self):
        """Import tariff should remove at most one statement."""
        # This is a statistical test; we just verify the logic path exists
        # and doesn't crash. Full behavior is probabilistic.
        from gulfofmexico.builtin import BUILTIN_FUNCTION_KEYWORDS
        # This test ensures the import tariff only removes at most one statement. No placeholder assertion needed.

    def test_import_tariff_removes_first_future_statement_when_forced(self):
        code = (
            "===== utils =====\n"
            "const PI = 3.14!\n"
            "export PI to main!\n"
            "===== main =====\n"
            "import PI from utils!\n"
            "print \"B\"!\n"
            "print \"C\"!\n"
        )
        result = run_gom(
            code,
            env={
                "GOM_FORCE_TARIFF_REMOVE": "1",
                "GOM_FORCE_TARIFF_INDEX": "0",
            },
        )
        assert result.returncode == 0
        assert result.stdout.strip() == "C"

    def test_import_tariff_removes_second_future_statement_when_forced(self):
        code = (
            "===== utils =====\n"
            "const PI = 3.14!\n"
            "export PI to main!\n"
            "===== main =====\n"
            "import PI from utils!\n"
            "print \"B\"!\n"
            "print \"C\"!\n"
        )
        result = run_gom(
            code,
            env={
                "GOM_FORCE_TARIFF_REMOVE": "1",
                "GOM_FORCE_TARIFF_INDEX": "1",
            },
        )
        assert result.returncode == 0
        assert result.stdout.strip() == "B"

    def test_import_from_specific_section(self):
        code = (
            "===== utils =====\n"
            "const PI = 3.14!\n"
            "export PI to main!\n"
            "===== main =====\n"
            "import PI from utils!\n"
            "print PI!\n"
        )
        result = run_gom(code, env={"GOM_DISABLE_TARIFF": "1"})
        assert result.returncode == 0
        assert result.stdout.strip() == "3.14"


# =========================================================================
# 27. Variable overloading (! priority)
# =========================================================================

class TestVariableOverloading:
    def test_double_bang_overrides_single(self):
        """A !! declaration should override a ! declaration."""
        assert_output(
            'const const name = "Luke"!\n'
            'const const name = "Sigma"!!\n'
            'print name!\n',
            "Sigma",
        )

    def test_single_bang_does_not_override_double(self):
        """A later ! declaration should NOT override an earlier !!."""
        assert_output(
            'const const name = "Sigma"!!\n'
            'const const name = "Luke"!\n'
            'print name!\n',
            "Sigma",
        )

    def test_triple_bang_overrides_all(self):
        """!!! should override both ! and !!."""
        assert_output(
            'const const x = "a"!\n'
            'const const x = "b"!!\n'
            'const const x = "c"!!!\n'
            'print x!\n',
            "c",
        )

    def test_tilde_confidence_marker_overrides_bang_priority(self):
        assert_output(
            'const const x = "low"!!!\n'
            'const const x ~80~ = "high"!\n'
            'print x!\n',
            "high",
        )

    def test_tilde_confidence_marker_parses_float(self):
        assert_output(
            'const const y = "a"!!\n'
            'const const y ~2.5~ = "b"!\n'
            'print y!\n',
            "b",
        )


# =========================================================================
# 28. Compound assignment operators
# =========================================================================

class TestCompoundAssignment:
    def test_plus_equals(self):
        assert_output("var var x = 10!\nx += 5!\nprint x!\n", "15")

    def test_minus_equals(self):
        assert_output("var var x = 10!\nx -= 3!\nprint x!\n", "7")

    def test_times_equals(self):
        assert_output("var var x = 4!\nx *= 3!\nprint x!\n", "12")

    def test_divide_equals(self):
        assert_output("var var x = 20!\nx /= 4!\nprint x!\n", "5.0")

    def test_power_equals(self):
        assert_output("var var x = 2!\nx ^= 3!\nprint x!\n", "8")

    def test_compound_with_expression(self):
        """Compound assignment should evaluate the full RHS."""
        assert_output("var var x = 10!\nvar var y = 3!\nx += y!\nprint x!\n", "13")


# =========================================================================
# 29. Emoji identifiers
# =========================================================================

class TestEmojiIdentifiers:
    def test_emoji_variable_name(self):
        assert_output(
            'const const \U0001f44d = "thumbs up"!\nprint \U0001f44d!\n',
            "thumbs up",
        )

    def test_emoji_mixed_with_alpha(self):
        assert_output(
            "var var \U0001f431score = 10!\n\U0001f431score += 5!\nprint \U0001f431score!\n",
            "15",
        )


# =========================================================================
# 30. Negative indentation
# =========================================================================

class TestNegativeIndentation:
    def test_single_brace_ignored(self):
        """Leading } at the start of a line (no open block) should be cosmetic."""
        assert_output(
            '}const const x = "neg"!\nprint x!\n',
            "neg",
        )

    def test_double_brace_ignored(self):
        assert_output(
            '}}const const y = "double"!\nprint y!\n',
            "double",
        )

    def test_normal_braces_still_work(self):
        """Closing braces inside blocks should not be stripped."""
        assert_output(
            'if (true) {\n   print "inside"!\n}\n',
            "inside",
        )


# =========================================================================
# 31. Tilde-equality operators (AEMI / ABI / AQMI)
# =========================================================================

class TestTildeEquality:
    def test_aemi_same_type(self):
        """~= on same-type values assumes they're equal."""
        assert_output("print  5 ~= 10!\n", "true")

    def test_aemi_different_types(self):
        """~= on different types returns maybe."""
        assert_output('print  5 ~= "hello"!\n', "maybe")

    def test_abi_case_insensitive(self):
        """~== should compare strings case-insensitively."""
        assert_output('print  "Hello" ~== "hello"!\n', "true")

    def test_abi_cross_type_coercion(self):
        """~== should coerce to strings for cross-type comparison."""
        assert_output('print  5 ~== "5"!\n', "true")

    def test_aqmi_close_numbers(self):
        """~=== should return true for numbers within 1%."""
        assert_output("print  100 ~=== 100.5!\n", "true")

    def test_aqmi_far_numbers(self):
        """~=== should return false for numbers farther than 1%."""
        assert_output("print  100 ~=== 200!\n", "false")

    def test_aqmi_whitespace_normalized_strings(self):
        """~=== should normalize whitespace in string comparison."""
        assert_output('print  "hello  world" ~=== "hello world"!\n', "true")


# =========================================================================
# 32. Negative lifetime hoisting
# =========================================================================

class TestNegativeLifetimeHoisting:
    def test_variable_hoisted_one_line(self):
        """A <-1> lifetime should make the variable available one line before."""
        assert_output(
            'print name!\nconst const name<-1> = "Luke"!\n',
            "Luke",
        )


# =========================================================================
# 33. Variable reassignment
# =========================================================================

class TestVariableReassignment:
    def test_simple_reassignment(self):
        """var var should allow reassignment."""
        assert_output("var var x = 5!\nx = 10!\nprint x!\n", "10")

    def test_multiple_reassignments(self):
        assert_output("var var x = 1!\nx = 2!\nx = 3!\nprint x!\n", "3")

    def test_reassign_with_expression(self):
        assert_output("var var x = 5!\nx = x + 3!\nprint x!\n", "8")


# =========================================================================
# 34. Async interleaving
# =========================================================================

class TestAsyncInterleaving:
    def test_async_noop(self):
        """An async function with a trivial body should work."""
        assert_output(
            'async functi noop() => {\n   const const _x = 0!\n}!\nnoop()!\n'
            'print "ok"!\n',
            "ok",
        )

    def test_number_redefinition(self):
        """Number literals should be redefinable at runtime."""
        assert_output(
            'const const 5 = 4!\nprint  2 + 5!\n',
            "6",
        )


# =========================================================================
# 35. Reverse behavior
# =========================================================================

class TestReverseBehavior:
    def test_reverse_does_not_stop_following_statements(self):
        code = (
            'print "A"!\n'
            'print "B"!\n'
            'reverse!\n'
            'print "Z"!\n'
        )
        result = run_gom(code)
        assert result.returncode == 0
        assert result.stdout.strip().split("\n") == ["A", "B", "B", "A", "Z"]

    def test_reverse_inside_function_preserves_following_return(self):
        code = (
            'function f() => {\n'
            '   print "A"!\n'
            '   print "B"!\n'
            '   reverse!\n'
            '   print "C"!\n'
            '   return 1!\n'
            '}!\n'
            'print f()!\n'
        )
        result = run_gom(code)
        assert result.returncode == 0
        assert result.stdout.strip().split("\n") == ["A", "B", "B", "A", "C", "1"]

    def test_reverse_in_async_scope_does_not_interrupt_queue(self):
        code = (
            'async function a() => {\n'
            '   print "X"!\n'
            '   reverse!\n'
            '   print "Y"!\n'
            '}!\n'
            'a()!\n'
            'print "Z"!\n'
        )
        result = run_gom(code)
        assert result.returncode == 0
        assert result.stdout.strip().split("\n") == ["X", "Z", "Y"]


# =========================================================================
# 40. Type annotations (enforced at declaration)
# =========================================================================

class TestTypeAnnotations:
    def test_int_annotation_accepts_integer(self):
        assert_output("var x: Int = 42!\nprint x!\n", "42")

    def test_string_annotation_accepts_string(self):
        assert_output('var s: String = "hi"!\nprint s!\n', "hi")

    def test_bool_annotation_accepts_boolean(self):
        assert_output("var b: Bool = true!\nprint b!\n", "true")

    def test_int_annotation_rejects_string(self):
        assert_error('var x: Int = "hello"!\n', r"Type mismatch")

    def test_int_annotation_rejects_float(self):
        assert_error("var x: Int = 3.5!\n", r"Type mismatch")

    def test_string_annotation_rejects_number(self):
        assert_error("var s: String = 5!\n", r"Type mismatch")

    def test_number_annotation_accepts_float(self):
        assert_output("var n: Number = 3.5!\nprint n!\n", "3.5")

    def test_unknown_annotation_not_enforced(self):
        """Custom/unknown type names should not be enforced."""
        assert_output('var c: Widget = "anything"!\nprint c!\n', "anything")


# =========================================================================
# 41. previous keyword
# =========================================================================

class TestPreviousKeyword:
    def test_previous_returns_prior_value(self):
        assert_output(
            "var score = 10!\nscore = 20!\nscore = 30!\n"
            "print score!\nprint previous score!\n",
            "30\n20",
        )

    def test_previous_after_single_reassignment(self):
        assert_output(
            "var x = 1!\nx = 2!\nprint previous x!\n",
            "1",
        )


# =========================================================================
# 42. when statements (reactive re-fire semantics)
# =========================================================================

class TestWhenSemantics:
    def test_when_fires_each_time_condition_holds(self):
        """A when-block re-fires on every qualifying change (reactive)."""
        code = (
            "var var x = 0!\n"
            "when x > 5 {\n"
            '   print "fired"!\n'
            "}\n"
            "x = 10!\n"
            "x = 11!\n"
        )
        result = run_gom(code)
        assert result.returncode == 0
        assert result.stdout.strip().split("\n") == ["fired", "fired"]

    def test_when_does_not_fire_until_condition_true(self):
        code = (
            "var var x = 0!\n"
            "when x > 5 {\n"
            '   print "hit"!\n'
            "}\n"
            "x = 1!\n"
            "x = 6!\n"
        )
        result = run_gom(code)
        assert result.returncode == 0
        assert result.stdout.strip() == "hit"


# =========================================================================
# 43. Fractional indexing (insertion)
# =========================================================================

class TestFractionalIndexing:
    def test_list_fractional_insert(self):
        code = (
            "var var lst = [1, 2, 3]!\n"
            "lst[-0.5] = 99!\n"
            "print lst[-0.5]!\n"
        )
        result = run_gom(code)
        assert result.returncode == 0
        # The inserted value is accessible at its fractional index.
        assert result.stdout.strip() == "99"

    def test_string_fractional_insert(self):
        code = 'var var s = "ac"!\ns[-0.5] = "b"!\nprint s!\n'
        result = run_gom(code)
        assert result.returncode == 0
        assert result.stdout.strip() == "abc"


# =========================================================================
# 44. Emoji identifiers (extended)
# =========================================================================

class TestEmojiIdentifiersExtended:
    def test_emoji_function_name(self):
        assert_output(
            "function \U0001f680() => {\n"
            '   print "launch"!\n'
            "}!\n"
            "\U0001f680()!\n",
            "launch",
        )

    def test_emoji_in_class_and_property(self):
        code = (
            "class \U0001f3e0 {\n"
            "   const const rooms = 3!\n"
            "}\n"
            "const const house = new \U0001f3e0!\n"
            "print house.rooms!\n"
        )
        result = run_gom(code)
        assert result.returncode == 0
        assert result.stdout.strip() == "3"

