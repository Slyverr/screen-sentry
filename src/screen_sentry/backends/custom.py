from __future__ import annotations

import base64
import json
from dataclasses import dataclass, field

from PySide6.QtCore import QUrl, QByteArray
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

from screen_sentry.backends.base import Backend
from screen_sentry.config.prompts import SYSTEM_PROMPT, USER_PROMPT

REQUIRED_PLACEHOLDERS = ("{{system}}", "{{prompt}}", "{{image}}")


@dataclass
class CustomOptions:
    url: str
    body: str
    response_path: str
    headers: dict[str, str] = field(default_factory=dict)
    model: str | None = None
    api_key: str | None = None
    timeout: int = 60


class CustomBackend(Backend):
    """
    Backend for user-defined request/response formats, for endpoints that
    don't match the openai_compat or anthropic API shapes.

    The user supplies the raw request `body` (as a JSON string containing
    placeholders) and, optionally, `headers`. Placeholders are substituted
    at send-time:

        {{system}}   -> the app's system prompt          (required)
        {{prompt}}   -> the app's user prompt             (required)
        {{image}}    -> base64-encoded image, no data URI (required)
        {{model}}    -> value of `model` in config         (optional)
        {{api_key}}  -> value of `api_key` in config        (optional)

    `response_path` is a dot-notation path used to extract the model's
    text reply from the JSON response, e.g. "choices.0.message.content".

    Expected [providers.X] config keys:
        url (str): full request URL
        body (str): JSON request body template containing the required
            placeholders above
        response_path (str): dot-notation path into the JSON response
        headers (table, optional): request headers; values may also
            contain {{api_key}} / {{model}} placeholders
        model (str, optional): substituted into {{model}} if present
        api_key (str, optional): substituted into {{api_key}} if present
        timeout (int, optional): request timeout in seconds, default 60
    """

    def __init__(self, provider_name: str, config: dict, parent=None) -> None:
        super().__init__(provider_name, config, parent)
        self._manager = QNetworkAccessManager(self)
        self._opts = self._validate_config(config)

    def _validate_config(self, config: dict) -> CustomOptions:
        url = config.get("url", "").strip()
        if not url:
            raise ValueError(f"[{self.provider_name}] missing 'url' in provider config")

        body = config.get("body", "")
        if not body:
            raise ValueError(
                f"[{self.provider_name}] missing 'body' in provider config"
            )

        missing = [p for p in REQUIRED_PLACEHOLDERS if p not in body]
        if missing:
            raise ValueError(
                f"[{self.provider_name}] 'body' is missing required placeholder(s): "
                f"{', '.join(missing)}"
            )

        response_path = config.get("response_path", "").strip()
        if not response_path:
            raise ValueError(
                f"[{self.provider_name}] missing 'response_path' in provider config"
            )

        return CustomOptions(
            url=url,
            body=body,
            response_path=response_path,
            headers=dict(config.get("headers", {})),
            model=config.get("model"),
            api_key=config.get("api_key"),
            timeout=config.get("timeout", 60),
        )

    def send(self, image_bytes: bytes) -> None:
        image_b64 = base64.b64encode(image_bytes).decode("ascii")

        rendered_body = self._render(self._opts.body, image_b64)
        try:
            payload = json.loads(rendered_body)
        except json.JSONDecodeError as exc:
            self._fail_api(
                f"'body' did not produce valid JSON after substitution: {exc}"
            )
            return

        request = QNetworkRequest(QUrl(self._opts.url))
        request.setHeader(
            QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json"
        )

        for key, value in self._opts.headers.items():
            rendered_value = self._render(value, image_b64=None)
            request.setRawHeader(key.encode("utf-8"), rendered_value.encode("utf-8"))

        body_bytes = QByteArray(json.dumps(payload).encode("utf-8"))
        reply = self._manager.post(request, body_bytes)
        reply.finished.connect(lambda: self._on_finished(reply))

    def _render(self, template: str, image_b64: str | None) -> str:
        """Substitute placeholders. image_b64=None skips {{image}} (used for headers)."""
        rendered = template.replace(
            "{{system}}", json.dumps(SYSTEM_PROMPT)[1:-1]
        ).replace("{{prompt}}", json.dumps(USER_PROMPT)[1:-1])

        if image_b64 is not None:
            rendered = rendered.replace("{{image}}", image_b64)
        if self._opts.model is not None:
            rendered = rendered.replace("{{model}}", self._opts.model)
        if self._opts.api_key is not None:
            rendered = rendered.replace("{{api_key}}", self._opts.api_key)
        return rendered

    def _on_finished(self, reply: QNetworkReply) -> None:
        reply.deleteLater()

        if reply.error() != QNetworkReply.NetworkError.NoError:
            status = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
            if status is None:
                self._fail_network(reply.errorString())
            else:
                self._fail_api(f"HTTP {status}: {reply.errorString()}")
            return

        raw = bytes(reply.readAll().data())
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            self._fail_api("response was not valid JSON")
            return

        try:
            text = self._extract(data, self._opts.response_path)
        except (KeyError, IndexError, TypeError) as exc:
            self._fail_api(
                f"response_path '{self._opts.response_path}' did not match response: {exc}"
            )
            return

        self.succeeded.emit(text)

    @staticmethod
    def _extract(data, path: str) -> str:
        value = data
        for part in path.split("."):
            value = value[int(part)] if part.isdigit() else value[part]
        return value
