from django.contrib import admin
from subscriptions.models import (Followers,
                                  Likes)


admin.site.register(Followers)
admin.site.register(Likes)
