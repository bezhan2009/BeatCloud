from django.urls import path

from . import views


urlpatterns = [
    path("", views.MusicList.as_view(), name="Music List"),
    path("detail/", views.MusicDetail.as_view(), name="Music Detail"),
    path("restore/", views.MusicRestoreView.as_view(), name="Music Restore View")
]
