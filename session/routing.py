from django.urls import path
from . import consumers


websocket_urlpatterns = [
    path('ws/session/<str:session_id>/', consumers.ChatConsumer),
]