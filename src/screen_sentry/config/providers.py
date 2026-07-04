import json
import tomllib
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

PROVIDERS_PATH = Path.home() / ".config" / "screen-sentry" / "providers.toml"


@dataclass
class ProviderConfig:
    url: str
    body: str
    response_path: str
    model: str
    timeout: int = 60

    def render_body(self, prompt: str, image_b64: str, system: str = "") -> dict:
        rendered = (
            self.body.replace("{{model}}", self.model)
            .replace("{{system}}", json.dumps(system)[1:-1])
            .replace("{{prompt}}", json.dumps(prompt)[1:-1])
            .replace("{{image}}", image_b64)
        )

        return json.loads(rendered)

    def extract_response(self, response_json: dict) -> str:
        value = response_json

        for part in self.response_path.split("."):
            if part.isdigit():
                value = value[int(part)]
            else:
                value = value[part]

        return value


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

    @property
    def active_name(self) -> str:
        return self._raw["active"]

    @property
    def active(self) -> ProviderConfig:
        return self.get(self.active_name)

    def get(self, name: str) -> ProviderConfig:
        return ProviderConfig(**self._raw["providers"][name])

    def names(self) -> list[str]:
        return list(self._raw["providers"].keys())
