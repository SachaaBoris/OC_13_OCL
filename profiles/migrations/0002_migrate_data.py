from django.db import migrations, models


def forward_func(apps, schema_editor):
    """
    Migrates data from the old 'oc_lettings_site' app to the new 'profiles' app.
    Copies all profiles records from 'oc_lettings_site' to 'profiles',
    maintaining the same IDs to preserve relationships.
    Args:
        apps: The Django app registry.
        schema_editor: Database schema editor to apply changes.
    """

    # Get models from both old and new apps
    OldProfile = apps.get_model('oc_lettings_site', 'Profile')
    NewProfile = apps.get_model('profiles', 'Profile')

    # Copy Profile data
    for old_profile in OldProfile.objects.all():
        new_profile = NewProfile(
            id=old_profile.id,
            favorite_city=old_profile.favorite_city,
            user_id=old_profile.user_id
        )
        new_profile.save()

    # Drop old table from the 'oc_lettings_site' app
    schema_editor.delete_model(OldProfile)


def reverse_func(apps, schema_editor):
    """
    Reverts the migration by copying the data back from the new 'profile' app
    to the old 'oc_lettings_site' app and then drops the new 'profiles' table.
    Args:
        apps: The Django app registry.
        schema_editor: Database schema editor to apply changes.
    """

    # Get models from both old and new apps
    NewProfile = apps.get_model('profiles', 'Profile')
    OldProfile = apps.get_model('oc_lettings_site', 'Profile')

    # Copy Profile data
    for new_profile in NewProfile.objects.all():
        old_profile = OldProfile(
            id=new_profile.id,
            favorite_city=new_profile.favorite_city,
            user_id=new_profile.user_id
        )
        old_profile.save()

    # Drop new table from the 'profiles' app
    schema_editor.delete_model(NewProfile)


class Migration(migrations.Migration):
    """
    Migration to transfer data from 'oc_lettings_site' to 'profiles'.
    """

    dependencies = [
        ('profiles', '0001_initial'),
        ('oc_lettings_site', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forward_func, reverse_func),
    ]
