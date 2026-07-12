import tomllib
from importlib.resources import files
from pathlib import Path

from screen_sentry.backends.base import Backend
from screen_sentry.backends.registry import get_backend_class

PROVIDERS_PATH = Path.home() / ".config" / "screen-sentry" / "providers.toml"


class ProvidersConfig:
    def __init__(self, path: Path = PROVIDERS_PATH) -> None:
        self._path = path
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                files("screen_sentry.config.presets")
                .joinpath("providers.toml")
                .read_text()
            )

        self._raw = tomllib.loads(path.read_text())
        self._instances: dict[str, Backend] = {}

    @property
    def active_name(self) -> str:
        return self._raw["active"]

    @property
    def active(self) -> Backend:
        return self.get(self.active_name)

    def get(self, name: str) -> Backend:
        """Return the backend instance for `name`, creating it on first use."""
        if name not in self._instances:
            self._instances[name] = self._build(name)

        return self._instances[name]

    def _build(self, name: str) -> Backend:
        try:
            table = self._raw["providers"][name]
        except KeyError:
            raise ValueError(f"no provider named '{name}' in providers.toml") from None

        try:
            backend_type = table["type"]
        except KeyError:
            raise ValueError(
                f"provider '{name}' is missing required 'type' field"
            ) from None

        backend_cls = get_backend_class(backend_type)
        return backend_cls(provider_name=name, config=table)

    def names(self) -> list[str]:
        return list(self._raw["providers"].keys())

    def set_active(self, name: str) -> None:
        if name not in self._raw["providers"]:
            raise ValueError(f"no provider named '{name}' in providers.toml")

        self._raw["active"] = name
