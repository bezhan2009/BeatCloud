from guardian.admin import GuardedModelAdmin
from django.contrib import admin
from playlistapp.models import Playlist


@admin.register(Playlist)
class PlaylistAdmin(GuardedModelAdmin):
    pass
