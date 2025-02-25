# project/routing.py
from django.urls import re_path
from diagram.consumers import DiagramConsumer

websocket_urlpatterns = [
    re_path(r'ws/diagram/$', DiagramConsumer.as_asgi()),
]