from django.test import TestCase
from django.urls import reverse
from .models import Address, Letting


class LettingTest(TestCase):
    def setUp(self):
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
        response = self.client.get(reverse('lettings:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Letting")
        self.assertTemplateUsed(response, 'lettings/index.html')

    def test_letting_detail_view(self):
        response = self.client.get(reverse('lettings:letting', args=[self.letting.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Letting")
        self.assertContains(response, "Test Street")
        self.assertTemplateUsed(response, 'lettings/letting.html')
