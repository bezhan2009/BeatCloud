from django.urls import path

from . import views


urlpatterns = [
    path('', views.MusicList.as_view(), name="Music List"),
    path('<int:pk>/', views.MusicDetail.as_view(), name="Music Detail"),
    path('restore/<int:pk>', views.MusicRestoreView.as_view(), name="Music Restore View"),
    path('genre/', views.GenreList.as_view(), name="Genre List"),
    path('genre/<int:pk>/', views.GenreDetail.as_view(), name="Genre Detail"),
    path('album/', views.AlbumList.as_view(), name="Album List"),
]
