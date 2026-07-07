from pathlib import Path
import sys

from PySide6.QtWidgets import QApplication, QSystemTrayIcon

from screen_sentry.context import AppContext
from screen_sentry.services.analyze import AnalyzeService
from screen_sentry.services.screenshot import ScreenshotService
from screen_sentry.services.watch import WatchService
from screen_sentry.utils.analysis_parser import AnalysisResult, ThreatLevel
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
        context = AppContext()

        self._screenshot_service = ScreenshotService(context)
        self._analyze_service = AnalyzeService(context)

    def _init_tray(self) -> None:
        self._tray = TrayIcon()
        self._tray.show()

    def _connect_signals(self) -> None:
        self._screenshot_service.capture_finished.connect(self._analyze_and_clean)

        self._analyze_service.analysis_finished.connect(self._on_analysis_finished)
        self._analyze_service.analysis_failed.connect(self._on_analysis_failed)

        self._tray.activated.connect(self._screenshot_service.capture)
        self._tray.capture_triggered.connect(self._screenshot_service.capture)
        self._tray.quit_triggered.connect(self.quit)

    def _analyze_and_clean(self, path: Path):
        self._analyze_service.analyze(path)
        path.unlink(missing_ok=True)

    def _on_analysis_finished(self, path: Path, result: AnalysisResult) -> None:
        self._tray.showMessage(
            "Analysis Complete",
            result.message,
            QSystemTrayIcon.MessageIcon.NoIcon,
            3000,
        )

    def _on_analysis_failed(self, path: Path, error: str) -> None:
        self._tray.showMessage(
            "Analysis Failed", error, QSystemTrayIcon.MessageIcon.NoIcon, 3000
        )
