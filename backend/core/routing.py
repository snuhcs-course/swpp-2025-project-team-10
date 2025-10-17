"""
WebSocket URL routing for Book Bartering Social Network.

This file defines the WebSocket URL patterns for real-time features
like messaging, notifications, and live updates.
"""

# Import consumers when they're created
# from social.consumers import ChatConsumer, NotificationConsumer

websocket_urlpatterns = [
    # Chat/Messaging WebSocket
    # path('ws/chat/<uuid:room_id>/', ChatConsumer.as_asgi()),
    # Notifications WebSocket
    # path('ws/notifications/', NotificationConsumer.as_asgi()),
    # Book Club Discussion WebSocket
    # path('ws/club/<uuid:club_id>/', BookClubConsumer.as_asgi()),
    # Barter Updates WebSocket
    # path('ws/barter/<uuid:barter_id>/', BarterConsumer.as_asgi()),
]

# For now, return empty list until consumers are implemented
websocket_urlpatterns = []
