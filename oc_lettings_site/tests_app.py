import re
import copy
import sentry_sdk
from django.test import TestCase
from django.urls import reverse
from django.template.exceptions import TemplateDoesNotExist
from django.contrib.auth.signals import user_login_failed
from django.contrib.auth.models import User


from oc_lettings_site.sentry_config import add_timestamp


class IndexTest(TestCase):
    """
    Test case for the index view of the application.
    Verifies that the index view loads correctly and uses
    the appropriate template.
    """
    def test_index_view(self):
        """
        Tests the index view response status, content, and template used.
        Ensures that the page loads with the correct status, contains
        the expected content, and uses the 'index.html' template.
        """
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to Holiday Homes")
        self.assertTemplateUsed(response, 'oc_lettings_site/index.html')

    def test_index_view_exception(self):
        """
        Tests that exceptions in the index view are properly handled.
        Verifies that a 500 error page is returned when an exception occurs.
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
            if name == 'oc_lettings_site/index.html':
                raise TemplateDoesNotExist(name)
            return original_find_template(self, name, dirs, skip)

        try:
            # Apply mocks
            Engine.find_template = mock_find_template
            sentry_sdk.capture_exception = mock_capture_exception
            sentry_sdk.capture_message = mock_capture_message

            # Call the view
            response = self.client.get(reverse('index'))

            # Check status 500 is returned
            self.assertEqual(response.status_code, 500)

            # Check Sentry call
            self.assertTrue(len(sentry_calls) >= 1)
            self.assertEqual(sentry_calls[0][0], 'exception')
            self.assertTrue(isinstance(sentry_calls[0][1], TemplateDoesNotExist))

            # Check for specific message
            message_found = False
            for call in sentry_calls:
                if call[0] == 'message' and call[1] == "Erreur dans oc_lettings_site.views index.":
                    message_found = True
                    break
            self.assertTrue(message_found)

        finally:
            # Restore the original functions
            Engine.find_template = original_find_template
            sentry_sdk.capture_exception = original_capture_exception
            sentry_sdk.capture_message = original_capture_message


class SentryTest(TestCase):
    """
    Test suite for Sentry timestamp functionality.
    Tests the add_timestamp function that adds timestamp information to Sentry events.
    """

    def setUp(self):
        """Prepare test data"""
        self.mock_event = {
            'event_id': '123456abcdef',
            'level': 'error',
            'message': 'Test error message',
        }
        self.mock_hint = {'exception': Exception('Test exception')}

    def test_add_timestamp_adds_tags(self):
        """Test that add_timestamp adds the timestamp to tags"""
        # Make a deep copy to avoid modifying the original
        event = copy.deepcopy(self.mock_event)

        # Execute the function being tested
        result = add_timestamp(event, self.mock_hint)

        # Verify that the timestamp tag was added
        self.assertIn('tags', result)
        self.assertIn('timestamp', result['tags'])

        # Verify that the format is correct (YYYY-MM-DD HH:MM:SS)
        timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        self.assertTrue(re.match(timestamp_pattern, result['tags']['timestamp']))

    def test_add_timestamp_adds_extra(self):
        """Test that add_timestamp adds the timestamp to extra data"""
        # Make a deep copy to avoid modifying the original
        event = copy.deepcopy(self.mock_event)

        # Execute the function being tested
        result = add_timestamp(event, self.mock_hint)

        # Verify that extra timestamp was added
        self.assertIn('extra', result)
        self.assertIn('timestamp', result['extra'])

        # Verify that the values in tags and extra are identical
        self.assertEqual(result['extra']['timestamp'], result['tags']['timestamp'])

    def test_add_timestamp_modifies_message(self):
        """Test that add_timestamp modifies the message with the timestamp"""
        original_message = "Test error message"

        # Make a deep copy to avoid modifying the original
        event = copy.deepcopy(self.mock_event)

        # Execute the function being tested
        result = add_timestamp(event, self.mock_hint)

        # Verify that the message was modified
        self.assertTrue(result['message'].startswith(original_message))
        self.assertIn("[Horodatage: ", result['message'])
        self.assertIn(result['tags']['timestamp'], result['message'])

    def test_add_timestamp_with_existing_tags_and_extra(self):
        """Test that add_timestamp preserves existing tags and extra data"""
        # Create an event with existing tags and extra
        event = copy.deepcopy(self.mock_event)
        event['tags'] = {'existing_tag': 'tag_value'}
        event['extra'] = {'existing_extra': 'extra_value'}

        # Execute the function being tested
        result = add_timestamp(event, self.mock_hint)

        # Verify that existing tags and extra are preserved
        self.assertEqual(result['tags']['existing_tag'], 'tag_value')
        self.assertEqual(result['extra']['existing_extra'], 'extra_value')

        # Verify that new timestamp entries are added
        self.assertIn('timestamp', result['tags'])
        self.assertIn('timestamp', result['extra'])

    def test_add_timestamp_without_message(self):
        """Test that add_timestamp works correctly without a message"""
        # Create an event without a message
        event = {
            'event_id': '123456abcdef',
            'level': 'error',
        }

        # Execute the function being tested
        result = add_timestamp(event, self.mock_hint)

        # Verify that tags and extra are added
        self.assertIn('timestamp', result['tags'])
        self.assertIn('timestamp', result['extra'])

        # Verify that no message was added
        self.assertNotIn('message', result)

    def test_timestamp_consistency(self):
        """Test that the same timestamp is used throughout the event"""
        event = copy.deepcopy(self.mock_event)

        # Execute the function being tested
        result = add_timestamp(event, self.mock_hint)

        # Extract the timestamp from different places
        tag_timestamp = result['tags']['timestamp']
        extra_timestamp = result['extra']['timestamp']
        message_timestamp = result['message'].split("[Horodatage: ")[1].rstrip("]")

        # Verify it's the same everywhere
        self.assertEqual(tag_timestamp, extra_timestamp)
        self.assertEqual(tag_timestamp, message_timestamp)


class SignalsTest(TestCase):
    """
    TestCase to verify that failed login attempts trigger the correct
    messages to Sentry via the user_login_failed signal.
    """
    def setUp(self):
        """
        Replace sentry_sdk.capture_message with a mock version
        to intercept messages during tests.
        """

        # Save the original capture_message function
        self.original_capture_message = sentry_sdk.capture_message

        # Prepare a list to collect messages sent to Sentry
        self.messages = []

        # Define a fake version of capture_message
        def fake_capture_message(msg):
            self.messages.append(msg)

        # Replace the original with the fake one
        sentry_sdk.capture_message = fake_capture_message

    def tearDown(self):
        """
        Restore the original sentry_sdk.capture_message function
        after each test.
        """
        sentry_sdk.capture_message = self.original_capture_message

    def test_failed_login_existing_user(self):
        """
        Test that a failed login attempt with an existing user
        triggers a message about incorrect password.
        """
        # Create a user that exists in the database
        User.objects.create_user(username="testuser", password="secret")

        # Simulate a failed login attempt with the correct username
        user_login_failed.send(
            sender=User,
            credentials={"username": "testuser"},
            request=None
        )

        # Assert that the expected message was captured
        assert self.messages == ["Échec de connexion pour l'utilisateur existant: testuser"]

    def test_failed_login_unknown_user(self):
        """
        Test that a failed login attempt with a non-existent username
        triggers a message about unknown user.
        """
        user_login_failed.send(
            sender=User,
            credentials={"username": "unknownuser"},
            request=None
        )

        assert self.messages == ["Échec de connexion pour l'utilisateur inexistant: unknownuser"]

    def test_failed_login_no_username(self):
        """
        Test that a failed login attempt without providing a username
        triggers a message about missing username.
        """
        user_login_failed.send(
            sender=User,
            credentials={},  # No 'username' key provided
            request=None
        )

        assert self.messages == ["Échec de connexion sans nom d'utilisateur fourni."]
