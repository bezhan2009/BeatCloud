# Generated by Django 5.0.6 on 2025-01-20 18:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('musicapp', '0005_alter_music_album'),
        ('userapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeaturedPlaylists',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='FeaturedAlbum',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('album', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='album', to='musicapp.album')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userapp.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='FeaturedMusic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('music', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='music', to='musicapp.music')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userapp.userprofile')),
            ],
        ),
    ]
