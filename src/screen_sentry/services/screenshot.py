from PySide6.QtCore import QObject, QProcess, Signal

from screen_sentry.context import AppContext


class ScreenshotService(QObject):
    capture_finished = Signal(bytes)
    capture_failed = Signal(str)

    def __init__(self, ctx: AppContext, parent: QObject | None = None) -> None:
        super().__init__(parent)

        self._process: QProcess | None = None

    def capture(self) -> None:
        if self._process is not None:
            return

        self._process = QProcess(self)
        self._process.finished.connect(self._on_finished)
        self._process.start("flameshot", ["gui", "--raw"])

    def _on_finished(self, exit_code: int, status) -> None:
        process = self._process
        self._process = None
        if process is None:
            return

        data = process.readAllStandardOutput().data()
        if exit_code == 0 and data:
            self.capture_finished.emit(data)
        else:
            self.capture_failed.emit("Flameshot capture failed or was cancelled")
