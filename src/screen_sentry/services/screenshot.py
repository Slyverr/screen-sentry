from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, QProcess, Signal

from screen_sentry.context import AppContext


class ScreenshotService(QObject):
    capture_finished = Signal(Path)
    capture_failed = Signal(str)

    def __init__(self, ctx: AppContext, parent: QObject | None = None) -> None:
        super().__init__(parent)

        self._save_dir = ctx.app_config.save_dir
        self._save_dir.mkdir(parents=True, exist_ok=True)
        self._process: QProcess | None = None

    def capture(self) -> None:
        if self._process is not None:
            return

        path = self._save_dir / f"capture_{datetime.now():%Y%m%d_%H%M%S}.png"
        self._process = QProcess(self)
        self._process.finished.connect(
            lambda code, status: self._on_finished(code, path)
        )
        self._process.start("flameshot", ["gui", "-p", str(path)])

    def _on_finished(self, exit_code: int, path: Path) -> None:
        self._process = None
        if exit_code == 0 and path.exists():
            self.capture_finished.emit(path)
        else:
            self.capture_failed.emit("Flameshot capture failed or was cancelled")
