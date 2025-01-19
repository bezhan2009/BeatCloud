from django.db import models
from musicapp.models import Music, Album
from userapp.models import UserProfile


class FeaturedMusic(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    music = models.ForeignKey(Music, on_delete=models.CASCADE, related_name='music')


class FeaturedAlbum(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='album')
