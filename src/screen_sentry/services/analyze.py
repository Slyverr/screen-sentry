import base64

import requests
from PySide6.QtCore import QObject, Signal

from screen_sentry.config.prompts import SYSTEM_PROMPT, USER_PROMPT
from screen_sentry.context import AppContext
from screen_sentry.utils.analysis_parser import AnalysisResult, parse_analysis


class AnalyzeService(QObject):
    analysis_finished = Signal(AnalysisResult)
    analysis_failed = Signal(str)

    def __init__(self, ctx: AppContext, parent: QObject | None = None) -> None:
        super().__init__(parent)

        self._ctx = ctx

    def analyze(self, image_bytes: bytes) -> None:
        try:
            raw = self._call_model(image_bytes)
            result = parse_analysis(raw)
        except Exception as exc:
            self.analysis_failed.emit(str(exc))
            return

        self.analysis_finished.emit(result)

    def _call_model(self, image_bytes: bytes) -> str:
        provider_name = self._ctx.app_config.get("app", "provider")
        provider = self._ctx.providers_config.get(provider_name)
        image_b64 = base64.b64encode(image_bytes).decode()

        body = provider.render_body(
            system=SYSTEM_PROMPT, prompt=USER_PROMPT, image_b64=image_b64
        )

        response = requests.post(provider.url, json=body, timeout=provider.timeout)
        response.raise_for_status()
        return provider.extract_response(response.json())
