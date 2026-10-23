"""
Interpreter Persistence - On-disk storage for persistent values

Persists ``const const const`` constants and infinite-lifetime variables so
they survive between interpreter runs.

Storage
-------
Everything lives under ``$GOM_HOME/.gulfofmexico_runtime`` (``$HOME`` when
``GOM_HOME`` is unset, which is what tests use to stay isolated)::

    .gulfofmexico_runtime/
    ├── store.json        # {"version": 1, "constants": {name: {...}}}
    └── .store.lock       # advisory lock held while writing

Values use a small explicit JSON schema (numbers, strings, booleans, lists,
maps, undefined). Nothing is ever unpickled: the store is data, not code, so a
writable runtime directory cannot lead to code execution.

Writes are atomic (temp file + ``os.replace``) and serialised with an advisory
``flock`` so concurrent runs cannot corrupt the store. The runtime directory is
created ``0700`` and the store ``0600``, because constant names and values can
hold secrets.

Damage is never silently destructive: an unparseable store is renamed to
``store.json.corrupt`` before being rebuilt, and a store written by a *newer*
schema is reported and then left alone -- writes refuse to replace it.
"""

from __future__ import annotations

import json
import os
import stat
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from gulfofmexico.builtin import (
    GulfOfMexicoBoolean,
    GulfOfMexicoList,
    GulfOfMexicoMap,
    GulfOfMexicoNumber,
    GulfOfMexicoSpecialBlankValue,
    GulfOfMexicoString,
    GulfOfMexicoUndefined,
    GulfOfMexicoValue,
    Variable,
    VariableLifetime,
)
from gulfofmexico.ui import print_warning

from .context import (
    DB_RUNTIME_PATH,
    DB_VAR_TO_VALUE_SEP,
    IMMUTABLE_CONSTANTS_PATH,
    IMMUTABLE_CONSTANTS_VALUES_PATH,
    INF_VAR_PATH,
    INF_VAR_VALUES_PATH,
    Namespace,
)

#: Bumped whenever the on-disk shape changes; unknown versions are ignored.
SCHEMA_VERSION = 1
STORE_FILENAME = "store.json"
CORRUPT_SUFFIX = "corrupt"
LOCK_FILENAME = ".store.lock"
LEGACY_NOTICE_FILENAME = ".legacy-pickle-notice"
#: Set to ``1`` to import values from the pre-JSON pickle store.
ALLOW_LEGACY_PICKLE_ENV = "GOM_ALLOW_LEGACY_PICKLE"

FOREVER = 100_000_000_000


class UnsupportedPersistedValue(Exception):
    """Raised when a value cannot be represented in the JSON store."""


# ---------------------------------------------------------------------------
# Locations and locking
# ---------------------------------------------------------------------------

def runtime_dir() -> Path:
    """Return the runtime directory, honouring ``GOM_HOME`` for isolation."""
    base = os.environ.get("GOM_HOME") or str(Path.home())
    return Path(base) / DB_RUNTIME_PATH


def _ensure_directory(directory: Path) -> None:
    """Create the runtime directory owner-only, tightening an older one.

    The store file is written ``0600``, but the directory also lists constant
    *names*, so it must not be group- or world-readable either.
    """
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        if stat.S_IMODE(directory.stat().st_mode) & (stat.S_IRWXG | stat.S_IRWXO):
            os.chmod(directory, 0o700)
    except OSError:  # pragma: no cover - exotic filesystems
        pass


@contextmanager
def _store_lock(directory: Path) -> Iterator[None]:
    """Hold an exclusive advisory lock for a read-modify-write cycle."""
    try:
        import fcntl  # noqa: PLC0415 - POSIX only
    except ImportError:  # pragma: no cover - Windows
        yield
        return
    _ensure_directory(directory)
    with open(directory / LOCK_FILENAME, "a+", encoding="utf-8") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


# ---------------------------------------------------------------------------
# Value codec
# ---------------------------------------------------------------------------

def _encode_key(key: object) -> dict:
    """Encode a map key, which is a raw ``str`` or number inside the map."""
    if isinstance(key, str):
        return {"t": "string", "v": key}
    if isinstance(key, (int, float)):
        return {"t": "number", "v": key}
    raise UnsupportedPersistedValue(f"map key {key!r} cannot be stored")


def _decode_key(payload: object) -> object:
    """Decode a map key previously produced by :func:`_encode_key`."""
    if isinstance(payload, dict) and "v" in payload:
        if payload.get("t") == "string":
            return str(payload["v"])
        if payload.get("t") == "number":
            return payload["v"]
    raise UnsupportedPersistedValue(f"malformed stored map key {payload!r}")


def encode_value(value: GulfOfMexicoValue) -> dict:
    """Encode *value* into the store's JSON-compatible schema."""
    match value:
        case GulfOfMexicoNumber():
            return {"t": "number", "v": value.value}
        case GulfOfMexicoString():
            return {"t": "string", "v": value.value}
        case GulfOfMexicoBoolean():
            return {"t": "bool", "v": value.value}
        case GulfOfMexicoUndefined():
            return {"t": "undefined"}
        case GulfOfMexicoSpecialBlankValue():
            return {"t": "blank"}
        case GulfOfMexicoList():
            return {"t": "list", "v": [encode_value(item) for item in value.values]}
        case GulfOfMexicoMap():
            entries = list(value.self_dict.items())
            if all(isinstance(key, str) for key, _ in entries):
                # The common case stays a plain JSON object, so old stores and
                # hand-edited files keep working.
                return {"t": "map", "v": {key: encode_value(item) for key, item in entries}}
            return {
                "t": "map",
                "pairs": [[_encode_key(key), encode_value(item)] for key, item in entries],
            }
    raise UnsupportedPersistedValue(
        f"{type(value).__name__} cannot be stored with const const const"
    )


def decode_value(payload: object) -> GulfOfMexicoValue:
    """Decode a value produced by :func:`encode_value`.

    Malformed payloads raise :class:`UnsupportedPersistedValue` rather than
    ``KeyError``/``TypeError``, so a damaged store entry is skipped by callers
    instead of escaping as an internal error.
    """
    if not isinstance(payload, dict):
        raise UnsupportedPersistedValue(f"malformed stored value {payload!r}")
    kind = payload.get("t")
    if kind == "undefined":
        return GulfOfMexicoUndefined()
    if kind == "blank":
        return GulfOfMexicoSpecialBlankValue()
    if kind not in ("number", "string", "bool", "list", "map"):
        raise UnsupportedPersistedValue(f"unknown stored value type {kind!r}")
    if kind == "map":
        return _decode_map(payload)
    if "v" not in payload:
        raise UnsupportedPersistedValue(f"malformed stored value {payload!r}")
    content = payload["v"]
    if kind == "number":
        if not isinstance(content, (int, float)):
            raise UnsupportedPersistedValue(f"malformed stored number {content!r}")
        return GulfOfMexicoNumber(content)
    if kind == "string":
        return GulfOfMexicoString(str(content))
    if kind == "bool":
        return GulfOfMexicoBoolean(content)
    if not isinstance(content, list):
        raise UnsupportedPersistedValue("malformed stored list")
    return GulfOfMexicoList([decode_value(item) for item in content])


def _decode_map(payload: dict) -> GulfOfMexicoMap:
    """Decode the two map shapes: string keys in ``v``, typed keys in ``pairs``."""
    if "pairs" in payload:
        pairs = payload["pairs"]
        if not isinstance(pairs, list):
            raise UnsupportedPersistedValue("malformed stored map")
        return GulfOfMexicoMap({_decode_key(key): decode_value(item) for key, item in pairs})
    entries = payload.get("v")
    if not isinstance(entries, dict):
        raise UnsupportedPersistedValue("malformed stored map")
    return GulfOfMexicoMap({key: decode_value(item) for key, item in entries.items()})


# ---------------------------------------------------------------------------
# Store access
# ---------------------------------------------------------------------------

def _empty_store() -> dict:
    return {"version": SCHEMA_VERSION, "constants": {}}


def _preserve_unreadable_store(path: Path) -> None:
    """Keep a copy of a store we cannot parse before it is overwritten."""
    backup = path.with_name(STORE_FILENAME + "." + CORRUPT_SUFFIX)
    try:
        os.replace(path, backup)
    except OSError:  # pragma: no cover - read-only runtime dir
        return
    print_warning(
        f"the stored values could not be read; kept a copy in {backup.name}",
        hint="the store will be rebuilt as constants are declared again",
    )


def _store_version(path: Path) -> object:
    """Return the schema version recorded in *path*, or ``None`` if unreadable."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data.get("version") if isinstance(data, dict) else None


def _read_store(directory: Path) -> dict:
    path = directory / STORE_FILENAME
    if not path.is_file():
        return _empty_store()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        _preserve_unreadable_store(path)
        return _empty_store()
    if not isinstance(data, dict) or data.get("version") != SCHEMA_VERSION:
        # A newer schema is left untouched and never overwritten, so an older
        # interpreter cannot destroy data written by a newer one.
        found = data.get("version") if isinstance(data, dict) else None
        print_warning(
            f"{path.name} uses store schema {found!r}, "
            "which this version of Gulf of Mexico does not understand",
            hint="upgrade the interpreter, or move the file aside",
        )
        return _empty_store()
    if not isinstance(data.get("constants"), dict):
        data["constants"] = {}
    return data


def _write_store(directory: Path, data: dict) -> None:
    _ensure_directory(directory)
    path = directory / STORE_FILENAME
    if path.is_file():
        version = _store_version(path)
        if version is not None and version != SCHEMA_VERSION:
            print_warning(
                f"not saving to {path.name}: it uses store schema {version!r}",
                hint="upgrade the interpreter, or move the file aside",
            )
            return
    tmp = directory / (STORE_FILENAME + ".tmp")
    tmp.write_text(
        json.dumps(data, indent=1, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    try:
        os.chmod(tmp, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:  # pragma: no cover - exotic filesystems
        pass
    os.replace(tmp, path)


def _migrate_legacy_store(directory: Path) -> dict:
    """Import the pre-JSON pickle store once, when explicitly allowed.

    Unpickling executes arbitrary code, so this only runs when the user opts in
    with ``GOM_ALLOW_LEGACY_PICKLE=1``.
    """
    import pickle  # noqa: PLC0415 - only on the explicit opt-in path

    store = _empty_store()
    index = directory / IMMUTABLE_CONSTANTS_PATH
    values_dir = directory / IMMUTABLE_CONSTANTS_VALUES_PATH
    if not index.is_file():
        return store
    for line in index.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            name, identity, confidence = line.split(DB_VAR_TO_VALUE_SEP)
        except ValueError:
            continue
        try:
            with open(values_dir / identity, "rb") as handle:
                value = pickle.load(handle)  # noqa: S301 - explicit opt-in
            store["constants"][name] = {
                "confidence": int(confidence),
                "value": encode_value(value),
            }
        except (OSError, TypeError, ValueError, pickle.UnpicklingError,
                UnsupportedPersistedValue):
            continue
    return store


def _notice_legacy_store(directory: Path) -> None:
    """Warn once that a legacy pickle store is being ignored."""
    notice = directory / LEGACY_NOTICE_FILENAME
    if notice.exists():
        return
    try:
        notice.write_text("ignored\n", encoding="utf-8")
    except OSError:  # pragma: no cover - read-only runtime dir
        pass
    print_warning(
        "ignoring the legacy pickle store (those constants were not loaded)",
        hint=(
            "run once with GOM_ALLOW_LEGACY_PICKLE=1 to migrate it to JSON, "
            "or re-run the program that creates those constants"
        ),
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_global_gulfofmexico_variables(namespaces: list[Namespace]) -> None:
    """Load infinite-lifetime variables from a legacy read-only index.

    This restores ``.inf_vars`` directories written by early versions of the
    interpreter. The current interpreter does not *write* this format --
    ``const const const`` values live in ``store.json`` -- so the loader exists
    only to keep such directories readable rather than silently ignored.
    """
    directory = runtime_dir()
    index = directory / INF_VAR_PATH
    values_dir = directory / INF_VAR_VALUES_PATH
    if not index.is_file():
        return
    for line in index.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        parts = line.split(DB_VAR_TO_VALUE_SEP)
        if len(parts) < 5:
            continue
        name, identity, reset, edit, confidence = parts[:5]
        try:
            payload = json.loads((values_dir / f"{identity}.json").read_text(encoding="utf-8"))
            value = decode_value(payload)
        except (OSError, ValueError, UnsupportedPersistedValue):
            # Legacy pickled values are intentionally not loaded.
            continue
        namespaces[-1][name] = Variable(
            name,
            [VariableLifetime(value, FOREVER, int(confidence), reset == "True", edit == "True")],
            [],
        )


def load_local_immutable_constants(namespaces: list[Namespace]) -> None:
    """Load ``const const const`` constants into *namespaces*."""
    directory = runtime_dir()
    if not directory.is_dir():
        return

    if (directory / STORE_FILENAME).is_file():
        store = _read_store(directory)
    elif os.environ.get(ALLOW_LEGACY_PICKLE_ENV) == "1":
        store = _migrate_legacy_store(directory)
        if store["constants"]:
            _write_store(directory, store)
    else:
        if (directory / IMMUTABLE_CONSTANTS_PATH).is_file():
            _notice_legacy_store(directory)
        return

    for name, entry in store.get("constants", {}).items():
        try:
            value = decode_value(entry["value"])
            confidence = int(entry.get("confidence", 0))
        except (KeyError, TypeError, ValueError, UnsupportedPersistedValue):
            continue
        namespaces[-1][name] = Variable(
            name,
            [VariableLifetime(value, FOREVER, confidence, False, False)],
            [],
        )


def save_local_immutable_constant(
    name: str, value: GulfOfMexicoValue, confidence: int
) -> None:
    """Persist (or update) a ``const const const`` constant."""
    try:
        encoded = encode_value(value)
    except UnsupportedPersistedValue as exc:
        print_warning(f"'{name}' was not persisted: {exc}")
        return

    directory = runtime_dir()
    with _store_lock(directory):
        store = _read_store(directory)
        store["constants"][name] = {"confidence": confidence, "value": encoded}
        _write_store(directory, store)


def load_public_global_variables(namespaces: list[Namespace]) -> None:
    """Load all public global variables (currently the local constants)."""
    load_local_immutable_constants(namespaces)


def load_globals(
    _filename: str,
    _code: str,
    _arg3: object,
    _arg4: object,
    _exported_names: list[tuple[str, str, GulfOfMexicoValue]],
    _importable_names: dict[str, GulfOfMexicoValue],
    namespaces: list[Namespace] | None = None,
) -> None:
    """Load global variables before interpretation begins.

    Delegates to ``load_global_gulfofmexico_variables`` and
    ``load_public_global_variables`` when *namespaces* is provided.
    """
    if namespaces is not None:
        load_global_gulfofmexico_variables(namespaces)
        load_public_global_variables(namespaces)
