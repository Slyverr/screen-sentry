import base64
import json
from dataclasses import dataclass

from PySide6.QtCore import QByteArray, QUrl
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest

from screen_sentry.backends.base import Backend
from screen_sentry.config.prompts import SYSTEM_PROMPT, USER_PROMPT


@dataclass
class OpenAICompatOptions:
    base_url: str
    model: str
    temperature: float = 0.2
    api_key: str | None = None


class OpenAICompatBackend(Backend):
    def __init__(self, provider_name: str, config: dict, parent=None) -> None:
        super().__init__(provider_name, config, parent)

        self._manager = QNetworkAccessManager(self)
        self._opts = self._validate_config(config)

    def _validate_config(self, config: dict) -> OpenAICompatOptions:
        base_url = config.get("base_url", "").rstrip("/")
        if not base_url:
            raise ValueError(
                f"[{self.provider_name}] missing 'base_url' in provider config"
            )

        model = config.get("model")
        if not model:
            raise ValueError(
                f"[{self.provider_name}] missing 'model' in provider config"
            )

        return OpenAICompatOptions(
            base_url=base_url,
            model=model,
            temperature=config.get("temperature", 0.2),
            api_key=config.get("api_key"),
        )

    def send(self, image_bytes: bytes) -> None:
        image_b64 = base64.b64encode(image_bytes).decode("ascii")

        payload = {
            "model": self._opts.model,
            "temperature": self._opts.temperature,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": USER_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{image_b64}"},
                        },
                    ],
                },
            ],
        }

        request = QNetworkRequest(QUrl(f"{self._opts.base_url}/chat/completions"))
        request.setHeader(
            QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json"
        )

        if self._opts.api_key:
            request.setRawHeader(
                b"Authorization", f"Bearer {self._opts.api_key}".encode("utf-8")
            )

        body = QByteArray(json.dumps(payload).encode("utf-8"))
        reply = self._manager.post(request, body)
        reply.finished.connect(lambda: self._on_finished(reply))

    def _on_finished(self, reply: QNetworkReply) -> None:
        reply.deleteLater()

        if reply.error() != QNetworkReply.NetworkError.NoError:
            status = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
            raw = bytes(reply.readAll().data())

            if status is None:
                self._fail_network(reply.errorString())
            else:
                detail = self._extract_error_detail(raw) or reply.errorString()
                self._fail_api(f"HTTP {status}: {detail}")
            return

        raw = bytes(reply.readAll().data())
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            self._fail_api("response was not valid JSON")
            return

        try:
            text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            self._fail_api(f"unexpected response shape: {data!r}")
            return

        self.succeeded.emit(text)

    @staticmethod
    def _extract_error_detail(raw: bytes) -> str | None:
        try:
            data = json.loads(raw)
            return data.get("error", {}).get("message")
        except (json.JSONDecodeError, AttributeError):
            return None
