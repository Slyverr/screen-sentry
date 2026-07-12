from PySide6.QtNetwork import QLocalServer, QLocalSocket

SERVER_NAME = "screen-sentry"


def try_send_to_running_instance(args: list[str]) -> bool:
    socket = QLocalSocket()
    socket.connectToServer(SERVER_NAME)
    if not socket.waitForConnected(200):
        return False

    message = " ".join(args) if args else "ping"
    socket.write(message.encode("utf-8"))
    socket.waitForBytesWritten(200)
    socket.disconnectFromServer()
    return True


def start_ipc_server(app) -> QLocalServer:
    QLocalServer.removeServer(SERVER_NAME)
    server = QLocalServer()
    server.listen(SERVER_NAME)

    def _on_new_connection():
        socket = server.nextPendingConnection()
        socket.waitForReadyRead(200)
        message = bytes(socket.readAll().data()).decode("utf-8")
        socket.disconnectFromServer()

        if message != "ping":
            app.handle_cli_command(message.split(" "))

    server.newConnection.connect(_on_new_connection)
    return server
