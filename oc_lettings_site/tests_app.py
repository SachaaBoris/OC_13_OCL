from django.test import TestCase
from django.urls import reverse


class IndexTest(TestCase):
    """
    Test case for the index view of the application.
    Verifies that the index view loads correctly and uses the appropriate template.
    """
    def test_index_view(self):
        """
        Tests the index view response status, content, and template used.
        Ensures that the page loads with the correct status, contains the expected content, 
        and uses the 'index.html' template.
        """
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to Holiday Homes")
        self.assertTemplateUsed(response, 'oc_lettings_site/index.html')
