# Generated by Django 5.0.6 on 2025-01-19 15:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('featuredapp', '0003_initial'),
        ('musicapp', '0005_alter_music_album'),
    ]

    operations = [
        migrations.AlterField(
            model_name='featuredalbum',
            name='album',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='album', to='musicapp.album'),
        ),
        migrations.AlterField(
            model_name='featuredmusic',
            name='music',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='music', to='musicapp.music'),
        ),
    ]
