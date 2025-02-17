# Generated by Django 5.0.6 on 2025-01-18 05:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30)),
                ('release_date', models.DateField(blank=True, null=True)),
                ('cover_image', models.ImageField(blank=True, null=True, upload_to='album_covers/')),
            ],
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Music',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30)),
                ('release_date', models.DateField(blank=True, null=True)),
                ('audio_file', models.FileField(upload_to='music_files/')),
                ('duration', models.DurationField(blank=True, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('listens', models.IntegerField(default=0)),
            ],
        ),
    ]
