from pathlib import Path

from screen_sentry.utils.toml import get_str, load_toml


CONFIG_PATH = Path.home() / ".config" / "screen-sentry" / "config.toml"


class AppConfig:
    def __init__(self, path: Path = CONFIG_PATH) -> None:
        self._path = path
        self._raw = load_toml(path, "config.toml")

    @property
    def provider(self) -> str | None:
        return get_str(self._raw, "app.provider")
