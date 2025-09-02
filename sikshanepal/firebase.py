import firebase_admin
from firebase_admin import credentials, messaging
import os

cred_path = "config/firebase/serviceAccountKey.json"

if not firebase_admin._apps:  # Prevent re-init errors
    print(f"[FIREBASE] Initializing with credentials at: {cred_path}")
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    print("[FIREBASE] Firebase initialized successfully!")


def send_blog_notification(title, body,blog_id=None ):
    """
    Send an FCM notification to the 'blogs' topic.
    """
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        topic="blogs",  # all subscribers
        data={
            "screen": "blogdetail" if blog_id else "notification",
            "blog_id": str(blog_id) if blog_id else "",
        }
    )
    try:
        response = messaging.send(message)
        print(f"[FIREBASE] Successfully sent message, response: {response}")
    except Exception as e:
        print(f"[ERROR] Failed to send notification: {e}")


def send_course_notification(title, body, course_id=None):
    """
    Send an FCM notification to the 'courses' topic.
    """
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        topic="courses",  # all subscribers
        data={
            "screen": "courses",
        }
    )
    try:
        response = messaging.send(message)
        print(f"[FIREBASE] Successfully sent course message, response: {response}")
    except Exception as e:
        print(f"[ERROR] Failed to send course notification: {e}")

def send_password_change_notification(token, title="Password Updated", body="Your password has been changed successfully!"):
    """
    Send a personal FCM notification to a specific device when the password is changed.
    Opens the 'profile' screen on tap.
    """
    if not token:
        print("[FIREBASE] No token provided, skipping personal notification.")
        return

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token,  # specific device
        data={
            "screen": "profile"
        }
    )

    try:
        response = messaging.send(message)
        print(f"[FIREBASE] Successfully sent password-change notification, response: {response}")
    except Exception as e:
        print(f"[ERROR] Failed to send password-change notification: {e}")
