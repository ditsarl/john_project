# Generated by Django 2.2.6 on 2020-12-13 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('john_app', '0040_taxi'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reservation_Taxi',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_taxi', models.DateField()),
                ('heure_taxi', models.TimeField()),
                ('lieu', models.CharField(max_length=200)),
                ('code_reservation', models.CharField(max_length=10)),
                ('active', models.BooleanField(default=True)),
                ('Taxi', models.ForeignKey(on_delete=None, to='john_app.Taxi')),
                ('client', models.ForeignKey(on_delete=None, to='john_app.Abonnement')),
            ],
        ),
    ]
