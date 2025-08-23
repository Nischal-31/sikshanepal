from allauth.account.signals import user_signed_up, user_logged_in
from allauth.socialaccount.signals import social_account_added
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save

User = get_user_model()

# Only fire welcome email for social signups via Allauth
@receiver(user_signed_up)
def send_welcome_email_allauth(sender, request, user, **kwargs):
    try:
        send_welcome_email(user)
    except Exception as e:
        print("Error sending welcome email:", e)

# Only fire for custom registrations, not social signups
@receiver(post_save, sender=User)
def send_welcome_email_custom(sender, instance, created, **kwargs):
    if created:
        # Skip if user_signed_up already sent email
        if not hasattr(instance, '_welcome_email_sent'):
            try:
                send_welcome_email(instance)
                instance._welcome_email_sent = True
            except Exception as e:
                print("Error sending welcome email:", e)


# 🔹 Shared email sending logic
def send_welcome_email(user):
    subject = 'Welcome to Our Website'
    from_email = 'xenobaka2@gmail.com'
    to_email = user.email
    html_content = render_to_string('user/Email.html', {'username': user.username})
    send_mail(subject, '', from_email, [to_email], html_message=html_content)

@receiver(user_logged_in)
def set_user_type_on_login(sender, request, user, **kwargs):
    if hasattr(user, 'socialaccount_set') and user.socialaccount_set.filter(provider='google').exists():
        user.user_type = 'normal'
        user.save()

    token, created = Token.objects.get_or_create(user=user)
    # Save token key to session for later API use
    request.session['auth_token'] = token.key
    print(f"[user_logged_in] Token saved to session: {token.key}")

@receiver(social_account_added)
def set_user_type_on_social_login(sender, request, sociallogin, user, **kwargs):
    if sociallogin.account.provider == 'google':
        user.user_type = 'normal'
        user.save()

    token, created = Token.objects.get_or_create(user=user)
    # Save token key to session for social login as well
    request.session['auth_token'] = token.key
    print(f"[social_account_added] Token saved to session: {token.key}")

@receiver(social_account_added)
def set_default_user_type(sender, request, sociallogin, **kwargs):
    user = sociallogin.user
    if not user.user_type:
        user.user_type = 'normal'
        user.save()
