import typer

from screen_sentry.ipc import try_send_to_running_instance

app = typer.Typer(help="Screen Sentry — screen monitoring and threat analysis.")
watch_app = typer.Typer(help="Control watch mode.")
app.add_typer(watch_app, name="watch")


def _send_or_dispatch(args: list[str]) -> None:
    if not try_send_to_running_instance(args):
        typer.echo("Screen Sentry is not running. Start it first.")
        raise typer.Exit(code=1)


@app.command()
def capture() -> None:
    """Take a single screenshot and analyze it."""
    _send_or_dispatch(["capture"])


@watch_app.command("on")
def watch_on() -> None:
    """Start watch mode."""
    _send_or_dispatch(["watch", "on"])


@watch_app.command("off")
def watch_off() -> None:
    """Stop watch mode."""
    _send_or_dispatch(["watch", "off"])


@watch_app.command("toggle")
def watch_toggle() -> None:
    """Toggle watch mode on/off."""
    _send_or_dispatch(["watch", "toggle"])


@app.command()
def quit() -> None:
    """Quit Screen Sentry."""
    _send_or_dispatch(["quit"])
