# Generated by Django 5.0.6 on 2025-01-18 05:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('singerapp', '0001_initial'),
        ('userapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='singer',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='userapp.userprofile'),
        ),
    ]
