from django.urls import path
from . import views

urlpatterns = [
    path('music/<int:music_id>/', views.CommentMusicList.as_view(), name='comment music list'),
    path('album/<int:album_id>/', views.CommentAlbumList.as_view(), name='comment album list'),
    path('<int:comment_id>/detail/', views.CommentDetail.as_view(), name='comment_detail'),
]
