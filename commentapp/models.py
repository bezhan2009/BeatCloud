from django.db import models
from django.contrib.auth.models import User
from musicapp.models import (Music,
                             Album)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    music = models.ForeignKey(Music, on_delete=models.CASCADE, null=True, blank=True)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=True, blank=True)
    parent_id = models.IntegerField(null=True)
    comment_text = models.TextField()
