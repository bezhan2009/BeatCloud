from django.contrib import admin
from featuredapp.models import (FeaturedMusic,
                                FeaturedAlbum)

admin.site.register(FeaturedMusic)
admin.site.register(FeaturedAlbum)
