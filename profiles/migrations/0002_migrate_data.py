from django.db import migrations


def forward_func(apps, schema_editor):
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


def reverse_func(apps, schema_editor):
    # Delete all data from new model
    NewProfile = apps.get_model('profiles', 'Profile')
    NewProfile.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
        ('oc_lettings_site', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forward_func, reverse_func),
    ]
