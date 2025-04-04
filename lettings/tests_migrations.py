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
    migration_path = os.path.join('lettings', 'migrations', '0002_migrate_data.py')
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
        """Méthode save simulée"""
        pass


class MockQuerySet:
    """
    Simule un QuerySet Django.
    """
    def __init__(self, items=None):
        self.items = items or []
    
    def all(self):
        return self.items
    
    def get(self, **kwargs):
        # Simulation simple de .get() - retourne le premier élément correspondant
        for item in self.items:
            match = True
            for key, value in kwargs.items():
                # Cas spécial pour address_id qui peut être stocké comme 'address_id' ou comme 'address.id'
                if key == 'id' and hasattr(item, 'id') and item.id == value:
                    continue
                elif not hasattr(item, key) or getattr(item, key) != value:
                    match = False
                    break
            if match:
                return item


class MockModelManager:
    """
    Simule un Manager Django.
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
    Simule le registre d'applications Django.
    """
    def __init__(self):
        self.models = {}
    
    def register_model(self, app_label, model_name, model_class, instances=None):
        """
        Enregistre un modèle fictif avec des instances optionnelles.
        """
        key = (app_label, model_name)
        model_class.objects = MockModelManager(model_class, instances)
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


class TestDataMigration(TestCase):
    """
    Test complet pour la migration de données entre les applications.
    """
    
    def setUp(self):
        """
        Configure l'environnement de test avec des modèles et des données fictifs.
        """
        # Créer des classes de modèles fictifs avec des méthodes spéciales
        class OldAddress(MockModel):
            def save(self):
                # Assurer que l'objet est disponible dans le queryset
                self.objects.queryset.items.append(self)
        
        class OldLetting(MockModel):
            def save(self):
                # Assurer que l'objet est disponible dans le queryset
                self.objects.queryset.items.append(self)
        
        class NewAddress(MockModel):
            def save(self):
                # Assurer que l'objet est disponible dans le queryset
                self.objects.queryset.items.append(self)
        
        class NewLetting(MockModel):
            def save(self):
                # Assurer que l'objet est disponible dans le queryset
                self.objects.queryset.items.append(self)
        
        # Créer des instances de données
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
        
        # S'assurer que les objets address ont également leurs ID accessibles
        # pour la fonction get() dans forward_func
        for addr in [self.old_address1, self.old_address2]:
            addr.pk = addr.id
        
        # Créer le registre d'apps fictif
        self.mock_apps = MockAppRegistry()
        
        # Enregistrer les modèles avec leurs instances
        self.mock_apps.register_model('oc_lettings_site', 'Address', OldAddress, 
                                      [self.old_address1, self.old_address2])
        self.mock_apps.register_model('oc_lettings_site', 'Letting', OldLetting, 
                                      [self.old_letting1, self.old_letting2])
        self.mock_apps.register_model('lettings', 'Address', NewAddress)
        self.mock_apps.register_model('lettings', 'Letting', NewLetting)
        
        # Créer un schema editor fictif
        self.mock_schema_editor = MockSchemaEditor()
        
        # Charger les fonctions de migration
        self.migration_module = load_migration_module()
        self.forward_func = self.migration_module.forward_func
        self.reverse_func = self.migration_module.reverse_func
    
    def test_forward_migration(self):
        """
        Test la migration en avant (de oc_lettings_site vers lettings).
        """
        # Appeler la fonction de migration
        self.forward_func(self.mock_apps, self.mock_schema_editor)
        
        # Vérifier que les modèles NewAddress ont été créés avec les bonnes données
        new_addresses = self.mock_apps.get_model('lettings', 'Address').objects.all()
        assert len(new_addresses) == 2, "Le nombre d'adresses migrées ne correspond pas"
        
        # Vérifier les attributs de la première adresse
        new_address1 = next((a for a in new_addresses if a.id == 1), None)
        assert new_address1 is not None, "L'adresse id=1 n'a pas été migrée"
        assert new_address1.number == 1
        assert new_address1.street == "123 Main St"
        assert new_address1.city == "Test City"
        assert new_address1.state == "TS"
        assert new_address1.zip_code == 12345
        assert new_address1.country_iso_code == "TST"
        
        # Vérifier que les modèles NewLetting ont été créés avec les bonnes données
        new_lettings = self.mock_apps.get_model('lettings', 'Letting').objects.all()
        assert len(new_lettings) == 2, "Le nombre de locations migrées ne correspond pas"
        
        # Vérifier les attributs de la première location
        new_letting1 = next((l for l in new_lettings if l.id == 1), None)
        assert new_letting1 is not None, "La location id=1 n'a pas été migrée"
        assert new_letting1.title == "Nice Apartment"
        
        # Vérifier que les anciens modèles ont été supprimés
        deleted_models = self.mock_schema_editor.deleted_models
        assert len(deleted_models) == 2, "Tous les anciens modèles n'ont pas été supprimés"
        
        # Vérifier les noms des classes des modèles supprimés
        deleted_model_names = [model.__name__ for model in deleted_models]
        assert 'OldAddress' in deleted_model_names
        assert 'OldLetting' in deleted_model_names
    
    def test_reverse_migration(self):
        """
        Test la migration inverse (de lettings vers oc_lettings_site).
        """
        # Pour tester la migration inverse, nous devons d'abord avoir des données dans les nouveaux modèles
        # Réinitialisons le registre d'apps
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
        
        # Mettre à jour les instances dans le registre
        NewAddress = self.mock_apps.get_model('lettings', 'Address')
        NewLetting = self.mock_apps.get_model('lettings', 'Letting')
        
        # Réinitialiser les collections
        self.mock_apps.register_model('lettings', 'Address', NewAddress, [])
        self.mock_apps.register_model('lettings', 'Letting', NewLetting, [])
        
        # Ajouter les instances - en s'assurant qu'elles sont correctement enregistrées
        for addr in [new_address1, new_address2]:
            addr.pk = addr.id
            NewAddress.objects.queryset.items.append(addr)
            
        for letting in [new_letting1, new_letting2]:
            letting.pk = letting.id
            NewLetting.objects.queryset.items.append(letting)
        
        # Réinitialiser les anciennes collections (comme si elles étaient vides avant la migration inverse)
        self.mock_apps.register_model('oc_lettings_site', 'Address', 
                                     self.mock_apps.get_model('oc_lettings_site', 'Address'), 
                                     [])
        self.mock_apps.register_model('oc_lettings_site', 'Letting', 
                                     self.mock_apps.get_model('oc_lettings_site', 'Letting'), 
                                     [])
        
        # Réinitialiser le schema editor
        self.mock_schema_editor = MockSchemaEditor()
        
        # Appeler la fonction de migration inverse
        self.reverse_func(self.mock_apps, self.mock_schema_editor)
        
        # Vérifier que les modèles OldAddress ont été créés avec les bonnes données
        old_addresses = self.mock_apps.get_model('oc_lettings_site', 'Address').objects.all()
        assert len(old_addresses) == 2, "Le nombre d'adresses migrées vers l'ancien modèle ne correspond pas"
        
        # Vérifier les attributs de la première adresse
        old_address1 = next((a for a in old_addresses if a.id == 1), None)
        assert old_address1 is not None, "L'adresse id=1 n'a pas été migrée vers l'ancien modèle"
        assert old_address1.number == 1
        assert old_address1.street == "123 Main St"
        
        # Vérifier que les modèles OldLetting ont été créés avec les bonnes données
        old_lettings = self.mock_apps.get_model('oc_lettings_site', 'Letting').objects.all()
        assert len(old_lettings) == 2, "Le nombre de locations migrées vers l'ancien modèle ne correspond pas"
        
        # Vérifier les attributs de la première location
        old_letting1 = next((l for l in old_lettings if l.id == 1), None)
        assert old_letting1 is not None, "La location id=1 n'a pas été migrée vers l'ancien modèle"
        assert old_letting1.title == "Nice Apartment"
        
        # Vérifier que les nouveaux modèles ont été supprimés
        deleted_models = self.mock_schema_editor.deleted_models
        assert len(deleted_models) == 2, "Tous les nouveaux modèles n'ont pas été supprimés"
        
        # Vérifier les noms des classes des modèles supprimés
        deleted_model_names = [model.__name__ for model in deleted_models]
        assert 'NewAddress' in deleted_model_names
        assert 'NewLetting' in deleted_model_names
