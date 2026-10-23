"""Conformance tests for the DreamBerd (Gulf of Mexico) specification.

Each test corresponds to a rule from the upstream specification:
https://github.com/TodePond/GulfOfMexico
"""

import pytest

from tests.test_interpreter import assert_error, assert_output, run_gom


# ---------------------------------------------------------------------------
# Exclamation marks, AEMI, ABI, AQMI
# ---------------------------------------------------------------------------

class TestTerminatorsAndAutoInsertion:
    def test_single_bang(self):
        assert_output('print("Hello world")!', "Hello world")

    def test_multiple_bangs(self):
        assert_output('print("Hello world")!!!', "Hello world")

    def test_question_mark_still_runs(self):
        result = run_gom('print("Hello world")?')
        assert result.returncode == 0
        assert "Hello world" in result.stdout

    def test_semicolon_is_not(self):
        assert_output('if (;false) {\n   print("Hello world")!\n}', "Hello world")

    def test_aemi_inserts_missing_terminator(self):
        result = run_gom('print("Hello world")')
        assert result.returncode == 0
        assert result.stdout.strip() == "Hello world"

    def test_abi_inserts_missing_brackets(self):
        result = run_gom('print("Hello world"')
        assert result.returncode == 0
        assert result.stdout.strip() == "Hello world"

    def test_aqmi_closes_missing_quote(self):
        result = run_gom('print("Hello world')
        assert result.returncode == 0
        assert result.stdout.strip() == "Hello world"


# ---------------------------------------------------------------------------
# Declarations
# ---------------------------------------------------------------------------

class TestDeclarationForms:
    def test_const_const_is_immutable(self):
        assert_output('const const name = "Luke"!\nprint(name)!', "Luke")
        assert_error('const const name = "Luke"!\nname = "Lu"!')

    def test_const_var_can_be_edited_not_reassigned(self):
        assert_output(
            'const var name = "Luke"!\nname.pop()!\nname.pop()!\nprint(name)!',
            "Lu",
        )
        assert_error('const var name = "Luke"!\nname = "Lu"!')

    def test_var_const_can_be_reassigned_not_edited(self):
        assert_output(
            'var const name = "Luke"!\nname = "Lu"!\nprint(name)!',
            "Lu",
        )
        assert_error('var const name = "Luke"!\nname.pop()!')

    def test_var_var_can_be_both(self):
        assert_output(
            'var var name = "Luke"!\nname = "Lu"!\nname.push("k")!\nname.push("e")!\nprint(name)!',
            "Luke",
        )

    def test_const_const_const_persists(self):
        assert_output("const const const dreamb_pi = 3.14!\nprint(dreamb_pi)!", "3.14")

    def test_any_unicode_name(self):
        assert_output("var const 👍 = True!\nvar var 1️⃣ = 1!\nprint(1️⃣)!", "1")

    def test_number_as_name(self):
        assert_output("const const 5 = 4!\nprint(2 + 2 === 5)!", "true")

    def test_overloading_uses_latest(self):
        assert_output(
            'const const name = "Luke"!\nconst const name = "Lu"!\nprint(name)!',
            "Lu",
        )

    def test_more_bangs_win_overloading(self):
        assert_output(
            'const const name = "Lu"!!\nconst const name = "Luke"!\nprint(name)!',
            "Lu",
        )

    def test_inverted_bang_is_negative_priority(self):
        assert_output(
            'const const name = "Lu"!\nconst const name = "Luke"¡\nprint(name)!',
            "Lu",
        )


# ---------------------------------------------------------------------------
# Arrays and strings
# ---------------------------------------------------------------------------

class TestArraysAndStrings:
    def test_minus_one_indexing(self):
        assert_output(
            "const const scores = [3, 2, 5]!\n"
            "print(scores[-1])!\nprint(scores[0])!\nprint(scores[1])!",
            "3\n2\n5",
        )

    def test_float_index_inserts(self):
        assert_output(
            "const var scores = [3, 2, 5]!\nscores[0.5] = 4!\nprint(scores)!",
            "[3, 2, 4, 5]",
        )

    def test_quadruple_quotes(self):
        assert_output('const const name = """"Luke""""!\nprint(name)!', "Luke")

    def test_triple_quotes(self):
        assert_output("const const name = '''Lu'''!\nprint(name)!", "Lu")

    def test_double_quotes_empty_string(self):
        assert_output('print ""!', "")

    def test_quote_count_nesting(self):
        assert_output('const s = ""she said "hi"""!\nprint(s)!', 'she said "hi"')

    def test_zero_quote_string(self):
        assert_output("const const name = Luke!\nprint(name)!", "Luke")

    def test_strings_are_arrays(self):
        assert_output('const s = "hello"!\nprint(s.length)!', "5")


# ---------------------------------------------------------------------------
# Interpolation
# ---------------------------------------------------------------------------

class TestInterpolation:
    @pytest.mark.parametrize(
        "template,expected",
        [
            ('"Hello ${name}!"', "Hello world!"),
            ('"Hello £{name}!"', "Hello world!"),
            ('"Hello ¥{name}!"', "Hello world!"),
            ('"Hello {name}€!"', "Hello world!"),
        ],
    )
    def test_currency_interpolation(self, template, expected):
        assert_output(f'const const name = "world"!\nprint({template})!', expected)

    def test_cape_verdean_interpolation(self):
        assert_output(
            'const const player = { name: "Lu" }!\nprint("Hello {player$name}!")!',
            "Hello Lu!",
        )


# ---------------------------------------------------------------------------
# Equality
# ---------------------------------------------------------------------------

class TestEquality:
    def test_loose_equality_across_types(self):
        assert_output('print(3.14 == "3.14")!', "true")

    def test_precise_equality_rejects_other_types(self):
        assert_output('print(3.14 === "3.14")!', "false")

    def test_reference_equality_self(self):
        assert_output("const const pi = 3.14!\nprint(pi ==== pi)!", "true")

    def test_reference_equality_same_literal(self):
        assert_output("print(3.14 ==== 3.14)!", "true")

    def test_reference_equality_literal_vs_variable(self):
        assert_output("const const pi = 3.14!\nprint(3.14 ==== pi)!", "false")

    def test_approximate_equality(self):
        assert_output("print(3 = 3.14)!", "true")


# ---------------------------------------------------------------------------
# Whitespace and parentheses
# ---------------------------------------------------------------------------

class TestWhitespaceAndParentheses:
    def test_significant_whitespace(self):
        assert_output("print(1 + 2*3)!", "7")
        assert_output("print(1+2 * 3)!", "9")

    def test_equal_spacing_falls_back_to_precedence(self):
        assert_output("print(2 * 1 + 3)!", "5")

    def test_parenthesised_call(self):
        assert_output(
            "function add(a, b) => a + b!\nprint(add(3, 2))!",
            "5",
        )

    def test_parentheses_are_whitespace_style(self):
        prog = "function add(a, b) => a + b!\nconst r = add)3, 2(!\nprint(r)!"
        assert_output(prog, "5")

    def test_nested_parentheses(self):
        assert_output(
            "function add(a, b) => a + b!\nprint((add (3, (add (5, 6)))))!",
            "14",
        )


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

class TestFunctions:
    @pytest.mark.parametrize("keyword", ["function", "func", "fun", "fn", "functi", "f", "functn"])
    def test_any_letters_of_function_in_order(self, keyword):
        assert_output(f"{keyword} add(a, b) => a + b!\nprint(add(2, 3))!", "5")

    def test_expression_body(self):
        assert_output("fn double(n) => n * 2!\nprint(double(4))!", "8")


# ---------------------------------------------------------------------------
# Miscellaneous language semantics
# ---------------------------------------------------------------------------

class TestTypes:
    def test_generic_regexp_annotation(self):
        assert_output(
            'const const email: RegExp<[a-z]+@[a-z]+> = "a@b"!\nprint(email)!',
            "a@b",
        )

    def test_int9_annotation_is_accepted(self):
        assert_output("const var age: Int9 = 28!\nprint(age)!", "28")


class TestSemantics:
    def test_divide_by_zero_is_undefined(self):
        assert_output("print(3 / 0)!", "undefined")

    def test_postfix_increment_assigns(self):
        assert_output("var score = 5!\nscore++!\nprint(score)!", "6")

    def test_postfix_decrement_assigns(self):
        assert_output("var score = 5!\nscore--!\nprint(score)!", "4")

    def test_previous_after_postfix(self):
        assert_output("var score = 5!\nscore++!\nprint(previous score)!", "5")

    def test_current(self):
        assert_output("var score = 5!\nprint(current score)!", "5")

    def test_await_next_does_not_crash(self):
        result = run_gom("var score = 5!\nprint(await next score)!\nscore++!")
        assert result.returncode == 0

    def test_delete_primitive_value(self):
        result = run_gom("delete 3!\nprint(2 + 1)!")
        assert result.returncode != 0
        assert "3 has been deleted" in result.stderr

    def test_delete_keyword(self):
        result = run_gom("delete class!\nclass Zed {}")
        assert result.returncode != 0
        assert "class" in result.stderr

    def test_delete_delete(self):
        result = run_gom("delete delete!")
        assert result.returncode == 0

    def test_when_watcher(self):
        # A `when` block runs when the watched value mutates - not when the
        # block is registered, even if the condition is already true.
        result = run_gom(
            "var var health = 10!\n"
            "when (health == 0) {\n"
            '   print("You lose")!\n'
            "}\n"
            "health = 0!"
        )
        assert result.returncode == 0
        assert result.stdout.count("You lose") == 1


# ---------------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------------

class TestClasses:
    def test_only_one_instance(self):
        result = run_gom(
            "class Player {\n   const var health = 10!\n}\n"
            "const var p1 = new Player()!\n"
            "const var p2 = new Player()!"
        )
        assert result.returncode != 0
        assert "Can't have more than one 'Player' instance" in result.stderr

    def test_nested_class_declarations_are_independent(self):
        code = (
            "class PlayerMaker {\n"
            "   function makePlayer() => {\n"
            "      class Player {\n"
            "         const var health = 10!\n"
            "      }\n"
            "      const const player = new Player()!\n"
            "      return player!\n"
            "   }\n"
            "}\n"
            "const const maker = new PlayerMaker()!\n"
            "const var p1 = maker.makePlayer()!\n"
            "const var p2 = maker.makePlayer()!\n"
            "print(p1.health)!"
        )
        assert_output(code, "10")

    def test_class_name_keyword(self):
        assert_output(
            "className Player2 {\n   const var health = 10!\n}\n"
            "const p = new Player2()!\nprint(p.health)!",
            "10",
        )


# ---------------------------------------------------------------------------
# Signals, async, time
# ---------------------------------------------------------------------------

class TestReactive:
    def test_signal_get_set(self):
        assert_output("const var s = use(0)!\ns(9)!\nprint(s())!", "9")

    def test_signal_split(self):
        assert_output(
            "const var [getS, setS] = use(0)!\nsetS(9)!\nprint(getS())!",
            "9",
        )

    def test_async_takes_turns(self):
        assert_output(
            "async funct count() => {\n   print(1)!\n   print(3)!\n}\ncount()!\nprint(2)!",
            "1\n2\n3",
        )

    def test_noop_wastes_a_turn(self):
        assert_output(
            "async func count() => {\n   print(1)!\n   noop!\n   print(4)!\n}\n"
            "count()!\nprint(2)!\nprint(3)!",
            "1\n2\n3\n4",
        )

    def test_date_now_settable(self):
        assert_output("Date.now() -= 3600000!\nprint(\"ok\")!", "ok")


# ---------------------------------------------------------------------------
# Maps / object literals and file sections
# ---------------------------------------------------------------------------

class TestStructures:
    def test_map_literal_and_access(self):
        assert_output('const m = { a: 1, b: 2 }!\nprint(m["a"])!\nprint(m.b)!', "1\n2")

    def test_named_file_sections(self):
        assert_output(
            "======= add.gom =======\n"
            "function add(a, b) => a + b!\n"
            "print(add(1, 2))!",
            "3",
        )

    def test_export_import_between_sections(self):
        # The import tariff randomly deletes an imported statement, so
        # disable it for a deterministic assertion.
        result = run_gom(
            "===== add.gom ==\n"
            "function add(a, b) => {\n   return a + b!\n}\n"
            'export add to "main.gom"!\n'
            "===== main.gom ==\n"
            "import add!\n"
            "print(add(3, 2))!",
            env={"GOM_DISABLE_TARIFF": "1"},
        )
        assert result.returncode == 0
        assert result.stdout.strip() == "5"
