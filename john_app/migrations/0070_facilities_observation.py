# Generated by Django 2.2.6 on 2021-02-02 01:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('john_app', '0069_auto_20210202_0242'),
    ]

    operations = [
        migrations.AddField(
            model_name='facilities',
            name='observation',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
