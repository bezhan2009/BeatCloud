from django.db import models
from userapp.models import UserProfile
from musicapp.models import Music
from singerapp.models import Singer


class Followers(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    singer = models.ForeignKey(Singer, on_delete=models.CASCADE)


class Likes(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    music = models.ForeignKey(Music, on_delete=models.CASCADE)

