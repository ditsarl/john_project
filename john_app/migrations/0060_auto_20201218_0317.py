# Generated by Django 2.2.6 on 2020-12-18 02:17

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('john_app', '0059_auto_20201218_0316'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='aircraft_available',
            name='jour',
        ),
        migrations.AddField(
            model_name='aircraft_available',
            name='dateVoyage',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
