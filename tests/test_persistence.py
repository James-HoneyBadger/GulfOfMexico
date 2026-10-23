"""Tests for the persistent-value store.

The store is data-only (JSON), atomic, locked, and isolated through ``GOM_HOME``.
"""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def run_gom(code: str, *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    import tempfile

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".gom", delete=False, encoding="utf-8"
    ) as handle:
        handle.write(code)
        path = handle.name
    try:
        return subprocess.run(
            [sys.executable, "-m", "gulfofmexico", path],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(ROOT),
            env={**os.environ, **(env or {})},
        )
    finally:
        os.unlink(path)


class TestValueCodec:
    @pytest.mark.parametrize(
        "value",
        [
            "GulfOfMexicoNumber(3.5)",
            'GulfOfMexicoString("hi")',
            "GulfOfMexicoBoolean(True)",
            "GulfOfMexicoBoolean(None)",
            "GulfOfMexicoUndefined()",
        ],
    )
    def test_scalar_round_trip(self, value):
        from gulfofmexico.interpreter.persistence import decode_value, encode_value

        original = eval(value, {"__builtins__": {}}, _builtin_ns())
        assert decode_value(encode_value(original)) == original

    def test_nested_collections_round_trip(self):
        from gulfofmexico.interpreter.persistence import decode_value, encode_value

        ns = _builtin_ns()
        value = ns["GulfOfMexicoList"]([
            ns["GulfOfMexicoNumber"](1),
            ns["GulfOfMexicoList"]([ns["GulfOfMexicoString"]("a")]),
            ns["GulfOfMexicoMap"]({"k": ns["GulfOfMexicoBoolean"](True)}),
        ])
        restored = decode_value(encode_value(value))
        assert restored.values[0].value == 1
        assert restored.values[1].values[0].value == "a"
        assert restored.values[2].self_dict["k"].value is True

    def test_unsupported_value_is_rejected(self):
        from gulfofmexico.builtin import GulfOfMexicoKeyword
        from gulfofmexico.interpreter.persistence import (
            UnsupportedPersistedValue,
            encode_value,
        )

        with pytest.raises(UnsupportedPersistedValue):
            encode_value(GulfOfMexicoKeyword("if"))


def _builtin_ns() -> dict:
    import gulfofmexico.builtin as builtin

    return {
        name: getattr(builtin, name)
        for name in (
            "GulfOfMexicoNumber",
            "GulfOfMexicoString",
            "GulfOfMexicoBoolean",
            "GulfOfMexicoUndefined",
            "GulfOfMexicoList",
            "GulfOfMexicoMap",
        )
    }


class TestStoreOnDisk:
    def test_constants_persist_across_runs(self, fresh_store):
        first = run_gom("const const const KEEP = 41!\nprint(KEEP)!")
        assert first.returncode == 0, first.stderr
        second = run_gom("print(KEEP)!")
        assert second.returncode == 0, second.stderr
        assert second.stdout.strip() == "41"

    def test_store_is_json_and_owner_only(self, fresh_store):
        run_gom("const const const SECRET = \"s\"!")
        store = fresh_store / ".gulfofmexico_runtime" / "store.json"
        assert store.is_file()
        assert store.read_text(encoding="utf-8").lstrip().startswith("{")
        mode = stat.S_IMODE(store.stat().st_mode)
        assert mode & (stat.S_IRWXG | stat.S_IRWXO) == 0

    def test_redeclaring_reuses_the_same_entry(self, fresh_store):
        run_gom("const const const AGAIN = 1!")
        run_gom("const const const AGAIN = 2!")
        store = json.loads(
            (fresh_store / ".gulfofmexico_runtime" / "store.json").read_text(encoding="utf-8")
        )
        assert list(store["constants"]) == ["AGAIN"]
        assert store["constants"]["AGAIN"]["value"]["v"] == 2

    def test_containers_persist(self, fresh_store):
        result = run_gom(
            "const const const LIST = [1, 2]!\nconst const const MAP = { a: 1 }!"
        )
        assert result.returncode == 0, result.stderr
        store = json.loads(
            (fresh_store / ".gulfofmexico_runtime" / "store.json").read_text(encoding="utf-8")
        )
        assert store["constants"]["LIST"]["value"]["t"] == "list"
        assert store["constants"]["MAP"]["value"]["t"] == "map"

    def test_unsupported_value_warns_instead_of_crashing(self, fresh_store):
        result = run_gom("fn add(a, b) => a + b!\nconst const const F = add!")
        assert result.returncode == 0, result.stderr
        assert "was not persisted" in result.stderr

    def test_json_path_never_unpickles(self, fresh_store, monkeypatch):
        """The JSON read/write cycle must not touch pickle at all."""
        import pickle

        from gulfofmexico.builtin import GulfOfMexicoNumber
        from gulfofmexico.interpreter import persistence

        def explode(*_args, **_kwargs):
            raise AssertionError("pickle.load must never run on the JSON store path")

        monkeypatch.setattr(pickle, "load", explode, raising=False)
        persistence.save_local_immutable_constant("SAFE", GulfOfMexicoNumber(3), 1)

        namespaces: list[dict] = [{}]
        persistence.load_local_immutable_constants(namespaces)
        assert namespaces[-1]["SAFE"].lifetimes[0].value == GulfOfMexicoNumber(3)

    def test_pickle_is_imported_only_for_migration(self):
        """Structurally: no module-level pickle import, only the opt-in path."""
        import ast

        source = (ROOT / "gulfofmexico" / "interpreter" / "persistence.py").read_text()
        tree = ast.parse(source)

        def imports_pickle(node):
            return isinstance(node, ast.Import) and any(a.name == "pickle" for a in node.names)

        assert not [node for node in tree.body if imports_pickle(node)]

        migration = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == "_migrate_legacy_store"
        ]
        assert len(migration) == 1
        assert [node for node in ast.walk(migration[0]) if imports_pickle(node)]

    def test_legacy_store_is_ignored_without_opt_in(self, fresh_store):
        legacy = fresh_store / ".gulfofmexico_runtime"
        legacy.mkdir()
        (legacy / ".immutable_constants").write_text("OLD;;;1;;;1\n", encoding="utf-8")
        result = run_gom("print 1!")
        assert result.returncode == 0
        assert "legacy pickle store" in result.stderr
        # Warning appears once, not on every run.
        again = run_gom("print 1!")
        assert "legacy pickle" not in again.stderr

    def test_legacy_store_can_be_migrated(self, fresh_store):
        pytest.importorskip("pickle")
        import pickle

        legacy = fresh_store / ".gulfofmexico_runtime"
        values = legacy / ".immutable_constants_values"
        values.mkdir(parents=True)
        (legacy / ".immutable_constants").write_text("OLD;;;42;;;1\n", encoding="utf-8")
        from gulfofmexico.builtin import GulfOfMexicoNumber

        with open(values / "42", "wb") as handle:
            pickle.dump(GulfOfMexicoNumber(7), handle)

        result = run_gom("print(OLD)!", env={"GOM_ALLOW_LEGACY_PICKLE": "1"})
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == "7"
        store = json.loads((legacy / "store.json").read_text(encoding="utf-8"))
        assert store["constants"]["OLD"]["value"] == {"t": "number", "v": 7}

    def test_gom_home_is_respected(self, tmp_path):
        result = run_gom("const const const SCOPED = 5!", env={"GOM_HOME": str(tmp_path)})
        assert result.returncode == 0, result.stderr
        assert (tmp_path / ".gulfofmexico_runtime" / "store.json").is_file()


class TestStoreRobustness:
    """Failure modes the store must survive without losing data or crashing."""

    def test_directory_is_owner_only(self, fresh_store):
        run_gom('const const const NAMES_ARE_SECRET = 1!')
        directory = fresh_store / ".gulfofmexico_runtime"
        mode = stat.S_IMODE(directory.stat().st_mode)
        assert mode & (stat.S_IRWXG | stat.S_IRWXO) == 0, oct(mode)

    def test_an_existing_permissive_directory_is_tightened(self, fresh_store):
        directory = fresh_store / ".gulfofmexico_runtime"
        directory.mkdir(parents=True)
        os.chmod(directory, 0o755)
        run_gom("const const const TIGHT = 1!")
        assert stat.S_IMODE(directory.stat().st_mode) == 0o700

    def test_corrupt_store_is_preserved_before_being_rebuilt(self, fresh_store):
        directory = fresh_store / ".gulfofmexico_runtime"
        directory.mkdir(parents=True)
        store = directory / "store.json"
        store.write_text("{not json", encoding="utf-8")

        result = run_gom("const const const FRESH = 2!")
        assert result.returncode == 0, result.stderr
        assert "store.json.corrupt" in result.stderr

        backup = directory / "store.json.corrupt"
        assert backup.read_text(encoding="utf-8") == "{not json"
        assert json.loads(store.read_text(encoding="utf-8"))["constants"]["FRESH"]["value"] == {
            "t": "number",
            "v": 2,
        }

    def test_newer_schema_is_ignored_and_never_overwritten(self, fresh_store):
        directory = fresh_store / ".gulfofmexico_runtime"
        directory.mkdir(parents=True)
        store = directory / "store.json"
        future = json.dumps({"version": 999, "constants": {"FUTURE": 1}})
        store.write_text(future, encoding="utf-8")

        result = run_gom("const const const MINE = 1!")
        assert result.returncode == 0, result.stderr
        assert "schema 999" in result.stderr
        assert store.read_text(encoding="utf-8") == future

    def test_one_malformed_entry_does_not_hide_the_others(self, fresh_store):
        directory = fresh_store / ".gulfofmexico_runtime"
        directory.mkdir(parents=True)
        (directory / "store.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "constants": {
                        "GOOD": {"confidence": 1, "value": {"t": "number", "v": 2}},
                        "UNKNOWN_TYPE": {"confidence": 1, "value": {"t": "nope"}},
                        "MISSING_VALUE": {"confidence": 1},
                    },
                }
            ),
            encoding="utf-8",
        )
        result = run_gom("print(GOOD)!")
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == "2"

    def test_concurrent_writers_all_survive(self, fresh_store):
        """Read-modify-write cycles are serialised by the store lock."""
        processes = [
            subprocess.Popen(
                [sys.executable, "-m", "gulfofmexico", "-c", f"const const const K{i} = {i}!"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(ROOT),
                env={**os.environ, "GOM_HOME": str(fresh_store)},
            )
            for i in range(8)
        ]
        for process in processes:
            process.communicate(timeout=60)
            assert process.returncode == 0

        store = json.loads(
            (fresh_store / ".gulfofmexico_runtime" / "store.json").read_text(encoding="utf-8")
        )
        assert sorted(store["constants"]) == [f"K{i}" for i in range(8)]


class TestCodecEdges:
    def test_blank_value_round_trips(self):
        from gulfofmexico.builtin import GulfOfMexicoSpecialBlankValue
        from gulfofmexico.interpreter.persistence import decode_value, encode_value

        assert encode_value(GulfOfMexicoSpecialBlankValue()) == {"t": "blank"}
        assert isinstance(decode_value({"t": "blank"}), GulfOfMexicoSpecialBlankValue)

    @pytest.mark.parametrize("payload", [None, [], "x", {}, {"t": "mystery"}])
    def test_malformed_payloads_are_rejected(self, payload):
        from gulfofmexico.interpreter.persistence import (
            UnsupportedPersistedValue,
            decode_value,
        )

        with pytest.raises(UnsupportedPersistedValue):
            decode_value(payload)

    def test_numeric_map_keys_keep_their_type(self):
        from gulfofmexico.builtin import GulfOfMexicoMap, GulfOfMexicoNumber
        from gulfofmexico.interpreter.persistence import decode_value, encode_value

        original = GulfOfMexicoMap({1: GulfOfMexicoNumber(2), 2.5: GulfOfMexicoNumber(3)})
        encoded = encode_value(original)
        assert "pairs" in encoded

        restored = decode_value(encoded)
        assert sorted(restored.self_dict) == [1, 2.5]
        assert all(isinstance(key, (int, float)) for key in restored.self_dict)

    def test_unsupported_map_key_is_rejected(self):
        from gulfofmexico.builtin import GulfOfMexicoMap, GulfOfMexicoNumber
        from gulfofmexico.interpreter.persistence import (
            UnsupportedPersistedValue,
            encode_value,
        )

        with pytest.raises(UnsupportedPersistedValue):
            encode_value(GulfOfMexicoMap({(1, 2): GulfOfMexicoNumber(3)}))

    @pytest.mark.parametrize("key", [{"t": "bogus"}, {"t": "number"}, "plain", None])
    def test_malformed_stored_map_key_is_rejected(self, key):
        from gulfofmexico.interpreter.persistence import (
            UnsupportedPersistedValue,
            decode_value,
        )

        with pytest.raises(UnsupportedPersistedValue):
            decode_value({"t": "map", "pairs": [[key, {"t": "number", "v": 1}]]})

    def test_string_keyed_maps_keep_the_plain_object_form(self):
        from gulfofmexico.builtin import GulfOfMexicoMap, GulfOfMexicoNumber
        from gulfofmexico.interpreter.persistence import encode_value

        encoded = encode_value(GulfOfMexicoMap({"k": GulfOfMexicoNumber(1)}))
        assert encoded == {"t": "map", "v": {"k": {"t": "number", "v": 1}}}

    def test_non_ascii_names_and_values_survive(self, fresh_store):
        result = run_gom('const const const HOLIDAY = "héllo 🌊"!', env={"GOM_HOME": str(fresh_store)})
        assert result.returncode == 0, result.stderr
        store = json.loads(
            (fresh_store / ".gulfofmexico_runtime" / "store.json").read_text(encoding="utf-8")
        )
        assert store["constants"]["HOLIDAY"]["value"] == {"t": "string", "v": "héllo 🌊"}

        second = run_gom("print(HOLIDAY)!", env={"GOM_HOME": str(fresh_store)})
        assert second.returncode == 0, second.stderr
        assert second.stdout.strip() == "héllo 🌊"


class TestLegacyFormats:
    def test_infinite_lifetime_index_is_readable(self, fresh_store):
        """.inf_vars directories written by early versions still load."""
        directory = fresh_store / ".gulfofmexico_runtime"
        values = directory / ".inf_vars_values"
        values.mkdir(parents=True)
        (directory / ".inf_vars").write_text("OLD_INF;;;42;;;True;;;True;;;1\n", encoding="utf-8")
        (values / "42.json").write_text(
            json.dumps({"t": "number", "v": 7}), encoding="utf-8"
        )

        result = run_gom("print(OLD_INF)!", env={"GOM_HOME": str(fresh_store)})
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == "7"

    def test_migration_is_skipped_when_a_json_store_exists(self, fresh_store):
        directory = fresh_store / ".gulfofmexico_runtime"
        directory.mkdir(parents=True)
        (directory / ".immutable_constants").write_text("LEGACY;;;1;;;1\n", encoding="utf-8")
        (directory / "store.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "constants": {"CURRENT": {"confidence": 1, "value": {"t": "number", "v": 5}}},
                }
            ),
            encoding="utf-8",
        )

        result = run_gom(
            "print(CURRENT)!", env={"GOM_HOME": str(fresh_store), "GOM_ALLOW_LEGACY_PICKLE": "1"}
        )
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == "5"
        store = json.loads((directory / "store.json").read_text(encoding="utf-8"))
        assert "LEGACY" not in store["constants"]
