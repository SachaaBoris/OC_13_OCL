import sentry_sdk
from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.template.exceptions import TemplateDoesNotExist
from .models import Address, Letting


class AddressModelTest(TestCase):
    """
    Test case for the Address model.
    """

    def setUp(self):
        """
        Sets up test data for Address model.
        """
        self.address = Address.objects.create(
            number=1,
            street="Test Street",
            city="Test City",
            state="TS",
            zip_code=12345,
            country_iso_code="TST"
        )

    def test_address_creation(self):
        """
        Tests that the Address model can be created with valid data.
        """
        self.assertEqual(self.address.number, 1)
        self.assertEqual(self.address.street, "Test Street")
        self.assertEqual(self.address.city, "Test City")
        self.assertEqual(self.address.state, "TS")
        self.assertEqual(self.address.zip_code, 12345)
        self.assertEqual(self.address.country_iso_code, "TST")

    def test_address_str(self):
        """
        Tests the string representation of the Address model.
        """
        self.assertEqual(str(self.address), "1 Test Street")

    def test_address_number_validator(self):
        """
        Tests the MaxValueValidator for the number field.
        """
        invalid_address = Address(
            number=10000,  # Exceeds MaxValueValidator(9999)
            street="Test Street",
            city="Test City",
            state="TS",
            zip_code=12345,
            country_iso_code="TST"
        )
        with self.assertRaises(ValidationError):
            invalid_address.full_clean()

    def test_address_state_validator(self):
        """
        Tests the MinLengthValidator for the state field.
        """
        invalid_address = Address(
            number=1,
            street="Test Street",
            city="Test City",
            state="T",  # Less than MinLengthValidator(2)
            zip_code=12345,
            country_iso_code="TST"
        )
        with self.assertRaises(ValidationError):
            invalid_address.full_clean()

    def test_address_zip_code_validator(self):
        """
        Tests the MaxValueValidator for the zip_code field.
        """
        invalid_address = Address(
            number=1,
            street="Test Street",
            city="Test City",
            state="TS",
            zip_code=100000,  # Exceeds MaxValueValidator(99999)
            country_iso_code="TST"
        )
        with self.assertRaises(ValidationError):
            invalid_address.full_clean()

    def test_address_country_iso_code_validator(self):
        """
        Tests the MinLengthValidator for the country_iso_code field.
        """
        invalid_address = Address(
            number=1,
            street="Test Street",
            city="Test City",
            state="TS",
            zip_code=12345,
            country_iso_code="TS"  # Less than MinLengthValidator(3)
        )
        with self.assertRaises(ValidationError):
            invalid_address.full_clean()

    def test_address_clean_exception_sentry(self):
        """
        Test that exceptions in the clean() method of the Address model
        are properly captured by Sentry.
        """
        # Backup original sentry functions
        original_capture_exception = sentry_sdk.capture_exception
        original_capture_message = sentry_sdk.capture_message

        sentry_calls = []

        # Mocks for Sentry capture
        def mock_capture_exception(exc):
            sentry_calls.append(('exception', exc))

        def mock_capture_message(msg):
            sentry_calls.append(('message', msg))

        # Create an address instance to test
        address = Address.objects.create(
            number=1,
            street="Test Street",
            city="Test City",
            state="TS",
            zip_code=12345,
            country_iso_code="TST"
        )

        # Backup the original clean method from models.Model (the superclass)
        original_super_clean = address.__class__.__base__.clean

        # Mock the superclass clean method to raise an exception
        def mock_super_clean(self):
            raise ValidationError("Mock validation failure")

        try:
            # Apply mocks
            sentry_sdk.capture_exception = mock_capture_exception
            sentry_sdk.capture_message = mock_capture_message
            address.__class__.__base__.clean = mock_super_clean  # Simulate exception

            # Trigger the clean() method which should catch the exception
            with self.assertRaises(ValidationError):
                address.clean()

            # Check Sentry was called properly
            exception_logged = any(
                call[0] == 'exception' and isinstance(call[1], ValidationError)
                for call in sentry_calls
            )
            message_logged = any(
                call == ('message', "Erreur de validation dans le modèle Address")
                for call in sentry_calls
            )

            self.assertTrue(exception_logged)
            self.assertTrue(message_logged)

        finally:
            # Restore original methods
            sentry_sdk.capture_exception = original_capture_exception
            sentry_sdk.capture_message = original_capture_message
            address.__class__.__base__.clean = original_super_clean


class LettingModelTest(TestCase):
    """
    Test case for the Letting model.
    """

    def setUp(self):
        """
        Sets up test data for Letting model.
        """
        self.address = Address.objects.create(
            number=1,
            street="Test Street",
            city="Test City",
            state="TS",
            zip_code=12345,
            country_iso_code="TST"
        )
        self.letting = Letting.objects.create(
            title="Test Letting",
            address=self.address
        )

    def test_letting_creation(self):
        """
        Tests that the Letting model can be created with valid data.
        """
        self.assertEqual(self.letting.title, "Test Letting")
        self.assertEqual(self.letting.address, self.address)

    def test_letting_str(self):
        """
        Tests the string representation of the Letting model.
        """
        self.assertEqual(str(self.letting), "Test Letting")

    def test_letting_address_relation(self):
        """
        Tests the OneToOne relationship between Letting and Address.
        """
        self.assertEqual(self.letting.address.street, "Test Street")
        self.assertEqual(self.letting.address.city, "Test City")

    def test_letting_cascade_delete(self):
        """
        Tests that when an Address is deleted, the associated Letting is also deleted.
        """
        address_id = self.address.id
        self.address.delete()

        # Verify that the letting was deleted along with the address
        with self.assertRaises(Letting.DoesNotExist):
            Letting.objects.get(address_id=address_id)

    def test_letting_clean_exception_sentry(self):
        """
        Test that exceptions in the clean() method of the Letting model
        are properly captured by Sentry.
        """
        # Backup original sentry functions
        original_capture_exception = sentry_sdk.capture_exception
        original_capture_message = sentry_sdk.capture_message

        sentry_calls = []

        # Mocks for Sentry capture
        def mock_capture_exception(exc):
            sentry_calls.append(('exception', exc))

        def mock_capture_message(msg):
            sentry_calls.append(('message', msg))

        # Use the letting instance from setUp
        letting = self.letting

        # Backup the original clean method from models.Model (the superclass)
        original_super_clean = letting.__class__.__base__.clean

        # Mock the superclass clean method to raise an exception
        class CustomError(Exception):
            """Custom exception to trigger in clean()."""
            pass

        def mock_super_clean(self):
            raise CustomError("Mock letting validation failure")

        try:
            # Apply mocks
            sentry_sdk.capture_exception = mock_capture_exception
            sentry_sdk.capture_message = mock_capture_message
            letting.__class__.__base__.clean = mock_super_clean  # Simulate exception

            # Trigger the clean() method which should catch the exception
            with self.assertRaises(CustomError):
                letting.clean()

            # Check Sentry was called properly
            exception_logged = any(
                call[0] == 'exception' and isinstance(
                    call[1], CustomError
                ) for call in sentry_calls
            )
            message_logged = any(
                call == ('message', "Erreur de validation dans le modèle Letting")
                for call in sentry_calls
            )

            self.assertTrue(exception_logged)
            self.assertTrue(message_logged)

        finally:
            # Restore original methods
            sentry_sdk.capture_exception = original_capture_exception
            sentry_sdk.capture_message = original_capture_message
            letting.__class__.__base__.clean = original_super_clean


class LettingViewTest(TestCase):
    """
    Test case for the Letting views.
    """

    def setUp(self):
        """
        Sets up test data for Letting and Address models.
        """
        address = Address.objects.create(
            number=1,
            street="Test Street",
            city="Test City",
            state="TS",
            zip_code=12345,
            country_iso_code="TST"
        )
        self.letting = Letting.objects.create(
            title="Test Letting",
            address=address
        )

    def test_letting_index_view(self):
        """
        Tests that the index view returns a 200 response, contains the letting title,
        and uses the correct template.
        """
        response = self.client.get(reverse('lettings:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Letting")
        self.assertTemplateUsed(response, 'lettings/index.html')

    def test_letting_detail_view(self):
        """
        Tests that the detail view for a specific letting returns a 200 response,
        contains the letting title and address, and uses the correct template.
        """
        response = self.client.get(reverse('lettings:letting', args=[self.letting.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Letting")
        self.assertContains(response, "Test Street")
        self.assertTemplateUsed(response, 'lettings/letting.html')

    def test_letting_detail_view_not_found(self):
        """
        Tests that the detail view returns a 404 response for a non-existent letting.
        """
        # Trouver un ID qui n'existe certainement pas
        max_id = (
            Letting.objects.all().order_by('-id').first().id
            if Letting.objects.exists()
            else 0
        )
        non_existent_id = max_id + 1000

        response = self.client.get(reverse('lettings:letting', args=[non_existent_id]))
        self.assertEqual(response.status_code, 404)

    def test_letting_index_view_exception(self):
        """
        Tests that exceptions in the index view are properly handled.
        Verifies that a 500 error page is returned when an exception occurs.
        """
        # Sauvegarder les fonctions originales
        from django.template import Engine
        original_find_template = Engine.find_template
        original_capture_exception = sentry_sdk.capture_exception
        original_capture_message = sentry_sdk.capture_message

        sentry_calls = []

        def mock_capture_exception(exc):
            sentry_calls.append(('exception', exc))
            return None

        def mock_capture_message(message):
            sentry_calls.append(('message', message))
            return None

        def mock_find_template(self, name, dirs=None, skip=None):
            if name == 'lettings/index.html':
                raise TemplateDoesNotExist(name)
            return original_find_template(self, name, dirs, skip)

        try:
            # Appliquer les mocks
            Engine.find_template = mock_find_template
            sentry_sdk.capture_exception = mock_capture_exception
            sentry_sdk.capture_message = mock_capture_message

            # Appeler la vue
            response = self.client.get(reverse('lettings:index'))

            # Vérifier que le statut 500 est retourné
            self.assertEqual(response.status_code, 500)

            # Vérifier que Sentry a bien été appelé
            self.assertTrue(len(sentry_calls) >= 1)
            self.assertEqual(sentry_calls[0][0], 'exception')
            self.assertTrue(isinstance(sentry_calls[0][1], TemplateDoesNotExist))

            # Vérifier le message spécifique
            message_found = False
            for call in sentry_calls:
                if call[0] == 'message' and call[1] == "Erreur dans lettings.views index.":
                    message_found = True
                    break
            self.assertTrue(message_found)

        finally:
            # Restaurer les fonctions originales
            Engine.find_template = original_find_template
            sentry_sdk.capture_exception = original_capture_exception
            sentry_sdk.capture_message = original_capture_message

    def test_letting_detail_view_exception(self):
        """
        Tests that exceptions in the letting detail view are properly handled.
        Verifies that a 500 error page is returned when an exception occurs (other than Http404).
        """
        # Sauvegarder les fonctions originales
        from django.template import Engine
        original_find_template = Engine.find_template
        original_capture_exception = sentry_sdk.capture_exception
        original_capture_message = sentry_sdk.capture_message

        sentry_calls = []

        def mock_capture_exception(exc):
            sentry_calls.append(('exception', exc))
            return None

        def mock_capture_message(message):
            sentry_calls.append(('message', message))
            return None

        def mock_find_template(self, name, dirs=None, skip=None):
            if name == 'lettings/letting.html':
                raise TemplateDoesNotExist(name)
            return original_find_template(self, name, dirs, skip)

        try:
            # Appliquer les mocks
            Engine.find_template = mock_find_template
            sentry_sdk.capture_exception = mock_capture_exception
            sentry_sdk.capture_message = mock_capture_message

            # Appeler la vue
            response = self.client.get(reverse('lettings:letting', args=[self.letting.id]))

            # Vérifier que le statut 500 est retourné
            self.assertEqual(response.status_code, 500)

            # Vérifier que Sentry a bien été appelé
            self.assertTrue(len(sentry_calls) >= 1)
            self.assertEqual(sentry_calls[0][0], 'exception')
            self.assertTrue(isinstance(sentry_calls[0][1], TemplateDoesNotExist))

            # Vérifier le message spécifique
            message_found = False
            for call in sentry_calls:
                if call[0] == 'message' and call[1] == "Erreur dans lettings.views index.":
                    message_found = True
                    break
            self.assertTrue(message_found)

        finally:
            # Restaurer les fonctions originales
            Engine.find_template = original_find_template
            sentry_sdk.capture_exception = original_capture_exception
            sentry_sdk.capture_message = original_capture_message
