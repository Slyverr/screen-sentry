import signal
import sys

from screen_sentry.app import App


def main() -> None:
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = App()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
