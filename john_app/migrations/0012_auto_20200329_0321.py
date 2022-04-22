# Generated by Django 2.0.6 on 2020-03-29 02:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('john_app', '0011_auto_20200309_2044'),
    ]

    operations = [
        migrations.AddField(
            model_name='abonnement',
            name='annuaire',
            field=models.BooleanField(default=False, verbose_name="Dans l'annuaire ?"),
        ),
        migrations.AddField(
            model_name='abonnement',
            name='contact2',
            field=models.CharField(default='', max_length=15, verbose_name='Téléphone 2'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='abonnement',
            name='contact3',
            field=models.CharField(default='', max_length=15, verbose_name='Téléphone 3'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='abonnement',
            name='email',
            field=models.CharField(default='', max_length=15, verbose_name='Email'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='abonnement',
            name='contact',
            field=models.CharField(max_length=15, verbose_name='Téléphone 1'),
        ),
    ]
