# Generated by Django 2.2.6 on 2020-12-02 01:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('john_app', '0030_gift_gift_gain'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gift',
            name='code',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
