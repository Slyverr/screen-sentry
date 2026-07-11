import os

from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon


class TrayIcon(QSystemTrayIcon):
    quit_triggered = Signal()
    capture_triggered = Signal()

    def __init__(self) -> None:
        super().__init__()

        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "assets", "icon.svg"
        )
        self.setIcon(QIcon(icon_path))
        self.setToolTip("Screen Sentry")

        self._build_menu()

    def _build_menu(self) -> None:
        menu = QMenu()
        menu.addAction("Capture", self.capture_triggered.emit)
        menu.addAction("Quit", self.quit_triggered.emit)
        self.setContextMenu(menu)
