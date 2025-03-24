from django.urls import re_path
from .consumers import ChatConsumer,BroadcastConsumer,GroupChatConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<chat_id>[\w-]+)/$", ChatConsumer.as_asgi()),
    re_path(r"ws/broadcast/$", BroadcastConsumer.as_asgi()),
    re_path(r"ws/group/(?P<group_id>[\w-]+)/$", GroupChatConsumer.as_asgi()),
]
