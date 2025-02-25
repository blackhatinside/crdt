# diagram/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
from ypy_websocket.websocket_server import YRoom

class DiagramConsumer(AsyncWebsocketConsumer):
    rooms = {}

    async def connect(self):
        self.room_name = "default_room"
        if self.room_name not in self.rooms:
            self.rooms[self.room_name] = YRoom()
        self.room = self.rooms[self.room_name]
        await self.accept()
        await self.room.connect(self)

    async def receive(self, text_data):
        await self.room.receive(text_data, self)

    async def disconnect(self, close_code):
        await self.room.disconnect(self)