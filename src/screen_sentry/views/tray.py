import os

from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon


class TrayIcon(QSystemTrayIcon):
    quit_triggered = Signal()
    capture_triggered = Signal()
    watch_toggled = Signal(bool)

    def __init__(self) -> None:
        super().__init__()

        self._watch_enabled = False

        self._assets_dir = os.path.dirname(os.path.dirname(__file__))
        self._icon_path_watch = os.path.join(
            self._assets_dir, "assets", "icon-watch.svg"
        )
        self._icon_path_default = os.path.join(self._assets_dir, "assets", "icon.svg")

        self.setIcon(QIcon(self._icon_path_default))
        self._build_menu()

    def _build_menu(self) -> None:
        menu = QMenu()

        menu.addAction("Capture", self.capture_triggered.emit)
        self._watch_action = menu.addAction("Start Watch Mode")
        self._watch_action.triggered.connect(self._toggle_watch)
        menu.addAction("Quit", self.quit_triggered.emit)

        self.setContextMenu(menu)

    def _toggle_watch(self) -> None:
        self._watch_enabled = not self._watch_enabled

        # Update menu text
        self._watch_action.setText(
            "Stop Watch Mode" if self._watch_enabled else "Start Watch Mode"
        )

        # Update icon
        if self._watch_enabled:
            self.setIcon(QIcon(self._icon_path_watch))
        else:
            self.setIcon(QIcon(self._icon_path_default))

        self.watch_toggled.emit(self._watch_enabled)
