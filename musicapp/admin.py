from django.contrib import admin

from .models import (
    Album,
    Genre,
    Music
    )

admin.site.register(Album)
admin.site.register(Genre)
admin.site.register(Music)
