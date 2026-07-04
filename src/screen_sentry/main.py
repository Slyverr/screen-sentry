import signal
import sys
from pathlib import Path

from .app import App
from .services.screenshot import ScreenshotService
from .views.tray import TrayIcon


def main() -> None:
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = App()
    app.setQuitOnLastWindowClosed(False)

    screenshot_service = ScreenshotService(
        save_dir=Path.home() / "Pictures" / "ScreenSentry"
    )

    tray = TrayIcon()
    tray.show()

    tray.activated.connect(screenshot_service.capture)
    tray.capture_triggered.connect(screenshot_service.capture)
    tray.quit_triggered.connect(app.quit)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
