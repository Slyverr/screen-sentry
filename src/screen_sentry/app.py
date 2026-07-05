import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from screen_sentry.config.config import AppConfig
from screen_sentry.config.providers import ProvidersConfig
from screen_sentry.services.analyze import AnalyzeService, AppContext
from screen_sentry.services.screenshot import ScreenshotService
from screen_sentry.views.tray import TrayIcon


class App(QApplication):
    def __init__(self, argv: list[str] = sys.argv) -> None:
        super().__init__(argv)

        self.setApplicationName("Screen Sentry")
        self.setApplicationVersion("0.1.0")
        self.setQuitOnLastWindowClosed(False)

        self._init_services()
        self._init_tray()

        self._connect_signals()

    def _init_services(self) -> None:
        context = AppContext(app=AppConfig(), providers=ProvidersConfig())

        self._screenshot_service = ScreenshotService(
            save_dir=Path.home() / "Pictures" / "ScreenSentry"
        )
        self._analyze_service = AnalyzeService(context)

    def _init_tray(self) -> None:
        self._tray = TrayIcon()
        self._tray.show()

    def _connect_signals(self) -> None:
        self._screenshot_service.capture_finished.connect(self._analyze_service.analyze)

        self._analyze_service.analysis_finished.connect(
            lambda path, result: print(f"[Analysis] {result}")
        )
        self._analyze_service.analysis_failed.connect(
            lambda error: print(f"[Error] {error}")
        )

        self._tray.activated.connect(self._screenshot_service.capture)
        self._tray.capture_triggered.connect(self._screenshot_service.capture)
        self._tray.quit_triggered.connect(self.quit)
