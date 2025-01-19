from django.db import models
from django.contrib.auth.models import User
from musicapp.models import (Music,
                             Album)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    music = models.ForeignKey(Music, on_delete=models.CASCADE, null=True, blank=True)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=True, blank=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='children'
    )  # Связь с самим собой для дерева комментариев
    comment_text = models.TextField()

    def __str__(self):
        return f"Comment by {self.user} on {self.music or self.album}"
