from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
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
