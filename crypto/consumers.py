import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PriceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("WebSocket подключен!")
        await self.accept()

    async def disconnect(self, close_code):
        print(f"WebSocket отключён! Код: {close_code}")

    async def connect(self):
        await self.channel_layer.group_add("prices", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("prices", self.channel_name)

    async def send_price_update(self, event):
        data = event.get("data", {})
        await self.send(text_data=json.dumps(data))
