"""
Mobile API for Bazzite Gaming Optimization Suite

Mobile companion app integration with real-time monitoring,
remote profile switching, and push notifications.

Version: 1.3.1
"""

from .server import MobileAPIServer, PushNotificationManager, MetricsStreamer, MobileClientSDK

__all__ = [
    'MobileAPIServer',
    'PushNotificationManager',
    'MetricsStreamer',
    'MobileClientSDK',
]

__version__ = '1.3.1'
