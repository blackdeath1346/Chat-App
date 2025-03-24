import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from .models import CommonMessage
from .serializers import CommonMessageSerializer

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Handles WebSocket connection when a user joins a chat.
        """
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group_name = f"chat_{self.chat_id}"
        
        # Add the user to the chat group
        await self.channel_layer.group_add(self.chat_group_name, self.channel_name)

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        """
        Handles WebSocket disconnection.
        """
        await self.channel_layer.group_discard(self.chat_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        sender = data["sender"]
        content = data["content"]
        file_attachment = data.get("file_attachment", None)
        reply_to = data.get("reply_to", None)
        
        # Broadcast the message including file attachment and reply_to if provided
        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                "type": "chat.message",
                "message": {
                    "sender": sender,
                    "content": content,
                    "file_attachment": file_attachment,
                    "reply_to": reply_to,
                }
            }
        )

    async def chat_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps(message))


class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Handles WebSocket connection when a user joins a group chat.
        """
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.group_group_name = f"group_{self.group_id}"
        
        # Add the user to the group chat
        await self.channel_layer.group_add(self.group_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        sender = data["sender"]
        content = data["content"]
        reply_to = data.get("reply_to", None)
        
        # Broadcast the group message including reply_to if provided
        await self.channel_layer.group_send(
            self.group_group_name,
            {
                "type": "group.message",
                "message": {
                    "sender": sender,
                    "content": content,
                    "reply_to": reply_to,
                }
            }
        )

    async def group_message(self, event):
        await self.send(text_data=json.dumps(event["message"]))


class BroadcastConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handles WebSocket connection for broadcasting."""
        self.group_name = "broadcast_group"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        sender_username = data["sender"]
        content = data["content"]

        sender = await sync_to_async(User.objects.get)(username=sender_username)

        message = await sync_to_async(CommonMessage.objects.create)(
            sender=sender, content=content
        )

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "broadcast.message",
                "message": {
                    "sender": sender_username,
                    "content": content,
                    "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                }
            }
        )

    async def broadcast_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps(message))
