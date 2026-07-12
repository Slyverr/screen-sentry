from abc import abstractmethod

from PySide6.QtCore import QObject, Signal


class Backend(QObject):
    succeeded = Signal(str)
    network_error = Signal(str)
    api_error = Signal(str)

    def __init__(
        self, provider_name: str, config: dict, parent: QObject | None = None
    ) -> None:
        super().__init__(parent)

        self.provider_name = provider_name
        self.config = config

    @abstractmethod
    def send(self, image_bytes: bytes) -> None:
        raise NotImplementedError

    def _fail_network(self, detail: str) -> None:
        self.network_error.emit(f"[{self.provider_name}] {detail}")

    def _fail_api(self, detail: str) -> None:
        self.api_error.emit(f"[{self.provider_name}] {detail}")
