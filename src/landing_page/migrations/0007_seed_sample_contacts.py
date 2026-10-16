from django.db import migrations


def add_sample_contacts(apps, schema_editor):
    Contact = apps.get_model('landing_page', 'Contact')
    samples = [
        ('Alex Rivera', 'President', 'alex.rivera@example.com'),
        ('Jordan Lee', 'Vice President', 'jordan.lee@example.com'),
        ('Sam Patel', 'Treasurer', 'sam.patel@example.com'),
    ]
    for name, role, email in samples:
        Contact.objects.get_or_create(email=email, defaults={'name': name, 'role': role})


class Migration(migrations.Migration):

    # KEEP the dependencies list that Django generated in your file.
    # Only the function above and the operations below get replaced.
    dependencies = [
            ('landing_page', '0006_contact'),
    ]

    operations = [
        migrations.RunPython(add_sample_contacts, migrations.RunPython.noop),
    ]
