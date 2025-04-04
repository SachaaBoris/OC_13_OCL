import pytest
import os
import importlib.util
from django.test import TestCase
from django.apps import apps
from django.db import models, connection


def load_migration_module():
    """
    Charge dynamiquement le module de migration.
    """
    migration_path = os.path.join('profiles', 'migrations', '0002_migrate_data.py')
    spec = importlib.util.spec_from_file_location("migration_module", migration_path)
    migration_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration_module)
    return migration_module


class MockModel:
    """
    Classe de base pour les modèles fictifs utilisés dans les tests.
    """
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def save(self):
        """Méthode save simulée qui ajoute l'objet au queryset"""
        self.__class__.objects.queryset.items.append(self)


class MockQuerySet:
    """
    Simule un QuerySet Django.
    """
    def __init__(self, items=None):
        self.items = items or []
    
    def all(self):
        return self.items
    
    def get(self, **kwargs):
        # Simulation de .get() améliorée
        pass


class MockModelManager:
    """
    Simule un Manager Django.
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
    Simule le registre d'applications Django.
    """
    def __init__(self):
        self.models = {}
    
    def register_model(self, app_label, model_name, model_class, instances=None):
        """
        Enregistre un modèle fictif avec des instances optionnelles.
        """
        key = (app_label, model_name)
        model_class.objects = MockModelManager(model_class, instances or [])
        self.models[key] = model_class
    
    def get_model(self, app_label, model_name):
        """
        Récupère un modèle fictif.
        """
        key = (app_label, model_name)
        return self.models.get(key)


class MockSchemaEditor:
    """
    Simule le schema editor Django.
    """
    def __init__(self):
        self.deleted_models = []
    
    def delete_model(self, model):
        """
        Simule la suppression d'un modèle.
        """
        self.deleted_models.append(model)


class MockUser:
    """
    Simule un modèle User Django pour les tests.
    """
    def __init__(self, id, username):
        self.id = id
        self.pk = id
        self.username = username


class TestProfilesMigration(TestCase):
    """
    Test pour la migration de données des profils entre les applications.
    """
    
    def setUp(self):
        """
        Configure l'environnement de test avec des modèles et des données fictifs.
        """
        # Créer des classes de modèles fictifs
        class OldProfile(MockModel):
            def save(self):
                # Surcharge pour assurer l'ajout au queryset
                OldProfile.objects.queryset.items.append(self)
        
        class NewProfile(MockModel):
            def save(self):
                # Surcharge pour assurer l'ajout au queryset
                NewProfile.objects.queryset.items.append(self)
                
        # Créer des utilisateurs fictifs
        self.user1 = MockUser(id=1, username="user1")
        self.user2 = MockUser(id=2, username="user2")
        
        # Créer des profils fictifs
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
        
        # Créer le registre d'apps fictif
        self.mock_apps = MockAppRegistry()
        
        # Enregistrer les modèles avec leurs instances
        self.mock_apps.register_model('oc_lettings_site', 'Profile', OldProfile, 
                                      [self.old_profile1, self.old_profile2])
        self.mock_apps.register_model('profiles', 'Profile', NewProfile, [])
        
        # Créer un schema editor fictif
        self.mock_schema_editor = MockSchemaEditor()
        
        # Charger les fonctions de migration
        self.migration_module = load_migration_module()
        self.forward_func = self.migration_module.forward_func
        self.reverse_func = self.migration_module.reverse_func
    
    def test_forward_migration(self):
        """
        Test la migration en avant (de oc_lettings_site vers profiles).
        """
        # Appeler la fonction de migration
        self.forward_func(self.mock_apps, self.mock_schema_editor)
        
        # Vérifier que les profils ont été créés avec les bonnes données
        new_profiles = self.mock_apps.get_model('profiles', 'Profile').objects.all()
        assert len(new_profiles) == 2, "Le nombre de profils migrés ne correspond pas"
        
        # Vérifier les attributs du premier profil
        new_profile1 = next((p for p in new_profiles if p.id == 1), None)
        assert new_profile1 is not None, "Le profil id=1 n'a pas été migré"
        assert new_profile1.favorite_city == "Paris"
        assert new_profile1.user_id == 1
        
        # Vérifier que l'ancien modèle a été supprimé
        deleted_models = self.mock_schema_editor.deleted_models
        assert len(deleted_models) == 1, "L'ancien modèle de profil n'a pas été supprimé"
        
        # Vérifier le nom de la classe du modèle supprimé
        deleted_model_names = [model.__name__ for model in deleted_models]
        assert 'OldProfile' in deleted_model_names
    
    def test_reverse_migration(self):
        """
        Test la migration inverse (de profiles vers oc_lettings_site).
        """
        # Configuration des données pour la migration inverse
        # D'abord, nous devons avoir des données dans le nouveau modèle
        NewProfile = self.mock_apps.get_model('profiles', 'Profile')
        OldProfile = self.mock_apps.get_model('oc_lettings_site', 'Profile')
        
        # Réinitialiser les collections
        self.mock_apps.register_model('profiles', 'Profile', NewProfile, [])
        self.mock_apps.register_model('oc_lettings_site', 'Profile', OldProfile, [])
        
        # Créer de nouveaux profils à migrer vers l'ancien modèle
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
        
        # S'assurer que les profils sont dans le queryset
        NewProfile.objects.queryset.items = [new_profile1, new_profile2]
        
        # Réinitialiser le schema editor
        self.mock_schema_editor = MockSchemaEditor()
        
        # Appeler la fonction de migration inverse
        self.reverse_func(self.mock_apps, self.mock_schema_editor)
        
        # Vérifier que les profils ont été migrés vers l'ancien modèle
        old_profiles = OldProfile.objects.all()
        assert len(old_profiles) == 2, "Le nombre de profils migrés vers l'ancien modèle ne correspond pas"
        
        # Vérifier les attributs du premier profil
        old_profile1 = next((p for p in old_profiles if p.id == 1), None)
        assert old_profile1 is not None, "Le profil id=1 n'a pas été migré vers l'ancien modèle"
        assert old_profile1.favorite_city == "Paris"
        assert old_profile1.user_id == 1
        
        # Vérifier que le nouveau modèle a été supprimé
        deleted_models = self.mock_schema_editor.deleted_models
        assert len(deleted_models) == 1, "Le nouveau modèle de profil n'a pas été supprimé"
        
        # Vérifier le nom de la classe du modèle supprimé
        deleted_model_names = [model.__name__ for model in deleted_models]
        assert 'NewProfile' in deleted_model_names
