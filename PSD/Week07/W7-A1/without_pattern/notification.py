from abc import ABC, abstractmethod

class Notification(ABC):
    @abstractmethod
    def send(self, message: str):
        pass

class EmailNotification(Notification):
    def send(self, message: str):
        print(f"📧 Email sent: {message}")

class SMSNotification(Notification):
    def send(self, message: str):
        print(f"📱 SMS sent: {message}")

class PushNotification(Notification):
    def send(self, message: str):
        print(f"🔔 Push notification sent: {message}")
