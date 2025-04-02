from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Profile


class ProfileTest(TestCase):
    def setUp(self):
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

    def test_profile_index_view(self):
        response = self.client.get(reverse('profiles:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testuser")
        self.assertTemplateUsed(response, 'profiles/index.html')

    def test_profile_detail_view(self):
        response = self.client.get(reverse('profiles:profile', args=["testuser"]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testuser")
        self.assertContains(response, "Test City")
        self.assertTemplateUsed(response, 'profiles/profile.html')
