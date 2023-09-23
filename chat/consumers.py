import base64
import json
import secrets
from datetime import datetime

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.core.files.base import ContentFile

from users.models import MyUser
from .models import Message, Conversation
from .serializers import MessageSerializer
from .tasks import get_gpt_response as ggr


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()
        # async_to_sync(self.channel_layer.send)(
        # channel_name, {"type": "chat.message", "message": message}
        # )
        print("connection accepted")

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data=None, bytes_data=None):
        # parse the json data into dictionary object
        print("Received message , ", text_data)
        text_data_json = json.loads(text_data)

    
        # unpack the dictionary into the necessary parts
        message, attachment = (
            text_data_json["message"],
            text_data_json.get("attachment"),
        )
      
        conversation = Conversation.objects.get(id=int(self.room_name))
        sender = self.scope["user"]
        
        # Attachment
        if attachment:
            file_str, file_ext = attachment["data"], attachment["format"]

            file_data = ContentFile(
                base64.b64decode(file_str), name=f"{secrets.token_hex(8)}.{file_ext}"
            )
            _message = Message.objects.create(
                sender=sender,
                attachment=file_data,
                text=message,
                conversation_id=conversation,
                is_from_user=True,
                message_type=Message.MessageType.User
            )
        else:
            _message = Message.objects.create(
                sender=sender,
                text=message,
                conversation_id=conversation,
                is_from_user=True,
                message_type=Message.MessageType.User
            )
        # Send message to room group
        chat_type = {"type": "chat_message"}
        message_serializer = (dict(MessageSerializer(instance=_message).data))
        return_dict = {**chat_type, **message_serializer}
        if _message.attachment:
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "sender": sender.email,
                    "attachment": _message.attachment.url,
                    "time": str(_message.timestamp),
                },
            )
        else:
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                return_dict,
            )
        task_id = ggr.delay(self.channel_name, conversation.id, message)
        print("New celery task : "+ str(task_id))
        #      async_to_sync(self.channel_layer.send)(
        # channel_name, {"type": "chat.message", "message": message}
        # )

    # Receive message from room group
    def chat_message(self, event):
        dict_to_be_sent = event.copy()
        dict_to_be_sent.pop("type")
        self.send(
                text_data=json.dumps(
                    dict_to_be_sent
                )
            )
