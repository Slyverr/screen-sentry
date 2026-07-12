from importlib.resources import files
from pathlib import Path
from typing import Any, Callable, TypeVar, overload

import tomlkit
from tomlkit.items import InlineTable, Table

_MISSING = object()
T = TypeVar("T")


def load_toml(
    path: Path,
    preset_resource: str,
    preset_package: str = "screen_sentry.config.presets",
) -> tomlkit.TOMLDocument:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(files(preset_package).joinpath(preset_resource).read_text())
    return tomlkit.parse(path.read_text())


def save_toml(path: Path, doc: tomlkit.TOMLDocument) -> None:
    path.write_text(tomlkit.dumps(doc))


def _get(doc: Any, path: str, default: Any = _MISSING) -> Any:
    value = doc
    for part in path.split("."):
        try:
            if isinstance(value, list):
                value = value[int(part)]
            else:
                value = value[part]
        except (KeyError, IndexError, TypeError, ValueError):
            if default is _MISSING:
                raise KeyError(f"config key '{path}' not found")
            return default
    return value


def _is_table(value: Any) -> bool:
    return isinstance(value, (dict, Table, InlineTable))


def get_typed(doc: Any, path: str, converter: Callable[[Any], T], default: T) -> T:
    value = _get(doc, path, default=_MISSING)
    if value is _MISSING or _is_table(value):
        return default
    try:
        return converter(value)
    except (TypeError, ValueError):
        return default


@overload
def get_str(doc: Any, path: str, default: str) -> str: ...


@overload
def get_str(doc: Any, path: str, default: None = None) -> str | None: ...


def get_str(doc: Any, path: str, default: str | None = None) -> str | None:
    return get_typed(doc, path, str, default)


@overload
def get_int(doc: Any, path: str, default: int) -> int: ...


@overload
def get_int(doc: Any, path: str, default: None = None) -> int | None: ...


def get_int(doc: Any, path: str, default: int | None = None) -> int | None:
    return get_typed(doc, path, int, default)


@overload
def get_float(doc: Any, path: str, default: float) -> float: ...


@overload
def get_float(doc: Any, path: str, default: None = None) -> float | None: ...


def get_float(doc: Any, path: str, default: float | None = None) -> float | None:
    return get_typed(doc, path, float, default)


@overload
def get_bool(doc: Any, path: str, default: bool) -> bool: ...


@overload
def get_bool(doc: Any, path: str, default: None = None) -> bool | None: ...


def get_bool(doc: Any, path: str, default: bool | None = None) -> bool | None:
    def to_bool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "on")
        return bool(value)

    return get_typed(doc, path, to_bool, default)


@overload
def get_dict(doc: Any, path: str, default: dict) -> dict: ...


@overload
def get_dict(doc: Any, path: str, default: None = None) -> dict | None: ...


def get_dict(doc: Any, path: str, default: dict | None = None) -> dict | None:
    value = _get(doc, path, default=_MISSING)
    if value is _MISSING or not _is_table(value):
        return default
    return dict(value)


@overload
def get_list(doc: Any, path: str, default: list) -> list: ...


@overload
def get_list(doc: Any, path: str, default: None = None) -> list | None: ...


def get_list(doc: Any, path: str, default: list | None = None) -> list | None:
    value = _get(doc, path, default=_MISSING)
    if value is _MISSING or not isinstance(value, list):
        return default
    return list(value)


def has_key(doc: Any, path: str) -> bool:
    try:
        _get(doc, path)
        return True
    except KeyError:
        return False
