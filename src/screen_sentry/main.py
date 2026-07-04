import signal
import sys

from .app import App
from .views.tray import TrayIcon


def main() -> None:
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = App()
    app.setQuitOnLastWindowClosed(False)

    tray = TrayIcon()
    tray.show()

    tray.activated.connect(lambda: print("Tray icon clicked"))
    tray.quit_triggered.connect(app.quit)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
