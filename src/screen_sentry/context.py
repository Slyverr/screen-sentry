from screen_sentry.config.config import AppConfig
from screen_sentry.config.providers import ProvidersConfig


class AppContext:
    def __init__(self) -> None:
        self.app_config = AppConfig()
        self.providers_config = ProvidersConfig()
