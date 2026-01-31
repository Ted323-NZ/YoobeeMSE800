from notification import EmailNotification, SMSNotification, PushNotification

class NotificationFactory:
    @staticmethod
    def create_notification(notification_type: str):
        if notification_type == "email":
            return EmailNotification()
        elif notification_type == "sms":
            return SMSNotification()
        elif notification_type == "push":
            return PushNotification()
        else:
            raise ValueError("Invalid notification type")
