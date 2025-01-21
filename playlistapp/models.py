from django.db import models
from guardian.shortcuts import assign_perm

from musicapp.models import Genre, Music
from userapp.models import UserProfile


class Playlist(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    music = models.ManyToManyField(Music, through='PlaylistMusic', blank=True, related_name='songs_with_count')
    private = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        permissions = [
            ("all_playlist_perms", "Full access to playlists"),
            ("get_playlist", "View playlist"),
            ("add_music", "Add music to playlist"),
            ("remove_music", "Remove music from playlist"),
        ]


class PlaylistMusic(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    music = models.ForeignKey(Music, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('playlist', 'music')
