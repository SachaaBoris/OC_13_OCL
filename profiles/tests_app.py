import sentry_sdk
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.template.exceptions import TemplateDoesNotExist
from .models import Profile


class ProfileTest(TestCase):
    """
    Test case for the Profile model and related views.
    Verifies that the profile views load correctly, display the correct data,
    and use the appropriate templates.
    """

    def setUp(self):
        """
        Sets up the test user and associated profile data.
        Creates a test user and their profile with a favorite city.
        """
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpassword",
            first_name="Test",
            last_name="User"
        )
        self.profile = Profile.objects.create(
            user=self.user,
            favorite_city="Test City"
        )

    def test_profile_model_str(self):
        """
        Tests the string representation of the Profile model.
        Verifies that the __str__ method returns the username of the associated user.
        """
        self.assertEqual(str(self.profile), self.user.username)
        self.assertEqual(str(self.profile), "testuser")

    def test_profile_index_view(self):
        """
        Tests the profile index view response status, content, and template used.
        Ensures that the index view loads correctly, contains the test user's username,
        and uses the 'profiles/index.html' template.
        """
        response = self.client.get(reverse('profiles:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testuser")
        self.assertTemplateUsed(response, 'profiles/index.html')

    def test_profile_detail_view(self):
        """
        Tests the profile detail view response status, content, and template used.
        Ensures that the profile detail page loads correctly, contains the test user's
        username and favorite city, and uses the 'profiles/profile.html' template.
        """
        response = self.client.get(reverse('profiles:profile', args=["testuser"]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testuser")
        self.assertContains(response, "Test City")
        self.assertTemplateUsed(response, 'profiles/profile.html')

    def test_profile_detail_view_404(self):
        """
        Tests the profile detail view with a non-existing user, ensuring a 404 is returned.
        """
        response = self.client.get(reverse('profiles:profile', args=["nonexistentuser"]))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_profile_index_view_exception(self):
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

        # Define mocks
        def mock_capture_exception(exc):
            sentry_calls.append(('exception', exc))
            return None

        def mock_capture_message(message):
            sentry_calls.append(('message', message))
            return None

        def mock_find_template(self, name, dirs=None, skip=None):
            if name == 'profiles/index.html':
                raise TemplateDoesNotExist(name)
            return original_find_template(self, name, dirs, skip)

        try:
            # Apply mocks
            Engine.find_template = mock_find_template
            sentry_sdk.capture_exception = mock_capture_exception
            sentry_sdk.capture_message = mock_capture_message

            # Call the view
            response = self.client.get(reverse('profiles:index'))

            # Check status 500 is returned
            self.assertEqual(response.status_code, 500)

            # Check Sentry was called
            self.assertTrue(len(sentry_calls) >= 1)
            self.assertEqual(sentry_calls[0][0], 'exception')
            self.assertTrue(isinstance(sentry_calls[0][1], TemplateDoesNotExist))

            # Check for specific message
            message_found = False
            for call in sentry_calls:
                if call[0] == 'message' and call[1] == "Erreur dans profiles.views index.":
                    message_found = True
                    break
            self.assertTrue(message_found)

        finally:
            # Restore original functions
            Engine.find_template = original_find_template
            sentry_sdk.capture_exception = original_capture_exception
            sentry_sdk.capture_message = original_capture_message

    def test_profile_detail_view_exception(self):
        """
        Tests that exceptions in the profile detail view are properly handled.
        Verifies that a 500 error page is returned when an exception occurs (other than Http404).
        """
        # Save original functions
        from django.template import Engine
        original_find_template = Engine.find_template
        original_capture_exception = sentry_sdk.capture_exception
        original_capture_message = sentry_sdk.capture_message

        sentry_calls = []

        # Define mocks
        def mock_capture_exception(exc):
            sentry_calls.append(('exception', exc))
            return None

        def mock_capture_message(message):
            sentry_calls.append(('message', message))
            return None

        def mock_find_template(self, name, dirs=None, skip=None):
            if name == 'profiles/profile.html':
                raise TemplateDoesNotExist(name)
            return original_find_template(self, name, dirs, skip)

        try:
            # Apply mocks
            Engine.find_template = mock_find_template
            sentry_sdk.capture_exception = mock_capture_exception
            sentry_sdk.capture_message = mock_capture_message

            # Call the view
            response = self.client.get(reverse('profiles:profile', args=["testuser"]))

            # Check status 500 is returned
            self.assertEqual(response.status_code, 500)

            # Check Sentry was called
            self.assertTrue(len(sentry_calls) >= 1)
            self.assertEqual(sentry_calls[0][0], 'exception')
            self.assertTrue(isinstance(sentry_calls[0][1], TemplateDoesNotExist))

            # Check for specific message
            message_found = False
            for call in sentry_calls:
                if call[0] == 'message' and call[1] == "Erreur dans profiles.views profile.":
                    message_found = True
                    break
            self.assertTrue(message_found)

        finally:
            # Restore original functions
            Engine.find_template = original_find_template
            sentry_sdk.capture_exception = original_capture_exception
            sentry_sdk.capture_message = original_capture_message

    def test_profile_clean_exception(self):
        """
        Tests that the Profile.clean() method correctly captures exceptions using Sentry.
        Simulates an exception raised from within clean() and ensures Sentry captures it.
        """
        # Backup original sentry functions
        original_capture_exception = sentry_sdk.capture_exception
        original_capture_message = sentry_sdk.capture_message

        sentry_calls = []

        def mock_capture_exception(exc):
            sentry_calls.append(('exception', exc))

        def mock_capture_message(msg):
            sentry_calls.append(('message', msg))

        class CustomError(Exception):
            """Custom exception to trigger in clean()."""
            pass

        # Backup original clean method from the superclass of Profile (i.e., models.Model)
        original_super_clean = self.profile.__class__.__base__.clean

        def mock_super_clean(self):
            raise CustomError("Mock validation failure")

        try:
            # Apply mocks
            sentry_sdk.capture_exception = mock_capture_exception
            sentry_sdk.capture_message = mock_capture_message
            self.profile.__class__.__base__.clean = mock_super_clean  # simulate exception

            with self.assertRaises(CustomError):
                self.profile.clean()

            # Check Sentry was called properly
            exception_logged = any(
                call[0] == 'exception' and isinstance(call[1], CustomError)
                for call in sentry_calls
            )
            message_logged = any(
                call == ('message', "Erreur de validation dans le modèle Profile")
                for call in sentry_calls
            )

            self.assertTrue(exception_logged)
            self.assertTrue(message_logged)

        finally:
            # Restore original methods
            sentry_sdk.capture_exception = original_capture_exception
            sentry_sdk.capture_message = original_capture_message
            self.profile.__class__.__base__.clean = original_super_clean
