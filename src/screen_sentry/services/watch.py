from PySide6.QtCore import QObject, QProcess, QTimer, Signal

from screen_sentry.context import AppContext


class WatchService(QObject):
    watch_capture_finished = Signal(bytes)
    watch_capture_failed = Signal(str)

    def __init__(self, ctx: AppContext, parent: QObject | None = None) -> None:

        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._capture)

        self._process: QProcess | None = None

    def start(self) -> None:
        self._timer.start()

    def stop(self) -> None:
        self._timer.stop()

    def toggle(self) -> None:
        if self.is_running():
            self._timer.stop()
        else:
            self._timer.start()

    def is_running(self) -> bool:
        return self._timer.isActive()

    def _capture(self) -> None:
        if self._process is not None:
            return

        self._process = QProcess(self)
        self._process.finished.connect(self._on_finished)
        self._process.start("flameshot", ["full", "--raw"])

    def _on_finished(self, exit_code: int, status) -> None:
        process = self._process
        self._process = None
        if process is None:
            return

        data = process.readAllStandardOutput().data()
        if exit_code == 0 and data:
            self.watch_capture_finished.emit(data)
        else:
            self.watch_capture_failed.emit("Watch capture failed")
