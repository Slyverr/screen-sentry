from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon


class TrayIcon(QSystemTrayIcon):
    quit_triggered = Signal()

    def __init__(self) -> None:
        super().__init__()

        self.setIcon(QIcon.fromTheme(""))
        self.setToolTip("Screen Sentry")

        self._build_menu()

    def _build_menu(self) -> None:
        menu = QMenu()
        menu.addAction("Quit", self.quit_triggered.emit)
        self.setContextMenu(menu)
