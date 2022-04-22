# Generated by Django 2.2.6 on 2021-02-09 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('john_app', '0076_marketing_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marketing',
            name='client',
            field=models.ForeignKey(on_delete=None, to='john_app.Abonnement'),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='remarque',
            field=models.TextField(blank=True, null=True),
        ),
    ]
