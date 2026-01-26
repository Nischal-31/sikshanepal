# analytics/utils.py
from .models import UserEvent

def log_event(request, action: str, item_type: str, item_id: int):
    user = request.user if request.user.is_authenticated else None

    if not request.session.session_key:
        request.session.save()

    UserEvent.objects.create(
        user=user,
        action=action,
        item_type=item_type,
        item_id=item_id,
        session_key=request.session.session_key or "",
        ip=request.META.get("REMOTE_ADDR"),
        user_agent=(request.META.get("HTTP_USER_AGENT") or "")[:255],
    )
