import sentry_sdk
from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """
    Represents a user profile with additional information linked to a Django User.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    favorite_city = models.CharField(max_length=64, blank=True)

    def __str__(self):
        """
        Returns the username associated with this profile.
        """
        return self.user.username

    def clean(self):
        try:
            super().clean()
        except Exception as e:
            # Capturing sentry exception
            sentry_sdk.capture_exception(e)
            sentry_sdk.capture_message("Erreur de validation dans le modèle Profile")
            raise
