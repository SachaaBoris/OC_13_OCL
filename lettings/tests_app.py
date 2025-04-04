from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError
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
        max_id = Letting.objects.all().order_by('-id').first().id if Letting.objects.exists() else 0
        non_existent_id = max_id + 1000
            
        response = self.client.get(reverse('lettings:letting', args=[non_existent_id]))
        self.assertEqual(response.status_code, 404)
