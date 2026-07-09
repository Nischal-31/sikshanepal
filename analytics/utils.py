from .models import UserEvent


def get_client_ip(request):
    """
    Returns the client's IP address.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


def log_event(request, action: str, item_type: str, item_id: int):
    """
    Logs a user interaction for analytics and recommendation generation.
    """

    user = request.user if request.user.is_authenticated else None

    # Ensure a session exists
    if not request.session.session_key:
        request.session.save()

    UserEvent.objects.create(
        user=user,
        action=action,
        item_type=item_type,
        item_id=item_id,
        session_key=request.session.session_key or "",
        ip_address=get_client_ip(request),      # ✅ Updated field name
        user_agent=(request.META.get("HTTP_USER_AGENT") or "")[:255],
    )