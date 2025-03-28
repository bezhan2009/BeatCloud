from django.utils import timezone
from django.db import models
from userapp.models import UserProfile
from singerapp.models import Singer


class Album(models.Model):
    title = models.CharField(max_length=30)
    singer = models.ForeignKey(Singer, on_delete=models.CASCADE)
    release_date = models.DateField(blank=True, null=True, default=timezone.now)
    cover_image = models.ImageField(upload_to='album_covers/', blank=True, null=True)

    def __str__(self):
        return self.title


class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Music(models.Model):
    title = models.CharField(max_length=30)
    singer = models.ForeignKey(Singer, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, blank=True, null=True,
                              related_name="songs")
    genre = models.ManyToManyField(Genre, blank=True)
    release_date = models.DateField(blank=True, null=True, default=timezone.now)
    audio_file = models.FileField(upload_to='music_files/')
    duration = models.DurationField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    listens = models.IntegerField(default=0)

    def __str__(self):
        return self.title
