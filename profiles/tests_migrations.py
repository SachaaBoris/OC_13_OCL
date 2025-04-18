import os
import importlib.util
from django.test import TestCase


def load_migration_module():
    """
    Dynamically loads the migration module.
    """
    migration_path = os.path.join('profiles', 'migrations', '0002_migrate_data.py')
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
        """Simulated save method that adds the object to the queryset"""
        self.__class__.objects.queryset.items.append(self)


class MockQuerySet:
    """
    Simulates a Django QuerySet.
    """
    def __init__(self, items=None):
        self.items = items or []

    def all(self):
        return self.items

    def get(self, **kwargs):
        # Improved .get() simulation
        pass


class MockModelManager:
    """
    Simulates a Django Manager.
    """
    def __init__(self, model_class, items=None):
        self.model_class = model_class
        self.queryset = MockQuerySet(items or [])

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
        model_class.objects = MockModelManager(model_class, instances or [])
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


class MockUser:
    """
    Simulates a Django User model for tests.
    """
    def __init__(self, id, username):
        self.id = id
        self.pk = id
        self.username = username


class TestProfilesMigration(TestCase):
    """
    Test for profile data migration between applications.
    """

    def setUp(self):
        """
        Sets up the test environment with mock models and data.
        """
        # Create mock model classes
        class OldProfile(MockModel):
            def save(self):
                # Override to ensure addition to the queryset
                OldProfile.objects.queryset.items.append(self)

        class NewProfile(MockModel):
            def save(self):
                # Override to ensure addition to the queryset
                NewProfile.objects.queryset.items.append(self)

        # Create mock users
        self.user1 = MockUser(id=1, username="user1")
        self.user2 = MockUser(id=2, username="user2")

        # Create mock profiles
        self.old_profile1 = OldProfile(
            id=1,
            pk=1,
            user=self.user1,
            user_id=1,
            favorite_city="Paris"
        )

        self.old_profile2 = OldProfile(
            id=2,
            pk=2,
            user=self.user2,
            user_id=2,
            favorite_city="London"
        )

        # Create the mock app registry
        self.mock_apps = MockAppRegistry()

        # Register models with their instances
        self.mock_apps.register_model(
            'oc_lettings_site', 'Profile', OldProfile,
            [self.old_profile1, self.old_profile2]
        )
        self.mock_apps.register_model(
            'profiles', 'Profile', NewProfile, []
        )

        # Create a mock schema editor
        self.mock_schema_editor = MockSchemaEditor()

        # Load migration functions
        self.migration_module = load_migration_module()
        self.forward_func = self.migration_module.forward_func
        self.reverse_func = self.migration_module.reverse_func

    def test_forward_migration(self):
        """
        Tests the forward migration (from oc_lettings_site to profiles).
        """
        # Call the migration function
        self.forward_func(self.mock_apps, self.mock_schema_editor)

        # Verify that profiles were created with the correct data
        new_profiles = self.mock_apps.get_model('profiles', 'Profile').objects.all()
        assert len(new_profiles) == 2, "Le nombre de profils migrés ne correspond pas"

        # Verify the attributes of the first profile
        new_profile1 = next((p for p in new_profiles if p.id == 1), None)
        assert new_profile1 is not None, "Le profil id=1 n'a pas été migré"
        assert new_profile1.favorite_city == "Paris"
        assert new_profile1.user_id == 1

        # Verify that the old model was deleted
        deleted_models = self.mock_schema_editor.deleted_models
        assert len(deleted_models) == 1, "L'ancien modèle de profil n'a pas été supprimé"

        # Verify the class name of the deleted model
        deleted_model_names = [model.__name__ for model in deleted_models]
        assert 'OldProfile' in deleted_model_names

    def test_reverse_migration(self):
        """
        Tests the reverse migration (from profiles to oc_lettings_site).
        """
        # Setup data for reverse migration
        # First, we need to have data in the new model
        NewProfile = self.mock_apps.get_model('profiles', 'Profile')
        OldProfile = self.mock_apps.get_model('oc_lettings_site', 'Profile')

        # Reset the collections
        self.mock_apps.register_model('profiles', 'Profile', NewProfile, [])
        self.mock_apps.register_model('oc_lettings_site', 'Profile', OldProfile, [])

        # Create new profiles to migrate to the old model
        new_profile1 = NewProfile(
            id=1,
            pk=1,
            user_id=1,
            favorite_city="Paris"
        )

        new_profile2 = NewProfile(
            id=2,
            pk=2,
            user_id=2,
            favorite_city="London"
        )

        # Ensure the profiles are in the queryset
        NewProfile.objects.queryset.items = [new_profile1, new_profile2]

        # Reset the schema editor
        self.mock_schema_editor = MockSchemaEditor()

        # Call the reverse migration function
        self.reverse_func(self.mock_apps, self.mock_schema_editor)

        # Verify that profiles were migrated to the old model
        old_profiles = OldProfile.objects.all()
        assert len(old_profiles) == 2, (
            "Le nombre de profils migrés vers l'ancien modèle ne correspond pas"
        )

        # Verify the attributes of the first profile
        old_profile1 = next((p for p in old_profiles if p.id == 1), None)
        assert old_profile1 is not None, "Le profil id=1 n'a pas été migré vers l'ancien modèle"
        assert old_profile1.favorite_city == "Paris"
        assert old_profile1.user_id == 1

        # Verify that the new model was deleted
        deleted_models = self.mock_schema_editor.deleted_models
        assert len(deleted_models) == 1, "Le nouveau modèle de profil n'a pas été supprimé"

        # Verify the class name of the deleted model
        deleted_model_names = [model.__name__ for model in deleted_models]
        assert 'NewProfile' in deleted_model_names
