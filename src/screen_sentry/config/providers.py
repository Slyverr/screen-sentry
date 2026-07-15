from pathlib import Path

from platformdirs import user_config_dir

from screen_sentry.backends.base import Backend
from screen_sentry.backends.registry import get_backend_class
from screen_sentry.utils.toml import get_dict, get_str, load_toml

CONFIG_DIR = Path(user_config_dir("screen-sentry"))
PROVIDERS_PATH = CONFIG_DIR / "providers.toml"


class ProvidersConfig:
    def __init__(self, path: Path = PROVIDERS_PATH) -> None:
        self._path = path
        self._raw = load_toml(path, "providers.toml")

        self._instances: dict[str, Backend] = {}

    def get_provider(self, name: str) -> Backend:
        if name not in self._instances:
            self._instances[name] = self._build_provider(name)

        return self._instances[name]

    def _build_provider(self, name: str) -> Backend:
        backend_type = get_str(
            self._raw,
            f"providers.{name}.type",
        )
        if backend_type is None:
            raise ValueError("Missing backend type")

        backend_cls = get_backend_class(backend_type)

        config = get_dict(self._raw, f"providers.{name}", default={})
        return backend_cls(provider_name=name, config=config)

    def list_providers(self) -> list[str]:
        providers = self._raw.get("providers", {})
        return list(providers.keys())

    def has_provider(self, name: str) -> bool:
        return name in self._raw.get("providers", {})
