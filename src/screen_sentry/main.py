import signal
import sys

from screen_sentry.app import App
from screen_sentry.cli import app as cli_app
from screen_sentry.ipc import start_ipc_server, try_send_to_running_instance


def main() -> None:
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    if len(sys.argv) > 1:
        cli_app()
        return

    if try_send_to_running_instance([]):
        print(
            "Screen Sentry is already running — check your system tray, or use `screen-sentry --help` for CLI commands."
        )
        sys.exit(0)

    app = App()
    start_ipc_server(app)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
