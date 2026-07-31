import json
from channels.generic.websocket import AsyncWebsocketConsumer


class IncidentConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.channel_layer.group_add(
            "incidents",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "incidents",
            self.channel_name
        )

    # NEW INCIDENT
    async def new_incident(self, event):
        print("🔥 Consumer received:", event)
        data = event["data"]

        data["message_type"] = "new_incident"

        await self.send(
            text_data=json.dumps(data)
        )

    # STATUS UPDATE
    async def status_update(self, event):

        data = event["data"]

        data["message_type"] = "status_update"
        print("🔥 STATUS UPDATE RECEIVED In consumer:", event)
        await self.send(
            text_data=json.dumps(data)
        )