from django.contrib.auth.models import User
from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver
import sentry_sdk


@receiver(user_login_failed)
def log_failed_login(sender, credentials, **kwargs):
    username = credentials.get('username')
    if not username:
        # No Username given
        sentry_sdk.capture_message("Échec de connexion sans nom d'utilisateur fourni.")
        return

    if User.objects.filter(username=username).exists():
        # Failed Password
        sentry_sdk.capture_message(f"Échec de connexion pour l'utilisateur existant: {username}")
    else:
        # Failed Username
        sentry_sdk.capture_message(f"Échec de connexion pour l'utilisateur inexistant: {username}")
