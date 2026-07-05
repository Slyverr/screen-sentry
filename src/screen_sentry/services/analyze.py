import base64
from pathlib import Path

import requests
from PySide6.QtCore import QObject, Signal

from screen_sentry.config.prompts import SYSTEM_PROMPT, USER_PROMPT
from screen_sentry.context import AppContext


class AnalyzeService(QObject):
    analysis_finished = Signal(Path, str)
    analysis_failed = Signal(str)

    def __init__(self, ctx: AppContext, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._ctx = ctx

    def analyze(self, image_path: Path) -> None:
        try:
            result = self._call_model(image_path)
        except Exception as exc:
            self.analysis_failed.emit(str(exc))
            return

        self.analysis_finished.emit(image_path, result)

    def _call_model(self, image_path: Path) -> str:
        provider_name = self._ctx.app_config.get("app", "provider")
        provider = self._ctx.providers_config.get(provider_name)

        image_b64 = base64.b64encode(image_path.read_bytes()).decode()
        body = provider.render_body(
            system=SYSTEM_PROMPT, prompt=USER_PROMPT, image_b64=image_b64
        )

        response = requests.post(provider.url, json=body, timeout=provider.timeout)
        response.raise_for_status()
        return provider.extract_response(response.json())
