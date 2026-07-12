import sys

from PySide6.QtWidgets import QApplication, QSystemTrayIcon

from screen_sentry.context import AppContext
from screen_sentry.services.analyze import AnalyzeService
from screen_sentry.services.screenshot import ScreenshotService
from screen_sentry.services.watch import WatchService
from screen_sentry.utils.analysis_parser import AnalysisResult
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
        self._ctx = AppContext()
        self._ctx.screenshot_service = ScreenshotService(self._ctx)
        self._ctx.analyze_service = AnalyzeService(self._ctx)
        self._ctx.watch_service = WatchService(self._ctx)

    def _init_tray(self) -> None:
        self._tray = TrayIcon()
        self._tray.show()

    def handle_cli_command(self, args: list[str]) -> None:
        if not args:
            return

        ctx = self._ctx
        match args:
            case ["watch", "on"]:
                ctx.watch_service.start()
            case ["watch", "off"]:
                ctx.watch_service.stop()
            case ["watch", "toggle"]:
                ctx.watch_service.toggle()
            case ["capture"]:
                ctx.screenshot_service.capture()
            case ["quit"]:
                self.quit()
            case _:
                print(f"unknown command: {' '.join(args)}", file=sys.stderr)

    def _connect_signals(self) -> None:
        ctx = self._ctx
        ctx.screenshot_service.capture_finished.connect(ctx.analyze_service.analyze)
        ctx.watch_service.watch_capture_finished.connect(ctx.analyze_service.analyze)

        ctx.analyze_service.analysis_finished.connect(self._on_analysis_finished)
        ctx.analyze_service.analysis_failed.connect(self._on_analysis_failed)

        self._tray.activated.connect(ctx.screenshot_service.capture)
        self._tray.watch_toggled.connect(ctx.watch_service.toggle)
        self._tray.capture_triggered.connect(ctx.screenshot_service.capture)
        self._tray.quit_triggered.connect(self.quit)

    def _on_analysis_finished(self, result: AnalysisResult) -> None:
        self._tray.showMessage(
            "Analysis Complete",
            result.message,
            QSystemTrayIcon.MessageIcon.NoIcon,
            3000,
        )

    def _on_analysis_failed(self, error: str) -> None:
        self._tray.showMessage(
            "Analysis Failed", error, QSystemTrayIcon.MessageIcon.NoIcon, 3000
        )
