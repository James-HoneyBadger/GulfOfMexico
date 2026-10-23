"""Tests for the standard collection methods, prelude, and scheduler."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run_gom(code: str, *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".gom", delete=False, encoding="utf-8") as handle:
        handle.write(code)
        path = handle.name
    try:
        return subprocess.run(
            [sys.executable, "-m", "gulfofmexico", path],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(ROOT),
            env={**os.environ, **(env or {})},
        )
    finally:
        os.unlink(path)


def output_of(code: str, *, env: dict[str, str] | None = None) -> str:
    result = run_gom(code, env=env)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


class TestListMethods:
    def test_insert(self):
        assert output_of("var l = [1, 2]!\nl.insert(1, 9)!\nprint(l)!") == "[1, 2, 9]"

    def test_insert_at_start(self):
        assert output_of("var l = [1, 2]!\nl.insert(-1, 0)!\nprint(l)!") == "[0, 1, 2]"

    def test_index_of_and_contains(self):
        code = "const l = [10, 20, 30]!\nprint(l.indexOf(20))!\nprint(l.indexOf(99))!\nprint(l.contains(30))!"
        assert output_of(code) == "0\nundefined\ntrue"

    def test_slice_is_minus_one_based(self):
        code = "const l = [10, 20, 30, 40]!\nprint(l.slice(-1, 0))!\nprint(l.slice(0, 1))!"
        assert output_of(code) == "[10, 20]\n[20, 30]"

    def test_join(self):
        assert output_of('const l = ["a", "b", "c"]!\nprint(l.join("-"))!') == "a-b-c"

    def test_sort_and_reverse_mutate(self):
        code = "var l = [3, 1, 2]!\nl.sort()!\nprint(l)!\nl.reverse()!\nprint(l)!"
        assert output_of(code) == "[1, 2, 3]\n[3, 2, 1]"

    def test_sort_is_stable_and_mixed(self):
        code = 'var l = ["b", 2, "a", 1]!\nl.sort()!\nprint(l)!'
        assert output_of(code) == "[1, 2, a, b]"

    def test_length_updates(self):
        code = "var l = [1]!\nl.insert(0, 2)!\nprint(l.length)!"
        assert output_of(code) == "2"


class TestStringMethods:
    def test_split(self):
        assert output_of('print("a,b".split(","))!') == "[a, b]"

    def test_case_and_trim(self):
        assert output_of('print("  Hi  ".trim().upper())!') == "HI"

    def test_case_does_not_mutate(self):
        assert output_of('const s = "hi"!\nprint(s.upper())!\nprint(s)!') == "HI\nhi"

    def test_replace_returns_new_string(self):
        assert output_of('const s = "abc"!\nprint(s.replace("b", "X"))!\nprint(s)!') == "aXc\nabc"

    def test_contains_and_affixes(self):
        code = 'const s = "hello"!\nprint(s.contains("ell"))!\nprint(s.startsWith("he"))!\nprint(s.endsWith("lo"))!'
        assert output_of(code) == "true\ntrue\ntrue"

    def test_index_of_is_minus_one_based(self):
        assert output_of('print("abc".indexOf("c"))!') == "1"
        assert output_of('print("abc".indexOf("z"))!') == "undefined"


class TestMapMethods:
    def test_keys_values_and_length(self):
        code = "const m = { a: 1, b: 2 }!\nprint(m.keys())!\nprint(m.values())!\nprint(m.length)!"
        assert output_of(code) == "[a, b]\n[1, 2]\n2"

    def test_length_tracks_assignment(self):
        code = 'var m = Map()!\nm["a"] = 1!\nprint(m.length)!\nm["b"] = 2!\nprint(m.length)!'
        assert output_of(code) == "1\n2"

    def test_has_and_delete(self):
        code = 'var m = { a: 1 }!\nprint(m.has("a"))!\nm.delete("a")!\nprint(m.has("a"))!\nprint(m.length)!'
        assert output_of(code) == "true\nfalse\n0"

    def test_dot_access_still_reads_entries(self):
        assert output_of("const m = { name: \"Lu\" }!\nprint(m.name)!") == "Lu"


class TestPrelude:
    def test_range(self):
        assert output_of("print(range(4))!") == "[0, 1, 2, 3]"

    def test_map_filter_reduce(self):
        code = (
            "fn double(x) => x * 2!\n"
            "fn isEven(x) => x / 2 == floor(x / 2)!\n"
            "fn add(a, b) => a + b!\n"
            "print(map([1, 2, 3], double))!\n"
            "print(filter([1, 2, 3, 4], isEven))!\n"
            "print(reduce([1, 2, 3], add, 0))!"
        )
        assert output_of(code) == "[2, 4, 6]\n[2, 4]\n6"

    def test_aggregates(self):
        code = "print(sum([1, 2, 3]))!\nprint(maxOf([4, 9, 2]))!\nprint(minOf([4, 9, 2]))!"
        assert output_of(code) == "6\n9\n2"

    def test_zip_take_reverse(self):
        code = 'print(zip([1, 2], ["a", "b"]))!\nprint(take([10, 20, 30], 2))!\nprint(reverseOf([1, 2, 3]))!'
        assert output_of(code) == "[[1, a], [2, b]]\n[10, 20]\n[3, 2, 1]"

    def test_sort_by(self):
        code = 'fn byLength(s) => s.length!\nprint(sortBy(["ccc", "a", "bb"], byLength))!'
        assert output_of(code) == "[a, bb, ccc]"

    def test_program_can_shadow_prelude(self):
        code = 'fn range(n) => "mine"!\nprint(range(3))!'
        assert output_of(code) == "mine"

    def test_prelude_can_be_disabled(self):
        result = run_gom("print(range(3))!", env={"GOM_NO_PRELUDE": "1"})
        assert result.returncode != 0

    def test_prelude_does_not_pollute_variable_snapshot(self, tmp_path):
        import json

        snapshot = tmp_path / "vars.json"
        result = subprocess.run(
            [sys.executable, "-m", "gulfofmexico", "--vars-json", str(snapshot), "-c", "const x = 1!"],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
            timeout=30,
        )
        assert result.returncode == 0, result.stderr
        names = {row["name"] for row in json.loads(snapshot.read_text(encoding="utf-8"))}
        assert "x" in names
        assert "range" not in names and "map" not in names


class TestScheduler:
    def test_after_does_not_block(self):
        code = 'print "a"!\nafter 10 {\n   print "c"!\n}\nprint "b"!'
        assert output_of(code) == "a\nb\nc"

    def test_after_runs_in_deadline_order(self):
        code = (
            'after 40 {\n   print "second"!\n}\n'
            'after 5 {\n   print "first"!\n}\n'
            'print "sync"!'
        )
        assert output_of(code) == "sync\nfirst\nsecond"

    def test_after_runs_even_when_last_statement(self):
        assert output_of('after 1 {\n   print "later"!\n}!') == "later"

    def test_sleep_still_blocks(self):
        code = 'print "one"!\nsleep 20!\nprint "two"!'
        assert output_of(code) == "one\ntwo"

    def test_after_can_be_nested(self):
        code = (
            'after 5 {\n'
            '   print "outer"!\n'
            '   after 5 {\n      print "inner"!\n   }\n'
            '}'
        )
        assert output_of(code) == "outer\ninner"
