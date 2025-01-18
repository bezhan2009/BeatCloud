# Generated by Django 5.0.6 on 2025-01-18 05:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('featuredapp', '0002_initial'),
        ('musicapp', '0002_initial'),
        ('userapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='featuredalbum',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userapp.userprofile'),
        ),
        migrations.AddField(
            model_name='featuredmusic',
            name='music',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='musicapp.music'),
        ),
        migrations.AddField(
            model_name='featuredmusic',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userapp.userprofile'),
        ),
    ]
