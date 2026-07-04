import sys

from PySide6.QtWidgets import QApplication


class App(QApplication):
    def __init__(self, argv: list[str] = sys.argv) -> None:
        super().__init__(argv)

        self.setApplicationName("Screen Sentry")
        self.setApplicationVersion("0.1.0")
