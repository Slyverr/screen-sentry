from pathlib import Path

from platformdirs import user_config_dir

from screen_sentry.utils.toml import get_str, load_toml

CONFIG_DIR = Path(user_config_dir("screen-sentry"))
CONFIG_PATH = CONFIG_DIR / "config.toml"


class AppConfig:
    def __init__(self, path: Path = CONFIG_PATH) -> None:
        self._path = path
        self._raw = load_toml(path, "config.toml")

    @property
    def provider(self) -> str | None:
        return get_str(self._raw, "app.provider")
