# Generated by Django 2.2.6 on 2020-12-13 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('john_app', '0041_reservation_taxi'),
    ]

    operations = [
        migrations.AddField(
            model_name='taxi',
            name='vip',
            field=models.BooleanField(default=False),
        ),
    ]
