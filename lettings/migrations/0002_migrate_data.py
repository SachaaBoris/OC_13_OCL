from django.db import migrations


def forward_func(apps, schema_editor):
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


def reverse_func(apps, schema_editor):
    # Delete all data from new models
    NewLetting = apps.get_model('lettings', 'Letting')
    NewAddress = apps.get_model('lettings', 'Address')

    NewLetting.objects.all().delete()
    NewAddress.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('lettings', '0001_initial'),
        ('oc_lettings_site', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forward_func, reverse_func),
    ]
