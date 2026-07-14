from PySide6.QtCore import QObject, Signal

from screen_sentry.context import AppContext
from screen_sentry.utils.analysis_parser import (
    AnalysisImage,
    AnalysisResult,
    parse_analysis,
)


class AnalyzeService(QObject):
    analysis_finished = Signal(AnalysisResult)
    analysis_failed = Signal(str)

    def __init__(self, ctx: AppContext, parent: QObject | None = None) -> None:
        super().__init__(parent)

        self._ctx = ctx
        self._busy = False

        provider_name = self._ctx.app_config.provider
        self._backend = self._ctx.providers_config.get_provider(str(provider_name))

        self._backend.succeeded.connect(self._on_backend_succeeded)
        self._backend.network_error.connect(self._on_backend_network_error)
        self._backend.api_error.connect(self._on_backend_api_error)

    def analyze(self, image: AnalysisImage) -> None:
        if self._busy:
            return

        self._busy = True
        self._backend.send(image)

    def _on_backend_succeeded(self, image: AnalysisImage, raw_text: str) -> None:
        self._busy = False

        try:
            result = parse_analysis(image, raw_text)
        except Exception as exc:
            self.analysis_failed.emit(f"parse error: {exc}")
            return

        self.analysis_finished.emit(result)

    def _on_backend_network_error(self, detail: str) -> None:
        self._busy = False
        self.analysis_failed.emit(f"network error: {detail}")

    def _on_backend_api_error(self, detail: str) -> None:
        self._busy = False
        self.analysis_failed.emit(f"api error: {detail}")
