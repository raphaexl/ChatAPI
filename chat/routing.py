from django.urls import path, re_path

from . import consumers

websocket_urlpatterns = [
    path("ws/chat/<int:room_name>", consumers.ChatConsumer.as_asgi()),
    #re_path(r"ws/chat/(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()),
]
