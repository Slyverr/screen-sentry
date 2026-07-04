import tomllib
from importlib.resources import files
from pathlib import Path

CONFIG_PATH = Path.home() / ".config" / "screen-sentry" / "config.toml"


class AppConfig:
    def __init__(self, path: Path = CONFIG_PATH) -> None:
        self._path = path
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                files("screen_sentry.config.presets")
                .joinpath("config.toml")
                .read_text()
            )
        self._raw = tomllib.loads(path.read_text())

    @property
    def save_dir(self) -> Path:
        return Path(self._raw["app"]["save_dir"]).expanduser()

    def get(self, section: str, key: str, default=None):
        return self._raw.get(section, {}).get(key, default)
