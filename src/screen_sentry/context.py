from screen_sentry.config.config import AppConfig
from screen_sentry.config.providers import ProvidersConfig

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from screen_sentry.services.screenshot import ScreenshotService
    from screen_sentry.services.watch import WatchService
    from screen_sentry.services.analyze import AnalyzeService


class AppContext:
    screenshot_service: ScreenshotService
    analyze_service: AnalyzeService
    watch_service: WatchService

    def __init__(self) -> None:
        self.app_config = AppConfig()
        self.providers_config = ProvidersConfig()
