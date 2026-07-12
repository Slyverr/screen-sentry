import os

from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from screen_sentry.context import AppContext

_ASSETS_DIR = os.path.dirname(os.path.dirname(__file__))
_ICON_PATH_WATCH = os.path.join(_ASSETS_DIR, "assets", "icon-watch.svg")
_ICON_PATH_DEFAULT = os.path.join(_ASSETS_DIR, "assets", "icon.svg")


class TrayIcon(QSystemTrayIcon):
    quit_triggered = Signal()
    capture_triggered = Signal()
    watch_toggled = Signal(bool)

    def __init__(self, ctx: AppContext) -> None:
        super().__init__()

        self._ctx = ctx

        self._build_menu()
        self._update_ui_state()

    def _build_menu(self) -> None:
        menu = QMenu()

        menu.addAction("Capture", self.capture_triggered.emit)
        self._watch_action = menu.addAction("Start Watch Mode")
        self._watch_action.triggered.connect(self._toggle_watch)
        menu.addAction("Quit", self.quit_triggered.emit)

        self.setContextMenu(menu)

    def _toggle_watch(self) -> None:
        watch_enabled = self._ctx.watch_service.is_running()
        new_state = not watch_enabled

        self.watch_toggled.emit(new_state)
        self._update_ui_state()

    def _update_ui_state(self) -> None:
        is_running = self._ctx.watch_service.is_running()

        if is_running:
            self.setIcon(QIcon(_ICON_PATH_WATCH))
            self._watch_action.setText("Stop Watch Mode")
        else:
            self.setIcon(QIcon(_ICON_PATH_DEFAULT))
            self._watch_action.setText("Start Watch Mode")
