__all__ = [
    'delete_message',
    'edit_message',
    'notify_user',
    'statistics',
    'send_log',
    'messages',
    'enumz',
]

def get_notification_types():
    """Ленивая загрузка NotificationTypes enum"""
    from .enumz.types_notifications import NotificationTypes
    return NotificationTypes