# Generated by Django 2.2.6 on 2021-02-02 01:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('john_app', '0067_auto_20210202_0201'),
    ]

    operations = [
        migrations.AddField(
            model_name='filiale',
            name='code',
            field=models.IntegerField(default=1),
        ),
    ]
