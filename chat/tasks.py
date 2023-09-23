import requests
from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from django.core.cache import cache
from core.utlis import askGPT
from .models import Conversation, Message
from .serializers import MessageSerializer
from ChatAPI.celery import app

channel_layer = get_channel_layer()

import time


# @app.task
@shared_task
def get_gpt_response(channel_name, conversation_id, prompt):
    has_errors, message = askGPT(conversation_id, prompt)
    # print("Before sleeping")
    # time.sleep(5)
    # print("After sleep")
    # has_errors, message = (True, "Not really")

    if not has_errors:
        conversation = Conversation.objects.get(id=conversation_id)
        sender = conversation.initiator
        _message = Message.objects.create(
            sender=sender,
            text=message,
            conversation_id=conversation,
            is_from_user=False,
            message_type=Message.MessageType.Assistant
        )
        # Send message to room group
        chat_type = {"type": "chat_message"}
        message_serializer = (dict(MessageSerializer(instance=_message).data))
        return_dict = {**chat_type, **message_serializer}

        async_to_sync(channel_layer.send)(
            channel_name,
            return_dict,
        )
    else:    
        async_to_sync(channel_layer.send)(
            channel_name, {"type": "chat.message", "message": message}
        )

@shared_task
def add(channel_name, x, y):
    message = "{}+{}={}".format(x, y, int(x) + int(y))
    async_to_sync(channel_layer.send)(
        channel_name, {"type": "chat.message", "message": message}
    )


@shared_task
def url_status(channel_name, url):
    if not url.startswith("http"):
        url = f"https://{url}"

    status = cache.get(url)
    if not status:
        try:
            r = requests.get(url, timeout=10)
            status = r.status_code
            cache.set(url, status, 60 * 60)
        except requests.exceptions.RequestException:
            status = "Not available"

    message = f"{url} status is {status}"
    async_to_sync(channel_layer.send)(
        channel_name, {"type": "chat.message", "message": message}
    )