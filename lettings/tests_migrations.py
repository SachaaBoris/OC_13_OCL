import os
import importlib.util
from django.test import TestCase


def load_migration_module():
    """
    Dynamically loads the migration module.
    """
    migration_path = os.path.join('lettings', 'migrations', '0002_migrate_data.py')
    spec = importlib.util.spec_from_file_location("migration_module", migration_path)
    migration_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration_module)
    return migration_module


class MockModel:
    """
    Base class for mock models used in tests.
    """
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def save(self):
        """Simulated save method"""
        pass


class MockQuerySet:
    """
    Simulates a Django QuerySet.
    """
    def __init__(self, items=None):
        self.items = items or []

    def all(self):
        return self.items

    def get(self, **kwargs):
        # Simple simulation of .get() - returns the first matching item
        for item in self.items:
            match = True
            for key, value in kwargs.items():
                # Special case for address_id
                if key == 'id' and hasattr(item, 'id') and item.id == value:
                    continue
                elif not hasattr(item, key) or getattr(item, key) != value:
                    match = False
                    break
            if match:
                return item


class MockModelManager:
    """
    Simulates a Django Manager.
    """
    def __init__(self, model_class, items=None):
        self.model_class = model_class
        self.queryset = MockQuerySet(items)

    def all(self):
        return self.queryset.all()

    def get(self, **kwargs):
        return self.queryset.get(**kwargs)


class MockAppRegistry:
    """
    Simulates the Django application registry.
    """
    def __init__(self):
        self.models = {}

    def register_model(self, app_label, model_name, model_class, instances=None):
        """
        Registers a mock model with optional instances.
        """
        key = (app_label, model_name)
        model_class.objects = MockModelManager(model_class, instances)
        self.models[key] = model_class

    def get_model(self, app_label, model_name):
        """
        Retrieves a mock model.
        """
        key = (app_label, model_name)
        return self.models.get(key)


class MockSchemaEditor:
    """
    Simulates the Django schema editor.
    """
    def __init__(self):
        self.deleted_models = []

    def delete_model(self, model):
        """
        Simulates model deletion.
        """
        self.deleted_models.append(model)


class TestDataMigration(TestCase):
    """
    Complete test for data migration between applications.
    """

    def setUp(self):
        """
        Sets up the test environment with mock models and data.
        """
        # Create mock model classes with special methods
        class OldAddress(MockModel):
            def save(self):
                # Ensure the object is available in the queryset
                self.objects.queryset.items.append(self)

        class OldLetting(MockModel):
            def save(self):
                # Ensure the object is available in the queryset
                self.objects.queryset.items.append(self)

        class NewAddress(MockModel):
            def save(self):
                # Ensure the object is available in the queryset
                self.objects.queryset.items.append(self)

        class NewLetting(MockModel):
            def save(self):
                # Ensure the object is available in the queryset
                self.objects.queryset.items.append(self)

        # Create data instances
        self.old_address1 = OldAddress(
            id=1,
            number=1,
            street="123 Main St",
            city="Test City",
            state="TS",
            zip_code=12345,
            country_iso_code="TST"
        )

        self.old_address2 = OldAddress(
            id=2,
            number=2,
            street="456 Oak Ave",
            city="Another City",
            state="AC",
            zip_code=67890,
            country_iso_code="ANT"
        )

        self.old_letting1 = OldLetting(
            id=1,
            title="Nice Apartment",
            address=self.old_address1,
            address_id=1
        )

        self.old_letting2 = OldLetting(
            id=2,
            title="Cozy House",
            address=self.old_address2,
            address_id=2
        )

        # Ensure that address objects also have their IDs accessible
        # for the get() function in forward_func
        for addr in [self.old_address1, self.old_address2]:
            addr.pk = addr.id

        # Create the mock app registry
        self.mock_apps = MockAppRegistry()

        # Register models with their instances
        self.mock_apps.register_model('oc_lettings_site', 'Address', OldAddress,
                                      [self.old_address1, self.old_address2])
        self.mock_apps.register_model('oc_lettings_site', 'Letting', OldLetting,
                                      [self.old_letting1, self.old_letting2])
        self.mock_apps.register_model('lettings', 'Address', NewAddress)
        self.mock_apps.register_model('lettings', 'Letting', NewLetting)

        # Create a mock schema editor
        self.mock_schema_editor = MockSchemaEditor()

        # Load migration functions
        self.migration_module = load_migration_module()
        self.forward_func = self.migration_module.forward_func
        self.reverse_func = self.migration_module.reverse_func

    def test_forward_migration(self):
        """
        Tests the forward migration (from oc_lettings_site to lettings).
        """
        # Call the migration function
        self.forward_func(self.mock_apps, self.mock_schema_editor)

        # Verify that NewAddress models were created with the correct data
        new_addresses = self.mock_apps.get_model('lettings', 'Address').objects.all()
        assert len(new_addresses) == 2, "Le nombre d'adresses migrées ne correspond pas"

        # Verify the attributes of the first address
        new_address1 = next((a for a in new_addresses if a.id == 1), None)
        assert new_address1 is not None, "L'adresse id=1 n'a pas été migrée"
        assert new_address1.number == 1
        assert new_address1.street == "123 Main St"
        assert new_address1.city == "Test City"
        assert new_address1.state == "TS"
        assert new_address1.zip_code == 12345
        assert new_address1.country_iso_code == "TST"

        # Verify that NewLetting models were created with the correct data
        new_lettings = self.mock_apps.get_model('lettings', 'Letting').objects.all()
        assert len(new_lettings) == 2, "Le nombre de locations migrées ne correspond pas"

        # Verify the attributes of the first letting
        new_letting1 = next((l for l in new_lettings if l.id == 1), None)
        assert new_letting1 is not None, "La location id=1 n'a pas été migrée"
        assert new_letting1.title == "Nice Apartment"

        # Verify that the old models were deleted
        deleted_models = self.mock_schema_editor.deleted_models
        assert len(deleted_models) == 2, "Tous les anciens modèles n'ont pas été supprimés"

        # Verify the class names of the deleted models
        deleted_model_names = [model.__name__ for model in deleted_models]
        assert 'OldAddress' in deleted_model_names
        assert 'OldLetting' in deleted_model_names

    def test_reverse_migration(self):
        """
        Tests the reverse migration (from lettings to oc_lettings_site).
        """
        # To test the reverse migration, we must first have data in the new models
        # Let's reset the apps registry
        new_address1 = self.mock_apps.get_model('lettings', 'Address')(
            id=1,
            number=1,
            street="123 Main St",
            city="Test City",
            state="TS",
            zip_code=12345,
            country_iso_code="TST"
        )

        new_address2 = self.mock_apps.get_model('lettings', 'Address')(
            id=2,
            number=2,
            street="456 Oak Ave",
            city="Another City",
            state="AC",
            zip_code=67890,
            country_iso_code="ANT"
        )

        new_letting1 = self.mock_apps.get_model('lettings', 'Letting')(
            id=1,
            title="Nice Apartment",
            address=new_address1,
            address_id=1
        )

        new_letting2 = self.mock_apps.get_model('lettings', 'Letting')(
            id=2,
            title="Cozy House",
            address=new_address2,
            address_id=2
        )

        # Update the instances in the registry
        NewAddress = self.mock_apps.get_model('lettings', 'Address')
        NewLetting = self.mock_apps.get_model('lettings', 'Letting')

        # Reset the collections
        self.mock_apps.register_model('lettings', 'Address', NewAddress, [])
        self.mock_apps.register_model('lettings', 'Letting', NewLetting, [])

        # Add the instances
        for addr in [new_address1, new_address2]:
            addr.pk = addr.id
            NewAddress.objects.queryset.items.append(addr)

        for letting in [new_letting1, new_letting2]:
            letting.pk = letting.id
            NewLetting.objects.queryset.items.append(letting)

        # Reset the old collections
        self.mock_apps.register_model(
            'oc_lettings_site',
            'Address',
            self.mock_apps.get_model('oc_lettings_site', 'Address'),
            []
        )
        self.mock_apps.register_model(
            'oc_lettings_site',
            'Letting',
            self.mock_apps.get_model('oc_lettings_site', 'Letting'),
            []
        )

        # Reset the schema editor
        self.mock_schema_editor = MockSchemaEditor()

        # Call the reverse migration function
        self.reverse_func(self.mock_apps, self.mock_schema_editor)

        # Verify that OldAddress models were created with the correct data
        old_addresses = self.mock_apps.get_model('oc_lettings_site', 'Address').objects.all()
        assert len(old_addresses) == 2, (
            "Le nombre d'adresses migrées vers l'ancien modèle ne correspond pas"
        )

        # Verify the attributes of the first address
        old_address1 = next((a for a in old_addresses if a.id == 1), None)
        assert old_address1 is not None, "L'adresse id=1 n'a pas été migrée vers l'ancien modèle"
        assert old_address1.number == 1
        assert old_address1.street == "123 Main St"

        # Verify that OldLetting models were created with the correct data
        old_lettings = self.mock_apps.get_model('oc_lettings_site', 'Letting').objects.all()
        assert len(old_lettings) == 2, (
            "Le nombre de locations migrées vers l'ancien modèle ne correspond pas"
        )

        # Verify the attributes of the first letting
        old_letting1 = next((l for l in old_lettings if l.id == 1), None)
        assert old_letting1 is not None, "La location id=1 n'a pas été migrée vers l'ancien modèle"
        assert old_letting1.title == "Nice Apartment"

        # Verify that the new models were deleted
        deleted_models = self.mock_schema_editor.deleted_models
        assert len(deleted_models) == 2, "Tous les nouveaux modèles n'ont pas été supprimés"

        # Verify the class names of the deleted models
        deleted_model_names = [model.__name__ for model in deleted_models]
        assert 'NewAddress' in deleted_model_names
        assert 'NewLetting' in deleted_model_names
