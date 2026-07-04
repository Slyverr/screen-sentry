import signal
import sys
from pathlib import Path

from screen_sentry.app import App
from screen_sentry.config.config import AppConfig
from screen_sentry.config.providers import ProvidersConfig
from screen_sentry.services.analyze import AnalyzeService, AppContext
from screen_sentry.services.screenshot import ScreenshotService
from screen_sentry.views.tray import TrayIcon


def main() -> None:
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = App()
    app.setQuitOnLastWindowClosed(False)

    tray = TrayIcon()
    tray.show()

    app_context = AppContext(app=AppConfig(), providers=ProvidersConfig())

    screenshot_service = ScreenshotService(
        save_dir=Path.home() / "Pictures" / "ScreenSentry"
    )
    analyze_service = AnalyzeService(app_context)

    screenshot_service.capture_finished.connect(analyze_service.analyze)

    analyze_service.analysis_finished.connect(
        lambda path, result: print(f"[Analysis] {result}")
    )
    analyze_service.analysis_failed.connect(lambda error: print(f"[Error] {error}"))

    tray.activated.connect(screenshot_service.capture)
    tray.capture_triggered.connect(screenshot_service.capture)
    tray.quit_triggered.connect(app.quit)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
