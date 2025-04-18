import sentry_sdk
from django.db import models
from django.core.validators import MaxValueValidator, MinLengthValidator


class Address(models.Model):
    """
    Represents a physical address with a street number,
    name, city, state, zip code, and country ISO code.
    """
    number = models.PositiveIntegerField(validators=[MaxValueValidator(9999)])
    street = models.CharField(max_length=64)
    city = models.CharField(max_length=64)
    state = models.CharField(max_length=2, validators=[MinLengthValidator(2)])
    zip_code = models.PositiveIntegerField(validators=[MaxValueValidator(99999)])
    country_iso_code = models.CharField(max_length=3, validators=[MinLengthValidator(3)])

    class Meta:
        verbose_name_plural = "Addresses"

    def __str__(self):
        """
        Returns a string representation of the address in the format: 'number street'.
        """
        return f'{self.number} {self.street}'

    def clean(self):
        try:
            super().clean()
        except Exception as e:
            # Capturing sentry exception
            sentry_sdk.capture_exception(e)
            sentry_sdk.capture_message("Erreur de validation dans le modèle Address")
            raise


class Letting(models.Model):
    """
    Represents a rental listing associated with a specific address.
    """
    title = models.CharField(max_length=256)
    address = models.OneToOneField(Address, on_delete=models.CASCADE)

    def __str__(self):
        """
        Returns the title of the letting.
        """
        return self.title

    def clean(self):
        try:
            super().clean()
        except Exception as e:
            # Capturing sentry exception
            sentry_sdk.capture_exception(e)
            sentry_sdk.capture_message("Erreur de validation dans le modèle Letting")
            raise
