from django.db import migrations


def forward_func(apps, schema_editor):
    """
    Migrates data from the old 'oc_lettings_site' app to the new 'lettings' app.
    Copies all Address and Letting records from 'oc_lettings_site' to 'lettings',
    maintaining the same IDs to preserve relationships.
    Args:
        apps: The Django app registry.
        schema_editor: Database schema editor to apply changes.
    """

    # Get models from both old and new apps
    OldAddress = apps.get_model('oc_lettings_site', 'Address')
    OldLetting = apps.get_model('oc_lettings_site', 'Letting')
    NewAddress = apps.get_model('lettings', 'Address')
    NewLetting = apps.get_model('lettings', 'Letting')

    # Copy Address data
    for old_address in OldAddress.objects.all():
        new_address = NewAddress(
            id=old_address.id,
            number=old_address.number,
            street=old_address.street,
            city=old_address.city,
            state=old_address.state,
            zip_code=old_address.zip_code,
            country_iso_code=old_address.country_iso_code
        )
        new_address.save()

    # Copy Letting data
    for old_letting in OldLetting.objects.all():
        new_address = NewAddress.objects.get(id=old_letting.address_id)
        new_letting = NewLetting(
            id=old_letting.id,
            title=old_letting.title,
            address=new_address
        )
        new_letting.save()

    # Drop old tables from the 'oc_lettings_site' app
    schema_editor.delete_model(apps.get_model('oc_lettings_site', 'Address'))
    schema_editor.delete_model(apps.get_model('oc_lettings_site', 'Letting'))


def reverse_func(apps, schema_editor):
    """
    Reverts the migration by copying the data back from the new 'lettings' app
    to the old 'oc_lettings_site' app and then drops the new 'lettings' tables.
    Args:
        apps: The Django app registry.
        schema_editor: Database schema editor to apply changes.
    """

    # Get models from both old and new apps
    NewAddress = apps.get_model('lettings', 'Address')
    NewLetting = apps.get_model('lettings', 'Letting')
    OldAddress = apps.get_model('oc_lettings_site', 'Address')
    OldLetting = apps.get_model('oc_lettings_site', 'Letting')

    # Copy Address data back to the old app
    for new_address in NewAddress.objects.all():
        old_address = OldAddress(
            id=new_address.id,
            number=new_address.number,
            street=new_address.street,
            city=new_address.city,
            state=new_address.state,
            zip_code=new_address.zip_code,
            country_iso_code=new_address.country_iso_code
        )
        old_address.save()

    # Copy Letting data back to the old app
    for new_letting in NewLetting.objects.all():
        old_address = OldAddress.objects.get(id=new_letting.address_id)
        old_letting = OldLetting(
            id=new_letting.id,
            title=new_letting.title,
            address=old_address
        )
        old_letting.save()

    # Drop new tables from the 'lettings' app
    schema_editor.delete_model(apps.get_model('lettings', 'Address'))
    schema_editor.delete_model(apps.get_model('lettings', 'Letting'))


class Migration(migrations.Migration):
    """
    Migration to transfer data from 'oc_lettings_site' to 'lettings'.
    """

    dependencies = [
        ('lettings', '0001_initial'),
        ('oc_lettings_site', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forward_func, reverse_func),
    ]
