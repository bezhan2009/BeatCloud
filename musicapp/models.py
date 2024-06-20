from django.db import models


class Artist(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Album(models.Model):
    title = models.CharField(max_length=100)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    release_date = models.DateField(blank=True, null=True)
    cover_image = models.ImageField(upload_to='album_covers/', blank=True, null=True)

    def __str__(self):
        return self.title


class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Music(models.Model):
    title = models.CharField(max_length=100)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, blank=True, null=True)
    genre = models.ManyToManyField(Genre, blank=True)
    release_date = models.DateField(blank=True, null=True)
    audio_file = models.FileField(upload_to='music_files/')
    duration = models.DurationField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.title
