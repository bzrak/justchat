import logging
from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect

from chat_server.connection.context import ConnectionContext
from chat_server.handler import router
from chat_server.protocol.message import BaseMessage


class ConnectionManager:
    """
    Manages WebSocket connections.
    """

    def __init__(self) -> None:
        self.active_connections: list[ConnectionContext] = []
        self._count: int = 0

    async def connect(self, websocket: WebSocket) -> None:
        """
        Accept and register a new WebSocket connection.

        If invalid connection raise a WebSocketDisconnect
        """

        await websocket.accept()
        self._count += 1
        conn_data = ConnectionContext(websocket=websocket, id=self._count, manager=self)
        if await conn_data.establish_connection():
            logging.info(f"Created ConnectionContext: {conn_data}")
            self.active_connections.append(conn_data)
        else:
            await websocket.close(reason="Invalid HELLO")
            raise WebSocketDisconnect

    def get_connection(self, websocket: WebSocket) -> "ConnectionContext | None":
        """
        Get the ConnectionContext for a given WebSocket.
        """
        # PERF: Not the most efficient lookup
        for conn in self.active_connections:
            if conn.websocket == websocket:
                return conn
        return None

    async def disconnect(self, websocket: WebSocket) -> None:
        """
        Remove a WebSocket connection from active connections.
        """
        # PERF: Not the most efficient lookup
        for conn in self.active_connections:
            if conn.websocket == websocket:
                self.active_connections.remove(conn)
                break
        logging.info("Connection disconnected.")

    async def handle_message(self, websocket: WebSocket, data: str) -> None:
        """
        Handle the message received by client appropriately
        """
        logging.info(f"CLIENT SEND: {data}")
        msg = BaseMessage.from_json(data)
        if msg is not None:
            ctx = self.get_connection(websocket)
            if ctx is not None:
                await router.dispatch(ctx, msg)
            else:
                logging.warning("Received message from unknown connection")

    async def send_text_all(self, message: str) -> None:
        for conn in self.active_connections:
            await conn.websocket.send_text(message)
