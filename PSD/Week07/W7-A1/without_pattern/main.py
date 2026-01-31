from notification import EmailNotification, SMSNotification, PushNotification


def main():
    notification_type = input("Enter notification type (email/sms/push): ").lower()

    if notification_type == "email":
        notification = EmailNotification()
    elif notification_type == "sms":
        notification = SMSNotification()
    elif notification_type == "push":
        notification = PushNotification()
    else:
        raise ValueError("Invalid notification type")

    notification.send("Hello! This is a Factory Pattern example.")


if __name__ == "__main__":
    main()
