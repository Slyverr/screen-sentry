import signal
import sys

from screen_sentry.app import App
from screen_sentry.ipc import (
    try_send_to_running_instance,
    start_ipc_server,
)


def main() -> None:
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    args = sys.argv[1:]
    if try_send_to_running_instance(args):
        sys.exit(0)

    app = App()
    start_ipc_server(app)

    if args:
        app.handle_cli_command(args)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
