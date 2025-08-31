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
